# Task List

Checkbox per phase from PROJECT_PLAN.md. ✅ done — 🟡 partially done — 🔴 open.
Anything non-obvious gets a footnote instead of inline prose — see bottom
of file. Full reasoning trails live in RESOLVED_QUESTIONS.md/
OPEN_QUESTIONS.md, not here.

## THE RANKED WORK QUEUE — ordered by measured impact on the sixteen

Measured 2026-09-18 against the current engine. This replaces the
open-questions book as the work queue; an item not on this list is not being
worked. Re-measure before reordering — every number below is reproducible
from the engine as it stands.

**Where the sixteen actually are:** mean |error| **1.5607%**, max **3.6309%**
(`superior`), 4 of 16 inside 1%, 11 of 16 inside 2%. Total residual
**+653,678 bytes on 47,539,368** = **+1.375%**. Nine files under-predict,
seven over-predict — the residual is **no longer one-sided**, so any
candidate that can only add bytes is wrong before it is tested.

**Category mass across the sixteen (predicted bytes):**

| category | bytes | share |
|---|---:|---:|
| `controller_tag` | 27,662,309 | 59.00% |
| `routine_logic` | 8,557,848 | 18.25% |
| `alarm_condition` | 4,488,720 | 9.57% |
| `udt_definition` | 3,072,275 | 6.55% |
| `module_io` | 1,408,235 | 3.00% |
| `program_tag` | 1,216,611 | 2.59% |
| `project_baseline` | 246,776 | 0.53% |
| `task_program_shell` | 232,916 | 0.50% |

### The order, and why

