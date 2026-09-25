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
constant had been hiding: **mean 2.86%, worst 5.42% (now 0.77% / 3.87% on eighteen —
operand spelling, then OQ-INDIRECTUDT and OQ-MIXEDTYPE, below) on the standard-processor
real programs**.
Every item below is aimed at that.

### 0g. The 174-capture batch — DONE

All 174 captured with zero build errors and no flagged reads (L9/v38 96, operand
spelling 50, realism 16, program scope 12). Closed eight questions; wired two:
- **OQ-INDIRECTUDT**: an index followed by a member +40 (KNOWN), a BOOL element +20,
  a STRING element +108 (FITTED).
- **OQ-MIXEDTYPE**: DINT↔REAL and DINT↔INT conversions per operand (FITTED).
Real set 1.79% → **0.77%** mean, 4.83% → **3.87%** worst; full census: no exact or
within-8 generated row moved. Confirmed without wiring: program scope is free;
the plant prices exactly at 25% and 50% fill; POINT I/O address = BOOL = alias;
REAL member/array spelling and AOI surcharges; STRING MOV = DINT MOV; L9 v38 = L81E
v38 + 2,276 and v35 → v38 = 0 on all 32 items. Series-output law exact again, still
unwired (OQ-SERIESREAL).

### 0k. Find the ~2% the series law was cancelling — NEXT

Checkpoint: tag `checkpoint-2026-09-25-pre-series-law`, commit `172f581` (0.58% state).
Real set with the law: 2.18% mean, 4.31% worst, all seventeen under, 1.19%–4.31%.

Already ruled out, measured:
- **Operand data types.** 91.7% of 84,846 real typed calls are one measured type,
  3.3% measured mixes; SINT/DINT, INT/REAL and other unmeasured mixes are 0.6%.
- **Instruction coverage.** Every native mnemonic with 5+ real uses is weighted.
- **Axes and alarm conditions.** They correlate with the gap only through size; both
  priced exact on the realism floor (`l9v38_m_kinetix`, `l9v38_m_alarms`), and real
  axis tags have exactly the generated tags' shape.
- **Documentation.** Descriptions and comments measured free.

**Where it lives (category scale test, seventeen programs).** Scaling one category alone
to absorb each file's shortfall: **routine logic needs +11.6%, spread ±3.1% across the
seventeen**, and would take the set to 0.45% mean. Every other category needs a scale that
varies wildly by file (tags +4.2% ±2.6%, UDT definitions +57% ±26%, modules +89% ±85%).
So the ~2% is almost certainly in **how real ladder is priced**, about 11% of logic,
consistently.

**What it is not, within logic.** The realism plant (1,280 stations of ordinary ladder
over 128 routines) prices exactly, so plain rungs, routines, member operands and the
XIC/OTE/TON/compare/ADD/MOV mix are right. Per-file counts of rungs, instructions,
operands, literals, branches, routines and AOI calls all fit the gap about equally
(0.45–0.6% mean), because all scale with size; 17 files cannot separate them.
Program-scope operand references are a few percent of real references and do not fit
(1.81%), though the two worst programs have the highest share (IPC 12%, export 18 25%).
Distinct operand paths per routine do not separate either: the plant has more (0.75 per
reference) than real ladder (0.53) and still prices exactly.

Leads, ranked:
0. **Feature transplant onto the plant** (spec, not built): the plant prices exactly, so
   add ONE real-ladder feature at a time at its real density and see which reads ~11%
   of its own logic under. About 12 files, each baseline + ~2,000 rungs: branch-heavy
   rungs (real density ~0.8 branch opens per rung), AOI calls at real density, 3-level
   member operands, JSR with parameters, literal-heavy MOV/compare, program-scoped
   operands, public program-scoped operands, COP/FLL block moves, bit-of-word operands
   (`Word.5`), timers/counters with real presets, CPT, and a mixed control.
