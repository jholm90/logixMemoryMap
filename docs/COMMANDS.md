# Command Reference

Every command used on this project. Three groups: the analyzer itself, the
capture pipeline (Windows, with Studio 5000), and the analysis and generation
scripts.

---

## 1. The analyzer

Run from `src/`, no install needed:

```bash
cd src
python -m l5x_memory_analyzer.cli ui    path/to/file.L5X   # treemap, file loaded
python -m l5x_memory_analyzer.cli ui                       # treemap, file picker
python -m l5x_memory_analyzer.cli size  path/to/file.L5X   # flat byte breakdown
python -m l5x_memory_analyzer.cli dump  path/to/file.L5X   # raw parsed XML
```

`ui` options: `--host` (default `127.0.0.1`), `--port` (default `8765`),
`--no-browser`.

After `pip install -e .` the same subcommands work as `l5x-memory-analyzer`
from anywhere:

```bash
l5x-memory-analyzer ui path/to/file.L5X --port 9000 --no-browser
```

## 2. Tests

```bash
python -m pytest -q
```

`pyproject.toml` sets `pythonpath = ["src"]` and `testpaths = ["tests"]`, so bare
`pytest` works from the repo root once dev extras are installed
(`pip install -e ".[dev]"`).

---

## 3. Capture pipeline

Run on the Windows machine with Studio 5000. Full procedure in
`TESTING_PLAN.md`. Three pieces, in order.

### Before handing over files: `check_proven_blocks.py`

```powershell
python scripts/check_proven_blocks.py samples/generated/modules/<file>.L5X
```

Every 2198 module and AXIS_CIP_DRIVE block in the file must match a block from a
capture with zero build errors, with names, addresses, MotionModule and AxisID
normalised. Non-zero exit on any unproven block. `tests/test_build_guards.py` runs it
over every file waiting for capture.

### 3a. Convert L5X to ACD

`scripts/batch_l5x_to_acd.ps1` wraps Rockwell's `l5xgit` CLI. **The l5xgit source
is vendored in `tools/ra-logix-designer-vcs-custom-tools`** (MIT, pinned commit in
`tools/README.md`) and built on first use by `scripts/build_l5xgit.ps1`, so no
separate checkout of the Rockwell repository is needed. Resumable, with
content-hash staleness tracking — safe to re-run against the same output directory
any time.

```powershell
# From the repository root. l5xgit is built from tools/ on first use.
.\scripts\batch_l5x_to_acd.ps1 -InputDir .\samples\generated -OutputDir C:\l5x_scratch\acd

# Build l5xgit on its own, or rebuild after updating the vendored source:
.\scripts\build_l5xgit.ps1
.\scripts\build_l5xgit.ps1 -Force
```

Parameters: `-InputDir` and `-OutputDir` (both required), `-L5xGitPath` (optional;
omit it to use the vendored build), `-UnsafeSkipDependencyCheck`, `-AdoptExisting`.

Machine prerequisites that cannot be vendored: the .NET 10 SDK, and Studio 5000
Logix Designer with the Logix Designer SDK 2.2+, whose local NuGet folder supplies
the proprietary `RockwellAutomation.LogixDesigner.CSClient` package the build needs.

Pushes `convert_log.csv` when it finishes.

> **Conversion success does not mean the program compiles.** The SDK only opens
> and parses the project. It performs no ladder verification, so a file with a
> missing array subscript converts cleanly and never builds at scale. That is what
> `src/sample_gen/lint.py` is for.

### 3b. AHK companion

`scripts/logix_build_capture.ahk` **must already be running before step 3c.** It
drives Studio's File > Open inside the same already-running instance — about 5
seconds per file against about 65 for a full close and reopen.

| key | action |
|---|---|
| `Ctrl+F1` | start the capture loop |
| `Esc` | abort |
| `F9` | debug helper — dump control text on the active window |

### 3c. Capture memory readings

`scripts/batch_memory_capture.ps1` consumes `convert_log.csv` from 3a. Fully
unattended, safe to leave running overnight.

```powershell
# Smoke test the first 10 files before committing to a full run:
./batch_memory_capture.ps1 -ConvertLog C:\l5x_scratch\acd\convert_log.csv -Limit 10

# Full run:
./batch_memory_capture.ps1 -ConvertLog C:\l5x_scratch\acd\convert_log.csv
```

Parameters: `-ConvertLog` (required), `-ManifestPath`, `-HandoffPath`,
`-OpenRequestPath`, `-TimeoutSeconds` (default 1200), `-Limit`.

