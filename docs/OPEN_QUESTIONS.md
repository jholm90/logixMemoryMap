# Open Questions

**Three: OQ-REALUNDER, OQ-STEXTENDED (batch E built) and OQ-STINSTR (opened 2026-10-25, batch F built).** Closed 2026-10-24 on the capture of batches B and C and the 1769
batch (RESOLVED_QUESTIONS, "Closed 2026-10-24"): OQ-UDTLAYOUT (wired: the aligned layout
predicted all twelve STRING-holding UDT files blind), OQ-STRSHAPE (every shape exact),
OQ-MODREPEAT (zero-connection catalogs wired; the packed 5069 card under the floor),
OQ-SAFETYLOGICIO (Output parameters, safety AOI call operands and slot-path reads wired;
RS-02 / RS-03 / RS-17 read −0.7 / −1.7 / −0.7% safety), OQ-UDTMEMBERNAME (measured, under the
floor) and OQ-CGL1769 (the 1769 programs inside 5% in both partitions). The nineteen standard
programs read **mean 1.158%, worst −2.66%, 18/19 inside 2%** (engine of 2026-10-24).

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

| question | state | answered by |
|---|---|---|
| **OQ-STINSTR** | Every instruction ST can call, one file each: 47 function blocks, 17 operand instructions, 18 ST functions, 10 motion instructions; the general-instruction list checked against the general instruction reference (1756-RM018). The engine has no weight for many (a call priced at nothing). Section 3. | batch F (`stinstr_*`, 93 files, built) |
| **OQ-STEXTENDED** | The ST constructs realprog_44 (the most ST-heavy program, the one outside 2%) writes and nothing has measured: function-block timers driven over several lines, JSR parameters into ST subroutines, AOI calls from ST, CASE, deep member paths behind tag indexes, string instructions, GSV / CPS, lower-case spelling. Section 2. | batch E (`ste_*`, 32 files, built) |
| **OQ-REALUNDER** | **1.158% mean, −2.66% worst, 8/19 inside 1%, 18/19 inside 2%** on the nineteen (2026-10-24, after the UDT layout); stopping rule NOT MET. Section 1. | the residual census below; `docs/REAL_PROGRAM_REPORT.md` |

---

## 1. OQ-REALUNDER — the residual itself

**Now 0.97% mean, 2.57% worst, 10/17 inside 1%** (2026-10-04) after the 92-file batch: InOut operands in AOI logic (+8 per instruction), AOI REAL arguments, AOI scan-mode routines (+268 each), a nested AOI call (+264 per calling definition), the motion literal law on MAJ/MAPC/MCCP/MAG. Worst: export 27 2.57%, export 16 2.23%, export 06 1.70%. Sum-weighted still +0.95%: the set still under-predicts. History below.

**Now 0.77% mean, 3.87% worst on eighteen programs** (export 43 added, with its reading, as a fitting input). The drop from 1.79% came from OQ-INDIRECTUDT (a member, BOOL or STRING element behind a tag-driven index costs 40 / 20 / 108 more than the calibrated 84) and OQ-MIXEDTYPE (DINT↔REAL and DINT↔INT conversions inside one call), both measured on the realism floor and wired with no generated exact row moving. Before that: 1.66% after operand spelling ("Spelling, not cost" below), and 2.86% in the history that follows.

**Standard processors only: mean 2.86%, worst 5.42% (after protected-content pricing), every one of the seventeen
standard-processor real programs present under-predicting.** Safety processors are
excluded from accuracy (CLAUDE.md, Platform scope). Including export 13, the one
safety program in the original set: mean 3.12%, worst 6.0% (sum-weighted +3.20%). That is worse than the 1.74% it read before
this batch, and the difference is a correction, not a regression:

- The per-caller `jsr_fixed_base_per_routine` (5,096) had only ever been measured on
  files with ONE caller routine, and was charged to every caller in real programs —
  10 to 87 of them. `jsrcallers_k*` proved a caller costs what any routine costs
  (OQ-JSRCALLERBASE). Removing the over-charge took the real set from 1.74% to 3.40%.
- The AOI argument cost (input references at 28, not 16) moved it back to 3.12%.
- The 2198 family repeat discount moved it to 3.13% — right on the Kinetix files,
  slightly wrong-way on real programs that carry many drives.
- The one-time 264 an RLL file with AOI calls carries moved it to 3.12%.
- Excluding safety processors from accuracy, and pricing structured JSR arguments as
  COP-style copies, leave the standard-processor figure at 3.07%.
- Pricing source-protected AOIs and routines at a minimum brought it to **2.86%**.

So about **3% of every real program is still unexplained**, and the old 1.7% figure was
that 3% partly cancelled by an error. This is CLAUDE.md failure mode 3 exactly, and the
right response is the same: keep the correct term, find the real one.

**What it tracks.** Everything size-like — programs (r = 0.92), routines (0.90),
rungs (0.86), tags (0.85) — and it is about 20% of the engine's `routine_logic` bytes.
No single count explains it under leave-one-out (best single term: JSR calls, LOO mean
1.16%, worst 4.9%), and a term fitted on the real set is not an answer anyway.

**The worst 25 generated files** — every clean standard-processor capture (3,130
rows) recomputed against the current engine, worst by |%|:

