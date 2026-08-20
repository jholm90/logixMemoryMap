<#
.SYNOPSIS
  Walks a batch of converted .ACD files one at a time with an explicit
  open / enter-memory / close / continue loop (James, 2026-08-20):

    1. Shows the next file.
    2. Press Enter to open it in Studio 5000.
    3. Verify/compile the project (no download needed -- Logix Designer
       shows memory usage in Controller Properties as soon as it compiles
       offline, see docs/TESTING_PLAN.md), read the Memory tab, type the
       number in.
    4. Close the project in Studio 5000, then press Enter to continue --
       this gate exists so the next file's Studio 5000 instance doesn't
       stack up on top of one still open.
    5. Row is logged immediately, then loops to the next file.

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

$alreadyLogged = @{}
if (Test-Path $ManifestPath) {
    Import-Csv $ManifestPath | ForEach-Object { $alreadyLogged[$_.l5x_path] = $true }
} else {
    "sample_id,description,category,l5x_path,predicted_bytes,actual_bytes,delta,delta_pct,controller_model,firmware_rev,date_tested,notes" |
        Out-File -FilePath $ManifestPath -Encoding utf8
}

$rows = Import-Csv $ConvertLog | Where-Object { $_.status -eq "ok" }
$remaining = $rows | Where-Object { -not $alreadyLogged.ContainsKey($_.l5x_path) }
Write-Host "$($rows.Count) converted sample(s) in log; $($alreadyLogged.Count) already logged; $($remaining.Count) remaining."
Write-Host "You can close this window at any time -- already-logged rows are skipped on the next run."

foreach ($row in $remaining) {
    $meta = Get-SampleIdAndDescription $row.l5x_path
    $category = Get-Category $row.l5x_path

    Write-Host ""
    Write-Host "=== $($meta.Id) : $($meta.Desc) [$category] ==="
    Write-Host "Next file: $($row.acd_path)"
    $key = Read-Host "Press Enter to open it (or 'q' to stop here)"
    if ($key -eq 'q') {
        Write-Host "Stopping. Resume later by re-running this script -- completed rows are skipped."
        break
    }

    Start-Process $row.acd_path
    Write-Host "Opened. Verify/compile the project, then read Controller Properties -> Memory tab."

    $bytes = Read-Host "Bytes used (or 's' to skip this file)"
    if ($bytes -eq 's' -or [string]::IsNullOrWhiteSpace($bytes)) {
        Write-Host "Skipped -- close the project manually if you opened it."
        continue
    }

    $notes = Read-Host "Notes (optional)"

    Read-Host "Close the project in Studio 5000, then press Enter to continue"

    $date = Get-Date -Format "yyyy-MM-dd"
    $line = @($meta.Id, $meta.Desc, $category, $row.l5x_path, "", $bytes, "", "", $ControllerModel, $FirmwareRev, $date, $notes) -join ","
    $line | Out-File -FilePath $ManifestPath -Append -Encoding utf8
    Write-Host "Logged."
}

Write-Host ""
Write-Host "Done for now. predicted_bytes/delta/delta_pct columns left blank -- fill by cross-referencing this tool's own 'size' CLI output (or the manifest row the sample generator already wrote, if this was a sample_gen-produced file)."
