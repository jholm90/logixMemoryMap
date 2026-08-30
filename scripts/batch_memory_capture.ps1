<#
.SYNOPSIS
  Fully unattended now (2026-08-22 rewrite #2, James: "I did a file|open and
  was able to open one of your generated files in less than 5s, as opposed
  to the 65s to do the close LogixDesigner/reOpen every time" -- 5s vs 65s
  across 500+ files is the whole ballgame). PowerShell no longer launches a
  new process per file (Start-Process, ~65s close/reopen cycle) -- it hands
  AHK the next ACD path to open via -OpenRequestPath, and AHK drives Studio
  5000's own File > Open (Ctrl+O) to switch files inside the SAME already-
  running instance. No Read-Host prompts anywhere in the loop anymore --
  this can run overnight against the full 500+ file corpus unattended.

  Two small handoff files carry the conversation, in opposite directions:
    -OpenRequestPath   PowerShell -> AHK.  This script writes the next ACD
                       path here; AHK waits for it, opens the file, deletes
                       the request (consumed) once read.
    -HandoffPath        AHK -> PowerShell. AHK overwrites this with
                       error_count,warning_count,message_value,ocd_value,
                       window_title once its build/verify/Capacity-read
                       cycle finishes for whatever file it just opened;
                       this script polls for it (see -TimeoutSeconds),
                       reads, deletes it (consumed), and logs. window_title
                       is cross-checked against the requested filename --
                       a mismatch is logged loudly and flagged in the
                       row's own notes rather than trusted quietly. A
                       literal "0" ocd_value is treated the same way
                       (2026-08-27) -- a real Capacity reading is never
                       actually 0, so a 0 read is a bad-read symptom, not
                       real data; flagged ZERO CAPACITY and auto-retried
                       next run, never silently counted.

  Per file:
    1. Write the ACD path to -OpenRequestPath.
    2. Poll for -HandoffPath to appear (up to -TimeoutSeconds -- build time
       scales with file size, so this is generous by default). Timeout logs
       a warning and asks once whether to retry/skip/stop rather than
       hanging forever or silently giving up.
    3. Read + delete -HandoffPath, log ocd_value as actual_bytes plus the
       new error_count/warning_count/message_value columns, matched by
       l5x_path against the row the sample generator already wrote (so
       predicted_bytes stays put).

  Never reuses a stale handoff: both files are cleared before being
  requested/waited on, so a leftover result from a previous run or a
  skipped file can't silently get attributed to the wrong row (see James's
  whole session today re: don't trust data that hasn't been validated).

  Resumable: Ctrl+C at any point loses nothing -- already-logged l5x_path
  rows are skipped on the next run, and nothing is written until a row is
  actually complete.

.PREREQS
  Run batch_l5x_to_acd.ps1 first; this script consumes its convert_log.csv.
  Your AHK script must be running, with a loop that: waits for
  -OpenRequestPath to appear, reads+deletes it, opens that path via Ctrl+O
  in the existing Logix Designer window, does its build/verify/Capacity
  read, then writes -HandoffPath (header + one data row:
  error_count,warning_count,message_value,ocd_value,window_title) before
  looping back to wait for the next request.

  ManifestPath/HandoffPath/OpenRequestPath all default to locations relative
  to this script's own folder (scripts\ahk_runtime\ for the two handoff
  files -- gitignored, never committed), so the common case needs none of
  them typed out. logix_build_capture.ahk's HANDOFF_PATH/OPEN_REQUEST_PATH
  constants must point at the exact same two paths -- update them once and
  you're done, no more copy-pasting a path into two places every run.

.EXAMPLE
  # Smoke test on the first 10 files before committing to a full run:
  ./batch_memory_capture.ps1 -ConvertLog C:\l5x_scratch\acd\convert_log.csv `
      -ControllerModel "5069-L306ER" -FirmwareRev "35.11" -Limit 10

  # Full run, same command without -Limit:
  ./batch_memory_capture.ps1 -ConvertLog C:\l5x_scratch\acd\convert_log.csv `
      -ControllerModel "5069-L306ER" -FirmwareRev "35.11"
