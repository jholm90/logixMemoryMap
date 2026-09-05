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
   **decided and wired 2026-09-03** (James: "they are safety tasks and
   safety programs therefore they need seperate sizing calculations").
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
   enforces the exclusion. James's shell decision doesn't resolve this —
   it was specifically about Task/Program/Routine containers, not tag
   content. Still needs a call: exclude Safety-class tags from sizing
   everywhere by design (and wire that exclusion explicitly), or size
   everything resolvable including Safety tag content and adjust the
   warning wording.[^safetyscope]

5. **OQ-AOIARRAYDIMENSION** — the `aoi_array_param_def_only.L5X` import
   thread is **CLOSED 2026-09-03, real root cause** (James, live
   controller testing: "the issue is BOOL/SINT/INT/DINT cannot be arrays
   for Inputs. Arrays require InOut"). The two prior "fixes" (Required/
   Visible forced true/true 2026-08-29, then a real `<Array>`/`<Element>`
   DefaultData body 2026-08-30) were chasing a formatting bug that never
   existed — an array-dimensioned atomic Input/Output Parameter is not a
   legal Logix construct at all; only `Usage="InOut"` permits an array
   Parameter (matches this project's own real corpus evidence,
   `LOG_HMIDisplay`/`BitArray` — both `Dimensions` AND `InOut`, which is
   now understood as the ONLY combination that can exist, not a coincidence
   of the only 2 examples on file). Fixed for real:
   `builders.py::_aoi_parameter_xml` now hard-fails (`ValueError`) if a
   caller ever asks for a dimensioned Input/Output Parameter, so this
   generator-level bug class cannot recur; `lint.py`'s new
   `aoi_array_param_wrong_usage` check is a defense-in-depth net for any
   L5X reaching lint by another path. The broken `aoi_array_param_def_
   only.L5X` file and its never-successfully-captured manifest row are
   removed (confirmed via `convert_log.csv`: FAILED at every one of 5
   logged attempts, 2026-08-30 through 2026-08-31, `XMLSrv_E_IMPORT_
   ABORTED_NO_CHANGES` every time — never had real ground truth to lose).
   Same fix pass also found and closed a second, previously-untested gap
   in the SAME function: the InOut branch never rendered a `Dimensions`
   attribute at all (no generated file had ever actually exercised
   `inout_params=[...]` with `dimension` set until a new test for this
   fix exercised it) — now fixed to match the real `LOG_HMIDisplay`/
   `BitArray` shape.

   **Still genuinely open, separate sub-thread**: the array-LocalTag
   dimension-scaling question (real +400/+404-byte, ~2%, gap on
   `aoi_array_localtag_1_instance`/`_def_only`, both at dimension=100 —
   the only 2 real data points on file, both the SAME size, so it's
   unknown whether the gap is a flat per-array-LocalTag declaration cost
   or scales with dimension/element type). The current `aoi_definition`
   formula charges `per_declared_item` once per declared item regardless
   of `dimension`, so if the real gap DOES scale with size this is a
   genuine missing term. 27-file isolation sweep built 2026-09-03
   (`gen_aoi_arraylocaltag_sweep.py`: dimension 10–1000, type SINT/INT/
   DINT/REAL/BOOL, multiplicity 1–3 array LocalTags/AOI) awaiting real
   capture.[^aoiarraydimension]

6b. **OQ-MODULESTRUCTURAL** — NEW, 2026-09-04, and it changes the target
   for OQ-MODULEIO below. James: *"the target application for this is to
   have an unknown file tested and we cannot 100% capture all catalog
   module numbers individually — you'll have to tell that a 16pt digital
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
     axis James is asking for -- 1756-IA16 and 1756-IB16 are different
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

    James, 2026-08-31, real, caught reviewing the target-content-scale
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

9. **OQ-AOIORPHAN** — **CLOSED. Full entry and reasoning trail moved to `docs/RESOLVED_QUESTIONS.md`** ("Closed 2026-09-05" section).

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

    **Import failure, 2026-08-30 — root-caused and fixed 2026-08-31.**
    `blockbytetest_l71_dint120000` failed to import; James pulled the real
    Studio 5000 error-log detail this time ("Name collision: imported
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
    (James's real capture batch, merged into `manifest.csv` this pass).
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
      click first... now resolved on James's end" — this data suggests
      that fix may not actually be reading the real value, just no
      longer erroring). **None of this 45-row batch should be treated as
      real ground truth or used to tune any formula** until James can
      confirm what the AHK script is actually reading for these two
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
      James's "bytes" vs "blocks" label difference may be a real Studio
      5000 UI distinction, but it doesn't appear to be *why* the L7x/1769
      numbers run high; a real per-family baseline term (analogous to the
      already-wired firmware-version baseline deltas) is the more likely
      fix once more clean (non-contaminated) L7x data points exist to fit
      it. Still needs at least one more clean L7x data point (ideally a
      near-empty-baseline file, to isolate the constant term from the
      content-scaling term) before wiring anything — one point can locate
      a family-level gap but can't separate "baseline is bigger" from "per
      element is bigger" on its own.

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

    **Import failures, 2026-08-30 (James's l5x2acd run) — 14 of the 50
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

        **Root-caused and fixed, 2026-08-31** (James pulled the real
        Studio 5000 error-log detail for `_07`): "Slot number in use by
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

      **Renamed with a "_r2" suffix, 2026-08-31** (James: "confirm that
      you will have different filenames for the 50 tests and abandon the
      old ones" — real Studio 5000 verify errors found separately, see
      OQ item covering aoi_call_arg_count_mismatch/XIC-OTE-data-type,
      meant every one of the 50 composite files changed real content
      again after James had already pushed an l5x2acd batch against the
      names above). All references to `composite_realistic_NN` in this
      section are the OLD, now-deleted filenames, describing what was
      diagnosed against them at the time — the CURRENT files are
      `composite_realistic_NN_r2.L5X` (same index numbers, same
      per-file composition/catalog mix, just fixed content). The 9 still
      catalog-explained-broken filenames in `known_conversion_failures.csv`
      were updated to their new `_r2` names alongside this rename so
      they stay correctly flagged.

      **Real capture landed, 2026-08-31 — the core question is
      essentially answered, and it's good news.** James's batch
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
      JSR-target content, and this time it's explained and wired.** James,
      2026-08-30: "I expect at least 50 large programs with io and logic to
      test your generation knowledge" — `gen_composite_realistic_v2.py`
      built 50 new files, same UDT/array/module/AOI-declaration shape as v1
      but with every referenced AOI now carrying real internal Logic-
      routine content (5-45 real instructions) and one real 0-param JSR-
      target subroutine per file (20-220 real instructions) — the two gaps
      OQ-JSRPARAMCOST/OQ-AOIINTERNALLOGIC found and wired in isolation,
      now exercised together at composite scale for the first time. Real
      capture landed against all 50 (5 files — `_07`/`_18`/`_19`/`_30`/
      `_50` — carry real Studio 5000 import errors unrelated to sizing: a
      193-ECM-ETR module-compatibility issue and a safety-drive-on-
      non-safety-PLC issue in the module mix, both James-deprioritized as
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
      sequential slot numbering) remain separately tracked, James-
      deprioritized until this tuning work lands.

12. **OQ-AOIINTERNALLOGIC** — new, real, corpus-wide gap, James 2026-08-31:
    "So you closed aois but never put logic inside? All aois have one
    subroutine but they can have more, see the HomeToTorque aoi."
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
    written earlier this session** (see OQ-COMPOSITESCALE below): neither
    this fix nor the JSR-target-content fix explains the composite
    batch's residual, since composite files don't currently exercise
    either gap — that residual's real source is still unidentified.

13. **OQ-IDENTNAMELEN** — new, real, found 2026-08-31 in the same push as
    James's "5/10/15/20/50 subroutines... different routine name lengths"
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
    old, invalid namelen48; see this session's fix) — and the two
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
    catalogs — see the correction below). James, 2026-09-02: real Studio
    5000 error on `composite_realistic_v2_18`/`_50` ("Error:
    TestMod2_193ECMETRA: Child module incompatible with parent module").
    Self-audit (checking for real currently-unreconciled `error_count`
    data per CLAUDE.md's standing rule, not just the composite files James
    named) found this is NOT composite-specific: BOTH standalone
    `modulesweep_193_ecm_etr_a`/`_b` already carry a real `error_count=1`
    in `manifest.csv` — sitting there uninvestigated since capture, never
    previously flagged. No real Studio 5000 error-log line exists for the
    standalone repro (only James's composite-context quote above), so the
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
    immediately after: James's own real production file
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
    guessed theory. A real, still-untested alternative worth checking
    first when real error-log detail is available: this project's own
    genericized `2198-S130-ERS3`/`2198-D057-ERS3` blocks may be missing a
    real Motion/Axis association these Kinetix drives need beyond the
    Diagnostics connection alone — James's real file's module carries
    plain `DiagnosticInput`-only connections in the excerpt checked so
    far, so this isn't confirmed either, just a real lead not yet a
    guess turned into code.

    **New real evidence, 2026-09-03 — the "missing Motion/Axis
    association" lead above is now DISPROVEN too.** All 50
    `composite_realistic_v3_*` files hit the exact same 2-error signature
    on real Studio 5000 conversion (James): `Tag 'D012_23:SI': Invalid
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
    (with or without an axis bound), while only James's own real
    Titusville production file has ever shown it working. Direct,
    attribute-by-attribute comparison of James's real `2198-D057-ERS3`
    Module block (from Titusville) against this project's generated
    `2198-D012-ERS3` block found them structurally near-identical
    (same Ports/EKey/Communications/Connections shape, same
    `SafetyEnabled="false"`, no `SafetyNetwork`) — the one confirmed
    difference is the real block's `<ExtendedProperties>`
    (`Vendor`/`CatNum`/`FeedbackDevice1-4`/`ConfigID`) is entirely absent
    from every generated instance, but that can't be confirmed as the
    cause either: `gen_module_sweep_variants.py`'s own real-corpus-
    verbatim `2198-D012-ERS3` "2conn" block (source:
    `motion_p208/p208_D012_NodeAndAxisDual3.L5X`, a real James-uploaded
    file) ALSO has no `<ExtendedProperties>` and the exact same zeroed
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
    channel, explaining the SI/SO auto-creation — James disproved this
    immediately with two more real reference exports
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
    2026-09-03.** James retested the Ch2->Ch3 fix (`modulemotion_
    d012_dual_axis.L5X`): same 2-error signature. He also clarified the
    actual crash: opening the **module's own I/O-tree profile page**
    (not the axis properties page) crashes Studio outright -- confirmed
    by testing his own original, unmodified real source file
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
    the module-page crash, though NOT yet confirmed (James said "P208
    isnt the issue" independently of this fix, before it was applied --
    still needs a retest of the regenerated file to know either way).
    Fixed: new `_dcbus_axis_tag()` helper using the real, verbatim-
    extracted DC-bus shape, wired into all 3 generators
    (`gen_module_motion.py`, `gen_composite_realistic_v3.py`,
    `gen_module_axis_scale.py` -- the last one had never been checked
    against this bug before). All affected files regenerated, lint-clean,
    177/177 tests passing.

    **Two separate, real bugs found and fixed the same pass, NOT this
    one:**
    - **Sequential slot numbering** (James: "lots of racks did not have
      the slot numbers used in sequence... please add this check").
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
      changed, flagged for James to confirm before any future regen.)
    - **"Safety-rated module in a non-safety-declared composite"
      (`2198-S130-ERS3`, `composite_realistic_v2_19`/`_30`)** — this WAS
      diagnosed and fixed here initially, then disproven within the hour
      by real evidence. See the CORRECTION under OQ-193ECMETR above for
      the full story: it's genuinely undiagnosed, not a safety-controller
      requirement, and now sits in the same exclusion bucket as
      `193-ECM-ETR/A`/`/B`.

15. **OQ-V3GENBUGS** — three real generator bugs found via James's actual
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
    (James still validating ACD conversion as of 2026-09-02) — no sizing
    formula changes from this item, generator-correctness only.

16. **OQ-JSRSCALE / OQ-COMPOSITESCALE** — the composite AOI/JSR surcharge.
    **REFITTED ON REAL PROGRAMS 2026-09-04. Was the project's #1 error
    source; is now its largest remaining one, but 5x smaller.**

    James supplied real Capacity readings for 8 whole real customer
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
    axis content is NOT "100%-blind, priced at exactly $0" as described to
    James earlier this session — AXIS_CIP_DRIVE/AXIS_SERVO/AXIS_VIRTUAL/
    COORDINATE_SYSTEM are wired and sizing without error today (FITTED,
    single-sample-each). See footnote for the actual unreconciled numbers
    and what's needed to close this for real.

18. **OQ-STSIZING** — new, 2026-09-04. **Structured Text is completely
    unmodeled.** `parse_rll_routines` handles RLL only, so every ST routine
    in every file contributes exactly **0** to the prediction. Every file
    in the `gen_st_sizing.py` batch predicts an identical 23,365 today —
    that is the diagnostic property, not a bug: whatever Capacity movement
    comes back IS the ST cost, with nothing to subtract.

    **This is not a small corner.** Measured across `samples/local/`, 23
    real files: **297 ST routines, 24,017 ST lines.**
    | construct | count | | construct | count |
    |---|---:|---|---|---:|
    | `:=` assignment | 8,688 | | `FOR`/`DO`/`END_FOR` | 600/879/148 |
    | `IF`/`THEN`/`END_IF` | 1,739/1,831/1,230 | | `WHILE`/`END_WHILE` | 38/3 |
    | `ELSIF`/`ELSE` | 559/332 | | `REPEAT`/`UNTIL` | 1/8 |
    | `CASE`/`OF`/`END_CASE` | 90/1,085/84 | | `EXIT`/`RETURN` | 39/5 |
    Comments: **5,931 leading `//`, 967 trailing `//`, 27 `(* *)` = 6,925
    lines, 29% of all real ST.** Instruction-style calls INSIDE ST: COP
    362, CONCAT 67, SBR 44, RET 42, DTOS 26, TRUNC 25, TONR 22, JSR 18,
    DELETE 16, OSRI 12, ABS 10, GSV 8, SIZE 7, STOD 7, BTDT 6, CPS 4,
    SCL 4, MSG 2, SSV 1.

    So real ST is ~36% control flow, ~29% comments, and it calls the SAME
    instructions the ladder does. That last fact is the cheapest possible
    route to closing this hole and is what group D tests: 1,000 COP /
    CONCAT / DTOS / SIZE calls hosted in ST, each using operands
    byte-for-byte identical to `gen_logic_sweep`'s own rung text, paired
    against the existing valid `instr_*_n01000` captures. **If they land on
    the same number, the entire per-instruction weight table transfers to
    ST unchanged** and ST needs only a per-statement term and control-flow
    terms on top.

    Sub-question, **OQ-STCOMMENT** (James, 2026-09-04: *"one thing not
    modelled is st comments and if a comment line or block takes up data
    memory or is like tag and rung comments and does not count towards data
    usage"*). The RLL half of this is already ANSWERED and free:
    `instr_cpt_n05000_comment100` and `instr_cpt_n05000_nocomment` came
    back **byte-identical at 2,282,944**. But that result does not
    transfer, and assuming it would be a real mistake: an RLL rung comment
    is a separate `<Comment>` element hanging off the rung — metadata
    beside the logic — whereas an ST comment lives INSIDE the routine's own
    source CDATA, in the same text Studio compiles. Group B holds 100
    executable lines identical to `realscale_st_n00100` and varies only the
    comments: 100 short leading, 100 long leading (110 chars, the real
    header width from Bender134053's T_ADD routine), 400 short leading, 100
    trailing (zero added lines), and 400 genuinely blank lines with no
    comments at all. That set separates per-comment-LINE from
    per-comment-CHARACTER from per-`<Line>`-element, and answers whether
    blank lines are free.

    Also open and covered by the same batch: whether an ST assignment with
    an arithmetic right-hand side is just a CPT expression (group E
    transcribes `instr_cpt_n01000`'s expression operand for operand into ST
    — if it lands on 474,944 the existing tier-aware CPT model is reusable
    as-is), and whether an ST routine used as a JSR target is charged the
    same parameter cost as an RLL one (group F; all JSR param constants
    were fitted on RLL targets only, and 44 SBR / 42 RET in the corpus say
    ST targets are a real shape). Blocked on capture — **not on James
    writing samples: 24,017 real ST lines is more idiom than this needs,
    and every construct and call in the batch is taken from that corpus,
    not invented.**

19. **OQ-EXPORTSCOPE** — new, 2026-09-04 (James: *"Can you please rewrite
    the estimation script for handling controller, udt, aoi, programs,
    routines, rungs logic exports... Anything that's not a controller
    export can not use the prices sir base load, but rungs, routines and
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
    needs James at the bench rather than a generator run.

20. **OQ-ALARMCOND** — **CLOSED. Full entry and reasoning trail moved to `docs/RESOLVED_QUESTIONS.md`** ("Closed 2026-09-05" section).

21. **OQ-SHELLSCALE** — **CLOSED. Full entry and reasoning trail moved to `docs/RESOLVED_QUESTIONS.md`** ("Closed 2026-09-05" section).

22. **OQ-BUILDFAIL-OPEN** — the 11 sample files that genuinely still fail to
    build, 2026-09-05. Audited down from 138 `error_count > 0` rows: 72 were
    stale captures against files regenerated after the fact (cleared, they
    re-run automatically), 13 were superseded by exact `realscale_*` tests,
    40 were obsolete composite v1/v2, 2 no longer exist. These 11 are real,
    and **nothing in this repo diagnoses any of them** — the generators'
    own comments are silent, so the cause has to come from James's Studio
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


23. **OQ-DEFSCALE** — new, 2026-09-04. **Now the single largest identified
    gap on real files, and the direct successor to OQ-SHELLSCALE.**

    With shells refit from isolation and alarms exact, all nine real
    programs still under-predict, every one of them:

    | file | actual | predicted | delta |
    |---|---:|---:|---:|
    | `murraybros_20260122r1` | 923,320 | 850,077 | **−7.93%** |
    | `ipc_edgerline_20251217r1` | 2,255,773 | 2,142,530 | −5.02% |
    | `accutally_20260803` | 5,999,972 | 5,747,134 | −4.21% |
    | `emporiumedger_20250905r1` | 1,703,932 | 1,640,431 | −3.73% |
    | `cmu_2025_10_14r00` | 5,217,440 | 5,066,834 | −2.89% |
    | `pukall_gang_20260414_r00` | 2,502,336 | 2,437,207 | −2.60% |
    | `emporium_2025_05_28r01` | 7,136,625 | 6,970,969 | −2.32% |
    | `k3m16_edgers_20220808r00` | 4,044,994 | 3,966,805 | −1.93% |
    | `mrfp_edger_2026_06_01_r00` | 2,281,316 | 2,259,476 | −0.96% |

    Mean absolute error **3.51%**, 1 of 9 inside the <1% North Star target.
    Every single one under-predicts, so this is a missing cost, not noise.

    Re-regressing the residual against structure AFTER the shell refit
    (the refit is what makes this reading meaningful — it removed the
    collinear program/routine signal that previously dominated):

        aoidefs    r=+0.878          routines   r=+0.581
        udts       r=+0.838          rungs      r=+0.545
        tags       r=+0.709          programs   r=+0.431
        sttext     r=+0.629          instrs     r=+0.388

    Programs and routines fell from +0.871/+0.829 to +0.431/+0.581 once
    their own constants were correct — which is exactly what a collinear
    artefact does when the real term underneath it gets fixed.

    **Why the existing corpus cannot answer this, checked before fitting
    anything.** Across all 1,961 captured non-real files the maximum is
    **7 AOI definitions** and **6 UDTs**, and 308 of the 312 files
    containing any AOI at all have exactly ONE. The nine real programs
    carry **11–39 AOI definitions and 53–174 UDTs**. So every real-file
    prediction extrapolates per-definition cost 5×–30× past the largest
    point it was ever measured at, on both axes simultaneously. The 127
    existing `*_def_only` files vary what is *inside* one definition
    (param count, param type, local tags, name length, packing) — never
    how many definitions exist.

    That is the identical shape of the error OQ-SHELLSCALE just caught:
    a constant fitted at n=2 and extrapolated to n=200, wrong by 8
    bytes/unit, invisible at n=2 and worth 1.97% at n=200.

    **Deliberately NOT fitted from the real files.** On a real project
    aoidefs, udts, tags and rungs all move together; that collinearity has
    now produced four wrong fits in a row (three surcharge fits, then the
    shell hypothesis). `gen_defscale.py` (30 files) isolates it instead:

    | sweep | varies | span | current model's slope |
    |---|---|---|---|
    | `defscale_aoidefs_n*` | AOI definitions, zero instances | 1→60 | 1,292/def |
    | `defscale_aoiinst_n*` | same defs, one instance each | 1→60 | 1,412/def |
    | `defscale_udts_n*` | UDT definitions, zero tags | 1→200 | 248/UDT |
    | `defscale_udttag_n*` | same UDTs, one tag each | 1→200 | 349/UDT |

    Spans deliberately bracket the real files on both sides, so a measured
    slope is interpolation on a real program rather than extrapolation.
    The model currently predicts a perfectly straight line in each sweep,
    so any slope error or curvature will be unambiguous. The paired
    with/without-instance sweeps separate definition cost from instance
    cost at scale, which no existing file does. **Blocked on capture.**


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
    call shapes verified by James's own build-clean Studio 5000 export
    (`instruction_shapes_20260904.L5X`), and none of them has a measured
    cost: **BRK, COS, LOG, SIN, PID, FBC, STOR, MCD, MCS, MCSV, MAG**.
    `gen_verified_instructions.py` builds each at n=10/100/1000 on an
    AXIS_VIRTUAL basis (no drive/module binding, so nothing has to be
    netted back out). The model currently prices all eleven at zero, so
    each sweep's predicted total is flat across n — any real slope is the
    instruction's cost, read directly. **Blocked on capture.**

    Provenance note worth keeping: NXT is excluded because James stated it
    is not a valid RLL mnemonic, and MCLM was skipped at his direction.
    Neither was inferred from documentation — which matters, because every
    previous attempt in this project to compose predefined-structure or
    instruction XML from a manual (alarm `ConditionType`s, the bare
    2-operand MAM/MAJ rungs, the Kinetix `:SI` safety tags) was rejected
    by the real toolchain.


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


27. **OQ-CPTNARROW** — how the SINT/INT → DINT widening scales. 2026-09-04.

    James, 2026-09-04: *"ints will use a behind the scenes conversion to
    dint."* That is the mechanism, and it resolved two things at once:
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
    batch and is not blocked on James for anything.

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


30. **OQ-REAL5069** — **the 5069 platform has ZERO real-file validation.**
    Found 2026-09-05, while checking a platform question from James
    ("Elmsdale had 5069").

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
    now formally dead architecture (James, 2026-09-05), which leaves
    5069/CompactLogix 5380 as the platform this tool most likely gets used
    on going forward -- and it is the one with no real evidence behind it.

    **What is needed:** one real 5069 export with a controller capture.
    James mentioned an "Elmsdale" project on 5069; that file is not in
    `samples/local/`. Any real 5069 program would do -- the point is a
    first real data point, not that specific one.

    Until then, the UI should arguably say so on a 5069 file the way it
    already warns on a Safety project. Not implemented yet -- flagged here
    rather than built, because a warning banner claiming more precision
    about its own uncertainty than the data supports would be its own kind
    of dishonesty.
