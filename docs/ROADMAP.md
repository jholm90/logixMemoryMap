# Roadmap

Where the tool stands and what is worth doing next. Structural phases live in
`PROJECT_PLAN.md`; the ranked queue lives in `TASKS.md`; individual questions live
in `OPEN_QUESTIONS.md`.

---

## Where the tool actually stands

Measured on the seventeen real production exports, which are the only accuracy
evidence that counts.

**Mean absolute error 1.5951%. Worst case 3.6309%. Four files inside 1%, eleven
inside 2%.** Total residual +822,938 bytes on 55,430,980 = **+1.485%**. Ten files
under-predict, seven over-predict.

| program | actual | error |
|---|---:|---:|
| `superior` | 3,129,275 | −3.63% |
| `ipc_edgerline` | 2,255,773 | −3.52% |
| `k3m16_edgers` | 4,044,994 | −2.50% |
| `cmu` | 5,217,440 | −2.31% |
| `cardin_trimsortstack` | 7,891,612 | −2.15% |
| `eastperry` | 4,634,308 | −2.04% |
| `emporiumedger` | 1,703,932 | +1.79% |
| `emporium` | 7,136,625 | −1.76% |
| `mrfp_edger` | 2,281,316 | −1.48% |
| `flarefunction` | 1,074,245 | +1.42% |
| `accutally` | 5,999,972 | −1.20% |
| `murraybros` | 923,320 | +1.17% |
| `salamanca` | 1,362,000 | +1.05% |
| `pukall_gang` | 2,502,336 | +0.55% |
| `elmsdale` | 1,147,896 | +0.24% |
| `horizon_edger` | 1,763,760 | −0.19% |
| `griffin_stackerline` | 2,362,176 | +0.11% |

**The residual is no longer one-sided.** It used to be: every file under-predicted
and the work was to find missing bytes. Seven files now over-predict, which means
**any candidate that can only add bytes is wrong before it is tested.**

### How to state the accuracy

**The max always travels with the mean.** The honest one-line claim is *mean
absolute error 1.60%, worst case 3.63%, read the worst case as up to 4%.* Not
"about 1.6% accurate" — the worst file is 2.3× the mean and the distribution has
a long right tail. Any headline number, in the README, in the UI or in a reply,
carries both figures or it misleads.

**The blind test is the only externally meaningful evidence.** The seventeen are
gitignored customer exports that nobody outside the project can audit, so the
mean over them cannot be verified by anyone else — and the model was tuned while
sixteen of them were available. One was not: `cardin_trimsortstack`, a 7.89 MB
program on a 1756-L83E, was **predicted at 7,722,352 against an actual of
7,891,612, +2.15%**, before its actual was used for anything. It lands inside the
existing error distribution rather than outside it. **Lead with that, not with the
mean.**

**Every future real export should be predicted, and the number written down,
before the controller reading is taken.** That is the only procedure that adds
auditable evidence. A file reconciled after the fact adds a fitting input, not a
test.

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
engine currently counts** — real content that is not being counted at all.

**That term now has measured support.** An immediate numeric literal in an
instruction operand costs **4 bytes** that the engine charges at zero, measured on
the bench in Logix Designer. Exposure across the real programs is 52,195 unpriced
literal operand slots — 12.1% of all operand slots, about a quarter of the total
residual — and it is the first candidate to move the **max**, from 3.63% to 2.90%,
against a cheating ceiling of 2.59%.

It is not wired. The 4 is measured for a REAL literal only; 98% of the exposure is
integer literals at an unmeasured rate. A 29-file batch is built and awaiting
capture. See `OQ-LITERALOPERAND`.

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
| Attribution by subtraction from a real export | Dead by the read-only rule — the derived files do not import. Not merely difficult. |

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
