# AOI Sizing — Known / Unknown Map

James, 2026-08-25: "Sounds like you don't know what needs to be addressed
for AOIs. I am nervous you don't have a gameplan for knowing how they
work... I need 100% accuracy for AOIs as it is a large foundation for our
PLC code." This doc is the gameplan — a plain accounting of what's actually
confirmed about AOI sizing versus what's still a real gap, so there's
something concrete to correct or add to rather than a vague "still working
on it." Update this file whenever an item below moves from unknown to
known, or a new unknown surfaces — don't let it go stale the way the
instruction table almost did.

## What an AOI *is*, structurally, in L5X (confirmed, not in question)

- An `AddOnInstructionDefinition` element declares Parameters (Input/
  Output/InOut) and LocalTags — same member-list shape as a UDT's
  `DataType`, just with a `Usage` attribute per parameter.
- An AOI-*typed tag* (an "instance") sizes exactly like a UDT-typed tag
  built from that same member list — Input/Output/LocalTags contribute to
  the instance's own storage, **InOut parameters do NOT** (an InOut
  parameter is a reference to the CALLER's own tag, not separate storage
  inside the instance). Confirmed against real corpus, wired in
  `parser/aoi.py`.
- Required/Visible/Hidden are per-parameter flags controlling what a
  calling rung must/may/can't wire at the call site (James's own
  explanation, tested): `Required=true` → tag mandatory on the call;
  `Required=false, Visible=true` → some value mandatory but wiring is
  optional (can be omitted, matches real corpus precedent); neither →
  hidden, tag-browser access only, never appears on a call. This is
  about call-site *syntax validity*, not proven to be zero-effect on byte
  size — see the Known/Unknown split below, it turns out to matter a
  little.

## KNOWN — confirmed, wired, trust these

1. **Standalone AOI-instance tag sizing (scalar, one instance).** Exact
   fit — an AOI-typed tag sizes as `Σ(Input+Output+LocalTag member sizes)
   + tag_overhead`, same formula as an ordinary UDT-typed tag. Confirmed
   across many real files, 0.00% residual when the AOI's own *definition*
   cost isn't in play (see the definition-cost gap below — that's a
   *separate* line item the engine currently doesn't charge at all, not
   an error in the instance formula itself).

2. **AOI array-of-instances, pure-atomic members (no BOOL anywhere).**
   Real per-element array cost (~124/instance) is close to the engine's
   own UDT-style array assumption (128/instance) — small ~4/instance gap,
   consistent with ordinary small-residual noise seen elsewhere in this
   project, not a distinct new effect. Trust the plain per-instance
   formula for BOOL-free AOI arrays.

3. **Required/Visible/Hidden call-site syntax.** Confirmed real: Required
   params must be wired, Visible-optional params may be omitted (matches
   real `PTimer` corpus precedent), Hidden params never appear on a call.
   This governs whether a generated test file *builds at all* — already
   load-bearing for every AOI test file this project writes.

## UNKNOWN — real, open, no formula yet (this is the actual gap)

