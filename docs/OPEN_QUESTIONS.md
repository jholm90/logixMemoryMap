# Open Questions

**Two.** Down from forty. Closed questions and their reasoning trails are in
`RESOLVED_QUESTIONS.md`; the capture batch after the blind set closed five at once
(JSRCALLERBASE, RUNGSHAPE, ALARMCONDREAL, BUILDFAIL-OPEN, MODULENAMELEN).

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

## What is left

| question | state |
|---|---|
| **OQ-REALUNDER** | The real residual: **3.12% mean, 6.0% worst** on the eighteen real programs present, after a compensating error was removed. |
| **OQ-OPERANDSHAPE** | The leading explanation for it: member-path operands, half of all real operands and never measured. 26 files built, awaiting capture. |

---

## 1. OQ-REALUNDER — the residual itself

**Mean 3.12%, worst 6.0%, every one of the eighteen real programs present
under-predicting** (sum-weighted +3.20%). That is worse than the 1.74% it read before
this batch, and the difference is a correction, not a regression:

- The per-caller `jsr_fixed_base_per_routine` (5,096) had only ever been measured on
  files with ONE caller routine, and was charged to every caller in real programs —
  10 to 87 of them. `jsrcallers_k*` proved a caller costs what any routine costs
  (OQ-JSRCALLERBASE). Removing the over-charge took the real set from 1.74% to 3.40%.
- The AOI argument cost (input references at 28, not 16) moved it back to 3.12%.
- The 2198 family repeat discount moved it to 3.13% — right on the Kinetix files,
  slightly wrong-way on real programs that carry many drives.
- The one-time 264 an RLL file with AOI calls carries moved it to **3.12%**.

So about **3% of every real program is still unexplained**, and the old 1.7% figure was
that 3% partly cancelled by an error. This is CLAUDE.md failure mode 3 exactly, and the
right response is the same: keep the correct term, find the real one.

**What it tracks.** Everything size-like — programs (r = 0.92), routines (0.90),
rungs (0.86), tags (0.85) — and it is about 20% of the engine's `routine_logic` bytes.
No single count explains it under leave-one-out (best single term: JSR calls, LOO mean
1.16%, worst 4.9%), and a term fitted on the real set is not an answer anyway.

**What distinguishes real programs from the generated files that fit.** The
multi-program composites (`composite_realistic_v3/v4`, `v3abl_*`: 7–11 programs,
JSR callers and targets, AOIs, modules) land within ±1% on the corrected engine. The
largest structural difference between them and real programs is **operand shape** —
see OQ-OPERANDSHAPE.

**Six new real programs arrived with no reading** (exports 37–42) and were predicted
before any Capacity reading, per the blind rule. Five are safety controllers
(5069-ERS2/ERMS2, 1756-L81ES), whose safety content the engine understates by
design; export 42 is a 1769 and is recorded but excluded from every accuracy figure.
Predictions and expected ranges are in `samples/manifest.csv` (`realprog_37`–`42`).

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

### Not available

Attribution by subtraction from a real export is dead by the read-only rule. The
Studio-side substitute — delete a category in Logix Designer, read Capacity twice — is
declined: each reading costs a bench session. A residual model fitted on the real
programs is judged by leave-one-out only and must beat 0.007 points.

---

## 2. OQ-OPERANDSHAPE — does a member-path operand cost more than a plain tag?

**Every instruction weight in the model was fitted on plain-tag operands.** Real
operands, counted over every instruction call in the eighteen real programs:

| operand | real programs | composites that fit |
|---|---:|---:|
| plain tag | 48.7% | ~75% |
| member path `A.B` | 32.6% | 0% |
| nested member `A.B.C` | 15.4% | 0% |
| deeper | 3.2% | 0% |
| array element, constant index | 22% of operands | ~80% |
| bit of a word `D.5` | 9% | ~25% |

Array elements and bit-of-word operands are in the composites that fit, so they are
already covered. **Member paths are half of all real operands and appear in no
captured generated file at all** — because lint's operand resolver returned the BASE
tag's type for `U.Bit`, refused it as a non-BOOL operand of XIC, and so blocked every
member-path rung any generator tried to write. The resolver now follows member paths
through the file's own UDT definitions.

**Mechanism and expected movement.** If a member reference costs more than a plain
tag in compiled logic, the under-charge scales with instruction count, which is what
the residual does. At the ~20% of `routine_logic` the residual represents, it would
need a few bytes per member operand; the batch measures it directly.

**Batch built — 26 files, `gen_operand_shape.py`, 1756-L81E fw35, lint clean, confound
gate clean.** One instruction per family, one operand's shape varied, identical tag
inventory in every file, at 250 and 1,000 rungs:

| family | shapes |
|---|---|
| `opshape_xic_*` — `XIC(<op>)OTE(Out)` | plain, mem, nest, arrmem, bitword |
| `opshape_ote_*` — `XIC(In)OTE(<op>)` | plain, mem, nest, arrmem |
| `opshape_mov_*` — `MOV(<src>,<dst>)` | plain, srcmem, dstmem, nest |

Each shape differences against its family's `plain` file at the same count; the two
counts give the per-rung slope. `arrmem` and `bitword` are controls.
