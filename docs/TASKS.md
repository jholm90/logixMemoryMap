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

Re-ranked at the close of the final review, on the real programs rather than on the
generated corpus. The previous first item — the INT/SINT literal over-charge — was
counted on all eighteen real exports and is worth **1,756 bytes across all of them**.
It is closed. The queue is now short, and every item on it either needs a capture or
needs a real program.

### 1. Capture the blind set

**The single most valuable thing left.** Six real exports have been predicted by the
final engine with **no capacity reading on record**. Their predictions are written
down in `ROADMAP.md` before any reading exists, which is the only procedure this
project accepts as evidence that the model generalises. It has been done once;
this would do it six more times at once.

| | |
|---|---|
| **Expected movement** | none on the model — this measures it |
| **Mechanism** | read Capacity on each of the six, compare with the numbers already on record |
| **Needs** | the six programs opened in Studio; no files to build |

The five recorded real programs missing from this checkout (`realprog_08, 25, 26, 29,
30`) should be dropped back into `samples/local/` as well, so the full seventeen can be
re-checked by `quick_eval.py --real-only` rather than twelve of them.

### 2. Capture `jsr_callerdist_*` — OQ-JSRCALLERBASE

`jsr_fixed_base_per_routine` (5,096) exceeds the ordinary `fixed_base_per_routine`
(4,816) by 280, which is exactly the residual on every clean 0-parameter JSR capture.
The constant is charged per JSR-caller routine and every JSR file in the corpus has one
caller, so per-file and per-caller fit identically.

| | |
|---|---|
| **Expected movement** | between 280 bytes and ~300 KB on a real program, which is the point |
| **Mechanism** | six built files holding 20 calls and 20 targets fixed while callers run 1 → 20 |
| **Needs** | one capture run; predictions for all three readings are already on record |

It is also the last 50% line on most real programs: **Subroutine Overhead** reads
Unverified until this lands, and moves to Exact whichever way it reads.

### 3. The real residual — OQ-REALUNDER

**Mean 1.66%, worst 3.52% on the twelve real programs present; 1.60% / 3.63% on the
seventeen on record.** The weighted residual is **+1.45% under-prediction**. The
stopping rule is not met and a cheating per-category fit shows it cannot be met by
correcting constants. See `FINAL_REPORT.md` for the proposed attack: a real-program
residual model built from features the engine does not count, cross-validated, never
fitted in-sample.

### 4. Resolve the per-rung term — OQ-RUNGSHAPE

`routine_logic` is 18% of the mass. Every calibration file is one instruction per
rung, so a per-rung cost and a per-instruction cost are perfectly confounded in
every weight. A packing sweep must use a **non-output** instruction — the last
attempt used an output and measured series cascades instead.

### 5. Close the alarm-condition gap — OQ-ALARMCONDREAL

Alarm conditions are 9.4% of predicted mass and 19–21% of actual memory on the two
real programs measured, landing within 0.16% on one and **8.8% short** on the other.
Missing: alarms on a UDT-scalar host, and whether alarm **sets** carry their own cost.

### 6. Structural module model

A generalisation item, not an accuracy one: module overhead is a per-catalog lookup
with a flat fallback, which cannot predict an unseen catalog. `module_io` is 2.9% of
mass. See `FUTURE_TESTS.md`.

### Capture backlog

| family | rows | state |
|---|---:|---|
| `jsr_callerdist_*` | 6 | **top priority** — item 2 |
| `composite_realistic_*_r2` | 9 | never submitted; eight have real lint findings to clear first |
| `fwmatrix_*` | 6 | awaiting first submission |
| `alarmcond_*` | 5 | condition-type arm, never captured |
| `predefprobe_*` | 3 | submitted and refused; needs the Studio error line |
| `cipmodule_*` | 2 | awaiting first submission |
| `litop_bool_*` | 4 | regenerated with valid call arity; **optional** — below the noise floor |

**A row captured but never differenced is work already paid for and thrown away.**
It happened again: the fifteen `mbshape_*` real-shape AOI files had been captured,
clean, and never differenced. They answered the question they were built for
(OQ-AOIREALSHAPE) the day someone looked. Run `scripts/unreconciled.py` after every
batch.

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

**`samples/manifest.csv` carries no real file names either.** Every real row's
`l5x_path` is the neutral `samples/local/realprog_NN.L5X`. The real file name lives
in `samples/local/aliases.csv`, which is gitignored like everything else in that
folder, and `load_manifest()` resolves each row by name under `samples/local/`
through it — whatever folder the archive happened to unpack into. The old reason
for keeping real names in the manifest ("rewriting it breaks prediction") no longer
applies.

### Removing a name from the working tree does not remove it from history

The names are still in every earlier commit. `git log -p` recovers all of them,
and so does any existing clone, fork or cache. **A working-tree cleanup is not a
disclosure remedy.** If the requirement is that a public reader cannot find
them, the history has to be rewritten or the repository re-initialised from the
current tree, and even then anything already cloned stays out.

The mapping from export number back to the real filename is recoverable from
that same history. In the working copy it lives only in the gitignored
`samples/local/aliases.csv`.

---

## The unexplained residual pattern

Kept because it is the only structure left in the residual that has not been
explained away.

The ratio of residual to `routine_logic` bytes is **bimodal** across the real set.
It is not a per-unit error — coefficient of variation is 1.74 per occurrence, 1.72
over the top four instructions and 1.73 per rung, so whatever it is does not scale
with any count the engine has.

Ten files under-predict and seven over-predict. **A candidate that can only add
bytes is wrong before it is tested**, which eliminates most of what looks plausible.

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
| Literal operands, including the INT/SINT over-charge | **Closed on real exposure**: 37 slots, 1,756 bytes across eighteen real exports. |
| AOI definition cost | **KNOWN.** 8-byte total alignment wired; 117 of 125 def-only captures inside ±8. |
| Hiding per-element confidence by default | Done: `?ConfidenceMode=true` shows it; the Errors tab always shows the file-level figure. |
