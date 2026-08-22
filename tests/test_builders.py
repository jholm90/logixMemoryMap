import xml.etree.ElementTree as ET

from sample_gen.builders import MemberSpec, custom_string_type_xml, rung_xml, rungs_xml, tag_xml, tags_xml, udt_xml

from l5x_memory_analyzer.parser.datatypes import parse_data_types
from l5x_memory_analyzer.parser.tags import parse_tags
from l5x_memory_analyzer.sizing.constants import load_memory_model
from l5x_memory_analyzer.sizing.udt import compute_array_size

MODEL = load_memory_model()


def _wrap_datatypes(*fragments):
    inner = "\n".join(fragments)
    return ET.fromstring(f"<Root><Controller><DataTypes>{inner}</DataTypes></Controller></Root>")


def test_udt_xml_bool_run_matches_confirmed_packing_rule():
    # James, 2026-08-20: BOOL,DINT,BOOL = 6 bytes; DINT,BOOL,BOOL = 5 bytes.
    root = _wrap_datatypes(
        udt_xml("BoolDintBool", [MemberSpec("A", "BOOL"), MemberSpec("C", "DINT"), MemberSpec("B", "BOOL")]),
        udt_xml("DintBoolBool", [MemberSpec("C", "DINT"), MemberSpec("A", "BOOL"), MemberSpec("B", "BOOL")]),
    )
    data_types = parse_data_types(root)
    assert compute_array_size("BoolDintBool", (), data_types, MODEL) == (6, "KNOWN")
    assert compute_array_size("DintBoolBool", (), data_types, MODEL) == (5, "KNOWN")


def test_udt_xml_bool_run_wraps_every_8_bits():
    members = [MemberSpec(f"Bit{i}", "BOOL") for i in range(10)]
    root = _wrap_datatypes(udt_xml("TenBools", members))
    data_types = parse_data_types(root)
    udt = data_types["TenBools"]
    hidden_sints = [m for m in udt.members if m.data_type == "SINT"]
    assert len(hidden_sints) == 2  # 8 + 2 -> two backing bytes
    size, _ = compute_array_size("TenBools", (), data_types, MODEL)
    assert size == 2  # two backing SINT bytes, nothing else


def test_custom_string_type_xml_sizes_len_plus_data():
    root = _wrap_datatypes(custom_string_type_xml("STRING40", 40))
    data_types = parse_data_types(root)
    size, confidence = compute_array_size("STRING40", (), data_types, MODEL)
    assert size == 44  # 4-byte LEN + 40-byte DATA
    assert confidence == "KNOWN"


def test_tag_xml_parses_with_dimensions():
    xml_frag = tag_xml("BigArray", "DINT", (100,))
    root = ET.fromstring(f"<Root><Controller><Tags>{xml_frag}</Tags></Controller></Root>")
    tags = parse_tags(root)
    assert tags[0].name == "BigArray"
    assert tags[0].dimensions == (100,)


def test_tags_xml_multiple_specs():
    xml_frag = tags_xml([("A", "DINT"), ("B", "SINT", (10,))])
    root = ET.fromstring(f"<Root><Controller><Tags>{xml_frag}</Tags></Controller></Root>")
    tags = parse_tags(root)
    assert {t.name for t in tags} == {"A", "B"}


def test_rung_xml_includes_comment_when_given():
    xml_frag = rung_xml(0, "XIC(A)OTE(B);", comment="hello")
    assert "hello" in xml_frag
    assert "XIC(A)OTE(B);" in xml_frag


def test_rungs_xml_generates_n_rungs_with_per_rung_callbacks():
    xml_frag = rungs_xml(3, lambda i: f"NOP(); // {i}", lambda i: "c" if i == 1 else None)
    assert xml_frag.count("<Rung ") == 3
    assert xml_frag.count("<Comment>") == 1
