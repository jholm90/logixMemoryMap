# Resolved Questions

Every closed sizing and behaviour question, with the verdict and the evidence.

**Check this file before repeating an investigation.** Its purpose is to stop a
question being re-asked, and especially to stop a refuted answer being re-derived —
several of the entries below record a formula that fitted its own data perfectly and
was wrong.

Constants live in `MEMORY_MODEL.md`. Open questions are in `OPEN_QUESTIONS.md`.

## The four ways a question closes here

| | |
|---|---|
| **SOLVED** | A measured law, wired, with the residual stated. |
| **CLOSED NEGATIVE** | The suspected effect does not exist. As valuable as a law — it stops the search. |
| **BOUNDED** | The effect is real and too small to matter. Closed without being solved. |
| **OUT OF SCOPE** | Deliberately excluded. Not a data gap. |

**Thirty-four questions closed at once on one finding.** An eight-parameter
per-category fit, fitted directly on the held-out real programs — cheating, an upper
bound no honest procedure can beat — reaches mean 1.01% / max 2.59% and still fails
the stopping rule; under leave-one-out it is worth 0.007 percentage points. **So
every question whose mechanism was "a cost constant is slightly wrong" has a measured
maximum payoff of approximately zero**, however cleanly it would have answered.

## A closed question can still own errored capture rows

The rows outlive the question. Where that happens the count is recorded in the
entry, because an error with nowhere to be recorded is an error that gets forgotten.
`scripts/capture_errors.py` enforces it.

---

# Tags, UDTs and strings

## OQ-BITSHIFT — BSR and BSL both cost exactly 60 bytes; the length operand is free

**SOLVED.** The assumed weight was right, and it is now measured rather than assumed.

All 15 files converted and captured with **0 errors and 0 warnings**.

**BSR = exactly 60.000 bytes per rung**, over four independent intervals:

| interval | bytes | rungs | per rung |
|---|---:|---:|---:|
| 10 → 50 | +2,400 | 40 | **60.000** |
| 50 → 100 | +3,000 | 50 | **60.000** |
| 100 → 500 | +24,000 | 400 | **60.000** |
| 500 → 1,000 | +30,000 | 500 | **60.000** |

**BSL is identical to BSR**, not merely close: differenced at equal rung count the
two families agree to **+0 at all five counts** — 19,008 / 21,408 / 24,408 / 48,408 /
78,408, the same numbers on both sides. The shared weight of 60 was an assumption; it
is now a measurement.

**The length operand costs nothing.** Lengths 32, 64, 128 and 256 against a fixed
DINT[8] array all capture at **24,432** — byte-identical, four for four. The array is
priced by the tag sizer; the operand itself is free.

**A per-rung CONTROL costs exactly its own tag storage and nothing more.**
`bitshift_ctlper_n01000` (one CONTROL per rung) minus `bitshift_bsr_n01000` (one
shared CONTROL) is 95,904 over 999 extra tags = **96.000 bytes each**, which is the
CONTROL tag size the model already charges. There is no per-instruction surcharge for
giving each rung its own control structure.

**Engine agreement: all 15 rows predict at −4 bytes**, inside the ±8
single-measurement noise floor. Mean |error| 0.0138%.

**Effect on reporting.** `instruction_accuracy` now carries `BSR {samples: 3,
worst_pct: 0.0083}` and `BSL {samples: 2, worst_pct: 0.0083}`, putting both in the
**Measured ±0.1%** band. The real routine that motivated the question — two BSR rungs
carrying 58% of its compiled size — moves from *Unverified, unbounded* to Measured
over those bytes.

**No sizing constant changed.** `BSL: 60` and `BSR: 60` stand as written; what changed
is that they are no longer assumptions.

**Two design errors caught before capture**, recorded because they are this project's
recurring failure mode: arm A originally declared one CONTROL per rung, moving tag
inventory with instruction count; arm C originally moved array size with the length
operand. `confound_check.py` refused both before any file was submitted.

## OQ-ALIGN — UDT member padding

**SOLVED.** No alignment padding between members at all. `BOOL, DINT, BOOL` = 6
bytes; `DINT, BOOL, BOOL` = 5. A run of consecutive BOOLs shares one backing byte and
**a non-BOOL member breaks the run**, forcing the next BOOL onto a fresh byte.
Confirmed against real capacity data across every UDT sweep, and the implementation
already produced it. Confidence flipped UNKNOWN → KNOWN.

## OQ-TAGOVERHEAD — per-tag flat cost

**SOLVED.** `84 + 8 × floor(name_len / 8)`, additive with the tag's own data size.
Tag names are stored in 8-character chunks. **Two independently derived measurements
agree exactly**, which is why this is KNOWN rather than FITTED. Type barely affects
it and is treated as type-independent.

## OQ-ALIASSIZE — do alias tags cost anything

**SOLVED, and it reversed the previous answer.** An alias costs
`56 + 8 × floor(name_len / 8)` — the same 8-character bucket shape as an ordinary
tag, with its own flat base and no data term. Exact across all three buckets tested.

> The earlier claim of zero was wrong. It correctly observed that an alias has no raw
> data size and **incorrectly concluded that meant no cost.** Roughly 21% of a real
> program's tags are aliases, so this was not an edge case.

## OQ-SHELLCONST — the standalone atomic tag data slot

**SOLVED.** A standalone atomic tag's data occupies a **fixed 4-byte slot regardless
of declared type.** SINT and INT are padded up to it; LINT is reported in it rather
than the 8 its value needs. Six bare 50-tag files, one type each, zero residual on
all six.

**This is what a large bucket of files sitting at exactly −5 had been.** Their tag
pool was 5 each of SINT/INT/DINT/LINT/REAL: −15 −10 +0 +20 +0 = −5 exactly, on every
file regardless of instruction. It was also most of the bytes behind the corpus's
largest residual bucket.

Arrays and structure members are deliberately untouched — this is a per-**tag** slot
rule, and a test asserts `SINT[100]` stays exactly 300 bytes smaller than `DINT[100]`.

## OQ-UDTTAGSLOT — is a standalone UDT tag's slot padded

**SOLVED.** Padded to 8 bytes, alongside a −4 extra. Derived from the one place two
captured families disagreed about what a single UDT tag costs — and they disagreed
only because they sit on opposite sides of that boundary. **Neither constant is
separable from either family alone.**

Arrays are deliberately untouched: padding elements instead improves the real files
more and destroys the tags category, so that gain is absorbing some other missing
term.

## OQ-UDTMEMBERNAME — do UDT member names cost anything

**SOLVED, and it was the largest single real-file gain in the project.** They cost an
8-aligned pool: `8 × ceil(Σ(len + 1) / 8)`. They were charged **nothing**.

**A raw one-byte-per-character rate fits five of seven measured points and misses
two.** That pair is the entire discrimination between the two forms — any sweep whose
name lengths share a residue mod 8 cannot tell them apart, which one follow-up batch
demonstrated by being unable to.

Cross-checked flat in tag count (so per definition, not per instance), and agreeing
across member counts and member types. Real UDT member names average about 12
characters and a real program carries on the order of 174 definitions.

## OQ-UDTBOOLMEMBER — superseded by OQ-UDTMEMBERNAME.

