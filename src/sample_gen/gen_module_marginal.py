"""Marginal module cost: does the per-module discount repeat per catalog?

Written 2026-09-11 against the 54 captured `asmclose_*` files, all of which
are now reconciled. Those 54 points say something exact and unexpected:

    over-prediction(n) = discount x (n - 1)

with zero residual at n=1, 2 and 4 for all 18 catalogs that have module XML
on file:

    1794-AENT                 432      1756-EN4TR             1520
    1734-AENT/B               520      1756-OB32 (rack)       1760
    1734-AENT/C               520      1756-IB16IF/A          2208
    1756-IB16                 792      440C-CR30-22BBB/A      3768
    1756-IB32/B               792      AL1222                    0
    PowerFlex 755-EENET-CM-S  976      842E-CM-M              1000

So the model charges full price for every module, and the real controller
charges full price for the FIRST one and `full - discount` for the rest.
`discount` is per-catalog-shape and ranges over an order of magnitude, and
AL1222 at exactly 0 is the control that says this is a real per-catalog
property and not a flat per-module fudge.

WHAT IS STILL UNKNOWN, and why the law must not be wired from these 54
points alone. Every one of those files holds ONE catalog. Two readings fit
all 54 equally:

  PER-CATALOG   the first module OF EACH CATALOG pays full price
                -> error on a mixed file = sum over catalogs of d_i x (n_i - 1)
  PER-FILE      the first module IN THE FILE pays full price, every module
                after it is discounted whatever its catalog
                -> error on a mixed file = sum(d_i x n_i) - d_first

On a single-catalog file the two are identical. On a real program -- which
carries 20-60 modules across 10-20 catalogs -- they differ by most of the
total. The nine real programs carry 824,864 bytes of module over-charge
under the per-catalog reading; the per-file reading gives a different number
entirely. Picking wrong is a multi-hundred-kilobyte error on every real
file, so this is decided by measurement, not by which is tidier.

ARM A -- n=8, same builders, same names (`asmclose_*_n08`).
    Linearity is currently established on three points, two of which (n=1
    and n=2) also define the law. n=8 is the first point that can falsify
    it: a per-rack or per-connection-block step would show up as a break
    from `d x 7`, and nothing in the existing data would catch it.

ARM B -- the mixture, which is the actual question.
    Three disjoint quadruples of catalogs with well-separated discounts,
    each built at 1 and at 2 copies per catalog:

      x1  4 catalogs, 1 each   PER-CATALOG predicts error 0
                               PER-FILE predicts sum(d) - d_first
      x2  4 catalogs, 2 each   PER-CATALOG predicts sum(d)
                               PER-FILE predicts 2 x sum(d) - d_first

    The two readings are separated by more than 2 KB in every quadruple, so
    one capture each decides it outright. `_x2rev` reverses the module order
    within the file: under PER-FILE the total error must move by
    (d_first - d_last), under PER-CATALOG it must not move at all. That
    makes the mixture self-checking rather than a single arithmetic
    coincidence.

    1756-OB32 is deliberately excluded from the mixtures: it is the one
    2-deep rack-aliased chain in the set and its n=1 residual is -88 rather
    than 0, so it would put an unexplained term inside the arithmetic that
    is supposed to be decisive.

ARM C -- the separate 2198 first-drive error.
    The -ERS3 drives do not fit `d x (n - 1)`; they carry an extra flat
    error at n=1 as well:

      D012/D020/D032/D057   +6,384 at n=1, then +7,368 per extra drive
      S086-ERS3             +3,264 at n=1, then +4,248 per extra drive
      S130-ERS3             +3,228 at n=1, then +4,212 per extra drive

    i.e. the second and later drives cost 984 (D-series) or 984 (S-series)
    LESS than the first, and the first is itself over-charged. This matters
    more than any other catalog: the 2198 family is 4.07% of the bytes in
    the nine real programs and every one of those bytes is ASSUMED.

    All 54 asmclose files hold bare drive modules with NO axis tag. Real
    programs never do -- a drive without an AXIS_CIP_DRIVE tag pointed at it
    does nothing. So the arm rebuilds the same drives WITH their axis (one
    AXIS_CIP_DRIVE per drive, one shared MOTION_GROUP, exactly the real
    shape), at the same counts. Differencing against the matching bare-drive
    capture separates the drive's own marginal cost from the axis's, which
    is the form the cost actually takes on a real file.

Run: python -m sample_gen.gen_module_marginal
"""

