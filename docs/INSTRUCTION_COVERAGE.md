# Instruction Coverage

What fraction of real logic is actually sized, instruction by instruction.
**Regenerated whenever capture data lands** — the counts below are live, not
transcribed.

Measured over the 17 real production exports: **41,374 RLL rungs,
125,275 instruction occurrences, 107 distinct native mnemonics**, plus
96 distinct AOI definitions whose call sites are counted separately.

## Headline

**99.72% of every real instruction occurrence carries a weight.** The
unweighted remainder is **0.282%** — 6 mnemonics, 353 occurrences — and is listed
in full below rather than rounded away.

Real logic is extremely top-heavy: **4 mnemonics cover half of all
occurrences, 18 cover 90%, and 44 cover 99%.** The long tail is real but
individually negligible, which is what the noise-floor rule in `CLAUDE.md` is for.

## Spelling across firmware

From v36 sixteen ladder instructions are renamed, and a v36+ project rejects the old
name:

| v35 | v36+ | v35 | v36+ | v35 | v36+ | v35 | v36+ |
|---|---|---|---|---|---|---|---|
| EQU | EQ | NEQ | NE | GRT | GT | GEQ | GE |
| LES | LT | LEQ | LE | MOV | MOVE | LIM | LIMIT |
| SQR | SQRT | TRN | TRUNC | XPY | EXPT | ACS | ACOS |
| ASN | ASIN | ATN | ATAN | TOD | TO_BCD | FRD | BCD_TO |

The engine reads either spelling as the same instruction, and the tables here use the
v35 name. All seventeen real programs are v31–v35.

## What "weighted" and "accurate" each mean

These are two different things and the table separates them.

**Weight** is the per-occurrence byte cost the engine charges. A blank means the
engine charges nothing for that mnemonic.

**Measured accuracy** is how far the engine's whole-file prediction actually landed
from the controller's reading, on captured files where **that instruction was the
only variable under test** — exactly one non-scaffold opcode, compiled logic the
dominant cost, and enough occurrences for the slope to beat the per-file base. It
is produced by `scripts/derive_instruction_accuracy.py`, which identifies isolation
files **by what they contain, never by name.**

A dash means no file isolates that instruction. That is not the same as untested:
XIC, XIO, OTE and NOP are the scaffolding every other test rung is built from, so
they can never be the single variable — but they are the **most-measured weights in
the model**, fixed by the empty-rung sweep and confirmed byte-exact by the
arrangement sweeps. SBR and RET are likewise scaffolding, measured through the
`subrtn_*` control rather than in isolation.

**90 of the 107 mnemonics in the table carry a measured accuracy; 17 show a dash.**
Four of the 17 are scaffolding (XIC, XIO, SBR, RET), three are Safety-family and
ignored (ESTOP, ROUT, RIN), and the other ten — MAS, MRP, MAW, MAH, MDR, MSO, MSF,
FOR, LC, SCP — are each below the noise floor in the real corpus, so none earns a
capture slot on its own.

**An accuracy marked `step`** comes from the slope arm of
`derive_instruction_accuracy.py`: the instruction's isolation files are mostly axis,
cam, array or message storage, so the whole-file error says nothing about the
instruction, but the same family captured at two or more counts measures it exactly —
the step between counts is instruction bytes and nothing else. The figure is the
error as a share of the instruction's own bytes, a stricter bound than the whole-file
one. Twenty-nine instructions were credited this way, all at 0.0000%.

**MAPC is Exact**, a named compiled-logic exception alongside the 0-parameter JSR:
260 bytes per call, the step between one rung and ten landing on the wired weight
with both files at the same +12 of file overhead. The third point,
`instrfirst_mapc_v2_x100`, captured at exactly the 87,688 predicted before capture.

## Two caveats that bound every "exact" claim here

**0. Operand shape does not change the weights.** Half of all real operands are
member paths (`A.B` 32.6%, `A.B.C` 15.4%, deeper 3.2%). The `opshape_*` batch put
member, nested-member, UDT-array-member and bit-of-word operands on XIC, OTE and MOV,
and every file was exact against the plain-tag weights (OQ-OPERANDSHAPE, closed).


**1. Every weight was fitted with DINT, LINT or REAL operands.** Operand type
changes the real cost substantially for ADD, SUB, MUL, DIV, MOD, EQU, GEQ, GRT,
LEQ, LES, NEQ, MOV, LIM and CPT — together a large share of the occurrence count
below. SINT and INT cost +88 to +164 more per rung; STRING costs +52 more for EQU
and NEQ. The operand-type surcharge is wired, but there is no per-operand-type
breakdown of the real corpus, so **read the headline as "the instruction mix is
understood," not "every real occurrence sizes exactly."** A program doing heavy
SINT or INT math will size less accurately than this table implies.

