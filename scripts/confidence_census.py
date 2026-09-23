"""Every element in a loaded file, bucketed by the confidence the UI shows.

Answers a question tile colours cannot: does the tool actually know what it
is reporting, or does it only look that way? It drives the real load path --
the same _load_state, the same hierarchy, the same subtree summaries -- and
then mirrors the client's own nodeConfidence walk, so the numbers are the
ones on screen rather than a second opinion about them.

Counts elements AND bytes separately, because they disagree sharply: a file
is mostly tiny exact leaves by count and mostly a few large aggregates by
byte. Leaves alone are summed for the byte view, since a parent and its
children would otherwise both be counted.

Run: python scripts/confidence_census.py <file.L5X>
"""

import sys, collections
from pathlib import Path as _P
sys.path.insert(0, str(_P(__file__).resolve().parent.parent / "src"))
from l5x_memory_analyzer.ui import server as S
from l5x_memory_analyzer.sizing.confidence import BANDS, PROVENANCE_BAND

_args = [a for a in sys.argv[1:] if not a.startswith("--")]
SUMMARY = "--summary" in sys.argv
if not _args:
    sys.exit("usage: confidence_census.py [--summary] <file.L5X> [...]")
F = _args[0]
state = S._load_state(F, _P(F).name, from_bytes=False)
R = state.report_json
H = R["hierarchy"]
RC = R.get("routine_confidence") or {}
RI = R.get("routine_instructions") or {}
ACC = R.get("instruction_accuracy") or {}
SCAF = R.get("scaffold_band") or {}
KEC = R.get("known_exact_calls") or {}
PB = R.get("provenance_band") or {}
BY = {b.key: b for b in BANDS}

def band_by_key(k): return BY.get(k or "", BY["UNVERIFIED"])

def band_for_opcode(op):
    if SCAF.get(op): return band_by_key(SCAF[op])
    if KEC.get(op): return band_by_key(KEC[op])
    a = ACC.get(op) or ACC.get(str(op).split("/")[0])
    if not a or not a.get("samples"): return band_by_key("UNVERIFIED")
    w = a["worst_pct"]
    return band_by_key("MEASURED" if w <= .1 else "CLOSE" if w <= 1 else "APPROX" if w <= 5 else "UNVERIFIED")

def node_value(n): return n.get("value") or n.get("bytes") or 0

def band_for_node(n):
    p = n.get("path") or n.get("_tagPath")
    inv = RI.get(p) if p else None
    ops = n.get("rung_instructions") or (inv if inv else None)
    if ops:
        worst = None
        for raw in ops:
            b = band_for_opcode(str(raw).split("(")[0].strip())
            if worst is None or b.pct < worst.pct: worst = b
        if worst: return worst
    return band_by_key(PB.get(n.get("basis") or "", "UNVERIFIED"))

def pct_from_mix(mix):
    bytes_ = w = 0
    for tier in ("KNOWN","FITTED","ASSUMED","UNKNOWN"):
        v = mix.get(tier, 0)
        if v > 0:
            bytes_ += v; w += v * band_by_key(PB.get(tier,"UNVERIFIED")).pct
    return (bytes_, w) if bytes_ else None

def walk(n):
    kids = n.get("children")
    if kids:
        b = w = 0
        for k in kids:
            rb, rw = walk(k); b += rb; w += rw
        if b: return (b, w)
    c = n.get("confidence")
    if c and c.get("total"):
        r = pct_from_mix(c)
        own = node_value(n)
        if r and own > 0: return (own, own * r[1] / r[0])
        if r: return r
    p = n.get("path") or n.get("_tagPath")
    v = node_value(n)
    if p in RC: return (v, v * RC[p])
    return (v, v * band_for_node(n).pct)

def node_pct(n):
    b, w = walk(n)
    return (round(w/b, 1) if b else None), b

def mix_of(node):
    """Bytes per band -- the client's confidenceMix, rule for rule: loaded
    children, then the subtree tier mix, then the routine's per-rung band
    split, then the node's own band."""
    RBM = R.get("routine_band_mix") or {}
    mix = collections.Counter()
    def walk(n):
        kids = n.get("children")
        if kids:
            got = sum(walk(k) for k in kids)
            if got: return got
        c = n.get("confidence")
        if c and c.get("total"):
            mt = sum(max(c.get(t, 0), 0) for t in ("KNOWN","FITTED","ASSUMED","UNKNOWN"))
            if mt > 0:
                own = node_value(n)
                scale = own / mt if own > 0 else 1
                for tier in ("KNOWN","FITTED","ASSUMED","UNKNOWN"):
                    v = c.get(tier, 0)
                    if v > 0: mix[PB.get(tier, "UNVERIFIED")] += v * scale
                return own if own > 0 else mt
        v = node_value(n)
        split = RBM.get(n.get("path") or n.get("_tagPath"))
        if split:
            for k, frac in split.items(): mix[k] += v * frac
            return v
        mix[band_for_node(n).key] += v
        return v
    walk(node)
    return mix

if SUMMARY:
    import os as _os
    def _summ(state_, name):
        global R, H, RC, RI, ACC, SCAF, KEC, PB
        R = state_.report_json; H = R["hierarchy"]
        RC = R.get("routine_confidence") or {}; RI = R.get("routine_instructions") or {}
        ACC = R.get("instruction_accuracy") or {}; SCAF = R.get("scaffold_band") or {}
        KEC = R.get("known_exact_calls") or {}; PB = R.get("provenance_band") or {}
        mx = mix_of(H); tot = sum(mx.values()) or 1
        pct = sum(v * BY[k].pct for k, v in mx.items()) / tot
        em = (mx["EXACT"] + mx["MEASURED"]) / tot * 100
        cols = "  ".join(f"{k[:5]} {100*mx[k]/tot:5.1f}%" for k in
                         ("EXACT","MEASURED","CLOSE","APPROX","UNVERIFIED","UNPRICED"))
        print(f"{name:28s} {pct:6.2f}%  exact+measured {em:5.1f}%  | {cols}")
    _summ(state, _os.path.basename(F)[:28])
    for extra in _args[1:]:
        _summ(S._load_state(extra, _P(extra).name, from_bytes=False), _os.path.basename(extra)[:28])
    sys.exit(0)