from __future__ import annotations

import re
from itertools import count as _count
from pathlib import Path

from sample_gen.gen_assumed_closeout import (
    _ERS3_CATALOGS,
    _UNPRICED_CATALOGS,
    _module_file,
    _slug,
)
from sample_gen.gen_module_motion import (
    _MOTION_GROUP_TAG_XML,
    _axis_tag,
    _drive_module_xml,
)
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.gen_module_sweep_variants import _MODULE_VARIANTS
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modules"

# The count that first-falsifies linearity. n=1/2/4 already captured.
ARM_A_COUNT = 8

# Measured over-charge for the Nth identical module, from the 54 captured
# asmclose_* rows. Recorded here only so the generator can print what each
# mixed file predicts under each of the two readings -- nothing reads these
# values at size time, and they do NOT belong in memory_model.yaml until the
# mixture says which reading is right.
_DISCOUNT = {
    "1794-AENT": 432,
    "1734-AENT/B": 520,
    "1734-AENT/C": 520,
    "1756-IB16": 792,
    "1756-IB32/B": 792,
    "PowerFlex 755-EENET-CM-S": 976,
    "842E-CM-M": 1000,
    "1756-EN4TR": 1520,
    "1756-IB16IF/A": 2208,
    "440C-CR30-22BBB/A": 3768,
    "AL1222": 0,
}

# Disjoint where it can be, widely separated discounts everywhere, AL1222's
# measured zero as the control in Q1. 1756-OB32 excluded (2-deep rack-aliased
# chain, -88 residual at n=1).
_QUADRUPLES = {
    "q1": ("AL1222", "1794-AENT", "1756-IB16", "1756-EN4TR"),
    "q2": ("1734-AENT/B", "PowerFlex 755-EENET-CM-S", "1756-IB16IF/A", "440C-CR30-22BBB/A"),
    "q3": ("1756-IB32/B", "842E-CM-M", "1756-EN4TR", "440C-CR30-22BBB/A"),
}


def _catalog_xml(catalog: str) -> tuple[str, str, str]:
    """(module XML, shape label, source file) for a catalog, from whichever
    real-module table holds it -- same lookup order as group B of
    gen_assumed_closeout, so a mixture is built from byte-identical blocks
    to the single-catalog files it is differenced against."""
    if catalog in _MODULE_VARIANTS:
        label, xml, source, _chain = _MODULE_VARIANTS[catalog][0]
        return xml, label, source
    xml, source, _chain = _MODULE_CHAINS[catalog]
    return xml, "1conn", source


def _place(xml: str, copies: int, tag: str, slots: _count, ips: _count) -> list[str]:
    """`copies` copies of one module block, placed against FILE-GLOBAL slot
    and IP counters.

    This is the one thing `_place_copies` in gen_assumed_closeout cannot do:
    it renumbers each catalog's copies from slot 1 and from the block's own
    captured IP, which is correct for a single-catalog file and collides
    immediately on a mixed one -- four Ethernet catalogs all carry the same
    captured 192.168.1.63, and four backplane catalogs would all want slot 1.
    Only identity (name, slot, IP) changes; connection list, RPI, data shape
    and EKey stay exactly as captured, because the mixture's whole premise is
    that each module is byte-identical to its single-catalog counterpart.
    """
    up = re.search(r'<Port [^>]*Upstream="true"[^>]*>', xml)
    if up is None:
        raise ValueError("module block has no upstream port")
    up_addr = re.search(r'Address="([^"]+)"', up.group(0)).group(1)
    numeric_slot = up_addr.isdigit()

    out = []
    for i in range(copies):
        suffix = f"{tag}{i + 1}"
        blk = re.sub(r'(<Module Name=")([^"]+)(")',
                     lambda m: f"{m.group(1)}{m.group(2)}{suffix}{m.group(3)}", xml, count=1)
        new_addr = str(next(slots)) if numeric_slot else f"192.168.1.{next(ips)}"
        blk = re.sub(r'(<Port [^>]*Upstream="true"[^>]*Address=")[^"]+(")',
                     lambda m: f"{m.group(1)}{new_addr}{m.group(2)}", blk)
        blk = re.sub(r'(<Port [^>]*Address=")[^"]+("[^>]*Upstream="true")',
                     lambda m: f"{m.group(1)}{new_addr}{m.group(2)}", blk)
        out.append(blk)
    return out


