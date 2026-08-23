# Instruction Coverage

What fraction of real logic is actually sized with confidence, instruction
by instruction — James, 2026-08-23: "generate a table of all of the
instructions natively supported on the controller, column with how
confident you are on calculating size, and a column with how often it's
used in the full sample programs I gave (both the new dnr set and the
original set)... I'll probably push you to be 100% confident for all of
the used instructions."

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
- **A real bug caught building this table:** the first pass of the
  analysis script used a strict `<Text><![CDATA[...]]></Text>` regex with
  no whitespace tolerance — most of this project's own generated samples
  export that way (single line), but a lot of real Studio-5000-exported
  files pretty-print it across multiple lines
  (`<Text>\n<![CDATA[...]]>\n</Text>`). That silently undercounted real
  usage by ~98% (3,036 occurrences found vs 201,393 once fixed). **This
  was a bug in the scratch analysis script only, not in the production
  parser** — `parser/logic.py` uses `xml.etree.ElementTree`'s real DOM
  `.find("Text")`/`.text`, which is whitespace-agnostic by construction
  and was never affected. Worth knowing about if anyone hand-rolls another
  regex-based corpus scan in the future: pretty-printed real exports are
  common, don't assume compact single-line formatting.
- **Side finding from the fix:** `CTD` was previously believed to have
  *zero* real corpus usage (`docs/MEMORY_MODEL.md`: "CTD intentionally not
  tested — zero real usage in the corpus, OQ-INSTRUCTIONSCOPE"). With the
  regex fixed, there's 1 real occurrence. Doesn't change the practical
  conclusion (1 occurrence out of 201,393 is still not worth a dedicated
  test), but the "zero" claim itself was an artifact of the same
  undercounting bug, not literally true — worth a quiet correction in
  MEMORY_MODEL.md next time that section is touched.

## Confidence categories

- **CONFIRMED** — exact fit (0.00% residual) against real Capacity data,
  correctly wired into `memory_model.yaml`/the engine.
- **WRONG** — wired into the engine, but proven incorrect by real data
  (CPT only — see `docs/OPEN_QUESTIONS.md` OQ-CMPCPTLAYOUT's 2026-08-23
  correction. The engine currently still applies this wrong weight because
  removing it and implying 0 cost would be worse, not because it's
  trusted).
- **WIRED (unvalidated split)** — a real, exact combined weight exists but
  had to be split between two instructions without independent data (LBL/
  JMP's 52/52 split of a confirmed-104 combined weight, valid only for the
  1:1 pairing this project has tested).
- **DERIVED not wired** — a real per-rung weight has been calculated from
  real data but isn't in `memory_model.yaml`/the engine yet (MAH/MSO, 60/
  rung, see `docs/OPEN_QUESTIONS.md` item 9) — contributes 0 to any
  estimate right now, a one-line fix once someone gets to it.
- **FLAGGED for re-capture** — a real syntax bug in the sample generator
  was found and fixed (missing array-subscript on an array-typed operand)
  but the corrected files haven't been re-captured yet (CPS/COP/FLL/BTD).
  Contributes 0 to any estimate right now.
- **NO DATA** — never tested at all. Contributes 0 to any estimate. The
  large majority of these are low-single-digit-occurrence instructions
  (math functions, shift/search/sort array ops, motion camming) that
  together are a rounding error of total real usage — see the summary
  below — but a few meaningfully-used ones stand out (RET/SBR, MSG, MAM/
  MAJ/MAS/MRP, INSERT) as real gaps worth prioritizing over the long tail.
- **OUT OF SCOPE** — DCS is a GuardLogix Safety instruction; this project
  is explicitly out-of-scope for Safety programs (`CLAUDE.md` OQ-SAFETY).
  Still shown here since it's real corpus usage, just not something this
  project will ever try to size.

## Coverage summary (by real occurrence, not by distinct instruction count)

| Status | Occurrences | % of all native instruction usage |
|---|---|---|
| CONFIRMED | 191,517 | 95.10% |
| FLAGGED for re-capture | 4,316 | 2.14% |
| WIRED (unvalidated split) | 2,281 | 1.13% |
| NO DATA | 2,229 | 1.11% |
| WRONG | 840 | 0.42% |
| DERIVED not wired | 145 | 0.07% |
| OUT OF SCOPE | 65 | 0.03% |

**95.1% of every real instruction occurrence across the whole corpus is
already an exact, confirmed fit.** The remaining ~4.9% breaks down into 4
already-understood, already-scoped gaps (re-capture pending, an
unvalidated LBL/JMP split, a known-wrong CPT constant, a derived-but-
unwired MAH/MSO weight) plus a genuine long tail of never-tested,
low-usage instructions.

## Full table

