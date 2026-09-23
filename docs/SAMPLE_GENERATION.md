# Sample Generation

How test L5X files are built, and every rule that decides whether one imports,
builds and measures what it claims to.

**Read this before writing a generator.** Almost every rule below exists because a
batch was lost to it.

---

## The standing rule: specify, then ask

**Test files are supplied, not invented.** The deliverable at the design step is a
written **spec** — what varies, what is held fixed, what each file discriminates,
and against which existing captures it differences — **not files on disk.**

Ask before generating anything, every time. **No prior batch authorises the next.**

The reason is specific: generated shapes have repeatedly turned out not to be the
shape they claimed. **A file that converts cleanly is not evidence the shape is
right.**

Every file in a batch must answer a real, currently-open question. There is no
minimum roster size to pad toward — if the genuine work is 20 files, spec 20.

---

## Method

Direct XML authoring. L5X is XML and Logix Designer imports hand-built files
cleanly, so a script takes parameters and emits valid XML. `src/sample_gen/`
holds the generators; `src/sample_gen/builders.py` holds the composable fragment
builders.

Generators live in the repo so a sample can be **regenerated exactly** rather than
hand-edited and drifted from its own generator.

### Naming and bookkeeping

- Files go to `samples/generated/<category>/<sample_id>.L5X`.
- Every sample gets a row in `samples/manifest.csv` at creation, with
  `predicted_bytes` filled in immediately from the sizing engine.
- **Every generator must name its open question in the sample's description.**
  `scripts/capture_errors.py` routes errored captures by that identifier, and a row
  with no owner fails the gate.

### Platform standard

**Every generated file is 1756-L81E at firmware 35.** No exceptions.

The point is comparability: a file on any other processor or firmware cannot be
differenced against the existing captures without first subtracting a baseline
difference that is itself only approximately known, which defeats the isolation
test.

Enforced by lint's `non_standard_processor` and `non_standard_firmware` rules
rather than left to each generator's defaults — **it has been violated twice, and
both times the deviation looked justified at the moment it was made.**

The exemptions are named individually with their reason: the firmware and catalog
matrix generators, for which sweeping those two fields *is* the variable under
test, and one Kinetix rack that needs an L83E because three dual-axis drives plus
two power supplies do not fit an L81E's 3 MB.

### The feedback loop

    generate → predict → convert → build → read actual → reconcile → adjust
    → re-predict EVERY prior sample → confirm no regressions

**That last step matters.** A constant tuned to fix one sample can silently break
another. Re-run the comparison after every constant change, not just on the sample
that prompted it.

---

## Rules that decide whether a file imports

### Logix identifier rules — a hard requirement on everything

**Every** name in the file: tags, programs, routines, tasks, modules, UDT members,
AOI parameters, local tags, data types, the **controller name**, and the export
header's `TargetName`.

- **No trailing underscore.**
- **No sequential underscores.**
- **No leading digit.**

All three fail with "Invalid name." and abort the whole import. One bad name costs
the entire file.

**Pad a name to a target length with filler letters, never underscores.**

Enforced in two places, deliberately:

- `builders.validate_logix_name` refuses to **build** an illegal name.
  `MemberSpec` validates in `__post_init__`, so one hook covers every member,
  parameter and local tag; each builder checks its own name.
- Lint's `invalid_logix_name` scans **every element with a `Name` attribute** plus
  the header's `TargetName`.

The one exemption is `<Version Name="1.1">` on an AOI revision, which is a version
string rather than an identifier — established by scanning millions of `Name`
attributes across the real exports, where it is the only name that breaks these
rules and still imports.

> This was hit three times, and **every instance came from a name composed out of
> parts**, which is exactly what a generator author cannot see by reading their own
> call site. The third one shipped after the lint rule existed, because that rule
> walked a hand-maintained list of ten element tags and `<Controller>` was not one
> of them. **That list is gone; the rule is universal.** That is why the build-time
> guard exists alongside the lint check.

