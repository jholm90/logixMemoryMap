<#
.SYNOPSIS
  Walks a batch of converted .ACD files one at a time, now driven by
  James's AHK build/verify automation instead of manual typing (2026-08-22
  rewrite -- was: read the Capacity tab's "Used" figure by eye and type it
  in; the AHK script now reads that value AND the Build results (error
  count, warning count, a trending message) directly off screen via
  ControlGetText, so this script's job shrinks to: open the next file,
  wait for the AHK cycle to finish, read what it captured, log it, repeat.

    1. Shows "[N/Total] sample_id : description" and auto-opens the ACD --
       no gate before opening.
    2. Prompts you to run the AHK build/verify automation (Ctrl+F1 in the
       Logix window, or however your loop is triggered) against the
       now-open file, then press Enter here once it's finished ('q' to
       stop here, 's' to skip this file unlogged).
    3. Reads the AHK handoff CSV (-HandoffPath, overwritten by AHK each
       cycle: error_count,warning_count,message_value,ocd_value) and logs
       all four values into this row -- ocd_value becomes actual_bytes
       (same "Capacity tab, 1 block == 1 byte" figure as before, just
       captured automatically instead of typed), error_count/warning_count/
       message_value are new columns for trending build/verify results
       alongside the memory data.
    4. The handoff file is deleted right after being read, every cycle --
       if AHK hasn't written a fresh one by the time you press Enter, this
       fails loudly and asks you to retry rather than silently reusing a
       stale value from the previous file (see James's whole session
       today re: don't trust data unless it's been validated).
    5. Row is updated in place (matched by l5x_path against the row the
       sample generator already wrote, so predicted_bytes stays put) and
       written immediately.

  Nothing in the script waits on you to close the previous Studio 5000
  instance -- that's on you to manage, not a gate it enforces.

  Resumable: you can close this window at any point without losing place.
  Already-logged l5x_path rows are skipped on the next run, and nothing is
  written until a row is actually complete, so there's never a half-done
  row to clean up.

.PREREQS
  Run batch_l5x_to_acd.ps1 first; this script consumes its convert_log.csv.
  Your AHK script must be running and writing its handoff CSV to -HandoffPath
  every cycle (error_count,warning_count,message_value,ocd_value -- header
  row + one data row, overwritten not appended).

.EXAMPLE
  ./batch_memory_capture.ps1 -ConvertLog C:\l5x_scratch\acd\convert_log.csv `
      -ManifestPath ..\samples\manifest.csv -ControllerModel "5069-L306ER" -FirmwareRev "35.11" `
      -HandoffPath C:\path\to\your\ahk\ahk_handoff.csv
#>
param(
    [Parameter(Mandatory = $true)][string]$ConvertLog,
    [Parameter(Mandatory = $true)][string]$ManifestPath,
    [Parameter(Mandatory = $true)][string]$ControllerModel,
    [Parameter(Mandatory = $true)][string]$FirmwareRev,
    [Parameter(Mandatory = $true)][string]$HandoffPath
)

function Get-SampleIdAndDescription($l5xPath) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($l5xPath)
    if ($base -match '^(sample_\d+)_(.+)$') {
        return @{ Id = $Matches[1]; Desc = ($Matches[2] -replace '_', ' ') }
    }
    return @{ Id = $base; Desc = "" }
}

function Get-Category($l5xPath) {
    (Get-Item $l5xPath).Directory.Name
}

function Get-RelPath($fullPath) {
    # convert_log.csv stores absolute Windows paths; manifest.csv stores
    # repo-relative posix paths (e.g. "samples/generated/udt/x.L5X") -- key
    # off the "samples" segment onward so the two can be matched regardless
    # of where the repo lives on disk.
    $parts = $fullPath -replace '\\', '/' -split '/'
    $idx = [array]::IndexOf($parts, "samples")
    if ($idx -lt 0) { return $fullPath -replace '\\', '/' }
    ($parts[$idx..($parts.Length - 1)]) -join '/'
}

$ManifestColumns = "sample_id,description,category,l5x_path,predicted_bytes,actual_bytes,delta,delta_pct," +
    "controller_model,firmware_rev,date_tested,notes,error_count,warning_count,message_value"

if (-not (Test-Path $ManifestPath)) {
    $ManifestColumns | Out-File -FilePath $ManifestPath -Encoding utf8
}
$manifest = @(Import-Csv $ManifestPath)
$alreadyLogged = @{}
$manifest | Where-Object { $_.actual_bytes } | ForEach-Object { $alreadyLogged[$_.l5x_path] = $true }

