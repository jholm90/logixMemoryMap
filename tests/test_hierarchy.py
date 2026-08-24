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


def test_type_utilization_rolls_up_across_scopes():
    rows = type_utilization(ENTRIES)
    by_type = {r["data_type"]: r for r in rows}

    assert by_type["DINT"]["bytes"] == 496  # BigArray + LocalDint, across scopes
    assert by_type["BOOL"]["bytes"] == 4
    # sorted descending by bytes
    assert rows[0]["data_type"] == "DINT"