## OQ-NESTEDUDT — **SOLVED.** A nested UDT member's size is that UDT's own total, recursed, with cycle detection. Only BOOLs pack, so a nested UDT always starts fresh. True by construction — no code path merges it into a preceding partial byte.

## OQ-ARRAYPACK / OQ-UDTARRAYALIGN — array element rounding

**SOLVED.** Array of UDT: `dimension × ceil(udt_size / 4) × 4` — each element rounds
up to 4 bytes, no padding beyond. Confirmed at five counts for a 3-byte-tight UDT and
for an already-8-byte UDT where the rounding is a no-op. **Atomic-type arrays are not
subject to this rounding.**

## OQ-BOOLPACK / OQ-BOOLARRAY — BOOL storage

**SOLVED for the distinction that matters.** A BOOL **array** bit-packs into
DINT-sized words, `ceil(dimension / 32) × 4`. A standalone BOOL **tag** does not — it
takes 4 bytes. **Do not conflate the two.** The array rule stays ASSUMED: it is
standard documented behaviour but this project has not validated it with its own data.

## OQ-TAGORDER — does declaration order matter

**CLOSED NEGATIVE. Order is free.** Raised from outside the model: "BOOL LINT INT
DINT BOOL takes up different space than another order." It does not.

Six files hold the same 400 tags with identical names and move nothing but the
sequence — grouped, wide-first, narrow-first, alternating, pairs, shuffled. The
engine, which has no order term, predicted all six at 56,528. **All six captured at
56,528.** That covers the widest span the multiset allows.

## OQ-TAGSHAPE — is the residual in tag data space

**CLOSED NEGATIVE, and this one matters most.** `controller_tag` is 60% of predicted
mass, which made it the obvious suspect. **Every real tag shape is already covered**,
and the untested ones total a few thousand bytes against a residual two orders of
magnitude larger. The name-length term — the strongest-looking candidate — is cleared
by 88 clean rows at mean 0.12%.

**The residual is not in tag data space.**

**CAPTURE ERRORS: 1 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the row outlives it, so the count is recorded here
rather than lost.

## OQ-STRINGTAGOVERHEAD / OQ-STRINGTAGOVERHEAD-BUILTIN — **SOLVED.** A built-in STRING tag costs exactly 2 bytes **less** than the ordinary per-tag formula predicts. Exact across a 9-point count sweep and a 4-point name-length cross-check: always `−2 × count`, independent of both.

## OQ-CUSTOMSTRING / OQ-CUSTOMSTRINGDEF — custom string types

**SOLVED, and it found a real bug.** The DATA member was sized raw with no rounding.
**DATA rounds to the nearest multiple of 8, rounding DOWN at the exact tie.** Verified
exact against nine maxlen points spanning every mod-4 and mod-8 remainder: 50 and 51
measure byte-identical, 100 is a tie and drops, 101 is already aligned and stays.

**One rule fully explains the real per-tag rate** — no separate correction needed.

The type definition itself costs a clean step function in its name length, exact
against 22 of 22 dense points, plus 8 more when maxlen ≡ 1 mod 4 (exact at 3 of 3).

## OQ-STRINGUDTMEMBER — **CLOSED NEGATIVE.** A built-in STRING as a UDT member needs no correction at all. The disentangling points already had unreconciled capture data showing so.

## OQ-STRINGARRAYPAD / OQ-CSARRAYBASE / OQ-STRARRAYLARGEN — **SOLVED and wired.** Array-of-STRING padding follows the same rules.

## OQ-STRINGCONSTFAIL — **RESOLVED as a generator bug**, not a sizing question. A double underscore in a padded tag name, from a filler ending in `_` abutting a numeric suffix.

## OQ-MIXEDUDT / OQ-LARGEMIXED — **CLOSED.** Mixed-type UDTs follow the same packing and definition rules as single-type ones. No interaction.

## OQ-TAGSCOPE — **CLOSED.** Program-scope tags size identically to controller-scope tags. Scope affects only where the entry lives.

---

# Add-On Instructions

## OQ-AOIINSTANCE — how an AOI-typed tag sizes

**SOLVED.** Every AOI-typed tag in a real export is a plain named Tag sized
identically to a UDT-typed one. Input, Output and LocalTags are storage; **InOut
parameters are excluded entirely** — an InOut is a reference to the caller's tag, not
separate storage.

That also answers whether a parameter duplicates the referenced tag's memory: **it
does not, because it is never sized.**

Engine error on the real corpus fell from 41.6% to 29.5% to 8.8% as this and the
predefined structures landed.

## OQ-AOIDEF — AOI type-name length

**SOLVED.** `8 × max(0, (len − 8) // 4) − 8`, exact at seven points.

> **The first divisor tried reproduced all seven points and was still wrong**, putting
> one length a whole bucket too high. It was caught only by cross-checking two
> unrelated files that differed solely in AOI type-name length. **Seven points
> agreeing does not pin a bucket boundary.**

## OQ-AOIDEFITEMIZE — the priced cost versus the itemised breakdown

**SOLVED as one itemised form.** The definition cost and its own member breakdown were
two different computations that disagreed on every real AOI. Now one form: a base, 12
per declared member, each member's own data bytes, 24 per 32-bit word the BOOLs
occupy, an 8-aligned name pool, and the type-name term.

Measured on **124 definition-only files** — no instance tag and no internal rungs, so
the definition is the only AOI cost in the file. **70 land exactly, 122 of 124 inside
±8.**

**The residual's shape makes it look like a per-member constant, and it is not** —
worth knowing, because that is exactly the wrong fix to reach for.

**This replaced four separate fitted terms that had each absorbed part of the same
error.** Every one fitted its own sweep exactly. `MEMORY_MODEL.md` records what each
was really measuring, which is the part worth keeping.

**CAPTURE ERRORS: 40 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-LITERALOPERAND — an immediate literal in an operand costs bytes the engine charges at zero

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


---


**Why this measurement is trustworthy where the strip ladder was not:** it was made
by editing a project in Logix Designer and letting Studio compile it, not by
rewriting exported XML. That is the path the read-only rule explicitly leaves open.

### Closed: every surviving term is under the noise floor

**BOUNDED.** The last live item was the INT/SINT literal over-charge, held open until
it could be counted on the real programs. Counted on all eighteen real exports now
available: the measured shape, `MOV(<integer literal>, <INT or SINT tag>)`, occurs
**37 times in total — 23 INT, 14 SINT — for 1,756 bytes of over-charge across
eighteen programs**, about 100 bytes a program and 0.002% of one. The worst single
program carries 784 bytes. Wiring it would move nothing a user could see, so it is
closed without wiring, which is the noise-floor rule doing its job.

What remains is recorded, not pending:

| term | per | real exposure | status |
|---|---|---|---|
| integer literal (DINT, LINT) | slot | 51,265 slots | **free, measured** |
| REAL literal | slot | 930 slots, 3,720 bytes | +4, below the floor |
| float literal FORM | rung | one pair only | +76, below the floor, needs a second point before any rate is believed |
| INT / SINT literal into `MOV` | slot | 37 slots, 1,756 bytes | engine −52 / −40 high, below the floor |
| BOOL literal into an AOI call | slot | 128 real call sites | regenerated `litop_bool_*` files lint clean; not worth a capture slot on this exposure |

