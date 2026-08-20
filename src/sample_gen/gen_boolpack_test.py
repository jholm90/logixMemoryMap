"""Generates the OQ-BOOLPACK isolating sample pair: a baseline project and
the same project plus 1000 standalone BOOL controller tags. The delta between
their real compiled memory (Studio 5000, Controller Properties -> Memory tab,
no download needed per TESTING_PLAN.md) divided by 1000 answers whether a
standalone BOOL tag really costs 4 bytes (current model) or packs, per
James's hunch (2026-08-20, docs/OPEN_QUESTIONS.md OQ-BOOLPACK).

Run: python -m sample_gen.gen_boolpack_test
"""

from __future__ import annotations

import csv
import xml.etree.ElementTree as ET
from pathlib import Path

from sample_gen.wrapper import bool_tags_xml, build_l5x

from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report

OUT_DIR = Path(__file__).parent.parent.parent / "samples" / "generated" / "boolpack"
MANIFEST = Path(__file__).parent.parent.parent / "samples" / "manifest.csv"

BOOL_COUNT = 1000


def _predicted_bytes(l5x_text: str) -> int:
    root = ET.fromstring(l5x_text)
    model = load_memory_model()
    entries, errors = build_report(root, model)
    if errors:
        raise RuntimeError(f"sample has unsized tags, fix the generator: {errors}")
    return sum(e.bytes for e in entries)


def _append_manifest_row(sample_id, description, category, l5x_path, predicted_bytes):
    is_new = not MANIFEST.exists()
    with open(MANIFEST, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(
                "sample_id,description,category,l5x_path,predicted_bytes,actual_bytes,"
                "delta,delta_pct,controller_model,firmware_rev,date_tested,notes".split(",")
            )
        writer.writerow(
            [
                sample_id,
                description,
                category,
                l5x_path,
                predicted_bytes,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    baseline = build_l5x(target_name="BoolPackBaseline", tags_xml="")
    baseline_path = OUT_DIR / "sample_0001_boolpack_baseline_0bool.L5X"
    baseline_path.write_text(baseline, encoding="utf-8")
    baseline_bytes = _predicted_bytes(baseline)

    with_bools = build_l5x(
        target_name="BoolPack1000", tags_xml=bool_tags_xml(BOOL_COUNT)
    )
    with_bools_path = OUT_DIR / f"sample_0002_boolpack_{BOOL_COUNT}bool.L5X"
    with_bools_path.write_text(with_bools, encoding="utf-8")
    with_bools_bytes = _predicted_bytes(with_bools)

    rel_baseline = baseline_path.relative_to(MANIFEST.parent.parent)
    rel_with_bools = with_bools_path.relative_to(MANIFEST.parent.parent)

    _append_manifest_row(
        "sample_0001", "boolpack baseline, 0 extra tags", "tag",
        str(rel_baseline), baseline_bytes,
    )
    _append_manifest_row(
        "sample_0002", f"boolpack test, {BOOL_COUNT} standalone BOOL tags", "tag",
        str(rel_with_bools), with_bools_bytes,
    )

    print(f"Wrote {baseline_path} (predicted {baseline_bytes} bytes)")
    print(f"Wrote {with_bools_path} (predicted {with_bools_bytes} bytes)")
    print(f"Predicted delta for {BOOL_COUNT} standalone BOOL tags: "
          f"{with_bools_bytes - baseline_bytes} bytes "
          f"({(with_bools_bytes - baseline_bytes) / BOOL_COUNT:.3f} bytes/tag)")
    print(f"Logged to {MANIFEST}")


if __name__ == "__main__":
    main()