| # | file | error | what it is |
|---:|---|---:|---|
| 1–2 | `srout_ote_k08`, `sroutc_c01_k08` | +126% | 1,000 rungs of one XIC then 8 OTEs in a row |
| 3, 5 | `sroutc_c02_k08`, `sroutc_c04_k08` | +118%, +106% | the same with 2 or 4 conditions before the outputs |
| 4, 6, 8 | `srout_ote_k07/k06/k05` | +115% / +102% / +88% | 7, 6, 5 OTEs in a row |
| 7 | `bridge_placeholder_ten` | +95% | 10 ETHERNET-BRIDGE modules, no connections |
| 9 | `srout_branch_k08` | +82% | 8 OTEs in parallel branch legs under one condition |
| 10–14 | `srout_ote_k04`, `srout_same_k04`, `sroutc_*_k04` | +57% to +71% | 4 outputs in a row, same or repeated types |
| 15 | `pioconn_enhanced_n16` | +53% | POINT I/O adapter + 16 1734-IB8 cards, Enhanced (non-rack) connection |
| 16 | `srout_ote_k03` | +52% | 3 OTEs in a row |
| 17 | `srout_branch_k04` | +51% | 4 OTEs in parallel legs |
| 18 | `litop_form_floatform` | −51% | 1,000 `MOV(5.0, DINT)` — float-written literal into an integer |
| 19 | `prodcons_produced` | −49% | 20 Produced tags (force-closed below the noise floor) |
| 20 | `cptnar_j3of6` | −44% | `CPT` into a DINT from REAL operands (known narrowing defect) |
| 21 | `pioconn_enhdata_n16` | +35% | POINT I/O, one InputData connection per card |
| 22 | `srout_mixed_k04` | +33% | OTE, MOV, ADD, CLR in a row |
| 23 | `cptnar_j5of6` | −32% | CPT narrowing again |
| 24 | `closeout_cptmix_ddintoreal_m1` | −32% | CPT into a DINT mixing REAL and DINT operands |
| 25 | `addit_dn_lh` (and 5 more `addit_*_lh`) | +31% | 4,000 rungs of `XIC MOV ADD OTE` — three outputs in a row |

(+ is over-prediction.)

**What they say.** 18 of the 25 are one thing: **series outputs.** Every output after
the first in a rung measures exactly 12 bytes cheaper than its own weight, over 16+
files, and the engine does not apply it because real programs rejected it. Real
programs carry 1,900–11,800 such extra outputs each (0.5–1.5% of their bytes), so
applying the discount would push the real set to ~4% under. The generated corpus and
the real set therefore disagree about multi-output rungs, and the disagreement is the
same order as the gap. Restricting the discount to outputs with no condition between
them still covers ~60% of real extras, so no rewording of the rule fixes it — real
multi-output rungs need to be measured in a real shape.

Nearly every other large miss is an **over**-prediction too (bridge placeholders,
POINT I/O Enhanced cards), while the real set is **under**-predicted. Fixing the
generated corpus's worst rows moves real programs the wrong way: the real gap is
content the generated corpus does not contain, not a mispriced rule it does.

**Eliminated in the latest batch:**

- **Operand shape.** Member paths (`U.Bit`, `U.Sub.Bit`, `UA[2].Bit`, `U.Val`) cost
  exactly what plain tags cost on XIC, OTE and MOV — all 26 `opshape_*` files exact.
- **Trends.** 92 trend definitions across 11 of the 17 programs, unpriced, but the
  residual correlates *negatively* with trend and pen count (r = −0.23).
- **JSR.** Every case now measured and wired; 79 JSR files at 0.02% mean.

**Source-protected content — now priced at a minimum and flagged.** Export 33 carries 39
protected routines (~305,000 encrypted characters) that the engine cannot see; the
engine now lists them as an unpriced gap instead of charging zero silently. It is the
second-worst file, so part of its 5.6% is this, but no calibration from ciphertext to
compiled size exists.

**What distinguishes real programs from the generated files that fit.** The
multi-program composites (`composite_realistic_v3/v4`, `v3abl_*`: 7–11 programs,
JSR callers and targets, AOIs, modules) land within ±1% on the corrected engine. The
largest structural difference between them and real programs is **operand shape** —
see OQ-OPERANDSHAPE.

**Second blind set — exports 37–42, predicted before any reading existed:**

| export | controller | actual | predicted before the reading | error | inside the pre-written range |
|---|---|---:|---:|---:|---|
| 37 | 5069-L330ERMS2 | 1,572,161 | 1,495,547 | −4.87% | yes |
| 38 | 1756-L81ES | 2,007,604 | 1,832,104 | −8.74% | no (below) |
| 39 | 5069-L340ERS2 | 2,935,942 | 2,811,103 | −4.25% | yes |
| 40 | 5069-L320ERMS2 | 1,279,555 | 1,211,456 | −5.32% | yes |
| 41 | 5069-L310ERS2 | 511,973 | 481,589 | −5.93% | no (below) |
| 42 | 1769-L33ERMS | 884,640 | 840,245 | −5.02% | yes — dead architecture, excluded from accuracy |

All six under-predict, by 4.2% to 8.7%; four of six inside the range written down in
advance. **None counts toward accuracy**: five are safety processors and one is a 1769,
both out of scope. They are recorded as evidence of direction only. On the five in scope the mean is 5.82%. Five are safety controllers, but their
safety content is small — one safety program, 2–8% of rungs — and does not explain it.

