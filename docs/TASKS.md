# Task List

Checkbox per phase from PROJECT_PLAN.md. ✅ done — 🟡 partially done — 🔴 open.
Anything non-obvious gets a footnote instead of inline prose — see bottom
of file. Full reasoning trails live in RESOLVED_QUESTIONS.md/
OPEN_QUESTIONS.md, not here.

## Phase 0 — Setup
- ✅ Stack decided, repo skeleton, real sample files added, manifest.csv
      created, XML load + schema sanity check

## Phase 1 — Tag / UDT / AOI sizing engine
- ✅ Atomic type sizes, BOOL packing (standalone/UDT-member/array), UDT
      parser + alignment, tag/UDT-definition overhead, array-of-atomic and
      array-of-UDT sizing, built-in + custom STRING sizing
- 🟡 Module/IO parser[^moduleio]
- ✅ Controller/program tag scope separation, flat output contract
      (`report.py` `SizeEntry`), unit tests, validated against 4 real
      production files

## Phase 2 — UI v1
Local Flask server, vanilla JS/SVG squarified treemap, no CDN dependency.
- ✅ Treemap, root view, UDT/AOI defs pool, click-to-drill (infinite
      depth, lazy `/api/node`), breadcrumbs, sortable list view,
      type-utilization pane, confidence styling (solid/hatched), File→Open
      picker + desktop shortcut, processor part number in header,
      export-type warning banner, list/type-summary scoped per level,
      breadcrumb sibling browser

## Phase 2b — AOI sizing
- ✅ AOI definition parser (locals+params size like a UDT), UI drill-down
      into defs pool, AOI definition cost wired[^aoidef], inline/anonymous
      AOI instances confirmed a zero-occurrence case (not built)

- 🟡 **AOI declaration cost as a function of STRUCTURE, not name**
      (2026-09-06, OQ-AOISTRUCT). The definition-cost function prices
      base + per-item rate + AOI TYPE-name length and nothing else, which
      leaves seven structural properties at exactly zero: member name
      length, member descriptions, InOut params, predefined-structure
      members (TIMER/COUNTER/STRING/MOTION_INSTRUCTION/MESSAGE — 752 real
      member uses, never generated once before today), array dimensions,
      member counts past the fitted range (real AOIs reach 102 params /
      128 locals / 85 internal rungs against a corpus that topped out near
      6/2/1), and extra internal routines. `gen_aoi_structure.py`, 56
      files, one property per group. Deliberately NOT fitted per-AOI-name
      against the definitions shared across the projects: the tool is going
      to people outside the organisation whose code will be different and
      whose AOI libraries will be unfamiliar.
      The model predicts a dead-flat line across every group except the
      three scale sweeps, so any spread in the captured numbers is an
      unpriced item with no disentangling required. **Blocked on capture.**

## Phase 3 — Sample validation round 1 — **CLOSED 2026-08-24**
Exit criterion met: tag/UDT/AOI predictions match real Capacity data with
0.00% residual across the confirmed-formula majority; every discrepancy is
a tracked open question with a generator already built.
- ✅ Array/UDT-array/nested-UDT/STRING/custom-string sweeps, produced/
      consumed decided not needed, AOI call-count sweep, tag-scope sweep,
      capture→reconcile→update workflow standing since Phase 0 (1299+ rows),
      final confidence documented (`docs/INSTRUCTION_COVERAGE.md`: 95.1%
      exact fit)

## Phase 4 — Logic sizing round 1 (bit logic)
- ✅ XIC/XIO/OTE/OTL/OTU at scale — CONFIRMED, 0.00% residual
- 🟡 Branch depth[^branchdepth]
- ✅ Comments cost 0 blocks at any length, empty rungs at scale, NOP rate
      confirmed

## Phase 4b — Logic sizing round 2 (other instructions)
Scope from real instruction-frequency data across the 4 production
files; PID and ASCII-module instructions dropped (zero real occurrences).
- ✅ Timers/counters, motion+cam/route, GSV/SSV, array/file, string
      instructions, indirect addressing — all CONFIRMED and wired