| # | item | measured basis for the rank | moves headline? |
|---:|---|---|---|
| 1 | **Verify the top instruction weights against real operand shapes** — **WORKED 2026-09-18, see `OQ-RUNGSHAPE`** | XIC/MOV/OTE/XIO are **160,469 of 255,027** real instruction occurrences (**63%**) and **every one of the top 25 is FITTED, none KNOWN**. A 4-byte error on those four alone is **1.35 percentage points** — the entire residual. Measured: the weights were fitted on **9.4%** branched rungs and **62%** single-instruction rungs, against **68.7%** and **7%** in real programs. Deliverable is the rung-shape sweep spec in `OQ-RUNGSHAPE`, awaiting approval to generate. | **yes, largest** |
| 2 | ~~**Controller tags**~~ — **WORKED 2026-09-18, CLOSED NEGATIVE, see `OQ-TAGSHAPE`** | 59% of all predicted mass, but every real tag shape is already covered and the untested ones (`Produced` 0.11%, `Consumed` 0.06%, 2-D arrays 0.16%) total ~8,700 bytes against a 653,678 residual. The name-length term, the strongest-looking candidate, is cleared by 88 clean rows at mean 0.1207%. **The residual is not in tag data space.** | **no** |
| 3 | **Gate on unreconciled clean captures** | The only real win of 2026-09-18 (0.10 pts) came from 54 rows already captured, already clean, never differenced. Recovers work already paid for. A sweep on 2026-09-18 found the remaining backlog is the 25-file batch already flagged (`cptnar_j3of6` −204,000, `cptnar_j3of4` −88,000, `cptnar_j5of6` −120,000, `cpttri_pow_adjacent` −48,000, `stc2_prem2_pow` −28,000, `srout_mixed`/`srout_same` +36,000 each) — no unflagged data is sitting unused. The gate is still needed so the next batch cannot repeat it. | **yes, as prevention** |
| 4 | **Rank open questions by real-bytes × uncertainty** | Directs 1–3 and retires the rest. This section is its first output. | indirect |
| 5 | **Confound linter before generation** — **BUILT 2026-09-18**, `scripts/confound_check.py` | Profiles every file in a family across 18 cost dimensions and fails when consecutive files move more than one. Exit code gates a generator. Caught `srout_oteuniq` moving instruction inventory and tag inventory together. Three false-clean blind spots found and fixed while building it — expressions inside a rung operand, ST bodies in `<Line>`, definition member order — each locked by a test in `tests/test_confound_check.py`. | indirect |
| 6 | **Exclude dead weight from default reports** — **DONE 2026-09-18** | `quick_eval` drops 1756-L7x / 1769 rows from the non-real reports by default (64 captured rows, including the corpus's worst sentinel at 65.69%); `--include-dead` restores them. Real rows are never filtered. | reporting only |
| 7 | **`quick_eval` reports the 16-file mean only** — **DONE 2026-09-18** | The real-set block now carries the stopping-rule verdict; corpus blocks are labelled leak-check, not accuracy. | reporting only |
| 8 | **Write the stopping rule down** — **DONE 2026-09-18** | In `CLAUDE.md` and enforced in code: `quick_eval` prints `STOPPING RULE ... MET / NOT MET` every run. Currently **NOT MET** — mean 1.5607%, max 3.6309%. | definition |
| 9 | **One capture roster, not five** | Scheduling. | none direct |
| 10 | ~~Refresh the strip ladders~~ | **DEAD** — see the read-only rule in `CLAUDE.md`. A derived variant of a real export does not build. | none |

### What has already been ruled out, so it is not re-tried

Each of these was tested against the sixteen on 2026-09-18 and failed. The
CV figure is the coefficient of variation of the implied per-unit cost
across the sixteen files; anything above ~0.3 is not identifying a value.

- **A constant error per instruction occurrence** — CV **1.74** over all
  255,027 occurrences, **1.72** over the top four, **1.73** per rung. The
  residual is not a uniform weight error, so no global logic scale.
- **Program-tag count as the carrier** — the single strongest correlate with
  residual *percentage* (r = **0.719**) and the best-scoring category scale
  (×1.399 → mean 1.238). Both are **spurious**: CV **4.14**, and `k3m16`
  carries +101,022 bytes of residual on **2** program tags, which is 50,511
  bytes each. It correlates because program-tag count and residual both grow
  with program size. `program_tag` × 1.399 also drives max **up** to 3.7668.
- **Any other single-category scale** — `alarm_condition`, `module_io`,
  `project_baseline`, `routine_logic`, `task_program_shell` and
  `udt_definition` each leave mean above 1.53 and max above 3.38.
- **Routine count** — r = 0.888 against residual *bytes*, retested with a
  measured constant rather than a fitted one: moves bias +1.375% → +0.957%
  and leaves the mean unchanged. Bias without spread is not a real term.

### The bimodal split, which is still unexplained

Ordered by residual per instruction occurrence, the sixteen fall into two
groups with **nothing between +0.31 and +2.65 bytes**:

- **High (8):** `emporium` 4.39, `cmu` 3.98, `superior` 5.61, `k3m16` 4.58,
  `eastperry` 4.49, `ipc_edgerline` 5.94, `accutally` 4.73, `mrfp_edger` 2.65
- **Low (8):** `horizon` 0.31, `griffin` −0.24, `elmsdale` −0.40,
  `murraybros` −1.49, `pukall` −0.80, `salamanca` −2.32,
  `flarefunction` −0.77, `emporiumedger` −2.60

**No single property separates them.** Tested and rejected as discriminators:
software revision, processor type, export year, safety class, and the counts
of controller tags, program tags, UDTs, AOIs, modules, programs, tasks,
routines, rungs, alarm conditions and ST routines — every one of them
overlaps between the groups. The groups do trend larger-to-smaller, but size
is not sufficient: `ipc_edgerline` (+3.52%) and `griffin` (−0.11%) are within
250 KB of each other.

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

## Capture roster, current as of 2026-09-12

Counted from `samples/manifest.csv` rather than carried forward, because the
previous entry said "149 pending files" and named six families when the real
number was already several times that.

- **678 committed files have no capture at all**, across 149 distinct sweep
  families. Biggest: `dscale_*` 39, `aoialgn_bc*` 36, `aoimix_*` 34, `udtmn_*`
  23, `modulesweep_*` 22, `cpttier_*` 22, `aoialgn_un_*` 21, `stx_ops_*` 20,
  `asmclose_*` 17, `platform_plateql_*` 15.
- **226 of those were built on 2026-09-12** and every one answers a question
  that is open right now: `aoialgn_*` 71 (AOI instance-array alignment
  closeout), `aoimix_*` 34, `ntag_*` 25 (zero-operand instruction density),
  `identnamelen_*` 24, `cpttier_*` 22, `aoishape_*` 17 (which AOI rung shape
  Studio rejects), `cmpfl_*` 13, `cptpow_*` 12, `v3abl_*` 8 (which v3 subsystem
  errors).
- **79 manifest rows point at a file that no longer exists.** Their
  `actual_bytes` cannot be checked against anything and must not be used; 25 of
  those rows also carry build errors. `scripts/capture_errors.py` lists them.

**Priority order for the next capture run**, given OQ-REALUNDER now dominates:

1. `aoishape_*` (17) — identifies the rung shape that corrupted
   OQ-AOIINTERNALLOGIC's calibration. That calibration is a leading candidate
   for the real-file under-prediction, so this gates a real fix.
2. `v3abl_*` (8) — identifies the v3 template defect, which taints
   OQ-COMPOSITESCALE's surcharge re-derivation.
3. ~~`modmarg_*` (9+) — discriminates per-rack from per-project for the module
   repeat discount, the one measured-but-unapplied constant.~~ **Done
   2026-09-13 (segment 14).** The mixtures settled per-catalog-vs-per-file, the
   discount is wired for ten catalogs, and per-rack-vs-per-project was measured
   to be byte-identical on all sixteen real programs. Still needed from this
   family: an **EN2T-only count sweep** (n=1/2/4/8, every copy under `Local`, no
   downstream child) to split 1756-EN2T from rack-aliased 1756-OB32, and a
   recapture of the six `modmarg_drvaxis_*` rows, all of which carry build
   errors.
4. `aoialgn_*` (71) and the rest.

Recapture, separately from the above: the 5 stale `aoi_logic_scale_*` /
`aoi_multiroutine_*` rows, and the ~130 errored rows that carry no error text
(every one captured before the error-log reader started working 2026-09-10).

### Added 2026-09-13 (capture-batch segment 4)

- **`aoidshape_*` (54 files), OQ-AOIDEFSHAPE — highest priority of the
  uncaptured batches.** The itemised AOI-definition re-derivation is worth 217
  more corpus rows inside ±8 and made five AOI categories exact, and it leaves
  exactly one 8-byte term confounded three ways. These 54 files break that
  confound and nothing else can: group A (25) reads the type-name bucket at
  every length 8-32 with the controller name pinned, group B (16) reads the
  name-pool residue twice around, group C (8) separates a per-member step from
  the pool offset, group D (5) isolates member order. All def-only, all
  1756-L81E at v35.
- Segments 1-4 of `docs/SEGMENT_TRACKER.md` are closed; segment 5 (`addit_*`,
  33 files, OQ-COMPOSITESCALE) is next.

### Added 2026-09-13 (capture-batch segment 5)

- **`srout_*` (16 files), OQ-SERIESOUTPUT.** Two captured shapes agree exactly
  that a series output cascade over-charges 12 per output beyond the first, and
  applying it takes the sixteen real programs from 2.07% to 2.90% with every one
  worse. These 16 files say which of four candidates explains the split — count
  shape, identical-rung repetition, series vs parallel, or repeated vs distinct
  instruction types. Until they land, nothing here gets fitted.
- **`udtslot_*` (52 files), OQ-UDTTAGSLOT.** The wired 8-byte UDT tag slot rests
  on two UDT sizes, 9 and 40, fitting two constants. Group A covers every residue
  mod 8 at two tag counts, group B says whether the step is at 8 and not 4, group
  C is the first array arm that can see an element rule at two residues.
- Segment 5 of `docs/SEGMENT_TRACKER.md` is closed; segment 6 (`stx_*`, 30 files,
  OQ-STEXPR) is next.

### Added 2026-09-13 (capture-batch segment 6)

- **`stc_*` (21 files), OQ-STEXPR.** The ST assignment law's four remaining
  assumptions: the operator premium at one operator and on the REAL row, `**` and
  `OR` in ST, the conversion rate for SINT/INT/LINT sources, and group E's
  separation of the +264 one-time from anything per-call — which no file in
  EITHER language currently does.
- **Verify a claimed corpus figure before sizing a batch from it.** Segment 6's
  call-statement arm was sized on "2,094 real ST call statements"; the real number
  is 68 AOI calls, and 690 of the 758 bare call statements were already priced. A
  five-minute count would have caught it. Applies to every generator docstring
  that quotes a real-corpus figure without naming the script that produced it.
- Segment 6 of `docs/SEGMENT_TRACKER.md` is closed; segment 7 (`genem_*`, 27
  files, OQ-MODULESTRUCTURAL) is next.

### Added 2026-09-13 (capture-batch segment 7)

- **Recapture 6 rebuilt `genem_*` files.** `genem_dtsint_{008,064,450}` (never
  converted -- CommMethod said INT, declared type said SINT),
  `genem_dtdint_064` / `genem_dtreal_064` (imported but Studio built them as INT
  connections, so their captures were voided), and `genem_noconn` (built with the
  connected CommMethod instead of 536870932, capture voided). All six now carry
  the real per-type CommMethod.
- **A file that converts cleanly is not evidence that its shape is right.**
  `genem_dtdint_064` and `genem_dtreal_064` converted, captured, and agreed with
  each other -- because Studio silently resolved a contradiction between
  CommMethod and the declared element type and built all three as the same
  connection. Two arms of a four-arm batch measured nothing. Check that a
  transplanted block's discriminant fields actually vary with the variable under
  test, not just that the file imports.
- Segment 7 of `docs/SEGMENT_TRACKER.md` is closed for ETHERNET-MODULE; segment 8
  (`ntag_*`, 25 files, OQ-VERIFINSTR) is next.

### Added 2026-09-13 (OQ-REALUNDER category differencing, task #128)

- **CAPTURE THE 24 STRIP-LADDER FILES.** `samples/local/stripped/` now holds an
  8-rung ladder for each of `superior` (+0.174 residual/logic), `ipc_edgerline`
  (+0.224) and `griffin_stackerline` (+0.006, the control). Gitignored by design.
  **L2 (minus all rung and ST content) is the decisive rung** -- L0 minus L2 says
  whether the missing bytes are in compiled ladder. This is the highest-value
  capture outstanding: it is the only instrument that measures a category's cost
  inside real content, and nothing in `samples/generated/` can substitute for it.
  Expect some rungs to be refused on import; the fix for a refused rung is to
  make that one by hand in Logix Designer (delete the category, re-export), which
  differences identically.
- Task #128 is DONE as an analysis: no single per-unit cost fits (every feature's
  ratio has cv >= 0.66), the residual is concentrated in `routine_logic`, and
  `residual / routine_logic_bytes` is bimodal with five files at ~0 and eleven at
  +0.086..+0.224. A global logic scale-up is ruled out by the 578 `logic_instr`
  rows. Full reasoning in OQ-REALUNDER.

