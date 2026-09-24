# Open Questions

**Eleven.** Three opened with the realism floor (REALISMFLOOR, SERIESREAL, PIOADDR); four with the operand-spelling finding (TYPEDMEMBER, INDIRECTUDT, STRINGMOV, MIXEDTYPE); two with the L9 / v38 batch (L9PLATFORM, V36MNEMONIC), which are platform scope rather than real-set residual. Closed questions and their reasoning trails are in
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
| **OQ-REALUNDER** | The real residual: **1.66% mean, 4.83% worst** on the seventeen standard-processor real programs present (was 2.86% / 5.42% before operand spelling was resolved). |
| **OQ-TYPEDMEMBER** | Confirm the newly wired rule: a member-path, alias or AOI-parameter operand pays the same type surcharge as a bare tag. Wired on real-set evidence. 23 files built, awaiting capture. |
| **OQ-INDIRECTUDT** | `UdtArray[Idx].Member` — 16,000 of the ~19,300 real indirect references — priced from one `DINT[20]` bare-MOV calibration. 14 files built, awaiting capture. |
| **OQ-STRINGMOV** | `MOV` of a STRING — 7,626 real uses, priced as a DINT MOV, never measured. 5 files built, awaiting capture. |
| **OQ-MIXEDTYPE** | A typed instruction mixing operand types (`MOV(DINT,REAL)`, `ADD(REAL,DINT,…)`) — 24 to 932 per real file; conversion cost measured only inside CPT. 8 files built, awaiting capture. |
| **OQ-PROGSCOPESTRUCT** | Program-scoped UDT and array tags — in 14 of 17 real programs, densest in the three worst, never built. 12 files built, rebuilt on the realism baseline, awaiting capture. |
| **OQ-REALISMFLOOR** | Does the model still hold on a controller that is a quarter full, with I/O, and with every output bit written once? 2 files awaiting capture. |
| **OQ-SERIESREAL** | The −12-per-extra-series-output law, re-measured with no duplicated bits on a full controller. 8 files awaiting capture. |
| **OQ-PIOADDR** | A POINT I/O address vs a controller BOOL vs an alias as a rung operand. 6 files awaiting capture. |
| **OQ-L9PLATFORM** | Is an L9 at v38 a constant offset from an L81E at v35? Firmware and platform separated by a third arm. 96 files built, awaiting capture. Moves nothing on the seventeen (none is L9 or v36+). |
| **OQ-V36MNEMONIC** | From v36 the comparisons are spelled GE/GT/LE/LT/EQ/NE. Priced identically to GEQ/GRT/LEQ/LES/EQU/NEQ; only GEQ→GE is a stated fact. 6 discriminator files built, awaiting capture. |

---

## 1. OQ-REALUNDER — the residual itself

**Now 1.66% mean, 4.83% worst — see "Spelling, not cost" below.** The history that follows is the 2.86% state.

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

## 2. OQ-PROGSCOPESTRUCT — does a UDT or array tag cost the same at program scope?

Program-scoped DINT tags are exact (`tagscope_*`, 10 to 1,000 tags). A program-scoped
**UDT or array** tag has never been built: an element sweep over the seventeen
standard-processor real programs found `Program/Tags/Tag/Data/Structure` and `/Array`
in 14 of them and in no generated file that captured clean. They are densest in the
three worst-predicted programs — exports 27, 06 and 33 carry 102, 118 and 157.

| | |
|---|---|
| **Mechanism** | a per-program tag table, or a per-tag cost for structured program tags, the engine does not charge |
| **Expected movement** | unknown until read; the three worst files carry the most of them |
| **Batch built** | 12 files, `gen_program_scope_struct.py`: the identical UDT tags (7 members) and DINT[20] arrays at controller scope vs program scope, at 10, 50 and 200 tags. 1756-L81E fw35, lint and confound clean. Rebuilt on the realism baseline, identical in all twelve |