### Every rung needs an output instruction

A rung containing only condition instructions has nothing terminating it and Studio
rejects it.

```
SBR(P0,P1,P2)NOP();     correct
SBR(P0,P1,P2);          rejected — no output instruction
```

**SBR only receives the caller's parameters. It has no effect of its own**, so it
behaves exactly like a bare `EQU` and takes the same fix. `RET();` on its own rung
is fine — RET is a real output.

Structured Text is exempt: it has no rungs and no output-instruction rule, and the
real corpus carries bare `SBR( a, b, c );` ST statements that build clean.

> **The lesson is about where a rule lives, not about SBR.** Lint already had this
> check for exactly this class; SBR simply was not in its pure-condition list. Eight
> of nine generators emitting an SBR got the `NOP()` right **by convention** and the
> ninth silently did not. **A rule enforced by convention across nine copies is a
> rule the tenth will break.** When a build-validity rule turns up, put it in
> `lint.py` — a comment in the generator you happen to be editing does not protect
> the others.

### An array-typed operand needs a subscript

Real syntax always requires `[index]`, and `SIZE` needs `.DATA[0]` on its STRING
operand. **A file with a bare array name converts cleanly and never builds at
scale**, which is why every affected instruction came back at an identical byte
count regardless of rung count.

### A structure cannot be an AOI Input parameter

**Input and Output parameters are passed by value, and Logix accepts only an atomic
type there.** A UDT, a nested AOI, a STRING or an AXIS_* must be `Usage="InOut"`,
which passes a reference. A `Radix` on a structure is wrong for the same reason a
structure tag never carries one.

`builders.py` raises on this at build time.

### A structure-typed tag needs a Structure body

Not a scalar `DataValue`, and no `Radix`. This is why exactly the files declaring
such a tag failed while the ones with none converted.

### A call site needs exactly the arguments the definition has slots for

A parameter declared `Required="false" Visible="false"` is hidden — **it has no
slot on the calling rung at all** — so wiring a value into it gives that argument
nowhere to go.

To let a **literal** reach a parameter, declare it `Required="false"
Visible="true"`. `Required="true"` demands a wired tag.

### Motion instructions need their full parameter list

The bare two-operand `(Axis, MotionInstruction)` call is **MAH and MSO's own shape,
not a general motion shape.** Real operand counts: MAM 20, MAJ 17, MAS 9, MRP 5.
Transplant each from a real example position for position, keeping keywords and
literals verbatim and substituting only tag names.

**MAPC needs two distinct axis tags** — an axis cannot cam to itself. Any two axis
types work; a CIP-Drive/Virtual pairing is not required.

### Labels are scoped per routine

Two routines can both use the same label name without colliding.

---

## Rules that decide whether a rack is right

### Bus size and slot numbers belong to the rack, not the module

Module blocks are copied verbatim from real exports. That is deliberate and it is
what makes them import — **but a real module carries two values that belong to the
application it came from:**

- its **bus size**, which is the size of that plant's rack, and
- its **slot address**, which is where it happened to be installed.

An output card found at slot 8 in one application is not a card that must live at
slot 8. **Both values have to be recomputed by the generator; inheriting them is
how a one-card rack ends up declaring fourteen slots.**

**Fixed backplanes — 1756 (`Port Type="ICP"`).** The slot count is a property of
the physical chassis catalog: 4, 10, 13 or 17. An under-populated 1756 chassis is a
normal design, never flagged.

**Dynamic backplanes — POINT I/O, FLEX and 5069.** There is no physical chassis;
the bus is exactly as long as what is plugged into it. The coupler occupies one
position and each card one more, so a correct rack declares the **smallest** size
that fits:

    Bus Size = 1 (coupler) + number of cards

Use `builders.chassis_bus_size()` for the size and `builders.renumber_rack_slots()`
to renumber the cards from slot 1 up. That helper only touches the **card-side**
port: a card connects upward to its coupler, so its address lives on the port
carrying `Upstream="true"`; the coupler's own downstream `Address="0"` is its
position, not a card slot.

