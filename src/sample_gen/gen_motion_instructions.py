"""OQ item 12 (roadmap 2026-08-22): motion instructions themselves (MAM/MAJ/
MAH/MAS/MSO/MRP), the real 2-operand call pattern confirmed against the
corpus: `MSO(Axis_BND1_Chuck_Drive,Axis_BND1_Chuck.MSO);`,
`MAH(EM48_Multichain1,MC1.Homing.MAH_Immediate);` -- (Axis, MotionInstruction
tag), same shape across every MAH/MSO/MAFR/MASR real example found. MAPC/
MCCP (camming, needs a CAM_PROFILE tag too) are NOT included here -- no real
corpus example of their call syntax turned up in the search, and this
project's own real CAM_PROFILE finding (the "voodoo" hidden-field one) means
guessing wrong here risks more than usual. Left for a follow-up once a real
reference turns up.

Real AXIS_CIP_DRIVE + MotionGroup tags copied from gen_axis_composite.py's
_AXIS_TAG_XML (same real reference already used and working there). One
shared MOTION_INSTRUCTION backing tag reused across all rungs in a given
file, same pool-reuse methodology as the main 244-file sweep.

Run: python -m sample_gen.gen_motion_instructions
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import motion_instruction_tag_xml, rungs_xml
from sample_gen.gen_axis_composite import _AXIS_TAG_XML
from sample_gen.lint import lint_or_raise
from sample_gen.manifest import append_manifest_row
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "axis"
COUNTS = [10, 100]

# Real 2-operand (Axis, MotionInstruction) call, confirmed for MAH/MSO/
# MAFR/MASR in the corpus. MAM/MAJ/MAS/MRP use the documented Rockwell
# standard version of the same 2-required-operand signature (optional
# trailing params default) -- not independently corpus-confirmed for these
# specific mnemonics the way MAH/MSO are, flagged in the manifest
# description below rather than silently treated as equally certain.
CORPUS_CONFIRMED = {"MAH", "MSO"}
INSTRUCTIONS = ["MAM", "MAJ", "MAH", "MAS", "MSO", "MRP"]


def _write_unmodeled(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    lint_or_raise(l5x, context=str(out_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(l5x, encoding="utf-8")
    append_manifest_row(out_name, f"{description} (unmodeled predefined structure)", "axis", out_path, 0)
    print(f"Wrote {out_path} (predicted N/A -- unmodeled axis structure)")


def main() -> None:
    motion_instr_tag = motion_instruction_tag_xml("MotionInstr1")
    tags = "\n".join([_AXIS_TAG_XML, motion_instr_tag])

    for instr in INSTRUCTIONS:
        confirmed_note = "corpus-confirmed call syntax" if instr in CORPUS_CONFIRMED else \
            "standard documented 2-operand signature, not independently corpus-confirmed for this exact mnemonic"
        for n in COUNTS:
            fn = lambda i, instr=instr: f"{instr}(Axis_Cip_Drive,MotionInstr1);"
            rungs = rungs_xml(n, fn)
            l5x = build_l5x(target_name=f"{instr}N{n}", tags_xml=tags, extra_rungs_xml=rungs)
            out_name = f"motioninstr_{instr.lower()}_n{n:05d}"
            _write_unmodeled(l5x, out_name,
                              f"{n} rungs of {instr}(Axis_Cip_Drive,MotionInstr1) -- {confirmed_note}")

    print(f"\nDone. {len(INSTRUCTIONS) * len(COUNTS)} files.")


if __name__ == "__main__":
    main()
