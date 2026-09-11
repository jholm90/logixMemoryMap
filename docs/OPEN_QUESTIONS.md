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
   2026-08-30, once AHK capture was working for this family, as it
   already was for L7x — previously only ever built as single-firmware/v35
   `fw_baseline` files; now part of the full 6-firmware sweep too. Real
   bugs found in the re-add, same day, from live controller testing (not
   code review): every 1769 catalog used a single guessed Bus Size (17,
   only confirmed for L33ERM) and was missing a real embedded
   `Discrete_IO` module entirely (L16ER–L27ERM-QBFC1B all have one;
   L30ERM/L33ERM genuinely don't) — fixed by extracting the real
   per-catalog Modules block verbatim from the 9 `fw_baseline` reference
   exports. **That fix was itself wrong and has been narrowed back out,
   same day**, on a real chassis-size error from a minimal
   1769-L24ER-QB1B repro file with Bus Size="6". Chassis sizes must not be
   guessed; the earlier fix had applied a guessed size to most chassis
   actually use ones that were referenced"). The extracted Bus Size
   values were never independently real-confirmed — they came from the
   `fw_baseline` reference files, which themselves carry a "MANUAL
   ENTRY... clicking Estimate" caveat (built by switching ProcessorType
   in Controller Properties from a base project, never proven to have
   round-tripped through l5xgit import). The ONLY independently real-
   confirmed 1769 Compact-bus Bus Size anywhere in the corpus is
   L33ERMS=17 (`samples/local/DnR_Personal/TOYOTA_135453_20221024.L5X`,
   a genuine customer file) — and even that catalog is included in
   the "L24..L27 and the L3 series fail" report, so its failure has
   some other, still-unidentified cause even though its Bus Size checks
   out. `_1769_CATALOGS` is back down to just the 4 PointIO-bus catalogs
   (L16ER-BB1B/L18ER-BB1B/L18ERM-BB1B/L19ER-BB1B), empirically confirmed
   working in the live batch (all "ok" at v33). L24ER-QB1B,
   L24ER-QBFC1B, L27ERM-QBFC1B, L30ERM, and L33ERM are pulled from
   automated generation — 30 generated files and their manifest rows
   removed — until real per-catalog data (or an unambiguous root cause)
   exists, same treatment as 1756-L85ES/1756-L9x below. Not guessing
   again.

   2026-08-30 update, `samples/convert_log.csv` reconciled (the
   L5X->ACD conversion log, real per-file build outcomes, not guesswork):
   confirms L24ER-QB1B/L24ER-QBFC1B/L27ERM-QBFC1B/L30ERM genuinely never
   produce an ACD at any firmware version (`XMLSrv_E_IMPORT_ABORTED_
   NO_CHANGES`), settling that removal independent of the Bus Size
   question. But L33ERM — also pulled at the same time — actually DOES
   convert cleanly (`status=ok`, all 6 firmware versions, real per-file
   window titles) and carried 6 real manifest rows in the push;
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
   factor either. Needs a manual read of what Studio 5000 actually shows on
   one of these two capture batches before either set is trusted as real
   data.

   Separately, and more plausibly real: the 1756-L81ES/L82ES/L83ES/L84ES
   (GuardLogix safety) rows across the same push show small, consistent,
   real deltas — -3.91% (v31/v32), -3.55% (v33), -6.38% (v34/v35/v38) —
   same magnitude within each firmware group, genuinely error-free
   captures, a plausible real safety-baseline refinement rather than a
   capture artifact. Not yet derived/wired.

   2026-08-31, SOLVED — a real bug in the capture pipeline, not the model:
   the AHK/PowerShell capture was reading Studio 5000's I/O
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
   symptom of the same wrong-field capture). All 1769/L7x files need
   re-testing against the fixed pipeline; awaiting that re-run. Also flagged a caveat on `catalog_baseline_delta` in
   `memory_model.yaml` (the 8 real 1769-series ASSUMED baseline deltas) —
   different capture METHOD (manual "Estimate" click, not this AHK
   automation) so unconfirmed whether the same bug applies there, not
   changed numerically, but worth confirming directly.[^baseline]

2. **OQ-CMPCPTLAYOUT** — down to one thread. Uniform, T1+T2, T1T3/T2T3,
   and (as of 2026-08-29) the all-3-tier mix are ALL solved and wired,
   confirmed exact on every real data point on file. Only the REAL-
   operand/float-literal interaction remains open, and it's now a harder
   problem than "assumed linear, awaiting more points" — real new data
   shows it's genuinely NOT monotonic in operand count, ruling out any
   simple per-count model. 2026-08-30: the 12 `cptmix_*` probe files
   (float1/real1/real2/real3 position/adjacency/nesting variants) got
   real captures in the latest push — all land within 0.7-1.3% (188-272
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
    2026-08-30: the dense/isolating files got real captures in the
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

    **Real capture landed 2026-08-31 for the dedicated boundary-crossing
    isolation sweep** (`aoibp_boundary_bc{16,24,31,32,33,40,48}_n{02,04,
    08}_iso2`, bit-count families straddling several byte/dword
    boundaries, each at 3 instance counts) — and it sharpens the lead into
    a precise one. Five of the seven bit-count families (16, 24, 33, 40,
    48) show a flat delta across all 3 instance counts (+36, +52, +92,
    +108, +124 respectively) — confirming the fixed-per-family-offset
    pattern already found. But the two families AT the 32-bit/DWORD
    boundary — bc31 and bc32 — do NOT stay flat: bc31 goes 92→100→116
    (n=2/4/8) and bc32 goes 100→108→124, both a clean +4 bytes/instance
    on top of their own fixed offset. **Every other tested boundary is a
    pure fixed one-time cost; only the 32-bit/DWORD boundary specifically
    also carries a real per-instance term.** This pinpoints exactly which
    boundary crossing needs the extra term (the DWORD one) rather than
    leaving it as "some boundary, not derived" — genuine progress toward
    a wireable formula, though still needs the "why 32-bit specifically"
    mechanism nailed down (likely a real DINT-alignment packing rule) and
    a check of whether bc63/64 (the next DWORD-adjacent pair up) shows the
    same +4/instance signature before generalizing.

4. **OQ-SAFETYSCOPE-SIZING** — Task/Program/Routine SHELL sub-thread
   **decided and wired 2026-09-03**: safety tasks and safety programs are
   a separate memory pool and need their own sizing calculation.
   `report.py` now excludes Safety tasks/programs/routines from the
   ordinary `task_program_shell` aggregate entirely and charges a new
   flat `safety_task_program_shell` (296 bytes/file, see
   `memory_model.yaml`) once per file with at least one Safety task
   instead, replacing the old +1,456-byte ordinary-shell overcharge.
   Live-verified against all 24 real L81ES-L84ES fwmatrix rows: exact (0
   delta) at fw v31-v33, a known +16-byte (0.087%) residual at v34-v38
   (real SafetyProgram MainRoutine content apparently drops to 0 bytes on
   that firmware; this engine still predicts a firmware-independent 16 —
   a separate, tiny, content-side gap, not a shell gap, well inside the
   <1% North Star, not chased further).

   **Still genuinely open, separate sub-thread, NOT covered by the above
   decision**: whether resolvable Safety-CLASSED TAG content (`DCI_STOP`,
   real corpus evidence, 80 bytes; `CONFIGURABLE_ROUT`, wired 52 bytes but
   Safety-family by name-root) should be sized at all. The tool already
   warns rather than refuses on a Safety-rated project
   (`is_safety_project`, cli.py/ui/server.py), but these two Safety-classed
   tag types are still left unsized by convention, not by any code that
   enforces the exclusion. the shell decision doesn't resolve this —
   it was specifically about Task/Program/Routine containers, not tag
   content. Still needs a call: exclude Safety-class tags from sizing
   everywhere by design (and wire that exclusion explicitly), or size
   everything resolvable including Safety tag content and adjust the
   warning wording.[^safetyscope]

5. **OQ-AOIARRAYLOCALTAG** (was the open sub-thread of
   OQ-AOIARRAYDIMENSION, whose import-failure thread closed 2026-09-03 and
   is now in RESOLVED_QUESTIONS.md) — an AOI array LocalTag's DIMENSION was
   unpriced. **All 27 sweep files were captured 2026-09-03 and never
   reconciled. Reconciled and the main term WIRED 2026-09-11; four smaller
   things stay open and are measured by a new 20-file batch.**

   `aoi_definition` charged `per_declared_item` once per declared member
   regardless of `dimension`, so an array member's data space cost nothing.
   Against a prediction that was FLAT at every dimension:

       DINT dim   10    50   100    250    500   1000
       deficit   -41  -201  -401  -1001  -2001  -4001

   Exactly `element_size x dimension`, and by element type at dimension 50:
   SINT 1.0/element, DINT and REAL 4.0/element. Definition-side only — every
   `_1_instance` twin carries the same deficit, so an instance does not pay it
   again. Now wired through `compute_array_size` (not element size x
   dimension: CAM_PROFILE is a predefined ARRAY structure with no scalar
   element size, real programs declare ten of them, and it raised
   `UnknownDataTypeError` on the first real file the new term met). 27 rows
   went from -41..-4001 to inside +-4 on 20 of them.

   **Exposure, measured before deciding how much to spend on it:** array
   LocalTags are ~17 KB across the sixteen real programs — **0.036%**, worst
   single file 0.058%. Real-file mean |error| moved 2.1733% -> 2.1504%. This
   category will never be the reason a real file misses 1%, and the 20-file
   batch below is sized accordingly. It exists because unexplained rows sit
   inside a category that otherwise measures exactly, which is how a wrong
   constant gets adopted — not because the bytes are large.

   **Still open, and `gen_aoi_arraylocaltag2.py` (20 files) measures each:**

     - **BOOL, deliberately left unpriced.** `BOOL[50]` measured -13, which
       fits neither the 7-byte packed size nor an 8-byte two-word rounding.
       `albool_n{1,8,16,32,33,50,64,65}` walks the packing boundaries. Real
       programs do declare BOOL array LocalTags (2, 64 elements).
     - **An 8-byte discount per array member after the first.** 1/2/3 arrays
       of 50 DINT measured 200/392/592, not 200/400/600 — 196 per array after
       the first. Two points cannot say whether that is linear;
       `almult_n{04,06,08}` settles it. After wiring, n02/n03 sit at +8.
     - **Structure element types, never tested.** The sweep covered five
       atomics. Two thirds of the real exposure is MOTION_INSTRUCTION (16
       arrays / 112 elements), CAM_PROFILE (10 / 100), STRING (4) and TIMER
       (2). `altype_*_n00010` prices one array of each of six structure types.
       The dimensioned-structure LocalTag shape (no `Radix`, no data body,
       unlike a dimensioned atomic which keeps `Radix="Decimal"`) was taken
       verbatim from the real exports before building any of them.
     - **The dim=25 outlier.** Every other dimension lands at -1 after
       wiring; 25 lands at +3 — four bytes, exactly one element, off the line
       through 10 and 50. The file's XML does declare `Dimensions="25"`, so it
       is not a generator bug. `aldim_n000{24,25,26}` re-measures it with its
       neighbours: either a real granularity effect near there, or the
       original row was a capture artefact.

   `INT[50]` at -99 against its predicted 100 is the fifth loose end and is
   covered by the same wiring note rather than a file of its own: the
   existing INT row already brackets it, and the multiplicity and neighbour
   arms above test the two mechanisms (a per-array term, or 4-byte
   granularity) that could produce it.

6b. **OQ-MODULESTRUCTURAL** — NEW, 2026-09-04, and it changes the target
   for OQ-MODULEIO below. The target application is testing an unknown
   file, and every catalog module number cannot be captured
   individually — the model has to tell that a 16pt digital
   card has XX overhead + 16pts of data, whereas a 8pt analog card has
   different overhead."*

   The per-catalog `module_overhead_by_catalog` table is the wrong shape
   for the real goal. It can only ever cover catalogs we have personally
   captured; a real customer file will contain catalogs we've never seen,
   and those silently fall back to one flat cross-catalog default (1,672)
   that is badly wrong for whole families (the 5069 family sits +28% to
   +35% under-predicted on that default). The table should become a
   FALLBACK for known-exact catalogs, not the primary mechanism.

   What's needed instead: predict a module's overhead from its own
   STRUCTURE, which is already in the L5X and already parsed. First look
   at the evidence, 2026-09-04:
   * A naive structural regression (constant + module count + connection
     input/output/config bytes + module_defined_bytes) over the 98
     error-free single-module `modulesweep_*` captures lands at MAE 845
     bytes / 3.84% mean — better than nothing but not close to the <1%
     target, because it lumps genuinely different module CLASSES (simple
     discrete I/O, analog, drives, safety, network bridges) into one
     linear model.
   * The missing variable is class, and Rockwell already states it: every
     module carries its own PROFILE string on its Input/Output/Config tag
     (`ModuleInfo.input_profile` etc., already parsed since 2026-08-27).
     `AB:1756_DI:I:0` is "1756 digital input", `AB:1756_DO:C:0` is
     "1756 digital output config", `AB:1734_8SLOT:I:0` is an 8-slot
     PointIO adapter, `AB:MotionDevice_Diagnostics:S:0` a drive. This is
     catalog-INDEPENDENT and exactly the "16pt digital vs 8pt analog"
     axis needed here -- 1756-IA16 and 1756-IB16 are different
     catalogs but both `AB:1756_DI`. Across the 98 valid files there are
     143 distinct profile strings resolving to a much smaller set of
     class tokens (DI, DO, IB, OE, OF, SLOT, ...).
   * Point count is recoverable the same way (the `_16` / `_8SLOT`
     numeric token, cross-checkable against the real connection byte
     counts already parsed).

   Proposed model shape, NOT yet fitted or wired:
       overhead = class_base[profile_class] + per_point[class] * points
                  + per_connection_byte * (in + out + cfg)
   fitted per class from the single-module captures, with the existing
   per-catalog table kept as an exact-match override where we have real
   data. This is the single highest-value remaining architecture change
   for the North Star, because it is what makes an UNSEEN catalog
   predictable at all.

6. **OQ-MODULEIO** — mostly closed 2026-08-29. 126 real module captures
   were sitting unreconciled in manifest.csv; 51 catalogs now have a real
   per-catalog overhead value (exact-match rate on real data went from
   1/126 to 54/126). Two real sub-threads remain, both needing
   architecture work not more generation: multi-module marginal cost
   (adding a 2nd/3rd of the same module doesn't cost the same as the
   1st), and a handful of catalogs with real connection-variant-dependent
   overhead.[^moduleio]


    **CAPTURE ERRORS: 42 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    12 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `modulemotion_d012_dual_axis`, `modulemotion_d012_single_axis`, `modulemotion_s086_safety_axis`, `modulerack_kinetix_full_bus`, `modulesweep_193_ecm_etr_a`, `modulesweep_193_ecm_etr_b` (+6 more)
    30 committed file(s) attempted and never reached `ok` in
    `convert_log.csv`: `modulerack_bender_full_program`, `modulerack_bender_full_program_r2`, `modulesweep_1734_ob8s_a`, `modulesweep_1734_ob8s_a_r2`, `modulesweep_1734_ob8s_b`, `modulesweep_1734_ob8s_b_r2` (+24 more)

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

    2026-08-31, real, structurally important: `report.py`'s `is_jsr_target`
    branch treats a JSR target's own logic content as fully absorbed into
    the flat `jsr_fixed_base_per_routine`/`A(n)` cost, `continue`s past it,
    and never weighs its instructions at all — confirmed 2026-08-22, but
    only ever tested against a trivial `SBR(...)NOP();RET();` stub target.
    Real AccuTally review (confidential, not committed) found 123 real
    JSR-target routines averaging 85 real instructions each (one has 201)
    — 10,488 total real instructions currently contribute $0. Built
    `jsr_target_content_scale_{010,050,100,150}` (target content as the
    only variable, 13-153 real instructions) to test this directly — the
    engine predicts the identical 19,452 bytes regardless of target size,
    proving the model treats content as irrelevant; awaiting real capture
    to prove whether that's actually true.

    **Real capture landed 2026-08-31 — confirmed, and cleanly linear.**
    File suffix is the real instruction count (010=10, 050=50, 100=100,
    150=150 instructions). Real deltas: n=10 → +76 (0.39%), n=50 → +800
    (4.11%), n=100 → +1,696 (8.72%), n=150 → +2,600 (13.37%) — escalating
    smoothly with content size exactly as hypothesized, proving JSR-target
    logic content is NOT free. Fitting `delta(n) = a + b*n` against the two
    most separated points (n=50, n=150) gives `b=18, a=-100`; checked
    against n=10 and n=100, both land within 4 bytes of that line (a clean
    4-point linear fit, no residual pattern left over). **18 bytes/
    instruction is suspiciously close to this project's own already-
    confirmed weighted-average instruction cost for ordinary routine
    logic** — consistent with the real fix being architectural, not a new
    formula: stop `continue`-ing past JSR target routines in `report.py`
    and weigh their instructions with the SAME per-instruction-type table
    already confirmed for every other routine, rather than treating target
    content as a special zero-cost case.

    **WIRED 2026-08-31.** `report.py`'s `is_jsr_target` branch now calls
    `compute_routine_logic_bytes(routine, model.logic_instructions,
    tag_types, charge_shell=False)` on the target's own content (using the
    REAL per-instruction weight table already confirmed for ordinary
    routines, not a new guessed 18/instr constant) and adds it to the A(n)
    entry, merged into one `logic_entries` tuple per routine path (two
    separate tuples sharing a path would have silently collided in any
    by-path grouping — caught and fixed before committing). `charge_shell=
    False` confirms the target still doesn't pay its own
    `fixed_base_per_routine` — that stays folded into the caller's
    `jsr_fixed_base_per_routine` as before. Re-validated against the real
    capture data with the new code: residuals dropped from 0.39%/4.11%/
    8.72%/13.37% (n=10/50/100/150) to **-0.81%/-2.13%/-3.47%/-4.75%** —
    max error cut from 13.37% to 4.75%, using only already-trusted
    weights, no new constant. `jsr_midchain_real_chain`/`_leaf_control`
    also improved: predicted delta went from 144 (old, wrong) to 276 (new),
    against a real delta of 332 — most of the previously-reported 188-byte
    "midchain" gap was actually THIS SAME target-content gap, not a
    separate outbound-call cost; only 56 bytes remain unexplained now (down
    from 188), too small to isolate a per-outbound-call rate from one data
    point. 3 pre-existing tests in `test_logic_sizing.py` had hardcoded the
    old (now-disproven) "target content is free" expectation — updated to
    the correct values, plus a new dedicated regression test
    (`test_jsr_target_content_scales_with_instruction_count`) added.
    Remaining small negative residual (grows to -4.75% at n=150) is a new,
    much smaller, separate open thread — not urgent at this magnitude.

    Same review also found `is_jsr_target` is checked BEFORE whether that
    routine itself makes further JSR calls (`continue`s immediately) — a
    routine that's both a target and a caller (mid-chain) has its own
    outbound call cost dropped too. 29 real AccuTally routines are
    mid-chain; one makes 10 real JSR calls of its own. Built
    `jsr_midchain_real_chain`/`jsr_midchain_leaf_control` to isolate this
    (predicted delta is 144, fully explained by the leaf's own A(2)
    declaration cost and nothing for the mid-chain call — any real delta
    beyond 144 proves the gap).

    **Real capture landed 2026-08-31 — the gap is real.** Predicted delta
    (real_chain minus leaf_control) = 144, as expected. Real delta = 332
    (19,068 vs 18,736) — **188 bytes beyond what the leaf's own A(2)
    declaration cost explains**, confirming a genuine, previously-
    unmodeled cost for a routine that is both a JSR target AND itself
    issues an outbound JSR call. Only one data point (a single real_chain
    file, one outbound call) — enough to confirm the gap is real, not
    enough to isolate a per-outbound-call rate yet; needs an n-scale sweep
    (2/5/10 outbound calls from the same mid-chain routine, matching the
    real AccuTally routine that makes 10) before this is wireable.

    **STRING/UDT per-call surcharge — extended 2026-08-31 with n=1/3/5
    disentangle points** (`jsr_paramtype_{udt,string}_n{01,03,05}_
    r00100_iso2`, 100 calls each, param count as the only variable). Real
    deltas: UDT n=1→+428 (1.5%), n=3→+2,448 (7.44%), n=5→+4,064 (10.89%);
    STRING n=1→+428 (1.5%), n=3→+2,464 (7.43%), n=5→+4,096 (10.81%). Two
    findings: (1) STRING and UDT deltas are nearly identical at every n
    (within 16-32 bytes) — the surcharge looks like a general "non-atomic-
    typed JSR param" cost, not type-specific. (2) It is NOT cleanly linear
    in n — fitting `a+b*n` off n=1/n=5 predicts 2,246 at n=3 against a real
    2,448 (202 off, 8.3% miss), a real, non-trivial deviation from a
    straight line. Genuine progress (3x the data of the original single-n
    anchor), but the functional form isn't nailed down yet — needs either
    one more n point or the exact per-call-site byte breakdown to
    distinguish a fixed-plus-linear form from something else before
    wiring anything.

    2026-08-31, real, caught reviewing the target-content-scale
    files: "if there was no jsr parameters then there is no sbr/ret
    instructions inside the called subroutine." Checked against all 8
    real customer L5X files in `samples/local/` (2,534 unique real JSR
    targets): 2,314/2,315 zero-param targets have NO SBR at all,
    2,218/2,315 (95.8%) have no RET either — essentially a hard rule.
    Every EXISTING JSR calibration file in this project uses nonzero
    params (1/5/7/8/9/10/15) and correctly includes SBR/RET (126/128 real
    nonzero-param targets DO have SBR, confirming that whole existing
    calibration set is representative). Only the two brand-new
    target-content-scale files (0 params) had this bug — fixed by
    removing the forced SBR()/RET(), now just ordinary logic rungs
    matching the real, dominant, previously-untested case (AccuTally: 77%
    of real JSR calls are 0-param, and all 103 of its real 0-param
    targets have zero SBR/RET, matching the corpus norm exactly).


    **CAPTURE ERRORS: 4 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    4 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `jsr_target_content_scale_010`, `jsr_target_content_scale_050`, `jsr_target_content_scale_100`, `jsr_target_content_scale_150`

