# AOI Sizing — What Is Known and What Is Not

AOIs are a large part of real PLC code, so this needs to be right. This file is
the honest accounting: what is confirmed and wired, what is genuinely still open,
and which plausible-looking answers have already been refuted.

Constants live in `MEMORY_MODEL.md`. This file is the map.

---

## What an AOI is, structurally

Not in question.

- An `AddOnInstructionDefinition` declares Parameters (Input, Output, InOut) and
  LocalTags — the same member-list shape as a UDT's `DataType`, with a `Usage`
  attribute per parameter.
- **An AOI-typed tag sizes exactly like a UDT-typed tag** built from that member
  list. Input, Output and LocalTags contribute to the instance's storage.
  **InOut parameters do not** — an InOut is a reference to the caller's own tag,
  not separate storage inside the instance.
- **Required and Visible are per-parameter flags governing call-site syntax:**
  - `Required="true"` → a tag is mandatory on the call.
  - `Required="false" Visible="true"` → the parameter MAY be given a value at the
    call site, and that value may be a **literal**. It may also be omitted: both
    forms build, confirmed across 2,154 committed files with a conversion status.
    So the legal arity is a RANGE, `Required <= args <= Required + Visible`.

    **This pair is NOT sufficient on its own.** An AOI with ZERO Required
    parameters and three Visible ones was rejected by Studio on every rung with
    *"Invalid number of arguments for instruction"* -- including the control whose
    arguments were all tags, so it is not about literals. The arity was inside the
    range above. Something else constrains a definition with no Required parameter
    and it is not yet known; see OQ-LITERALOPERAND's BOOL arm. Do not build another
    AOI test file on this pair alone without a Required parameter present.
  - Neither → hidden. Tag-browser access only, never appears on a call.

  This governs whether a generated test file builds at all, so it is load-bearing
  for every AOI test file.

---

## Known and wired

### Instance tags — exact

An AOI-typed tag costs `Σ(Input + Output + LocalTag member sizes) + tag_overhead`,
the same formula as an ordinary UDT-typed tag, with zero residual across many real
files.

This was worth a large accuracy jump on its own: engine error on the real corpus
fell from 41.6% to 29.5% (alias tags plus predefined structures) to 8.8% once AOI
instance sizing landed.

### Definition cost — one itemised form

An AOI's declaration has a real one-time cost independent of any instance. The
form is in `MEMORY_MODEL.md`: a base, 12 per declared member, each member's own
data bytes, 24 per 32-bit word the declared BOOLs occupy, an 8-aligned pool for
the member names, and a bucketed term for the AOI's own type name.

Measured on **124 definition-only files** — no instance tag anywhere and no
internal rungs, so the definition is the only AOI cost in the file. **70 land
exactly, 122 of 124 inside ±8.**

### Type-name length — closed

`8 × max(0, (len − 8) // 4) − 8`, exact at seven points.

### Internal logic — wired

All of an AOI's internal routines are aggregated into one pseudo-routine and
weighted with the ordinary instruction table. **Per-routine count does not matter,
only total content.** Cut maximum residual on the isolation sweep from 12.02% to
0.55%.

### Call site — wired

`120 + 16 per parameter passed`, the instance tag not counting. Fixed by two
independently written generators with different AOI shapes.

### Instance arrays — wired

The whole block is padded to an 8-byte boundary:
`8 × ceil(n × per_instance / 8)`. 48 of 48 captured families agree with zero
exceptions across 17 distinct per-instance sizes.

### Required / Visible / Hidden do not affect definition cost

Closed. An apparent ±16 swing is inside the project noise band, confirmed across
both the DINT-only case and a BOOL-Input-plus-InOut-AXIS shape.

---

## Refuted — do not re-derive these

Each of these fitted its own data cleanly and is wrong. They are recorded because
every one of them looks like an answer.

### `marginal_bytes_per_instance = 124 − 4 × bool_member_count`

Zero residual at **nine** points, from 0 to 30 BOOL members. About as clean a fit
as this project has produced. **Superseded.**

Every point came from AOIs with the same total member count (30), so the formula
could not distinguish a per-BOOL effect from something depending on total member
count. The real mechanism is the **8-byte block alignment** above: composition
only moved the per-instance size, and the residue mod 8 was doing all the work.

### The 32-element boundary hypothesis

The guess was that BOOL members inside an array of AOI instances pack across
elements the way a top-level BOOL array does, 32 per word, predicting a step
discontinuity at 32 instances.

**Refuted.** A boundary-crossing sweep at n = 16, 31, 32, 33, 48, 64, 65 and 96
shows no such step — marginal cost is flat across the whole range, with no
boundary feature. Whatever the mechanism is, it is not cross-element bit packing.

### Four separate fitted definition-cost terms