The projected max 3.63% → 2.90% that ranked this question first was an artefact of
charging 4 bytes to integer literals that cost nothing. **The hypothesis that
unpriced literal content carries the real residual is refuted.**


## OQ-TASKNAMEROUND — a task name rounds up where the identifier term rounds down

**BOUNDED.** `task_extra` is exact at 2, 3 and 6 tasks — `taskoverhead_n02tasks`,
`_n03tasks` and all five `identnamelen_task_c*` files — and the task/program shell is
KNOWN on that evidence. The one miss, `taskoverhead_n04tasks` at **+24**, is not
`task_extra`: its three extra task names are 13 characters, the only
non-multiple-of-8 task name ever captured. The identifier term rounds 13 down to 8;
the file reads as if a task name rounds up to 16. Three names × 8 = 24, exactly.

Rounding task names up fits all six task-name points (4 → 8, 8 → 8, 13 → 16, 16, 32,
40), and it would retire the `task_min_bytes` special case, which exists only to make
a round-down law read 8 at length 4. It is not wired: at most 8 bytes per task, and a
real program has a handful of tasks, so it is under the noise floor. Program and
routine names are **not** covered by this — every captured program or routine name
length is a multiple of 8 or sits inside the per-routine constant, so which way they
round at other lengths is untested.

## OQ-AOIDEFSHAPE — the AOI definition's residual

**SOLVED for the 4-byte half, BOUNDED for the 8-byte half.** `aoi_definition` is now
**KNOWN.**

**The 4-byte half: the definition is 8-byte aligned.** The entry that used to stand
here reported 0 on 70 files and +8 on 35. Re-run against the live engine, the same
125-file instrument had drifted to four values — 0 on 8, **+4 on 53**, +8 on 23, +12
on 21 — which is the "re-run the census after any shared change" failure mode caught
late. The split is exactly the unaligned sum's value mod 8: every file the formula put
at 4 mod 8 read 4 bytes high, every file at 0 mod 8 read as predicted.

Aligning `(sum + 1)` up to 8 and removing the 1 again — the same project-wide 1-byte
offset the array-member terms carry — fixes it:

| | before | after |
|---|---:|---:|
| instrument files exactly 0 | 8 | **68** |
| inside the ±8 noise floor | 94 / 125 | **117 / 125** |
| mean \|residual\| | 6.99 B | **4.48 B** |
| every clean AOI-bearing capture, exactly 0 | 38 | **201** |
| every clean AOI-bearing capture, inside ±8 | 295 | **506** |
| non-AOI captures moved | — | **0** |

16- and 32-byte alignment were tested and are strictly worse. It is the same mechanism
and constant as OQ-AOIBOOLPACK-PAIRING below, found independently on the instance
side — the cross-check that this is real rather than fitted.

**The 8-byte half: bounded, not solved.** 47 instrument files still read +8. No single
feature separates them from the 68 at zero: AOI name length leans toward it at 14–16
characters — the bucket boundary the name-length sweep never sampled — and so does
controller name length at 6–7 mod 8, but neither splits the groups cleanly. It is
**exactly the ±8 single-measurement noise floor**, which the project treats as
agreement, and it is not worth a capture slot.

**The eight outliers** are named shapes: a MOTION_INSTRUCTION local (+48), BOOL-array
locals (+16, deliberately unpriced — OQ-AOIARRAYLOCALTAG), and one three-deep nesting
(−16). None is common enough in the real set to clear the noise-floor rule.

**Why KNOWN.** Measured alone on 125 def-only captures, with every residual inside the
noise floor except those named shapes — the project's written rule for a known
constant. The name-length term meets the same rule on its own (seven lengths, 7/7
exact; the unsampled boundary can be wrong by at most one 8-byte bucket). Pinned by a
test.

## OQ-AOIREALSHAPE — does the AOI model hold at real population shape

**BOUNDED. The per-definition cost is confirmed at real shape; the per-member cost is
1.8 bytes high.**

`gen_realshape_aoi.py` built 15 files reproducing a real export's AOI population —
19 definitions, 453 parameters, 280 locals, 349 internal rungs — and ladders that move
one kind of content at a time. All 15 captured clean. **They were never differenced
until the final review**, which is the backlog failure the capture checklist warns
about.

| ladder | what moves | actual per unit | predicted per unit |
|---|---|---:|---:|
| `mbshape_defs_n{05,19,40}` | same members over 5 → 40 definitions | **1,231 / definition** | 1,233 |
| `mbshape_params_{05,10,20}` | 229 → 906 parameters | **20.3 / parameter** | 22.2 |
| `mbshape_locals_{05,10,20}` | 137 → 560 locals | **20.4 / local** | 22.2 |
| `mbshape_rungs_{05,10,20}` | internal rungs | flat — exact | flat |
| `mbshape_axis_k{0,3}` | three AXIS_CIP_DRIVE parameters | +8 difference | — |

- **The per-definition cost is right at real scale.** The generator's key
  discriminator came back per-member, not per-definition.
- **The per-member cost is 1.8 bytes high** on BOOL-heavy real mixes (about half the
  members are BOOL). On the real export this population was copied from — 733
  members in a 923 KB program — that is about 1.3 KB, **0.14%**, under the
  noise-floor rule. That export now over-predicts by 1.17% (10.9 KB), so this
  over-charge is roughly an eighth of its residual.
  Instance and definition charges move together in these ladders, so the 1.8 cannot be
  split between them without a def-only twin; not worth a slot.
- **The axis-parameter charge is right.** The generator flagged 22,656 bytes per axis
  parameter as "very likely wrong". Three of them move the file by 8 bytes against the
  prediction.
- **Internal rungs are exact** at real count.

**The control file does not reproduce the real export's under-prediction.**
`mbshape_asbuilt` over-predicts by 1,448 bytes (2.3%), where the real export it copies
was under-predicted by about 7% when this family was built. So that under-prediction
did not live in its AOI population — the hypothesis the family was built to test is
refuted. (Other fixes have since moved that export to a 1.17% over-prediction.)

## OQ-AOIBOOLPACK-PAIRING — instance-array packing

**SOLVED, after two wrong readings that are both instructive.**

The answer: **the whole instance-array block is padded to an 8-byte boundary**,
`8 × ceil(n × per_instance / 8)`. The extra 4 bytes appear exactly when
`per_instance ≡ 4 (mod 8)` and never otherwise. **48 of 48 captured families agree
with zero exceptions**, over 17 distinct per-instance sizes. Same mechanism and same
constant as the predefined array structures' element-block padding, which is the
independent cross-check.

Also found: the engine counted packed words as `ceil(bool_count / 32)`. **The real
count is `ceil((bool_count + 2) / 32)`** — EnableIn and EnableOut occupy two bits in
the same words, and `bool_count` excludes them because they are not declared members.

**Two refuted readings, recorded so they are not re-derived:**

- **`124 − 4 × bool_member_count`.** Zero residual at nine points from 0 to 30 BOOL
  members — about as clean a fit as this project has produced. **Every point came from
  AOIs with the same total member count**, so it could not distinguish a per-BOOL
  effect from one depending on total members. Composition only moved the per-instance
  size; the residue mod 8 was doing all the work.
