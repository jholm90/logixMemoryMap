"""OQ-SAFETYPARTITION, round 6: the safety I/O shapes the real safety programs carry that
round 5 did not build, each at 1 and 2 devices so its first-of-catalog and per-device
standard costs separate. The 1756-L81ES plant, v35, against safe_n00:

  safe_io6_ob8sa_<n>     n 1734-OB8S/A (Safety3, ConfigID 204: RS-06, RS-09) in a further
                         1734-AENTR/C rack
  safe_io6_ib8s1c_<n>    n 1734-IB8S/B with the SafetyInput connection only (Safety6:
                         RS-06, RS-09), beside round 5's safe_io_ib8s1c_4
  safe_io6_442g_<n>      n 442G-MABLB-UR-E0JP4679/A on the controller's Ethernet port
                         (RS-07)

Blocks are the repository's module-sweep blocks completed with the ExtendedProperties
every compiled export of the catalog carries (gen_safety_io.EXTENDED*), as in round 5.

What the safety figure still needs after those (OQ-SAFETYPARTITION, owner's direction
2026-10-20 that it be within a few percent): RS-01, RS-03, RS-17 (1756-L81ES) and RS-07
(5069-L320ERMS3) are SIL3, and nothing at SIL3 was ever measured; RS-03 / RS-17 carry a
safety produced and a safety consumed tag to a peer safety controller; RS-04 is v31.

  safe_sil3_n00, _step      1756-L81ES SIL3 with its 1756-L8SP partner, empty safety task; the
                            same with round 4's content step (50 safety DINTs, 10 RIN rungs)
  safe_sil3_ib8s_2 / _4     2 / 4 1734-IB8S/B in a rack at SIL3 (against safe_io_ib8s_2 / _4)
  safe_sil2_5069l320s3_n00  5069-L320ERMS3 v35 at SIL2: the catalog's own control
  safe_sil3_5069_n00, _step 5069-L320ERMS3 v35 at SIL3; with the content step
  safe_sil3_5069_ib8s_2     2 5069-IB8S/A on its bus at SIL3
  safe_pc6_def              the plant with a safety message UDT (CONNECTION_STATUS + DINT)
  safe_pc6_prod_1 / _2      1 / 2 safety Produced tags of it
  safe_pc6_peer             the UDT and a peer 5069-L306ERS2 safety controller in the I/O tree
  safe_pc6_cons_1 / _2      the peer and 1 / 2 safety Consumed tags from it
  safe_pc6_both             the peer, one Produced and one Consumed (as RS-03 / RS-17 carry them)
  safe_base_5069l310_v31, _content   5069-L310ERS2 v31 (RS-04's platform), the safety base
                            and round 4's content step (controller prefix SafeBase)

The standard 5069 cards those programs carry on the controller's own bus, packed data as
every real one is (RS-05 and RS-08 two 5069-IB16/A and two 5069-OB16/B, RS-10 three of
each): the module-type sharing law (OQ-MODREPEAT) discounts a second card's packed types
and was fitted on standard-data cards in 5069-AENTR racks. A packed card exists only on a
5069 controller's bus, so these sit on round 4's 5069-L330ERMS2 v35 safety base:

  safe_io6_5069_ib16_<n>    n = 1 / 2 5069-IB16/A, the module-sweep block
  safe_io6_5069_ob16_1      one 5069-OB16/B
  safe_io6_5069_mix_2_2     two of each, as RS-05 / RS-08 carry them

Run: python -m sample_gen.gen_safety_round6 [--only REGEX]
"""

from __future__ import annotations

import re

from sample_gen import gen_safety_io as IO
from sample_gen import gen_safety_partition as G
from sample_gen import gen_safety_round2 as R
from sample_gen import gen_safety_round4 as R4
from sample_gen.builders import MemberSpec, udt_xml
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x, safety_partner_module_xml

OQ = "OQ-SAFETYPARTITION"