### Added 2026-09-14 (strip ladder captured, task #128 closed for real)

**TWO LADDERS CAPTURED, `elmsdale` (5069-L330ERM v35) and `griffin`
(1756-L81E v35), seven rungs each.** Full reasoning and the step table are in
OQ-REALUNDER. Headline: **compiled ladder is OVER-charged on both files**, so
the five-segment hypothesis that the real-file deficit lives in `routine_logic`
is dead and must not be refit. The remaining error is in tag-based alarms, the
controller shell, modules, and UDT/AOI definitions.

Nothing is being wired from two data points. In priority order, what the ladder
says to do next:

1. ~~Alarm associated-tag audit (OQ-ALARMCONDREAL).~~ **DONE 2026-09-14, and it
   ruled itself out.** Both programs use the identical `Alarms_SE` UDT at
   `Dimensions=200` with the identical three members referenced; all 37
   `AlarmCondition` attributes are identically distributed apart from names,
   which are proven free. The only structural difference left standing is
   **conditions per associated array element** — Elmsdale 1:1, Griffin 2:1 —
   and `base + flat-per-condition` provably cannot fit both files (the solve
   gives a non-integer 1000.44 per condition). **What is now needed is 4–6
   files sweeping conditions-per-array-element and array size with condition
   count held fixed, plus re-submitting the four never-captured
   `alarmcond_type_{trip,trip_high,trip_low,deviation}` rows** — condition type
   is assumed free and has never actually been measured, and every real
   condition is `TRIP`. SPEC ONLY until asked.
