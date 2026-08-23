# Memory Model

Single source of truth for every sizing constant, formula, and packing rule.
Parser/calculator code must reference this file's values (as named constants in
whatever config format Phase 0 picks), never hardcode a byte size inline.

Every entry is tagged with a confidence level:
- **KNOWN** — documented AB behavior or trivially derivable, no validation needed
- **ASSUMED** — standard Logix behavior per general knowledge, not yet empirically
  confirmed by this project's own test data (Phase 3/4)
- **FITTED** — derived from regression against sample data, includes residual error
- **UNKNOWN** — placeholder, blocked on an open question

## Atomic data types (KNOWN)

| Type | Bytes | Notes |
|---|---|---|
| BOOL (standalone tag) | 4 | ASSUMED — allocated as DINT, not bit-packed. See OQ-BOOLPACK. |
| BOOL (UDT member) | 1/8 (bit-packed) | Packs 8 per backing SINT byte. See UDT rules below. |
| SINT | 1 | |
| INT | 2 | |
| DINT | 4 | |
| LINT | 8 | |
| REAL | 4 | |
| STRING (built-in) | 4 + 82 = 86 | 4-byte LEN (DINT) + 82-byte DATA (SINT[82]) default |
| Custom string type | 4 + N | 4-byte LEN + N-byte DATA, N = user-defined max length |

## Predefined structure types (KNOWN)

Firmware-native structures referenced by name in L5X Tag/Member DataType
attributes but never given a member list in `Controller/DataTypes` --
Logix Designer resolves them internally, so there's nothing to recurse.
Only types with a well-documented, version-stable layout are modeled here;
everything else found in real samples (MESSAGE, PID, AXIS_CIP_DRIVE and
other motion/safety structures) is deliberately left unsized rather than
guessed -- see OQ-PREDEFINED.

| Type | Bytes | Notes |
|---|---|---|
| TIMER | 12 | 1 status DINT (EN/TT/DN bits) + PRE (DINT) + ACC (DINT) |
| COUNTER | 12 | 1 status DINT (CU/CD/DN/OV/UN bits) + PRE (DINT) + ACC (DINT) |
| CONTROL | 12 | 1 status DINT (EN/EU/DN/EM/ER/UL/IN/FD bits) + LEN/PRE-equivalent (DINT) + POS (DINT) |

## Alias tags (KNOWN)

A Tag with `TagType="Alias"` carries no `DataType` of its own in the L5X
(only an `AliasFor` pointing at another tag or a module I/O point) and
consumes no memory beyond what that target already accounts for. Sized as
0 bytes, tagged `data_type=ALIAS`, confidence KNOWN -- not an error, not a
guess, just genuinely zero-cost. Confirmed against real production L5X data
(2026-08-20): 294 of 3394 tags across 4 real files were Alias tags with no
DataType, ~21% of everything that failed to size before this was handled.

## Per-tag flat overhead (KNOWN, 2026-08-22)

Every top-level `<Tag>` entry (Controller/Tags or Program/Tags) costs a flat
overhead **additive with** its own raw data size (the atomic/predefined/UDT/
array size computed elsewhere in this file): `84 + 8 × floor(name_length /
8)` blocks. Exact fit across 16 independent real data points (13-point
DINT-50-tag count sweep + 3-point REAL-40-tag cross-check at a different
type/count), plus a separate 8/8-point count sweep from 5 to 1000 tags
landing on exactly the same constant at name_length=8 (92 blocks) — two
independently-derived real measurements agreeing exactly, which is why this
is KNOWN rather than FITTED. Tag names are stored in 8-character-aligned
chunks. Type barely affects it (SINT 95/INT 94/DINT 92/LINT 88/REAL 92/BOOL
92 at name_length=8) — treated as type-independent.

Does **not** yet apply to Alias tags — that's OQ-ALIASSIZE, still open
(test built, awaiting capture); Alias tags stay at 0 total until confirmed.

