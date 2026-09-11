"""Per-axis and per-drive-module marginal cost, decoupled.

Written 2026-09-11. `scripts/unreconciled.py` (new, same day) recomputed all
2,770 captured rows against the current engine and the largest single-sign
unreconciled block in the whole corpus is the 31-row axis family: every
`axis_scale_*` file with n>=2 over-predicts, monotonically, up to +62,528
bytes (+10.5%) at 20 axes. It has been captured since 2026-09-03.

Both arms are PERFECTLY linear in the axis count, with zero residual at every
step:

    single-axis drives   +3,288 per axis   (n=2,4,6,8,12,16,20)
    dual-axis drives     +2,600 per axis   (n=2,4,6,8,12,16,20)

and the two shared base points (n=1 single, n=2 dual) both sit at +56, i.e.
exact. So this is a marginal-cost error, not a base-constant error -- the
FIRST axis in a file is priced correctly and every one after it is not.

Real exposure is large: the sixteen real programs carry 359 AXIS_CIP_DRIVE and
65 AXIS_VIRTUAL tags. At the single-arm rate that is roughly 650 KB of
over-prediction hiding in the real-file totals, the same order as
OQ-MODULEMARGINAL's 824,864.

WHY THE TWO ARMS DO NOT DECOMPOSE ON THEIR OWN. The naive reading takes the
difference between the arms as the drive-module term:

    single: 1 module per axis     A + M     = 3,288
    dual:   1 module per 2 axes    A + M/2  = 2,600
    -> M = 1,376, A = 1,912

and A comes out identical from both arms, which looks decisive. It is not, for
two reasons found by reading the files rather than the numbers:

  - The single arm is 8 x 2198-S086-ERS3, ONE catalog repeated. The dual arm
    is one each of D012/D020/D032/D057, FOUR DISTINCT catalogs at low n,
    repeating only as n grows. OQ-MODULEMARGINAL's open question is precisely
    whether the module discount is per catalog or per file, so "M" is not the
    same quantity in the two arms and the subtraction is not valid.
  - Every one of these files carries error_count = n+1 with an EMPTY
    error_log. All 144 errored rows in the manifest were captured between
    2026-08-23 and 2026-09-08; the error-log reader in
    `logix_build_capture.ahk` only started working 2026-09-10, so not one of
    them has any error text on record. The n=1 file has 2 errors and is
    nonetheless byte-exact, which suggests the errors are benign, but that is
    an inference and the rows stay suspect until the text is known.

THE DECOUPLING ARM -- `axmarg_virtual_n*`. AXIS_VIRTUAL needs no drive module
at all. A count sweep of virtual axes with ZERO modules in the file measures
the per-axis term with nothing to share it with, which neither existing arm
can do. Real programs carry 65 of them, so this is the shape they actually
have, not a contrivance.

    axmarg_virtual_n{01,02,04,08,12,16,20}   7 files, pure per-axis term

THE CATALOG ARM -- `axmarg_1cat_n*`. Eight axes on four dual drives of ONE
catalog, swept by count, against the existing four-distinct-catalog arm at the
same counts. Same axis count, same module count, only catalog repetition
differs, so it reads OQ-MODULEMARGINAL's per-catalog-vs-per-file question off
files that also carry axes.

    axmarg_1cat_n{02,04,08,12,20}            5 files

THE CROSSING ARM -- `axmarg_ncat_n08_{1,2,4}cat`. Eight axes on four dual
drives drawn from 1, 2 or 4 catalogs. Axis count and module count are both
pinned; only the number of DISTINCT catalogs moves. Under the per-catalog
reading the error changes across these three; under the per-file reading it
does not move at all.

    axmarg_ncat_n08_{1,2,4}cat               3 files

THE ADDITIVITY ARM -- `axmarg_mixed_n08`. Eight AXIS_VIRTUAL plus eight
AXIS_CIP_DRIVE in one file, against the two single-type files at the same
counts. Says whether the per-axis term is per axis TAG regardless of type or
per axis of each type.

    axmarg_mixed_n08                         1 file

Run: python -m sample_gen.gen_axis_marginal
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from sample_gen.gen_axis_composite import _AXIS_VIRTUAL_TAG_XML
from sample_gen.gen_module_motion import (
    _MOTION_GROUP_TAG_XML,
    _axis_tag,
    _drive_module_xml,
)
from sample_gen.manifest import append_manifest_row, write_sample_unmodeled
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "axis"

AXIS_COUNTS = (1, 2, 4, 8, 12, 16, 20)
CAT_SWEEP_COUNTS = (2, 4, 8, 12, 20)

# The single-axis arm's own catalog, so axmarg_1cat differences against it.
ONE_CATALOG = "2198-S086-ERS3"
# The dual arm's four, in its own order.
FOUR_CATALOGS = ("2198-D012-ERS3", "2198-D020-ERS3", "2198-D032-ERS3", "2198-D057-ERS3")


def _virtual_axis_tag(name: str) -> str:
    """One AXIS_VIRTUAL tag, real shape from gen_axis_composite, renamed and
    given its own AxisID -- a duplicate AxisID is a real Studio import error
    the moment two axis tags coexist (found 2026-08-27), and this batch puts
    twenty of them in one file."""
    body = _AXIS_VIRTUAL_TAG_XML.replace('Name="Axis_Virtual"', f'Name="{name}"')
    body = body.replace('MotionGroup="MotionGroup"', 'MotionGroup="Motion"')
    digest = int(hashlib.sha256(name.encode()).hexdigest(), 16)
    return body.replace('AxisUpdateSchedule="Alternate 1"',
                        f'AxisID="{digest % 900_000_000 + 100_000_000}" '
                        f'AxisUpdateSchedule="Alternate 1"')


def _write(l5x: str, name: str, description: str) -> None:
    out = OUT_ROOT / f"{name}.L5X"
    write_sample_unmodeled(l5x, out)
    append_manifest_row(name, description, "axis", out, 0)


def arm_virtual() -> int:
    """Per-axis term with NO drive module anywhere in the file."""
    for n in AXIS_COUNTS:
        tags = "\n".join([_MOTION_GROUP_TAG_XML]
                         + [_virtual_axis_tag(f"Vax{i + 1:02d}") for i in range(n)])
        _write(
            build_l5x(target_name=f"AxMargVirt{n:02d}", tags_xml=tags),
            f"axmarg_virtual_n{n:02d}",
            f"{n} AXIS_VIRTUAL tags plus the one shared MOTION_GROUP, and ZERO modules of any "
            f"kind. The decoupling arm: both captured axis_scale arms move axis count and drive-"
            f"module count together, so their exact +3,288/axis (single) and +2,600/axis (dual) "
            f"cannot be split into an axis term and a module term -- especially since the single "
            f"arm repeats ONE catalog and the dual arm uses four distinct ones, which is exactly "
            f"OQ-MODULEMARGINAL's open per-catalog-vs-per-file question. An AXIS_VIRTUAL needs no "
            f"drive at all, so this sweep measures the per-axis term with nothing to share it "
            f"with. Real programs carry 65 AXIS_VIRTUAL tags, so this is a real shape.",
        )
    return len(AXIS_COUNTS)


def _dual_drive_file(n_axes: int, catalogs: tuple[str, ...], name: str,
                     description: str) -> None:
    """n_axes axes riding two-per-module on dual-axis drives, catalogs cycled."""
    n_modules = (n_axes + 1) // 2
    modules = "\n".join(
        _drive_module_xml(f"Drv{i + 1:02d}", catalogs[i % len(catalogs)], "false",
                          address=f"192.168.1.{20 + i}")
        for i in range(n_modules)
    )
    axis_tags = []
    for i in range(n_axes):
        module_index = i // 2
        channel = "Ch1" if i % 2 == 0 else "Ch3"
        axis_tags.append(_axis_tag(f"Ax{i + 1:02d}", f"Drv{module_index + 1:02d}:{channel}"))
    tags = "\n".join([_MOTION_GROUP_TAG_XML] + axis_tags)
    _write(build_l5x(target_name=name[:24], tags_xml=tags, extra_modules_xml=modules),
           name, description)


def arm_one_catalog() -> int:
    for n in CAT_SWEEP_COUNTS:
        _dual_drive_file(
            n, (ONE_CATALOG,), f"axmarg_1cat_n{n:02d}",
            f"{n} AXIS_CIP_DRIVE tags riding two-per-module on {(n + 1) // 2} dual-axis "
            f"{ONE_CATALOG} drives -- ONE catalog repeated. Differences against the captured "
            f"axis_scale_n{n:02d}_dual, which has the identical axis and module counts but draws "
            f"its modules from FOUR distinct catalogs. Same axes, same modules, only catalog "
            f"repetition differs, so this reads OQ-MODULEMARGINAL's per-catalog-vs-per-file "
            f"question off files that also carry axes.",
        )
    return len(CAT_SWEEP_COUNTS)


def arm_catalog_crossing() -> int:
    n = 8
    for n_cats in (1, 2, 4):
        # All three files draw from the SAME catalog family (D012/D020/D032/
        # D057), which the engine prices identically -- so all three predict
        # the same total and any difference in the captured actual is purely
        # the catalog-DIVERSITY effect. Using ONE_CATALOG (S086) for the
        # 1-catalog file would have changed the predicted base as well and
        # confounded the very thing this arm isolates.
        cats = FOUR_CATALOGS[:n_cats]
        _dual_drive_file(
            n, cats, f"axmarg_ncat_n{n:02d}_{n_cats}cat",
            f"{n} AXIS_CIP_DRIVE tags on {(n + 1) // 2} dual-axis drives drawn from {n_cats} "
            f"distinct catalog(s). Axis count and module count are BOTH pinned across these three "
            f"files; only the number of distinct catalogs moves. Under a per-catalog module "
            f"discount the over-prediction changes across the set; under a per-file one it does "
            f"not move at all. That is the same fork modmarg_mix* tests without axes present, and "
            f"having it both ways guards against an axis-module interaction being mistaken for "
            f"either answer.",
        )
    return 3


def arm_mixed() -> int:
    n = 8
    n_modules = (n + 1) // 2
    modules = "\n".join(
        _drive_module_xml(f"Drv{i + 1:02d}", ONE_CATALOG, "false",
                          address=f"192.168.1.{20 + i}")
        for i in range(n_modules)
    )
    cip = [_axis_tag(f"Ax{i + 1:02d}", f"Drv{i // 2 + 1:02d}:{'Ch1' if i % 2 == 0 else 'Ch3'}")
           for i in range(n)]
    virt = [_virtual_axis_tag(f"Vax{i + 1:02d}") for i in range(n)]
    tags = "\n".join([_MOTION_GROUP_TAG_XML] + cip + virt)
    _write(
        build_l5x(target_name=f"AxMargMix{n:02d}", tags_xml=tags, extra_modules_xml=modules),
        f"axmarg_mixed_n{n:02d}",
        f"{n} AXIS_CIP_DRIVE tags on {n_modules} dual {ONE_CATALOG} drives PLUS {n} AXIS_VIRTUAL "
        f"tags with no modules, in one file. Against axmarg_1cat_n{n:02d} and "
        f"axmarg_virtual_n{n:02d} at the same counts this says whether the per-axis marginal term "
        f"is per axis TAG regardless of type, or per axis of each type separately. Real programs "
        f"mix the two in exactly this way -- all but three of the sixteen carry both.",
    )
    return 1


def main() -> None:
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    v = arm_virtual()
    o = arm_one_catalog()
    c = arm_catalog_crossing()
    m = arm_mixed()
    print(f"Virtual-axis decoupling arm:   {v}")
    print(f"One-catalog dual-drive arm:    {o}")
    print(f"Catalog-count crossing arm:    {c}")
    print(f"Mixed axis-type arm:           {m}")
    print(f"Total: {v + o + c + m}")


if __name__ == "__main__":
    main()
