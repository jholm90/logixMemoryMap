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

## UDT packing (ASSUMED, pending OQ-ALIGN / OQ-BOOLPACK confirmation)

- Recurse members in declared order.
- BOOL members: pack 8 to a backing SINT byte, per the existing BIT-member
  generation convention (one hidden SINT per byte of BOOL members, incrementing
  BitNumber 0–7, new SINT for bits 8–15, etc).
- Non-BOOL members: size = atomic/nested-UDT size, per table above.
- Alignment/padding between members: **UNKNOWN — OQ-ALIGN**. Current formula
  assumes tight packing with no padding. This is the single highest-risk
  assumption in the whole model and should be the first thing Phase 3
  invalidates or confirms.
- Nested UDT: recursive — a UDT member's size is that UDT's total computed size
  (itself subject to the same alignment question, compounding uncertainty at
  depth — watch this closely in the 3-level-nesting Phase 3 sample).

## Array sizing

- Array of atomic type: `dimension × element_size`. KNOWN with confidence, no
  packing ambiguity for a single atomic type (BOOL arrays are a known Logix
  special case — BOOL *arrays* bit-pack into DINT-sized words, unlike standalone
  BOOL tags; confirm this distinction explicitly in Phase 3, don't conflate with
  OQ-BOOLPACK).
- Array of UDT: `dimension × udt_size`, formula pending OQ-ARRAYPACK (per-element
  vs whole-block padding).
- Multi-dimensional arrays: product of all dimensions × element size, no known
  special case, but not yet tested at scale >2D.

## AOI sizing

- Definition: sum of local tag sizes (own UDT-like recursion) + parameter tag
  sizes, computed once from `AddOnInstructionDefinitions`.
- Instance cost: **ASSUMED** each call site allocates a full separate copy of
  local tag memory (standard AOI instance behavior) — pending OQ-AOIINSTANCE
  and blocked on logic-parse call-site counting (Phase 1/4 dependency).
- Formula: `total_aoi_memory = call_site_count × (locals + params)`, params
  typically small/pointer-like but need explicit confirmation they don't
  duplicate the *referenced* tag's memory (they shouldn't — parameters are
  references to caller-scope tags, not new allocations — but confirm).

## Module / I/O tag sizing

- Local (backplane) I/O: **UNKNOWN**, not yet modeled. Depends on module type
  (input/output point count, analog vs digital) — needs its own type table,
  likely sourced from module EDS/catalog data rather than computed generically.
- Produced/Consumed: **UNKNOWN — OQ-PRODCONS**. Overhead formula not yet
  isolated from base connection cost vs. payload cost vs. consumer count.

## Logic instruction weights (FITTED — empty until Phase 4)

Table to be populated during Phase 4/4b. Format once populated:

| Instruction | Base bytes | Per-operand bytes | Sample size (n) | Residual error |
|---|---|---|---|---|
| _(none yet)_ | | | | |

Do not estimate these ahead of data. No placeholder numbers — an empty table is
more honest than a guessed one that gets silently treated as real later.

## Change log

Log every constant change here with date + which sample(s) drove the change, so
there's a record of *why* a number is what it is, not just what it currently is.

- (none yet — populate starting Phase 3)
