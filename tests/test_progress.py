"""sample_gen.progress: parallel runs report every item and stop on a stuck one."""

from __future__ import annotations

import time

import pytest

from sample_gen.progress import run


def _square(x: int) -> int:
    return x * x


def _sleepy(x: int) -> int:
    time.sleep(x)
    return x


def test_every_item_comes_back_under_its_key_with_a_progress_line(capsys):
    assert run(((f"k{i}", i) for i in range(6)), _square, label="t", workers=2) == {
        f"k{i}": i * i for i in range(6)}
    err = capsys.readouterr().err
    assert "[t 6/6]" in err and "done: 6 item(s)" in err


def test_the_watchdog_names_the_stuck_item(monkeypatch):
    import sample_gen.progress as P
    monkeypatch.setattr(P, "POLL_SECONDS", 0.2)
    started = time.monotonic()
    with pytest.raises(TimeoutError, match="stuck"):
        run([("fast", 0), ("stuck", 30)], _sleepy, label="t", item_timeout=1, workers=2)
    assert time.monotonic() - started < 10