- **A per-family fixed offset tied to which boundary the packed BOOLs cross**, then
  **a two-variable surface in (bool_count, atomic_count).** Both wrong.

## OQ-AOIARRAYDIMENSION — why an array-parameter file would not import

**SOLVED, and the cause was not a formatting bug.** An array-dimensioned atomic
Input or Output parameter **is not a legal Logix construct at all.** Only
`Usage="InOut"` permits an array parameter.

Two prior fixes — forcing the Required/Visible flags, then building a real array
DefaultData body — were **chasing a formatting bug that never existed.** The real
corpus already showed it: every real array parameter carries both `Dimensions` and
`InOut`, which is now understood as the only possible combination rather than a
coincidence.

The same rule generalises: **an Input or Output parameter is passed by value and
accepts only an atomic type.** Any structure must be InOut.

## OQ-AOIARRAYLOCALTAG — array LocalTag data space

**SOLVED for the main term.** An array-dimensioned declared member costs its own data
space, and the array's bytes **replace** the scalar element size a non-array member
would pay rather than stacking on it.

Computed through the array-size path rather than `element × dimension`, because the
predefined array structures have their own shape and no scalar element size — going
the naive route raised an error on the first real file it met.

**Three residuals recorded rather than fitted:** BOOL arrays measure neither the
packed size nor a two-word rounding and stay deliberately unpriced; an 8-byte discount
applies per array member after the first; and one dimension lands exactly one element
off the line through its neighbours.

## OQ-AOIINTERNALLOGIC — do an AOI's own routines cost anything

**SOLVED.** They were priced at zero. All of an AOI's internal routines are aggregated
into one pseudo-routine — **per-routine count does not matter, only total content** —
and weighted with the ordinary instruction table, with the shell not charged because
the definition's base covers it. Cut maximum residual on the isolation sweep from
12.02% to 0.55%.

**CAPTURE ERRORS: 5 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-AOIORPHAN — does an uninstantiated AOI definition cost memory

**CLOSED NEGATIVE.** A minimal-pair capture confirms the existing no-extra rule is
correct rather than merely assumed — 8-byte residual on the unreferenced file, 0.04%.

## OQ-AOISTRUCT — what an AOI costs as a function of its structure

**SOLVED in part, and it is the entry that matters most for other people's code.**

The definition form prices a finite list of properties, and the generated corpus
barely exercises several that real AOIs have in quantity: member name length (mean
12.1 characters), member descriptions (803 of 2,120 real members have one, the corpus
generated none), InOut parameters, predefined-struct members (hundreds of real TIMER
members, none generated), array dimensions, counts far past the fitted range, and
extra internal routines.

**Why it matters more than the byte counts suggest:** a correction fitted against the
AOIs that recur across the real projects — the byte-identical shared ones — **would
score well on the real set and be worthless on someone else's.**

**So: never fit anything to a specific AOI name.** Cost models must be functions of
structure. See `AOI_KNOWLEDGE_MAP.md`.

## OQ-AOIGEN — **CLOSED.** AOI cost generalises across shapes once the itemised form replaced the per-type rates. The apparent non-additivity was the name-pool error surfacing as a composition effect.

## OQ-AOIINTERNAL- — a truncated cross-reference, not a question.

---

# Compiled logic

## OQ-LBLJMP / OQ-LBLJMP-STALE — separating LBL from JMP

**SOLVED, and it is KNOWN at any ratio.** The 1:1 pair is an exact linear fit at 120
per pair across five rung counts. **A 1:1 sweep alone cannot split the pair, however
many counts it covers.** Two further sweeps did: LBL-only rungs isolate LBL+NOP at 80,
so LBL is 64; a fixed-LBL varying-JMP sweep isolates JMP at 40. The cross-check closes
exactly — 64 + 16 + 40 = 120.

**Three independent captures agreeing, with each instruction isolated from the other**,
is why this is KNOWN and valid for any ratio.

An earlier figure of 104 was a miscalculation, not a measurement error — the raw data
was always 120.

## OQ-BRANCHDEPTH — what a branch costs

**SOLVED, with a mechanism rather than a curve fit.** A branch compiles to real
BST/NXB/BND instructions — one BST, one NXB per extra leg, one BND, so
`leg_count + 1` per bracket group — and each costs a flat **4 bytes**. Nested branches
recurse.

Verified exact against all 17 captured points. **The same 4-byte rate explains two
independently built datasets**, not two separate fits.

The bracket counter does a real matching scan, distinguishing a branch-opening `[`
from an array index by the preceding character and tracking paren depth so a
multi-argument call inside a leg is not miscounted as extra legs.

Stays FITTED: tested at one rung count and one tag shape.

## OQ-SERIESOUTPUT — a rung with more than one output in series

**SOLVED as a law, with its competing candidate killed.** `−12 × (outputs − 1)`,
measured at 2, 3 and 4 outputs.

**The ratio hypothesis is dead**, and so is the repetition candidate — a one-rung file
pays the full discount, so the cost cannot depend on repetition, and a later packing
sweep re-measured the law at four new points at exactly −12.000 with every file
distinct, which kills per-distinct-rung too.

## OQ-VERIFINSTR — instruction weights measured but never confirmed at scale

**SOLVED for the zero-operand half.** MCR, TND, UID and UIE each land **exactly at all
five counts from 10 to 5,000 rungs** — 20 of 20 rows, zero residual — so those weights
are confirmed at three orders of magnitude and no longer need a caveat.

The non-exact rows in that family were all the paired shape and belonged to
OQ-SERIESOUTPUT, which they sharpened considerably.

## OQ-INSTRFIRSTPASS / -X10 / -FLATOFFSET — first-pass instruction coverage

**SOLVED, 34 of 36 weights confirmed and wired.** SCP, FBC and PID were the gaps — SCP
had no second real example, FBC and PID no real examples at all. **Closed as out of
scope rather than left open awaiting data that is not coming.**

A flat +12-byte gap across all 64 clean files, about 0.06% of file total, narrowed to
an interaction effect and **not worth reopening the question over.**

## OQ-INSTRUCTIONSCOPE — **CLOSED.** CTD and several others are deliberately untested: zero real usage. Coverage is measured against real usage, not against the instruction set.

## OQ-MAHMSO — **SOLVED.** 60 per rung each, identical real numbers, on the two-operand `(Axis, MotionInstruction)` shape which is **theirs and not a general motion shape.**

## OQ-MAMFAMILY-BUILDFAIL / OQ-CROUT-MAPC-BUILDFAIL — motion build failures

**SOLVED, and one was not a bug at all.**

**MAM, MAJ, MAS and MRP** failed because they were built on MAH and MSO's two-operand
shape. Each needs its own full parameter list — real operand counts 20, 17, 9 and 5.
Fixed by position-for-position transplant from real examples.

**MAPC** needed two **distinct** axis tags — an axis cannot cam to itself. The
type constraint is looser than assumed: any two axis types work, and a
CIP-Drive/Virtual pairing is not required.

**CROUT is not a generator bug.** It is a Safety instruction requiring a safety CPU.
Reclassified OUT OF SCOPE alongside DCS — there is nothing to fix on a standard
controller.

