# The Ranked Work Queue

**An item not on this list is not being worked.**

Phases and exit criteria are in `PROJECT_PLAN.md`. Project state, the accuracy
figures and the full elimination table are in `ROADMAP.md`. Individual questions are
in `OPEN_QUESTIONS.md`.

**Before adding anything here, state how many percentage points it should move on
the seventeen real programs, and by what mechanism.** An item that cannot state that
is not worked. If the mechanism is "a category cost constant is slightly wrong," the
ceiling result in `ROADMAP.md` already answers it.

---

## Where the error is, and where it is not

Category mass across the seventeen, as predicted bytes. **This is where the mass
is, which is not the same as where the error is.**

| category | bytes | share |
|---|---:|---:|
| `controller_tag` | 32,892,544 | 60.23% |
| `routine_logic` | 9,799,473 | 17.95% |
| `alarm_condition` | 5,151,920 | 9.43% |
| `udt_definition` | 3,423,387 | 6.27% |
| `module_io` | 1,587,575 | 2.91% |
| `program_tag` | 1,233,347 | 2.26% |
| `project_baseline` | 260,072 | 0.48% |
| `task_program_shell` | 259,724 | 0.48% |

**`controller_tag` carries 60% of the mass and is not where the error is.** Every
real tag shape is already covered; the untested ones total a few thousand bytes
against a residual two orders of magnitude larger. The name-length term — the
strongest-looking candidate — is cleared by 88 clean rows at mean 0.12%.

**Only two categories have a self-consistent required per-file correction**:
`controller_tag` (coefficient of variation 0.039) and `routine_logic` (0.087).
Everything else ranges into the absurd — `program_tag` needs a scale of 347 on one
file and −26 on another — which is a restatement of the fact that those categories
are too small to carry the residual.

---

## The queue

### 1. Capture the literal-operand batch

**29 files built, awaiting conversion and capture.** The only candidate with
measured support that the ceiling result does not bound, and the only one so far
that moves the **max** rather than the mean.

| | |
|---|---|
| **Expected movement** | max 3.63% → 2.90% at a flat rate; the point of the batch is to find the right per-type rates instead |
| **Mechanism** | An immediate numeric literal in an operand costs bytes the engine charges at zero. Measured at +4.000 per slot on the bench. Not proportional to any category the engine counts. |
| **Exposure** | 52,195 unpriced literal operand slots, 12.1% of all operand slots, about a quarter of the residual |
| **What it must return** | the per-type rate for **integer** literals, which are 98% of the exposure and completely unmeasured |

**Read arm G first** — it reproduces the bench measurement at 1,000 rungs and should
return +24,000. If it does not, the pipeline does not reproduce the bench and
nothing else in the batch can be trusted.

**Then arm D.** If `0` and `1` are folded, the 205,060-byte integer exposure
collapses and this item drops down the queue. They are the most common literals in
real ladder.

**Then arm C.** If distinct values cost more than repeated ones, the cost is
per-distinct-value rather than per-slot, which changes the real arithmetic
substantially — real ladder reuses `0` and `1` heavily. A competing law already died
by exactly this confusion.

See `OQ-LITERALOPERAND` and `SAMPLE_GENERATION.md`.

### 2. More real captured programs

**The only thing that can settle anything at real scale.** Two or three previously
unseen exports with capacity readings would do more than any generated batch.

Real programs sit 16× to 54× outside the range the synthetic composites cover on
JSR-target and AOI content, so a law fitted on the synthetic range behaves
differently in the real one.

**Predict each one and write the number down before the capacity reading is taken.**
That is the only procedure that adds auditable evidence. It has been done once, and
that blind test is the strongest evidence the project has.

### 3. Resolve the per-rung term

`routine_logic` is 18% of the mass and the second-largest category. **Every
calibration file is one instruction per rung, so a per-rung cost and a
per-instruction cost are perfectly confounded in every weight.**