def _place_chain(xml: str, copies: int, tag: str, slots: _count, ips: _count) -> list[str]:
    """`copies` copies of a MULTI-module chain (adapter + the cards behind it).

    `_place_copies` in gen_assumed_closeout renames only the first <Module>
    in a block, which is correct for the 17 standalone catalogs and silently
    wrong for the one 2-deep chain in the set: every copy after the first
    kept the child's original name AND its ParentModule pointer to the FIRST
    adapter AND its slot, so Studio merged the duplicates and the capture
    measured n adapters with one shared card. Zero import errors, wrong
    experiment. `lint.duplicate_module_name` now catches that class
    outright; this builds it correctly instead.

    Every module in the copy is renamed, internal ParentModule references
    are repointed at the renamed sibling, and only the TOP module's upstream
    address is reassigned -- a child sits on its own parent's downstream bus,
    so its slot is private to its own copy of the rack and must not move.
    """
    names = re.findall(r'<Module Name="([^"]+)"', xml)
    top = re.search(r'<Module Name="([^"]+)"', xml).group(1)
    up = re.search(r'<Port [^>]*Upstream="true"[^>]*>', xml)
    up_addr = re.search(r'Address="([^"]+)"', up.group(0)).group(1)
    numeric_slot = up_addr.isdigit()

    out = []
    for i in range(copies):
        suffix = f"{tag}{i + 1}"
        blk = xml
        for nm in names:
            blk = blk.replace(f'<Module Name="{nm}"', f'<Module Name="{nm}{suffix}"')
            blk = blk.replace(f'ParentModule="{nm}"', f'ParentModule="{nm}{suffix}"')
        new_addr = str(next(slots)) if numeric_slot else f"192.168.1.{next(ips)}"
        blk = re.sub(r'(<Module Name="' + re.escape(top + suffix) + r'".*?<Port [^>]*Upstream="true"[^>]*Address=")[^"]+(")',
                     lambda m: f"{m.group(1)}{new_addr}{m.group(2)}", blk, count=1, flags=re.S)
        blk = re.sub(r'(<Module Name="' + re.escape(top + suffix) + r'".*?<Port [^>]*Address=")[^"]+("[^>]*Upstream="true")',
                     lambda m: f"{m.group(1)}{new_addr}{m.group(2)}", blk, count=1, flags=re.S)
        out.append(blk)
    return out


