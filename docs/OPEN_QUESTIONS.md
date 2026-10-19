# Open Questions

**Five.** OQ-UDTMEMBERNAME reopened 2026-10-19 (the UDT member-name pool does not fit its own sweeps live). OQ-SAFETYPARTITION opened 2026-10-17 (the safety memory partition, a separate quantity from the standard figure). The 92-file capture of 2026-10-03 closed eight at once — MOTIONLIT, BLOCKSTR, AOILITARG, AOIINTERNAL, PUBLICTAG, SMALLINSTR, STREAL and AOICOMPLEX — and wired five laws that took the real set from 1.27% to **0.97%** mean, 3.08% to **2.57%** worst (RESOLVED_QUESTIONS, top). OQ-AOIBOOLINST opened from that batch. Closed questions and their reasoning trails are in
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
| **OQ-REALUNDER** | **0.97% mean, 2.57% worst, 10/17 inside 1%, 15/17 inside 2%** after the 2026-10-03 batch (InOut operands in AOI logic, AOI REAL arguments, AOI scan-mode routines, nested AOI calls, the motion literal law). Mean under 1% for the first time; the stopping rule still fails on the max (export 27 2.57%, export 16 2.23%). Every real program but one still under-predicts (sum-weighted +0.95%). Checkpoint of the 0.58% state: tag `checkpoint-2026-09-25-pre-series-law` (commit `172f581`). |
| **OQ-AOIBOOLINST** | `aoiint_n00` over-predicts by 12,198 before any logic: its AOI carries 55 BOOL members and 50 instances (engine 320 per instance). 672 real instances carry 40–47 BOOL members. Spec in TASKS 0p; not built. |
| **OQ-SERIESREAL** | **WIRED (option A).** −12 per extra writing instruction in a rung (OTE/OTL/OTU, word-destination writers, TON), exact in all 38 isolating files. Kept open only as the record of why the headline rose; closes once OQ-REALUNDER finds what it was cancelling. |
| **OQ-SAFETYPARTITION** | Opened 2026-10-17. **302 files captured in four rounds, zero errors; the laws are wired** (MEMORY_MODEL, "Safety memory is a separate partition"): safety exact on all 299 safety files, on 1756-L81ES v32/v34/v35 and 5069-L330ERMS2/L320ERMS2 v35; tag mapping measured at zero. Open: safety I/O (in every real safety program), the signature and the lock (a Studio-made variant), `safe_aoi_call_60` (converted, not captured); 17 real safety programs predicted blind (below). Moves **no** standard-processor figure: safety processors are excluded from accuracy. |
| **OQ-UDTMEMBERNAME** | **Reopened 2026-10-19.** Re-priced live, the member-name pool does not fit its own four-DINT length sweep (−16 / −8 / −16 / −16) or the safety rounds' short-named UDTs (pool 0 where 16 and 32 are charged, on a 1756-L81E twin too). A candidate fits those and misses the BOOL arm by 8. Section 5. |

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

### A standard array tag on the plant reads +4 (2026-10-19)

Found by the safety rounds and confirmed on a plain 1756-L81E: every standard array tag
added to the realism plant reads 4 above the engine (`safetwin_sref_ctl`, six `BOOL[64]` /
`DINT[64]` arrays, +24; `safe_sref2_ctl`, one, +4; `safe_ref_*`, `safe_sref_*`,
`safe_comp_2` the same per array). Scalars added beside them read exact, and the
bare-baseline array sweeps (`array_dint_*`, `boolarray_n*`) were exact, but the plant
carries no array tag of its own, so whether this is a plant-context term, a short-name
term (these names are 4 to 6 characters) or a size term is not separable from the files
on disk. Real exposure: a few hundred array tags a program, about 0.05% at +4 each, in the
direction that reduces the real under-prediction. A discriminating set is specced in
TASKS 0y.

---

## 2. OQ-SERIESREAL — the series-output law with no duplicated bits

`OQ-SERIESOUTPUT` measured −12 per output after the first, exactly, on 16+ files —
every one near-empty and, bar the three `srout_oteuniq` files, writing the same bits in
every rung. Applying it to the real set makes every real file worse. 18 of the 25 worst
generated files are this one law.

