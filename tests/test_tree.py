import pytest

from l5x_memory_analyzer.parser.datatypes import DataTypeDef, Member
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.tree import (
    NotDrillableError,
    expand_children,
    expand_definition_children,
    has_children,
    resolve_type_at_path,
)
from l5x_memory_analyzer.sizing.udt import (
    RecursiveUdtError,
    compute_aoi_definition_cost,
    compute_udt_definition_cost,
)

MODEL = load_memory_model()

INNER = DataTypeDef(
    name="Inner", members=[Member(name="A", data_type="DINT", dimension=0)]
)  # 4 bytes
MOTOR = DataTypeDef(
    name="Motor",
    members=[
        Member(name="Speed", data_type="REAL", dimension=0),
        Member(name="Readings", data_type="DINT", dimension=5),
        Member(name="ZZZZZZZZZZBoolMember01", data_type="SINT", dimension=0),
        Member(name="Running", data_type="BIT", dimension=0),
        Member(name="Nested", data_type="Inner", dimension=0),
    ],
)
CYCLE = DataTypeDef(name="Cycle", members=[Member(name="Self", data_type="Cycle", dimension=0)])
STR40 = DataTypeDef(
    name="STRING40",
    family="StringFamily",
    members=[Member(name="LEN", data_type="DINT", dimension=0), Member(name="DATA", data_type="SINT", dimension=40)],
)

DATA_TYPES = {"Inner": INNER, "Motor": MOTOR, "Cycle": CYCLE, "STRING40": STR40}


def test_scalar_atomic_not_drillable():
    assert has_children("DINT", (), DATA_TYPES, MODEL) is False
    with pytest.raises(NotDrillableError):
        expand_children("DINT", (), DATA_TYPES, MODEL)


def test_udt_expands_to_members_including_bit_alias_leaf():
    children = expand_children("Motor", (), DATA_TYPES, MODEL)
    by_name = {c.name: c for c in children}

    assert by_name["Speed"].bytes == 4
    assert by_name["Speed"].has_children is False

    assert by_name["Readings"].dimensions == (5,)
    assert by_name["Readings"].bytes == 20
    assert by_name["Readings"].has_children is True  # array, drillable

    assert by_name["ZZZZZZZZZZBoolMember01"].bytes == 1  # backing SINT

    assert by_name["Running"].data_type == "BIT"
    assert by_name["Running"].bytes == 0
    assert by_name["Running"].has_children is False  # bit-level, true leaf

    assert by_name["Nested"].data_type == "Inner"
    assert by_name["Nested"].bytes == 4
    assert by_name["Nested"].has_children is True


def test_dint_array_expands_to_one_child_per_element():
    children = expand_children("DINT", (10,), DATA_TYPES, MODEL)
    assert len(children) == 10
    assert all(c.bytes == 4 and c.data_type == "DINT" and not c.has_children for c in children)
    assert children[3].segment == "[3]"


def test_bool_array_expands_to_proportional_shares_summing_to_total():
    total, _ = MODEL.bool.array_packed_word_bytes, None
    children = expand_children("BOOL", (33,), DATA_TYPES, MODEL)
    assert len(children) == 33
    # 33 bools -> ceil(33/32)=2 words -> 8 bytes total, per docs/MEMORY_MODEL.md
    assert sum(c.bytes for c in children) == pytest.approx(8.0)
    assert all(c.has_children is False for c in children)


def test_predefined_structure_expands_to_three_dint_fields():
    children = expand_children("TIMER", (), DATA_TYPES, MODEL)
    assert [c.name for c in children] == ["Status", "PRE", "ACC"]
    assert all(c.bytes == 4 for c in children)

    control_children = expand_children("CONTROL", (), DATA_TYPES, MODEL)
    assert [c.name for c in control_children] == ["Status", "PRE", "POS"]


def test_custom_string_expands_to_len_and_data():
    children = expand_children("STRING40", (), DATA_TYPES, MODEL)
    by_name = {c.name: c for c in children}
    assert by_name["LEN"].bytes == 4
    assert by_name["DATA"].bytes == 40
    assert by_name["DATA"].dimensions == (40,)


def test_builtin_string_expands_to_len_and_data():
    children = expand_children("STRING", (), DATA_TYPES, MODEL)
    by_name = {c.name: c for c in children}
    assert by_name["LEN"].bytes == 4
    assert by_name["DATA"].bytes == 82


def test_self_referential_udt_raises_on_expand():
    with pytest.raises(RecursiveUdtError):
        expand_children("Cycle", (), DATA_TYPES, MODEL)


def test_resolve_path_walks_member_then_array_index():
    dt, dims = resolve_type_at_path("Motor", (), [".Readings", "[2]"], DATA_TYPES, MODEL)
    assert (dt, dims) == ("DINT", ())


def test_resolve_path_walks_nested_udt_member():
    dt, dims = resolve_type_at_path("Motor", (), [".Nested", ".A"], DATA_TYPES, MODEL)
    assert (dt, dims) == ("DINT", ())


