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
  syntax doesn't actually work in Studio 5000 (MAM/MAJ/MAS/MRP, 2026-08-25:
  every single rung of every real capture file errored). Contributes 0.
  Do NOT retry with a guessed variant — needs a real corpus or Studio-
  5000-verified reference for the correct call shape first.
- **CAPTURED, blocked on unmodeled structure** — real n=1 data exists but
  can't be turned into a weight yet because the instruction also needs a
  brand-new predefined structure (CAM for MCCP/MAPC, MESSAGE for MSG) that
  has no byte-size formula of its own yet. Contributes 0 until that
  structure is resolved.
- **CAPTURED (preliminary)** — real n=1 data exists and looks clean, but
  per James's own explicit methodology ("let's do a 10-count test for
  each... if something comes out of line then we can do more per
  instruction testing as required") nothing gets wired into
  `memory_model.yaml` off a single data point. `_x10` files exist for all
  of these (`gen_instruction_firstpass.py`), awaiting capture. Contributes
  0 to any estimate right now — this is a deliberate, temporary zero, not
  an oversight.
- **NO DATA** — never tested at all. Contributes 0 to any estimate.
- **OUT OF SCOPE** — DCS is a GuardLogix Safety instruction; this project
  is explicitly out-of-scope for Safety programs (`CLAUDE.md` OQ-SAFETY).

## Coverage summary (by real occurrence, not by distinct instruction count)

| Status | Occurrences | % of all native instruction usage |
|---|---|---|
| CONFIRMED | 198,259 | 98.44% |
| CAPTURED (preliminary, x10 pending) | 919 | 0.46% |
| WRONG | 840 | 0.42% |
| BUILD FAILED | 582 | 0.29% |
| NO DATA | 387 | 0.19% |
| CAPTURED, blocked on CAM structure | 242 | 0.12% |
| CAPTURED, blocked on MESSAGE structure | 99 | 0.05% |
| OUT OF SCOPE | 65 | 0.03% |