| | |
|---|---|
| **Mechanism** | the discount belongs to the calibration shape (empty controller, repeated bits), not to series outputs as real ladder has them |
| **Expected movement** | none directly — the law is not wired. If it vanishes here, the engine is right to leave it out and the contradiction is closed; if it holds, real programs carry 0.5–1.5% of bytes the model over-charges, and the true residual is that much larger |
| **Batch built** | 1,600 distinct output BOOLs, each written once, a distinct condition per rung, identical tags in all 8: `realism_srout_series_k{01,02,04,08}` (1600/k rungs of XIC then k OTEs), `_branch_k{02,08}` (parallel legs), `_inter_k{02,08}` (k XIC-OTE pairs per rung — the instruction list of k01 exactly, only rung packing moves) |
| **Captured** | **The law holds, exactly.** Against `_series_k01`, per extra output: −12 at k = 2, 4, 8 in series; `_branch_k{02,08}` identical to series; `_inter_k{02,08}` (a condition before every output) identical too. The L9/v38 density rungs (`XIC … MOV … OTE`) show it again, −12 per rung on 1,600 rungs. So it is not the empty controller, not repeated bits, and not a single condition. |
| **Real shapes** | Of real extra outputs (rungs with 2+ writing instructions): 27% plain series, 12% output-only branch legs, **61% branch legs each carrying their own conditions** — the one shape never built |
| **Batch built** (styles) | `gen_series_styles.py`, `samples/generated/srstyle/`, 14 files, one tag inventory, each output written once, realism floor: `srsty_k01` control; `_legs_k{02,04,08}` (legs with own conditions); `_prelegs_k{02,04}` (shared + own conditions); `_legs2_k04` (two conditions per leg); `_nested_k04`; `_mid_k03` (output mid-rung then legs); `_otl_k04` (series latches); `_mixlegs_k04` (OTE/OTL/MOV/OTE legs); `_ton_k01` / `_ton_k04` / `_tonlegs_k04` (timers, which the counter does not count as writers). Each residual against its control is the discount for that shape |
| **Captured (styles)** | All 14 `srsty_*` files, zero errors. Against `srsty_k01` / `srsty_ton_k01`, every shape reads exactly −12 per extra writer: `_legs_k{02,04,08}`, `_prelegs_k{02,04}`, `_legs2_k04`, `_nested_k04`, `_mid_k03`, `_otl_k04`, `_mixlegs_k04`, `_ton_k04`, `_tonlegs_k04`. TON is a writer for this law although the counter did not count it. |
| **Trial** | Counter extended with TON, `apply: true`: all 38 series files (`realism_srout_*`, `srsty_*`) exact. Real set, seventeen counted: **0.58% → 2.18%**, all seventeen under-predicting, 1.19% to 4.31%. Reverted, pending decision. The law is right on every file that isolates it, so the real set's agreement without it is a compensating error (CLAUDE.md failure mode 3): something real programs carry is under-charged by about the size of the discount. Wiring it means the headline reads ~2% until that is found |
| **Still contradicted** | Applied to the real set it takes 0.77% → **2.48%**; applied only to branch-free rungs, 0.77% → 1.16%. Either real multi-output rungs are shaped differently from every measured form, or the per-instruction weights already absorb it for real rung mixes. The one real shape never built is **branch legs that each carry their own conditions**, `[XIC(a)OTE(x),XIC(b)OTE(y)]`. Unwired until that is measured |


---

## 3. OQ-AOIBOOLINST — AOI instances with many BOOL members

| | |
|---|---|
| **Evidence** | `aoiint_n00` (one AOI `AiOps`: 3 inputs, 1 output, 55 BOOL locals; 50 controller instances; one virtual axis, one UDT tag) reads 12,198 under the engine before any logic, while every logic file built on it is exact relative to it. The virtual axis is priced exactly elsewhere (16,880 per axis, `axmarg_virtual_*`); the instances are charged 320 each and the definition 2,168, so the 12,198 sits in the instance data or the BOOL-heavy definition (-244 per instance if it is all instances). Real exposure: 672 instances of AOIs with 40–47 BOOL parameters and locals, 11 with 64+. |
| **Expected movement** | If the instance figure is over-charged by ~240 for a 40+-BOOL AOI, ~160 KB across the seventeen in the over-prediction direction — on files that under-predict overall, so it would unmask under-charges elsewhere rather than improve the mean by itself. |
| **Spec** | TASKS 0p. Not built. |
| **CAPTURE** | Round 1: 119 files (the seven `safe_std_*` rebuilt as `_r2` after `SIn` failed as SIN), round 2: 74, round 3: 78; all 271 converted and captured 2026-10-17/18 with zero build errors and a safety reading on every row. Warnings only where intended: `safe_rtn_idle_1/5` ("routine cannot be reached"), `safe_lg_afi_20` ("AFI detected"). |

