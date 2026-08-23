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

1. **AOI DEFINITION cost — the single biggest unknown, unresolved.** The
   AOI's own type declaration (independent of any instance) has a real,
   substantial cost the engine currently doesn't model at all (charges
   0). Real `*_def_only` captures show gaps in the 1,256–1,808 range
   depending on shape — not the same number twice, so it's shape-
   dependent, but the shape of that dependence isn't known:
   - Does it scale with parameter count? **The one dataset built to
     answer this (`paramcount_n02/n04/n08_def_only`) is contaminated** —
     a stale-capture-window bug (OQ-CAPTURERACE) means `n04` accidentally
     recorded `n02`'s value and `n08`'s reading is also suspect. Clean
     recapture (`paramcount_n04_def_only_v2`/`n08_def_only_v2`) is
     generated and sitting in the manifest, awaiting a real capture.
   - Does the ordinary UDT-definition formula (`168 + 16×member_count`,
     name-length term, BOOL-run bonus) apply unchanged to AOIs? **No good
     reason to assume yes** — UDTs and AOIs are different real Rockwell
     objects even though their instance-storage shape is identical; the
     gap sizes seen so far don't obviously match that formula scaled to
     AOI parameter counts, but nothing's been fit yet.
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

2. **AOI array-of-instances, BOOL-heavy members — real numbers, no
   mechanism.** Real per-element array cost depends dramatically on how
   many members are BOOL, and not in a way that's currently explained:
   - Zero BOOL (pure atomic): ~124/instance (close to the plain formula,
     see KNOWN #2 above).
   - ALL BOOL (30/30 members): ~4/instance — dramatically cheaper, looks
     like genuine bit-packing across array elements (the way a plain
     BOOL *array* packs 32 elements/word), but the 5 count points tested
     so far (1/5/10/25/50) don't cleanly cross a 32-element boundary, so
     this can't be told apart from some other quantized effect yet. A
     boundary-crossing sweep (n=16/31/32/33/48/64/65/96) is generated and
     awaiting capture.
   - HALF BOOL (15/30 members): exactly **64/instance**, suspiciously
     exactly half of the pure-atomic 128/instance assumption, and this
     one IS cleanly linear (not noisy like the all-BOOL case) — but
     tested at only ONE ratio. Don't know if 64 is special to a 50/50
     split, or if it's some other real rule (e.g. per-BOOL-member
     packing that happens to land on 64 at this specific member count/
     ratio). Six more ratios (1:29 through 29:1) are generated and
     awaiting capture, specifically to answer this.
   - **The honest state of understanding:** I do not know the actual
     Rockwell packing mechanism here. My best current guess is "BOOL
     members inside an AOI, when the AOI is put into an array, pack
     across array elements the way a top-level BOOL array does" — but
     that's a hypothesis built to explain 3 shapes at 1 fixed member
     count (30) each, not a confirmed mechanism. It could just as
     plausibly be wrong in a way that only shows up at a different
     member count, a different total-BOOL-count, or past a 32-element
     boundary.

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
answer cleanly:

- Is there a real, known reason an AOI's own compiled definition would
  cost differently than an ordinary UDT's, structurally? (e.g. does an
  AOI carry extra internal bookkeeping — a signature/revision hash, an
  edit-in-progress flag, something visible in Logix Designer's own
  compare/verify tooling — that a plain UDT doesn't?)
- Is BOOL-parameter packing inside an array of AOI instances something
  you've seen discussed/documented anywhere (Rockwell KB, AB forums), or
  is this genuinely undocumented territory that only shows up empirically?
- Does the Required/Visible/Hidden flag combination have any known
  real-world effect on compiled size, or is the small ±16 swing seen
  above more likely something else entirely (e.g. an artifact of exactly
  which parameters got marked Hidden vs Visible, not the flag pattern
  itself)?

## Where this leaves the "100% accuracy" goal

Not there yet, and the gap is now itemized rather than vague: definition
cost (biggest, unresolved, contaminated retest already re-issued),
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
