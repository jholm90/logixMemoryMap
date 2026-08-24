"""1756-Ethernet LOCAL rack talking to a REMOTE 1756-Ethernet rack that
carries its own remote 1756 I/O modules (2026-08-27, James: "I also want to
see... 1756-Ethernet that talks to another 1756-Ethernet rack that has
remote 1756 io modules").

**Honesty note, unlike every other file in the module sweep:** this
specific topology is a SYNTHESIS of two independently real, corpus-
confirmed pieces, not one literal real chain extracted whole (the usual
"never invent" bar for this project). Checked first, not guessed:
  1. The bridge-to-bridge linkage syntax IS real and literal, pulled
     verbatim from samples/local/L5X_Samples/RobbinsGrn_2026_05_13r00.L5X
     ("Control_Ethernet" 1756-ENBT/A at ParentModule="Local", "MoCo_Stacker"
     1756-ENBT/A at ParentModule="Control_Ethernet" ParentModPortId="2" --
     a second bridge networked off the first one's Ethernet port, with its
     OWN real `<Bus Size="13"/>` on its own backplane Port, confirming the
     remote module IS modeled as having its own real chassis with room for
     children).
  2. `ParentModule=<remote bridge>`/`ParentModPortId="1"`/`Type="ICP"` for a
     module living on that remote bridge's own backplane is the exact same
     real syntax every local-rack module already uses (gen_module_sweep.py)
     -- Rockwell's L5X addressing scheme doesn't distinguish "local" vs
     "remote" chassis syntactically, only by which module Name sits in
     ParentModule.
  Searched the full real corpus for a literal example of #1 and #2
  combined (a remote bridge with real I/O children, not just a peer
  controller) -- none exists in the 63 real files on hand (every real
  EN-under-EN case found only has a PROCESSOR as the remote child, i.e. a
  peer PLC on the network, not a remote I/O chassis). Nothing here is
  invented syntax, but the specific combination is assembled, not
  attested as one real file -- flagged here and in OQ-MODULEIO so it's
  never mistaken for the same confidence level as the rest of the sweep.

Local side: 1756-ENBT/A "noconn" shape (real, gen_module_sweep_variants.py
-- a plain local bridge, no local rack-optimized children) plus 2 real
local 1756 I/O modules (reused from gen_module_sweep.py) for a realistic
local rack, not just a bare bridge. Remote side: a second 1756-ENBT/A
(the real Control_Ethernet/MoCo_Stacker linkage shape above) with 4 real
1756 I/O modules reused from gen_module_sweep.py as its remote children,
ParentModule redirected and re-slotted onto the remote chassis's own
13-slot bus (Bus Size="13", matching the real MoCo_Stacker value).

Run: python -m sample_gen.gen_module_rack_1756remote
"""

from __future__ import annotations

import re
from pathlib import Path

from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.gen_module_sweep_variants import _MODULE_VARIANTS
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

_PORT_RE = re.compile(r'(<Port Id="1" Address=")\d+(" Type="ICP" Upstream="true" ?/>)')
_NAME_RE = re.compile(r'(<Module Name=")[^"]+(")')
_PARENT_RE = re.compile(r'(ParentModule=")[^"]+(")')

_LOCAL_IO_CATALOGS = ["1756-IB16", "1756-IF8/A"]
_REMOTE_IO_CATALOGS = ["1756-OA16", "1756-OF4/A", "1756-IA32/A", "1756-HSC/A"]

# Real, literal -- RobbinsGrn's own "Control_Ethernet" (local bridge).
_LOCAL_BRIDGE_XML = """\
<Module Name="RemoteTest_LocalBridge" CatalogNumber="1756-ENBT/A" Vendor="1" ProductType="12" ProductCode="58" Major="3" Minor="9" ParentModule="Local" ParentModPortId="1" Inhibited="false" MajorFault="false">
<EKey State="Disabled" />
<Ports>
<Port Id="1" Address="16" Type="ICP" Upstream="true" />
<Port Id="2" Address="192.168.1.100" Type="Ethernet" Upstream="false">
<Bus />
</Port>
</Ports>
</Module>
"""

