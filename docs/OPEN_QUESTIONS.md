# Open Questions

Every unresolved question gets an ID (OQ-xxx). Resolved items move to
`docs/RESOLVED_QUESTIONS.md`. One line each here — full derivation is in
the matching footnote at the bottom, not inline.

1. **OQ-BASELINE-PROCFW** — partially wired 2026-08-29. Firmware-version
   (v30/v31/v32/v33), 5069-safety-capable-model, and (found the same day
   via a full manifest.csv audit) 1769-series per-catalog baseline deltas
   are now real, confirmed, and wired into `report.py`/`memory_model.yaml`
   — validated against all 50 real (untainted) `fw_catalog_matrix` rows
   plus 8 real 1769-series and 2 more `fw_baseline` points, every one now
   predicts within 32 bytes (was off by up to 80,832 for 1769). Still
   genuinely open: v38 (only real capture is WINDOW-TITLE-MISMATCH-
   flagged, awaiting the batch script's automatic retry), v36/v37 (no real
   sample at all), and any 1769 catalog beyond the 9 exact ProcessorType
   strings now confirmed (real data shows a single suffix character
   changes the value by 13,000+ bytes, so unconfirmed catalogs correctly
   stay unmodeled rather than guessed). L7x/L8xES catalogs in the matrix
   still await their own capture (L8xES additionally needed a real
   ProductCode fix 2026-08-30, see RESOLVED_QUESTIONS.md — L81ES-L84ES
   now real-tested and importing; **1756-L85ES removed from the
   automated matrix the same day** after its inferred ProductCode (215)
   failed real testing while the SAME +1-per-step inference correctly
   predicted L82ES/L83ES — the sequence breaks specifically at the top
   of the range, no second real anchor exists to re-derive it from.
   1756-L85ES is a real, current product (confirmed via web search, not
   a fake catalog), same as 1756-L9x below — sourced but deliberately
   not generated until a real sample or its real ProductCode surfaces).
   The 9
   1769-series catalogs were re-added to the automated `fw_catalog_matrix`
   2026-08-30 (James: AHK capture now works for this family, same as
   L7x) — previously only ever built as single-firmware/v35
   `fw_baseline` files; now part of the full 6-firmware sweep too. Real
   bugs found in the re-add, same day, from live James testing (not
   code review): every 1769 catalog used a single guessed Bus Size (17,
   only confirmed for L33ERM) and was missing a real embedded
   `Discrete_IO` module entirely (L16ER–L27ERM-QBFC1B all have one;
   L30ERM/L33ERM genuinely don't) — fixed by extracting the real
   per-catalog Modules block verbatim from the 9 `fw_baseline` reference
   exports. **That fix was itself wrong and has been narrowed back out,
   same day** (James: real chassis-size error from his own minimal
   1769-L24ER-QB1B repro file, Bus Size="6" — "you f'd up most chassis
   sizes" / "seems like you shouldnt be guessing chassis sizes and
   actually use ones that were referenced"). The extracted Bus Size
   values were never independently real-confirmed — they came from the
   `fw_baseline` reference files, which themselves carry a "MANUAL
   ENTRY... clicking Estimate" caveat (built by switching ProcessorType
   in Controller Properties from a base project, never proven to have
   round-tripped through l5xgit import). The ONLY independently real-
   confirmed 1769 Compact-bus Bus Size anywhere in the corpus is
   L33ERMS=17 (`samples/local/DnR_Personal/TOYOTA_135453_20221024.L5X`,
   a genuine customer file) — and even that catalog is included in
   James's "L24..L27 and the L3 series fail" report, so its failure has
   some other, still-unidentified cause even though its Bus Size checks
   out. `_1769_CATALOGS` is back down to just the 4 PointIO-bus catalogs
   (L16ER-BB1B/L18ER-BB1B/L18ERM-BB1B/L19ER-BB1B), empirically confirmed
   working in James's live batch (all "ok" at v33). L24ER-QB1B,
   L24ER-QBFC1B, L27ERM-QBFC1B, L30ERM, and L33ERM are pulled from
   automated generation — 30 generated files and their manifest rows
   removed — until real per-catalog data (or an unambiguous root cause)
   exists, same treatment as 1756-L85ES/1756-L9x below. Not guessing
   again.

   2026-08-30 update, `samples/convert_log.csv` reconciled (James's
   L5X->ACD conversion log, real per-file build outcomes, not guesswork):
   confirms L24ER-QB1B/L24ER-QBFC1B/L27ERM-QBFC1B/L30ERM genuinely never
   produce an ACD at any firmware version (`XMLSrv_E_IMPORT_ABORTED_
   NO_CHANGES`), settling that removal independent of the Bus Size
   question. But L33ERM — also pulled at the same time — actually DOES
   convert cleanly (`status=ok`, all 6 firmware versions, real per-file
   window titles) and carried 6 real manifest rows in James's push;
   restored those rows into `manifest.csv` this merge (files themselves
   NOT yet regenerated — `gen_fw_catalog_matrix.py` still excludes it,
   needs a deliberate re-add if this is worth pursuing further).

   Both L33ERM's restored captures and the 4 kept PointIO catalogs'
   real captures show a genuinely strange pattern worth flagging before
   trusting either: L33ERM's `actual_bytes` is the exact same 6,640
   across all 6 firmware versions despite predicted ranging 94,104-97,112
   (a real, huge, -93%-ish gap); the 4 PointIO catalogs' `actual_bytes`
   is the exact same 2,976 across all 4 catalogs and all firmware
   versions despite predicted ranging 69,616-83,864 (a real, ~-2,200%
   to -2,700% gap). Both sets have clean per-file window titles matching
   the file under test and 0 logged errors/warnings — not an obvious
   window-title-mismatch artifact. A real, error-free capture landing on
   the exact same tiny value regardless of which distinct file was open
   looks like a capture-tooling or units issue rather than 5+ independent
   sizing-formula bugs that all happen to collapse to the same constant —
   ties into OQ-BLOCKBYTE below (all captures here are 1769/L7x-family,
   the "bytes"-labeled side of that question), though the ratios aren't a
   single clean constant across the two groups (94104/6640≈14.2 vs
   80856/2976≈27.2), so it isn't simply a fixed blocks-to-bytes scale
   factor either. Needs James to manually eyeball what Studio 5000 is
   actually showing on one of these two specific capture batches before
   either set gets trusted as real data.

   Separately, and more plausibly real: the 1756-L81ES/L82ES/L83ES/L84ES
   (GuardLogix safety) rows across the same push show small, consistent,
   real deltas — -3.91% (v31/v32), -3.55% (v33), -6.38% (v34/v35/v38) —
   same magnitude within each firmware group, genuinely error-free
   captures, a plausible real safety-baseline refinement rather than a
   capture artifact. Not yet derived/wired.

   2026-08-31, MYSTERY SOLVED (James, self-caught, real bug on his side):
   his AHK/PowerShell capture pipeline was reading Studio 5000's I/O
   memory field, not the logical (program) memory field this project
   actually sizes, for EVERY 1756-L7x (L71-L75) and 1769-family capture —
   confirmed directly: `fwmatrix_v31_1769_l33erm.ACD` real Logic
   memory=71,968 bytes (out of a 2,097,152-byte total budget for that
   controller) vs the 6,640 that was sitting in `manifest.csv`. This
   fully explains the "suspiciously tiny, near-identical value across
   different files" pattern flagged above — I/O memory for these
   near-empty test files legitimately IS small and similar regardless of
   content, since it's logic/tags (not I/O config) that actually varies
   between them. All 60 real `manifest.csv` rows captured against an
   L7x/1769 processor (the full historical corpus, not just this push —
   found via window_title regex, not the unreliable controller_model
   field) had their capture columns cleared 2026-08-31, not just the
   handful flagged above — 9 of the 60 were additionally garbled
   (`actual_bytes` values like `"Revision:"`/`"Type:"`, a second real
   symptom of the same wrong-field capture). James: "I NEED ALL THE
   1769/L7 files to re-test with new data" — awaiting his re-run with the
   fixed pipeline. Also flagged a caveat on `catalog_baseline_delta` in
   `memory_model.yaml` (the 8 real 1769-series ASSUMED baseline deltas) —
   different capture METHOD (manual "Estimate" click, not this AHK
   automation) so unconfirmed whether the same bug applies there, not
   changed numerically, but worth asking James directly.[^baseline]

2. **OQ-CMPCPTLAYOUT** — down to one thread. Uniform, T1+T2, T1T3/T2T3,
   and (as of 2026-08-29) the all-3-tier mix are ALL solved and wired,
   confirmed exact on every real data point on file. Only the REAL-
   operand/float-literal interaction remains open, and it's now a harder
   problem than "assumed linear, awaiting more points" — real new data
   shows it's genuinely NOT monotonic in operand count, ruling out any
   simple per-count model. 2026-08-30: the 12 `cptmix_*` probe files
   (float1/real1/real2/real3 position/adjacency/nesting variants) got
   real captures in James's latest push — all land within 0.7-1.3% (188-272
   bytes on ~20,500-byte totals), small and real but too tight/consistent
   across position/nesting variants on their own to isolate a clean new
   term from; still needs the dedicated architecture work, not more raw
   points.[^cmpcpt]

