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

  Staleness-aware, content-hash-based (2026-08-23, third version same
  week -- see git history on this file for the two that didn't work).
  v1 tracked convert_log.csv rows with no time info at all -> real Build
  errors against pre-fix .ACD binaries that never got reconverted. v2
  switched to comparing each L5X's LastWriteTimeUtc against its own
  .ACD's mtime -- fixed v1's bug, but broke on the next `git reset --hard`:
  git NEVER preserves file mtimes across checkout/reset/pull (fundamental
  git behavior, not a bug in this repo) -- every file git had to write
  during that reset got "now" stamped on it regardless of whether its
  real content changed, so 336 files came up stale when only 15 actually
  were. James: "this is not fast 50s per file.. 500 minutes is a very
  long time."

  v3: track a SHA256 content hash per converted file in convert_log.csv
  instead of any timestamp. A file is stale only if its current hash
  doesn't match what was recorded when its .ACD was last produced --
  immune to git resets, pulls, checkouts, and clocks, since it only cares
  about actual bytes. Cost: rows converted under v1/v2 have no hash on
  file, so by default they're treated as needing reconversion once (same
  "forced full pass" problem as before) -- see -AdoptExisting below to
  avoid paying that cost when you already know nothing actually changed.

.PARAMETER AdoptExisting
  One-time migration helper. For any file that already has a .ACD on
  disk but no recorded hash in the log (i.e. converted under v1/v2),
  don't reconvert it -- just record its current hash as the trusted
  baseline and move on. Use this the FIRST time you run v3, after
  deleting the .ACD for any file you already know is genuinely stale (a
  real generator fix landed today) so it isn't wrongly adopted as good.
  Every run after that first one, omit this switch -- hash comparison
  alone is enough from then on, permanently, since hashes never get
  reset by git.

.PREREQS
  - Studio 5000 Logix Designer + Logix Designer SDK 2.2+ installed
  - l5xgit.exe built from https://github.com/RockwellAutomation/ra-logix-designer-vcs-custom-tools
    (dotnet build against .NET 10 SDK) and either on PATH or passed via -L5xGitPath

.EXAMPLE
  # First run after upgrading to this version (adopts everything already
  # converted instead of paying for a full reconvert):
  ./batch_l5x_to_acd.ps1 -InputDir ..\samples\generated -OutputDir C:\l5x_scratch\acd -AdoptExisting

  # Every run after that:
  ./batch_l5x_to_acd.ps1 -InputDir ..\samples\generated -OutputDir C:\l5x_scratch\acd
#>
param(
    [Parameter(Mandatory = $true)][string]$InputDir,
    [Parameter(Mandatory = $true)][string]$OutputDir,
    [string]$L5xGitPath = "l5xgit",
    [switch]$UnsafeSkipDependencyCheck,
    [switch]$AdoptExisting
)

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
$logPath = Join-Path $OutputDir "convert_log.csv"
$canonicalHeader = "l5x_path,acd_path,status,message,l5x_hash"

if (Test-Path $logPath) {
    # A log from v1/v2 has an l5x_mtime header instead -- Import-Csv names
    # columns off the header line, so leaving it as-is would mean every
    # newly-appended hash value silently gets read back as $null forever
    # under the old "l5x_mtime" property name. One-time migration: keep
    # l5x_path/acd_path/status/message, blank out the old (now-meaningless
    # mtime) 5th column rather than pretend it's a real hash, rewrite with
    # the correct header.
    $firstLine = Get-Content -Path $logPath -TotalCount 1
    if ($firstLine -ne $canonicalHeader) {
        Write-Host "Migrating $logPath to hash-tracked format (one-time)..."
        $oldRows = Import-Csv $logPath
        $migrated = $oldRows | ForEach-Object {
            [pscustomobject]@{ l5x_path = $_.l5x_path; acd_path = $_.acd_path; status = $_.status; message = $_.message; l5x_hash = "" }
        }
        $canonicalHeader | Out-File -FilePath $logPath -Encoding utf8
        foreach ($r in $migrated) {
            "$($r.l5x_path),$($r.acd_path),$($r.status),$($r.message),$($r.l5x_hash)" | Out-File -FilePath $logPath -Append -Encoding utf8
        }
    }
} else {
    $canonicalHeader | Out-File -FilePath $logPath -Encoding utf8
}

