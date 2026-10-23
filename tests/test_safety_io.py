"""Round 5, safety I/O (gen_safety_io.py, OQ-SAFETYPARTITION, TASKS 0z)."""

import re

from sample_gen import gen_safety_io as IO
from sample_gen import gen_safety_partition as G
from sample_gen import gen_safety_round2 as R
from sample_gen import gen_safety_round3 as R3
from sample_gen import gen_safety_round4 as R4
from sample_gen.lint import lint_l5x


def _plan():
    return {sid: kw for sid, _, kw in IO.plan()}


def test_round_5_is_17_new_files():
    ids = [sid for sid, _, _ in IO.plan()]
    assert len(ids) == len(set(ids)) == 17
    earlier = {s for mod in (G, R, R3, R4) for s, _, _ in mod.plan()}
    assert not set(ids) & earlier


def test_one_file_of_each_family_lints_clean():
    # write_sample lints every file as it is built; this pins one of each shape.
    for sid in ("safe_io_mix_4_4", "safe_io_racks_2x2", "safe_io_ib8s1c_4", "safe_io_5069_ib8s_4", "safe_io_5069_obv8s_4"):
        assert not lint_l5x(IO.make(sid, _plan()[sid])), sid


def test_each_card_carries_its_profile_configid_and_its_rack_network():
    l5x = IO.make("safe_io_mix_4_4", _plan()["safe_io_mix_4_4"])
    cards = re.findall(r'<Module Name="SRACK_1_S\d"[^>]*>.*?</Module>', l5x, re.S)
    assert len(cards) == 8
    for card in cards:
        assert re.search(r"<ConfigID>(102|205)</ConfigID>", card)
        assert f'SafetyNetwork="{IO.RACK_SNN[0]}"' in card
    assert '<Bus Size="9" />' in re.search(r'<Module Name="SRACK_1" .*?</Module>', l5x, re.S).group(0)


def test_a_5069_card_takes_its_bus_port_network():
    l5x = IO.make("safe_io_5069_obv8s_2", _plan()["safe_io_5069_obv8s_2"])
    snn = IO.local_snn(l5x, "1")
    cards = re.findall(r'<Module CatalogNumber="5069-OBV8S/A"[^>]*>', l5x)
    assert len(cards) == 2 and all(f'SafetyNetwork="{snn}"' in c for c in cards)
    assert 'ProcessorType="5069-L330ERMS2"' in l5x


def test_lint_refuses_a_safety_card_without_its_configid():
    l5x = IO.make("safe_io_ib8s_1", _plan()["safe_io_ib8s_1"])
    stripped = re.sub(r"<ExtendedProperties>\n<public><ConfigID>102</ConfigID>.*?</ExtendedProperties>\n", "", l5x,
                      count=1, flags=re.S)
    assert stripped != l5x
    assert [f for f in lint_l5x(stripped) if f.kind == "safety_io_without_configid"]


def test_a_safety_device_is_priced_by_its_connections_types_and_an_unseen_one_by_the_device_law():
    from l5x_memory_analyzer.sizing.constants import load_memory_model
    from l5x_memory_analyzer.sizing.safety_io import SafetyDevice, safety_rows, standard_rows
    m = load_memory_model()
    drives = [SafetyDevice(f"D{i}", "2198-D032-ERS3", ("AB:CIP_Motion_Device_Safety2",), 1, 1, 72, 0, True)
              for i in range(3)]
    card = SafetyDevice("C", "1734-IB8S/B", ("AB:1734_IB8S", "AB:1734_IB8S_Safety2"), 1, 1, 4)
    rows, unmeasured = safety_rows(drives + [card], m)
    assert sum(r[3] for r in rows) == 3 * 4717 + 3513 and unmeasured == {}
    # A device of types never measured: an overhead per safety connection plus its data.
    odd_in = SafetyDevice("X", "1791ES-IB8XOBV4/A", ("AB:1791ES_IB8XOBV4_Safety",), 1, 0, 10)
    odd_io = SafetyDevice("Y", "Some-Robot/A", ("XX:Robot_SI", "XX:Robot_SO"), 1, 1, 24, 1)
    rows, unmeasured = safety_rows([odd_in, odd_io], m)
    assert [(r[3], r[4]) for r in rows] == [(1653 + 160, "FITTED"), (1653 + 1814 + 16 * 24, "FITTED")]
    assert unmeasured == {"AB:1791ES_IB8XOBV4_Safety": 1, "XX:Robot_SI+XX:Robot_SO": 1}
    # and on the standard side a per-device overhead by its connections (types come on top)
    assert m.safety_io.unseen_standard_bytes(odd_in) == 600
    assert m.safety_io.unseen_standard_bytes(odd_io) == 600 + 162 + 1242
    # standard: the type's first-device cost once, then each drive its own
    assert sum(r[3] for r in standard_rows(drives, m)) == 4160 + 3 * 684
    pair = [SafetyDevice("I", "1756-IB16S/A", ("AB:5000_SDI16",)), SafetyDevice("O", "1756-OBV8S/A", ("AB:5000_SDO8",))]
    assert sum(r[3] for r in standard_rows(pair, m)) == 368 + 1832 + 1104 - 2 * 917


