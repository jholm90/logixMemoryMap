# Open Questions

**Six.** Down from forty, and the thirty-six that went were not abandoned — they
were **bounded** or answered. Closed questions and their reasoning trails are in
`RESOLVED_QUESTIONS.md`.

## The bar for opening a new one

**State, before any file is built, how many percentage points it should move on the
seventeen real programs and by what mechanism.**

If the mechanism is a category scale, it is already answered: an eight-parameter
per-category fit, fitted directly on the held-out real programs — cheating, an upper
bound no honest procedure can beat — reaches mean 1.01% / max 2.59% and **still
fails** the stopping rule. Under leave-one-out it is worth **0.007 percentage
points**, with half the files getting worse.

So **every question whose mechanism was "a cost constant is slightly wrong" has a
measured maximum payoff of approximately zero**, however cleanly it would answer.
That is why thirty-four closed at once; a thirty-fifth, literal operands, closed on its real-program exposure.

## What is left, and why each survives the ceiling

| question | why the ceiling does not bound it |
|---|---|
| **OQ-JSRCALLERBASE** | Per-file versus per-caller-routine is untestable on the existing corpus and differs by up to ~300 KB on a real program. Six files built, awaiting capture. |
| **OQ-REALUNDER** | It *is* the residual. The ceiling bounds every proposed explanation without closing the gap. |
| **OQ-RUNGSHAPE** | A per-rung term the model does not have, perfectly confounded with every per-instruction weight. |
| **OQ-ALARMCONDREAL** | A 9.4%-of-mass category that is 8.8% short on one real file. Not a scale error — the two files disagree with each other. |
| **OQ-BUILDFAIL-OPEN** | A defect log. Kept visible on purpose. |
| **OQ-MODULENAMELEN** | A term the engine charges at zero, measured on a clean isolation pair. Not a scale error. |

---

## 1. OQ-JSRCALLERBASE — is the 280-byte JSR premium per file or per caller routine

**The marginal cost of a no-parameter JSR is exact and the engine already has it
right.** One distinct 0-parameter target plus its JSR call costs **368 bytes**,
measured straight off the captures:

| pair | interval | per unit |
|---|---:|---:|
| `jsr_multi_distinct_targets_01` → `_03` → `_05` | 2 | **368** |
| `..._n05` → `_n10` → `_n15` → `_n20` | 5 | **368** |
| `..._n20` → `_n50` | 30 | **368** |
| `jsr_crossed_n20_namelen16` → `_n40_namelen16` | 20 | **368** |

Eight independent intervals across two generators, zero residual. `jsr_crossed_n20_namelen16`
and `jsr_multi_distinct_targets_n20` were built by different generators and capture
at the identical 25,472. Target name length is separately priced and also exact —
all five `namelen` rows carry the same residual.

**The residual is a single flat constant.** Recomputed live against the current
engine, all 14 clean 0-parameter rows over-predict by **exactly 280 bytes** — at
n = 1, 3, 5, 10, 15, 20, 40, 50 and at name lengths 4, 8, 16, 32, 40. The slope is
perfect; only the intercept is wrong.

**It is `jsr_fixed_base_per_routine`, and the arithmetic is not subtle.** The model
carries two per-routine bases: `fixed_base_per_routine` = **4,816** for an ordinary
routine, and `jsr_fixed_base_per_routine` = **5,096** for a routine containing a JSR.

    5,096 - 4,816 = 280

That is the residual exactly, and the `subrtn_shell` control — same file shape, no
JSR — predicts at **0.000%** at 1, 5, 25 and 100 routines, so the 4,816 path is
right and the 5,096 path carries the whole error. The 280 premium was presumably
meant to cover the caller declaring a target subroutine, but the per-target cost is
already charged separately through `jsr_target_declaration`, so it is charged twice.

That also explains the band. `derive_instruction_accuracy.py` divides a whole-file
error by file size, so a fixed 280 on a 19,952-byte file reads as 1.40% — and the
recorded JSR worst case is **1.4034%**. The number is a constant divided by a file
size, not a property of JSR.

**Blocked, and this is the reason it is not being changed.** `jsr_fixed_base_per_routine`
is charged **once per JSR-caller routine**, not once per file. Every one of the 30
JSR files in the corpus has **exactly one** caller routine — checked directly, not
assumed. So "280 once per file" and "280 per caller routine" fit all 30 rows
identically and the corpus cannot separate them. A real program has tens to hundreds
of caller routines, so the two readings differ by thousands of bytes there, in the
direction that would make the real files worse: they currently under-predict, and
the per-caller reading subtracts more.

