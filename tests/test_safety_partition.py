"""The safety-partition batch (OQ-SAFETYPARTITION): its call shapes, its plan, and the
capture column that carries the safety reading."""

from __future__ import annotations

from sample_gen import gen_safety_partition as G
from sample_gen.lint import lint_l5x


def test_every_call_names_real_members_and_studios_operand_count():
    G.check_shapes()


def test_the_plan_covers_every_safety_routine_instruction():
    ids = [sid for sid, _, _ in G.plan()]
    assert len(ids) == len(set(ids)) == 119
    for mn in G.SHAPES:
        counts = G.REAL_USE_COUNTS if mn in G.REAL_USE else (G.OTHER_COUNT,)
        for n in counts:
            assert f"safe_{mn.lower()}_{n}" in ids and f"safe_{mn.lower()}_tags_{n}" in ids


def test_a_pair_differs_only_by_its_rungs():
    plan = {sid: kw for sid, _, kw in G.plan()}
    tags_only, with_rungs = plan["safe_sls_tags_20"], plan["safe_sls_20"]
    assert tags_only["safety_tags"] == with_rungs["safety_tags"]
    assert "safety_rungs" not in tags_only and len(with_rungs["safety_rungs"]) == 20
    # One shared SFX tag, then per rung the backing tag and its three output tags.
    assert len(with_rungs["safety_tags"]) == 1 + 20 * 4


def test_the_control_passes_lint_on_the_safety_platform():
    x = G.build("safe_n00")
    assert 'ProcessorType="1756-L81ES"' in x and 'MajorRev="35"' in x
    assert 'ConfigureSafetyIOAlways="false"' in x and 'Class="Safety"' in x
    assert lint_l5x(x) == []


def test_captures_carry_a_safety_column():
    from sample_gen.manifest_store import CAPTURE_COLUMNS, JOINED_COLUMNS, load_manifest
    assert CAPTURE_COLUMNS[-1] == "safety_bytes" and "safety_bytes" in JOINED_COLUMNS
    # A captures.csv written before the column existed still joins: the key is empty.
    assert all("safety_bytes" in row for row in load_manifest()[:5])


def _safety_eval():
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "safety_eval", Path(__file__).parent.parent / "scripts" / "safety_eval.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_safety_eval_differences_both_partitions_and_sets_suspects_aside():
    ev = _safety_eval()

    def row(sid, std, saf, errors="0", notes=""):
        return {"sample_id": sid, "actual_bytes": str(std), "safety_bytes": str(saf),
                "error_count": errors, "notes": notes}

    base_std, base_saf = 842_000, 1_394
    rows = [row("safe_n00", base_std, base_saf)]
    for n in (10, 50, 200):    # 56 standard and 100 safety per tag
        rows.append(row(f"safe_tag_dint_{n}", base_std + 56 * n, base_saf + 100 * n))
    for n in (10, 50, 200):    # RIN: tags 60 / 120, rungs 0 / 300
        rows.append(row(f"safe_rin_tags_{n}", base_std + 60 * n, base_saf + 120 * n))
        rows.append(row(f"safe_rin_{n}", base_std + 60 * n, base_saf + 420 * n))
    rows.append(row("safe_dcs_tags_20", base_std, base_saf, errors="3"))
    good, suspect = ev.readings(rows)
    assert "safe_dcs_tags_20" not in good and suspect == [("safe_dcs_tags_20", "error_count=3")]
    assert ev.diff(good, "safe_tag_dint_50", "safe_n00") == (2_800, 5_000)
    assert ev.diff(good, "safe_rin_200", "safe_rin_tags_200") == (0, 60_000)
    text = ev.report(rows)
    assert "dint x50  std +2,800 (+56.00/each), safety +5,000 (+100.00/each)" in text
    assert "rung slope 10->200: std +0 (+0.00/each), safety +57,000 (+300.00/each)" in text
    assert "SUSPECT safe_dcs_tags_20: error_count=3" in text