# Real, literal -- RobbinsGrn's own "MoCo_Stacker" (remote bridge, networked
# off the local bridge's port 2, its own real 13-slot backplane Bus).
_REMOTE_BRIDGE_XML = """\
<Module Name="RemoteTest_RemoteBridge" CatalogNumber="1756-ENBT/A" Vendor="1" ProductType="12" ProductCode="58" Major="1" Minor="1" ParentModule="RemoteTest_LocalBridge" ParentModPortId="2" Inhibited="true" MajorFault="false">
<EKey State="Disabled" />
<Ports>
<Port Id="1" Address="2" Type="ICP" Upstream="false">
<Bus Size="13" />
</Port>
<Port Id="2" Address="192.168.1.101" Type="Ethernet" Upstream="true" />
</Ports>
<Communications CommMethod="536870914">
<Connections />
</Communications>
</Module>
"""


def _reslot_local(xml: str, slot: int, new_name: str) -> str:
    xml = _PORT_RE.sub(rf"\g<1>{slot}\g<2>", xml, count=1)
    xml = _NAME_RE.sub(rf"\g<1>{new_name}\g<2>", xml, count=1)
    return xml


def _reslot_remote(xml: str, slot: int, new_name: str, parent: str) -> str:
    xml = _PORT_RE.sub(rf"\g<1>{slot}\g<2>", xml, count=1)
    xml = _NAME_RE.sub(rf"\g<1>{new_name}\g<2>", xml, count=1)
    xml = _PARENT_RE.sub(rf"\g<1>{parent}\g<2>", xml, count=1)
    return xml


def main() -> None:
    blocks = [_LOCAL_BRIDGE_XML, _REMOTE_BRIDGE_XML]

    local_slot = 1
    for catalog in _LOCAL_IO_CATALOGS:
        xml, source, chain_len = _MODULE_CHAINS[catalog]
        slug = "".join(c if c.isalnum() else "" for c in catalog)
        blocks.append(_reslot_local(xml, local_slot, f"RemoteTest_Local_{slug}"))
        local_slot += 1

    remote_slot = 3  # remote bridge itself sits at slot 2 on its own bus
    for catalog in _REMOTE_IO_CATALOGS:
        xml, source, chain_len = _MODULE_CHAINS[catalog]
        slug = "".join(c if c.isalnum() else "" for c in catalog)
        blocks.append(_reslot_remote(xml, remote_slot, f"RemoteTest_Remote_{slug}", "RemoteTest_RemoteBridge"))
        remote_slot += 1

    xml = "\n".join(blocks)
    l5x = build_l5x(target_name="Rack1756Remote", tags_xml="", extra_modules_xml=xml)
    out_path = OUT_ROOT / "modulerack_1756_remote.L5X"
    write_sample_unmodeled(l5x, out_path)
    append_manifest_row(
        "modulerack_1756_remote",
        "1756-Ethernet local rack (2 real local I/O modules + real ENBT/A local bridge) "
        "talking over Ethernet to a REMOTE 1756-Ethernet rack (real ENBT/A remote bridge "
        "shape, verbatim from RobbinsGrn's Control_Ethernet/MoCo_Stacker linkage) carrying "
        "4 real remote 1756 I/O modules on its own 13-slot backplane. SYNTHESIZED from two "
        "independently real, corpus-confirmed pieces -- no single real file in the corpus "
        "shows a remote bridge with real I/O children (only peer-controller cases found). "
        "See this generator's own docstring and OQ-MODULEIO for the honesty caveat.",
        "modules", out_path, 0,
    )
    print("Done. 1 remote-rack file written (2 bridges + 6 I/O modules).")


if __name__ == "__main__":
    main()
