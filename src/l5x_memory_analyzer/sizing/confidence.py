"""Confidence-tier ordering, per docs/MEMORY_MODEL.md's KNOWN/ASSUMED/FITTED/UNKNOWN tags."""

from __future__ import annotations

_ORDER = {"KNOWN": 0, "ASSUMED": 1, "FITTED": 2, "UNKNOWN": 3}


def weakest(*confidences: str) -> str:
    """Combining sizes propagates the least-confident tier involved."""
    return max(confidences, key=lambda c: _ORDER[c])