## OQ-BTD — **SOLVED**, along with COP, CPS, FLL and SIZE. All five shared one cause: an array-typed operand emitted without its `[index]`. **Such a file converts cleanly and never compiles at scale**, which is why every one returned an identical byte count regardless of rung count.

## OQ-EMPTYROUTINE — **SOLVED.** A routine's fixed base is 4,816, confirmed identical across 42 instructions; 5,096 for a routine containing a JSR.

## OQ-TASKOVERHEAD — per-task cost

**MEASURED, deliberately not wired.** A clean, exactly −1,472 per extra task. Wiring
it needs a parser change to distinguish per-task and per-program overhead from
per-routine-in-the-same-program, which does not exist. **Recorded rather than
rushed.**

## OQ-SHELLSCALE — task, program and routine shell scaling

**SOLVED, and the answer reversed the question's own conclusion.** The entry predicted
the per-program and per-routine constants were far too **small** — a claimed 10× and 2×
extrapolation failure. The isolation batch says the opposite: **both were slightly too
LARGE, by exactly 8 bytes each.** The routine sweep measures exactly 264.000 per
routine across all seven steps.

**The reversal is the useful part.** An extrapolation inferred from whole-program
residuals pointed the wrong way by an order of magnitude.

## OQ-SAFETYSCOPE-SIZING — safety shells

**SOLVED.** Safety tasks and programs are a separate memory pool. They are excluded
from the ordinary shell aggregate and charged a flat per-file constant instead,
replacing an over-charge. Verified exact against every real safety-processor row at
the lower firmwares, with a known small residual at the higher ones that belongs to the
firmware content gap.

## OQ-XPROGREF — **CLOSED.** A shared alias across programs costs about −16 per rung per additional program. An earlier large negative gap no longer exists against the current engine; the real data had been sitting unreconciled.

## OQ-INDIRECT — indirect addressing

**SOLVED.** A direct array index costs nothing beyond existing indexed-tag handling. A
**tag-driven** index costs roughly 84 per rung and an **arithmetic-offset** tag-driven
index roughly 108. The direct-index case having no cost is why this looked like a
non-effect at first.

## OQ-OPERANDTYPE — does operand data type change instruction cost

**SOLVED, and it bounds every "exact" claim in the project.** It does, substantially,
for 14 instructions. SINT and INT cost +88 to +164 more per rung; REAL costs +16 to
+56 more for some and less for LIM; STRING costs +52 more for EQU and NEQ. **LINT
behaves identically to DINT.**

**Every zero-residual instruction weight is proven only for DINT, LINT and REAL
operands.** A program doing heavy SINT or INT math sizes less accurately than the
coverage table implies.

## OQ-RUNGSHAPE — see `OPEN_QUESTIONS.md`. Partially answered: arrangement is byte-exact at every leg count, so the corpus's branch coverage gap is a fact about the corpus and not an error. The per-rung term remains confounded.

---

# Expressions and Structured Text

## OQ-CMPCPTLAYOUT — CPT and CMP expression cost

**SOLVED across four threads, and one of them corrected a rate that had been applied
universally.**

**CPT is priced per call from its own expression's operator tokens**, not a flat rung
weight. A single flat weight was wrong as a general constant — it was one complex
expression's cost, and applied to a simpler expression it over-predicted one file by
over 300,000 bytes. **The fix was an architecture change, not a constant edit.**

**The extra-operand rate is per tier.** The wired 24 came from a sweep using one
operator throughout, so it was only ever a **tier-1** rate while being charged for
every uniform-tier expression. Uniform tier-2 measures 16 more per operator beyond the
first, with one tier-2 operator already exact to pin the intercept.

**CMP shares the same law.** It was priced as a flat weight plus two boolean
surcharges with **no expression model at all**, so a CMP whose operands are arithmetic
paid nothing for the arithmetic. **No separate CMP fit was needed** — the tier table
fitted on CPT lands on CMP's measured residuals unchanged, which is the evidence they
share one law. Three shapes went from −36, −36 and −100 to exactly 0.

Comparison operators and the `&&` / `||` connectives are deliberately not tokenised as
arithmetic: the connective is already priced, and double-charging would break every
bare compound CMP, all of which measure exact.

## OQ-CPTARRANGE — does operator arrangement change CPT cost

**CLOSED NEGATIVE, with one exception that is a rule rather than noise.** Four arms
sweep operand counts 3 to 9 with the multiplications in completely different places,
and 26 of 28 rows land on the **identical** residual, with the slopes agreeing exactly
too. **The arrangement-blind expression model is right.**

Reading those rows also turned up a +348 nobody had seen, and a leading-tier-1-run
term now wired at 4 and 2.

## OQ-CPTREALDEST — REAL-destination CPT

**SOLVED.** A CPT writing to a REAL destination is evaluated in floating point and
priced by a separate model: the integer operator-tier costs do not apply, and every
non-float operand carries a conversion cost. Exact on every captured row.

Coverage gaps recorded rather than hidden: only operator counts 1, 2 and 5 are
covered, and BOOL falls through uncharged because no real example exists to confirm it
converts the same way.

**CAPTURE ERRORS: 1 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the row outlives it.

## OQ-CPTNARROW — how SINT/INT widening scales

**SOLVED as a mechanism, BOUNDED as a constant.** Integers use a behind-the-scenes
conversion to DINT. That resolved two things at once: **LINT operands cost nothing**
(already 64-bit, no widening) and SINT/INT operands cost +256 per rung on the
three-operator all-REAL control.

**How that 256 splits is not determined** — there is exactly one data point. This is
the defect that makes CPT read as the worst measured accuracy of any instruction.

## OQ-CPTTYPEMISMATCH — destination and operands disagreeing in type

**MEASURED, deliberately not fitted.** Two type-mismatch costs found on a clean 2×2,
and not wired because the real exposure is three of several hundred occurrences.
**Below the noise floor, recorded so the measurement is not lost.**

## OQ-STSIZING — Structured Text sizing

**SOLVED, from a starting point of completely unmodelled.** Every ST routine
contributed exactly zero.

**An instruction inside ST costs exactly what it costs in a rung.** Against matching
RLL captures, ST is a flat **+432** — the ST routine shell — and nothing else, across
five independent pairs. **The entire weight table transfers unchanged.**

**ST comments are free.** That needed testing rather than assuming: an RLL rung comment
is a separate element, while an ST comment sits inside the compiled source text, so the
RLL result does not transfer.

Control flow is priced per construct, and **a loop-heavy routine is not priced like a
branch-heavy one** — FOR costs several times what IF does.

## OQ-STEXPR — ST assignment cost

**SOLVED as one law replacing a five-entry table** whose fallback over-predicted a
one-operator assignment roughly threefold.

**An ST assignment is not priced like the equivalent CPT.** That was the working
hypothesis, and a mirror pair differing by exactly the routine shell looked
conclusive — routing every assignment through the CPT model on that basis
over-predicted one file by **+132%**.

The law: a base by operator count and destination type, plus each operator's CPT tier
premium above tier 1, plus a conversion term per integer-typed **named** source read
into a REAL destination. **Integer literals do not pay the conversion term** — that is
what fixes the rate.

**All three of the old table's non-trivial entries come back from the law**, which is
what says it was mis-parameterised rather than incomplete. Each had been measured on a
different expression and then keyed on operator count alone.

