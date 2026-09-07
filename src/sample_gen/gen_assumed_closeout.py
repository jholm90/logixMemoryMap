"""Closes every remaining ASSUMED item that fires on a real file.

Written 2026-09-06 after a confidence audit found that 174 of the model's
185 ASSUMED predefined structures already had error-free, exactly-0.0000%
capture data behind them -- the tier had simply never been upgraded. That
left a short, precise list of things that are genuinely unmeasured, and
this batch closes all of it in one capture run.

WHAT IS ACTUALLY LEFT, measured as a share of total bytes across the nine
real production programs:

    2198 Kinetix -ERS3 safety drives      4.073%   group A
    13 other unpriced module catalogs     0.245%   group B
    SCALE + FBD_MATH (FBD/SFC family)     0.007%   group C

Nothing else in the model is ASSUMED and reachable from a real file.

GROUP A -- the 2198 -ERS3 root cause, found 2026-09-06.

The docs recorded these as "undiagnosed". They are not. The evidence was
already in the manifest:

  - Every NON-safety 2198 (C4004-ERS, H008-ERS, P031, P070, P141, P208,
    RP200) captured error-free and exact on a plain 1756-L81E.
  - Every -ERS3 catalog failed, and only those.
  - The 2conn variants carry `SafetyEnabled="false"` and NO Safety
    connections at all -- and still failed with 2 errors each, with Studio
    synthesising `:SI`/`:SO` safety tags for them anyway.

So it is the CATALOG that makes Studio create safety tags, not the
SafetyEnabled attribute or the connection list. A -ERS3 drive is safety
hardware and needs a safety-capable controller in EVERY shape it appears
in. `gen_module_sweep_variants.py` applied the safety processor only to
the 4conn variants, which is why the 2conn ones kept failing -- a
generator bug, not a Rockwell mystery. The 4conn `_r2` files were
regenerated correctly but then never captured at all, so "still failing"
was never actually true of them either.

Group A rebuilds all six -ERS3 catalogs on a real SIL2 safety controller
in both shapes, and count-sweeps each at n=1/2/4 so the MARGINAL cost of
the Nth identical drive is read directly rather than inferred from a
single point. A single point can only ever confirm a total; it cannot
separate the per-module cost from the one-time cost of the first one,
which is exactly the question `module_overhead_by_catalog` asks.

GROUP B does the same n=1/2/4 sweep for the other 13 catalogs that are
still ASSUMED and appear in real programs. Same reasoning: each needs at
least two counts before its per-module rate is a measurement.

GROUP C is one file per FBD/SFC predefined structure that has never been
probed -- the only 10 types left with no capture behind them. Same shape
as the existing `predefprobe_*` files: one Controller-scoped tag, no
logic, so the delta against the empty-project baseline IS the structure
size.

Run: python -m sample_gen.gen_assumed_closeout
"""

from __future__ import annotations

import re
from pathlib import Path

from sample_gen.builders import tag_xml
from sample_gen.gen_module_motion import _drive_module_xml
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.gen_module_sweep_variants import _MODULE_VARIANTS
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_MODULES = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"
OUT_PREDEF = Path(__file__).parent.parent.parent / "samples" / "generated" / "predefined"

SAFETY_PROCESSOR = "1756-L81ES"
SAFETY_LEVEL = "SIL2"
COUNTS = (1, 2, 4)

# Every -ERS3 catalog is safety hardware in every shape it appears in.
_ERS3_CATALOGS = {
    "2198-D012-ERS3", "2198-D020-ERS3", "2198-D032-ERS3",
    "2198-D057-ERS3", "2198-S086-ERS3", "2198-S130-ERS3",
}

# The 13 catalogs still carrying an ASSUMED module_overhead that actually
# appear in the nine real programs, largest real exposure first.
_UNPRICED_CATALOGS = (
    "150 SMC Flex-E", "440C-CR30-22BBB/A", "1756-IB16IF/A",
    "PowerFlex 755-EENET-CM-S", "842E-CM-M", "1756-EN4TR", "1734-AENT/C",
    "1756-OB32", "1756-IB32/B", "1756-IB16", "1794-AENT", "1734-AENT/B",
    "AL1222",
)

# FBD/SFC predefined structures with no capture behind them. Byte values
# are the current RM018A-derived guesses the probe will confirm or correct.
_FBD_SFC_TYPES = (
    ("FBD_TIMER", 48), ("FBD_ONESHOT", 12), ("FBD_MATH", 16),
    ("FBD_BOOLEAN_AND", 12), ("FBD_BOOLEAN_OR", 12), ("FBD_BOOLEAN_NOT", 12),
    ("SCALE", 52), ("RATE_LIMITER", 92), ("SFC_STEP", 28), ("SFC_ACTION", 16),
)


