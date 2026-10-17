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
