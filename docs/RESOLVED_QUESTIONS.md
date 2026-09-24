# Resolved Questions

Every closed sizing and behaviour question, with the verdict and the evidence.

**Check this file before repeating an investigation.** Its purpose is to stop a
question being re-asked, and especially to stop a refuted answer being re-derived —
several of the entries below record a formula that fitted its own data perfectly and
was wrong.

Constants live in `MEMORY_MODEL.md`. Open questions are in `OPEN_QUESTIONS.md`.

## The four ways a question closes here

| | |
|---|---|
| **SOLVED** | A measured law, wired, with the residual stated. |
| **CLOSED NEGATIVE** | The suspected effect does not exist. As valuable as a law — it stops the search. |
| **BOUNDED** | The effect is real and too small to matter. Closed without being solved. |
| **OUT OF SCOPE** | Deliberately excluded. Not a data gap. |

**Thirty-four questions closed at once on one finding.** An eight-parameter
per-category fit, fitted directly on the held-out real programs — cheating, an upper
bound no honest procedure can beat — reaches mean 1.01% / max 2.59% and still fails
the stopping rule; under leave-one-out it is worth 0.007 percentage points. **So
every question whose mechanism was "a cost constant is slightly wrong" has a measured
maximum payoff of approximately zero**, however cleanly it would have answered.

## A closed question can still own errored capture rows

The rows outlive the question. Where that happens the count is recorded in the
entry, because an error with nowhere to be recorded is an error that gets forgotten.
`scripts/capture_errors.py` enforces it.

---

# Tags, UDTs and strings

## OQ-PROGSCOPESTRUCT — does a UDT or array tag cost the same at program scope?

**RESOLVED — scope is free.** Captured on the realism floor: every `progscope_ctl_*` file reads byte-identical to its `progscope_prog_*` twin at 10, 50 and 200 tags, UDT and array alike, and the engine already predicted them identical. Program scope costs exactly what controller scope costs. Side finding, not a scope effect: a standalone `DINT[20]` array tag reads +4 over its prediction per tag in both scopes (arrays n010/n050/n200: +16/+176/+776 against the UDT arm, i.e. −24 + 4n). Real exposure is a few kilobytes; recorded, not wired.

**The question as it was asked:**

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

## OQ-REALISMFLOOR — does the model hold on a full controller?

**RESOLVED — the model holds on a full controller.** `realism_base_f25` (842,178 predicted) and `realism_base_f50` (1,632,706, the plant doubled) both read **−1,794**, to the byte. The plant — 1,280 then 2,560 stations of ordinary ladder — is priced exactly at a quarter and at half of the controller; operand encoding does not depend on fill, data-table offset or distinct-tag count. The −1,794 is a constant of the baseline shell (the five POINT I/O racks are the likely owner: a sixth identical rack, `l9v38_m_pointio`, reads −826 on its own), present identically in every file built on the baseline.

**The question as it was asked:**

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

## OQ-PIOADDR — POINT I/O address vs controller BOOL vs alias

**RESOLVED — no difference.** `realism_pio_{bool,addr,alias}` read byte-identical at 80 and at 160 operands: a rack-optimized POINT I/O address (`RACK_n:s:I.b`), a controller BOOL and an alias onto the I/O point cost the same as a rung operand, and the engine already priced them the same.

**The question as it was asked:**

Real standard programs use 100–1,700 direct module-tag operands each
(`RACK:slot:I.b` is the commonest POINT I/O form: 1,108 input and 510 output uses), and
up to 3,350 alias tags onto I/O. No generated file has ever put a module tag in a rung.

| | |
|---|---|
| **Mechanism** | a module-tag operand resolves through the adapter's rack-optimized connection image, and an alias adds a level; either could cost more than a plain BOOL reference |
| **Expected movement** | per-operand delta × real count: at +8 per operand, 1,500 operands is 12 KB, ~0.2–0.5% on a mid-size program |
| **Batch built** | `realism_pio_{bool,addr,alias}_n{080,160}`: n rungs of `XIC(in)OTE(out)`; controller BOOLs, the RACK_n:slot:I.b / O.b points directly, or alias tags onto them. All 320 BOOLs and 320 aliases declared in all six. 160 is every point the five racks have |

## OQ-TYPEDMEMBER — does a member-path operand pay the bare tag's type surcharge?

**RESOLVED — confirmed.** REAL operands spelled as a bare tag, a UDT member, or a member of a literal-indexed UDT-array element read byte-identical for ADD, MOV and GRT, as wired. The AOI arm (`opsp_aoi_add_real` vs `_dint`) is exact: AOI-internal logic pays the surcharge. INT member/array-element operands read **+4 per rung** over the bare INT spelling in all six files; each of those rungs has exactly one INT member at a non-4-byte offset, so the data cannot separate "+4 per rung" from "+4 per misaligned INT operand". Recorded, not wired: 2,716 real calls carry an INT member operand (0.63% of real instructions), about 11 KB at +4 each — ~0.02% of real bytes, below the floor.

**The question as it was asked:**

Wired on real-set evidence (above): resolving member paths, aliases, program scope and
AOI parameters moved all 17 real files toward zero. No generated file carries a typed
member operand, so the rule itself has never been captured in isolation.

| | |
|---|---|
| **Mechanism** | the surcharge follows the operand's type, however it is spelled |
| **Expected movement** | none if confirmed (already wired); up to +0.9 points back if a member path does NOT pay it |
| **Already in the waiting batch** | the realism plant carries 1,280 `LES(Stn.Pv,Stn.PvHi)` on REAL members — 20,480 bytes of this rule in every `realism_*` and `progscope_*` file. `realism_base_f25` against its own prediction reads it before any new file is built |
| **Batch built** | `opsp_typed_{add,mov,grt}_{real,int}_{bare,member,arrelem}` (18) + `opsp_typed_*_dint_bare` DINT controls (3) + `opsp_aoi_add_{real,dint}` (AOI definition, 100 internal ADDs on REAL vs DINT locals). Each member file against its bare twin |

## OQ-INDIRECTUDT — indirect addressing into a UDT array

**RESOLVED — WIRED, and the largest single gain since operand spelling.** What the index selects matters; its size does not. Against their literal-index twins, 500 rungs each:

| indexed operand | measured | was charged |
|---|---:|---:|
| `Arr[Idx].Member`, element 4 / 8 / 12 / 76 bytes, MOV and EQU; a BOOL member by XIC | **124** | 84 |
| `BoolArr[Idx]` by XIC | **104** | 84 |
| `StrArr[Idx]` by MOV | **192** | 84 |

`indirect_index.member_access_cost` 40 (KNOWN, six files), `bool_element_cost` 20 and `string_element_cost` 108 (FITTED, one file each). A bit after the index is unmeasured and charged nothing extra. The parser now records each index's array path and what follows it (`_indirect_index_sites`); sizing resolves the element type. With OQ-MIXEDTYPE: **real set 1.79% → 0.77% mean, 4.83% → 3.87% worst**; no generated exact row moved.

**The question as it was asked:**

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

## OQ-STRINGMOV — MOV of a STRING

**RESOLVED.** `MOV` of a STRING costs exactly a DINT `MOV` (`opsp_str_mov`, `_movcustom` = `_movdint`), as the engine already charged; `COP` of one STRING is exact too. The one gap was an **indexed** STRING-array source, +108 over the index cost — wired under OQ-INDIRECTUDT.

**The question as it was asked:**

7,626 real `MOV`s have a STRING operand (6,044 STRING→STRING, 1,001 with an indexed
source), 53 to 1,309 per file. The engine charges a DINT `MOV` (36). A STRING is an
88-byte structure; `COP` of a structure costs more than an atomic move (JSR structured
arguments: +8 per copy). Never measured.

| | |
|---|---|
| **Mechanism** | a structure move compiled as a copy, not a register move |
| **Expected movement** | 0.2–0.6 points; export 16 (2.6%) carries 1,309 |
| **Batch built** | `opsp_str_{mov,cop,movidx,movcustom,movdint}` — 5 files. The engine predicts `mov` and `movcustom` identical to the DINT control |

## OQ-MIXEDTYPE — a typed instruction whose operands differ in type

**RESOLVED — WIRED.** Bytes per call over the DINT control, 500 rungs each: MOV(D→R) 76, MOV(R→D) 72, ADD(D,R,R) 68, ADD(R,D,D) 108, GRT(R,D) 68, MOV(I→D) 60, MOV(D→I) 52, GRT(I,D) 60. The law (`operand_type_surcharge.mixed`, FITTED):
- DINT with REAL: the instruction's REAL surcharge + **52** per DINT source + a DINT destination **40** (48 on MOV). The 52 is exact three ways.
- DINT with INT: **52** per INT operand + **8** when an INT is a source; uniform INT is 52 per operand already (MOV 104, ADD 156).
- Any other mix keeps the old first-operand rule.

All eight files read exact after wiring.

**The question as it was asked:**

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

## OQ-L9PLATFORM — is the L9 at v38 a constant offset from the L81E at v35?

**RESOLVED — two constants, both already wired.** 32 content items (five densities, 21 instructions × 1,000 rungs, six module/alarm items), each on three arms:

| difference | every one of the 32 items |
|---|---:|
| 1756-L81E v38 − 1756-L81E v35 | **0** |
| 1756-L908TS v38 − 1756-L81E v38 | **+2,276** |

Flat from an empty controller to 1,600 density units, across every instruction and module type — the firmware move costs nothing for content and the L9 is the same +2,276 project constant the engine already charges from the blank captures. The v36 respellings (MOVE, LIMIT, GE…) read identical to their v35 twins. Still open outside the files: the L9 capacity budgets (OQ-L9BUDGET) and a real L9 program predicted blind. Side findings on the shared baseline (identical in all arms): a sixth POINT I/O rack over-predicted by 826; one generic ETHERNET-MODULE (8 in / 8 out SINT) under by 440; the density rungs carry the series-output law again (−12 per rung with MOV + OTE; see OQ-SERIESREAL).

**The question as it was asked:**

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

## OQ-V36MNEMONIC — sixteen ladder instructions renamed at v36

**RESOLVED as a stated fact, not a capture.** From v36 these instructions are spelled
differently, and a v36+ project **does not accept the v35 name**:

| v35 | v36+ | v35 | v36+ | v35 | v36+ | v35 | v36+ |
|---|---|---|---|---|---|---|---|
| EQU | EQ | NEQ | NE | GRT | GT | GEQ | GE |
| LES | LT | LEQ | LE | MOV | MOVE | LIM | LIMIT |
| SQR | SQRT | TRN | TRUNC | XPY | EXPT | ACS | ACOS |
| ASN | ASIN | ATN | ATAN | TOD | TO_BCD | FRD | BCD_TO |

The table is the conversion map the capture tooling applies (`LegacyToV36`). The ST
function names already used SQRT, ACOS, ASIN, ATAN and TRUNC; the rename brings ladder
into line.

**What is wired.** `parser.logic.V36_MNEMONIC_ALIASES` / `canonical_rung_text` respell
rung text to the v35 name wherever it is read (program routines, AOI internal logic,
coverage), so every weight, surcharge and destination table applies unchanged and both
spellings price identically; a file-declared AOI of the same name wins. `lint` refuses an
old name at MajorRev ≥ 36 (`v35_mnemonic_at_v36`) and a new name below 36
(`v36_mnemonic_before_v36`). `lint.to_v36_spelling` respells a whole file's rung text.

**What was withdrawn.** The first L9/v38 build asked whether v38 still takes the old
spelling with six `l9v38_spell_*_v35spelling` files. It does not, so the files were
deleted before capture, and the rest of the batch was rebuilt with MOV and LIM respelled
too (the first build had respelled only the six comparisons, which would have failed on
every MOV in the baseline).

**Exposure.** None of the seventeen real programs is v36+. Without the mapping, a v36+
export would price every one of these instructions at zero — the six comparisons plus
MOV and LIM are about 21% of every real instruction occurrence.

## OQ-BITSHIFT — BSR and BSL both cost exactly 60 bytes; the length operand is free

**SOLVED.** The assumed weight was right, and it is now measured rather than assumed.

All 15 files converted and captured with **0 errors and 0 warnings**.

**BSR = exactly 60.000 bytes per rung**, over four independent intervals:

| interval | bytes | rungs | per rung |
|---|---:|---:|---:|
| 10 → 50 | +2,400 | 40 | **60.000** |
| 50 → 100 | +3,000 | 50 | **60.000** |
| 100 → 500 | +24,000 | 400 | **60.000** |
| 500 → 1,000 | +30,000 | 500 | **60.000** |

**BSL is identical to BSR**, not merely close: differenced at equal rung count the
two families agree to **+0 at all five counts** — 19,008 / 21,408 / 24,408 / 48,408 /
78,408, the same numbers on both sides. The shared weight of 60 was an assumption; it
is now a measurement.

**The length operand costs nothing.** Lengths 32, 64, 128 and 256 against a fixed
DINT[8] array all capture at **24,432** — byte-identical, four for four. The array is
priced by the tag sizer; the operand itself is free.