Both rows step once at two operators and are dead linear after — **the step is the
mechanism**: a single-operator assignment compiles to one instruction and a compound
one reaches for expression evaluation.

The ST family went from 8.33% to **0.0091%** mean absolute error, 60 of 69 rows
byte-exact.

**CAPTURE ERRORS: 1 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the row outlives it.

## OQ-STEXPR-OPERATOR — the per-operator premiums

**SOLVED.** All four outstanding assumptions measured.

**The one-operator premium is not a premium — it is a lookup per operator class**:
additive, multiplicative, bitwise and exponent each have their own value. **The
premium on the REAL row does not scale up, it vanishes.** AND and XOR are now measured
at tier 1, which the CPT table did not cover at all.

> It was blocked for a period with every number measured and none wirable, because
> each operator had exactly two points and the fit needed two parameters. **Recording
> that state, rather than fitting it anyway, is why the eventual numbers are trusted.**

## OQ-STCOMMENT — **CLOSED with OQ-STSIZING.** ST comments are free.

## OQ-CPT / OQ-CMP — early identifiers, superseded by OQ-CMPCPTLAYOUT.

---

# JSR, subroutines and program structure

## OQ-JSRPARAMCOST — JSR parameter cost

**SOLVED.** The flat per-rung weight covers the base call only. The per-parameter cost
decomposes as a per-call-site marginal rate plus a one-time declaration charged **once
per distinct target, never per call site.**

`n` is read straight off each call's own second argument — **the declared parameter
count Studio itself writes there** — rather than by counting arguments.

**A JSR target does not charge its own routine base**; that stays folded into the
caller's constant. Charging it again over-counted every JSR-using program by roughly
4,832 bytes.

**But the target's own instruction content is not skipped.** A target with substantial
content genuinely costs memory — maximum 13.37% residual before this was fixed, 4.75%
after.

**CAPTURE ERRORS: 4 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-JSRSCALE / OQ-JSRSHARED — the composite surcharge

**SOLVED, and it was the project's largest error source.** A file-wide cap on the
AOI/JSR content surcharge was fitted against the synthetic composites and behaved
completely differently on a real program — **mild trimming on the files it was fitted
on, total annihilation at real scale**, suppressing over a million bytes on one real
file.

The cause: **real programs carry 16× to 54× more JSR-target instructions than any
synthetic composite.** With the cap the model ignored target content almost entirely,
which silently undid the finding that target content is not free.

Refitting on real programs cut it roughly fivefold. **Neither extreme was right** —
capped under-predicted by over 12%, fully uncapped over-predicted by 6.5%.

## OQ-JSRFOLD — how a target's cost folds in

**SOLVED.** A JSR and its target are over-charged at low counts and under-charged per
unit, and the shape pointed at how the fold works. Measured across four counts of N
JSR rungs against N target routines.

**CAPTURE ERRORS: 2 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-IDENTNAMELEN — do object names cost bytes

**SOLVED as one shared law.** `0` up to 4 characters, `2 × (len − 4)` from 4 to 8, and
**exactly `len` above 8 with no bucketing** — which distinguishes it from the AOI
type-name and alias-tag costs, both of which bucket.

Two independent sweeps of ten identifiers each, at five name lengths up to Rockwell's
real 40-character cap, return the identical per-identifier cost. Program name rows
went from a large spread to exactly 0, and the JSR rows collapsed onto a uniform
under-charge that turned out to be a separate per-target term.

Stays FITTED: the middle interval is an interpolation between two anchors with no data
of its own.

## OQ-DEFSCALE — definition and instance-count scaling

**SOLVED for the terms that could be separated.** Four exact linear laws came out of
30 files with zero import errors. One term wired exactly; another **measured exactly
and blocked by a confound that runs through the whole corpus**, and recorded as such
rather than wired.

This is the batch that produced the standalone UDT tag slot rule, from the one place
two families disagreed.

## OQ-LADDERBASE — two capture sessions disagreeing

**BOUNDED.** Two capture sessions on one real export disagree by 18–25 KB. It needs
three existing files recaptured **in one session**, which is a capture-discipline
matter rather than a modelling one. **Recorded so a future disagreement is recognised
rather than investigated from scratch.**

---

# Modules, I/O and platform

## OQ-MODULEIO — per-catalog module overhead

**SOLVED in large part.** 126 real module captures were sitting unreconciled; 51
catalogs now carry a real per-catalog overhead and the exact-match rate on real data
went from 1 in 126 to 54 in 126.

**CAPTURE ERRORS: 9 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-MODULESTRUCTURAL — the shape module cost should have

**SOLVED for one profile, and it reframed the target.** A per-catalog table **can only
ever cover catalogs personally captured.** A real customer file will contain catalogs
never seen, and those fall back to one flat default that is badly wrong for whole
families.

**A generic Ethernet connection's data costs 4× its declared bytes**, with each
direction rounded to a word, the word counts summed, and 16 per word less 8 when the
total is odd. Exact on all 14 captured points.

**The two directions are interchangeable** — only the sum of the word counts matters.
**No real instance could show this**, because real devices vary both directions at
once.

That profile is 25% of all non-CPU modules in the real programs and had no per-catalog
entry at all.

**Deliberately scoped to that profile.** The rack sweeps point the same way, so a 4×
connection cost may well be general — but applying it to every captured module row on
one profile's evidence is the move this project has had to undo before.

Also settled: **the file is the final decision on module sizing.** A module costs its
per-catalog overhead plus the size the L5X states, and every module gets sized. Several
catalogs are configurable, so **two instances of the same catalog are different
devices.**

## OQ-MODULEMARGINAL — does the Nth copy cost the same as the first

**SOLVED for ten catalogs, and it found a compensating error.** From the second module
of a catalog on, overhead drops to a second per-catalog rate — not a constant and not a
ratio. Measured at four counts with zero variance, and **per catalog rather than per
file**: settled by mixture files in which reversing module order leaves the total
byte-identical, while a per-file reading requires it to shift.

**The six 2198 drive catalogs cost the same as each other** — 4,624 for the first and
3,640 for each additional — and the per-catalog distinction previously believed to
exist between them was itself an artifact of guessing.

**The old guesses ran 6,384 bytes high per drive, and removing them unmasked a
systematic under-prediction on every real program** that the over-charge had been
cancelling. One real program with 12 such drives moved by exactly 12 × 6,384. **A
compensating error hides a real one.**

**Seven measured rates are deliberately excluded**, each for a stated reason: the
generic Ethernet placeholder's rate is the cost of a second identical clone, which no
real program has; and the six drives were measured on bare modules with no axis tag,
which no real program contains. Those two families were 95% of what the full table
would have removed.

The occurrence-count scope — project-wide or restarting under each parent — is
**undetermined by data** and cannot change a real-file number until a real file splits
a catalog across racks.

**CAPTURE ERRORS: 6 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-POINTIOCONN — POINT I/O connection format

**MEASURED.** A card's cost depends on its connection format, which the model does not
represent, and the flat rate charged instead is **wrong in both directions.** Three
real captures with identical content otherwise, where the non-module part of the
prediction is byte-identical across all three — so the difference is entirely the
connection format.