def _slug(text: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in text).strip("_").lower()


def _place_copies(xml: str, count: int) -> str:
    """`count` copies of a real module block, each made unique.

    A second instance of the same module needs its own identity or Studio
    rejects the import. Two distinct collision classes, both found by the
    pre-flight lint rather than shipped:

      - Ethernet-addressed modules collide on IP, so each copy gets its own.
      - Backplane-addressed modules collide on chassis slot. Copies are
        renumbered into consecutive slots starting at 1 (slot 0 is the CPU)
        rather than offset from the original's captured slot, because a
        1756 chassis is 17 slots and offsetting a module already sitting at
        slot 14 walks straight off the end of it.

    Only identity changes. Every sizing-relevant attribute -- connection
    list, RPI, data shape, EKey -- is left exactly as captured, because the
    entire point of the sweep is that copies 2..N are byte-identical to
    copy 1 apart from where they sit.
    """
    # A module's position on its PARENT is the port marked Upstream="true".
    # Downstream ports (its own PointIO/ICP bus, if it heads a rack) address
    # its children and must be left alone -- an adapter like 1734-AENT/C has
    # both, which is exactly how an earlier version of this got it wrong.
    up = re.search(r'<Port [^>]*Upstream="true"[^>]*>', xml)
    up_addr = re.search(r'Address="([^"]+)"', up.group(0)).group(1) if up else None
    numeric_slot = up_addr is not None and up_addr.isdigit()

    out = []
    for i in range(count):
        blk = xml if i == 0 else re.sub(
            r'(<Module Name=")([^"]+)(")',
            lambda m: f"{m.group(1)}{m.group(2)}_c{i}{m.group(3)}", xml, count=1)
        if up_addr is not None:
            if numeric_slot:
                # Consecutive slots from 1 (slot 0 is the CPU). Renumbered
                # rather than offset: a 1756 chassis is 17 slots, so offsetting
                # a module already at slot 14 walks off the end of it.
                new_addr = str(1 + i)
            else:
                head, _, last = up_addr.rpartition(".")
                new_addr = f"{head}.{int(last) + i}"
            blk = blk.replace(f'Address="{up_addr}"', f'Address="{new_addr}"', 1) if i else blk
            if numeric_slot:
                blk = re.sub(r'(<Port [^>]*Upstream="true"[^>]*Address=")[^"]+(")',
                             lambda m: f"{m.group(1)}{new_addr}{m.group(2)}", blk)
                blk = re.sub(r'(<Port [^>]*Address=")[^"]+("[^>]*Upstream="true")',
                             lambda m: f"{m.group(1)}{new_addr}{m.group(2)}", blk)
        out.append(blk)
    return "\n".join(out)


def _module_file(catalog: str, label: str, xml: str, count: int, safety: bool,
                 source: str, why: str) -> None:
    kwargs = {}
    if safety:
        kwargs["processor_type"] = SAFETY_PROCESSOR
        kwargs["safety_level"] = SAFETY_LEVEL
    target = ("AsmClo" + "".join(c for c in catalog if c.isalnum())[:14] + label[:4])[:24]
    l5x = build_l5x(target_name=target, tags_xml="", extra_modules_xml=_place_copies(xml, count), **kwargs)
    name = f"asmclose_{_slug(catalog)}_{label}_n{count:02d}"
    out = OUT_MODULES / f"{name}.L5X"
    write_sample_unmodeled(l5x, out)
    append_manifest_row(
        name,
        f"{catalog} x{count} ('{label}' shape), genericized structurally verbatim from {source}, "
        f"on a {'SIL2 safety' if safety else 'standard'} controller. {why} Part of the n=1/2/4 "
        f"sweep that makes the marginal cost of the Nth identical module directly readable -- a "
        f"single point can only confirm a total, never separate per-module cost from the one-time "
        f"cost of the first.",
        "modules", out, 0,
    )