#>
param(
    [Parameter(Mandatory = $true)][string]$ConvertLog,
    [string]$ManifestPath = (Join-Path $PSScriptRoot "..\samples\manifest.csv"),
    [Parameter(Mandatory = $true)][string]$ControllerModel,
    [Parameter(Mandatory = $true)][string]$FirmwareRev,
    [string]$HandoffPath = (Join-Path $PSScriptRoot "ahk_runtime\ahk_handoff.csv"),
    [string]$OpenRequestPath = (Join-Path $PSScriptRoot "ahk_runtime\open_request.txt"),
    [int]$TimeoutSeconds = 1200,
    [int]$Limit
)

New-Item -ItemType Directory -Force -Path (Split-Path $HandoffPath -Parent) | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $OpenRequestPath -Parent) | Out-Null

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

$ManifestColumns = "sample_id,description,category,l5x_path,predicted_bytes,actual_bytes,delta,delta_pct," +
    "controller_model,firmware_rev,date_tested,notes,error_count,warning_count,message_value,window_title"

if (-not (Test-Path $ManifestPath)) {
    $ManifestColumns | Out-File -FilePath $ManifestPath -Encoding utf8
}
$manifest = @(Import-Csv $ManifestPath)
$alreadyLogged = @{}
# James, 2026-08-25: "any test that fails for window title mismatch should
# be rerun... make sure you can rerun those tests next time without me
# prompting you." A row flagged WINDOW TITLE MISMATCH or (2026-08-27)
# ZERO CAPACITY in notes still has actual_bytes populated (with data that
# may belong to a different file, or may just be a bad "0" read -- see
# the checks below), so without this exclusion it would silently count as
# "already logged" forever. Excluding it here means it's treated as
# never-captured and gets picked back up automatically the very next time
# this script runs against the same $ConvertLog -- no ACD rebuild needed,
# since convert_log.csv already has status=ok for it (only the capture
# READ was suspect, not the conversion).
$manifest | Where-Object { $_.actual_bytes -and ($_.notes -notmatch 'WINDOW TITLE MISMATCH|ZERO CAPACITY') } |
    ForEach-Object { $alreadyLogged[$_.l5x_path] = $true }
$mismatchFlagged = @{}
$manifest | Where-Object { $_.notes -match 'WINDOW TITLE MISMATCH|ZERO CAPACITY' } |
    ForEach-Object { $mismatchFlagged[$_.l5x_path] = $true }

$rows = Import-Csv $ConvertLog | Where-Object { $_.status -eq "ok" }
$remaining = $rows | Where-Object { -not $alreadyLogged.ContainsKey((Get-RelPath $_.l5x_path)) }
if ($Limit -gt 0) { $remaining = $remaining | Select-Object -First $Limit }
$retryCount = @($remaining | Where-Object { $mismatchFlagged.ContainsKey((Get-RelPath $_.l5x_path)) }).Count
Write-Host "$($rows.Count) converted sample(s) in log; $($alreadyLogged.Count) already logged; $($remaining.Count) remaining this pass ($retryCount of those are window-title-mismatch/zero-capacity retries)."

# James, 2026-08-30: list every file before starting, not just the count --
# a batch review before committing to a long capture run, same reasoning as
# batch_l5x_to_acd.ps1's equivalent listing.
if ($remaining.Count -gt 0) {
    Write-Host ""
    Write-Host "Files to capture this pass ($($remaining.Count)):"
    $n = 0
    foreach ($row in $remaining) {
        $n++
        $retryTag = if ($mismatchFlagged.ContainsKey((Get-RelPath $row.l5x_path))) { " [RETRY]" } else { "" }
        Write-Host ("  [{0}/{1}] {2}{3}" -f $n, $remaining.Count, (Get-RelPath $row.l5x_path), $retryTag)
    }
    Write-Host ""
}

Write-Host "Ctrl+C at any time -- already-logged rows are skipped on the next run."
Write-Host "Make sure your AHK script is already running and waiting before this starts."