$rows = Import-Csv $ConvertLog | Where-Object { $_.status -eq "ok" }
$remaining = $rows | Where-Object { -not $alreadyLogged.ContainsKey((Get-RelPath $_.l5x_path)) }
Write-Host "$($rows.Count) converted sample(s) in log; $($alreadyLogged.Count) already logged; $($remaining.Count) remaining."
Write-Host "You can close this window at any time -- already-logged rows are skipped on the next run."

# Stale handoff from a previous, unrelated run shouldn't get attributed to
# the first file of this run -- start clean.
if (Test-Path $HandoffPath) { Remove-Item $HandoffPath -Force }

$total = $remaining.Count
$idx = 0
foreach ($row in $remaining) {
    $idx++
    $relPath = Get-RelPath $row.l5x_path
    $meta = Get-SampleIdAndDescription $row.l5x_path
    $category = Get-Category $row.l5x_path
    $existing = $manifest | Where-Object { $_.l5x_path -eq $relPath } | Select-Object -First 1

    Write-Host ""
    Write-Host "=== [$idx/$total] $($meta.Id) : $($meta.Desc) [$category] ==="
    Write-Host "Opening: $($row.acd_path)"
    Start-Process $row.acd_path

    $ready = $false
    $blocksUsed = $null
    $errorCount = ""
    $warningCount = ""
    $messageValue = ""

    while (-not $ready) {
        $ack = Read-Host "Run the AHK build/verify on this file, then press Enter here when it's done ('q' to stop, 's' to skip)"
        if ($ack -eq 'q') {
            Write-Host "Stopping. Resume later by re-running this script -- completed rows are skipped."
            $idx = $total + 1  # break the outer loop below too
            break
        }
        if ($ack -eq 's') {
            Write-Host "Skipped -- close the project manually if you opened it."
            break
        }

        if (-not (Test-Path $HandoffPath)) {
            Write-Host "No handoff file found at $HandoffPath yet -- AHK hasn't written a result. Try again once it's finished."
            continue
        }

        $handoff = Import-Csv $HandoffPath
        if (-not $handoff -or $handoff.Count -eq 0) {
            Write-Host "Handoff file is empty/unreadable -- try again."
            continue
        }
        $result = $handoff[0]
        if ([string]::IsNullOrWhiteSpace($result.ocd_value)) {
            Write-Host "Handoff file has no ocd_value -- AHK may not have finished the Capacity read. Try again."
            continue
        }

        $blocksUsed = $result.ocd_value
        $errorCount = $result.error_count
        $warningCount = $result.warning_count
        $messageValue = $result.message_value
        Remove-Item $HandoffPath -Force  # consumed -- next file must produce a fresh one
        $ready = $true
    }

    if ($idx -gt $total) { break }
    if (-not $ready) { continue }

    $notes = ""
    $date = Get-Date -Format "yyyy-MM-dd"
    $predicted = if ($existing -and $existing.predicted_bytes) { $existing.predicted_bytes } else { "" }
    $delta = ""
    $deltaPct = ""
    if ($predicted -ne "") {
        $delta = [int]$blocksUsed - [int]$predicted
        if ([int]$predicted -ne 0) { $deltaPct = [math]::Round(100.0 * $delta / [int]$predicted, 2) }
    }

    if ($existing) {
        $existing.actual_bytes = $blocksUsed
        $existing.delta = $delta
        $existing.delta_pct = $deltaPct
        $existing.controller_model = $ControllerModel
        $existing.firmware_rev = $FirmwareRev
        $existing.date_tested = $date
        $existing.notes = $notes
        $existing.error_count = $errorCount
        $existing.warning_count = $warningCount
        $existing.message_value = $messageValue
    } else {
        $manifest += [pscustomobject]@{
            sample_id = $meta.Id; description = $meta.Desc; category = $category; l5x_path = $relPath
            predicted_bytes = ""; actual_bytes = $blocksUsed; delta = $delta; delta_pct = $deltaPct
            controller_model = $ControllerModel; firmware_rev = $FirmwareRev; date_tested = $date; notes = $notes
            error_count = $errorCount; warning_count = $warningCount; message_value = $messageValue
        }
    }
    $manifest | Export-Csv -Path $ManifestPath -NoTypeInformation -Encoding utf8
    Write-Host "Logged: actual_bytes=$blocksUsed errors=$errorCount warnings=$warningCount message=`"$messageValue`""
}

Write-Host ""
Write-Host "Done for now."

# Auto-push (James, 2026-08-20: "so i dont have to ask").
. (Join-Path $PSScriptRoot "_autopush.ps1")
Push-RepoFile -RepoRoot (Split-Path $PSScriptRoot -Parent) -FilePath $ManifestPath -CommitMessage "Log real memory capture + build/verify results"
