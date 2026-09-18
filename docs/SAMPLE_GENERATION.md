# Sample Generation

Need a repeatable, scriptable way to produce the 30-40+ test L5X files without
hand-clicking each one in Studio 5000.

## Open question first (OQ-GENMETHOD)

L5X is just XML, so it's mechanically generatable — the real question is
whether Logix Designer's File→Import will accept hand-built XML cleanly, or
whether it needs GUIDs/checksums/schema quirks that make raw authoring
unreliable. **First sample generated should go straight through the full
TESTING_PLAN.md loop (import → compile → download) before writing a generator
for the other 29+.** If import fails or requires manual fixup, pivot to one of
the fallback approaches below rather than fighting hand-authored XML.

## Approach A — Direct XML authoring (preferred if OQ-GENMETHOD confirms it works)

Template-based generation: a script takes parameters (element count, data
type, nesting depth, instruction type, rung count) and emits valid L5X XML
matching Rockwell's schema for that content type. Fastest iteration — no
Studio 5000 UI automation needed, just XML templates + a parameter sweep.

Needs, at minimum:
- Tag element template (name, data type, dimensions)
- DataType (UDT) template (name, members list)
- AddOnInstructionDefinition template
- Rung/Routine template (instruction text, comments)
- A minimal-but-valid Controller wrapper (the boilerplate every L5X needs:
  controller element, single empty task/program/routine, RSLogix5000Content
  root with correct SchemaRevision/SoftwareRevision matching OQ-L5XVERSION)

## Approach B — Studio 5000 automation (fallback if raw XML import is unreliable)

Logix Designer has a COM/.NET automation interface. A C# script (fits existing
toolchain — same pattern as the WinForms V36 converter) could programmatically
create tags/UDTs/logic in an open project, which sidesteps any raw-XML
schema-fidelity problems since Logix Designer itself generates the L5X on
export. Slower per-sample (UI automation overhead) but guaranteed valid.

## Approach C — Hybrid

Generate the bulk structure via Approach A (fast), but if any sample fails to
import cleanly, hand-fix that one sample in Studio 5000 UI and re-export as the
template for that category going forward. Practical middle ground — don't
over-invest in perfecting the XML generator for edge cases that hit once.

## Naming / organization

- `samples/generated/<category>/<sample_id>_<short_desc>.L5X`
- Every generated sample gets a row in `samples/manifest.csv` at creation time
  (predicted_bytes filled in immediately from the tool's own calculation;
  actual_bytes filled in after the TESTING_PLAN.md loop runs)
- Keep generator scripts in `src/sample_gen/` so a sample can be regenerated
  exactly (not hand-edited and drifted from its own generator)

**Generator CLI built 2026-08-20** — builds L5X files for whatever needs
testing:
`python -m sample_gen.cli {udt,tags,rungs} ...` -- see that module's
docstring for exact flags. `udt` builds a UDT + one tag of it (matches the
now-confirmed BOOL-packing-run rule exactly, see OQ-ALIGN); `tags` builds N
tags of a given type/dimensions; `rungs` builds N rungs of an instruction
pattern with an optional filler comment (OQ-COMMENTS). All three write the
L5X, compute predicted_bytes via this project's own sizing engine, and log
a manifest.csv row automatically -- actual_bytes stays blank until run
through `scripts/batch_l5x_to_acd.ps1` + `scripts/batch_memory_capture.ps1`
(both resumable, "press any key to stop" / "close the window at any time"
per the spec) or manually through Studio 5000.

## Feedback loop shape

```
generate sample → predict bytes (this tool) → import/download (Studio 5000)
→ read actual bytes → log to manifest → diff → adjust MEMORY_MODEL.md
→ re-predict all prior samples with new constants → confirm no regressions
```

That last step matters — a constant tuned to fix sample #12 can silently break
the prediction for sample #4. Re-run the full manifest's predicted-vs-actual
comparison after every constant change, not just the sample that prompted it.

## Before hand-picking catalogs into any script (including one-off chat samples)

