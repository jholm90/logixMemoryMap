# L5X Memory Analyzer

WinDirStat for Logix controller memory. Point it at an L5X export and it shows
where the controller's memory budget is actually going — tags, UDTs, AOIs, module
and I/O overhead, alarm conditions, and compiled ladder logic — as a drillable
treemap.

The purpose is to find memory hogs before a download fails: a hidden
1000-element array, a bloated UDT, a runaway routine.

## Accuracy

On seventeen real production exports, which are the only accuracy evidence that
counts: **mean absolute error 1.60%, worst case 3.63%.** Read the worst case as
up to 4% on an unfamiliar file — the error distribution has a long right tail and
the worst file is more than twice the mean.

The strongest single piece of evidence is a blind test: one 7.89 MB program was
predicted at **+2.15%** before its actual memory figure was used for anything.

Two very different confidence levels exist inside the tool and it never blurs
them:

- **Tag, UDT and AOI data space is calculable exactly.** Atomic sizes and packing
  rules are known and empirically verified.
- **Compiled ladder logic size is a fitted heuristic.** L5X is the
  human-readable representation and does not reveal how Logix compiles rungs to
  its internal execution format. Every logic-derived number is visually flagged
  as estimated.

## Usage

### Treemap UI

```bash
cd src
python -m l5x_memory_analyzer.cli ui path/to/file.L5X
```

Opens `http://127.0.0.1:8765` with the file loaded. Omit the path to start with a
file picker instead, which suits a desktop shortcut with no command prompt:

```bash
python -m l5x_memory_analyzer.cli ui
```

Options: `--host` (default `127.0.0.1`), `--port` (default `8765`),
`--no-browser`.

### Command line

```bash
cd src
python -m l5x_memory_analyzer.cli size path/to/file.L5X   # flat byte breakdown
python -m l5x_memory_analyzer.cli dump path/to/file.L5X   # raw parsed XML
```

After `pip install -e .` the same subcommands are available as
`l5x-memory-analyzer` without the `cd src` prefix.

## Platform support

| platform | status |
|---|---|
| 1756-L8x ControlLogix | supported, well represented in the real set |
| 5069 / CompactLogix 5380 | supported, represented in the real set |
| 1756-L7x, 1769 | dead architecture — existing wiring kept, nothing new invested |
| 1756-L9x | firmware matrix only, no real validation |

## Documentation

| file | contents |
|---|---|
| [FINAL_REPORT.md](docs/FINAL_REPORT.md) | **start here** — results, wins, losses, what is open, how to get more accuracy |
| [MEMORY_MODEL.md](docs/MEMORY_MODEL.md) | every sizing constant, formula and packing rule |
| [OPEN_QUESTIONS.md](docs/OPEN_QUESTIONS.md) | unresolved sizing and behaviour questions |
| [RESOLVED_QUESTIONS.md](docs/RESOLVED_QUESTIONS.md) | closed questions and why |
| [TASKS.md](docs/TASKS.md) | the ranked work queue |
| [PROJECT_PLAN.md](docs/PROJECT_PLAN.md) | phases and their exit criteria |
| [ROADMAP.md](docs/ROADMAP.md) | where the tool stands and what is next |
| [INSTRUCTION_COVERAGE.md](docs/INSTRUCTION_COVERAGE.md) | per-instruction weight status against real usage |
| [AOI_KNOWLEDGE_MAP.md](docs/AOI_KNOWLEDGE_MAP.md) | what is known and unknown about AOI sizing |
| [TESTING_PLAN.md](docs/TESTING_PLAN.md) | how predictions are validated against real controllers |
| [SAMPLE_GENERATION.md](docs/SAMPLE_GENERATION.md) | how test files are built, and every batch |
| [COMMANDS.md](docs/COMMANDS.md) | every script and CLI command |
| [IO_MODULES.md](docs/IO_MODULES.md) | module and I/O sizing reference |
| [CMP_CPT_REFERENCE.md](docs/CMP_CPT_REFERENCE.md) | expression instruction reference |
| [OPEN_BUILD_ERRORS.md](docs/OPEN_BUILD_ERRORS.md) | sample files that will not build |
| `CLAUDE.md` | working context and the rules that govern changes |

## Licence

Apache-2.0. Python end to end.

`tools/ra-logix-designer-vcs-custom-tools/` is Rockwell Automation's `l5xgit`
source, vendored under its own MIT licence for the capture pipeline's L5X→ACD
conversion; see [tools/README.md](tools/README.md).
