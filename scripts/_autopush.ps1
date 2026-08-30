# Shared by batch_l5x_to_acd.ps1 and batch_memory_capture.ps1 (James,
# 2026-08-20: "i dont want to copy/paste from powershell everytime" -- both
# scripts push their results straight to the repo so Claude can read them
# without a manual paste). Dot-source this file, then call Push-RepoFile.
#
# Straight to main, no branches/merges -- commits local results FIRST (so
# they're safe in a commit, not sitting as uncommitted changes), then
# rebases that commit onto origin/main (linear history, no merge commit)
# before pushing. Committing before syncing matters: if a commit lands on
# origin/main while a long batch run is in progress (2026-08-20, real
# case: a doc/sample push arrived mid-53-file-run), the file being pushed
# is uncommitted right up until this point, and syncing against a dirty
# working tree fails every time. Committing first avoids that.
# A real rebase conflict aborts cleanly and says so rather than leaving
# things mid-rebase.

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

# James, 2026-08-30: "you should cover ALL files in that project
# directory" -- broader than Push-RepoFile's one-file-at-a-time scope.
# Stages and pushes EVERYTHING dirty in the working tree (git add -A,
# not just tracked files -- new/untracked files get swept in too), one
# commit, same fetch/rebase/push-to-main mechanism as Push-RepoFile.
# Still respects .gitignore (git add -A never adds an ignored path), so
# this project's own no-proprietary-L5X-in-git rule (CLAUDE.md) still
# holds as long as real customer exports stay gitignored like they're
# supposed to -- but there is no per-file review step here: whatever is
# dirty when this runs gets committed and pushed, without you choosing
# file-by-file. If you're mid-edit on something you don't want pushed
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