def test_the_device_law_reproduces_every_measured_device_type_within_three_and_a_half_percent():
    """Each measured type's safety cost against the law that prices an unmeasured one. The
    devices come from the safety I/O generators, built in memory, and the templates built
    locally (samples/local/safety_io, git-ignored); without the local ones the set is short."""
    import xml.etree.ElementTree as ET
    from pathlib import Path
    import pytest
    from l5x_memory_analyzer.sizing.constants import load_memory_model
    from l5x_memory_analyzer.sizing.safety_io import device_key, safety_devices
    from sample_gen import gen_safety_io, gen_safety_round6
    sio = load_memory_model().safety_io
    local = Path(__file__).parent.parent / "samples" / "local" / "safety_io"
    roots = [ET.fromstring(mod.make(sid, kw)) for mod in (gen_safety_io, gen_safety_round6)
             for sid, _desc, kw in mod.plan() if sid.startswith("safe_io") and sid.endswith("_1")]
    roots += [ET.parse(f).getroot() for f in sorted(local.glob("safe_iol_*_1.L5X"))]
    seen = {}
    for root in roots:
        for d in safety_devices(root):
            seen.setdefault(device_key(d), d)
    if len(seen) < 18 and not local.is_dir():
        pytest.skip("the locally built safety I/O templates are not on this machine")
    assert len(seen) == 18
    for key, d in seen.items():
        law, real = sio.unseen_safety_bytes(d), sio.safety_bytes[key]
        assert abs(law - real) <= 0.035 * real, (key, law, real)


# Batch A (2026-10-21): each device type's safety cost, exact at every count captured.
BATCH_A_SAFETY = {
    "AB:1734_IB8S+AB:1734_IB8S_Safety2": 3513, "AB:1734_IB8S_Safety6": 1629,
    "AB:1734_OB8S+AB:1734_OB8S_Safety1": 3457, "AB:1734_OB8S+AB:1734_OB8S_Safety3": 3457,
    "AB:5000_SDI8": 2513, "AB:5000_DO8+AB:5000_SDO8": 4497, "AB:5000_SDI8_Packed": 1873,
    "AB:5000_DO8_Packed+AB:5000_SDO8_Packed": 3741, "AB:442G_MABB_E0JP4679": 3621,
    "FR:Safety_RobotPlus_8Bytes": 3745, "AB:ETHERNET_MODULE_SINT_12Bytes+AB:ETHERNET_MODULE_SINT_8Bytes": 3745,
    "AB:CIP_Drive_Safety2": 3578,
}


def test_the_batch_a_device_types_carry_their_measured_safety_cost():
    from l5x_memory_analyzer.sizing.constants import load_memory_model
    sio = load_memory_model().safety_io
    assert {k: sio.safety_bytes[k] for k in BATCH_A_SAFETY} == BATCH_A_SAFETY
    assert (sio.unseen_input_connection_bytes, sio.unseen_output_connection_bytes, sio.unseen_data_byte_bytes) == (
        1653, 1814, 16)