- 🟡 Math/compare[^cmpcpt] -- REAL-destination CPT is now exact on all 47
      captured calls (2026-09-04, including the SINT/INT->DINT widening and
      the LINT-is-free correction). Integer-dest
      two-tier mixes are 19/23; four points sit exactly -4 on an operator
      ARRANGEMENT effect that the current probes demonstrably cannot
      resolve. 58-file `gen_cpt_closeout.py` batch covers every remaining
      CPT dimension -- see OQ-CPTARRANGE / OQ-CPTNARROW.
- ✅ JSR param cost[^jsrparam]
- ✅ MSG logic weight wired (48/rung); operand's own structure cost — see
      OPEN_QUESTIONS.md OQ-PREDEFINED
- ✅ Consolidate full instruction-weight table into MEMORY_MODEL.md
- ✅ Holdout validation[^holdout]
- ✅ **Structured Text wired** (2026-09-04, OQ-STSIZING). ST contributed
      exactly ZERO before this while the real corpus carries 297 ST
      routines / 24,017 ST lines. 22 of 23 captured ST files now land
      within 11 bytes. Key finding: an instruction inside ST costs exactly
      what it costs in a rung (four operand-for-operand pairs came back
      separated by exactly +432, the routine shell, and nothing else), so
      ST reuses the weight table rather than duplicating it. ST comments
      and blank lines are FREE -- count, length and position all -- which
      was an explicit question and did NOT transfer from the RLL
      result, since an ST comment lives inside the compiled source rather
      than beside it.
- 🟡 ST assignment expressions[^stexpr]

## Phase 4d — Motion structures
- ✅ AXIS_* / MOTION_GROUP / COORDINATE_SYSTEM predefined sizes, own root
      group in the UI tree
- 🟡 11 instructions with hand-verified call shapes generated but not yet
      captured (BRK/COS/LOG/SIN/PID/FBC/STOR/MCD/MCS/MCSV/MAG, on
      AXIS_VIRTUAL so there is no module overhead to net out) -- see
      OQ-VERIFINSTR

## Phase 5 — UI v2 (logic browsing)
- ✅ Routines/rungs share the tag data contract, Task→Program→Routine
      drill, subroutine call-tree (JSR cost-included tooltip), Estimated
      badge/dashed-outline styling, combined root view[^rootview]

## Batch review — 2026-09-11 capture (87 rows)

Ran the standing eight-step sequence on the batch as pushed.

1. ✅ **Reconciled** by row-level CSV merge on `sample_id`, never a git
      merge: 2,833 remote rows kept, 27 local ones added, nothing dropped.
      Every delta recomputed live against the current engine.
2. ✅ **Conversion status** cross-referenced, last row per filename wins.
      2,682 `ok`, **40 FAILED**, 60 with no record. 39 of the 40 share the
      one uninformative `XMLSrv_E_IMPORT_ABORTED_NO_CHANGES` error and were
      already tracked; the 40th is new, diagnosed and fixed
      (`daxis_axis_cip_drive`, trailing underscore). Nine
      `composite_realistic_*_r2` have still never been submitted at all.
      See docs/OPEN_BUILD_ERRORS.md.
3. ✅ **Re-derived and wired**: CAM base 8 → 4 plus 8-byte element-block
      alignment (15/15 exact, was 3/15), CAM_PROFILE FITTED → KNOWN on 13
      points, `FOR: 80` (4 points, zero intercept), `SBR: 0` / `RET: 0` as
      measured zeros rather than absences (12/12 exact).
4. ✅ **Open-questions review.** OQ-CAMSHAPE, RET/SBR and FOR closed and
      moved out. OQ-UDTBOOLMEMBER superseded by OQ-UDTMEMBERNAME after a
      structural twin contradicted it. New OQ-JSRFOLD, OQ-CAMSCALAR.
5. ✅ Docs brought current together: OPEN_QUESTIONS, RESOLVED_QUESTIONS,
      OPEN_BUILD_ERRORS, TASKS.
