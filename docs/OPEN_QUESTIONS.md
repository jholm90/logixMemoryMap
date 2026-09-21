# Open Questions

**Eight.** Down from forty, and the thirty-four that went were not abandoned — they
were **bounded**. Closed questions and their reasoning trails are in
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
That is why thirty-four closed at once.

## What is left, and why each survives the ceiling

| question | why the ceiling does not bound it |
|---|---|
| **OQ-LITERALOPERAND** | Answered by capture. Integer literals are free; what survives is an engine over-charge on narrow-integer literals. |
| **OQ-REALUNDER** | It *is* the residual. The ceiling bounds every proposed explanation without closing the gap. |
| **OQ-RUNGSHAPE** | A per-rung term the model does not have, perfectly confounded with every per-instruction weight. |
| **OQ-ALARMCONDREAL** | A 9.4%-of-mass category that is 8.8% short on one real file. Not a scale error — the two files disagree with each other. |
| **OQ-EXPORTSCOPE** | A correctness requirement, not an accuracy question. |
| **OQ-BUILDFAIL-OPEN** | A defect log. Kept visible on purpose. |
| **OQ-MODULENAMELEN** | A term the engine charges at zero, measured on a clean isolation pair. Not a scale error. |

---

## 1. OQ-LITERALOPERAND — an immediate literal in an operand costs bytes the engine charges at zero

**The measurement.** One rung in one project, edited in Logix Designer, compiled by
Studio, Capacity read twice. Six MAM operand slots changed from a tag reference to
the immediate `99.99`:

    74,224  →  74,248   = +24 over 6 slots = +4.000 per slot, six for six

**The four source tags stay declared AND referenced in both versions**, by four EQU
instructions on the same rung. So this is not a tag being deleted — it is the same
tag population with six slots re-pointed at inline constants.

**The engine charges nothing.** Run on both rung texts it returns 320 bytes either
way — a zero delta against a real 24.

**It is not a new constant.** The CPT model already carries 4 per float literal,
fitted across 12 files. The same 4 now appears in MAM, an unrelated instruction on
an unrelated code path. **One constant appearing independently in two unrelated
places is what a general law looks like**, not a per-instruction quirk. Today
literals are priced only inside CPT expressions, CMP operands and ST statements.

**Exposure across the seventeen**, counting numeric literals in operand slots of
instructions that are not CPT or CMP:

| | count | at 4 bytes |
|---|---:|---:|
| integer literals | 51,265 | 205,060 |
| float literals | 930 | 3,720 |
| **total** | **52,195** | **208,780** |

**12.1% of all 432,850 operand slots**, and about a quarter of the total residual.
Every one of the seventeen carries between 8.8% and 16.2% literal slots, so this is
not one file's quirk. Top carriers: MOV 9,835, EQU 9,089, ADD 5,259, NEQ 3,132,
COP 2,841, JSR 2,631.

**What charging it does**, float held at the measured 4 and integer swept:

| int cost | mean | max | <1% | <2% |
|---:|---:|---:|---:|---:|
| baseline | 1.5951 | 3.6309 | 4/17 | 11/17 |
| 0 | 1.5973 | 3.6198 | 4/17 | 11/17 |
| 2 | **1.5818** | 3.3811 | 4/17 | 12/17 |
| 4 | 1.5885 | 3.1424 | 5/17 | 12/17 |
| 6.5 | 1.5951 | **2.9022** | 5/17 | 12/17 |

**Read the max, not the mean.**

- **The max moves, and nothing else has.** 3.6309% → 2.9022%. For scale, the
  cheating ceiling fit only reached 2.5919%. A single mechanistic term gets most of
  that way without fitting anything per-category.
- **The mean barely moves** because the term can only ADD bytes and seven files
  already over-predict. All six worst files improve; all seven over-predictors get
  worse. That is a reason to be careful about the rate, **not a reason to dismiss the
  mechanism** — the mechanism is measured, and the over-prediction in those seven
  files is a separate defect.
- **Mean-optimal is 2, max-optimal is 6.5.** They disagree, which is positive
  evidence that **a single flat rate is the wrong shape** and the cost is
  type-dependent.

**CAPTURE ERRORS: 0 row(s).** The whole BOOL arm, `litop_bool_*`, previously
carried 4. Every rung of all four had failed with *"Invalid number of arguments for
instruction"*, 1,000 errors on 1,000 rungs, so the ladder never compiled and all
four read an identical 20,028. The arm measured nothing, the cause is found and
fixed, and **the four capture rows are cleared** — the files they measured no
longer exist in that shape. Diagnosis below. The regenerated files await capture.

---

## The batch answered it. The law is per-type, and it is mostly zero.

**Arm G first, as the plan required.** The bench rung rebuilt at 1,000 rungs:

    litop_mam_lit_n01000   419,456      six REAL literal slots
    litop_mam_tag_n01000   395,456      the same rung, all tags
                          --------
                           +24,000  =  +24.000 per rung  =  +4.000 per slot

