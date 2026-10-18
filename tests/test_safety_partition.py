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


# --- the engine's laws for safety content (MEMORY_MODEL, "Safety memory is a separate
# partition"), each pinned at the value the safe_* batch measured --------------------

import xml.etree.ElementTree as ET

import pytest

from l5x_memory_analyzer.parser.logic import _operand_roots
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import build_report
from l5x_memory_analyzer.sizing.safety import build_safety_report
from sample_gen.builders import rung_xml
from sample_gen.wrapper import build_l5x

_MODEL = load_memory_model()


def _small(controller_tags=(), safety_tags=(), safety_rungs=(), standard_rungs=()) -> ET.Element:
    """A safety project without the realism plant: the laws are differences."""
    arm = {
        "extra_programs_xml": G._safety_program(list(safety_tags), list(safety_rungs)),
        "extra_tasks_xml": G._SAFETY_TASK,
        "extra_rungs_xml": "\n".join(rung_xml(i, r) for i, r in enumerate(standard_rungs)),
        "tags_xml": "\n".join(controller_tags),
    }
    return ET.fromstring(build_l5x("SafeTest", processor_type=G.PROCESSOR, safety_level="SIL2", **arm))


def _both(root: ET.Element) -> tuple[int, int]:
    return (sum(e.bytes for e in build_report(root, _MODEL)[0]),
            sum(e.bytes for e in build_safety_report(root, _MODEL)[0]))


def _delta(a: ET.Element, b: ET.Element) -> tuple[int, int]:
    (sa, fa), (sb, fb) = _both(a), _both(b)
    return sa - sb, fa - fb


def test_the_measured_constants():
    sp = _MODEL.safety_partition
    assert (sp.base_bytes, sp.data_header_bytes, sp.data_alignment) == (1394, 28, 8)
    assert {mn: sp.rung_bytes[mn] for mn in ("ESTOP", "RIN", "ROUT", "LC", "NOP")} == {
        "ESTOP": 360, "RIN": 360, "ROUT": 360, "LC": 436, "NOP": 16}
    assert all(sp.rung_confidence(mn) == "KNOWN" for mn in ("ESTOP", "RIN", "ROUT", "LC"))
    assert set(sp.rung_bytes) >= set(G.SHAPES)


@pytest.mark.parametrize("data_type", ["BOOL", "SINT", "INT", "DINT", "REAL"])
def test_a_controller_safety_tag_is_its_name_entry_standard_and_its_data_block_safety(data_type):
    tags = [G._controller_safety_tag(f"SafeTag{i:05d}", data_type) for i in range(10)]   # 12 characters
    assert _delta(_small(controller_tags=tags), _small()) == (10 * 64, 10 * 32)


def test_the_standard_half_follows_the_name_and_the_safety_half_does_not():
    tags = [G._controller_safety_tag(f"S{'x' * 35}{i:04d}", "DINT") for i in range(10)]   # 40 characters
    assert _delta(_small(controller_tags=tags), _small()) == (10 * (56 + 8 * 5), 10 * 32)


def test_a_safety_program_tag_is_all_safety_partition():
    tags = [G._program_safety_tag(f"SafeTag{i:05d}", "DINT") for i in range(10)]
    assert _delta(_small(safety_tags=tags), _small()) == (0, 10 * 96)
    rin = [G._studio_tag(f"RIN_{i:03d}", "REDUNDANT_INPUT", controller_scope=False) for i in range(10)]
    assert _delta(_small(safety_tags=rin), _small()) == (0, 10 * 136)


def test_safety_rungs_cost_nothing_standard_and_their_measured_cost_safety():
    tags, rungs = G.instruction_pair("RIN", 10)
    # The rungs replace the routine's single NOP rung (16).
    assert _delta(_small(safety_tags=tags, safety_rungs=rungs), _small(safety_tags=tags)) == (0, 10 * 360 - 16)


def test_standard_logic_reading_a_safety_tag_pays_eight_per_operand():
    ref = [G._controller_safety_tag("SRefIn", "BOOL", (256,)),
           G.tag_xml("StdRefOut", "BOOL", dimensions=(256,)), G.tag_xml("StdIn", "BOOL", dimensions=(256,))]
    ctl = _small(controller_tags=ref)
    safe = _small(controller_tags=ref, standard_rungs=[f"XIC(SRefIn[{i}])OTE(StdRefOut[{i}]);" for i in range(10)])
    plain = _small(controller_tags=ref, standard_rungs=[f"XIC(StdIn[{i}])OTE(StdRefOut[{i}]);" for i in range(10)])
    assert _delta(safe, plain) == (10 * 8, 0)
    assert _delta(safe, ctl)[1] == 0


def test_a_project_without_a_safety_program_has_no_safety_partition():
    root = ET.fromstring(build_l5x("Plain", tags_xml=G.tag_xml("Std", "DINT")))
    assert build_safety_report(root, _MODEL) == ([], [])


def test_operand_roots_are_each_operands_root_tag():
    # Member names are not roots; a tag used as an index is.
    assert _operand_roots(["XIC(SRefIn[3].Ok)OTE(Out.Bit[Idx]);"]) == ("SRefIn", "Out", "Idx")
