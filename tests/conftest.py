"""Shared fixtures.

The generated L5X files are not kept in the repository once their batch has been
captured and written up (samples/manifest.csv and samples/captures.csv keep every
number). A test that needs one of those files rebuilds it from its generator
into a temporary folder: every generator path under samples/generated/ is
redirected there, the manifest is never written, and neither the realism floor nor the
later build-validity lint rules are applied (these files are test inputs, never
captures).
"""

from __future__ import annotations

import hashlib
import importlib
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GENERATED = REPO / "samples" / "generated"
# Rebuilt files are kept between runs here (git-ignored), keyed by a hash of every
# generator source and data file, so a run rebuilds them only after a generator changes.
REGEN_CACHE = REPO / ".cache" / "regenerate"


def _generator_key() -> str:
    h = hashlib.sha256()
    for f in sorted((REPO / "src" / "sample_gen").rglob("*")):
        if f.suffix in (".py", ".json", ".csv") and "__pycache__" not in f.parts:
            h.update(f.relative_to(REPO).as_posix().encode())
            h.update(f.read_bytes())
    return h.hexdigest()[:16]


@pytest.fixture(scope="session")
def regenerate(tmp_path_factory):
    """regenerate("gen_x", "gen_y") -> a stand-in for samples/generated/ holding
    everything those generators write, built once per generator-source state."""
    root = REGEN_CACHE / _generator_key()
    root.mkdir(parents=True, exist_ok=True)
    done: set[str] = {m.stem for m in root.glob("*.done")}

    def _run(*modules: str) -> Path:
        with pytest.MonkeyPatch.context() as mp:
            import sample_gen.manifest as manifest
            mp.setattr(manifest, "append_manifest_row", lambda *a, **k: None)
            # Files rebuilt for a test are parser inputs, never captured, so the
            # realism floor (a capture-validity rule added after many of these
            # generators were written) is not applied to them.
            mp.setattr(manifest, "realism_or_raise", lambda *a, **k: None)
            # Nor are the build-validity lint rules added since (one alarm-definition
            # arm is firmware v38 on purpose): the tests read content, not buildability.
            mp.setattr(manifest, "lint_or_raise", lambda *a, **k: None)
            for name in modules:
                if name in done:
                    continue
                mod = importlib.import_module(f"sample_gen.{name}")
                for attr, value in list(vars(mod).items()):
                    if isinstance(value, Path) and (value == GENERATED or GENERATED in value.parents):
                        mp.setattr(mod, attr, root / value.relative_to(GENERATED))
                    elif attr == "append_manifest_row":
                        mp.setattr(mod, attr, lambda *a, **k: None)
                mod.main()
                done.add(name)
                (root / f"{name}.done").touch()
        return root

    return _run


@pytest.fixture(scope="session")
def demo_l5x(tmp_path_factory) -> Path:
    """The synthetic demo project the README screenshots come from: modules, a
    Kinetix bus, UDTs, an AOI, programs, used and unused content."""
    sys.path.insert(0, str(REPO / "scripts"))
    import build_demo_project
    out = tmp_path_factory.mktemp("demo") / "DemoLine.L5X"
    out.write_text(build_demo_project.build(), encoding="utf-8")
    return out