This is the collinearity failure mode exactly — two constants against points that
only ever vary one of them. Applying either reading now would be fitting, not
measuring.

**The discriminating family is built: `jsrcallers_k{01,02,04,05,10,20}`** (first built as
`jsr_callerdist_k*`, never picked up by the converter, rebuilt under new names).

Total JSR calls held at **20** and distinct 0-parameter targets at **20** in every
file. Only the distribution moves: with K callers, MainRoutine takes 20/K calls and
K−1 extra caller routines take 20/K each. K runs over the divisors of 20 so no file
carries a remainder routine the others lack.

`confound_check.py` reports **every consecutive pair varies exactly one dimension —
`routines`**, which is the variable itself. Rung text, instruction inventory, tag
inventory and the target set are identical across all six. A plain extra routine is
separately priced at exactly **280 bytes** by `subrtn_shell` (four counts, zero
residual), so that component subtracts cleanly. All six lint clean on 1756-L81E
firmware 35.

K=1 reproduces `jsr_multi_distinct_targets_n20`'s shape and target names exactly and
predicts at the identical 25,752, so it is anchored to a capture already in hand
(25,472).

**Predictions written down before the capture run, per the blind-test rule:**

| file | callers | engine predicts | **A** per file | **B** per caller | **C** flat −280 |
|---|---:|---:|---:|---:|---:|
| `jsrcallers_k01` | 1 | 25,752 | 25,472 | 25,472 | 25,472 |
| `jsrcallers_k02` | 2 | 30,848 | **25,736** | **30,288** | **30,568** |
| `jsrcallers_k04` | 4 | 41,040 | **26,264** | **39,920** | **40,760** |
| `jsrcallers_k05` | 5 | 46,136 | **26,528** | **44,736** | **45,856** |
| `jsrcallers_k10` | 10 | 71,616 | **27,848** | **68,816** | **71,336** |
| `jsrcallers_k20` | 20 | 122,576 | **30,488** | **116,976** | **122,296** |

- **A — the base belongs to the file.** An extra caller routine costs what any
  routine costs, 264 plus its rungs. `actual(K) = 25,472 + 264·(K−1)`.
- **B — the base belongs to each caller.** The engine's structure is right and only
  the 280 premium is wrong. `actual(K) = predicted(K) − 280·K`.
- **C — the engine is right and the 280 is something else.**
  `actual(K) = predicted(K) − 280`.

All three agree at K=1 by construction and separate by **86,488 bytes** at K=20.
There is no reading of the result that leaves this open.

**If A holds, this is not a 280-byte item.** The engine charges 5,096 per caller
routine; a real export has 60 of them, so it would be over-charging roughly 300,000
bytes there and something else is under-charging by more, since the real files
currently under-predict. That is the compensating-error failure mode, and it would
make this the largest single identified defect in the model.

Hold `jsr_fixed_base_per_routine` at 5,096 until the capture reads.

**The 280 is now billed where it belongs and is visible.** The per-caller shell
is its own `subroutine_shell` entry under a **Subroutine Overhead** tree group,
labelled with the caller count — 122,304 bytes across 24 caller routines, 1.58%,
on the real export. It was previously folded into each calling routine's
instruction total, invisible, and the difference was charged against the JSR
instruction. Reclassification only: totals byte-identical on all 3,551 corpus
files. The uncertainty this question tracks now sits on that line item.

**The confidence side is already fixed and does not wait on the capture.** The
280 is a per-routine shell constant, not a JSR cost, so it was never JSR's band
to lose. `JSR/0` now reads **Exact ±0**: see `MEMORY_MODEL.md`, "A 0-parameter
JSR is EXACT". On the real export that moves 13 routines from 75% to 100% while
the 20 carrying a parameterised JSR stay at 75%. What the capture settles is the
byte total, not the band.

**A second, smaller band sits underneath it.** The `jsr_paramcount_*` family
residuals cluster at **−296 / −300** rather than −280, flat across rung counts from
10 to 1,000 and across parameter counts 1 to 15. That is a further 16–20 bytes
outside the ±8 floor, constant, and it appears only once SBR/RET carry operands. It
is the same shape of defect and almost certainly resolves with the same file.

**Why this is worth the time despite being 280 bytes.** It is not the bytes. It is
that the confidence display points at the wrong instruction, so the one number a
user judges a dispatch routine by is wrong for every routine that dispatches — and
the same constant is charged per caller routine across every real program, where
it is not 280 bytes at all.

