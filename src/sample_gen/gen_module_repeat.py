"""OQ-MODREPEAT: the second and later copy of a catalog measured only once.

Five Ethernet catalogs carry an ASSUMED overhead from one isolation capture each
(`modulesweep_*`) and no repeat cost, so every copy is charged full price. Real
safety-controller programs carry them repeated -- 6 to 7 1732E-IB16M12R/A, 3 to 4
1732E-OB16M12R/A and 3 EX260-SEN1/A in each of RS-06 and RS-09, 4 EX260-SEN3/A in RS-10,
4 PowerFlex 525-EENET in each of RS-02, RS-03 and RS-17 -- and RS-06 and RS-09, the same
program with two more IB16M12R, differ by about 700 a copy where the engine charges 1,432
(OPEN_QUESTIONS OQ-MODREPEAT; the law is OQ-MODULEMARGINAL's).

Each catalog at 1, 2 and 4 copies on the realism floor, 1756-L81E v35, the repository's
own module-sweep block (captured clean as `modulesweep_*`) placed by
gen_assumed_closeout._place_copies (each copy its own name and address); each against
`realism_base_f25`, the plant alone.

Run: python -m sample_gen.gen_module_repeat
"""

from __future__ import annotations

from pathlib import Path

from sample_gen.gen_assumed_closeout import _place_copies, _slug
from sample_gen.gen_module_sweep import _MODULE_CHAINS
from sample_gen.manifest import append_manifest_row, write_sample
from sample_gen.realism import with_baseline
from sample_gen.wrapper import build_l5x

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "modrep"
CATEGORY = "modules"
OQ = "OQ-MODREPEAT"
CATALOGS = ("1732E-IB16M12R/A", "1732E-OB16M12R/A", "EX260-SEN1/A", "EX260-SEN3/A", "PowerFlex 525-EENET")
COUNTS = (1, 2, 4)


def plan() -> list[tuple[str, str, int]]:
    return [(f"modrep_{_slug(c)}_n{n:02d}", c, n) for c in CATALOGS for n in COUNTS]


def make(sample_id: str, catalog: str, count: int) -> str:
    xml, _source, chain_len = _MODULE_CHAINS[catalog]
    assert chain_len == 1, catalog
    target = ("ModRep" + "".join(ch for ch in catalog if ch.isalnum())[:16] + f"N{count}")[:40]
    return build_l5x(target_name=target, **with_baseline(extra_modules_xml=_place_copies(xml, count)))


def main() -> None:
    for sample_id, catalog, count in plan():
        out = OUT_ROOT / f"{sample_id}.L5X"
        predicted = write_sample(make(sample_id, catalog, count), out)
        append_manifest_row(sample_id, f"{OQ}: {count} {catalog} (the repository's module-sweep block, each copy "
                                       f"its own name and address) on the realism floor, 1756-L81E v35, against "
                                       f"realism_base_f25: the first copy and each further copy.",
                            CATEGORY, out, predicted)
        print(f"Wrote {out.name} (predicted {predicted:,})")


if __name__ == "__main__":
    main()
