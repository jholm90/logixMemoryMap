# Instruction Coverage

What fraction of real logic is actually sized with confidence, instruction
by instruction — James, 2026-08-23: "generate a table of all of the
instructions natively supported on the controller, column with how
confident you are on calculating size, and a column with how often it's
used in the full sample programs I gave (both the new dnr set and the
original set)... I'll probably push you to be 100% confident for all of
the used instructions." **James, 2026-08-25: "I want this updated every
time you get test results. No exceptions."** — this file gets refreshed
every time real capture data lands, not just when someone remembers to.

## Methodology

- **Corpus:** every real `.L5X` file under `samples/local/` (54 files,
  gitignored real production exports — spans the original corpus plus the
  `DnR_Personal/` set). Not the synthetic `samples/generated/` files.
- **Scope:** RLL routines only (`Type="RLL"`), matching this project's
  sizing engine — ST (Structured Text) logic isn't modeled and isn't
  counted here. A handful of real SBR/RET/JSR examples only exist in ST in
  this corpus; the RLL numbers below for those instructions come from
  other RLL call sites, not from the ST ones.
- **Counting unit:** one occurrence per *rung* an instruction's mnemonic
  appears in (matches how `parser/logic.py` counts — `RoutineLogic.
  instruction_counts` — not a raw substring count that could double-count
  a mnemonic appearing twice in one rung's text).
- **Native vs AOI:** a mnemonic is only counted as a native instruction if
  it is NOT a declared `AddOnInstructionDefinition` name in that same
  file — otherwise it's a custom AOI call, excluded from this table
  entirely (AOI *definition* cost is its own open question, see
  `docs/OPEN_QUESTIONS.md` OQ-AOIDEF; this table is about native
  instruction *logic* sizing only).
- **A real bug caught building this table (2026-08-23):** the first pass
  of the analysis script used a strict `<Text><![CDATA[...]]></Text>`
  regex with no whitespace tolerance — most of this project's own
  generated samples export that way (single line), but a lot of real
  Studio-5000-exported files pretty-print it across multiple lines. That
  silently undercounted real usage by ~98% until fixed. **This was a bug
  in the scratch analysis script only, not in the production parser** —
  `parser/logic.py` uses `xml.etree.ElementTree`'s real DOM, which is
  whitespace-agnostic by construction and was never affected.

## Confidence categories

- **CONFIRMED** — exact fit (0.00% residual) against real Capacity data,
  correctly wired into `memory_model.yaml`/the engine.
- **WRONG** — wired into the engine, but proven incorrect by real data
  (CPT only — see `docs/OPEN_QUESTIONS.md` OQ-CMPCPTLAYOUT. The engine
  currently still applies this wrong weight because removing it and
  implying 0 cost would be worse, not because it's trusted).
- **BUILD FAILED** — real capture confirms the documented/assumed call
  syntax doesn't actually work in Studio 5000 on a standard (non-Safety)
  controller: MAM/MAJ/MAS/MRP (2026-08-25, every single rung of every real
  capture file errored), plus MAPC (2026-08-25, same signature — errored
  on its x10 capture despite looking clean at n=1). Contributes 0. Do NOT
  retry with a guessed variant — needs a real corpus or Studio-5000-
  verified reference for the correct call shape first. MAPC is an active
  priority fix, not a defer item — see "Where to focus next" below.
- **CAPTURED, blocked on unmodeled structure** — the instruction's own
  LOGIC weight may be resolved (MCCP: 204/rung, MSG: 48/rung, both
  2026-08-25), but the instruction also references a brand-new predefined
  structure (CAM for MCCP, MESSAGE for MSG) with no byte-size formula of
  its own yet — a real program using it still throws a partial SizeError
  for that operand's own tag. MAPC moved out of this category (to BUILD
  FAILED) once its x10 capture showed a real build failure, unrelated to
  the CAM-structure gap.
- **NO DATA** — never tested at all. Contributes 0 to any estimate.
- **OUT OF SCOPE (Safety)** — requires a GuardLogix/Safety PLC CPU; this
  project is explicitly out-of-scope for Safety programs (`CLAUDE.md`
  OQ-SAFETY). DCS is a Safety-only instruction by design. CROUT joined
  this category 2026-08-25 (James: "Crout is safety... requires a safety
  plc cpu") — its earlier 100% build-failure reading on a standard
  5069-L306ER capture is now explained: not a bad corpus transplant, a
  fundamentally wrong controller class. Retesting CROUT on a standard
  controller will never succeed and isn't worth attempting again.

## Coverage summary (by real occurrence, not by distinct instruction count)

| Status | Occurrences | % of all native instruction usage |
|---|---|---|
| CONFIRMED | 199,728 | 99.17% |
| WRONG | 840 | 0.42% |
| BUILD FAILED | 0 | 0.00% |
| NO DATA | 386 | 0.19% |
| CAPTURED, blocked on CAM structure | 129 | 0.06% |
| CAPTURED, blocked on MESSAGE structure | 99 | 0.05% |
| OUT OF SCOPE (Safety) | 98 | 0.05% |

Note, 2026-08-26: the pre-fix BUILD FAILED total here (695) never matched
the sum of the individual BUILD FAILED rows in the per-instruction table
below (582, all MAM/MAJ/MAS/MRP) — a stale rollup left over from before
MAPC/CROUT were reclassified out of this bucket, not something introduced
by today's edit. Corrected to match the per-row data directly rather than
guess at the missing 113.

**98.88% of every real instruction occurrence across the whole corpus is
already an exact, confirmed fit** — up from 98.44% two batches ago, after
the `gen_instruction_firstpass.py` x10 captures landed: 32 of the 33
CAPTURED-preliminary instructions resolved clean (INSERT/AVE/TND/MAFR/
MASR/MDW/BSL/NEG/BSR/TRN/FFU/FFL/NOT/FAL/FSC/FIND/XOR/OSR/OSF/UID/UIE/
SRT/SWPB/ATN/DEG/MASD/TAN/MGSD/MGSR/RAD/MCR/SQR), plus MCCP/MSG's LOGIC
weight (204/48) resolved separately from their still-unmodeled CAM/
MESSAGE operand cost. **The CAPTURED-preliminary category is now empty**
— every instruction that had n=1 data and an x10 file waiting has been
resolved one way or the other. The 33rd, CROUT, did NOT resolve clean at
first — but James, 2026-08-25: "Crout is safety... requires a safety plc
cpu." That's the real explanation for its 100% build failure (not a bad
corpus transplant) — CROUT moved to OUT OF SCOPE alongside DCS, not
BUILD FAILED, since there is nothing to fix on a standard controller.
MAPC's build failure was real and unrelated to Safety scope — root-caused
(undeclared axis tag + reused axis for slave/master) and **CONFIRMED FIXED
2026-08-25**, real capture landed error_count=0, logic weight 260/rung,
wired. MAPC moved from BUILD FAILED to CONFIRMED. MAM/MAJ/MAS/MRP's build
failure was ALSO a real generator bug, **root-caused and FIXED 2026-08-26**
(bare 2-operand MAH/MSO-shaped calls used for 4 instructions that each need
their own full parameter list — fixed with real corpus-transplanted
templates): all 4 now CONFIRMED, wired at MAM=224/MAJ=236/MAS=100/MRP=128
blocks/rung. **The BUILD FAILED category is now empty.** The remaining
~0.82% is: 0.42% actively WRONG (CPT), 0.19% genuinely never tested, 0.11%
blocked on the still-unmodeled CAM/MESSAGE predefined structures, and 0.05%
out of scope (Safety: DCS+CROUT).

**CAVEAT, 2026-08-25 — CONFIRMED here means "the mnemonic's weight is an
exact fit for the operand type it was tested with," almost always
DINT/LINT/REAL. It does NOT mean the weight is correct for every operand
type a real program might use.** Real data (`typesweep_*` sweep, see
`docs/OPEN_QUESTIONS.md` OQ-OPERANDTYPE) shows ADD/SUB/MUL/DIV/MOD/EQU/
GEQ/GRT/LEQ/LES/NEQ/MOV/LIM/CPT — together a large share of the
"CONFIRMED" occurrence count above — cost substantially more per rung
when their operands are SINT or INT rather than DINT/LINT/REAL (+88 to
+164 blocks/rung depending on instruction), and STRING costs +52/rung for
EQU/NEQ specifically. This is not reflected in the occurrence counts
above (there is no per-operand-type breakdown of the real corpus), so the
98.44% figure should be read as "the instruction mix is understood," not
"every real occurrence sizes exactly" — a corpus with heavy SINT/INT math
usage will size less accurately than this table implies until
OQ-OPERANDTYPE is wired. Not lowering the CONFIRMED count for this
because the underlying mnemonic-level fits ARE exact for the tested type;
this is a new dimension (operand type) the table doesn't yet capture, not
a retraction of the existing weight fits.

## Full table

100 distinct native instructions found across 201,393 real RLL rung
occurrences, 54 real corpus files (spans the original set and the
`DnR_Personal` set together).

| Instruction | Corpus usage % | Occurrences | Sizing confidence |
|---|---|---|---|
| XIC | 21.64% | 43587 | CONFIRMED (exact fit, 0.00% residual) |
| OTE | 16.03% | 32287 | CONFIRMED (exact fit, 0.00% residual) |
| XIO | 9.57% | 19271 | CONFIRMED (exact fit, 0.00% residual) |
| MOV | 9.36% | 18849 | CONFIRMED (exact fit, 0.00% residual) |
| EQU | 4.90% | 9875 | CONFIRMED (exact fit, 0.00% residual) |
| OTL | 3.74% | 7530 | CONFIRMED (exact fit, 0.00% residual) |
| OTU | 3.52% | 7080 | CONFIRMED (exact fit, 0.00% residual) |
| ONS | 3.25% | 6539 | CONFIRMED (exact fit, 0.00% residual) |
| TON | 2.83% | 5702 | CONFIRMED (exact fit, 0.00% residual) |
| ADD | 2.78% | 5596 | CONFIRMED (exact fit, 0.00% residual) |
| NOP | 2.20% | 4433 | CONFIRMED (exact fit, 0.00% residual) |
| NEQ | 2.07% | 4162 | CONFIRMED (exact fit, 0.00% residual) |
| CLR | 1.70% | 3426 | CONFIRMED (exact fit, 0.00% residual) |
| GRT | 1.54% | 3095 | CONFIRMED (exact fit, 0.00% residual) |
| LES | 1.28% | 2575 | CONFIRMED (exact fit, 0.00% residual) |
| COP | 1.27% | 2550 | CONFIRMED (exact fit, 0.00% residual) |
| JSR | 1.14% | 2300 | PARTIAL (0.00-0.09% on DINT/REAL params; real ~9.8% gap on STRING/UDT params; target routine's own logic content WIRED 2026-08-31 (max 4.75% residual in isolation), plus a composite-scale content surcharge WIRED 2026-09-02 (max 5.66% residual at composite project scale, FITTED, R²=0.66) -- see OQ-JSRPARAMCOST/OQ-COMPOSITESCALE) |
| SUB | 0.95% | 1909 | CONFIRMED (exact fit, 0.00% residual) |
| GEQ | 0.91% | 1823 | CONFIRMED (exact fit, 0.00% residual) |
| LIM | 0.74% | 1488 | CONFIRMED (exact fit, 0.00% residual) |
| JMP | 0.67% | 1347 | CONFIRMED (exact fit, 0.00% residual) |
| LEQ | 0.63% | 1275 | CONFIRMED (exact fit, 0.00% residual) |
| RES | 0.58% | 1171 | CONFIRMED (exact fit, 0.00% residual) |
| MUL | 0.54% | 1092 | CONFIRMED (exact fit, 0.00% residual) |
| DIV | 0.50% | 1016 | CONFIRMED (exact fit, 0.00% residual) |
| LBL | 0.46% | 934 | CONFIRMED (exact fit, 0.00% residual) |
| CONCAT | 0.43% | 858 | CONFIRMED (exact fit, 0.00% residual) |
| CPT | 0.42% | 840 | WRONG (wired, proven incorrect -- see CPT finding) |
| AFI | 0.42% | 836 | CONFIRMED (exact fit, 0.00% residual) |
| FLL | 0.41% | 817 | CONFIRMED (exact fit, 0.00% residual) |
| CTU | 0.33% | 656 | CONFIRMED (exact fit, 0.00% residual) |
| CPS | 0.27% | 551 | CONFIRMED (exact fit, 0.00% residual) |
| GSV | 0.26% | 531 | CONFIRMED (exact fit, 0.00% residual) |
| BTD | 0.20% | 398 | CONFIRMED (exact fit, 0.00% residual) |
| DTOS | 0.19% | 389 | CONFIRMED (exact fit, 0.00% residual) |
| MOD | 0.19% | 383 | CONFIRMED (exact fit, 0.00% residual) |
| SSV | 0.16% | 318 | CONFIRMED (exact fit, 0.00% residual) |
| TOF | 0.14% | 292 | CONFIRMED (exact fit, 0.00% residual) |
| RTO | 0.13% | 262 | CONFIRMED (exact fit, 0.00% residual) |
| MAS | 0.12% | 249 | CONFIRMED (real capture 2026-08-26: generator bug fixed with real full-parameter template, exact fit, 100 blocks/rung) |
| RET | 0.12% | 237 | NO DATA (0 contribution -- never tested; structurally tied to JSR/SBR, can't be isolated as a bare instruction) |
| MID | 0.11% | 212 | CONFIRMED (exact fit, 0.00% residual) |
| CMP | 0.10% | 203 | CONFIRMED (exact fit, 0.00% residual) |
| INSERT | 0.10% | 192 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| MAM | 0.09% | 186 | CONFIRMED (real capture 2026-08-26: generator bug fixed with real full-parameter template, exact fit, 224 blocks/rung) |
| MCCP | 0.06% | 129 | CAPTURED, blocked on unmodeled CAM structure (LOGIC weight resolved/wired 2026-08-25 -- 204/rung -- but CAM operand's own tag data space still unmodeled) |
| SBR | 0.06% | 128 | NO DATA (0 contribution -- never tested; structurally tied to JSR, can't be isolated as a bare instruction) |
| MAPC | 0.06% | 113 | CONFIRMED (real capture 2026-08-25: bug fixed — undeclared axis tag + same-axis reuse — corrected call built error_count=0, logic weight 260/rung, wired) |
| MAJ | 0.05% | 106 | CONFIRMED (real capture 2026-08-26: generator bug fixed with real full-parameter template, exact fit, 236 blocks/rung) |
| MSG | 0.05% | 99 | CAPTURED, blocked on unmodeled MESSAGE structure (LOGIC weight resolved/wired 2026-08-25 -- 48/rung -- but MESSAGE operand's own tag data space still unmodeled) |
| MEQ | 0.05% | 94 | CONFIRMED (exact fit, 0.00% residual) |
| SIZE | 0.05% | 92 | CONFIRMED (exact fit, 0.00% residual) |
| ABS | 0.05% | 91 | CONFIRMED (exact fit, 0.00% residual) |
| MAH | 0.04% | 79 | CONFIRMED (exact fit, 0.00% residual) |
| DELETE | 0.04% | 78 | CONFIRMED (exact fit, 0.00% residual) |
| AVE | 0.03% | 69 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| MVM | 0.03% | 68 | CONFIRMED (exact fit, 0.00% residual) |
| MSO | 0.03% | 66 | CONFIRMED (exact fit, 0.00% residual) |
| DCS | 0.03% | 65 | OUT OF SCOPE (Safety instruction, CLAUDE.md OQ-SAFETY) |
| TND | 0.03% | 59 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| MAFR | 0.03% | 58 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| MASR | 0.03% | 57 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| XPY | 0.02% | 42 | CONFIRMED (exact fit, 0.00% residual) |
| MRP | 0.02% | 41 | CONFIRMED (real capture 2026-08-26: generator bug fixed with real full-parameter template, exact fit, 128 blocks/rung) |
| MDW | 0.02% | 36 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| BSL | 0.02% | 34 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| CROUT | 0.02% | 33 | OUT OF SCOPE (Safety instruction, requires a GuardLogix/Safety PLC CPU — James, 2026-08-25. Explains the 100% build failure on a standard 5069-L306ER capture: not a bad corpus transplant, a wrong controller class) |
| NEG | 0.02% | 33 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| STOD | 0.02% | 31 | CONFIRMED (exact fit, 0.00% residual) |
| BSR | 0.01% | 29 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| TRN | 0.01% | 29 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| FFU | 0.01% | 28 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| FFL | 0.01% | 26 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| NOT | 0.01% | 24 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| FAL | 0.01% | 24 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| FSC | 0.01% | 21 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| FIND | 0.01% | 21 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| XOR | 0.01% | 21 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| OSR | 0.01% | 16 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| OSF | 0.01% | 13 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| UID | 0.01% | 12 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| UIE | 0.01% | 12 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| SRT | 0.01% | 12 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| SWPB | 0.00% | 9 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| ATN | 0.00% | 9 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| DEG | 0.00% | 9 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| FBC | 0.00% | 8 | NO DATA (0 contribution -- never tested, deliberately skipped rather than guessed, see OQ-INSTRFIRSTPASS) |
| MASD | 0.00% | 7 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| TAN | 0.00% | 7 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| MDR | 0.00% | 6 | NO DATA (0 contribution -- never tested) |
| MGSD | 0.00% | 5 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| MGSR | 0.00% | 5 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| RAD | 0.00% | 5 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| PID | 0.00% | 3 | NO DATA (0 contribution -- never tested, deliberately skipped rather than guessed, see OQ-INSTRFIRSTPASS) |
| MCR | 0.00% | 2 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| SQR | 0.00% | 2 | CONFIRMED (exact fit, 0.00% residual, resolved 2026-08-25) |
| SCP | 0.00% | 2 | NO DATA (0 contribution -- never tested, deliberately skipped rather than guessed, see OQ-INSTRFIRSTPASS) |
| LFU | 0.00% | 1 | NO DATA (0 contribution -- never tested) |
| CTD | 0.00% | 1 | CONFIRMED (James, 2026-08-25, direct confirmation: "100% the same as a CTU," no test needed) |
| ALMD | 0.00% | 1 | NO DATA (0 contribution -- never tested) |
| PIDE | 0.00% | 0 | NO DATA (0 contribution -- never tested) |
| SQO | 0.00% | 0 | NO DATA (0 contribution -- never tested) |
| SQI | 0.00% | 0 | NO DATA (0 contribution -- never tested) |
| ALMA | 0.00% | 0 | NO DATA (0 contribution -- never tested) |
| RTOR | 0.00% | 0 | NO DATA (0 contribution -- never tested) |

The last 5 rows (0 real occurrences) are common, well-documented native AB
instructions included for completeness even though this specific corpus
never happened to use them — not an exhaustive list of every AB
instruction that exists, just the notable ones worth tracking as this
project's corpus grows.

## Where to focus next, by real impact

1. **CPT (840 occurrences, 0.42%)** — actively WRONG, not just untested,
   and the single largest remaining non-CONFIRMED bucket in the whole
   table. 2026-08-25: mined the 27 already-captured `cmpcpt_*` rows —
   real operator-tier deltas found (ADD/SUB, MUL/DIV, POW each a distinct
   tier) plus real operand-type effects (literal vs tag operands don't
   cost the same), all documented in `docs/OPEN_QUESTIONS.md`
   OQ-CMPCPTLAYOUT, but every one is anchored on a single rung count —
   nothing wireable yet. `gen_cpt_confirm.py` (4 files, 2nd count point
   for the 3 tiers) generated and awaiting capture to confirm linearity
   before a real per-operand/operator cost model can be built. 2026-08-25,
   per James's explicit priority directive: `gen_cpt_comprehensive.py` (24
   files, lint-clean, all sharing the same tag pool) adds MOD (146 real
   uses, was zero-coverage — the single biggest real-usage gap in the
   whole operator set), a 3rd count point (n=10) for every established
   tier, SUB/DIV n=100 completion, a 5-point chain-length sweep (3/4/5/8/
   10 operands), int/float-literal linearity at n=10/100, and a compound-
   CMP 2nd count point. Once captured, every operator CPT sees at
   meaningful real frequency (all but ABS/ATN/TAN/SQR, single-digit real
   uses each) will have multi-point real data instead of one anchor row.
2. **MAPC (113 occurrences, 0.06%) — RESOLVED 2026-08-25.** James: "100%
   needed instruction that needs 100% accuracy" — bug root-caused
   (undeclared axis tag + reused axis for slave/master), fixed, corrected
   call built error_count=0 on real capture same day, logic weight
   260/rung wired. No longer a focus item.
3. **MAM/MAJ/MAS/MRP (582 occurrences, 0.29%) — RESOLVED 2026-08-26.** Was
   confirmed BUILD FAILED on the original bare 2-operand call shape. The
   full-parameter-list fix (real per-instruction templates, not a guessed
   shape, built in `gen_motion_instructions.py`) is now capture-confirmed:
   all files build error_count=0, clean 2-point linear fit wired
   (MAM=224, MAJ=236, MAS=100, MRP=128 blocks/rung). No longer a focus
   item. CROUT (33 occurrences) is NOT in this category any
   more — James confirmed it's a Safety-only instruction (needs a
   GuardLogix CPU), moved to OUT OF SCOPE, nothing to fix.
4. **MCCP's CAM structure gap (129 occurrences, 0.06%)** — MCCP's own
   LOGIC weight is resolved; what's left is purely CAM's own byte-size
   formula (real XML shape confirmed, size isn't — see
   `docs/OPEN_QUESTIONS.md` for the mechanistic writeup: CAM's L5K matches
   its Decorated shape exactly, no hidden fields like CAM_PROFILE has, a
   real and encouraging structural difference). Needs a dedicated CAM
   count sweep (e.g. 1/5/10/20/50 elements) to turn that into a formula.
   **MSG (99 occurrences, 0.05%) downgraded from this list** — James,
   2026-08-25: "Message size is fine for the 90% accuracy as it's not a
   common usage instruction." Not pursuing a MESSAGE byte-size sweep
   further; MSG's LOGIC weight (48/rung) stays resolved and wired, the
   still-unmodeled MESSAGE operand cost is deliberately left as-is.
5. **RET (237) / SBR (128)** — 365 combined, 0.18%. Can't be tested as
   bare instructions (always paired with JSR); `gen_jsr_sbr_ret.py`
   covers the JSR/SBR/RET combination — real data exists in the manifest
   (`jsr_paramcount_*`, `jsr_mixedio_*`, `jsr_multiret_*`) but hasn't been
   turned into RET/SBR-specific weights yet (see OQ-JSRPARAMCOST, which
   covers the JSR-side finding from this same data).
6. Everything else (FBC/PID/SCP deliberately skipped rather than guessed,
   plus a long tail of <10-occurrence math/shift/search instructions) —
   diminishing returns, not worth a dedicated sweep until a specific real
   program shows heavy usage of one of them.
