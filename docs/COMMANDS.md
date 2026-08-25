# Command Reference

Every command/script invocation used on this project, in one place, so
nothing has to get re-dug-out of chat history. Grouped by what it's for:
capture pipeline (James runs these), analyzer CLI + webpage (either of you
runs these), sample generator (mostly Claude, listed here in case you want
to run one directly).

## 1. Capture pipeline (PowerShell + AHK) — the daily driver

Full procedure: `docs/TESTING_PLAN.md`. Three pieces, run in order.

### 1a. Convert L5X -> ACD (`scripts/batch_l5x_to_acd.ps1`)

Wraps Rockwell's own `l5xgit` CLI (Logix Designer SDK). Resumable, content-
hash-based staleness tracking — safe to re-run against the same
`-OutputDir` any time.

```powershell
# First run after upgrading this script (adopts already-converted files
# instead of paying for a full reconvert):
./batch_l5x_to_acd.ps1 -InputDir ..\samples\generated -OutputDir C:\l5x_scratch\acd -AdoptExisting

# Every run after that:
./batch_l5x_to_acd.ps1 -InputDir ..\samples\generated -OutputDir C:\l5x_scratch\acd
```

Params: `-InputDir` (required), `-OutputDir` (required), `-L5xGitPath`
(default `l5xgit`), `-UnsafeSkipDependencyCheck`, `-AdoptExisting`.

Auto-pushes `convert_log.csv` to `main` when it finishes (via
`_autopush.ps1`, dot-sourced internally — nothing extra to run).

### 1b. AHK companion (`scripts/logix_build_capture.ahk`)

Must already be running before step 1c. Drives Studio 5000's File > Open
inside the same already-running instance (~5s/file vs ~65s for a full
close/reopen).

- `Ctrl+F1` — start the capture loop
- `Esc` — abort
- `F9` — debug helper, dumps control text on the active window

### 1c. Capture real memory readings (`scripts/batch_memory_capture.ps1`)

Consumes `convert_log.csv` from step 1a. Fully unattended — no prompts,
safe to leave running overnight against the full corpus.

```powershell
# Smoke test on the first 10 files before committing to a full run:
./batch_memory_capture.ps1 -ConvertLog C:\l5x_scratch\acd\convert_log.csv `
    -ControllerModel "5069-L306ER" -FirmwareRev "35.11" -Limit 10

# Full run, same command without -Limit:
./batch_memory_capture.ps1 -ConvertLog C:\l5x_scratch\acd\convert_log.csv `
    -ControllerModel "5069-L306ER" -FirmwareRev "35.11"
```

Params: `-ConvertLog` (required), `-ControllerModel` (required),
`-FirmwareRev` (required), `-ManifestPath` (default
`samples/manifest.csv`), `-HandoffPath`, `-OpenRequestPath`,
`-TimeoutSeconds` (default 1200), `-Limit`.

Auto-pushes `samples/manifest.csv` to `main` when it finishes — same
mechanism as 1a. Window-title-mismatch and zero-Capacity rows are
detected and retried automatically on the next run, no manual re-flagging
(see `docs/TESTING_PLAN.md`).

**Known gap:** 1769-series processors (`L1xER`/`L2xER`/`L3xER`) need the
"Estimate" button clicked before Controller Properties shows a Capacity
number — the AHK loop doesn't do this yet, so those rows still need
manual reporting.

## 2. Analyzer CLI + webpage

