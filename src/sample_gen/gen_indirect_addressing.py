"""OQ item 14 (roadmap 2026-08-22): indirect addressing overhead -- direct
(literal) array index vs indirect (tag-driven) array index, same instruction
and rung count, only the index expression differs. Fixed at RUNG_COUNT=1000
(comparable scale to the confirmed MOV weight: 36 blocks/rung direct).

Extended 2026-08-22 (James: "Does tag[idx+1] take up the same space as
tag[Idx]?") with a third variant: an indirect index PLUS an arithmetic
offset (`Arr[Idx+1]`), not just a bare index tag. Standard, well-documented
Logix indirect-addressing capability (expressions are allowed inside an
array subscript), but unlike the bare-index/literal-index patterns this
specific `[tag+n]` shape wasn't found verbatim anywhere in the real corpus
-- flagged, not silently treated as equally corpus-confirmed.

Run: python -m sample_gen.gen_indirect_addressing
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import rungs_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "logic"
RUNG_COUNT = 1000

_TAGS_XML = "\n".join([
    tag_xml("Arr", "DINT", dimensions=(20,)),
    tag_xml("Dest", "DINT"),
    tag_xml("Idx", "DINT"),
])


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "logic_instr", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def main() -> None:
    fn_direct = lambda i: f"MOV(Arr[{i % 20}],Dest);"
    rungs = rungs_xml(RUNG_COUNT, fn_direct)
    l5x = build_l5x(target_name="IndirectDirect", tags_xml=_TAGS_XML, extra_rungs_xml=rungs)
    _write(l5x, f"indirect_direct_index_n{RUNG_COUNT:05d}",
           f"{RUNG_COUNT} rungs of MOV(Arr[literal],Dest) -- direct/literal array index")

    fn_indirect = lambda i: "MOV(Arr[Idx],Dest);"
    rungs = rungs_xml(RUNG_COUNT, fn_indirect)
    l5x = build_l5x(target_name="IndirectTag", tags_xml=_TAGS_XML, extra_rungs_xml=rungs)
    _write(l5x, f"indirect_tag_index_n{RUNG_COUNT:05d}",
           f"{RUNG_COUNT} rungs of MOV(Arr[Idx],Dest) -- indirect/tag-driven array index, "
           f"same instruction and rung count as the direct-index baseline")

    fn_offset = lambda i: "MOV(Arr[Idx+1],Dest);"
    rungs = rungs_xml(RUNG_COUNT, fn_offset)
    l5x = build_l5x(target_name="IndirectTagOffset", tags_xml=_TAGS_XML, extra_rungs_xml=rungs)
    _write(l5x, f"indirect_tag_offset_index_n{RUNG_COUNT:05d}",
           f"{RUNG_COUNT} rungs of MOV(Arr[Idx+1],Dest) -- indirect index WITH an arithmetic offset, "
           f"vs the bare-tag-index baseline indirect_tag_index_n{RUNG_COUNT:05d}")

    print("\nDone. 3 files.")


if __name__ == "__main__":
    main()