def arm_d_ob32_chain() -> int:
    """The 1756-OB32 rack-aliased chain, rebuilt so the copies are real.

    Its captured n=1/2/4 rows are not usable: n=2 and n=4 duplicate the OB32
    card's name, so what was imported was n adapters sharing ONE output card.
    The full count sweep is rebuilt here under its own name rather than
    regenerated in place, because regenerating in place would leave the old
    captured actual_bytes attached to different file content.
    """
    n = 0
    xml, label, source = _catalog_xml("1756-OB32")
    for copies in (1, 2, 4, ARM_A_COUNT):
        slots, ips = _count(1), _count(20)
        blocks = _place_chain(xml, copies, "k", slots, ips)
        name = f"modmarg_ob32chain_n{copies:02d}"
        l5x = build_l5x(target_name=f"ModMargOb32N{copies:02d}", tags_xml="",
                        extra_modules_xml="\n".join(blocks))
        out = OUT / f"{name}.L5X"
        write_sample_unmodeled(l5x, out)
        append_manifest_row(
            name,
            f"1756-OB32 x{copies} on its real 2-deep '{label}' chain (1756-EN2T adapter + the "
            f"output card behind it), genericized from {source}, with EVERY module in every copy "
            f"renamed and its ParentModule repointed at its own adapter. Replaces the "
            f"asmclose_1756_ob32_rackaliased_n01/02/04 sweep, which is unusable: its copier "
            f"renamed only the first module of the chain, so n=2 and n=4 shipped a duplicated "
            f"card name and Studio merged them -- those captures measured n adapters sharing ONE "
            f"output card, at zero import errors, and the 1760-byte 'OB32 discount' read off them "
            f"is the cost of the cards that were never imported. Now caught by "
            f"lint.duplicate_module_name.",
            "modules", out, 0,
        )
        n += 1
    return n


def arm_a_n8() -> int:
    """n=8 for every catalog that already has n=1/2/4 on record."""
    n = 0
    for catalog in sorted(_ERS3_CATALOGS):
        blocks = "\n".join(
            _drive_module_xml(f"Drv{i + 1}", catalog, "false", address=f"192.168.1.{20 + i}")
            for i in range(ARM_A_COUNT)
        )
        target = ("AsmDrv" + "".join(c for c in catalog if c.isalnum())[:14])[:24]
        l5x = build_l5x(target_name=target, tags_xml="", extra_modules_xml=blocks)
        name = f"asmclose_{_slug(catalog)}_n{ARM_A_COUNT:02d}"
        out = OUT / f"{name}.L5X"
        write_sample_unmodeled(l5x, out)
        append_manifest_row(
            name,
            f"{catalog} x{ARM_A_COUNT} on a plain non-safety 1756-L81E, same "
            f"_drive_module_xml() blocks as the captured n=1/2/4 files in this family. Extends "
            f"the count sweep to the first point that can FALSIFY the measured marginal law: "
            f"n=1/2/4 fit over-prediction = 6384 + 7368 x (n-1) exactly, but a per-rack or "
            f"per-connection-block step above 4 modules would be invisible in three points, two "
            f"of which define the law. Differences directly against n=4 of the same family.",
            "modules", out, 0,
        )
        n += 1

    for catalog in _UNPRICED_CATALOGS:
        if catalog == "1756-OB32":
            continue  # 2-deep chain, rebuilt properly by arm_d_ob32_chain
        if catalog in _MODULE_VARIANTS:
            label, xml, source, _chain = _MODULE_VARIANTS[catalog][0]
        elif catalog in _MODULE_CHAINS:
            xml, source, _chain = _MODULE_CHAINS[catalog]
            label = "1conn"
        else:
            print(f"  SKIP {catalog}: no real module XML on file in either sweep table")
            continue
        _module_file(
            catalog, label, xml, ARM_A_COUNT, safety=False, source=source,
            why=(
                f"Extends this catalog's captured n=1/2/4 sweep to n=8, the first point that can "
                f"falsify the measured law over-prediction = discount x (n-1). The three existing "
                f"points fit it exactly, but two of them define it, so a step above 4 modules "
                f"would not show. Differences directly against n=4 of the same family."
            ),
        )
        n += 1
    return n