**A per-rung CONTROL costs exactly its own tag storage and nothing more.**
`bitshift_ctlper_n01000` (one CONTROL per rung) minus `bitshift_bsr_n01000` (one
shared CONTROL) is 95,904 over 999 extra tags = **96.000 bytes each**, which is the
CONTROL tag size the model already charges. There is no per-instruction surcharge for
giving each rung its own control structure.

**Engine agreement: all 15 rows predict at −4 bytes**, inside the ±8
single-measurement noise floor. Mean |error| 0.0138%.

**Effect on reporting.** `instruction_accuracy` now carries `BSR {samples: 3,
worst_pct: 0.0083}` and `BSL {samples: 2, worst_pct: 0.0083}`, putting both in the
**Measured ±0.1%** band. The real routine that motivated the question — two BSR rungs
carrying 58% of its compiled size — moves from *Unverified, unbounded* to Measured
over those bytes.

**No sizing constant changed.** `BSL: 60` and `BSR: 60` stand as written; what changed
is that they are no longer assumptions.

**Two design errors caught before capture**, recorded because they are this project's
recurring failure mode: arm A originally declared one CONTROL per rung, moving tag
inventory with instruction count; arm C originally moved array size with the length
operand. `confound_check.py` refused both before any file was submitted.

## OQ-ALIGN — UDT member padding

**SOLVED.** No alignment padding between members at all. `BOOL, DINT, BOOL` = 6
bytes; `DINT, BOOL, BOOL` = 5. A run of consecutive BOOLs shares one backing byte and
**a non-BOOL member breaks the run**, forcing the next BOOL onto a fresh byte.
Confirmed against real capacity data across every UDT sweep, and the implementation
already produced it. Confidence flipped UNKNOWN → KNOWN.

## OQ-TAGOVERHEAD — per-tag flat cost

**SOLVED.** `84 + 8 × floor(name_len / 8)`, additive with the tag's own data size.
Tag names are stored in 8-character chunks. **Two independently derived measurements
agree exactly**, which is why this is KNOWN rather than FITTED. Type barely affects
it and is treated as type-independent.

## OQ-ALIASSIZE — do alias tags cost anything

**SOLVED, and it reversed the previous answer.** An alias costs
`56 + 8 × floor(name_len / 8)` — the same 8-character bucket shape as an ordinary
tag, with its own flat base and no data term. Exact across all three buckets tested.

> The earlier claim of zero was wrong. It correctly observed that an alias has no raw
> data size and **incorrectly concluded that meant no cost.** Roughly 21% of a real
> program's tags are aliases, so this was not an edge case.

## OQ-SHELLCONST — the standalone atomic tag data slot

**SOLVED.** A standalone atomic tag's data occupies a **fixed 4-byte slot regardless
of declared type.** SINT and INT are padded up to it; LINT is reported in it rather
than the 8 its value needs. Six bare 50-tag files, one type each, zero residual on
all six.

**This is what a large bucket of files sitting at exactly −5 had been.** Their tag
pool was 5 each of SINT/INT/DINT/LINT/REAL: −15 −10 +0 +20 +0 = −5 exactly, on every
file regardless of instruction. It was also most of the bytes behind the corpus's
largest residual bucket.

Arrays and structure members are deliberately untouched — this is a per-**tag** slot
rule, and a test asserts `SINT[100]` stays exactly 300 bytes smaller than `DINT[100]`.

## OQ-UDTTAGSLOT — is a standalone UDT tag's slot padded

**SOLVED.** Padded to 8 bytes, alongside a −4 extra. Derived from the one place two
captured families disagreed about what a single UDT tag costs — and they disagreed
only because they sit on opposite sides of that boundary. **Neither constant is
separable from either family alone.**

Arrays are deliberately untouched: padding elements instead improves the real files
more and destroys the tags category, so that gain is absorbing some other missing
term.

## OQ-UDTMEMBERNAME — do UDT member names cost anything

**SOLVED, and it was the largest single real-file gain in the project.** They cost an
8-aligned pool: `8 × ceil(Σ(len + 1) / 8)`. They were charged **nothing**.

**A raw one-byte-per-character rate fits five of seven measured points and misses
two.** That pair is the entire discrimination between the two forms — any sweep whose
name lengths share a residue mod 8 cannot tell them apart, which one follow-up batch
demonstrated by being unable to.

Cross-checked flat in tag count (so per definition, not per instance), and agreeing
across member counts and member types. Real UDT member names average about 12
characters and a real program carries on the order of 174 definitions.

## OQ-UDTBOOLMEMBER — superseded by OQ-UDTMEMBERNAME.

## OQ-NESTEDUDT — **SOLVED.** A nested UDT member's size is that UDT's own total, recursed, with cycle detection. Only BOOLs pack, so a nested UDT always starts fresh. True by construction — no code path merges it into a preceding partial byte.

## OQ-ARRAYPACK / OQ-UDTARRAYALIGN — array element rounding

**SOLVED.** Array of UDT: `dimension × ceil(udt_size / 4) × 4` — each element rounds
up to 4 bytes, no padding beyond. Confirmed at five counts for a 3-byte-tight UDT and
for an already-8-byte UDT where the rounding is a no-op. **Atomic-type arrays are not
subject to this rounding.**

## OQ-BOOLPACK / OQ-BOOLARRAY — BOOL storage

**SOLVED for the distinction that matters.** A BOOL **array** bit-packs into
DINT-sized words, `ceil(dimension / 32) × 4`. A standalone BOOL **tag** does not — it
takes 4 bytes. **Do not conflate the two.** The array rule stays ASSUMED: it is
standard documented behaviour but this project has not validated it with its own data.

## OQ-TAGORDER — does declaration order matter

**CLOSED NEGATIVE. Order is free.** Raised from outside the model: "BOOL LINT INT
DINT BOOL takes up different space than another order." It does not.

Six files hold the same 400 tags with identical names and move nothing but the
sequence — grouped, wide-first, narrow-first, alternating, pairs, shuffled. The
engine, which has no order term, predicted all six at 56,528. **All six captured at
56,528.** That covers the widest span the multiset allows.

## OQ-TAGSHAPE — is the residual in tag data space

**CLOSED NEGATIVE, and this one matters most.** `controller_tag` is 60% of predicted
mass, which made it the obvious suspect. **Every real tag shape is already covered**,
and the untested ones total a few thousand bytes against a residual two orders of
magnitude larger. The name-length term — the strongest-looking candidate — is cleared
by 88 clean rows at mean 0.12%.

**The residual is not in tag data space.**

**CAPTURE ERRORS: 1 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the row outlives it, so the count is recorded here
rather than lost.

## OQ-STRINGTAGOVERHEAD / OQ-STRINGTAGOVERHEAD-BUILTIN — **SOLVED.** A built-in STRING tag costs exactly 2 bytes **less** than the ordinary per-tag formula predicts. Exact across a 9-point count sweep and a 4-point name-length cross-check: always `−2 × count`, independent of both.

## OQ-CUSTOMSTRING / OQ-CUSTOMSTRINGDEF — custom string types

**SOLVED, and it found a real bug.** The DATA member was sized raw with no rounding.
**DATA rounds to the nearest multiple of 8, rounding DOWN at the exact tie.** Verified
exact against nine maxlen points spanning every mod-4 and mod-8 remainder: 50 and 51
measure byte-identical, 100 is a tie and drops, 101 is already aligned and stays.

**One rule fully explains the real per-tag rate** — no separate correction needed.

The type definition itself costs a clean step function in its name length, exact
against 22 of 22 dense points, plus 8 more when maxlen ≡ 1 mod 4 (exact at 3 of 3).

## OQ-STRINGUDTMEMBER — **CLOSED NEGATIVE.** A built-in STRING as a UDT member needs no correction at all. The disentangling points already had unreconciled capture data showing so.

## OQ-STRINGARRAYPAD / OQ-CSARRAYBASE / OQ-STRARRAYLARGEN — **SOLVED and wired.** Array-of-STRING padding follows the same rules.

## OQ-STRINGCONSTFAIL — **RESOLVED as a generator bug**, not a sizing question. A double underscore in a padded tag name, from a filler ending in `_` abutting a numeric suffix.

## OQ-MIXEDUDT / OQ-LARGEMIXED — **CLOSED.** Mixed-type UDTs follow the same packing and definition rules as single-type ones. No interaction.

## OQ-TAGSCOPE — **CLOSED.** Program-scope tags size identically to controller-scope tags. Scope affects only where the entry lives.

---

# Add-On Instructions

## OQ-AOIINSTANCE — how an AOI-typed tag sizes

**SOLVED.** Every AOI-typed tag in a real export is a plain named Tag sized
identically to a UDT-typed one. Input, Output and LocalTags are storage; **InOut
parameters are excluded entirely** — an InOut is a reference to the caller's tag, not
separate storage.

That also answers whether a parameter duplicates the referenced tag's memory: **it
does not, because it is never sized.**

Engine error on the real corpus fell from 41.6% to 29.5% to 8.8% as this and the
predefined structures landed.

## OQ-AOIDEF — AOI type-name length

**SOLVED.** `8 × max(0, (len − 8) // 4) − 8`, exact at seven points.

> **The first divisor tried reproduced all seven points and was still wrong**, putting
> one length a whole bucket too high. It was caught only by cross-checking two
> unrelated files that differed solely in AOI type-name length. **Seven points
> agreeing does not pin a bucket boundary.**

## OQ-AOIDEFITEMIZE — the priced cost versus the itemised breakdown

**SOLVED as one itemised form.** The definition cost and its own member breakdown were
two different computations that disagreed on every real AOI. Now one form: a base, 12
per declared member, each member's own data bytes, 24 per 32-bit word the BOOLs
occupy, an 8-aligned name pool, and the type-name term.

Measured on **124 definition-only files** — no instance tag and no internal rungs, so
the definition is the only AOI cost in the file. **70 land exactly, 122 of 124 inside
±8.**

**The residual's shape makes it look like a per-member constant, and it is not** —
worth knowing, because that is exactly the wrong fix to reach for.

**This replaced four separate fitted terms that had each absorbed part of the same
error.** Every one fitted its own sweep exactly. `MEMORY_MODEL.md` records what each
was really measuring, which is the part worth keeping.

**CAPTURE ERRORS: 40 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-LITERALOPERAND — an immediate literal in an operand costs bytes the engine charges at zero

**The measurement.** One rung in one project, edited in Logix Designer, compiled by
Studio, Capacity read twice. Six MAM operand slots changed from a tag reference to
the immediate `99.99`:

    74,224  →  74,248   = +24 over 6 slots = +4.000 per slot, six for six

**The four source tags stay declared AND referenced in both versions**, by four EQU
instructions on the same rung. So this is not a tag being deleted — it is the same
tag population with six slots re-pointed at inline constants.

**The engine charges nothing.** Run on both rung texts it returns 320 bytes either
way — a zero delta against a real 24.

**It is not a new constant.** The CPT model already carries 4 per float literal,
fitted across 12 files. The same 4 now appears in MAM, an unrelated instruction on
an unrelated code path. **One constant appearing independently in two unrelated
places is what a general law looks like**, not a per-instruction quirk. Today
literals are priced only inside CPT expressions, CMP operands and ST statements.

**Exposure across the seventeen**, counting numeric literals in operand slots of
instructions that are not CPT or CMP:

| | count | at 4 bytes |
|---|---:|---:|
| integer literals | 51,265 | 205,060 |
| float literals | 930 | 3,720 |
| **total** | **52,195** | **208,780** |

**12.1% of all 432,850 operand slots**, and about a quarter of the total residual.
Every one of the seventeen carries between 8.8% and 16.2% literal slots, so this is
not one file's quirk. Top carriers: MOV 9,835, EQU 9,089, ADD 5,259, NEQ 3,132,
COP 2,841, JSR 2,631.

**What charging it does**, float held at the measured 4 and integer swept:

| int cost | mean | max | <1% | <2% |
|---:|---:|---:|---:|---:|
| baseline | 1.5951 | 3.6309 | 4/17 | 11/17 |
| 0 | 1.5973 | 3.6198 | 4/17 | 11/17 |
| 2 | **1.5818** | 3.3811 | 4/17 | 12/17 |
| 4 | 1.5885 | 3.1424 | 5/17 | 12/17 |
| 6.5 | 1.5951 | **2.9022** | 5/17 | 12/17 |

**Read the max, not the mean.**

- **The max moves, and nothing else has.** 3.6309% → 2.9022%. For scale, the
  cheating ceiling fit only reached 2.5919%. A single mechanistic term gets most of
  that way without fitting anything per-category.
- **The mean barely moves** because the term can only ADD bytes and seven files
  already over-predict. All six worst files improve; all seven over-predictors get
  worse. That is a reason to be careful about the rate, **not a reason to dismiss the
  mechanism** — the mechanism is measured, and the over-prediction in those seven
  files is a separate defect.
