# Shared by batch_l5x_to_acd.ps1 and batch_memory_capture.ps1 (James,
# 2026-08-20: "i dont want to copy/paste from powershell everytime" -- both
# scripts push their results straight to the repo so Claude can read them
# without a manual paste). Dot-source this file, then call Push-RepoFile.
#
# Straight to main, no branches/merges -- ff-only pull first so a push never
# turns into a merge commit; if local main has diverged, it stops and says
# so rather than doing anything automatic about that case.

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

        git fetch origin main *>$null
        git merge --ff-only origin/main *>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Local main has diverged from origin/main -- not auto-pushing. Resolve manually, then commit/push $FilePath yourself."
            return
        }

        git add $fileFull
        git commit -m $CommitMessage *>$null
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