# Expand every drillable node the way the UI does on click.
def expand(n, depth=0):
    if n.get("children"): 
        for k in n["children"]: expand(k, depth+1)
        return
    if not n.get("has_children") or not n.get("data_type"): return
    # A type DEFINITION node carries its type name as data_type, but it is
    # not an instance: the UI drills it into its declaration breakdown, not
    # into instance members. Expanding it as an instance inflated the count.
    if (n.get("path") or "").startswith(("udt_definitions/", "aoi_definitions/")): return
    try:
        kids = S._expand_cached(n["data_type"], tuple(n.get("dimensions") or ()), state)
    except Exception:
        return
    if not kids: return
    out = []
    for c in kids:
        d = {"name": c.name, "segment": c.segment, "data_type": c.data_type,
             "dimensions": list(c.dimensions), "value": c.bytes,
             "basis": c.basis, "has_children": c.has_children,
             "alias_of": c.alias_of,
             "confidence": S._child_confidence(c, state)}
        out.append(d)
    n["children"] = out
    if depth < 40:
        for k in out: expand(k, depth+1)

for c in H.get("children") or []: expand(c)

rows = []
def collect(n, path=""):
    nm = n.get("name") or ""
    p = f"{path}>{nm}" if path else nm
    pct, b = node_pct(n)
    rows.append((p, nm, pct, b, bool(n.get("children") or n.get("has_children"))))
    for k in (n.get("children") or []): collect(k, p)
for c in H.get("children") or []: collect(c)

print(f"file total: {sum((e.bytes or 0) for e in state.entries):,} bytes")
print(f"elements enumerated: {len(rows):,}\n")

def bucket(p):
    if p is None: return "no bytes"
    if p >= 99.5: return "100  Exact"
    if p >= 97.5: return " 98  Measured"
    if p >= 89.5: return " 90  Close"
    if p >= 74.5: return " 75  Approximate"
    if p >= 49.5: return " 50  Unverified"
    if p > 0: return "  1-49 mixed"
    return "  0  Not counted"

cnt = collections.Counter()
leaf_cnt = collections.Counter()
leaf_byt = collections.Counter()
for _, _, pct, b, drill in rows:
    k = bucket(pct)
    cnt[k] += 1
    if not drill:                      # leaves only: these sum to the file
        leaf_cnt[k] += 1
        leaf_byt[k] += b

order = ["100  Exact"," 98  Measured"," 90  Close"," 75  Approximate",
         "  1-49 mixed"," 50  Unverified","  0  Not counted","no bytes"]
tot_el = len(rows)
tot_leaf = sum(leaf_cnt.values()) or 1
tot_b = sum(leaf_byt.values()) or 1

print("EVERY element in the tree (parents and leaves), by confidence:")
print(f"{'band':18s} {'elements':>11s} {'% of elements':>14s}")
for k in order:
    if not cnt[k]: continue
    print(f"{k:18s} {cnt[k]:11,d} {100*cnt[k]/tot_el:13.1f}%")

print(f"\nLEAVES only -- the things that actually hold bytes "
      f"({tot_leaf:,} of them, {tot_b:,.0f} bytes):")
print(f"{'band':18s} {'leaves':>11s} {'% leaves':>10s} {'bytes':>14s} {'% bytes':>9s}")
for k in order:
    if not leaf_cnt[k] and not leaf_byt[k]: continue
    print(f"{k:18s} {leaf_cnt[k]:11,d} {100*leaf_cnt[k]/tot_leaf:9.1f}% "
          f"{leaf_byt[k]:14,.0f} {100*leaf_byt[k]/tot_b:8.1f}%")

GREEN = ("100  Exact"," 98  Measured")
print(f"\nExact or Measured : {sum(cnt[k] for k in GREEN):,}/{tot_el:,} elements "
      f"({100*sum(cnt[k] for k in GREEN)/tot_el:.1f}%)")
print(f"                    {sum(leaf_byt[k] for k in GREEN):,.0f} bytes "
      f"({100*sum(leaf_byt[k] for k in GREEN)/tot_b:.1f}%)")

print("\nTop-level groups as the user first sees them:")
for c in H.get("children") or []:
    pct, b = node_pct(c)
    if not b: continue
    print(f"   {c.get('name'):34s} {pct if pct is not None else 0:5.1f}%  {b:12,.0f} bytes")

print("\n\nWHAT IS ACTUALLY LOW-CONFIDENCE (leaves under 98%), grouped:")
low = collections.Counter(); lowb = collections.Counter()
for path, nm, pct, b, drill in rows:
    if drill or pct is None or pct >= 97.5: continue
    top = path.split(">")[0]
    key = (top, round(pct))
    low[key] += 1; lowb[key] += b
for (top, pct), n in sorted(lowb.items(), key=lambda kv: -kv[1])[:20]:
    print(f"   {pct:3d}%  {top:38s} {low[(top,pct)]:6,d} leaves {lowb[(top,pct)]:12,.0f} bytes")

print("\nSample of the 50% leaves (name -> bytes):")
shown = 0
for path, nm, pct, b, drill in rows:
    if drill or pct is None or pct > 55 or b <= 0: continue
    print(f"   {b:9,.0f}  {path[:110]}")
    shown += 1
    if shown >= 12: break
