# Roadmap

Where the tool stands and what is worth doing next. Structural phases live in
`PROJECT_PLAN.md`; the ranked queue lives in `TASKS.md`; individual questions live
in `OPEN_QUESTIONS.md`.

---

## Where the tool actually stands

Measured on the seventeen real production exports, which are the only accuracy
evidence that counts.

### Current — after the capture batch that followed the blind set

**Eighteen real programs present: mean absolute error 3.12%, worst 5.99%, every one
under-predicting (sum-weighted −3.20%).** Stopping rule NOT MET.

This is worse than the 1.67% below, and it is a correction rather than a regression.
The per-caller `jsr_fixed_base_per_routine` (5,096), measured only on one-caller files
and charged 10–87 times per real program, was an over-charge; `jsrcallers_k*` proved a
caller routine costs what any routine costs (OQ-JSRCALLERBASE). Removing it took the
mean from 1.74% to 3.40%; the AOI input-argument cost and the 2198 family rule then
brought it to 3.12%. **About 3% of every real program is unexplained, and the old
figure was that 3% partly cancelled by an error.** OQ-OPERANDSHAPE is the batch aimed
at it.

| program | prediction error |
|---|---:|
| export 27 | -5.99% |
| blind_03 | -5.60% |
| export 06 | -5.33% |
| export 13 | -4.05% |
| export 16 | -3.66% |
| blind_02 | -3.38% |
| export 07 | -3.20% |
| export 17 | -3.01% |
| blind_06 | -2.95% |
| blind_01 | -2.86% |
| export 09 | -2.72% |
| export 18 | -2.67% |
| blind_05 | -2.25% |
| export 01 | -1.96% |
| export 28 | -1.93% |
| blind_04 | -1.90% |
| export 14 | -1.72% |
| export 10 | -1.01% |

(Error is prediction minus actual; negative is under-prediction. The five programs
absent from `samples/local/` are not recomputed.)

### Second blind set — exports 37–42

| export | controller | actual | predicted before the reading | error | inside the pre-written range |
|---|---|---:|---:|---:|---|
| 37 | 5069-L330ERMS2 | 1,572,161 | 1,495,547 | −4.87% | yes |
| 38 | 1756-L81ES | 2,007,604 | 1,832,104 | −8.74% | no (below) |
| 39 | 5069-L340ERS2 | 2,935,942 | 2,811,103 | −4.25% | yes |
| 40 | 5069-L320ERMS2 | 1,279,555 | 1,211,456 | −5.32% | yes |
| 41 | 5069-L310ERS2 | 511,973 | 481,589 | −5.93% | no (below) |
| 42 | 1769-L33ERMS | 884,640 | 840,245 | −5.02% | yes — dead architecture, excluded from accuracy |

Every one under-predicts; four of six inside the pre-written range. Five are safety
controllers, whose safety content is small and lives in a separate memory partition
(see OQ-REALUNDER). Together with the eighteen above, **every real program with a
reading now under-predicts.**

### Before that batch — kept for the record

**All twenty-three real programs with a reading — the seventeen below plus six blind
(next section): mean absolute error 1.67%, worst case 3.99%, residual about +1.72%,
sixteen under and seven over.**

The original seventeen: **mean absolute error 1.5951%. Worst case 3.6309%. Four files
inside 1%, eleven inside 2%.** Total residual +822,938 bytes on 55,430,980 = **+1.485%**. Ten files
under-predict, seven over-predict.

| program | actual | error |
|---|---:|---:|
| `export 30` | 3,129,275 | −3.63% |
| `export 27` | 2,255,773 | −3.52% |
| `export 16` | 4,044,994 | −2.50% |
| `export 06` | 5,217,440 | −2.31% |
| `export 07` | 7,891,612 | −2.15% |
| `export 25` | 4,634,308 | −2.04% |
| `export 10` | 1,703,932 | +1.79% |
| `export 09` | 7,136,625 | −1.76% |
| `export 17` | 2,281,316 | −1.48% |
| `export 13` | 1,074,245 | +1.42% |
| `export 01` | 5,999,972 | −1.20% |
| `export 18` | 923,320 | +1.17% |
| `export 29` | 1,362,000 | +1.05% |
| `export 28` | 2,502,336 | +0.55% |
| `export 08` | 1,147,896 | +0.24% |
| `export 26` | 1,763,760 | −0.19% |
| `export 14` | 2,362,176 | +0.11% |