2026-09-03: two real Studio 5000 errors that were both **already
diagnosed and fixed elsewhere in this codebase** before being rebuilt from
scratch by hand: (1) `193-ECM-ETR/A` used directly in a scratch sample --
already in `gen_composite_realistic.py`'s `_UNDIAGNOSED_COMPOSITE_CATALOGS`
exclusion set with a documented real "Child module incompatible with
parent module" error; the response was to delete it from
`_MODULE_CHAINS` entirely. (2) Several real 5069 Compact I/O catalogs
combined onto the default 1756-L81E non-safety controller -- `gen_module_
sweep.py` already documents (2026-08-27) that 5069 modules need
`_5069_PROCESSOR_TYPE = "5069-L306ER"` (a 5069-series processor, not
1756-L81E -- `Type="5069"` Ports only match a 5069 controller's own local
bus) and that 2 of the 6 (`_5069_SAFETY_CATALOGS`) are
`SafetyEnabled="true"`, needing `5069-L306ERMS2` (safety-rated). The
requirement: read each module and verify that safety-rated hardware cannot
be placed on a non-safety processor.

**Before writing ANY script that picks catalogs by name** (`_MODULE_CHAINS`
keys, `_5069_*`, `_UNDIAGNOSED_*`, etc.), grep this file's own generators
for that catalog first -- an existing exclusion set, a dedicated processor-
type constant, or a safety-catalog set means the question is already
answered. `sample_gen.lint.lint_l5x` now also catches the safety case
mechanically (`safety_module_on_non_safety_controller`, checks every
Module's own `SafetyEnabled="true"` against the file's `<SafetyInfo>`
presence) -- run it on every generated file before sending it anywhere,
scratch chat samples included, not just committed batches.

## After fixing a generator bug: the committed files don't fix themselves

2026-09-04, caught via `batch_l5x_to_acd.ps1` output showing
files still queued for conversion that had already been reported fixed.
Real gap found: `gen_module_pointio_rack.py`'s Bus Size/slot-resize
fix landed in the generator SOURCE (2026-09-03), and a direct in-memory
test of the fixed function was reported as verification -- but the
actual COMMITTED `rack_pointio_n02...n07_full/_alt` files in `samples/
generated/` were never regenerated afterward. They still had the old,
pre-fix content (last touched by an earlier commit), so they kept showing
`FAILED`/never-logged in `convert_log.csv` -- not because the fix was
wrong, but because the shipped files never picked it up. A code fix is not
done until `python -m sample_gen.<module>` has actually been re-run and the
resulting file diff committed -- verifying the FUNCTION in isolation is not
the same as verifying the FILE that ships. Same session, a parallel check
on `cipmodule_scale_*.L5X` (also flagged in the same PowerShell output)
found the opposite: regenerating changed nothing but the export timestamp
-- that fix had already made it into the committed files; the file was
just sitting on a stale, never-retried `FAILED` log entry from before the
fix landed. Distinguishing these two cases (stale FILE vs. stale LOG
entry) needs an actual regeneration + diff, every time -- not an assumption
either way.

## Build a real-scale batch out of already-proven rung text

2026-09-04, on the first real virgin-file miss, against a 12% error:

The batch that answers a real-scale question has to actually BUILD at real
scale, and this project has already spent one whole batch learning that the
hard way. `jsr_target_content_scale_*` was built to answer exactly the
JSR-target-content question, used its own hand-rolled instruction mix over
its own hand-rolled tag pool, and came back with 5/26/50/75 build errors —
so all four rows are invalid fitting points and the question stayed open
for four more days. The cause of those specific errors is still genuinely
undiagnosed; do not claim otherwise without a real Studio 5000 error-log
line.

`gen_realscale_surcharge.py` (2026-09-04) is built the other way round, and
this is the pattern to copy for any future large batch:

- **Take the rung text verbatim from `gen_logic_sweep.INSTRUCTIONS` and the
  tag pool verbatim from its `_POOL_TAGS_XML`.** That shape has an
  error-free build on record at 5,000 rungs (the whole `instr_*_n05000`
  sweep) and at 27,267 rungs (`randommix_05_n27267rungs_23types`,
  `error_count` 0). Nothing in a new batch should re-invent an operand
  shape that a valid capture already proves.
- **Pick counts that PAIR with existing valid captures.** Five of the eight
  files in its JSR ladder use exactly `gen_logic_sweep.COUNTS`
  (10/50/100/1000/5000), so each one differs from an existing error-free
  row by one deliberate change — the rungs sit behind a JSR instead of in
  MainRoutine — and the answer falls out as a paired difference with no
  model in between. A ladder that shares no count with the existing corpus
  throws that away.
- **If the proven shape ALSO errors in the new placement, that is the
  result**, not a setback: it isolates the placement as what Studio 5000
  objects to, which no existing row can distinguish today.