---

## 2. OQ-REALUNDER — the residual itself

**+822,938 bytes on 55,430,980 = +1.485%** over the original seventeen. Ten files
under-predict, seven over-predict.

**Six blind programs, predicted before their readings existed, all under-predict:**
mean 1.90%, worst 3.99%, every one low (export 31–36). Five of six landed inside the
range written down in advance; the sixth missed it by 29 KB. Across all twenty-three
the residual is **about +1.72%, sixteen under and seven over.** The blind set is the
cleanest evidence the project has that the missing bytes are real, systematic and
one-directional *on the kind of program users actually bring* — large 1756-L83E line
controllers — and that the over-predicting files are the exception. Export 32 is a
later revision of export 07 and misses by almost the same amount (−2.31% against
−2.14%): **the residual is a property of the program, stable across revisions.** That
is what makes a real-program residual model worth trying rather than more constants.

**The residual is no longer one-sided**, which is the most important structural fact
about it. It used to be — every file under-predicted and the work was to find missing
bytes. **Any candidate that can only add bytes is now wrong before it is tested.**

### What has been eliminated

Each of these was tested and failed. The full table is in `ROADMAP.md`; the
load-bearing ones:

- **Any per-routine, per-rung, per-program or per-tag constant.** All four are
  collinear with size, so each moves the bias and leaves the spread. **The remaining
  error is not a missing per-unit cost.**
- **Any flat per-file constant.** Swept from 2,000 to 10,000 bytes; every value made
  the mean worse, monotonically. A per-file term moves all files equally, so bias
  improves and spread does not.
- **A global `routine_logic` scale-up.** Ruled out twice — by 578 instruction rows,
  and by direct measurement in both directions on real programs.
- **Tag data space.** Every real tag shape is covered; the untested ones total a few
  thousand bytes. The name-length term is cleared by 88 clean rows at mean 0.12%.

**So both remaining shapes are eliminated: the residual is CONTENT-DEPENDENT.**
Neither counting structural units nor charging every file the same can reach it.

### What is left

**A term not proportional to any category the engine counts.** OQ-LITERALOPERAND
showed such terms exist, then closed on its own real exposure — 1,756 bytes across
eighteen programs — so it proved the kind of term without being the one. It is still
the only live lead.

### The structure that is still unexplained

The ratio of residual to `routine_logic` bytes is **bimodal** across the real set,
and nothing explains why. It is not a per-unit error — the coefficient of variation
is 1.74 per instruction occurrence, 1.72 over the top four instructions, and 1.73
per rung. **Whatever it is does not scale with any count the engine has.**

### The instrument that could have found the rest is gone

Attribution by subtraction from a real export is **dead** by the read-only rule, not
merely difficult. And no generated file can carry content that generated files do not
have, **which is the definition of the gap.**

**The Studio-side substitute is declined as well.** Deleting a category inside Logix
Designer and reading Capacity twice would attribute the residual at real scale
without breaking the read-only rule, but each reading is a bench session the owner
will not spend. It is struck, not pending.

**What remains is a residual model on the real programs themselves, scored only by
leave-one-out.** One term per feature the engine does not count — distinct tag
names, program count, data-to-logic ratio — fitted on twenty-three files and
judged on each file held out in turn. The bar is the 0.007-point result the
per-category fit managed. A term that does not clear it is dropped, however well it
fits in-sample. Every new real export is predicted and recorded before its reading
exists, and each one both tests the current model and widens the fitting base.

That is not a reason to keep trying variations. It is the reason the 1% target may
not be reachable at all.

---

## 3. OQ-RUNGSHAPE — a per-rung term, confounded with every instruction weight

**Every calibration file in the project is one instruction per rung.** So a per-rung
cost and a per-instruction cost are **perfectly confounded** in every weight in the
model. `routine_logic` is 18% of predicted mass, so this is not a small exposure.

### The coverage gap is real but is NOT the error

The weights are fitted on a corpus that is **9.4% branched rungs and 62%
single-instruction rungs**, against real programs at **68.7% and 7%** — measured over
41,374 real rungs and 125,275 real instruction occurrences.

That was the largest suspected error source in compiled logic. **It was measured, and
the terms hold exactly.** Holding eight XIC conditions and one OTE fixed across 500
rungs and moving only the arrangement across 1, 2, 4 and 8 parallel legs, the
predicted steps are correct **to the byte at every leg count**, and a second pair
confirms it at the real population's composition.

**So the branch-bracket cost extrapolates correctly outside the shape it was fitted
on.** The coverage gap is a fact about the corpus, not a defect.

