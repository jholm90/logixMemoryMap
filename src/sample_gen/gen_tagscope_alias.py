"""OQ-TAGSCOPE and OQ-ALIASSIZE -- both real XML shapes confirmed against
the corpus (see program_tag_xml/alias_tag_xml docstrings in builders.py),
neither tested yet.

  A. group_tagscope -- Program-scoped DINT tags, Local (no Usage attribute)
     vs Public (Usage="Public"), at 10/100/1000 count each. Does scope
     affect the per-tag storage cost the way it doesn't for Description
     (OQ-TAGOVERHEAD)?
  B. group_aliassize -- N Alias tags (1/10/1000) each pointing at one of 5
     fixed real target DINT tags (round-robin), target-tag count held
     constant across all three so the marginal alias-only cost isolates
     cleanly.

Run: python -m sample_gen.gen_tagscope_alias
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.builders import alias_tag_xml, program_tag_xml, tag_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "tags"


def _write(l5x: str, out_name: str, description: str) -> None:
    out_path = OUT_ROOT / f"{out_name}.L5X"
    bytes_ = write_sample(l5x, out_path)
    append_manifest_row(out_name, description, "tags", out_path, bytes_)
    print(f"Wrote {out_path} (predicted {bytes_} bytes)")


def group_tagscope() -> None:
    for usage_label, usage in [("local", None), ("public", "Public")]:
        for n in [10, 100, 1000]:
            tags = "\n".join(program_tag_xml(f"PT{i}", "DINT", usage=usage) for i in range(n))
            l5x = build_l5x(target_name=f"TagScope{usage_label}{n}", tags_xml="", extra_program_tags_xml=tags)
            _write(l5x, f"tagscope_{usage_label}_n{n:05d}",
                   f"{n} Program-scoped DINT tags, Usage={'Public' if usage else 'Local (default)'}")


def group_aliassize() -> None:
    target_tags = "\n".join(tag_xml(f"AliasTarget{i}", "DINT") for i in range(5))
    for n in [1, 10, 1000]:
        aliases = "\n".join(alias_tag_xml(f"Alias{i}", f"AliasTarget{i % 5}") for i in range(n))
        tags = target_tags + "\n" + aliases
        l5x = build_l5x(target_name=f"AliasSizeN{n}", tags_xml=tags)
        _write(l5x, f"aliassize_n{n:05d}",
               f"{n} Alias tags (round-robin over 5 fixed real DINT targets, target count held constant)")


def main() -> None:
    group_tagscope()
    group_aliassize()
    print("\nDone. 9 files.")


if __name__ == "__main__":
    main()