- **Mean-optimal is 2, max-optimal is 6.5.** They disagree, which is positive
  evidence that **a single flat rate is the wrong shape** and the cost is
  type-dependent.

**CAPTURE ERRORS: 0 row(s).** The whole BOOL arm, `litop_bool_*`, previously
carried 4. Every rung of all four had failed with *"Invalid number of arguments for
instruction"*, 1,000 errors on 1,000 rungs, so the ladder never compiled and all
four read an identical 20,028. The arm measured nothing, the cause is found and
fixed, and **the four capture rows are cleared** — the files they measured no
longer exist in that shape. Diagnosis below. The regenerated files await capture.

---


**The BOOL arm's recapture (`litop_bool_*_n01000_r2`) answered a different question.**
Those files pass literals and tags into a Required AOI Input, and the difference is in
the AOI call, not in any native operand: an Input argument that is anything but the
literal 0 or 1 costs 28 bytes, not 16 — tag and `12345` alike, BOOL and DINT alike.
Every earlier AOI calibration passed `0` to its inputs. Wired as
`aoi_call_site.input_ref_extra_bytes = 12`; real programs pass a tag to ~90% of their
AOI inputs. See `MEMORY_MODEL.md`, AOI call site.
## The batch answered it. The law is per-type, and it is mostly zero.

**Arm G first, as the plan required.** The bench rung rebuilt at 1,000 rungs:

    litop_mam_lit_n01000   419,456      six REAL literal slots
    litop_mam_tag_n01000   395,456      the same rung, all tags
                          --------
                           +24,000  =  +24.000 per rung  =  +4.000 per slot

**Six for six, identical to the bench.** The pipeline reproduces a hand measurement
at 1,000× scale, so the rest of the batch can be believed.

**Arm A settles the shape, and it is not what either hypothesis predicted.** One
literal operand slot, literal file minus tag file, 1,000 rungs each:

| operand type | per slot | the engine today |
|---|---:|---|
| DINT | **0** | 0 — correct |
| LINT | **0** | 0 — correct |
| REAL | **+4** | 0 — under by 4 |
| INT | **−52** | over by 52 |
| SINT | **−40** | over by 40 |

**An integer literal is free.** Not cheap — free, at both DINT and LINT, to the
byte. That kills the exposure this question was ranked on: 51,265 of the 52,195
unpriced slots are integer literals, and they cost nothing. The projected max
3.63% → 2.90% was an artefact of charging 4 for slots that are worth 0.

**A narrow-integer literal is CHEAPER than a tag, and that is an engine defect, not
a literal cost.** A SINT or INT *tag* operand drags in the widening block the model
already charges; a literal needs no widening because it is already the right width
inline. The engine charges the widening either way, so it over-predicts
`litop_type_int_lit_n01000` by **+21.82%** and `litop_type_sint_lit_n01000` by
**+18.67%** while both *tag* files land at exactly 0.00%. Those two rows are the
largest single-file errors in the batch and they are ours, not Rockwell's.

**Value and distinctness are free.** Arm D: `0`, `1` and `2` all identical. Arm C:
all-distinct, all-same and two-repeated all identical. So there is no
per-distinct-value term and no folding of 0/1 — the competing law that a previous
question died on is dead here too, for a better reason.

**The written FORM of a float costs, and it is unpriced.** Arm E: `floatform`
against `small`, same slot count, **+76,000 over 1,000 rungs = +76 per rung**,
engine delta **−50.57%**. That is an order of magnitude above the +4 for a REAL
literal and is a different mechanism — it is about how the constant is written, not
that it exists. One pair, so the rate is not the finding; the existence is.

**A separate finding fell out of arm G.** Both MAM files under-predict — the
all-tag baseline by **−40,000 over 1,000 rungs, −40 per rung**, before any literal
is involved. That is the MAM instruction weight being short, not a literal term,
and `unreconciled.py` flags the pair. It is the larger of the two numbers in that
arm and it belongs to motion sizing, not here.

### What this changes

| | before the batch | after |
|---|---|---|
| mechanism | "a literal costs bytes" | only REAL (+4) and float-form (+76) cost; integer literals are free |
| exposure | 52,195 slots, 208,780 bytes | 930 float slots, 3,720 bytes |
| expected movement | max 3.63% → 2.90% | **approximately none** |

**So this question drops out of first place.** It was ranked on an exposure that the
measurement has removed. What survives is smaller and sharper: a +4 REAL-literal
term, a +76 float-form term needing a second point, and the INT/SINT widening
defect, which is the only one of the three that moves a real number.

### The BOOL arm was a generator bug. Resolved: a call site passes exactly the Required parameters

All four `litop_bool_*` files emitted `LitSensor(Sensor,RawIn,NormOpen,TimeHigh);`
against an AOI whose three parameters were `Required="false" Visible="true"`.
Studio rejected every rung of all four, **including the all-tag control**, so it
was about argument COUNT, not literals.

The rule is `args == Required` exactly, and `Visible="true"` alone creates no call
slot. Across the real exports there are **917 AOI call sites and the argument count
equals the Required count at every one**, while those same exports declare 120
`Required="false" Visible="true"` parameters — so the unanimity is not for want of
optional parameters to pass. One real AOI has three Required and four Visible-only
parameters and is called with three arguments everywhere. Required is not even a
prefix of the parameter list (13 of 48 real definitions interleave), so the
unpassed ones are not merely trailing.

**The "legal arity is a range" reading came from counting conversions, not builds.**
Two generated files wired optional parameters and were counted as evidence because
they converted and returned a capacity number. Conversion performs no ladder
verification, and `litop_bool_*` proves a capacity number is returned even when
every rung errors. Their apparent cost over the definition-only baseline was tag
storage for the argument tags, not compiled rungs. Both files are deleted, and
`gen_aoi_required_visible.py` no longer emits that shape.

Wired:

- `lint.py`'s `aoi_call_arg_count_mismatch` now requires exact equality with the
  Required count. It previously allowed the range, which is why it passed the
  1,000-rung family that failed to build.
- `gen_literaloperand.py` arm F declares the three parameters `Required="true"`;
  the four files are regenerated and lint clean.
- `AOI_KNOWLEDGE_MAP.md` carries the rule and its evidence.
- The four `litop_bool_*` capture rows are **cleared**, not reused. They measured a
  file that no longer exists in that shape.

No probe file is needed. The four-file Required-count probe proposed here is
withdrawn — the real corpus already answers it at 917 call sites.

**Still open in this arm:** the BOOL literal cost itself is unmeasured. The
regenerated files are awaiting capture.

---


---


**Why this measurement is trustworthy where the strip ladder was not:** it was made
by editing a project in Logix Designer and letting Studio compile it, not by
rewriting exported XML. That is the path the read-only rule explicitly leaves open.

### Closed: every surviving term is under the noise floor

**BOUNDED.** The last live item was the INT/SINT literal over-charge, held open until
it could be counted on the real programs. Counted on all eighteen real exports now
available: the measured shape, `MOV(<integer literal>, <INT or SINT tag>)`, occurs
**37 times in total — 23 INT, 14 SINT — for 1,756 bytes of over-charge across
eighteen programs**, about 100 bytes a program and 0.002% of one. The worst single
program carries 784 bytes. Wiring it would move nothing a user could see, so it is
closed without wiring, which is the noise-floor rule doing its job.

What remains is recorded, not pending:

| term | per | real exposure | status |
|---|---|---|---|
| integer literal (DINT, LINT) | slot | 51,265 slots | **free, measured** |
| REAL literal | slot | 930 slots, 3,720 bytes | +4, below the floor |
| float literal FORM | rung | one pair only | +76, below the floor, needs a second point before any rate is believed |
| INT / SINT literal into `MOV` | slot | 37 slots, 1,756 bytes | engine −52 / −40 high, below the floor |
| BOOL literal into an AOI call | slot | 128 real call sites | regenerated `litop_bool_*` files lint clean; not worth a capture slot on this exposure |

The projected max 3.63% → 2.90% that ranked this question first was an artefact of
charging 4 bytes to integer literals that cost nothing. **The hypothesis that
unpriced literal content carries the real residual is refuted.**


## OQ-TASKNAMEROUND — a task name rounds up where the identifier term rounds down

**BOUNDED.** `task_extra` is exact at 2, 3 and 6 tasks — `taskoverhead_n02tasks`,
`_n03tasks` and all five `identnamelen_task_c*` files — and the task/program shell is
KNOWN on that evidence. The one miss, `taskoverhead_n04tasks` at **+24**, is not
`task_extra`: its three extra task names are 13 characters, the only
non-multiple-of-8 task name ever captured. The identifier term rounds 13 down to 8;
the file reads as if a task name rounds up to 16. Three names × 8 = 24, exactly.

Rounding task names up fits all six task-name points (4 → 8, 8 → 8, 13 → 16, 16, 32,
40), and it would retire the `task_min_bytes` special case, which exists only to make
a round-down law read 8 at length 4. It is not wired: at most 8 bytes per task, and a
real program has a handful of tasks, so it is under the noise floor. Program and
routine names are **not** covered by this — every captured program or routine name
length is a multiple of 8 or sits inside the per-routine constant, so which way they
round at other lengths is untested.

## OQ-AOIDEFSHAPE — the AOI definition's residual

**SOLVED for the 4-byte half, BOUNDED for the 8-byte half.** `aoi_definition` is now
**KNOWN.**

**The 4-byte half: the definition is 8-byte aligned.** The entry that used to stand
here reported 0 on 70 files and +8 on 35. Re-run against the live engine, the same
125-file instrument had drifted to four values — 0 on 8, **+4 on 53**, +8 on 23, +12
on 21 — which is the "re-run the census after any shared change" failure mode caught
late. The split is exactly the unaligned sum's value mod 8: every file the formula put
at 4 mod 8 read 4 bytes high, every file at 0 mod 8 read as predicted.

Aligning `(sum + 1)` up to 8 and removing the 1 again — the same project-wide 1-byte
offset the array-member terms carry — fixes it:

| | before | after |
|---|---:|---:|
| instrument files exactly 0 | 8 | **68** |
| inside the ±8 noise floor | 94 / 125 | **117 / 125** |
| mean \|residual\| | 6.99 B | **4.48 B** |
| every clean AOI-bearing capture, exactly 0 | 38 | **201** |
| every clean AOI-bearing capture, inside ±8 | 295 | **506** |
| non-AOI captures moved | — | **0** |

16- and 32-byte alignment were tested and are strictly worse. It is the same mechanism
and constant as OQ-AOIBOOLPACK-PAIRING below, found independently on the instance
side — the cross-check that this is real rather than fitted.

**The 8-byte half: bounded, not solved.** 47 instrument files still read +8. No single
feature separates them from the 68 at zero: AOI name length leans toward it at 14–16
characters — the bucket boundary the name-length sweep never sampled — and so does
controller name length at 6–7 mod 8, but neither splits the groups cleanly. It is
**exactly the ±8 single-measurement noise floor**, which the project treats as
agreement, and it is not worth a capture slot.

**The eight outliers** are named shapes: a MOTION_INSTRUCTION local (+48), BOOL-array
locals (+16, deliberately unpriced — OQ-AOIARRAYLOCALTAG), and one three-deep nesting
(−16). None is common enough in the real set to clear the noise-floor rule.

**Why KNOWN.** Measured alone on 125 def-only captures, with every residual inside the
noise floor except those named shapes — the project's written rule for a known
constant. The name-length term meets the same rule on its own (seven lengths, 7/7
exact; the unsampled boundary can be wrong by at most one 8-byte bucket). Pinned by a
test.

## OQ-AOIREALSHAPE — does the AOI model hold at real population shape

**BOUNDED. The per-definition cost is confirmed at real shape; the per-member cost is
1.8 bytes high.**

`gen_realshape_aoi.py` built 15 files reproducing a real export's AOI population —
19 definitions, 453 parameters, 280 locals, 349 internal rungs — and ladders that move
one kind of content at a time. All 15 captured clean. **They were never differenced
until the final review**, which is the backlog failure the capture checklist warns
about.

| ladder | what moves | actual per unit | predicted per unit |
|---|---|---:|---:|
| `mbshape_defs_n{05,19,40}` | same members over 5 → 40 definitions | **1,231 / definition** | 1,233 |
| `mbshape_params_{05,10,20}` | 229 → 906 parameters | **20.3 / parameter** | 22.2 |
| `mbshape_locals_{05,10,20}` | 137 → 560 locals | **20.4 / local** | 22.2 |
| `mbshape_rungs_{05,10,20}` | internal rungs | flat — exact | flat |
| `mbshape_axis_k{0,3}` | three AXIS_CIP_DRIVE parameters | +8 difference | — |

- **The per-definition cost is right at real scale.** The generator's key
  discriminator came back per-member, not per-definition.