What is already settled, so it is not re-tried: branch arrangement is byte-exact at
every leg count, branch fraction is not the carrier, and a constant error per
instruction occurrence is ruled out by a coefficient of variation of 1.74.

The one attempt to isolate the per-rung term instead landed on the series-output
law, because the instrument used an output instruction and packing it built series
cascades. **A packing sweep must use a non-output instruction.** See `OQ-RUNGSHAPE`.

### 4. Close the alarm-condition gap inside real content

Alarm conditions are **9.4% of predicted mass and 19–21% of actual memory on the two
real programs measured** — the second-largest category in both. The per-condition
formula lands within 0.16% on one and **8.8% short on the other.**

At that scale, 8.8% is worth more than most items on this list. What is missing:
alarms on a UDT-scalar host, and whether alarm **sets** carry their own cost. See
`OQ-ALARMCONDREAL`.

### 5. Clear the capture backlog

54 manifest rows have no capture. **29 are the literal-operand batch (item 1).** The
rest:

| family | rows | state |
|---|---:|---|
| `composite_realistic_*_r2` | 9 | never submitted; eight have real lint findings to clear first |
| `fwmatrix_*` | 6 | awaiting first submission |
| `alarmcond_*` | 5 | condition-type arm, never captured |
| `predefprobe_*` | 3 | submitted and refused; needs the Studio error line |
| `cipmodule_*` | 2 | awaiting first submission |

**A row captured but never differenced is work already paid for and thrown away.**
The one real win of a recent session came entirely from rows already captured,
already clean, never reconciled. `scripts/unreconciled.py` exists to stop that
recurring — **run it after every batch.**

### 6. Structural module model

The blocker for ever predicting an **unseen** catalog. Module overhead is a
per-catalog lookup with a flat fallback today, which cannot generalise.

`module_io` is 2.9% of mass, so this is not an accuracy item — **it is a
generalisation item**, and it belongs with the phase-8 work on making the tool safe
to hand to someone else. See `FUTURE_TESTS.md` for the ladder it needs.

---

## Standing gates

These are process items, and every one of them exists because its absence cost
something. **They are the part that gets skipped, so they are listed as work.**

| gate | state |
|---|---|
| `quick_eval` prints the stopping-rule verdict every run | done |
| `quick_eval` scoped by default; `--full` only for reconciliation and final checks | done |
| Dead-architecture rows excluded from default reports, never from real rows | done |
| `capture_errors.py` routes every errored row to an owning question and exits non-zero otherwise | done |
| `confound_check.py` gates a generator before files are built | done |
| `unreconciled.py` run after every batch | **run it** |
| One capture roster, not five | one outstanding: item 1 |

---

## The unexplained residual pattern

Kept because it is the only structure left in the residual that has not been
explained away.

The ratio of residual to `routine_logic` bytes is **bimodal** across the real set.
It is not a per-unit error — coefficient of variation is 1.74 per occurrence, 1.72
over the top four instructions and 1.73 per rung, so whatever it is does not scale
with any count the engine has.

Ten files under-predict and seven over-predict. **A candidate that can only add
bytes is wrong before it is tested**, which eliminates most of what looks plausible
and is why item 1's per-type rate table matters more than its flat rate.

---

## Done, and not to be re-opened

| item | outcome |
|---|---|
| Verify the top instruction weights against real rung shapes | Worked. The weights hold exactly outside the shape they were fitted on. |
| Controller tag shapes | Closed negative. The residual is not in tag data space. |
| Rank open questions by real bytes × uncertainty | Done. This file is its output. |
| Write the stopping rule down and enforce it in code | Done. |
| Refresh the strip ladders | **Dead.** A derived variant of a real export does not build. See the read-only rule in `CLAUDE.md`. |
| The controller-shell probe | **Cancelled.** There was nothing to probe — the engine predicts a File\|New project exactly. |
| Produced and consumed tags | **Force-closed** below the noise floor. Do not reopen. |