6. ✅ INSTRUCTION_COVERAGE.md updated — FOR added, RET/SBR moved from
      "NO DATA" to "CONFIRMED ZERO", MCCP unblocked now that the CAM
      operand's data space is closed.
7. ✅ **Next batch decided and built**: 24 `udtmn_*` member-name files and
      27 `pioconn_*`/`pioname_*` POINT I/O files. Every one answers a
      currently-open question.
8. ✅ Reported, including the conversion-failure log from step 2.

Real-file accuracy after this batch: **2.17% mean |error|, 4/16 within 1%,
9/16 within 2%** — unchanged. The wirings were exact on their own families
and worth a few bytes each on real files; none of them is the 2–5%.

## Phase 6b — UI browsing pass (2026-09-11)
Eleven reported browsing defects, all fixed and browser-verified against
the real Elmsdale and TrimmerTally exports.
- ✅ Breadcrumb keeps intermediate levels. Drilling from a nested
      (depth > 1) tile jumped straight from "All" to the leaf; the
      ancestor chain the click passed through is now carried into the
      stack, and the cross-reference/definition links navigate by chain
      instead of landing with an empty one.
- ✅ Array `[size]` on drilled members. `/api/node` had always sent
      `dimensions`; the client dropped it, so a UDT member array read as a
      scalar once opened (`Message` rather than `Message[200]`).
      `alias_of`/`alias_bit`/`confidence` were being dropped the same way.
- ✅ Module tiles carry the module NAME. A module's data_type IS its
      catalog number, so labelling by data_type rendered
      "PowerFlex 525-EENET / PowerFlex 525-EENET" with the name nowhere.
- ✅ Rack hierarchy. Modules nest under their stated `ParentModule`, so a
      1734-AENT draws its POINT I/O inside it the way Logix Designer's I/O
      tree does. Unmodeled shapes (rack-aliased, processor-embedded,
      legacy-network) are now emitted as zero-byte entries instead of
      being skipped entirely -- they were missing from the tree, not just
      from the total. Charged bytes are unchanged.
- ✅ "AOI Size: ( ) instance ( ) definition" radio pair replaces the lone
      checkbox, and reads AOI or UDT from the declared AOI names rather
      than from the path, which cannot tell them apart.
- ✅ Back button matches the breadcrumb's own size and colour.
- ✅ File load shows real progress (upload percentage, then an
      indeterminate parse phase) and resets to root/All on the Treemap.
- ✅ Depth defaults to 2.
- ✅ Cross-Reference tab is hidden, not merely disabled, off a UDT/AOI.
- ✅ Opening more than 100 children shows a modal with a live count.
- ✅ Alarm Conditions drill into their individual conditions (`/api/alarms`),
      200 rows summing exactly to the host tag's priced entry, instead of
      one undifferentiated block.

Four defects found while verifying the above, none of them reported:
- ✅ The treemap did not sum to the report. An AOI's member breakdown
      comes in lower than its priced definition entry on every real AOI
      (66,908 bytes, 6.1% of Elmsdale) -- carried as an explicit
      "Unitemized definition cost" row rather than dropped. See
      OQ-AOIDEFITEMIZE for the underlying disagreement.
- ✅ `build_hierarchy` raised UnboundLocalError on any file whose first
      entry was a non-tag category -- 4 of the 10 sample exports would not
      open at all.
- ✅ A CAM/CAM_PROFILE array advertised itself as drillable and then
      answered 400, because those types are priced per element and have no
      scalar size.
- ✅ The List tab threw on a zero-byte row (BIT alias, unmodeled module):
      confidence is null there by design and only the treemap honoured it.

