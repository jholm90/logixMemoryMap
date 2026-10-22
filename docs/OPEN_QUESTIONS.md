# Open Questions

**Eight.** OQ-SAFETYLOGICIO opened 2026-10-21 (the three real safety programs still outside a few percent on the safety figure; its opening lead refuted and its candidates re-ranked 2026-10-22). Batch A (2026-10-21) closed OQ-AOIBOOLINST and wired laws into OQ-SAFETYPARTITION, OQ-STSHAPE, OQ-MODREPEAT and OQ-STRSHAPE (RESOLVED_QUESTIONS, "Batch A of 2026-10-21"). OQ-STSHAPE, OQ-MODREPEAT and OQ-STRSHAPE opened 2026-10-20 (the standard figure on real safety-controller programs). OQ-UDTMEMBERNAME reopened 2026-10-19. OQ-SAFETYPARTITION opened 2026-10-17 (the safety memory partition, a separate quantity from the standard figure). The 92-file capture of 2026-10-03 closed eight at once and took the real set to **0.97%** mean, **2.57%** worst (RESOLVED_QUESTIONS); the scalar AOI law of 2026-10-21 moves that set and it has not been re-scored (OQ-REALUNDER). Closed questions and their reasoning trails are in `RESOLVED_QUESTIONS.md`.

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
| **OQ-REALUNDER** | **0.97% mean, 2.57% worst, 10/17 inside 1%, 15/17 inside 2%** after the 2026-10-03 batch. **Not re-scored since the scalar AOI law (2026-10-21):** it re-prices every scalar AOI instance, an estimated −100 KB across the seventeen toward under-prediction (672 instances of 40–47-BOOL AOIs); the seventeen are not in this checkout, so the figures above stand until `scripts/quick_eval.py` is run on the owner's machine. Every real program but one still under-predicts. |
| **OQ-SERIESREAL** | **WIRED (option A).** −12 per extra writing instruction in a rung (OTE/OTL/OTU, word-destination writers, TON), exact in all 38 isolating files. Kept open only as the record of why the headline rose; closes once OQ-REALUNDER finds what it was cancelling. |
| **OQ-SAFETYPARTITION** | Opened 2026-10-17. **Batch A wired 2026-10-21: safety exact on all 393 captured safety files.** Every safety device type in the real programs measured (18 types, exact at every count, additive, SIL3 = SIL2) and any other priced by the device law (1,653 a safety input connection + 1,814 an output connection + 16 a data byte: all 18 within 3.4%); produced / consumed safety tags; the SIL3 partner and a peer controller. **Safety figure on the real programs: −1.0% to −1.8% on nine, −5.6% / −8.3% / −7.3% on RS-02 / RS-03 / RS-17** (OQ-SAFETYLOGICIO). Standard figure on the ten counted: **mean 1.34%, worst −2.45%** (1.58% / −3.64% before batch A). Section 3. |
| **OQ-SAFETYLOGICIO** | Opened 2026-10-21. RS-02 / RS-03 / RS-17 (one machine at three revisions) read 6,960 / 16,408 / 14,436 low on the safety figure. **The opening lead, module-tag operands in safety logic, is refuted by the other programs** (about 1.4 bytes an operand, 2026-10-22). Left after the generic term and the encoded AOI's minimum: RS-02 ~4.5 KB, RS-17 ~13.2 KB, in content only these three carry and nothing has measured: a safety AOI call with eight operands (two measured), program parameters (Public, AOI-typed Output) in the safety program, descriptions on safety tags, DCS chained on a rung. Batch B, revised. Section 8. |
| **OQ-STSHAPE** | **Wired 2026-10-21:** 39 `stshape_*` files, every shape exact (tag index 84 / 108 / +40 / +20 as in a rung, a second index 8 less, conditions +16 a comparison / +4 an AND / +16 an OR / +20 on a REAL, ELSE 28, BOOL destinations 28 / 32 / 44). RS-05 / RS-08 / RS-10 −3.43 / −3.64 / −3.08% → −2.38 / −2.45 / −2.01%. The rest is not ST (Section 5). |
| **OQ-MODREPEAT** | **Batch A wired 2026-10-21:** nine catalogs' measured repeat rates; a prefix-less type is the module's own only on a 5069 card (the 843E's are shared); a further copy holds its per-channel configuration again (the 1756-IF8 / OF8, 2.2 × its packed bytes, the owner's diagnosis: specialty cards with a lot of configuration per channel). Open: packed 5069 cards on a controller's bus, a further 1734-AENTR/C adapter (~470–830 over). Section 6. |
| **OQ-STRSHAPE** | **Captured 2026-10-21:** every STRING shape exact against its control. Open: the control's own inventory reads 4 a UDT array element under (a STRING member padded, or a custom string), and EQU / NEQ (built on a REAL bit; rebuilt). Section 7. |
| **OQ-UDTMEMBERNAME** | **Reopened 2026-10-19.** Re-priced live, the member-name pool does not fit its own four-DINT length sweep (−16 / −8 / −16 / −16) or the safety rounds' short-named UDTs (pool 0 where 16 and 32 are charged, on a 1756-L81E twin too). A candidate fits those and misses the BOOL arm by 8. Section 4. |

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

