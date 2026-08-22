<#
.SYNOPSIS
  Batch-converts every .L5X in a folder to .ACD using Rockwell's own l5xgit
  CLI (from RockwellAutomation/ra-logix-designer-vcs-custom-tools), so
  hundreds of samples can be compiled without opening Logix Designer by hand.

  Resumable (James, 2026-08-20): re-running with the same -OutputDir picks
  up where it left off -- already-converted files (status "ok" in
  convert_log.csv) are skipped, so stopping partway through doesn't lose
  progress. Press any key at any point to stop cleanly after the file
  currently converting finishes; nothing is lost, just re-run the same
  command later to continue.

  Auto-pushes a copy of the log to samples/convert_log.csv in the repo on
  every run (success or early-stop) so conversion failures are visible
  without pasting terminal output.

.PREREQS
  - Studio 5000 Logix Designer + Logix Designer SDK 2.2+ installed
  - l5xgit.exe built from https://github.com/RockwellAutomation/ra-logix-designer-vcs-custom-tools
    (dotnet build against .NET 10 SDK) and either on PATH or passed via -L5xGitPath

.EXAMPLE
  ./batch_l5x_to_acd.ps1 -InputDir ..\samples\generated -OutputDir C:\l5x_scratch\acd
#>
param(
    [Parameter(Mandatory = $true)][string]$InputDir,
    [Parameter(Mandatory = $true)][string]$OutputDir,
    [string]$L5xGitPath = "l5xgit",
    [switch]$UnsafeSkipDependencyCheck
)

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$logPath = Join-Path $OutputDir "convert_log.csv"

$alreadyDone = @{}
if (Test-Path $logPath) {
    Import-Csv $logPath | Where-Object { $_.status -eq "ok" } | ForEach-Object { $alreadyDone[$_.l5x_path] = $true }
} else {
    "l5x_path,acd_path,status,message" | Out-File -FilePath $logPath -Encoding utf8
}

$files = Get-ChildItem -Path $InputDir -Filter *.L5X -Recurse
Write-Host "Found $($files.Count) L5X file(s) under $InputDir; $($alreadyDone.Count) already converted."
Write-Host "Press any key at any time to stop cleanly after the current file (resume later by re-running)."

# Clear any buffered keypresses from before the loop started.
while ([Console]::KeyAvailable) { [Console]::ReadKey($true) | Out-Null }

$i = 0
$stopRequested = $false
$fileTimes = @()
$batchSw = [System.Diagnostics.Stopwatch]::StartNew()
foreach ($f in $files) {
    if ($alreadyDone.ContainsKey($f.FullName)) {
        continue
    }

    $i++
    $acdPath = Join-Path $OutputDir ($f.BaseName + ".ACD")
    Write-Host "[$i/$($files.Count - $alreadyDone.Count)] $($f.Name) -> $acdPath"
    $fileSw = [System.Diagnostics.Stopwatch]::StartNew()

    $argList = @("l5x2acd", "--l5x", $f.FullName, "--acd", $acdPath)
    if ($UnsafeSkipDependencyCheck) { $argList += "--unsafe-skip-dependency-check" }

    $result = & $L5xGitPath @argList 2>&1
    $exitCode = $LASTEXITCODE
    $fileSw.Stop()
    $fileSeconds = [math]::Round($fileSw.Elapsed.TotalSeconds, 1)
    $fileTimes += $fileSeconds

    if ($exitCode -eq 0) {
        "$($f.FullName),$acdPath,ok," | Out-File -FilePath $logPath -Append -Encoding utf8
        Write-Host "  ok (${fileSeconds}s)"
    } else {
        $msg = ($result -join " ") -replace ",", ";"
        "$($f.FullName),$acdPath,FAILED,$msg" | Out-File -FilePath $logPath -Append -Encoding utf8
        Write-Warning "  Conversion failed (${fileSeconds}s): $msg"
    }

    if ([Console]::KeyAvailable) {
        [Console]::ReadKey($true) | Out-Null
        Write-Host "Key pressed -- stopping. Re-run the same command to resume; already-converted files are skipped."
        $stopRequested = $true
        break
    }
}
$batchSw.Stop()

if ($fileTimes.Count -gt 0) {
    $avgSeconds = [math]::Round((($fileTimes | Measure-Object -Average).Average), 1)
    $totalMinutes = [math]::Round($batchSw.Elapsed.TotalMinutes, 1)
    Write-Host "Batch: $($fileTimes.Count) file(s) converted this pass, ${totalMinutes}min total, avg ${avgSeconds}s/file."
}

if (-not $stopRequested) {
    Write-Host "Done. Log: $logPath"
} else {
    Write-Host "Stopped early. Log: $logPath"
}

# Copy the log into the repo and push it (James, 2026-08-20: "i dont want to
# copy/paste from powershell everytime") -- $OutputDir/convert_log.csv lives
# outside the repo (it's next to the .ACD binaries), so without this Claude
# never sees conversion failures unless they're pasted in by hand.
$repoRoot = Split-Path $PSScriptRoot -Parent
$repoLogPath = Join-Path $repoRoot "samples\convert_log.csv"
Copy-Item -Path $logPath -Destination $repoLogPath -Force
. (Join-Path $PSScriptRoot "_autopush.ps1")
Push-RepoFile -RepoRoot $repoRoot -FilePath $repoLogPath -CommitMessage "Log L5X->ACD conversion results"