def plan() -> list[tuple[str, str, dict]]:
    files: list[tuple[str, str, dict]] = []
    for n in (1, 2):
        files.append((f"safe_io6_ob8sa_{n}", f"{n} 1734-OB8S/A (series A, SafetyInput + SafetyOutput) in a further "
                      "1734-AENTR/C rack", {"racks": [["ob8sa"] * n]}))
        files.append((f"safe_io6_ib8s1c_{n}", f"{n} 1734-IB8S/B with the SafetyInput connection only, beside "
                      "round 5's safe_io_ib8s1c_4", {"racks": [["ib8s1c"] * n]}))
        files.append((f"safe_io6_442g_{n}", f"{n} 442G-MABLB-UR-E0JP4679/A on the L81ES Ethernet port",
                      {"ethernet": ["442g"] * n}))
    files = [(sid, f"{desc}, 1756-L81ES v35 plant, against safe_n00", kw) for sid, desc, kw in files]
    sil3 = [
        ("safe_sil3_n00", "1756-L81ES v35 at SIL3 with its 1756-L8SP partner, empty safety task, plant; against "
                          "safe_n00 (SIL2)", {"sil3": "1756", "content": False}),
        ("safe_sil3_step", "the same with round 4's content step (50 safety DINTs, 10 RIN rungs)",
         {"sil3": "1756", "content": True}),
        ("safe_sil3_ib8s_2", "SIL3 L81ES with 2 1734-IB8S/B in a further rack; against safe_io_ib8s_2",
         {"sil3": "1756", "content": False, "racks": [["ib8s"] * 2]}),
        ("safe_sil3_ib8s_4", "SIL3 L81ES with 4 1734-IB8S/B in a further rack; against safe_io_ib8s_4",
         {"sil3": "1756", "content": False, "racks": [["ib8s"] * 4]}),
        ("safe_sil2_5069l320s3_n00", "5069-L320ERMS3 v35 at SIL2, empty safety task, plant: the catalog's control",
         {"base": "5069-L320ERMS3", "level": "SIL2", "major": "35", "content": False}),
        ("safe_sil3_5069_n00", "5069-L320ERMS3 v35 at SIL3, empty safety task, plant",
         {"base": "5069-L320ERMS3", "level": "SIL3", "major": "35", "content": False}),
        ("safe_sil3_5069_step", "5069-L320ERMS3 v35 at SIL3 with round 4's content step",
         {"base": "5069-L320ERMS3", "level": "SIL3", "major": "35", "content": True}),
        ("safe_sil3_5069_ib8s_2", "5069-L320ERMS3 v35 at SIL3 with 2 5069-IB8S/A on its bus",
         {"base": "5069-L320ERMS3", "level": "SIL3", "major": "35", "content": False, "local": ["5069ib8s"] * 2}),
        ("safe_base_5069l310_v31", "5069-L310ERS2 v31 (RS-04's platform), the safety base on the plant",
         {"base": "5069-L310ERS2", "level": "SIL2", "major": "31", "content": False}),
        ("safe_base_5069l310_v31_content", "5069-L310ERS2 v31 with round 4's content step",
         {"base": "5069-L310ERS2", "level": "SIL2", "major": "31", "content": True}),
    ]
    pc = [
        ("safe_pc6_def", "the L81ES plant with a safety message UDT (CONNECTION_STATUS + DINT), no tag of it",
         {"pc": {"peer": False, "prod": 0, "cons": 0}}),
        ("safe_pc6_prod_1", "and one safety Produced tag of it", {"pc": {"peer": False, "prod": 1, "cons": 0}}),
        ("safe_pc6_prod_2", "and two safety Produced tags of it", {"pc": {"peer": False, "prod": 2, "cons": 0}}),
        ("safe_pc6_peer", "the UDT and a peer 5069-L306ERS2 safety controller in the I/O tree",
         {"pc": {"peer": True, "prod": 0, "cons": 0}}),
        ("safe_pc6_cons_1", "the peer and one safety Consumed tag from it", {"pc": {"peer": True, "prod": 0, "cons": 1}}),
        ("safe_pc6_cons_2", "the peer and two safety Consumed tags from it", {"pc": {"peer": True, "prod": 0, "cons": 2}}),
        ("safe_pc6_both", "the peer, one safety Produced and one safety Consumed tag",
         {"pc": {"peer": True, "prod": 1, "cons": 1}}),
    ]
    l330 = {"base": "5069-L330ERMS2", "level": "SIL2", "major": "35", "content": False}
    std = [
        ("safe_io6_5069_ib16_1", "one standard 5069-IB16/A (packed data, the module-sweep block)", ["5069-IB16/A"]),
        ("safe_io6_5069_ib16_2", "two standard 5069-IB16/A", ["5069-IB16/A"] * 2),
        ("safe_io6_5069_ob16_1", "one standard 5069-OB16/B (packed data, the module-sweep block)", ["5069-OB16/B"]),
        ("safe_io6_5069_mix_2_2", "two 5069-IB16/A and two 5069-OB16/B, as RS-05 / RS-08 carry them",
         ["5069-IB16/A", "5069-IB16/A", "5069-OB16/B", "5069-OB16/B"]),
    ]
    std = [(sid, f"{desc} on a 5069-L330ERMS2 v35's own bus (OQ-MODREPEAT), against safe_base_5069l330_v35",
            dict(l330, std_local=cards)) for sid, desc, cards in std]
    return [(sid, f"{OQ}: {desc}", kw) for sid, desc, kw in files + sil3 + pc + std]


