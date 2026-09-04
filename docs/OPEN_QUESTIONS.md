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

9. **OQ-AOIORPHAN** — **RESOLVED 2026-08-31, moved to
   RESOLVED_QUESTIONS.md.** Core question (does an orphaned/never-
   instantiated AOI definition cost real memory) is closed: minimal-pair
   real capture confirms `report.py`'s existing $0-extra rule is correct,
   not just assumed (8-byte residual on the unreferenced file, 0.04%).
   See RESOLVED_QUESTIONS.md for the full writeup. The only piece still
   genuinely open is tracked under OQ-COMPOSITESCALE below: real capture
   on the remaining `gen_composite_realistic.py` files (32 of 50 not yet
   captured, 8 of those blocked on an unrelated CIP-Safety-catalog import
   bug) — a larger/varied corroboration, not a reopening of the core
   question.

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

**Correction, 2026-08-31: the 2026-08-29 Required/Visible fix did NOT
actually resolve the import failure.** James's 2026-08-30 l5x2acd run
shows `aoi_array_param_def_only` still failing with the identical
`XMLSrv_E_IMPORT_ABORTED_NO_CHANGES` generic wrapper text, on the
regenerated (post-fix) file. The `Required="true" Visible="true"` change
was a hypothesis extended from the two real InOut-array examples in the
corpus, explicitly flagged above as "not positively confirmed for
Input/Output" — that hypothesis is now disproven, or at least insufficient
on its own; there's still a real, separate import blocker. Task list
previously (wrongly) marked this fixed — corrected here. Root cause
remains unknown; the wrapper text carries no per-file detail, so guessing
further isn't productive. Added to `samples/known_conversion_failures.csv`.
Need the real Studio 5000 error-log line from James to make any further
progress on this file.

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

**Import failure, 2026-08-30 — root-caused and fixed 2026-08-31.**
`eventtask_instronly` failed to import; James pulled the real error this
time: "Failed to set the 'Size' property (Chassis size exceeds the
allowable size for a chassis.)" on the Local module's own backplane Bus —
with NO axis tag involved, which disproves the earlier (2026-08-30)
dismissal of this exact error class as a downstream artifact of the
WatchedAxis tag bug (see that comment above); it's a real, independent
bug. Root cause: `processor_type="5069-L306ER"` (bare, no S2/M/MS2/MS3
suffix) was used ONLY in this one file in the entire project — every
other 5069 generator uses a specific suffixed variant — so
`_5069_BUS_SIZE_BY_MODEL`'s assumption that all L306 variants share Bus
Size=9 (confirmed only against the Safety+Motion `L306ERS2_Sample.L5X`)
was never actually tested against the bare model. Also found: this file's
docstring claimed it mirrors `taskoverhead_n02tasks`'s "5069-L306ER"
baseline, but `gen_task_overhead.py` never passes a `processor_type`
override either — that file is really 1756-L81E, so the comparison was
never actually apples-to-apples. Fixed by dropping the processor_type
override entirely (uses the wrapper default, 1756-L81E) — fixes the
untested/broken bus size AND the baseline mismatch in one real, evidenced
change. Removed from `known_conversion_failures.csv`. `eventtask_axiswatch`
got the same fix (same override removed) even though it wasn't in this
failure batch, since it shares the identical root cause. Needs a real
reconversion pass to confirm — not independently verifiable from here.

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
140/140 unit tests pass with this batch included. The v3 follow-on
generator (`gen_composite_realistic_v3.py`, see OQ-V3GENBUGS) reuses this
module-cycling and AOI/orphan machinery unchanged and adds deliberately
wide-varying program/subroutine/AOI counts (5-24 AOIs, 5-12 programs,
1-3 subs/program) plus a target-byte-count-by-construction technique: it
measures the real content "floor" via a direct `build_report()` call, then
sizes one filler DINT array via already-KNOWN formulas to land within a
few bytes of a per-file target between 1,550,000 and 2,449,999.

[^axiscombo]: Two different real-data-derived axis/motion
predefined-structure number sets exist and were never cross-checked
against each other. OQ-PREDEFINED (RESOLVED_QUESTIONS.md, derived
2026-08-23 via `residual = actual - sizeable_engine_total -
empty_project_baseline`, single-sample-each, FITTED) gives
AXIS_CIP_DRIVE=22,636, COORDINATE_SYSTEM=9,516, AXIS_SERVO=
AXIS_VIRTUAL=16,796 — these ARE the values currently wired into
`memory_model.yaml`'s `predefined_structures`, and the sizing engine does
NOT error on these 4 axis types today. A separate note, OQ-AXISSTRUCT
(RESOLVED_QUESTIONS.md, appears in the Tag/UDT section ahead of
OQ-PREDEFINED's section but reads as never reconciled against it),
records a second real set of Capacity totals — AXIS_CIP_DRIVE=22,728,
COORDINATE_SYSTEM=9,616, AXIS_SERVO=AXIS_VIRTUAL=16,888 — each
consistently 92-100 blocks HIGHER than the wired values — "measured over
a MotionGroup-only local baseline (19,296 blocks)." That 19,296 baseline
figure doesn't appear anywhere else in this project's docs and doesn't
cleanly decompose from what's already wired: `empty_project_baseline`
(13,296) + `MOTION_GROUP` (1,076) = 14,372, leaving an unexplained
~4,924-block gap. Without the actual source L5X/file composition behind
the OQ-AXISSTRUCT numbers, there's no way to tell from the two aggregate
totals alone whether this second set reflects (a) formula drift in some
shared cost since 2026-08-23, (b) a real MotionGroup-only baseline file
with more content than OQ-PREDEFINED's bare per-axis isolation files, or
(c) the still-open multi-axis "combo" case rather than the
single-axis-in-isolation case OQ-PREDEFINED already solved. Genuinely
blocked on that source data (or a fresh, clearly-labeled real capture) —
not guessable from two aggregate totals, and not acted on (no formula
change made) pending it.