100 distinct native instructions found across 201,393 real RLL rung
occurrences, 54 real corpus files (spans the original set and the
`DnR_Personal` set together, not broken out separately — usage patterns
were consistent enough across both that a combined ranking is more useful
than two separate small tables; ask if a split view is wanted later).

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
| COP | 1.27% | 2550 | FLAGGED for re-capture (syntax bug fixed, 0 contribution until data lands) |
| JSR | 1.14% | 2300 | CONFIRMED (exact fit, 0.00% residual) |
| SUB | 0.95% | 1909 | CONFIRMED (exact fit, 0.00% residual) |
| GEQ | 0.91% | 1823 | CONFIRMED (exact fit, 0.00% residual) |
| LIM | 0.74% | 1488 | CONFIRMED (exact fit, 0.00% residual) |
| JMP | 0.67% | 1347 | WIRED (52/52 split unvalidated beyond 1:1 LBL:JMP pairing) |
| LEQ | 0.63% | 1275 | CONFIRMED (exact fit, 0.00% residual) |
| RES | 0.58% | 1171 | CONFIRMED (exact fit, 0.00% residual) |
| MUL | 0.54% | 1092 | CONFIRMED (exact fit, 0.00% residual) |
| DIV | 0.50% | 1016 | CONFIRMED (exact fit, 0.00% residual) |
| LBL | 0.46% | 934 | WIRED (52/52 split unvalidated beyond 1:1 LBL:JMP pairing) |
| CONCAT | 0.43% | 858 | CONFIRMED (exact fit, 0.00% residual) |
| CPT | 0.42% | 840 | WRONG (wired, proven incorrect -- see CPT finding) |
| AFI | 0.42% | 836 | CONFIRMED (exact fit, 0.00% residual) |
| FLL | 0.41% | 817 | FLAGGED for re-capture (syntax bug fixed, 0 contribution until data lands) |
| CTU | 0.33% | 656 | CONFIRMED (exact fit, 0.00% residual) |
| CPS | 0.27% | 551 | FLAGGED for re-capture (syntax bug fixed, 0 contribution until data lands) |
| GSV | 0.26% | 531 | CONFIRMED (exact fit, 0.00% residual) |
| BTD | 0.20% | 398 | FLAGGED for re-capture (syntax bug fixed, 0 contribution until data lands) |
| DTOS | 0.19% | 389 | CONFIRMED (exact fit, 0.00% residual) |
| MOD | 0.19% | 383 | CONFIRMED (exact fit, 0.00% residual) |
| SSV | 0.16% | 318 | CONFIRMED (exact fit, 0.00% residual) |
| TOF | 0.14% | 292 | CONFIRMED (exact fit, 0.00% residual) |
| RTO | 0.13% | 262 | CONFIRMED (exact fit, 0.00% residual) |
| MAS | 0.12% | 249 | NO DATA (0 contribution -- never tested) |
| RET | 0.12% | 237 | NO DATA (0 contribution -- never tested) |
| MID | 0.11% | 212 | CONFIRMED (exact fit, 0.00% residual) |
| CMP | 0.10% | 203 | CONFIRMED (exact fit, 0.00% residual) |
| INSERT | 0.10% | 192 | NO DATA (0 contribution -- never tested) |
| MAM | 0.09% | 186 | NO DATA (0 contribution -- never tested) |
| MCCP | 0.06% | 129 | NO DATA (0 contribution -- never tested) |
| SBR | 0.06% | 128 | NO DATA (0 contribution -- never tested) |
| MAPC | 0.06% | 113 | NO DATA (0 contribution -- never tested) |
| MAJ | 0.05% | 106 | NO DATA (0 contribution -- never tested) |
| MSG | 0.05% | 99 | NO DATA (0 contribution -- never tested) |
| MEQ | 0.05% | 94 | CONFIRMED (exact fit, 0.00% residual) |
| SIZE | 0.05% | 92 | CONFIRMED (exact fit, 0.00% residual) |
| ABS | 0.05% | 91 | CONFIRMED (exact fit, 0.00% residual) |
| MAH | 0.04% | 79 | DERIVED not wired (60/rung known, 0 contribution until wired) |
| DELETE | 0.04% | 78 | CONFIRMED (exact fit, 0.00% residual) |
| AVE | 0.03% | 69 | NO DATA (0 contribution -- never tested) |
| MVM | 0.03% | 68 | CONFIRMED (exact fit, 0.00% residual) |
| MSO | 0.03% | 66 | DERIVED not wired (60/rung known, 0 contribution until wired) |
| DCS | 0.03% | 65 | OUT OF SCOPE (Safety instruction, CLAUDE.md OQ-SAFETY) |
| TND | 0.03% | 59 | NO DATA (0 contribution -- never tested) |
| MAFR | 0.03% | 58 | NO DATA (0 contribution -- never tested) |
| MASR | 0.03% | 57 | NO DATA (0 contribution -- never tested) |
| XPY | 0.02% | 42 | CONFIRMED (exact fit, 0.00% residual) |
| MRP | 0.02% | 41 | NO DATA (0 contribution -- never tested) |
| MDW | 0.02% | 36 | NO DATA (0 contribution -- never tested) |
| BSL | 0.02% | 34 | NO DATA (0 contribution -- never tested) |
| CROUT | 0.02% | 33 | NO DATA (0 contribution -- never tested) |
| NEG | 0.02% | 33 | NO DATA (0 contribution -- never tested) |
| STOD | 0.02% | 31 | CONFIRMED (exact fit, 0.00% residual) |
| BSR | 0.01% | 29 | NO DATA (0 contribution -- never tested) |
| TRN | 0.01% | 29 | NO DATA (0 contribution -- never tested) |
| FFU | 0.01% | 28 | NO DATA (0 contribution -- never tested) |
| FFL | 0.01% | 26 | NO DATA (0 contribution -- never tested) |
| NOT | 0.01% | 24 | NO DATA (0 contribution -- never tested) |
| FAL | 0.01% | 24 | NO DATA (0 contribution -- never tested) |
| FSC | 0.01% | 21 | NO DATA (0 contribution -- never tested) |
| FIND | 0.01% | 21 | NO DATA (0 contribution -- never tested) |
| XOR | 0.01% | 21 | NO DATA (0 contribution -- never tested) |
| OSR | 0.01% | 16 | NO DATA (0 contribution -- never tested) |
| OSF | 0.01% | 13 | NO DATA (0 contribution -- never tested) |
| UID | 0.01% | 12 | NO DATA (0 contribution -- never tested) |
| UIE | 0.01% | 12 | NO DATA (0 contribution -- never tested) |
| SRT | 0.01% | 12 | NO DATA (0 contribution -- never tested) |
| SWPB | 0.00% | 9 | NO DATA (0 contribution -- never tested) |
| ATN | 0.00% | 9 | NO DATA (0 contribution -- never tested) |
| DEG | 0.00% | 9 | NO DATA (0 contribution -- never tested) |
| FBC | 0.00% | 8 | NO DATA (0 contribution -- never tested) |
| MASD | 0.00% | 7 | NO DATA (0 contribution -- never tested) |
| TAN | 0.00% | 7 | NO DATA (0 contribution -- never tested) |
| MDR | 0.00% | 6 | NO DATA (0 contribution -- never tested) |
| MGSD | 0.00% | 5 | NO DATA (0 contribution -- never tested) |
| MGSR | 0.00% | 5 | NO DATA (0 contribution -- never tested) |
| RAD | 0.00% | 5 | NO DATA (0 contribution -- never tested) |
| PID | 0.00% | 3 | NO DATA (0 contribution -- never tested) |
| MCR | 0.00% | 2 | NO DATA (0 contribution -- never tested) |
| SQR | 0.00% | 2 | NO DATA (0 contribution -- never tested) |
| SCP | 0.00% | 2 | NO DATA (0 contribution -- never tested) |
| LFU | 0.00% | 1 | NO DATA (0 contribution -- never tested) |
| CTD | 0.00% | 1 | NO DATA (previously believed zero real usage -- corrected 2026-08-23, 1 real occurrence found) |
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