def std_card(catalog: str, name: str, slot: int) -> str:
    """A standard 5069 card's module-sweep block on the controller's own bus, renamed and
    re-slotted."""
    from sample_gen.gen_module_sweep import _MODULE_CHAINS
    block = re.sub(r'Name="[^"]+"', f'Name="{name}"', _MODULE_CHAINS[catalog][0], count=1)
    return re.sub(r'(<Port Id="1" Address=")\d+(" Type="5069" Upstream="true")', rf"\g<1>{slot}\g<2>", block, count=1)


SAFE_MSG = "SafeMsg"
SAFE_MSG_MEMBERS = [MemberSpec("CommsStatus", "CONNECTION_STATUS"), MemberSpec("Data", "DINT")]
PEER = "SafePeer"


def _safe_msg_data(run_mode: int) -> str:
    return (f'<Data Format="L5K">\n<![CDATA[[[{run_mode}],0]]]>\n</Data>\n<Data Format="Decorated">\n'
            f'<Structure DataType="{SAFE_MSG}">\n<StructureMember Name="CommsStatus" DataType="CONNECTION_STATUS">\n'
            f'<DataValueMember Name="RunMode" DataType="BOOL" Value="{run_mode}"/>\n'
            f'<DataValueMember Name="ConnectionFaulted" DataType="BOOL" Value="0"/>\n</StructureMember>\n'
            f'<DataValueMember Name="Data" DataType="DINT" Radix="Decimal" Value="0"/>\n</Structure>\n</Data>')


def produced_tag(name: str) -> str:
    """A safety Produced tag as compiled exports carry it (ProduceInfo, both Data forms)."""
    return (f'<Tag Name="{name}" Class="Safety" TagType="Produced" DataType="{SAFE_MSG}" Constant="false" '
            f'ExternalAccess="Read/Write">\n<ProduceInfo ProduceCount="1" ProgrammaticallySendEventTrigger="true" '
            f'UnicastPermitted="true"/>\n{_safe_msg_data(0)}\n</Tag>')


def consumed_tag(name: str, remote: str) -> str:
    """A safety Consumed tag from the peer, ConsumeInfo as compiled exports carry it."""
    return (f'<Tag Name="{name}" Class="Safety" TagType="Consumed" DataType="{SAFE_MSG}" ExternalAccess="Read/Write">\n'
            f'<ConsumeInfo Producer="{PEER}" RemoteTag="{remote}" RemoteInstance="0" RPI="20" TimeoutMultiplier="2" '
            f'NetworkDelayMultiplier="200" ReactionTimeLimit="80" MaxObservedNetworkDelay="0" Unicast="true"/>\n'
            f'{_safe_msg_data(1)}\n</Tag>')


def peer_module() -> str:
    """A peer safety controller in the I/O tree: no connections of its own; Ports and the
    profile's ExtendedProperties as a compiled export carries a 5069-L306ERS2 there."""
    return (f'<Module Name="{PEER}" CatalogNumber="5069-L306ERS2" Vendor="1" ProductType="14" ProductCode="235" '
            f'Major="35" Minor="11" ParentModule="Local" ParentModPortId="2" Inhibited="false" MajorFault="false" '
            f'SafetyNetwork="16#0000_4c3a_0291_5e17">\n<EKey State="CompatibleModule"/>\n<Ports>\n'
            f'<Port Id="1" Type="5069" Upstream="false">\n<Bus Size="32"/>\n</Port>\n'
            f'<Port Id="2" Address="192.168.1.90" Type="Ethernet" Upstream="true"/>\n</Ports>\n<ExtendedProperties>\n'
            f'<public><ConfigID>100</ConfigID><CatNum>5069-L306ERS2</CatNum></public>\n</ExtendedProperties>\n</Module>')


