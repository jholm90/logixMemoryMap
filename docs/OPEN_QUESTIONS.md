# Open Questions

**Four.** OQ-MOTIONOP and OQ-DENSERUNG opened on export 27's routine and rung variants. OQ-BRIDGEPH and OQ-V36MNEMONIC closed on the 29-file batch after. The capture batch that followed export 43 closed eight at once: PROGSCOPESTRUCT, REALISMFLOOR, PIOADDR, TYPEDMEMBER, INDIRECTUDT, STRINGMOV, MIXEDTYPE and L9PLATFORM. INDIRECTUDT and MIXEDTYPE were wired and took the real set from 1.79% to **0.77%** mean. Closed questions and their reasoning trails are in
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
| **OQ-REALUNDER** | **2.18% mean, 4.31% worst, all seventeen under** (export 33 excluded) since the series-output law was wired. The ~2% is a real under-charge the unwired law had been cancelling; the leads and the plan are in TASKS 0k. Checkpoint of the 0.58% state: tag `checkpoint-2026-09-25-pre-series-law`. |
| **OQ-SERIESREAL** | **WIRED (option A).** −12 per extra writing instruction in a rung (OTE/OTL/OTU, word-destination writers, TON), exact in all 38 isolating files. Kept open only as the record of why the headline rose; closes once OQ-REALUNDER finds what it was cancelling. |
| **OQ-MOTIONOP** | Axis attributes and MOTION_INSTRUCTION members read short in real ladder; 44-file `motop_*` batch built, awaiting capture. |
| **OQ-DENSERUNG** | Whether dense real-shaped rungs (5–7 instructions, branches, many writers) cost more than their parts; built in the same batch. |

---

## 1. OQ-REALUNDER — the residual itself

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

## 3. OQ-MOTIONOP — operands that live in the motion system

| | |
|---|---|
| **Evidence** | Plant + export 27's worst program, one routine removed per file (Studio-made): all seven routines read short of the engine by 6.8%–38.6%. Two rungs isolated from it (one rung kept per routine, differenced against the routine-removed file): homing-routine rung 7 measured **712 vs 568** predicted (short 144, 25%); cam-correction rung 3 measured **2,484 vs 2,232** (short 252, 11%). A two-feature fit over the seven routines gave ~+50 per axis-attribute reference and ~+29 per MOTION_INSTRUCTION member reference (rms ±216), but those rates over-predict both isolated rungs (rung 7: 3 axis + 8 MI refs → ~380; rung 3: 12 axis refs → ~600), so the rates are not right as stated. |
| **Mechanism** | The engine prices `Axis.ActualPosition` and `Mi.DN` as ordinary member operands and cannot type axis attributes. A MOTION_INSTRUCTION status bit is a bit of FLAGS the way TIMER.DN is a bit of its control word; whether the axis/MI path pays a premium, per reference or per distinct axis, is what the batch measures. |
| **Expected movement** | Real exposure (17 programs): 6,440 axis-attribute and 1,366 MI-member references. At the fitted rates ~20% of the real shortfall on average (2% to 68% by program), i.e. ~0.4 pp of the 2.18% mean; at the rates the two isolated rungs allow, less. |
| **Batch built** | `gen_motion_operands.py`, `samples/generated/motop/`, 44 files, 1756-L81E v35, realism floor, the captured-exact `l9v38_m_kinetix_l8v35` content plus one shared inventory (4 AXIS_VIRTUAL; MOTION_INSTRUCTION and TIMER as 400 scalars, a [400] array each, and members of 100 `MoCell` UDT tags; plain `MoRef` UDT controls). `motop_n00` control. `axr_*` (14): axis REAL attribute in MOV/GRT/LIM/SUB vs `MoRef.R`; CIP vs virtual, one axis vs two, ActualPosition vs CommandVelocity, 100 vs 400. `axb_*` (7): AxisHomedStatus / VelocityStandstillStatus in XIC/XIO vs a BOOL member and a DINT-member bit. `mi_*` (15): XIC and OTU on MI .DN (and EN/DN/ER/PC/IP cycling) as scalar, array element and UDT member, each vs a TIMER in the same position, plus a DINT-array bit. Real-rung templates were built and withdrawn before commit: a real rung's structure over synthetic tags is customer-derived content and may not sit under `samples/generated/`; a real rung shape is measured only from Studio-made variants. |
| **Reads** | motion − paired control = the premium per reference; `_n100` vs `_n400` = per-reference scaling; `cip1` vs `cip` = per distinct axis; `sub1`/`sub2` = per reference vs per call; `mi_xic_dw_arr` = whether a status bit costs like a word-bit read. |
| **CAPTURE** | not yet captured |

## 4. OQ-DENSERUNG — dense real-shaped rungs

| | |
|---|---|
| **Evidence** | Export 27's transplanted programs carry 530–680 instructions, 116–214 extra writers and 70–94 branch openings per 100 rungs (plant: 249, 0, ~10) and read 9–15% of their logic short. Each feature was measured exact alone (series law across 38 shapes incl. `srsty_*` legs to k=8; branch tests), so the suspect is their combination in long rungs. |
| **Mechanism** | A per-rung or per-branch cost that grows with rung length beyond what the series law and branch costs charge. |
| **Expected movement** | Unknown until captured; if dense rungs carry it, up to the ~11% of logic the category test found (the whole residual). |
| **Batch built** | In the `motop_*` batch: `dens_ser_k{01,04,16,64}`, `dens_br_k{04,16}`, `dens_nest_k16` — the same 1,600 heterogeneous units (XIC/XIO, GRT/LES, MOV or OTE) in every file, 1 to 64 per rung in series, 4 and 16 as branch legs, 16 nested two deep. |
| **Reads** | residual of each against `dens_ser_k01` is what density costs beyond the model; zero means dense rungs are priced right and the shortfall is in operands. |
| **CAPTURE** | not yet captured |
