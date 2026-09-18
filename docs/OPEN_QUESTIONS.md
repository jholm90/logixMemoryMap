# Open Questions

**Six.** Down from forty, and the thirty-four that went were not abandoned — they
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
| **OQ-LITERALOPERAND** | A term not proportional to any category the engine counts. Measured, not hypothesised. |
| **OQ-REALUNDER** | It *is* the residual. The ceiling bounds every proposed explanation without closing the gap. |
| **OQ-RUNGSHAPE** | A per-rung term the model does not have, perfectly confounded with every per-instruction weight. |
| **OQ-ALARMCONDREAL** | A 9.4%-of-mass category that is 8.8% short on one real file. Not a scale error — the two files disagree with each other. |
| **OQ-EXPORTSCOPE** | A correctness requirement, not an accuracy question. |
| **OQ-BUILDFAIL-OPEN** | A defect log. Kept visible on purpose. |

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

**NOTHING IS WIRED, and the reason is specific.** The 4 is measured for a REAL
literal in a REAL-typed motion parameter — 930 of the 52,195 slots, worth 3,720
bytes. **98% of the mass is integer literals and the measurement says nothing about
them.** Charging 51,265 slots at a rate extrapolated 55× beyond its evidence is the
move that has produced every bad constant in this project.

**The hypothesis:** an immediate costs the width of its type, inline — REAL 4
(measured), DINT 4, INT 2, SINT 1, LINT 8. The competing hypothesis is that it
follows the **slot's** declared type rather than the literal's.

**29 files built**, seven arms, awaiting capture. See `SAMPLE_GENERATION.md` for what
each arm discriminates and the order to read them in.

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
| `griffin_stackerline` | 400 | 443,128 | 442,400 | 1,107.8 | 1,106.0 |
| `elmsdale` | 200 | 243,040 | 221,600 | **1,215.2** | 1,108.0 |

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
