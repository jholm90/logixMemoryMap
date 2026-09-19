"""Re-extract src/sample_gen/data/kinetix.py from the real corpus.

Run this, never hand-edit the data module. The 2198 faults of all
came from a payload that was transcribed by hand once and then adjusted by hand
again -- including an "adjustment" that deleted a value to make a count match,
in the wrong direction.

Reads every 2198 module in samples/local/ and records, per catalog, the most
commonly attested (Vendor, ProductType, ProductCode, Major, Minor) and every
distinct (ConfigSize, value_count) -> payload seen. samples/local/ is gitignored
real program data; only these module-configuration constants are committed, the
same way the verified module and axis XML blocks already are.

Run: python scripts/extract_kinetix_data.py
"""

from __future__ import annotations

import collections
import glob
import re
import sys
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT = REPO_ROOT / "src" / "sample_gen" / "data" / "kinetix.py"
HEADER = (REPO_ROOT / "src" / "sample_gen" / "data" / "kinetix.py")


def main() -> int:
    rec: dict[str, dict] = collections.defaultdict(
        lambda: {"attrs": collections.Counter(), "blobs": {}})
    files = sorted(glob.glob(str(REPO_ROOT / "samples" / "local" / "**" / "*.L5X"),
                             recursive=True))
    if not files:
        print("no real files under samples/local/ -- nothing to extract", file=sys.stderr)
        return 1
    for path in files:
        for module in ET.parse(path).getroot().iter("Module"):
            catalog = module.get("CatalogNumber") or ""
            if not catalog.startswith("2198"):
                continue
            rec[catalog]["attrs"][(
                module.get("Vendor"), module.get("ProductType"),
                module.get("ProductCode"), module.get("Major"), module.get("Minor"),
            )] += 1
            for config in module.iter("ConfigData"):
                size = int(config.get("ConfigSize") or 0)
                for data in config.iter("Data"):
                    if data.get("Format") != "L5K" or not data.text:
                        continue
                    values = [v for v in re.split(r"[,\s\[\]]+", data.text) if v != ""]
                    rec[catalog]["blobs"].setdefault((size, len(values)), values)

    # Preserve the existing module docstring; only the data below is regenerated.
    existing = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    doc_end = existing.find('"""', existing.find('"""') + 3)
    doc = existing[:doc_end + 3] if doc_end > 0 else '"""Verified 2198 Kinetix data."""'

    out = [doc, "", "from __future__ import annotations", "",
           "# catalog -> (Vendor, ProductType, ProductCode, Major, Minor)",
           "MODULE_IDENTITY: dict[str, tuple[str, str, str, str, str]] = {"]
    for catalog in sorted(rec):
        identity, n = rec[catalog]["attrs"].most_common(1)[0]
        out.append(f"    {catalog!r}: {identity!r},   # attested {n}x")
    out += ["}", "",
            "# catalog -> {(ConfigSize, value_count): comma-joined values}",
            "CONFIG_DATA: dict[str, dict[tuple[int, int], str]] = {"]
    for catalog in sorted(rec):
        if not rec[catalog]["blobs"]:
            continue
        out.append(f"    {catalog!r}: {{")
        for (size, count), values in sorted(rec[catalog]["blobs"].items()):
            out.append(f"        ({size}, {count}): (")
            for chunk in textwrap.wrap(",".join(values), 92,
                                       break_long_words=False, break_on_hyphens=False):
                out.append(f"            {chunk!r}")
            out.append("        ),")
        out.append("    },")
    pairs = sorted({k for c in rec for k in rec[c]["blobs"]})
    out += ["}", "",
            "# Every (ConfigSize, value_count) pair observed in the real corpus.",
            f"REAL_CONFIG_PAIRS: frozenset[tuple[int, int]] = frozenset({pairs})",
            "", ACCESSOR]
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{OUT.relative_to(REPO_ROOT)}: {len(rec)} catalog(s) from {len(files)} real file(s)")
    print(f"real (ConfigSize, value_count) pairs: {pairs}")
    return 0


ACCESSOR = '''
def payload_for(catalog: str) -> tuple[int, str]:
    """(ConfigSize, comma-joined L5K values) for this catalog's fullest real
    payload. Raises for an unknown catalog rather than substituting another
    catalog's data -- silently falling back is exactly how one drive's identity
    spread to five others.

    The value count is re-verified against the key here, so a payload edited by
    hand that no longer matches its own declared length fails loudly at
    generation time instead of shipping.
    """
    variants = CONFIG_DATA.get(catalog)
    if not variants:
        raise ValueError(
            f"No verified real ConfigData for {catalog!r}. Extract it from a real "
            f"export with scripts/extract_kinetix_data.py."
        )
    (size, count), values = max(variants.items(), key=lambda kv: kv[0])
    actual = len([v for v in values.split(",") if v != ""])
    if actual != count:
        raise ValueError(
            f"{catalog} payload for ConfigSize={size} holds {actual} values but its key "
            f"says {count}. Re-extract it rather than adjusting either number."
        )
    return size, values
'''.lstrip("\n")


if __name__ == "__main__":
    raise SystemExit(main())
