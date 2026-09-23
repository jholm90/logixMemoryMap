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

Re-ranked after the capture batch that followed the blind set. That batch closed five
questions (JSRCALLERBASE, RUNGSHAPE, ALARMCONDREAL, BUILDFAIL-OPEN, MODULENAMELEN) and,
by correcting the JSR caller base, exposed a larger real residual that a wrong
constant had been hiding: **mean 3.07%, worst 5.99% on the seventeen standard-processor
real programs**, all under-predicting.
Every item below is aimed at that.

### 1. Capture the operand-shape batch — OQ-OPERANDSHAPE, 26 files

| family | files | what it measures |
|---|---:|---|
| `opshape_xic_{plain,mem,nest,arrmem,bitword}_n{0250,1000}` | 10 | a read operand's shape |
| `opshape_ote_{plain,mem,nest,arrmem}_n{0250,1000}` | 8 | a written operand's shape |
| `opshape_mov_{plain,srcmem,dstmem,nest}_n{0250,1000}` | 8 | source vs destination member |

| | |
|---|---|
| **Expected movement** | up to the whole ~3% real residual, if member operands cost more than plain tags |
| **Mechanism** | half of all real operands are member paths (`A.B`, `A.B.C`); no calibration file has ever carried one, because lint refused them until this batch |
| **Needs** | one capture run |

### 2. Take safety content out of the standard total (engine correctness only)

Safety processors are out of scope for accuracy, so this no longer moves any headline
number; it is about a safety user's report being right.

Safety tags and safety logic live in a separate memory partition. Exclude Class="Safety"
program logic and Class="Safety" tags from the standard total; keep the measured 296
safety shell; keep standard-program references to safety tags as ordinary logic. Worth
0.7–1.9 points on the seven safety files, in the wrong-looking direction — correct, and
it removes a compensating error before it hides anything else.

### 2a. Calibrate file confidence to real error

The file-level confidence reads 97–99% on real programs whose error is 2–6%. It must
carry the unexplained real residual, not only the component bands, until that residual
is explained.

### 3. The real residual — OQ-REALUNDER

Once the operand batch reads, rerun the real set. If member operands carry the cost,
wire it and re-measure. If they do not, the next candidates in order are the other
things real rungs have and calibration rungs do not: many instructions per rung with
mixed operand shapes, and program-scoped tags at real density. No term is fitted on
the real set itself.

### 4. Structural module model — generalisation

Unseen 2198 drives and supplies are now priced from their family (4,113 / 3,589 first
copy, 984 repeat discount). An unseen non-2198 catalog still gets the flat 1,672, plus
its declared connection data; a generic Ethernet node gets the measured 4x connection
law. `module_io` is 2.9% of mass. See `FUTURE_TESTS.md`.

### Capture backlog

34 files: the 26 `opshape_*` of item 1 and the 8 `jsredge_*` JSR parameter edges
(structured returns, UDT-member arguments), below the noise floor but built to close
the last two JSR cases on measurement rather than mechanism.

**A row captured but never differenced is work already paid for and thrown away.**
Run `scripts/unreconciled.py` after every batch.

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
| One capture roster, not five | done: item 1 is the only roster |
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

With the JSR caller base corrected, all eighteen real programs present under-predict. **A candidate that can only add
bytes is wrong before it is tested**, which eliminates most of what looks plausible.

---

## Done, and not to be re-opened

| item | outcome |
|---|---|
| JSR caller base — OQ-JSRCALLERBASE | **Closed.** A caller routine costs what any routine costs; the per-caller 5,096 was an over-charge on every real program and is gone. |
| Per-rung term — OQ-RUNGSHAPE | **Closed negative.** 12 packing files, all exact. |
| Alarm conditions at real scale — OQ-ALARMCONDREAL | **Solved.** 0–600 real-shape conditions, flat +12 only. |
| Build-failure log — OQ-BUILDFAIL-OPEN | **Closed.** Every file builds; causes enforced in lint. |
| Module name length — OQ-MODULENAMELEN | **Bounded.** Law measured (name stored twice, each rounded to 8), 0.02% real exposure, not wired. |
| AOI call arguments | **Wired.** An Input argument that is not the literal 0/1 costs 28, not 16; an RLL file with AOI calls carries a one-time 264. |
| JSR with UDT/STRING parameters | **Wired.** A structured argument is copied like COP: +8 per call, +12 on the target. 8.0% → 0.03% on those files. |
| Safety processors in accuracy | **Excluded.** Accuracy is measured on standard processors only. |
| 2198 repeat and unseen catalogs | **Wired.** Family-wide repeat discount of 984; unseen drives and supplies priced from their family. |
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
| Partial exports on import — OQ-EXPORTSCOPE | **Closed, accepted in use.** AOI, UDT and program imports behave as needed; the unmeasured import shell stays uncharged. |
| Attribute the real residual with Studio-made deletions | **Declined.** Costs a bench session per reading. Struck from the plan; item 3 is what remains. |
| MAPC | **EXACT.** 260 bytes per call; the steps 1→10→100 are exact, the 100-call reading landing on the number written down before capture. |
| CROUT and the rest of the Safety family | **Ignored.** Out of scope, zero real uses; `instrfirst_crout_x10`'s errored row is owned by OQ-SAFETY. |
