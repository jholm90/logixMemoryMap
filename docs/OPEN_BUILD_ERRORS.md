# Open Build / Conversion Errors

First pass 2026-08-25, worked through while l5x→acd conversion was running.
Every item from *that pass* has since been either root-caused and fixed, or
confirmed as a scope decision (Safety) rather than a bug.

**The claim that once stood here — "nothing currently needs a new error
code" — was wrong, and is corrected below (2026-09-10).** It was written
without running the cross-reference that would have tested it. A
systematic pass of every committed `samples/generated/**/*.L5X` against
the last recorded status per filename in `samples/convert_log.csv` finds
**59 committed files whose last record is FAILED**, and thirty of them are
a module family that had never been surfaced in any batch summary. (That
figure was correct on 2026-09-10; it is 41 as of 2026-09-11 — see the
dated status block below, which is the one to read.)

The lesson is the process one: a conversion-failure list assembled from
what someone reports is not the same as one assembled from the log, and
only the second kind can be trusted. This file is now regenerated from
`convert_log.csv`, never from recollection.

## Status as of 2026-09-11

Re-run against the current `convert_log.csv` (5,296 rows) and the current
committed tree (2,783 files), matching on filename with the LAST row per
file winning, so a later success supersedes an earlier failure:

| | count |
|---|---|
| committed `samples/generated/**/*.L5X` | 2,783 |
| last record `ok` | 2,682 |
| last record FAILED | **40** |
| no conversion record at all | **60** |

**40, down from 59.** The batch converted a large part of what was
outstanding. What is left splits cleanly:

- **39 of the 40 share one error**, `XMLSrv_E_IMPORT_ABORTED_NO_CHANGES`,
  which names nothing on its own — it only says the import was refused and
  to read Studio's own error log. These are the `modulesweep_*` safety and
  4-connection variants, the `predefprobe_ref_to_*` reference probes, and
  `modulerack_bender_full_program`, all already tracked below.
- **The 40th is new in this batch and is already fixed.**
  `daxis_axis_cip_drive.L5X` failed 2026-09-11 with a controller named
  `DaxAxCIP_` — a trailing underscore, from `"AXIS_CIP_DRIVE"[5:9]`, a
  fixed slice landing on the underscore. Regenerated as `DaxAxCIPD` and
  the whole class is now impossible to reintroduce: `validate_logix_name`
  refuses to build one and the lint rule checks every element carrying a
  Name plus the export header's TargetName. **Needs re-submitting.**
Of the **60 with no record at all**, 51 are new and simply awaiting their
first run — the 27 `pioconn_*`/`pioname_*` POINT I/O files and the 24
`udtmn_*` member-name files, both built 2026-09-11. The remaining **nine
are not new and have never been submitted even once** — see "No conversion
record at all" below; they have been in that state since 2026-09-10.

Two different failure stages, kept separate below:
- **L5X→ACD conversion failure** — the `l5x2acd` tool couldn't even open
  the project (fails before any build/verify step runs).
- **Build/verify error** — the project opened fine, but Studio 5000's own
  verify step reported N errors on import/build.

## All fixed, awaiting recapture

**`stringoverhead_namelen32_n050.L5X`** — L5X→ACD conversion failure
- Real cause: a double underscore in a tag name, which Logix forbids.
- Root cause confirmed: the name-length padding filler
  (`"_LONGNAME" * k`, truncated to hit an exact target length) happened to
  end in `_` right where it abuts the tag's own `_NN` numeric suffix, at
  `pad_needed mod 9 == 1` — 32 is the only one of the 5 name lengths
  tested (4/8/16/32/40) where that remainder occurs.
