"""The unused report: every controller tag, program tag, AOI tag and UDT element nothing uses.

Built on `usage.UsageIndex`, so "used" means exactly what it means everywhere else in the UI:
named by logic, an alias, an alarm, an axis or a module reference somewhere in this L5X. An HMI,
SCADA or another controller can still read a tag this calls unused; the report says "no
references in this project", never "safe to delete".

Four kinds, each a list of items, each item a list of elements:

  controller_tags  one item a controller-scope tag; elements its leaf members and elements
  program_tags     the same, one item a program-scope tag ("Program/Tag")
  aoi_tags         one item an AOI definition; elements its parameters and local tags
  udt_elements     one item a user data type; elements its members

An item is "used" when it and every element of it are used, "partial" when it is used but at
least one element is not, and "unused" when nothing of it is.

Arrays: an array of an atomic type up to ARRAY_ELEMENT_LIMIT elements lists each element; a
larger one, or an array of a structure, is listed as `[*]` (any element), with the structure's
members under it. Structures are followed MEMBER_DEPTH levels deep.
"""

from __future__ import annotations

from l5x_memory_analyzer.usage import (CONTROLLER_SCOPE, HIDDEN_MEMBER_PREFIX, SYSTEM_MEMBERS, WILD,
                                       UsageIndex, _Node)

ARRAY_ELEMENT_LIMIT = 64
MEMBER_DEPTH = 4
ELEMENT_LIMIT = 2000

KINDS = (("controller_tags", "Controller Tags"), ("program_tags", "Program Tags"),
         ("aoi_tags", "AOI Tags"), ("udt_elements", "UDT Elements"))


def _dims(text: str) -> list[int]:
    try:
        return [int(d) for d in (text or "0").split() if int(d) > 0]
    except ValueError:
        return []


def _visible(member: str) -> bool:
    return member not in SYSTEM_MEMBERS and not member.startswith(HIDDEN_MEMBER_PREFIX)