# Keyed by l5x_path -> the recorded content hash at last successful
# conversion. Rows from before this version (no l5x_hash column) simply
# won't have an entry here.
$recordedHash = @{}
Import-Csv $logPath | Where-Object { $_.status -eq "ok" -and $_.l5x_hash } | ForEach-Object { $recordedHash[$_.l5x_path] = $_.l5x_hash }

Write-Host "Hashing $InputDir ..."
$allFiles = Get-ChildItem -Path $InputDir -Filter *.L5X -Recurse
$currentHash = @{}
foreach ($f in $allFiles) {
    $currentHash[$f.FullName] = (Get-FileHash -Path $f.FullName -Algorithm SHA256).Hash
}

# Files this pass actually needs to run through l5xgit for.
$files = $allFiles | Where-Object {
    $acdPath = Join-Path $OutputDir ($_.BaseName + ".ACD")
    if (-not (Test-Path $acdPath)) { return $true }  # never converted -- needs it
    $recorded = $recordedHash[$_.FullName]
    if (-not $recorded) { return -not $AdoptExisting }  # no hash on file -- reconvert to be safe, unless adopting
    return $recorded -ne $currentHash[$_.FullName]  # true if the content actually changed
}

# Files -AdoptExisting is trusting as-is: has a .ACD, no recorded hash,
# and we're choosing not to reconvert it. Logged with the current hash
# so every run after this one compares against real content, no
# reconversion involved here at all.
$adopted = @()
if ($AdoptExisting) {
    $adopted = $allFiles | Where-Object {
        $acdPath = Join-Path $OutputDir ($_.BaseName + ".ACD")
        (Test-Path $acdPath) -and (-not $recordedHash[$_.FullName])
    }
}

$upToDateCount = $allFiles.Count - $files.Count - $adopted.Count
Write-Host "Found $($allFiles.Count) L5X file(s) under $InputDir; $upToDateCount already converted and up to date; $($adopted.Count) adopted as-is (no reconversion); $($files.Count) to convert this pass."
Write-Host "Press any key at any time to stop cleanly after the current file (resume later by re-running)."

if ($adopted.Count -gt 0) {
    foreach ($f in $adopted) {
        $acdPath = Join-Path $OutputDir ($f.BaseName + ".ACD")
        "$($f.FullName),$acdPath,ok,adopted-existing,$($currentHash[$f.FullName])" | Out-File -FilePath $logPath -Append -Encoding utf8
    }
    Write-Host "Adopted $($adopted.Count) existing .ACD file(s) into the hash-tracked log without reconverting."
}

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
    # environment). Deleting the old file first removes the question.
    if (Test-Path $acdPath) { Remove-Item $acdPath -Force }

    $argList = @("l5x2acd", "--l5x", $f.FullName, "--acd", $acdPath)
    if ($UnsafeSkipDependencyCheck) { $argList += "--unsafe-skip-dependency-check" }

    $result = & $L5xGitPath @argList 2>&1
    $exitCode = $LASTEXITCODE
    $fileSw.Stop()
    $fileSeconds = [math]::Round($fileSw.Elapsed.TotalSeconds, 1)
    $fileTimes += $fileSeconds
    $hash = $currentHash[$f.FullName]

    if ($exitCode -eq 0) {
        "$($f.FullName),$acdPath,ok,,$hash" | Out-File -FilePath $logPath -Append -Encoding utf8
        Write-Host "  ok (${fileSeconds}s)"
    } else {
        $msg = ($result -join " ") -replace ",", ";"
        "$($f.FullName),$acdPath,FAILED,$msg,$hash" | Out-File -FilePath $logPath -Append -Encoding utf8
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
