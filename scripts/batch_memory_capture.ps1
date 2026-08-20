<#
.SYNOPSIS
  Walks a batch of converted .ACD files one at a time (James, 2026-08-20,
  simplified 2026-08-20 to a single prompt per file):

    1. Shows "[N/Total] sample_id : description" and auto-opens the ACD --
       no gate before opening.
    2. One prompt: "Blocks used, from Capacity tab ('q' to stop here or
       's' to skip this file)". Verify/compile the project in Studio 5000
       (no download needed -- Logix Designer shows memory usage in
       Controller Properties as soon as it compiles offline, see
       docs/TESTING_PLAN.md), read the Capacity tab's "Used" figure
       (reported in "blocks" -- confirmed 1 block == 1 byte), type the
       number and press Enter -- that logs the row AND opens the next
       file in one step. 'q' stops here; 's' skips this file unlogged.
    3. Row is updated in place (matched by l5x_path against the row the
       sample generator already wrote, so predicted_bytes/delta/delta_pct
       stay on the same row) and written immediately.

  Nothing in the script waits on you to close the previous Studio 5000
  instance -- that's on you to manage, not a gate it enforces.

  Resumable: you can close this window at any point without losing place.
  Already-logged l5x_path rows are skipped on the next run, and nothing is
  written until a row is actually complete, so there's never a half-done
  row to clean up.

.PREREQS
  Run batch_l5x_to_acd.ps1 first; this script consumes its convert_log.csv.

.EXAMPLE
  ./batch_memory_capture.ps1 -ConvertLog C:\l5x_scratch\acd\convert_log.csv `
      -ManifestPath ..\samples\manifest.csv -ControllerModel "5069-L306ER" -FirmwareRev "35.11"
#>
param(
    [Parameter(Mandatory = $true)][string]$ConvertLog,
    [Parameter(Mandatory = $true)][string]$ManifestPath,
    [Parameter(Mandatory = $true)][string]$ControllerModel,
    [Parameter(Mandatory = $true)][string]$FirmwareRev
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

if (-not (Test-Path $ManifestPath)) {
    "sample_id,description,category,l5x_path,predicted_bytes,actual_bytes,delta,delta_pct,controller_model,firmware_rev,date_tested,notes" |
        Out-File -FilePath $ManifestPath -Encoding utf8
}
$manifest = @(Import-Csv $ManifestPath)
$alreadyLogged = @{}
$manifest | Where-Object { $_.actual_bytes } | ForEach-Object { $alreadyLogged[$_.l5x_path] = $true }

$rows = Import-Csv $ConvertLog | Where-Object { $_.status -eq "ok" }
$remaining = $rows | Where-Object { -not $alreadyLogged.ContainsKey((Get-RelPath $_.l5x_path)) }
Write-Host "$($rows.Count) converted sample(s) in log; $($alreadyLogged.Count) already logged; $($remaining.Count) remaining."
Write-Host "You can close this window at any time -- already-logged rows are skipped on the next run."

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

    # James (2026-08-20): Studio 5000's Capacity tab reports "blocks", not
    # bytes -- confirmed 1 block == 1 byte (Total shown there matched this
    # project's controller_budgets.yaml byte figure exactly), so the raw
    # number goes straight into actual_bytes with no conversion. Single
    # prompt per file: enter the number and Enter logs it and opens the
    # next file; 'q' quits; 's' skips this file without logging it.
    $blocksUsed = Read-Host "Blocks used, from Capacity tab ('q' to stop here or 's' to skip this file)"
    if ($blocksUsed -eq 'q') {
        Write-Host "Stopping. Resume later by re-running this script -- completed rows are skipped."
        break
    }
    if ($blocksUsed -eq 's' -or [string]::IsNullOrWhiteSpace($blocksUsed)) {
        Write-Host "Skipped -- close the project manually if you opened it."
        continue
    }

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
    } else {
        $manifest += [pscustomobject]@{
            sample_id = $meta.Id; description = $meta.Desc; category = $category; l5x_path = $relPath
            predicted_bytes = ""; actual_bytes = $blocksUsed; delta = $delta; delta_pct = $deltaPct
            controller_model = $ControllerModel; firmware_rev = $FirmwareRev; date_tested = $date; notes = $notes
        }
    }
    $manifest | Export-Csv -Path $ManifestPath -NoTypeInformation -Encoding utf8
    Write-Host "Logged."
}

Write-Host ""
Write-Host "Done for now."

# Auto-push (James, 2026-08-20: "so i dont have to ask").
. (Join-Path $PSScriptRoot "_autopush.ps1")
Push-RepoFile -RepoRoot (Split-Path $PSScriptRoot -Parent) -FilePath $ManifestPath -CommitMessage "Log real memory capture results"
