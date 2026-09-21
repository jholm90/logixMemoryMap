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

### 1. The INT/SINT literal widening defect

**The literal-operand batch came back and demoted its own question.** Integer
literals are free — measured at DINT and LINT, to the byte — so the 51,265-slot
exposure this item was ranked on does not exist. What the batch did find is an
engine defect worth more than the term it was looking for.

| | |
|---|---|
| **Expected movement** | unmeasured on the real set; it removes an 18–22% over-prediction on two isolation files |
| **Mechanism** | a narrow-integer TAG operand pulls in the widening block; a LITERAL needs no widening because it is already the right width inline. The engine charges the widening for both. |
| **Evidence** | `litop_type_int_lit` over by +21.82%, `litop_type_sint_lit` by +18.67%, while both tag files land at exactly 0.00% |

Only-adds-bytes candidates were the problem before. This one **removes** bytes,
and seven of the seventeen real programs over-predict.

**Wire nothing until it is checked against the seventeen.** The corpus exposure of
narrow-integer literal operands has not been counted.

### 1b. Two smaller terms from the same batch

- **REAL literal operand: +4 per slot.** Measured three times now — the bench
  rung, arm G at 1,000 rungs, and arm A's single-slot pair. 930 slots across the
  real set, 3,720 bytes. Exact, and far below the noise floor.
- **Float literal FORM: +76 per rung**, engine charges 0, one pair only. Ten times
  the REAL-literal term and a different mechanism. Needs a second count point
  before any rate is believed.

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

25 manifest rows have no capture. The literal-operand batch has landed and is
reconciled; what is left:

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
| Comments carry facts, not conversation or dates | done: every comment and docstring |
| No date in source | done: Python, YAML, JavaScript, PowerShell, AutoHotkey, docs |
| No customer program name in source | done: replaced by export numbers |
| No customer program name in git HISTORY | **not done -- see below** |

### Real exports are referred to by number

Every real export is `export NN` throughout the source, the docs and
`memory_model.yaml`. The numbering is stable and the names are gone.

A comparative claim needs the files told apart -- "one declares STRING[200],
another STRING[255]" is only checkable if both can be identified -- so the names
became numbers rather than vanishing into "a real export". Where a citation
pointed at a file only to say where a shape came from, it now reads "a real
export" and keeps the tag or member name, which is the part that makes it
checkable.

**`samples/manifest.csv` is the exception, and it is deliberate.** Its
`l5x_path` column is a real filesystem path into the gitignored
`samples/local/`. Rewriting it breaks prediction on all seventeen real programs
until the files on disk are renamed to match. `sample_id` and the row
descriptions are renamed to `realprog_NN`; `l5x_path` is not.

### Removing a name from the working tree does not remove it from history

The names are still in every earlier commit. `git log -p` recovers all of them,
and so does any existing clone, fork or cache. **A working-tree cleanup is not a
disclosure remedy.** If the requirement is that a public reader cannot find
them, the history has to be rewritten or the repository re-initialised from the
current tree, and even then anything already cloned stays out.

The mapping from export number back to the real filename is recoverable from
that same history and is not written anywhere in the tree on purpose.

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
