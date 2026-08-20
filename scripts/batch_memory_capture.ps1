<#
.SYNOPSIS
  Walks a batch of converted .ACD files one at a time with an
  auto-open / enter-blocks / close / continue loop (James, 2026-08-20,
  updated 2026-08-20 to auto-open + show progress):

    1. Shows "[N/Total] sample_id : description" and auto-opens the ACD --
       no press-Enter-to-open gate, since Logix Designer's load time meant
       waiting around and missing that prompt.
    2. Press Enter once it's loaded and compiled (or 'q' to stop right
       there -- the earliest bail-out point, before waiting through
       verify/compile).
    3. Verify/compile the project (no download needed -- Logix Designer
       shows memory usage in Controller Properties as soon as it compiles
       offline, see docs/TESTING_PLAN.md), read the Capacity tab's "Used"
       figure (reported in "blocks" -- confirmed 1 block == 1 byte), type
       the number in.
    4. Close the project in Studio 5000, then press Enter to continue --
       this gate exists so the next file's Studio 5000 instance doesn't
       stack up on top of one still open.
    5. Row is updated in place (matched by l5x_path against the row the
       sample generator already wrote, so predicted_bytes/delta/delta_pct
       stay on the same row) and written immediately, then loops to the
       next file.

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

    # Fires the open immediately (no press-Enter-to-open gate) since Logix
    # Designer's load time meant James was repeatedly walking away and
    # missing that prompt. This is now the earliest point he can bail --
    # 'q' here stops before waiting through verify/compile at all.
    $key = Read-Host "Opened. Press Enter once it's loaded and compiled (or 'q' to stop here)"
    if ($key -eq 'q') {
        Write-Host "Stopping. Resume later by re-running this script -- completed rows are skipped."
        break
    }
    Write-Host "Read Controller Properties -> Capacity tab."

    # James (2026-08-20): Studio 5000's Capacity tab reports "blocks", not
    # bytes -- confirmed 1 block == 1 byte (Total shown there matched this
    # project's controller_budgets.yaml byte figure exactly), so the raw
    # number goes straight into actual_bytes with no conversion.
    $blocksUsed = Read-Host "Blocks used, from Capacity tab (or 's' to skip this file)"
    if ($blocksUsed -eq 's' -or [string]::IsNullOrWhiteSpace($blocksUsed)) {
        Write-Host "Skipped -- close the project manually if you opened it."
        continue
    }

    $notes = Read-Host "Notes (optional)"

    Read-Host "Close the project in Studio 5000, then press Enter to continue"

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