8. **OQ-EVENTTRIGGER** — new, real. task_extra (+700) was derived only
    from CONTINUOUS+PERIODIC tasks; EVENT-type tasks are completely
    untested, and so is trigger-source (Axis Watch vs. EVENT-instruction)
    within EVENT. Two files built, awaiting capture.[^eventtrigger]

    **`eventtask_instronly` real capture landed 2026-08-31 — the task-TYPE
    question is closed.** Predicted 19,600, real 19,600 — exact, 0.00%
    residual. `task_extra`'s existing formula (derived only from
    CONTINUOUS/PERIODIC before now) extends cleanly to an EVENT-type task
    with no separate term needed. Still open: `eventtask_axiswatch` (the
    trigger-SOURCE sub-question, Axis Watch vs. EVENT-instruction) has no
    real capture yet — that comparison is the only piece of this OQ still
    genuinely awaiting data.


    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    1 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `eventtask_axiswatch`

10. **OQ-BLOCKBYTE** — new, very serious if real. Raised 2026-08-30:
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
    readings. Awaiting capture on both (not yet in the tooling as of
    2026-08-30 — only just pushed at the time).

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

    **Import failure, 2026-08-30 — root-caused and fixed 2026-08-31.**
    `blockbytetest_l71_dint120000` failed to import. The real
    Studio 5000 error-log detail this time read ("Name collision: imported
    Module 'Local' renamed to 'Local1'" / "Required property 'Port' was
    missing" / Controller/EthernetPorts "Requested item could not be
    found"). Root cause: `wrapper.py`'s default branch assumed every
    non-1769/non-5069 processor is Ethernet-embedded like the L8xE family
    this project is built around — wrong for the older pre-5580
    ControlLogix line (1756-L6x/L7x), confirmed against a real reference
    export already in this repo (`samples/local/L7_v21_Sample.L5X`,
    ProcessorType="1756-L71"): its Local module has exactly one ICP Port,
    no embedded Ethernet Port, and the file has no Controller-level
    `<EthernetPorts>` element at all. Fixed with a dedicated
    `is_pre5580_1756` branch (ICP-only Local, no `<EthernetPorts>`) plus
    the real ProductCode (92) for 1756-L71. Regenerated, removed from
    `known_conversion_failures.csv`. Still needs a real reconversion pass
    to confirm the fix actually imports clean — not independently
    verifiable from here.

    **Circumstantial evidence now essentially CONFIRMED, 2026-08-31**
    (a real capture batch, merged into `manifest.csv` this pass).
    The full 1756-L7x/1769 firmware x catalog matrix came back with real
    Capacity numbers — and every one of them is flat, content- and
    firmware-independent:
      - All 25 `fwmatrix_v{31,32,34,35,38}_1756_l{71,72,73,74,75}` rows
        (5 distinct catalogs × 5 firmware versions, genuinely different
        ProductCode/Major-rev content each) read the exact same
        `actual_bytes = 30152`. Zero variance. **Extended 2026-08-31 with
        a 2nd push:** `fwmatrix_v31_1756_l{71,72,73,74}` (4 rows, `l75`
        missing from this group) all read `actual_bytes = 78312`, and
        `fwmatrix_v33_1756_l{71,72,73,74,75}` (full 5-catalog group) all
        read `actual_bytes = 87888` — two MORE flat values, same defect
        signature. Every one of these 30 L7x rows (old batch and new)
        ALSO has `controller_model` permanently stuck at `"5069-L306ER"`
        instead of the real L7x catalog it claims to test — direct
        evidence the capture window/project was never actually reloaded
        between these specific conversions, not merely a units question.
        Five distinct flat values across five capture groups now (30152,
        2976, 6640, 78312, 87888), none relating to each other or to this
        engine's predictions by a clean ratio.
      - All 20 `fwmatrix_v{31,32,34,35,38}_1769_l{16er,18er,18erm,19er}`
        rows (4 distinct catalogs with real, different embedded
        Discrete_IO module content, 5 firmware versions) read the exact
        same `actual_bytes = 2976`. Zero variance.
      - All 5 `fwmatrix_v{31,32,34,35,38}_1769_l33erm` rows read the
        exact same `actual_bytes = 6640`. Zero variance.
      Three different real numbers, but each one is IDENTICAL across
      every firmware version and (for the two multi-catalog groups)
      every distinct catalog within its family — genuinely different
      project content (different ProductCode, different real embedded
      module XML for the 1769 tier) cannot legitimately compile to a
      byte-identical Capacity reading. This isn't proof of the original
      "blocks vs bytes" unit-scale theory specifically (the three flat
      values don't relate to each other or to this engine's own
      predictions by any obvious clean ratio — 30152/2976 ≈ 10.13,
      30152/6640 ≈ 4.54, neither a round conversion factor), but it is
      now very strong, repeated (three independent capture groups
      across two sessions) evidence that the 1756-L7x/1769 real-capture
      *pipeline itself* is not reading genuine per-project memory usage
      for these two families — it's returning some fixed/default/stub
      reading regardless of content. Matches the tooling's own known
      quirk (`docs/TESTING_PLAN.md`: "the AHK capture pipeline couldn't
      read a 1769's Capacity value without a manual 'Estimate' button
      click first... now resolved on the end" — this data suggests
      that fix may not actually be reading the real value, just no
      longer erroring). **None of this 45-row batch should be treated as
      real ground truth or used to tune any formula** until it is
      confirmed what the AHK script is actually reading for these two
      families (a live screenshot/manual cross-check against Controller
      Properties → Capacity in Studio 5000 for one single 1769/L7x file
      would settle it immediately).

      **`blockbytetest_l71_dint120000` real capture landed 2026-08-31 —
      and it changes the conclusion.** This is the dedicated, clean,
      isolated two-file test (byte-identical content: one DINT[120000]
      tag, nothing else) that this whole OQ was built to settle, and it
      is NOT contaminated by the fw_catalog_matrix pipeline defect above
      (distinct real Capacity value, `controller_model` correctly reads
      the right family for its own row, 0 errors, clean window title).
      Both halves of the pair:
        - `blockbytetest_dint120000` (1756-L81E): predicted 498,236,
          real 498,240 — 4-byte residual, essentially exact.
        - `blockbytetest_l71_dint120000` (1756-L71, byte-identical
          content): predicted 498,236 (same), real 569,336 — **+71,100
          bytes (14.27%) more than the identical L81E file.**
      The ratio (569336/498236 ≈ 1.143) is not a clean unit-conversion
      factor (not 2x, 10x, or anything round) — ruling out the original
      "blocks vs bytes" unit-SCALING theory this OQ was named for. What
      it looks like instead is a real, ADDITIVE per-family baseline
      difference: 1756-L71 (pre-5580 ControlLogix, same architecture
      generation as 1769/CompactLogix 5370) genuinely consumes more real
      memory than 1756-L81E (5580) for identical content — consistent
      with, and now corroborating, the already-documented `[^baseline]`
      finding that "1769-series runs 69,600-98,944, far above the flat
      prediction." **Revised conclusion: this is very likely a real
      pre-5580-family baseline/overhead gap, not a unit-labeling bug** —
      the "bytes" vs "blocks" label difference may be a real Studio
      5000 UI distinction, but it doesn't appear to be *why* the L7x/1769
      numbers run high; a real per-family baseline term (analogous to the
      already-wired firmware-version baseline deltas) is the more likely
      fix once more clean (non-contaminated) L7x data points exist to fit
      it. Still needs at least one more clean L7x data point (ideally a
      near-empty-baseline file, to isolate the constant term from the
      content-scaling term) before wiring anything — one point can locate
      a family-level gap but can't separate "baseline is bigger" from "per
      element is bigger" on its own.


    **CAPTURE ERRORS: 35 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    35 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `composite_realistic_03_r2`, `composite_realistic_04_r2`, `composite_realistic_05_r2`, `composite_realistic_06_r2`, `composite_realistic_08_r2`, `composite_realistic_09_r2` (+29 more)

11. **OQ-COMPOSITESCALE** — new, real, raised 2026-08-30 after a review of
    a confidential project found a >20% real gap. The requirement: at
    least 50 large programs with I/O and logic, exercising AOIs and UDTs
    at production scale. Every calibration file in this
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
    CPT/TON/CTU/AOI-calls. All on the wrapper's default 1756-L81E/fw35.05
    (corrected 2026-08-31; the processor-family question is isolated
    separately, OQ-BLOCKBYTE, to keep this batch's findings unambiguous).
    26 of the 50 have a fully-predicted total; 24 hit an already-known
    unmodeled real I/O module shape
    (rack-aliased connections, legacy-network bridges, a handful of
    modules with unrecognized nested member types) and fall back to
    predicted_bytes=0/unmodeled, same convention as elsewhere in this
    project — genuinely unmodeled, not a bug in this batch. Real Capacity
    on the 26 fully-predicted files is the actual test: if predicted and
    real land within ~1% at this scale, the individually-confirmed
    formulas really are additive; any real divergence pinpoints an
    interaction effect (or a formula that only breaks at
    scale/density) invisible to every prior isolated test.[^compositescale]

    **Import failures, 2026-08-30 (the l5x2acd run) — 14 of the 50
    fail, not just "awaiting capture."** All 14 hit the same generic
    `XMLSrv_E_IMPORT_ABORTED_NO_CHANGES` wrapper text, no per-file detail.
    Cross-referenced every file's module catalog mix (deterministic,
    computed via `_profile_for_index`) against
    `samples/known_conversion_failures.csv`'s already-known-bad catalog
    list:
      - **8 fully explained** — each includes at least one already-known-
        bad catalog baked into its module mix, no separate cause:
        `composite_realistic_10` (5069-OB16/B, 5069-OBV8S/A),
        `_11` (FANUC Robot R30iB Plus/A), `_22` (5069-IY4/A, 5069-OB16/A,
        5069-OB16/B), `_34` (5069-IB16/A, 5069-IB8S/A, 5069-IY4/A),
        `_36` (PowerFlex 527-STO CIP Safety), `_46` (442G-MABLB-UR-
        E0JP4679/A, 5069-IB16/A), `_47` (5069-OBV8S/A), `_48` (FANUC
        Robot R30iB Plus/A).
      - **6 genuinely new and unexplained (at the time)** — module mix
        contains NO already-known-bad catalog: `composite_realistic_07`
        (1794-OE4/B, 1794-OW8/A, 1794-VHSC/A), `_19` (1794-IR8/A,
        1794-OA8/A, 1794-OE4/B), `_31` (1794-IB16XOB16P/A, 1794-IB32/A,
        1794-IR8/A), `_32` (193-ECM-ETR/A, 193-ECM-ETR/B, 2097-V34PR5-LM,
        2198-C4004-ERS), `_43` (1794-IA16/A, 1794-IB16/A,
        1794-IB16XOB16P/A), `_44` (1794-OW8/A, 1794-VHSC/A,
        193-ECM-ETR/A, 193-ECM-ETR/B).

        **Root-caused and fixed, 2026-08-31**, from the real
        Studio 5000 error-log detail for `_07`: "Slot number in use by
        another module" + "Failed to set the 'ParentModule' property
        (Requested item could not be found.)". All three of `_07`'s
        catalogs were extracted from the SAME real reference export
        (`RobbinsGrn_2026_05_13r00.L5X`) and each independently claims the
        identical real backplane slot that one customer's rack actually
        used — fine standalone, a genuine collision once 2+ such catalogs
        land in the same composite file (same class of bug as the IP
        collision `_modules_xml_unique_ips` already fixed 2026-08-30, just
        a different attribute). Fixed by also remapping each catalog's own
        Local-parented ICP slot to a unique value per file
        (`_remap_local_icp_slot`, `gen_composite_realistic.py`). `_19`,
        `_31`, `_43`, `_44` share the same "2+ catalogs from the same real
        1794-family source rack" pattern and are very likely fixed by the
        same change (not independently confirmed each, but the mechanism
        is generic, not `_07`-specific) — removed from
        `known_conversion_failures.csv` alongside `_07`. `_32` has NO
        1794-family catalog in its mix at all, so this fix doesn't apply
        to it — stays in `known_conversion_failures.csv`, genuinely still
        unexplained, still needs its own real error-log line.

      All 8 catalog-explained failures (`_10`, `_11`, `_22`, `_34`, `_36`,
      `_46`, `_47`, `_48`) remain in `known_conversion_failures.csv` —
      unrelated bug class (the still-undiagnosed CIP-Safety-connection
      failure shared with the standalone modulesweep files), not touched
      by this fix. Cross-checked against which of the 50 have a
      fully-predicted total (predicted_bytes != 0 in manifest.csv, 26
      files) vs which fell back to unmodeled (predicted_bytes=0, 24
      files): 8 of the 14 original failures (`_10`, `_11`, `_22`, `_32`,
      `_34`, `_36`, `_46`, `_48`) are among the 26 fully-predicted files.
      Of those 8, only `_32` is still blocked — the other 7 remain fully
      catalog-explained and still blocked by the separate CIP-Safety bug,
      so real capture on this OQ is still gated on that unrelated fix
      too. `_07`, `_19`, `_31`, `_43`, `_44` were already unmodeled/$0,
      so fixing their import doesn't add real-capture value to this OQ
      directly, but does let them serve as clean structural validation
      (does the file import and match the real module count/shape) even
      without a byte comparison. Needs a real reconversion pass to
      confirm any of this — not independently verifiable from here.

      **Renamed with a "_r2" suffix, 2026-08-31.** The 50 tests needed
      new filenames and the old ones abandoned: real Studio 5000 verify
      errors found separately (see
      OQ item covering aoi_call_arg_count_mismatch/XIC-OTE-data-type,
      meant every one of the 50 composite files changed real content
      again after an l5x2acd batch had already run against the
      names above). All references to `composite_realistic_NN` in this
      section are the OLD, now-deleted filenames, describing what was
      diagnosed against them at the time — the CURRENT files are
      `composite_realistic_NN_r2.L5X` (same index numbers, same
      per-file composition/catalog mix, just fixed content). The 9 still
      catalog-explained-broken filenames in `known_conversion_failures.csv`
      were updated to their new `_r2` names alongside this rename so
      they stay correctly flagged.

      **Real capture landed, 2026-08-31 — the core question is
      essentially answered, and it's good news.** the batch
      captured real Capacity for 36 of the old-named files; 18 of those
      are among the 26 fully-predicted (not catalog-explained-broken,
      not unmodeled) composites — mapped onto the current `_r2` rows
      (confirmed safe: predicted_bytes is identical before/after the
      AOI-arg/XIC-OTE fixes for every index checked). Real vs predicted
      across those 18: **mean +3.15% underprediction, range -0.46% to
      +5.25%**, only one file (`_03`, -0.46%) overpredicted. This is a
      dramatically better result than the >20% real gap on the
      confidential project that started this whole OQ — at realistic
      project scale/density (multiple UDTs/AOIs/arrays/modules/rungs
      combined), the individually-confirmed formulas ARE essentially
      additive; no interaction effect blew up the total the way the
      confidential-project review worried it might. The remaining ~3%
      is small but real and consistently one-directional (17/18 files
      underpredict, not scattered noise) — worth a future investigation
      into which specific residual bucket accounts for it (candidates:
      the still-ESTIMATED-tier logic-content weighting, or a small
      per-file baseline this project hasn't isolated yet), but not
      urgent at this magnitude. The other 8 fully-predicted composites
      (`_10/_11/_22/_34/_36/_46/_47/_48`) remain blocked on the separate
      CIP-Safety-catalog import bug, still no real data for them.

      **Candidate hypothesis proposed 2026-08-31, RULED OUT same day once
      wired.** The OQ-JSRPARAMCOST target-content fix and OQ-AOIINTERNAL-
      LOGIC fix above were both wired and re-checked directly against
      these 18 composite files: **the residual is completely unchanged,
      byte-for-byte, before and after both fixes** (mean still +3.28%,
      same range -0.45% to +5.55%). Root cause: despite the composite
      generator's own docstring claiming "AOI calls... mixing... AOI-
      calls," `gen_composite_realistic.py`'s AOI definitions still use the
      OLD hardcoded self-closing `<Routine Name="Logic" Type="RLL"/>`
      shape (never updated to pass `aoi_xml()`'s `logic_rungs_xml` param,
      the same gap OQ-AOIINTERNALLOGIC found everywhere else) — so there's
      no internal AOI content to weigh in these files either way. Same for
      JSR: the composite generator doesn't appear to declare any JSR-
      target routines with real content. **The composite batch's ~3%
      residual remains genuinely unexplained** — this was a real, testable
      hypothesis, tested directly against real data, and it didn't hold;
      not left as an untested guess.

      **6 more real captures landed 2026-08-31** for composites that fall
      back to unmodeled (`predicted_bytes=0`): `composite_realistic_
      {02,07,19,31,43,44}_r2` now have real Capacity on file (69,048 /
      108,712 / 175,528 / 235,272 / 300,976 / 274,882) but aren't usable
      for tuning anything — no predicted total to compare against. Kept on
      record for whenever the unmodeled real-I/O-module shapes these files
      hit get real formulas of their own.

      **New v2 batch, 2026-09-02 — the residual reappears at a MUCH larger
      magnitude once composites actually exercise AOI-internal-logic and
      JSR-target content, and this time it's explained and wired.**
      Against the 2026-08-30 requirement for 50 large programs with I/O and
      logic, `gen_composite_realistic_v2.py`
      built 50 new files, same UDT/array/module/AOI-declaration shape as v1
      but with every referenced AOI now carrying real internal Logic-
      routine content (5-45 real instructions) and one real 0-param JSR-
      target subroutine per file (20-220 real instructions) — the two gaps
      OQ-JSRPARAMCOST/OQ-AOIINTERNALLOGIC found and wired in isolation,
      now exercised together at composite scale for the first time. Real
      capture landed against all 50 (5 files — `_07`/`_18`/`_19`/`_30`/
      `_50` — carry real Studio 5000 import errors unrelated to sizing: a
      193-ECM-ETR module-compatibility issue and a safety-drive-on-
      non-safety-PLC issue in the module mix, both deprioritized as
      generator-script fixes, not sizing bugs; excluded from all figures
      below). Before any composite-scale fix, the 45 error-free files
      under-predicted by a mean **+5.16%** even with both isolated-test
      fixes already wired — the composite hypothesis this OQ's 2026-08-31
      entry ruled out for v1 (v1 never exercised either gap) turned out to
      be real once a generator actually did exercise them.

      Linear regression (`np.linalg.lstsq`, no intercept) of real residual
      bytes against candidate explanatory variables across the 22 files
      with BOTH zero reported import errors AND a fully-modeled I/O mix
      (indices 1,2,3,4,8,9,10,21,23,26,27,29,31,32,33,34,37,40,42,43,45,46):
      `residual ≈ 20.155 × (AOI-internal-logic instruction count) +
      47.331 × (JSR-target instruction count)`, R²=0.6619511766511494, mean
      abs error 1,507.79 bytes. Beat a flat-%-of-predicted model (R²=0.6015)
      and a combined model (R²=0.6631 — barely better, with the flat-%
      term going slightly negative, meaning the content-count model does
      the real work, not a size proxy). Rounded and wired 2026-09-02 as
      `aoi_logic_composite_surcharge_per_instr: 20` and
      `jsr_target_composite_surcharge_per_instr: 47`
      (`memory_model.yaml`/`constants.py`), applied additively on top of
      the already-wired per-instruction content weight at both the
      AOI-internal-logic and JSR-target-content sites in `report.py`.

      **Re-validated post-wiring: mean abs error on the 22 clean files
      drops from 5.16% to 1.06% (max 5.66%, file #10); all 45 error-free
      v2 files average 1.17% mean abs error.** Confidence is FITTED, not
      KNOWN — R²=0.66 leaves real unexplained variance (max residual still
      5.66% on one file), and the JSR rate being ~2.3x the AOI rate despite
      a similar real instruction mix is not yet mechanistically understood,
      just what the real data shows. More isolated real data — ideally
      varying AOI-count/JSR-content independently of overall file scale,
      rather than all three scaling together as they do in this batch —
      would sharpen or could disprove either constant. The 5 error-flagged
      files' generation-script fixes (module catalog compatibility,
      sequential slot numbering) remain separately tracked and
      deprioritized until this tuning work lands.


    **CAPTURE ERRORS: 47 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    47 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `composite_realistic_v3_02`, `composite_realistic_v3_03`, `composite_realistic_v3_04`, `composite_realistic_v3_05`, `composite_realistic_v3_06`, `composite_realistic_v3_07` (+41 more)

12. **OQ-AOIINTERNALLOGIC** — new, real, corpus-wide gap, found 2026-08-31:
    AOIs were closed out without ever putting logic inside one. Every AOI
    has at least one internal subroutine and can have more (HomeToTorque
    is the real example).
    `aoi_xml()` (builders.py) has hardcoded a self-closing
    `<Routine Name="Logic" Type="RLL"/>` for EVERY AOI test file this
    project has ever generated — $0 real internal-logic content has ever
    been exercised in ANY AOI calibration file, and the shared builder
    never supported more than one internal routine. The existing
    `aoi_definition` formula (base + per_declared_item*count +
    name-length term) is purely a Parameter/LocalTag declaration-cost
    model — it has never been tested against real Logic-routine content
    or a second internal routine, both of which are common in real AOIs.
    Real confidential-project review (not committed, never named beyond
    this generic description) confirms this is a real, material gap: 39
    real AOI definitions there have 573 total real rungs of internal
    logic (111,507 chars) — 100% currently unsized anywhere in this
    project — and 8 of the 39 have 2 internal RLL routines, not 1 (e.g.
    HomeToTorque: Logic 21 rungs + EnableInFalse 1 rung). Fixed the
    builder (`logic_rungs_xml`/`extra_routines_xml` params, both default
    `""`, confirmed byte-identical output for every existing caller) and
    built `aoi_logic_scale_{000,010,050,100}` (Logic-content-scale sweep)
    plus `aoi_multiroutine_control`/`aoi_multiroutine_real` (mirrors
    HomeToTorque's real 2-routine shape exactly) — all 6 predict the
    identical 19,440 bytes regardless of Logic content size or
    second-routine presence, confirming both are currently zero-weighted.
    Awaiting real capture; if either scales with real Capacity, this is a
    second, independent, currently-unmodeled cost category on top of
    OQ-JSRPARAMCOST's target-content finding — real AccuTally logic
    content (routine + AOI-internal combined) may be substantially larger
    than this project has ever priced.

    **Real capture landed 2026-08-31 — confirmed, AOI internal logic
    content is NOT free, and multi-routine vs single-routine content of
    the same size costs the same.** All 6 files share predicted 19,440
    (the model still doesn't weigh AOI-internal logic at all). Real
    results: `aoi_logic_scale_000` (0 rungs) → 19,440, exact 0.00% —
    confirms the empty-shell baseline itself is right. `_010` → 19,676
    (+236, 1.21%), `_050` → 20,620 (+1,180, 6.07%), `_100` → 21,776
    (+2,336, 12.02%) — a clean, escalating, real cost that scales with
    logic-content size, same shape as the JSR-target-content finding
    above. `aoi_multiroutine_control` (HomeToTorque's real 2-routine
    shape, same total content as `_050`) reads the exact same 20,620 as
    `_050` — **splitting the same content across 2 internal routines
    instead of 1 costs identically to keeping it in one routine**, so the
    per-routine count itself isn't a separate cost driver, only total
    content is. `aoi_multiroutine_real` (the literal HomeToTorque content,
    not a synthetic same-size stand-in) reads 20,912 (+1,472, 7.57%) —
    close to but not identical to `_control`, the gap presumably from real
    instruction-mix differences (HomeToTorque's real rungs vs the
    synthetic control's), not the routine-count structure. **Architectural
    conclusion: AOI internal Logic-routine content should be weighed with
    the same per-instruction model as ordinary routine logic (same fix
    direction as the JSR-target-content finding above), not treated as
    zero-cost; the per-routine-count dimension can be dropped from the
    model entirely — real data shows it doesn't matter.**

    **WIRED 2026-08-31.** New `parser/logic.py` function,
    `parse_aoi_internal_logic()`: walks `Controller/
    AddOnInstructionDefinitions/AddOnInstructionDefinition/Routines/
    Routine` for every AOI definition and aggregates ALL of its internal
    RLL routines' rung text into ONE pseudo-`RoutineLogic` per AOI name
    (deliberately not tracked per-routine, matching the confirmed "routine
    count doesn't matter" finding). `report.py`'s AOI-definition-cost path
    now calls `compute_routine_logic_bytes(..., charge_shell=False)` on
    that aggregate and adds it to the existing param/localtag declaration
    cost (`AoiDefinitionModel` untouched — confirmed via the n=0 file
    landing at an exact 0.00% match, so no double-counting). Re-validated
    against real data: residuals dropped from 0.00%/1.21%/6.07%/12.02%
    (n=0/10/50/100) to **0.00%/0.00%/-0.29%/-0.55%** — essentially exact
    at every point tested, max error cut from 12.02% to 0.55%.
    `aoi_multiroutine_control` (2 internal routines, same total content as
    `_050`) now predicts identically to `_050` as designed (-0.29%);
    `aoi_multiroutine_real` (literal HomeToTorque content) lands at +1.02%,
    a small real instruction-mix difference, not a routine-count effect.
    **Checked against `gen_composite_realistic.py`'s AOI calls: this fix
    does NOT move the composite batch's ~3% residual at all** — that
    generator still uses the old hardcoded self-closing `<Routine
    Name="Logic" Type="RLL"/>` shape (never updated to use `aoi_xml()`'s
    new `logic_rungs_xml` param), so its AOIs have zero internal content to
    weigh either way. **Correcting the composite-residual hypothesis
    written earlier in the same pass** (see OQ-COMPOSITESCALE below): neither
    this fix nor the JSR-target-content fix explains the composite
    batch's residual, since composite files don't currently exercise
    either gap — that residual's real source is still unidentified.

13. **OQ-IDENTNAMELEN** — new, real, found 2026-08-31 in the same push as
    the "5/10/15/20/50 subroutines... different routine name lengths"
    directive. `gen_jsr_multi_distinct_targets_scale.py`'s
    `group_name_length` (10 fixed JSR targets, name length swept 4/8/16/
    32/40 chars — 40 capped per Rockwell's real Logix identifier limit,
    see that generator's own comment) and `gen_program_multi_distinct_
    scale.py`'s matching `group_name_length` (10 fixed extra Programs,
    same length sweep) both currently predict a FLAT total regardless of
    name length — neither `jsr_target_param_counts`' `A(n)` nor
    `task_program_shell`'s `program_extra` has a name-length term, unlike
    tags/UDTs/AOI definitions (all confirmed real name-length bucket
    costs already).

    **Real capture landed 2026-08-31 for both sweeps at namelen04/08/16/
    32 (namelen40 not yet captured — that variant failed import under the
    old, invalid namelen48; see the fix below) — and the two
    independent sweeps show the SAME real pattern.** Deltas (against the
    flat predicted baseline, so pure name-length signal) at len 4/8/16/32,
    10 items per file:
      - JSR targets: +1,440 / +1,520 / +1,600 / +1,760 (7.13% / 7.53% /
        7.92% / 8.72%)
      - Programs: -160 / -80 / 0 / +160 (-0.62% / -0.31% / 0.00% / 0.62%)
    (JSR shows a large constant offset because its predicted baseline is
    already under-costed by the separate, still-open target-content and
    per-param findings above; Programs' baseline is exact at len=16 so its
    deltas read as pure signal directly.) Per-item, both sweeps show the
    IDENTICAL step shape: +8/item from len4→len8 (a 4-char step), +8/item
    from len8→len16 (an 8-char step — HALF the per-char rate of the first
    step), +16/item from len16→len32 (a 16-char step — same per-char rate
    as the second step). Expressed relative to a 4-char name: `extra_bytes
    (len) = 2*(min(len,8)-4)` for `4<=len<=8`, `= len` for `len>8` — fits
    all 8 real data points (both sweeps) within rounding. The doubled rate
    in the first 4-char step, then a steady ~1 byte/char/item above that,
    is consistent with a real 8-byte-aligned minimum name-field allocation
    (matches the shape, though not the exact constants, of the already-
    wired AOI type-name-length bucket formula). **Real, general, and
    reproducible across two independent identifier classes (JSR target
    routine names, Program names) — genuinely new, not previously known,
    and NOT yet wired.** Needs the len=40 capture (in flight) to confirm
    the fit holds at the real Rockwell maximum before committing to
    exact constants, and a decision on whether this generalizes to
    Routine names too (untested) or is specific to JSR-target/Program
    identifiers.

14. **OQ-193ECMETR** — new, real, genuinely undiagnosed (now covering TWO
    catalogs — see the correction below). 2026-09-02, real Studio
    5000 error on `composite_realistic_v2_18`/`_50` ("Error:
    TestMod2_193ECMETRA: Child module incompatible with parent module").
    Self-audit (checking for real currently-unreconciled `error_count`
    data per CLAUDE.md's standing rule, not just the composite files
    originally reported) found this is NOT composite-specific: BOTH standalone
    `modulesweep_193_ecm_etr_a`/`_b` already carry a real `error_count=1`
    in `manifest.csv` — sitting there uninvestigated since capture, never
    previously flagged. No real Studio 5000 error-log line exists for the
    standalone repro (only the composite-context quote above), so the
    exact cause is unconfirmed — plausible candidates (EKey/revision
    mismatch between the extracted 1756-EN4TR adapter and the E300 relay
    child, or the E300 family needing a different real parent device
    entirely) are just guesses, not verified. Excluded from
    `gen_composite_realistic.py`'s module pool
    (`_UNDIAGNOSED_COMPOSITE_CATALOGS`) so future composite files stop
    reproducing it. Needs the real per-file Studio 5000 error-log detail
    (not just the generic error line already quoted) to actually
    root-cause.

    **CORRECTION, same day, within the hour:** `2198-S130-ERS3` was
    initially diagnosed below as "requires a safety-capable controller"
    and wired into `_SIL2_CATALOGS` — DISPROVEN by real evidence almost
    immediately after: a real production file
    (`TitusvilleTrimmer_20260902r2.L5X`) runs a real `2198-D057-ERS3`
    module (`EM113_TrimmerLC_EM109_TrimInfdLC`) on a plain non-safety
    1756-L82E (`<SafetyInfo/>` empty, no SafetyTask anywhere) —
    `SafetyEnabled="false"`, no `SafetyNetwork`, structurally the same
    shape this project's own genericized block already uses. An
    "-ERS3" catalog genuinely CAN run on a non-safety controller for
    real, so the safety-controller theory is wrong. Reverted out of
    `_SIL2_CATALOGS`. The real `error_count=2` signal on
    `modulesweep_2198_s130_ers3` (and the clean 7/7 correlation across
    every "-ERS3" catalog in the corpus) is still real and still
    unexplained — `2198-S130-ERS3` moves into the SAME genuinely-
    undiagnosed bucket as `193-ECM-ETR/A`/`/B` above
    (`_UNDIAGNOSED_COMPOSITE_CATALOGS`) rather than standing on a second
    guessed theory.

    **SOLVED 2026-09-06, and the lead above was close.** The genericized
    `-ERS3` blocks were indeed missing something the real modules carry: the
    `<ExtendedProperties>` element (Vendor, CatNum, FeedbackDevice1-4,
    ConfigID), plus a corrupted ConfigData payload of 119 L5K values against
    the real 118. Both confirmed by diffing against
    `composite_realistic_v4_001`, which carries the same catalogs on a plain
    non-safety 1756-L81E and captured at zero errors — one of 31 such files.
    The `<ExtendedProperties>` fix had already been made on 2026-09-03 in
    `gen_module_motion.py`'s `_drive_module_xml()`;
    `gen_module_sweep_variants.py` keeps a separate hardcoded copy of the
    module XML and never received it. Full entry in RESOLVED_QUESTIONS.md.

    **Worth recording, because it cost real time:** the safety-controller
    theory was disproven here, in writing, with real evidence — and was then
    re-derived from scratch two weeks later and briefly wired into a lint
    rule that flagged the known-good files. The disproof was in this
    document the whole time. Read the correction before re-opening a
    question, and check the repo for files that already work before
    theorising about why one does not.

    **New real evidence, 2026-09-03 — the "missing Motion/Axis
    association" lead above is now DISPROVEN too.** All 50
    `composite_realistic_v3_*` files hit the exact same 2-error signature
    on real Studio 5000 conversion: `Tag 'D012_23:SI': Invalid
    data type for safety tag` + `Project size exceeds controller
    capacity` — 2 errors, matching the "clean X/X correlation" pattern
    already noted above for other "-ERS3" catalogs. Critically, v3's
    `2198-D012-ERS3` module is NOT missing a Motion/Axis association the
    way `modulesweep_2198_s130_ers3` was — it's dual-axis-bound (2 real
    `AXIS_CIP_DRIVE` tags, `MotionModule="D012_NN:Ch1"`/`"...Ch2"`,
    matching `gen_module_motion.py`'s already-real, already-confirmed
    shape) plus a shared MOTION_GROUP tag, and STILL hits the identical
    error. So the "needs a real axis" theory doesn't hold either — every
    "-ERS3" catalog this project has ever generated fails this way
    (with or without an axis bound), while only a real
    Titusville production file has ever shown it working. Direct,
    attribute-by-attribute comparison of a real `2198-D057-ERS3`
    Module block (from Titusville) against this project's generated
    `2198-D012-ERS3` block found them structurally near-identical
    (same Ports/EKey/Communications/Connections shape, same
    `SafetyEnabled="false"`, no `SafetyNetwork`) — the one confirmed
    difference is the real block's `<ExtendedProperties>`
    (`Vendor`/`CatNum`/`FeedbackDevice1-4`/`ConfigID`) is entirely absent
    from every generated instance, but that can't be confirmed as the
    cause either: `gen_module_sweep_variants.py`'s own real-corpus-
    verbatim `2198-D012-ERS3` "2conn" block (source:
    `motion_p208/p208_D012_NodeAndAxisDual3.L5X`, a real reference
    export) ALSO has no `<ExtendedProperties>` and the exact same zeroed
    `ControllerToDriveConnectionSize`/etc. diagnostic fields our
    generator produces — meaning that shape was already confirmed real
    once, not a generator bug in itself, so a missing `ConfigID` isn't a
    safe conclusion without a same-catalog real counter-example that DOES
    import clean. Still needs the raw Designer error-log detail (not
    l5xgit's one-line summary) or a same-catalog Titusville-style real
    file confirmed to import successfully in isolation to make further
    progress — not re-guessing a third theory here. `Project size exceeds
    controller capacity` is unconfirmed whether it's a second real issue
    or a downstream artifact of the first import failure (this project's
    own established pattern elsewhere: a primary import failure has
    previously been found to silently produce a second, misleading
    symptom — see the IP-duplicate/axis-tags-never-made finding,
    2026-08-27, `gen_module_motion.py`).

    **Real generator bug found and fixed, 2026-09-03 — root cause of the
    SI/SO error still NOT confirmed, but a real, independently-confirmed
    channel-numbering mistake found and corrected along the way.** This
    project's own real source file for the dual-axis case
    (`motion_p208/p208_D012_NodeAndAxisDual.L5X`/`Dual3.L5X`, which
    `gen_module_motion.py`'s own docstring claims to genericize
    "structurally verbatim") uses `MotionModule="D012_1:Ch1"` and
    `"...Ch3"` for its two axis tags — **never Ch2.** Both
    `gen_module_motion.py`'s `group_motion_dual_axis_drive()` and
    `gen_composite_realistic_v3.py` had instead hand-typed `Ch2` for the
    second axis — a real transcription bug, confirmed independently
    against 2 real corpus files, not a guess. Fixed (Ch2 -> Ch3 in both
    places), all affected files regenerated, lint-clean.

    **CORRECTION, same day, within the hour:** initially theorized Ch2
    might be internally reserved for the drive's Safe-Torque-Off/safety
    channel, explaining the SI/SO auto-creation — disproven
    immediately by two more real reference exports
    (`SampleAxis.L5X`/`SampleAxis_2and4.L5X`): a real 4-axis Kinetix 5700
    config genuinely uses all 4 channels — Ch1/Ch3 carry the two real
    motor axes (`AxisConfiguration="Position Loop"`), Ch2/Ch4 carry their
    paired **Feedback-Only companion axes** (`AxisConfiguration="Feedback
    Only"`, `FeedbackConfiguration="Master Feedback"`, no motor/tuning
    params at all) — legitimate, ordinary channels, nothing safety-related
    about them. So Ch2 itself isn't the problem; the real, still-open
    question is why our generator's ORIGINAL mistake (a full
    `Position Loop`-configured axis tag placed on Ch2, a slot real
    Kinetix 5700 configs use for a structurally DIFFERENT
    `Feedback Only`-shaped axis) specifically produced a SAFETY-tagged
    error rather than some other kind of mismatch error. The Ch1/Ch3 fix
    still stands (matches 2 independent real corpus captures exactly for
    a 2-declared-axis file), but calling it "the fix for the SI/SO
    error" is not yet confirmed — needs a real ACD retest of the
    regenerated files to know whether it actually clears that error or
    just happens to also be correct for an unrelated reason.

    **Real symptom clarified, real second bug found and fixed, still
    2026-09-03.** A retest of the Ch2->Ch3 fix (`modulemotion_
    d012_dual_axis.L5X`) gave the same 2-error signature, and clarified the
    actual crash: opening the **module's own I/O-tree profile page**
    (not the axis properties page) crashes Studio outright -- confirmed
    by testing the original, unmodified real source file
    (`p208_D012_NodeAndAxisDual.L5X`, the one this project's D012 module
    block is extracted from) side by side: **that file opens fine.**
    Definitive proof the bug is in how this project's own pipeline
    reassembles the real content, not in the real content itself. A
    precise structural diff (whitespace-normalized, identifiers scrubbed)
    against that real file found a second real, concrete bug: `_axis_tag`
    -- the ONE helper this project used to build every axis tag -- was
    also being used to build P208's own on-board "DC BUS" axis, but a
    real DC-bus axis is a structurally DIFFERENT, much shorter
    `AxisConfiguration="Non-Regenerative AC/DC Converter"` shape with no
    servo-tuning parameters at all -- nothing like the full `Position
    Loop` servo template `_axis_tag` always applied. Every P208 axis this
    project has ever generated (5 `modulemotion_*` files, all 50
    `composite_realistic_v3_*` files, all 18 `axis_scale_*` files) has
    been structurally malformed this way -- the leading real suspect for
    the module-page crash, though NOT yet confirmed (the P208 module was
    ruled out independently of this fix, before it was applied -- still
    needs a retest of the regenerated file to know either way).
    Fixed: new `_dcbus_axis_tag()` helper using the real, verbatim-
    extracted DC-bus shape, wired into all 3 generators
    (`gen_module_motion.py`, `gen_composite_realistic_v3.py`,
    `gen_module_axis_scale.py` -- the last one had never been checked
    against this bug before). All affected files regenerated, lint-clean,
    177/177 tests passing.

    **Two separate, real bugs found and fixed the same pass, NOT this
    one:**
    - **Sequential slot numbering.** Many racks did not use slot numbers in
      sequence; a lint check for this was added.
      `gen_composite_realistic.py`'s `_modules_xml_unique_ips` keyed each
      catalog's assigned Local-ICP backplane slot off its raw index in the
      file's full catalog list (`slot=2+i`), regardless of whether that
      catalog even has an ICP-backplane root module — an Ethernet-only
      catalog between two ICP catalogs silently consumed an index without
      consuming a slot, leaving a real gap (confirmed real example:
      `composite_realistic_22_r2.L5X`, slots 3 and 5 present, 4 missing).
      Also always started at slot 2, one too high — `wrapper.py`'s own
      Local module template puts the CPU's downstream ICP port at
      `Address="0"` in every branch, so the first real expansion module is
      physically slot 1. Fixed: only catalogs whose block actually
      contains a Local-ICP root module consume a slot, numbered
      sequentially from 1 with no gaps. New lint check added,
      `non_sequential_module_slots` (`sample_gen/lint.py`
      `_slot_sequence_findings`) — flags any (ParentModule, PortId) group
      of 2+ modules with numeric addresses that isn't a contiguous run, so
      a future generator can't reintroduce this silently. (Also flags 2
      pre-existing `modulerack_1756_local`/`_remote` files not touched by
      this fix — those may be intentionally sparse racks, not bugs; not
      changed, flagged for confirmation before any future regen.)
    - **"Safety-rated module in a non-safety-declared composite"
      (`2198-S130-ERS3`, `composite_realistic_v2_19`/`_30`)** — this WAS
      diagnosed and fixed here initially, then disproven within the hour
      by real evidence. See the CORRECTION under OQ-193ECMETR above for
      the full story: it's genuinely undiagnosed, not a safety-controller
      requirement, and now sits in the same exclusion bucket as
      `193-ECM-ETR/A`/`/B`.


    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    1 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `modulemotion_d012_dual_axis`

15. **OQ-V3GENBUGS** — three real generator bugs found via the actual
    Studio 5000 ACD-conversion errors on the v3 composite batch (50 files,
    2026-09-02), all root-caused to the exact reported symptom and fixed:
    `_LOCAL_ICP_SLOT_RE` crossing `<Module>` boundaries in DOTALL mode
    (corrupted an unrelated child module's valid ICP slot when the "root"
    module's own port didn't match), `lint.py`'s `_module_slot_findings`
    treating a real, valid nameless `<Module>` (e.g. `1756-OF8/B`) as
    invisible to slot-collision checks, and an IPv4 4th-octet overflow in
    `_modules_xml_unique_ips` (`base = 60 + (i+1)*10` broke past ~19
    catalogs/file — v3 routinely has 15-34). All three fixed and covered
    by new regression tests (`tests/test_gen_composite_realistic.py`).
    New test batches this same pass, all lint-clean and pushed:
    `composite_realistic_v3_*` (50, deliberately wide-varying program/AOI/
    subroutine counts — see [^compositescale] — built specifically to
    re-derive the JSR/AOI composite-scale surcharge that over-generalized
    at Titusville's real 179-distinct-JSR-target scale, see OQ-JSRSCALE
    below), `axis_scale_*` (18, single/dual-axis 2198 servo drive counts
    1-20 ± regen), `rack_5069_*` (11, real `Remote5069.L5X`-derived AENTR
    multi-child racks), `rack_pointio_*` (11, real `1734-AENT/B` multi-slot
    adapter), `rack_1756_*` (12, local-rack size scaling 2-16 modules),
    `cipmodule_scale_*` (7, CIP-MODULE declared-I/O-size sweep 64-2048
    bytes, anchored against Titusville's real 496-byte `IO_Optm` instance),
    `bridge_placeholder_*` (2, real zero-connection `ETHERNET-BRIDGE`
    IP-only fan-out node). None of these have real capture data back yet
    (ACD conversion still being validated as of 2026-09-02) — no sizing
    formula changes from this item, generator-correctness only.

16. **OQ-JSRSCALE / OQ-COMPOSITESCALE** — the composite AOI/JSR surcharge.
    **REFITTED ON REAL PROGRAMS 2026-09-04. Was the project's #1 error
    source; is now its largest remaining one, but 5x smaller.**

    supplied real Capacity readings for 8 whole real customer
    programs, joining `Cardin_TrimSortStack` for **9 real data points** —
    the first time this question has had more than one. Under the old model
    (`aoi=20`, `jsr=47`, file-wide cap 12,000) **all nine under-predicted**,
    by +8.35% to +30.63%, aggregate **+12.62%**, mean |error| **14.95%**.

    The driver was identified BEFORE anything was refitted, deliberately —
    correlating each real file's residual against every measurable
    candidate:

    | driver | corr | | driver | corr |
    |---|---:|---|---|---:|
    | JSR-target instructions | **+0.813** | | routine count | +0.769 |
    | all RLL instructions | +0.805 | | controller tags | +0.514 |
    | unweighted instructions | +0.524 | | AOI-internal instructions | +0.203 |
    | **ST source lines** | **−0.396** | | **unsized modules** | **−0.255** |

    So the residual is JSR-target logic content, and it is NOT unmodeled ST
    (negative) and NOT the unsized rack-aliased modules (negative). That
    matters: it rules out the two most tempting alternative explanations
    before the surcharge was touched, which is the check that was missing
    when the drive-bus discount got fitted on bad data and had to be
    reverted.

    Refit: least squares of (actual − prediction-with-no-surcharge) on
    [aoi_instr, jsr_instr] over all 9 real files → **52.52 / 20.81**,
    rounded to **52 / 21** with no meaningful loss. **Cap disabled** (0) —
    it was a patch for a jsr rate 2.3x too high, and at real scale it was
    suppressing 252,749–1,260,885 bytes per file, which IS the +12.62%.

    Leave-one-out over the 9 (fit on 8, predict the 9th): **mean |error|
    3.83%, max 9.41%**. Two rates beat one combined rate (same mean, max
    12.78%) and a JSR-only rate (4.86% / 17.69%), which is why both are
    kept.

    Result: real programs **14.95% → 3.29%** mean, aggregate **+12.62% →
    −0.41%**, 2 of 8 now inside ±1%. Cost, stated not buried: the 176
    corpus rows carrying AOI/JSR content go 3.09% → 3.57% and the whole
    1,885-row corpus 1.378% → 1.423%. The synthetic composites and the real
    programs genuinely disagree about this law; this trades a rounding
    error on the instruments for a 5x gain on the thing the project exists
    to predict, per CLAUDE.md's North Star.

    **STILL OPEN, and this is the main remaining gap:** 3.29% is not <1%,
    and leave-one-out says expect ~3.8% on a file nobody has seen. The two
    worst are `MurrayBros` (+7.43%, the smallest file at 923 KB) and
    `K3M16_Edgers` (+5.55%) — both still UNDER — against `Pukall_Gang`
    (−5.44%) OVER, so the remaining error is not a single sign and not a
    simple scale term. What is needed: **more real programs** (each one has
    been worth more than any synthetic batch), and the captures for the
    already-generated `realscale_jsrtgt_xic_n*` ladder, which is the only
    thing that can separate per-instruction cost from per-target and
    per-routine cost at real scale.

17. **OQ-AXISCOMBO** — cited in RESOLVED_QUESTIONS.md (OQ-AXISSTRUCT,
    OQ-AXISDEEP) as "the one remaining piece," but no item by this name —
    or covering this ground — was ever actually created here. A real
    doc-sync gap, not a resolved one. Chasing it down surfaced a second,
    more substantive gap: OQ-AXISSTRUCT's real Capacity numbers don't
    match what's already wired into `memory_model.yaml`'s
    `predefined_structures` from OQ-PREDEFINED. Correction to the record:
    axis content is NOT "100%-blind, priced at exactly $0" as previously
    stated — AXIS_CIP_DRIVE/AXIS_SERVO/AXIS_VIRTUAL/
    COORDINATE_SYSTEM are wired and sizing without error today (FITTED,
    single-sample-each). See footnote for the actual unreconciled numbers
    and what's needed to close this for real.

19. **OQ-EXPORTSCOPE** — new, 2026-09-04. The estimation path has to handle
    controller, UDT, AOI, program, routine and rung-logic exports.
    Anything that is not a controller export cannot use the base load, but
    rungs, routines and
    programs might contain controller tags"*). The scope machinery is now
    WIRED (`parser/export_scope.py`): a partial export gets no project base
    load, no firmware/catalog/safety baseline delta and no task/program
    shell, and its total is reported split three ways — target / context /
    project. What remains genuinely open is what a partial export costs
    **on import**, which is not the same question and has no data at all:

    - **A Program export's own shell.** Importing a program into a
      controller creates a program, and `task_program_overhead.program_extra`
      is the marginal cost of an extra program in a whole project — but
      that constant was fitted across whole-project captures and has never
      been checked against "import one program into an existing project".
      Charging it here would be a guess, so nothing is charged.
    - **A Routine export's own shell**, same argument with `routine_extra`.
    - **A Rung export** creates no structural container at all, so
      arguably zero — untested.
    - **The context/target boundary in bytes.** Context declarations are
      reported separately because they cost their bytes only if the
      destination controller does not already have them. Whether Logix
      charges anything extra for reconciling an already-present declaration
      on import is unknown.

    Test shape needed: export one program from a known project, import it
    into a second known project, and read Capacity before and after. That
    is a controller-in-the-loop test, not a file-generation one, so it
    needs a controller at the bench rather than a generator run.

22. **OQ-BUILDFAIL-OPEN** — the 11 sample files that genuinely still fail to
    build, 2026-09-05. Audited down from 138 `error_count > 0` rows: 72 were
    stale captures against files regenerated after the fact (cleared, they
    re-run automatically), 13 were superseded by exact `realscale_*` tests,
    40 were obsolete composite v1/v2, 2 no longer exist. These 11 are real,
    and **nothing in this repo diagnoses any of them** — the generators'
    own comments are silent, so the cause has to come from the Studio
    5000 error log rather than from a guess (guessing is what produced the
    invented alarm `ConditionType` names that all four failed on).

    | file | errors | why it still matters |
    |---|---:|---|
    | `almd_minimal`, `almd_realtext` | 1 ea | **ALMD instruction cost — now high value.** Alarms turned out to be the single biggest unpriced item in the model (OQ-ALARMCOND); ALMD is the *other* alarm mechanism and is still completely unmeasured. |
    | `modulesweep_2198_{d012,d020,d032,d057,s086,s130}_ers3*` | 2 ea | The 2198 drive catalogs, all failing identically at 2 errors — one shared cause, six files. OQ-MODULEIO's per-catalog table has no entry for any of them. |
    | `modulerack_kinetix_full_bus` | 4 | Same family, full Kinetix bus. |
    | `predefprobe_axis_generic` | 1 | AXIS predefined-structure probe (OQ-AXISCOMBO). |
    | `eventtask_axiswatch` | 1 | EVENT-task trigger cost. |

    **What is needed:** the real error line for one 2198 file (all six fail
    the same way, so one diagnosis fixes six) and one for `almd_minimal`.
    That is two error messages for 9 of the 11 files.



    **CAPTURE ERRORS: 15 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    6 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `almd_minimal`, `aoi_multiroutine_control`, `aoi_multiroutine_real`, `instrfirst_crout_x10`, `instrfirst_mapc_x10`, `predefprobe_axis_generic`
    9 committed file(s) attempted and never reached `ok` in
    `convert_log.csv`: `predefprobe_opcua_server_address`, `predefprobe_ref_to_axis_cip_drive`, `predefprobe_ref_to_axis_consumed`, `predefprobe_ref_to_axis_general_drive`, `predefprobe_ref_to_axis_servo`, `predefprobe_ref_to_axis_servo_drive` (+3 more)

23. **OQ-DEFSCALE** — definition- and instance-count scaling. **CAPTURED
    AND RECONCILED 2026-09-11, all 30 files, zero import errors. Four exact
    linear laws, none of them wired, and the reason is a confound, not a
    doubt about the numbers.**

    All four sweeps came back perfectly linear with zero residual:

        defscale_aoidefs_n*    over-prediction = +3 x n          7 points
        defscale_aoiinst_n*    over-prediction = -264 - 157 x n  7 points
        defscale_udts_n*       over-prediction = -16 x n         8 points
        defscale_udttag_n*     over-prediction = -19 x n         8 points

    Subtracting the paired sweeps: an AOI **definition** is over-charged by
    **3** bytes; an **instantiated** AOI is under-charged by **160** per unit
    plus **264** once; a **UDT definition** is under-charged by **16**; a UDT
    that has a tag is under-charged by a further **3**.

    Applied to the sixteen real programs those four numbers give:

        mean |error|   2.17%  ->  1.63%
        within 1%          4  ->  6
        within 2%          9  ->  11

    and they move every file UP — the direction the real files need, and the
    opposite direction to OQ-MODULEMARGINAL's module over-charge. The two
    together are the clearest evidence yet that the real-file residual is
    composed of large offsetting terms rather than one missing cost.

    **Why it is not wired: every sweep varies two things at once.**
    `defscale_aoiinst_n` holds n definitions, each with exactly ONE instance
    tag AND exactly ONE calling rung, so n = definitions = instance tags =
    calls, and "160 per instance tag", "160 per AOI call" and "160 extra for
    a definition that is instantiated at all" fit all seven points
    identically. `defscale_udttag_n` holds n UDTs with ONE tag each, so "3
    per UDT tag" and "3 once for a UDT that has any tag" fit all eight.

    On a real program those readings are nowhere near each other. AccuTally
    carries 902 AOI instances across 39 definitions and 33,574 UDT tags
    across 174 UDT definitions:

        per instance / per tag   160 x 902 + 3 x 33,574  = +245,042
        per definition           160 x  39 + 3 x    174  =   +6,762

    238 KB apart on one file, 4% of it — the same structural ambiguity as
    OQ-MODULEMARGINAL's per-catalog-vs-per-file question, in a different cost
    category, and it gets measured for the same reason: on this project the
    tidier reading has been wrong before.

    **Test files built 2026-09-11, `gen_defscale2.py`, 39 files.** Every
    definition is built from `gen_defscale`'s own `_aoi_members()` /
    `_udt_members()`, so they are byte-identical to the captured sweep and
    difference straight against it. The model's own prediction is a perfectly
    straight line across every new sweep (112/instance tag, 101/UDT tag,
    20/AOI array element, 12/UDT array element, and **0 per call**), so any
    slope error or curvature in the capture is unambiguous.

    | arm | files | what is pinned | what it decides |
    |---|---:|---|---|
    | `dscale2_aoi_d001_t*_call` | 8 | 1 definition | slope is per-INSTANCE, not per-definition (1→100 instances) |
    | `dscale2_aoi_d001_t*_nocall` | 4 | 1 definition, no logic | splits the instance TAG from its CALL |
    | `dscale2_aoi_d001_t001_c*` | 3 | 1 definition, 1 instance | the converse: call count varies alone. The model charges 0 per call, so any movement here is pure call cost |
    | `dscale2_aoi_d*_t*_nocall` | 3 | — | `defscale_aoiinst_n{05,20,60}` minus its calling rungs, for a direct difference at real-file scale |
    | `dscale2_aoi_arr*` | 3 | 1 definition, 1 tag | per-instance or per-tag: an ARRAY of 2/10/50 instances |
    | `dscale2_udt_u001_t*` | 9 | 1 UDT definition | slope is per-TAG, not per-definition (1→500 tags) |
    | `dscale2_udt_u{005,025}_t*` | 5 | — | definition count x tag count crossed: additive or interacting |
    | `dscale2_udt_arr*` | 4 | 1 UDT, 1 tag | per-element or per-tag, 2→500 elements |

    `dscale2_udt_u001_t001` is byte-identical to the already-captured
    `defscale_udttag_n001` and is kept deliberately: it anchors the new
    sweep's intercept in the same capture run and doubles as a
    run-to-run reproducibility check.

    **Not covered, and reported rather than guessed:** program-scoped
    structure tags. A Program-scoped ATOMIC tag has a confirmed real shape
    (`program_tag_xml`, dual L5K+Decorated), but no real corpus file has been
    read for a Program-scoped UDT or AOI-instance tag — and real programs put
    most of their instances there. Building one from a guessed shape would
    put an unverified XML shape inside the experiment meant to settle the
    question. It needs a real export first.

    **The original framing of this item stands and is now confirmed rather
    than suspected.** Across all captured non-real files the maximum was 7
    AOI definitions and 6 UDTs, while the real programs carry 11–39
    definitions and 51–174 UDTs; the first batch to bracket them found an
    exact error at every point. What the first batch could not do was
    attribute it, which is what the 39 new files are for.


24. **OQ-SHELLCONST** — new, 2026-09-04, split out of OQ-SHELLSCALE. Two
    small CONSTANT (non-scaling) residuals the shell isolation exposed
    once the slopes were exact:

    - **−23 bytes** on every `shellscale_programs_*` and
      `shellscale_routines_*` file, dead flat from n=1 to n=200. A fixed
      per-file baseline offset, worth 0.09% at the small end and 0.03% at
      the large end. Too small to chase on its own, but it is real and
      exact, so it is probably one concrete unpriced item rather than
      accumulated rounding.
    - **−815 bytes** on all four `shellscale_crossed_*` files, also dead
      flat. These have the same Program and Routine counts as their pure
      counterparts (verified by element count) but come from a different
      generator, so something that generator emits — most likely the
      cross-program JSR wiring — costs 815 bytes that nothing prices. This
      one is worth identifying: 815 flat is 1.5% on a 54 KB file.

    Both are constants, not slopes, so neither affects the OQ-DEFSCALE
    reading above.


25. **OQ-VERIFINSTR** — new, 2026-09-04. Eleven instructions now have
    call shapes verified by the build-clean Studio 5000 export
    (`instruction_shapes_20260904.L5X`), and none of them has a measured
    cost: **BRK, COS, LOG, SIN, PID, FBC, STOR, MCD, MCS, MCSV, MAG**.
    `gen_verified_instructions.py` builds each at n=10/100/1000 on an
    AXIS_VIRTUAL basis (no drive/module binding, so nothing has to be
    netted back out). The model currently prices all eleven at zero, so
    each sweep's predicted total is flat across n — any real slope is the
    instruction's cost, read directly. **Blocked on capture.**

    Provenance note worth keeping: NXT is excluded because it is not a
    valid RLL mnemonic, and MCLM was deliberately skipped.
    Neither was inferred from documentation — which matters, because every
    previous attempt in this project to compose predefined-structure or
    instruction XML from a manual (alarm `ConditionType`s, the bare
    2-operand MAM/MAJ rungs, the Kinetix `:SI` safety tags) was rejected
    by the real toolchain.



    **CAPTURE ERRORS: 3 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    3 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `unweighted_dtr_n00010`, `unweighted_dtr_n00100`, `unweighted_dtr_n01000`

26. **OQ-CPTREALDEST** — REAL-destination CPT: two measured constants with
    no known mechanism. 2026-09-04. **Not blocking — the path is exact on
    all 47 captured calls — but both terms are descriptions, not theory,
    and a model you cannot explain is a model that will surprise you on a
    file you have not seen.**

    The ladder itself is clean and tier-blind: `124 + 40n`, and fitting
    `a + b*tier1 + c*tier2` against the opcount files returns b = c = 40
    (which makes sense — it is all float arithmetic, so a MUL should not
    cost more than an ADD the way it does on the integer path). Sitting on
    top:

    - **A 5-operator expression measures 328, not the 324 the ladder
      says.** Three files from three different generators
      (`cptmix_real*`, `cptcx_constants_floatconst_n4`,
      `instr_cpt_literaloperands`) independently agree on 328, and 6 and 8
      operators are back on the ladder exactly (364, 444). So it is not a
      ">= 5" step — the previous model had it as one and over-charged the
      6- and 8-operator files by 4 each.
    - **`**` adds 8, plus another 4 when the expression also contains a
      tier-2 operator**, and a pow expression does NOT get the 5-operator
      bump (`powmulti_n05` is 324+12, not 328+12).

    Two ad-hoc +4s is one too many to be comfortable. `cptrdops_n07/09/10`
    fills the ladder either side of the anomaly, `cptrdpow_k2/k3` tests
    whether pow_extra is per-operator or per-call (every existing real-dest
    pow file has exactly ONE `**`), and `cptrdarrange_*` tests whether the
    5-operator +4 is really the same arrangement effect OQ-CPTARRANGE
    found on the integer path, wearing a different hat. Blocked on capture.



    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    1 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `cptrd_operand_bool`

27. **OQ-CPTNARROW** — how the SINT/INT → DINT widening scales. 2026-09-04.

    2026-09-04: INTs use a behind-the-scenes conversion to DINT. That is
    the mechanism, and it resolved two things at once:
    LINT operands cost **nothing** (already 64-bit, no widening), and
    SINT/INT operands cost **+256/rung** on the 3-operator all-REAL control.

    **What is NOT determined: how that 256 splits.** There is exactly one
    file in the corpus with narrow operands in a REAL-destination CPT
    (`cptrd_operand_sint`, 3 SINT operands). 256/3 is not an integer, which
    rules out a pure per-operand rate, but per-call, per-operand-plus-block
    and per-conversion-site all fit that single point identically. The
    model currently charges `3*40 + 136` — the ordinary per-int-operand
    conversion each operand pays, plus one widening block per call. That
    split has a physical story and no evidence.

    It matters for real files, which have arbitrary SINT/INT counts: if the
    truth is per-operand, a 10-narrow-operand expression is wrong by ~600
    bytes per call.

    `cptnarrow_{sint,int}_k0..4` varies ONLY the narrow count at a fixed
    3-operator shape (k=0 must reproduce the 244/rung control, which is the
    built-in check that the batch is comparable). INT is swept alongside
    SINT because the model assumes they behave identically and that has
    never been tested — this project already assumed LINT belonged in the
    same set and it turned out to cost nothing. `cptwide_lint_k1..4`
    confirms LINT is free at every count rather than just at the one count
    (3) the single existing file happens to use, and
    `cptwide_mixed_sint_lint` covers mixed integer WIDTHS, which nothing in
    the corpus does. Blocked on capture.



    **CAPTURE ERRORS: 5 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    5 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `cptwide_lint_k1`, `cptwide_lint_k2`, `cptwide_lint_k3`, `cptwide_lint_k4`, `cptwide_mixed_sint_lint`

28. **OQ-CPTARRANGE** — does operator ARRANGEMENT change CPT cost?
    2026-09-04. **The last real CPT unknown, and the data proves it is real
    rather than a bad fit.**

    The integer-destination two-tier mix is now priced per tier
    (`100 + 24*t1 + 40*t2`, 19/23 exact, cross-validated against the
    single-operator captures which put MUL/DIV exactly 16 above ADD/SUB).
    Four points sit exactly −4 and **no linear model in (t1, t2) can reach
    them** — the system is over-determined and inconsistent. The smoking
    gun:

    | file | expression | t1 | t2 | measured |
    |---|---|---:|---:|---:|
    | `cptmix_scaling_alternating_n05` | `L0+L1*L2+L3*L4` | 2 | 2 | **228** |
    | `cptmix_scaling_grouped_n05` | `L0+L1+L2*L3*L4` | 2 | 2 | **232** |

    Identical tier counts, 4 bytes apart. Yet at 11 operators the same
    alternating/grouped pair measures IDENTICALLY. So arrangement matters
    at some sizes and not others, and two files cannot say which.

    Several hypotheses were tested against the data and all died: adjacent
    same-tier operators (`grouped_n08` has three adjacent T1 and is exact),
    maximal same-tier runs (`operatormix_nested` has a different run count
    from `operatormix_mixedops` and the same cost), and tier-transition
    count. Not patched with an invented rule — the miss is pinned in
    `test_cpt_t1_t2_mix_has_four_known_unexplained_misses` so any future
    refit claiming to explain it has to move those numbers deliberately.

    `cptarrange_{alternating,grouped,frontloaded,split}_n03..09` holds the
    tier counts fixed and varies only the order, at every operator count
    from 3 to 9. If arrangement is real the four curves separate and the
    pattern is readable; if the n=5 pair was a one-off they collapse and
    the −4 belongs to something else. Blocked on capture.

    Also in the same batch and genuinely never tested: **a float literal
    with an INTEGER destination** (`cptidflit_k1..3`). All ~97 integer-dest
    captures have zero float literals, so the integer path has no
    float-literal term at all and silently charges nothing — while real
    logic writes `CPT(Dest,A*1.5+B)` against a DINT routinely.


29. **OQ-STEXPR** — ST assignment expression cost, five shapes measured.
    2026-09-04.

    An ST assignment is **not** priced like the equivalent CPT. That was
    the working hypothesis — the `st_expr_cpt_mirror`/`instr_cpt` pair
    differ by exactly the +432 routine shell, which looked conclusive — and
    routing every assignment through the tier-aware CPT model on that basis
    over-predicted `realscale_st_n01000` by **+132%**.

    | shape | operators | dest | measured |
    |---|---:|---|---:|
    | `D := 0;` | 0 (bare literal) | DINT | 36 |
    | `D := D + 1;` | 1 | DINT | 40 |
    | `D := D + D * 2;` | 2 | DINT | 164 |
    | `R := D + D;` | 1 | REAL | 152 |
    | `R := (D+D)*R - R/2 + 1.5;` | 5 | REAL | 452 |

    The tell is the 1-operator case at 40: that is an ADD's own weight, not
    a CPT's. Logix appears to compile a simple assignment to the single
    equivalent instruction and only reach for CPT-like evaluation on a
    compound expression — which is why the 2-operator DINT case lands on
    the CPT number and the 1-operator cases land nowhere near it.

    Five points are clearly not one curve, so they are stored as an
    explicit sparse table rather than interpolated. A shape outside it
    falls back to the CPT model AND is reported as a
    `coverage/st_expression/...` gap, so a real file says so rather than
    quietly carrying a wrong number.

    **What would close it:** the direct ST analogue of what `cmpcpt_*` did
    for RLL — operator count 0..6 × DINT/REAL destination × with and
    without a float literal. Not yet generated; it is the obvious next ST
    batch and is not blocked on anything external.

    Also still open on ST, one thread each:
    - `st_jsr_param_target_n00100` is the only ST file not exact (−243,
      −0.52%). Every JSR parameter constant was fitted on RLL targets, and
      the corpus has 44 SBR / 42 RET inside ST, so an ST JSR target is a
      real shape that may be charged differently.
    - `st_ctl_case` carries a +21 residual; the CASE decomposition into
      per-construct and per-selector is one data point short.
    - `while_block` was corrected 72 → 76 on the strength of the
      literal-RHS rate (36). Only one WHILE file exists, so the split
      between per-WHILE and per-assignment rests on that substitution.



    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    1 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `st_instr_concat_n01000`

30. **OQ-REAL5069** — **SHELVED 2026-09-11 until 2026-09-18. Not closed,
    and not to be raised again before then.**

    Two corrections belong on the record first.

    **The premise below is out of date.** Four of the sixteen real captured
    programs ARE 5069 (elmsdale and salamanca and superior on 5069-L330ERM,
    flarefunction on 5069-L320ERMS3). The platform is no longer unvalidated.

    **The platform breakdown that replaced it was worse than the stale
    premise, and it was mine.** Grouping the sixteen real files by processor
    family gave 5069-L330ERM a -4.00% median and called it the corpus's
    worst platform — with **salamanca at +1.08%, one of the four most
    accurate files in the whole set, counted inside that bucket.** Family
    sizes are n=1, n=2 and n=3. Those medians are not measurements.

    The disproof is already in the same table: **murraybros is -5.16% on a
    1756-L81E**, worse than every 5069 file, on the family with the best
    median. Whatever drives the large residuals is not the processor, and
    reading one into a catalog string is exactly the failure this file
    already documents once — the rejected per-platform baseline that fitted
    190 near-empty files beautifully and broke 612 real ones.

    `gen_platform_equivalence.py` and its 15 files are KEPT, uncaptured, for
    when this is picked back up. They are still the right experiment if the
    question turns out to be real; nothing about them assumes it is.

    Priority: low, by the project owner's call. The residual is real and
    lives somewhere else.

    ---

    *Original entry, retained for history:*

    **the 5069 platform has ZERO real-file validation.**
    Found 2026-09-05, while checking which platforms the real corpus
    actually covers.

    Every one of the nine real production exports in `samples/local/` is a
    **1756-L8x**:

    | file | processor | fw |
    |---|---|---|
    | k3m16_edgers | 1756-L82E | 32.04 |
    | murraybros | 1756-L81E | 35.05 |
    | emporium | 1756-L83E | 32.04 |
    | pukall_gang | 1756-L81E | 35.05 |
    | ipc_edgerline | 1756-L81E | 35.05 |
    | cmu | 1756-L82E | 35.05 |
    | emporiumedger | 1756-L81E | 35.05 |
    | mrfp_edger | 1756-L81E | 35.05 |
    | accutally | 1756-L83E | 35.05 |

    Everything the model knows about 5069 -- the safety-capable baseline
    delta (+304), the 5069 catalog entries in `module_overhead_by_catalog`,
    the 5069 processor baselines -- comes from files this project generated
    itself. Not one of them has ever been checked against a real 5069
    program.

    That is the same extrapolation risk as OQ-DEFSCALE, and it went
    unnoticed for the same reason: corpus-level pass rates looked healthy
    because the corpus is full of synthetic 5069 files that the model was
    fitted on. Per CLAUDE.md's accuracy rule (real programs only, generated
    files are an instrument not evidence), the honest statement is that
    **this tool is validated on 1756-L8x and unvalidated on 5069.**

    It matters more than the raw file count suggests: 1756-L7x and 1769 are
    now formally dead architecture (2026-09-05), which leaves
    5069/CompactLogix 5380 as the platform this tool most likely gets used
    on going forward -- and it is the one with no real evidence behind it.

    **What is needed:** one real 5069 export with a controller capture.
    An "Elmsdale" project is known to run on 5069, but that file is not in
    `samples/local/`. Any real 5069 program would do -- the point is a
    first real data point, not that specific one.

    Until then, the UI should arguably say so on a 5069 file the way it
    already warns on a Safety project. Not implemented yet -- flagged here
    rather than built, because a warning banner claiming more precision
    about its own uncertainty than the data supports would be its own kind
    of dishonesty.


31. **OQ-AOISTRUCT** — **what an AOI costs to DECLARE, as a function of its
    structure rather than its name.** New, 2026-09-06, under two
    constraints set the same day: the AOIs in the worst-predicting real
    file also appear in other real projects, so they are not that file's
    problem; and the tool is going to people outside the organisation whose
    code will be different and whose AOI libraries will be entirely
    unfamiliar.

    Those two together rule out the tempting move. MurrayBros' residual
    correlates hardest with AOI structure (aoiaxisparam +0.889, aoirungs
    +0.848, aoidefs +0.838, aoilocals +0.835), and the shared definitions
    that recur across the nine projects (`PTimer`, `HomeToTorque`,
    `SpecialInputs`, `T_ADD`, `T_DST`, `AnalogSensor`, `Debounce`,
    `ts_PilotLight`, `VirtualAxis`, `ts_AxisGap`, `TierPinchAOI`,
    `ts_TotalSB` are byte-identical across projects) would make a
    per-AOI-name correction table easy to fit and worth exactly nothing to
    a stranger importing an L5X full of AOIs this project has never seen.

    **What the model prices today**, read straight out of
    `compute_aoi_definition_cost` + `AoiDefinitionModel.bytes_for`: base
    1184, plus a per-type rate (BOOL 16 / SINT 18 / INT 18 / LINT 24,
    single-type definitions only) or a flat 20 per declared item, plus AOI
    TYPE-name length buckets. That is the entire function.

    **Seven structural properties are therefore priced at exactly ZERO**,
    each of them an untested assumption rather than a measurement, and
    each measured against the real corpus (81 AOI definitions / 2,120
    Parameters+LocalTags in `samples/local`):

    | # | unpriced property | real corpus evidence |
    |---|---|---|
    | 1 | member NAME length | mean 12.1 chars, max 32; tag names elsewhere in this model cost 8 bytes per 8-char chunk |
    | 2 | member DESCRIPTIONS | 803 of 2,120 carry one; **zero** generated files ever emitted one |
    | 3 | InOut parameters | skipped outright by `compute_aoi_definition_cost`; 94 real ones, and the only legal way to pass an array/STRING/MESSAGE/UDT into an AOI |
    | 4 | predefined-structure members | TIMER 557 real member uses, DateTime 120, COUNTER 66, STRING 58, MOTION_INSTRUCTION 36, MESSAGE 15 — **none ever generated**; all fall off the per-type table onto the flat atomic rate |
    | 5 | array dimensions | a member counts once whether scalar or `Dimensions="1024"`; 46 real dimensioned AOI members |
    | 6 | member counts past the fitted range | real AOIs run to 102 params / 128 locals / 85 internal rungs (median 12/11/11); the generated corpus topped out near 6/2/1 |
    | 7 | extra internal routines | 7 of 81 real definitions carry an EnableInFalse and/or Prescan routine besides Logic |

    #6 is the identical extrapolation shape as OQ-SHELLSCALE (a constant
    fitted at n=2, applied at n=200, wrong by 8 bytes/unit and invisible
    until the ladder was built) and OQ-DEFSCALE. Both of those were real.

    **`gen_aoi_structure.py`, 56 files**, one property per group, everything
    else held fixed — including the AOI type name, which IS priced and
    would otherwise contaminate every reading:

    | group | files | varies |
    |---|---:|---|
    | `aoistr_namelen_c{04,08,12,16,20,28,40}` | 7 | member name length, 20 DINT params |
    | `aoistr_desc_l{000,016,064,256}`, `_all_l{000,064}`, `_aoidesc_l256`, `_aoirevnote_l256` | 8 | member and AOI-level description text |
    | `aoistr_inout_n{00,04,16,48}` | 4 | InOut param count |
    | `aoistr_predef_{base,timer,counter,motion,string,msg_inout}_n{01,08}` | 11 | predefined-structure member type |
    | `aoistr_dim_{base,local_atomic,local_timer,inout}_d{8,64,512}` | 9 | array dimension |
    | `aoistr_scale_{param,local,rung}_n*` | 12 | member/rung count to the real p90 and past it |
    | `aoistr_routines_n{1,2,3}` | 3 | internal routine count, total rungs held at 24 |
    | `aoistr_real_{median,p90}` | 2 | composite: do the isolated parts add? |

    **The design property that makes this readable**: the model predicts a
    DEAD FLAT line across every group except the three scale sweeps —
    19,712 for all seven name-length files, 19,472 for all nine
    inout/predefined files, 19,392 for all nine dimension files, 20,352 for
    all three routine-count files. Any spread at all in the captured
    numbers is an unpriced item, with no fitting or disentangling required
    to see it.

    Platform is 1756-L81E fw35.05 for all 56 — the same processor and
    firmware as MurrayBros and MRFP_Edger, so nothing here is confounded by
    OQ-BASELINE-PROCFW.

    Only the two composites are instantiated; the other 54 are
    definition-only, so what is captured is the declaration cost itself
    with no tag_overhead or member storage mixed in.

    Three generator gaps had to be closed to build this and are worth
    recording, because each one was a silent hole rather than a deliberate
    omission:
    - `builders.py` could not emit a predefined-structure AOI member at
      all. The atomic path writes a bare `Radix` + scalar `DataValue`
      (wrong for TIMER); the nested-UDT path writes an L5K value list that
      does not match the real positional encoding (a real TIMER LocalTag's
      L5K default is `[0,1500,0]` — three fields for five members, because
      EN/TT/DN alias into the leading status word). `predefined_members.py`
      now supplies the exact block captured from the real corpus rather
      than a guessed encoding that would only have failed in Studio 5000,
      costing a capture run to discover.
    - `builders.py` could not emit a member `<Description>`, an AOI-level
      `<Description>`/`<RevisionNote>`, or an `EnableInFalse`/`Prescan`
      routine. All three now render in the real shape and order
      (Description then RevisionNote before `<Parameters>`; routines
      alphabetical as EnableInFalse/Logic/Prescan, with the matching
      `ExecuteEnableInFalse`/`ExecutePrescan` attribute flipped to "true").
    - `lint.py`'s missing-array-subscript rule fired on an array InOut
      Parameter passed bare to an AOI call — which is the correct real
      form (LOG_HMIDisplay `Dimensions="25"`, BitArray
      `Dimensions="1024"`). Exempted at the AOI call site. This project had
      never before wired an array InOut param to an actual caller, so the
      rule had never been exercised against it.

    **Blocked on capture.**


32. **OQ-MODULEMARGINAL** — the last ASSUMED exposure that reaches a real
    file. 4.15% of real-file bytes on the current engine, of which the 2198
    `-ERS3` drives are 4.07% and eleven other catalogs are the rest. The
    worst-exposed real files are `k3m16` (7.06% ASSUMED), `horizon` (7.00%)
    and `ipc` (6.44%), and every ASSUMED byte in all sixteen real files is a
    `module_io` entry — nothing else in the model is both ASSUMED and
    reachable from a real export.

    **CAPTURED AND RECONCILED 2026-09-11, 54 files (`asmclose_*`, n=1/2/4
    per catalog). The marginal law is exact, and it must not be wired on
    its own.**

    Over-prediction is exactly linear in the module count, with zero
    residual at n=1, n=2 and n=4 for every catalog:

        over-prediction(n) = discount x (n - 1)

        1794-AENT                 432      1756-EN4TR             1520
        1734-AENT/B               520      1756-IB16IF/A          2208
        1734-AENT/C               520      440C-CR30-22BBB/A      3768
        1756-IB16                 792      AL1222                    0
        1756-IB32/B               792      842E-CM-M              1000
        PowerFlex 755-EENET-CM-S  976

    So the model charges every module full price and the controller charges
    the first one full price and `full - discount` for the rest. AL1222 at
    exactly 0 is the control that makes this a real per-catalog-shape
    property rather than a flat per-module fudge.

    The 2198 `-ERS3` family does not fit that form — it carries an extra
    flat error at n=1 as well:

        D012 / D020 / D032 / D057   +6,384 at n=1, then +7,368 per extra
        S086-ERS3                   +3,264 at n=1, then +4,248 per extra
        S130-ERS3                   +3,228 at n=1, then +4,212 per extra

    i.e. a drive after the first costs 984 less than the first, AND the
    first is itself over-charged. This is the single largest ASSUMED block
    in the project.

    **WHY IT IS NOT WIRED YET — this is the important part.** Applying the
    law as measured removes 824,864 bytes of module cost from the sixteen
    real files and makes EVERY ONE OF THEM WORSE: the median real-file error
    moves from -1.69% to roughly -3.5%. The law is not wrong; it is exact on
    54 points. What it shows is that the module over-charge has been masking
    an equal under-charge somewhere else, which is the compensating-error
    problem stated in OQ-REALGAP with a hard number attached for the first
    time. It gets wired together with whatever the strip ladder resolves,
    not before.

    **The one thing 54 single-catalog captures cannot decide.** Every one of
    those files holds ONE catalog, and two readings fit all 54 identically:

      - PER-CATALOG — the first module *of each catalog* pays full price:
        error = sum over catalogs of `d_i x (n_i - 1)`
      - PER-FILE — the first module *in the file* pays full price and
        everything after it is discounted whatever its catalog:
        error = `sum(d_i x n_i) - d_first`

    On a single-catalog file these are the same number. On a real program
    carrying 20-60 modules across 10-20 catalogs they differ by most of the
    module total, so picking wrong is a multi-hundred-kilobyte error on
    every real file.

    **Test files built 2026-09-11, `gen_module_marginal.py`, 36 files.**

      - **Arm A, 17 files** (`asmclose_*_n08`) — n=8 for every catalog that
        already has n=1/2/4, from the same builders so it differences
        straight against n=4. This is the first point that can FALSIFY the
        law: three points fit it exactly but two of them define it, so a
        per-rack or per-connection-block step above four modules would be
        invisible in the existing data.
      - **Arm B, 9 files** (`modmarg_mix{q1,q2,q3}_{x1,x2,x2rev}`) — the
        decisive experiment. Three quadruples of catalogs with widely
        separated discounts, each at 1 and 2 copies per catalog. The two
        readings are separated by 2,744 / 6,952 / 6,288 bytes on the `x1`
        and `x2` files, on files that are otherwise exact to the byte, so
        one capture each settles it. The `x2rev` files reverse module order
        within the file: PER-FILE requires the total error to move by
        `d_first - d_last` (1,224 / 3,704 / 3,312 here), PER-CATALOG
        requires it not to move at all — so the mixture is self-checking
        rather than one arithmetic coincidence.
      - **Arm C, 6 files** (`modmarg_drvaxis_*`) — the -ERS3 drives WITH
        their axis (one `AXIS_CIP_DRIVE` per drive plus the one shared
        `MOTION_GROUP`), at n=1/2/4/8 for D012 and n=1/2 for S086. All 54
        `asmclose_*` files hold bare drive modules with no axis tag; a real
        program never does. Differencing against the bare-drive capture at
        the same count separates the drive's own marginal cost from the
        axis's, which is the form the cost actually takes on a real file.
      - **Arm D, 4 files** (`modmarg_ob32chain_n{01,02,04,08}`) — see the
        contamination note below.

    **Contaminated data found and cleared, 2026-09-11.**
    `asmclose_1756_ob32_rackaliased_n02` and `_n04` are not usable and their
    capture columns have been cleared. The 1756-OB32 block is the only
    2-deep chain in the set (a 1756-EN2T adapter plus the output card behind
    it), and the copier that multiplies a module block renames only the
    FIRST `<Module>` in it. Every copy after the first therefore shipped an
    identically-named OB32 still pointing at `ParentModule="<the first
    adapter>"` and still sitting in the same slot 3. Studio merged the
    identical duplicates instead of rejecting them, so both files captured
    at ZERO import errors while measuring N adapters sharing ONE output
    card. The "1756-OB32 discount = 1760" read off them is therefore not a
    discount at all — it is the cost of the cards that never got imported.
    `lint.duplicate_module_name` now catches this class outright; a
    corpus-wide sweep found these two files and no others. Arm D rebuilds
    the full n=1/2/4/8 sweep under a new sample_id, with every module in
    every copy renamed and its `ParentModule` repointed at its own adapter,
    rather than regenerating in place — regenerating in place would leave
    the old captured `actual_bytes` attached to different file content.

    One catalog is still deliberately not covered and is reported rather
    than faked: **150 SMC Flex-E** (0.069% exposure) has no real module XML
    in either sweep table, so there is nothing verbatim to build from. It
    needs a real export before it can be tested at all.

    **Blocked on capture of the 36.** Arm B alone decides whether the
    already-measured law is worth hundreds of kilobytes per real file or a
    few tens.


33. **OQ-ALARMDEF** — datatype-level alarm definitions are priced at zero.
    New, 2026-09-08, found in the real 1756-L9xTS v38 exports.

    **CAPTURED 2026-09-11, 28 files across two processors. Three of the
    four questions are answered; one result does not fit and is not being
    wired until it does.**

    Answered, and replicated independently on 1756-L81E and 1756-L902TS
    with identical numbers:

      - **Operator message text is FREE.** `msg_none/s/m/l` all measure
        byte-identical (18,696 on L81, 20,972 on L902TS). Message length
        contributes nothing, the same result RLL rung comments and ST
        comments already gave.
      - **Member alarm count is FREE.** `d1_m00` through `d1_m16` — zero
        to sixteen `MemberAlarmDefinition` elements under one
        `DatatypeAlarmDefinition` — are all byte-identical. A definition
        costs what it costs regardless of how many members hang off it.
      - **Definition count is linear at exactly 8 bytes per
        `DatatypeAlarmDefinition`**, zero residual:

            d02 -> +16    d04 -> +32    d08 -> +64

        Both processors give the identical increments (L81 18,592 /
        19,056 / 19,984; L902TS 20,868 / 21,332 / 22,260 — differences of
        464 and 928 in both).

    **Does not fit, and is the reason nothing is wired yet:** every file
    in the `d1_*` family sits at +72, not the +8 that one definition
    should cost by the slope above. The extra 64 bytes are constant
    across all eleven `d1_*` files and appear on both processors. The
    `d1_*` UDT carries 18 members against 2 in the `d0N_*` files, so the
    suspect is a UDT-shape term leaking into this residual rather than an
    alarm term — but that is a hypothesis, and wiring 8/definition while
    a 64-byte hole sits next to it would bake the hole into the model.

    **The "one file settles it" note above was wrong, and is corrected
    here.** The problem is not one bad data point, it is that the first
    batch has no control. In `d0N` the UDT count, BIT-member count,
    backing-SINT count and definition count are ALL N, so "8 per UDT",
    "8 per definition", "8 per BIT member" and "8 per backing SINT" fit
    it identically, and `d1` fits none of them (8 / 8 / 128 / 16 against
    an actual 72). That is a two-variable surface, and no single extra
    file resolves one.

    **Test files built 2026-09-11**, `gen_alarm_separation.py`, 33 files.
    `alarmsep_u{01,02,04}_b{01,02,04,08,16}_{alarm,noalarm}` builds every
    point TWICE -- once with a DatatypeAlarmDefinition on each UDT, once
    with identical DataTypes and no `<AlarmDefinitions>` element at all.
    Differencing a pair cancels the UDT cost, the backing-SINT packing,
    the baseline and the shell exactly, so the remainder is the alarm
    cost with nothing else in it. The engine prices alarm definitions at
    0 today, so each pair differences to 0 in prediction and the measured
    difference IS the answer.

    Read along the `_noalarm` arm alone, the same files measure how a
    UDT's BOOL members and hidden backing SINTs are priced with no alarm
    content present; B=8 fills one backing SINT exactly and B=16 two, so
    a packing term cannot hide. `alarmsep_u04_b04_def{1,2,3}` decouples
    definition count from UDT count, giving five points on the definition
    axis with everything else frozen.

    Not captured: `inst_t{01,04,16}` and `noinst_t{01,04,16}` failed
    conversion in both arms (12 files), so whether an uninstantiated
    template costs anything is still completely open.

    `<AlarmDefinitions><DatatypeAlarmDefinition><MemberAlarmDefinition>` is
    a v38 shape: an alarm TEMPLATE attached to a data type, distinct from
    the tag-level `<AlarmConditions>` this engine already sizes exactly
    (OQ-ALARMCOND, closed). A stock Rockwell P_PID definition carrying six
    member alarms was priced at zero and reported nothing at all.

    That silence was the real problem, and it is fixed: `audit_coverage()`
    now emits a `coverage/alarm_definitions` notice, so the content is
    visible as unpriced rather than vanishing into the total. The byte cost
    itself is still unknown.

    **Test files built 2026-09-08**, `samples/generated/alarmdefs/`, 40
    files, awaiting capture. Rebuilt 2026-09-10 onto the v35 standard.

    The batch was first built entirely at v38, reasoning that the element
    is absent from all 26 real corpus exports at MajorRev 20-35 and present
    in all four at 38. That reasoning does not hold: those 26 files are
    projects that did not USE the feature, so their silence says nothing
    about whether v35 accepts one. Building off-standard on that basis cost
    the comparability against the ~2,400 existing v35 captures that the
    standard exists to provide.

    Now 20 files at v35 (primary, matching every other batch) and 20 at v38
    on the same 1756-L81E, so firmware is the only variable between the two
    arms and the v35-vs-v38 difference is readable directly. If v35 does
    reject the element, the v35 arm's conversion failures establish the
    version boundary while the v38 arm still closes the question.

      - Group A, `alarmdef_{proc}_d1_m{00,01,02,04,08,16}` and
        `alarmdef_{proc}_d{02,04,08}_m1`: member-count slope and
        per-definition intercept, swept independently so they are not
        collinear the way the single real example leaves them.
      - Group B, `alarmdef_{proc}_inst_t{00,01,04,16}` against
        `alarmdef_{proc}_noinst_t{01,04,16}`: whether an uninstantiated
        template costs anything. Worth asking because the real exports
        carry a P_PID definition while `<DataTypes/>` is empty and no
        P_PID tag exists anywhere -- a template can outlive any instance
        of its type.
      - Group C, `alarmdef_{proc}_msg_{none,s,m,l}`: whether the operator
        message CDATA counts, definition and member count held fixed.


    **CAPTURE ERRORS: 1 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    1 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `almd_realtext`

34. **OQ-L9BUDGET** — no memory budget for the 1756-L9xTS family.
    `controller_budgets.yaml` returns None for all four catalogs, so the UI
    has no denominator on an L9 file and cannot show headroom.

    Deliberately not guessed. The catalog digits look like they encode
    memory (L902/L905/L908/L915), but that is a pattern, not a source, and
    this project has been wrong before inferring a constant from a catalog
    name. Needs the real per-catalog user memory from a datasheet or a
    controller.

    The UI degrades correctly today -- it shows the byte total without a
    percentage rather than inventing one.

    **Test files built 2026-09-08**: `fwmatrix_v38_1756_l9{02,05,08,15}ts`.

    **CAPTURED 2026-09-11, and they do NOT close it.** The premise above
    was wrong: the capture harness records memory USED, not the capacity
    denominator, and `message_value` came back 0 on all four. What the
    four files did settle is the **baseline**, which was a different
    question — an empty v38 L9 project measures 20,404 against 18,128 for
    a 1756-L81E on the same firmware, a flat **+2,276 with zero variance
    across all four catalogs**. Wired as a `catalog_baseline_delta`, and
    independently replicated by the 14 `alarmdef_l902ts_*` files, which
    sit exactly 2,276 above their L81 twins once the shared alarm offset
    is removed.

    The budget itself still needs the real per-catalog user memory from a
    datasheet or a controller. The UI continues to degrade correctly,
    showing the byte total with no percentage rather than inventing one. Generated at v38
    only -- the family postdates the v31-v37 firmwares in the matrix, and
    building an L9 at v31 would fabricate a firmware that never shipped.


37. **OQ-UDTMEMBERNAME** (supersedes OQ-UDTBOOLMEMBER) — a UDT member's
    NAME LENGTH is unmodelled, and the whole corpus is blind to it because
    every generator ever written used two-character member names.

    The `alarmsep` batch captured 2026-09-11 and its 15 points fit one law
    with **zero residual**:

        deficit = udt_definitions x (8 + 8 * floor(bool_members / 2))

            u\b      1     2     4     8    16
              1     -8   -16   -24   -40   -72
              2    -16   -32   -48   -80  -144
              4    -32   -64   -96  -160  -288

    That reads as a BOOL-member cost, which is what OQ-UDTBOOLMEMBER
    predicted, and it is **wrong**. `udttype_bool_n4` is a structural twin
    of `alarmsep_u01_b04` — one UDT, one hidden backing SINT, four BIT
    members, no tags, both type names bucketing to the same ceil(len/8) —
    and it predicts EXACTLY while alarmsep_u01_b04 is 24 short. The one
    thing that differs is the member names: `M0`..`M3` against
    `Sts_A00`..`Sts_A03`. Two characters against seven.

    So the driver is member name length, or something travelling with it,
    and alarmsep cannot separate them because it varies BOOL count and
    total name length together. Nothing is wired off that law.

    `udt_definition` charges for the TYPE name (`name_per_8_chars`) and
    nothing at all for member names. Real programs are nothing like the
    fixtures:

        311DGeneratedProgram          689 members, avg  8.2 chars
        BaillieLeitchField_Edger      619 members, avg 10.2 chars
        Elmsdale                      877 members, avg 10.7 chars
        SJ_Gormley                    509 members, avg  9.8 chars
        FlareFunction_311D          2,284 members, avg  9.7 chars
        BAI10048_TrimmerTally       1,861 members, avg 12.3 chars

    **Test files built 2026-09-11**, `gen_udt_membername.py`, 24 files, all
    1756-L81E v35, type name held at exactly 8 characters throughout so the
    already-modelled type-name bucket cannot move. The engine predicts
    IDENTICALLY across every name length in every arm, so all 24 are direct
    measurements of an unmodelled quantity:

      - `udtmn_bool_short_b{01,02,04,08,16}` — BOOL count at 2-char names.
        The control; should predict exactly, matching udttype_bool_n4.
      - `udtmn_bool_l07_b{01,02,04,08,16}` — the same counts at alarmsep's
        7-char names, with no alarm definitions in the file at all.
      - `udtmn_bool_len{02,04,08,12,16,24,32}_b04` — the pure name-length
        sweep. Free, per character, or bucketed by 8 like every other name
        cost in this model?
      - `udtmn_dint_len{02,07,16,32}_n04` — the same on DINT. BOOLs are the
        one member kind with a hidden backing SINT, so this rules a
        BOOL-specific explanation in or out.
      - `udtmn_bool_len{02,07,16}_b16` — name length where a second backing
        SINT appears, and where the alarmsep law needed floor(b/2) rather
        than a flat per-member rate.

    **HOLE FOUND IN THAT BATCH, 2026-09-11, same day.** All 24 `udtmn_*`
    files carry `tags_xml=""`. Zero tags, in every arm. So whatever they
    measure, they measure it PER DEFINITION, and they are structurally
    incapable of saying whether the same term is ALSO charged per tag of the
    type. That distinction is the whole of the real-file exposure: AccuTally
    carries 33,574 UDT tags against 174 UDT definitions -- 193 tags per
    definition -- so a per-definition name term and a per-tag one differ by
    more than two orders of magnitude on that file. It is the identical
    failure mode OQ-DEFSCALE's captured sweeps hit from the other direction.

    `gen_udt_membername2.py`, **23 more files**, built from the same
    `_member_name()` / `_type_name()` so every arm differences straight
    against the 24 pending ones. Type names stay at 8 characters throughout,
    and the engine predicts IDENTICALLY across name length in every arm, so
    every difference is a measurement:

      - `udtmn2_bool_len{02,16,32}_b04_t{01,05,25}` (9) — the same 4-BOOL UDT
        at three name lengths with 1/5/25 tags of it; the t=0 point already
        exists. Per-definition means the length effect is identical at every
        t; per-tag means it grows 25x across the arm.
      - `udtmn2_dint_len{02,32}_n04_t{01,25}` (4) — the same on DINT. A
        BOOL-specific explanation was already assumed once and was wrong
        (OQ-UDTBOOLMEMBER), so no name-length result is believed on BOOL
        evidence alone.
      - `udtmn2_nest_len{02,32}` (2) — an outer UDT whose 4 members are each
        an inner UDT with 4 members at the swept length. Are a nested type's
        member names charged again inside every containing definition? If so
        the cost compounds with nesting depth, and real programs nest heavily.
      - `udtmn2_bool_len32_b04_arr{010,100}` (2) — one tag that is an array of
        10/100 elements. Per-tag applies once; per-element multiplies.
      - `udtmn2_aoi_{plen,llen}{02,16,32}` (6) — the same question for an AOI's
        PARAMETER and LOCAL TAG names, which no generator has ever varied.

    **Do not oversell this as the fix for the real-file error.** Checked
    directly: the real-file deficit per declared member/parameter/local tag
    ranges from **+15 to −46 bytes** across the 16 real programs, and four
    of them over-predict. Whatever drives the 2–5% real-file error is not
    one missing per-name term, and this is not it. It is a real gap worth
    closing on its own terms, not the headline.

    Also confirmed by this batch, and worth keeping: **alarm DEFINITIONS
    cost nothing.** Every `alarmsep_*_alarm` measured byte-identical to its
    `_noalarm` twin, and `def1/def2/def3` identical again.


38. **OQ-JSRFOLD** — new, 2026-09-11. A JSR and its target routine are
    over-charged at low counts and under-charged per unit, and the shape
    points at how the target's cost is folded in.

    `forloop_ctl_r{001,005,025,100}` — N JSR rungs against N target
    routines, built as the control arm for FOR:

        N      predicted   actual   delta
        1         18,831   18,552    +279
        5         20,235   19,960    +275
       25         27,255   27,000    +255
      100         53,580   53,400    +180

    Both arms are exactly linear and they disagree in two ways at once:
    actual is `18,552 + 352(N-1)`, predicted is `18,831 + 351(N-1)`. So a
    fixed **+279 excess** plus **1 byte per unit short**.

    Routine shells alone are not the problem: `subrtn_shell_r100` adds 100
    extra routines and predicts exactly, 12 of 12 across that family. What
    differs here is that these targets are JSR TARGETS, and report.py
    deliberately never emits a JSR target as its own SizeEntry — its cost
    is folded into the caller instead (`RoutineLogic.is_jsr_target`). The
    FOR arm has the same 100 target routines and, once FOR was weighted,
    predicts exactly at all four counts; those targets are NOT JSR targets
    and so are emitted normally. That asymmetry is the suspect.

    Not wired. A 1-byte-per-unit term is not a plausible memory quantity on
    its own, so the fold-in is probably misattributing a larger cost rather
    than being off by one, and guessing at that would be fitting noise. The
    isolation needed is a JSR-target sweep that varies the TARGET's own
    content while holding the call count fixed, which nothing covers:
    every existing JSR file uses a one-rung target.

    Stake: real programs are full of JSRs. Small per-file, but it applies
    everywhere.



    **CAPTURE ERRORS: 2 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    2 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `jsr_midchain_leaf_control`, `jsr_midchain_real_chain`

39. **OQ-CAMSCALAR** — CLOSED as OQ-CAMSHAPE 2026-09-11 (see
    RESOLVED_QUESTIONS.md: container shape is a non-effect, the CAM base was
    corrected 8 -> 4 with 8-byte element-block alignment, CAM_PROFILE
    promoted to KNOWN). What survives is narrower and stays open:

      - `camx_scalar_cam` (-104) and `camx_scalar_prof` (-144). A SCALAR
        CAM or CAM_PROFILE — no dimension at all. The corpus contains ZERO
        real examples of one, and this model prices it as an array of one
        element, which these two files say is wrong by about a hundred
        bytes. Whether a scalar is even legal in real Logix is part of the
        question; the files converted, so it is.
      - `camx_mixed_d10/d20` (+4), `camx_nested_i01/i05` (+4/+20) and
        `camx_udtarray_n05` (+28). Each carries one unknown beyond the cam
        types themselves — two cam members in one UDT, depth, and an array
        of a UDT containing arrays of a predefined. All four are small and
        none is explained by the cam constants, which are now exact
        standalone and as members.

40. **OQ-AOIDEFITEMIZE** — an AOI's priced definition cost and its own
    itemized member breakdown are two different computations, and they
    disagree by a large margin on every real AOI.

    Found 2026-09-11 while making the treemap sum to the report. For each
    AOI, `report.py` charges a definition cost (per-declared-member rate
    table plus the type-name-length bucket, OQ-AOIDEF's wiring), while
    `sizing/tree.py`'s `expand_definition_children` enumerates the same
    definition member by member. The enumeration always comes in LOWER.
    On Elmsdale, all 21 AOIs:

        AOI               priced    itemized    unexplained
        DriveAxis         18,873       3,633         15,240
        T_DST             12,344       3,000          9,344
        TS_VFD            10,581       3,361          7,220
        T_Clock            6,975       2,231          4,744
        VirtualAxis        6,589       2,085          4,504
        HomeToTorque       6,122       1,902          4,220
        TS_TrackSts        5,268       1,568          3,700
        ... (21 total)                              66,908

    66,908 bytes, 6.1% of that file's whole predicted total, is charged by
    the report and accounted for by nothing in the breakdown. It is not
    a rounding effect and it is not uniform: it scales with something the
    member enumeration does not see.

    Two possibilities, and they need separating before either is acted on:

      - The per-member rate table is right and the enumeration is
        incomplete — it is missing whole categories of declared thing
        (nested UDT members expanded at the wrong depth, InOut parameters,
        local tags of structured type). This would be a pure display bug.
      - The rate table over-charges and the real definition cost is closer
        to the enumeration. This would be a SIZING error worth 6% on a
        real file, which is six times the whole error budget.

    The first is more likely — the rate table was fitted against real
    capture data and the real-file error is currently 2.17%, which a 6%
    over-charge would not survive — but "more likely" is not measured.

    The isolation test is cheap and exists in shape already: a
    single-AOI file whose definition declares a known member roster,
    captured, differenced against the same file with one member added.
    `aoidef_*` covers the flat single-type case; what is missing is an AOI
    whose members are themselves structured (a UDT member, a TIMER, an
    InOut of UDT type), which is exactly what every real AOI above has and
    every existing test file lacks.

    Until then the UI carries the difference as an explicit
    "Unitemized definition cost" row rather than dropping it, so the
    treemap sums to the report total and the size of the unexplained part
    is visible instead of silent.


    **CAPTURE ERRORS: 43 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    43 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `aoi_logic_scale_010`, `aoi_logic_scale_050`, `aoi_logic_scale_100`, `composite_realistic_03_r2`, `composite_realistic_04_r2`, `composite_realistic_05_r2` (+37 more)

41. **OQ-POINTIOCONN** — a POINT I/O card's memory cost depends on its
    connection format, which the model does not represent at all, and the
    flat rate it charges instead is wrong in both directions.

    Three real captures, 2026-09-11. Identical content otherwise: one
    1756-L81E v35, one adapter, sixteen 1734-IB8/C cards. The non-module
    part of the prediction is byte-identical (18,336) across all three, so
    the whole difference is the I/O subsystem.

        format          adapter          actual   module subsystem   per module
        Enhanced        1734-AENTR/C     32,616        14,280             840
        Enhanced Data   1734-AENTR/C     37,320        18,984           1,117
        Optimized       1734-AENT/A      28,688        10,352             609

    Against predictions of 47,280 / 47,360 / 20,050 — over by 45% and 27%
    on the first two, under by 30% on the third.

    The three formats are structurally distinct in the L5X and the parser
    already tells them apart:

      - **Enhanced** — the card has a ConfigTag and NO `<Connections>`
        element at all.
      - **Enhanced Data** — the card carries its own `InputData`
        `<Connection>`.
      - **Optimized** — the card carries `<RackConnection><InAliasTag/>`,
        its I/O aliased into the adapter's own Slot array.

    One clean single-variable result is already in hand. Enhanced Data
    minus Enhanced is the same adapter, the same sixteen cards and only
    the connection format changed: **+4,704, exactly 16 × 294.** A card's
    own connection costs 294 bytes more than no connection. That is a real
    per-module, per-format cost and nothing in the model has a term for it.

    What is NOT separable from these three points: the adapter's own cost
    from the per-card cost, because every file has sixteen cards; and the
    Optimized arm changes the adapter catalog (1734-AENT/A) at the same
    time as the format, confounding the two.

    Both fall out of a count sweep — the same differencing method every
    other constant in this project came from. For each format, N =
    1, 2, 4, 8, 16 cards: the slope is the per-card cost of that format
    and the intercept is that adapter's own cost, each fitted
    independently of the other.

    **Built 2026-09-11**, `gen_pointio_conn_sweep.py`, **15 files** --
    `pioconn_{enhanced,enhdata,optimized}_n{01,02,04,08,16}`, 1756-L81E
    v35, every module block verbatim from the real exports. Only what
    genuinely depends on the card count is rewritten, and the three
    formats need different rewrites because they carry the rack
    differently:

      - **Enhanced Data** -- the adapter's InputTag is just the two status
        DINTs and every card carries its own self-contained Connection.
        Only the card count, the adapter's Bus Size, the L5K per-slot
        blobs and the rack-sized `pad` arrays on its input and output
        types change.
      - **Enhanced** -- the adapter's InputTag holds one StructureMember
        per card (`Slot01`..`Slot16`), and the file DEFINES that
        module-scoped type itself under `<ExtendedProperties>`, so the
        slot list is rewritten in both places alongside the status arrays
        and the output pad. The type NAME carries a Studio-computed hash,
        `AB:1734_ERACK_649387C8:I:0`, which is not derivable from the
        L5X, so it is kept verbatim; the file supplies the matching
        definition. Whether Studio 5000 accepts a self-described type
        whose hash it would have computed differently is something a real
        conversion answers and guesswork does not.
      - **Optimized** -- every card is rack-aliased into the adapter's own
        SINT array and the profile is named after the slot count,
        `AB:1734_17SLOT:I:0`. Systematic rather than hashed, so it is
        rewritten to match along with the array dimensions and element
        lists. Unlike the Enhanced case this type is NOT defined in the
        file -- it is a catalog profile -- so if `AB:1734_<n>SLOT` does
        not exist at some n, that file fails to import.

    A conversion failure in either of the latter two arms is a RESULT, not
    a defect: it says the rack-optimized profile exists only at certain
    sizes, or that the ERACK hash must match. Logged, not worked around.

    Verified before shipping: slots 1..N, adapter Bus Size N+1, per-slot
    L5K arrays and pad dimensions all N+1, slot member lists trimmed in
    both the Decorated structure and the type definition, and zero sizing
    errors in the two arms the model can price.

    **Naming arm, 12 more files** (`pioname_*`). Every card in all three
    real exports is NAMELESS -- catalog and slot only. That is the unusual
    shape, not the normal one: a module you name in the I/O tree gets
    module-defined tags of its own, and this model already charges real
    bytes for a tag's NAME LENGTH elsewhere (`alias_tag`, the AOI and UDT
    type-name-length buckets). So naming a card plausibly costs something,
    plausibly scales with the name, and plausibly differs by connection
    format -- a rack-aliased card has no tag of its own to name, so it may
    be free there and not free in the other two.

      - `pioname_{enhanced,enhdata,optimized}_named_n08` — 8 named cards,
        8-character names, one per format. Differences against the
        nameless `pioconn_<fmt>_n08` at the same count.
      - `pioname_enhdata_len{05,08,16,24,32}_n08` — the same 8 cards at
        five name lengths. Flat rate or per character?
      - `pioname_enhdata_named_n{01,02,04,16}` — named-card count, against
        the nameless file at each count. Per card or once per file?

    The engine currently predicts **exactly the same total named or
    nameless, at every length and every count** — it has no term for a
    module name at all. That makes all twelve direct measurements of an
    unmodeled quantity: any nonzero capture delta is a gap, and a zero
    delta confirms the zero rather than leaving it assumed.

    Stake: this is not a corner case. Elmsdale alone has three of these
    racks (JB101_IO, C102_IO, MCP101_IO — 19 cards), all currently priced
    at either a flat 1,672 they do not cost or, for the rack-aliased ones,
    at zero.


42. **OQ-AXISMARGINAL** — new 2026-09-11, and the largest single-sign
    unreconciled block in the corpus. Found by `scripts/unreconciled.py`, also
    new that day, which recomputes every captured row against the CURRENT
    engine: **1,601 of 2,770 captured rows sit outside +-8 bytes**, and the
    worst family by magnitude is the 31-row axis set, captured 2026-09-03.

    Every `axis_scale_*` file with n>=2 over-predicts, monotonically, to
    **+62,528 bytes (+10.5%)** at 20 axes. Both arms are perfectly linear in
    axis count with zero residual at every step:

        single-axis drives   +3,288 per axis    n = 2,4,6,8,12,16,20
        dual-axis drives     +2,600 per axis    n = 2,4,6,8,12,16,20

    and the two shared base points (n=1 single, n=2 dual) both sit at +56 —
    exact. So the FIRST axis in a file is priced right and every one after it
    is not. This is a marginal error, not a base-constant error, which matters
    because `AXIS_CIP_DRIVE` was promoted FITTED -> KNOWN earlier the same day
    on single-axis evidence. That promotion is correct for one axis and wrong
    for the twentieth, and the entry should be read that way until this
    closes.

    Real exposure: the sixteen real programs carry **359 AXIS_CIP_DRIVE and 65
    AXIS_VIRTUAL** tags. At the single-arm rate that is roughly **650 KB** of
    over-prediction sitting inside the real totals, the same order as
    OQ-MODULEMARGINAL's 824,864 — and in the same direction, so the two
    together are most of what the under-predicting real files are being
    compensated by.

    **Why the two arms do not decompose on their own.** The naive subtraction
    gives a clean-looking answer:

        single: 1 module per axis      A + M    = 3,288
        dual:   1 module per 2 axes    A + M/2  = 2,600
        -> M = 1,376, A = 1,912   (A identical from both arms)

    It is not valid, for two reasons that come from reading the files rather
    than the numbers:

      - The single arm is 8 x 2198-S086-ERS3, **one catalog repeated**. The
        dual arm is one each of D012/D020/D032/D057, **four distinct
        catalogs**, repeating only as n grows. OQ-MODULEMARGINAL's open
        question is exactly whether the module discount is per catalog or per
        file, so `M` is not the same quantity in the two arms.
      - **Every one of these 31 files carries `error_count = n+1` with an
        EMPTY `error_log`.** All 144 errored rows in the manifest were
        captured between 2026-08-23 and 2026-09-08; the error-log reader in
        `logix_build_capture.ahk` only began working 2026-09-10, so not one of
        them has any error text on record. The n=1 file has 2 errors and is
        still byte-exact, which suggests they are benign — but that is an
        inference, and this is the direct reason a 31-row family with a 10%
        systematic error sat unexamined: there was no way to tell whether the
        rows were trustworthy. **The 144 errored rows need recapture under the
        current tooling**, and that is the single highest-value thing the
        capture rig can do.

    **Test files built 2026-09-11, `gen_axis_marginal.py`, 16 files.**

      - `axmarg_virtual_n{01,02,04,08,12,16,20}` (7) — the decoupling arm.
        AXIS_VIRTUAL needs no drive module at all, so a count sweep with ZERO
        modules in the file measures the per-axis term with nothing to share
        it with, which neither captured arm can do. Real programs carry 65 of
        these, so it is their real shape.
      - `axmarg_1cat_n{02,04,08,12,20}` (5) — the same axis and module counts
        as the captured `axis_scale_n*_dual`, but ONE catalog repeated instead
        of four distinct. Same axes, same modules, only catalog repetition
        differs.
      - `axmarg_ncat_n08_{1,2,4}cat` (3) — axis count AND module count both
        pinned at 8 and 5; only the number of distinct catalogs moves. All
        three predict an identical 245,080 (they draw from one catalog family
        the engine prices identically), so any difference in the captured
        actual is purely the catalog-diversity effect. Under a per-catalog
        discount the three differ; under a per-file one they do not move.
      - `axmarg_mixed_n08` (1) — 8 AXIS_VIRTUAL plus 8 AXIS_CIP_DRIVE in one
        file, against the two single-type files at the same count: is the
        marginal term per axis TAG regardless of type, or per type?

    **Do not wire any of this before the virtual arm lands.** The 1,912/1,376
    split is arithmetically exact on 14 points and still rests on an
    assumption the data cannot support, which is the same mistake the axis
    promotion already made once today.

    **CAPTURE ERRORS: 66 row(s)** flagged here by `scripts/capture_errors.py` (step 2b), 2026-09-11.
    65 captured WITH Studio build errors, so their `actual_bytes` is
    SUSPECT rather than wrong — part of the file may never have reached the
    controller, which inflates apparent over-prediction. None of them carries
    any error text: every errored row in the manifest was captured between
    2026-08-23 and 2026-09-08, and the error-log reader only began working
    2026-09-10, so these need RECAPTURE before their numbers are used.
    `axis_scale_n01_single`, `axis_scale_n02_dual`, `axis_scale_n02_single`, `axis_scale_n04_dual`, `axis_scale_n04_single`, `axis_scale_n06_dual` (+59 more)
    1 committed file(s) attempted and never reached `ok` in
    `convert_log.csv`: `daxis_axis_cip_drive`

