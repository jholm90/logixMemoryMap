# Reference manuals on file

The Rockwell manuals the project works from. **The owner keeps the PDFs** (owner's decision,
2026-10-29, for at least 365 days) and sends them over chat when a session needs them. They are
never committed: the repository is public and they are Rockwell's. A session copies them into
the gitignored `samples/local/reference/manuals/` and checks each against its SHA-256 below,
so every session reads the same edition. `scripts/build_instruction_reference.py` rebuilds the
parsed reference (`samples/local/reference/`) from them.

| publication | title | edition | pages | bytes | SHA-256 |
|---|---|---|---:|---:|---|
| 1756-RM018A-EN-P | Logix 5000 Controllers General Instructions | September 2025 | 927 | 15,469,736 | `3ad1653f6b5e88c8ae83dad1f4e5c20e4a2cc96e3e53a16229a307c29ef549fc` |
| 1756-PM006L-EN-P | Logix 5000 Controllers Sequential Function Charts | September 2024 | 77 | 3,115,616 | `bca3d344e71ab35fb43c2d83697fba850eeb8c17fb52badbc3c06b63f2d14af0` |
| 1756-PM007 | Logix 5000 Controllers Structured Text Programming Manual | September 2024 | 37 | 1,881,577 | `46267b7fc5a3bf793682954df22764030ba4ba589a90a5438bdf764a37419ecc` |
| 1756-PM009J-EN-P | Logix 5000 Controllers Function Block Diagram | March 2022 | 32 | 1,918,673 | `6cdb98e1556c51d8edb8f18b1c8898b3975186a04e31e955140a8488be23d272` |

RM018 arrived as a RAR (`1756-rm018_-en-p.rar`, SHA-256
`b8239389d790a8b875f08e4601d58b248b8862fbd16396a958ccc0cb67f4cec4`); `unar` extracts it.

**Not on file, asked for:** 1756-RM006 (process control and drives instructions: the function
blocks) and MOTION-RM002 (motion instructions). Until they arrive the function-block and motion
lists in batch F, and the reference for them, are unchecked against Rockwell's own tables.

PM006 is the SFC manual: SFC is never worked (CLAUDE.md), so it is kept for completeness only.