1. **AOI DEFINITION cost — WIRED 2026-08-27, close but not total closure.**
   The full `localtype_*`/`paramtype_*`/`aoidefcost_type*` def_only batch
   (85/85 AOI manifest rows) had landed captured but sat unprocessed —
   closed this pass. `aoi_definition` (memory_model.yaml) now uses a
   per-type declared-item rate (BOOL=16, SINT=18, INT=18, DINT=20, REAL=20,
   LINT=24 per item, base=1184 unchanged) whenever an AOI declares items of
   a SINGLE type — this directly fixes the previously-flagged "BOOL/LINT-
   heavy AOIs under-predicted" gap (LINT-heavy: was -32/item, now exact;
   BOOL-run: was -5-6%, now ~1.1%). Live-recomputed against all 85 captured
   AOI rows: 32 exact, 52 within 1%, 1 at 2.10% (`aoi_array_localtag_1_
   instance` — that's the separate array-vs-definition-cost tangle, item 3
   below, not a def-cost miss). Deliberately did NOT extend per-type rates
   to MIXED-type AOI defs (some DINT + some BOOL together) — real data
   proves the rates don't compose additively once BOOL sits alongside
   another type (`aoi_boolpack_interspersed20_def_only`, 20 BOOL + 20 DINT,
   matches the OLD flat-20 formula exactly; a naive per-type sum
   under-predicts it by 80). Mixed-type AOI defs keep the flat
   per_declared_item=20 rate, which real realistic-shape data
   (`BasicAOI`/`RealisticAOI50`) already sits within 1-2% of. See
   memory_model.yaml's `aoi_definition` comment for the full derivation.

   Still genuinely open, both small (<2% of a file's total predicted
   bytes at the tested extremes):
   - AOI name length has a real but non-uniform stepping effect
     (`aoiname_len08/13/20/30_def_only`: +0/+8/+16/+32 vs a fixed
     DINT:4 baseline) — not the clean `8*ceil(len/8)` bucket the UDT/
     tag_overhead formulas use, not force-fit into a guess.
   - Required/Visible/Hidden's small +-16 definition-cost swing —
     recapture batch (BOOL+InOut AXIS shape) still awaiting capture.

   Original per-item-count/type-scaling questions this item used to track
   (now folded into the wired formula above), kept for history:
   - Does it scale with parameter count? **The one dataset built to
     answer this (`paramcount_n02/n04/n08_def_only`) is contaminated** —
     a stale-capture-window bug (OQ-CAPTURERACE) means `n04` accidentally
     recorded `n02`'s value and `n08`'s reading is also suspect. Clean
     recapture (`paramcount_n04_def_only_v2`/`n08_def_only_v2`) is
     generated and sitting in the manifest, awaiting a real capture.
   - Does the ordinary UDT-definition formula (`168 + 16×member_count`,
     name-length term, BOOL-run bonus) apply unchanged to AOIs? **No —
     confirmed different, and now a real shape exists.** The contaminated
     `paramcount_n04/n08_def_only` retest (`_v2` files, OQ-CAPTURERACE)
     landed clean 2026-08-25 (`error_count=0` both). Real gap vs. the
     currently-predicted value: n04=1272, n08=1344 → linear at exactly
     **18/param**, extrapolating to a flat **~1200** at param_count=0. The
     3rd point (`paramcount_n02_def_only`, real actual=19360) — generated
     under an older code path with a different predicted_bytes baseline,
     not directly comparable on the gap number — still checks out: the
     fitted formula (baseline + 1200 + 18×2) predicts 19364 against a real
     19360, a 4-byte miss. **`aoi_def_cost ≈ 1200 + 18×param_count`,
     DINT/Input-only, 0-instance shape, 3 points, essentially zero
     residual.** Not wired (needs more param TYPES — INT/BOOL/REAL/Output/
     InOut all untested — before trusting `18/param` as universal, and the
     UDT-definition formula comparison above is still worth running once
     more param shapes exist), but this is the clearest signal yet on the
     AOI-vs-UDT structural difference James confirmed is real in the
     2026-08-25 Q&A (see below) — plausibly the ~1200 flat term IS that
     extra bookkeeping. **Generated 2026-08-25, `gen_aoi_generalization.py`,
     awaiting capture:** INT/BOOL/REAL Input params at n=2/4/8 (9 files)
     and Output/InOut direction at n=4/8 (4 files), matching the confirmed
     DINT/Input points exactly so the comparison isolates only type or
     direction.
   - Does Required/Visible/Hidden affect DEFINITION cost, not just
     call-site syntax? **Yes, a little, unexplained.** Real data:
     `reqvis_allhidden_n4_def_only` = `reqvis_allrequired_n4_def_only` =
     1,272 gap (identical), `reqvis_allvisibleoptional_n4_def_only` =
     1,288 (+16 vs the other two), `reqvis_mixed_n4_def_only` (2
     required + 1 visible-optional + 1 hidden) = 1,256 (-16 vs
     allhidden/allrequired). So the flag combination genuinely moves the
     number by ±16, but there's no theory yet for why all-Hidden and
     all-Required land on the exact same value while all-Visible-optional
     is +16 and one specific mix is -16. Four data points, one real
     small effect, zero mechanistic understanding.
     **2026-08-25, James: "check if size is different when marking them
     as not visible vs visible vs required."** That earlier sweep only
     ever used plain DINT Input params, no InOut param in the mix.
     `gen_axis_composite.py`'s new `group_axis_aoi_inout_reqvis_sweep`
     (3 files, hidden/visible-optional/required, all def_only, all
     lint-clean) tests the same 3-way flag split on the BOOL Input +
     InOut AXIS_CIP_DRIVE shape instead — the first check of whether this
     effect holds the same way when an InOut param is also present, not
     assumed to generalize from the DINT-only case. Awaiting capture.