2. **Three generated files: the controller-shell probe (OQ-CTLSHELL).**
   1756-L81E v35 empty, plus one with a real `EthernetPorts`/`Bus` block and one
   with `Trends`/`DataLogs`/`QuickWatchLists` populated. Worth 0.2–0.6% of real
   error across all sixteen files and it is the cheapest item on the board.
   SPEC ONLY until asked — CLAUDE.md step 7.
3. ~~Capture `Elmsdale_NoProgramLogic.L5X`.~~ **DONE 2026-09-14: 760,800
   against 722,288 predicted.** The split says program shells and program tags
   are not the problem — the sub-step carrying all 9 shells and all 63 program
   tags lands **−156 on 26,812**. All −29,520 of the over-charge is in the 56
   machine-logic routines, at +20.5% per rung, while the 3 alarm/message
   routines in the same program price at +0.8%. Content-dependent, so no global
   multiplier can fix it.

   **The instrument that follows from this is a PER-PROGRAM strip of Elmsdale,
   not another category ladder.** Nine programs, nine equations, nine different
   real logic mixes, and the engine's per-routine predicted bytes are already
   known for all 59 routines. Same export, cut a different way, nothing
   generated. Roster (strip one program's routines at a time, keep everything
   else): `TiltHoist` (21 routines), `TiltHoist_Infeed` (10), `Housekeeping`
   (5), `TiltHoist_Outfeed` (5), `Inputs` (4), `Outputs` (4), `InfeedData` (4),
   `PlanerInterface` (3). `AlarmsAndMessages` is already measured by sub-step B.
   Eight files, and the four smallest alone would test whether the over-charge
   tracks JSR/SBR content.