**Safety memory is a separate partition.** A safety controller keeps safety tags and
safety logic in its own memory, which does not count toward the standard memory that
Capacity reports for standard logic and data. Non-safety tags may not be used in a
safety program; safety tags MAY be used in standard programs, where they cost standard
**logic** (the reference) but not standard **tag** memory. The engine still sizes safety
routine logic (Class="Safety" programs) and Class="Safety" controller tags into the
standard total — 6.7 KB to 22.8 KB on the seven safety files with readings. The measured
296-byte safety task/program shell stays: it was fitted against real standard-memory
readings. Excluding the rest is the correct model and moves those files 0.7 to 1.9
points further under, so it is not the source of the gap.

**The confidence display is not calibrated to real error.** With the Subroutine
Overhead line gone, file confidence reads 97–99% on most real programs (export 07:
99.2%), while their real error is 2–6% (export 27: 98.5% confident, 6.0% wrong). The
bands describe how well each *component* is measured on isolation files; they say
nothing about the unexplained real residual. Until that residual is explained, the
file-level figure must carry it.

### Spelling, not cost — 2.86% → 1.66% with no constant changed

Two measured costs were being charged only when the operand was spelled one way.

1. **The operand-type surcharge** (SINT/INT/REAL/STRING, `operand_type_surcharge`)
   resolved only a BARE controller tag name. A member path (`Stn.Pv`), an array
   element (`Arr[i].Cnt`), an alias, a program-scope tag and an AOI parameter inside
   the AOI's own logic all resolved to nothing and paid DINT rate. Half of all real
   operands are member paths, and OQ-OPERANDSHAPE had already measured a member path
   costing exactly what a plain tag costs. `sizing/operand_types.py` now follows every
   spelling to its type. Real set: 2.86% / 5.42% → **1.98% / 4.89%**, 17 of 17 files
   toward zero, 11–119 KB per file.
2. **The tag-driven index** (84, or 108 with an offset) matched only a bare index tag,
   so `Arr[Stn.Idx]` and `Arr[Stn.Idx+1]` — 2,700 real occurrences — were free. Same
   mechanism, spelled as a member. Real set → **1.66% / 4.83%**, 16 of 17 better;
   exports 18 and 10 land at +23 and −96 bytes (0.00%).

Full census on both changes: all 3,234 captured generated rows **unchanged** (no
calibration file uses either spelling), 18 real rows moved, the only one worse is
export 13, a safety processor excluded from accuracy. Pinned by
`tests/test_operand_types.py`.

**So the calibration corpus's defining habit — bare tag names — hid the gap, not a
wrong constant.** The same audit applies to every other rule keyed on operand text;
the four questions below are the shapes real programs use and no file has measured.

**Leads not yet a mechanism.** After the two fixes, CONCAT count alone fits the
remaining residual at LOO 0.99% (0.82% without export 33) — but at ~900 bytes per
CONCAT, ten times CONCAT's own measured weight, and 1,640 of 1,850 real CONCATs are
plain `STRING` in the calibrated shape. It is a proxy for something string-heavy,
most likely STRING MOV (OQ-STRINGMOV) or string-typed tag content, not a cost.
Export 33 (4.83%) is dominated by 39 source-protected routines the engine cannot see.

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

### Re-scored 2026-10-23: nineteen standard programs, mean 1.262%, worst −2.83%

Every standard-processor program with a reading on disk (the owner's capture of 2026-10-23, read
by the capture tool from the L5X), engine of 2026-10-23, `scripts/quick_eval.py --real-only`:
**mean 1.262%, worst −2.83% (realprog_44), 7/19 inside 1%, 15/19 inside 2%, sum-weighted
−1.29%.** Stopping rule NOT MET. realprog_33 (39 source-protected routines) excluded: −2.97%.
realprog_07, _25, _26, _29, _30 and _31 and _43 had a reading and no file on disk: their records are
deleted (owner, 2026-10-23: the current engine is the only basis, and a reading with no file to
price is no reference). realprog_37 to _42 are the safety-controller programs RS-08, RS-01, RS-10,
RS-05, RS-04 and RS-16 (the last by platform: the only 1769-L33ERMS v32.13 file). Every figure is
also in `docs/REAL_PROGRAM_REPORT.md`, regenerated by `scripts/real_program_report.py`. Labels
key to the git-ignored `samples/local/aliases.csv`; realprog_44 to _47 are new and arrived with their readings (fitting
inputs, not blind).

| label | platform | engine | with the hostlast UDT layout (OQ-UDTLAYOUT, not wired) | |
|---|---|---:|---:|---|
| realprog_44 | 1756-L82E | -2.83% | -2.66% | new 2026-10-23 |
| realprog_16 | 1756-L82E | -2.06% | -1.98% |  |
| realprog_27 | 1756-L81E | -2.04% | -1.98% | re-read -20,456 against the reading on file |
| realprog_46 | 1756-L83E | -2.04% | -1.93% | new 2026-10-23 |
| realprog_36 | 1756-L83E | -1.67% | -1.55% |  |
| realprog_09 | 1756-L83E | -1.51% | -1.33% |  |
| realprog_01 | 1756-L83E | -1.43% | -0.74% |  |
| realprog_06 | 1756-L82E | -1.41% | -0.77% | re-read -19,928 against the reading on file |
| realprog_47 | 1756-L83E | -1.38% | -1.16% | new 2026-10-23 |
| realprog_45 | 1756-L83E | -1.34% | -1.19% | new 2026-10-23 |
| realprog_32 | 1756-L83E | -1.24% | -0.89% |  |
| realprog_35 | 1756-L83E | -1.16% | -0.89% |  |
| realprog_17 | 1756-L81E | -0.88% | -0.82% |  |
| realprog_34 | 1756-L83E | -0.76% | -0.51% |  |
| realprog_08 | 5069-L330ERM | -0.18% | -0.05% | re-read -21,440 against the reading on file |
| realprog_28 | 1756-L81E | +0.24% | +0.34% | re-read -20,936 against the reading on file |
| realprog_14 | 1756-L81E | +0.27% | +0.73% | re-read -728 against the reading on file |
| realprog_10 | 1756-L81E | +0.73% | +0.81% | re-read -24,896 against the reading on file |
| realprog_18 | 1756-L81E | +0.81% | +1.14% | re-read -19,392 against the reading on file |

