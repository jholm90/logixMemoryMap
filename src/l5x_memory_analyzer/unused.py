"""Element Usage: every controller tag, program tag, AOI and UDT, and what in it nothing uses.

Built on `usage.UsageIndex`, so "used" means exactly what it means everywhere else in the UI:
named by logic, an alias, an alarm, an axis or a module reference somewhere in this L5X. An HMI,
SCADA or another controller can still read something this calls unused; the tab says "no
references in this project", never "safe to delete".

Four kinds, each a list of items; each item is a tree of its elements, browsed column by column:

  controller_tags  one item a controller-scope tag; its members and array elements below it
  program_tags     the same for program-scope tags ("Program/Tag")
  aoi_tags         one item an AOI definition; its parameters and local tags, then their members
  udt_elements     one item a user data type; its members, then theirs

Sizes are the engine's (`sizing.tree.expand_children`): a tag's own figure from the report, an
element's the bytes it occupies, an AOI or UDT item one instance. Usage is counted on the leaves:
an item or element reads "u of k used", and is "used" when every leaf is, "partial" when some
are, "unused" when none is.

A tag's element is used when logic reaches it: by name, through an index (`Arr[Idx]` uses every
element), as part of a whole structure passed as one (COP, an AOI InOut), or, for an AOI
instance, by the AOI's own logic on each call. An AOI or UDT member is used when anything names
it on any instance; a UDT copied whole somewhere counts all its members used.
"""

from __future__ import annotations

from l5x_memory_analyzer.sizing.tree import expand_children
from l5x_memory_analyzer.sizing.udt import compute_array_size
from l5x_memory_analyzer.usage import (CONTROLLER_SCOPE, HIDDEN_MEMBER_PREFIX, SYSTEM_MEMBERS, WILD,
                                       UsageIndex, _Node)

MAX_LEVELS = 6               # element levels below an item
ARRAY_LIST_LIMIT = 256       # a larger array is one "[*]" element: any index
NODE_BUDGET = 20000          # elements per item before the rest are left unexpanded

KINDS = (("controller_tags", "Controller Tags"), ("program_tags", "Program Tags"),
         ("aoi_tags", "AOI Tags"), ("udt_elements", "UDT Elements"))


def _visible(name: str) -> bool:
    return name not in SYSTEM_MEMBERS and not name.startswith(HIDDEN_MEMBER_PREFIX)


def _type_text(dtype: str, dims: tuple[int, ...]) -> str:
    return dtype + (f"[{','.join(str(d) for d in dims)}]" if dims else "")


def _dims(text) -> tuple[int, ...]:
    try:
        return tuple(int(d) for d in str(text or "0").split() if int(d) > 0)
    except ValueError:
        return ()


def _status(used: int, total: int) -> str:
    if total and used == total:
        return "used"
    return "partial" if used else "unused"


class _Budget:
    def __init__(self) -> None:
        self.left = NODE_BUDGET
        self.truncated = False

    def take(self) -> bool:
        if self.left <= 0:
            self.truncated = True
            return False
        self.left -= 1
        return True


