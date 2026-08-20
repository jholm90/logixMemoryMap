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
