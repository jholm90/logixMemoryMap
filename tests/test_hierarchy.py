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
    #
    # Extended 2026-09-10: the tags get a "Program Tags" container of their
    # own for the same reason. With only one side contained, the single
    # "Routines" tile sat among dozens of loose tag tiles and was easy to
    # lose; a program now reads as exactly two parts.
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
    subgroups = {c["name"]: c for c in program_group["children"]}
    assert set(subgroups) == {"Program Tags", "Routines"}

    tag_names = {c["name"] for c in subgroups["Program Tags"]["children"]}
    assert tag_names == {"LocalFlag", "LocalDint"}  # tags together, routines excluded

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


def test_program_with_no_known_task_is_kept_and_marked_unscheduled():
    """A program with no owning Task must never be dropped or hidden -- and
    since 2026-09-05 it is also LABELLED, because in real Logix that means
    it is unscheduled (the controller fault handler and power-up handler
    live here, as do programs parked out of the scan). It still consumes
    controller memory while never executing, which is precisely what this
    tool exists to surface, so rendering it indistinguishable from a
    scheduled program was hiding something real. 2026-09-05: "be
    sure this is visible in the web gui."
    """
    tree = build_hierarchy(ENTRIES, program_to_task={"SomeOtherProgram": "SomeTask"})
    group_names = [c["name"] for c in tree["children"]]
    assert group_names == ["Controller Tags", "Program: MainProgram (unscheduled)"]
    prog = next(c for c in tree["children"] if c["name"].startswith("Program: "))
    assert prog["unscheduled"] is True


def test_type_utilization_rolls_up_across_scopes():
    rows = type_utilization(ENTRIES)
    by_type = {r["data_type"]: r for r in rows}

    assert by_type["DINT"]["bytes"] == 496  # BigArray + LocalDint, across scopes
    assert by_type["BOOL"]["bytes"] == 4
    # sorted descending by bytes
    assert rows[0]["data_type"] == "DINT"


def _module_entry(name: str, catalog: str, size: int) -> SizeEntry:
    return SizeEntry(
        path=f"modules/{name}", category="module_io", data_type=catalog,
        bytes=size, pct_of_total=0.0, tier="estimated", basis="FITTED",
    )


def test_module_tile_is_labelled_by_module_name_not_catalog_twice():
    # A module's data_type IS its catalog number, so labelling by data_type
    # rendered "PowerFlex 525-EENET / PowerFlex 525-EENET" -- the catalog
    # twice and the module's own name nowhere.
    tree = build_hierarchy([_module_entry("EM101_InfdPkgDeck1", "PowerFlex 525-EENET", 900)])
    group = next(c for c in tree["children"] if c["name"] == "I/O Modules")
    leaf = group["children"][0]
    assert leaf["name"] == "EM101_InfdPkgDeck1"
    assert leaf["data_type"] == "PowerFlex 525-EENET"


def test_modules_nest_under_their_stated_parent_module():
    entries = [
        _module_entry("JB101_IO", "1734-AENT/B", 1636),
        _module_entry("JB101_IO_SLOT1", "1734-IB8/C", 0),
        _module_entry("JB101_IO_SLOT2", "1734-IE4C/C", 1887),
        _module_entry("EM101", "PowerFlex 525-EENET", 900),
    ]
    parents = {
        "JB101_IO": "Local",
        "JB101_IO_SLOT1": "JB101_IO",
        "JB101_IO_SLOT2": "JB101_IO",
        "EM101": "Local",
    }
    tree = build_hierarchy(entries, module_parents=parents)
    group = next(c for c in tree["children"] if c["name"] == "I/O Modules")
    # "Local" is the processor's own entry and is never emitted, so both
    # local-chassis modules stay at the top level.
    assert [c["name"] for c in group["children"]] == ["JB101_IO", "EM101"]

    adapter = group["children"][0]
    assert [c["name"] for c in adapter["children"]] == [
        "Module", "JB101_IO_SLOT1", "JB101_IO_SLOT2",
    ]
    # The adapter's own cost moves into its "Module" child rather than
    # being counted twice or dropped.
    assert adapter["children"][0]["value"] == 1636
    assert "value" not in adapter
    assert sum(c["value"] for c in adapter["children"]) == 1636 + 0 + 1887


def test_module_parent_cycle_does_not_recurse_forever():
    entries = [_module_entry("A", "cat", 10), _module_entry("B", "cat", 20)]
    tree = build_hierarchy(entries, module_parents={"A": "B", "B": "A"})
    group = next(c for c in tree["children"] if c["name"] == "I/O Modules")
    names = [c["name"] for c in group["children"]]
    assert names  # terminated at all, rather than hanging


def test_non_tag_entry_first_does_not_leak_or_crash_on_dimensions():
    # dims used to be assigned only on the tag branch, so a leading non-tag
    # entry raised UnboundLocalError -- real, on 4 of the sample exports.
    entries = [
        SizeEntry(path="project_baseline", category="project_baseline",
                  data_type="Baseline", bytes=100, pct_of_total=0.0,
                  tier="estimated", basis="FITTED"),
    ] + ENTRIES
    tree = build_hierarchy(entries)
    overhead = next(c for c in tree["children"] if c["name"] == "Project Overhead")
    assert overhead["children"][0]["dimensions"] == []


def test_alarm_host_tag_is_drillable_into_its_conditions():
    entries = [SizeEntry(
        path="alarms/AlarmActive_TiltHoist", category="alarm_condition",
        data_type="200 condition(s)", bytes=221600, pct_of_total=0.0,
        tier="estimated", basis="KNOWN",
    )]
    tree = build_hierarchy(entries)
    group = next(c for c in tree["children"] if c["name"] == "Alarm Conditions")
    leaf = group["children"][0]
    assert leaf["name"] == "AlarmActive_TiltHoist"
    assert leaf["has_children"] is True