- **The per-member cost is 1.8 bytes high** on BOOL-heavy real mixes (about half the
  members are BOOL). On the real export this population was copied from — 733
  members in a 923 KB program — that is about 1.3 KB, **0.14%**, under the
  noise-floor rule. That export now over-predicts by 1.17% (10.9 KB), so this
  over-charge is roughly an eighth of its residual.
  Instance and definition charges move together in these ladders, so the 1.8 cannot be
  split between them without a def-only twin; not worth a slot.
- **The axis-parameter charge is right.** The generator flagged 22,656 bytes per axis
  parameter as "very likely wrong". Three of them move the file by 8 bytes against the
  prediction.
- **Internal rungs are exact** at real count.

**The control file does not reproduce the real export's under-prediction.**
`mbshape_asbuilt` over-predicts by 1,448 bytes (2.3%), where the real export it copies
was under-predicted by about 7% when this family was built. So that under-prediction
did not live in its AOI population — the hypothesis the family was built to test is
refuted. (Other fixes have since moved that export to a 1.17% over-prediction.)

## OQ-AOIBOOLPACK-PAIRING — instance-array packing

**SOLVED, after two wrong readings that are both instructive.**

The answer: **the whole instance-array block is padded to an 8-byte boundary**,
`8 × ceil(n × per_instance / 8)`. The extra 4 bytes appear exactly when
`per_instance ≡ 4 (mod 8)` and never otherwise. **48 of 48 captured families agree
with zero exceptions**, over 17 distinct per-instance sizes. Same mechanism and same
constant as the predefined array structures' element-block padding, which is the
independent cross-check.

Also found: the engine counted packed words as `ceil(bool_count / 32)`. **The real
count is `ceil((bool_count + 2) / 32)`** — EnableIn and EnableOut occupy two bits in
the same words, and `bool_count` excludes them because they are not declared members.

**Two refuted readings, recorded so they are not re-derived:**

- **`124 − 4 × bool_member_count`.** Zero residual at nine points from 0 to 30 BOOL
  members — about as clean a fit as this project has produced. **Every point came from
  AOIs with the same total member count**, so it could not distinguish a per-BOOL
  effect from one depending on total members. Composition only moved the per-instance
  size; the residue mod 8 was doing all the work.
- **A per-family fixed offset tied to which boundary the packed BOOLs cross**, then
  **a two-variable surface in (bool_count, atomic_count).** Both wrong.

## OQ-AOIARRAYDIMENSION — why an array-parameter file would not import

**SOLVED, and the cause was not a formatting bug.** An array-dimensioned atomic
Input or Output parameter **is not a legal Logix construct at all.** Only
`Usage="InOut"` permits an array parameter.

Two prior fixes — forcing the Required/Visible flags, then building a real array
DefaultData body — were **chasing a formatting bug that never existed.** The real
corpus already showed it: every real array parameter carries both `Dimensions` and
`InOut`, which is now understood as the only possible combination rather than a
coincidence.

The same rule generalises: **an Input or Output parameter is passed by value and
accepts only an atomic type.** Any structure must be InOut.

## OQ-AOIARRAYLOCALTAG — array LocalTag data space

**SOLVED for the main term.** An array-dimensioned declared member costs its own data
space, and the array's bytes **replace** the scalar element size a non-array member
would pay rather than stacking on it.

Computed through the array-size path rather than `element × dimension`, because the
predefined array structures have their own shape and no scalar element size — going
the naive route raised an error on the first real file it met.

**Three residuals recorded rather than fitted:** BOOL arrays measure neither the
packed size nor a two-word rounding and stay deliberately unpriced; an 8-byte discount
applies per array member after the first; and one dimension lands exactly one element
off the line through its neighbours.

## OQ-AOIINTERNALLOGIC — do an AOI's own routines cost anything

**SOLVED.** They were priced at zero. All of an AOI's internal routines are aggregated
into one pseudo-routine — **per-routine count does not matter, only total content** —
and weighted with the ordinary instruction table, with the shell not charged because
the definition's base covers it. Cut maximum residual on the isolation sweep from
12.02% to 0.55%.

**CAPTURE ERRORS: 5 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-AOIORPHAN — does an uninstantiated AOI definition cost memory

**CLOSED NEGATIVE.** A minimal-pair capture confirms the existing no-extra rule is
correct rather than merely assumed — 8-byte residual on the unreferenced file, 0.04%.

## OQ-AOISTRUCT — what an AOI costs as a function of its structure

**SOLVED in part, and it is the entry that matters most for other people's code.**

The definition form prices a finite list of properties, and the generated corpus
barely exercises several that real AOIs have in quantity: member name length (mean
12.1 characters), member descriptions (803 of 2,120 real members have one, the corpus
generated none), InOut parameters, predefined-struct members (hundreds of real TIMER
members, none generated), array dimensions, counts far past the fitted range, and
extra internal routines.

**Why it matters more than the byte counts suggest:** a correction fitted against the
AOIs that recur across the real projects — the byte-identical shared ones — **would
score well on the real set and be worthless on someone else's.**

**So: never fit anything to a specific AOI name.** Cost models must be functions of
structure. See `AOI_KNOWLEDGE_MAP.md`.

## OQ-AOIGEN — **CLOSED.** AOI cost generalises across shapes once the itemised form replaced the per-type rates. The apparent non-additivity was the name-pool error surfacing as a composition effect.

## OQ-AOIINTERNAL- — a truncated cross-reference, not a question.

---

# Compiled logic

## OQ-LBLJMP / OQ-LBLJMP-STALE — separating LBL from JMP

**SOLVED, and it is KNOWN at any ratio.** The 1:1 pair is an exact linear fit at 120
per pair across five rung counts. **A 1:1 sweep alone cannot split the pair, however
many counts it covers.** Two further sweeps did: LBL-only rungs isolate LBL+NOP at 80,
so LBL is 64; a fixed-LBL varying-JMP sweep isolates JMP at 40. The cross-check closes
exactly — 64 + 16 + 40 = 120.

**Three independent captures agreeing, with each instruction isolated from the other**,
is why this is KNOWN and valid for any ratio.

An earlier figure of 104 was a miscalculation, not a measurement error — the raw data
was always 120.

## OQ-BRANCHDEPTH — what a branch costs

**SOLVED, with a mechanism rather than a curve fit.** A branch compiles to real
BST/NXB/BND instructions — one BST, one NXB per extra leg, one BND, so
`leg_count + 1` per bracket group — and each costs a flat **4 bytes**. Nested branches
recurse.

Verified exact against all 17 captured points. **The same 4-byte rate explains two
independently built datasets**, not two separate fits.

The bracket counter does a real matching scan, distinguishing a branch-opening `[`
from an array index by the preceding character and tracking paren depth so a
multi-argument call inside a leg is not miscounted as extra legs.

Stays FITTED: tested at one rung count and one tag shape.

## OQ-SERIESOUTPUT — a rung with more than one output in series

**SOLVED as a law, with its competing candidate killed.** `−12 × (outputs − 1)`,
measured at 2, 3 and 4 outputs.

**The ratio hypothesis is dead**, and so is the repetition candidate — a one-rung file
pays the full discount, so the cost cannot depend on repetition, and a later packing
sweep re-measured the law at four new points at exactly −12.000 with every file
distinct, which kills per-distinct-rung too.

## OQ-VERIFINSTR — instruction weights measured but never confirmed at scale

**SOLVED for the zero-operand half.** MCR, TND, UID and UIE each land **exactly at all
five counts from 10 to 5,000 rungs** — 20 of 20 rows, zero residual — so those weights
are confirmed at three orders of magnitude and no longer need a caveat.

The non-exact rows in that family were all the paired shape and belonged to
OQ-SERIESOUTPUT, which they sharpened considerably.

## OQ-INSTRFIRSTPASS / -X10 / -FLATOFFSET — first-pass instruction coverage

**SOLVED, 34 of 36 weights confirmed and wired.** SCP, FBC and PID were the gaps — SCP
had no second real example, FBC and PID no real examples at all. **Closed as out of
scope rather than left open awaiting data that is not coming.**

A flat +12-byte gap across all 64 clean files, about 0.06% of file total, narrowed to
an interaction effect and **not worth reopening the question over.**

## OQ-INSTRUCTIONSCOPE — **CLOSED.** CTD and several others are deliberately untested: zero real usage. Coverage is measured against real usage, not against the instruction set.

## OQ-MAHMSO — **SOLVED.** 60 per rung each, identical real numbers, on the two-operand `(Axis, MotionInstruction)` shape which is **theirs and not a general motion shape.**

## OQ-MAMFAMILY-BUILDFAIL / OQ-CROUT-MAPC-BUILDFAIL — motion build failures

**SOLVED, and one was not a bug at all.**

**MAM, MAJ, MAS and MRP** failed because they were built on MAH and MSO's two-operand
shape. Each needs its own full parameter list — real operand counts 20, 17, 9 and 5.
Fixed by position-for-position transplant from real examples.

**MAPC** needed two **distinct** axis tags — an axis cannot cam to itself. The
type constraint is looser than assumed: any two axis types work, and a
CIP-Drive/Virtual pairing is not required.

**CROUT is not a generator bug.** It is a Safety instruction requiring a safety CPU.
Reclassified OUT OF SCOPE alongside DCS — there is nothing to fix on a standard
controller.

**CAPTURE ERRORS: 1 row(s)** — `instrfirst_mapc_x10`, the original MAPC build with
both generator bugs, 20 errors. Cause known and fixed: `instrfirst_mapc_v2` and
`_v2_x10` captured with zero errors and MAPC is wired EXACT from them. No re-trigger.

## OQ-BTD — **SOLVED**, along with COP, CPS, FLL and SIZE. All five shared one cause: an array-typed operand emitted without its `[index]`. **Such a file converts cleanly and never compiles at scale**, which is why every one returned an identical byte count regardless of rung count.

## OQ-EMPTYROUTINE — **SOLVED.** A routine's fixed base is 4,816, confirmed identical across 42 instructions; 5,096 for a routine containing a JSR.

## OQ-TASKOVERHEAD — per-task cost

**MEASURED, deliberately not wired.** A clean, exactly −1,472 per extra task. Wiring
it needs a parser change to distinguish per-task and per-program overhead from
per-routine-in-the-same-program, which does not exist. **Recorded rather than
rushed.**

## OQ-SHELLSCALE — task, program and routine shell scaling

**SOLVED, and the answer reversed the question's own conclusion.** The entry predicted
the per-program and per-routine constants were far too **small** — a claimed 10× and 2×
extrapolation failure. The isolation batch says the opposite: **both were slightly too
LARGE, by exactly 8 bytes each.** The routine sweep measures exactly 264.000 per
routine across all seven steps.

**The reversal is the useful part.** An extrapolation inferred from whole-program
residuals pointed the wrong way by an order of magnitude.

## OQ-SAFETYSCOPE-SIZING — safety shells

**SOLVED.** Safety tasks and programs are a separate memory pool. They are excluded
from the ordinary shell aggregate and charged a flat per-file constant instead,
replacing an over-charge. Verified exact against every real safety-processor row at
the lower firmwares, with a known small residual at the higher ones that belongs to the
firmware content gap.

## OQ-XPROGREF — **CLOSED.** A shared alias across programs costs about −16 per rung per additional program. An earlier large negative gap no longer exists against the current engine; the real data had been sitting unreconciled.

## OQ-INDIRECT — indirect addressing

**SOLVED.** A direct array index costs nothing beyond existing indexed-tag handling. A
**tag-driven** index costs roughly 84 per rung and an **arithmetic-offset** tag-driven
index roughly 108. The direct-index case having no cost is why this looked like a
non-effect at first.

## OQ-OPERANDTYPE — does operand data type change instruction cost

**SOLVED, and it bounds every "exact" claim in the project.** It does, substantially,
for 14 instructions. SINT and INT cost +88 to +164 more per rung; REAL costs +16 to
+56 more for some and less for LIM; STRING costs +52 more for EQU and NEQ. **LINT
behaves identically to DINT.**

**Every zero-residual instruction weight is proven only for DINT, LINT and REAL
operands.** A program doing heavy SINT or INT math sizes less accurately than the
coverage table implies.

## OQ-RUNGSHAPE — see `OPEN_QUESTIONS.md`. Partially answered: arrangement is byte-exact at every leg count, so the corpus's branch coverage gap is a fact about the corpus and not an error. The per-rung term remains confounded.

---

# Expressions and Structured Text

## OQ-CMPCPTLAYOUT — CPT and CMP expression cost

**SOLVED across four threads, and one of them corrected a rate that had been applied
universally.**

**CPT is priced per call from its own expression's operator tokens**, not a flat rung
weight. A single flat weight was wrong as a general constant — it was one complex
expression's cost, and applied to a simpler expression it over-predicted one file by
over 300,000 bytes. **The fix was an architecture change, not a constant edit.**

**The extra-operand rate is per tier.** The wired 24 came from a sweep using one
operator throughout, so it was only ever a **tier-1** rate while being charged for
every uniform-tier expression. Uniform tier-2 measures 16 more per operator beyond the
first, with one tier-2 operator already exact to pin the intercept.