A per-declared-item rate of 20, a per-type rate table (BOOL 16, SINT 18, INT 18,
DINT 20, REAL 20, LINT 24), a per-character member-name rate, and a
per-member-type extra. **Each fitted its own sweep exactly. All four were absorbing
parts of the same error.** `MEMORY_MODEL.md` records what each was really
measuring.

The mixed-versus-single-type split went with them. Per-type rates appeared not to
compose additively once BOOL sat beside another type **because the name-pool error
was surfacing as a composition effect**, not because of any real interaction.

### `aoi_def_cost ≈ 1200 + 18 × param_count`

Three clean points, essentially zero residual, DINT-Input-only. Superseded by the
itemised form.

---

## Genuinely open

### 1. The structural blind spot — the one that matters for strangers' code

**This reframes everything else.** The definition-cost form prices a finite list of
properties. Several structural properties of a real AOI are therefore priced at
whatever the itemised terms happen to cover, and the generated corpus barely
exercises them.

Measured across 81 real AOI definitions and 2,120 real parameters and LocalTags:

| property | real corpus |
|---|---|
| member name length | mean 12.1 characters, max 32 |
| member descriptions | 803 of 2,120 have one; the corpus generated none |
| InOut parameters | 94 real |
| predefined-struct members | TIMER 557, DateTime 120, COUNTER 66, STRING 58, MOTION_INSTRUCTION 36, MESSAGE 15 — the corpus generated none |
| array dimensions | 46 real dimensioned members |
| counts past the fitted range | real AOIs reach 102 parameters, 128 locals, 85 internal rungs; the corpus topped out near 6, 2 and 1 |
| extra internal routines | 7 of 81 have EnableInFalse or Prescan besides Logic |

**Why this matters more than the byte counts suggest.** This tool is going to
people whose AOIs will have these properties in different amounts. **A correction
fitted against the definitions that recur across the real projects — the
byte-identical shared AOIs like `PTimer`, `HomeToTorque` and `Debounce` — would
score well on the real set and be worthless on theirs.**

So: **never fit anything to a specific AOI name.** Cost models must be functions of
structure. A 56-file isolation batch exists, one property per group, with the AOI
type name held constant across all of them so the one priced name term cannot
contaminate the readings. The model predicts a dead flat line across every group
except the deliberate scale sweeps, so **any spread in the captured numbers is an
unpriced item.** Blocked on capture.

### 2. The 8-byte definition term

Exactly 0 on 70 instrument files and exactly +8 on 35. Confounded three ways:
the type-name bucket boundary, a fixed offset inside the name pool, and member
order. A 54-file batch is built to break the confound.

The base is deliberately set to centre the residual on zero for the 124-file
instrument. **A base 8 higher scores more exact rows corpus-wide and is
deliberately not taken** — taking it would bury the term rather than solve it.

### 3. AOI BOOL packing

Unlike UDT members, AOI parameters and LocalTags of type BOOL appear in the L5X as
plain `DataType="BOOL"` with no hidden-SINT or BIT-alias representation. **Whether
they pack 8 per byte like a UDT member or allocate unpacked like a standalone tag
is unconfirmed.**

Implemented as unpacked at 4 bytes, which is what the XML shape shows. This is an
open question, not a KNOWN fact.

### 4. Three instance-array families still vary with instance count

The 8-byte block rule is exact on every family that can test it, but three remain
count-dependent. Closeout files are generated, not captured. This is why the array
rule stays FITTED.

### 5. Nested and composite AOIs

Residuals now sit under 1.5% of file total, most of it plausibly the same
per-file noise band accepted throughout the project. **Not yet confirmed as pure
noise versus a small real effect.** The scale of the question has changed
completely — worth a fresh look when more captures land, not treated as settled
either way.

---

## Rockwell-internals questions

Places where "how does Logix actually compile this" is a genuine internals
question that more test files alone cannot answer cleanly.

**Does an AOI's compiled definition cost differently from an ordinary UDT's,
structurally?** **Yes — AOIs carry real extra metadata.** This confirms the
definition cost is a genuine structural AOI-versus-UDT difference, not measurement
noise or an artifact of test shape. It is a real, permanent line item every
AOI-using program pays, and it will not wash out with more data.

**Is BOOL-parameter packing inside an array of AOI instances documented
anywhere?** **No.** Genuinely undocumented territory that only shows up
empirically. There is no shortcut to a known mechanism here.

---

## Where this leaves the accuracy goal

AOI cost is no longer the largest gap. It was — for a long period every AOI-using
program was silently missing the definition-cost line entirely, a real, known,
unflagged under-prediction. That is fixed and drillable in the UI.

What remains is small in bytes and large in risk: **the byte counts are close, and
the confidence that they stay close on unfamiliar AOIs is not measured.** Items 1
and 3 above are the ones that decide whether this tool works on someone else's
code, and neither is a byte-count question.

**A rough, clearly-labelled estimate is more honest than reporting zero.** That
principle is what got the definition cost wired in the first place, and it still
applies to anything on the open list.