**2. A per-rung term is still confounded with the per-instruction terms.** Every
calibration file is one instruction per rung, so a per-rung cost and a
per-instruction cost cannot be separated in the weights below. The attempt to
isolate it landed on the series-output law instead. See `OQ-RUNGSHAPE`.

## Rung arrangement is validated

The weights are fitted on a corpus that is **9.4% branched rungs and 62%
single-instruction rungs**, against real programs at **68.7% and 7%**. That gap was
the largest suspected error source in compiled logic, on the reasoning that terms
calibrated on flat one-instruction rungs need not hold on real ladder.

**Measured, and the terms hold exactly.** Holding eight XIC conditions and one OTE
fixed across 500 rungs and moving only the arrangement — all in series, then 2, 4
and 8 parallel legs — the predicted steps are correct **to the byte at every leg
count**. A second pair confirms it at the real population's composition (1 to 10
conditions per rung, 70% carrying three or more), where the predicted
series-versus-branch step also lands exactly.

So the branch coverage gap is a real fact about the corpus and is **not** an error:
the branch-bracket cost extrapolates correctly outside the shape it was fitted on.

## Structured Text is priced by these same weights

The table counts RLL only. **That is a counting choice, not a modelling limit** —
instruction cost proved identical in both languages, so counting ST call sites
separately would double-report the same evidence.

Four ST/RLL pairs built operand-for-operand identical came back separated by
exactly **+432** — the ST routine shell — and by nothing else:

| pair | ST | RLL | difference |
|---|---:|---:|---:|
| COP x1000 | 135,376 | 134,944 | +432 |
| DTOS x1000 | 95,376 | 94,944 | +432 |
| SIZE x1000 | 151,376 | 150,944 | +432 |
| CPT-mirror x1000 | 475,376 | 474,944 | +432 |

So every weight below applies unchanged to the same instruction called from ST. The
real set carries **4 ST routines and 1,098 ST lines** whose instruction
content is priced by these numbers.

## Counting rules

- **One occurrence per rung a mnemonic appears in**, matching how the parser
  counts — not a raw substring count that would double-count a mnemonic appearing
  twice in one rung.
- **A mnemonic is native only if it is not a declared AOI name in that same file.**
  Several Rockwell-authored AOIs share names with what look like instructions;
  counting them as native would both inflate the instruction count and lose the AOI
  call-site cost.
- Real exports only. The generated corpus is the instrument, not the evidence.

## The table

Sorted by real usage. Measured accuracy is mean / worst, with sample count.