4. **A third ladder, on a program that OVER-predicts.** Both captured ladders
   disagree in sign on three of seven categories. `emporiumedger_20250905r1`
   (−2.077%) or `salamanca_20250425r00` (−1.475%) would say which of the two
   patterns is typical. Do not fit any category constant until a third arm
   exists.

Retired by the ladder, do not spend on these:
- **Axis is exact on Griffin** — 0 bytes of error over 37 axis tags and 778,728
  bytes, the largest single category in that file. The "axis is ~650 KB of
  unwired real exposure" line in OQ-REALUNDER's candidate list is obsolete.
- **A global `routine_logic` scale-up.** Ruled out twice now: by the 578
  `logic_instr` rows, and now by direct measurement in both directions.
- **The empty-project baseline constant.** It is byte-exact on every generated
  empty file; the real-shell gap is unpriced content, not a wrong constant.

### Added 2026-09-18 (the in-depth open-questions review, second pass)

The 2026-09-17 pass was triage: every entry recomputed and given a status. This
one went through the ones it left open, one at a time, re-derived each question's
numbers from the captures on disk rather than from what the entry claimed, and
either wired the result or said in counted terms why not.

**Real set 1.6894% -> 1.6566% mean absolute error, all sixteen the right way.**
Two corpus families rebuilt: Structured Text **8.3291% -> 0.0091%** (60 of 69
byte-exact) and `unweighted_*` **4.6865% -> 0.1574%**.

**SEVEN CONSTANTS WIRED**, all measured, derivations in MEMORY_MODEL.md's
changelog: the JSR multi-operand step (4, keyed on total operands, not inputs),
`jsr_target_declaration.per_target` 152 -> 160, 112 per target whose SBR/RET
carry operands, `DTR = 40`, ST's own operator classification, ST per-source
conversion rates, and the CPT leading-tier-1-run arrangement term.

**THREE BLOCKERS DISSOLVED, each by questioning the entry rather than the data.**
OQ-STEXPR-OPERATOR's "two unknowns from two points" was a misreading of the law's
own shape -- it already has two regimes, so each point pins a constant alone.
OQ-JSRPARAMCOST's "non-linear" non-atomic surcharge was linear all along and had
been measured against the wrong baseline. OQ-VERIFINSTR's DTR had no weight at
all, not the 16 the entry said was wired.

**TWO PARSER DEFECTS, both right-answer-wrong-reason.** `_DESTINATION_ARG` gave
COP/CPS/FLL/BSL/BSR a destination position of -1, which inspects the LENGTH
operand and only charged correctly because a literal length does not resolve to
BOOL. `_NUMBER` in the ST sizer matched digits inside identifiers, so `R0 * R1`
counted five integer literals -- harmless until the operator premium keyed on it.

**ONE NORMALISATION that had to be found before anything could be read:** a
per-file -352 runs through all 58 captured `cpt` rows from `gen_cpt_closeout.py`
except the five whose logic references a LINT tag. With it subtracted every
residual in the batch is an exact multiple of 4 bytes per rung. Without it the
batch looks like noise, and several conclusions had been contaminated by a
spurious 352 from differencing against an older generator.

