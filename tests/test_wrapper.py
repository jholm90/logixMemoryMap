"""James, 2026-08-31: "You made many working l71 filed before this failed
test, why did you generate this failed ethernet port? These should be
caught with your validation scripts better."

Real answer: this project has TWO independent XML-building
implementations that both know how to shape a 1756-L71 project --
wrapper.py's build_l5x() (shared default path, used by gen_blockbyte_l71.py
and most other generators) and gen_fw_catalog_matrix.py's own _build_xml()/
_local_ports_xml() (a separate, parallel implementation). The "no embedded
Ethernet on 1756-L7x" bug was found and fixed in gen_fw_catalog_matrix.py
on 2026-08-28 (commit 378f929) -- BEFORE gen_blockbyte_l71.py was even
written (commit bd67504) -- but the fix never got ported to wrapper.py,
so the same real fact had to be rediscovered the hard way when James ran
blockbytetest_l71_dint120000.L5X through real Studio 5000.

These tests exist so that can't happen silently again: they cross-check
wrapper.py's shape for 1756-L71 against gen_fw_catalog_matrix.py's
independently-derived shape (both ultimately sourced from the same real
reference export, samples/local/L7_v21_Sample.L5X) and fail loudly if the
two ever diverge, instead of waiting for a real Studio 5000 rejection to
notice.
"""

from sample_gen.gen_fw_catalog_matrix import _local_ports_xml, _product_code
from sample_gen.wrapper import build_l5x


def test_1756_l71_has_no_embedded_ethernet_port():
    l5x = build_l5x(target_name="Test", tags_xml="", processor_type="1756-L71")
    # No embedded Ethernet Port on the Local module...
    assert 'Type="Ethernet"' not in l5x.split("<Programs>")[0].split("<AddOnInstructionDefinitions>")[0]
    # ...and no Controller-level EthernetPorts element describing one.
    assert "<EthernetPorts>" not in l5x


def test_1756_l71_local_ports_match_fw_catalog_matrix_implementation():
    """The two independent implementations must agree -- if one changes
    without the other, this fails instead of shipping a divergent file."""
    l5x = build_l5x(target_name="Test", tags_xml="", processor_type="1756-L71")
    modules_block = l5x.split("<Modules>")[1].split("</Modules>")[0]
    fw_matrix_ports_xml = _local_ports_xml("1756-L71")
    assert fw_matrix_ports_xml.replace("\n", "") in modules_block.replace("\n", "")


def test_1756_l71_product_code_matches_fw_catalog_matrix_implementation():
    l5x = build_l5x(target_name="Test", tags_xml="", processor_type="1756-L71")
    assert f'ProductCode="{_product_code("1756-L71")}"' in l5x