Lint's `chassis_size_mismatch` enforces this for dynamic backplanes only.

### A 2198 drive's ConfigSize is a function of its Major revision

**Not of its catalog number.**

| module class | Major | ConfigSize / value count |
|---|---|---|
| drives `2198-D*-ERS3`, `2198-S*-ERS3` | 7 | 376 / 96 |
| | 9, 11 | 448 / 114 |
| | 13, 14 | 468 / 119 |
| supplies `2198-P*` | any | 376 / 96 |
| `2198-RP200` | 11 | 452 / 115 |

The same catalog appears at different revisions in different real programs, so **a
`(catalog, Major)` pair fixes the payload and a catalog alone does not.**

> This rejected 15 of 32 files in one round with "Data type mismatch." Every stored
> payload was an exact byte match to a real module — **the payloads were never
> wrong, the revision they were paired with was.** The one catalog correctly paired
> imported clean throughout, which is what made the fault look catalog-specific.

Lint's `module_major_configsize_mismatch` enforces the pairing, and
`module_identity_mismatch` checks `Major` alongside ProductType and ProductCode.

### Which channel a 2198 drive's second axis uses

**`Ch1` and `Ch3`** for every D-series dual drive, with one real D057 also using
`Ch4`.

**`Ch2` is real but appears exactly once anywhere** — one S086 at Major 13. No
D-series drive uses it, and no catalog mixes the two schemes. An S086 riding two
axes on Ch1/Ch3 is rejected with "Invalid channel/node for motion module," which
sank six files.

`2198-S130-ERS3` and every `2198-P*` supply are Ch1 only.

### Check for an existing diagnosis before hand-picking a catalog

Two real errors were rebuilt from scratch by hand when **both were already
diagnosed and excluded elsewhere in this codebase** — one catalog sitting in a
documented exclusion set with its real "Child module incompatible with parent
module" error, and several 5069 catalogs combined onto the default non-safety
controller.

**Grep the generators for the catalog before using it.**

---

## Rules that decide whether a batch measures what it claims

### Vary exactly one dimension per pair

`scripts/confound_check.py` checks this mechanically across 18 dimensions. **Scope
it to one arm** — a whole-family run walks files alphabetically and crosses arm
boundaries.

The script has found six blind spots in itself: expressions inside rung operands,
ST bodies, definition member order, rung structure, tag declaration order, and
mixed-case AOI call sites. **A false negative is the one failure worse than not
checking.**

### Build a real-scale batch out of already-proven rung text

**The batch that answers a real-scale question has to actually build at real
scale.**

> One batch was built to answer exactly its question using a hand-rolled
> instruction mix over a hand-rolled tag pool, came back with 5, 26, 50 and 75
> build errors, and left the question open for four more days. **The cause of those
> specific errors is still undiagnosed.**

The pattern to copy:

- **Take the rung text and tag pool verbatim from a shape with an error-free build
  on record** at the scale you need. **Nothing in a new batch should re-invent an
  operand shape a valid capture already proves.**
- **Pick counts that pair with existing valid captures.** Then each file differs
  from an error-free row by one deliberate change, and the answer falls out as a
  paired difference with no model in between. A ladder sharing no count with the
  existing corpus throws that away.
- **If the proven shape also errors in the new placement, that is the result**, not
  a setback — it isolates the placement as what Studio objects to, which no existing
  row can distinguish.

### Hold the source tag declared and referenced

When a pair moves an operand from a tag to a literal, **keep the tag both declared
and referenced in both members.** Otherwise the term under test is confounded with
per-tag declaration cost, which is 84+ bytes and swamps most effects.

### Transplant, never compose

Rung text and backing tag XML for anything unusual come out of a real export
verbatim. Composing a call shape from a manual has cost real time three times:
invented alarm condition types (all four rejected), bare motion instruction calls
(every rung failed), and safety tags Studio synthesises itself.

### A generator fix is not done until the committed files are regenerated