**Six earlier exports re-read about 20 KB lower** than the reading on file (−19,392 to −24,896;
realprog_14 −728), across programs of 0.9 to 5.2 MB, while ten others re-read to the byte. The
readings on file for those six were not taken by the capture tool from an L5X-built ACD; the new
ones were, as every generated file is. Which one the model should predict is the owner's to
settle (TASKS 0zh); the table uses the new readings.

**What the deep dive found (2026-10-23):**

- **The common shortfall is tag data, and it is UDT layout** (OQ-UDTLAYOUT, Section 6). Scaling
  one category at a time, fitted on the real set as a diagnostic only, `controller_tag` by 2%
  gives the best worst case of any category (LOO 0.74%, max 1.72%). The engine sizes a UDT as the
  plain sum of its members. The one realistic mixed UDT ever captured reads 240 an array element
  against 216 priced, exactly a naturally aligned layout. A layout that also keeps every packed
  capture exact (below) takes the set to **1.130% / −2.66%**, full natural alignment to
  **0.970% / −2.32%**.
- **The scalar AOI law (OQ-AOIBOOLINST) took 0.16 points of mean** (1.099% without it): it
  lowered every program 1 to 40 KB. It is right on 22 isolation files and moved 70 of 75 AOI
  captures closer; it uncovered a shortfall rather than causing one.
- **ST is realprog_44's own extra, not the common term.** realprog_44 carries 3,051 ST
  statements (308 KB priced), the other three over 2% almost none. Its ST is mostly copies
  (DINT 1,100, BOOL 275, INT 234, a custom string 89) through deep member paths with a tag index
  on an array that is itself a member, 1,244 times, a shape no file has measured; at ~45 more a
  site it would carry the program's excess over the common shortfall. Its four unsized
  encoder-diagnostic tags are under 1 KB.
- **Zero-connection modules** on the flat 2,344: realprog_16 carries four peer controllers,
  realprog_47 five, realprog_35 four; batch C's `zcm_*` prices them, in the over-prediction
  direction.
- **Eliminated on these nineteen:** event tasks, periodic tasks, AOI definitions, parameters and
  locals, alarm conditions, documentation volume (rung comments, descriptions, member comments;
  every program downloads its documentation), MSG, aliases, SBR / RET, COP / FLL — none beats a
  uniform size scaling under leave-one-out (0.777% / 2.20%), which is itself a fit on the real set
  and not wired.

### The standard figure on real safety-controller programs — not counted toward accuracy

Safety processors are excluded from accuracy (CLAUDE.md), but their standard Capacity is the
quantity the model predicts, so they are evidence of direction. Engine of 2026-10-23 (unchanged
since 2026-10-21), prediction minus reading: RS-02 −1.89%, RS-03 −0.27%, RS-04u −0.61% (locked
−2.80%), RS-05 −2.38%, RS-06 / RS-09 +1.65% / +1.66%, RS-07 +0.25%, RS-08 −2.45%, RS-10 −2.01%,
RS-17 −0.26%: **mean 1.34%, worst −2.45% on the ten.** RS-01 (−8.19%) stays uncounted: it
carries SFC, which is out of scope.

Where the rest points (2026-10-23):

- **STRINGs held in UDTs.** RS-05 / RS-08 / RS-10 hold 35 to 49% of their predicted bytes in
  scalar tags of UDTs that hold STRINGs, most of them in arrays nested one level down, against 3
  to 5% in RS-02 / RS-03 / RS-07. A STRING member at 88 rather than 86 is worth about 0.6 / 0.35 /
  0.9 points on the three, a custom string at 48 rather than 44 about 0.2 / 0.6 / 0.1 more
  (OQ-STRSHAPE; batch B `strm_*`, batch C `strn_*`).
- **Zero-connection modules on the flat rate**, the other way: RS-07 carries seven (16,408
  bytes at 2,344 each), RS-05 two, RS-10 one; every zero-connection catalog measured costs 320 to
  625 (OQ-MODREPEAT; batch C `zcm_*`). If these read like the others, RS-07 moves to about −0.9%.
- **RS-06 / RS-09's +1.65%** is content priced at v32 (batch B, `safe_base_5069l320_v32`).

A standard array tag's +4 on the realism plant: closed 2026-10-23, BOUNDED (RESOLVED_QUESTIONS,
OQ-ARRAYTAG4).

---

## 2. OQ-STEXTENDED — the ST that realprog_44 writes, opened 2026-10-24