## Phase 6 — Polish
- ✅ Safety-project warning (UI banner + CLI stderr)[^safety]
- ✅ Generator-side safety check (2026-09-03): verify that safety-rated
      hardware cannot be placed on a non-safety processor. `sample_gen.lint.lint_l5x`'s new
      `safety_module_on_non_safety_controller` check flags any Module
      with `SafetyEnabled="true"` in a file with no `<SafetyInfo>`
      element. Real trigger: 5069-IB8S/A and 5069-OBV8S/A rebuilt into a
      non-safety controller by hand without checking `gen_module_sweep.py`'s
      already-documented `_5069_SAFETY_CATALOGS`/`_5069_PROCESSOR_TYPE`
      fix from 2026-08-27 first. See docs/SAMPLE_GENERATION.md's "Before
      hand-picking catalogs into any script" section.
- ✅ Wire Safety Task/Program/Routine shell as its own sizing calculation
      (2026-09-03): safety tasks and safety programs need their own sizing
      calculation. New flat
      `safety_task_program_shell` (296 bytes/file) replaces the old
      ordinary-shell overcharge for a Safety task/program pair. Live-
      verified exact at fw v31-v33, 0.087% residual at v34-v38 (see
      OPEN_QUESTIONS.md OQ-SAFETYSCOPE-SIZING). The separate Safety-
      classed-TAG-content policy question (DCI_STOP/CONFIGURABLE_ROUT)
      is NOT resolved by this and stays open.
- ✅ **Tag-based alarm conditions SOLVED EXACTLY** (2026-09-05,
      OQ-ALARMCOND): `800 + 500*conditions + sum(associated-tag cost by
      type)`, zero residual on 37/37 captured files. These live INSIDE the
      `<Tag>` element (`<AlarmConditions><AlarmCondition>`), not in a
      top-level container, which is why a tag-walking parser missed 3,463
      of them on one real file. HMIGroup, alarm name length, Severity,
      OnDelay, Latched and AckRequired are all FREE. Given its own root
      group in the UI tree (2026-09-04, alongside Axis Definitions).
- 🔴 ALMD/ALMA *instruction* overhead -- still open, and now the higher-
      value half: `almd_minimal`/`almd_realtext` both fail to build with
      "Invalid number of arguments". The real ALMD faceplate shows 7
      operand slots with NO `In` operand (the input is the rung condition),
      and the call was rebuilt to match, but it has not been re-captured
      since. See OQ-BUILDFAIL-OPEN.
- ✅ Per-part-number memory budget (`controller_budgets.yaml`, prefix-
      matched against `Controller/@ProcessorType`, unknown types show
      "budget unknown" rather than a guess)
- ✅ Export report (CSV/XLSX)[^export]

---

