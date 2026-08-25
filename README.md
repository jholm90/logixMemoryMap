# L5X Memory Analyzer

WinDirStat for CompactLogix controller memory. Parses an L5X export and shows
where your 4MB (or whatever the target is) is actually going — tags, UDTs, AOIs,
module/IO overhead, and (eventually, heuristically) compiled logic size.

Not a one-shot build. See `docs/PROJECT_PLAN.md` for the phased approach and
`CLAUDE.md` for full working context if you're driving this with Claude Code.

## Quick links
- [Project Plan](docs/PROJECT_PLAN.md)
- [Task List](docs/TASKS.md)
- [Open Questions](docs/OPEN_QUESTIONS.md)
- [Memory Model (sizing constants)](docs/MEMORY_MODEL.md)
- [Testing Plan](docs/TESTING_PLAN.md)
- [Sample Generation](docs/SAMPLE_GENERATION.md)
- [Full Command Reference](docs/COMMANDS.md) — every script/CLI command used on this project

## Usage

### Webpage (treemap UI)

```bash
cd src
python -m l5x_memory_analyzer.cli ui path/to/file.L5X
```

Opens `http://127.0.0.1:8765` in your default browser with the file
pre-loaded. Drop the path to start with a File->Open picker instead
(useful for a desktop-shortcut launch with no command prompt):

```bash
python -m l5x_memory_analyzer.cli ui
```

Options: `--host` (default `127.0.0.1`), `--port` (default `8765`),
`--no-browser` (skip auto-opening the browser).

### Script (CLI)

```bash
cd src
python -m l5x_memory_analyzer.cli size path/to/file.L5X   # flat tag/UDT/AOI byte breakdown, printed to stdout
python -m l5x_memory_analyzer.cli dump path/to/file.L5X   # raw parsed XML, for debugging a load issue
```

After `pip install -e .` from the repo root, the same subcommands are
available as `l5x-memory-analyzer` (e.g. `l5x-memory-analyzer ui
path/to/file.L5X`) without the `cd src` / `python -m` prefix.

See [docs/COMMANDS.md](docs/COMMANDS.md) for the full command reference,
including the real-controller capture pipeline (PowerShell + AHK) and
every sample generator script.