**Transplant results (export 27, Studio-made).** Four of its programs were imported one
at a time INTO the plant (`realism_base_f25`, 840,384, priced exact), so each file's
error belongs to the imported content alone. Split by category, the shortfall is the
imported logic: **15.2%, 9.1% and 10.6% of added logic** on the three clean programs
(the fourth, 30.9%, carries a source-protected AOI and is a minimum by design) — the same
+11.6% ±3.1% the category test found across the seventeen. A second file with the spares
removed confirmed unused AOIs/spares are priced right (46,560 measured, 46,080
predicted). Real ladder against the plant, per 100 rungs: 530–680 instructions (plant
249), 116–214 extra writers (0), 70–94 branch openings (~10), 51–106 bit-of-word operands
(0), 187–259 multi-level member paths (0). Each of those was measured exact ALONE
(OQ-OPERANDSHAPE, OQ-SERIESREAL, branch tests), so the suspect is their combination in
dense rungs. Next: routine-level variants of the worst program (below).

**Source-protected AOIs: REJECTED — no sidecar, no user-supplied sizes, ever.** A
protected AOI stays priced at its visible interface with the source-protected warning;
the tool never takes sizes from the user. (Measured for reference: export 27's protected
AOI exposes ~20 of its 124 data-type bytes; its encrypted logic is likely ~15 KB of the
plant+Line2 transplant's 24,420 shortfall.) Do not re-propose it.

**Routine-level results (plant + export 27's worst program, one routine removed per
file, JSR and SBR removed with it).** All seven routines read short of the engine, by
6.8% to 38.6% of their predicted cost (136 to 1,184 bytes). Fitting the seven shortfalls
on two features at a time, the best pair is **operands that live in the motion system**:
~+50 per reference to an axis attribute (`Axis.ActualPosition`, `.ActualVelocity`,
`.AxisHomedStatus`, `.CommandVelocity`, `.RegEvent1Status`, …) and ~+29 per reference to
a MOTION_INSTRUCTION member (`Mam.DN`, `OTU(Mah.EN)`, …) — rms ±216 on seven points, so a
lead, not a constant. The engine prices both as plain operands and cannot resolve axis
attribute types at all. Real exposure (17 programs): 6,440 axis-attribute and 1,366
MI-member references; at those rates ~20% of the real shortfall on average (2% to 68% by
program). **Rung-level (Studio-made, one rung kept per routine, against the routine-removed file):** homing-routine rung 7 measured 712 vs 568 predicted (short 144, 25%); cam-correction rung 3 measured 2,484 vs 2,232 (short 252, 11%). The two-feature rates over-predict both rungs (~380 and ~600), so the motion lead is real in direction but not in size, and density is still in play. **Built, awaiting capture:** `gen_motion_operands.py`, 44 `motop_*` files (OQ-MOTIONOP, OQ-DENSERUNG) — axis REAL/BOOL attributes and MI members against paired plain controls, and a 1–64-units-per-rung density sweep. Real-rung templates (the two isolated rungs rebuilt over synthetic tags) were withdrawn before commit as customer-derived; the same question is answered by Studio-made variants of the real rung with its motion operands swapped for plain tags. Next: capture, then wire whichever premium the pairs show.

1. **Studio-made variants of export 27 (IPC, 4.31%) — METHOD AGREED.** Subtractive,
   one program at a time, starting from the full project:
   - Delete ONE program in Logix Designer (its routines and program tags). Leave
     controller tags, UDTs, AOIs and modules alone, so only that program's logic and
     program data leave.
   - Verify, read Capacity (Used), and **export the WHOLE project** (File > Save As
     .L5X), not a program-level export: only a whole-project file can be set against a
     whole-controller reading.
   - Save as `<export>_minus_<program>.L5X` with the Used figure; files go to
     `samples/local/` over chat, never the repository.
   - Order by the engine's predicted logic per program, largest first; the six largest
     carry ~70% of its logic.
   Per program: measured delta (full - variant) against the engine's delta for the same
   two files. A program whose measured delta beats its predicted delta by ~11% or more
   is where the shortfall lives; its rung shapes are then the next test. The variants
   are fitting inputs, not blind tests.
   **Next, one level down:** in the plant-plus-program file of the worst program, empty
   ONE routine at a time (delete its rungs, leave one `NOP();` so JSRs still verify),
   re-read Capacity, largest routines first. Each delta is one routine's rungs. — the technique that found literal
   operands. In Logix Designer, one change at a time, re-read Capacity: (a) delete the
   7 unused AOI definitions; (b) change the 83 `Usage="Public"` program tags to Local;
   (c) delete one heavy data-mapping program. Each gives an exact delta to set against
   the engine's own delta for the same content.
2. **Public program tags** (spec, not built): 6 files, the captured-exact
   `progscope_prog_{udt,arr}_n{010,050,200}` with every tag `Usage="Public"`,
   differenced directly against them. Only three real programs use public tags (83,
   41, 23 of them) and two are among the four worst.
3. **Module-typed operands**: 4.4% of real typed calls do not resolve, mostly
   `Module:slot:I.Data[n]` operands whose element type (often INT) the parser skips, so
   they pay the DINT rate. Code-only: resolve them from the module-defined types.
4. **Structure** (weak, 17 points): per-routine +339 and per-JSR +314 beyond size.
   Wait for leads 1–3.

### 0j. Series-output law — WIRED (option A)

−12 per extra writing instruction, TON counted. Headline 0.58% → 2.18% by design.

The 14 `srsty_*` captures make it universal: −12 per extra writing instruction in
every shape, timers included. Applied, all 38 series files are exact and the real set
reads 2.18% (all under) instead of 0.58%. Either ship it and hunt the ~2% under-charge
it exposes, or keep it off. See OQ-SERIESREAL.

### 0i. The other eight v36 renames — DONE (captured, ACS/ASN/TOD/FRD weights wired)

`gen_v36_renames.py`, 8 files: SQRT, TRUNC, EXPT, ACOS, ASIN, ATAN, TO_BCD, BCD_TO, one
each, 1756-L81E v38, realism floor, 1,000 rungs in the v35 calibration shape. A clean
import confirms v38 takes the name; SQRT/TRUNC/EXPT/ATAN are compared with their v35
weights, ACOS/ASIN/TO_BCD/BCD_TO have none on file and are measured. OQ-V36MNEMONIC.

### 0h. Series-output styles — CAPTURED (see 0j)

14 `srsty_*` files (`gen_series_styles.py`) for OQ-SERIESREAL, built on request: the
dominant real multi-output shape (branch legs with their own conditions, 61% of real
extra outputs) at k = 2/4/8, plus shared-condition legs, two-condition legs, nested
branches, output mid-rung, series latches, mixed writers in legs, and timers. Supersedes
spec item 1 below.

### Accuracy headline excludes protected-heavy programs — DONE

`quick_eval.py` drops real programs with 10+ `<EncodedData>` blocks (export 33 only).
Seventeen counted: 0.58% mean, 2.37% worst.

### Next batch — SPECIFIED, NOT BUILT (ask before generating)

Each answers a still-open item; v35 / 1756-L81E, realism floor.
1. **OQ-SERIESREAL, branch legs with their own conditions** — 6 files, 1,600 unique
   output BOOLs each: `[XIC(a)OTE(x),XIC(b)OTE(y)]` with k = 2, 4, 8 legs, against the
   same outputs as k single-output rungs (k01) and as `XIC(c)[OTE…]` (the measured
   output-only form). Discriminates: whether −12 applies when every leg has its own
   condition, the one real shape never built.
2. **Sixth POINT I/O rack over-predicted by 826** (`l9v38_m_pointio`) — 4 files: the
   baseline plus 1, 2, 4 extra RACK_n racks. Discriminates a per-rack repeat discount
   (AENTR/C or card) from a one-off. Differenced against `realism_base_f25`.
3. **Generic ETHERNET-MODULE under by 440** (`l9v38_m_geneth`, also +392 on the
   near-empty capture) — 3 files: 1, 2, 4 modules of 8/8 SINT. Separates a per-module
   overhead from the connection-data law. ETHERNET-MODULE is 25% of real modules.
4. ~~INT member alignment~~ — **dropped, below the floor in bytes.** 2,716 real typed
   calls carry an INT member operand (0.63% of 431,798 real instructions), but at +4
   each that is about 11 KB across every real export, ~0.02% of bytes.
Plus the 7 `bridgeph_*` files already built (OQ-BRIDGEPH), not yet converted.

### 0f. Export 43 — bridge placeholders, POINT I/O notices, indirect-bit usage — DONE, capture pending

Export 43 (1756-L81E v35, reading supplied with the file, so a fitting input) predicted
2,616,308 on receipt (−2.51%), 2,612,260 now (−2.66%). Its coverage notices were:
- **ETHERNET-BRIDGE placeholders** (inhibited, nothing beneath): charged the flat 2,344
  with a notice. Now 320 each, no notice, for a childless ETHERNET-BRIDGE only
  (OQ-BRIDGEPH). A gateway 1756-EN2T keeps the flat rate and its notice. 7 files
  built to confirm, awaiting capture.
- **Rack-aliased 1734 cards**: already priced (488 all-in, OQ-POINTIOCONN); the notice
  text claiming otherwise was stale and is gone.
- **Usage**: `Tag[Ptr].[BitNum]` (an indirect bit of an indexed element) failed to
  parse, so the array, pointer and bit-number tags read unused. 158 such operands
  across 18 real exports. Fixed and pinned in `tests/test_usage.py`.

### 0d. Usage counts in the UI — DONE

`l5x_memory_analyzer/usage.py`, built once per file at load. Every tag, member, array
element, UDT/AOI member, routine and module carries a use count in the List (**Uses**
column; unused rows tinted amber with an UNUSED pill) and in the treemap (amber stripes,
which take priority over the estimated-logic outline, and a tooltip note). A use is a
reference from ladder, ST or FBD operands, an alias target, an alarm input or associated
tag, an axis's motion group or drive module, a JSR target, or a main routine. Indexed
access uses every element; a file instruction on an element uses the whole array; a
reference to a whole structure uses its members "via parent" (the UDT definition view
still reports a member nothing names as unused, noting it is copied whole). AOI
EnableIn/EnableOut and hidden BOOL-packing members carry no count. HMI/SCADA access is
not visible in an L5X, and the tooltip says so. Pinned by `tests/test_usage.py`. The
light/dark toggle was removed; the page follows the OS setting.

### 0c. L9 (ControlLogix 5590) — DONE

96 files captured clean: L81E v38 = L81E v35 and L9 v38 = L81E v38 + 2,276 on all 32
content items (OQ-L9PLATFORM). Budgets from published user memory, 2 / 5 / 8 / 15 MB
(OQ-L9BUDGET). Nothing further planned for the L9.

### 0e. v36+ instruction names — done

Sixteen renames (EQU→EQ … MOV→MOVE, LIM→LIMIT, FRD→BCD_TO) priced identically to the v35
names; lint refuses the old name at v36+ and the new one below v36. Resolved,
`RESOLVED_QUESTIONS.md` OQ-V36MNEMONIC.

### 0b. UI: an AOI definition's "instance" size view disagrees with the instance tag

On the demo project (`scripts/build_demo_project.py`), opening Add-On Instructions ›
`Valve_Ctrl` with **AOI Size: instance** reads 28 B, the sum of its seven 4-byte members,
while the instance tag `V001` of that same AOI is priced at 104 B in Controller Tags. One
of the two views is leaving out the per-instance overhead the tag sizer charges. Fix so
both views give the instance tag's figure. The README deliberately shows the definition page
and the instance tag, not the instance view, until then.

### 0a. Operand spelling — DONE, 2.86% → 1.66%

The operand-type surcharge and the tag-driven index cost were charged only on bare tag
names. `sizing/operand_types.py` resolves member paths, aliases, program scope and AOI
parameters; the index regex accepts a member-path index. Real set 2.86% / 5.42% →
1.66% / 4.83%; zero generated rows moved. Four questions follow from it
(OQ-TYPEDMEMBER, OQ-INDIRECTUDT, OQ-STRINGMOV, OQ-MIXEDTYPE) — **50 files built**
(`gen_operand_spelling.py`, `samples/generated/opspell/`), awaiting capture alongside
the realism and progscope batches (78 files waiting in all). Ranked by expected
movement: INDIRECTUDT (≤0.6), STRINGMOV (0.2–0.6), MIXEDTYPE (0.1–0.4), TYPEDMEMBER
(confirmation of what is wired).

The confound gate counted any `[` as a branch, so an array subscript read as a branched
rung. Fixed (`_BRANCH_OPEN`, pinned in `test_confound_check.py`).

**Next audit of the same kind:** every other rule keyed on operand TEXT — CPT's REAL
destination (bare `tag_types` lookup), JSR structured-argument detection, CMP operands,
alarm AssocTag resolution — for a spelling it silently skips.

### 0. The realism floor — every generated file from here on

At least 5 Ethernet I/O nodes, at least 25% of the controller predicted, no output bit
written by more than one OTE/ONS and no OTL/OTU target also OTE'd. `sample_gen/realism.py`
builds a baseline that meets it (RACK_1..RACK_5: 1734-AENTR/C + 4 IB8 + 4 OB8 each; a
1,280-station plant, 842,178 predicted alone). `write_sample()` refuses a file below it
(`lint.realism_findings`) and `test_build_guards` refuses a waiting batch below it. An
older generator re-run without the baseline now fails, deliberately.

### 1. Capture the realism batch and the program-scope batch — 28 files

| family | files | question |
|---|---:|---|
| `realism_base_f{25,50}` | 2 | OQ-REALISMFLOOR — is the model exact on a full controller? |
| `realism_srout_{series,branch,inter}_k*` | 8 | OQ-SERIESREAL — does −12/extra output survive unique bits at real fill? |
| `realism_pio_{bool,addr,alias}_n{080,160}` | 6 | OQ-PIOADDR — POINT I/O address vs BOOL vs alias |

`samples/generated/realism/`, `gen_realism_batch.py`.

### 1b. The program-scope batch — OQ-PROGSCOPESTRUCT, 12 files (rebuilt on the baseline)

| family | files | what it measures |
|---|---:|---|
| `progscope_{ctl,prog}_udt_n{010,050,200}` | 6 | a 7-member UDT tag at controller vs program scope |
| `progscope_{ctl,prog}_arr_n{010,050,200}` | 6 | a DINT[20] array tag at controller vs program scope |

| | |
|---|---|
| **Mechanism** | program-scoped structured tags are in 14 of 17 real programs, densest in the three worst, and have never been built |
| **Needs** | one capture run |

The operand-shape batch that held this slot closed negative: member paths cost what
plain tags cost.

### 1a. Real rung skeletons — held until the realism batch reads

The proposed real-rung-skeleton batch (the commonest real instruction sequences with
generated tag names) waits on OQ-SERIESREAL and OQ-REALISMFLOOR: if the plant reproduces
the real under-prediction, the skeleton batch is built on the same baseline; if it lands
exact, fill is eliminated and the skeletons are the next discriminator.

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

12 files, the `progscope_*` of item 1. The `opshape_*` and `jsredge_*` batches are
captured and closed.

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
| Operand shape — OQ-OPERANDSHAPE | **Closed negative.** 26 files exact; member paths cost what plain tags cost. |
| JSR parameter edges | **Wired.** UDT member args at the structured rate; UDT returns +16/call; RET values 48 + 22 each, less 72 per target. |
| Source-protected content | **Reported.** Encrypted routines and AOIs are listed as an unpriced gap; not estimable. |
| Source-protected AOIs and routines | **Priced at a minimum**: stand-in definition from visible Parameters (instances, calls, interface); routine shells. UI banner says MINIMUM. 3.06% → 2.86%. |
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