### The attempt to isolate the per-rung term failed, by design error

A packing sweep held 4,000 instructions fixed and varied how many sat on each rung,
so rung count moved while instruction count did not — which is the only way to
separate the two terms.

**It used OTE, which is an output.** Packing outputs onto one rung builds series
cascades, so extra series outputs and rung count moved together identically in every
file. **Total confound.**

It was not wasted: it re-measured the series-output law at four new points at exactly
−12.000, and **killed that law's competing candidate** — the files were all distinct,
so the cost cannot be per-distinct-rung.

**A packing sweep must use a non-output instruction.** That is the one design
constraint the next attempt has to respect.

### Built: `rungpack_{xic,equ}_k{01,02,04,08,16,40}` — 12 files

4,000 instructions in every file, packed k per rung (4,000 → 100 rungs), every rung
closed by one `NOP()`. XIC and EQU are both non-output, so no series cascade forms at
any k. Operand text and tag inventory are identical across each arm; the confound gate
reports one moving dimension per pair.

**What the slope says.** Bytes per removed rung, against the NOP-plus-rung cost the
engine already charges. Equal: the instruction weights carry no hidden per-rung share.
Larger: the excess is the per-rung cost folded into every weight, read directly. Two
arms so the answer does not rest on one instruction.

---

## 4. OQ-ALARMCONDREAL — 107 bytes per condition, on a category worth 9.4% of mass

**Promoted from the resolved file.** It was filed there because the per-condition
formula was derived and wired; the disagreement below is unexplained and the exposure
is large enough that calling it closed understates it.

| program | conditions | actual step | predicted step | actual per condition | predicted |
|---|---:|---:|---:|---:|---:|
| `export 14` | 400 | 443,128 | 442,400 | 1,107.8 | 1,106.0 |
| `export 08` | 200 | 243,040 | 221,600 | **1,215.2** | 1,108.0 |

**Within 0.16% on one file and 8.8% short on the other** — and that is **19% and 21%
of total controller memory** respectively, the second-largest category in both.

**The step is clean.** An exhaustive element-tag diff of each full export against its
alarm-free sibling shows `AlarmCondition`, `AlarmConfig`, `HMIGroup` and the
`AlarmConditions` container are the **only** elements that differ. No tags, rungs,
routines, programs, UDTs or AOIs moved.

**This is not a scale error — the two files disagree with each other**, on the same
wired formula, with every condition in both hanging off a single BOOL array tag. So
something differs between them that the formula does not see.

**Two caveats on the numbers.** Both readings came from files derived from real
exports, which were later found not to import — so **re-derive before citing them
further.** The per-condition formula itself rests on a 37-file generated batch and is
unaffected.

**What is untested:** alarms on a UDT-scalar host (a handful of real conditions sit on
a UDT rather than a BOOL array, and the batch only covers array hosts), and whether
alarm **sets** carry their own cost — the operator and rollup inclusion flags are true
on every real condition and no file varies them.

**What the eighteen real exports say, counted in the final review.** 4,655 of their
4,663 alarm conditions are exactly the shape the generated sweep already prices — TRIP,
severity 500, array-indexed input on a BOOL array host, three associated tags and an
HMI group of at most 15 characters. The other 8 are inherited from a type-level
definition in one program. **No real program uses alarm sets or any other condition
type**, so neither untested item above has real exposure. And the whole-program
results argue against the 8.8% figure: export 08, the file it came from, is predicted
**+0.24%** overall with alarms at 21% of its memory — an 8.8% alarm under-charge would
put it about 1.8% low.

**Built: `alarmcond_realcount_n{000,200,400,600}`** — the real shape at real counts,
host and associated arrays fixed at 640 so only the condition count moves. The existing
real-shape sweep is exact (a flat +16 file residual) but stops at 128 conditions; this
is the check that the law holds where real programs actually sit. If it does, the
question closes.

**Do not confuse this with the ALMD instructions**, which are parked with zero
occurrences in the real set, or with an ordinary scheduled program named for alarms.
One real program carries both this and such a program.

---

## 5. OQ-BUILDFAIL-OPEN — the defect log

Kept visible on purpose. Full diagnostic rules and root-cause reference are in
`OPEN_BUILD_ERRORS.md`; this entry exists so the errored rows have an owner.

**What is genuinely still failing, and what each would buy:**

