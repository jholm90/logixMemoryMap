# Shared by batch_l5x_to_acd.ps1 and batch_memory_capture.ps1. Results
# should never need copy/pasting out of PowerShell by hand, so
# both scripts push straight to the repo instead. Dot-source this file, then
# call Push-RepoFile.
#
# Straight to main, no branches/merges -- commits local results FIRST (so
# they're safe in a commit, not sitting as uncommitted changes), then
# rebases that commit onto origin/main (linear history, no merge commit)
# before pushing. Committing before syncing matters: if a commit lands on
# origin/main while a long batch run is in progress (real
# case: a doc/sample push arrived mid-53-file-run), the file being pushed
# is uncommitted right up until this point, and syncing against a dirty
# working tree fails every time. Committing first avoids that.
# A real rebase conflict aborts cleanly and says so rather than leaving
# things mid-rebase.

# NOTHING CONFIDENTIAL LEAVES THIS MACHINE. Both push functions stage, then call
# this before committing. A staged path is refused when it is under samples/local/,
# under any folder named Customer or PROGRAMS, or is a project file (.L5X, .L5K,
# .ACD, .zip, .7z) that no generator wrote: its name is not a non-real sample_id
# in samples/manifest.csv. On a refusal nothing is committed or pushed and the
# index is reset; the working tree is untouched.
#
# Drawn after a capture run swept 23 customer programs, dropped into
# samples/generated/Customer/ to be converted, onto the public repository:
# Push-AllChanges staged everything untracked and only .gitignore stood in the way.
function Get-ConfidentialStaged {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)
    $generatedIds = @{}
    $manifestPath = Join-Path $RepoRoot "samples\manifest.csv"
    if (Test-Path $manifestPath) {
        Import-Csv $manifestPath | Where-Object { $_.category -ne 'real_program' } |
            ForEach-Object { $generatedIds[$_.sample_id] = $true }
    }
    $refused = @()
    # The two result logs are committed, and a row names its file: a new row for a
    # file no generator wrote puts a real program's name, window title and error
    # text into a public file. Every added line must name a manifest sample.
    $knownIds = @{}
    if (Test-Path $manifestPath) { Import-Csv $manifestPath | ForEach-Object { $knownIds[$_.sample_id] = $true } }
    # The STAGED file is parsed as CSV, not its diff read line by line: a multi-line field
    # (a build error log) puts lines in the diff that are no row's start, and feeding their
    # text to a path function threw "Illegal characters in path" and stopped the commit.
    foreach ($log in @('samples/captures.csv', 'samples/convert_log.csv')) {
        if (-not (git diff --cached --name-only -- $log)) { continue }
        $staged = (git show ":$log") -join "`n"
        $key = if ($log -like '*captures.csv') { 'sample_id' } else { 'l5x_path' }
        foreach ($row in @($staged | ConvertFrom-Csv)) {
            $first = [string]$row.$key
            if (-not $first) { continue }
            $id = ($first -replace '\\', '/') -replace '^.*/', '' -replace '\.[^.]*$', ''
            if (-not $knownIds.ContainsKey($id)) { $refused += "${log}: row for '$id'" }
        }
    }
    foreach ($path in @(git diff --cached --name-only --diff-filter=ACMR)) {
        $q = $path -replace '\\', '/'
        if ($q -like 'samples/local/*' -or $q -match '(^|/)(Customer|PROGRAMS)/') { $refused += $q; continue }
        if ($q -match '\.(l5x|l5k|acd|zip|7z)$') {
            $id = [System.IO.Path]::GetFileNameWithoutExtension($q)
            if (-not $generatedIds.ContainsKey($id)) { $refused += $q }
        }
    }
    return ,$refused
}

function Test-SafeToCommit {
    param([Parameter(Mandatory = $true)][string]$RepoRoot)
    $refused = Get-ConfidentialStaged -RepoRoot $RepoRoot
    if ($refused.Count -eq 0) { return $true }
    git reset -q
    Write-Host ""
    Write-Host "NOT COMMITTED, NOT PUSHED: $($refused.Count) staged file(s) are not generated test files." -ForegroundColor Red
    Write-Host "Real exports belong in samples\local\ (git-ignored), never under samples\generated\." -ForegroundColor Red
    $refused | Select-Object -First 20 | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    Write-Host "Move them out (or delete the copies there), then rerun. Nothing was lost: the index was reset, files are untouched." -ForegroundColor Red
    return $false
}

function Push-RepoFile {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string]$CommitMessage
    )

    $fileFull = (Resolve-Path $FilePath).Path
    Push-Location $RepoRoot
    try {
        $dirty = git status --porcelain -- $fileFull
        if (-not $dirty) {
            Write-Host "No changes to push for $FilePath."
            return
        }

        git add $fileFull
        if (-not (Test-SafeToCommit -RepoRoot $RepoRoot)) { return }
        git commit -m $CommitMessage *>$null

        git fetch origin main *>$null
        git rebase origin/main *>$null
        if ($LASTEXITCODE -ne 0) {
            git rebase --abort *>$null
            Write-Host "Rebase onto origin/main hit a real conflict -- not auto-pushing. Your results are safe in a local commit. Resolve manually: 'git rebase origin/main', fix conflicts, 'git rebase --continue', then 'git push origin main'."
            return
        }

        git push origin main
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Pushed."
        } else {
            Write-Host "Push failed -- run 'git push origin main' manually."
        }
    } finally {
        Pop-Location
    }
}

# the push must cover ALL files in the project directory,
# broader than Push-RepoFile's one-file-at-a-time scope.
# Stages and pushes EVERYTHING dirty in the working tree (git add -A,
# not just tracked files -- new/untracked files get swept in too), one
# commit, same fetch/rebase/push-to-main mechanism as Push-RepoFile.
# Respects .gitignore, and Test-SafeToCommit refuses the whole commit if anything
# staged is not a generated test file (see above) -- .gitignore alone was not
# enough. Otherwise there is no per-file review step: whatever is dirty when this
# runs gets committed and pushed, without you choosing file-by-file. If you're mid-edit on something you don't want pushed
# yet, commit/stash it separately (or gitignore it) before running a
# batch script, since this no longer asks first.
function Push-AllChanges {
    param(
        [Parameter(Mandatory = $true)][string]$RepoRoot,
        [Parameter(Mandatory = $true)][string]$CommitMessage
    )

    Push-Location $RepoRoot
    try {
        $dirty = git status --porcelain
        if (-not $dirty) {
            Write-Host "No changes to push."
            return
        }

        git add -A
        if (-not (Test-SafeToCommit -RepoRoot $RepoRoot)) { return }
        git commit -m $CommitMessage *>$null

        git fetch origin main *>$null
        git rebase origin/main *>$null
        if ($LASTEXITCODE -ne 0) {
            git rebase --abort *>$null
            Write-Host "Rebase onto origin/main hit a real conflict -- not auto-pushing. Your results are safe in a local commit. Resolve manually: 'git rebase origin/main', fix conflicts, 'git rebase --continue', then 'git push origin main'."
            return
        }

        git push origin main
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Pushed."
        } else {
            Write-Host "Push failed -- run 'git push origin main' manually."
        }
    } finally {
        Pop-Location
    }
}