> A rack generator's fix landed in the source and an in-memory test of the fixed
> function was reported as verification — **but the committed files were never
> regenerated.** They still had pre-fix content and kept failing, not because the
> fix was wrong but because the shipped files never picked it up.

**Verifying the function is not the same as verifying the file that ships.** Re-run
the generator and commit the diff.

The opposite case exists too: regenerating another family changed nothing but a
timestamp — that fix had already shipped, and the file was sitting on a stale,
never-retried failure entry. **Distinguishing a stale file from a stale log entry
needs an actual regeneration and diff, every time.**

---

## The realism floor — every file from here on

`sample_gen/realism.py`, enforced by `write_sample()` (`lint.realism_findings`) and by
`tests/test_build_guards.py` on the waiting batch:

- **≥ 5 Ethernet I/O nodes.** The baseline adds RACK_1..RACK_5, each a 1734-AENTR/C
  (from the clean `modulesweep_1734_ib8_c` block, resized to Bus Size 9 as the clean
  `pioconn_optimized_n08` proves AB:1734_9SLOT) with 1734-IB8/C in slots 1–4 and
  1734-OB8/C in 5–8, rack-optimized. Points are `RACK_n:slot:I.b` / `RACK_n:slot:O.b`.
- **≥ 25% of the controller predicted** (786,432 on the 1756-L81E). The baseline plant is
  1,280 stations in four line programs, ten stations per JSR-called area routine; alone
  it predicts 842,178.
- **No output bit written twice.** No OTE/ONS target repeated; no OTL/OTU target also
  OTE'd. AOI-internal logic is exempt (it runs per instance).

Build with `build_l5x(target_name=..., **realism.with_baseline(**arm_kwargs))`.

## Current batch: the realism batch — 16 files

`gen_realism_batch.py`, `samples/generated/realism/`. Every file on the baseline; each
arm declares the same tags in every file.

| family | differenced against | question |
|---|---|---|
| `realism_base_f25`, `_f50` | its own prediction; each other per station | OQ-REALISMFLOOR |
| `realism_srout_series_k{01,02,04,08}` | `_series_k01` | OQ-SERIESREAL |
| `realism_srout_branch_k{02,08}` | `_series_k` at the same k | OQ-SERIESREAL |
| `realism_srout_inter_k{02,08}` | `_series_k01` (same instructions, fewer rungs) | OQ-SERIESREAL |
| `realism_pio_{bool,addr,alias}_n{080,160}` | the other two arms at the same n; own other n | OQ-PIOADDR |

## Also waiting: program-scoped structured tags — OQ-PROGSCOPESTRUCT, 12 files (on the baseline)

`gen_program_scope_struct.py`. The identical tags at controller scope and at program
scope (MainProgram), at 10, 50 and 200: a 7-member UDT (4 DINT, 2 BOOL, REAL) and a
DINT[20] array. One NOP rung in every file.

| family | differenced against |
|---|---|
| `progscope_ctl_{udt,arr}_n*` | `progscope_prog_*` at the same count |
| `progscope_prog_{udt,arr}_n*` | `progscope_ctl_*` at the same count, and its own other counts |

## Previous batch: operand shape — OQ-OPERANDSHAPE, 26 files

**Captured: all 26 exact, zero errors.** Closed negative.

`gen_operand_shape.py`. One instruction per family, one operand's shape varied, the
identical tag inventory (plain BOOL/DINT tags, a UDT `U` with a BOOL, a DINT and a
nested UDT member, and a 4-element array of it) in every file, at 250 and 1,000 rungs.

| family | shapes | differenced against |
|---|---|---|
| `opshape_xic_*` — `XIC(<op>)OTE(Out)` | plain, mem `U.Bit`, nest `U.Sub.Bit`, arrmem `UA[2].Bit`, bitword `PD.5` | `opshape_xic_plain` at the same count |
| `opshape_ote_*` — `XIC(In)OTE(<op>)` | plain, mem, nest, arrmem | `opshape_ote_plain` |
| `opshape_mov_*` — `MOV(<src>,<dst>)` | plain, srcmem, dstmem, nest | `opshape_mov_plain` |

