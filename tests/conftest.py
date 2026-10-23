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

import ast
import hashlib
import importlib
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GENERATED = REPO / "samples" / "generated"
SAMPLE_GEN = REPO / "src" / "sample_gen"
# Rebuilt files are kept between runs here (git-ignored), keyed by a hash of the requested
# generators, every sample_gen module they import (transitively) and the package's data
# files: a run rebuilds a family only after something it is built from changes, not after
# an unrelated generator does.
REGEN_CACHE = REPO / ".cache" / "regenerate"


class _Unpriced:
    """What write_sample returns for a rebuilt file. Its prediction only ever reaches the
    manifest, which is not written here, so the file is not priced. Printing it works;
    arithmetic, comparison or truth-testing raises, so a generator whose CONTENT depended
    on its own prediction would fail here instead of building a different file."""

    def __format__(self, spec: str) -> str:
        return "unpriced"

    def __repr__(self) -> str:
        return "unpriced"

    def _refuse(self, *_a):
        raise TypeError("a rebuilt file is not priced; its generator must not use the prediction")

    __eq__ = __lt__ = __le__ = __gt__ = __ge__ = __bool__ = __int__ = __index__ = __hash__ = _refuse


def _module_file(module: str) -> Path | None:
    """The source file of a sample_gen module named relative to the package ("" is the
    package itself, "data.kinetix" a submodule), or None if it is not one."""
    base = SAMPLE_GEN.joinpath(*module.split(".")) if module else SAMPLE_GEN
    for path in (base.with_suffix(".py") if module else None, base / "__init__.py"):
        if path is not None and path.is_file():
            return path
    return None


def _imports(module: str, seen: set[str]) -> set[str]:
    """module, its packages and every sample_gen module it imports -- absolute or relative,
    anywhere in the file -- transitively. Names are relative to sample_gen."""
    path = _module_file(module)
    if module in seen or path is None:
        return seen
    seen.add(module)
    parts = module.split(".") if module else []
    for i in range(len(parts)):
        _imports(".".join(parts[:i]), seen)
    package = parts if path.name == "__init__.py" else parts[:-1]
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.ImportFrom):
            if node.level:
                base = package[:len(package) - node.level + 1] + (node.module.split(".") if node.module else [])
            elif node.module == "sample_gen" or (node.module or "").startswith("sample_gen."):
                base = node.module.split(".")[1:]
            else:
                continue
            _imports(".".join(base), seen)
            for alias in node.names:
                _imports(".".join(base + [alias.name]), seen)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("sample_gen."):
                    _imports(".".join(alias.name.split(".")[1:]), seen)
    return seen


def _generator_key(modules: tuple[str, ...]) -> str:
    seen: set[str] = set()
    for module in modules:
        _imports(module, seen)
    files = sorted({_module_file(m) for m in seen}) + sorted(
        f for f in SAMPLE_GEN.rglob("*") if f.suffix in (".json", ".csv") and "__pycache__" not in f.parts)
    h = hashlib.sha256()
    for f in files:
        h.update(f.relative_to(REPO).as_posix().encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def _claim(root: Path, name: str) -> bool:
    """True once this process holds the right to build `name` into `root`; False if another
    process (a parallel test worker) built it meanwhile. The lock is a directory, created
    atomically on every platform; one older than STALE_LOCK_SECONDS is a dead run's."""
    lock = root / f"{name}.lock"
    while True:
        try:
            lock.mkdir()
        except FileExistsError:
            if (root / f"{name}.done").exists():
                return False
            try:
                if time.time() - lock.stat().st_mtime > STALE_LOCK_SECONDS:
                    lock.rmdir()
            except FileNotFoundError:
                pass
            time.sleep(0.2)
            continue
        if (root / f"{name}.done").exists():
            lock.rmdir()
            return False
        return True


STALE_LOCK_SECONDS = 600


@pytest.fixture(scope="session")
def regenerate(tmp_path_factory):
    """regenerate("gen_x", "gen_y") -> a stand-in for samples/generated/ holding
    everything those generators write, built once per state of what they are built from."""

    def _run(*modules: str) -> Path:
        root = REGEN_CACHE / _generator_key(modules)
        root.mkdir(parents=True, exist_ok=True)
        done: set[str] = {m.stem for m in root.glob("*.done")}
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
            # Nor is each file priced as it is written: the tests price what they read.
            mp.setattr(manifest, "predicted_bytes", lambda *a, **k: _Unpriced())
            for name in modules:
                if name in done or not _claim(root, name):
                    continue
                try:
                    mod = importlib.import_module(f"sample_gen.{name}")
                    for attr, value in list(vars(mod).items()):
                        if isinstance(value, Path) and (value == GENERATED or GENERATED in value.parents):
                            mp.setattr(mod, attr, root / value.relative_to(GENERATED))
                        elif attr == "append_manifest_row":
                            mp.setattr(mod, attr, lambda *a, **k: None)
                    mod.main()
                    done.add(name)
                    (root / f"{name}.done").touch()
                finally:
                    try:
                        (root / f"{name}.lock").rmdir()
                    except FileNotFoundError:
                        pass
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
