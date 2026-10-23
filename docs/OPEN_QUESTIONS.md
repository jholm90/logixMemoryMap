# Open Questions

**Seven, each waiting only on a capture or on the seventeen.** Opened 2026-10-23: OQ-UDTLAYOUT (the deep dive into the owner's capture of that day) and OQ-CGL1769 (the 1769 Compact GuardLogix programs, in scope by the owner's decision of that day). Closed 2026-10-23: OQ-SERIESREAL,
OQ-STSHAPE and OQ-SAFETYPARTITION (their laws wired and exact, their open items moved or
closed), and on real exposure a standard array tag's +4, a further 1734-AENTR/C adapter, a
safety structure's member read by standard logic and FBD logic (BOUNDED, under the floor) and a
scalar word operand in a safety routine (in no real program); SFC is out of scope permanently
(owner, CLAUDE.md). All in RESOLVED_QUESTIONS, "Closed 2026-10-23". **Batch B** (built
2026-10-22, TASKS 0zd) answers OQ-SAFETYLOGICIO, OQ-STRSHAPE's two readings and OQ-MODREPEAT's
packed cards; **batch C** (built 2026-10-23, TASKS 0zg) answers OQ-UDTMEMBERNAME, OQ-MODREPEAT's
zero-connection modules and OQ-STRSHAPE's nested shape; **OQ-REALUNDER** needs
`scripts/quick_eval.py` run on the seventeen, which are not in this checkout. The 92-file capture
of 2026-10-03 took the real set to **0.97%** mean, **2.57%** worst; the scalar AOI law of
2026-10-21 moves that set and it has not been re-scored.

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
| **OQ-REALUNDER** | **0.97% mean, 2.57% worst, 10/17 inside 1%, 15/17 inside 2%** after the 2026-10-03 batch; **not re-scored since the scalar AOI law (2026-10-21)**, an estimated −100 KB across the seventeen toward under-prediction (672 instances of 40–47-BOOL AOIs). The ten real safety-controller programs read **mean 1.34%, worst −2.45%** on the standard figure (not counted toward accuracy). Section 1. | `quick_eval.py` on the seventeen (owner's machine), then batch B and C's laws against them |
| **OQ-SAFETYLOGICIO** | RS-02 / RS-03 / RS-17 (one machine at three revisions) read 6,960 / 16,408 / 14,436 low on the safety figure (−5.6% / −8.3% / −7.3%); the eight others −1.0% to −1.8%. The module-operand lead is refuted (about 1.4 bytes an operand). Left: a safety AOI call's operands beyond two, program parameters by usage, descriptions on safety tags, DCS chained on a rung, an uncalled routine's content, the AxisSTO instance layout, and a generic per-rung term. Section 5. | batch B (26 files, four Studio variants of RS-17) |
| **OQ-STRSHAPE** | Every STRING shape exact against its control. Open: a UDT array element holding STRINGs reads 4 above the engine (a STRING member at 88, or a custom string at 48), worth up to 0.9 points on the three programs the standard figure reads lowest; EQU / NEQ (rebuilt). Section 4. | batch B (`strm_*`, `strx_*_r2`); batch C (`strn_*`, the nested shape) |
| **OQ-MODREPEAT** | Nine catalogs' repeat rates wired; a module-defined type is defined once a project. Open: packed 5069 cards on a controller's bus; zero-connection modules still on the flat 2,344 (RS-07 seven, 16,408 bytes). Section 3. | batch B (`safe_io6_5069_*`); batch C (`zcm_*`) |
| **OQ-UDTMEMBERNAME** | The wired member-name pool does not fit its own four-DINT sweep or the safety rounds' short-named UDTs; a candidate fits those and misses the BOOL arm by 8. Section 2. | batch C (`udtpool_*`, 16) |
| **OQ-CGL1769** | The 1769 Compact GuardLogix programs RS-11 to RS-16. Standard −5% to −12% until a 1769 safety catalog took its standard twin's blank baseline (provisional, 2026-10-23): now +1.4% / +2.6% / +1.4% / −2.4% / +3.2% / −0.25%. Safety +28% to +42%, every one high, unexplained. Section 7. | the `cgl_*` batch (TASKS 0zi, 36 files at v32 and v35, built) |
| **OQ-UDTLAYOUT** | Reopened from OQ-ALIGN 2026-10-23. A UDT is priced as the plain sum of its members; the one realistic mixed UDT captured reads 240 an element against 216, and `strx_*` 4 an element high, both exactly an aligned layout. A layout that keeps every packed capture exact (210 of 210) takes the nineteen to 1.130% / −2.66%. Section 6. | batch D (TASKS 0zh, specified); batch B `strm_*`, batch C `strn_*` |

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

## 2. OQ-UDTMEMBERNAME — the UDT member-name pool, reopened 2026-10-19

| | |
|---|---|
| **The bar** | Real programs carry about 174 UDT definitions with member names of about 12 characters. The wired pool charges `8 × ceil(Σ(len + 1) / 8)` a definition; the candidate below charges about 3 a member less, on the order of 5 KB (0.1 to 0.5%) a real program, **in the direction that deepens the real under-prediction**. So a change here is judged on the seventeen real programs, which are not in this session's checkout, and is not wired from generated rows alone. |
| **Why reopened** | Re-priced live (the generators' own files rebuilt in memory, no files written), the sweeps the law was derived from do not all fit it: four BOOL members, lengths 2 to 32, a flat −8 (the form fits, the level is 8 high); four DINT members, lengths 2 / 7 / 16 / 32: −16 / −8 / −16 / −16 (not flat); nested UDT, lengths 2 and 32: −32 / −32; BOOL count 1 / 2 / 4 / 8 / 16 at length 7: +8 / 0 / −8 / −24 / −48. The AOI-name controls read 0. Safety rounds 2 and 4: `SafeUdtS` (D, R, B1, B2) and `SafeUdtL` (D0..D9) read 16 and 32 below the engine on a 1756-L81ES and on its 1756-L81E twin alike, so their pool is 0. |
| **Candidate** | `8 × ceil(Σ max(0, len − 2) / 8)`, names of up to two characters free: exact on the DINT arm and both safety UDTs, 8 off on the BOOL length arm. The BOOL member-count arm moves with the BOOL count, not the names, so a BOOL-run term is mixed in it. |
| **Test — batch C, BUILT 2026-10-23** | `gen_udt_name_pool.py`, 16 files on the plant, each one UDT definition (`PoolUdtA`, used by no tag) whose member names are all one length: `udtpool_dint_n4_len{01,02,03,04,08,12}`, `udtpool_dint_n8_len{01,02,04,12}`, `udtpool_bool_n4_len{01,02,03,04,08,12}`, each against `realism_base_f25` (TASKS 0zg). Each manifest row records the wired and candidate pools: the reading is the engine's less the plant's 1,794 under the wired form, less again 8 to 24 under the candidate. Whichever form fits all three arms then goes against the seventeen before it is wired. |

---

---

## 3. OQ-MODREPEAT — what a further module costs, any catalog, any count; opened 2026-10-20

| | |
|---|---|
| **The bar** | RS-06 and RS-09 (one program on two controllers) over-predicted by +2.32% / +2.52%. RS-09 carries two more 1732E-IB16M12R/A than RS-06 and reads 3,016 above it where the engine predicted 4,364: about 700 a copy where 1,432 was charged. Five Ethernet catalogs measured once each paid full price for every copy. The owner's direction (2026-10-20): the law has to handle any I/O module used by anyone, any number of times, not the catalogs measured. |
| **Law, wired 2026-10-20** (MEMORY_MODEL, "A module-defined type is defined once per project") | A module's connection tags carry Rockwell's own data types; a project defines each once. A module whose vendor-prefixed types an earlier module already defined pays its overhead less their UDT-law definitions. It reproduces the nine measured repeat discounts within −72..+104 and one at +240 (440C-CR30), across catalogs as well as copies. An unseen catalog is a base (1,064 for one connection or none, 2,579 for two or more) plus its new types. Not applied to EDS-profile types, CIP Safety devices, rack-aliased cards, adapters and bridges, or a copy whose own repeat rate is measured. |
| **Found 2026-10-20 on 34 existing captures** | The `rack_5069_*` family (one to twelve 5069 cards behind a 5069-AENTR, ten racks with 64 cards in one file, all zero errors) had never been re-priced under the law. With every type shared, the ten-rack file read 29,422 under (−16.6%). The cards' channel types have **no vendor prefix** (`CHANNEL_DI:I:0`): they are defined by every module that carries one, a copy an earlier module defined costing 76 more; the prefixed types are shared. A joint fit (adapter, the 76, each catalog's first copy) leaves rms 17, max 41 bytes on all 34. The adapter, charged the flat 2,344 zero-connection rate, costs 625; the 5069-SERIAL/A 367. The nine 5069 catalogs without an entry were priced blind by the unseen law first: eight within −247..+329 of their own single-card capture, six within ±85; then wired from those captures. |
| **Census** | 251 clean module captures, engine before and after the law: total \|error\| 214,854 → 131,710, inside ±8 117 → 128. The ten-rack file read +12,402 (+7.0%) before the law, −29,422 with every type shared, +570 (+0.32%) now, and every other 5069 rack is within ±0.35%; nothing outside them moved under the channel-type rule; the 497 batch-A files on disk unmoved by it. Real safety-controller programs (prediction minus reading): RS-06 +2.32% → +1.78%, RS-09 +2.52% → +1.80%, RS-03 / RS-17 +0.41% → +0.23%, RS-07 −0.12% → +0.04%; RS-02 −0.72% → −1.19% (four PowerFlex 525 sharing two types, and the D012 first-copy correction +4,008), RS-05 / RS-08 / RS-10 −0.1 to −0.3 point (their packed 5069-IB16 / OB16 sharing `AB:5000_DI16_Packed:I:0` and the rest, and their ETHERNET-MODULEs the configuration type). |
| **Open, 2026-10-20** (superseded below) | (1) Packed 5069 cards on a 5069 controller's own bus share their types under the law as fitted on standard-data cards in racks; the real ones (RS-05 / RS-08 two IB16 and two OB16, RS-10 three of each) are measured by `safe_io6_5069_*`. A catalog's entry is one number whatever its data format: 5069-IB16/A's (measured packed) priced its standard-data rack card within 3 bytes; 5069-OB16/B's (measured standard) prices the packed real cards, which `safe_io6_5069_ob16_1` reads. (2) The 1756-CNB/D, 1756-HYD02 and similar zero-connection modules cost less than the flat 2,344 (`rack_1756_n12` to `_n16` +2,384 to +3,458), not separated. (3) The D012 bare-drive `asmclose_2198_d012_*` rows read +4,008 now, as the with-axis shape requires; a drive with no axis exists in no real program. |
| **Test** | `modrep_*`, 36 files on the L81E plant against `realism_base_f25` (TASKS 0zb): round 1, the five catalogs at 1 / 2 / 4; round 2, one class of module each, every one a blind prediction — 1756-IF8/A and 1756-OF8/B (chassis analog), 843E encoders (two prefixed and two prefix-less types on an Ethernet device), PowerFlex 755-EENET at 1 / 2 / 4; 1 / 2 / 4 1734-IE2C/C on their own connections in a sixth POINT rack; 5069-OB16/B one rack × one card, one × four, four × one (a per-card cost inside a rack against a per-copy cost); generic ETHERNET-MODULE one, a second sharing its input type, a second sharing only the configuration type. Plus `safe_io6_5069_*`, 4 files (packed 5069-IB16 / OB16 on the 5069-L330ERMS2 safety base). Captured 2026-10-21 (batch A): all 36 `modrep_*` and the two `safe_io6_5069_ib16_*`, zero errors. |
| **Captured and wired, 2026-10-21** | All 36 `modrep_*` and the two `safe_io6_5069_ib16_*` clean. **Every first copy was already exact; each further copy costs the same at 2 and at 4**, so the nine catalogs carry their measured `repeat_bytes` and every `modrep_*` file now reads exact against its first copy. The law's own repeat, the error for an unmeasured catalog: 1732E +56 / +40, EX260 −72, 843E −40, PowerFlex 525 −224, 1734-IE2C +221, PowerFlex 755 +632 a copy. **The 843E's prefix-less types are shared** (paid again they charged 2,647 a copy against 1,535): a type is the module's own only on a 5069 card. **Per-channel configuration is per copy** (the owner: "specialty cards with lots of configuration per channel that can't be reduced"): the 1756-IF8 / OF8 read 432 / 744 a copy above the law, 2.28 / 2.16 times their nested per-channel configuration (189.5 / 345 bytes packed), the five cards without any −221..+72; wired as 2.2 × those bytes for a further copy of a catalog without its own rate (IF8 −14, OF8 +15 from the law alone). The declared data omits nested structure members (the IF8's 239 bytes of per-channel configuration, the OF8's 628); recorded, not altered. |
| **Still open, 2026-10-23** | (1) **Packed 5069 cards on a controller's own bus**: a second packed 5069-IB16/A reads 568 below the engine (`safe_io6_5069_ib16_2`); the OB16/B never converted, rebuilt in batch B (`safe_io6_5069_ob16_1`, `_mix_2_2`). RS-05 / RS-08 / RS-10 carry two or three of each. (2) **Zero-connection modules on the flat rate, re-scoped on real exposure.** The 1756-CNB/D / HYD02 case is in no real program on disk. What is: inhibited generic ETHERNET-MODULE placeholders with no connection (an HMI or NAT address kept in the tree: RS-05 two, RS-07 four, RS-10 one), a 1756-L75 and a 1756-L84ES peer controller and a 1783-NATR (RS-07) — seven modules and 16,408 bytes at the flat 2,344 in RS-07 alone, while every zero-connection catalog measured costs 320 to 625 (ETHERNET-BRIDGE 320, 1756-L8SP 528, 5069-L306ERS2 560, 5069-AENTR 625). **Test: batch C `zcm_*`, BUILT 2026-10-23** (`gen_zero_conn_modules.py`, 7 files: the placeholder at 1 / 2 / 4, the 1783-NATR at 1 / 2, the 1756-L75 at 1 / 2, each against `realism_base_f25`; TASKS 0zg). |
| **Closed 2026-10-23** | A further 1734-AENTR/C adapter reading 470 to 830 below its price: BOUNDED, under the floor (RESOLVED_QUESTIONS, OQ-AENTRREPEAT). |
| **Capture errors** | **CAPTURE ERRORS: 2 row(s)** — `safe_io6_5069_ob16_1` and `safe_io6_5069_mix_2_2` never converted (XMLSrv_E_IMPORT_ABORTED_NO_CHANGES): the 5069-OB16/B module-sweep block carries no ExtendedProperties ConfigID (711 packed on a controller's bus in every real export carrying one, 110 in standard data on an adapter), and Studio refuses the catalog without it; the IB16/A sweep block imported without one. `gen_safety_round6.std_card` adds it, lint refuses a 5069-OB16 without it (`module_without_configid`), both rebuilt in batch B. Still open (1) above rests on these two. |

---

---

## 4. OQ-STRSHAPE — STRING operands the way real programs write them, opened 2026-10-20

| | |
|---|---|
| **The bar** | The string instructions' weights were confirmed on the realism floor on STRING array elements (`blkstr_*`: CONCAT, DTOS, COP, SIZE) and MOV of a STRING costs a DINT MOV (OQ-STRINGMOV). The ten counted real safety-controller programs write them otherwise: 2,424 STRING operands of EQU and 2,151 of MOV are members behind an index; 777 INSERT (weighed once, near-empty), 713 CONCAT (264 operands custom-typed), 191 MID. The seventeen standard programs carry 1,850 CONCAT, and OQ-REALUNDER's one string-heavy lead (CONCAT count tracking the residual at ten times CONCAT's own weight) was never explained. |
| **Mechanism** | Unknown: the operand-shape surcharges (OQ-INDIRECTUDT: +40 a member after a tag index, +108 on a STRING array) were measured on numeric instructions; whether a STRING operand's member path or custom type adds its own cost is not. |
| **Test** | `strx_*`, 21 files (`gen_string_shapes.py`, TASKS 0zb): one inventory in every file (STRING arrays, a UDT with STRING, a 40-character custom string, DINT and REAL members, an index tag), 400 calls each, every destination distinct: EQU on elements / members / behind an index, NEQ, MOV member and behind an index, COP member, CONCAT member and custom-typed, INSERT, MID (and behind an index), DELETE, FIND, DTOS, STOD, RTOS, STOR, UPPER; each against `strx_n00`. Captured 2026-10-21 (batch A), 21 readings. LOWER left out: lint does not know it and no real program uses it. |
| **Captured, 2026-10-21** | 17 clean files. **Every STRING shape exact against `strx_n00`**: MOV and COP of members and behind tag indexes, CONCAT of members and of a custom string type, INSERT, MID (and behind an index), DELETE, FIND, DTOS, STOD, RTOS, STOR, UPPER — the string instructions' weights hold on the shapes real programs write. **The control itself reads 4,808 below the engine: 4 an element of the UDT array holding a STRING, a 40-character custom string, DINT and REAL members (engine 224 an element, real 228).** Which member carries it — the STRING padded to 88, or the custom string to 48 — is not separable from these files; it contradicts the "no alignment padding" of OQ-STRINGUDTMEMBER for one of them. Real exposure: 0 to 500 such elements a real safety program (RS-05 0, RS-10 20, RS-08 250), a few KB at most. |
| **Exposure recounted, 2026-10-22** | The "a few KB at most" above counted only array elements that hold a STRING directly. Counted as STRING members nested anywhere in a UDT tag, with every array multiplicity, the three programs the standard figure reads 2.0–2.45% low carry **3,880 / 2,744 / 12,677** (RS-05 / RS-08 / RS-10; RS-08 also 2,361 custom strings), the others 327 to 1,623. A STRING array's element is already 88 (`string_array.builtin_per_element`, KNOWN); a STRING inside a UDT is priced 86. At 88 there the standard figure on the eight programs moves 1.44% → about 1.21% (RS-10 −2.01 → −1.15%, RS-05 −2.38 → −1.78%, RS-04u −0.61 → −0.14%; RS-07 and RS-06 move away by 0.2 and 0.4 points); the custom-string reading (44 → 48) moves it to 1.42%. Not wired: `strx_n00` cannot tell them apart. **Test:** `strm_s2_400`, `_c2_400`, `_sc_400`, `_sd_400` (`gen_string_members.py`, built 2026-10-22, batch B): two STRINGs read +1,600 and the others nothing if a STRING member is 88; two custom strings +3,200 and the STRING + custom string +1,600 if the custom string is 48; STRING + DINT nothing either way. |
| **Nested twins — batch C, BUILT 2026-10-23** | The real programs hold most of those STRINGs one level down: a scalar tag of a UDT whose member is an array of the STRING-holding UDT, the shape 35 to 49% of RS-05 / RS-08 / RS-10's predicted bytes sit in. `strn_s2_400`, `_c2_400`, `_sc_400`, `_sd_400` (`gen_string_members.py`) carry each `strm_*` file's 400 elements as that member of one scalar tag. Each differs from its twin by one outer UDT definition (200, the same under both member-name pool forms) and the tag's form; engine twin + 200. A pair reading twin + 200 says the twin's finding holds in the nested shape; anything else is a term of the nested shape itself (TASKS 0zg). |
| **Capture errors** | **CAPTURE ERRORS: 4 row(s)** — `strx_equ_elem`, `strx_equ_member`, `strx_equ_vidx`, `strx_neq_member`, 400 errors each, "OTE, Operand 0: Invalid bit specifier": the generator wrote each comparison's result to `SuC[i].R.0`, a bit of a REAL member. All four read 16 below `strx_n00`, so none of their 400 rungs reached the controller; the rows measure nothing about EQU / NEQ. Lint now refuses a bit subscript on a REAL (`bit_specifier_on_real`); `gen_string_shapes` writes a BOOL destination and the four are rebuilt in batch B. |


---

---

## 5. OQ-SAFETYLOGICIO — what RS-02 / RS-03 / RS-17 carry in the safety partition that nothing has measured, opened 2026-10-21

| | |
|---|---|
| **The bar** | After batch A the safety figure reads −1.0% to −1.8% on the eight other real safety programs and **−5.6% / −8.3% / −7.3% on RS-02 / RS-03 / RS-17** (one machine's program at three revisions): 6,960 / 16,408 / 14,436 bytes. The owner's tolerance on the safety figure is a few percent. The standard figure is not involved. |
| **Opened on a lead that the other programs refute (2026-10-22)** | The question was opened on module-tag operands in safety logic (slot-path card points at ~24 an operand, drive members at ~34). A census of every real safety program's safety content (all routines, operands by spelling, tags, devices, AOIs, parameters, documentation) bounds them: RS-01 has 129 adapter slot-path operands (`Adapter:1:I.Pt04Data`), RS-06 42 drive `SI` / `SO` members and 43 slot-path operands, RS-08 68 `Local:1:I` points, RS-04u 60, and each reads 300 to 1,036 low in all. Fitted with the rung count, a module operand in an ordinary safety instruction costs **about 1.4 bytes**, and at most 5 to 8 even if each program's whole gap were its operands. On RS-17's 316 that is ~0.4 KB, not the 7.5 KB the lead claimed. |
| **Ruled out with existing data** | Device blocks: RS-02 and RS-17's drives, cards and local pair carry exactly the connections, sizes and revisions of the measured templates, and devices are additive at 1 / 2 / 4 drives, 1 to 8 IB8S and a second rack; standard-only drives leave the safety reading at 1,410 (`safe_iol_kinstd_*`). Rung comments (RS-01 15,129 characters), safety-tag member comments (RS-10 3,240, RS-07 1,749, RS-05 1,565), cards without a module name (RS-10 2, RS-08 4), SIL3 (RS-01, RS-07), the lock and signature (RS-03 reads RS-17's 197,262 with every safety element identical but the AOI exported encoded): each sits in a program 0.3 to 1 KB low. The AxisSTO call routine is identical in RS-02 and RS-17 (29 calls, nine operands each, 14 rungs of two calls), so whatever it costs it cannot explain RS-17's increase over RS-02. |
| **What is left to explain** | **Generic, all eleven:** the eight others fit 152 + 4.08 a safety rung (leave-one-out rms 89 bytes) or 54 + 42 a device + 0.58 a bit instruction (81); not identified, inside a few percent, and no single test targets it. **Specific to the three:** RS-02 and RS-03 export AxisSTO encoded, priced at a minimum (its locals and logic, 1,972 = RS-03 − RS-17 at identical readings). Less that and the generic term: **RS-02 ~4.5 KB, RS-17 ~13.2 KB**. |
| **Candidates — none measured, ranked by fit** | 1. **Operands of a safety AOI call beyond two.** Every measured safety call passed two (`SafeAoiA(Inst, AiIn[i], AiOut[i])`, +44 a call over the standard call law); AxisSTO passes eight on a 16-parameter AOI. Read per operand or per parameter, the +44 is 22 / 11 each, and the 29 calls are short **3.8 KB in both revisions**, most of RS-02's ~4.5 KB. 2. **Program parameters in the safety program**: RS-02 38 `Usage="Public"` BOOLs; RS-17 59 Public (BOOL, TIMER, DCI_STOP) and the 29 AxisSTO instances as `Usage="Output"`. Public is free in standard memory (OQ-PUBLICTAG); Input / Output have never been measured in either partition, and no other real safety program has one. Carrying RS-17's further ~8.7 KB alone, an Output AOI parameter would cost ~300, about twice its data block. 3. **Descriptions on safety tags**: RS-02 31 (1,019 characters), RS-17 94 (3,261), every other program 0 to 3. 4.3 to 4.4 a character fits both revisions by itself, but descriptions and comments are free in standard memory (`tagcomment_*`, `udt*comment_*`), member comments are free in safety (above), and RS-04u's 83 characters would put it 440 over. 4. **DCS chained 2 to 10 on a rung with nothing else** (RS-02's 24; every measured DCS stood alone on its rung): RS-06's one chain of three bounds it near 40 an instruction, ≤ 0.9 KB. 5. **Content in an uncalled safety routine**: measured only as one NOP (`safe_rtn_idle_*`); RS-02's ten subroutines are never called. Priced as if called; if they are not compiled the engine over-charges RS-02. 6. **The AxisSTO instance layout**: priced unpacked (116 an element, block 136); packed (60, block 88) would mean 1.4 KB over-charged on RS-17, the true remainder larger. |
| **From OQ-SAFETYPARTITION (closed 2026-10-23)** | The eight other programs' generic 300 to 1,036 bytes low on the safety figure (152 + 4.08 a safety rung, leave-one-out rms 89) is this question's too: batch B's `safe_mix_*` family tests a per-rung residual on the realism plant. A scalar word operand in a safety routine, the one other candidate left there, is in no real program. |
| **Test (batch B, TASKS 0zd, BUILT 2026-10-22: 26 files, blind predictions recorded)** | Studio-made variants of RS-17 measure the AxisSTO calls and the instances with their definition in place. Isolation files measure each candidate alone, each against a control in its own family: a safety AOI call's operand count and kind, program parameters by usage, descriptions on safety tags, DCS chained on a rung, content in an uncalled routine, an AxisSTO-like AOI's instances; one module-operand pair confirms the bound above; a mixed-rung family tests the generic per-rung residual. |

---

## 6. OQ-UDTLAYOUT — a UDT's members are aligned, reopened from OQ-ALIGN 2026-10-23

| | |
|---|---|
| **The bar** | On the nineteen real standard programs the engine reads 1.29% low sum-weighted, and tag data is ~60% of their bytes. A UDT is priced as the plain sum of its members (OQ-ALIGN, "no alignment padding"). Under the layout below the nineteen move +1.3 KB to +41.6 KB each, **1.262% → 1.130% mean, −2.83% → −2.66% worst**; under full natural alignment 0.970% / −2.32%. In the real UDT definitions the members that land off their boundary are a nested UDT (310 sites), DINT (188), STRING (105), REAL (80), TIMER (47), DINT[] (41), STRING[] (29), MOTION_INSTRUCTION (14), BOOL[] (12), COUNTER (9), INT (8), LINT (6). |
| **Evidence** | `mixedudt_messy_*` (the one realistic mixed UDT captured: STRING, scattered BOOLs, a nested-UDT array, a custom string, DINT[8], LINT, SINT, REAL): **240.3 an array element read, 216 priced**; laid out aligned it is 240, and the three files then sit on a flat −64 / −64 / −56, which is already the definition-only file's −64 (the member-name pool, OQ-UDTMEMBERNAME). `strx_*` (17 files, batch A): every one read 4,808 above the engine, 4 an element of a UDT holding two STRINGs, a custom string, a DINT and a REAL; aligned, all 17 land on the realism plant's own −1,794 (−1,786). **Against it:** `opshape_*` (26 files), a UDT of BOOL, DINT and a nested {BOOL, DINT} in a 4-element array, reads exactly packed (12 an element); full natural alignment puts it 16 over. |
| **The layout that fits every capture** ("hostlast") | Non-BOOL members in declaration order, each at a multiple of its alignment (SINT 1, INT 2, DINT / REAL 4, LINT 8; a STRING, custom string, predefined structure or nested UDT its own largest member); **the hidden SINTs that back BOOL members after them**; a nested UDT not tail-padded; a UDT array element (at top level or as a member) rounded to its alignment, 4 at least. Re-priced on 301 rebuilt captures of every UDT family (udtslot, udtmn, defscale, dscale2, stringarray, stringoverhead, udtstring, arraypack, udtarrayalign, pool, opshape, progscope, blkstr, stringcop, ...): **210 exact before, 210 after**, nothing moved; the messy and `strx` files become exact. Full natural alignment: 210 → 184 (the 26 `opshape`). Fitted on three discriminating captures, so the layout is a hypothesis, not a measurement (CLAUDE.md failure mode 2). |
| **Why OQ-ALIGN read "no padding"** | Its sweeps were BOOL / DINT shapes on scalar tags and homogeneous arrays, where the scalar tag's 8-byte slot and an array element's 4-byte rounding absorb the padding. |
| **Test** | **Batch D (TASKS 0zh), SPECIFIED, NOT BUILT:** one array of 200 of one UDT per file on the realism plant, each shape chosen so packed, hostlast and natural predict different element sizes. Batch B's `strm_*` and batch C's `strn_*` also read this: hostlast predicts what the STRING-at-88 reading does (`strm_s2_400` +1,600, the other three 0). Not wired until a capture decides; wiring needs the full residual census (CLAUDE.md, "Cost of measurement"). |

## 7. OQ-CGL1769 — the 1769 Compact GuardLogix programs, opened 2026-10-23

**In scope by the owner's decision of 2026-10-23**, the one exception to 1769 being dead
architecture (CLAUDE.md): RS-11 to RS-16, six customer programs on 1769-L30ERMS and L33ERMS at
v30 and v32, to within about 5% in each partition.

**Standard partition.** On the engine of that morning the six read −8.98 / −9.93 / −8.98 /
−11.55 / −5.08 / −7.57%. A 1769 safety catalog had no `catalog_baseline_delta`, which is keyed
by the exact ProcessorType, so its empty project was priced at the L8x's 18 to 24 KB; a 1769
blank reads 58 to 83 KB. The 1769-L30ERM / L33ERM blank's +64,736 is now applied to its safety
variant (ASSUMED, `memory_model.yaml`): a 1756-L81ES and a 5069 safety catalog carry their
standard twin's empty project, the safety task shell apart. The six read **+1.42 / +2.56 / +1.40
/ −2.40 / +3.16 / −0.25%**. The v30 programs read high and the v32 ones low, which is the shape
of a baseline that moves with firmware: the L16ER blank rises 58,720 → 63,456 → 69,632 from v31
to v32 to v35, so a v30 or v32 1769 blank is below the v35 value applied. The base files read it.

Not settled, and the batch reads both: whether a module's I/O lands in the figure read (a 1769
Capacity tab, like the L7x's, reports I/O memory apart from data and logic; the engine prices
35 to 42 KB of `module_io` in each of the six), and whether content costs on a 1769 what it
costs on an L81E (the per-station rate, against the plant's exact L81E rate).

**Safety partition.** +28.6% (RS-11 / RS-12 / RS-13, one safety program, 22,709 against
17,656), +28.5% (RS-14), +42.3% (RS-15); RS-16 has no safety reading. Every term is priced at
its 1756-L81ES v35 / 5069 value: the base 1,394, routine shells, rung logic, and 8,599 of safety
I/O in RS-11 (two 1734-IB8S/B, one 1734-OB8S/A). RS-15 reads 10,200 high and carries three
Kinetix 5500 safety drives priced 10,731. Either the 1769 prices safety I/O well below the L8x,
or the base, the routine shells or the rungs differ; the readings on file cannot tell which.

**The `cgl_*` batch** (TASKS 0zi): every safety and standard term the six carry, on each
catalog at v32, each a step on its arm's base. **v32 is the floor: the conversion tooling cannot
build a v30 project** (owner, 2026-10-23), so the four v30 programs (RS-11 to RS-13, RS-15) are
reached from v32 and the firmware step on the safety catalog itself, which `cgl_l30v35_base` and
`cgl_l33v35_base` read (engine 413,130 and 709,578; the
engine's ladder puts v35 11,240 below v32, the L16ER blank reads 6,176 above). Predicted before
any reading, engine of 2026-10-23 (the reading is the engine's less the plant's 1,794 where the
engine is right):

| step | `l30v32` standard / safety | `l33v32` standard / safety |
|---|---:|---:|
| `base` | 424,370 / 1,410 | 720,818 / 1,410 |
| `plant2x` | +296,448 / +0 | +592,896 / +0 |
| `dint400` | +38,400 / +0 | +38,400 / +0 |
| `udtdef20` | +9,760 / +0 | +9,760 / +0 |
| `logic400` | +21,140 / +0 | +21,140 / +0 |
| `progs10` | +18,040 / +0 | +18,040 / +0 |
| `mods` | +15,441 / +0 | +15,441 / +0 |
| `safecontent` | +3,200 / +6,544 | +3,200 / +6,544 |
| `safertn8` | +0 / +2,800 | +0 / +2,800 |
| `saferung60` | +0 / +3,576 | +0 / +3,576 |
| `safeinstr` | +0 / +5,008 | +0 / +5,008 |
| `sio_ib8s` | +4,063 / +7,026 | +4,063 / +7,026 |
| `sio_ib8s1c` | +3,363 / +3,258 | +3,363 / +3,258 |
| `sio_ob8s` | +3,288 / +3,457 | +3,288 / +3,457 |
| `sio_mix` | +6,044 / +8,599 | +6,044 / +8,599 |

Twins on the 1756-L81ES v35 standard plant, against safe_n00: `safe_cgl_rung60` (842,474 /
4,986) and `safe_cgl_rtn8` (842,474 / 4,210). The Kinetix 5500 safety drive with its axis on
`l33v32`: `safe_iol_cgl32_h008s_1` / `_2` (748,694 / 4,987 and
773,802 / 8,564).

**What decides it.** The base files give the 1769 baseline on each catalog at v32 and v35;
`plant2x` gives the content rate (the L30ERMS `plant2x` and the L33ERMS `base` carry the same
content, so the catalogs difference directly); `mods` gives whether module I/O is in the figure;
the `safe*` steps price the safety base, routine shells, rungs and DCS / CROUT on a 1769; the
`sio_*` steps price each 1734 safety card type and their sum; the drive files price RS-15's
Kinetix. Whatever each reads is wired, and the six re-priced against it; a v30 baseline is
taken from the v32 reading and the 1769 firmware ladder, and says so.