def _sil3_1756(sample_id: str, content: bool) -> str:
    name = "SafePart" + "".join(w.capitalize() for w in sample_id.split("_")[1:])
    tags, rungs = G.instruction_pair("RIN", 10) if content else ([], [])
    arm = {"extra_programs_xml": R._program(R.MAIN, tags, [("MainRoutine", rungs)]),
           "extra_tasks_xml": R._task([R.MAIN]),
           "tags_xml": "\n".join(R.ctl_tag(f"SafeDint{i:04d}", "DINT") for i in range(50)) if content else "",
           "extra_modules_xml": safety_partner_module_xml(name)}
    l5x = build_l5x(name, processor_type=G.PROCESSOR, safety_level="SIL3", **with_baseline(**arm))
    return l5x.replace('ConfigureSafetyIOAlways="true"', 'ConfigureSafetyIOAlways="false"', 1)


def _base(sample_id: str, processor: str, level: str, major: str, content: bool) -> str:
    """round 4's build_base at a chosen safety level (the round 4 bases are all SIL2)."""
    name = "SafeBase" + "".join(w.capitalize() for w in sample_id.split("_")[1:])
    software = {"35": "35.05", "31": "31.02"}[major]
    l5x = R4.build_base(name, processor, major, software, content)
    if level == "SIL3":
        l5x = l5x.replace('SafetyLevel="SIL2/PLd"', 'SafetyLevel="SIL3/PLe"', 1)
    return l5x


def make(sample_id: str, kw: dict) -> str:
    if "sil3" in kw:
        l5x = _sil3_1756(sample_id, kw["content"])
    elif "base" in kw:
        l5x = _base(sample_id, kw["base"], kw["level"], kw["major"], kw["content"])
    elif "pc" in kw:
        pc = kw["pc"]
        tags = ([produced_tag(f"SafeOut{i + 1}") for i in range(pc["prod"])]
                + [consumed_tag(f"SafeIn{i + 1}", f"PeerOut{i + 1}") for i in range(pc["cons"])])
        l5x = R.build(sample_id, controller_tags=tags, datatypes_xml=udt_xml(SAFE_MSG, SAFE_MSG_MEMBERS))
        return IO.with_modules(l5x, [peer_module()] if pc["peer"] else [])
    else:
        l5x = R.build(sample_id)
    modules: list[str] = []
    if "std_local" in kw:
        modules += [std_card(c, f"Std{'In' if 'IB' in c else 'Out'}{slot}", slot)
                    for slot, c in enumerate(kw["std_local"], start=1)]
    if "local" in kw:
        snn = IO.local_snn(l5x, "1")
        modules += [IO.place(IO.TEMPLATES[k], None, "Local", "1", slot, snn) for slot, k in enumerate(kw["local"], start=1)]
    for i, cards in enumerate(kw.get("racks", [])):
        modules += IO.rack(f"SRACK_{i + 1}", f"192.168.1.{200 + i}", IO.RACK_SNN[i], cards)
    if "ethernet" in kw:
        snn = IO.local_snn(l5x, "2")
        for i, kind in enumerate(kw["ethernet"]):
            block = IO.place(IO.TEMPLATES[kind], f"SafeDev{i + 1}", "Local", "2", 0, snn)
            modules.append(re.sub(r'Address="192\.168\.1\.\d+"', f'Address="192.168.1.{70 + i}"', block, count=1))
    return IO.with_modules(l5x, modules)


def _make(job: tuple[str, dict]) -> int:
    sample_id, kw = job
    return write_sample(make(sample_id, kw), G.OUT_ROOT / f"{sample_id}.L5X")


def main() -> None:
    import argparse
    from sample_gen.progress import run
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", metavar="REGEX", help="build only the sample_ids this matches")
    args = ap.parse_args()
    jobs = [j for j in plan() if not args.only or re.search(args.only, j[0])]
    predicted = run(((sid, (sid, kw)) for sid, _, kw in jobs), _make, label="safety-r6")
    for sample_id, description, _ in jobs:
        append_manifest_row(sample_id, description, G.CATEGORY, G.OUT_ROOT / f"{sample_id}.L5X", predicted[sample_id])


if __name__ == "__main__":
    main()