## SBR is a condition, not an output -- every rung still needs a terminator

2026-09-04, real Studio 5000 failure on `jsr_paramtype_udt_n*_r00100`: an
SBR rung with no output instruction fails to build. SBR behaves like a
comparison and needs an output after it, so SBR rungs are generated with a
trailing `NOP()`.

`SBR` only RECEIVES the caller's parameters. It has no effect of its own, so
a rung containing nothing but `SBR(...)` has nothing terminating it and
Studio 5000 rejects it — **exactly** like a bare `EQU`, and with the same
fix:

```
SBR(P0,P1,P2)NOP();     <- correct
SBR(P0,P1,P2);          <- rejected, no output instruction
```

`RET();` on its own rung is fine — RET is a real output, not a condition.
Structured Text is also exempt: ST has no rungs and no output-instruction
rule, and the real corpus carries bare `SBR( a, b, c );` ST statements
(44 of them) that build clean.

**The lesson is about where a rule lives, not about SBR.** This project
already knew it — `lint.py`'s `_rung_missing_output_findings` was written in
August for exactly this class, off the *"conditional instructions like
EQU with no operand at the end of the rung"*. `SBR` simply was not in
`_PURE_CONDITION_INSTRUCTIONS`, so 8 of the 9 generators that emit an SBR
got the `NOP()` right **by convention** and the 9th silently did not. A rule
enforced by convention across nine copies is a rule that will be broken by
the tenth. When a build-validity rule turns up, add it to `lint.py` — a
comment in the generator you happen to be editing does not protect the
others.


## Logix identifier rules — a hard requirement, on everything

**Every** name in the file, with no exceptions: tags, programs, routines,
tasks, modules, UDT members, AOI parameters, local tags, data types, the
**controller/processor name** and the export header's `TargetName`.

- **No trailing underscore.** `InParam00___` fails with "Error creating
  'Parameter' (Invalid name.)".
- **No sequential underscores.** `Bad__Name` fails the same way.
- **No leading digit.**

Pad a name to a target length with filler LETTERS, never underscores.

Enforced in two places, deliberately:

- `builders.validate_logix_name` refuses to BUILD an illegal name.
  `MemberSpec` validates in `__post_init__`, so every member, parameter
  and local tag is covered by one hook; `tag_xml`, `udt_xml`,
  `aoi_xml`, `program_xml`, `task_xml`, `custom_string_type_xml`,
  `string_array_tag_xml`, `program_tag_xml`, `alias_tag_xml` and
  `build_l5x`'s `target_name` each check their own.
- `lint.py`'s `invalid_logix_name` check scans **every element with a
  `Name` attribute**, plus the header's `TargetName`, on every file. The
  one exemption is `<Version Name="1.1">` on an AOI revision, which is a
  version string rather than an identifier — established by scanning all
  3.6M `Name` attributes across the 80 real exports, where it is the only
  name that breaks these rules and still imports.

This has now been hit three times, and each of the first two fixes was
applied only inside the generator that failed:

- 2026-08, a string name-length batch.
- 2026-09-06, a padding helper that filled names to an exact length with
  underscores, breaking 52 of 56 files in one batch.
- 2026-09-11, `daxis_axis_cip_drive` shipped a controller named
  `DaxAxCIP_` — `"AXIS_CIP_DRIVE"[5:9]`, a fixed slice landing on the
  underscore. The lint rule existed by then and did not catch it, because
  it walked a hand-maintained list of ten element tags and `<Controller>`
  was not one of them. That list is gone; the rule is universal.

Every instance came from a name COMPOSED out of parts, which is exactly
what a generator author cannot see by reading their own call site. That is
why the build-time guard exists alongside the lint check.

## Racks: bus size and slot numbers are properties of the rack, not the module

Module blocks in this project are copied verbatim from real exports. That is
deliberate and it is what makes them import cleanly -- but a real module
carries two values that belong to the application it came from, not to the
rack being built:

- its **bus size**, which is the size of that plant's rack, and
- its **slot address**, which is where it happened to be installed.

An OB8E found at slot 8 in one application is not an OB8E that must live at
slot 8. Next application it may be slot 2. Both values have to be recomputed
by the generator; inheriting them is how a one-card rack ends up declaring
fourteen slots.