## 3. OQ-SAFETYPARTITION — sizing the safety memory partition

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
| **Measured, safety I/O, 2026-10-19** (41 captured, every one converted `ok`) | **Safety: each CIP Safety device a fixed cost by its safety connections' data type, nothing once, exact at 1 / 2 / 4:** 1756-IB16S (`AB:5000_SDI16`) 6,049; 1756-OBV8S (`AB:5000_SDO8`) 4,497 (the pair reads their sum); BNI00HN 3,901; PowerFlex 527 and 2198-H008-ERS2 (both `AB:CIP_Drive_Safety1`) 3,577; 2198-D012/D020/D032/D057-ERS3 integrated safety (`AB:CIP_Motion_Device_Safety2`) 4,717 each with or without axes; 2198-S086-ERS3 (`AB:CIP_Motion_Device_Safety1`) 4,123. **Standard:** each device a first-of-catalog cost and a per-device cost beyond the module sizing (MEMORY_MODEL, "Safety I/O"). Wired; every file now reads the plant constant on both partitions, except two standard-engine terms that are not safety's: a 2198-D012-ERS3 with axes reads like the other D0xx drives (+2,222 against the engine), and a non-safety S086 with its axis +1,958. `safe_aoi_call_60` (+12,728 safety for 60 calls) exact. Real safety programs: safety from −18…−66% to −1.5…−44%, every remaining gap naming unpriced 1734 cards. **CAPTURE ERRORS: 5 row(s)** — `safe_iol_kx_d012_std_1` / `_2` (the proven non-safety D012 block reports a bus-sharing error, "Primary Bus Sharing Group 3 contains a module configured as Shared DC ... with no module configured as Shared AC/DC"; its reading equals the other D0xx controls' to the byte, so not used for any law); and three files that never converted (XMLSrv_E_IMPORT_ABORTED_NO_CHANGES): `safe_io6_5069_ob16_1` and `safe_io6_5069_mix_2_2` (their 5069-OB16/B module-sweep block carries no ExtendedProperties ConfigID, which every compiled export of the catalog carries; `gen_safety_round6.std_card` now adds it, lint refuses the catalog without it, `module_without_configid`; rebuilt in batch B), and `safe_sil2_5069l320s3_n00` (5069-L320ERMS3 at SIL2; the same catalog at SIL3 converted and captured, `safe_sil3_5069_n00`; **cause unknown** — the converter log carries only the abort, and the Studio error-log line is needed). |
| **Round 5, 2026-10-19** | Safety I/O built (TASKS 0za, 17 files): 1734-IB8S/B and OB8S/B at 1 / 2 / 4 / 8 in a further rack, the IB8S without its test-output connection, a mixed rack, a second rack, and 5069-IB8S/A and OBV8S/A at 1 / 2 / 4 on a 5069-L330ERMS2. The Kinetix safety drive, 1756 safety I/O and PowerFlex 527 wait on a Studio-made export each or permission for derived templates. |
| **Round 6, 2026-10-20** (TASKS 0zb, batch A of 2) | **27 files in the repository** (`gen_safety_round6.py`): 1734-OB8S/A (`AB:1734_OB8S+AB:1734_OB8S_Safety3`, RS-06 / RS-09), 1734-IB8S/B with one connection (`AB:1734_IB8S_Safety6`, beside `safe_io_ib8s1c_4`), 442G-MABLB (`AB:442G_MABB_E0JP4679`, RS-07), each at 1 and 2 on the L81ES plant; **SIL3**, never measured before (RS-01 / RS-03 / RS-07 / RS-17): the 1756-L81ES with its 1756-L8SP partner empty and with round 4's content step, 2 and 4 1734-IB8S/B at SIL3, the 5069-L320ERMS3 at SIL2 (its own control) and at SIL3 empty / stepped / with 2 5069-IB8S/A; **safety produced and consumed tags** to a peer 5069-L306ERS2 (RS-03 / RS-17): the message UDT alone, 1 and 2 produced, the peer alone, 1 and 2 consumed, one of each — measured in the safety partition though standard produced / consumed tags stay force-closed below the floor; the **v31 5069-L310ERS2** base and its content step (RS-04's platform); four standard packed 5069 cards on the 5069-L330ERMS2 base (OQ-MODREPEAT). **13 local files** (templates from compiled real exports, CLAUDE.md exception of 2026-10-19, handed over to go into `samples/generated/safety/`): the generic Ethernet safety device for a robot (`AB:ETHERNET_MODULE_SINT_12Bytes+AB:ETHERNET_MODULE_SINT_8Bytes`, RS-04 / RS-07) and the FANUC R30iB Plus (`FR:Safety_RobotPlus_8Bytes`, RS-01) at 1 and 2; the revision-11 2198-D032-ERS3 with network STO (`AB:CIP_Drive_Safety2`, RS-01) at 1 and 2, `safe_iol_kinsafe_n` with the drive swapped; RS-04's packed 5069 cards (`AB:5000_SDI8_Packed`, `AB:5000_DO8_Packed+AB:5000_SDO8_Packed`, module revision 1) at 1 and 2 on the v31 L310ERS2; the round-5 Kinetix drive and the 1756-IB16S + OBV8S pair at SIL3. With round 5's 17 (still to capture) every safety device type in the ten counted programs has a file; what stays unmeasurable is the encoded AxisSTO safety AOI of RS-02 / RS-03 (source-protected). Partner fix: a 1756-L8SP block needs the ExtendedProperties ConfigID 100 a compiled export carries; lint now refuses one without. |
| **Safety figure, engine of 2026-10-20** | Prediction against reading: RS-05 −1.5%, RS-10 −15.3%, RS-06 / RS-09 −20.9%, RS-03 −25.1%, RS-17 −24.1%, RS-08 −39.5%, RS-07 −42.0%, RS-04 / RS-04u −43.0%, RS-01 −44.0% (not counted), RS-02 −8.4%. Every gap names unpriced devices, and each has a batch-A or round-5 file: 1734-IB8S/B (`Safety2`, RS-01 / 02 / 03 / 07 / 10 / 17) and 1734-OB8S/B (`Safety1`) `safe_io_*`; one-connection IB8S (`Safety6`, RS-06 / 09) `safe_io6_ib8s1c_*`; OB8S/A (`Safety3`) `safe_io6_ob8sa_*`; 5069-IB8S/A and OBV8S/A (RS-08) `safe_io_5069_*`; the packed 5069 cards (RS-04) `safe_iol_5069p_*`; the robot interfaces (RS-04 / RS-07, RS-01) `safe_iol_gensafe_*`, `safe_iol_fanucs_*`; the 442G (RS-07) `safe_io6_442g_*`; the revision-11 STO drives (RS-01) `safe_iol_kx11_*`; SIL3 (RS-01 / 03 / 07 / 17) `safe_sil3_*`; the produced / consumed pair (RS-03 / 17) `safe_pc6_*`; v31 (RS-04) `safe_base_5069l310_v31*`. The encoded AxisSTO safety AOI of RS-02 / RS-03 stays a minimum. |
| **Measured, batch A, 2026-10-21** (round 5's 17, round 6's 27 and the 13 local files; zero build errors but the two non-safety D012 controls; three files never converted) | **Safety: every device type exact at every count built, additive, SIL3 the same as SIL2.** Twelve new types (MEMORY_MODEL, "Safety I/O"): 1734-IB8S/B with and without its output connection 3,513 / 1,629, OB8S/B and OB8S/A 3,457, 5069-IB8S/A 2,513 (packed 1,873), 5069-OBV8S/A 4,497 (packed 3,741), 442G 3,621, FANUC and the generic robot interface 3,745, the revision-11 2198-D032-ERS3 3,578. **Produced / consumed safety tags** 3,788 / 1,169 safety beyond the data block, exact at 1 and 2 and additive; standard exact already. **SIL3**: the 1756-L8SP partner 528 standard (it was charged the flat 2,344), nothing in safety; SIL3 cards, drives, pair, empty base and content step (`safe_sil3_step`, read on the retry of 2026-10-21) identical to SIL2 in both partitions, on the 1756-L81ES and the 5069-L320ERMS3. The peer 5069-L306ERS2 costs 560 standard and nothing in safety. The v31 5069-L310ERS2 base and step exact. **Standard:** each type a first-device and a per-device term (fitted at every count). |
| **Wired, 2026-10-21** | The twelve types; **the device law for any other safety device** — 1,653 per safety input connection + 1,814 per output connection + 16 per byte of connection data, every one of the 18 measured types within 3.4%, each left out of its own fit within 115 bytes (5.5%); priced from the law alone the twelve real programs' safety figure moves at most 1.1 points — and its standard side for an unmeasured catalog (600, +162 with an output connection, +1,242 a standard connection, plus its types' definitions when first defined: a further copy within −312..+248 of the measured ones); the produced / consumed terms; the partner and peer. Standard terms keyed by device key where a catalog has two safety shapes. **All 393 safety files on disk: safety exact on every one; standard at the plant constant except the 1734 cards' fit residuals (−145..+75) and `safe_io_racks_2x2` (+489, its second safety-only adapter).** |
| **Real safety programs, engine of 2026-10-21** | Safety figure (prediction minus reading): RS-01 −1.2%, RS-04 / RS-04u −1.1%, RS-05 −1.5%, RS-06 / RS-09 −1.3%, RS-07 −1.0%, RS-08 −1.8%, RS-10 −1.2%; **RS-02 −5.6%, RS-03 −8.3%, RS-17 −7.3%** (Section 8). Standard figure: RS-02 −1.89%, RS-03 −0.27%, RS-04u −0.61% (locked −2.80%), RS-05 −2.38%, RS-06 / RS-09 +1.65% / +1.66%, RS-07 +0.25%, RS-08 −2.45%, RS-10 −2.01%, RS-17 −0.26%; RS-01 −8.19% not counted (7 SFC routines, 272 steps, and FBD). **Mean 1.34%, worst −2.45% on the ten** (1.58% / −3.64% before batch A); the scalar AOI law moved RS-02 by −0.80 points of that. RS-06 / RS-09 (one program on two v32 controllers) read +1.65%, about the 11,240 v32 baseline delta, which was read off bare files; the v31 RS-04u reads −0.61% under the same kind of delta, so it is a lead, not a finding. |
| **Still open** | 1. **RS-02 / RS-03 / RS-17 on the safety figure** — OQ-SAFETYLOGICIO (Section 8). 2. **The eight others (nine files) read 300 to 1,036 low on the safety figure**: 152 + 4.08 a safety rung fits them (leave-one-out rms 89); module-tag operands are about 1.4 bytes each, not the cause (Section 8). 3. **Never converted** (retried 2026-10-21, same abort): `safe_io6_5069_ob16_1` / `_mix_2_2` (the 5069-OB16/B block without its ConfigID; fixed in `gen_safety_round6`, lint refuses it; rebuilt in batch B) and `safe_sil2_5069l320s3_n00` (5069-L320ERMS3 at SIL2; its SIL3 twins converted; **cause unknown — the Studio error-log line is needed**). 4. The 1734 first-card standard term carries the test rack's adapter (~630 low on a real mixed rack). 5. Not measured: a scalar word operand inside a safety routine (priced 4; 8 in standard logic); an encoded (safety-locked) safety AOI's logic. Measured and closed: the signature and the lock (0 safety, at most 144 standard), SIL3, produced / consumed tags. |
| **Confidence, 2026-10-21** | **Measured exact, wired:** everything in the 2026-10-19 row below, plus every safety I/O device type in the twelve real programs, SIL3, produced / consumed safety tags and the peer controller. **A program whose safety logic names only safety tags is expected exact to tens of bytes on the safety figure on these platforms; one that addresses safety I/O tags in its safety logic reads low by Section 8's amount.** An unmeasured safety device is priced by the device law (within about 3%). |
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