**CMP shares the same law.** It was priced as a flat weight plus two boolean
surcharges with **no expression model at all**, so a CMP whose operands are arithmetic
paid nothing for the arithmetic. **No separate CMP fit was needed** — the tier table
fitted on CPT lands on CMP's measured residuals unchanged, which is the evidence they
share one law. Three shapes went from −36, −36 and −100 to exactly 0.

Comparison operators and the `&&` / `||` connectives are deliberately not tokenised as
arithmetic: the connective is already priced, and double-charging would break every
bare compound CMP, all of which measure exact.

## OQ-CPTARRANGE — does operator arrangement change CPT cost

**CLOSED NEGATIVE, with one exception that is a rule rather than noise.** Four arms
sweep operand counts 3 to 9 with the multiplications in completely different places,
and 26 of 28 rows land on the **identical** residual, with the slopes agreeing exactly
too. **The arrangement-blind expression model is right.**

Reading those rows also turned up a +348 nobody had seen, and a leading-tier-1-run
term now wired at 4 and 2.

## OQ-CPTREALDEST — REAL-destination CPT

**SOLVED.** A CPT writing to a REAL destination is evaluated in floating point and
priced by a separate model: the integer operator-tier costs do not apply, and every
non-float operand carries a conversion cost. Exact on every captured row.

Coverage gaps recorded rather than hidden: only operator counts 1, 2 and 5 are
covered, and BOOL falls through uncharged because no real example exists to confirm it
converts the same way.

**CAPTURE ERRORS: 1 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the row outlives it.

## OQ-CPTNARROW — how SINT/INT widening scales

**SOLVED as a mechanism, BOUNDED as a constant.** Integers use a behind-the-scenes
conversion to DINT. That resolved two things at once: **LINT operands cost nothing**
(already 64-bit, no widening) and SINT/INT operands cost +256 per rung on the
three-operator all-REAL control.

**How that 256 splits is not determined** — there is exactly one data point. This is
the defect that makes CPT read as the worst measured accuracy of any instruction.

## OQ-CPTTYPEMISMATCH — destination and operands disagreeing in type

**MEASURED, deliberately not fitted.** Two type-mismatch costs found on a clean 2×2,
and not wired because the real exposure is three of several hundred occurrences.
**Below the noise floor, recorded so the measurement is not lost.**

## OQ-STSIZING — Structured Text sizing

**SOLVED, from a starting point of completely unmodelled.** Every ST routine
contributed exactly zero.

**An instruction inside ST costs exactly what it costs in a rung.** Against matching
RLL captures, ST is a flat **+432** — the ST routine shell — and nothing else, across
five independent pairs. **The entire weight table transfers unchanged.**

**ST comments are free.** That needed testing rather than assuming: an RLL rung comment
is a separate element, while an ST comment sits inside the compiled source text, so the
RLL result does not transfer.

Control flow is priced per construct, and **a loop-heavy routine is not priced like a
branch-heavy one** — FOR costs several times what IF does.

## OQ-STEXPR — ST assignment cost

**SOLVED as one law replacing a five-entry table** whose fallback over-predicted a
one-operator assignment roughly threefold.

**An ST assignment is not priced like the equivalent CPT.** That was the working
hypothesis, and a mirror pair differing by exactly the routine shell looked
conclusive — routing every assignment through the CPT model on that basis
over-predicted one file by **+132%**.

The law: a base by operator count and destination type, plus each operator's CPT tier
premium above tier 1, plus a conversion term per integer-typed **named** source read
into a REAL destination. **Integer literals do not pay the conversion term** — that is
what fixes the rate.

**All three of the old table's non-trivial entries come back from the law**, which is
what says it was mis-parameterised rather than incomplete. Each had been measured on a
different expression and then keyed on operator count alone.

Both rows step once at two operators and are dead linear after — **the step is the
mechanism**: a single-operator assignment compiles to one instruction and a compound
one reaches for expression evaluation.

The ST family went from 8.33% to **0.0091%** mean absolute error, 60 of 69 rows
byte-exact.

**CAPTURE ERRORS: 1 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the row outlives it.

## OQ-STEXPR-OPERATOR — the per-operator premiums

**SOLVED.** All four outstanding assumptions measured.

**The one-operator premium is not a premium — it is a lookup per operator class**:
additive, multiplicative, bitwise and exponent each have their own value. **The
premium on the REAL row does not scale up, it vanishes.** AND and XOR are now measured
at tier 1, which the CPT table did not cover at all.

> It was blocked for a period with every number measured and none wirable, because
> each operator had exactly two points and the fit needed two parameters. **Recording
> that state, rather than fitting it anyway, is why the eventual numbers are trusted.**

## OQ-STCOMMENT — **CLOSED with OQ-STSIZING.** ST comments are free.

## OQ-CPT / OQ-CMP — early identifiers, superseded by OQ-CMPCPTLAYOUT.

---

# JSR, subroutines and program structure

## OQ-JSRPARAMCOST — JSR parameter cost

**SOLVED.** The flat per-rung weight covers the base call only. The per-parameter cost
decomposes as a per-call-site marginal rate plus a one-time declaration charged **once
per distinct target, never per call site.**

`n` is read straight off each call's own second argument — **the declared parameter
count Studio itself writes there** — rather than by counting arguments.

**A JSR target does not charge its own routine base**; that stays folded into the
caller's constant. Charging it again over-counted every JSR-using program by roughly
4,832 bytes.

**But the target's own instruction content is not skipped.** A target with substantial
content genuinely costs memory — maximum 13.37% residual before this was fixed, 4.75%
after.

**CAPTURE ERRORS: 4 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-JSRSCALE / OQ-JSRSHARED — the composite surcharge

**SOLVED, and it was the project's largest error source.** A file-wide cap on the
AOI/JSR content surcharge was fitted against the synthetic composites and behaved
completely differently on a real program — **mild trimming on the files it was fitted
on, total annihilation at real scale**, suppressing over a million bytes on one real
file.

The cause: **real programs carry 16× to 54× more JSR-target instructions than any
synthetic composite.** With the cap the model ignored target content almost entirely,
which silently undid the finding that target content is not free.

Refitting on real programs cut it roughly fivefold. **Neither extreme was right** —
capped under-predicted by over 12%, fully uncapped over-predicted by 6.5%.

## OQ-JSRFOLD — how a target's cost folds in

**SOLVED.** A JSR and its target are over-charged at low counts and under-charged per
unit, and the shape pointed at how the fold works. Measured across four counts of N
JSR rungs against N target routines.

**CAPTURE ERRORS: 2 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-IDENTNAMELEN — do object names cost bytes

**SOLVED as one shared law.** `0` up to 4 characters, `2 × (len − 4)` from 4 to 8, and
**exactly `len` above 8 with no bucketing** — which distinguishes it from the AOI
type-name and alias-tag costs, both of which bucket.

Two independent sweeps of ten identifiers each, at five name lengths up to Rockwell's
real 40-character cap, return the identical per-identifier cost. Program name rows
went from a large spread to exactly 0, and the JSR rows collapsed onto a uniform
under-charge that turned out to be a separate per-target term.

Stays FITTED: the middle interval is an interpolation between two anchors with no data
of its own.

## OQ-DEFSCALE — definition and instance-count scaling

**SOLVED for the terms that could be separated.** Four exact linear laws came out of
30 files with zero import errors. One term wired exactly; another **measured exactly
and blocked by a confound that runs through the whole corpus**, and recorded as such
rather than wired.

This is the batch that produced the standalone UDT tag slot rule, from the one place
two families disagreed.

## OQ-LADDERBASE — two capture sessions disagreeing

**BOUNDED.** Two capture sessions on one real export disagree by 18–25 KB. It needs
three existing files recaptured **in one session**, which is a capture-discipline
matter rather than a modelling one. **Recorded so a future disagreement is recognised
rather than investigated from scratch.**

---

# Modules, I/O and platform

## OQ-MODULEIO — per-catalog module overhead

**SOLVED in large part.** 126 real module captures were sitting unreconciled; 51
catalogs now carry a real per-catalog overhead and the exact-match rate on real data
went from 1 in 126 to 54 in 126.

**CAPTURE ERRORS: 9 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-MODULESTRUCTURAL — the shape module cost should have

**SOLVED for one profile, and it reframed the target.** A per-catalog table **can only
ever cover catalogs personally captured.** A real customer file will contain catalogs
never seen, and those fall back to one flat default that is badly wrong for whole
families.

**A generic Ethernet connection's data costs 4× its declared bytes**, with each
direction rounded to a word, the word counts summed, and 16 per word less 8 when the
total is odd. Exact on all 14 captured points.

**The two directions are interchangeable** — only the sum of the word counts matters.
**No real instance could show this**, because real devices vary both directions at
once.

That profile is 25% of all non-CPU modules in the real programs and had no per-catalog
entry at all.

**Deliberately scoped to that profile.** The rack sweeps point the same way, so a 4×
connection cost may well be general — but applying it to every captured module row on
one profile's evidence is the move this project has had to undo before.

Also settled: **the file is the final decision on module sizing.** A module costs its
per-catalog overhead plus the size the L5X states, and every module gets sized. Several
catalogs are configurable, so **two instances of the same catalog are different
devices.**

## OQ-MODULEMARGINAL — does the Nth copy cost the same as the first

**SOLVED for ten catalogs, and it found a compensating error.** From the second module
of a catalog on, overhead drops to a second per-catalog rate — not a constant and not a
ratio. Measured at four counts with zero variance, and **per catalog rather than per
file**: settled by mixture files in which reversing module order leaves the total
byte-identical, while a per-file reading requires it to shift.

**The six 2198 drive catalogs cost the same as each other** — 4,624 for the first and
3,640 for each additional — and the per-catalog distinction previously believed to
exist between them was itself an artifact of guessing.

**The old guesses ran 6,384 bytes high per drive, and removing them unmasked a
systematic under-prediction on every real program** that the over-charge had been
cancelling. One real program with 12 such drives moved by exactly 12 × 6,384. **A
compensating error hides a real one.**

**Seven measured rates are deliberately excluded**, each for a stated reason: the
generic Ethernet placeholder's rate is the cost of a second identical clone, which no
real program has; and the six drives were measured on bare modules with no axis tag,
which no real program contains. Those two families were 95% of what the full table
would have removed.

The occurrence-count scope — project-wide or restarting under each parent — is
**undetermined by data** and cannot change a real-file number until a real file splits
a catalog across racks.

**CAPTURE ERRORS: 6 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-POINTIOCONN — POINT I/O connection format

**MEASURED.** A card's cost depends on its connection format, which the model does not
represent, and the flat rate charged instead is **wrong in both directions.** Three
real captures with identical content otherwise, where the non-module part of the
prediction is byte-identical across all three — so the difference is entirely the
connection format.

## OQ-193ECMETR — **BOUNDED.** A real "Child module incompatible with parent module" error on two catalogs, genuinely undiagnosed. Needs the raw Studio error line; the catalogs are excluded from the generators meanwhile.

## OQ-LEGACYNETOVERHEAD — ControlNet and legacy networks

**OUT OF SCOPE, deliberately.** ControlNet, DeviceNet, DH+, DH-485 and Remote I/O
bridges are excluded from sizing entirely — the same treatment given to rack-aliased
modules.

> This was briefly reopened as a data gap and a flat overhead wired for a ControlNet
> bridge, then reverted the same day. **A real capture existing is not the same as the
> shape being in scope.**

## OQ-2198ERS3 — **SOLVED with OQ-MODULEMARGINAL**, and see `SAMPLE_GENERATION.md` for the separate finding that ConfigSize is a function of the module's Major revision rather than its catalog.

## OQ-BASELINE — the empty-project baseline

**SOLVED.** A fixed, zero-variance cost confirmed across 200+ independent data points
spanning wildly different test categories, all landing on the same number once every
other sizeable element is accounted for. **Those points are independent in test
content, not in processor or firmware.**

## OQ-BASELINE-PROCFW — does the baseline vary by processor and firmware

**SOLVED for the active scope.** It does. The active platform is **exact** at every
firmware, and the one non-zero residual there is **not a baseline error** — it is a
firmware-dependent **content** gap where real MainRoutine content drops to zero on
later hardware while the engine still predicts a small amount.

Per-family corrections for the other active platform took baseline rows from 68 of 140
exact to 118 of 140.

> **One ladder cannot serve every processor.** Each processor's residual is constant
> within a firmware band and the bands differ by family. On a bare-baseline file the
> residual *is* the baseline error by definition, so this reads a lookup table off its
> own measurement rather than fitting free parameters.

> **A correction that looked right moved 787 previously-exact captures to wrong.** It
> was caught only by re-running the residual census immediately after wiring. Pattern
> order in that table is also load-bearing, and a test asserts it.

## OQ-BLOCKBYTE — is a block a byte

**CLOSED, and it was correctly flagged as foundational.** Studio labels its capacity
readout "bytes" for some processors and "blocks" for others, while this project treats
the figure as one uniform unit. **If a block were not numerically a byte, every
constant fitted against the dominant baseline would need rescaling.**

