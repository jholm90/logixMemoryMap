"""OQ-BRIDGEPH: a bridge with nothing beneath it is priced at its measured
node overhead, with no coverage notice; a rack-aliased POINT I/O card is priced
and carries no notice either."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from l5x_memory_analyzer.sizing.constants import load_memory_model  # noqa: E402
from l5x_memory_analyzer.sizing.report import build_report  # noqa: E402
from sample_gen.gen_bridge_placeholder import ethernet_bridge_xml  # noqa: E402
from sample_gen.realism import rack_xml  # noqa: E402
from sample_gen.wrapper import build_l5x  # noqa: E402

MODEL = load_memory_model()


def _modules(xml: str) -> tuple[dict[str, int], list]:
    entries, errors = build_report(ET.fromstring(
        build_l5x(target_name="BridgeT", tags_xml="", extra_modules_xml=xml)), MODEL)
    return {e.path: e.bytes for e in entries if e.path.startswith("modules/")}, errors


_GATEWAY_EN2T = (
    '<Module Name="Gateway" CatalogNumber="1756-EN2T" Vendor="1" ProductType="12" '
    'ProductCode="166" Major="11" Minor="2" ParentModule="Local" ParentModPortId="1" '
    'Inhibited="false" MajorFault="false"><EKey State="CompatibleModule"/><Ports>'
    '<Port Id="1" Address="1" Type="ICP" Upstream="true"/>'
    '<Port Id="2" Address="10.10.0.10" Type="Ethernet" Upstream="false"><Bus/></Port></Ports>'
    '<Communications CommMethod="536870914"><Connections/></Communications></Module>')


def test_childless_ethernet_bridge_takes_its_measured_rate_silently():
    mods, errors = _modules(ethernet_bridge_xml("BrPh01", "192.168.1.201", True))
    assert list(mods.values()) == [MODEL.zero_connection_by_catalog["ETHERNET-BRIDGE"][0]]
    assert not errors


def test_a_gateway_en2t_keeps_the_flat_rate_and_its_notice():
    mods, errors = _modules(_GATEWAY_EN2T)
    assert list(mods.values()) == [MODEL.zero_connection_module_bytes]
    assert [e.path for e in errors] == ["coverage/module_zero_connection/Gateway"]


def test_a_bridge_with_a_device_beneath_it_keeps_the_flat_rate():
    child = ('<Module Name="Behind" CatalogNumber="ETHERNET-MODULE" Vendor="1" ProductType="0" '
             'ProductCode="0" Major="1" Minor="1" ParentModule="BrPh01" ParentModPortId="1" '
             'Inhibited="false" MajorFault="false"><EKey State="Disabled"/><Ports>'
             '<Port Id="1" Type="CIPBus" Upstream="true"/></Ports></Module>')
    mods, _ = _modules(ethernet_bridge_xml("BrPh01", "192.168.1.201", True) + "\n" + child)
    assert any(v == MODEL.zero_connection_module_bytes for k, v in mods.items() if "BrPh01" in k)


def test_rack_aliased_pointio_cards_are_priced_without_a_notice():
    mods, errors = _modules(rack_xml("RACK_9", "192.168.1.109"))
    assert len(mods) == 9
    assert not [e for e in errors if "module_unmodeled_shape" in e.path]