**NEXT, in priority order, and none of it is generated -- SPEC ONLY:**
1. `sroutc_c{1,2,4}_k{1,2,4,8}` (12 files, already built, awaiting capture) --
   the decisive measurement for the whole project. `addit_*` is now the THIRD
   independent family confirming -12 per extra output, and all sixteen real
   programs still reject it.
2. A 1..6 float-literal sweep at an integer CPT destination. +120 to +188 per
   rung, charged nothing, the largest unpriced CPT term in the project.
3. Two POINT I/O files on ONE adapter catalog (Enhanced and Optimized, 8 cards
   each). Separates format from adapter and makes the 34 unclassifiable real
   cards classifiable. -1,136 per card would take Elmsdale from +22,862 to +142.
4. Three files for the -352: the same rung shape with no LINT tags, with one,
   and with four of which one is referenced.
5. Three n=5 REAL-dest CPT discriminators: all-REAL parenthesised, all-REAL with
   one float literal, mixed-operand unparenthesised.

**Doc currency:** seven stale `**CAPTURE ERRORS**` blocks retired (the gate only
checks questions it routes rows TO, so a block whose rows were recaptured is
invisible to it and survives as a false warning) and two stale in-entry claims
corrected.

### Added 2026-09-17 (212-row batch reviewed; four families closed, two blocked)

Gates first: step 2 clean (3,442 ok / 3 FAILED / 9 never submitted); step 2b now
passes after two stale counts were corrected -- OQ-AXISMARGINAL 51 -> 57 and
OQ-MODULEMARGINAL 0 -> 6.

**CLOSED AND WIRED** -- EVENT instruction (56/rung), 1756-EN2T (432), the six
2198 -ERS3 per-catalog costs (flat per copy, no discount), and Task name cost
(step with a minimum of 8). Full derivations in MEMORY_MODEL.md's changelog.

**NEWLY DIAGNOSED, not fixed: every generated Kinetix file declares a shared DC
bus with no converter.** Studio's own text, available for the first time:
"Primary Bus Sharing Group N contains a module configured as Shared DC or Shared
DC/DC with no module configured as Shared AC/DC". Bus sharing lives in the
module ConfigData blob and is a per-PROJECT property, but payloads are stored
per-CATALOG, so mixing donors across real exports cannot produce a coherent bus.
Full diagnosis, the located-but-undecoded indices, and the standalone-donor fix
are in OQ-MODULEMARGINAL. This is a decision about file shape, not a cleanup.

**BLOCKED ON A MISSING MIDPOINT, deliberately not fitted (OQ-STEXPR-OPERATOR).**
The 21 `stc_*` rows measure real ST costs -- bitwise operators +84 at one
operand, `**` −168 at four, REAL destinations −64/−288, type conversion
+88/+112/−96/+44 -- but every operator has exactly two points and needs two
parameters. Six 2-operator files would over-determine it. SPEC ONLY.

