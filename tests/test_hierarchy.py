from l5x_memory_analyzer.parser.datatypes import DataTypeDef, Member
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.report import SizeEntry
from l5x_memory_analyzer.ui.hierarchy import build_hierarchy, type_utilization

ENTRIES = [
    SizeEntry(
        path="controller/BigArray",
        category="controller_tag",
        data_type="DINT",
        bytes=400,
        pct_of_total=80.0,
        tier="exact",
        basis="KNOWN",
    ),
    SizeEntry(
        path="program:MainProgram/LocalFlag",
        category="program_tag",
        data_type="BOOL",
        bytes=4,
        pct_of_total=0.8,
        tier="exact",
        basis="ASSUMED",
    ),
    SizeEntry(
        path="program:MainProgram/LocalDint",
        category="program_tag",
        data_type="DINT",
        bytes=96,
        pct_of_total=19.2,
        tier="exact",
        basis="KNOWN",
    ),
]


def test_build_hierarchy_groups_by_scope():
    tree = build_hierarchy(ENTRIES)
    assert tree["name"] == "root"
    assert tree["value"] == 500

    group_names = [c["name"] for c in tree["children"]]
    assert group_names == ["Controller Tags", "Program: MainProgram"]

    controller_group = tree["children"][0]
    assert [c["name"] for c in controller_group["children"]] == ["BigArray"]
    assert controller_group["children"][0]["value"] == 400

    program_group = tree["children"][1]
    assert {c["name"] for c in program_group["children"]} == {"LocalFlag", "LocalDint"}


def test_build_hierarchy_breaks_out_axis_tags_at_root():
    entries = ENTRIES + [
        SizeEntry(
            path="controller/Axis1",
            category="controller_tag",
            data_type="AXIS_CIP_DRIVE",
            bytes=22636,
            pct_of_total=0.0,
            tier="estimated",
            basis="FITTED",
        ),
        SizeEntry(
            path="program:MainProgram/LocalAxis",
            category="program_tag",
            data_type="AXIS_VIRTUAL",
            bytes=16796,
            pct_of_total=0.0,
            tier="estimated",
            basis="FITTED",
        ),
    ]
    tree = build_hierarchy(entries)
    group_names = [c["name"] for c in tree["children"]]
    assert "Axis Definitions" in group_names
    assert "Controller Tags" in group_names

    axis_group = next(c for c in tree["children"] if c["name"] == "Axis Definitions")
    axis_names = {c["name"] for c in axis_group["children"]}
    assert axis_names == {"Axis1", "LocalAxis"}

    controller_group = next(c for c in tree["children"] if c["name"] == "Controller Tags")
    assert "Axis1" not in {c["name"] for c in controller_group["children"]}


def test_has_children_defaults_false_without_data_types():
    tree = build_hierarchy(ENTRIES)
    controller_group = tree["children"][0]
    assert controller_group["children"][0]["has_children"] is False


def test_has_children_true_for_array_tag_even_though_data_type_alone_looks_scalar():
    # BigArray's SizeEntry.data_type is just "DINT" (SizeEntry doesn't carry
    # dimensions) -- without tag_dimensions this would wrongly look like a
    # plain scalar. Regression test for exactly that bug.
    model = load_memory_model()
    tree = build_hierarchy(ENTRIES, data_types={}, model=model, tag_dimensions={"controller/BigArray": (100,)})
    controller_group = tree["children"][0]
    assert controller_group["children"][0]["has_children"] is True


def test_has_children_true_for_udt_typed_tag():
    udt = DataTypeDef(name="Motor", members=[Member(name="Speed", data_type="DINT", dimension=0)])
    model = load_memory_model()
    entries = [
        SizeEntry(
            path="controller/M1", category="controller_tag", data_type="Motor",
            bytes=4, pct_of_total=100.0, tier="exact", basis="UNKNOWN",
        )
    ]
    tree = build_hierarchy(entries, data_types={"Motor": udt}, model=model)
    assert tree["children"][0]["children"][0]["has_children"] is True


def test_routine_logic_nests_under_a_routines_subgroup_not_flat_with_tags():
    # Phase 5 (2026-08-27): a program's routine_logic entries must NOT sit
    # as flat siblings next to that program's tags -- they get their own
    # "Routines" subgroup within the program's group.
    entries = ENTRIES + [
        SizeEntry(
            path="program:MainProgram/MainRoutine", category="routine_logic",
            data_type="RLL", bytes=500, pct_of_total=50.0, tier="estimated", basis="FITTED",
        ),
        SizeEntry(
            path="program:MainProgram/SecondRoutine", category="routine_logic",
            data_type="RLL", bytes=300, pct_of_total=30.0, tier="estimated", basis="FITTED",
        ),
    ]
    tree = build_hierarchy(entries)
    program_group = next(c for c in tree["children"] if c["name"] == "Program: MainProgram")
    tag_names = {c["name"] for c in program_group["children"] if "children" not in c}
    assert tag_names == {"LocalFlag", "LocalDint"}  # tags stay flat, routines excluded

    routines_group = next(c for c in program_group["children"] if c["name"] == "Routines")
    assert {c["name"] for c in routines_group["children"]} == {"MainRoutine", "SecondRoutine"}
    assert routines_group["value"] == 800
    assert all(c["tier"] == "estimated" for c in routines_group["children"])


def test_programs_nest_under_task_when_mapping_supplied():
    # Phase 5 Task-level grouping (2026-08-27): real L5X-stated
    # Controller/Tasks/ScheduledProgram relationship, not a fitted byte
    # formula -- a Task's total is just the sum of its Programs' bytes.
    tree = build_hierarchy(ENTRIES, program_to_task={"MainProgram": "MainTask"})
    group_names = [c["name"] for c in tree["children"]]
    assert group_names == ["Controller Tags", "Task: MainTask"]

    task_group = tree["children"][1]
    assert task_group["value"] == 100  # LocalFlag(4) + LocalDint(96)
    assert [c["name"] for c in task_group["children"]] == ["Program: MainProgram"]


def test_program_with_no_known_task_stays_top_level():
    # A real gap in the source L5X (or no mapping supplied at all) must
    # never drop or hide a program -- it just isn't nested.
    tree = build_hierarchy(ENTRIES, program_to_task={"SomeOtherProgram": "SomeTask"})
    group_names = [c["name"] for c in tree["children"]]
    assert group_names == ["Controller Tags", "Program: MainProgram"]


def test_type_utilization_rolls_up_across_scopes():
    rows = type_utilization(ENTRIES)
    by_type = {r["data_type"]: r for r in rows}

    assert by_type["DINT"]["bytes"] == 496  # BigArray + LocalDint, across scopes
    assert by_type["BOOL"]["bytes"] == 4
    # sorted descending by bytes
    assert rows[0]["data_type"] == "DINT"