3. **OQ-AOIBOOLPACK-PAIRING** — split off the now-closed OQ-AOIDEF's old
    "BOOL-array-packing-boundary" thread once its 27 already-captured
    points got reconciled. The `aoi_array` per-instance formula was tagged
    KNOWN ("confirmed exact... 15 real points") but that claim was only
    ever checked at 3 widely-spaced instance counts per shape (n=1/10/25)
    — real dense data disproves it. Confidence downgraded to FITTED.
    2026-08-30: the dense/isolating files got real captures in James's
    latest push. Pattern is now clearer, not yet closed: each `bc<N>`
    family (bit-count-per-element family, presumably) carries its OWN
    fixed offset that's constant across instance count within that family
    but differs BETWEEN families — `aoibp_dense_bc10_*` off by a flat
    ~20-24 bytes regardless of n (2 through 12), `bc20_*` flat ~36-40,
    `bc60_*` flat 140, while `aoibp_puremix_8b2a_*` is flat ~-8 to -12 and
    `aoibp_split_allinput30_*` flat ~60-64. A per-family fixed offset that
    doesn't scale with instance count points at a missing per-
    boundary-crossing term (something tied to WHICH bit/byte boundary the
    packed BOOLs cross, not how many instances exist) rather than a
    missing per-instance term — real, promising lead, not yet
    derived/wired.[^aoiboolpackpairing]

