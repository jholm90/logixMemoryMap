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


def test_a_safety_device_is_priced_by_its_connections_types_and_only_when_measured():
    from l5x_memory_analyzer.sizing.constants import load_memory_model
    from l5x_memory_analyzer.sizing.safety_io import SafetyDevice, safety_rows, standard_rows
    m = load_memory_model()
    drives = [SafetyDevice(f"D{i}", "2198-D032-ERS3", ("AB:CIP_Motion_Device_Safety2",)) for i in range(3)]
    card = SafetyDevice("C", "1734-IB8S/B", ("AB:1734_IB8S", "AB:1734_IB8S_Safety2"))
    rows, unpriced = safety_rows(drives + [card], m)
    assert sum(r[3] for r in rows) == 3 * 4717
    assert unpriced == {"AB:1734_IB8S+AB:1734_IB8S_Safety2": 1}
    # standard: the type's first-device cost once, then each drive its own
    assert sum(r[3] for r in standard_rows(drives, m)) == 4160 + 3 * 684
    pair = [SafetyDevice("I", "1756-IB16S/A", ("AB:5000_SDI16",)), SafetyDevice("O", "1756-OBV8S/A", ("AB:5000_SDO8",))]
    assert sum(r[3] for r in standard_rows(pair, m)) == 368 + 1832 + 1104 - 2 * 917


def test_round_6_is_6_files_each_a_compiled_shape():
    import xml.etree.ElementTree as ET
    from sample_gen import gen_safety_round6 as R6
    from l5x_memory_analyzer.sizing.safety_io import device_key, safety_devices
    plan = {sid: kw for sid, _, kw in R6.plan()}
    assert len(plan) == 6 and not set(plan) & {sid for sid, _, _ in IO.plan()}
    keys = {}
    for sid, kw in plan.items():
        l5x = R6.make(sid, kw)
        assert not lint_l5x(l5x), sid
        keys[sid] = {device_key(d) for d in safety_devices(ET.fromstring(l5x))}
    assert keys["safe_io6_ob8sa_2"] == {"AB:1734_OB8S+AB:1734_OB8S_Safety3"}
    assert keys["safe_io6_ib8s1c_1"] == {"AB:1734_IB8S_Safety6"}
    assert keys["safe_io6_442g_2"] == {"AB:442G_MABB_E0JP4679"}
    assert "<ConfigID>204</ConfigID>" in R6.make("safe_io6_ob8sa_1", plan["safe_io6_ob8sa_1"])
