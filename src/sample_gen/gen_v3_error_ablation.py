"""Which subsystem of the v3 composite template does Studio reject? (2026-09-12,
OQ-V3GENBUGS.)

OQ-V3GENBUGS records three real generator bugs found and fixed from the v3
batch's conversion errors, and closes with: "None of these have real capture
data back yet (ACD conversion still being validated as of 2026-09-02) -- no
sizing formula changes from this item, generator-correctness only."

That status is stale. Every one of the 133 rows across the seven families that
entry names is captured, and 65 of them captured WITH Studio build errors:

    composite_realistic_v3   50 rows   49 errored, EXACTLY 2 errors each
    axis_scale               18 rows   18 errored, n+1 (single) / n/2+1 (dual)
    rack_5069                34 rows    0 errored
    rack_pointio             12 rows    0 errored
    rack_1756                12 rows    0 errored
    cipmodule_scale           7 rows    0 errored, but 2 never attempted and
                                        their files no longer exist
    bridge_placeholder        2 rows    0 errored

The axis_scale signature -- one error per axis plus one -- is the exact pattern
CLAUDE.md cites as the reason the step-2b gate exists, and it routes to
OQ-AXISMARGINAL, which already carries it.

The v3 one is different and is what this batch is for. 49 of 50 files carry
EXACTLY 2 errors, constant across a batch whose size ranges 1.3-1.9 MB and
whose programs/AOIs/modules/routines all vary widely. A count that does not
scale with any content dimension is two discrete defects in the template, not a
per-item problem. It matters beyond generator hygiene: the v3 batch was built
specifically to re-derive the composite-scale JSR/AOI surcharge
(OQ-COMPOSITESCALE), so that re-derivation is standing on 49 suspect rows.

Structural inference has been tried and did not find it. Recorded here so it is
not repeated:

  - v3 declares four catalogs v4 does not (1756-OA16I, 1756-OF4/A, 1756-OF8/B,
    1794-IB16/A). ALL of them, plus 1794-ACN15/C and 1756-CNB/D, have their own
    standalone modulesweep_* capture at zero errors. No single catalog is the
    offender.
  - Nameless <Module> elements are not it either: v3_12 has 3 and errors,
    v4_013 has 8 and is clean. They are legitimate drive-peripheral and POINT
    I/O sub-modules.
  - The one clean v3 file, composite_realistic_v3_13, is not structurally
    special -- 11 programs, 18 AOIs, 48 modules, 4 axes, right in the middle of
    the batch's range. Its neighbours v3_12 and v3_14 both error.
  - v4 is clean: 31 captured rows, 0 errors, from a successor generator whose
    files are BIGGER (97 modules, 14 axes against v3's 48 and 4).

So this measures it. `_profile_for_index(12)` is a known 2-error profile; each
file below is that exact profile with ONE subsystem removed. The arm that drops
to zero errors names the subsystem, and the unmodified control has to reproduce
the 2 to prove the comparison is valid at all.

Every arm lands within 2 bytes of the same 1.75 MB total, because the generator
pads to a target size with a filler DINT array. That is a feature here: overall
project size cannot be the confound, only the removed subsystem varies. The
error count is the measurement and these files' actual_bytes is not calibration
data for anything.

If the control does not reproduce 2 errors, the v3 template has changed since
those captures and the whole batch needs recapturing before anything else is
concluded from it. If every arm still shows 2, the defect is in the fixed
scaffolding none of these ablations touch -- the motion block, the MainProgram,
or the controller header -- and the next step is the raw Studio 5000 error-log
line for one v3 file rather than another round of inference.

Run: python -m sample_gen.gen_v3_error_ablation
"""

from __future__ import annotations

import copy
from pathlib import Path

from sample_gen.gen_composite_realistic_v3 import _build, _profile_for_index
from sample_gen.manifest import append_manifest_row, write_sample

OUT_ROOT = Path(__file__).parent.parent.parent / "samples" / "generated" / "composite"

BASE_INDEX = 12

# (label, what to change, one-line statement of what a clean result would mean)
ABLATIONS = (
    ("control", {}, "unmodified profile 12 -- must reproduce the 2 errors or the "
                    "comparison is invalid and the batch needs recapturing"),
    ("noaoi", {"aoi_count": 0},
     "no AOI definitions at all; clean here means an AOI declaration is rejected"),
    # udt_count=0 and array_sizes=[] both make _build index past the end, so
    # these two arms go to ONE instead of none. Still decisive: 1 UDT against
    # 11, and 1 array against 8.
    ("minudt", {"udt_count": 1},
     "one user-defined type instead of eleven; clean here means a UDT "
     "declaration is rejected"),
    ("nomodules", {"module_catalogs": []},
     "no Ethernet or backplane I/O modules (the motion modules are fixed "
     "scaffolding and stay); clean here means an I/O module declaration is rejected"),
    ("noprograms", {"program_count": 1, "subs_per_program": [1]},
     "one extra Program with one subroutine instead of ten; clean here means a "
     "Program or JSR-target declaration is rejected"),
    ("norungs", {"rung_count": 0},
     "empty MainRoutine; clean here means a rung in the generated ladder is rejected"),
    ("nostrings", {"string_count": 0},
     "no custom STRING types; clean here means a custom string definition is rejected"),
    ("minarrays", {"array_sizes": [300]},
     "one atomic array instead of eight; clean here means an array tag "
     "declaration is rejected"),
)


def main() -> None:
    written = 0
    for label, changes, meaning in ABLATIONS:
        profile = copy.deepcopy(_profile_for_index(BASE_INDEX))
        for field, value in changes.items():
            setattr(profile, field, value)
        try:
            l5x, _desc, total = _build(profile)
        except Exception as exc:  # noqa: BLE001 -- report, never abort the sweep
            print(f"SKIP {label}: _build raised {type(exc).__name__}: {exc}")
            continue
        out_name = f"v3abl_{label}"
        out_path = OUT_ROOT / f"{out_name}.L5X"
        bytes_ = write_sample(l5x, out_path)
        append_manifest_row(
            out_name,
            f"v3 composite template, profile {BASE_INDEX}, with ONE subsystem removed: "
            f"{meaning}. OQ-V3GENBUGS error-source ablation: 49 of 50 "
            f"composite_realistic_v3 files captured with EXACTLY 2 Studio build errors, "
            f"constant across a batch whose size and every content count vary widely, so it "
            f"is two discrete template defects rather than a per-item problem -- and the v3 "
            f"batch is what OQ-COMPOSITESCALE's surcharge re-derivation rests on. Every "
            f"v3-only catalog has a clean standalone capture, nameless modules are clean in "
            f"v4, and the one clean v3 file is not structurally special, so inference has not "
            f"found it. The arm that drops to zero errors names the subsystem. If every arm "
            f"still shows 2, the defect is in the fixed scaffolding no ablation touches "
            f"(motion block, MainProgram, controller header) and the raw Studio error-log "
            f"line is needed instead",
            "composite", out_path, bytes_)
        print(f"Wrote {out_path} (predicted {bytes_} bytes, floor {total})")
        written += 1
    print(f"\nDone. {written} files.")


if __name__ == "__main__":
    main()