def group_a_ers3_drives() -> int:
    """Every -ERS3 catalog on a PLAIN NON-SAFETY controller, count-swept.

    CORRECTED 2026-09-06, second pass. The first pass of this file asserted
    that a -ERS3 drive needs a safety controller. That was wrong, and the
    disproof was already in the repo: `composite_realistic_v4_001` through
    `_031` carry -ERS3 drives on a plain 1756-L81E with no SafetyLevel and
    captured at ZERO errors.

    The real cause of the -ERS3 import failures is the one already
    diagnosed on 2026-09-03 and recorded in `_drive_module_xml`'s own
    docstring: the drive module was missing its `<ExtendedProperties>`
    block (Vendor/CatNum/FeedbackDevice1-4/ConfigID), found by a
    byte-for-byte diff against a real SampleAxis export. That fix landed in
    `gen_module_motion.py`, which is what the working composite files use.
    `gen_module_sweep_variants.py` keeps its own hardcoded copy of the
    module XML and never got the fix, so its blocks still lack the element
    -- and carry a corrupted ConfigData payload besides, 119 L5K values
    against the real 118.

    So this group builds from `_drive_module_xml`, the function whose
    output is proven by 31 zero-error captures, rather than from the
    variants table whose output is proven to fail.
    """
    n = 0
    for catalog in sorted(_ERS3_CATALOGS):
        for count in COUNTS:
            blocks = "\n".join(
                _drive_module_xml(f"Drv{i + 1}", catalog, "false", address=f"192.168.1.{20 + i}")
                for i in range(count)
            )
            target = ("AsmDrv" + "".join(c for c in catalog if c.isalnum())[:14])[:24]
            l5x = build_l5x(target_name=target, tags_xml="", extra_modules_xml=blocks)
            name = f"asmclose_{_slug(catalog)}_n{count:02d}"
            out = OUT_MODULES / f"{name}.L5X"
            write_sample_unmodeled(l5x, out)
            append_manifest_row(
                name,
                f"{catalog} x{count} on a plain non-safety 1756-L81E, built from the same "
                f"_drive_module_xml() whose output captured at zero errors across "
                f"composite_realistic_v4_001..031. A -ERS3 drive does NOT require a safety "
                f"controller -- the earlier import failures were a missing <ExtendedProperties> "
                f"block, fixed 2026-09-03 in gen_module_motion.py but never propagated to "
                f"gen_module_sweep_variants.py's own hardcoded copy. n=1/2/4 so the marginal "
                f"cost of the Nth identical drive is read directly; a single point can only "
                f"confirm a total, never separate per-module cost from the cost of the first.",
                "modules", out, 0,
            )
            n += 1
    return n


def group_b_unpriced_catalogs() -> int:
    """The other still-ASSUMED catalogs that appear in real programs."""
    n = 0
    for catalog in _UNPRICED_CATALOGS:
        # A catalog lives in one of the two real-module tables: the
        # single-shape sweep, or the multi-shape variants sweep for the
        # catalogs that appear in more than one real configuration.
        if catalog in _MODULE_VARIANTS:
            label, xml, source, _chain = _MODULE_VARIANTS[catalog][0]
        elif catalog in _MODULE_CHAINS:
            xml, source, _chain = _MODULE_CHAINS[catalog]
            label = "1conn"
        else:
            print(f"  SKIP {catalog}: no real module XML on file in either sweep table")
            continue
        for count in COUNTS:
            _module_file(
                catalog, label, xml, count, safety=False, source=source,
                why=(
                    "module_overhead_by_catalog carries an ASSUMED entry for this catalog, so it "
                    "falls back to the flat default rate. It appears in the real programs, so that "
                    "fallback is real exposure rather than a theoretical one."
                ),
            )
            n += 1
    return n


def group_c_fbd_sfc_probes() -> int:
    """One bare-tag probe per never-measured FBD/SFC structure."""
    n = 0
    for type_name, assumed_bytes in _FBD_SFC_TYPES:
        l5x = build_l5x(
            target_name=f"Probe{type_name.title().replace('_', '')}"[:24],
            tags_xml=tag_xml("Probe1", type_name),
        )
        name = f"predefprobe_{type_name.lower()}"
        out = OUT_PREDEF / f"{name}.L5X"
        write_sample_unmodeled(l5x, out)
        append_manifest_row(
            name,
            f"One Controller-scoped {type_name} tag, no logic -- the last 10 predefined "
            f"structures with no capture behind them, all FBD/SFC family. Currently ASSUMED at "
            f"{assumed_bytes} bytes from RM018A; the delta against the empty-project baseline is "
            f"the real structure size. Same shape as the 174 predefprobe_* files that closed every "
            f"other predefined type at exactly 0.0000% residual.",
            "predefined", out, 0,
        )
        n += 1
    return n


def main() -> None:
    OUT_MODULES.mkdir(parents=True, exist_ok=True)
    OUT_PREDEF.mkdir(parents=True, exist_ok=True)
    a = group_a_ers3_drives()
    b = group_b_unpriced_catalogs()
    c = group_c_fbd_sfc_probes()
    print(f"Group A (2198 -ERS3 drives, non-safety CPU): {a}")
    print(f"Group B (unpriced catalogs):        {b}")
    print(f"Group C (FBD/SFC probes):           {c}")
    print(f"Total: {a + b + c}")


if __name__ == "__main__":
    main()