---

## 4. OQ-SAFETYPARTITION — sizing the safety memory partition

| | |
|---|---|
| **Evidence** | A safety controller keeps safety tags and safety logic in a partition that standard Capacity does not count (MEMORY_MODEL, "Safety memory is a separate partition"). Until 2026-10-18 the engine priced nothing in that partition and folded Class="Safety" logic and tags into the standard total (6.7 KB to 22.8 KB on the seven real safety files with readings); both are now wired from the `safe_*` captures (below). The capture script reads the safety value as `safety_bytes` since 2026-10-17. Safety-family instructions in the real set: ESTOP 4, ROUT 4, RIN 1 (INSTRUCTION_COVERAGE); the rest of the real safety logic is ordinary instructions in safety routines. |
| **Expected movement** | **Zero on the seventeen-program headline**: safety processors are excluded from accuracy by rule. The payoff is a new reported number, safety memory used, for GuardLogix users, plus TASKS 2 (removing safety content from the standard total, 0.7 to 1.9 points on the seven safety files, toward under-prediction). |
| **Needed before any spec** | 1. A screenshot of Controller Properties > Capacity on a safety project, and the Window Spy control names of its safety fields, so the capture script can record the safety reading next to the standard one. 2. A Studio-made seed project: 1756-L81ES at v35, File > New defaults, one Safety task/program/routine with one rung per instruction the safety routine offers, Studio-created backing tags, a few safety tags of each atomic type, verified with 0 errors, exported to L5X with both Capacity readings. It supplies syntax and backing-tag types and proves the L5X-to-ACD converter handles safety content; as one total it cannot separate per-instruction costs. 3. The real safety exports (13, 38 to 41, and the 5069-L306ERS2 program) back in `samples/local/`, to rank what real safety programs use before anything is built. |
| **Method once those are in** | Count sweeps on the seed's shapes (each safety-routine instruction at several rung counts, each safety tag type at several counts, the safety task/program/routine shell, safety tags read from standard logic), each differenced against its own zero-content control, specced in TASKS and approved before generation. Safety files need a 1756-L81ES v35 exemption in `lint.py` and CLAUDE.md, the same narrow form as `PlatNine`. |
| **Seed readings, 2026-10-17** (Studio-made, 1756-L81ES, v34, SIL2/PLd, kept in `samples/local/`) | `L81ES.L5X`, File > New (MainTask/MainProgram/MainRoutine plus SafetyTask/SafetyProgram/MainRoutine, no content): **standard 18,408, safety 1,394.** Engine 18,408, exact (13,296 baseline + 4,816 routine base + 296 safety shell). `L81ES_Sample.L5X`, the same plus three controller-scope safety tags (FPMS : FIVE_POS_MODE_SELECTOR, RIN : REDUNDANT_INPUT, ROUT : REDUNDANT_OUTPUT) and one rung each of FPMS, ROUT and RIN in the safety routine: **standard 18,576 (+168), safety 2,754 (+1,360).** The engine prices the three tags as ordinary standard tags (120 + 136 + 120 = 376) and the three instructions at 0, so it reads 208 high on the standard side. 168 = 3 × 56, the alias-tag formula 56 + 8 × floor(len / 8) at names under 8 characters: a hypothesis from one point with three unknowns, not wired. Instruction syntax and backing-tag types are as exported: `RIN(RIN,AUTOMATIC,A,B,CircuitReset,FaultReset)`, `ROUT(ROUT,NEGATIVE,Enable,Feedback1,Feedback2,FaultReset)`, `FPMS(FPMS,Input1,...,Input5,FaultReset)`. |
| **Seed 2, handed over 2026-10-17** | The safety routine's instruction set (a Studio scrap of every instruction it offers) checked against the weight table: 37 never sized. One rung each, one backing tag each (`<MNEMONIC>_1`), BOOL operands on one safety `SBit : BOOL[64]`, ATAN2 on `SReal : REAL[8]`. **Filled in full** (operand order from the seed's RIN shape or known): ESTOP, ENPEN, DIN (as RIN), LC, CROUT, DCS, SMAT, ATAN2; the enum spellings in LC, CROUT, DCS and SMAT are not confirmed. **Backing tag only, other operands `?`** (order not known here; Rockwell's help site is unreachable from the sandbox): THRS, THRSe, DCST, DCSTL, DCSTM, DCSRT, DCM, TSAM, TSSM, FSBM, DCA, DCAF; the metal-form set CPM, CBIM, CBSSM, CBCM, CSM, EPMS, AVC, MMVC, MVC; the drive-safety set SFX, SS1, SS2, SBC, SOS, SDI, SLS, SLP. Backing types are the predefined names already sized in `memory_model.yaml` (DCI_STOP, MUTING_*, CB_*, SAFE_*, SAFELY_*...). The completed export is the syntax source for generation. **Real use:** ESTOP 4, ROUT 4, LC 2, RIN 1; the other 33 have none, so under the floor rule they get their seed rung and no generated sweep. |
| **Operand = member rule** | In the seed's decorated data, each safety instruction's operands after its backing tag are exactly the backing structure's members between `EnableIn` and `EnableOut`, in declaration order: REDUNDANT_INPUT (ResetType, ChannelA, ChannelB, CircuitReset, FaultReset), REDUNDANT_OUTPUT (FeedbackType, Enable, Feedback1, Feedback2, FaultReset), FIVE_POS_MODE_SELECTOR (Input1 to Input5, FaultReset). A `*Type` member is a drop-down keyword in the rung (AUTOMATIC, NEGATIVE), not a tag. Member names known: the three seed types, EMERGENCY_STOP (ChannelA, ChannelB, CircuitReset, FaultReset), CONFIGURABLE_ROUT (Actuate, Feedback1, Feedback2, InputStatus, OutputStatus, Reset; a real call, `gen_instruction_firstpass.py`). Inferred from the family, unconfirmed: ENABLE_PENDANT and DIVERSE_INPUT as EMERGENCY_STOP; LIGHT_CURTAIN as ChannelA, ChannelB, InputFilterTime, MuteLightCurtain, CircuitReset, FaultReset (operand order confirmed by a real call, `coverage.py`). The other 29 backing types: member names unknown. A helper project went out 2026-10-17 to get them: the seed's empty L81ES with one Class="Safety" tag of each of the 36 backing types (empty `<Structure>` bodies, the form the predefined probe imported with 0 errors) plus `SReal : REAL[8]`. Opened and re-exported by Studio, its decorated data lists every member; it is a discovery file, not a capture, and is not kept in the repository. Not used: the seed-2 rungs are being built by hand in Studio instead, and that export is the syntax source. |
| **Seed 2 in, 2026-10-17** | A Studio-made v35 safety routine, one rung per instruction, every operand filled (36 instructions), with its printed ladder naming each operand. Every call shape is in `docs/SAFETY_INSTRUCTIONS.md`. It corrects the operand = member rule: settings come first (drop-down keywords written with their spaces, `EQUIVALENT - ACTIVE HIGH`, and times as numbers or tags), then inputs as the backing tag's own members; the drive-safety instructions also take the SFX tag and end with separate output tags. THRSe was invisible to the parser (the only lowercase mnemonic) and is now counted. A routine export cannot be compared with a reading: the measurement needs the whole project exported plus its standard and safety Capacity values, and the same two values for an empty v35 L81ES. |
| **Measured, 2026-10-18** (112 files, 1756-L81ES v35, zero build errors, both readings on every row) | Every sweep exact, to the byte, at every count. **Controller-scope safety tag:** 56 + 8 × floor(len / 8) standard (the alias-tag formula; four name lengths) and the data block in safety (8 × ceil((28 + data) / 8) as fitted here; round 2 corrected it to 24 + data for a scalar and 32 + data for an array, the 28 having fitted only because every round-1 size was 4 mod 8), the same for BOOL, SINT, INT, DINT and REAL at 10, 50 and 200 tags; a BOOL[256] pays 64 safety. **Safety-program tag:** 0 standard, both halves safety: DINT 96, and all 39 backing structures with zero residual. **Safety-instruction rungs:** 0 standard; per-rung safety costs in MEMORY_MODEL (ESTOP, RIN, ROUT 360 and LC 436 exact at 10/50/200). The routine's NOP: 16 safety, 0 standard. **Safety base:** 1,394 with no rungs at v34 and v35 alike. **Standard logic reading a safety BOOL:** 28 a rung against 20 on standard tags, +8 per safety operand (one shape). The safety partition does not move with standard content: `safe_ref_*` read 1,474 throughout. `safe_n00` reads −1,810 against the old engine: the realism plant's −1,794 (OQ-REALISMFLOOR, every baseline file) plus the safety NOP's 16, now removed. |
| **Wired, 2026-10-18** | Rounds 1 to 3 (271 files): `sizing/report.py` leaves safety-program tags, aliases and logic out of the standard total, charges a controller-scope safety tag its name entry, each extra safety program 64 + its name, a safety AOI its definition less 800, and standard logic 8 / 4 per safety bit / word operand; `sizing/safety.py` prices the safety partition (base, tags, aliases, shells, every safety and ordinary instruction, safety AOIs and their calls, encoded (safety-locked) ones at a minimum), shown by the CLI and the UI as its own bar. **Safety: all 271 files exact to the byte. Standard: 249 exact against the realism plant's −1,794; the other 22 within 32 bytes of it** (Still open, 2). Both Studio seeds exact on both partitions. |
| **Measured, round 4, 2026-10-19** (31 of 32 files captured, zero errors; `safe_aoi_call_60` converted but has no capture row) | **Safety exact on all 28 safety files, before any change.** Tag mapping at 0 / 1 / 10 / 50 / 200 pairs: 0 in both partitions. Safety AOI instances at 5 and 60 and calls at 5; definitions with 3/3 and 6/6 BOOL parameters and 9 locals move only the standard share; 10 internal rungs +180 safety. Routine names of 16 / 24 / 40 characters +8 / +16 / +32. ATAN2, COP, FLL at 100 rungs on their corrections. The safety base and one content step on 5069-L330ERMS2, 5069-L320ERMS2 (v35) and 1756-L81ES v32 / v34: the same 1,410 and +6,544 safety everywhere, +3,200 standard everywhere. **Standard:** the 5069 bases read 280 / 296 below the engine (the safety shell charged twice, below); MOV from a scalar safety DINT 8 a rung, not 4; the UDT twins on 1756-L81E read the same −16 / −32 as on the L81ES, and the array twin the same +4 per array tag, so neither is a safety term. Three warnings, all `safe_rtn_name*`'s designed uncalled routine. |
| **Wired, 2026-10-19** | 1. `safety_capable_baseline_delta` (296) only when the file has no safety task: it is the safety task/program shell Studio creates for a safety controller whose file carries none (the firmware-matrix 5069 S2/S3 files had none), and a file with its own safety task is already charged that shell; 5069-L320ERMS2 now reads exactly the plant constant, L330ERMS2 +16. 2. Standard logic naming a scalar atomic safety tag alone pays 8 (`standard_scalar_operand_bytes`), exact on `safe_sref2_mov_50` and consistent with `safe_comp_2`'s twelve. 3. KNOWN now: routine names (five buckets), the ATAN2 / COP / FLL corrections (20 and 100 rungs), the safety AOI split and call terms (six definitions, instances at 5/20/60, calls at 5/20). No other file moved; the real safety programs' standard predictions drop 296 on every 5069 and nothing else changes. |
| **Still open** | 1. **Safety I/O**: every real safety program carries it (2 to 25 safety modules each: 1734 IB8S/OB8S, 5069 and 1756 safety I/O, Kinetix 2198 safety drives, PowerFlex 527, a FANUC robot, BNI00HN) and none of it is priced in the safety partition; the dominant gap, and the reason real predictions are minimums (TASKS 0w, 0x). 2. Standard-side residuals beyond the plant's −1,794, each under 0.004%: a 1/1 safety AOI definition −8 (noise floor; larger ones exact); 5069-L330ERMS2 +16 (L320ERMS2 exact); 1756-L81ES v32 +16 (the known L8x v34/v35 +16); +4 per standard array tag and UDT definitions −16 / −32, both shown by their 1756-L81E twins to be standard-engine terms (OQ-REALUNDER, "A standard array tag on the plant reads +4"; OQ-UDTMEMBERNAME). 3. Not measured: a scalar word operand inside a safety routine (priced 4; 8 in standard logic), the signature and the lock (in 9 of 17 real programs; a Studio-made variant of `safe_n00`, TASKS 0x), SIL3, an encoded (safety-locked) safety AOI's logic, `safe_aoi_call_60` (converted 2026-10-19, no capture row). |
| **Confidence, 2026-10-19, after round 4** | **Measured exact, wired:** every safety tag shape at both scopes (atomics, structures, LINT, UDTs, arrays, AOI instances, aliases, names 4 to 40), the base and one content step on 1756-L81ES v32 / v34 / v35 and 5069-L330ERMS2 / L320ERMS2 v35, routine and program shells and routine names to 40 characters, all 39 safety instructions with operands anywhere, ordinary logic in a safety routine (the law covering every instruction of the palette, its three corrections at two counts), standard logic reading safety tags, safety AOIs (six definitions, instances to 60, calls to 20), and tag mapping (free). **Safety: 299 of 299 captured files exact to the byte.** **On a program with no safety I/O, signed or not, the safety figure is expected exact to tens of bytes on these platforms.** **Not yet priced:** safety I/O (in every real safety program, so their safety predictions are minimums), the signature and the lock. |
| **CAPTURE** | two Studio-made readings above; the `safe_*` batch (119 files) built 2026-10-17, rebuilt the same day with the Local module's ProductCode corrected (164 → 211); the rebuilt files convert (about 90 s each), except all seven `safe_std_*` (control included, so a tag, not a rung): Studio rejected the BOOL array `SIn` as an invalid tag name — it is the SIN function, matched case-insensitively. Renamed to `SfIn`/`SfOut`/`SfTmr`/`SfDa`/`SfDb`/`SfRa`/`SfRb`/`SfRc`; `validate_logix_name` and lint now refuse any name equal to an expression function or operator. The seven failed files are abandoned, never captured, and rebuilt 2026-10-18 as `safe_std_*_r2`, awaiting conversion. The other 112 converted and captured 2026-10-18 with zero errors and a safety reading on every row. Rounds 2 and 3 (152 files) captured 2026-10-18, zero errors. Round 4: 32 files converted `ok` 2026-10-19 (hashes match the committed files), 31 captured with zero errors (three designed warnings); `safe_aoi_call_60` has no capture row. |

### Blind predictions — real safety programs, 2026-10-18

Seventeen real safety programs, predicted on both partitions by the engine of 2026-10-18 before any Capacity reading was taken; the standard column re-predicted 2026-10-19, still before any reading, after round 4 removed a double-charged safety shell (every 5069 row 296 lower; nothing else moved). Label and file-hash prefix only; the key is `samples/local/safety_aliases.csv` (git-ignored). Read each against its own Capacity tab, standard and safety. **Every one carries content the engine does not yet price in the safety partition** (the right-hand columns), so a safety reading above the prediction by about that content's size is expected, not a model error; 1769 rows are dead architecture and are not tuned on.

| label | sha-256 | platform | standard | safety | safety I/O modules (unpriced) | tag-map pairs | signed / locked | other |
|---|---|---|---:|---:|---:|---:|---|---|
| RS-01 | `752e0a1ffded` | 1756-L81ES v32.11 | 1,829,092 | 39,438 | 12 | 0 | yes / yes | v32 (base measured at v34/v35) |
| RS-02 | `01f580f9e815` | 1756-L81ES v35.11 | 1,479,644 | 44,318 | 16 | 0 | no / no | encoded (safety-locked) safety AOI (minimum) |
| RS-03 | `b561fb3dd64b` | 1756-L81ES v35.14 | 2,809,860 | 67,086 | 25 | 1 | yes / yes | encoded (safety-locked) safety AOI (minimum) |
| RS-17 | `eca51f2acf20` | 1756-L81ES v35.14 | 2,808,372 | 69,058 | 25 | 1 | no / no | an earlier revision of RS-03 with its safety signature and lock removed; its safety AOI in clear text, priced whole |
| RS-04 | `a2482118129e` | 5069-L310ERS2 v31.12 | 496,929 | 15,322 | 4 | 3 | yes / yes | v31 (base measured at v34/v35) |
| RS-05 | `a56a78264b31` | 5069-L320ERMS2 v34.11 | 1,234,386 | 18,746 | 2 | 1 | yes / yes |  |
| RS-06 | `2408d3a7c51c` | 5069-L320ERMS2 v32.11 | 673,888 | 16,382 | 6 | 0 | no / no | v32 (base measured at v34/v35) |
| RS-07 | `843ea76ed63c` | 5069-L320ERMS3 v35.11 | 1,071,773 | 16,402 | 6 | 8 | no / no |  |
| RS-08 | `3dc33183e17d` | 5069-L330ERMS2 v34.14 | 1,513,827 | 19,310 | 5 | 1 | yes / yes |  |
| RS-09 | `725c7eda172e` | 5069-L330ERMS2 v32.13 | 678,252 | 16,382 | 6 | 0 | no / no | v32 (base measured at v34/v35) |
| RS-10 | `3451c8af3cc3` | 5069-L340ERS2 v35.11 | 2,845,175 | 34,610 | 4 | 1 | no / no |  |
| RS-11 | `2c50a52a64fa` | 1769-L30ERMS v30.11 | 571,978 | 14,110 | 4 | 0 | no / no | dead architecture; v30 (base measured at v34/v35) |
| RS-12 | `e060d6900501` | 1769-L30ERMS v30.12 | 471,851 | 14,110 | 4 | 0 | no / no | dead architecture; v30 (base measured at v34/v35) |
| RS-13 | `e12cca1a2ccd` | 1769-L30ERMS v30.14 | 573,330 | 14,110 | 4 | 0 | yes / yes | dead architecture; v30 (base measured at v34/v35) |
| RS-14 | `4f6521c6d420` | 1769-L30ERMS v32.13 | 656,281 | 15,802 | 4 | 0 | yes / yes | dead architecture; v32 (base measured at v34/v35) |
| RS-15 | `96dde6b4e9fe` | 1769-L33ERMS v30.14 | 753,452 | 16,858 | 6 | 0 | yes / yes | dead architecture; v30 (base measured at v34/v35) |
| RS-16 | `5b9bf99acaf1` | 1769-L33ERMS v32.13 | 852,085 | 12,390 | 6 | 0 | no / no | dead architecture; v32 (base measured at v34/v35) |

---

## 5. OQ-UDTMEMBERNAME — the UDT member-name pool, reopened 2026-10-19

| | |
|---|---|
| **The bar** | Real programs carry about 174 UDT definitions with member names of about 12 characters. The wired pool charges `8 × ceil(Σ(len + 1) / 8)` a definition; the candidate below charges about 3 a member less, on the order of 5 KB (0.1 to 0.5%) a real program, **in the direction that deepens the real under-prediction**. So a change here is judged on the seventeen real programs, which are not in this session's checkout, and is not wired from generated rows alone. |
| **Why reopened** | Re-priced live (the generators' own files rebuilt in memory, no files written), the sweeps the law was derived from do not all fit it: four BOOL members, lengths 2 to 32, a flat −8 (the form fits, the level is 8 high); four DINT members, lengths 2 / 7 / 16 / 32: −16 / −8 / −16 / −16 (not flat); nested UDT, lengths 2 and 32: −32 / −32; BOOL count 1 / 2 / 4 / 8 / 16 at length 7: +8 / 0 / −8 / −24 / −48. The AOI-name controls read 0. Safety rounds 2 and 4: `SafeUdtS` (D, R, B1, B2) and `SafeUdtL` (D0..D9) read 16 and 32 below the engine on a 1756-L81ES and on its 1756-L81E twin alike, so their pool is 0. |
| **Candidate** | `8 × ceil(Σ max(0, len − 2) / 8)`, names of up to two characters free: exact on the DINT arm and both safety UDTs, 8 off on the BOOL length arm. The BOOL member-count arm moves with the BOOL count, not the names, so a BOOL-run term is mixed in it. |
| **Test** | TASKS 0y: one-UDT definitions on the plant, DINT and BOOL members separately, lengths 1 / 2 / 3 / 4 / 8 / 12 at 4 and 8 members, each against the plant alone. Then the candidate goes against the seventeen. |