**Controller model and firmware are not parameters.** They are read from each
L5X's own `Controller/@ProcessorType` and
`RSLogix5000Content/@SoftwareRevision`. A file whose head cannot be parsed records
`UNKNOWN` with a `PROCTYPE-UNREAD` note rather than a guess.

> They used to be mandatory switches, and whatever was typed on the command line
> was stamped onto every row regardless of what the file declared — 1,926 of 1,959
> captured rows ended up carrying a processor that contradicted their own XML.
> **Never ask for a value the file already states.**

Writes `samples/captures.csv` and pushes it when finished. Window-title-mismatch
and zero-capacity rows are detected and retried automatically on the next run.

> **Known gap:** 1769-series processors need the Estimate button clicked before
> Controller Properties shows a capacity figure. The AHK loop does not do this, so
> those rows need manual reporting. 1769 is dead architecture, so this is not
> being fixed.

---

## 4. Analysis scripts

### `confidence_census.py` — what the UI actually claims to know

```
python scripts/confidence_census.py samples/local/<file>.L5X
python scripts/confidence_census.py --summary samples/local/*.L5X   # one line per file
```

`--summary` prints the file-level figure the Errors tab shows, and its band split,
without expanding every element — seconds per file rather than minutes.

Expands every element the tree can reach and buckets it by the confidence the UI
shows, driving the real load path and mirroring the client's own `nodeConfidence`
walk rather than forming a second opinion about it.

Counts elements and bytes separately, because they disagree sharply: a file is
mostly tiny exact leaves by count and a few large aggregates by byte. Only leaves
are summed for the byte view, so a parent and its children are not both counted.

Use it to answer "does this look like guessing?" with a number instead of an
impression, and to find which groups carry the real uncertainty.

### `quick_eval.py` — the accuracy check

`--real-only` evaluates the real production exports and nothing else — no generated
sentinels — and names any recorded real program that is not present. Real exports
are found by file name anywhere under `samples/local/`; a renamed export is mapped
in the gitignored `samples/local/aliases.csv` (`recorded_name.L5X,actual_name.L5X`).

**The default instrument.** Evaluates the family under test, all seventeen real
programs, and one sentinel per category to catch a change that leaked further
than intended. Prints `STOPPING RULE ... MET / NOT MET` every run.

```bash
python scripts/quick_eval.py --family '<regex>'
python scripts/quick_eval.py --full          # every manifest row
python scripts/quick_eval.py --real-only     # the real programs and nothing generated
```

Use `--full` for exactly two things: reconciling a newly landed capture batch,
and the single final check before a constant is committed. **Not for iterating** —
a full recompute re-parses thousands of rows and takes minutes where a scoped one
takes seconds.

Other flags: `--worst N`, `--lenient`, `--include-dead` (1756-L7x and 1769 rows,
excluded by default as dead architecture).

### `capture_errors.py` — the error gate

Routes every capture that errored to the open question that asked for the test,
and fails if any of them has nowhere to be recorded.

```bash
python scripts/capture_errors.py          # the gate
python scripts/capture_errors.py --list   # every offending sample_id
```

Two classes are routed:

- Rows with `error_count > 0`. The L5X imported and built, but Studio reported
  errors, so **`actual_bytes` is SUSPECT rather than wrong** — part of the file
  may never have reached the controller, which shows up as the model apparently
  over-predicting.
- Committed generated files that were attempted and never reached `ok`.

**A file with no conversion-log row at all is not a failure** — it has simply
never been submitted, which is the normal state of a batch built today.

Ownership comes from the `OQ-` identifier in the sample's own manifest
description, so **every generator must name its question there**.
`samples/oq_owners.csv` covers the two cases a description cannot: a legacy family
whose generator no longer exists, and a closed question handing its errored rows
to its successor. An explicit entry wins over the description.

The gate requires a `**CAPTURE ERRORS: <n> row(s)**` line in each owning
question's entry, with `<n>` matching the live count. **Exit 1 on a missing line,
a stale count, or an unowned row** — the count cannot drift without failing the
check, which is the whole point.

> This exists because it already failed once: a 31-file family sat unexamined at
> +10.5% because every file carried errors, no error text was recorded, and
> nothing tied that fact to the question the files were built to answer.

### `unreconciled.py` — captured rows nobody acted on

Recomputes every captured row against the **current** engine and groups the ones
outside a tolerance by sweep family.