**Fixed backplanes -- 1756 (`Port Type="ICP"`).** The slot count is a
property of the physical chassis catalog: 4, 10, 13 or 17 slots. An
under-populated 1756 chassis is a normal design, not a defect, and is never
flagged.

**Dynamic backplanes -- Point I/O (`PointIO`), Flex, and 5069.** There is no
physical chassis; the bus is exactly as long as what is plugged into it. The
bus coupler occupies one position and each card occupies one more, so a
correctly generated rack declares the SMALLEST size that fits:

    Bus Size = 1 (coupler) + number of cards

Use `builders.chassis_bus_size(card_count)` for the size and
`builders.renumber_rack_slots(modules_xml)` to renumber the cards from slot 1
upward. `renumber_rack_slots` only touches the card-side port -- a card
connects upward to its coupler, so its own address lives on the port carrying
`Upstream="true"`; the coupler's own `Address="0"` downstream port is its
position, not a card slot.

`lint.py`'s `chassis_size_mismatch` enforces this for dynamic backplanes only.

## Building a 2198 Kinetix module: the Major revision decides ConfigSize

Found 2026-09-14 from a conversion round in which 15 of 32 files were rejected
with "Data type mismatch - the object's value does not match its data type" on
`Communications/ConfigData/Data`.

**`ConfigSize` is a function of the module's `Major` revision, not of its
catalog number.** Read out of every 2198 module in `samples/local/`:

| module class | Major | ConfigSize / L5K value count |
|---|---|---|
| drives `2198-D*-ERS3`, `2198-S*-ERS3` | 7 | 376 / 96 |
| | 9 | 448 / 114 |
| | 11 | 448 / 114 |
| | 13 | 468 / 119 |
| | 14 | 468 / 119 |
| supplies `2198-P*` | any (3, 11, 13, 14 seen) | 376 / 96 |
| `2198-RP200` | 11 | 452 / 115 |

The same catalog appears at different revisions in different real programs —
Griffin carries D012/D020/D032/D057/S086 all at Major 11 with 448/114, while
Baillie and SJ_Gormley carry the same catalogs at Major 13/14 with 468/119. So
a `(catalog, Major)` pair fixes the payload and a catalog alone does not.

`sample_gen/data/kinetix.py` had listed D020/D032/D057 at Major 11 and S130 at
Major 11 while storing their Major-14 and Major-13 payloads. Every stored
payload is an exact byte match to a real module, so the payloads were never
wrong — the revision they were paired with was. D012, correctly paired at Major
14, imported clean throughout, which is what made the fault look catalog-specific.
`lint.py`'s `module_major_configsize_mismatch` now enforces the pairing, and
`module_identity_mismatch` now checks `Major` as well as ProductType/ProductCode
(it had been unpacked and discarded).

## Which channel a 2198 drive's second axis goes on

`Ch1` and `Ch3` for every D-series dual drive — 2198-D012/D020/D032/D057 — with
one D057 in the corpus also using `Ch4`.

`Ch2` is real but appears exactly once anywhere: `2198-S086-ERS3`
`DRV01_BedRolls` in EmporiumEdger, at Major 13. No D-series drive uses it, and
no catalog mixes the two schemes. An S086 riding two axes on Ch1/Ch3 is
rejected with "Invalid channel/node for motion module", which is what sank six
`axmarg_*` files; the one-catalog arm now uses 2198-D020-ERS3, a real Ch1/Ch3
dual and the most-attested drive in the corpus.

`2198-S130-ERS3` and every `2198-P*` supply are Ch1 only.

## Literal-operand batch — BUILT 2026-09-18 (OQ-LITERALOPERAND)

29 files, `src/sample_gen/gen_literaloperand.py`, written to
`samples/generated/logic/` as `litop_*`. Generated on explicit request; the
BOOL arm (F) was added to the original 20-file spec at the same time.

**What it measures.** An immediate numeric literal in an instruction operand
costs bytes the engine charges at zero. Measured on the bench at **+4.000 bytes
per slot** for a REAL literal in a REAL-typed MAM parameter (six slots, one
rung, +24 exactly). The question is the rate for every OTHER operand type,
because integer literals are 51,265 of the 52,195 unpriced slots in the real
set — 98% of the mass, and the part the bench does not cover.

**The hypothesis.** An immediate costs the width of its type, stored inline:
REAL 4 (measured), DINT 4, INT 2, SINT 1, LINT 8. The competing hypothesis is
that the cost follows the SLOT's declared type rather than the literal's.