def test_a_catalog_with_two_safety_shapes_is_keyed_by_its_device_key_on_the_standard_side():
    from l5x_memory_analyzer.sizing.constants import load_memory_model
    from l5x_memory_analyzer.sizing.safety_io import SafetyDevice, standard_rows
    m = load_memory_model()
    two_conn = [SafetyDevice(f"C{i}", "1734-IB8S/B", ("AB:1734_IB8S", "AB:1734_IB8S_Safety2"), True) for i in range(2)]
    one_conn = [SafetyDevice(f"S{i}", "1734-IB8S/B", ("AB:1734_IB8S_Safety6",)) for i in range(2)]
    assert sum(r[3] for r in standard_rows(two_conn, m)) == 1013 - 2 * 416
    assert sum(r[3] for r in standard_rows(one_conn, m)) == 437 - 2 * 438
    # each a first device of its own key, whatever order they come in
    assert sum(r[3] for r in standard_rows(one_conn + two_conn, m)) == 1013 - 2 * 416 + 437 - 2 * 438
    # the revision-11 2198-D032-ERS3 (network STO) is its own key, not the catalog's 684
    rev11 = [SafetyDevice(f"K{i}", "2198-D032-ERS3", ("AB:CIP_Drive_Safety2",), True) for i in range(2)]
    assert sum(r[3] for r in standard_rows(rev11, m)) == 800 + 2 * 1184


def test_round_6_is_27_files_each_a_compiled_shape():
    import xml.etree.ElementTree as ET
    from sample_gen import gen_safety_round6 as R6
    from l5x_memory_analyzer.sizing.safety_io import device_key, safety_devices
    plan = {sid: kw for sid, _, kw in R6.plan()}
    assert len(plan) == 27 and not set(plan) & {sid for sid, _, _ in IO.plan()}
    keys = {}
    for sid, kw in plan.items():
        if not sid.startswith("safe_io6_"):
            continue
        l5x = R6.make(sid, kw)
        assert not lint_l5x(l5x), sid
        keys[sid] = {device_key(d) for d in safety_devices(ET.fromstring(l5x))}
    assert keys["safe_io6_ob8sa_2"] == {"AB:1734_OB8S+AB:1734_OB8S_Safety3"}
    assert keys["safe_io6_ib8s1c_1"] == {"AB:1734_IB8S_Safety6"}
    assert keys["safe_io6_442g_2"] == {"AB:442G_MABB_E0JP4679"}
    assert "<ConfigID>204</ConfigID>" in R6.make("safe_io6_ob8sa_1", plan["safe_io6_ob8sa_1"])
    # the standard 5069 cards: packed, as every real one is, and no safety device
    assert keys["safe_io6_5069_mix_2_2"] == set()
    mix = R6.make("safe_io6_5069_mix_2_2", plan["safe_io6_5069_mix_2_2"])
    assert mix.count("AB:5000_DI16_Packed:I:0") >= 4 and 'ProcessorType="5069-L330ERMS2"' in mix


def test_round_6_sil3_carries_its_partner_and_the_safety_message_tags_their_shape():
    from sample_gen import gen_safety_round6 as R6
    plan = {sid: kw for sid, _, kw in R6.plan()}
    sil3 = R6.make("safe_sil3_n00", plan["safe_sil3_n00"])
    assert 'SafetyLevel="SIL3/PLe"' in sil3 and 'CatalogNumber="1756-L8SP"' in sil3
    assert "<ConfigID>100</ConfigID><CatNum>1756-L8SP</CatNum>" in sil3
    both = R6.make("safe_pc6_both", plan["safe_pc6_both"])
    assert 'TagType="Produced"' in both and 'TagType="Consumed"' in both and 'CatalogNumber="5069-L306ERS2"' in both
    for sid in ("safe_sil3_n00", "safe_sil3_5069_ib8s_2", "safe_pc6_both", "safe_base_5069l310_v31"):
        assert not lint_l5x(R6.make(sid, plan[sid])), sid


def test_lint_refuses_a_safety_partner_without_its_configid():
    from sample_gen import gen_safety_round6 as R6
    plan = {sid: kw for sid, _, kw in R6.plan()}
    sil3 = R6.make("safe_sil3_n00", plan["safe_sil3_n00"])
    stripped = re.sub(r"<ExtendedProperties>\n<public><ConfigID>100</ConfigID><CatNum>1756-L8SP</CatNum></public>\n"
                      r"</ExtendedProperties>\n", "", sil3, count=1)
    assert stripped != sil3
    assert [f for f in lint_l5x(stripped) if f.kind == "safety_io_without_configid"]
