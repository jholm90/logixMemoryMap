// Vanilla JS/SVG squarified treemap -- no external deps by design, since this
// runs on engineering workstations that are frequently airgapped OT networks.
//
// Infinite-depth lazy drill-down (James, 2026-08-20): a node's .children is
// only populated when the user actually drills into it, via /api/node --
// never masks a large array or deep UDT nesting just because materializing
// the whole tree up front would be enormous. Color is reserved for data
// type; confidence is shown as solid (KNOWN) vs. diagonal-hatch overlay
// (anything else) instead.

let REPORT = null;
let CURRENT_NODE = null; // node currently shown as the treemap root
let NODE_STACK = [];     // ancestors of CURRENT_NODE, for the breadcrumb
let SORT_STATE = { key: "bytes", dir: -1 };
let SPLIT_OPEN = false;  // James 2026-08-27: List/Type Summary docked
                         // alongside the treemap, always-available toggle
let DEPTH2_ENABLED = false; // James 2026-08-27: render grandchildren nested
                             // inside their parent's tile

async function main() {
  setupTabs();
  setupSplitDock();
  setupDepth2Toggle();
  setupTreemapResize();
  setupFileOpen();
  await loadReport();
}

async function loadReport() {
  const res = await fetch("/api/report");
  REPORT = await res.json();
  renderAll();
}

function renderAll() {
  const loaded = !!(REPORT && REPORT.loaded !== false);
  document.getElementById("empty-state").classList.toggle("hidden", loaded);
  document.querySelector("main").style.display = loaded ? "" : "none";
  document.getElementById("tabs").style.display = loaded ? "" : "none";
  if (!loaded) {
    document.getElementById("file-info").textContent = "No file loaded";
    document.getElementById("export-warning").classList.add("hidden");
    document.getElementById("safety-warning").classList.add("hidden");
    document.getElementById("export-buttons").classList.add("hidden");
    return;
  }

  const infoParts = [`Schema ${REPORT.schema_revision}`];
  if (REPORT.software_revision) infoParts.push(`Software ${REPORT.software_revision}`);
  if (REPORT.processor_type) infoParts.push(REPORT.processor_type);
  document.getElementById("file-info").textContent =
    `${REPORT.file_name}  (${infoParts.join(", ")})`;
  document.getElementById("export-buttons").classList.remove("hidden");

  const safetyWarn = document.getElementById("safety-warning");
  if (REPORT.is_safety_project) {
    safetyWarn.classList.remove("hidden");
    safetyWarn.textContent =
      `This is a Safety-rated project (${REPORT.safety_level}) -- Safety Task/Program content is ` +
      `NOT sized by this tool at all. The total below is understated, not a full picture. Treat it ` +
      `as informational only until Safety content sizing is built (OQ-SAFETY).`;
  } else {
    safetyWarn.classList.add("hidden");
  }

  const warn = document.getElementById("export-warning");
  if (!REPORT.is_controller_export) {
    warn.classList.remove("hidden");
    warn.textContent =
      `This is a "${REPORT.target_type || "unknown"}"-type export, not a full Controller export -- ` +
      `totals may be incomplete (only what this partial export actually contains). Full support for ` +
      `Program/UDT/AOI-only exports is a feature-request item, not yet built.`;
  } else {
    warn.classList.add("hidden");
  }

  const fill = document.getElementById("budget-bar-fill");
  const label = document.getElementById("budget-label");
  if (REPORT.budget_bytes) {
    const pct = (REPORT.total_bytes / REPORT.budget_bytes) * 100;
    fill.style.width = `${Math.min(pct, 100)}%`;
    fill.classList.toggle("over", pct > 100);
    const archNote = REPORT.budget_architecture === "divided" ? " (I/O + Data/Logic pools summed)" : "";
    label.textContent =
      `${fmtBytes(REPORT.total_bytes)} / ${fmtBytes(REPORT.budget_bytes)} (${pct.toFixed(2)}%)${archNote}`;
  } else {
    // James (2026-08-20): capacity is part-number specific, don't fake a
    // number for a processor type we don't have real data for.
    fill.style.width = "0%";
    fill.classList.remove("over");
    label.textContent =
      `${fmtBytes(REPORT.total_bytes)} used -- budget unknown for processor "${REPORT.processor_type || "?"}"`;
  }

  const errEl = document.getElementById("errors-footer");
  if (REPORT.errors && REPORT.errors.length) {
    errEl.classList.remove("hidden");
    errEl.textContent = `${REPORT.errors.length} tag(s) could not be sized: ` +
      REPORT.errors.slice(0, 5).map(e => `${e.path} (${e.message})`).join("; ") +
      (REPORT.errors.length > 5 ? ` ...and ${REPORT.errors.length - 5} more` : "");
  } else {
    errEl.classList.add("hidden");
  }

  CURRENT_NODE = REPORT.hierarchy;
  annotateTagPaths(CURRENT_NODE);
  NODE_STACK = [];

  renderCurrentLevel();
}