**The engine predicts a ZERO delta for every pair in this batch.** Verified
after generation: all five arm-A pairs, and every file within arms B, C, D and
F, carry identical `predicted_bytes`. That is the defect, stated as a
falsifiable prediction — any non-zero capture delta is the unmodelled cost.

**Held fixed everywhere** — 1756-L81E at v35 (enforced by
`non_standard_processor` / `non_standard_firmware`), one Task, one Program, one
Routine, 1,000 rungs, and the source tag both DECLARED and REFERENCED in every
member of every pair by a byte-identical `EQU`. That last point is what made
the bench measurement clean; without it the literal term is confounded with
per-tag declaration cost, which is 84+ bytes and would swamp a 4-byte effect.

| arm | files | what moves | what it decides |
|---|---:|---|---|
| A `litop_type_*` | 10 | destination type, tag vs literal | the per-type rate, directly, as (lit − tag) / 1000 |
| B `litop_form_*` | 4 | the literal, on a fixed DINT destination | slot width vs value magnitude vs written form |
| C `litop_pool_*` | 3 | number of distinct values over 2,000 fixed slots | per-slot cost vs constant-pool cost |
| D `litop_fold_*` | 3 | literal 0 / 1 / 2 | whether Studio folds 0 and 1 |
| E `litop_family_*` | 3 | instruction family at a fixed literal | whether the law reaches MOV/EQU/JSR |
| F `litop_bool_*` | 4 | one AOI call-site argument | whether a BOOL slot prices 0/1 differently |
| G `litop_mam_*` | 2 | the bench shape at n=1000 | whether the pipeline reproduces the bench |

**Arm A caveat that will bite if ignored.** SINT and INT predict far higher than
DINT (254,288 and 290,288 against 74,288) because the existing
`operand_type_surcharge` charges narrow-integer widening. It is identical within
each pair, so it does not touch the pair differences — but the per-type rate
must be read from WITHIN-pair differences only. Comparing `litop_type_sint_lit`
against `litop_type_dint_lit` measures that surcharge, not the literal.

**Arm E differences against arm A, not internally.** Comparing MOV to EQU to
JSR necessarily moves instruction inventory, so `confound_check` flags those
pairs and is right to. Each arm-E file differences against
`litop_type_dint_tag_n01000`, the identical MOV shape with a tag operand.

**Arm F is a MECHANISM probe, not a real shape.** All 886 real `DigitalSensor`
call sites pass exactly two TAG arguments — instance plus the one Required
input — and set the optional inputs on the instance tag. A literal into a BOOL
parameter is therefore not attested in any real program. The arm is kept
because BOOL is the one atomic width where the width hypothesis predicts
something different, and because 0/1 folding is the highest-leverage unknown in
arm D. It must not be cited as real-shape evidence. Parameters are
`Required="false" Visible="true"`, the flag pair that permits a literal or a tag
at the call site; `Required="true"` demands a wired tag and would reject the
literal.

**Arm G is the pipeline control and is deliberately isolated.** Its operand list
is transplanted verbatim from the rung Studio compiled — transplant, never
compose, the rule that exists because bare composed MAM/MAJ/MAS/MRP rungs failed
every rung once. Only tag names are substituted, for `verified_tags.py` blocks
of the same types (`Axis1` AXIS_VIRTUAL, `MCD` MOTION_INSTRUCTION), because
those blocks are verbatim real. The pair should differ by 24,000 bytes; if it
does not, the generated pipeline does not reproduce the bench and nothing else
here can be trusted. `predicted_bytes` is 0 for both — an `AXIS_*` tag makes it
uncomputable (OQ-AXISSTRUCT) — so this pair is differenced against itself.

**Verify with** `python scripts/confound_check.py --family '^litop_<arm>'` per
arm. A whole-family run walks files alphabetically and so crosses arm
boundaries, which legitimately varies several dimensions; scope to one arm to
check the pairs that are actually differenced. All ten differenceable arms pass.

**This batch found a sixth blind spot in `confound_check.py`**, which is why it
exists: its instruction regex required an ALL-CAPS mnemonic, so every AOI call
site's operands were invisible, and it reported the four arm-F files — whose
call arguments genuinely differ — as IDENTICAL. A false negative is the one
failure worse than not checking. The pattern now accepts mixed-case names, which
is what real AOIs have (`DigitalSensor`, `AnalogSensor`, `PTimer`).
