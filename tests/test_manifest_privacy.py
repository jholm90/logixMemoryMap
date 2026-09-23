"""The committed manifest must never carry a real export's file name.

Real rows use the neutral samples/local/realprog_NN.L5X; the real name lives in
the gitignored samples/local/aliases.csv. load_manifest() resolves the neutral
path to the real file for readers, so any writer that round-trips through it
would write the real name back -- which happened once and was caught before it
left the machine. Pinned here rather than trusted.
"""

import csv
import re

from sample_gen.manifest_store import MANIFEST_PATH, load_manifest

_NEUTRAL = re.compile(r"^samples/local/realprog_\d+\.L5X$")


def test_every_committed_real_row_uses_the_neutral_path():
    with open(MANIFEST_PATH, newline="", encoding="utf-8-sig") as fh:
        rows = [r for r in csv.DictReader(fh) if r["category"] == "real_program"]
    assert rows
    bad = [(r["sample_id"], r["l5x_path"]) for r in rows if not _NEUTRAL.match(r["l5x_path"])]
    assert not bad, bad


def test_writers_see_raw_paths():
    raw = {r["sample_id"]: r["l5x_path"] for r in load_manifest(resolve_local=False)}
    for sid, path in raw.items():
        if sid.startswith("realprog_"):
            assert _NEUTRAL.match(path), (sid, path)