## OQ-193ECMETR — **BOUNDED.** A real "Child module incompatible with parent module" error on two catalogs, genuinely undiagnosed. Needs the raw Studio error line; the catalogs are excluded from the generators meanwhile.

## OQ-LEGACYNETOVERHEAD — ControlNet and legacy networks

**OUT OF SCOPE, deliberately.** ControlNet, DeviceNet, DH+, DH-485 and Remote I/O
bridges are excluded from sizing entirely — the same treatment given to rack-aliased
modules.

> This was briefly reopened as a data gap and a flat overhead wired for a ControlNet
> bridge, then reverted the same day. **A real capture existing is not the same as the
> shape being in scope.**

## OQ-2198ERS3 — **SOLVED with OQ-MODULEMARGINAL**, and see `SAMPLE_GENERATION.md` for the separate finding that ConfigSize is a function of the module's Major revision rather than its catalog.

## OQ-BASELINE — the empty-project baseline

**SOLVED.** A fixed, zero-variance cost confirmed across 200+ independent data points
spanning wildly different test categories, all landing on the same number once every
other sizeable element is accounted for. **Those points are independent in test
content, not in processor or firmware.**

## OQ-BASELINE-PROCFW — does the baseline vary by processor and firmware

**SOLVED for the active scope.** It does. The active platform is **exact** at every
firmware, and the one non-zero residual there is **not a baseline error** — it is a
firmware-dependent **content** gap where real MainRoutine content drops to zero on
later hardware while the engine still predicts a small amount.

Per-family corrections for the other active platform took baseline rows from 68 of 140
exact to 118 of 140.

> **One ladder cannot serve every processor.** Each processor's residual is constant
> within a firmware band and the bands differ by family. On a bare-baseline file the
> residual *is* the baseline error by definition, so this reads a lookup table off its
> own measurement rather than fitting free parameters.

> **A correction that looked right moved 787 previously-exact captures to wrong.** It
> was caught only by re-running the residual census immediately after wiring. Pattern
> order in that table is also load-bearing, and a test asserts it.

## OQ-BLOCKBYTE — is a block a byte

**CLOSED, and it was correctly flagged as foundational.** Studio labels its capacity
readout "bytes" for some processors and "blocks" for others, while this project treats
the figure as one uniform unit. **If a block were not numerically a byte, every
constant fitted against the dominant baseline would need rescaling.**

**A block is a byte on the active platform.** The two-file test — a single
120,000-element DINT array and nothing else, so 480,000 bytes of the total is exactly
120,000 × 4 with zero packing ambiguity — confirms it.

> **The test had been captured and never read.** That is the recurring failure this
> project has tooling for now.

## OQ-REAL5069 — does the second platform need its own cost model

**CLOSED NEGATIVE for content.** Two platforms carrying identical content at five
densities produce **byte-identical residuals at every density**, so the platform
difference is a single project-level constant rather than a per-feature one.

**Read this as "no per-platform CONTENT model is needed", not "the platform difference
is fully wired."** The result was measured on generated files.

## OQ-L9BUDGET — memory budget for one controller family

**BOUNDED, deliberately not guessed.** There is no budget for that family, so the UI
has no denominator and cannot show headroom. **The catalog digits look like they encode
memory, but that is a pattern, not a source**, and this project has been wrong before
inferring a constant from a catalog number.

## OQ-PREDEFINED — firmware-native structure sizes

**SOLVED for all 195 known types.** A 184-file blank-tag discovery batch gave 174 real
capacity deltas, wired in one batch. The two longest-blocked types are resolved with
real totals.

**One type was wrongly documented as unmodelled** when its probe had in fact captured
real data and it was already wired — found by checking rather than trusting the note.

**One type wired from real decorated data matched its later real capture exactly**,
which independently confirms the derivation **method**, not just that one type.

The SFC and function-block families stay ASSUMED: read off real data with zero
variance, but not capture-confirmed, and two of them rest on a single instance each.
**None is drillable to a per-field breakdown** — only the total is confirmed, field
counts vary widely, and a fabricated even split would misrepresent that.

## OQ-AXISSTRUCT / OQ-AXISDEEP / OQ-AXISCOMBO — axis structures

**SOLVED as empirical constants, with a discrepancy recorded rather than resolved.**
The axis and motion-group values are empirical because Rockwell does not publish the
layout. Axis sizing is **byte-exact on one real program** over 37 axis tags and
778,728 bytes — the largest single category in that file.

**A second set of totals exists and is deliberately not wired**, each roughly 92–100
bytes higher, measured against a baseline that does not itself reconcile. The file
composition behind it is not available, so it is recorded rather than silently trusted
or silently dropped.

## OQ-AXISMARGINAL — multi-drive axis scaling

**CLOSED, and it is the canonical validity failure.** Every file in the sweep carried
`error_count = drives + 1`, and its residuals were almost perfectly linear in drive
count — so it looked like an exact per-drive over-charge finding, **was derived to zero
residual on 18 of 18 points, and was wired and committed.** It was an artifact of the
drives failing to build. Reverted the same session.

The real cause, identified from the error **counts** alone when no error text existed:
a drive needs its bus supply module **and** that supply's converter axis. Four
generators fixed, two lint rules added, and six first-instance module values downgraded
from KNOWN to ASSUMED because they rested on the same broken captures.

**A clean, exact-looking linear fit is not evidence of validity. Check the error count
first.**

**CAPTURE ERRORS: 57 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-CAMSHAPE / OQ-CAMSCALAR — CAM structures

**SOLVED, and it corrected a wired constant.** CAM was fitted on standalone tags while
every real use is a UDT member. **The container does not matter** — but the original
constant was wrong, and the member arm is what exposed it.

The base corrected from 8 to 4, plus 8-byte element-block alignment. **The old value
read exact at two counts and "a flat −4 of familiar small noise" at three others. It
was not noise** — the −4 fell exactly on the even element counts, which is where the
element total is already 8-aligned.

A scalar CAM stays open in principle and unpriced in practice: the corpus contains
**zero** real examples, and this model prices it as a one-element array, which two files
say is wrong by about a hundred bytes.

---

# Alarms

## OQ-ALARMCOND — tag-based alarm conditions

**SOLVED with zero residual on every captured point, from a starting point of the
single largest unpriced item in the model.** Thousands of real elements across the
corpus, hundreds in every real program, **all costing exactly zero.**

A file base, a per-condition rate, and an associated-tag term keyed on the resolved
type of what each association points at. Derived from a 37-file batch.

**Alarm name length, message text, severity and delay values were all proved free.**

The leftover residual after an earlier refit correlated +0.583 with alarm count — the
strongest identified driver at the time, which is what pointed at this.

> The per-condition formula holds. Its measurement **inside real content** does not
> fully agree across two real programs — see `OQ-ALARMCONDREAL` in
> `OPEN_QUESTIONS.md`, which was promoted back out of this file for that reason.

## OQ-ALARMDEF — the ALMD and ALMA instructions

**PARKED, not closed.** **Zero occurrences across all real programs.** No
alarm-instruction question may be worked ahead of something that moves real prediction
error.

**Scope note: this covers the INSTRUCTIONS only.** Tag-based alarm condition elements
are a separate feature, are present in real programs at 19–21% of total memory, and are
**not** parked. Three separate things share the word "alarm" and must never be reported
as one.