| file | what it measures |
|---|---|
| `almd_minimal`, `almd_realtext` | **ALMD instruction cost.** The other alarm mechanism, still completely unmeasured. Parked while ALMD has zero real occurrences, so low priority despite being unmeasured. |
| `eventtask_axiswatch` | EVENT-task trigger cost. |
| `modulerack_kinetix_full_bus` | Never captured at all — the recorded error count has no row behind it. |

**What is needed:** the real Studio error line. **Nothing in this repo diagnoses any
of them** — the generators' own comments are silent, so the cause must come from the
error log rather than a guess. **Guessing is what produced the invented alarm
condition types, all four of which failed.**

The 2198 drive half of this entry **closed without needing an error log**: those files
no longer exist, and a later sweep superseded them with 18 clean captures covering
all six catalogs at three module counts each. **The measurement was already on
disk.** Check for that before asking for an error line.

**CAPTURE ERRORS: 4 row(s)** flagged here by `scripts/capture_errors.py`.

None is worth a new file. `almd_minimal` is the ALMD instruction, parked by
`CLAUDE.md` (one use across eighteen real programs). `instrfirst_mapc_x10` is the old
MAPC build whose bug `instrfirst_mapc_v2` / `_v2_x10` fixed — both captured clean, and MAPC is now wired EXACT from them.
`instrfirst_crout_x10` errored on all 80 rungs; CROUT is a Safety-family
instruction, out of scope under OQ-SAFETY and **ignored** — zero uses in the eighteen
real programs, and no rebuild will be made. `predefprobe_axis_generic`'s file no longer exists. The three
other `predefprobe_*` files that failed import four times each were retired: their
types occur in none of the real programs.

Six captured **with** Studio build errors, so their actual figures are **suspect
rather than wrong** — part of the file may never have reached the controller, which
inflates apparent over-prediction. **None carries any error text**: every errored row
in the manifest predates the error-log reader, so these need **recapture** before
their numbers are used. Plus committed files attempted and never reached `ok`.

Run `python scripts/capture_errors.py --list` for the current row identities rather
than reading a list here, which goes stale.


---

## 6. OQ-MODULENAMELEN — a module's NAME length costs bytes the engine charges at zero

**The measurement.** Two committed isolation files, both a 1756-L81E with a single
2198-P208 under the local rack, no tags and no axes. They differ in exactly one
thing: what the module is called.

| file | module name | chars | actual | predicted | delta |
|---|---|---:|---:|---:|---:|
| `modulemotion_p208_baseline` | `P208` | 4 | 22,136 | 22,136 | **0** |
| `modulesweep_2198_p208` | `TestMod1_2198P208` | 17 | 22,160 | 22,136 | **−24** |

Both captured with `error_count = 0`. The controller name is 17 characters in both,
so it is not that. **+13 characters of module name is worth +24 bytes**, and the
engine charges nothing for a module name at any length.

**Why this is not already answered.** Identifier name length is priced for tags, for
UDT type names, for AOI type names and for custom string type names -- four separate
laws in `memory_model.yaml`, all of them a step of 8 bytes per bucket. None of them
applies to a `<Module Name=...>`, and no sweep has ever varied one.

**Why it is not wired.** One pair is one equation. A step of 8 bytes per
`floor(len / 4)` bucket reproduces +24 exactly, and so do several other shapes --
that is two points against a two-parameter family, which this project has already
been burned by. The existing name-length laws bucket by 8 characters, not 4, so
matching them would predict +16, not +24. Something is different here and one pair
cannot say what.

**Consequence for confidence.** `2198-P208` reads ASSUMED rather than KNOWN, and so
do the other flat-fitted 2198 supply catalogs. That is correct and should not be
overridden: its two isolation captures do not agree with each other, and until the
name term is priced, a P208 in a real file is predicted exactly only when its name
happens to be short. The frequency of the catalog in real programs is not evidence
about the constant -- only an isolation capture is.

**Built: `modname_p208_len{04,06,08,10,12,13,16,17,20,24,32,40}`** — one 2198-P208,
no tags, no axes, only the module name length moving. Lengths include 6, 10, 13 and 17
because the task-name finding (OQ-TASKNAMEROUND) showed only non-multiples of 8 can
tell a round-up rule from a round-down one. It reads the step directly instead of
fitting it.

**Exposure before building anything.** Real programs carry 20-60 modules each. At
24 bytes for a 13-character name this is on the order of a kilobyte per file against
a residual of tens of kilobytes, so by the noise-floor rule it does **not** earn a
capture slot ahead of the literal-operand batch. It is recorded because it explains a
specific wrong-looking confidence tier, not because it is worth a session.