**98.44% of every real instruction occurrence across the whole corpus is
already an exact, confirmed fit** — up from 95.10% on 2026-08-23, after
processing a backlog of already-captured real data (BTD/COP/CPS/FLL
resolved, LBL/JMP corrected and fully decomposed, MAH/MSO wired). The
remaining 1.56% is now almost entirely EITHER already-captured-and-
awaiting-a-second-data-point (0.46% CAPTURED preliminary, 0.17% blocked
on a new predefined structure) OR a real negative result that needs a
better reference before retrying (0.29% BUILD FAILED) — genuinely
never-tested instructions are down to 0.19% of all real usage.

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
| JSR | 1.14% | 2300 | CONFIRMED (exact fit, 0.00% residual) |
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
| MAS | 0.12% | 249 | BUILD FAILED (real capture 2026-08-25: documented syntax rejected by Studio 5000, every rung errored) |
| RET | 0.12% | 237 | NO DATA (0 contribution -- never tested; structurally tied to JSR/SBR, can't be isolated as a bare instruction) |
| MID | 0.11% | 212 | CONFIRMED (exact fit, 0.00% residual) |
| CMP | 0.10% | 203 | CONFIRMED (exact fit, 0.00% residual) |
| INSERT | 0.10% | 192 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| MAM | 0.09% | 186 | BUILD FAILED (real capture 2026-08-25: documented syntax rejected by Studio 5000, every rung errored) |
| MCCP | 0.06% | 129 | CAPTURED, blocked on unmodeled CAM structure (n=1 real data in hand) |
| SBR | 0.06% | 128 | NO DATA (0 contribution -- never tested; structurally tied to JSR, can't be isolated as a bare instruction) |
| MAPC | 0.06% | 113 | CAPTURED, blocked on unmodeled CAM structure (n=1 real data in hand) |
| MAJ | 0.05% | 106 | BUILD FAILED (real capture 2026-08-25: documented syntax rejected by Studio 5000, every rung errored) |
| MSG | 0.05% | 99 | CAPTURED, blocked on unmodeled MESSAGE structure (n=1 real data in hand) |
| MEQ | 0.05% | 94 | CONFIRMED (exact fit, 0.00% residual) |
| SIZE | 0.05% | 92 | CONFIRMED (exact fit, 0.00% residual) |
| ABS | 0.05% | 91 | CONFIRMED (exact fit, 0.00% residual) |
| MAH | 0.04% | 79 | CONFIRMED (exact fit, 0.00% residual) |
| DELETE | 0.04% | 78 | CONFIRMED (exact fit, 0.00% residual) |
| AVE | 0.03% | 69 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| MVM | 0.03% | 68 | CONFIRMED (exact fit, 0.00% residual) |
| MSO | 0.03% | 66 | CONFIRMED (exact fit, 0.00% residual) |
| DCS | 0.03% | 65 | OUT OF SCOPE (Safety instruction, CLAUDE.md OQ-SAFETY) |
| TND | 0.03% | 59 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| MAFR | 0.03% | 58 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| MASR | 0.03% | 57 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| XPY | 0.02% | 42 | CONFIRMED (exact fit, 0.00% residual) |
| MRP | 0.02% | 41 | BUILD FAILED (real capture 2026-08-25: documented syntax rejected by Studio 5000, every rung errored) |
| MDW | 0.02% | 36 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| BSL | 0.02% | 34 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| CROUT | 0.02% | 33 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| NEG | 0.02% | 33 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| STOD | 0.02% | 31 | CONFIRMED (exact fit, 0.00% residual) |
| BSR | 0.01% | 29 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| TRN | 0.01% | 29 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| FFU | 0.01% | 28 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| FFL | 0.01% | 26 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| NOT | 0.01% | 24 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| FAL | 0.01% | 24 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| FSC | 0.01% | 21 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| FIND | 0.01% | 21 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| XOR | 0.01% | 21 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| OSR | 0.01% | 16 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| OSF | 0.01% | 13 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| UID | 0.01% | 12 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| UIE | 0.01% | 12 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| SRT | 0.01% | 12 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| SWPB | 0.00% | 9 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| ATN | 0.00% | 9 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| DEG | 0.00% | 9 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| FBC | 0.00% | 8 | NO DATA (0 contribution -- never tested, deliberately skipped rather than guessed, see OQ-INSTRFIRSTPASS) |
| MASD | 0.00% | 7 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| TAN | 0.00% | 7 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| MDR | 0.00% | 6 | NO DATA (0 contribution -- never tested) |
| MGSD | 0.00% | 5 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| MGSR | 0.00% | 5 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| RAD | 0.00% | 5 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| PID | 0.00% | 3 | NO DATA (0 contribution -- never tested, deliberately skipped rather than guessed, see OQ-INSTRFIRSTPASS) |
| MCR | 0.00% | 2 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| SQR | 0.00% | 2 | CAPTURED (n=1 preliminary + x10 files generated, awaiting x10 capture before wiring) |
| SCP | 0.00% | 2 | NO DATA (0 contribution -- never tested, deliberately skipped rather than guessed, see OQ-INSTRFIRSTPASS) |
| LFU | 0.00% | 1 | NO DATA (0 contribution -- never tested) |
| CTD | 0.00% | 1 | NO DATA (deliberately untested, ~0 real corpus usage) |
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

1. **The 33 CAPTURED-preliminary instructions (919 occurrences, 0.46%)**
   — real n=1 data already in hand for every one, `_x10` files already
   generated and sitting in `samples/generated/logic/`
   (`gen_instruction_firstpass.py`). Purely waiting on capture — the
   single highest-leverage thing to close next, no analysis or generation
   work left, just data.
2. **MCCP/MAPC/MSG (341 occurrences, 0.17%)** — blocked on the CAM and
   MESSAGE predefined structures, which have no byte-size formula at all
   yet (real XML shapes are known, sizes aren't). Needs a dedicated CAM/
   MESSAGE-structure sweep (multiple element counts for CAM, since it's
   used as an array; MESSAGE is likely a flat one-time cost, needs at
   least 2 count points to confirm that shape too).
3. **MAM/MAJ/MAS/MRP (582 occurrences, 0.29%)** — confirmed BUILD FAILED,
   the documented 2-operand signature is wrong for these 4 specifically
   (works for MAH/MSO/MAFR/MASR). Needs a real corpus or Studio-5000-
   verified reference for the correct call shape before retrying — do not
   guess again.
4. **CPT (840 occurrences, 0.42%)** — actively WRONG, not just untested.
   Needs the per-operand/operator cost model described in
   `docs/OPEN_QUESTIONS.md` OQ-CMPCPTLAYOUT — `gen_cmpcpt_complexity.py`
   exists to gather the data for this, awaiting capture.
5. **RET (237) / SBR (128)** — 365 combined, 0.18%. Can't be tested as
   bare instructions (always paired with JSR); `gen_jsr_sbr_ret.py`
   covers the JSR/SBR/RET combination, awaiting capture.
6. Everything else (FBC/PID/SCP deliberately skipped rather than guessed,
   plus a long tail of <10-occurrence math/shift/search instructions) —
   diminishing returns, not worth a dedicated sweep until a specific real
   program shows heavy usage of one of them.