Ranked by real occurrence count among non-CONFIRMED rows — this is the
priority order if the goal is closing the 4.9% gap fastest, not
alphabetical or by category:

1. **COP (2,550), FLL (817), CPS (551), BTD (398)** — 4,316 occurrences,
   2.14% of the whole corpus. Generator bug already fixed, files already
   regenerated (`gen_logic_sweep.py`), purely waiting on a re-capture
   batch. The single highest-leverage thing to close next — no analysis
   work needed, just data.
2. **CPT (840)** — 0.42%, but disproportionately important since it's not
   just "no data," it's actively wrong. Needs the per-operand/operator
   cost model described in `docs/OPEN_QUESTIONS.md` OQ-CMPCPTLAYOUT — the
   new `gen_cmpcpt_complexity.py` sweep (2026-08-23) exists specifically
   to gather the data for this.
3. **LBL (934) / JMP (1,347)** — 2,281 combined, 1.13%. Already has a
   real combined weight, just needs the 1:1-only split resolved with
   independent data — `gen_lbljmp_rules.py`'s many-JMP-to-one-LBL and
   LBL-with-no-JMP files (2026-08-23) target exactly this.
4. **MAH (79) / MSO (66)** — 145 combined, 0.07%. Already derived (60/
   rung), just needs a one-line addition to `memory_model.yaml`.
5. **RET (237) / SBR (128)** — 365 combined, 0.18%. No data at all yet.
   `gen_jsr_sbr_ret.py` (2026-08-23) now covers this.
6. **MSG (99), INSERT (192), MAM/MAJ/MAS/MRP/MAPC/MCCP (motion, ~830
   combined)** — real but lower-frequency; worth a future sweep batch, not
   urgent.
7. Everything else (shift/search/sort/trig/math misc, <30 occurrences
   each) — long tail, diminishing returns, not worth a dedicated sweep
   until/unless a specific real program shows heavy usage of one of them.