// Re-renders everything that depends on CURRENT_NODE -- called after any
// navigation (drill in, breadcrumb click, sibling jump) so the List and
// Type Summary tabs (and their docked twins, see setupSplitDock) stay in
// sync with wherever the treemap is, even when they're not the active tab.
function renderCurrentLevel() {
  renderBreadcrumb();
  renderTreemap();
  renderList();
  renderTypeSummary();
}

// The initial /api/report hierarchy is always exactly 3 levels: root ->
// scope group ("Controller Tags" / "Program: X" / "Type Definitions" /
// "Project Overhead") -> leaf. Only the leaves need a _tagPath/_subPath for
// lazy /api/node fetches -- anything deeper than that is fetched on demand
// (see ensureChildren), which sets _tagPath/_subPath directly on the
// freshly created child nodes itself. Applies uniformly to every group,
// not just the tag-scope ones -- a "Type Definitions" leaf's `path` is
// already "udt_definitions/<Name>" (see hierarchy.py), which /api/node's
// dedicated branch resolves the same way (2026-08-26, defs-pool drill-down).
function annotateTagPaths(root) {
  for (const group of root.children || []) {
    for (const leaf of group.children || []) {
      leaf._tagPath = leaf.path;
      leaf._subPath = "";
    }
  }
}

function fmtBytes(n) {
  if (n == null) return "-";
  if (n < 1 && n > 0) return n.toFixed(3) + " B (shared/packed)";
  if (n >= 1024 * 1024) return (n / (1024 * 1024)).toFixed(2) + " MB";
  if (n >= 1024) return (n / 1024).toFixed(1) + " KB";
  return Math.round(n) + " B";
}

function nodeValue(node) {
  if (typeof node.value === "number") return node.value;
  if (!node.children) return 0;
  return node.children.reduce((s, c) => s + nodeValue(c), 0);
}

// A node is drillable if it already has children, or the backend says it
// would (lazy -- not fetched yet). A true leaf has neither.
function isDrillable(node) {
  return !!(node.children || node.has_children);
}

function isGroup(node) {
  // Structural group (root / scope groups) vs. a typed tag/member node.
  return node.data_type == null;
}

// Real rung count for a routine_logic leaf, keyed by the exact same
// routine.path every such leaf's own node.path already carries (James,
// 2026-08-27: "routines need to have indication how many rungs").
function rungCountFor(node) {
  return REPORT && REPORT.rung_counts ? REPORT.rung_counts[node.path] : null;
}

// A "Program: X" group's routine count, read off its own nested "Routines"
// subgroup (hierarchy.py always builds this subgroup when a program has
// any routine_logic entries) -- no backend change needed, the count is
// just that subgroup's own child count.
function routineCountFor(groupNode) {
  if (!isGroup(groupNode) || !groupNode.children) return null;
  const routines = groupNode.children.find(c => c.name === "Routines");
  return routines && routines.children ? routines.children.length : null;
}

// ---- tabs ----

function setupTabs() {
  document.querySelectorAll(".tab-btn[data-tab]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn[data-tab]").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`panel-${btn.dataset.tab}`).classList.add("active");
      if (btn.dataset.tab === "treemap") renderTreemap();
    });
  });
}