Building it required a lint fix: the operand resolver returned the base tag's type for
`U.Bit` and refused it as a non-BOOL XIC operand, which is why no earlier file carried
a member-path operand. It now follows member paths through the file's UDTs.

### JSR parameter edges, 8 files — captured, all zero errors, wired

`gen_jsr_param_edges.py`, 100 calls per file, identical tag inventory within each arm.

| family | varies | question |
|---|---|---|
| `jsredge_ret_{dint,udt}_n{1,3}_r00100` | DINT vs UDT RETURN values | does a structured return cost what a structured input costs? |
| `jsredge_in_{bare,member}_n{1,3}_r00100` | bare UDT tag vs a member `W.S0` whose type is that UDT | does a UDT member argument get the structured rate? |

## Previous batch: every open capture, regenerated, plus the open questions

**Captured.** 49 of 52 at zero errors; the three failures were rebuilt as `_r3` and
captured clean.

52 files. The conversion and capture tooling skip any file name they have already
seen, so an open capture that was attempted once — or never reached the converter —
never surfaced again. Everything open was rebuilt under a new name, and every open
question a generated file can answer got a family.

| family | files | generator | question |
|---|---:|---|---|
| `jsrcallers_k{01,02,04,05,10,20}` | 6 | `gen_jsr_caller_distribution.py` | OQ-JSRCALLERBASE |
| `rungpack_{xic,equ}_k{01,02,04,08,16,40}` | 12 | `gen_rung_packing.py` | OQ-RUNGSHAPE |
| `modname_p208_len{04,06,08,10,12,13,16,17,20,24,32,40}` | 12 | `gen_module_name_length.py` | OQ-MODULENAMELEN |
| `alarmcond_realcount_n{000,200,400,600}` | 4 | `gen_alarm_real_count.py` | OQ-ALARMCONDREAL |
| `composite_realistic_{10,11,22,32,34,36,46,47,48}_r3` | 9 | `gen_composite_realistic.py --regenerate-open` | composite instrument |
| `litop_bool_{alltag,zero,one,dint}_n01000_r2` | 4 | `gen_literaloperand.py` arm F | OQ-LITERALOPERAND |
| `instrfirst_mapc_v2_x100` | 1 | `gen_instruction_firstpass.group_mapc_v2(count=100)` | MAPC third point |
| `almd_{minimal,realtext}_r2` | 2 | `gen_almd_singletag.py --suffix _r2` | OQ-BUILDFAIL-OPEN |
| `eventtask_axiswatch_r2` | 1 | `gen_event_task_trigger.py --regenerate-open` | OQ-BUILDFAIL-OPEN |
| `modulerack_kinetix_full_bus_r2` | 1 | `gen_module_kinetix_bus.py --suffix _r2` | OQ-BUILDFAIL-OPEN |
| `almd_{minimal,realtext}_r3` | 2 | `gen_almd_singletag.py --suffix _r3` | OQ-BUILDFAIL-OPEN — real 5-operand ALMD |
| `modulerack_kinetix_full_bus_r3` | 1 | `gen_module_kinetix_bus.py --suffix _r3` | OQ-BUILDFAIL-OPEN — proven blocks only |

**Captured: 49 of the 52 `_r2`-era files at zero errors.** The `_r3` rows replace the
three that failed Build; see OQ-BUILDFAIL-OPEN.

The nine composites were never sent because lint refused them — a CIP Safety module on
a non-safety controller, two modules in one slot, a Kinetix drive with no bus supply.
They are rebuilt from the same profile with the module window slid until nothing
build-blocking remains.

`confound_check.py` gained two dimensions to check this batch: **module name lengths**
and **alarm-condition count**. Without them it read the name and alarm families as
byte-identical, the same class of blind spot its docstring already records six times.

