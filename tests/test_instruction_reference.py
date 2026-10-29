"""The instruction reference is manual content: it may only be written under samples/local/reference/."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _script():
    spec = importlib.util.spec_from_file_location("build_instruction_reference",
                                                  ROOT / "scripts" / "build_instruction_reference.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_refuses_a_destination_outside_the_local_reference(tmp_path):
    assert _script().main([str(tmp_path / "m.pdf"), "--out", str(ROOT / "docs")]) == 2
    assert _script().main([str(tmp_path / "m.pdf"), "--out", str(tmp_path)]) == 2


def test_the_local_reference_is_gitignored():
    import subprocess
    r = subprocess.run(["git", "check-ignore", "-q", "samples/local/reference/instructions.json"], cwd=ROOT)
    assert r.returncode == 0