# Stale files from a previous run (or a skipped file) shouldn't get
# attributed to the first file of this run -- start clean.
if (Test-Path $HandoffPath) { Remove-Item $HandoffPath -Force }
if (Test-Path $OpenRequestPath) { Remove-Item $OpenRequestPath -Force }

$total = $remaining.Count
$idx = 0
$stopRequested = $false
$fileTimes = @()
$batchSw = [System.Diagnostics.Stopwatch]::StartNew()
foreach ($row in $remaining) {
    if ($stopRequested) { break }
    $idx++
    $relPath = Get-RelPath $row.l5x_path
    $meta = Get-SampleIdAndDescription $row.l5x_path
    $category = Get-Category $row.l5x_path
    $existing = $manifest | Where-Object { $_.l5x_path -eq $relPath } | Select-Object -First 1
    $fileSw = [System.Diagnostics.Stopwatch]::StartNew()

    Write-Host ""
    Write-Host "=== [$idx/$total] $($meta.Id) : $($meta.Desc) [$category] ==="
    Write-Host "Requesting AHK open: $($row.acd_path)"
    Set-Clipboard -Value $row.acd_path  # AHK pastes this into the Open dialog (^v) instead of typing it
    $row.acd_path | Out-File -FilePath $OpenRequestPath -Encoding utf8 -NoNewline  # existence = "go" signal; content is a fallback if you'd rather FileRead than paste

    $blocksUsed = $null
    $errorCount = ""
    $warningCount = ""
    $messageValue = ""

    $elapsed = 0
    $pollInterval = 2
    while ($elapsed -lt $TimeoutSeconds) {
        if (Test-Path $HandoffPath) { break }
        Start-Sleep -Seconds $pollInterval
        $elapsed += $pollInterval
    }

    if (-not (Test-Path $HandoffPath)) {
        Write-Warning "Timed out after ${TimeoutSeconds}s waiting on AHK for $($meta.Id) -- check Studio 5000/AHK manually."
        $resp = Read-Host "'r' to retry waiting on this same file, 's' to skip it, anything else/Enter to stop"
        if ($resp -eq 'r') {
            # Leave the open request in place and just go around again with a fresh wait.
            $elapsed = 0
            while ($elapsed -lt $TimeoutSeconds) {
                if (Test-Path $HandoffPath) { break }
                Start-Sleep -Seconds $pollInterval
                $elapsed += $pollInterval
            }
        }
        if (-not (Test-Path $HandoffPath)) {
            if ($resp -ne 's') { $stopRequested = $true }
            if (Test-Path $OpenRequestPath) { Remove-Item $OpenRequestPath -Force }
            continue
        }
    }

    Start-Sleep -Milliseconds 300  # let AHK's write fully flush before reading
    $handoff = Import-Csv $HandoffPath
    if (-not $handoff -or $handoff.Count -eq 0 -or [string]::IsNullOrWhiteSpace($handoff[0].ocd_value)) {
        Write-Warning "Handoff for $($meta.Id) was empty/incomplete -- skipping this file, check AHK."
        Remove-Item $HandoffPath -Force -ErrorAction SilentlyContinue
        continue
    }

    $result = $handoff[0]
    $blocksUsed = $result.ocd_value
    $errorCount = $result.error_count
    $warningCount = $result.warning_count
    $messageValue = $result.message_value
    $windowTitle = $result.window_title
    Remove-Item $HandoffPath -Force  # consumed -- next file must produce a fresh one

    # Independent cross-check (James, 2026-08-22: "window title is valid
    # there with the filename.acd present inside") -- the title AHK
    # captured at read-time should contain the file PowerShell requested.
    # Real title format confirmed 2026-08-22 doesn't include the .ACD
    # extension ("Logix Designer - array_dint_00001 [1756-L81E 35.11]*"),
    # so match on the base name only -- checking for the extension too
    # was producing false-positive mismatches. A real mismatch means the
    # automation may have read stale data (confirmed real case, same day:
    # a request for array_dint_00005 came back with array_dint_00002 still
    # in the title -- the file switch silently didn't happen) -- still
    # logged rather than silently dropped, but flagged loudly and in the
    # row's own notes so it's never trusted quietly.
    $expectedFileName = [System.IO.Path]::GetFileNameWithoutExtension($row.acd_path)
    $notes = ""
    if ($windowTitle -notmatch [regex]::Escape($expectedFileName)) {
        Write-Warning "Window title mismatch for $($meta.Id): expected '$expectedFileName' in `"$windowTitle`" -- may have captured the wrong file's data."
        $notes = "WINDOW TITLE MISMATCH: expected '$expectedFileName', got `"$windowTitle`""
    }
    # James, 2026-08-27: "if memory size is 0 it needs to be flagged and
    # not counted." A real controller's Capacity-tab reading is never
    # actually 0 (every project carries the empty_project_baseline floor
    # at minimum) -- a "0" read is a bad-read symptom (wrong dialog/field
    # focused, a timing glitch), not a real data point, but it would
    # otherwise pass the blank-check above and silently log as valid.
    # Same treatment as WINDOW TITLE MISMATCH: flagged loudly, and
    # excluded from "already logged" below so it's automatically retried
    # next run, no manual re-flagging needed.
    if ($blocksUsed -eq "0") {
        Write-Warning "Capacity read as 0 for $($meta.Id) -- almost certainly a bad read, not a real value. Flagging, not counting."
        $notes = if ($notes) { "$notes; ZERO CAPACITY: read as 0, not a real value, not counted" } else { "ZERO CAPACITY: read as 0, not a real value, not counted" }
    }
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
        $existing.error_count = $errorCount
        $existing.warning_count = $warningCount
        $existing.message_value = $messageValue
        $existing.window_title = $windowTitle
    } else {
        $manifest += [pscustomobject]@{
            sample_id = $meta.Id; description = $meta.Desc; category = $category; l5x_path = $relPath
            predicted_bytes = ""; actual_bytes = $blocksUsed; delta = $delta; delta_pct = $deltaPct
            controller_model = $ControllerModel; firmware_rev = $FirmwareRev; date_tested = $date; notes = $notes
            error_count = $errorCount; warning_count = $warningCount; message_value = $messageValue
            window_title = $windowTitle
        }
    }
    $manifest | Export-Csv -Path $ManifestPath -NoTypeInformation -Encoding utf8
    $fileSw.Stop()
    $fileSeconds = [math]::Round($fileSw.Elapsed.TotalSeconds, 1)
    $fileTimes += $fileSeconds
    Write-Host "Logged: ${fileSeconds}s Actual_Bytes=$blocksUsed errors=$errorCount Warnings=$warningCount Message=$messageValue Title=$windowTitle"
}