**A block is a byte on the active platform.** The two-file test — a single
120,000-element DINT array and nothing else, so 480,000 bytes of the total is exactly
120,000 × 4 with zero packing ambiguity — confirms it.

> **The test had been captured and never read.** That is the recurring failure this
> project has tooling for now.

## OQ-REAL5069 — does the second platform need its own cost model

**CLOSED NEGATIVE for content.** Two platforms carrying identical content at five
densities produce **byte-identical residuals at every density**, so the platform
difference is a single project-level constant rather than a per-feature one.

**Read this as "no per-platform CONTENT model is needed", not "the platform difference
is fully wired."** The result was measured on generated files.

## OQ-L9BUDGET — memory budget for one controller family

**BOUNDED, deliberately not guessed.** There is no budget for that family, so the UI
has no denominator and cannot show headroom. **The catalog digits look like they encode
memory, but that is a pattern, not a source**, and this project has been wrong before
inferring a constant from a catalog number.

## OQ-PREDEFINED — firmware-native structure sizes

**SOLVED for all 195 known types.** A 184-file blank-tag discovery batch gave 174 real
capacity deltas, wired in one batch. The two longest-blocked types are resolved with
real totals.

**One type was wrongly documented as unmodelled** when its probe had in fact captured
real data and it was already wired — found by checking rather than trusting the note.

**One type wired from real decorated data matched its later real capture exactly**,
which independently confirms the derivation **method**, not just that one type.

The SFC and function-block families stay ASSUMED: read off real data with zero
variance, but not capture-confirmed, and two of them rest on a single instance each.
**None is drillable to a per-field breakdown** — only the total is confirmed, field
counts vary widely, and a fabricated even split would misrepresent that.


**CAPTURE ERRORS: 1 row(s)** — `predefprobe_axis_generic`, 1 error, captured with a
window-title mismatch and its file no longer exists. AXIS_GENERIC occurs in none of the
eighteen real programs, so it is retired with the other absent predefprobe types rather
than re-triggered.
## OQ-AXISSTRUCT / OQ-AXISDEEP / OQ-AXISCOMBO — axis structures

**SOLVED as empirical constants, with a discrepancy recorded rather than resolved.**
The axis and motion-group values are empirical because Rockwell does not publish the
layout. Axis sizing is **byte-exact on one real program** over 37 axis tags and
778,728 bytes — the largest single category in that file.

**A second set of totals exists and is deliberately not wired**, each roughly 92–100
bytes higher, measured against a baseline that does not itself reconcile. The file
composition behind it is not available, so it is recorded rather than silently trusted
or silently dropped.

## OQ-AXISMARGINAL — multi-drive axis scaling

**CLOSED, and it is the canonical validity failure.** Every file in the sweep carried
`error_count = drives + 1`, and its residuals were almost perfectly linear in drive
count — so it looked like an exact per-drive over-charge finding, **was derived to zero
residual on 18 of 18 points, and was wired and committed.** It was an artifact of the
drives failing to build. Reverted the same session.

The real cause, identified from the error **counts** alone when no error text existed:
a drive needs its bus supply module **and** that supply's converter axis. Four
generators fixed, two lint rules added, and six first-instance module values downgraded
from KNOWN to ASSUMED because they rested on the same broken captures.

**A clean, exact-looking linear fit is not evidence of validity. Check the error count
first.**

**CAPTURE ERRORS: 57 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it.

## OQ-CAMSHAPE / OQ-CAMSCALAR — CAM structures

**SOLVED, and it corrected a wired constant.** CAM was fitted on standalone tags while
every real use is a UDT member. **The container does not matter** — but the original
constant was wrong, and the member arm is what exposed it.

The base corrected from 8 to 4, plus 8-byte element-block alignment. **The old value
read exact at two counts and "a flat −4 of familiar small noise" at three others. It
was not noise** — the −4 fell exactly on the even element counts, which is where the
element total is already 8-aligned.

A scalar CAM stays open in principle and unpriced in practice: the corpus contains
**zero** real examples, and this model prices it as a one-element array, which two files
say is wrong by about a hundred bytes.

---

# Alarms

## OQ-ALARMCOND — tag-based alarm conditions

**SOLVED with zero residual on every captured point, from a starting point of the
single largest unpriced item in the model.** Thousands of real elements across the
corpus, hundreds in every real program, **all costing exactly zero.**

A file base, a per-condition rate, and an associated-tag term keyed on the resolved
type of what each association points at. Derived from a 37-file batch.

**Alarm name length, message text, severity and delay values were all proved free.**

The leftover residual after an earlier refit correlated +0.583 with alarm count — the
strongest identified driver at the time, which is what pointed at this.

> The per-condition formula holds. Its measurement **inside real content** does not
> fully agree across two real programs — see `OQ-ALARMCONDREAL` in
> `OPEN_QUESTIONS.md`, which was promoted back out of this file for that reason.

## OQ-ALARMDEF — the ALMD and ALMA instructions

**PARKED, not closed.** **Zero occurrences across all real programs.** No
alarm-instruction question may be worked ahead of something that moves real prediction
error.

**Scope note: this covers the INSTRUCTIONS only.** Tag-based alarm condition elements
are a separate feature, are present in real programs at 19–21% of total memory, and are
**not** parked. Three separate things share the word "alarm" and must never be reported
as one.

**CAPTURE ERRORS: 1 row(s)** — owned by this question, captured with Studio build
errors. The question is parked; the row outlives it.

## OQ-ALARMPROPBYTES — **CLOSED with OQ-ALARMCOND.** The per-property costs are proved free.

---

# Closed in the capture batch after the blind set

## OQ-JSRCALLERBASE — a JSR caller routine costs what any routine costs

**SOLVED and wired.** The 280-byte premium is not per caller routine and not per
file: **a routine that calls a subroutine carries no premium at all.**
`jsrcallers_k{01,02,04,05,10,20}` hold 20 calls and 20 targets fixed while the caller
count runs 1 → 20:

| callers | 1 | 2 | 4 | 5 | 10 | 20 |
|---|---:|---:|---:|---:|---:|---:|
| actual | 25,472 | 25,752 | 26,312 | 26,592 | 27,992 | 30,792 |
| step per extra caller | | 280 | 280 | 280 | 280 | 280 |
| old prediction | 25,752 | 30,848 | 41,040 | 46,136 | 71,616 | 122,576 |