**Still open from this batch:** `asmclose_2198_d012_ers3_n08` needs recapture
(reads 52,240 where D012's own three linear points give 48,232), and the 8
`axmarg_*` / 6 `modmarg_drvaxis_*` rows cannot be used until the bus-sharing
shape is settled.

### Added 2026-09-14 (Kinetix guards made catalog-aware; 163 stale files found)

The channel guard that was supposed to prevent the axmarg failure **existed and
did not fire**, because it was written from three D-series exports and
generalised into one global {Ch1, Ch3} set. It passed S086-on-Ch3 (the shape
Studio rejects) and would have flagged the one real Ch2 in the corpus. Replaced
with a per-catalog table (`DRIVE_CHANNELS` in `sample_gen/data/kinetix.py`) plus
six regression tests asserting both directions.

**Found while re-linting: 163 of the 310 generated files containing a 2198
module still fail lint, and none of it is new.** Breakdown by family:
`composite_realistic_v4` 74, `composite_realistic_v3` 50, `v3abl_*` 8, plus
scattered others. The findings are `chassis_size_mismatch` (136),
`module_configdata_size_mismatch` (135) and `module_identity_mismatch` (76) --
e.g. `composite_realistic_v4_005` carries ProductCode 11 (D012's) on a
2198-D020-ERS3. These families were generated before the 2026-09-13 identity fix
and were never regenerated, so they still carry the original defect.

Zero `drive_axis_unreal_channel` and zero `drive_axis_too_many` findings anywhere,
so the new rule does not false-positive and the 32-file batch is clean.

Not regenerated here: `v3abl_*` is the BLOCKED segment-24 family and
`composite_realistic_v3/v4` carry captured rows whose predictions would move.
Both need a decision before they are rebuilt.

### Added 2026-09-14 (per-program strip: the two batches disagree)

**STOP WIRING ANYTHING FROM ELMSDALE.** The nine per-program variants and the
Trials category ladder cannot both be true; they differ by 18,000–25,000 bytes.
A single wrong full-file baseline (captured 1,147,896 against an implied
~1,129,868) explains the per-program batch AND the alarm-per-condition anomaly
at once, but does not reconcile the `NoProgramLogic` / `NoLogic` rungs. Full
reasoning and the settling measurement in OQ-LADDERBASE.

**Next capture is three files in one session, back to back:** the unmodified
`Elmsdale_20251017r01` export, `Elmsdale_NoAlarms`, and any one per-program
variant. Nothing generated, nothing new to build.

Also fixed en route: the archive's `Elmsdale_20251017r01.L5X` is mislabelled —
it is the `NoOutputs` variant (8 programs, `Outputs` missing). The true full
export was not in the batch, which is part of how the baseline went unchecked.

### Added 2026-09-13 (capture-batch segment 8)

- Nothing to build. Segment 8 needed no engine change and no new files: the four
  zero-operand weights are confirmed exact at five counts each, and the paired
  shape's five rows did more for OQ-SERIESOUTPUT than a new batch would have.
- **`srout_oteuniq_k{02,04,08}_n00200` (group B of the already-built
  `srout_*` batch) is now redundant.** Its purpose was to test whether the
  −12-per-extra-output discount needs identical repeated rungs;
  `ntag_uidpair_n00001` is a one-rung file that pays the full −12, which answers
  it without capture. Deprioritise those 3 in the capture roster.

### Added 2026-09-13 (capture-batch segments 10 and 11)

- **A UDT member-count sweep with NO BOOL members** is the one thing
  OQ-UDTMEMBERNAME still needs, and the corpus has exactly one such point
  (`udtmn_dint_len*_n04`). With the name-length law wired, every family collapses
  to a per-shape constant that `−(4m − 8r + 16)` fits five of seven times --
  three constants on five points, in the one family where declared member count
  and hidden backing SINTs cannot be separated. Not fitted; spec only, per the
  step-7 rule.
- Segments 9, 13, 16, 30 and 31 are DEFERRED to the end of the tracker: each has
  errored capture rows, and an errored row is suspect rather than wrong, so they
  are worked once the clean ones are done.

### Added 2026-09-13 (capture-batch segment 12, reviewed with 18 and 19)

- **`**` ADJACENCY is an unmodelled term worth 40 bytes/rung**, and it blocks any
  uniform tier-3 rate: `cptpow_p2` −16, `cptpow_p3` −12, `cptpow_p2_adjacent`
  **+24**, same operator count. Needs a sweep varying adjacency at fixed `**`
  count, with the rest of the expression held identical -- spec only, per the
  step-7 rule.
- **`cmpfl_*` cannot close on what exists.** All 13 rows are single-rung files, so
  every one is a point with no slope, and 13 isolated points cannot separate
  operand type from operator tier from literal count. Any future float-literal
  batch must sweep RUNG COUNT at each shape so a slope exists.
- Segments 18 and 19 are marked reviewed-with-12 in the tracker rather than
  pending: their data was read in full, it just does not close.



## Conversion status audit, 2026-09-14 (CLAUDE.md step 2)

Step 2 had never been run as a cross-reference because it had no tool.
`scripts/conversion_status.py` is that tool now. Of 3,498 committed generated
L5X files: **3,277 last recorded `ok`, 55 last recorded FAILED, 166 have no
`convert_log` record at all.**

`convert_log`'s `message` column only ever says *"The Import was cancelled due to
errors ... See error log"*, so it carries no per-file diagnosis. Lint has grown
enough since these ran that it now names the cause for 30 of the 55.

### The 55 that failed

| n | family | lint diagnosis | disposition |
|---:|---|---|---|
| 12 | `modulesweep_*` | `chassis_size_mismatch`, `non_standard_processor` | **OPEN — discard candidate** |
| 10 | `modulesweep_*` | `kinetix_drive_without_bus_supply`, `non_standard_processor` | **OPEN — discard candidate** |
| 6 | `modulesweep_*` | `non_standard_processor` | **OPEN — discard candidate** |
| 2 | `modulerack_bender_full_program*` | `kinetix_axis_without_converter` | **OPEN — fixable, generator not yet touched** |
| 9 | `predefprobe_*` | lint clean | **OPEN — needs the Studio error log** |
| 5 | `identnamelen_task_c*` | lint clean | OPEN — flagged in OQ-IDENTNAMELEN |
| 5 | `platform_plateql330_*` | lint clean | OPEN — flagged in OQ-REAL5069 |
| 3 | `genem_dtsint_*` | lint clean | **OPEN — needs the Studio error log** |
| 3 | `uwclose_*` | lint clean | OPEN — segment 29, never captured |

The 28 `modulesweep_*` are the discard candidates because
`gen_assumed_closeout`'s own docstring documents that generator as known-bad --
hardcoded module XML missing `<ExtendedProperties>`, plus a corrupted ConfigData
payload at 119 L5K values against the real 118 -- and says the `asmclose_*` sweep
supersedes it with clean captures. 26 of the 28 hold no data at all. **Not
deleted: discarding removes the record that those catalogs were attempted, and
that is a call for the project owner, not a cleanup.**

### Fixed on the spot

`modulesweep_1734_ob8s_a` and `_b` had a FAILED *last* status while still
carrying `actual_bytes` -- a capture taken from an earlier version of the file.
A later failure supersedes an earlier success exactly as a later success
supersedes an earlier failure, and that rule had only ever been applied in one
direction. Both cleared for recapture.

### The 166 with no record

`aoidshape` 54, `udtslot` 52, `stc` 21, `srout` 16, `closeout` 11,
`composite` 9, `aoierr` 3 -- almost all generated after the last conversion run,
so never submitted rather than defective. The 9 `composite` are the existing
"9 never-converted composite_realistic_r2" item.

### Resolved 2026-09-14: 44 discarded, 11 kept and re-stamped

The 55 never-converted files were triaged against the rule that a feature absent
from `samples/local/` waits. **44 discarded and scrapped from the record** (files
deleted, manifest rows dropped, 3,593 rows -> 3,549):

| n | family | why |
|---:|---|---|
| 28 | `modulesweep_*` | Known-bad generator superseded by `asmclose_*`, and they are 1756-L81ES / 5069 safety variants -- outside what this project needs to predict. |
| 6 | `predefprobe_*` | **Zero occurrences in all sixteen real programs**: OPCUA, AXIS_CONSUMED, AXIS_GENERIC_DRIVE, AXIS_SERVO, AXIS_SERVO_DRIVE, COORDINATE_SYSTEM. |
| 5 | `platform_plateql330_*` | Segment 17 already reached its conclusion on two processors with byte-identical residuals at all five densities. A third adds nothing. |
| 3 | `genem_dtsint_*` | Segment 7's connection law is wired and exact on 24 rows; these were the arms that turned out invalid. |
| 2 | `modulerack_bender_full_program*` | 1756-L81ES safety, same reason as the sweeps. |

**11 kept, with `ExportDate` / `ProjectCreationDate` / `LastModifiedDate` bumped
so the conversion tooling re-picks them up.** Each earns its place on real usage:

| n | files | real-file basis |
|---:|---|---|
| 5 | `identnamelen_task_c{04,08,16,32,40}` | The third arm of the name law. Programs and routines closed 2026-09-14; whether a Task's name follows the same step is the only part left. |
| 3 | `uwclose_event_n{00010,00100,01000}` | `EVENT` appears in **4 of 16** real programs. |
| 3 | `predefprobe_{ref_to_axis_cip_drive,ref_to_axis_virtual,timer_t}` | AXIS_CIP_DRIVE in 5 of 16, AXIS_VIRTUAL in 3 of 16, TIMER instructions in 6 of 16. |

All 11 are lint-clean, so they need the raw Studio error-log line — which is what
the re-stamp is for.

### Tooling gap worth closing

The conversion harness should capture the real Studio error-log line per file,
the way the memory-capture harness now does. Without it, 25 of these 55 cannot
be diagnosed at all -- the same blocker as the AOI calibration files.