See also the [README's Usage section](../README.md#usage) for the short
version. Full syntax:

```bash
# From the repo's src/ directory, no install needed:
cd src
python -m l5x_memory_analyzer.cli dump  path/to/file.L5X   # raw XML dump
python -m l5x_memory_analyzer.cli size  path/to/file.L5X   # flat byte breakdown, tags/UDT/AOI
python -m l5x_memory_analyzer.cli ui    path/to/file.L5X   # treemap webpage, pre-loaded
python -m l5x_memory_analyzer.cli ui                       # treemap webpage, File->Open picker

# ui options:
#   --host 127.0.0.1   (default)
#   --port 8765         (default)
#   --no-browser        don't auto-open the default browser
```

Or, after `pip install -e .` from the repo root, the same subcommands are
available as a console script:

```bash
l5x-memory-analyzer dump path/to/file.L5X
l5x-memory-analyzer ui   path/to/file.L5X --port 9000 --no-browser
```

## 3. Sample generator — parameterized CLI (`sample_gen.cli`)

Run from `src/`. Every subcommand writes an L5X to
`samples/generated/<category>/` and a `samples/manifest.csv` row with
`predicted_bytes` filled in from this project's own sizing engine.

```bash
# UDT + one tag of that type
python -m sample_gen.cli udt --name MotorStatus \
    --member Running:BOOL --member Speed:DINT --member Faulted:BOOL \
    --out motorstatus_test

# N tags of a given type/dimensions
python -m sample_gen.cli tags --type DINT --dims 10000 --out dint_10k_array

# N rungs of a given instruction pattern
python -m sample_gen.cli rungs --count 1000 \
    --instr "XIC(In{i})OTE(Out{i});" \
    --decl-tag "In{i}:BOOL" --decl-tag "Out{i}:BOOL" \
    --comment-len 100 --out xic_ote_1000_comment100
```

Full flag reference (`--help` on each subcommand shows all of these):
`udt` — `--name --member --member-desc-len --type-desc-len --tag-desc-len
--tag-dims --instances --out`.
`tags` — `--type --dims --count --desc-len --name-prefix --name-len --out`.
`rungs` — `--count --instr --comment-len --decl-tag --out`.

## 4. Sample generator — one-shot sweep scripts

Every other test batch is its own standalone script (`python -m
sample_gen.<name>`, no arguments — each one is a fixed, already-designed
sweep). Listed here for reference/re-running, not because you'd typically
type these by hand. Grouped by what they test; each writes its own files
+ manifest rows, same as the CLI above.

### Tags / UDT
| Command | Covers |
|---|---|
| `python -m sample_gen.gen_batch2` | Nested UDTs, nested arrays |
| `python -m sample_gen.gen_mixed_udt` | OQ-MIXEDUDT |
| `python -m sample_gen.gen_arraypack_boolarray` | OQ-BOOLARRAY, OQ-UDTARRAYALIGN, OQ-ARRAYPACK |
| `python -m sample_gen.gen_tagscope_alias` | OQ-TAGSCOPE, OQ-ALIASSIZE |
| `python -m sample_gen.gen_comment_sweep` | Comment/description-length sweep |
| `python -m sample_gen.gen_sweep_batch` | Large general sweep batch |
| `python -m sample_gen.gen_retest_v2` | Retest of 6 rows flagged by the 2026-08-25 manifest audit |

### AOI
| Command | Covers |
|---|---|
| `python -m sample_gen.gen_aoi_sweep` | Big AOI data-sizing sweep |
| `python -m sample_gen.gen_aoi_sweep2` | Second AOI sweep, closing remaining items |
| `python -m sample_gen.gen_aoi_array_packing` | AOI-instance-array packing resolution |
| `python -m sample_gen.gen_aoi_boolpack_clean` | Clean re-test of OQ-AOIBOOLPACK |
| `python -m sample_gen.gen_aoi_closure` | Small targeted AOI additions |
| `python -m sample_gen.gen_aoi_generalization` | AOI generalization batch |
| `python -m sample_gen.gen_aoi_nested_inout` | Nested AOI-with-required-InOut-param |
| `python -m sample_gen.gen_aoi_required_visible` | AOI Parameter Required/Visible flag sweep |
| `python -m sample_gen.gen_boolpack_test` | OQ-BOOLPACK isolating sample pair |

### Logic / instructions
| Command | Covers |
|---|---|
| `python -m sample_gen.gen_logic_sweep` | Per-instruction logic-sizing sweep |
| `python -m sample_gen.gen_logic_typesweep` | Instruction operand-TYPE sweep |
| `python -m sample_gen.gen_logic_random_mix` | Random-combination logic validation harness |
| `python -m sample_gen.gen_instruction_firstpass` | First-pass single-instruction coverage sweep |
| `python -m sample_gen.gen_cpt_comprehensive` | CPT comprehensive batch |
| `python -m sample_gen.gen_cpt_confirm` | CPT operator-tier linearity confirmation |
| `python -m sample_gen.gen_cpt_mixed_operators` | CPT mixed-operator-tier cost sweep |
| `python -m sample_gen.gen_cmpcpt_complexity` | CPT/CMP expression-complexity sweep |
| `python -m sample_gen.gen_cmpcpt_layout` | CPT/CMP operand-layout and background-optimization sweep |
| `python -m sample_gen.gen_indirect_addressing` | Indirect addressing overhead |
| `python -m sample_gen.gen_lbljmp_rules` | LBL/JMP validation-rule sweep |
| `python -m sample_gen.gen_jsr_sbr_ret` | JSR/SBR/RET parameter-passing sweep |
| `python -m sample_gen.gen_jsr_decompose` | JSR param-cost follow-up (OQ-JSRPARAMCOST) |
| `python -m sample_gen.gen_branch_empty_rungs` | Phase 4 bit-logic closeout, branch/empty rungs |
| `python -m sample_gen.gen_empty_routine` | OQ-EMPTYROUTINE |
| `python -m sample_gen.gen_phase3_closeout` | Phase 3 literal-checklist closeout |
| `python -m sample_gen.gen_batch3_followups` | Batch 3 follow-up sweep |

### Task / Program / Routine
| Command | Covers |
|---|---|
| `python -m sample_gen.gen_task_overhead` | Per-Task overhead, isolated from logic |
| `python -m sample_gen.gen_task_overhead_disentangle` | Per-Task overhead disentangling, missing axis |
| `python -m sample_gen.gen_xprogref` | OQ-XPROGREF round 2 |

### Motion / Axis
| Command | Covers |
|---|---|
| `python -m sample_gen.gen_axis_composite` | Axis + composite-UDT sweep |
| `python -m sample_gen.gen_motion_instructions` | MAM/MAJ/MAS/MRP motion instructions |
| `python -m sample_gen.gen_motion_predefined` | OQ-PREDEFINED: MOTION_INSTRUCTION, CAM_PROFILE |
| `python -m sample_gen.gen_motion_syntax_combos` | MAM/MAJ/MAS/MRP keyword-combination validation |
| `python -m sample_gen.gen_cam_sweep` | CAM structure byte-size count sweep |

### Modules / I/O
| Command | Covers |
|---|---|
| `python -m sample_gen.gen_io_modules` | I/O module sizing sweep, first batch |
| `python -m sample_gen.gen_module_sweep` | Full I/O module sweep — one file per real corpus catalog |
| `python -m sample_gen.gen_module_sweep_variants` | Real catalogs with 2+ different real configurations |
| `python -m sample_gen.gen_module_sweep_gap` | Closes the last real catalog coverage gap |
| `python -m sample_gen.gen_module_motion` | Motion/drive module batch (Kinetix power supply + axis) |
| `python -m sample_gen.gen_module_vfd` | VFD (PowerFlex 525/755) module batch |
| `python -m sample_gen.gen_module_prototype` | Module/IO prototype batch |
| `python -m sample_gen.gen_module_kinetix_bus` | Full Kinetix 5700 shared-bus test |
| `python -m sample_gen.gen_module_rack_pointio` | Point I/O rack tests, multiple real modules on one adapter |
| `python -m sample_gen.gen_module_rack_1756local` | 1756 local rack, multiple real ControlLogix I/O modules |
| `python -m sample_gen.gen_module_rack_1756remote` | 1756 local rack talking to a 1756 remote rack over Ethernet |
| `python -m sample_gen.gen_module_bender_full` | Full-fidelity replica of James's real Bender program (69 modules) |

### Strings
| Command | Covers |
|---|---|
| `python -m sample_gen.gen_string_tagoverhead` | STRING/custom-string tag_overhead resolution |
| `python -m sample_gen.gen_string_closure` | STRING closure batch |
| `python -m sample_gen.gen_string_batch2` | STRING accuracy batch 2 |
| `python -m sample_gen.gen_string_close_out` | STRING closing batch, round 2 |

## 5. Tests

```bash
# From the repo root:
python3 -m pytest tests -q
```

`pyproject.toml` sets `pythonpath = ["src"]` and `testpaths = ["tests"]`,
so plain `pytest` also works from the repo root once `dev` extras are
installed (`pip install -e ".[dev]"`).