$batchSw.Stop()
Write-Host ""
if ($fileTimes.Count -gt 0) {
    $avgSeconds = [math]::Round((($fileTimes | Measure-Object -Average).Average), 1)
    $totalMinutes = [math]::Round($batchSw.Elapsed.TotalMinutes, 1)
    Write-Host "Batch: $($fileTimes.Count) file(s) logged, ${totalMinutes}min total, avg ${avgSeconds}s/file."
}
Write-Host "Done for now."

# Auto-push (James, 2026-08-20: "so i dont have to ask").
. (Join-Path $PSScriptRoot "_autopush.ps1")
$repoRoot = Split-Path $PSScriptRoot -Parent
Push-RepoFile -RepoRoot $repoRoot -FilePath $ManifestPath -CommitMessage "Log real memory capture + build/verify results"

# James, 2026-08-30: "the ahk file is my file and i edit it when i want and
# dont want any side effects" -- same reasoning as batch_l5x_to_acd.ps1's
# equivalent block. No-op if unchanged this run.
$ahkPath = Join-Path $repoRoot "scripts\logix_build_capture.ahk"
if (Test-Path $ahkPath) {
    Push-RepoFile -RepoRoot $repoRoot -FilePath $ahkPath -CommitMessage "Update AHK capture script"
}
