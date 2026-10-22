# Build and Conversion Failures

Sample files that do not convert or do not build, and the diagnostic rules for
dealing with them.

**Regenerate this file from `samples/convert_log.csv`, never from recollection.**
A failure list assembled from what someone reports is not the same as one
assembled from the log, and only the second can be trusted. The command is
`python scripts/conversion_status.py`.

---

## Current status

Matched on filename against the log with the **last row per file winning**, so a
later success supersedes an earlier failure:

| | count (2026-10-22) |
|---|---:|
| committed generated L5X | 522 (written-up batches are deleted; CLAUDE.md) |
| last status `ok` | 519 |
| last status FAILED | **3** — batch A, below |
| no conversion record | 0 |

**Three conversion failures and eight build-error rows open, all from batch A** (below);
earlier batches had none open. The `_r3` rebuilds of 2026-10 captured with zero errors and
OQ-BUILDFAIL-OPEN is closed.

### Batch A, 2026-10-21

Three files never converted and eight built with errors; each is flagged against its
question (`scripts/capture_errors.py`, exit 0).

| file | stage | Studio message | cause | enforced by / next |
|---|---|---|---|---|
| `safe_io6_5069_ob16_1`, `safe_io6_5069_mix_2_2` | import (retried 2026-10-21, same) | XMLSrv_E_IMPORT_ABORTED_NO_CHANGES | the 5069-OB16/B module-sweep block has no ExtendedProperties ConfigID (every compiled export carries 711 packed on a controller's bus, 110 in a rack); the IB16/A block imported without one | `module_without_configid`; `gen_safety_round6.std_card` adds it; **rebuilt 2026-10-22** (batch B), awaiting conversion |
| `safe_sil2_5069l320s3_n00` | import (retried, same) | XMLSrv_E_IMPORT_ABORTED_NO_CHANGES | **unknown** — the same catalog at SIL3 converts; the converter log carries only the abort | not needed (the SIL3 files read exact without it); dropped from batch B unless the Studio error-log line arrives |
| `strx_equ_elem`, `_equ_member`, `_equ_vidx`, `strx_neq_member` | build, 400 errors each | Rung n, OTE, Operand 0: Invalid bit specifier | each result written to `SuC[i].R.0`, a bit of a REAL; none of the 400 rungs reached the controller (each reads 16 below `strx_n00`) | `bit_specifier_on_real`; **rebuilt 2026-10-22 as `strx_*_r2`** writing `SuC[i].D.0`, a bit of the DINT member (inventory unchanged), awaiting conversion |
| `stshape_aoi_n00`, `_assign400`, `_if200`, `_param400` | build, 1 error each | Rung 0: Missing output instruction | the call rung is an AOI with no visible output alone on a rung | not rebuilt: AOI-internal ST is under the floor (TASKS 0zd) |
| `safe_iol_kx_d012_std_1` / `_2` | build, 2 / 4 errors | Primary Bus Sharing Group 3 … Shared DC with no Shared AC/DC | the proven non-safety D012 block's bus-sharing setting | reading equals the other D0xx controls'; used for no law |

The capture tool once stored a status line as a Capacity value
(`safe_sil3_step`: "Read 1769 series Edit8 OCD value: …"), which stopped every loader that
parses it. It now refuses a non-numeric reading (`CAPACITY NOT NUMERIC`, retried next run),
and `load_manifest()` treats one as uncaptured.

### Build errors from an earlier batch

Three files converted and then failed Build. Causes, now enforced by lint:

| file | Studio error | enforced by |
|---|---|---|
| `almd_minimal_r2`, `almd_realtext_r2` | *Rung 0, ALMD: Invalid number of arguments for instruction* | `native_instruction_arg_count` |
| `modulerack_kinetix_full_bus_r2` | *Tag '<drive>:SI': Invalid data type for safety tag* (from the original's log; the `_r2` log was truncated) | `kinetix_drive_missing_configid`, `scripts/check_proven_blocks.py` |

---|---:|---|
| `modname_p208_len*` | 12 | OQ-MODULENAMELEN |
| `rungpack_{xic,equ}_k*` | 12 | OQ-RUNGSHAPE |
| `composite_realistic_*_r3` | 9 | composite instrument; lint defects of the `_r2` builds cleared |
| `jsrcallers_k*` | 6 | OQ-JSRCALLERBASE |
| `alarmcond_realcount_n*` | 4 | OQ-ALARMCONDREAL |
| `litop_bool_*_n01000_r2` | 4 | OQ-LITERALOPERAND BOOL arm |
| `almd_minimal_r2`, `almd_realtext_r2` | 2 | OQ-BUILDFAIL-OPEN re-trigger |
| `eventtask_axiswatch_r2` | 1 | OQ-BUILDFAIL-OPEN re-trigger |
| `modulerack_kinetix_full_bus_r2` | 1 | OQ-BUILDFAIL-OPEN re-trigger, converter axes fixed |
| `instrfirst_mapc_v2_x100` | 1 | MAPC third point |

The four re-triggers exist to have their Studio error log recorded; the capture
harness writes it into the `error_log` column.

---

## Two distinct failure stages

Keep these separate. They have different causes and different evidence.

| stage | meaning |
|---|---|
| **L5X → ACD conversion failure** | The tool could not open the project. Fails before any build or verify step runs. |
| **Build / verify error** | The project opened fine, but Studio's verify step reported N errors. The capture may still record a byte figure — which is of an **incomplete** project and is therefore suspect. |

---

## The diagnostic rules

Each of these is the generalisation of a failure that cost real time.

### 1. Check stale-versus-genuine before reading a single error message

    the file's last write time   vs   the row's capture date

**If the L5X was regenerated after the capture, the recorded errors were against a
version that no longer exists.** In one audit 72 of 138 error rows were exactly
that. Diagnosing any of them as a live bug would have been chasing a ghost.

### 2. A generic import-abort message is not a diagnosis

`XMLSrv_E_IMPORT_ABORTED_NO_CHANGES` means the import was refused. It does not
distinguish causes, and files failing for completely unrelated reasons all report
it identically. **Do not group files by that message and assume one cause.**

### 3. The safety-controller hypothesis has been wrong before

The tempting explanation for a safety-rated catalog failing is that it sits on a
plain non-safety controller.

**That exact hypothesis was the original diagnosis for the 2198-ERS3 failures, and
it was disproved** — dozens of composite files carry ERS3 drives on a plain
1756-L81E with no `SafetyLevel` at zero errors. It also failed to explain several
non-safety 5069 catalogs failing alongside them.

Do not assert it again without the error text.

### 4. Check the donor before concluding data is missing

One rack was recorded as unrepairable because a non-safety ERS3 shape "needs
config data captured from a real non-safety module, which this project does not
have."

**That was false when it was written.** The module blocks that rack uses were
donated by a real export running a plain non-safety 1756-L83E, and every one
already carries `SafetyEnabled="false"`. The config was in the corpus the whole
time; the note simply never checked the donor.

### 5. A guessed ProductCode fails on line 1

The same rack's real blocker was its processor: a 1756-L85ES whose ProductCode was
a guess. A guessed catalog identifier produces `E_INVALIDARG` at the very start of
the file, which looks nothing like a content problem.

Rebuilding on a real catalog fixed it. L83E rather than L81E for the one part of
the original reasoning that did hold: three dual-axis drives plus two power
supplies do not fit an L81E's 3 MB.

**A wrong ProductCode can also read as a missing port.** The first `safe_*` batch
(2026-10-17) failed conversion on every file with *"required property 'port' was
missing"* at the Local module's `</Ports>`: `build_l5x` had no code for 1756-L81ES and
fell back to the 1756-L81E's 164, while GuardLogix 5580 is numbered apart (L81ES 211).
Studio's own re-export of one file showed the single change. `build_l5x` now refuses a
1756 catalog it has no code for, and lint's `local_module_product_code` refuses a Local
module whose code is not its catalog's.

### 6. Conversion success does not mean the program compiles

The SDK only opens and parses. It performs no ladder verification. A file with a
missing array subscript on an array-typed operand **converts cleanly and never
builds at scale** — which is why every affected instruction came back at an
identical byte count regardless of rung count.

### 7. A platform or firmware no capture has built is checked against a real export first

Before safety round 4 (TASKS 0x) went out, its first files on 5069 safety controllers and
on 1756-L81ES v32 / v34 were compared, structure only, with the real safety exports of
the same catalog and firmware: controller attributes, Local module and its ports,
`SafetyInfo`, `EthernetPorts`, every module by catalog, revision and parent port, the tag
map and its tags, and the safety AOI definitions and instances. Four defects that no
capture could have shown, because no generated file had used these shapes before:

| defect | real shape | fix |
|---|---|---|
| 5069-L320ERMS2 Local module ProductCode 223 (the L330ERMS2's, by default) | 222 | `build_l5x` refuses a 5069 catalog it has no code for; lint `local_module_product_code` refuses one with no confirmed code |
| 1734-AENTR/C revision 7 at v32 and v34 | 6 in the one real v32 1756-L81ES; 7 only at v35 | the v32 / v34 bases carry 6, which has also built at v35 (`rack_pointio_*`) |
| a 5069 listing one embedded Ethernet port, labelled `1` | A1 and A2, both enabled, in all 7 real 5069 exports (v31 to v35) | `build_l5x` writes the pair for every 5069 |
| a mapped standard tag with no `Class` | `Class="Standard"` on every standard controller tag of a real safety project | `safe_map_*` writes it on its 200 standard tags |

A 5069's Local ports depend on its EtherNet/IP mode: Dual-IP has 1, 3 and 4, and every
real Dual-IP program puts its Ethernet modules on 4; Linear/DLR has 1 and 2. A module on a
port its parent lacks does not import ("No port was found with the given port number"),
and lint `parent_port_missing` now refuses it. No real export trips it (23 checked), and
neither does any generated file on disk.

`safe_lock_trial` (SafetyLocked="true" with no signature) was withdrawn before handover:
every real locked export (8 of 8) carries a safety signature, so the shape has no
compiled precedent. Locking is measured from a Studio-made variant instead (TASKS 0x).

---

## Root causes found and fixed, kept as a reference

These are the failure classes that have actually occurred. Each is now prevented
at build time rather than caught after a capture run.

### Invalid identifier names

Logix rejects a name that **ends in an underscore, contains two consecutive
underscores, or starts with a digit** — with "Invalid name." and an aborted
import. One bad name costs the entire file. **A name equal to an expression
function or operator, in any case, fails too:** the safety array `SIn` was
rejected as an invalid tag name (it is SIN) and took all seven `safe_std_*` files
with it. `validate_logix_name` and lint refuse the whole set
(`builders.RESERVED_EXPRESSION_NAMES`).

Both real instances came from a helper composing a name out of parts, which is
exactly the case a generator author cannot see by reading their own call site:

- A name-length padding filler ending in `_` right where it abutted a numeric
  suffix.
- A fixed slice of a type name, `"AXIS_CIP_DRIVE"[5:9]`, landing on the
  underscore.

**Now impossible to reintroduce.** `validate_logix_name` refuses to build one, and
it runs on every name entering a file — tags, programs, routines, tasks, modules,
UDT members, AOI parameters, and the controller itself, whose own name is written
twice and was the one thing nothing checked.

### A structure as an AOI Input parameter

**An AOI Input or Output parameter is passed by value, and Logix accepts only an
atomic type there.** Anything structured — a UDT, a nested AOI, a STRING, an
AXIS_* — must be `Usage="InOut"`, which passes a reference. A `Radix` on a
structure is wrong for the same reason a structure tag never carries one.

`builders.py` now raises on a structure Input parameter at build time, beside the
existing guard for array Input parameters that was found the same way.

### A call site wiring a hidden parameter

**A call site needs exactly as many arguments as the definition has parameters
with a slot.** A parameter declared `Required="false" Visible="false"` is hidden —
it has no slot on the calling rung at all — so wiring a value into it gives that
argument nowhere to go.

### A structure-typed tag emitted as a scalar DataValue

    <Tag Name="AlarmSrc00" DataType="AlarmSrcType" Radix="Decimal">
      <Data Format="Decorated"><DataValue DataType="AlarmSrcType" .../>

A UDT-typed tag needs a `Structure` body, not a scalar `DataValue`, and carries no
`Radix`. This is why exactly the files declaring such a tag failed while the ones
with none converted.

### Motion instructions need their full parameter list

The bare two-operand `(Axis, MotionInstruction)` call is **MAH and MSO's own real
shape, not a general motion shape.** Real operand counts differ per instruction:
MAM 20, MAJ 17, MAS 9, MRP 5.

Each is now a position-for-position transplant from a real example, real keywords
and literals kept verbatim, only tag names substituted.

### MAPC needs two distinct axis tags

An axis cannot cam to itself. The axis-type constraint is looser than first
assumed: **any two axis types work** — virtual master with virtual slave is fine —
it only needs two distinct tags, not a CIP-Drive/Virtual pairing.

### An array-typed operand needs a subscript

Real Rockwell syntax always requires `[index]`, and `SIZE` needs `.DATA[0]` on its
STRING operand. See rule 6 above for why this survives conversion.

---

## Out of scope, not bugs

**Safety-family instructions require a safety CPU** — CROUT, DCS, ROUT, ESTOP,
RIN. There is nothing to fix on a standard controller and nothing to retest.

**Invented alarm condition types.** Four were guessed and all four were rejected.
The alarm `ConditionType` dropdown list is still needed from Studio. **This is the
canonical example of why guessing between plausible causes is not allowed here.**
