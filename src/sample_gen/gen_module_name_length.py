"""OQ-MODULENAMELEN: what a module's NAME length costs.

One committed pair says +13 characters of module name is worth +24 bytes, and
the engine charges nothing for a module name at any length: `P208` (4 chars)
predicts exactly, `TestMod1_2198P208` (17 chars) reads 24 bytes high. One pair
is one equation, and several step shapes reproduce +24.

This family reads the step directly. A single 2198-P208 under the local rack,
the exact module XML modulemotion_p208_baseline was built from, no tags and no
axes, and only the module's Name attribute changes. Lengths run 4 to 40 --
Rockwell's identifier limit -- and include values that are not multiples of 4
or 8 (6, 10, 13, 17), because a task name was found to round UP at 13
characters where the identifier term rounds down (OQ-TASKNAMEROUND), and only
non-multiples can tell those rules apart.

Every file is 1756-L81E at firmware 35, the controller name is fixed, and the
module name is the only moving dimension. Differenced against its neighbours,
no model involved.

Run: python -m sample_gen.gen_module_name_length
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.gen_module_motion import _P208_MODULE_XML
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

LENGTHS = (4, 6, 8, 10, 12, 13, 16, 17, 20, 24, 32, 40)


def _name(length: int) -> str:
    # Valid identifier: a letter first, then filler, exact length.
    return ("P208" + "X" * max(length - 4, 0))[:length]


def main() -> None:
    for length in LENGTHS:
        name = _name(length)
        module = _P208_MODULE_XML.replace('Name="P208"', f'Name="{name}"', 1)
        assert f'Name="{name}"' in module
        l5x = build_l5x(target_name="ModuleNameLen", tags_xml="", extra_modules_xml=module)
        out_name = f"modname_p208_len{length:02d}"
        out_path = OUT_ROOT / f"{out_name}.L5X"
        write_sample_unmodeled(l5x, out_path)
        append_manifest_row(
            out_name,
            f"OQ-MODULENAMELEN: one 2198-P208 under the local rack, no tags, no axes, module "
            f"named {name!r} ({length} chars). Controller name and every other attribute fixed; "
            f"the module name length is the only variable.",
            "modules", out_path, 0)
        print(f"Wrote {out_path}")
    print(f"\nDone. {len(LENGTHS)} files.")


if __name__ == "__main__":
    main()