280 is the plain-routine increment (`routine_extra` 264 plus the routine's name), so
every extra caller costs exactly what an extra plain routine costs, and the first
shares the file's one-time `fixed_base_per_routine`. **Fix:** a JSR caller is counted
as an ordinary routine in the task/program shell; `jsr_fixed_base_per_routine` is no
longer charged and the separate "Subroutine Overhead" line is gone. All six files are
now exact, `jsr_sbr_ret` goes from 10.3% to 1.4% mean, `subroutine_for` to exact, and
the multi-program composites from 2.8% to 1.3%. JSR's per-instruction accuracy moves
from 0.91% mean / 1.40% worst to 0.016% / 0.29%.

**An ST routine that is a JSR target now pays the RLL target's declaration**
(`jsr_target_declaration` + A(n)). It had no charge; the old per-caller constant had
been covering it, and every `st_*` file read +280 the moment it was removed. 67 of 74
ST rows are inside ±8 against 26 before.

**It unmasked a compensating error on the real programs.** The per-caller 5,096 had
only ever been measured on single-caller files, yet it was applied to every caller in
real programs, 10–87 of them each. Removing it moves the real-set mean from 1.74% to
3.12%: real programs are missing about 3% that the over-charge had been hiding. That
is OQ-REALUNDER's problem now, and OQ-OPERANDSHAPE is the first targeted attack on it.

### The derivation as it stood before the capture


**The marginal cost of a no-parameter JSR is exact and the engine already has it
right.** One distinct 0-parameter target plus its JSR call costs **368 bytes**,
measured straight off the captures:

| pair | interval | per unit |
|---|---:|---:|
| `jsr_multi_distinct_targets_01` → `_03` → `_05` | 2 | **368** |
| `..._n05` → `_n10` → `_n15` → `_n20` | 5 | **368** |
| `..._n20` → `_n50` | 30 | **368** |
| `jsr_crossed_n20_namelen16` → `_n40_namelen16` | 20 | **368** |

Eight independent intervals across two generators, zero residual. `jsr_crossed_n20_namelen16`
and `jsr_multi_distinct_targets_n20` were built by different generators and capture
at the identical 25,472. Target name length is separately priced and also exact —
all five `namelen` rows carry the same residual.

**The residual is a single flat constant.** Recomputed live against the current
engine, all 14 clean 0-parameter rows over-predict by **exactly 280 bytes** — at
n = 1, 3, 5, 10, 15, 20, 40, 50 and at name lengths 4, 8, 16, 32, 40. The slope is
perfect; only the intercept is wrong.

**It is `jsr_fixed_base_per_routine`, and the arithmetic is not subtle.** The model
carries two per-routine bases: `fixed_base_per_routine` = **4,816** for an ordinary
routine, and `jsr_fixed_base_per_routine` = **5,096** for a routine containing a JSR.

    5,096 - 4,816 = 280

That is the residual exactly, and the `subrtn_shell` control — same file shape, no
JSR — predicts at **0.000%** at 1, 5, 25 and 100 routines, so the 4,816 path is
right and the 5,096 path carries the whole error. The 280 premium was presumably
meant to cover the caller declaring a target subroutine, but the per-target cost is
already charged separately through `jsr_target_declaration`, so it is charged twice.

That also explains the band. `derive_instruction_accuracy.py` divides a whole-file
error by file size, so a fixed 280 on a 19,952-byte file reads as 1.40% — and the
recorded JSR worst case is **1.4034%**. The number is a constant divided by a file
size, not a property of JSR.

**Blocked, and this is the reason it is not being changed.** `jsr_fixed_base_per_routine`
is charged **once per JSR-caller routine**, not once per file. Every one of the 30
JSR files in the corpus has **exactly one** caller routine — checked directly, not
assumed. So "280 once per file" and "280 per caller routine" fit all 30 rows
identically and the corpus cannot separate them. A real program has tens to hundreds
of caller routines, so the two readings differ by thousands of bytes there, in the
direction that would make the real files worse: they currently under-predict, and
the per-caller reading subtracts more.

This is the collinearity failure mode exactly — two constants against points that
only ever vary one of them. Applying either reading now would be fitting, not
measuring.

**The discriminating family is built: `jsrcallers_k{01,02,04,05,10,20}`** (first built as
`jsr_callerdist_k*`, never picked up by the converter, rebuilt under new names).

Total JSR calls held at **20** and distinct 0-parameter targets at **20** in every
file. Only the distribution moves: with K callers, MainRoutine takes 20/K calls and
K−1 extra caller routines take 20/K each. K runs over the divisors of 20 so no file
carries a remainder routine the others lack.

`confound_check.py` reports **every consecutive pair varies exactly one dimension —
`routines`**, which is the variable itself. Rung text, instruction inventory, tag
inventory and the target set are identical across all six. A plain extra routine is
separately priced at exactly **280 bytes** by `subrtn_shell` (four counts, zero
residual), so that component subtracts cleanly. All six lint clean on 1756-L81E
firmware 35.

K=1 reproduces `jsr_multi_distinct_targets_n20`'s shape and target names exactly and
predicts at the identical 25,752, so it is anchored to a capture already in hand
(25,472).

**Predictions written down before the capture run, per the blind-test rule:**

| file | callers | engine predicts | **A** per file | **B** per caller | **C** flat −280 |
|---|---:|---:|---:|---:|---:|
| `jsrcallers_k01` | 1 | 25,752 | 25,472 | 25,472 | 25,472 |
| `jsrcallers_k02` | 2 | 30,848 | **25,736** | **30,288** | **30,568** |
| `jsrcallers_k04` | 4 | 41,040 | **26,264** | **39,920** | **40,760** |
| `jsrcallers_k05` | 5 | 46,136 | **26,528** | **44,736** | **45,856** |
| `jsrcallers_k10` | 10 | 71,616 | **27,848** | **68,816** | **71,336** |
| `jsrcallers_k20` | 20 | 122,576 | **30,488** | **116,976** | **122,296** |

- **A — the base belongs to the file.** An extra caller routine costs what any
  routine costs, 264 plus its rungs. `actual(K) = 25,472 + 264·(K−1)`.
- **B — the base belongs to each caller.** The engine's structure is right and only
  the 280 premium is wrong. `actual(K) = predicted(K) − 280·K`.
- **C — the engine is right and the 280 is something else.**
  `actual(K) = predicted(K) − 280`.

All three agree at K=1 by construction and separate by **86,488 bytes** at K=20.
There is no reading of the result that leaves this open.

**If A holds, this is not a 280-byte item.** The engine charges 5,096 per caller
routine; a real export has 60 of them, so it would be over-charging roughly 300,000
bytes there and something else is under-charging by more, since the real files
currently under-predict. That is the compensating-error failure mode, and it would
make this the largest single identified defect in the model.

Hold `jsr_fixed_base_per_routine` at 5,096 until the capture reads.

**The 280 is now billed where it belongs and is visible.** The per-caller shell
is its own `subroutine_shell` entry under a **Subroutine Overhead** tree group,
labelled with the caller count — 122,304 bytes across 24 caller routines, 1.58%,
on the real export. It was previously folded into each calling routine's
instruction total, invisible, and the difference was charged against the JSR
instruction. Reclassification only: totals byte-identical on all 3,551 corpus
files. The uncertainty this question tracks now sits on that line item.

**The confidence side is already fixed and does not wait on the capture.** The
280 is a per-routine shell constant, not a JSR cost, so it was never JSR's band
to lose. `JSR/0` now reads **Exact ±0**: see `MEMORY_MODEL.md`, "A 0-parameter
JSR is EXACT". On the real export that moves 13 routines from 75% to 100% while
the 20 carrying a parameterised JSR stay at 75%. What the capture settles is the
byte total, not the band.

**A second, smaller band sits underneath it.** The `jsr_paramcount_*` family
residuals cluster at **−296 / −300** rather than −280, flat across rung counts from
10 to 1,000 and across parameter counts 1 to 15. That is a further 16–20 bytes
outside the ±8 floor, constant, and it appears only once SBR/RET carry operands. It
is the same shape of defect and almost certainly resolves with the same file.

**Why this is worth the time despite being 280 bytes.** It is not the bytes. It is
that the confidence display points at the wrong instruction, so the one number a
user judges a dispatch routine by is wrong for every routine that dispatches — and
the same constant is charged per caller routine across every real program, where
it is not 280 bytes at all.

## OQ-RUNGSHAPE — no per-rung term is missing

**CLOSED NEGATIVE.** `rungpack_{xic,equ}_k{01,02,04,08,16,40}` pack 4,000 instructions
k to a rung, each rung closed by a NOP, using a **non-output** instruction so no series
output cascade is involved. All twelve files are **exact** — zero residual at every
packing, XIC and EQU alike. The per-rung base and per-instruction weights already
separate correctly, so the confound between them costs nothing.


**Every calibration file in the project is one instruction per rung.** So a per-rung
cost and a per-instruction cost are **perfectly confounded** in every weight in the
model. `routine_logic` is 18% of predicted mass, so this is not a small exposure.

### The coverage gap is real but is NOT the error

The weights are fitted on a corpus that is **9.4% branched rungs and 62%
single-instruction rungs**, against real programs at **68.7% and 7%** — measured over
41,374 real rungs and 125,275 real instruction occurrences.

That was the largest suspected error source in compiled logic. **It was measured, and
the terms hold exactly.** Holding eight XIC conditions and one OTE fixed across 500
rungs and moving only the arrangement across 1, 2, 4 and 8 parallel legs, the
predicted steps are correct **to the byte at every leg count**, and a second pair
confirms it at the real population's composition.

**So the branch-bracket cost extrapolates correctly outside the shape it was fitted
on.** The coverage gap is a fact about the corpus, not a defect.

### The attempt to isolate the per-rung term failed, by design error

A packing sweep held 4,000 instructions fixed and varied how many sat on each rung,
so rung count moved while instruction count did not — which is the only way to
separate the two terms.

**It used OTE, which is an output.** Packing outputs onto one rung builds series
cascades, so extra series outputs and rung count moved together identically in every
file. **Total confound.**

It was not wasted: it re-measured the series-output law at four new points at exactly
−12.000, and **killed that law's competing candidate** — the files were all distinct,
so the cost cannot be per-distinct-rung.

**A packing sweep must use a non-output instruction.** That is the one design
constraint the next attempt has to respect.

### Built: `rungpack_{xic,equ}_k{01,02,04,08,16,40}` — 12 files

4,000 instructions in every file, packed k per rung (4,000 → 100 rungs), every rung
closed by one `NOP()`. XIC and EQU are both non-output, so no series cascade forms at
any k. Operand text and tag inventory are identical across each arm; the confound gate
reports one moving dimension per pair.

**What the slope says.** Bytes per removed rung, against the NOP-plus-rung cost the
engine already charges. Equal: the instruction weights carry no hidden per-rung share.
Larger: the excess is the per-rung cost folded into every weight, read directly. Two
arms so the answer does not rest on one instruction.

## OQ-ALARMCONDREAL — 107 bytes per condition, confirmed at real scale

**SOLVED.** `alarmcond_realcount_n{000,200,400,600}` put 0–600 alarm conditions in the
real production shape (TRIP, three associated tags, HMI group) on arrays held at 640.
Every file reads the universal **+12** file residual and nothing else: the
per-condition cost is exact at real counts and real shape. The 8.8% gap on one real
program is therefore not a per-condition cost; it stays with OQ-REALUNDER. No real
program carries alarm sets, so that arm has no exposure.


**Promoted from the resolved file.** It was filed there because the per-condition
formula was derived and wired; the disagreement below is unexplained and the exposure
is large enough that calling it closed understates it.

| program | conditions | actual step | predicted step | actual per condition | predicted |
|---|---:|---:|---:|---:|---:|
| `export 14` | 400 | 443,128 | 442,400 | 1,107.8 | 1,106.0 |
| `export 08` | 200 | 243,040 | 221,600 | **1,215.2** | 1,108.0 |

**Within 0.16% on one file and 8.8% short on the other** — and that is **19% and 21%
of total controller memory** respectively, the second-largest category in both.

**The step is clean.** An exhaustive element-tag diff of each full export against its
alarm-free sibling shows `AlarmCondition`, `AlarmConfig`, `HMIGroup` and the
`AlarmConditions` container are the **only** elements that differ. No tags, rungs,
routines, programs, UDTs or AOIs moved.

**This is not a scale error — the two files disagree with each other**, on the same
wired formula, with every condition in both hanging off a single BOOL array tag. So
something differs between them that the formula does not see.

**Two caveats on the numbers.** Both readings came from files derived from real
exports, which were later found not to import — so **re-derive before citing them
further.** The per-condition formula itself rests on a 37-file generated batch and is
unaffected.

**What is untested:** alarms on a UDT-scalar host (a handful of real conditions sit on
a UDT rather than a BOOL array, and the batch only covers array hosts), and whether
alarm **sets** carry their own cost — the operator and rollup inclusion flags are true
on every real condition and no file varies them.

**What the eighteen real exports say, counted in the final review.** 4,655 of their
4,663 alarm conditions are exactly the shape the generated sweep already prices — TRIP,
severity 500, array-indexed input on a BOOL array host, three associated tags and an
HMI group of at most 15 characters. The other 8 are inherited from a type-level
definition in one program. **No real program uses alarm sets or any other condition
type**, so neither untested item above has real exposure. And the whole-program
results argue against the 8.8% figure: export 08, the file it came from, is predicted
**+0.24%** overall with alarms at 21% of its memory — an 8.8% alarm under-charge would
put it about 1.8% low.

**Built: `alarmcond_realcount_n{000,200,400,600}`** — the real shape at real counts,
host and associated arrays fixed at 640 so only the condition count moves. The existing
real-shape sweep is exact (a flat +16 file residual) but stops at 128 conditions; this
is the check that the law holds where real programs actually sit. If it does, the
question closes.

**Do not confuse this with the ALMD instructions**, which are parked with zero
occurrences in the real set, or with an ordinary scheduled program named for alarms.
One real program carries both this and such a program.

## OQ-BUILDFAIL-OPEN — the defect log

**CLOSED.** Every file on it now builds: `almd_minimal_r3`, `almd_realtext_r3` (0
errors, 0 warnings) and `modulerack_kinetix_full_bus_r3` (0 errors, 24 axis warnings),
plus `eventtask_axiswatch_r2` (0 errors). The causes are enforced in lint rather than
remembered: `kinetix_drive_missing_configid`, `native_instruction_arg_count`, and
`scripts/check_proven_blocks.py` before any Kinetix file is handed over.

ALMD itself stays unpriced (the instruction is parked); its files now build, so its
cost can be read off them if the park is ever lifted — about 320–360 bytes above the
engine on these two files.


Full diagnostic rules and root-cause reference are in `OPEN_BUILD_ERRORS.md`; this
entry exists so errored rows have an owner.

### What the re-triggers returned

| file | result | cause |
|---|---|---|
| `eventtask_axiswatch_r2` | **0 errors**, 6 axis warnings | builds. The original's error was the 5069 processor it was captured on |
| `almd_minimal_r2`, `almd_realtext_r2` | 1 error each: *"Rung 0, ALMD: Invalid number of arguments for instruction"* | the generator's 7-operand call. The one real ALMD in the eighteen real exports takes **5**: `ALMD(tag,1,1,0,0)` |
| `modulerack_kinetix_full_bus_r2` | 4 errors, 24 warnings; the error text was cut off | the original's log names it: *"Tag '<drive>:SI': Invalid data type for safety tag"* on all three drives, plus *"Project size exceeds controller capacity"* |

**The Kinetix failure was a known defect shipped again.** `gen_assumed_closeout.py`
had already recorded that the hand-copied 2198 `-ERS3` blocks in
`gen_module_sweep_variants.py` / `gen_module_sweep.py` lack the `<ExtendedProperties>`
ConfigID, that Studio then configures the drive for networked safety, and that drives
must come from `_drive_module_xml`. That was a comment, not a check: the blocks stayed
importable, lint did not test for the element, and `gen_module_kinetix_bus.py` kept
using them. The `_r2` rebuild fixed the converter axis and processor and inherited
the drives unchanged. Every real 2198 drive — about 250 — carries a ConfigID.

**Now enforced, not advised:**

- `lint.py` `kinetix_drive_missing_configid` refuses any file with a 2198 `-ERS`
  drive lacking a ConfigID. Every generator writes through lint, so nothing bypasses it.
- Both module tables replace their `-ERS3` blocks at import with `_drive_module_xml`
  output. The safety-wired 4conn variants are dropped.
- `lint.py` `native_instruction_arg_count` checks ALMD's operand count against the
  real form.
- `scripts/check_proven_blocks.py` requires every 2198 module and AXIS_CIP_DRIVE block
  in a file to match a block from a **zero-error capture**. It flags all three drives
  in both failed Kinetix builds and passes the rebuild.
- `tests/test_build_guards.py` pins all of this and runs lint and the proven-block
  check over every file waiting for capture.
- The capture script kept only the first 300 characters of Studio's log, and Studio
  lists warnings first, so the `_r2` Kinetix log lost all four errors. It now keeps
  every Error line first, then the summary, then warnings while room remains.

### Re-triggered again, awaiting capture

| file | what changed |
|---|---|
| `almd_minimal_r3`, `almd_realtext_r3` | the real 5-operand call |
| `modulerack_kinetix_full_bus_r3` | rebuilt only from proven blocks: one 2198-P208 supply with its converter axis, 2198-D032/D057/D020-ERS3 drives from `_drive_module_xml`, six servo axes on Ch1/Ch3. **One bus, not two:** the P031/P070 supplies occur in no real program, and a second bus needs a second bus-sharing group whose ConfigData has never been verified |

The ALMD pair is generated despite the ALMD park because the goal is to close the defect
log, not to work the instruction.

### Moved out, because the cause is already known

| row | now owned by | why no re-trigger |
|---|---|---|
| `instrfirst_mapc_x10` | OQ-MAMFAMILY-BUILDFAIL | the original MAPC generator bugs; `_v2` and `_v2_x10` captured clean and MAPC is EXACT |
| `instrfirst_crout_x10` | OQ-SAFETY | CROUT needs a safety CPU; Safety family ignored |
| `predefprobe_axis_generic` | OQ-PREDEFINED | AXIS_GENERIC is in none of the real programs; file gone |

**CAPTURE ERRORS: 4 row(s)** flagged here by `scripts/capture_errors.py` —
`almd_minimal`, `almd_minimal_r2`, `almd_realtext_r2` and
`modulerack_kinetix_full_bus_r2`, each with its cause diagnosed above. The question
closes when the three `_r3` files capture clean.

Run `python scripts/capture_errors.py --list` for the current row identities.

## OQ-MODULENAMELEN — a module's name is stored twice

**BOUNDED — law measured, deliberately not wired.** `modname_p208_len*` (4–40
characters, twelve files, all clean) fit one law exactly: the name is stored twice,
each copy rounded up to 8 bytes,

    name_bytes(L) = roundup8(L + 3) + roundup8(L + 5)       (charged relative to L = 4)

It predicted the Kinetix bus files independently: +80 on
`modulerack_kinetix_full_bus_r3` (three 14-character drive names at +24, one
10-character supply at +8) and +72 on the Studio-made two-supply file, which are
exactly their residuals. **Real exposure is 0.02%** — 18 KB across 1,058 real
modules, median name 9 characters — and wiring it correctly means re-deriving 51
per-catalog constants that were each measured at a different name length (the sweeps
used ~18 characters). Below the noise floor, so recorded and closed. The +80/+72 on
those two files is this term.


**The measurement.** Two committed isolation files, both a 1756-L81E with a single
2198-P208 under the local rack, no tags and no axes. They differ in exactly one
thing: what the module is called.

| file | module name | chars | actual | predicted | delta |
|---|---|---:|---:|---:|---:|
| `modulemotion_p208_baseline` | `P208` | 4 | 22,136 | 22,136 | **0** |
| `modulesweep_2198_p208` | `TestMod1_2198P208` | 17 | 22,160 | 22,136 | **−24** |

Both captured with `error_count = 0`. The controller name is 17 characters in both,
so it is not that. **+13 characters of module name is worth +24 bytes**, and the
engine charges nothing for a module name at any length.

**Why this is not already answered.** Identifier name length is priced for tags, for
UDT type names, for AOI type names and for custom string type names -- four separate
laws in `memory_model.yaml`, all of them a step of 8 bytes per bucket. None of them
applies to a `<Module Name=...>`, and no sweep has ever varied one.

**Why it is not wired.** One pair is one equation. A step of 8 bytes per
`floor(len / 4)` bucket reproduces +24 exactly, and so do several other shapes --
that is two points against a two-parameter family, which this project has already
been burned by. The existing name-length laws bucket by 8 characters, not 4, so
matching them would predict +16, not +24. Something is different here and one pair
cannot say what.

**Consequence for confidence.** `2198-P208` reads ASSUMED rather than KNOWN, and so
do the other flat-fitted 2198 supply catalogs. That is correct and should not be
overridden: its two isolation captures do not agree with each other, and until the
name term is priced, a P208 in a real file is predicted exactly only when its name
happens to be short. The frequency of the catalog in real programs is not evidence
about the constant -- only an isolation capture is.

**Built: `modname_p208_len{04,06,08,10,12,13,16,17,20,24,32,40}`** — one 2198-P208,
no tags, no axes, only the module name length moving. Lengths include 6, 10, 13 and 17
because the task-name finding (OQ-TASKNAMEROUND) showed only non-multiples of 8 can
tell a round-up rule from a round-down one. It reads the step directly instead of
fitting it.

**Exposure before building anything.** Real programs carry 20-60 modules each. At
24 bytes for a 13-character name this is on the order of a kilobyte per file against
a residual of tens of kilobytes, so by the noise-floor rule it does **not** earn a
capture slot ahead of the literal-operand batch. It is recorded because it explains a
specific wrong-looking confidence tier, not because it is worth a session.

## OQ-OPERANDSHAPE — a member-path operand costs what a plain tag costs

**CLOSED NEGATIVE.** All 26 `opshape_*` files are exact against the engine as it
stood: member paths (`U.Bit`), nested members (`U.Sub.Bit`), UDT-array members
(`UA[2].Bit`) and bit-of-word (`PD.5`) on XIC and OTE, and member source, member
destination and nested member on MOV, at 250 and 1,000 rungs. Operand shape does not
carry the real residual.

What the batch did find: lint's operand resolver refused `U.Bit` as a non-BOOL
operand, which is why no earlier generated file had ever carried a member path. It
now follows member paths through the file's UDTs.

## JSR parameter edges — structured returns and UDT-member arguments

**SOLVED and wired** from `jsredge_*` (8 files, 100 calls each):

- A **UDT member argument** (`W.S0`, of UDT type) costs exactly what a bare UDT tag
  costs; the structured check now follows member paths and array elements.
- A **UDT return value** costs 16 more per call than a DINT return (twice an input's
  8), plus 12 on the target.
- A **RET that returns values** costs 48 plus 22 per value, less 72 once per target —
  five RLL files solved together, all inside ±4 bytes.

JSR files now 0.02% mean, 0.29% worst across 79 rows.

### The question as it stood before the capture


**Every instruction weight in the model was fitted on plain-tag operands.** Real
operands, counted over every instruction call in the eighteen real programs:

| operand | real programs | composites that fit |
|---|---:|---:|
| plain tag | 48.7% | ~75% |
| member path `A.B` | 32.6% | 0% |
| nested member `A.B.C` | 15.4% | 0% |
| deeper | 3.2% | 0% |
| array element, constant index | 22% of operands | ~80% |
| bit of a word `D.5` | 9% | ~25% |

Array elements and bit-of-word operands are in the composites that fit, so they are
already covered. **Member paths are half of all real operands and appear in no
captured generated file at all** — because lint's operand resolver returned the BASE
tag's type for `U.Bit`, refused it as a non-BOOL operand of XIC, and so blocked every
member-path rung any generator tried to write. The resolver now follows member paths
through the file's own UDT definitions.

**Mechanism and expected movement.** If a member reference costs more than a plain
tag in compiled logic, the under-charge scales with instruction count, which is what
the residual does. At the ~20% of `routine_logic` the residual represents, it would
need a few bytes per member operand; the batch measures it directly.

**Batch built — 26 files, `gen_operand_shape.py`, 1756-L81E fw35, lint clean, confound
gate clean.** One instruction per family, one operand's shape varied, identical tag
inventory in every file, at 250 and 1,000 rungs:

| family | shapes |
|---|---|
| `opshape_xic_*` — `XIC(<op>)OTE(Out)` | plain, mem, nest, arrmem, bitword |
| `opshape_ote_*` — `XIC(In)OTE(<op>)` | plain, mem, nest, arrmem |
| `opshape_mov_*` — `MOV(<src>,<dst>)` | plain, srcmem, dstmem, nest |

Each shape differences against its family's `plain` file at the same count; the two
counts give the per-rung slope. `arrmem` and `bitword` are controls.

# Process, tooling and scope

## OQ-GENMETHOD — can hand-built XML be imported

**SOLVED.** Yes. Direct XML authoring works and is the method. The fallback approaches
— driving Studio's automation interface, or hand-fixing failures and re-exporting —
were never needed as the default path, though the second remains the only way to
produce a valid variant of a real export.

## OQ-EMULATE / OQ-MEMREADMETHOD — how to read memory

**SOLVED, and it simplified the loop substantially.** **No download and no emulator
are needed** — Studio shows memory usage as soon as a project compiles offline.

**There is no programmatic memory read, online or offline.** GSV has no memory
attribute on any Logix 5000 platform, and the documented message-based path is
explicitly unsupported across the current lineup. **Controller Properties, read by eye,
is the only method.**

## OQ-CAPTURERACE — a capture reading the wrong file

**SOLVED at the source.** The window title is cross-checked against the file requested.
A real confirmed case had one request come back with the previous file's title still
showing.

**The subtle part:** an "already logged" check that only asks whether a value is
non-empty treats a mismatched row as done forever, because it **does** have a value — a
wrong one. The filter now excludes flagged rows, so they are retried automatically and
self-heal.

## OQ-TOLERANCE — what counts as good enough

**SOLVED.** Exact-tier predictions: within 1% good, 3% acceptable, above 5% a real gap.
Logic-tier is not held to the same bar, because compiled logic size is a fitted
heuristic by nature of the problem. **An error in the tier the tool calls exact
undermines its value proposition more than an acknowledged estimate does.**

The project-wide single-measurement noise floor is **±8 bytes**.

## OQ-EXPORTSCOPE — what a partial export costs on import

**CLOSED — accepted in use.** Partial exports of AOIs, UDTs and programs import and
are sized correctly enough for their purpose; the owner has confirmed the behaviour
and needs nothing further from it.

The scope machinery stays as wired: a partial export gets no project base load, no
firmware, catalog or safety baseline delta and no task/program shell, and its total
is reported split three ways — target, context and project. The rules are in
`MEMORY_MODEL.md`.

**What was never measured, recorded so it is not mistaken for known:** the shell an
imported Program or Routine creates in the destination project, and whether
reconciling an already-present context declaration costs anything. Nothing is charged
for either. Measuring them needs a Capacity reading before and after an import into
an existing project in Studio — a bench session, not a generated file, since the
capture pipeline only converts whole projects. It was a correctness requirement, not
an accuracy one: it moves no real-program number and is not reopened for accuracy
work.

## OQ-L5XVERSION — **CLOSED.** The corpus spans several schema revisions and the parser handles them. Two older revisions have no real sample in hand and are backlogged rather than guessed.

## OQ-SAFETY — **SOLVED.** A safety project's total is understated, and the UI warns. Safety-family instructions are out of scope.

CROUT and the rest of the Safety family (DCS, ROUT, ESTOP, RIN) are **ignored**: no
test file is built for them and a failed build of one is not pursued.

**CAPTURE ERRORS: 1 row(s)** — `instrfirst_crout_x10`, 80 errors, one per rung-level
CROUT on a standard controller. The cause is the instruction itself needing a safety
CPU. No re-trigger.

## OQ-COMMENTS — **SOLVED.** An RLL rung comment is free. **An ST comment needed testing separately** and is also free — the RLL result does not transfer, because a rung comment is a separate element while an ST comment sits inside compiled source text.

## OQ-LOGICVISIBILITY — **CLOSED.** Logic-derived numbers are flagged estimated everywhere they appear, per the ground-truth constraint.

## OQ-EVENTTRIGGER — EVENT instruction and task trigger cost

**SOLVED for the instruction half.** The EVENT instruction had **no weight at all** and
was charged zero. Three counts with nothing else varying read exactly `56n + 8`, the 8
being the universal per-file residual.

**CAPTURE ERRORS: 1 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the row outlives it.

## OQ-V3GENBUGS — generator defects found by ablation

**CLOSED, with one arm permanently BLOCKED and that is the lesson.** Three real
generator bugs were found and fixed, including unsigned atomic types falling through a
parser's own hardcoded table so any module member declared with one turned the module
total into a floor.

**The ablation arm cannot be differenced at all, because it is not single-variable** —
turning off several things together measures their sum. **That is a design failure, not
a capture failure, and no amount of recapturing fixes it.**

## OQ-COMPOSITESCALE — are the categories additive

**CLOSED NEGATIVE, which is the answer that was wanted.** The question was whether
formulas each fitted by scaling one thing at a time stay correct when a real project
mixes everything at once, and whether an interaction between categories explains why
synthetic composites over-predict small and under-predict large.

**There is no interaction.** A 3×3 grid for each of the six pairs drawn from UDT-typed
tags, rungs, AOI instances and modules, with everything unnamed held at zero, comes
back additive — 24 of 24 exactly.

**So the composite residual is not an interaction effect**, and the remaining
composite error is the superseded-generator blend recorded in `SEGMENT_TRACKER.md`.

**CAPTURE ERRORS: 82 row(s)** — owned by this question, captured with Studio build
errors. The question is closed; the rows outlive it. **Every one is from a superseded
generation, and none ever fed a number** — the validity filter already rejected them.

## OQ-REALGAP / OQ-STACK — early framings of the real-file residual, superseded by OQ-REALUNDER.

## OQ-FBDSFC — **CLOSED.** The SFC and function-block predefined structures are sized; their routines' own content is out of scope, as the corpus is overwhelmingly RLL and ST.

## OQ-CTLSHELL — the supposed unpriced controller shell

**CLOSED NEGATIVE, and the withdrawal is the point.** It was opened on a bare real
shell reading 21,096 against a predicted 13,296 — a 7,800-byte hole in unpriced shell
content. **Both numbers were wrong.**

**A File|New project reads 18,112 and the engine predicts 18,112.** Exact, confirmed
twice: read off a fresh Studio project, and back-solved from the empty-rung captures.

13,296 is the controller-only **component**, not a whole-file total. The
MainTask/MainProgram/MainRoutine that File|New also creates cost 4,816 more, and
13,296 + 4,816 = 18,112. The actual was wrong too — the real figure is 17,352.

**Corrected, the sign flips**: the engine **over**-charges that shell by 760 rather
than under-charging by 7,800.

**Two rules follow.** **Quote a whole-file prediction against a whole-file capture,
never a component against a total.** And a measurement taken off the strip ladder is
suspect by default — those files were later found not to import at all.

One byproduct kept, unwired: a dual-IP / DLR controller configuration costs +40 bytes.
One reading, one controller.

**Closing this removed the last measured evidence of content the engine does not count
at all — for about six hours**, until the literal-operand measurement supplied new
evidence of exactly that shape.

## OQ-PRODCONS — produced and consumed tags

**FORCE-CLOSED below the noise floor. Do not reopen and do not spec another file.**

No special connection formula is needed: a correctly built produced or consumed tag's
DataType already includes a connection-status member, so ordinary UDT recursion covers
it, and that member type is itself wired.

**A Produced tag does carry +1,072 bytes the model does not charge — measured, not
guessed — and it is still closed**, because the entire real population of them is on the
order of a thousand bytes against a residual three orders of magnitude larger, and most
of what such a tag costs is already charged through its UDT definition and its module.

They are 0.11% and 0.06% of real tags. **Apply the noise floor before building, not
after capturing.**