| Instruction | Real usage | Occurrences | Weight | Measured accuracy |
|---|---:|---:|---:|---|
| XIC | 21.67% | 27,146 | 4 | — |
| OTE | 16.29% | 20,413 | 16 | 0.0142% / 0.0205% (2) |
| MOV | 9.75% | 12,219 | 36 | 0.0076% / 0.0202% (16) |
| XIO | 9.00% | 11,280 | 4 | — |
| EQU | 4.73% | 5,921 | 20 | 0.0019% / 0.0136% (9) |
| OTL | 4.35% | 5,452 | 16 | 0.0142% / 0.0205% (2) |
| ADD | 3.39% | 4,253 | 40 | 0.0023% / 0.0127% (7) |
| OTU | 3.16% | 3,962 | 16 | 0.0142% / 0.0205% (2) |
| ONS | 3.15% | 3,946 | 36 | 0.0064% / 0.0101% (2) |
| TON | 2.13% | 2,665 | 20 | 0.0126% / 0.0186% (2) |
| NEQ | 2.12% | 2,661 | 20 | 0.0022% / 0.0136% (8) |
| NOP | 2.10% | 2,629 | 16 | 0.0094% / 0.0205% (3) |
| GRT | 1.93% | 2,421 | 20 | 0.0025% / 0.0136% (7) |
| CLR | 1.70% | 2,129 | 32 | 0.0095% / 0.0146% (2) |
| LES | 1.60% | 2,005 | 20 | 0.0025% / 0.0136% (7) |
| JSR | 1.25% | 1,567 | 68 | 0.0162% / 0.2886% (19) |
| SUB | 1.14% | 1,432 | 40 | 0.0023% / 0.0127% (7) |
| COP | 1.00% | 1,254 | 112 | 0.0102% / 0.0234% (3) |
| LEQ | 0.99% | 1,246 | 20 | 0.0025% / 0.0136% (7) |
| GEQ | 0.93% | 1,160 | 20 | 0.0025% / 0.0136% (7) |
| LIM | 0.62% | 781 | 52 | 0.0016% / 0.0088% (7) |
| JMP | 0.60% | 747 | 40 | 0.0099% / 0.0229% (3) |
| LBL | 0.56% | 697 | 64 | 0.0099% / 0.0229% (3) |
| MUL | 0.54% | 675 | 56 | 0.0018% / 0.0101% (7) |
| RES | 0.46% | 578 | 20 | 0.0126% / 0.0186% (2) |
| DIV | 0.45% | 560 | 56 | 0.0018% / 0.0101% (7) |
| CONCAT | 0.41% | 511 | 104 | 0.0106% / 0.0240% (3) |
| FLL | 0.39% | 490 | 68 | 0.0055% / 0.0088% (2) |
| CTU | 0.35% | 434 | 20 | 0.0126% / 0.0186% (2) |
| CPS | 0.31% | 385 | 112 | 0.0102% / 0.0234% (3) |
| CPT | 0.27% | 341 | not a flat weight | 3.2725% / 119.6078% (164) |
| MOD | 0.23% | 289 | 56 | 0.0018% / 0.0101% (7) |
| RET | 0.20% | 246 | 0 | — |
| MCCP | 0.16% | 200 | 204 | 0.0000% / 0.0000% (1) step |
| AFI | 0.15% | 192 | 4 | 0.0126% / 0.0186% (2) |
| MAS | 0.15% | 186 | 100 | — |
| GSV | 0.15% | 182 | 84 | 0.0116% / 0.0255% (3) |
| BTD | 0.12% | 147 | 64 | 0.0058% / 0.0092% (2) |
| SSV | 0.10% | 128 | 84 | 0.0116% / 0.0255% (3) |
| MAM | 0.10% | 127 | 224 | 0.0244% / 0.0244% (1) |
| MAPC | 0.10% | 126 | 260 | **Exact** — 260/call, step 1→10 at 0.0000% |
| SBR | 0.10% | 121 | 0 | — |
| DTOS | 0.09% | 114 | 72 | 0.0053% / 0.0084% (2) |
| TOF | 0.09% | 107 | 20 | 0.0126% / 0.0186% (2) |
| MEQ | 0.06% | 78 | 32 | 0.0072% / 0.0113% (2) |
| CMP | 0.06% | 77 | 76 | 0.0194% / 0.2380% (14) |
| RTO | 0.06% | 74 | 20 | 0.0126% / 0.0186% (2) |
| EVENT | 0.05% | 57 | 56 | 0.0000% / 0.0000% (1) |
| AVE | 0.05% | 57 | 176 | 0.0000% / 0.0000% (1) step |
| ABS | 0.04% | 55 | 120 | 0.0099% / 0.0229% (3) |
| BSL | 0.03% | 43 | 60 | 0.0067% / 0.0083% (2) |
| MRP | 0.03% | 42 | 128 | — |
| SIZE | 0.03% | 42 | 128 | 0.0096% / 0.0224% (3) |
| MAG | 0.03% | 37 | 124 | 0.0000% / 0.0000% (1) |
| MAW | 0.03% | 37 | 128 | — |
| BSR | 0.03% | 34 | 60 | 0.0052% / 0.0083% (3) |
| MDW | 0.03% | 34 | 60 | 0.0000% / 0.0000% (1) step |
| MVM | 0.03% | 32 | 56 | 0.0064% / 0.0101% (2) |
| MAH | 0.02% | 30 | 60 | — |
| MAJ | 0.02% | 29 | 236 | 0.0240% / 0.0240% (1) |
| MCSV | 0.02% | 25 | 96 | 0.0000% / 0.0000% (2) |
| XOR | 0.02% | 23 | 40 | 0.0000% / 0.0000% (1) step |
| AND | 0.02% | 23 | 40 | 0.0067% / 0.0067% (1) |
| MASR | 0.02% | 21 | 60 | 0.0000% / 0.0000% (1) step |
| MAFR | 0.02% | 21 | 60 | 0.0000% / 0.0000% (1) step |
| MAR | 0.01% | 17 | 196 | 0.0255% / 0.0255% (1) |
| MSG | 0.01% | 16 | 48 | 0.0000% / 0.0000% (1) step |
| FFL | 0.01% | 15 | 72 | 0.0000% / 0.0000% (1) step |
| XPY | 0.01% | 14 | 116 | 0.0101% / 0.0232% (3) |
| MDR | 0.01% | 14 | 68 | — |
| FFU | 0.01% | 13 | 72 | 0.0000% / 0.0000% (1) step |
| NOT | 0.01% | 12 | 40 | 0.0000% / 0.0000% (1) step |
| MSO | 0.01% | 12 | 60 | — |
| MSF | 0.01% | 12 | 60 | — |
| STOD | 0.01% | 10 | 80 | 0.0118% / 0.0259% (3) |
| ATN | 0.01% | 10 | 60 | 0.0000% / 0.0000% (1) step |
| DEG | 0.01% | 10 | 64 | 0.0000% / 0.0000% (1) step |
| STOR | 0.01% | 10 | 80 | 0.0000% / 0.0000% (2) |
| NEG | 0.01% | 9 | 40 | 0.0000% / 0.0000% (1) step |
| UID | 0.01% | 8 | 40 | 0.0000% / 0.0000% (2) |
| UIE | 0.01% | 8 | 40 | 0.0000% / 0.0000% (2) |
| MID | 0.01% | 8 | 100 | 0.0108% / 0.0243% (3) |
| DELETE | 0.01% | 8 | 100 | 0.0108% / 0.0243% (3) |
| TAN | 0.01% | 7 | 60 | 0.0000% / 0.0000% (1) step |
| SRT | 0.01% | 7 | 116 | 0.0000% / 0.0000% (1) step |
| MCD | 0.01% | 7 | 184 | 0.0000% / 0.0000% (2) |
| RAD | 0.00% | 6 | 116 | 0.0000% / 0.0000% (1) step |
| TRN | 0.00% | 4 | 52 | 0.0000% / 0.0000% (1) step |
| SQR | 0.00% | 4 | 52 | 0.0000% / 0.0000% (1) step |
| OR | 0.00% | 4 | 40 | 0.0067% / 0.0067% (1) |
| SWPB | 0.00% | 4 | 76 | 0.0000% / 0.0000% (1) step |
| ESTOP | 0.00% | 4 | **unweighted** | — |
| ROUT | 0.00% | 4 | **unweighted** | — |
| FOR | 0.00% | 2 | 80 | — |
| RTOS | 0.00% | 2 | 72 | 0.0095% / 0.0146% (2) |
| FIND | 0.00% | 2 | 100 | 0.0000% / 0.0000% (1) step |
| MASD | 0.00% | 2 | 60 | 0.0000% / 0.0000% (1) step |
| MGSD | 0.00% | 2 | 56 | 0.0000% / 0.0000% (1) step |
| MGSR | 0.00% | 2 | 56 | 0.0000% / 0.0000% (1) step |
| FSC | 0.00% | 2 | 104 | 0.0000% / 0.0000% (1) step |
| LC | 0.00% | 2 | **unweighted** | — |
| SCP | 0.00% | 1 | **unweighted** | — |
| LOG | 0.00% | 1 | 60 | 0.0000% / 0.0000% (1) |
| COS | 0.00% | 1 | 60 | 0.0000% / 0.0000% (1) |
| SIN | 0.00% | 1 | 60 | 0.0000% / 0.0000% (1) |
| INSERT | 0.00% | 1 | 116 | 0.0000% / 0.0000% (1) step |
| RIN | 0.00% | 1 | **unweighted** | — |