**Six for six, identical to the bench.** The pipeline reproduces a hand measurement
at 1,000× scale, so the rest of the batch can be believed.

**Arm A settles the shape, and it is not what either hypothesis predicted.** One
literal operand slot, literal file minus tag file, 1,000 rungs each:

| operand type | per slot | the engine today |
|---|---:|---|
| DINT | **0** | 0 — correct |
| LINT | **0** | 0 — correct |
| REAL | **+4** | 0 — under by 4 |
| INT | **−52** | over by 52 |
| SINT | **−40** | over by 40 |

**An integer literal is free.** Not cheap — free, at both DINT and LINT, to the
byte. That kills the exposure this question was ranked on: 51,265 of the 52,195
unpriced slots are integer literals, and they cost nothing. The projected max
3.63% → 2.90% was an artefact of charging 4 for slots that are worth 0.

**A narrow-integer literal is CHEAPER than a tag, and that is an engine defect, not
a literal cost.** A SINT or INT *tag* operand drags in the widening block the model
already charges; a literal needs no widening because it is already the right width
inline. The engine charges the widening either way, so it over-predicts
`litop_type_int_lit_n01000` by **+21.82%** and `litop_type_sint_lit_n01000` by
**+18.67%** while both *tag* files land at exactly 0.00%. Those two rows are the
largest single-file errors in the batch and they are ours, not Rockwell's.

**Value and distinctness are free.** Arm D: `0`, `1` and `2` all identical. Arm C:
all-distinct, all-same and two-repeated all identical. So there is no
per-distinct-value term and no folding of 0/1 — the competing law that a previous
question died on is dead here too, for a better reason.

**The written FORM of a float costs, and it is unpriced.** Arm E: `floatform`
against `small`, same slot count, **+76,000 over 1,000 rungs = +76 per rung**,
engine delta **−50.57%**. That is an order of magnitude above the +4 for a REAL
literal and is a different mechanism — it is about how the constant is written, not
that it exists. One pair, so the rate is not the finding; the existence is.

**A separate finding fell out of arm G.** Both MAM files under-predict — the
all-tag baseline by **−40,000 over 1,000 rungs, −40 per rung**, before any literal
is involved. That is the MAM instruction weight being short, not a literal term,
and `unreconciled.py` flags the pair. It is the larger of the two numbers in that
arm and it belongs to motion sizing, not here.

### What this changes

| | before the batch | after |
|---|---|---|
| mechanism | "a literal costs bytes" | only REAL (+4) and float-form (+76) cost; integer literals are free |
| exposure | 52,195 slots, 208,780 bytes | 930 float slots, 3,720 bytes |
| expected movement | max 3.63% → 2.90% | **approximately none** |

**So this question drops out of first place.** It was ranked on an exposure that the
measurement has removed. What survives is smaller and sharper: a +4 REAL-literal
term, a +76 float-form term needing a second point, and the INT/SINT widening
defect, which is the only one of the three that moves a real number.

### The BOOL arm was a generator bug. Resolved: a call site passes exactly the Required parameters

All four `litop_bool_*` files emitted `LitSensor(Sensor,RawIn,NormOpen,TimeHigh);`
against an AOI whose three parameters were `Required="false" Visible="true"`.
Studio rejected every rung of all four, **including the all-tag control**, so it
was about argument COUNT, not literals.

The rule is `args == Required` exactly, and `Visible="true"` alone creates no call
slot. Across the real exports there are **917 AOI call sites and the argument count
equals the Required count at every one**, while those same exports declare 120
`Required="false" Visible="true"` parameters — so the unanimity is not for want of
optional parameters to pass. One real AOI has three Required and four Visible-only
parameters and is called with three arguments everywhere. Required is not even a
prefix of the parameter list (13 of 48 real definitions interleave), so the
unpassed ones are not merely trailing.

**The "legal arity is a range" reading came from counting conversions, not builds.**
Two generated files wired optional parameters and were counted as evidence because
they converted and returned a capacity number. Conversion performs no ladder
verification, and `litop_bool_*` proves a capacity number is returned even when
every rung errors. Their apparent cost over the definition-only baseline was tag
storage for the argument tags, not compiled rungs. Both files are deleted, and
`gen_aoi_required_visible.py` no longer emits that shape.

Wired:

- `lint.py`'s `aoi_call_arg_count_mismatch` now requires exact equality with the
  Required count. It previously allowed the range, which is why it passed the
  1,000-rung family that failed to build.
- `gen_literaloperand.py` arm F declares the three parameters `Required="true"`;
  the four files are regenerated and lint clean.
- `AOI_KNOWLEDGE_MAP.md` carries the rule and its evidence.
- The four `litop_bool_*` capture rows are **cleared**, not reused. They measured a
  file that no longer exists in that shape.

No probe file is needed. The four-file Required-count probe proposed here is
withdrawn — the real corpus already answers it at 917 call sites.