class UnusedReport:
    def __init__(self, usage: UsageIndex, data_types: dict, model, tag_bytes: dict[str, float] | None = None) -> None:
        self.u = usage
        self.types = data_types
        self.model = model
        self.tag_bytes = tag_bytes or {}
        self._kid_cache: dict = {}

    # ---- the engine's children ------------------------------------------

    def _kids(self, dtype: str, dims: tuple[int, ...]) -> list[tuple[str, str, str, tuple, float]]:
        """(label, segment, data type, dims, bytes) one level down, or [] for a leaf."""
        key = (dtype, dims)
        if key not in self._kid_cache:
            out = []
            n = 1
            for d in dims:
                n *= d
            if dims and n > ARRAY_LIST_LIMIT:
                out = [(f"[*] any of {n:,}", WILD, dtype, (), self._size(dtype, dims))]
            else:
                try:
                    children = expand_children(dtype, dims, self.types, self.model)
                except Exception:
                    children = []
                for c in children:
                    if not c.segment:                       # an overhead row, not an element
                        continue
                    if c.segment.startswith(".") and not _visible(c.segment[1:]):
                        continue
                    out.append((c.name, c.segment, c.data_type, tuple(c.dimensions), c.bytes))
            self._kid_cache[key] = out
        return self._kid_cache[key]

    def _size(self, dtype: str, dims: tuple[int, ...]) -> float:
        try:
            return compute_array_size(dtype, dims, self.types, self.model)[0]
        except Exception:
            return 0

    # ---- tags --------------------------------------------------------------

    def _step(self, frontier: list[_Node], seg: str) -> list[_Node]:
        """The usage-trie nodes one segment down: an index also matches a run-time index
        (`[*]` in the trie), and the "[*]" element matches every index."""
        nxt = []
        for n in frontier:
            if seg == WILD:
                nxt += [kid for key, kid in n.kids.items() if key.startswith("[")]
                continue
            kid = n.kids.get(seg)
            if kid is not None:
                nxt.append(kid)
            if seg.startswith("["):
                kid = n.kids.get(WILD)
                if kid is not None:
                    nxt.append(kid)
        return nxt

    def _tag_node(self, label, dtype, dims, size, frontier, whole, implicit, level, budget) -> dict:
        """One element of a tag, with the usage-trie nodes that reach it (`frontier`),
        whether a whole-structure use sits above it, and its AOI-logic uses."""
        node = {"n": label, "t": _type_text(dtype, dims), "s": size}
        kids = self._kids(dtype, dims) if level < MAX_LEVELS else []
        children = []
        whole_here = whole or any(n.end for n in frontier)
        called = any(n.n for n in frontier)
        for k_label, seg, k_type, k_dims, k_bytes in kids:
            if not budget.take():
                break
            internal = 0
            if seg.startswith(".") and dtype in self.u._aoi_names and called:
                internal = self.u._aoi_internal.get((dtype, seg[1:]), 0)
            children.append(self._tag_node(k_label, k_type, k_dims, k_bytes, self._step(frontier, seg),
                                           whole_here, internal or implicit, level + 1, budget))
        if children:
            node["c"] = children
            node["u"] = sum(c["u"] for c in children)
            node["k"] = sum(c["k"] for c in children)
            return node
        uses = sum(n.n for n in frontier)
        used = bool(uses or whole or implicit)
        node.update(u=int(used), k=1, x=uses, w=bool(whole and not uses), i=implicit)
        return node

    def _tag(self, scope: str, name: str, label: str, dtype: str, dims_text) -> dict:
        dims = _dims(dims_text)
        root = self.u._tries.get(f"{scope}/{name}")
        size = self.tag_bytes.get(f"{scope}/{name}")
        if size is None:
            size = self._size(dtype, dims)
        budget = _Budget()
        node = self._tag_node(label, dtype, dims, size, [root] if root is not None else [], False, 0, 0, budget)
        node["truncated"] = budget.truncated
        return node

    def _scope(self, scope: str, label=lambda n: n) -> list[dict]:
        return [self._tag(scope, name, label(name), dtype, dims)
                for name, (dtype, dims) in sorted(self.u._types.get(scope, {}).items(), key=lambda kv: kv[0].lower())]

    def controller_tags(self) -> list[dict]:
        return self._scope(CONTROLLER_SCOPE)

    def program_tags(self) -> list[dict]:
        out = []
        for scope in sorted(s for s in self.u._types if s.startswith("program:")):
            program = scope[len("program:"):]
            out += self._scope(scope, lambda n, p=program: f"{p}/{n}")
        return out

    # ---- definitions -------------------------------------------------------

    def _member_used(self, owner: str, member: str) -> tuple[int, bool, int]:
        internal = self.u._aoi_internal.get((owner, member), 0)
        named = self.u._type_member.get((owner, member), 0) - internal
        whole = owner not in self.u._aoi_names and self.u.copied_whole(owner)
        return max(named, 0), whole, internal

    def _def_node(self, label, owner, member, dtype, dims, size, level, alive, budget) -> dict:
        node = {"n": label, "t": _type_text(dtype, dims), "s": size}
        children = []
        if level < MAX_LEVELS and (dtype in self.types or dtype in self.u._members):
            for k_label, seg, k_type, k_dims, k_bytes in self._kids(dtype, ()):
                if not seg.startswith(".") or not budget.take():
                    continue
                children.append(self._def_node(k_label, dtype, seg[1:], k_type, k_dims, k_bytes,
                                               level + 1, alive, budget))
        if children:
            node["c"] = children
            node["u"] = sum(c["u"] for c in children)
            node["k"] = sum(c["k"] for c in children)
            return node
        uses, whole, internal = self._member_used(owner, member) if alive else (0, False, 0)
        used = bool(uses or whole or internal)
        node.update(u=int(used), k=1, x=uses, w=whole, i=internal)
        return node

    def _definition(self, name: str, kind_text: str, alive: bool) -> dict:
        budget = _Budget()
        node = {"n": name, "t": kind_text, "s": self._size(name, ())}
        children = [self._def_node(k_label, name, seg[1:], k_type, k_dims, k_bytes, 1, alive, budget)
                    for k_label, seg, k_type, k_dims, k_bytes in self._kids(name, ())
                    if seg.startswith(".") and budget.take()]
        node["c"] = children
        node["u"] = sum(c["u"] for c in children)
        node["k"] = sum(c["k"] for c in children)
        node["truncated"] = budget.truncated
        return node

    def aoi_tags(self) -> list[dict]:
        return [self._definition(aoi, "AOI", self.u.aoi_calls(aoi) > 0 or self.u.type_instances(aoi) > 0)
                for aoi in sorted(self.u._aoi_names, key=str.lower)]

    def udt_elements(self) -> list[dict]:
        out = []
        for name, dt in self.types.items():
            if getattr(dt, "is_aoi", False):
                continue
            node = self._definition(name, "String" if dt.is_string_family else "UDT", self.u.type_instances(name) > 0)
            node["instances"] = self.u.type_instances(name)
            out.append(node)
        return sorted(out, key=lambda i: i["n"].lower())

    # ---- all of it ---------------------------------------------------------

    def build(self) -> dict:
        kinds = []
        for key, label in KINDS:
            items = getattr(self, key)()
            for it in items:
                it["status"] = _status(it["u"], it["k"])
            kinds.append({"key": key, "label": label, "items": items,
                          "counts": {s: sum(1 for i in items if i["status"] == s)
                                     for s in ("used", "partial", "unused")}})
        return {"kinds": kinds}


def unused_report(usage: UsageIndex, data_types: dict, model, tag_bytes: dict[str, float] | None = None) -> dict:
    return UnusedReport(usage, data_types, model, tag_bytes).build()


def item_summary(item: dict) -> dict:
    """An item without its element tree: what the item column lists."""
    return {k: v for k, v in item.items() if k != "c"} | {"has_children": bool(item.get("c"))}
