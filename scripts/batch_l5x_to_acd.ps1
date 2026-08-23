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

  Staleness-aware (2026-08-22, rewritten same day after the first version
  backfired). Originally tracked each L5X's LastWriteTimeUtc in
  convert_log.csv and compared against that on the next run -- fixed the
  original bug (real Build errors against pre-fix .ACD binaries, because
  the old "already converted" cache had no time info at all) but had its
  own flaw: old-format log rows (from before this column existed) were
  always treated as stale, forcing a full reconversion of the entire
  corpus on upgrade. James: "this is not fast 50s per file.. 500 minutes
  is a very long time" -- 586 files all being reconverted because of a
  log-format migration, when maybe 15 actually needed it.

  Now compares timestamps directly off disk instead, no log dependency:
  a file is stale (needs reconversion) only if its .L5X is newer than its
  own already-existing .ACD at $OutputDir. No .ACD yet -> never
  converted, needs it. .ACD newer than or equal to the .L5X -> still
  good, skipped. This is ground truth (doesn't care what convert_log.csv
  says or whether it's in an old format) and self-heals: nothing forces a
  full pass ever again, each file's real staleness is just re-checked
  fresh every run.

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
if (-not (Test-Path $logPath)) {
    "l5x_path,acd_path,status,message,l5x_mtime" | Out-File -FilePath $logPath -Encoding utf8
}

$allFiles = Get-ChildItem -Path $InputDir -Filter *.L5X -Recurse
$files = $allFiles | Where-Object {
    $acdPath = Join-Path $OutputDir ($_.BaseName + ".ACD")
    if (-not (Test-Path $acdPath)) { return $true }  # never converted -- needs it
    return $_.LastWriteTimeUtc -gt (Get-Item $acdPath).LastWriteTimeUtc  # true if the L5X is newer than its own .ACD
}
$upToDateCount = $allFiles.Count - $files.Count
Write-Host "Found $($allFiles.Count) L5X file(s) under $InputDir; $upToDateCount already converted and up to date; $($files.Count) to convert this pass."
Write-Host "Press any key at any time to stop cleanly after the current file (resume later by re-running)."

# Clear any buffered keypresses from before the loop started.
while ([Console]::KeyAvailable) { [Console]::ReadKey($true) | Out-Null }

$i = 0
$total = $files.Count
$stopRequested = $false
$fileTimes = @()
$batchSw = [System.Diagnostics.Stopwatch]::StartNew()
foreach ($f in $files) {
    $i++
    $acdPath = Join-Path $OutputDir ($f.BaseName + ".ACD")
    Write-Host "[$i/$total] $($f.Name) -> $acdPath"
    $fileSw = [System.Diagnostics.Stopwatch]::StartNew()

    # James, 2026-08-22: "you will need to append V2 onto the ACD files
    # you are regenerating as youre probably not overwriting them" -- the
    # staleness check above correctly decides a file needs reconverting,
    # but that's worthless if l5xgit itself silently refuses to overwrite
    # an existing .ACD at the destination path (unverified either way
    # from here -- l5xgit is Windows-only, not runnable in this
    # environment). Deleting the old file first removes the question:
    # whatever l5xgit does with a missing destination, "stale content
    # still on disk after a successful reconversion" can't happen. Also
    # means the staleness check's own .ACD-mtime comparison always sees a
    # genuinely fresh write, never a stale file l5xgit silently declined
    # to touch.
    if (Test-Path $acdPath) { Remove-Item $acdPath -Force }

    $argList = @("l5x2acd", "--l5x", $f.FullName, "--acd", $acdPath)
    if ($UnsafeSkipDependencyCheck) { $argList += "--unsafe-skip-dependency-check" }

    $result = & $L5xGitPath @argList 2>&1
    $exitCode = $LASTEXITCODE
    $fileSw.Stop()
    $fileSeconds = [math]::Round($fileSw.Elapsed.TotalSeconds, 1)
    $fileTimes += $fileSeconds
    $mtime = $f.LastWriteTimeUtc.ToString("o")

    if ($exitCode -eq 0) {
        "$($f.FullName),$acdPath,ok,,$mtime" | Out-File -FilePath $logPath -Append -Encoding utf8
        Write-Host "  ok (${fileSeconds}s)"
    } else {
        $msg = ($result -join " ") -replace ",", ";"
        "$($f.FullName),$acdPath,FAILED,$msg,$mtime" | Out-File -FilePath $logPath -Append -Encoding utf8
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