---

## 3. OQ-REALISMFLOOR — does the model hold on a full controller?

Every instruction weight was fitted on files that are almost empty: typically under 5%
of the controller, no I/O, and ten BOOLs reused thousands of times
(`gen_logic_sweep._b(i)` is `B{i % 10}`). Real programs fill 16–94%, every standard one
has at least 5 Ethernet I/O nodes, and they reference thousands of distinct tags. If
operand encoding depends on where a tag sits in the data table or how many distinct tags
a routine touches, no calibration file could have seen it.

| | |
|---|---|
| **Mechanism** | an operand or instruction cost that depends on controller fill, data-table offset or distinct-tag count |
| **Expected movement** | up to the whole residual (~2.9 points) if the plant under-predicts at real fill; zero, and the hypothesis eliminated, if it lands exact |
| **Batch built** | `realism_base_f25` (baseline alone, 842,178 predicted, 26% of an L81E) and `realism_base_f50` (plant doubled, 1,632,706). Plant = 1,280 stations, each a UDT instance, a TIMER and ten rungs (seal-in branch, TON and its DN, GRT, ONS+ADD, EQU+OTL, OTU, MOV, LES), all isolation-confirmed instructions, every output bit written once. f25→f50 is a count sweep of a composite unit, so the confound gate flags it; it is read as residual per station, not as one cost |

## 4. OQ-SERIESREAL — the series-output law with no duplicated bits

`OQ-SERIESOUTPUT` measured −12 per output after the first, exactly, on 16+ files —
every one near-empty and, bar the three `srout_oteuniq` files, writing the same bits in
every rung. Applying it to the real set makes every real file worse. 18 of the 25 worst
generated files are this one law.

| | |
|---|---|
| **Mechanism** | the discount belongs to the calibration shape (empty controller, repeated bits), not to series outputs as real ladder has them |
| **Expected movement** | none directly — the law is not wired. If it vanishes here, the engine is right to leave it out and the contradiction is closed; if it holds, real programs carry 0.5–1.5% of bytes the model over-charges, and the true residual is that much larger |
| **Batch built** | 1,600 distinct output BOOLs, each written once, a distinct condition per rung, identical tags in all 8: `realism_srout_series_k{01,02,04,08}` (1600/k rungs of XIC then k OTEs), `_branch_k{02,08}` (parallel legs), `_inter_k{02,08}` (k XIC-OTE pairs per rung — the instruction list of k01 exactly, only rung packing moves) |

## 5. OQ-PIOADDR — POINT I/O address vs controller BOOL vs alias

Real standard programs use 100–1,700 direct module-tag operands each
(`RACK:slot:I.b` is the commonest POINT I/O form: 1,108 input and 510 output uses), and
up to 3,350 alias tags onto I/O. No generated file has ever put a module tag in a rung.

| | |
|---|---|
| **Mechanism** | a module-tag operand resolves through the adapter's rack-optimized connection image, and an alias adds a level; either could cost more than a plain BOOL reference |
| **Expected movement** | per-operand delta × real count: at +8 per operand, 1,500 operands is 12 KB, ~0.2–0.5% on a mid-size program |
| **Batch built** | `realism_pio_{bool,addr,alias}_n{080,160}`: n rungs of `XIC(in)OTE(out)`; controller BOOLs, the RACK_n:slot:I.b / O.b points directly, or alias tags onto them. All 320 BOOLs and 320 aliases declared in all six. 160 is every point the five racks have |


## 6. OQ-TYPEDMEMBER — does a member-path operand pay the bare tag's type surcharge?

Wired on real-set evidence (above): resolving member paths, aliases, program scope and
AOI parameters moved all 17 real files toward zero. No generated file carries a typed
member operand, so the rule itself has never been captured in isolation.