[^moduleio]: `parser/modules.py` reads Connection/ConfigTag/ConfigScript
sizes straight off the L5X (Logix Designer states them directly). Real
per-catalog overhead (51 catalogs, `module_overhead_by_catalog`) replaced
the flat n=2 `module_overhead` estimate for those catalogs 2026-08-29 —
see OPEN_QUESTIONS.md OQ-MODULEIO. Two real threads remain (multi-module
marginal cost, a few connection-variant-dependent catalogs), both need
their own architecture work, not more test generation.
Produced/consumed tags (OQ-PRODCONS) RESOLVED — no special formula needed,
ordinary UDT-member recursion already covers a produced/consumed tag's
`CONNECTION_STATUS`-typed member, which is itself now a wired
`predefined_structures` entry (4 bytes, 2026-08-29 batch). See
RESOLVED_QUESTIONS.md.
**Zero-connection modules made visible 2026-09-02** (`report.py`):
modules with no Connection/stated size of their own (e.g. a bare
`ETHERNET-BRIDGE` IP-only fan-out, a real "placeholder for IP
addresses with no PLC logic connections" pattern) were being silently
skipped with no SizeEntry and no SizeError; now flagged with an explicit
SizeError (visibility-only, no total changed) — `"Local"` itself stays
excluded since its overhead is already covered by
`empty_project_baseline`. New test file: `bridge_placeholder_*`.
Three more real module-generator bugs found and fixed the same pass (a
regex crossing `<Module>` boundaries, a nameless-module lint blind spot,
an IPv4 4th-octet overflow past ~19 catalogs/file) — see OPEN_QUESTIONS.md
OQ-V3GENBUGS. New per-catalog-shape test batches awaiting real capture:
`axis_scale_*` (18, servo/dual-axis 2198 drive count scaling),
`rack_5069_*` (11), `rack_pointio_*` (11), `rack_1756_*` (12),
`cipmodule_scale_*` (7, CIP-MODULE generic-EDS declared-I/O-size sweep —
first real test of whether the flat `module_overhead` default shows the
same "scales with declared I/O size" pattern already confirmed for
ETHERNET-MODULE/ETHERNET-PANELVIEW).

[^aoidef]: `sizing/udt.py` `compute_aoi_definition_cost()`, FITTED not
KNOWN. AOI type-name-length step CLOSED 2026-08-30 (7/7 exact). The
separate array-of-AOI-instances element-cost formula (`aoi_array`,
downgraded KNOWN→FITTED 2026-08-30) is now its own open item — see
OPEN_QUESTIONS.md OQ-AOIBOOLPACK-PAIRING. **AOI internal Logic-routine
content WIRED 2026-08-31**: `parse_aoi_internal_logic()` aggregates every
AOI's internal RLL routine(s) into one pseudo-routine, weighed with the
same per-instruction-type table as ordinary routine logic
(`charge_shell=False`) — cut max residual on the isolation sweep from
12.02% to 0.55%. Real per-instance routine-count doesn't matter (splitting
content across 2 routines costs identically to 1), so it's aggregated, not
tracked per-routine. **Composite-scale content surcharge WIRED
2026-09-02** (`aoi_logic_composite_surcharge_per_instr=20`, FITTED via
regression on 22 real composite_realistic_v2 files) — real multi-AOI/
JSR-combined project scale showed a further systematic under-prediction
beyond the per-instruction weight alone; see OPEN_QUESTIONS.md
OQ-COMPOSITESCALE for the fit and remaining unexplained variance
(R²=0.66). **Does NOT generalize to real production scale, found
2026-09-02**: `TitusvilleTrimmer_20260902r2.L5X` (real file, 179 distinct
JSR targets, vs. the 22-file/1-target-each fit) misses by +7.71% with the
surcharge applied (+824,363 bytes of surcharge overshoot) but WORSE
(-14.7%) with it removed entirely — a real, larger, separate
under-prediction in the base per-instruction weighting only shows up at
real JSR-target counts. See OPEN_QUESTIONS.md OQ-JSRSCALE. **Now the #1
error source in the project, 2026-09-04**: the first real virgin-file
measurement (`Cardin_TrimSortStack_20260624r00`, 1756-L83E/fw 35.13)
came back **12.4% UNDER** (7,162,455 predicted vs 8,178,556 real), and
the `composite_surcharge_cap` alone suppresses 1,551,065 bytes of that.
The real file's uncapped surcharge is 130x the cap where the largest
synthetic composite is 8.2x, so the cap was fitted in a regime the corpus
could not leave. `gen_realscale_surcharge.py` (23 files, 2026-09-04) is
built to measure the law rather than fit that one point — a JSR-target
placement ladder paired file-for-file against the existing valid
`instr_xic_n*` captures out to 45,000 target instructions, a
same-content/K-targets split to test whether the cap is really file-wide,
and the first isolated AOI-internal-content ladder (there is no valid
nonzero AOI-content point on file today). Blocked on capture, and on more
real virgin files.

[^branchdepth]: Real cost confirmed (branch bracket structure costs real
memory beyond leg instructions), formula not yet fit — see
OPEN_QUESTIONS.md OQ-BRANCHDEPTH for the leg-count and staggered/nested
test batches now awaiting capture.

[^cmpcpt]: Everything except one CPT thread is CONFIRMED. CPT's
uniform-tier, T1+T2, T1T3/T2T3, and (2026-08-29) all-3-tier mixed cases
are all solved and wired (`sizing/constants.py` `CptExpressionModel`,
confirmed 0 residual on every real data point on file). One thread
remains — the REAL-operand/float-literal interaction is real data
demonstrating genuinely non-monotonic behavior, not yet a wireable
formula — see OPEN_QUESTIONS.md OQ-CMPCPTLAYOUT. CMP's own weight and
OQ-OPERANDTYPE's per-type surcharge are both resolved and wired.