**Still open in this arm:** the BOOL literal cost itself is unmeasured. The
regenerated files are awaiting capture.

---

### The JSR band is an artefact. The +280 is found; applying it is blocked by a collinearity

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

**The discriminating test, specified (not generated — no file is to be built from
this without being asked for):**

> Two files, identical in every other respect, differing only in how the same total
> JSR work is distributed across caller routines:
>
> - **A** — 1 caller routine issuing 20 JSR calls to 20 distinct 0-parameter targets.
>   This is the existing `jsr_multi_distinct_targets_n20` shape and its capture
>   (25,472) can be reused; no new file needed for this arm.
> - **B** — 20 caller routines, each issuing 1 JSR call to 1 distinct 0-parameter
>   target. Same 20 targets, same 16-character target names, same rung content,
>   same tag inventory. Only the caller count moves.
>
> One file. B − A is 19 extra caller routines. If the residual stays at −280, the
> over-charge is per file. If it goes to −5,600, it is per caller routine. Nothing
> else in the model distinguishes them, and no amount of re-fitting the existing
> corpus will.

Hold `jsr_fixed_base_per_routine` at 5,096 until that reads.

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


**Why this measurement is trustworthy where the strip ladder was not:** it was made
by editing a project in Logix Designer and letting Studio compile it, not by
rewriting exported XML. That is the path the read-only rule explicitly leaves open.

---

## 2. OQ-REALUNDER — the residual itself

**+822,938 bytes on 55,430,980 = +1.485%.** Ten files under-predict, seven
over-predict.

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

**A term not proportional to any category the engine counts.** That was a hypothesis
with zero measured support until OQ-LITERALOPERAND supplied some. It is the only
live lead.

### The structure that is still unexplained

The ratio of residual to `routine_logic` bytes is **bimodal** across the real set,
and nothing explains why. It is not a per-unit error — the coefficient of variation
is 1.74 per instruction occurrence, 1.72 over the top four instructions, and 1.73
per rung. **Whatever it is does not scale with any count the engine has.**

### The instrument that could have found the rest is gone

Attribution by subtraction from a real export is **dead** by the read-only rule, not
merely difficult. And no generated file can carry content that generated files do not
have, **which is the definition of the gap.**

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

**Do not confuse this with the ALMD instructions**, which are parked with zero
occurrences in the real set, or with an ordinary scheduled program named for alarms.
One real program carries both this and such a program.

---

## 5. OQ-EXPORTSCOPE — what a partial export costs on import

Studio exports at six granularities. **The scope machinery is wired**: a partial
export gets no project base load, no firmware, catalog or safety baseline delta and
no task/program shell, and its total is reported split three ways — target, context
and project. The rules are in `MEMORY_MODEL.md`.

**What remains open is a different question with no data at all: what a partial
export costs when it is IMPORTED.**

- **A Program export's own shell.** Importing a program creates a program, and the
  marginal cost of an extra program in a whole project is known — but that constant
  was fitted across whole-project captures and has never been checked against
  "import one program into an existing project." **Charging it here would be a guess,
  so nothing is charged.**
- **A Routine export's own shell**, same argument.
- **A Rung export** creates no structural container at all, so arguably zero.
  Untested.
- **The context/target boundary in bytes.** Context declarations cost their bytes
  only if the destination controller does not already have them. Whether Logix
  charges anything for reconciling an already-present declaration is unknown.

**Test shape needed:** export one program from a known project, import it into a
second known project, read Capacity before and after. **That is a
controller-in-the-loop test, not a file-generation one** — it needs a controller at
the bench, not a generator run.

This is a **correctness** requirement rather than an accuracy one. It does not move
the real-file number, and it is not bounded by the ceiling because it is not a
category scale.

---

## 6. OQ-BUILDFAIL-OPEN — the defect log

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

**CAPTURE ERRORS: 7 row(s)** flagged here by `scripts/capture_errors.py`.

Six captured **with** Studio build errors, so their actual figures are **suspect
rather than wrong** — part of the file may never have reached the controller, which
inflates apparent over-prediction. **None carries any error text**: every errored row
in the manifest predates the error-log reader, so these need **recapture** before
their numbers are used. Plus committed files attempted and never reached `ok`.

Run `python scripts/capture_errors.py --list` for the current row identities rather
than reading a list here, which goes stale.


---

## 7. OQ-MODULENAMELEN — a module's NAME length costs bytes the engine charges at zero

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

**What would settle it.** One sweep, module name length 4/8/12/16/20/24/32 on a
single fixed catalog, everything else held. Seven files, differences against each
other, no model involved. It reads the step directly instead of fitting it.

**Exposure before building anything.** Real programs carry 20-60 modules each. At
24 bytes for a 13-character name this is on the order of a kilobyte per file against
a residual of tens of kilobytes, so by the noise-floor rule it does **not** earn a
capture slot ahead of the literal-operand batch. It is recorded because it explains a
specific wrong-looking confidence tier, not because it is worth a session.