### Readings, 2026-10-19 — the blind test scored

Capacity read on 16 of the 17 (RS-16 dropped, not to be read). Prediction minus reading, as a share of the reading.

| label | standard read | standard error | safety read | safety error | safety gap (read − predicted) |
|---|---:|---:|---:|---:|---:|
| RS-01 | 2,007,604 | −8.89% | 83,129 | −52.6% | 43,691 |
| RS-02 | 1,510,245 | −2.03% | 124,952 | −64.5% | 80,634 |
| RS-03 | 2,819,627 | −0.35% | 197,262 | −66.0% | 130,176 |
| RS-04 | 511,973 | −2.94% | 26,858 | −43.0% | 11,536 |
| RS-05 | 1,279,555 | −3.53% | 22,987 | −18.4% | 4,241 |
| RS-06 | 655,664 | +2.78% | 34,288 | −52.2% | 17,906 |
| RS-07 | 1,074,245 | −0.23% | 34,995 | −53.1% | 18,593 |
| RS-08 | 1,572,161 | −3.71% | 31,910 | −39.5% | 12,600 |
| RS-09 | 658,680 | +2.97% | 34,288 | −52.2% | 17,906 |
| RS-10 | 2,935,942 | −3.09% | 50,058 | −30.9% | 15,448 |
| RS-17 | 2,817,995 | −0.34% | 197,262 | −65.0% | 128,204 |
| RS-11 (1769) | 622,636 | −8.14% | 17,656 | −20.1% | 3,546 |
| RS-12 (1769) | 518,040 | −8.92% | 17,656 | −20.1% | 3,546 |
| RS-13 (1769) | 624,084 | −8.13% | 17,656 | −20.1% | 3,546 |
| RS-14 (1769) | 707,484 | −7.24% | 20,548 | −23.1% | 4,746 |
| RS-15 (1769) | 785,944 | −4.13% | 24,104 | −30.1% | 7,246 |