[^jsrparam]: JSR's own flat weight (72/rung) and per-param cost
(`B(n)=4+20n` per call site, `A(n)=104+20n` once per distinct target)
both wired 2026-08-25. `parser/logic.py`'s `_jsr_calls()` reads the param
count off each real call's own 2nd argument. Verified end-to-end against
all 6 real capture points: 4 exact, 2 off by the same small +8 noise seen
elsewhere. **Output/return-param cost added 2026-08-29** —
`output_param_cost=20`/arg, charged per call site — see
RESOLVED_QUESTIONS.md OQ-JSRPARAMCOST for the full correction (the
original wiring only ever saw input-only calibration data) and
OPEN_QUESTIONS.md OQ-JSRPARAMCOST for the remaining residuals: A(n) not
yet output-param-adjusted, a STRING/UDT-specific per-call surcharge (not
cleanly linear yet, 3 real n-points on file). **JSR target content WIRED
2026-08-31**: `is_jsr_target` now weighs the target's own instructions with
the same per-instruction-type table as ordinary routines
(`charge_shell=False`), cutting max residual on the isolated content-scale
sweep from 13.37% to 4.75%. **Composite-scale content surcharge WIRED
2026-09-02** (`jsr_target_composite_surcharge_per_instr=47`, FITTED via
regression on 22 real composite_realistic_v2 files) — real multi-AOI/
JSR-combined project scale showed a further systematic under-prediction
beyond the per-instruction weight alone; see OPEN_QUESTIONS.md
OQ-COMPOSITESCALE for the fit and remaining unexplained variance
(R²=0.66). Same real-scale generalization failure as the AOI surcharge
above (found on `TitusvilleTrimmer_20260902r2.L5X`'s 179 distinct JSR
targets) — see OQ-JSRSCALE.

[^holdout]: 10 real captured files never used to fit anything (random
instruction-type combinations) checked against the current engine: 7/10
land within 0.05%, the other 3 fully explained by the already-tracked
OQ-CMPCPTLAYOUT gap, scaled by call count. No other instruction weight
implicated.

[^rootview]: Tags+logic share the "Program: X" root group; module I/O is
informational/non-summed `SizeError` entries by design — folding it into
the summed total is purely an OQ-MODULEIO confidence question, tracked
there only.

[^safety]: `L5XDocument.is_safety_project`/`.safety_level` parses
`Controller/SafetyInfo/@SafetyLevel`. Doesn't size Safety Task/Program
content — just warns the total is understated on a safety-rated project,
per the OQ-SAFETY decision (RESOLVED_QUESTIONS.md).

[^export]: `sizing/export.py`, same flat SizeEntry/SizeError contract as
the CLI `size` command and the UI, just serialized differently — no new
sizing logic. CSV is stdlib-only, always available; XLSX needs `openpyxl`
(optional `[xlsx]` extra, pyproject.toml) and degrades to a clear error
(CLI: message + exit 1; UI: 501 JSON error) rather than a broken file if
it's missing. CLI: `l5x-memory-analyzer export <l5x_path> <output_path>`,
format inferred from the output extension. UI: two toolbar buttons next to
File Open, `/api/export.csv` and `/api/export.xlsx`, downloading the
currently-loaded file's report.

[^stexpr]: Only five ST assignment SHAPES are measured (0/1/2 operators
    integer-dest, 1/5 operators REAL-dest), stored as an explicit sparse
    table. An ST assignment is NOT priced like the equivalent CPT -- that
    was the working hypothesis and it over-predicted by +132%. A
    1-operator assignment costs 40, which is an ADD's own weight, so Logix
    appears to compile a simple assignment to the single equivalent
    instruction and only reach for CPT-like evaluation on a compound
    expression. Shapes outside the table fall back to the CPT model AND
    are reported as a coverage gap rather than passing silently. See
    OQ-STEXPR.