## The unweighted remainder

Six mnemonics, 353 occurrences, 0.282% of all real logic.

| mnemonic | occurrences | status |
|---|---:|---|
| CPT | 341 | **Not a flat weight by design.** Priced per call from its own expression's operator tokens. Deliberately absent from the weight table so the per-mnemonic loop cannot double-count it. |
| ESTOP | 4 | Safety-family instruction. Out of scope. |
| ROUT | 4 | Safety-family instruction. Out of scope. |
| LC | 2 | Never tested. Below the noise floor. |
| SCP | 1 | Never tested. Below the noise floor. |
| RIN | 1 | Safety-family instruction. Out of scope. |

**CPT is the one that matters**, and it is not a gap — it is the one instruction
whose cost genuinely cannot be a flat per-rung number. Its expression model is in
`MEMORY_MODEL.md`. The known defect there is narrow-integer widening, which reads
as the worst measured accuracy of any instruction in the table.

**SCP and LC are the only genuinely untested mnemonics in real use**, at three
occurrences between them. Deliberately not worked: a precise number on a negligible
feature is a day not spent on the residual.

## Instructions that are out of scope or will not build

**Safety family** — DCS, CROUT, ROUT, ESTOP, RIN. These require a safety CPU. Not
weight-table gaps; there is nothing to fix on a standard controller. **Ignored, not
parked:** no test file is built for any of them, and `instrfirst_crout_x10`'s failed
build is not pursued.

**ALMD, ALMA, ALARM_DIGITAL and ALARM_ANALOG as instructions** — zero occurrences
across all real programs. Parked, not closed. This does **not** park tag-based
alarm conditions, which are a different feature and are 19–21% of total memory on
the two real programs measured.

**MAM, MAJ, MAS and MRP** fail to build with the bare 2-operand
`(Axis, MotionInstruction)` signature that works for MAH and MSO. Each needs its
own full parameter list. A verified MAM shape, transplanted from a project Studio
compiled, is in `MEMORY_MODEL.md`. **Do not retry with a guessed variant.**

**CTD** is untested deliberately — zero real usage.