| | |
|---|---|
| **Mechanism** | the surcharge follows the operand's type, however it is spelled |
| **Expected movement** | none if confirmed (already wired); up to +0.9 points back if a member path does NOT pay it |
| **Already in the waiting batch** | the realism plant carries 1,280 `LES(Stn.Pv,Stn.PvHi)` on REAL members — 20,480 bytes of this rule in every `realism_*` and `progscope_*` file. `realism_base_f25` against its own prediction reads it before any new file is built |
| **Batch built** | `opsp_typed_{add,mov,grt}_{real,int}_{bare,member,arrelem}` (18) + `opsp_typed_*_dint_bare` DINT controls (3) + `opsp_aoi_add_{real,dint}` (AOI definition, 100 internal ADDs on REAL vs DINT locals). Each member file against its bare twin |

## 7. OQ-INDIRECTUDT — indirect addressing into a UDT array

The whole indirect-index price rests on `MOV(Arr[Idx],Dest)` with `Arr` a `DINT[20]`:
a 4-byte element, a power of two, read by one MOV. Real indirect references:

| shape | real uses |
|---|---:|
| `UdtArr[Idx].Member` | 15,936 |
| `UdtArr[Idx]` (whole element, mostly COP) | 1,355 |
| `StrArr[Idx]` | 1,014 |
| `DintArr[Idx]` — the calibrated shape | 366 |
| `BoolArr[Idx]` | 229 |

…inside MOV, EQU, XIC, NEQ, COP, XIO, SUB, ADD, OTL. An element size that is not a
power of two needs a multiply; a BOOL array needs a bit address; a member adds an
offset. Before the member-index fix, `UdtArr[Idx].Member` count alone took the
residual from 1.98% to LOO 1.29%.

| | |
|---|---|
| **Mechanism** | address computation depends on element size, member offset and bit addressing |
| **Expected movement** | up to ~0.6 points |
| **Batch built** | `opsp_ind_mov_e{04,08,12,76}_{idx,lit}`, `opsp_ind_xicmem_*`, `opsp_ind_xicbool_*`, `opsp_ind_equ_e76_*` — 14 files, each `_idx` against its literal-index `_lit` twin. The engine predicts every element size identically (+84 per indexed rung) |

## 8. OQ-STRINGMOV — MOV of a STRING

7,626 real `MOV`s have a STRING operand (6,044 STRING→STRING, 1,001 with an indexed
source), 53 to 1,309 per file. The engine charges a DINT `MOV` (36). A STRING is an
88-byte structure; `COP` of a structure costs more than an atomic move (JSR structured
arguments: +8 per copy). Never measured.

| | |
|---|---|
| **Mechanism** | a structure move compiled as a copy, not a register move |
| **Expected movement** | 0.2–0.6 points; export 16 (2.6%) carries 1,309 |
| **Batch built** | `opsp_str_{mov,cop,movidx,movcustom,movdint}` — 5 files. The engine predicts `mov` and `movcustom` identical to the DINT control |

## 9. OQ-MIXEDTYPE — a typed instruction whose operands differ in type

The surcharge table was fitted on files where every operand of a call has one type;
the engine charges by the first resolvable operand. Real files carry 24 to 932 mixed
calls each (`MOV(DINT,REAL)`, `ADD(REAL,DINT,REAL)`, `GRT(INT,DINT)`). Inside CPT a
DINT→REAL conversion measures 40 per operand; outside CPT it has never been measured.

| | |
|---|---|
| **Mechanism** | an implicit conversion per mismatched operand |
| **Expected movement** | 0.1–0.4 points |
| **Batch built** | `opsp_mixed_{mov_d2r,mov_r2d,mov_i2d,mov_d2i,add_drr,add_rdd,grt_rd,grt_id}` — 8 files, sharing one tag inventory with `opsp_typed_*` so the uniform twins are the typed `_bare` and `_dint_bare` files |