### Retired, not rebuilt

Each of these targets a shape that appears in **none of the eighteen real programs**,
or dead architecture. Rebuilding them would spend a capture on something no user's
program contains — and three had already been refused on import four times.

| spec row | why |
|---|---|
| `fwmatrix_v31_1769_l33erm` | 1769 is dead architecture (CLAUDE.md); no further 1769 test files |
| `fwmatrix_v32_1769_l33erm` | 1769 is dead architecture (CLAUDE.md); no further 1769 test files |
| `fwmatrix_v33_1769_l33erm` | 1769 is dead architecture (CLAUDE.md); no further 1769 test files |
| `fwmatrix_v34_1769_l33erm` | 1769 is dead architecture (CLAUDE.md); no further 1769 test files |
| `fwmatrix_v35_1769_l33erm` | 1769 is dead architecture (CLAUDE.md); no further 1769 test files |
| `predefprobe_timer_t` | type appears in none of the 18 real exports; refused on import four times |
| `predefprobe_ref_to_axis_cip_drive` | type appears in none of the 18 real exports; refused on import four times |
| `predefprobe_ref_to_axis_virtual` | type appears in none of the 18 real exports; refused on import four times |
| `alarmcond_type_trip` | all 4,663 real alarm conditions are TRIP at the defaults already measured; orphan spec, no generator |
| `alarmcond_type_trip_high` | condition type appears in none of the 18 real exports |
| `alarmcond_type_trip_low` | condition type appears in none of the 18 real exports |
| `alarmcond_type_deviation` | condition type appears in none of the 18 real exports |
| `alarmcond_hmigroup_len64` | real HMI groups are at most 15 characters; 4/16/40 already captured |
| `cipmodule_scale_1024b` | real CIP-MODULE connections top out at 496 bytes |
| `cipmodule_scale_2048b` | real CIP-MODULE connections top out at 496 bytes |
| `fwmatrix_v38_1769_l33erm` | 1769 is dead architecture (CLAUDE.md); no further 1769 test files |

`gen_fw_catalog_matrix.py` no longer emits 1756-L7x or 1769 catalogs, so a re-run
cannot bring those rows back.

## Previous batch: JSR caller distribution

6 files, `src/sample_gen/gen_jsr_caller_distribution.py`, written to
`samples/generated/logic/` as `jsr_callerdist_k{01,02,04,05,10,20}`.

**What it measures.** Whether `jsr_fixed_base_per_routine` (5,096) is charged once
per file or once per JSR-caller routine. Every existing JSR file has exactly one
caller, so the two readings fit the entire corpus identically. The 86 captured files
that do have several callers are multi-megabyte composites with 10,000–94,000-byte
residuals from unrelated defects, so none of them isolates it either.

**What is held fixed.** Total JSR calls at 20, distinct 0-parameter targets at 20,
rung text, instruction inventory, tag inventory (empty), target names, processor and
firmware. With K callers, MainRoutine takes 20/K calls and K−1 extra caller routines
take 20/K each; K runs over the divisors of 20 so no file carries a remainder
routine the others lack.

**What moves.** The routine count, and only the routine count —
`confound_check.py` confirms every consecutive pair varies exactly one dimension.
Extra caller routines cannot be added without adding routines; the plain-routine
component is separately priced at exactly 280 bytes by `subrtn_shell` at four counts
with zero residual, so it subtracts cleanly.

**What it differences against.** K=1 reproduces `jsr_multi_distinct_targets_n20`'s
shape and target names and predicts at the identical 25,752, anchoring the family to
a capture already in hand (25,472).

**Predictions are recorded in `OPEN_QUESTIONS.md` before the capture run.** The
three competing readings agree at K=1 and separate by 86,488 bytes at K=20, so no
outcome leaves the question open.

## Previous batch: literal operands

29 files, `src/sample_gen/gen_literaloperand.py`, written to
`samples/generated/logic/` as `litop_*`.

