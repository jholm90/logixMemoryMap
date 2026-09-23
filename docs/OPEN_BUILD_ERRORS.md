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

| | count |
|---|---:|
| committed generated L5X | 3,583 |
| last status `ok` | 3,580 |
| last status FAILED | **0** |
| no conversion record at all | **3** |

**No conversion failures.** The 52-file batch converted in full and captured 49 clean.

### The 3 with no record

| file | question |
|---|---|
| `almd_minimal_r3`, `almd_realtext_r3` | OQ-BUILDFAIL-OPEN — the real 5-operand ALMD form |
| `modulerack_kinetix_full_bus_r3` | OQ-BUILDFAIL-OPEN — rebuilt only from blocks with zero-error captures |

### Build errors from the last batch

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

### 6. Conversion success does not mean the program compiles

The SDK only opens and parses. It performs no ladder verification. A file with a
missing array subscript on an array-typed operand **converts cleanly and never
builds at scale** — which is why every affected instruction came back at an
identical byte count regardless of rung count.

---

## Root causes found and fixed, kept as a reference

These are the failure classes that have actually occurred. Each is now prevented
at build time rather than caught after a capture run.

### Invalid identifier names

Logix rejects a name that **ends in an underscore, contains two consecutive
underscores, or starts with a digit** — with "Invalid name." and an aborted
import. One bad name costs the entire file.

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