## UDT DataType-definition cost (KNOWN, landed 2026-08-22, corrected same day)

A **one-time** cost per distinct UDT *type definition* actually declared in
the L5X (not per instance, and regardless of whether any tag currently uses
it — see the "def_only, 0 instances" real data below) — additive with both
the per-tag flat overhead above and the tight-packed instance/member size
computed via UDT packing below.

**`160 + 16 × declared_member_count + 8 × ceil(name_length / 8) +
32 × bool_run_count`**, all in ONE formula, verified exact against every
real `udt`-category manifest row with `declared_member_count ≥ 4`.
`declared_member_count` counts members the way a user would (a run of N
BOOL members is still N members, not N+1 — excludes only the hidden
backing SINT itself, not the visible BIT-alias members it backs).
`bool_run_count` is the number of *separate* BOOL runs (each with its own
hidden backing SINT) — a `BOOL, DINT, BOOL` shape has 2, not 1, since the
DINT breaks the run (per OQ-ALIGN).

**Two real bugs found and fixed the same day this first landed, caught by
running the engine against every real tag/udt-category manifest row and
comparing to actual Capacity data (not just unit tests):**

1. The formula was originally implemented as two SEPARATE additive terms —
   `168 + 16×member_count` (from the member-count sweep, name length held
   at 8 chars) PLUS `224 + 8×ceil(name_len/8)` (from the name-length sweep,
   member count held at 4) — because each fit its own sweep exactly in
   isolation. But they're two different 1-D slices through the same
   2-variable surface, both including the same shared base constant;
   adding them together double-counted it (predicting e.g. 416 blocks for
   a real case where actual was 192). Solved the two slices as simultaneous
   equations instead: one true base of **160**, confirmed exact for
   `declared_member_count ≥ 4` (n=1,2 keep the same small-N anomaly already
   documented for tag count, off by a further ~8-16 blocks — not yet
   understood, low priority given it's irrelevant at real-program scale).
2. `bool_run_count` was originally a boolean (`has_bool_run`, +32 flat
   regardless of how many separate runs existed) and computed backwards —
   excluding BIT-alias members instead of hidden ones, so an all-BOOL UDT
   computed `declared_member_count=0`. Fixed to count real declared members
   correctly and apply the bonus once per separate hidden-SINT-backed run.

Also caught the same day: custom STRING types (`Family="StringFamily"`)
were incorrectly getting a udt_definition entry too (this formula was
fit against ordinary UDTs, doesn't apply) — excluded now, but that leaves
a real, still-unexplained gap: every real `customstring_*` data point now
under-predicts by a fairly consistent ~204-208 blocks, meaning custom
string types likely need their **own** one-time definition-cost constant,
not yet derived. Flagged, not guessed at.

Applies only to true UDTs — an AOI-typed tag still sizes exactly like a
UDT instance (see AOI sizing below), but AOI *definition* cost isn't a
confirmed formula yet (an early type/param-count sweep suggested something
like `1184 + 20×n` but was explicitly never formally logged as confirmed),
so no AOI-definition line item is emitted until that lands.

## UDT packing (KNOWN, OQ-ALIGN resolved 2026-08-22)

- Recurse members in declared order.
- BOOL members: pack 8 to a backing SINT byte, per the existing BIT-member
  generation convention (one hidden SINT per byte of BOOL members, incrementing
  BitNumber 0–7, new SINT for bits 8–15, etc).
- Non-BOOL members: size = atomic/nested-UDT size, per table above.
- Alignment/padding between members: **KNOWN, confirmed 2026-08-22 (was
  ASSUMED).** James (100% confident from field experience): `BOOL, DINT,
  BOOL` = 8+32+8 = 6 bytes; `DINT, BOOL, BOOL` = 32+8 = 5 bytes — i.e. no
  4-byte alignment padding at all, and a run of consecutive BOOLs shares one
  backing byte but a non-BOOL member breaks the run, forcing the next
  BOOL(s) onto a fresh backing byte. `compute_udt_size` already produced
  this unchanged (`tests/test_sizing.py::
  test_bool_packing_run_broken_by_non_bool_member`). Now backed by real
  Capacity-tab data too — every real UDT test across the whole per-tag/
  per-UDT-definition sweep (dozens of samples, see per-tag/definition
  sections above) landed on predictions consistent with tight-packing, not
  just James's field opinion. `udt.alignment_confidence` in
  `memory_model.yaml` flipped UNKNOWN→KNOWN.
- Nested UDT: recursive — a UDT member's size is that UDT's total computed
  size. James also believes (stated with less certainty, "I also assume")
  that a nested UDT-typed member always starts fresh rather than packing
  into a partial leftover byte from an adjacent BOOL run — "only BOOLS
  pack." Already true of the implementation: there is no code path that
  merges a nested UDT's bytes into a preceding member's partial byte, so
  this holds by construction, not by an explicit rule that could drift.

## Array sizing

- Array of atomic type: `dimension × element_size`. KNOWN with confidence, no
  packing ambiguity for a single atomic type (BOOL arrays are a known Logix
  special case — BOOL *arrays* bit-pack into DINT-sized words, unlike standalone
  BOOL tags; confirm this distinction explicitly in Phase 3, don't conflate with
  OQ-BOOLPACK).
  - BOOL array formula (ASSUMED, OQ-BOOLARRAY): `ceil(dimension / 32) × 4`
    bytes — 32 bits packed per DINT-sized word. Implemented now since it's
    standard/documented AB behavior, but not yet validated by this project's
    own sample data.
- Array of UDT: `dimension × udt_size`, formula pending OQ-ARRAYPACK (per-element
  vs whole-block padding).
- Multi-dimensional arrays: product of all dimensions × element size, no known
  special case, but not yet tested at scale >2D.

## AOI sizing

**Named AOI-instance tags (implemented, Phase 2b, 2026-08-20):** confirmed
against real production L5X data that every AOI-typed tag found there is a
plain named `Tag` with `DataType=<AOIName>`, sized identically to a UDT-typed
tag — no logic/call-site parsing needed for this case, which turned out to be
the overwhelming majority of real usage (660 of 3394 real tags). Recurses the
same as a UDT: `Input`/`Output` usage Parameters + `LocalTags` are storage
members; `InOut` usage Parameters are excluded entirely (a reference to the
caller-scope tag passed in, not a new allocation — this is the one place the
old "confirm params don't duplicate the referenced tag's memory" question
below is actually answered: they don't, because they're not sized at all).
AOI definitions can nest other AOIs as a LocalTag's type, recursed the same
way nested UDTs are, with the same self-reference cycle detection.

Confidence: inherits `udt.alignment_confidence` (now KNOWN, see UDT packing
above) via the same `compute_udt_size` path, since an AOI instance structure
is internally UDT-shaped. One AOI-specific sub-question doesn't reduce to
OQ-ALIGN/OQ-BOOLPACK though — see OQ-AOIBOOLPACK: unlike UDT members, AOI
Parameters/LocalTags of type BOOL show up in L5X as plain `DataType="BOOL"`
with no hidden-SINT/BIT-alias representation, so it's not yet confirmed
whether they pack 8-per-byte like a UDT member or allocate unpacked like a
standalone tag. Implemented as unpacked (4 bytes) since that's what the XML
shape actually shows with no basis to assume otherwise, but this is a real
open question, not a confirmed KNOWN fact.

**Inline/anonymous instances and call-site multiplication (OQ-AOIINSTANCE,
still blocked):** a *separate*, smaller question from the above — whether an
AOI called in logic without ever getting its own named backing tag (does
Logix always require one, or can it be anonymous/inline?) allocates memory
per call site the same way. Needs call-site counting from logic parsing,
which is a genuine Phase 1/4 dependency and stays deferred.

## Module / I/O tag sizing

- Local (backplane) I/O: **UNKNOWN**, not yet modeled. Depends on module type
  (input/output point count, analog vs digital) — needs its own type table,
  likely sourced from module EDS/catalog data rather than computed generically.
- Produced/Consumed: **UNKNOWN — OQ-PRODCONS**. Overhead formula not yet
  isolated from base connection cost vs. payload cost vs. consumer count.

## Logic instruction weights (FITTED, 2026-08-22 — not yet wired into the engine)

`delta_blocks = fixed_base + weight × rung_count`, baseline-corrected against
an empty-project baseline of 18,128 blocks. **Every routine also carries a
fixed_base cost of 4,816 blocks** (5,096 for a routine containing a JSR —
the extra 280 is presumably the target subroutine's own routine-definition
overhead), confirmed identical across 42 instructions. Fit from the
244-file per-instruction sweep (`gen_logic_sweep.py`), 5 rung-count points
each (10/50/100/1000/5000), **0.00% residual against the raw per-file
measurement** — an exact linear fit, not a loose regression. **Landed in
code 2026-08-22** — `memory_model.yaml`'s `logic_instructions`,
`parser/logic.py` (RLL rung-text tokenizer), `sizing/logic.py`
(`compute_routine_logic_bytes`), wired into `report.py` as `tier=
"estimated"` entries, separate from the tag/UDT `tier="exact"` entries per
CLAUDE.md's ground-truth constraint.

**Correction, same day as first landed:** several sweep files' rung text
isn't just the named instruction — e.g. XIC's file is literally
`"XIC(tag)OTE(tag);"`, not `"XIC(tag);"` alone, because a bare XIC can't
legally close a rung. The table below shows the raw *per-file* measured
weight (still 0.00% residual, still real) next to the **isolated
per-instruction weight** actually used by the engine — decomposed using
OTE's own clean 16 (its file, `"OTE(tag);"`, has no companion) as the
anchor, so summing occurrences of whatever instructions actually appear in
a real rung reconstructs the right total instead of double-counting a
shared companion. Caught by cross-checking the engine's own prediction
against real data for `instr_xic_n01000` (engine said 40,816 before the
fix; real delta was 24,816 — the corrected engine now matches exactly, see
`tests/test_logic_sizing.py`). Composability across *different*
instruction types sharing a rung is exactly what `gen_logic_random_mix.py`
tests, not yet confirmed by real data at that composed level.

5 instructions (CPS, COP, FLL, SIZE, BTD) are excluded below — flagged for
re-capture, see `docs/OPEN_QUESTIONS.md`. The EQU n=100/CMP n=10 garbled-
value glitch this used to also flag is long since fixed and re-captured.
Do not backfill numbers for the still-excluded 5 from other sources; wait
for the re-capture.

**Root cause of the CPS/COP/FLL/SIZE/BTD glitch, found 2026-08-22 (James
spot-checked and caught it):** these instructions take an array-typed
operand, and the generator was emitting the bare tag name (`Arr`) instead
of a subscripted reference (`Arr[0]`) — real Rockwell syntax always
requires `[index]` on an array-typed operand (confirmed against the real
corpus, e.g. `BTD(CNET_ENTRY_STATUS[11],12,...)`). SIZE has the same bug
via its STRING operand, which needs `.DATA[0]`, matching the real corpus
`SIZE(_DisplayBuffer.szString[0],0,...)`. A file with this bug still
converts "ok" through `l5xgit l5x2acd` (see the SDK-verification note
below) — that's why it wasn't caught earlier and why every instance came
back at an identical byte count regardless of rung count (the program
never actually compiled at scale, per James). Fixed in `gen_logic_sweep.py`;
all 5 instructions regenerated and re-flagged for re-capture.

**T_ADD removed entirely, not re-flagged (2026-08-22):** T_ADD is a real
Rockwell-authored `AddOnInstructionDefinition` ("DateTime := DateTime +
Time", found in 18+ real corpus files, Vendor="Rockwell Automation"), not
a native instruction — a misclassification from earlier corpus scanning.
The generated test (`T_ADD(D0,D1,D2,D3)`, four bare DINTs, no AOI
definition, no instance tag) doesn't correspond to any valid real call
shape (real usage: `T_ADD(Wrk_T_ADD5,Wrk_EoDST,Wrk_Offset,Wrk_SoST)`), so
there's no fix that makes the original test meaningful — the 5 files and
their manifest rows were deleted outright rather than queued for
re-capture.

**SDK-verification finding (James asked, 2026-08-22): does `l5xgit
l5x2acd` catch bad programs before James burns real capture time on
them?** No. Confirmed empirically via `samples/convert_log.csv` (398 "ok"
/ 27 "FAILED"): every file affected by both bugs above shows status "ok"
— the SDK's L5X→ACD conversion only opens/parses the project (catching
structural/schema failures like an unsupported ProcessorType — all 27 real
FAILED rows are that class) and does not perform ladder-logic
verification. There's no real Studio-5000-grade verify reachable from this
environment. Mitigation: `src/sample_gen/lint.py`, a local heuristic
pre-flight check wired into every generator's write path, catching exactly
these two error classes (missing array subscript on an array-typed
operand; instruction/AOI call with no matching native-instruction entry or
declared AOI definition in the same file). Not a substitute for real
verification — it only catches classes of error already found the hard
way — but a retroactive sweep of all 586 previously-generated files came
back with 0 findings once its native-instruction whitelist was completed,
which is reasonable (not conclusive) evidence these two bug classes are
now contained.

| Instruction | raw per-file weight | isolated weight (used by engine) | fixed_base | n | Residual |
|---|---|---|---|---|---|
| CPT | 452 | 452 (solo rung) | 4,816 | 5 | 0.00% |
| ABS | 120 | 120 (solo rung) | 4,816 | 5 | 0.00% |
| XPY | 116 | 116 (solo rung) | 4,816 | 5 | 0.00% |
| CONCAT | 104 | 104 (solo rung) | 4,816 | 5 | 0.00% |
| MID | 100 | 100 (solo rung) | 4,816 | 5 | 0.00% |
| DELETE | 100 | 100 (solo rung) | 4,816 | 5 | 0.00% |
| CMP | 92 | **76** (CMP+OTE combined) | 4,816 | 4 | 0.00% |
| LBL/JMP (pair) | 88 | *not decomposed — see note below* | 4,816 | 5 | 0.00% |
| GSV | 84 | 84 (solo rung) | 4,816 | 5 | 0.00% |
| SSV | 84 | 84 (solo rung) | 4,816 | 5 | 0.00% |
| STOD | 80 | 80 (solo rung) | 4,816 | 5 | 0.00% |
| DTOS | 72 | 72 (solo rung) | 4,816 | 5 | 0.00% |
| JSR | 72 | 72 (solo rung) | 5,096 | 5 | 0.00% |

**JSR target routines are skipped entirely by the engine, not charged
their own fixed_base.** Found the same day as the paired-instruction fix
above, same root cause: the JSR sweep's target routine ("SubTest", always
exactly one `NOP();` rung, never varying across the whole 10-5000 count
sweep) had its entire cost absorbed into the calling routine's `5,096`
constant, since it was the same constant across every calibration point.
Charging SubTest its *own* independent `fixed_base_per_routine` on top
(what an early version of `report.py` did) overcounted every JSR-using
program by ~4,832 blocks. `parser/logic.py`'s `RoutineLogic.is_jsr_target`
flags any routine that some other routine in the same program calls via
JSR; `report.py` skips those entirely when building logic entries.
Verified against real data for all 5 JSR count points, exact match. Only
confirmed for a trivial (1-NOP-rung) target — a JSR target with
*substantial* content is untested territory, same caveat as OQ-JSRSHARED.
| LIM | 68 | **52** (LIM+OTE combined) | 4,816 | 5 | 0.00% |
| ONS | 56 | **36** (XIC+ONS+OTE combined) | 4,816 | 5 | 0.00% |
| MUL | 56 | 56 (solo rung) | 4,816 | 5 | 0.00% |
| DIV | 56 | 56 (solo rung) | 4,816 | 5 | 0.00% |
| MOD | 56 | 56 (solo rung) | 4,816 | 5 | 0.00% |
| MVM | 56 | 56 (solo rung) | 4,816 | 5 | 0.00% |
| MEQ | 48 | **32** (MEQ+OTE combined) | 4,816 | 5 | 0.00% |
| ADD | 40 | 40 (solo rung) | 4,816 | 5 | 0.00% |
| SUB | 40 | 40 (solo rung) | 4,816 | 5 | 0.00% |
| MOV | 36 | 36 (solo rung) | 4,816 | 5 | 0.00% |
| EQU | 36 | **20** (EQU+OTE combined) | 4,816 | 4 | 0.00% |
| NEQ | 36 | **20** (NEQ+OTE combined) | 4,816 | 5 | 0.00% |
| GRT | 36 | **20** (GRT+OTE combined) | 4,816 | 5 | 0.00% |
| GEQ | 36 | **20** (GEQ+OTE combined) | 4,816 | 5 | 0.00% |
| LES | 36 | **20** (LES+OTE combined) | 4,816 | 5 | 0.00% |
| LEQ | 36 | **20** (LEQ+OTE combined) | 4,816 | 5 | 0.00% |
| CLR | 32 | 32 (solo rung) | 4,816 | 5 | 0.00% |
| XIC | 20 | **4** (XIC+OTE combined) | 4,816 | 5 | 0.00% |
| XIO | 20 | **4** (XIO+OTE combined) | 4,816 | 5 | 0.00% |
| AFI | 20 | **4** (AFI+OTE combined) | 4,816 | 5 | 0.00% |
| TON | 20 | 20 (solo rung) | 4,816 | 5 | 0.00% |
| TOF | 20 | 20 (solo rung) | 4,816 | 5 | 0.00% |
| RTO | 20 | 20 (solo rung) | 4,816 | 5 | 0.00% |
| CTU | 20 | 20 (solo rung) | 4,816 | 5 | 0.00% |
| RES | 20 | 20 (solo rung) | 4,816 | 5 | 0.00% |
| OTE | 16 | 16 (solo rung, decomposition anchor) | 4,816 | 5 | 0.00% |
| OTL | 16 | 16 (solo rung) | 4,816 | 5 | 0.00% |
| OTU | 16 | 16 (solo rung) | 4,816 | 5 | 0.00% |
| NOP | 16 | 16 (solo rung) | 4,816 | 5 | 0.00% |

LBL/JMP not decomposed or wired into the engine: it's a *pair* measurement
(a paired LBL rung + JMP rung, not one rung with two instructions), and the
sweep doesn't separately isolate LBL's cost from JMP's — needs its own
follow-up before it can be added as two proper per-instruction weights.

CTD intentionally not tested — zero real usage in the corpus (OQ-INSTRUCTIONSCOPE).

**Known gaps, not yet in any sweep (generators built 2026-08-22, awaiting
capture):** motion instructions MAM/MAJ/MAH/MAS/MSO/MRP against a real Axis
tag (`gen_motion_instructions.py` — MAH/MSO's 2-operand call syntax is
corpus-confirmed, the others use the same documented signature but aren't
independently confirmed for that exact mnemonic; MAPC/MCCP camming
skipped, no real call-syntax reference found), per-Task overhead
(`gen_task_overhead.py`, 2nd/3rd Task — distinct from JSR call-site cost,
and note this engine currently charges fixed_base per-*routine* without
knowing whether the real cost is actually per-routine, per-program, or
per-task, since every sweep file had exactly one of each), indirect
addressing overhead (`gen_indirect_addressing.py`, direct vs. indirect
same logic), CMP/CPT operator/layout variance (`gen_cmpcpt_layout.py`).

## Change log

Log every constant change here with date + which sample(s) drove the change, so
there's a record of *why* a number is what it is, not just what it currently is.

- **2026-08-22** — Landed in code (`memory_model.yaml`/`constants.py`/
  `udt.py`/`report.py`): per-tag flat overhead (`84 + 8×floor(len/8)`),
  UDT DataType-definition cost (`168 + 16×member_count` + name cost +
  BOOL-run bonus, one-time per distinct type including nested-only-used
  types), and flipped `udt.alignment_confidence` UNKNOWN→KNOWN (OQ-ALIGN
  resolved).
- **2026-08-22, same day** — Logic instruction weight table also landed in
  code: `parser/logic.py` (RLL rung tokenizer), `sizing/logic.py`
  (`compute_routine_logic_bytes`), wired into `report.py` as
  `tier="estimated"` entries. Caught and fixed a real double-counting bug
  the same day it landed: several sweep files' raw per-file weight was
  really an instruction+companion-OTE combined measurement (e.g. XIC's
  file is `"XIC(tag)OTE(tag);"`, not XIC alone), so naively summing raw
  weights by token occurrence double-counted OTE wherever it appeared as a
  companion. Decomposed 13 instructions (XIC/XIO/AFI/EQU/NEQ/GRT/GEQ/LES/
  LEQ/LIM/MEQ/CMP/ONS) into isolated per-instruction weights using OTE's
  own clean 16 as the anchor. Verified against real captured data for 6
  affected instructions (XIC/ONS/LIM/MEQ/EQU/CMP at n=1000) — engine
  prediction matches real Capacity delta exactly on all 6 after the fix.
  `gen_logic_random_mix.py` (the random-combination validation batch)
  rewritten to predict via the real engine instead of a hand-rolled
  formula, for the same reason.
- **2026-08-22, same day, second fix** — a JSR target routine (e.g.
  "SubTest") was also getting double-counted: the engine charged it its
  own independent `fixed_base_per_routine` on top of the calling routine's
  `jsr_fixed_base_per_routine`, but the target's cost is already folded
  into that constant (confirmed: its content was fixed across the entire
  calibration sweep). Added `RoutineLogic.is_jsr_target` and skip such
  routines entirely in `report.py`. All 205 real logic_instr data points
  (every instruction with real captured data, including all 5 JSR points)
  now match the engine's prediction exactly, 0 mismatches.
- **2026-08-22, same day, tag/UDT side** — ran the same adversarial check
  against the tag/UDT side (every real `tag`/`tags`/`udt`-category manifest
  row) and found three more real bugs, all fixed same-day: (1) the
  udt_definition formula's two halves double-counted a shared base
  constant (see "UDT DataType-definition cost" above for the full fix,
  `160` replacing the old `168`+`224`); (2) `declared_member_count` for an
  all-BOOL UDT computed 0 (excluded bit-aliases instead of hidden backing
  SINTs); (3) the BOOL-run bonus was flat +32 regardless of how many
  separate runs existed, instead of +32 per run. `udt`-category real data
  points went from 103/103 mismatching (most off by 100s-1000s of blocks)
  to 50/103 mismatching, and every one of those 50 is now either an
  already-flagged known gap (array dimension surcharge, small-N count/
  member anomaly, atomic-type micro-variance, OQ-ARRAYPACK/UDTARRAYALIGN)
  or the newly-surfaced custom-string-definition-cost gap noted above.