2. **AOI array-of-instances, BOOL-heavy members — 2026-08-25: SOLVED for
   the tested shape, formula found, not yet wired (see confidence caveat
   below).** Real per-element array cost depends on how many of the AOI's
   30 members are BOOL, and it turns out to be exactly linear:

   **`marginal_bytes_per_instance = 124 - 4 × bool_member_count`**
   (bool_member_count out of 30 total members in every AOI tested here)

   Confirmed against 8 real data points, computed by direct subtraction
   between consecutive instance counts within each ratio (same tag pool,
   only instance count varies — this project's standard methodology), and
   every single one lands on the formula exactly:

   | BOOL members (of 30) | formula (124-4n) | real marginal/instance |
   |---|---|---|
   | 0  | 124 | ~124 (KNOWN #2 above) |
   | 1  | 120 | 120 |
   | 5  | 104 | 104 |
   | 10 | 84  | 84 |
   | 15 | 64  | 64 (the original single ratio point) |
   | 20 | 44  | 44 |
   | 25 | 24  | 24 |
   | 29 | 8   | 8 |
   | 30 | 4   | ~4 (boundary sweep below) |

   Zero residual at every point — this is about as clean a fit as this
   project has ever produced.

   **The 32-element-boundary hypothesis is REFUTED.** The original guess
   was "BOOL members inside an AOI pack across array elements the way a
   top-level BOOL array does" (32-per-word), which predicts a step
   discontinuity at 32 instances. The boundary-crossing sweep
   (n=16/31/32/33/48/64/65/96, all-BOOL 30/30) shows NO such step — real
   marginal cost is a flat ~4/instance across the entire range (31→32:
   +0, 32→33: +8, 48→64: +4.0/instance, 65→96: +3.87/instance — noisy at
   the byte level but flat, no boundary feature). Whatever the real
   Rockwell mechanism is, it is NOT simple 32-per-word cross-element bit
   packing. James, in the 2026-08-25 quick-fire Q&A: never seen this
   documented anywhere — this formula is purely empirical, no known
   mechanism behind the `124 - 4n` shape.

   **Confidence caveat — why this isn't wired into memory_model.yaml
   yet:** every single data point above comes from AOIs with the SAME
   total member count (30). The formula could genuinely be universal
   (some per-BOOL-member packing effect independent of how many other
   members exist) or could be specific to 30-member AOIs (e.g. if the
   real mechanism depends on total member count, not just BOOL count).
   Untested. **This is now the single highest-value next AOI test**: repeat
   the same ratio sweep at a different total member count (e.g. 10 or 60
   members) to see if `124 - 4n` still holds or the coefficients shift.

   **Generated 2026-08-25, `gen_aoi_generalization.py`, awaiting capture:**
   the ratio sweep at member_count=10/20/60 (5 ratio points × 3 instance
   counts each, 45 files) plus a layout variant (BOOL-first/BOOL-last/
   interspersed at the confirmed 15/30 ratio, 6 files) to test whether the
   formula holds at other member counts and whether BOOL position (not
   just count) matters.

3. **AOI array cost vs AOI definition cost — currently tangled
   together, can't be cleanly separated.** Because the definition-cost
   gap (unknown #1) is itself unresolved, every array-of-instances
   number above is really "definition cost (unknown) + N × per-element
   cost (partially known)" collapsed into one real Capacity reading —
   there's no way yet to know how much of any array file's gap belongs to
   which piece. Solving #1 first would make #2's numbers much easier to
   trust.

4. **Nested/composite AOIs — very thin data.** An AOI containing another
   AOI, or an AOI with an InOut `AXIS_CIP_DRIVE`/UDT parameter, has only
   2-3 real data points (`aoi_deepnest3_*`, `nested_aoi_*`,
   `aoi_realistic_composite_*`) — small clean-looking gaps (2,000-3,600
   range) but not enough points to fit anything, and these gaps are
   plausibly just the same unresolved definition-cost gap (#1) showing up
   again, not a separate nesting-specific effect. Not independently
   confirmed either way.

## Questions where James's own knowledge would help most

These are the places where "how does Logix actually compile this" is a
real Rockwell-internals question, not something more test files alone can
answer cleanly. **Quick-fire Q&A run 2026-08-25 (James's request) —
answers below.**

- Is there a real, known reason an AOI's own compiled definition would
  cost differently than an ordinary UDT's, structurally? (e.g. does an
  AOI carry extra internal bookkeeping — a signature/revision hash, an
  edit-in-progress flag, something visible in Logix Designer's own
  compare/verify tooling — that a plain UDT doesn't?)
  **James: yes, AOIs carry real extra metadata.** Confirms the
  definition-cost gap (unknown #1 above) is a genuine structural AOI-vs-
  UDT difference, not measurement noise or an artifact of test shape —
  raises the priority of actually fitting that gap's formula, since it's
  now confirmed to be a real, permanent line item every AOI-using program
  pays, not something that might wash out with more data.
- Is BOOL-parameter packing inside an array of AOI instances something
  you've seen discussed/documented anywhere (Rockwell KB, AB forums), or
  is this genuinely undocumented territory that only shows up empirically?
  **James: never seen it documented.** Stays purely empirical — no
  shortcut to a known mechanism, the boundary-crossing (n=16/31/32/33/
  48/64/65/96) and ratio sweeps already generated/awaiting capture are
  the only path to a mechanism here.
- Does the Required/Visible/Hidden flag combination have any known
  real-world effect on compiled size, or is the small ±16 swing seen
  above more likely something else entirely (e.g. an artifact of exactly
  which parameters got marked Hidden vs Visible, not the flag pattern
  itself)?
  **James: no idea, need more data.** Stays open — the
  `group_axis_aoi_inout_reqvis_sweep` files (BOOL Input + InOut
  AXIS_CIP_DRIVE, hidden/visible-optional/required) already generated and
  awaiting capture are the next data point; no reason yet to expect the
  DINT-only ±16 result to hold or not hold on this shape.

## Where this leaves the "100% accuracy" goal

**2026-08-26 update: both unknown #1 (definition cost) and the BOOL-array-
packing mechanism are now WIRED into `memory_model.yaml`, closing the
"nothing wired yet" gap the 2026-08-25 update below still had.**
BOOL-array-packing: `aoi_array` (flat_discount=4, bool_word_size=32,
bool_word_extra=4), confidence KNOWN — confirmed across 4 member counts,
see RESOLVED (this doc's own earlier sections). Definition cost:
`aoi_definition` (base=1184, per_declared_item=20), confidence FITTED, NOT
KNOWN — confirmed exact on 2 independent axes (local-tag count, param
count) but DINT-rate only; a real localtype/paramtype sweep already shows
BOOL/LINT cost differently (unmodeled), so every AOI's definition-cost
number is now a real, non-zero, DINT-confirmed FLOOR rather than the
previous silent zero — an honest improvement, not a claim of exactness for
every AOI. Both are also now drillable in the UI (`sizing/tree.py`'s
`expand_definition_children`, James's Phase 2/2b "locals+params breakdown"
ask). Still tangled/unresolved: AOI name length, BOOL run/pack adjacency at
the definition level, and non-DINT parameter types — see OPEN_QUESTIONS.md
OQ-AOIDEF for the live detail, this doc stays the high-level map.

**2026-08-25 update: real progress, not there yet.** BOOL-array-packing
(unknown #2) now has a clean, zero-residual formula (`124 - 4×bool_count`)
confirmed at 8 real data points and a refuted competing hypothesis — the
single biggest jump in AOI understanding this project has made. Definition
cost (unknown #1) now has a real linear shape too (`~1200 + 18×param_count`,
3 clean points) instead of a bare list of unexplained gaps. Neither is
wired yet — both are confirmed at only one AOI shape (30 members / DINT-
Input-only respectively) and need a second shape to confirm the
coefficients generalize before memory_model.yaml gets touched. That's now
a concrete, narrow, two-item next-batch target instead of an open-ended
unknown.

Below is the pre-2026-08-25 state for what's still genuinely unresolved:
definition cost (formula found, still needs a 2nd shape to confirm),
BOOL-array-packing mechanism (partially characterized, 3 more shapes
generated awaiting capture), and the two are currently tangled together in
every array data point. Nothing above is guessed into `memory_model.yaml`
— every AOI number the tool currently reports is either the confirmed
scalar-instance formula (trustworthy) or silently missing the definition-
cost line item entirely (a real, known, currently-unflagged
under-prediction for every AOI-using real program). That under-prediction
being currently invisible to a user is itself worth fixing before anything
else on this list — even a rough, clearly-labeled-as-estimated definition-
cost number would be more honest than reporting 0.
