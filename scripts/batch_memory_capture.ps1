<#
.SYNOPSIS
  Walks a batch of converted .ACD files one at a time, opens each in Studio
  5000 Logix Designer, and prompts you to type in the memory-used figure from
  Controller Properties -> Memory tab. Appends each result as a row to
  samples/manifest.csv. Resumable: already-logged l5x_path rows are skipped,
  so you can stop partway through a few hundred samples and pick back up.

  This does NOT go online/download or read memory automatically — that part
  (OQ-MEMREADMETHOD) is still open. This script only removes the file-hunting
  and manifest-formatting toil around the manual read.

.PREREQS
  Run batch_l5x_to_acd.ps1 first; this script consumes its convert_log.csv.

.EXAMPLE
  ./batch_memory_capture.ps1 -ConvertLog C:\l5x_scratch\acd\convert_log.csv `
      -ManifestPath ..\samples\manifest.csv -ControllerModel "1769-L33ER" -FirmwareRev "35.11"
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
Write-Host "$($rows.Count) converted sample(s) in log; $($alreadyLogged.Count) already in manifest."

foreach ($row in $rows) {
    if ($alreadyLogged.ContainsKey($row.l5x_path)) {
        continue
    }

    $meta = Get-SampleIdAndDescription $row.l5x_path
    $category = Get-Category $row.l5x_path

    Write-Host ""
    Write-Host "=== $($meta.Id) : $($meta.Desc) [$category] ==="
    Write-Host "Opening $($row.acd_path) ..."
    Start-Process $row.acd_path

    $bytes = Read-Host "Bytes used (Controller Properties -> Memory tab). Enter number, 's' to skip, or 'q' to stop"
    if ($bytes -eq 'q') {
        Write-Host "Stopping. Resume later by re-running this script — completed rows are skipped."
        break
    }
    if ($bytes -eq 's' -or [string]::IsNullOrWhiteSpace($bytes)) {
        Write-Host "Skipped."
        continue
    }

    $notes = Read-Host "Notes (optional)"
    $date = Get-Date -Format "yyyy-MM-dd"
    $line = @($meta.Id, $meta.Desc, $category, $row.l5x_path, "", $bytes, "", "", $ControllerModel, $FirmwareRev, $date, $notes) -join ","
    $line | Out-File -FilePath $ManifestPath -Append -Encoding utf8
    Write-Host "Logged."
}

Write-Host ""
Write-Host "Done. predicted_bytes/delta/delta_pct columns left blank — fill by cross-referencing this tool's own 'size' CLI output per sample."
