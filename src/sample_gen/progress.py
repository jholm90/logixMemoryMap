"""Long runs: every item in parallel, one progress line per item, and a watchdog.

A run over many L5X files (generating a batch, pricing it with the engine) costs a
second or more per file. Run serially and silently it looks the same as a hang. Through
`run`, the work is spread over every core, each finished item prints a line with the
time it took and the time left, and an item that runs past `item_timeout` seconds, or a
run past `total_timeout`, stops the whole run with the stuck items named.
"""

from __future__ import annotations

import multiprocessing
import os
import sys
import time
from concurrent.futures import FIRST_COMPLETED, Future, ProcessPoolExecutor, wait
from typing import Any, Callable, Iterable

POLL_SECONDS = 5


def run(items: Iterable[tuple[str, Any]], fn: Callable[[Any], Any], *, label: str,
        item_timeout: float = 120, total_timeout: float = 1800, workers: int | None = None) -> dict[str, Any]:
    """fn(arg) for every (key, arg), in worker processes; {key: result}. fn must be a
    module-level function and arg picklable."""
    items = list(items)
    n = len(items)
    workers = max(1, min(workers or os.cpu_count() or 1, n or 1))
    out: dict[str, Any] = {}
    start = time.monotonic()
    print(f"[{label}] {n} item(s) on {workers} worker(s); watchdog {item_timeout:.0f}s an item, "
          f"{total_timeout:.0f}s in all", file=sys.stderr, flush=True)
    # spawn, not fork: forking a process that already runs threads can deadlock a worker,
    # and spawn is what Windows does anyway.
    pool = ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"))
    pending: dict[Future, tuple[str, float]] = {}
    queue = iter(items)

    def submit() -> None:
        for key, arg in queue:
            pending[pool.submit(fn, arg)] = (key, time.monotonic())
            return

    try:
        for _ in range(workers):
            submit()
        while pending:
            done, _ = wait(pending, timeout=POLL_SECONDS, return_when=FIRST_COMPLETED)
            now = time.monotonic()
            for future in done:
                key, began = pending.pop(future)
                out[key] = future.result()
                elapsed = now - start
                left = elapsed / len(out) * (n - len(out))
                print(f"[{label} {len(out)}/{n}] {key} {now - began:.1f}s | {elapsed:.0f}s elapsed, "
                      f"~{left:.0f}s left", file=sys.stderr, flush=True)
                submit()
            stuck = [key for key, began in pending.values() if now - began > item_timeout]
            if stuck or now - start > total_timeout:
                why = (f"{', '.join(stuck)} past {item_timeout:.0f}s" if stuck
                       else f"the run past {total_timeout:.0f}s with {len(pending)} item(s) unfinished")
                raise TimeoutError(f"[{label}] watchdog: {why}")
    except BaseException:
        for process in list(getattr(pool, "_processes", {}).values()):
            process.terminate()
        raise
    finally:
        pool.shutdown(wait=False, cancel_futures=True)
    print(f"[{label}] done: {n} item(s) in {time.monotonic() - start:.0f}s", file=sys.stderr, flush=True)
    return out