def arm_b_mixtures() -> int:
    """4 catalogs x {1, 2} copies -- per-catalog vs per-file discount."""
    n = 0
    for key, catalogs in _QUADRUPLES.items():
        for copies in (1, 2):
            for reverse in (False, True):
                if reverse and copies == 1:
                    continue  # the order test needs >1 copy to be readable
                order = tuple(reversed(catalogs)) if reverse else catalogs
                slots, ips = _count(1), _count(20)
                blocks: list[str] = []
                for idx, catalog in enumerate(order):
                    xml, _label, _source = _catalog_xml(catalog)
                    blocks += _place(xml, copies, f"m{idx + 1}c", slots, ips)

                d = [_DISCOUNT[c] for c in order]
                per_catalog = sum(d) * (copies - 1)
                per_file = sum(x * copies for x in d) - d[0]

                label = f"x{copies}" + ("rev" if reverse else "")
                name = f"modmarg_mix{key}_{label}"
                target = f"ModMargMix{key.upper()}{label.title()}"[:24]
                l5x = build_l5x(target_name=target, tags_xml="",
                                extra_modules_xml="\n".join(blocks))
                out = OUT / f"{name}.L5X"
                write_sample_unmodeled(l5x, out)
                append_manifest_row(
                    name,
                    f"{len(order)} catalogs x {copies} copies each = {len(blocks)} modules on a "
                    f"plain 1756-L81E, in file order "
                    f"{', '.join(order)}. Module blocks are byte-identical to the captured "
                    f"single-catalog asmclose_* files apart from slot/IP/name, so this differences "
                    f"straight against them. Decides the one thing 54 single-catalog captures "
                    f"cannot: whether the measured per-module discount repeats for the first "
                    f"module of EACH catalog (predicts over-prediction {per_catalog:+d}) or applies "
                    f"once to the first module in the FILE (predicts {per_file:+d}). "
                    + (
                        "Module order is reversed against the non-rev file of the same shape: the "
                        "per-file reading requires the total error to move by (d_first - d_last), "
                        "the per-catalog reading requires it not to move at all."
                        if reverse else
                        "Real programs carry 10-20 catalogs, so the two readings differ by most of "
                        "the module total on every real file."
                    ),
                    "modules", out, 0,
                )
                n += 1
    return n


def arm_c_drive_with_axis() -> int:
    """The same -ERS3 drives, but carrying their axis, as on a real file."""
    n = 0
    for catalog, counts in (("2198-D012-ERS3", (1, 2, 4, 8)), ("2198-S086-ERS3", (1, 2))):
        for copies in counts:
            modules = "\n".join(
                _drive_module_xml(f"Drv{i + 1}", catalog, "false", address=f"192.168.1.{20 + i}")
                for i in range(copies)
            )
            tags = "\n".join(
                [_MOTION_GROUP_TAG_XML]
                + [_axis_tag(f"Ax{i + 1}", f"Drv{i + 1}:Ch1") for i in range(copies)]
            )
            slug = _slug(catalog)
            name = f"modmarg_drvaxis_{slug}_n{copies:02d}"
            target = ("MMDrvAx" + "".join(c for c in catalog if c.isalnum())[:12]
                      + f"N{copies:02d}")[:24]
            l5x = build_l5x(target_name=target, tags_xml=tags, extra_modules_xml=modules)
            out = OUT / f"{name}.L5X"
            write_sample_unmodeled(l5x, out)
            append_manifest_row(
                name,
                f"{catalog} x{copies}, each with its own AXIS_CIP_DRIVE tag on channel Ch1, plus "
                f"the one shared MOTION_GROUP -- the real shape, where the bare-drive "
                f"asmclose_{slug}_n{copies:02d} file it differences against is not. The -ERS3 "
                f"family is the only one that does not fit discount x (n-1): it carries an extra "
                f"flat over-charge at n=1 as well (D-series +6,384 then +7,368 per extra drive), "
                f"and it is 4.07% of the bytes in the nine real programs with every one of those "
                f"bytes still ASSUMED. Differencing this against the bare-drive capture at the "
                f"same count separates the drive's own marginal cost from the axis's.",
                "modules", out, 0,
            )
            n += 1
    return n


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    a = arm_a_n8()
    b = arm_b_mixtures()
    c = arm_c_drive_with_axis()
    d = arm_d_ob32_chain()
    print(f"Arm A (n=8 linearity falsifier):   {a}")
    print(f"Arm B (mixed-catalog discount):    {b}")
    print(f"Arm C (drive + its axis):          {c}")
    print(f"Arm D (OB32 chain, rebuilt):       {d}")
    print(f"Total: {a + b + c + d}")


if __name__ == "__main__":
    main()
