<#
.SYNOPSIS
  Clears actual_bytes (and delta/delta_pct/date_tested/notes) for a specific
  list of manifest.csv rows so the next batch_memory_capture.ps1 run
  re-prompts for exactly those, and skips everything already good.

  James, 2026-08-21: found via cross-checking the pushed results --
    - 3 rows with a garbled actual_bytes value ("dgrade[", not a number) --
      likely an AutoHotkey mis-fire during the unattended run.
    - 1 row never got a value entered at all (nested_udt_array_member).
    - aoi_deepnest3_def_only / aoi_deepnest3_1_instance: def_only shows
      MORE memory than the 1-instance version, which is impossible --
      adding an instance can only add memory, never remove it. Looks
      swapped between the two prompts.
    - aoi_realistic_composite_1_instance and _10_instance_array are
      byte-for-byte identical, which isn't plausible (predicted jump alone
      is 128->1280 bytes for going from 1 instance to a 10-element array)
      -- a stuck/duplicate paste. aoi_nested_array_localtag_1_instance
      shares that same suspicious value, so it's cleared too even though
      James only flagged two -- cheap to re-verify rather than assume
      coincidence.

.EXAMPLE
  ./reset_discrepancies.ps1 -ManifestPath ..\samples\manifest.csv
#>
param(
    [Parameter(Mandatory = $true)][string]$ManifestPath
)

$toReset = @(
    "nested_udt_scalar",
    "array_of_nested_udt_100",
    "customstring_len2000",
    "nested_udt_array_member",
    "aoi_deepnest3_def_only",
    "aoi_deepnest3_1_instance",
    "aoi_realistic_composite_1_instance",
    "aoi_realistic_composite_10_instance_array",
    "aoi_nested_array_localtag_1_instance"
)

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
