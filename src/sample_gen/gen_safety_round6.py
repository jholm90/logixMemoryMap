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

Run: python -m sample_gen.gen_safety_round6
"""

from __future__ import annotations

import re

from sample_gen import gen_safety_io as IO
from sample_gen import gen_safety_partition as G
from sample_gen import gen_safety_round2 as R
from sample_gen.manifest import append_manifest_row, write_sample

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
    return [(sid, f"{OQ}: {desc}, 1756-L81ES v35 plant, against safe_n00", kw) for sid, desc, kw in files]


def make(sample_id: str, kw: dict) -> str:
    l5x = R.build(sample_id)
    modules: list[str] = []
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
    from sample_gen.progress import run
    jobs = plan()
    predicted = run(((sid, (sid, kw)) for sid, _, kw in jobs), _make, label="safety-r6")
    for sample_id, description, _ in jobs:
        append_manifest_row(sample_id, description, G.CATEGORY, G.OUT_ROOT / f"{sample_id}.L5X", predicted[sample_id])


if __name__ == "__main__":
    main()
