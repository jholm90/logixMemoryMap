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


def test_type_utilization_rolls_up_across_scopes():
    rows = type_utilization(ENTRIES)
    by_type = {r["data_type"]: r for r in rows}

    assert by_type["DINT"]["bytes"] == 496  # BigArray + LocalDint, across scopes
    assert by_type["BOOL"]["bytes"] == 4
    # sorted descending by bytes
    assert rows[0]["data_type"] == "DINT"