**Standard figure on 1756 / 5069 safety controllers: mean 2.20%, worst −3.71% on ten programs.** Blind on the safety figure throughout; on the standard figure blind for three (RS-02, RS-03, RS-17) — seven others already had a standard reading on file (`realprog_13`, `realprog_37` to `_42`), which safety processors keep out of every fit, so they were not tuned on, but they were not unseen. RS-01 is not counted (decided 2026-10-19): it carries 7 SFC and 2 FBD routines, languages the engine does not size, so its −8.89% measures the missing languages, not the model. RS-16 is dropped and will not be read. Nine of the ten others inside 3.6%. The 1769 rows (dead architecture) read −4% to −9% and are not tuned on.

**Safety figure: −18% to −66%, every one low, and the gap is safety I/O.** It scales with the safety module count (about 2 to 3 KB a 1734 / 5069 safety module, about 5 KB a Kinetix safety drive, a 1756 safety module more). A per-family charge fitted on these readings does not hold up: leave-one-out misses run from +34% to −56%, and one constant a module leaves ±30%. So safety I/O is measured from Studio seeds, not fitted (TASKS 0x item 1).

**Signature and lock cost nothing in safety:** RS-03 (signed and locked) and RS-17 (an earlier revision with both removed, its safety AOI in clear text) read the same 197,262. On the standard side RS-03 reads 1,632 more than RS-17 against 1,488 predicted for their content difference, so the signature and the lock together cost at most about 144 standard. RS-06 and RS-09 (the same safety content on 5069-L320ERMS2 and L330ERMS2, v32) read the same 34,288, as predicted (16,382 each).

---

## 4. OQ-UDTMEMBERNAME — the UDT member-name pool, reopened 2026-10-19