**Re-verified at the final review on the twelve of the seventeen present in the
working copy** (`quick_eval.py --real-only`): every one of the twelve reproduces the
table above to within 0.01 percentage points — mean 1.66%, worst 3.52% over those
twelve. The engine has not drifted on real programs. The other five
(`export 08, 25, 26, 29, 30`) were not in the delivered archive and carry their
recorded figures.

**The residual is no longer one-sided.** It used to be: every file under-predicted
and the work was to find missing bytes. Seven files now over-predict, which means
**any candidate that can only add bytes is wrong before it is tested.**

### How to state the accuracy

**The max always travels with the mean.** The honest one-line claim is *mean
absolute error 1.67%, worst case 3.99%, read the worst case as up to 4%* — over
twenty-three real programs, six of them blind. Not
"about 1.6% accurate" — the worst file is 2.3× the mean and the distribution has
a long right tail. Any headline number, in the README, in the UI or in a reply,
carries both figures or it misleads.

**The blind test is the only externally meaningful evidence.** The seventeen are
gitignored customer exports that nobody outside the project can audit, so the
mean over them cannot be verified by anyone else — and the model was tuned while
sixteen of them were available. One was not: `export 07`, a 7.89 MB
program on a 1756-L83E, was **predicted at 7,722,352 against an actual of
7,891,612, +2.15%**, before its actual was used for anything. It lands inside the
existing error distribution rather than outside it. **Lead with that, not with the
mean.**

**Every future real export should be predicted, and the number written down,
before the controller reading is taken.** That is the only procedure that adds
auditable evidence. A file reconciled after the fact adds a fitting input, not a
test.

### Six blind predictions — written down first, then read

Six real exports arrived with **no capacity reading anywhere**. Predicted by the
final engine and written here before any reading exists. The name-to-ID mapping
stays in the gitignored `samples/local/blind_predictions.csv`.

"Expected" applies the seventeen's measured +1.49% under-prediction; the range is
the seventeen's own spread (−3.63% to +1.79%). A reading outside the range is a
finding, not noise.

| ID | recorded as | processor | firmware | predicted | range written in advance | **actual** | **error** |
|---|---|---|---|---:|---:|---:|---:|
| `blind_01` | export 31 | 1756-L83E | 32.04 | 9,090,346 | 8,930,356 – 9,433,052 | **9,262,907** | **-1.86%** |
| `blind_02` | export 32 | 1756-L83E | 35.05 | 7,970,364 | 7,830,086 – 8,270,847 | **8,159,036** | **-2.31%** |
| `blind_03` | export 33 | 1756-L83E | 33.01 | 7,399,658 | 7,269,424 – 7,678,625 | **7,707,453** | **-3.99%** — outside range |
| `blind_04` | export 34 | 1756-L83E | 32.04 | 6,418,673 | 6,305,704 – 6,660,657 | **6,480,713** | **-0.96%** |
| `blind_05` | export 35 | 1756-L83E | 35.05 | 5,939,350 | 5,834,817 – 6,163,263 | **6,010,365** | **-1.18%** |
| `blind_06` | export 36 | 1756-L83E | 35.05 | 3,704,851 | 3,639,646 – 3,844,524 | **3,744,752** | **-1.07%** |

**Outcome: mean 1.90%, worst 3.99%, all six low.** Five of six inside the range; `blind_03` missed it by 29 KB. Worse than the in-sample seventeen (1.60% / 3.63%), which is what a genuine held-out test is supposed to reveal: the model generalises, with a real systematic under-prediction on large line controllers. `blind_02` (export 32), a later revision of export 07, misses by −2.31% against export 07's −2.14% — the residual is a property of the program and survives a revision.


---

## The 1% target has not been shown to be reachable

`CLAUDE.md`'s stopping rule is mean under 1% **and** max under 2%. It is checked
in code — `scripts/quick_eval.py` prints `STOPPING RULE ... MET / NOT MET` on
every run — and it is NOT MET.

**More than that: it is not shown to be achievable, and the reasoning is recorded
so it is not re-litigated.**

Let all eight category scales float and fit them **directly on the held-out real
programs** — cheating, an upper bound no honest procedure can beat. The result is
mean 1.0149% and max 2.5919%, which **still fails**. Under leave-one-out
cross-validation that same fit is worth **0.007 percentage points**, with half the
files getting worse.

Two consequences:

1. **No per-category correction can close this.** A task whose mechanism is "a
   cost constant is slightly wrong" is dead before it starts.