4. **OQ-SAFETYSCOPE-SIZING** — real, unresolved product decision, split
   out 2026-08-30 from the now-closed OQ-PREDEFINED (moved to
   RESOLVED_QUESTIONS.md — the byte-value derivation for all 195 known
   predefined structure types is done; this is a separate policy
   question, not a data gap). The tool already warns rather than refuses
   on a Safety-rated project (`is_safety_project`, cli.py/ui/server.py),
   but within a warned-and-still-processed project, resolvable
   Safety-classed content (`DCI_STOP`, real corpus evidence, 80 bytes;
   `CONFIGURABLE_ROUT`, wired 52 bytes but Safety-family by name-root) is
   currently left unsized by convention, not by any code that actually
   enforces the exclusion. Needs a call from James: exclude Safety-class
   tags from sizing everywhere by design (and wire that exclusion
   explicitly instead of it being incidental), or size everything
   resolvable including Safety content and adjust the warning
   wording.

   2026-08-31, concrete new evidence (James: "what are you going to do
   about the L8 guardlogix?"): traced the real -3.55% to -6.38% GuardLogix
   ES gap from the last review to its exact source. It is NOT a missing
   catalog-suffix baseline delta (tried wiring one at the real +312-byte
   safety/non-safety delta derived from `fwmatrix_v3x_1756_l81e` vs
   `l81es` actuals — made the prediction WORSE, caught by testing before
   committing, reverted). The real cause: `task_program_shell` charges the
   SafetyTask's shell/container the SAME full weight as an ordinary task
   (4,816 -> 6,272, a real +1,456-byte jump) even though its actual
   Program/Routine CONTENT is correctly left unsized (SafetyProgram's
   MainRoutine only contributes 16 bytes) — this is exactly the "left
   unsized by convention, not by code" gap the policy question above
   already names, just showing up in the task/program SHELL specifically
   rather than tag content. Real total safety/non-safety delta is only
   +312 (confirmed flat across v31-v35, +296 at v38) — nowhere near the
   +1,472 the engine currently produces. Not fixing until James decides
   the policy question: if Safety Task/Program shells are meant to be
   excluded from sizing the same as their content, `task_program_shell`
   needs a Safety-task carve-out; if shells ARE meant to count (a
   SafetyTask genuinely does reserve its own container in the controller
   independent of its logic), the shell weight itself needs a real
   Safety-specific value, not the ordinary-task one it's using now.[^safetyscope]

5. **OQ-AOIARRAYDIMENSION** — real parser bug fixed 2026-08-27:
   `<Parameter>`/`<LocalTag>` array size is a "Dimensions" (plural)
   attribute, not "Dimension" (singular, correct only for a plain UDT
   `<Member>`) — was silently sizing every array-dimensioned AOI local/
   param as a scalar. 5 existing test files need a fresh real capture;
   their prior "confirmed" numbers almost certainly tested scalar
   behavior by coincidence, not the array behavior they were meant
   to. Second real bug, found 2026-08-30 (James: `aoi_array_param_def_
   only.L5X` still fails to import — `XMLSrv_E_IMPORT_ABORTED_NO_CHANGES`
   — even after the earlier Required/Visible fix): the generator omitted
   `<DefaultData>` entirely for ANY dimensioned Parameter, conflating
   "is an array" with "is InOut" the same way the Required/Visible bug
   did (`BitArray`/`LOG_HMIDisplay`, the only 2 real array-Parameter
   examples on file, are both InOut AND dimensioned, so the array case
   alone was never actually isolated). Real corpus check confirms every
   non-InOut Parameter with `ExternalAccess` also carries `<DefaultData>`
   (scalar `WindowStart`/`WindowEnd`/etc., `TS_TrackSts` AOI) — InOut
   params are the only ones that go bare. Fixed: a dimensioned atomic
   Input/Output Parameter now gets a real `<Array>`/`<Element>`
   DefaultData body (same convention `_array_body_xml` already uses for
   an ordinary array Tag) plus a bracketed-list L5K default. No real
   corpus example of an array Input/Output Parameter exists anywhere to
   confirm this exact shape — still ASSUMED, generalized from adjacent
   confirmed conventions, not independently verified.[^aoiarraydimension]

6. **OQ-MODULEIO** — mostly closed 2026-08-29. 126 real module captures
   were sitting unreconciled in manifest.csv; 51 catalogs now have a real
   per-catalog overhead value (exact-match rate on real data went from
   1/126 to 54/126). Two real sub-threads remain, both needing
   architecture work not more generation: multi-module marginal cost
   (adding a 2nd/3rd of the same module doesn't cost the same as the
   1st), and a handful of catalogs with real connection-variant-dependent
   overhead.[^moduleio]

7. **OQ-JSRPARAMCOST** — reopened 2026-08-29 for one small residual.
    Output/return-param call-site cost is now wired and confirmed
    (see RESOLVED_QUESTIONS.md). The callee's own one-time `A(n)`
    Parameters-block cost almost certainly ALSO needs an output-param
    term (real Parameters blocks include both Input and Output entries)
    — `jsr_multiret_n04` still off by +332 after the call-site fix, too
    small relative to a 1-distinct-target sample to isolate from noise.
    Needs a dedicated small file (2+ distinct targets with different
    output-param counts, input count held constant) to isolate A(n)'s
    real output term cleanly. 2026-08-30: `jsr_multiret_n02_r01000` came
    back within 0.09% (140/155,272), consistent with the wired call-site
    fix. But two NEW real, larger, param-TYPE-specific gaps showed up in
    the same push: `jsr_paramtype_string_n05_r00100` is off by +4,096
    (9.76%) and `jsr_paramtype_udt_n05_r00100` by +4,048 (9.78%) — both
    5-param/100-call files, both off by almost exactly the same amount,
    while the plain-DINT/REAL paramtype files in the same batch
    (`jsr_paramcount_*`, `jsr_paramtype_real_n05_r00100`) land within
    0.04%. Points at a real, currently-unwired per-call-site surcharge
    specifically for STRING/UDT-typed JSR parameters (not a flat A(n)
    definition-cost issue, since it scales with something in this file
    that plain-atomic-typed params don't have) — genuinely new, not yet
    derived.

8. **OQ-EVENTTRIGGER** — new, real. task_extra (+700) was derived only
    from CONTINUOUS+PERIODIC tasks; EVENT-type tasks are completely
    untested, and so is trigger-source (Axis Watch vs. EVENT-instruction)
    within EVENT. Two files built, awaiting capture.[^eventtrigger]

9. **OQ-AOIORPHAN** — new, real, found 2026-08-30 reviewing a real
   confidential customer project (not committed, never named here). 12 of
   that project's 39 declared AOI definitions had zero real tag anywhere
   (even transitively) instantiating them — confirmed by raw grep,
   independent of this project's own parser. `report.py`'s definition-cost
   pass only counts a UDT/AOI reachable from an actually-sized tag
   (`referenced_udts`), so an orphaned AOI predicts $0 extra, no error.
   Whether Logix Designer's compiler actually reserves memory for an AOI
   definition that's never instantiated anywhere, or drops it entirely, is
   genuinely unknown — not derivable from the L5X alone. Two-file test
   built to isolate it (`aoi_orphaned_referenced`/`aoi_orphaned_
   unreferenced`, byte-identical except one has a live instance+call of a
   moderate utility AOI and the other has the same AOI declared but never
   instantiated), awaiting capture.[^aoiorphan] Extended 2026-08-30 with 50
   more real data points at realistic project scale/composition (see
   `gen_composite_realistic.py` below) — every one of the 50 composite
   files declares at least one orphaned AOI alongside several referenced
   ones, so once captured this closes with a much larger, varied sample
   than the original minimal pair, not just confirms it.

10. **OQ-BLOCKBYTE** — new, very serious if real. James, 2026-08-30:
    Studio 5000's Capacity readout is labeled "bytes" for 1769/L7x
    processors but "blocks" for 5069/L8x processors — and this project has
    treated `actual_bytes` as one uniform unit across the whole
    `manifest.csv` corpus regardless of which family captured it, with
    1756-L81E (L8x, "blocks"-labeled) as the dominant baseline processor
    for nearly the entire history of this project. If "block" isn't
    numerically identical to "byte", essentially every formula in
    `memory_model.yaml` fit against L81E/5069 data needs rescaling by
    whatever the real conversion factor turns out to be. Two-file test
    built to check it directly: `blockbytetest_dint120000` (1756-L81E) and
    `blockbytetest_l71_dint120000` (1756-L71, same firmware 35.05/35.11),
    byte-identical content — a single 120,000-element DINT array tag,
    nothing else, both predicting 498,236 (480,000 of that is exactly
    120,000×4, zero packing ambiguity). Any real conversion factor will
    show up as an obvious clean ratio between the two files' real Capacity
    readings. Awaiting capture on both (not yet in James's tooling as of
    2026-08-30 — only just pushed this session).

    Circumstantial evidence surfaced 2026-08-30 in OQ-BASELINE-PROCFW
    above: two different 1769/L7x-family capture batches (the restored
    L33ERM rows and the kept PointIO catalog rows) both landed on a
    single tiny constant value regardless of which distinct file was
    captured, with clean window titles and 0 errors. Doesn't confirm or
    rule out a units mismatch on its own (the two groups' implied ratios
    don't match each other), but it's a second, independent hint that
    something about how 1769/L7x-family Capacity gets read may not be
    behaving the same as the L81E/5069 baseline this project is built
    on.[^blockbyte]

11. **OQ-COMPOSITESCALE** — new, real, James 2026-08-30 directive after
    the confidential-project review found a >20% real gap: "I expect at
    least 50 large programs with io and logic to test your generation
    knowledge and test aois and udts." Every calibration file in this
    project before now isolated ONE feature at a time — never tested
    whether the individually-confirmed formulas are actually additive at
    real project scale/density, or whether interaction effects between
    many UDTs/AOIs/arrays/modules/rungs at once produce a real
    discrepancy that isolated tests can't catch. 50 composite files built
    (`gen_composite_realistic.py`, `samples/generated/composite/`), each a
    genuinely different combination (not the same shape resized): 2-6
    UDTs (1 always nested), 2-5 referenced AOIs + 1-3 orphaned AOIs (also
    feeds OQ-AOIORPHAN), 3-6 large atomic arrays + 1 UDT array,
    TIMER/COUNTER, 2-4 real I/O modules (cycled from `gen_module_sweep.
    py`'s 86 real catalog blocks), 150-900 rungs mixing XIC/OTE/MOV/ADD/
    CPT/TON/CTU/AOI-calls. All on 5069-L306ER/fw35.11 (the processor-
    family question is isolated separately, OQ-BLOCKBYTE, to keep this
    batch's findings unambiguous). 26 of the 50 have a fully-predicted
    total; 24 hit an already-known unmodeled real I/O module shape
    (rack-aliased connections, legacy-network bridges, a handful of
    modules with unrecognized nested member types) and fall back to
    predicted_bytes=0/unmodeled, same convention as elsewhere in this
    project — genuinely unmodeled, not a bug in this batch. Real Capacity
    on the 26 fully-predicted files is the actual test: if predicted and
    real land within ~1% at this scale, the individually-confirmed
    formulas really are additive; any real divergence pinpoints an
    interaction effect (or a formula that only breaks at
    scale/density) invisible to every prior isolated test.[^compositescale]

---

[^instrfirstpass]: CROUT (safety-only) and MAPC resolved separately
(RESOLVED_QUESTIONS.md). SCP (no 2nd real example), FBC (0 real
examples), PID (0 real examples, needs its own structure tag) —
deprioritized 2026-08-25 (James: "move to safety related feature"),
**explicitly closed as out-of-scope 2026-08-30 (James: doesn't care about
these)** rather than left open awaiting data that was never coming.
Small residual noted for the record, not blocking closure: a flat
**+12** byte gap (corrected from a misrecorded +6) across all 64 clean
`instrfirst_*` files (~0.06% of file total), narrowed to an interaction
effect among the 7 distinct tag types the shared pool declares but not
isolated to which one.

[^baseline]: `empty_project_baseline=13,296` only confirmed for
1756-L81E/fw 35.05 — real variance found so far: firmware 30→33 adds a
real, distinct step (29,272 → 32,376 at fw33); 1769-series runs
69,600-98,944, far above the flat prediction; 5069-L306ER family sits at
18,144 base. An "M motion processor costs more" hypothesis was tested and
answered NO (2 identical base-vs-M pairs). The 8 files previously flagged
"contaminated" (named `SafetyTask`/`SafetyProgram` but carrying no real
safety marker — no `Class="Safety"`, empty `<SafetyInfo/>`) are now
corrected and included: subtracting the known task/program/routine shell
overhead (1,456) gives a clean baseline of 18,112 for 4 of them (exact
match to the already-confirmed reference point) and 18,120-18,144 for the
other 4 (small real per-model variance, not error) — see `manifest.csv`
notes on `v35_l82e/l83e/l84e/l85e/l3100erm/l320er/l330er/l340er`. 20 files
remain awaiting capture.

**Full catalog x firmware matrix built 2026-08-25, expanded same day**
(`gen_fw_catalog_matrix.py`, 232 files, `fw_catalog_matrix` category).
Every real catalog number sourced from Rockwell literature/distributor
documentation via web search (not guessed), cross-checked against this
project's own already-confirmed ProductCodes before generating anything:
29 catalogs × 8 firmware versions (31-38, v30 excluded — SDK confirmed
unable to build it at all):
- 5× ControlLogix 5580 (1756-L8x), 14× CompactLogix 5380 (5069-Lxxx) —
  original 152-file batch.
- 5× ControlLogix 5570 (1756-L7x, L71/L72/L75 real ProductCode 92/93/96,
  L73/L74 INFERRED 94/95 from the sequential pattern — flagged per-file).
- 5× GuardLogix 5580 safety-rated (1756-L8xES — real ProductCodes
  CORRECTED 2026-08-30, see below: L81ES=211, L84ES=214 both real,
  L82ES/L83ES/L85ES=212/213/215 INFERRED from that 2-point sequential
  pattern — flagged per-file). Each gets a real `SafetyTask`/`SafetyProgram` pair
  with `Class="Safety"` on both elements (the real marker, confirmed
  against Gormley/Bender corpus — NOT the element name) plus a populated
  `<SafetyInfo SafetyLevel="SIL2/PLd" .../>`.

Firmware attribute shape (SoftwareRevision, AutoDiagsEnabled/
WebServerEnabled presence, v38's DataExchangeId) is real per version,
confirmed from the existing v31-35/v38 samples. **v36/v37 removed
entirely 2026-08-28** (James: not asked for, told to leave out) — they
were the only two ASSUMED/unconfirmed firmware majors in the table (no
real v36/v37 L5X sample ever existed in this project); the batch is now
174 files (6 firmware x 29 catalogs), all on real-confirmed firmware
attribute shapes. Files sorted `fwmatrix_v{NN}_{catalog}` so a plain
directory listing groups all of v31 together, then v32, etc.

**Real, systemic structural bug found and fixed 2026-08-28** (James:
"your controller firmware tests are really really bad. very high failure
rate. you obviously have missed something" — followed by a fresh real
Studio 5000 export of 1756-L71 sent for direct comparison; the exact same
evidence was ALSO already sitting unused in `samples/local/
L7_v21_Sample.L5X`, meaning this generator was built without ever
cross-checking against corpus evidence that was already available).
ControlLogix 5570 (1756-L7x) has NO embedded Ethernet interface on the
CPU module itself — real shape is exactly ONE Local Port (`Type="ICP"`,
`Bus Size="4"`, not the L8x-style 17) and no top-level `<EthernetPorts>`
element at all. This generator applied the L8x shape (second Ethernet
Port + EthernetPorts element describing a port that doesn't physically
exist) to all 5 L7x catalogs across every firmware version — a real
structural error, not a cosmetic one, plausible root cause for a large
share of the reported high failure rate. Fixed: `_local_ports_xml` now
branches for `_L7X_PRODUCT_CODES`, and the top-level `<EthernetPorts>`
is conditionally omitted for that family. Only L71 is directly
corpus-confirmed; L72-L75 are the same ControlLogix 5570 physical form
factor so treated identically, not independently confirmed per-catalog.
Also added two real Controller/RedundancyInfo attributes confirmed by
both real references (`TimeSlice="20" ShareUnusedTimeSlice="1"`,
`IOMemoryPadPercentage="90" DataTablePadPercentage="50"`) — `build_l5x`'s
own already-working template omits both and still imports fine across
~1300 tested files, so these are almost certainly Studio-5000-optional
rather than the actual failure cause, but added for fidelity now that
real values exist. All 174 files regenerated — awaiting real
re-conversion to confirm the L7x fix actually resolves the failure rate,
not just structurally plausible like the module fixes earlier today.

**Sourced but deliberately NOT generated, real ProductCode still
unconfirmed:** ControlLogix 5590 (1756-L9x, "TS" suffix — L902TS/L905TS/
L908TS/L915TS/L925TS/L950TS/L980TS) — a brand-new family (FactoryTalk
Design Studio only added support in v2.03, Nov 2025) with zero real L5X
corpus examples anywhere, and zero real ProductCode/Module-signature data
found anywhere publicly accessible despite thorough web search (Rockwell's
own domains are all blocked by this environment's egress proxy; even
distributor/3rd-party sites carry catalog numbers but never the internal
ProductCode). James asked for one L9 sample minimum v38 — still blocked on
this, needs either a real sample from him or explicit sign-off on a
flagged best-effort placeholder. CompactLogix 5480 (5069-L4xx process
controllers — L430ERMW/L450ERMW/L4100ERMW/L4200ERMW) — also zero real
corpus examples, not yet requested by James. Building either without a
real sample risks fabricating a ProductCode/Module shape that fails
Studio 5000 import outright.

**1769-series real per-catalog baseline + v30 wired 2026-08-29** (found
during a full manifest.csv audit, James: "make another in-depth pass" —
these 9 real points had been sitting in the `fw_baseline` category,
MANUAL ENTRY, since before this project even had a `firmware_baseline_
delta` mechanism to wire them into, and were never revisited). 8 real
1769-series (CompactLogix 5370) blank-baseline captures, all v35.05 —
real total baseline runs 69,600-98,944 against a flat 18,112 predicted
for everything else, previously documented as "not modeled at all."
Wired as `catalog_baseline_delta` (memory_model.yaml), keyed by the
EXACT `ProcessorType` string (not prefix/suffix-matched like
`safety_capable_baseline_delta`) — real data shows a single expansion-
module suffix character changes the value by 13,000+ bytes
(`1769-L24ER-QB1B`=67,160 vs `1769-L24ER-QBFC1B`=80,832), so any
catalog beyond the 9 exact strings now confirmed correctly stays
unmodeled. Firmware-independence assumed (same convention as
`firmware_baseline_delta`) but genuinely unconfirmed — zero 1769 data
exists at any firmware besides v35. Separately, `l81_v30` (real MANUAL
ENTRY point, James read Capacity directly off a real v30 controller —
this project's SDK can't build/convert v30 exports at all) added to
`firmware_baseline_delta` at +11,160, ASSUMED confidence (single point).
All 29 real `fw_baseline`-category rows now checked: 17 exact, 6 within
the small per-file noise band (<=16 bytes), 3 already-documented small
per-model variance (+32 bytes, `l306er`/`l306erm`/`l320er`), and 3
already-documented Safety-Task-bearing-file gap (`l306erms2`/`erms3`/
`ers2`, -1,424 — real Safety Task/Program content this tool doesn't
size, see this same footnote's `v35_l306erms2`/`v35_l306erms3` note
further below for the root cause).

[^cmpcpt]: T1T3/T2T3 wired 2026-08-25: real capture data existed
unreconciled since 2026-08-24; `pow_tier_mix_base=160,
pow_tier_mix_per_operator=64` is exact at 4 of 5 points, and T1T3/T2T3
give IDENTICAL real bytes at every point (T1-vs-T2 stops mattering once
POW is present). See `sizing/constants.py` `CptExpressionModel.cost_for`.
**All-3-tier mixes: CLOSED 2026-08-29.** The 3
`cptmix_threetier_rem2_n06/n09/n12` files (plus the 4 disentangle files
below) had real capture data from 2026-08-27 sitting unreconciled in
manifest.csv this whole time — found and fixed the same day James pushed
on why this wasn't closed already. The earlier `44*T1-116*T2+76*T3+72`
attempt was wrong (not just "misses n=15" — checked directly, it doesn't
reproduce the n=3/5/8/10/11 points it was supposedly fit from either).
Correct formula, confirmed 0 residual across ALL 9 real all-3-tier points
on file (operator counts 4-14): `base_by_remainder[operator_count % 3] +
4 * pow_operand_count`, `base_by_remainder = {0: 72, 1: 116, 2: 144}`.
remainder=1 exact at 3/3 points, remainder=2 exact at 4/4 points
(including the original n=15 outlier AND the 3 new rem2 probe files —
confirms the remainder-2 trigger hypothesis exactly, and that it's NOT a
flat bonus, it scales at +4/POW-operand same as the other two remainder
classes). remainder=0 rests on a single point (n=10) — same slope,
extrapolated base, one point short of independent confirmation. Wired in
`sizing/constants.py` `CptExpressionModel.cost_for` / `memory_model.yaml`
cpt_expression.

**REAL-operand/float-literal interaction: investigated 2026-08-29, still
open — now for a more specific and more interesting reason than "not
enough points."** The 4 disentangle files' real data (also from
2026-08-27, also unreconciled) rules out any simple per-operand-count
model: extra cost at R=1 REAL operand (276) is HIGHER than at R=2 (236),
and the same pattern holds for float literals (F=1: 280, F=2: 244) — going
from 1 to 2 of the same factor makes the file SMALLER, not bigger. That's
not sub-linear/saturating, it's genuinely non-monotonic, and it holds
identically for both factors, which rules out coincidence/noise. No
formula wired — CLAUDE.md's ground-truth discipline means not force-
fitting a linear or bilinear surface onto data that demonstrably isn't
one. Real hypothesis worth testing next: cost may track the number of
DINT→REAL type-PROMOTION points in the expression tree (a structural
property of where mixed-type sub-expressions meet), not the raw REAL-
operand/float-literal COUNT — needs files that vary operand/literal
POSITION at a fixed count, not just count alone. Additive fallback (no
surcharge) stays the honest default. Full data: 9 total points across the
`cptmix_stacked_*` (5, already on file 2026-08-24) and `cptmix_
disentangle_*` (4, captured 2026-08-27) sample sets.

**Position-probe files built 2026-08-29** (`gen_cpt_mixed_operators.py`
`group_real_float_position_probe`, James: "generate new tests... they
have been dragging on for far too long" -- fair, the hypothesis above had
sat undertested since it was written). 4 new files, all built/lint-clean/
zero engine errors, awaiting real capture: `cptmix_real1_pos_first`/
`cptmix_real1_pos_last` (1 REAL operand at slot 1 vs slot 6 of the same
6-operand T1+T2 shape, "middle" position already on file as
`cptmix_disentangle_real1_noliteral`) and `cptmix_float1_pos_first`/
`cptmix_float1_pos_divisor` (1 float literal at slot 1 vs the divisor
slot, "last" position already on file as `cptmix_disentangle_
float1_noreal`). Once captured: if all 3 positions per factor land on the
same real delta, position is ruled out (points back to an unexplained
pure-count effect); if they differ, the pattern across first/middle/last
tells us whether edge positions (fewer operator-adjacency "boundaries")
cost less, which would directly support the type-promotion-point
hypothesis.

**James, 2026-08-30: "are you sure you only need 4 tests for cpt?" —
correct, no.** The 4 position-probe files above hold REAL-operand/
float-literal COUNT fixed at 1 and only vary where that single factor
sits — they can't touch the actual anomaly this whole thread exists to
explain (2 REAL operands costing LESS than 1, non-monotonic in count).
Added `group_real_pair_adjacency_probe`: `cptmix_real2_adjacent` (2 REAL
operands at slots 1-2, adjacent) vs `cptmix_real2_spread` (2 REAL operands
at slots 1 and 6, same count, spread to opposite ends of the same 6-slot
shape) — directly tests whether adjacency (fewer DINT↔REAL promotion-point
crossings) is what drives the count anomaly, or whether the two layouts
measure the same (which would falsify the promotion-point hypothesis
itself, not just leave it uncalibrated). Built, lint-clean, zero engine
errors, awaiting capture — 6 CPT probe files on file total now, not 4.

**James, 2026-08-30: "have you got enough tests to fully close this?"**
— honest answer: no, still not guaranteed. The adjacent/spread pair only
disambiguates 1-vs-2 REAL operands; it says nothing about whether the
non-monotonic dip continues, reverses, or was specific to exactly 2.
Added `cptmix_real3_adjacent` (3 REAL operands, slots 1-3, same shape) to
extend the count sequence 1→2→3. Even with this, two things stay
untested and are flagged honestly rather than silently assumed closed:
whether REAL-count and float-literal effects compose when both are
present at varying counts/positions together, and whether a different
expression tree shape (not just this flat 6-slot layout) changes the
answer.

**James, 2026-08-30: "add more tests to fully close this instead of
guessing."** Both remaining gaps now have dedicated files instead of
being left untested:
- **REAL-count x float-literal composition**: `cptmix_real1_float1`,
  `real2_adjacent_float1`, `real3_adjacent_float1` -- same shapes as
  real1_pos_first/real2_adjacent/real3_adjacent with the trailing slot
  replaced by the float literal 1.5, so the marginal float-literal cost
  can be read directly by subtraction at each REAL count (constant
  across n = additive/no interaction; varies = real interaction).
- **Alternate expression tree shape**: `cptmix_real1_nested`,
  `real2_nested` -- same operand/operator multiset as
  real1_pos_first/real2_adjacent but deeply right-nested instead of a
  flat left-to-right chain, REAL operand(s) at the innermost position.
  Tests whether the type-promotion-point hypothesis holds once tree
  structure (not just flat token position) changes.

12 CPT probe files on file now, covering count (1/2/3), position
(first/last/divisor), adjacency (adjacent/spread), float composition, and
tree shape. This is the full hypothesis space as currently understood --
not claiming it's exhaustive of every possible expression shape, but
every specific mechanism proposed so far now has a real test.

**Cross-validated at scale, 2026-08-29** (full manifest.csv audit):
`randommix_07_n19811rungs_24types` (`logic_random_mix` category, real
capture) was off by +39,959 -- traced to its 208 real CPT calls, which
all use `gen_logic_sweep.py`'s exact `(D+D)*R-R/2+1.5` shape (2 REAL
operands, 1 float literal) -- the SAME `original_shape` this thread
already covers. 208 x the already-known ~200/call gives ~41,600, close
to the real 39,959 (the small gap is plausibly the rotating tag pool's
per-call operand variety, not a new effect). Confirms this is the same
open thread recurring at volume, not a separate bug -- no new formula
needed or wired, consistent with the additive-fallback default already
in place.

[^aoidef]: Per-type declared-item rate table (BOOL=16, SINT/INT=18,
DINT/REAL=20, LINT=24/item, base=1184) wired for single-type defs;
mixed-type defs use the flat rate (confirmed non-additive once BOOL sits
next to another type). Live-verified against 85 captured AOI rows: 32
exact, 52 within 1%, 1 at 2.10%. Full derivation: `docs/AOI_KNOWLEDGE_MAP.md`.
Required/Visible/Hidden flag combinations: CLOSED 2026-08-25 — real
2026-08-23 capture data was sitting unreconciled, deltas land within a
32-block band with no direction tied to flag config (noise, not a real
effect).

**Name-length CLOSED 2026-08-30**: `aoiname_len08/09/13/16/20/25/30_def_only`
(7 real points, all sitting unreconciled) confirmed exact against
`8*max(0,(len-8)//4) - 8` — wired into `AoiDefinitionModel.name_length_bytes`.
A real off-by-one bug was found and fixed along the way: the first version
wired (divisor `(len-7)//4`, chosen because it also reproduces all 7 of the
same points) put len=19 one bucket too high. Caught by cross-checking two
real AOI-array-packing captures that only differ in AOI type name length —
`AoiPureBoolDense` (16 chars) and `AoiPureBoolBoundary` (19 chars), both 10
BOOL In/10 BOOL Out/10 BOOL Local, both array of 16 instances — which must
land on the identical total byte count if the shared shape is identical,
but disagreed by exactly 8 bytes under the old divisor. `(len-8)//4`
reproduces all 7 originally-tested lengths identically (none of them sit at
len%4==3, the only residue class where the two divisors disagree) and
resolves the cross-check to 0 bytes apart. AOI-instance-array element cost
split off as its own item, OQ-AOIBOOLPACK-PAIRING, below.

[^aoiboolpackpairing]: The `aoi_array` model's "confirmed exact, 15 real
points" claim (mc=10/20/30/60, but only ever checked at n=1/10/25 per
shape) doesn't survive dense n. Reconciling 27 already-captured points that
were sitting unreconciled proved it: for a single-packed-word AOI
(bool_count<=32), real array bytes follow `8*ceil(n/2) + B` — an odd-length
array costs 4 bytes MORE than the even-length prediction the current
formula makes, a term the formula has no place for at all. B itself is
real and flat per shape but does NOT extrapolate cleanly across bool_count:
B=20 for 10-BOOL-all-Input (`aoipack_mc10_b10_array_n01/10/25`, 3/3 exact),
B=44 for 20-BOOL-all-Input (`aoipack_mc20_b20_array_n01/10/25`, 3/3 exact),
B=28 for the original 30-BOOL/3-way-split shape — 10 In+10 Out+10 Local —
(`aoipack_bool_array_n01/05/10/25/50` + `aoipack_bool_boundary_n16-96` +
`aoipack_bool_dense_array_n16-40`, 18/18 exact). Since B doesn't scale
linearly with bool_count across those three, and the only structural
difference between the 30-BOOL case and the 10/20-BOOL cases is the 3-way
section split (the current parser only tracks a flat total bool_count, not
per-section In/Out/Local counts), the section split itself may be what
actually drives B — untested directly until now.

The 60-BOOL case (2 packed words/instance, `aoipack_mc60_b60_array_n01/10/25`)
is worse: all 3 points show a flat +148-byte miss with **no** odd/even
signal at all against the old formula, but do not fit `8*ceil(n/2)+const`
either when checked directly — multi-word packing is a materially
different, still-open shape from the 3 points on file.

Confidence downgraded `aoi_array`: KNOWN → FITTED (`memory_model.yaml`,
2026-08-30) — the formula is left un-replaced rather than guessing a
generalized fix from underdetermined data (this project already ate one
overfit formula this session, the CPT three-tier bug — not repeating it).
New dense/isolating test files generated instead, not yet captured:
`gen_aoi_boolpack_pairing.py` → `aoibp_dense_bc{10,20,60}_n{02,03,04,06,08,12}`
(18 files, dense n right where the pairing period would show, including
the FIRST dense points at all for bool_count=60) and
`aoibp_split_allinput30_n{01,05,10,16,25}` (5 files, same bool_count=30 as
the already-solved 3-way-split shape but all-Input/single-section, at the
same n values, to directly test the section-split hypothesis). 23 files
total — not padded to the 60-file floor (James, 2026-08-25: not a quota).

**Wider dataset surfaced 2026-08-30** (James: "review open questions...
full depth... no possible open items" — a full manifest.csv reconciliation
sweep against the live engine, not just the mc10/20/60 family already
covered above). **Correction to an initial write-up of this same finding**
(James caught it directly: "are there new tests for all of those points"
— checking the claim while answering surfaced the error): this is NOT the
3-way-split shape (10 In + 10 Out + 10 Local) the original `aoipack_bool_*`
finding used. `aoipack_ratio_01b29a` through `_29b01a`
(`gen_batch3_followups.py` `group_b_ratio_sweep`, 6 BOOL:DINT ratios x
n=1/10/25/50, 24 real points) is SINGLE-SECTION (all-Input, mixing BOOL
and DINT in one Parameters list) — structurally the SAME family as
mc10/mc20 above, just with a fixed 30-member total and a MIXED (not pure)
type composition. It shows a real, different residual shape from mc10/
mc20 anyway: FLAT per ratio, **no** odd/even n-parity signal at all
(01b29a=+52 at every n, 05b25a=+36 at every n, 10b20a=+12 to +16,
20b10a=-24 to -28, 25b05a=-44 at every n, 29b01a=-60 at every n, all flat
within measurement) — where mc10/mc20 (single-section, PURE BOOL, no DINT
at all) show real odd/even pairing. A separate non-atomic-type variant
(`aoipack_nonatomic_real/sint_10b20a/20b10a`, 8 real points, REAL/SINT
non-BOOL operands instead of DINT) shows smaller, still-flat-ish deltas
(-66 to +8). Neither dataset was previously reconciled against the live
engine.

This reframes the open question precisely: within the SAME single-section
structural family, a PURE-BOOL declared-member list (mc10/mc20) shows real
2-instance pairing quantization, but a MIXED BOOL+non-BOOL list (the ratio
family, same family, same section shape) does not — suggesting the
pairing mechanism may specifically depend on whether every declared
member is BOOL, not just on section layout. Untested directly until the
`aoibp_puremix_*` isolation batch below.

[^safetyscope]: `DCI_STOP` (35 errors) has real decorated evidence
(SJ_Gormley_20251112_r02.L5X, 80 bytes/20 DINT) but is deliberately NOT
wired -- every real instance found carries `Class="Safety"` on the Tag
itself, and this project's Safety content is currently NOT sized by
design (the UI's red warning banner) even though nothing in the code
actually enforces that exclusion per-tag today -- it just happens that
Safety AOI types are mostly unresolvable native structures. Wiring
DCI_STOP would make Safety-scoped totals partially counted for the first
time, which needs a decision from James (exclude Safety-class tags by
design everywhere, or size everything resolvable including Safety and
adjust the warning wording) before it's just silently changed.

`CONFIGURABLE_ROUT` -- CORRECTED 2026-08-29, an earlier pass had this
wrong: it DOES have real capture data and IS wired (52 bytes, see
RESOLVED_QUESTIONS.md OQ-PREDEFINED) -- not read in RM018A, but that's
moot now that a real Capacity-based value exists directly. Falls under
the same Safety-scope decision as DCI_STOP (name root matches `CROUT`,
the confirmed Safety-only instruction).

**AOI array "anomaly" investigated 2026-08-29, was contaminated data, not
a real formula problem.** Of the 5 AOI array files re-captured after the
real Dimension/Dimensions bug fix, 4 show a modest positive delta (+400/
+404/+60/+64, plausibly a small remaining formula gap, still genuinely
open) but `aoi_array_param_def_only`'s row was flagged
`WINDOW TITLE MISMATCH` in manifest.csv (window title read back
"ProbeDciStop" -- a completely different file from the predefined-
structure probe batch, not this one) -- the "-1,044 byte overshoot" a
previous pass reported was that mismatched file's real bytes, not this
one's. Per CLAUDE.md's standing rule that row's capture columns are
cleared, not trusted; `aoi_array_param_def_only` is back to needing a
real, clean capture (still in the same NEEDS-RE-CAPTURE bucket the
Dimension/Dimensions bug fix already put it in -- see
[^aoiarraydimension] below, this was never actually re-captured cleanly).
No engine change made or needed here -- AOI array PARAMETER sizing is
UNTESTED, not confirmed broken.

[^aoiarraydimension]: James, 2026-08-27: "be sure you are handling the bit
mapped bools from hidden sints" prompted a broader audit of AOI-local
sizing, which surfaced a real, separate bug (verified via
`compute_udt_size`, `is_bit_alias`/`hidden` in parser/datatypes.py: the
BOOL-hidden-SINT question ITSELF was already correct and directly unit-
tested — `test_udt_mixed_bool_dint_string_with_bit_packing` — 1 byte for
the backing SINT regardless of how many BOOL aliases point into it, 0
extra for each alias, confirmed exact). The real bug found instead:
`parser/aoi.py`'s `_member_from_element` read a `<Parameter>`/`<LocalTag>`
element's array size off a "Dimension" (singular) attribute — correct for
a plain UDT `<Member>` (parser/datatypes.py, unaffected), but real
`<Parameter>`/`<LocalTag>` elements carry it on "Dimensions" (PLURAL) —
confirmed against 80 real `<Parameter Dimensions="N">` and 191 real
`<LocalTag Dimensions="N">` elements across all 64 corpus files, zero
counter-examples for the singular form anywhere. Every array-dimensioned
AOI Parameter/LocalTag was silently sized as a scalar. Real customer-file
impact: 35 tag-sizing errors closed immediately (all CAM_PROFILE, which
was already correctly wired in `predefined_array_structures` but never
reachable through this bug).

Fixed in `parser/aoi.py`. `sample_gen/builders.py` had the IDENTICAL bug
(`Dimension=` instead of `Dimensions=`) generating AOI Parameter/LocalTag
XML — the two bugs self-consistently masked each other for this project's
own synthetic test files (both sides wrong the same way), which is why no
existing test caught it. Fixed there too. 5 existing files (
`aoi_array_localtag_def_only`/`_1_instance`, `aoi_array_param_def_only`,
`aoi_nested_array_localtag_def_only`/`_1_instance`) regenerated with the
corrected attribute — flagged `NEEDS RE-CAPTURE` in manifest.csv, old
actual_bytes/delta cleared rather than trusted. Reasoning: the prior
2026-08-22 capture of these files almost certainly measured SCALAR
behavior, not array behavior — Studio 5000 very likely didn't recognize
the malformed singular attribute either (real syntax requires plural) and
silently coerced it to scalar on import, same as this project's own
buggy parser did. The math backs this out precisely for
`aoi_array_localtag_1_instance`: fixed-engine prediction is 19,832 bytes,
old real capture was 19,424 — a 408-byte gap, matching almost exactly
what a 100-element DINT array minus a scalar DINT should cost (396) plus
the small universal per-file noise (~8-12) seen everywhere else in this
project. Needs a fresh real capture of the corrected files before this
project can claim the AOI-array-local/param formula is confirmed at all
— it currently rests entirely on the already-validated general
array-of-atomic/array-of-UDT member cost formula being assumed to apply
unchanged to an AOI's own Parameter/LocalTag members too, which was never
actually tested end-to-end against a real capture.

**Real import-failure bug found and fixed, 2026-08-29** (James: "the file
does not open, regenerate it"). `aoi_array_param_def_only` itself
wouldn't import into Studio 5000 at all -- a real, separate bug from the
Dimension/Dimensions one above, not just a bad capture read. Root cause:
`sample_gen/builders.py` `_aoi_parameter_xml` used the generic
`Required="false" Visible="false"` default for the array Input Parameter
(`InputBuffer`, `Dimensions="50"`). Zero real corpus evidence supports
false/false on an array Parameter of any Usage -- the only two real
array-Parameter examples this project has (`LOG_HMIDisplay
Dimensions="25"`, `BitArray Dimensions="1024"`, both from real customer
files) are both `Usage="InOut"` and both `Required="true" Visible="true"`,
already-confirmed for InOut specifically but never independently tested
for Input/Output. Fixed by forcing `Required="true" Visible="true"` on
ANY dimensioned Input/Output Parameter, extending the one confirmed
real pattern (this is a hypothesis-driven fix given the available
evidence, not a positively-confirmed Input-array real example --
flagged here, not silently treated as certain). File regenerated,
lint-clean, zero engine errors; Required/Visible flag choice doesn't
affect the sizing formula itself (already confirmed no real effect,
see the Required/Visible closure note above), so predicted_bytes is
unchanged (19,332). Still needs a real capture -- was never actually
captured cleanly (first attempt hit the Dimension/Dimensions bug, second
attempt hit WINDOW TITLE MISMATCH, and the underlying file itself was
broken this whole time under both attempts).

[^moduleio]: `module_overhead = 1,672 bytes/module` (flat, mean of 2 real
deltas), wired as ESTIMATED tier. 141 files in `samples/generated/modules/`:
per-catalog sweep (119/119 real corpus catalogs), rack-level tests, a full
Kinetix 2-bus/8-axis subgraph, and a full-fidelity replica of James's real
Bender program (69 modules incl. GuardLogix Safety Partner). GuardLogix
SIL2/SIL3 handling is a reusable `build_l5x(..., safety_level=...)`
capability. Real Studio 5000 conversion errors from the 2026-08-24/25
batch all root-caused and fixed: module-level `SafetyEnabled="true"` vs a
non-safety controller; 5069 modules needing `Port Type="5069"`; User-
Defined-Catalog devices needing their real `ExtendedProperties/
UdcAopVersion` schema (150 SMC Flex-E, PowerFlex 525-EENET — PF755
confirmed NOT affected); duplicate Ethernet IPs/AxisIDs; a slot collision;
`ParentModPortId` mismatches. Rack slot-address gaps ("a module in slot
10" concern) audited and confirmed NOT a bug — module size reads
exclusively from `ArrayMember/@Dimensions`, never slot number.
Deliberately not charged `module_overhead`: rack-aliased modules,
`CatalogNumber="Embedded"` I/O. Produced/consumed tags: RESOLVED, see
RESOLVED_QUESTIONS.md OQ-PRODCONS. PowerFlex 525 has multiple real I/O
payload UDTs beyond the one profile covered — needs more real corpus
examples, not guessed.

**Real per-catalog overhead table wired 2026-08-29.** The 141-file batch
above had real capture data landing since 2026-08-22 — 126 rows total, of
which 90 were never checked against the live engine and stayed on the
flat 1,672 estimate. Found the same way OQ-CMPCPTLAYOUT was: re-running
every module-category manifest row through the current engine and
diffing against real actual_bytes. Derived `module_overhead_by_catalog`
(memory_model.yaml, `constants.py` `ModuleOverheadModel`) via the same
subtraction methodology as `predefined_structures`:
`real_catalog_overhead = 1,672 + (actual_bytes - engine_predicted)`, ONLY
for real captures where the file's entire module list is exactly
`[Local, one real module]` — strict on purpose, since several
adapter/bridge catalogs (e.g. `1734-AENTR/C`) turned out to be absorbing
a whole rack of aliased child I/O modules into their own single entry,
which would have corrupted a looser per-catalog derivation with
configuration-dependent numbers. 51 catalogs got a clean, unambiguous
real value (real range: -793 to +10,497 — the flat 1,672 mean was a poor
proxy for this much real spread). Real exact-match rate against the 126
real module rows: 1/126 (before) -> 54/126 (after); full-manifest
regression checked (89 rows affected, 12 multi-module files got
marginally worse by 4-68 bytes each — all already inside the "not solved
this pass" bucket below, net effect strongly positive).

**6 catalogs show a real, unmodeled connection-variant effect** and were
deliberately left off the table rather than force-averaged:
`ETHERNET-MODULE`/`ETHERNET-PANELVIEW` (generic-catalog placeholders —
real overhead scales with declared I/O size, not flat at all),
`1734-AENTR/C` and `1756-EN2T` (real 1-conn vs 2-conn/rack-aliased
variance, up to +2,156 apart for the "same" catalog), PowerFlex
525/755-EENET (a smaller ~48-byte gap between two independent
file-generation methods, ambiguous which is representative).

**38 multi-module files reveal a real, distinct architecture gap: the
per-module marginal cost is NOT flat.** `module_1756_ib16_n01/n03/n10`
(1/3/10 identical 1756-IB16 modules in one file) show delta -4, -1,588,
-7,160 against "N x flat-per-catalog-overhead" — the SAME catalog's 2nd,
3rd, ... Nth instance costs LESS than the 1st, not the same. Rack files
(`modulerack_*`) and zero-connection modules (several `_variant_noconn`
files cost real nonzero bytes despite `module_defined_bytes=0` and
getting silently skipped by the current `continue`-on-0/0 check) show the
same class of gap. Needs its own marginal-vs-fixed decomposition, the
same shape task_program_overhead already got for Task/Program/Routine
counts — real architecture work, not a quick constant fix, so not rushed
into this pass.

**CORRECTION, 2026-08-28** (James: "did a super in-depth memory analysis
on the last pushed file? ... review the last batch of l5x conversions,
there was more than 50"): the "1734-OB8S/A/B, 442G-MABLB ... CIP Safety
connections needing a safety controller even without that attribute"
claim above was WRONG/incomplete — the earlier fix (switching to a
safety-rated processor_type) was necessary but not sufficient. These
files, plus 5 more, still failed real conversion in the 226-row
2026-08-27 batch (`53e91d9`, `samples/convert_log.csv`) with a generic
`XMLSrv_E_IMPORT_ABORTED_NO_CHANGES ... See error log` that gave no
detail on its own. Real root cause found by diffing a passing vs. failing
pair that differ by exactly one real config axis (`modulesweep_2198_
d012_ers3_variant_2conn` PASS vs. `_variant_4conn` FAIL — same catalog,
2conn has Integrated Safety off, 4conn has it on): `wrapper.py`'s
`build_l5x(..., safety_level="SIL2")` branch assumed a single non-
redundant safety-capable primary (no CPU partner) needed no
`SafetyNetwork` attribute on its own Local module's ICP/Ethernet ports —
"no adjacent slot to reserve, since there's no partner. Only SafetyInfo
differs for SIL2." That conflated two separate real Rockwell concepts:
`Width="2"` reserves the adjacent slot for a redundant CPU partner
(correctly SIL3-only); `SafetyNetwork` establishes the safety NETWORK
SEGMENT identity that any downstream safety-enabled I/O module's own
`SafetyNetwork` attribute references, needed whenever a descendant module
has `SafetyEnabled="true"`, with or without a redundant partner. Every
one of the affected files had a downstream module correctly declaring
`SafetyNetwork`, referencing a network segment the project never
established — an orphaned reference. Confirmed against real corpus
(`SJ_Gormley_20251112_r02.L5X`): its Local module's ICP port carries
`SafetyNetwork="...cbbc"` and its Ethernet port carries `"...cbbd"`, the
exact value every downstream Kinetix ERS3 safety module in that file
references. The `is_5069` branch (checked BEFORE `safety_level`, so a
5069-family safety project like `5069-L306ERMS2` hosting
`5069-IB8S/A`/`5069-OBV8S/A` never reached the SIL2 logic at all) had the
identical bug via a separate code path — confirmed against a second real
corpus file (`samples/local/L306ERS2_Sample.L5X`, `5069-L306ERS2`): all
THREE Local ports (the local "5069" bus and both Ethernet ports) carry a
real `SafetyNetwork`. Both branches fixed 2026-08-28, regenerated (the
`_r2`-suffixed retest files, matching the existing suffix convention so
James's re-test run doesn't collide with old files): 12 of the 17 real
failures now carry the fix (6× `2198-*-ERS3` 4conn variants,
`1734-OB8S/A`+`B`, `PowerFlex 527-STO`, `442G-MABLB`, `FANUC Robot`,
`5069-IB8S/A`, `5069-OBV8S/A`) — awaiting a real re-conversion to confirm
this actually resolves the import error, not just structurally plausible.
**The 4 remaining 5069 failures ALSO root-caused, 2026-08-28** (James sent
the real Studio 5000 error this time, not just the generic CSV wrapper):
`5069-IB16/A`, `5069-IY4/A`, `5069-OB16/A`, `5069-OB16/B` all real-error
`Failed to set the 'Size' property (Chassis size exceeds the allowable
size for a chassis.)` at `Modules/Module[@Name="Local"]/Ports/Port/Bus` —
a completely different, non-Safety cause from the 13 above, confirming
the earlier guess that these 4 needed a separate diagnosis. `wrapper.py`
used a flat `Bus Size="32"` for every 5069 catalog, sourced from only ONE
real corpus file (5069-L330ERMS2) and silently assumed universal — it's
actually a real per-model maximum local-I/O-slot count, not a constant.
An empty project (no local module attached) never trips this validation
regardless of the declared value (confirmed: `v35_l306er.L5X` passes 8/8
with the same wrong "32"), which is exactly why this stayed hidden until
a real local 5069 I/O module got attached — every one of these 4 failing
files attaches one. Real per-catalog values pulled from 6 separate real
corpus files (never guessed): `5069-L306ERS2`→9 (`L306ERS2_Sample.L5X`),
`5069-L310ERS2`→9 (`PWO_134190.L5X`), `5069-L320ERMS2`/`MS3`→17
(`Fisher_Synergy_Bead_20240725.L5X`, `FlareFunction_311D_240731.L5X`),
`5069-L330ERMS2`→32 (`BT1XX_FFC_20240325.L5X`), `5069-L340ERS2`→32
(`Fisher_P800Sub_20240531.L5X`). The failing files all use
`5069-L306ER` (real max 9, was getting 32) — fixed by keying Bus Size off
the base model number extracted from `processor_type` (the M/MS2/MS3/S2/
ER suffix doesn't change physical backplane capacity within the same
tier), regenerated the 4 `_r2` retest files plus re-verified the 2
already-safety-fixed 5069 files keep their correct value too. All 17 of
the original real failures now have a real, evidenced fix — awaiting
real re-conversion of all 17 affected `_r2` files to confirm.

**A second, separate real 5069 bug found 2026-08-28** (James: "looks
like your 5069-LxxERMSx has issues as well"). `EtherNetIPMode="A1/A2:
Dual-IP"` is a real Controller-level attribute confirmed present, with
the identical value, in EVERY 5069 corpus file checked (6/6, zero
variance) — describes how the CPU's two embedded Ethernet ports are
addressed, something only a 5069 processor has (1756/1769 have at most
one embedded port). It was missing from both `wrapper.py`'s
`build_l5x` (the primary template used across ~1300 already-tested
files) and `gen_fw_catalog_matrix.py`, for every 5069 catalog, not
specifically the ERMSx (motion+safety) subset James happened to be
testing — confirmed by diffing a plain non-motion S2 catalog's real
export against a motion+safety ERMS2 one and finding the attribute
identical in both. Fixed in both generators (conditional on
`processor_type`/`catalog` starting with `"5069"`); regenerated all 90
affected files (`fw_catalog_matrix`'s 15 5069 catalogs x 6 firmware, plus
the module-sweep/variant/bender-full files that call `build_l5x`
directly). Whether this attribute is actually required for import or,
like `TimeSlice`/the `RedundancyInfo` pad percentages, Studio-5000-
optional is still unconfirmed — added regardless now that a real value
exists, same reasoning as those two.

**1769-family had the identical class of bug, found by generalizing**
(James: "the 5069 and 1769 have different backplane sizes based on the
catalog number ordered"). Worse than 5069's case: there was no `is_1769`
branch in `wrapper.py` at all, so every 1769 processor silently fell
through to the generic ICP-chassis `else` branch — wrong Port TYPE
(`"ICP"`), not just a wrong Bus Size number. Real corpus evidence
(`samples/local/DnR_Personal/TOYOTA_135453_20221024.L5X`, `1769-L33ERMS`)
shows a real, distinct `Type="Compact"` (neither 1756's `"ICP"` nor
5069's `"5069"`), single Ethernet port (unlike 5069's dual-Ethernet).
Fixed 2026-08-28: added the missing branch with the correct Port Type
and SafetyNetwork handling (mirroring the SIL2 fix, though not
independently confirmed as required for 1769 the way it was for 5069/
1756 — the one real corpus file has a populated SafetyNetwork but no
downstream safety module to test the orphaned-reference failure mode
against). Only ONE real per-catalog Bus Size data point exists
(`L33ERMS` → 17) — every other 1769 catalog's real max is genuinely
UNCONFIRMED, kept as an explicit fallback rather than guessed model-by-
model the way the 5069 table could be. The 9 existing `fw_baseline`
1769 files predate the current generator scripts (moved in from
elsewhere per `git log`, not reproducible via `python -m`) and already
pass conversion regardless (same "empty project never trips the
validation" pattern already confirmed for 5069) — not regenerated, the
structural fix matters for any NEW 1769 generation going forward.

[^eventtrigger]: James, 2026-08-25: "Does an event task triggered by MAW
cost more than an event task triggered by the EVENT instruction?" Real
corpus grep (12 real `Type="EVENT"` Tasks across SJ_Gormley_20251112_r02
and Sorter1_20260722r00) confirms exactly two real `EventTrigger` values:
"EVENT Instruction Only" (no EventTag) and "Axis Watch" (EventTag pointing
at a real `AXIS_CIP_DRIVE` tag — confirmed against Gormley's
`EM108_GradingLC`). "Axis Watch" is a Task-level config, not the MAW
*instruction* itself, but it's the real mechanism James's "MAW" question
maps to — there's no other real EVENT-trigger shape in the corpus.
Genuinely untested axis: every existing task-overhead calibration file
(`taskoverhead_n0Xtasks`, the ones that produced task_extra=+700) used
only CONTINUOUS/PERIODIC tasks, never EVENT — so it's currently unknown
whether EVENT itself costs differently from PERIODIC, on top of the
trigger-source question. `eventtask_instronly` and `eventtask_axiswatch`
(`gen_event_task_trigger.py`) mirror `taskoverhead_n02tasks` exactly
(1 Continuous + 1 extra Task, 5069-L306ER/fw35.11, NOP-only programs),
changing only the extra Task's Type/trigger, so direct deltas isolate
both questions. `eventtask_axiswatch` also declares a real
`AXIS_CIP_DRIVE` tag (EventTag must reference a real tag) — that tag has
its own separately-modeled cost and will need subtracting from the raw
capture delta before comparing trigger sources.

[^aoiorphan]: `gen_aoi_orphaned_def.py`. Both files declare the identical
`UtilOrphanTest` AOI (2 DINT Input params, 1 BOOL Output param, 5 DINT
LocalTags — a moderate utility-AOI shape, roughly matching the real
orphaned AOIs found in the source review, not a trivial single-param
stub). `aoi_orphaned_referenced` additionally declares a `UtilInstance`
tag of that type and one rung calling it
(`UtilOrphanTest(UtilInstance,0,0,OutBit);`); `aoi_orphaned_unreferenced`
has neither — same AOI definition, zero instances, zero calls, otherwise
byte-identical (same processor/firmware baseline, same empty-shell
structure). Current engine predicts 19,676 bytes for the referenced file
and 19,472 for the unreferenced one (a 204-byte delta covering the
instance tag + call-rung logic + this project's already-wired AOI
definition+instance formula) — real Capacity on both isolates whether
that 204-byte delta is actually the FULL real difference (current
`referenced_udts`-gated behavior is correct) or whether the "unreferenced"
file's real Capacity is meaningfully higher than baseline (orphaned AOI
definitions do cost real memory, and the gating is a genuine under-count
bug affecting every real project with unused/library AOI definitions).

[^blockbyte]: `gen_blockbyte_l71.py` (the 1756-L71 half) plus the earlier
`blockbytetest_dint120000` (1756-L81E, `sample_gen.cli tags --type DINT
--dims 120000`). Deliberately the simplest possible content: one DINT[
120000] tag, no other tags, minimal empty-shell program/task/routine, so
the predicted total decomposes into pieces that are all independently
verifiable by hand — 480,000 (120,000×4, atomic array sizing has zero
packing ambiguity per this project's own established rule) + 13,296
(project_baseline) + 4,816 (per-routine fixed_base) + 16 (single NOP rung)
= 498,236. Both files predict exactly that number by construction (same
content, same firmware 35.05/35.11, only `ProcessorType`/`ProductCode`
differ: 1756-L81E/164 vs 1756-L71/92). If both real Capacity readings
come back ~498,236, "block" and "byte" are the same unit, just a
different UI word per processor generation — no corpus-wide fix needed.
If they diverge, the ratio between them (almost certainly a clean
divisor/multiple of the 480,000 array-content portion, since that's the
overwhelming majority of the total) is the real block size, and every
formula in `memory_model.yaml` derived from L81E/5069-family data needs
rescaling by it — which is most of this project's real corpus.

[^compositescale]: `gen_composite_realistic.py` — a deterministic
index-based feature schedule (`_profile_for_index`), not randomness, so
every one of the 50 files' exact composition is reproducible and
documented in its own manifest.csv description. UDT 0 in every file
nests UDT 1 as a member (real "mixed and garbled" nesting pattern,
matching `gen_axis_composite.py`'s established real corpus shape).
Referenced AOIs get a real instance tag + a call rung
(`AoiName(InstanceTag,0,...,OutBit);`); orphaned AOIs get neither, same
mechanism as `gen_aoi_orphaned_def.py`. I/O modules are cycled from
`gen_module_sweep.py`'s `_MODULE_CHAINS` (86 real, previously-extracted
catalog blocks, never fabricated) via `(index*7) % 86` plus an offset, so
the 50 files sample a wide, deterministic spread of the catalog list
rather than always picking the same easy ones. The 24 files that hit an
unmodeled module shape fall back to `write_sample_unmodeled` and are
flagged in their own manifest description — real, already-documented
engine limitations (rack-aliased connections, legacy-network bridges,
modules with unrecognized nested member types), not something this batch
introduced. Full corpus crash-swept clean (1801 files, 0 crashes) and
140/140 unit tests pass with this batch included.
