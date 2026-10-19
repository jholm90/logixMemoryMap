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


def test_every_file_lints_clean():
    for sid, kw in _plan().items():
        assert not lint_l5x(IO.make(sid, kw)), sid


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