// James 2026-08-27: "Type/list should be always visible but hidden. if
// clicked the treeview should resize to fit half size and share with the
// type/list." A single always-visible toggle button splits the Treemap
// panel in half, docking a mini List/Type-Summary pane (its own small
// tab pair) alongside the SVG. The full-page List/Type Summary tabs are
// untouched -- this is an additional way to see the same data, not a
// replacement.
function setupSplitDock() {
  const btn = document.getElementById("split-toggle");
  const treemapPanel = document.getElementById("panel-treemap");
  btn.addEventListener("click", () => {
    SPLIT_OPEN = !SPLIT_OPEN;
    treemapPanel.classList.toggle("split-mode", SPLIT_OPEN);
    btn.classList.toggle("active", SPLIT_OPEN);
    // Let the layout settle before measuring the SVG's new (halved) width.
    requestAnimationFrame(renderTreemap);
  });

  document.querySelectorAll(".dock-tab-btn").forEach(dbtn => {
    dbtn.addEventListener("click", () => {
      document.querySelectorAll(".dock-tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".dock-panel").forEach(p => p.classList.remove("active"));
      dbtn.classList.add("active");
      document.querySelector(`.dock-panel[data-dock-panel="${dbtn.dataset.dock}"]`).classList.add("active");
    });
  });
}

// James 2026-08-27: "the treeview shows a nice map on stuff that level, i
// think we need the option/checkbox to see two levels deep with there
// being some obvious difference between parent/children." See
// renderTreemap's nested-squarify block for the paint side; nested tiles
// get a dashed stroke + reduced opacity + smaller label so they're never
// mistaken for a same-level sibling.
function setupDepth2Toggle() {
  document.getElementById("depth2-toggle").addEventListener("change", ev => {
    DEPTH2_ENABLED = ev.target.checked;
    renderTreemap();
  });
}

function setupTreemapResize() {
  let t;
  window.addEventListener("resize", () => {
    clearTimeout(t);
    t = setTimeout(renderTreemap, 100);
  });
}

// ---- File -> Open ----

function setupFileOpen() {
  for (const id of ["file-input", "file-input-2"]) {
    document.getElementById(id).addEventListener("change", async ev => {
      const file = ev.target.files[0];
      if (!file) return;
      const formData = new FormData();
      formData.append("file", file);
      document.getElementById("file-info").textContent = `Loading ${file.name}...`;
      const res = await fetch("/api/load", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) {
        alert(`Failed to load ${file.name}: ${data.error || res.statusText}`);
        return;
      }
      REPORT = data;
      renderAll();
      ev.target.value = "";
    });
  }
}

// ---- breadcrumb / drill ----

function renderBreadcrumb() {
  const el = document.getElementById("breadcrumb");
  el.innerHTML = "";
  const chain = [...NODE_STACK, CURRENT_NODE];
  chain.forEach((node, i) => {
    if (i > 0) {
      const sep = document.createElement("span");
      sep.className = "sep";
      sep.textContent = "›";
      el.appendChild(sep);
    }
    const crumb = document.createElement("span");
    crumb.textContent = node.name === "root" ? "All" : node.name;
    crumb.addEventListener("click", () => {
      NODE_STACK = chain.slice(0, i);
      CURRENT_NODE = node;
      renderCurrentLevel();
    });

    // Sibling browser: hover a crumb to jump sideways without backing all
    // the way up and re-drilling down (James, 2026-08-20). The parent's
    // children are already sitting in memory -- every ancestor here got
    // onto the breadcrumb by having its children enumerated already.
    if (i > 0) {
      const parent = chain[i - 1];
      const siblings = (parent.children || []).filter(s => s !== node);
      if (siblings.length) {
        crumb.addEventListener("mouseenter", () => showSiblingPreview(crumb, parent, siblings, chain.slice(0, i)));
        crumb.addEventListener("mouseleave", scheduleHideSiblingPreview);
      }
    }

    el.appendChild(crumb);
  });
}

let _siblingHideTimer = null;

function showSiblingPreview(anchorEl, parentNode, siblings, stackForJump) {
  clearTimeout(_siblingHideTimer);
  hideSiblingPreview();

  const popup = document.createElement("div");
  popup.id = "sibling-popup";
  const preview = siblings.slice(0, 10);
  popup.innerHTML =
    `<div class="sibling-popup-header">${preview.length} of ${siblings.length} siblings under "${parentNode.name === "root" ? "All" : parentNode.name}"</div>` +
    preview.map((s, idx) =>
      `<div class="sibling-item" data-idx="${idx}">${s.name} <span class="sibling-bytes">${fmtBytes(nodeValue(s))}</span></div>`
    ).join("");

  popup.addEventListener("mouseenter", () => clearTimeout(_siblingHideTimer));
  popup.addEventListener("mouseleave", scheduleHideSiblingPreview);
  popup.querySelectorAll(".sibling-item").forEach((el, idx) => {
    el.addEventListener("click", () => {
      hideSiblingPreview();
      jumpToSibling(preview[idx], stackForJump);
    });
  });

  document.body.appendChild(popup);
  const rect = anchorEl.getBoundingClientRect();
  popup.style.left = rect.left + "px";
  popup.style.top = (rect.bottom + 4) + "px";
}

function scheduleHideSiblingPreview() {
  _siblingHideTimer = setTimeout(hideSiblingPreview, 250);
}

function hideSiblingPreview() {
  const existing = document.getElementById("sibling-popup");
  if (existing) existing.remove();
}

async function jumpToSibling(sibling, parentStack) {
  const kids = await ensureChildren(sibling);
  if (!kids || !kids.length) return; // leaf sibling -- nothing to show as a treemap root
  NODE_STACK = parentStack;
  CURRENT_NODE = sibling;
  renderCurrentLevel();
}

async function ensureChildren(node) {
  if (node.children) return node.children;
  if (!node.has_children) return null;

  const params = new URLSearchParams({ tag: node._tagPath || "", path: node._subPath || "" });
  const res = await fetch(`/api/node?${params}`);
  if (!res.ok) {
    console.error("failed to expand node", node, await res.text());
    return null;
  }
  const data = await res.json();
  node.children = data.children.map(c => ({
    name: c.name,
    value: c.value,
    data_type: c.data_type,
    basis: c.basis,
    has_children: c.has_children,
    tier: "exact",
    _tagPath: node._tagPath,
    _subPath: (node._subPath || "") + c.segment,
  }));
  return node.children;
}

async function drillInto(node) {
  if (!isDrillable(node)) return;
  const kids = await ensureChildren(node);
  if (!kids || !kids.length) return;
  NODE_STACK.push(CURRENT_NODE);
  CURRENT_NODE = node;
  renderCurrentLevel();
}

// ---- squarified treemap ----

function layoutArea(items, x, y, w, h, scale) {
  const shortSide = Math.min(w, h);
  let row = [items[0]];
  let rowSum = items[0].v;
  let best = worstRatio(rowSum, row, scale, shortSide);
  let i = 1;
  while (i < items.length) {
    const testSum = rowSum + items[i].v;
    const testRatio = worstRatio(testSum, row.concat([items[i]]), scale, shortSide);
    if (testRatio <= best) {
      row.push(items[i]);
      rowSum = testSum;
      best = testRatio;
      i++;
    } else {
      break;
    }
  }
  return { row, rowSum, consumed: i };
}

function worstRatio(rowSum, row, scale, shortSide) {
  const rowArea = rowSum * scale;
  const thickness = shortSide > 0 ? rowArea / shortSide : 0;
  let worst = 1;
  for (const item of row) {
    const itemArea = item.v * scale;
    const length = thickness > 0 ? itemArea / thickness : 0;
    if (length <= 0) continue;
    const ratio = Math.max(thickness / length, length / thickness);
    if (isFinite(ratio)) worst = Math.max(worst, ratio);
  }
  return worst;
}

function squarify(nodes, x, y, w, h, out) {
  let items = nodes
    .map(n => ({ node: n, v: nodeValue(n) }))
    .filter(i => i.v > 0)
    .sort((a, b) => b.v - a.v);
  if (!items.length || w <= 0 || h <= 0) return;

  const total = items.reduce((s, i) => s + i.v, 0);
  const scale = (w * h) / total;

  let rx = x, ry = y, rw = w, rh = h;
  while (items.length) {
    const { row, rowSum, consumed } = layoutArea(items, rx, ry, rw, rh, scale);
    const rowArea = rowSum * scale;
    if (rw >= rh) {
      const colW = rh > 0 ? rowArea / rh : 0;
      let cy = ry;
      for (const item of row) {
        const itemH = rowSum > 0 ? (item.v / rowSum) * rh : 0;
        out.push({ node: item.node, x: rx, y: cy, w: colW, h: itemH });
        cy += itemH;
      }
      rx += colW;
      rw -= colW;
    } else {
      const rowH = rw > 0 ? rowArea / rw : 0;
      let cx = rx;
      for (const item of row) {
        const itemW = rowSum > 0 ? (item.v / rowSum) * rw : 0;
        out.push({ node: item.node, x: cx, y: ry, w: itemW, h: rowH });
        cx += itemW;
      }
      ry += rowH;
      rh -= rowH;
    }
    items = items.slice(consumed);
  }
}

const HATCH_PATTERN_SVG =
  '<pattern id="hatch" width="6" height="6" patternTransform="rotate(45)" patternUnits="userSpaceOnUse">' +
  '<line x1="0" y1="0" x2="0" y2="6" stroke="#000" stroke-opacity="0.4" stroke-width="3"/>' +
  '</pattern>';

// Second line of a tile's label -- rung count for a routine, routine count
// for a Program group, [DataType] for an ordinary tag/member leaf (James,
// 2026-08-27: "all tags need [DataType] as a 2nd line", "routines need to
// have indication how many rungs", "programs need indication how many
// routines"). Returns [] when there's nothing extra to say.
function subLabelFor(node) {
  if (isGroup(node)) {
    if (node.name.startsWith("Program: ")) {
      const n = routineCountFor(node);
      if (n != null) return [`${n} routine${n === 1 ? "" : "s"}`];
    }
    return [];
  }
  if (node.data_type === "RLL") {
    const rc = rungCountFor(node);
    if (rc != null) return [`${rc} rung${rc === 1 ? "" : "s"}`];
    return [];
  }
  return [`[${node.data_type}]`];
}

async function renderTreemap() {
  const svg = document.getElementById("treemap-svg");
  if (!svg.clientWidth) return; // hidden tab, nothing to measure yet
  const children = CURRENT_NODE.children || [];

  // Depth-2 mode needs every visible node's own children loaded before we
  // can lay any of it out -- fetch them all up front (they're cheap local
  // Flask JSON round-trips) rather than trying to paint incrementally.
  if (DEPTH2_ENABLED) {
    await Promise.all(children.filter(isDrillable).map(ensureChildren));
  }

  paintTreemap(svg, children);
}

function paintTreemap(svg, children) {
  svg.innerHTML = "";
  const w = svg.clientWidth, h = svg.clientHeight;
  svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

  const svgNS = "http://www.w3.org/2000/svg";
  const defs = document.createElementNS(svgNS, "defs");
  defs.innerHTML = HATCH_PATTERN_SVG;
  svg.appendChild(defs);

  const rects = [];
  squarify(children, 0, 0, w, h, rects);

  for (const r of rects) {
    const node = r.node;
    const g = document.createElementNS(svgNS, "g");

    const rect = document.createElementNS(svgNS, "rect");
    rect.setAttribute("x", r.x);
    rect.setAttribute("y", r.y);
    rect.setAttribute("width", Math.max(r.w, 0));
    rect.setAttribute("height", Math.max(r.h, 0));
    rect.classList.add("tm-rect");
    rect.style.fill = isGroup(node) ? "var(--group-fill)" : colorForType(node.data_type);
    rect.addEventListener("click", () => drillInto(node));
    rect.addEventListener("mousemove", ev => showTooltip(ev, node));
    rect.addEventListener("mouseleave", hideTooltip);
    g.appendChild(rect);

    if (!isGroup(node) && node.basis && node.basis !== "KNOWN") {
      const hatch = document.createElementNS(svgNS, "rect");
      hatch.setAttribute("x", r.x);
      hatch.setAttribute("y", r.y);
      hatch.setAttribute("width", Math.max(r.w, 0));
      hatch.setAttribute("height", Math.max(r.h, 0));
      hatch.setAttribute("fill", "url(#hatch)");
      hatch.style.pointerEvents = "none";
      g.appendChild(hatch);
    }

    // "Estimated" flag (CLAUDE.md ground-truth constraint) -- a dashed
    // outline, deliberately a DIFFERENT visual channel from the basis
    // hatch fill above so the two confidence concepts (tier vs basis)
    // never blur together. Only leaf nodes carry a tier at all (group
    // nodes mix tiers, so they're left unmarked, same convention the
    // basis hatch above already uses).
    if (!isGroup(node) && node.tier === "estimated") {
      const outline = document.createElementNS(svgNS, "rect");
      outline.setAttribute("x", r.x + 1);
      outline.setAttribute("y", r.y + 1);
      outline.setAttribute("width", Math.max(r.w - 2, 0));
      outline.setAttribute("height", Math.max(r.h - 2, 0));
      outline.setAttribute("fill", "none");
      outline.setAttribute("stroke", "var(--tier-estimated)");
      outline.setAttribute("stroke-width", "2");
      outline.setAttribute("stroke-dasharray", "4,3");
      outline.style.pointerEvents = "none";
      g.appendChild(outline);
    }

    let labelLinesUsed = 0;
    if (r.w > 40 && r.h > 14) {
      const label = document.createElementNS(svgNS, "text");
      label.setAttribute("x", r.x + 4);
      label.setAttribute("y", r.y + 14);
      label.classList.add("tm-label");
      label.textContent = truncateLabel(node.name, r.w);
      g.appendChild(label);
      labelLinesUsed = 1;

      const subLines = subLabelFor(node);
      if (subLines.length && r.h > 28) {
        const label2 = document.createElementNS(svgNS, "text");
        label2.setAttribute("x", r.x + 4);
        label2.setAttribute("y", r.y + 27);
        label2.classList.add("tm-label", "tm-label-sub");
        label2.textContent = truncateLabel(subLines[0], r.w);
        g.appendChild(label2);
        labelLinesUsed = 2;
      }
    }

    // Depth-2 nesting (James, 2026-08-27): paint this tile's own children
    // inset inside it, visually distinct (dashed stroke, reduced opacity,
    // smaller label) so a grandchild is never mistaken for a same-level
    // sibling. Reserves the header strip the label above already used.
    if (DEPTH2_ENABLED && isDrillable(node) && node.children && node.children.length) {
      const inset = 3;
      const headerH = labelLinesUsed === 2 ? 28 : labelLinesUsed === 1 ? 14 : 0;
      const nx = r.x + inset, ny = r.y + inset + headerH;
      const nw = Math.max(r.w - 2 * inset, 0), nh = Math.max(r.h - 2 * inset - headerH, 0);
      const innerRects = [];
      squarify(node.children, nx, ny, nw, nh, innerRects);
      for (const ir of innerRects) {
        const cnode = ir.node;
        const crect = document.createElementNS(svgNS, "rect");
        crect.setAttribute("x", ir.x);
        crect.setAttribute("y", ir.y);
        crect.setAttribute("width", Math.max(ir.w, 0));
        crect.setAttribute("height", Math.max(ir.h, 0));
        crect.classList.add("tm-rect", "tm-rect-nested");
        crect.style.fill = isGroup(cnode) ? "var(--group-fill)" : colorForType(cnode.data_type);
        crect.addEventListener("click", () => drillInto(cnode));
        crect.addEventListener("mousemove", ev => showTooltip(ev, cnode));
        crect.addEventListener("mouseleave", hideTooltip);
        g.appendChild(crect);

        if (ir.w > 26 && ir.h > 12) {
          const clabel = document.createElementNS(svgNS, "text");
          clabel.setAttribute("x", ir.x + 3);
          clabel.setAttribute("y", ir.y + 10);
          clabel.classList.add("tm-label", "tm-label-nested");
          clabel.textContent = truncateLabel(cnode.name, ir.w);
          g.appendChild(clabel);
        }
      }
    }

    svg.appendChild(g);
  }
}

function truncateLabel(name, widthPx) {
  const maxChars = Math.max(3, Math.floor(widthPx / 6.5));
  return name.length > maxChars ? name.slice(0, maxChars - 1) + "…" : name;
}

// Color is reserved for data type (James, 2026-08-20) -- confidence is
// shown via the hatch overlay instead, never by recoloring.
const TYPE_COLORS = {
  SINT: "#5b8dd6", INT: "#4f7fc4", DINT: "#3d6bb0", LINT: "#2c5590",
  REAL: "#3ba17a", BOOL: "#c98a2c", BIT: "#c98a2c", STRING: "#8a5fbf",
  ALIAS: "#5c6472", TIMER: "#d1607a", COUNTER: "#c14f6b", CONTROL: "#a83f5a",
};

function colorForType(dataType) {
  if (TYPE_COLORS[dataType]) return TYPE_COLORS[dataType];
  let hash = 0;
  for (let i = 0; i < dataType.length; i++) hash = (hash * 31 + dataType.charCodeAt(i)) >>> 0;
  const hue = hash % 360;
  return `hsl(${hue}, 50%, 42%)`;
}

// JSR call-tree note (Phase 5, 2026-08-27): a routine's own byte total
// already correctly folds in its JSR targets' cost (no double-counting --
// see parser/logic.py's is_jsr_target/jsr_target_names docstrings), but a
// called subroutine never appears as its own treemap/list node at all, so
// without this note there's no way to see WHY. REPORT.jsr_calls is keyed
// by the exact same routine.path every routine leaf's node.path already
// carries, so this is a direct lookup, not a search.
function jsrCallsNote(node) {
  const targets = REPORT && REPORT.jsr_calls && REPORT.jsr_calls[node.path];
  if (!targets || !targets.length) return "";
  return `<br><span class="text-dim-on-dark">Calls via JSR: ${targets.join(", ")} ` +
    `(cost already included above)</span>`;
}

// % of the CURRENT treemap root's total this node represents -- a half-
// full bar means this element is half of its parent's usage (James,
// 2026-08-27). Uses CURRENT_NODE (the treemap's current drill root), not
// the node's structural parent, since that's what the visible tiles are
// actually being sized relative to.
function tooltipParentBar(node) {
  const parentTotal = nodeValue(CURRENT_NODE);
  const val = isGroup(node) ? nodeValue(node) : node.value;
  const pct = parentTotal ? (val / parentTotal) * 100 : 0;
  const parentName = CURRENT_NODE.name === "root" ? "All" : CURRENT_NODE.name;
  return (
    `<div class="tooltip-bar-wrap"><div class="tooltip-bar" style="width:${Math.min(pct, 100).toFixed(1)}%"></div></div>` +
    `<div class="tooltip-bar-label">${pct.toFixed(1)}% of ${parentName}</div>`
  );
}

function showTooltip(ev, node) {
  const tooltip = document.getElementById("tooltip");
  tooltip.classList.remove("hidden");
  const wrap = document.getElementById("treemap-main").getBoundingClientRect();
  tooltip.style.left = (ev.clientX - wrap.left + 12) + "px";
  tooltip.style.top = (ev.clientY - wrap.top + 12) + "px";

  if (isGroup(node)) {
    const routines = routineCountFor(node);
    tooltip.innerHTML = `<strong>${node.name}</strong><br>${fmtBytes(nodeValue(node))}` +
      (routines != null ? `<br>${routines} routine${routines === 1 ? "" : "s"}` : "") +
      tooltipParentBar(node) +
      (isDrillable(node) ? " (click to drill in)" : "");
  } else {
    const rc = node.data_type === "RLL" ? rungCountFor(node) : null;
    tooltip.innerHTML =
      `<strong>${node.name}</strong><br>` +
      `${node.data_type}<br>` +
      (rc != null ? `${rc} rung${rc === 1 ? "" : "s"}<br>` : "") +
      `${fmtBytes(node.value)}<br>` +
      (node.tier === "estimated" ? `<span class="tier-chip">ESTIMATED</span>` : "") +
      `<span class="basis-chip basis-${node.basis}">${node.basis}</span>` +
      jsrCallsNote(node) +
      tooltipParentBar(node) +
      (isDrillable(node) ? " (click to drill in)" : "");
  }
}

function hideTooltip() {
  document.getElementById("tooltip").classList.add("hidden");
}

// ---- list view ----
// Scoped to CURRENT_NODE's direct children (James, 2026-08-20: "if im down
// branches then those should represent the current level") -- not the
// whole file. Re-rendered on every navigation via renderCurrentLevel so it
// stays in sync even when this tab isn't the active one. Rendered into
// BOTH the full-page list table and its docked twin (see setupSplitDock)
// every time -- cheap, and keeps them from ever going stale relative to
// each other.

function currentLevelRows() {
  const kids = CURRENT_NODE.children || [];
  const total = kids.reduce((s, c) => s + nodeValue(c), 0);
  return kids.map(c => {
    const bytes = nodeValue(c);
    return {
      node: c,
      name: c.name,
      data_type: c.data_type || "(group)",
      bytes,
      pct_of_total: total ? (bytes / total) * 100 : 0,
      basis: c.basis || "",
      tier: c.tier || "",
      jsr_targets: (REPORT && REPORT.jsr_calls && REPORT.jsr_calls[c.path]) || null,
      rung_count: c.data_type === "RLL" ? rungCountFor(c) : null,
      routine_count: routineCountFor(c),
    };
  });
}

const LIST_TABLE_IDS = ["list-table", "list-table-dock"];

function renderList() {
  for (const id of LIST_TABLE_IDS) renderListInto(id);
}

// James 2026-08-27: rows are now click-to-drill (same target a treemap
// tile click would drill into), matching "List should be browsable to see
// inside each element name or type."
function renderListInto(tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;
  const tbody = table.querySelector("tbody");
  const rows = currentLevelRows().sort((a, b) => {
    const { key, dir } = SORT_STATE;
    if (typeof a[key] === "string") return a[key].localeCompare(b[key]) * dir;
    return (a[key] - b[key]) * dir;
  });

  tbody.innerHTML = "";
  for (const e of rows) {
    const tr = document.createElement("tr");
    const drillable = isDrillable(e.node);
    tr.classList.toggle("row-drillable", drillable);
    if (drillable) tr.addEventListener("click", () => drillInto(e.node));

    const subNote = e.jsr_targets
      ? `<br><span class="text-dim">Calls via JSR: ${e.jsr_targets.join(", ")}</span>`
      : e.rung_count != null
      ? `<br><span class="text-dim">${e.rung_count} rung${e.rung_count === 1 ? "" : "s"}</span>`
      : e.routine_count != null
      ? `<br><span class="text-dim">${e.routine_count} routine${e.routine_count === 1 ? "" : "s"}</span>`
      : "";
    tr.innerHTML =
      `<td>${e.name}${subNote}</td>` +
      `<td>${e.data_type}</td>` +
      `<td class="num">${Math.round(e.bytes).toLocaleString()}</td>` +
      `<td class="num">${e.pct_of_total.toFixed(2)}%</td>` +
      `<td>${e.tier === "estimated" ? `<span class="tier-chip">ESTIMATED</span>` : ""}` +
      `${e.basis ? `<span class="basis-chip basis-${e.basis}">${e.basis}</span>` : ""}</td>`;
    tbody.appendChild(tr);
  }

  table.querySelectorAll("th").forEach(th => {
    th.onclick = () => {
      const key = th.dataset.sort;
      SORT_STATE.dir = SORT_STATE.key === key ? -SORT_STATE.dir : -1;
      SORT_STATE.key = key;
      renderList();
    };
  });
}

// ---- type summary ----
// Also scoped to CURRENT_NODE's direct children, same reasoning as the
// list. Rendered into both the full-page pane and its docked twin.

const TYPE_SUMMARY_IDS = ["type-summary", "type-summary-dock"];

function renderTypeSummary() {
  for (const id of TYPE_SUMMARY_IDS) renderTypeSummaryInto(id);
}

function renderTypeSummaryInto(elId) {
  const el = document.getElementById(elId);
  if (!el) return;
  el.innerHTML = "";

  const kids = CURRENT_NODE.children || [];
  const totals = {};
  for (const c of kids) {
    const key = c.data_type || "(group)";
    totals[key] = (totals[key] || 0) + nodeValue(c);
  }
  const grandTotal = Object.values(totals).reduce((s, v) => s + v, 0);
  const rows = Object.entries(totals)
    .map(([data_type, bytes]) => ({ data_type, bytes, pct_of_total: grandTotal ? (bytes / grandTotal) * 100 : 0 }))
    .sort((a, b) => b.bytes - a.bytes);

  const maxPct = Math.max(...rows.map(t => t.pct_of_total), 1);
  for (const t of rows) {
    const row = document.createElement("div");
    row.className = "type-row";
    // type-name is a bounded, ellipsis-truncated flex item now (James,
    // 2026-08-27: "Type summary needs to be more dynamic for
    // REALLY_VERY_LONG_TAGS_AND_UDT_NAMES") -- the full name is always
    // available via the title attribute on hover.
    row.innerHTML =
      `<div class="type-swatch" style="background:${colorForType(t.data_type)}"></div>` +
      `<div class="type-name" title="${t.data_type}">${t.data_type}</div>` +
      `<div class="type-bar-wrap"><div class="type-bar" style="width:${(t.pct_of_total / maxPct) * 100}%"></div></div>` +
      `<div class="type-bytes">${fmtBytes(t.bytes)} (${t.pct_of_total.toFixed(2)}%)</div>`;
    el.appendChild(row);
  }
}

main();