| | |
|---|---|
| **The bar** | Real programs carry about 174 UDT definitions with member names of about 12 characters. The wired pool charges `8 × ceil(Σ(len + 1) / 8)` a definition; the candidate below charges about 3 a member less, on the order of 5 KB (0.1 to 0.5%) a real program, **in the direction that deepens the real under-prediction**. So a change here is judged on the seventeen real programs, which are not in this session's checkout, and is not wired from generated rows alone. |
| **Why reopened** | Re-priced live (the generators' own files rebuilt in memory, no files written), the sweeps the law was derived from do not all fit it: four BOOL members, lengths 2 to 32, a flat −8 (the form fits, the level is 8 high); four DINT members, lengths 2 / 7 / 16 / 32: −16 / −8 / −16 / −16 (not flat); nested UDT, lengths 2 and 32: −32 / −32; BOOL count 1 / 2 / 4 / 8 / 16 at length 7: +8 / 0 / −8 / −24 / −48. The AOI-name controls read 0. Safety rounds 2 and 4: `SafeUdtS` (D, R, B1, B2) and `SafeUdtL` (D0..D9) read 16 and 32 below the engine on a 1756-L81ES and on its 1756-L81E twin alike, so their pool is 0. |
| **Candidate** | `8 × ceil(Σ max(0, len − 2) / 8)`, names of up to two characters free: exact on the DINT arm and both safety UDTs, 8 off on the BOOL length arm. The BOOL member-count arm moves with the BOOL count, not the names, so a BOOL-run term is mixed in it. |
| **Test** | TASKS 0y: one-UDT definitions on the plant, DINT and BOOL members separately, lengths 1 / 2 / 3 / 4 / 8 / 12 at 4 and 8 members, each against the plant alone. Then the candidate goes against the seventeen. |

---

## 5. OQ-STSHAPE — the Structured Text shapes real programs use, opened 2026-10-20

| | |
|---|---|
| **The bar** | The seventeen standard programs carry about 1,510 ST lines in all, so this moves them by under 0.1 point. It is opened for the standard figure on real safety-controller programs (TASKS 0zb, owner's direction 2026-10-20), where it is the largest term: RS-05, RS-08 and RS-10 read −3.30%, −3.42% and −2.78% on the standard figure, −42,240 / −53,725 / −81,592 bytes, against 576 / 756 / 1,126 executable ST lines — −73, −71 and −72 a line. The engine charges about 70 a line there, so real ST costs about twice what it is priced at. |
| **Mechanism** | The ST law (MEMORY_MODEL, structured_text) was measured on `D0 := D1 + D2;`, `IF B0 THEN`, `FOR StIdx := 0 TO 9 DO` and literal array indexes. In the three programs: 444 / 250 / 170 member-path destinations, 298 / 206 / 122 tag indexes, 141 / 102 / 69 IF / ELSIF conditions carrying 185 / 133 / 85 comparisons and 117 / 84 / 51 AND / OR / NOT, 59 / 43 / 33 BOOL destinations, 39 / 27 / 19 ELSE. Priced by analogy with ladder (a comparison as CMP, a tag index at 84 / 108, a member after it +40), these make up roughly half to two-thirds of the gap; the rest is unexplained until measured. |
| **Fixed without a constant, 2026-10-20** | `/* */` comments stripped (charged as code before); ST operand types through the routine's own scope; operands read whole; subscripts not counted as operators or literals. All 79 measured ST files unmoved. |
| **Test** | `stshape_*`, 43 files (TASKS 0zb): each real shape at 400 statements, 200 IF blocks or 50 FOR blocks, against `stshape_n00` (or `stshape_aoi_n00`) and its sibling. Captured 2026-10-21 (batch A), 42 readings; `stshape_vidx_src400` captured against another window (title "TeamViewer options") and its capture columns are cleared, recapture in batch B. |
| **Captured and wired, 2026-10-21** | 39 program-routine files clean (`stshape_vidx_src400` recaptured on the retry, 902,936: a tag-indexed source costs the 84 an indexed destination does). **Every shape exact after wiring** (MEMORY_MODEL, "The shapes real ST is written in"): a tag index 84, an index expression 108, a member after it +40, a tag-indexed BOOL +20 — the rung's own `indirect_index` constants, wherever the index sits — and a second index in one statement 8 less; conditions +16 a comparison, +4 an AND, +16 an OR, +20 more on a REAL; ELSE +28; a BOOL destination 28 from a BOOL or NOT (its right-hand side priced as a condition: AND 32, comparison 44), 44 from a literal; a float literal in a one-operator REAL assignment +4. The 79 earlier ST captures do not move. **RS-05 / RS-08 / RS-10: −3.43 / −3.64 / −3.08% → −2.38 / −2.45 / −2.01%** (with the scalar AOI law). |
| **Still open** | **The remaining 2.0–2.45% on those three is not ST.** Every real ST shape is now a measured one (BOOL destinations 146 literal, 38 copy, 18 comparison; conditions comparisons, AND, OR); AOI-internal ST is 80 statements each (+4 a statement at most); UDT array elements with STRING members 0 to 250 each (Section 7); no FBD or SFC routine. What carries 30 to 58 KB in each is not identified from the readings. The AOI-internal +4 a statement waits on batch B's rebuilt files. |
| **Capture errors** | **CAPTURE ERRORS: 4 row(s)** — `stshape_aoi_n00`, `_assign400`, `_if200`, `_param400`, one error each, "Rung 0: Missing output instruction": the call rung `StAoi(StAoiInst);` is an AOI with no visible output parameter alone on a rung, which does not verify. The AOI's own ST routine is compiled with its definition and the four differ only inside it, so their differences are probably sound, but they are suspect and no law rests on them: `gen_st_shapes` puts a NOP after the call and the four are rebuilt in batch B. |

## 6. OQ-MODREPEAT — what a further module costs, any catalog, any count; opened 2026-10-20

| | |
|---|---|
| **The bar** | RS-06 and RS-09 (one program on two controllers) over-predicted by +2.32% / +2.52%. RS-09 carries two more 1732E-IB16M12R/A than RS-06 and reads 3,016 above it where the engine predicted 4,364: about 700 a copy where 1,432 was charged. Five Ethernet catalogs measured once each paid full price for every copy. The owner's direction (2026-10-20): the law has to handle any I/O module used by anyone, any number of times, not the catalogs measured. |
| **Law, wired 2026-10-20** (MEMORY_MODEL, "A module-defined type is defined once per project") | A module's connection tags carry Rockwell's own data types; a project defines each once. A module whose vendor-prefixed types an earlier module already defined pays its overhead less their UDT-law definitions. It reproduces the nine measured repeat discounts within −72..+104 and one at +240 (440C-CR30), across catalogs as well as copies. An unseen catalog is a base (1,064 for one connection or none, 2,579 for two or more) plus its new types. Not applied to EDS-profile types, CIP Safety devices, rack-aliased cards, adapters and bridges, or a copy whose own repeat rate is measured. |
| **Found 2026-10-20 on 34 existing captures** | The `rack_5069_*` family (one to twelve 5069 cards behind a 5069-AENTR, ten racks with 64 cards in one file, all zero errors) had never been re-priced under the law. With every type shared, the ten-rack file read 29,422 under (−16.6%). The cards' channel types have **no vendor prefix** (`CHANNEL_DI:I:0`): they are defined by every module that carries one, a copy an earlier module defined costing 76 more; the prefixed types are shared. A joint fit (adapter, the 76, each catalog's first copy) leaves rms 17, max 41 bytes on all 34. The adapter, charged the flat 2,344 zero-connection rate, costs 625; the 5069-SERIAL/A 367. The nine 5069 catalogs without an entry were priced blind by the unseen law first: eight within −247..+329 of their own single-card capture, six within ±85; then wired from those captures. |
| **Census** | 251 clean module captures, engine before and after the law: total \|error\| 214,854 → 131,710, inside ±8 117 → 128. The ten-rack file read +12,402 (+7.0%) before the law, −29,422 with every type shared, +570 (+0.32%) now, and every other 5069 rack is within ±0.35%; nothing outside them moved under the channel-type rule; the 497 batch-A files on disk unmoved by it. Real safety-controller programs (prediction minus reading): RS-06 +2.32% → +1.78%, RS-09 +2.52% → +1.80%, RS-03 / RS-17 +0.41% → +0.23%, RS-07 −0.12% → +0.04%; RS-02 −0.72% → −1.19% (four PowerFlex 525 sharing two types, and the D012 first-copy correction +4,008), RS-05 / RS-08 / RS-10 −0.1 to −0.3 point (their packed 5069-IB16 / OB16 sharing `AB:5000_DI16_Packed:I:0` and the rest, and their ETHERNET-MODULEs the configuration type). |
| **Still open** | (1) Packed 5069 cards on a 5069 controller's own bus share their types under the law as fitted on standard-data cards in racks; the real ones (RS-05 / RS-08 two IB16 and two OB16, RS-10 three of each) are measured by `safe_io6_5069_*`. A catalog's entry is one number whatever its data format: 5069-IB16/A's (measured packed) priced its standard-data rack card within 3 bytes; 5069-OB16/B's (measured standard) prices the packed real cards, which `safe_io6_5069_ob16_1` reads. (2) The 1756-CNB/D, 1756-HYD02 and similar zero-connection modules cost less than the flat 2,344 (`rack_1756_n12` to `_n16` +2,384 to +3,458), not separated. (3) The D012 bare-drive `asmclose_2198_d012_*` rows read +4,008 now, as the with-axis shape requires; a drive with no axis exists in no real program. |
| **Test** | `modrep_*`, 36 files on the L81E plant against `realism_base_f25` (TASKS 0zb): round 1, the five catalogs at 1 / 2 / 4; round 2, one class of module each, every one a blind prediction — 1756-IF8/A and 1756-OF8/B (chassis analog), 843E encoders (two prefixed and two prefix-less types on an Ethernet device), PowerFlex 755-EENET at 1 / 2 / 4; 1 / 2 / 4 1734-IE2C/C on their own connections in a sixth POINT rack; 5069-OB16/B one rack × one card, one × four, four × one (a per-card cost inside a rack against a per-copy cost); generic ETHERNET-MODULE one, a second sharing its input type, a second sharing only the configuration type. Plus `safe_io6_5069_*`, 4 files (packed 5069-IB16 / OB16 on the 5069-L330ERMS2 safety base). Captured 2026-10-21 (batch A): all 36 `modrep_*` and the two `safe_io6_5069_ib16_*`, zero errors. |
| **Captured and wired, 2026-10-21** | All 36 `modrep_*` and the two `safe_io6_5069_ib16_*` clean. **Every first copy was already exact; each further copy costs the same at 2 and at 4**, so the nine catalogs carry their measured `repeat_bytes` and every `modrep_*` file now reads exact against its first copy. The law's own repeat, the error for an unmeasured catalog: 1732E +56 / +40, EX260 −72, 843E −40, PowerFlex 525 −224, 1734-IE2C +221, PowerFlex 755 +632 a copy. **The 843E's prefix-less types are shared** (paid again they charged 2,647 a copy against 1,535): a type is the module's own only on a 5069 card. **Per-channel configuration is per copy** (the owner: "specialty cards with lots of configuration per channel that can't be reduced"): the 1756-IF8 / OF8 read 432 / 744 a copy above the law, 2.28 / 2.16 times their nested per-channel configuration (189.5 / 345 bytes packed), the five cards without any −221..+72; wired as 2.2 × those bytes for a further copy of a catalog without its own rate (IF8 −14, OF8 +15 from the law alone). The declared data omits nested structure members (the IF8's 239 bytes of per-channel configuration, the OF8's 628); recorded, not altered. |
| **Still open, 2026-10-21** | (1) **Packed 5069 cards on a controller's own bus**: a second packed 5069-IB16/A reads 568 below the engine (`safe_io6_5069_ib16_2`); the OB16/B never converted (rebuilt in batch B). RS-05 / RS-08 / RS-10 carry two or three of each. (2) **A further 1734-AENTR/C adapter reads 470 to 830 below its price**: 467 (`modrep_1734_ie2c_c_rack`'s sixth rack), 634 (`safe_io_racks_2x2`'s second safety rack), 826 (`l9v38_m_pointio`'s sixth rack); the catalog has no repeat rate, and its first copy reads −66. The likely owner of the realism plant's +1,794 (five racks). Real programs carry 3 to 5 each: a few KB. (3) The 1756-CNB/D, HYD02 and similar zero-connection modules (unchanged). |
| **Capture errors** | **CAPTURE ERRORS: 2 row(s)** — `safe_io6_5069_ob16_1` and `safe_io6_5069_mix_2_2` never converted (XMLSrv_E_IMPORT_ABORTED_NO_CHANGES): the 5069-OB16/B module-sweep block carries no ExtendedProperties ConfigID (711 packed on a controller's bus in every real export carrying one, 110 in standard data on an adapter), and Studio refuses the catalog without it; the IB16/A sweep block imported without one. `gen_safety_round6.std_card` adds it, lint refuses a 5069-OB16 without it (`module_without_configid`), both rebuilt in batch B. Still open (1) above rests on these two. |

---

## 7. OQ-STRSHAPE — STRING operands the way real programs write them, opened 2026-10-20

| | |
|---|---|
| **The bar** | The string instructions' weights were confirmed on the realism floor on STRING array elements (`blkstr_*`: CONCAT, DTOS, COP, SIZE) and MOV of a STRING costs a DINT MOV (OQ-STRINGMOV). The ten counted real safety-controller programs write them otherwise: 2,424 STRING operands of EQU and 2,151 of MOV are members behind an index; 777 INSERT (weighed once, near-empty), 713 CONCAT (264 operands custom-typed), 191 MID. The seventeen standard programs carry 1,850 CONCAT, and OQ-REALUNDER's one string-heavy lead (CONCAT count tracking the residual at ten times CONCAT's own weight) was never explained. |
| **Mechanism** | Unknown: the operand-shape surcharges (OQ-INDIRECTUDT: +40 a member after a tag index, +108 on a STRING array) were measured on numeric instructions; whether a STRING operand's member path or custom type adds its own cost is not. |
| **Test** | `strx_*`, 21 files (`gen_string_shapes.py`, TASKS 0zb): one inventory in every file (STRING arrays, a UDT with STRING, a 40-character custom string, DINT and REAL members, an index tag), 400 calls each, every destination distinct: EQU on elements / members / behind an index, NEQ, MOV member and behind an index, COP member, CONCAT member and custom-typed, INSERT, MID (and behind an index), DELETE, FIND, DTOS, STOD, RTOS, STOR, UPPER; each against `strx_n00`. Captured 2026-10-21 (batch A), 21 readings. LOWER left out: lint does not know it and no real program uses it. |
| **Captured, 2026-10-21** | 17 clean files. **Every STRING shape exact against `strx_n00`**: MOV and COP of members and behind tag indexes, CONCAT of members and of a custom string type, INSERT, MID (and behind an index), DELETE, FIND, DTOS, STOD, RTOS, STOR, UPPER — the string instructions' weights hold on the shapes real programs write. **The control itself reads 4,808 below the engine: 4 an element of the UDT array holding a STRING, a 40-character custom string, DINT and REAL members (engine 224 an element, real 228).** Which member carries it — the STRING padded to 88, or the custom string to 48 — is not separable from these files; it contradicts the "no alignment padding" of OQ-STRINGUDTMEMBER for one of them. Real exposure: 0 to 500 such elements a real safety program (RS-05 0, RS-10 20, RS-08 250), a few KB at most. |
| **Exposure recounted, 2026-10-22** | The "a few KB at most" above counted only array elements that hold a STRING directly. Counted as STRING members nested anywhere in a UDT tag, with every array multiplicity, the three programs the standard figure reads 2.0–2.45% low carry **3,880 / 2,744 / 12,677** (RS-05 / RS-08 / RS-10; RS-08 also 2,361 custom strings), the others 327 to 1,623. A STRING array's element is already 88 (`string_array.builtin_per_element`, KNOWN); a STRING inside a UDT is priced 86. At 88 there the standard figure on the eight programs moves 1.44% → about 1.21% (RS-10 −2.01 → −1.15%, RS-05 −2.38 → −1.78%, RS-04u −0.61 → −0.14%; RS-07 and RS-06 move away by 0.2 and 0.4 points); the custom-string reading (44 → 48) moves it to 1.42%. Not wired: `strx_n00` cannot tell them apart. **Test:** `strm_s2_400`, `_c2_400`, `_sc_400`, `_sd_400` (`gen_string_members.py`, built 2026-10-22, batch B): two STRINGs read +1,600 and the others nothing if a STRING member is 88; two custom strings +3,200 and the STRING + custom string +1,600 if the custom string is 48; STRING + DINT nothing either way. |
| **Capture errors** | **CAPTURE ERRORS: 4 row(s)** — `strx_equ_elem`, `strx_equ_member`, `strx_equ_vidx`, `strx_neq_member`, 400 errors each, "OTE, Operand 0: Invalid bit specifier": the generator wrote each comparison's result to `SuC[i].R.0`, a bit of a REAL member. All four read 16 below `strx_n00`, so none of their 400 rungs reached the controller; the rows measure nothing about EQU / NEQ. Lint now refuses a bit subscript on a REAL (`bit_specifier_on_real`); `gen_string_shapes` writes a BOOL destination and the four are rebuilt in batch B. |


---

## 8. OQ-SAFETYLOGICIO — what RS-02 / RS-03 / RS-17 carry in the safety partition that nothing has measured, opened 2026-10-21

| | |
|---|---|
| **The bar** | After batch A the safety figure reads −1.0% to −1.8% on the eight other real safety programs and **−5.6% / −8.3% / −7.3% on RS-02 / RS-03 / RS-17** (one machine's program at three revisions): 6,960 / 16,408 / 14,436 bytes. The owner's tolerance on the safety figure is a few percent. The standard figure is not involved. |
| **Opened on a lead that the other programs refute (2026-10-22)** | The question was opened on module-tag operands in safety logic (slot-path card points at ~24 an operand, drive members at ~34). A census of every real safety program's safety content (all routines, operands by spelling, tags, devices, AOIs, parameters, documentation) bounds them: RS-01 has 129 adapter slot-path operands (`Adapter:1:I.Pt04Data`), RS-06 42 drive `SI` / `SO` members and 43 slot-path operands, RS-08 68 `Local:1:I` points, RS-04u 60, and each reads 300 to 1,036 low in all. Fitted with the rung count, a module operand in an ordinary safety instruction costs **about 1.4 bytes**, and at most 5 to 8 even if each program's whole gap were its operands. On RS-17's 316 that is ~0.4 KB, not the 7.5 KB the lead claimed. |
| **Ruled out with existing data** | Device blocks: RS-02 and RS-17's drives, cards and local pair carry exactly the connections, sizes and revisions of the measured templates, and devices are additive at 1 / 2 / 4 drives, 1 to 8 IB8S and a second rack; standard-only drives leave the safety reading at 1,410 (`safe_iol_kinstd_*`). Rung comments (RS-01 15,129 characters), safety-tag member comments (RS-10 3,240, RS-07 1,749, RS-05 1,565), cards without a module name (RS-10 2, RS-08 4), SIL3 (RS-01, RS-07), the lock and signature (RS-03 reads RS-17's 197,262 with every safety element identical but the AOI exported encoded): each sits in a program 0.3 to 1 KB low. The AxisSTO call routine is identical in RS-02 and RS-17 (29 calls, nine operands each, 14 rungs of two calls), so whatever it costs it cannot explain RS-17's increase over RS-02. |
| **What is left to explain** | **Generic, all eleven:** the eight others fit 152 + 4.08 a safety rung (leave-one-out rms 89 bytes) or 54 + 42 a device + 0.58 a bit instruction (81); not identified, inside a few percent, and no single test targets it. **Specific to the three:** RS-02 and RS-03 export AxisSTO encoded, priced at a minimum (its locals and logic, 1,972 = RS-03 − RS-17 at identical readings). Less that and the generic term: **RS-02 ~4.5 KB, RS-17 ~13.2 KB**. |
| **Candidates — none measured, ranked by fit** | 1. **Operands of a safety AOI call beyond two.** Every measured safety call passed two (`SafeAoiA(Inst, AiIn[i], AiOut[i])`, +44 a call over the standard call law); AxisSTO passes eight on a 16-parameter AOI. Read per operand or per parameter, the +44 is 22 / 11 each, and the 29 calls are short **3.8 KB in both revisions**, most of RS-02's ~4.5 KB. 2. **Program parameters in the safety program**: RS-02 38 `Usage="Public"` BOOLs; RS-17 59 Public (BOOL, TIMER, DCI_STOP) and the 29 AxisSTO instances as `Usage="Output"`. Public is free in standard memory (OQ-PUBLICTAG); Input / Output have never been measured in either partition, and no other real safety program has one. Carrying RS-17's further ~8.7 KB alone, an Output AOI parameter would cost ~300, about twice its data block. 3. **Descriptions on safety tags**: RS-02 31 (1,019 characters), RS-17 94 (3,261), every other program 0 to 3. 4.3 to 4.4 a character fits both revisions by itself, but descriptions and comments are free in standard memory (`tagcomment_*`, `udt*comment_*`), member comments are free in safety (above), and RS-04u's 83 characters would put it 440 over. 4. **DCS chained 2 to 10 on a rung with nothing else** (RS-02's 24; every measured DCS stood alone on its rung): RS-06's one chain of three bounds it near 40 an instruction, ≤ 0.9 KB. 5. **Content in an uncalled safety routine**: measured only as one NOP (`safe_rtn_idle_*`); RS-02's ten subroutines are never called. Priced as if called; if they are not compiled the engine over-charges RS-02. 6. **The AxisSTO instance layout**: priced unpacked (116 an element, block 136); packed (60, block 88) would mean 1.4 KB over-charged on RS-17, the true remainder larger. |
| **Test (batch B, TASKS 0zd, BUILT 2026-10-22: 26 files, blind predictions recorded)** | Studio-made variants of RS-17 measure the AxisSTO calls and the instances with their definition in place. Isolation files measure each candidate alone, each against a control in its own family: a safety AOI call's operand count and kind, program parameters by usage, descriptions on safety tags, DCS chained on a rung, content in an uncalled routine, an AxisSTO-like AOI's instances; one module-operand pair confirms the bound above; a mixed-rung family tests the generic per-rung residual. |