class UnusedReport:
    def __init__(self, usage: UsageIndex) -> None:
        self.u = usage

    # ---- one tag ---------------------------------------------------------

    def _paths(self, dtype: str, dims: str, depth: int = 0):
        """(segments, data type) for every leaf element of a declaration."""
        members = self.u._members
        sizes = _dims(dims)
        if sizes:
            total = 1
            for s in sizes:
                total *= s
            if dtype not in members and total <= ARRAY_ELEMENT_LIMIT and len(sizes) == 1:
                for i in range(total):
                    yield [f"[{i}]"], dtype
                return
            for segs, t in self._paths(dtype, "0", depth):
                yield [WILD] + segs, t
            return
        if dtype in members and depth < MEMBER_DEPTH and members[dtype]:
            any_member = False
            for name, (mtype, mdims) in members[dtype].items():
                if not _visible(name):
                    continue
                any_member = True
                for segs, t in self._paths(mtype, mdims, depth + 1):
                    yield [f".{name}"] + segs, t
            if any_member:
                return
        yield [], dtype

    def _walk(self, root: _Node | None, segs: list[str], dtype: str) -> tuple[int, bool, int]:
        """(uses, used as part of a whole, uses by the AOI's own logic) of one element."""
        if root is None:
            return 0, False, 0
        frontier, whole, cur = [root], False, dtype
        for s in segs:
            if any(n.end for n in frontier):
                whole = True
            if s.startswith(".") and cur in self.u._aoi_names and any(n.n for n in frontier):
                internal = self.u._aoi_internal.get((cur, s[1:]), 0)
                if internal:
                    return 0, whole, internal
            nxt = []
            for n in frontier:
                for key, kid in n.kids.items():
                    if key == s or (s.startswith("[") and (s == WILD and key.startswith("[") or key == WILD)):
                        nxt.append(kid)
            frontier = nxt
            if s.startswith("."):
                cur = self.u._members.get(cur, {}).get(s[1:], (None,))[0]
            if not frontier:
                return 0, whole, 0
        return sum(n.n for n in frontier), whole, 0

    def _tag(self, scope: str, name: str, dtype: str, dims: str) -> dict:
        root = self.u._tries.get(f"{scope}/{name}")
        elements, truncated = [], False
        for segs, etype in self._paths(dtype, dims):
            if len(elements) >= ELEMENT_LIMIT:
                truncated = True
                break
            count, whole, internal = self._walk(root, segs, dtype)
            elements.append({"name": name + "".join(segs), "type": etype or "", "uses": count,
                             "whole": whole, "internal": internal,
                             "used": bool(count or whole or internal)})
        used_self = root is not None and root.n > 0
        if not used_self:
            for e in elements:
                e.update(uses=0, whole=False, internal=0, used=False)
        return self._item(name, dtype + (f"[{dims.replace(' ', ',')}]" if _dims(dims) else ""),
                          used_self, elements, truncated)

    @staticmethod
    def _item(name: str, type_text: str, used_self: bool, elements: list[dict], truncated: bool = False) -> dict:
        unused = sum(1 for e in elements if not e["used"])
        if not used_self or (elements and unused == len(elements)):
            status = "unused"
        elif unused:
            status = "partial"
        else:
            status = "used"
        return {"name": name, "type": type_text, "status": status, "elements": elements,
                "unused_elements": unused, "truncated": truncated}

    # ---- the four kinds --------------------------------------------------

    def _scope_tags(self, scope: str, label=lambda n: n) -> list[dict]:
        return [{**self._tag(scope, name, dtype, dims), "name": label(name)}
                for name, (dtype, dims) in sorted(self.u._types.get(scope, {}).items(), key=lambda kv: kv[0].lower())]

    def controller_tags(self) -> list[dict]:
        return self._scope_tags(CONTROLLER_SCOPE)

    def program_tags(self) -> list[dict]:
        out = []
        for scope in sorted(s for s in self.u._types if s.startswith("program:")):
            program = scope[len("program:"):]
            out += self._scope_tags(scope, lambda n, p=program: f"{p}/{n}")
        return out

    def aoi_tags(self) -> list[dict]:
        out = []
        for aoi in sorted(self.u._aoi_names, key=str.lower):
            called = self.u.aoi_calls(aoi) > 0 or self.u.type_instances(aoi) > 0
            elements = []
            for name, (mtype, mdims) in self.u._members.get(aoi, {}).items():
                if not _visible(name):
                    continue
                internal = self.u._aoi_internal.get((aoi, name), 0)
                outside = self.u._type_member.get((aoi, name), 0) - internal
                used = called and bool(internal or outside)
                elements.append({"name": name, "type": mtype + (f"[{mdims}]" if _dims(mdims) else ""),
                                 "uses": max(outside, 0) if called else 0, "whole": False,
                                 "internal": internal if called else 0, "used": used})
            out.append(self._item(aoi, "AOI", called, elements))
        return out

    def udt_elements(self) -> list[dict]:
        out = []
        for dt in self.u._root.iter("DataType"):
            name = dt.get("Name")
            if dt.get("Class") not in (None, "User"):
                continue
            instances = self.u.type_instances(name)
            whole = self.u.copied_whole(name)
            elements = []
            for m in dt.iter("Member"):
                member = m.get("Name")
                if not _visible(member):
                    continue
                count = self.u._type_member.get((name, member), 0) if instances else 0
                elements.append({"name": member, "type": (m.get("DataType") or "")
                                 + (f"[{m.get('Dimension')}]" if _dims(m.get("Dimension")) else ""),
                                 "uses": count, "whole": bool(instances and whole), "internal": 0,
                                 "used": bool(instances and (count or whole))})
            item = self._item(name, "String" if dt.get("Family") == "StringFamily" else "UDT", instances > 0, elements)
            item["instances"] = instances
            out.append(item)
        return sorted(out, key=lambda i: i["name"].lower())

    def build(self) -> dict:
        kinds = []
        for key, label in KINDS:
            items = getattr(self, key)()
            kinds.append({"key": key, "label": label, "items": items,
                          "counts": {s: sum(1 for i in items if i["status"] == s)
                                     for s in ("used", "partial", "unused")}})
        return {"kinds": kinds}


def unused_report(usage: UsageIndex) -> dict:
    return UnusedReport(usage).build()