realprog_44 is 123 ST routines, 3,051 statements and 19,977 lines, the one standard program
outside 2%. Census against the other eighteen (read only, 2026-10-24): it is the only program
with function-block timers in ST (TONR on FBD_TIMER, each driven over five lines: PRE,
TimerEnable, Reset, the call, the ACC or DN read), JSR with parameters from ST into ST
subroutines that take them with SBR and return with RET (112 calls), AOI calls from ST (41),
18 CASE blocks, 1,361 tag-driven indexes and 709 three-deep member paths, CONCAT / DTOS /
DELETE / FIND / SIZE, GSV / SSV and CPS in ST, and instruction names and keywords in lower or
mixed case (`cop`, `Cop`, `jsr`, `sbr`, `Concat`, `Ret`, `Size`, `if ... then ... end_if`).

**Fixed in code the same day:** the instruction scanner shared with ladder matched upper-case
mnemonics only, so every lower- or mixed-case instruction call in ST was priced at nothing;
an instruction in any case is now its mnemonic (`structured_text.upper_case_mnemonics`; a
declared AOI keeps its spelling). realprog_44 −2.66% → −2.32%; no other real program writes
them. And a REAL one-operator multiply, measured long ago (`stshape_real_mul400` reads exactly
`stshape_real400`), is no longer flagged unpriced.

**What the engine still does not price, by construction:** TONR / TOFR / RTOR carry no weight
(a timer call costs nothing); a JSR's parameters from an ST caller are not counted (only ladder
callers are); the three-deep path and CASE shapes are extrapolated from shallower ones.

**Batch E** (`gen_st_extended.py`, 32 files, `samples/generated/stext/`): one JSR-called ST
routine on the realism floor, 1756-L81E v35; every file carries the same tags, UDTs (a nested
one), two AOIs and two ST subroutines, so each differences against `ste_n00`. Predicted before
any reading (engine of 2026-10-24; the reading is the engine's less the plant's 1,794 where
the engine is right):

| file | what | engine | step over `ste_n00` |
|---|---|---:|---:|
| `ste_n00` | control: one assignment | 941,678 | +0 |
| `ste_tonr_full50` | 50 FBD_TIMER timers each driven over five lines: PRE, TimerEnable, Reset, TONR, the ACC read | 948,838 | +7,160 |
| `ste_tonr_call50` | 50 TONR calls alone | 941,638 | -40 |
| `ste_tonr_set50` | the same four member lines on each timer without the TONR call | 948,838 | +7,160 |
| `ste_tonr_dnif50` | 50 TONR calls each followed by an IF on its DN bit with an ELSE | 950,038 | +8,360 |
| `ste_tofr_full50` | the five-line timer with TOFR | 948,838 | +7,160 |
| `ste_rtor_full50` | the five-line timer with RTOR | 948,838 | +7,160 |
| `ste_jsr0_50` | 50 JSR without parameters to an ST subroutine | 945,038 | +3,360 |
| `ste_jsr3_50` | 50 JSR passing three parameters and taking one back, into the ST subroutine that takes them with SBR and returns with RET | 945,038 | +3,360 |
| `ste_jsr3deep_50` | the same with the parameters written as member paths behind tag indexes | 955,038 | +13,360 |
| `ste_jsr3lower_50` | ste_jsr3_50 written in lower case | 945,038 | +3,360 |
| `ste_aoi_p2_50` | 50 calls of an AOI with two Required DINT inputs | 949,502 | +7,824 |
| `ste_aoi_p6_50` | 50 calls of an AOI with six Required DINT inputs | 952,702 | +11,024 |
| `ste_aoi_p6deep_50` | the same with member-path arguments | 962,702 | +21,024 |
| `ste_case20x5` | 20 CASE blocks of five selectors, one statement each | 951,338 | +9,660 |
| `ste_case20x10` | 20 CASE blocks of ten selectors | 961,038 | +19,360 |
| `ste_casemember20x5` | 20 CASE blocks of five selectors on a member-path selector | 951,338 | +9,660 |
| `ste_dot3_400` | 400 assignments through a nested UDT's members (three deep) | 957,638 | +15,960 |
| `ste_vidxdot3_400` | the same with the destination behind an index written as a member path | 1,007,238 | +65,560 |
| `ste_innerarr400` | 400 assignments on a UDT member's array element indexed by a tag | 1,021,638 | +79,960 |
| `ste_amp400` | 400 BOOL destinations from an &  | 954,438 | +12,760 |
| `ste_concat100` | 100 CONCAT | 952,038 | +10,360 |
| `ste_dtos100` | 100 DTOS | 948,838 | +7,160 |
| `ste_delete100` | 100 DELETE | 951,638 | +9,960 |
| `ste_find100` | 100 FIND | 951,638 | +9,960 |
| `ste_size50` | 50 SIZE on a UDT array | 948,038 | +6,360 |
| `ste_cop200` | 200 COP of a UDT element | 964,038 | +22,360 |
| `ste_coplower200` | ste_cop200 written in lower case | 964,038 | +22,360 |
| `ste_gsv50` | 50 GSV of the wall clock into a DINT array | 945,838 | +4,160 |
| `ste_cps50` | 50 CPS of a UDT element | 947,238 | +5,560 |
| `ste_ifupper200` | 200 IF blocks, keywords in upper case | 959,238 | +17,560 |
| `ste_iflower200` | the same with keywords in lower case | 959,238 | +17,560 |