2. **Treat 1% as an aspiration that has not been shown achievable**, not as a
   pending item. A result outside 2% on a real file is still a broken estimator,
   not an open question.

Changing the target to 2% would change none of the work below: a 2% **mean** is
already met and a 2% **max** is not reachable by any per-category fit either.

---

## What is left that the ceiling result does not bound

The one shape not eliminated is **a term not proportional to any category the
engine currently counts** — real content that is not being counted at all, or an
interaction that only appears at real scale.

**Unpriced literal content was the leading candidate and is refuted.** The
literal-operand batch showed integer literals cost nothing, and a count over
eighteen real exports put every remaining literal term — REAL +4, float form +76,
the INT/SINT over-charge — under the noise floor. The projected max 3.63% → 2.90%
came from charging 4 bytes to slots worth 0.

**The AOI population was the other candidate for the AOI-dense programs, and is
refuted too.** Fifteen real-shape AOI files reproducing export 18's population were
built when export 18 was under-predicted by about 7%. The copy over-predicts by
2.3%, so the population was never the cause, and the files confirm the
per-definition cost at real scale. Export 18 now over-predicts by 1.17%; the copy's
1.8-byte-per-member over-charge accounts for about 1.3 KB of its 10.9 KB residual.
See OQ-AOIREALSHAPE.

**What that leaves** is in `FINAL_REPORT.md` under "How to get more accuracy": the
residual has to be modelled from real programs directly, with features the engine
does not count, and judged only by cross-validation.

---

## What has been eliminated, so it is not re-tried

Each of these was tested and failed. They are recorded here because every one of
them looks reasonable on first inspection.

| candidate | why it is dead |
|---|---|
| A global `routine_logic` scale-up | Ruled out twice: by 578 instruction rows, and by direct measurement in both directions on real programs. |
| A constant error per instruction occurrence | Coefficient of variation 1.74 across the real set, 1.72 over the top four instructions, 1.73 per rung. Not a uniform weight error. |
| Branch fraction as the carrier | Nearly flat across the real set at 58.6–76.1%, correlates at only −0.250. |
| Any flat per-file constant | Swept from 2,000 to 10,000 bytes; every value made the mean worse. A per-file term moves all files equally, so bias improves and spread does not. |
| Any per-routine, per-rung, per-program or per-tag constant | All four are collinear with size, so each moves the bias and leaves the spread. |
| The empty-project baseline | Byte-exact on every generated empty file and on a File\|New real project (18,112 predicted, 18,112 actual). |
| Axis sizing | Byte-exact on one real program over 37 axis tags and 778,728 bytes — the largest single category in that file. |
| Tag declaration order | Six files, byte-identical. Order is free. |
| Branch arrangement | Byte-exact at 1, 2, 4 and 8 legs with inventory held fixed. |
| 2-D array subscripts | Cost zero. |
| Unpriced literal operands | Integer literals are free; every remaining literal term totals under the noise floor on eighteen real exports. |
| The AOI population in AOI-dense programs | Real-shape copies over-predict where the real program under-predicts. Per-definition cost confirmed at real scale. |
| The INT/SINT literal over-charge | 37 real occurrences, 1,756 bytes across eighteen programs. |
| Attribution by subtraction from a real export | Dead by the read-only rule — the derived files do not import. Not merely difficult. |
| Attribution by Studio-made deletion on a real project | Declined — every reading costs a bench session. The real residual is modelled from the real programs directly instead. |

---

## Known blockers needing external input

- **Studio error-log lines** for the remaining build failures. See
  `OPEN_BUILD_ERRORS.md`.
- **The alarm `ConditionType` dropdown list** plus one analog alarm example.
- **A real 1769 export with a controller capture**, if 1769 ever stops being dead
  architecture. Its baseline is not modelled at all.

---

## Standing rules

- **Cross-validation decides every fit.** In-sample fit has been wrong repeatedly
  on this project.
- **Real files are the scoreboard. The generated corpus is the instrument.**
  Never report a corpus pass rate as the project's accuracy — the model is fitted
  on it, so that number is circular.
- **A capture row with errors is never a valid fitting point.** It is suspect, not
  wrong: the actual figure got filled in, but part of the file may never have
  reached the controller. Never quietly use such a row and never quietly drop it.
- **Fix the estimator, do not just document the gap.**
- **State up front how many percentage points a task should move.** A task that
  cannot state that is not worked.