**CAPTURE ERRORS: 1 row(s)** — owned by this question, captured with Studio build
errors. The question is parked; the row outlives it.

## OQ-ALARMPROPBYTES — **CLOSED with OQ-ALARMCOND.** The per-property costs are proved free.

---

# Process, tooling and scope

## OQ-GENMETHOD — can hand-built XML be imported

**SOLVED.** Yes. Direct XML authoring works and is the method. The fallback approaches
— driving Studio's automation interface, or hand-fixing failures and re-exporting —
were never needed as the default path, though the second remains the only way to
produce a valid variant of a real export.

## OQ-EMULATE / OQ-MEMREADMETHOD — how to read memory

**SOLVED, and it simplified the loop substantially.** **No download and no emulator
are needed** — Studio shows memory usage as soon as a project compiles offline.

**There is no programmatic memory read, online or offline.** GSV has no memory
attribute on any Logix 5000 platform, and the documented message-based path is
explicitly unsupported across the current lineup. **Controller Properties, read by eye,
is the only method.**

## OQ-CAPTURERACE — a capture reading the wrong file

**SOLVED at the source.** The window title is cross-checked against the file requested.
A real confirmed case had one request come back with the previous file's title still
showing.

**The subtle part:** an "already logged" check that only asks whether a value is
non-empty treats a mismatched row as done forever, because it **does** have a value — a
wrong one. The filter now excludes flagged rows, so they are retried automatically and
self-heal.

## OQ-TOLERANCE — what counts as good enough

**SOLVED.** Exact-tier predictions: within 1% good, 3% acceptable, above 5% a real gap.
Logic-tier is not held to the same bar, because compiled logic size is a fitted
heuristic by nature of the problem. **An error in the tier the tool calls exact
undermines its value proposition more than an acknowledged estimate does.**

The project-wide single-measurement noise floor is **±8 bytes**.

## OQ-EXPORTSCOPE — what a partial export costs on import

**CLOSED — accepted in use.** Partial exports of AOIs, UDTs and programs import and
are sized correctly enough for their purpose; the owner has confirmed the behaviour
and needs nothing further from it.

The scope machinery stays as wired: a partial export gets no project base load, no
firmware, catalog or safety baseline delta and no task/program shell, and its total
is reported split three ways — target, context and project. The rules are in
`MEMORY_MODEL.md`.

**What was never measured, recorded so it is not mistaken for known:** the shell an
imported Program or Routine creates in the destination project, and whether
reconciling an already-present context declaration costs anything. Nothing is charged
for either. Measuring them needs a Capacity reading before and after an import into
an existing project in Studio — a bench session, not a generated file, since the
capture pipeline only converts whole projects. It was a correctness requirement, not
an accuracy one: it moves no real-program number and is not reopened for accuracy
work.

## OQ-L5XVERSION — **CLOSED.** The corpus spans several schema revisions and the parser handles them. Two older revisions have no real sample in hand and are backlogged rather than guessed.

## OQ-SAFETY — **SOLVED.** A safety project's total is understated, and the UI warns. Safety-family instructions are out of scope.

## OQ-COMMENTS — **SOLVED.** An RLL rung comment is free. **An ST comment needed testing separately** and is also free — the RLL result does not transfer, because a rung comment is a separate element while an ST comment sits inside compiled source text.

## OQ-LOGICVISIBILITY — **CLOSED.** Logic-derived numbers are flagged estimated everywhere they appear, per the ground-truth constraint.

## OQ-EVENTTRIGGER — EVENT instruction and task trigger cost

**SOLVED for the instruction half.** The EVENT instruction had **no weight at all** and
was charged zero. Three counts with nothing else varying read exactly `56n + 8`, the 8
being the universal per-file residual.

**CAPTURE ERRORS: 1 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the row outlives it.

## OQ-V3GENBUGS — generator defects found by ablation

**CLOSED, with one arm permanently BLOCKED and that is the lesson.** Three real
generator bugs were found and fixed, including unsigned atomic types falling through a
parser's own hardcoded table so any module member declared with one turned the module
total into a floor.

**The ablation arm cannot be differenced at all, because it is not single-variable** —
turning off several things together measures their sum. **That is a design failure, not
a capture failure, and no amount of recapturing fixes it.**

## OQ-COMPOSITESCALE — are the categories additive

**CLOSED NEGATIVE, which is the answer that was wanted.** The question was whether
formulas each fitted by scaling one thing at a time stay correct when a real project
mixes everything at once, and whether an interaction between categories explains why
synthetic composites over-predict small and under-predict large.

**There is no interaction.** A 3×3 grid for each of the six pairs drawn from UDT-typed
tags, rungs, AOI instances and modules, with everything unnamed held at zero, comes
back additive — 24 of 24 exactly.

**So the composite residual is not an interaction effect**, and the remaining
composite error is the superseded-generator blend recorded in `SEGMENT_TRACKER.md`.

**CAPTURE ERRORS: 82 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it. **Every one is from a superseded
generation, and none ever fed a number** — the validity filter already rejected them.

## OQ-REALGAP / OQ-STACK — early framings of the real-file residual, superseded by OQ-REALUNDER.

## OQ-FBDSFC — **CLOSED.** The SFC and function-block predefined structures are sized; their routines' own content is out of scope, as the corpus is overwhelmingly RLL and ST.

## OQ-CTLSHELL — the supposed unpriced controller shell

**CLOSED NEGATIVE, and the withdrawal is the point.** It was opened on a bare real
shell reading 21,096 against a predicted 13,296 — a 7,800-byte hole in unpriced shell
content. **Both numbers were wrong.**

**A File|New project reads 18,112 and the engine predicts 18,112.** Exact, confirmed
twice: read off a fresh Studio project, and back-solved from the empty-rung captures.

13,296 is the controller-only **component**, not a whole-file total. The
MainTask/MainProgram/MainRoutine that File|New also creates cost 4,816 more, and
13,296 + 4,816 = 18,112. The actual was wrong too — the real figure is 17,352.

**Corrected, the sign flips**: the engine **over**-charges that shell by 760 rather
than under-charging by 7,800.

**Two rules follow.** **Quote a whole-file prediction against a whole-file capture,
never a component against a total.** And a measurement taken off the strip ladder is
suspect by default — those files were later found not to import at all.

One byproduct kept, unwired: a dual-IP / DLR controller configuration costs +40 bytes.
One reading, one controller.

**Closing this removed the last measured evidence of content the engine does not count
at all — for about six hours**, until the literal-operand measurement supplied new
evidence of exactly that shape.

## OQ-PRODCONS — produced and consumed tags

**FORCE-CLOSED below the noise floor. Do not reopen and do not spec another file.**

No special connection formula is needed: a correctly built produced or consumed tag's
DataType already includes a connection-status member, so ordinary UDT recursion covers
it, and that member type is itself wired.

**A Produced tag does carry +1,072 bytes the model does not charge — measured, not
guessed — and it is still closed**, because the entire real population of them is on the
order of a thousand bytes against a residual three orders of magnitude larger, and most
of what such a tag costs is already charged through its UDT definition and its module.

They are 0.11% and 0.06% of real tags. **Apply the noise floor before building, not
after capturing.**
