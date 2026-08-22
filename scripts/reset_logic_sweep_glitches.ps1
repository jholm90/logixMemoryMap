<#
.SYNOPSIS
  Clears actual_bytes (and delta/delta_pct/date_tested/notes) for the 32
  logic_instr rows flagged from the 244-file capture batch, so the next
  batch_memory_capture.ps1 run re-prompts for exactly those.

  James, 2026-08-22, "add those 32 rows to the next test":
    - instr_equ_n00100, instr_cmp_n00010: garbled "dgrade[" value, same
      AutoHotkey mis-fire pattern seen before.
    - CPS, COP, FLL, SIZE, BTD, T_ADD (5 counts each = 30 rows): all 5
      count-points for each of these 6 instructions read back the exact
      same value (22,944) regardless of rung count -- looks like the
      capture script got stuck on a stale dialog reading for a contiguous
      stretch of the run. Also worth double-checking T_ADD is the intended
      mnemonic (not a real Rockwell instruction as far as we know) when
      re-running gen_logic_sweep.py's INSTRUCTIONS dict.

.EXAMPLE
  ./reset_logic_sweep_glitches.ps1 -ManifestPath ..\samples\manifest.csv
#>
param(
    [Parameter(Mandatory = $true)][string]$ManifestPath
)

$stuckInstructions = @("cps", "cop", "fll", "size", "btd", "t_add")
$counts = @("00010", "00050", "00100", "01000", "05000")

$toReset = @("instr_equ_n00100", "instr_cmp_n00010")
foreach ($instr in $stuckInstructions) {
    foreach ($n in $counts) {
        $toReset += "instr_${instr}_n${n}"
    }
}

$rows = Import-Csv $ManifestPath
$cleared = 0
foreach ($row in $rows) {
    if ($toReset -contains $row.sample_id) {
        $row.actual_bytes = ""
        $row.delta = ""
        $row.delta_pct = ""
        $row.date_tested = ""
        $row.notes = ""
        $cleared++
        Write-Host "Cleared: $($row.sample_id)"
    }
}

if ($cleared -ne $toReset.Count) {
    Write-Warning "Expected to clear $($toReset.Count) rows, actually cleared $cleared -- check sample_id spelling against manifest.csv."
}

$rows | Export-Csv -Path $ManifestPath -NoTypeInformation -Encoding utf8
Write-Host "`nDone. Re-run batch_memory_capture.ps1 -- these $cleared row(s) will be re-prompted, everything else is skipped as usual."