**What decides it:** `ste_tonr_call50` against `ste_n00` prices a timer call, `_set50` its
member lines, `_full50` both together (additivity), `_dnif50` the DN read in a condition;
TOFR / RTOR whether every FB timer costs the same. `ste_jsr3_50` against `ste_jsr0_50` prices
three parameters and a return from an ST caller; `_deep` the member-path arguments; `_lower`
confirms the case fix on the device. `ste_aoi_p2` / `_p6` the per-parameter AOI rate from ST at
a second count; `ste_case20x5` / `x10` the per-selector rate; the path files the three-deep and
inner-array forms; the string, GSV and CPS files each instruction's ST weight against its
ladder weight; `ste_iflower200` against `ste_ifupper200` that keyword case costs nothing.

**CAPTURE ERRORS: 0 row(s)** (not yet captured).

## 3. OQ-STINSTR — every instruction ST can call, opened 2026-10-25

**Owner's request 2026-10-25:** a test for every instruction ST can call, those ladder cannot
call included. The instruction list is the engine's weight table, the real programs' ST and
the function blocks of the FBD manual (1756-PM009), and since 2026-10-29 the general
instruction reference (1756-RM018, chat-only): every instruction whose ST entry there gives a
call form, and every operator and function its expression table marks usable in ST, is in
batch E or F or listed below with its reason. The process and drives reference (1756-RM006)
and the motion reference (MOTION-RM002) are not on file, so the function-block and motion
lists are still checked against them when they arrive.

**Checked against RM018 (2026-10-29), what changed:** AVE and STD are ladder-only, so their
two files were removed; ATAN2, TOD, FRD, IsINF and IsNAN are ST functions and were added
(TOD / FRD are the spellings below v36 of TO_BCD / BCD_TO; ATAN2, IsINF and IsNAN apply to the
5380 / 5580 families and their firmware floor is not stated, so a conversion failure on one
of those three files at v35 is the answer to that, not a defect to chase). TRUNC stays: the
real programs at v32 to v35 write TRUNC in ST (the v36 rename is a ladder rename). The
ladder-only instructions (TON / TOF / RTO, CTU / CTD, RES, FAL / FSC / FLL, BTD, MVM, CLR, the
compare and arithmetic instructions, NEG, MCR, AFI, NOP, UNK, LV) are written in ST as
operators or not at all and have no file here; the ST operators are batch-C and closeout
territory (`gen_st_expression_grid.py`, `gen_st_closeout.py`). Batch E already carries
TONR / TOFR / RTOR, JSR / SBR / RET, AOI calls, CONCAT / DTOS / DELETE / FIND / SIZE, COP, CPS
and GSV.

**Left out, each with its reason:** ALMD / ALMA (parked, CLAUDE.md "Out of scope until
real-file error is under 1%"); ASO (an alarm-set operation: alarm instructions are parked and
no real program has an alarm set); REF (its operand is a REF_TO_AXIS reference type that no
file here has built and no real program uses, so its tag XML would be a guess); SFP / SFR (SFC is never worked); ABL / ACB / ACL / AHL / ARD /
ARL / AWA / AWT (a 1756-L81E has no serial port, so a file built on the standard platform
cannot verify); the equipment-phase and equipment-sequence instructions (they need phase
programs and sequences, a structure no file builds); every motion instruction whose operand
list no captured file has proved (MAG, MCD, MCS, MCLM, MCCM, MCCD, MCT, MCTP, MCSV, MCPM,
MAPC, MATC, MDAC, MAOC, MDOC, MGS and the rest: the motion reference is needed first).

**Batch F** (`gen_st_instructions.py`, 93 files, `samples/generated/stinstr/`): one
JSR-called ST routine on the realism floor, 1756-L81E v35; each file the plant, the
instruction's own backing tags (every structure priced exactly by the engine) and 50 calls (20
for CC / IMC / MMC). The reading less the engine's figure is what the calls cost in ST. In ST
the motion operands that ladder writes as keywords are numbers (`Units per sec` 0, `S-Curve` 1,
`% of Maximum` 1): the one assumption in the batch, and the first thing a build error on a
`stinstr_mo_*` file would name. Predicted before any reading (engine of 2026-10-25):