def test_resolve_path_into_predefined_structure_field():
    dt, dims = resolve_type_at_path("Motor", (), [".Readings"], DATA_TYPES, MODEL)
    # Readings is DINT[5], not a predefined structure -- sanity check the
    # actual predefined-structure case via a TIMER-typed member instead.
    timer_udt = DataTypeDef(name="HasTimer", members=[Member(name="Tmr", data_type="TIMER", dimension=0)])
    dts = {**DATA_TYPES, "HasTimer": timer_udt}
    dt2, dims2 = resolve_type_at_path("HasTimer", (), [".Tmr", ".PRE"], dts, MODEL)
    assert (dt2, dims2) == ("DINT", ())


def test_resolve_path_bit_alias_member_is_a_leaf():
    dt, dims = resolve_type_at_path("Motor", (), [".Running"], DATA_TYPES, MODEL)
    assert (dt, dims) == ("BIT", ())
    assert has_children("BIT", (), DATA_TYPES, MODEL) is False


# ---------------------------------------------------------------------------
# expand_definition_children -- 2026-08-26, James's Phase 2/2b "defs pool
# drill-down" fix. Breaks a definition's own one-time cost into its
# contributing pieces; must always sum back exactly to what udt.py's own
# compute_*_definition_cost would report for the same type, or the treemap
# would show a defs-pool node whose children don't add up to its own value.
# ---------------------------------------------------------------------------

BOOLRUN_UDT = DataTypeDef(
    name="WithBoolRun",
    members=[
        Member(name="ZZZZZZZZZZBoolMember01", data_type="SINT", dimension=0, hidden=True),
        Member(name="FlagA", data_type="BIT", dimension=0),
        Member(name="FlagB", data_type="BIT", dimension=0),
        Member(name="Count", data_type="DINT", dimension=0),
    ],
)
AOI_FIXTURE = DataTypeDef(
    name="fbDebounce",
    is_aoi=True,
    members=[
        Member(name="EnableIn", data_type="BOOL", dimension=0),
        Member(name="RawInput", data_type="BOOL", dimension=0),
        Member(name="DebTmr", data_type="TIMER", dimension=0),
    ],
)
DEF_DATA_TYPES = {**DATA_TYPES, "WithBoolRun": BOOLRUN_UDT, "fbDebounce": AOI_FIXTURE}


def test_expand_udt_definition_sums_to_compute_udt_definition_cost():
    children = expand_definition_children("Motor", DEF_DATA_TYPES, MODEL)
    expected_total, _ = compute_udt_definition_cost("Motor", DEF_DATA_TYPES, MODEL)
    assert sum(c.bytes for c in children) == expected_total
    # One row per declared member (Speed, Readings, ZZZZZZZZZZBoolMember01,
    # Running, Nested -- all 5 are not `hidden`, Motor has no bool run of
    # its own) plus one "Base + type name" row.
    assert len(children) == 6
    names = {c.name for c in children}
    assert {"Speed", "Readings", "ZZZZZZZZZZBoolMember01", "Running", "Nested"} <= names


def test_expand_udt_definition_bool_run_gets_its_own_row():
    children = expand_definition_children("WithBoolRun", DEF_DATA_TYPES, MODEL)
    expected_total, _ = compute_udt_definition_cost("WithBoolRun", DEF_DATA_TYPES, MODEL)
    assert sum(c.bytes for c in children) == expected_total
    boolrun_rows = [c for c in children if c.name.startswith("BOOL packing")]
    assert len(boolrun_rows) == 1
    assert boolrun_rows[0].bytes == MODEL.udt_definition.bool_run_bonus
    # Declared members exclude the hidden backing SINT: FlagA, FlagB, Count.
    declared_names = {"FlagA", "FlagB", "Count"}
    assert declared_names <= {c.name for c in children}
    assert "ZZZZZZZZZZBoolMember01" not in {c.name for c in children}


def test_expand_string_definition_sums_to_report_formula():
    children = expand_definition_children("STRING40", DEF_DATA_TYPES, MODEL)
    # maxlen=40, 40 % 4 == 0 -- no mod-4 bonus row, just the flat base.
    # "STRING40" is 8 chars -- lands in the confirmed flat 5-12 bucket.
    assert sum(c.bytes for c in children) == MODEL.string.custom_definition_cost_for(len("STRING40"))
    assert len(children) == 1
    assert children[0].basis == MODEL.string.custom_definition_confidence


def test_expand_aoi_definition_sums_to_compute_aoi_definition_cost_and_excludes_enablein():
    children = expand_definition_children("fbDebounce", DEF_DATA_TYPES, MODEL)
    expected_total, expected_basis = compute_aoi_definition_cost("fbDebounce", DEF_DATA_TYPES, MODEL)
    assert sum(c.bytes for c in children) == expected_total
    assert all(c.basis == expected_basis == "FITTED" for c in children)
    names = {c.name for c in children}
    assert "RawInput" in names and "DebTmr" in names
    assert "EnableIn" not in names
    assert all(c.has_children is False for c in children)