- Fixed in 3 places sharing the same filler-truncation pattern (`cli.py`'s
  `_padded_tag_name`, `gen_string_tagoverhead.py` and
  `gen_string_batch2.py`'s namelen groups) — all now guard against a
  trailing `_`, swapping it for a non-underscore character so the exact
  requested length is still hit. Regenerated, lint-clean.

**`axis_aoi_inout_1_instance.L5X`** / **`axis_full_combo.L5X`** —
build/verify errors (2 each)
- Real cause: the AOI declares the instance tag and the InOut as
  required/visible, but the calling routine passes
  `tagName,FaultResetVal,Axis_Cip_Drive` — the third argument has nowhere
  to go. A call site needs exactly as many arguments as the definition has
  required parameters.
- Root cause confirmed: the AOI's BOOL Input param (`FaultReset`) was
  declared with `Required=False/Visible=False` (hidden — real semantics:
  no slot on the calling rung at all), but the rung text wired
  `FaultResetVal` into it anyway.
- Fixed by marking `FaultReset` `Required=True/Visible=True` in
  `gen_axis_composite.py` (both files share the exact same bug, both
  fixed together) — keeps the call-site wiring as originally intended.
  Regenerated, lint-clean; stale `actual_bytes`/`error_count` from the
  broken version cleared from the manifest so they don't read as current.

**`motioninstr_mam_n00010`/`_n00100`, `motioninstr_maj_n00010`/`_n00100`,
`motioninstr_mas_n00010`/`_n00100`, `motioninstr_mrp_n00010`/`_n00100`**
(8 files) — build/verify errors, `error_count` == rung count (every rung
failed)
- Real cause: motion instructions need all their parameters populated. The
  call was `MAM(Axis_Cip_Drive,MotionInstr1)`, missing the rest.
- Root cause confirmed: the bare 2-operand call these 4 used is MAH/MSO's
  own real shape, not theirs. Reading the real corpus directly confirmed
  four genuinely different real operand counts: MAM=20, MAJ=17, MAS=9,
  MRP=5.
- Fixed in `gen_motion_instructions.py`: MAM uses the corrected
  template verbatim; MAJ/MAS/MRP built as position-for-position
  transplants from one real corpus example each (same method as the MAPC
  fix below), real keywords/literals kept verbatim, only tag names
  substituted. MAH/MSO's own call is untouched. All 12 files regenerated,
  lint-clean, stale error data cleared from the manifest.

**`instrfirst_mapc_x10`** — 20 errors (2/rung × 10 rungs)
- Real cause, matching the one found independently: the axis tag
  `Axis_Cip_Drive` was never declared in the file, and the same axis tag
  was reused for both master and slave — an axis cannot cam to itself.
  The axis-type constraint is looser than first assumed: MAPC accepts two
  axes of any type (virtual master with virtual slave is fine); it only
  needs two distinct tags, not a CIP-Drive/Virtual pairing.
- Fixed in `instrfirst_mapc_v2`/`_v2_x10` (generated, lint-clean,
  awaiting capture). Original buggy files kept for the audit trail.

## Resolved, not a bug

**`instrfirst_crout_x10`** — 80 errors (8/rung × 10 rungs)
- Real cause: needs a safety processor. CROUT is
  a Safety-only instruction (GuardLogix CPU required), this project's
  test corpus is all standard controllers. Reclassified OUT OF SCOPE
  alongside DCS. Nothing to fix, nothing to retest on a standard
  controller.


## Open conversion failures, from convert_log.csv (2026-09-10)

Every committed generated file whose LAST recorded status is FAILED. A
later success supersedes an earlier failure, so these are current, not
historical. 57 of the 59 report the same generic
`XMLSrv_E_IMPORT_ABORTED_NO_CHANGES` — that is the import refusing as a
whole, not a diagnosis, and it does not distinguish these causes from one
another.

### Already tracked elsewhere (36 files)

| files | where |
|---|---|
| `daxis_*` (8), `mbshape_axis_k3` | OQ-AXISINOUT — axis passed as an AOI InOut |
| `predefprobe_*` (18) | Caused by the scalar-`DataValue` structure-tag bug fixed in `c85fab5`; regenerated, awaiting recapture |
| `modulesweep_2198_*_ers3_variant_4conn` (10) | OQ-MODULEIO, and see the corrected `-ERS3` diagnosis — not a safety-controller mismatch, a missing XML block |

### Not previously recorded anywhere (11 files)

These appear in no document and in no batch summary. Cause is **not
established**, and no fix is claimed here.

| file | notes |
|---|---|
| `modulesweep_5069_ib16_a` | |
| `modulesweep_5069_iy4_a` | |
| `modulesweep_5069_ob16_a` / `_a_r2` / `_b` / `_b_r2` | |
| `modulesweep_5069_ib8s_a` | safety-rated catalog |
| `modulesweep_5069_obv8s_a` | safety-rated catalog |
| `modulesweep_powerflex_527_sto_cip_safety` / `_r2` | CIP Safety |
| `modulerack_bender_full_program` / `_r2` | verbatim real donor modules |

The tempting hypothesis is that the safety-rated catalogs fail because
they sit on a plain non-safety controller. **That exact hypothesis has
already been wrong once** — it was the original diagnosis for the 2198
`-ERS3` failures, and it was disproved by `composite_realistic_v4_001`
through `_031`, which carry `-ERS3` drives on a plain 1756-L81E with no
`SafetyLevel` at zero errors. It is not asserted again here, and it does
not explain `5069_ib16`, `5069_iy4` or `5069_ob16` at all, none of which
are safety catalogs.

**What is needed:** the raw Studio 5000 error-log line for one 5069
`modulesweep` file and one `modulerack_bender_full_program`. The generic
import-aborted message cannot distinguish a bad slot, an unsupported
catalog, a missing XML block, or a connection-config mismatch, and
guessing between those has already cost one wrong diagnosis. The AHK
capture harness now records the error-log text into the manifest's
`error_log` column, so a recapture of these eleven files will carry the
real line without anyone reading it off a screen.

### No conversion record at all

`composite_realistic_{10,11,22,32,34,36,46,47,48}_r2` — nine committed
files with no row in `convert_log.csv` in either direction. They were
never converted, rather than converted and failed. Lint flags real defects
in several (`safety_module_on_non_safety_controller` on 10/11/34,
`duplicate_module_slot` and `non_sequential_module_slots` on 22/34), so
these need the lint findings cleared and then a first conversion attempt.

Awaiting first capture, not failures: the 40 `alarmdef_*`, 4 `fwmatrix_v38_1756_l9*`,
and the 77 `csarrbase_*`/`csarrcount_*`/`csarrmaxlen_*`/`strarrcount_*`
files built for OQ-CSARRAYBASE and OQ-STRARRAYLARGEN.


## The 21-file failure list, resolved 2026-09-11

Three distinct causes, none of which the generic
`XMLSrv_E_IMPORT_ABORTED_NO_CHANGES` message distinguished.

### Repaired: 8 axis files (generator bug, now impossible to reintroduce)

`daxis_axis_{cip_drive,servo,virtual}`, `daxis_axisn_k{1,2,3}`,
`daxis_full`, `mbshape_axis_k3`.

Every one declared its axis as `Usage="Input"`:

    <Parameter Name="Drive_Axis" DataType="AXIS_CIP_DRIVE"
               Usage="Input" Radix="Decimal" .../>

An AOI Input/Output Parameter is passed BY VALUE and Logix accepts only an
atomic type there. Anything structured -- a UDT, a nested AOI, a STRING, an
AXIS_* -- must be `Usage="InOut"`, which passes a reference. The `Radix` on
a structure is wrong for the same reason a structure tag never carries one.

Fixed in `builders.py`, which now RAISES on a structure Input parameter at
build time, next to the existing guard for array Input parameters that was
found the same way. Both generators updated to route structures through
`inout_params=`. All 30 axis-family files regenerate lint-clean.

### Deleted: 12 alarm-definition files (superseded, and defective)

`alarmdef_{l81,l902ts}_{inst,noinst}_t{01,04,16}`.

They carried the structure-tag bug fixed in `c85fab5` -- a UDT-typed tag
emitted as a scalar `<DataValue>` with a `Radix`:

    <Tag Name="AlarmSrc00" DataType="AlarmSrcType" Radix="Decimal">
      <Data Format="Decorated"><DataValue DataType="AlarmSrcType" .../></Data>

which is why exactly the files declaring a tag failed while the ones with
none converted. None carried a capture, all were off the platform standard
(v38, or a 1756-L9x), and `alarmdef_l81_v35_{inst,noinst}_t*` already
replaces them correctly. A scan confirms the 12 were the only files in the
batch still carrying the defect.

### REPAIRED 2026-09-11: modulerack_kinetix_full_bus

Rebuilt on **1756-L83E, no safety**. The section below records why the
previous attempt concluded this was impossible, and why that conclusion
was wrong -- both halves of its reasoning failed.

The E_INVALIDARG was the 1756-L85ES ProductCode, a guess this project
already records elsewhere as "fails on line 1 of the l5x".

The claim that a non-safety -ERS3 shape "needs config data captured from
a real non-safety module, which this project does not have" was false
when it was written. The 2conn module blocks this rack uses were donated
by BaillieLeitchField_Edger_20260812_r00.L5X -- a **1756-L83E, a plain
non-safety controller** -- and every one already carries
SafetyEnabled="false". The config was in the corpus the whole time; the
note simply never checked the donor.

L83E rather than L81E for the one part that did hold: three dual-axis
drives plus two power supplies do not fit an L81E's 3 MB. L83E is the
smallest standard catalog with the headroom, and is what the donor runs.
It is a named exemption in the platform-standard lint rule, with that
reason recorded beside it.

### Superseded: the earlier "cannot be repaired" finding

Its topology is already correct -- byte-for-byte the same parent/port shape
as the `composite_realistic_v4_*` files that convert clean. The blocker is
the processor: it is built on 1756-L85ES, and `gen_fw_catalog_matrix.py`
records that catalog's ProductCode as a guess that "fails on line 1 of the
l5x", which is exactly the `E_INVALIDARG` seen here.

The obvious fix is not available either. The generator's own note explains
why it chose L85ES: three dual-axis drives plus two power supplies do not
fit an L81E's 3 MB, and the -ERS3 blocks it emits carry safety connections
and safety config, which a non-safety controller rejects. A non-safety
-ERS3 shape is buildable -- a real 2198-D057-ERS3 runs on a non-safety
1756-L82E in the field -- but it needs config data captured from a real
non-safety module, which this project does not have.

NOT deleted, because it holds the only capture for this shape (230,896
bytes). That capture is contaminated: it was taken at error_count=4, so it
is not a usable fitting point either. It is kept as a record rather than
as data, and the file stays off the platform standard until one of the two
missing inputs arrives.