| file | calls | engine | over `stinstr_n00` |
|---|---|---:|---:|
| `stinstr_n00` | control: the plant, the common tags and one assignment | 853,718 | +0 |
| `stinstr_fb_ctud` | 50 CTUD calls, each on its own FBD_COUNTER | 859,278 | +5,560 |
| `stinstr_fb_osri` | 50 OSRI calls, each on its own FBD_ONESHOT | 858,878 | +5,160 |
| `stinstr_fb_osfi` | 50 OSFI calls, each on its own FBD_ONESHOT | 858,878 | +5,160 |
| `stinstr_fb_setd` | 50 SETD calls, each on its own DOMINANT_SET | 858,878 | +5,160 |
| `stinstr_fb_resd` | 50 RESD calls, each on its own DOMINANT_RESET | 858,878 | +5,160 |
| `stinstr_fb_dff` | 50 DFF calls, each on its own FLIP_FLOP_D | 858,478 | +4,760 |
| `stinstr_fb_jkff` | 50 JKFF calls, each on its own FLIP_FLOP_JK | 858,878 | +5,160 |
| `stinstr_fb_btdt` | 50 BTDT calls, each on its own FBD_BIT_FIELD_DISTRIBUTE | 859,678 | +5,960 |
| `stinstr_fb_mvmt` | 50 MVMT calls, each on its own FBD_MASKED_MOVE | 859,278 | +5,560 |
| `stinstr_fb_scl` | 50 SCL calls, each on its own SCALE | 860,478 | +6,760 |
| `stinstr_fb_pide` | 50 PIDE calls, each on its own PID_ENHANCED | 878,078 | +24,360 |
| `stinstr_fb_alm` | 50 ALM calls, each on its own ALARM | 862,478 | +8,760 |
| `stinstr_fb_intg` | 50 INTG calls, each on its own INTEGRATOR | 862,478 | +8,760 |
| `stinstr_fb_pi` | 50 PI calls, each on its own PROP_INT | 864,478 | +10,760 |
| `stinstr_fb_pmul` | 50 PMUL calls, each on its own PULSE_MULTIPLIER | 860,478 | +6,760 |
| `stinstr_fb_scrv` | 50 SCRV calls, each on its own S_CURVE | 864,078 | +10,360 |
| `stinstr_fb_soc` | 50 SOC calls, each on its own SEC_ORDER_CONTROLLER | 866,478 | +12,760 |
| `stinstr_fb_updn` | 50 UPDN calls, each on its own UP_DOWN_ACCUM | 859,678 | +5,960 |
| `stinstr_fb_hpf` | 50 HPF calls, each on its own FILTER_HIGH_PASS | 865,678 | +11,960 |
| `stinstr_fb_lpf` | 50 LPF calls, each on its own FILTER_LOW_PASS | 865,678 | +11,960 |
| `stinstr_fb_ntch` | 50 NTCH calls, each on its own FILTER_NOTCH | 867,278 | +13,560 |
| `stinstr_fb_ldlg` | 50 LDLG calls, each on its own LEAD_LAG | 864,878 | +11,160 |
| `stinstr_fb_ldl2` | 50 LDL2 calls, each on its own LEAD_LAG_SEC_ORDER | 866,878 | +13,160 |
| `stinstr_fb_derv` | 50 DERV calls, each on its own DERIVATIVE | 862,478 | +8,760 |
| `stinstr_fb_tot` | 50 TOT calls, each on its own TOTALIZER | 863,678 | +9,960 |
| `stinstr_fb_d2sd` | 50 D2SD calls, each on its own DISCRETE_2STATE | 860,078 | +6,360 |
| `stinstr_fb_d3sd` | 50 D3SD calls, each on its own DISCRETE_3STATE | 860,478 | +6,760 |
| `stinstr_fb_esel` | 50 ESEL calls, each on its own SELECT_ENHANCED | 861,278 | +7,560 |
| `stinstr_fb_hll` | 50 HLL calls, each on its own HL_LIMIT | 859,678 | +5,960 |
| `stinstr_fb_mux` | 50 MUX calls, each on its own MULTIPLEXER | 860,878 | +7,160 |
| `stinstr_fb_rlim` | 50 RLIM calls, each on its own RATE_LIMITER | 862,878 | +9,160 |
| `stinstr_fb_sel` | 50 SEL calls, each on its own SELECT | 858,878 | +5,160 |
| `stinstr_fb_sneg` | 50 SNEG calls, each on its own SELECTABLE_NEGATE | 859,278 | +5,560 |
| `stinstr_fb_ssum` | 50 SSUM calls, each on its own SELECTED_SUMMER | 862,478 | +8,760 |
| `stinstr_fb_maxc` | 50 MAXC calls, each on its own MAXIMUM_CAPTURE | 859,678 | +5,960 |
| `stinstr_fb_minc` | 50 MINC calls, each on its own MINIMUM_CAPTURE | 859,678 | +5,960 |
| `stinstr_fb_posp` | 50 POSP calls, each on its own POSITION_PROP | 864,478 | +10,760 |
| `stinstr_fb_srtp` | 50 SRTP calls, each on its own SPLIT_RANGE | 863,678 | +9,960 |
| `stinstr_fb_imc` | 20 IMC calls, each on its own IMC | 941,678 | +87,960 |
| `stinstr_fb_cc` | 20 CC calls, each on its own CC | 1,029,198 | +175,480 |
| `stinstr_fb_mmc` | 20 MMC calls, each on its own MMC | 1,183,118 | +329,400 |
| `stinstr_fb_hmibc` | 50 HMIBC calls, each on its own HMIBC | 859,678 | +5,960 |
| `stinstr_fb_dedt` | 50 DEDT calls, each on its own DEADTIME with its Storage REAL[10] arguments | 863,810 | +10,092 |
| `stinstr_fb_fgen` | 50 FGEN calls, each on its own FUNCTION_GENERATOR with its X1, Y1, X2, Y2 REAL[10] arguments | 861,406 | +7,688 |
| `stinstr_fb_mave` | 50 MAVE calls, each on its own MOVING_AVERAGE with its Storage, Weight REAL[10] arguments | 861,142 | +7,424 |
| `stinstr_fb_mstd` | 50 MSTD calls, each on its own MOVING_STD_DEV with its Storage REAL[10] arguments | 861,410 | +7,692 |
| `stinstr_fb_rmps` | 50 RMPS calls, each on its own RAMP_SOAK with its Ramp, Soak, Time REAL[10] arguments | 864,074 | +10,356 |
| `stinstr_op_pid` | 50 PID calls | 874,678 | +20,960 |
| `stinstr_op_msg` | 50 MSG calls | 894,678 | +40,960 |
| `stinstr_op_ssv` | 50 SSV calls | 857,878 | +4,160 |
| `stinstr_op_iot` | 50 IOT calls | 853,678 | -40 |
| `stinstr_op_event` | 50 EVENT calls | 857,186 | +3,468 |
| `stinstr_op_uid` | 50 UID calls each bracketed by UIE | 859,678 | +5,960 |
| `stinstr_op_tnd` | 50 TND calls | 857,278 | +3,560 |
| `stinstr_op_eot` | 50 EOT calls | 853,678 | -40 |
| `stinstr_op_swpb` | 50 SWPB calls | 857,478 | +3,760 |
| `stinstr_op_insert` | 50 INSERT calls | 859,478 | +5,760 |
| `stinstr_op_mid` | 50 MID calls | 858,678 | +4,960 |
| `stinstr_op_stod` | 50 STOD calls | 857,678 | +3,960 |
| `stinstr_op_rtos` | 50 RTOS calls | 857,278 | +3,560 |
| `stinstr_op_stor` | 50 STOR calls | 857,678 | +3,960 |
| `stinstr_op_upper` | 50 UPPER calls | 857,878 | +4,160 |
| `stinstr_op_lower` | 50 LOWER calls | 853,678 | -40 |
| `stinstr_op_srt` | 50 SRT calls | 864,278 | +10,560 |
| `stinstr_fn_abs` | 50 REAL assignments `SiQ[i] := ABS(SiR[i]);` | 858,878 | +5,160 |
| `stinstr_fn_sqrt` | 50 REAL assignments `SiQ[i] := SQRT(SiR[i]);` | 856,678 | +2,960 |
| `stinstr_fn_ln` | 50 REAL assignments `SiQ[i] := LN(SiR[i]);` | 856,678 | +2,960 |
| `stinstr_fn_log` | 50 REAL assignments `SiQ[i] := LOG(SiR[i]);` | 859,678 | +5,960 |
| `stinstr_fn_sin` | 50 REAL assignments `SiQ[i] := SIN(SiR[i]);` | 859,678 | +5,960 |
| `stinstr_fn_cos` | 50 REAL assignments `SiQ[i] := COS(SiR[i]);` | 859,678 | +5,960 |
| `stinstr_fn_tan` | 50 REAL assignments `SiQ[i] := TAN(SiR[i]);` | 859,678 | +5,960 |
| `stinstr_fn_asin` | 50 REAL assignments `SiQ[i] := ASIN(SiR[i]);` | 856,678 | +2,960 |
| `stinstr_fn_acos` | 50 REAL assignments `SiQ[i] := ACOS(SiR[i]);` | 856,678 | +2,960 |
| `stinstr_fn_atan` | 50 REAL assignments `SiQ[i] := ATAN(SiR[i]);` | 856,678 | +2,960 |
| `stinstr_fn_deg` | 50 REAL assignments `SiQ[i] := DEG(SiR[i]);` | 859,878 | +6,160 |
| `stinstr_fn_rad` | 50 REAL assignments `SiQ[i] := RAD(SiR[i]);` | 862,478 | +8,760 |
| `stinstr_fn_trunc` | 50 REAL assignments `SiQ[i] := TRUNC(SiR[i]);` | 856,678 | +2,960 |
| `stinstr_fn_atan2` | 50 assignments `REAL := ATAN2(REAL, REAL)` | 856,678 | +2,960 |
| `stinstr_fn_tod` | 50 assignments `DINT := TOD(DINT)` | 858,078 | +4,360 |
| `stinstr_fn_frd` | 50 assignments `DINT := FRD(DINT)` | 858,078 | +4,360 |
| `stinstr_fn_isinf` | 50 assignments `BOOL := IsINF(REAL)` | 855,078 | +1,360 |
| `stinstr_fn_isnan` | 50 assignments `BOOL := IsNAN(REAL)` | 855,078 | +1,360 |
| `stinstr_mo_mam` | 50 MAM calls on one axis, each on its own MOTION_INSTRUCTION | 894,622 | +40,904 |
| `stinstr_mo_maj` | 50 MAJ calls on one axis, each on its own MOTION_INSTRUCTION | 892,622 | +38,904 |
| `stinstr_mo_mah` | 50 MAH calls on one axis, each on its own MOTION_INSTRUCTION | 886,422 | +32,704 |
| `stinstr_mo_mas` | 50 MAS calls on one axis, each on its own MOTION_INSTRUCTION | 888,422 | +34,704 |
| `stinstr_mo_mso` | 50 MSO calls on one axis, each on its own MOTION_INSTRUCTION | 886,422 | +32,704 |
| `stinstr_mo_mrp` | 50 MRP calls on one axis, each on its own MOTION_INSTRUCTION | 889,822 | +36,104 |
| `stinstr_mo_msf` | 50 MSF calls on one axis, each on its own MOTION_INSTRUCTION | 886,422 | +32,704 |
| `stinstr_mo_maw` | 50 MAW calls on one axis, each on its own MOTION_INSTRUCTION | 889,822 | +36,104 |
| `stinstr_mo_mar` | 50 MAR calls on one axis, each on its own MOTION_INSTRUCTION | 893,222 | +39,504 |
| `stinstr_mo_mdr` | 50 MDR calls on one axis, each on its own MOTION_INSTRUCTION | 886,822 | +33,104 |

**CAPTURE ERRORS: 0 row(s)** (not yet captured).