All 50 files (`gen_operand_spelling.py`, `samples/generated/opspell/`) are on the
realism floor (RACK_1..RACK_5, ≥25% fill, no duplicated output bits), 1756-L81E fw35,
500 added rungs each, identical tag inventory within each question; lint and confound
clean. Awaiting capture.

## 10. OQ-L9PLATFORM — is the L9 at v38 a constant offset from the L81E at v35?

An L9 cannot run v35, so any L9 file differs from every existing capture in platform
**and** firmware at once. The engine charges the L9 +2,276 bytes over an L81E, read off
18 near-empty v38 captures, and charges nothing for v35→v38 on an L81E. Neither has been
seen with content in the file.

| | |
|---|---|
| **Mechanism** | a per-content rate that differs by firmware or platform, which near-empty files cannot show (the rejected per-platform baseline broke 612 files for exactly that reason) |
| **Expected movement** | none on the seventeen, which are all v31–v35 L8x/5069. It is what makes an L9 number quotable at all |
| **Batch built** | `gen_l9_v38.py`, `samples/generated/l9v38/`, 96 files: 32 content items × three arms — `l8v35` (1756-L81E v35.05, v35 spelling, the control), `l8v38` (1756-L81E v38.02, v36+ spelling), `l9v38` (1756-L908TS v38.02, v36+ spelling). Content byte-identical across arms apart from the spelling. Items: densities `d0000..d1600` (stages 1–2), 21 instructions × 1,000 rungs `i_*` (stage 3), and `m_{kinetix,pf525,geneth,pointio,local1756,alarms}` (stage 4). Every file on the realism baseline |
| **How to read it** | `l8v38 − l8v35` per item = the firmware move; `l9v38 − l8v38` = the L9. Both flat across the densities → two project constants, and stages 3–4 confirm. Either growing → a rate, and stage 3 says which instruction carries it |
| **Unproven in the build** | an L9 Ethernet child is parented to Local port 4. The L9 blanks carry no modules; port 4 is where all five real 5069 programs put theirs. The L9 arm's Kinetix blocks are the L8 arm's proven blocks re-parented; `check_proven_blocks.py` now reads a block parented to the controller's own Ethernet port (2 on L8, 4 on L9) as one shape, and still refuses any other port |
| **Not covered** | the L9 capacity budget (OQ-L9BUDGET, resolved as bounded): a bench reading on an empty project per catalog, not a file |

## 11. OQ-V36MNEMONIC — the v36 comparison renames

From Logix Designer v36 the ladder comparison instructions are spelled **GE, GT, LE, LT,
EQ, NE** where v35 and earlier spell them **GEQ, GRT, LEQ, LES, EQU, NEQ**. GEQ→GE is a
stated fact; the other five are the same renaming carried across the family, and no
v36+ export with ladder is on file to confirm them. The six are 9.3% of every instruction
occurrence across the real exports in `samples/local/`, so a v36+ file read without the mapping would price every
comparison at zero.

| | |
|---|---|
| **Wired** | `parser.logic.V36_MNEMONIC_ALIASES` / `canonical_rung_text`: rung text is respelled to v35 where it is read (program routines, AOI internal logic, coverage), so both spellings price identically. A file-declared AOI of the same name wins. `lint` accepts the new spellings on MajorRev ≥ 36 and refuses them below (`v36_mnemonic_before_v36`); `lint.to_v36_spelling` respells a whole file for a v36+ build |
| **Open** | whether v38 still imports the v35 spelling, and whether the other five renames are right |
| **Batch built** | `l9v38_spell_{equ,neq,grt,les,geq,leq}_l8v38_v35spelling` — each the `l9v38_i_*_l8v38` file with the v35 spelling left in. An import error answers "not accepted"; a clean import reading the same as its twin answers "alias", and a re-export shows which spelling Studio writes. A rejected new spelling in the `i_*` v38 files would equally falsify that rename |
| **Expected movement** | none on the seventeen; without it, every comparison in a v36+ export is unpriced |

