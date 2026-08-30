"""1756-L71 counterpart of blockbytetest_dint120000.L5X (samples/generated/
tags/, built via `sample_gen.cli tags`) -- James, 2026-08-30: "Youll also
have to make that test for the l71 on the same firmware to get the
comparison." That earlier file tests the "blocks" side of the question
(1756-L81E, an L8x-family processor -- Studio 5000 labels its Capacity
readout "blocks", per James, whereas 1769/L7x-family readouts are labeled
"bytes"). This file is the direct comparison point: byte-identical content
(same 120,000-element DINT array, nothing else) on 1756-L71 (L7x family,
"bytes"-labeled), same firmware (35.05/35.11) so firmware isn't a
confound. If Studio 5000's real Capacity numbers for the two files match
(both ~498,236), "block" and "byte" are numerically the same unit, just a
different word per processor generation. If they don't, the ratio between
them is the real block-to-byte conversion factor -- and since 480,000 of
the 498,236 predicted total is exactly 120,000 x 4 (atomic array content,
zero packing ambiguity), any real conversion factor will show up as an
obvious clean ratio.

Run: python -m sample_gen.gen_blockbyte_l71
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "tags", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def main() -> None:
    array_tag = tag_xml("blockbytetest_dint120000", "DINT", dimensions=(120000,))
    l5x = build_l5x(
        target_name="BlockByteTestL71", tags_xml=array_tag, processor_type="1756-L71",
    )
    _write(
        l5x, "blockbytetest_l71_dint120000",
        "1756-L71 (L7x family, \"bytes\"-labeled per James) counterpart of "
        "blockbytetest_dint120000.L5X (1756-L81E, \"blocks\"-labeled) -- byte-identical content "
        "(single 120,000-element DINT array tag, nothing else), same firmware 35.05/35.11, "
        "isolating whether the two families' Capacity readouts are numerically the same unit or a "
        "real conversion factor apart. Same predicted total (498,236 bytes) as the L81E file by "
        "construction -- the comparison is entirely in the two files' real captured Capacity values.",
    )


if __name__ == "__main__":
    main()