```bash
python scripts/unreconciled.py
python scripts/unreconciled.py --threshold 64 --csv out.csv
```

A stored delta cannot answer this — it goes stale the moment any constant moves,
which is exactly how a clean, exact, answered measurement hides in plain sight.
**A family with many rows, one sign, and a median far from zero is an unreconciled
measurement, not noise.**

### `confound_check.py` — does this family isolate one variable?

Profiles a family across 18 dimensions and fails when consecutive files move more
than one.

```bash
python scripts/confound_check.py --family '^litop_type_sint'
```

**Scope it to one arm.** A whole-family run walks files alphabetically and crosses
arm boundaries, which legitimately varies several dimensions.

> This script exists because generated shapes have repeatedly turned out not to be
> the shape they claimed, and it has since found six blind spots in itself —
> expressions inside rung operands, ST bodies, definition member order, rung
> structure, tag declaration order, and mixed-case AOI call sites. A file that
> converts cleanly is not evidence the shape is right.

### `derive_instruction_accuracy.py` — measured per-instruction accuracy

Finds every captured file where one instruction is the variable under test and
records how far the engine actually landed from the controller's reading. Writes
the table into `memory_model.yaml`.

```bash
python scripts/derive_instruction_accuracy.py
python scripts/derive_instruction_accuracy.py --write
```

**Isolation files are identified by what they CONTAIN, never by name.** Two
filename whitelists were tried and both silently dropped real evidence. Naming
conventions drift; rung text does not.

### Others

| script | purpose |
|---|---|
| `accuracy_report.py` | full corpus accuracy report and the shared capture-validity rule |
| `predict_batch.py` | whole-file predictions — the only figure comparable to a controller capacity reading |
| `audit_confidence.py` | confidence-tier audit across the model |
| `coverage_audit.py` | instruction and feature coverage against real usage |
| `conversion_status.py` | cross-reference committed files against the conversion log |
| `extract_module_data.py`, `extract_kinetix_data.py` | pull real module shapes out of the corpus |
| `l5x_validator/` | schema validation helpers |
| `LaunchUI.pyw` | double-click launcher for the UI, no console window |

> **`strip_ladder.py` is deleted.** Deriving variants of a real export by
> rewriting its XML is forbidden — see the read-only rule in `CLAUDE.md`. Its
> history is in git. Do not revive it, reimplement it with a different XML library,
> or work around it with text-level surgery.

---

## 5. Sample generators

### Parameterised CLI

Run from `src/`. Each subcommand writes an L5X to
`samples/generated/<category>/` and a `samples/manifest.csv` row with
`predicted_bytes` filled in by the sizing engine.

```bash
# A UDT plus one tag of that type
python -m sample_gen.cli udt --name MotorStatus \
    --member Running:BOOL --member Speed:DINT --member Faulted:BOOL \
    --out motorstatus_test

# N tags of a given type and dimensions
python -m sample_gen.cli tags --type DINT --dims 10000 --out dint_10k_array

# N rungs of a given instruction pattern
python -m sample_gen.cli rungs --count 1000 \
    --instr "XIC(In{i})OTE(Out{i});" \
    --decl-tag "In{i}:BOOL" --decl-tag "Out{i}:BOOL" \
    --comment-len 100 --out xic_ote_1000_comment100
```

Flags (`--help` on each shows all):

| subcommand | flags |
|---|---|
| `udt` | `--name --member --member-desc-len --type-desc-len --tag-desc-len --tag-dims --instances --out` |
| `tags` | `--type --dims --count --desc-len --name-prefix --name-len --out` |
| `rungs` | `--count --instr --comment-len --decl-tag --out` |

### One-shot sweep scripts

Every other batch is a standalone script taking no arguments — each is a fixed,
already-designed sweep:

```bash
python -m sample_gen.gen_<name>
```

**Each script's own module docstring is its documentation**: what it measures,
what is held fixed, what each file discriminates, and which question it answers.
Read that rather than a summary table, which goes stale. There are around 140.

**Every new file goes on the realism floor** — build with
`build_l5x(target_name=..., **sample_gen.realism.with_baseline(**arm))`. `write_sample()`
refuses a file with fewer than 5 Ethernet I/O nodes, under 25% of the controller
predicted, or an output bit written twice. The first batch on it is
`python -m sample_gen.gen_realism_batch`.

Grouped by area:

**Tags and UDTs** — `batch2`, `mixed_udt`, `arraypack_boolarray`, `tagscope_alias`,
`comment_sweep`, `sweep_batch`, `retest_v2`, `udt_membername`, `udt_membername2`,
`udt_realworld_isolation`, `udttagslot_closeout`, `tagorder`, `pool_residual`,
`defscale`, `defscale2`, `shell_scale`, `additivity`

**Strings** — `string_tagoverhead`, `string_closure`, `string_batch2`,
`string_close_out`, `custom_string_array_closure`

**AOIs** — `aoi_sweep`, `aoi_sweep2`, `aoi_array_packing`,
`aoi_array_align_closeout`, `aoi_arraylocaltag_sweep`, `aoi_arraylocaltag2`,
`aoi_boolmix_grid`, `aoi_boolpack_clean`, `aoi_boolpack_pairing`,
`aoi_boolpack_pairing_iso2`, `aoi_closeout2`, `aoi_closure`,
`aoi_generalization`, `aoi_internal_logic_isolation`,
`aoi_internal_shape_isolation`, `aoi_localtag_density`, `aoi_nested_inout`,
`aoi_orphaned_def`, `aoi_required_visible`, `aoi_structure`,
`aoidefshape_closeout`, `boolpack_test`, `driveaxis_aoi`

**Logic and instructions** — `logic_sweep`, `logic_typesweep`,
`logic_random_mix`, `instruction_firstpass`, `unweighted_instructions`,
`unweighted_closeout`, `nontag_instruction_sweep`, `verified_instructions`,
`branch_empty_rungs`, `branchdepth_closeout`, `branchdepth_staggered`,
`rungshape`, `seriesoutput_closeout`, `literaloperand`, `empty_routine`,
`indirect_addressing`, `lbljmp_rules`, `msg_typesweep`, `phase3_closeout`,
`batch3_followups`, `model_gap_closers`, `oq_closeout`, `assumed_closeout`,
`segment_closeout`

**Expressions** — `cpt_comprehensive`, `cpt_confirm`, `cpt_mixed_operators`,
`cpt_arrangement_closeout`, `cpt_closeout`, `cmpcpt_complexity`,
`cmpcpt_layout`, `cmpcpt_expr_closeout`

**Structured Text** — `st_sizing`, `st_expression_grid`, `st_closeout`

**JSR, SBR and subroutines** — `jsr_sbr_ret`, `jsr_decompose`,
`jsr_midchain_isolation`, `jsr_multi_distinct_targets`,
`jsr_multi_distinct_targets_scale`, `jsr_paramcost_closeout`,
`jsr_paramtype_isolation`, `jsr_paramtype_isolation_iso2`,
`jsr_target_content_scale`, `subroutine_and_for`

**Tasks, programs and scope** — `task_overhead`, `task_overhead_disentangle`,
`xprogref`, `program_multi_distinct_scale`, `event_task_trigger`

**Motion and axis** — `axis_composite`, `axis_marginal`, `motion_instructions`,
`motion_predefined`, `motion_syntax_combos`, `cam_sweep`, `cam_closure`,
`module_axis_scale`

**Modules and I/O** — `io_modules`, `module_sweep`, `module_sweep_variants`,
`module_sweep_gap`, `module_motion`, `module_vfd`, `module_prototype`,
`module_kinetix_bus`, `module_marginal`, `module_bridge_placeholder`,
`module_cip_generic_scale`, `module_rack_pointio`, `module_pointio_rack`,
`pointio_conn_sweep`, `module_rack_1756local`, `module_rack_1756remote`,
`module_1756_rack_scale`, `module_5069_aent_rack`, `module_full_program`,
`generic_ethernet_module`, `prodcons`

**Alarms** — `alarm_conditions`, `alarm_definitions`, `alarm_bitbacking`,
`alarm_separation`, `almd_singletag`

**Platform and baseline** — `fw_catalog_matrix`, `platform_equivalence`,
`blockbyte_l71`, `identname_closeout`, `predefined_probe`

**Composite and realistic** — `composite_realistic`, `composite_realistic_v2`,
`composite_realistic_v3`, `composite_realistic_v4`, `realscale_surcharge`,
`realshape_aoi`, `v3_error_ablation`

> **Test files are supplied, not invented.** Ask before generating a batch, every
> time; no prior batch authorises the next. The deliverable at the design step is a
> written spec — what varies, what is held fixed, what each file discriminates,
> and against which existing captures it differences — not files on disk. See
> `SAMPLE_GENERATION.md`.