**What it measures.** An immediate numeric literal in an instruction operand costs
bytes the engine charges at zero — measured on the bench at **+4.000 bytes per
slot** for a REAL literal in a REAL-typed motion parameter. The question is the
rate for every other operand type, because integer literals are 98% of the real
exposure and the part the bench does not cover.

**The engine predicts a zero delta for every pair in this batch**, verified after
generation. That is the defect stated as a falsifiable prediction: any non-zero
capture delta is the unmodelled cost.

| arm | files | what moves | what it decides |
|---|---:|---|---|
| A `litop_type_*` | 10 | destination type, tag versus literal | the per-type rate, directly, as (lit − tag) / 1000 |
| B `litop_form_*` | 4 | the literal, on a fixed DINT destination | slot width versus value magnitude versus written form |
| C `litop_pool_*` | 3 | distinct values over 2,000 fixed slots | per-slot cost versus constant-pool cost |
| D `litop_fold_*` | 3 | literal 0 / 1 / 2 | whether Studio folds 0 and 1 |
| E `litop_family_*` | 3 | instruction family at a fixed literal | whether the law reaches MOV, EQU and JSR |
| F `litop_bool_*` | 4 | one AOI call-site argument | whether a BOOL slot prices 0 and 1 differently |
| G `litop_mam_*` | 2 | the bench shape at 1,000 rungs | whether the pipeline reproduces the bench |

**Arm A must be read WITHIN pairs only.** SINT and INT predict far higher than DINT
because the existing operand-type surcharge charges narrow-integer widening. It is
identical inside each pair so the differences are clean — but comparing
`litop_type_sint_lit` against `litop_type_dint_lit` measures that surcharge, not
the literal.

**Arm E differences against arm A, not internally.** Comparing MOV to EQU to JSR
necessarily moves instruction inventory, so the confound checker flags those pairs
and is right to. Each arm-E file differences against `litop_type_dint_tag`, the
identical MOV shape with a tag operand.

**Arm F is a mechanism probe, not a real shape.** All real `DigitalSensor` call
sites pass exactly two **tag** arguments — instance plus the one required input —
and set the optional inputs on the instance tag. A literal into a BOOL parameter is
**not attested in any real program.** The arm is kept because BOOL is the one
atomic width where the width hypothesis predicts something different, and because
0/1 folding is the highest-leverage unknown in arm D: those are the most common
literals in real ladder, so if they are free the whole exposure collapses. **It
must not be cited as real-shape evidence.**

**Arm G is the canary and is deliberately isolated** so a MAM import failure cannot
take the other 27 with it. The pair should differ by 24,000 bytes. **If it does
not, the generated pipeline does not reproduce the bench and nothing else in the
batch can be trusted.** Its predicted bytes are 0 for both, because an `AXIS_*` tag
makes prediction uncomputable, so it is differenced against itself.

---

## Reference: what earlier batches established

Kept because each answers a question a future batch might otherwise re-ask.

**A bare CMP cannot close a rung**, so every CMP test file carries a trailing
`OTE`. Same reason several instructions in the original sweep are paired with a
companion output.

**A repeated identical expression scales linearly.** Spot-check files repeating one
expression across 100 rungs confirmed that single-rung reads can be trusted
directly — there is no dedup or background optimisation of identical expressions.

**Required / Visible flags do not affect definition cost**, only call-site syntax
validity. Confirmed across all flag combinations, with and without an InOut
parameter in the mix.

**Leaving an optional parameter unwired costs the same as wiring it.** Matches the
real corpus pattern where a real AOI call wires only two of its four non-hidden
inputs.

**A JSR target's parameters arrive at SBR as the routine's first instruction, and
RET can appear multiple times, conditionally, with no limit.** Confirmed against
real examples before any of it was generated.

**LBL and JMP were separable only by testing them apart** — one LBL with N JMPs
isolates JMP's rate, and LBL-only rungs with no JMP anywhere isolate LBL's. A
1:1-pair sweep alone cannot split the pair, however many counts it covers.
