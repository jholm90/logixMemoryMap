"""Where a UDT or AOI is actually used, everywhere it is reachable.

"This type costs 40KB" is only half an answer. The other half is which
tags carry that cost, and a type is rarely used directly -- it is a member
of a UDT that is a member of another UDT that a tag finally declares. A
flat "tags whose DataType is X" list misses every one of those.

So this walks from every tag DOWNWARD through the member graph and records
each path that arrives at the target type, which is the only way to reach
a type buried three levels inside something else. The paths it returns are
the same drill paths the tree uses, so each one is directly navigable.

Cost is real -- a wide controller has thousands of tags over types nested
several deep -- which is why the UI only asks for this when the tab is
opened, and why the per-type member scan is memoised.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from l5x_memory_analyzer.parser.datatypes import DataTypeDef

# A single walk will not follow a member chain deeper than this. Logix
# itself forbids recursive UDTs, so any chain this long means a malformed
# file rather than real nesting, and the cap keeps a bad file from hanging
# the UI instead of erroring.
MAX_MEMBER_DEPTH = 24


@dataclass(frozen=True)
class Usage:
    path: str          # drill path, e.g. "controller/Stacker.QueueHook[0].ClearWhenDn"
    tag_path: str      # the owning tag, e.g. "controller/Stacker"
    member_path: str   # the part below the tag, e.g. ".QueueHook[0].ClearWhenDn"
    scope: str         # "controller" or the program name
    via: str           # the declaring type -- what the member was declared on
    direct: bool       # True when the tag itself is the type, not a member


def _member_paths_to(
    type_name: str,
    target: str,
    data_types: dict[str, DataTypeDef],
    _depth: int = 0,
    _seen: frozenset[str] = frozenset(),
) -> list[tuple[str, str]]:
    """[(member path, declaring type)] from `type_name` down to `target`.

    _seen guards against a cyclic definition rather than trusting the file
    to be well-formed; MAX_MEMBER_DEPTH bounds the honest-but-deep case.
    """
    if _depth >= MAX_MEMBER_DEPTH or type_name in _seen:
        return []
    dtdef = data_types.get(type_name)
    if dtdef is None:
        return []
    seen = _seen | {type_name}
    found: list[tuple[str, str]] = []
    for member in dtdef.members:
        if member.hidden or member.is_bit_alias:
            continue
        base = f".{member.name}"
        if member.dimension and member.dimension > 0:
            # Element 0 stands for the array. Listing all N would bury the
            # answer in identical rows; the path is still navigable and the
            # count is shown beside it.
            base = f"{base}[0]"
        if member.data_type == target:
            found.append((base, type_name))
        for deeper, declaring in _member_paths_to(
            member.data_type, target, data_types, _depth + 1, seen
        ):
            found.append((base + deeper, declaring))
    return found


def find_usages(
    target: str,
    data_types: dict[str, DataTypeDef],
    tag_index: dict[str, tuple[str, tuple[int, ...]]],
) -> list[Usage]:
    """Every navigable path that lands on `target`, direct or nested."""
    nested_cache: dict[str, list[tuple[str, str]]] = {}
    usages: list[Usage] = []

    for tag_path, (tag_type, dims) in sorted(tag_index.items()):
        scope, _, _ = tag_path.partition("/")
        prefix = "[0]" if dims and math.prod(dims) > 0 else ""
        if tag_type == target:
            usages.append(Usage(
                path=f"{tag_path}{prefix}", tag_path=tag_path, member_path=prefix,
                scope=scope, via=tag_type, direct=True,
            ))
            continue
        if tag_type not in nested_cache:
            nested_cache[tag_type] = _member_paths_to(tag_type, target, data_types)
        for member_path, declaring in nested_cache[tag_type]:
            usages.append(Usage(
                path=f"{tag_path}{prefix}{member_path}", tag_path=tag_path,
                member_path=f"{prefix}{member_path}", scope=scope,
                via=declaring, direct=False,
            ))
    return usages
