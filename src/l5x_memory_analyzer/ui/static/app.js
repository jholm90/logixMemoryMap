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

async function main() {
  setupTabs();
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
    return;
  }

  const infoParts = [`Schema ${REPORT.schema_revision}`];
  if (REPORT.software_revision) infoParts.push(`Software ${REPORT.software_revision}`);
  if (REPORT.processor_type) infoParts.push(REPORT.processor_type);
  document.getElementById("file-info").textContent =
    `${REPORT.file_name}  (${infoParts.join(", ")})`;

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

  const pct = REPORT.budget_bytes ? (REPORT.total_bytes / REPORT.budget_bytes) * 100 : 0;
  const fill = document.getElementById("budget-bar-fill");
  fill.style.width = `${Math.min(pct, 100)}%`;
  fill.classList.toggle("over", pct > 100);
  document.getElementById("budget-label").textContent =
    `${fmtBytes(REPORT.total_bytes)} / ${fmtBytes(REPORT.budget_bytes)} (${pct.toFixed(2)}%)`;

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

  renderBreadcrumb();
  renderTreemap();
  renderList();
  renderTypeSummary();
}

// The initial /api/report hierarchy is always exactly 3 levels: root ->
// scope group ("Controller Tags" / "Program: X") -> tag leaf. Only the tag
// leaves need a _tagPath/_subPath for lazy /api/node fetches -- anything
// deeper than that is fetched on demand (see ensureChildren), which sets
// _tagPath/_subPath directly on the freshly created child nodes itself.
function annotateTagPaths(root) {
  for (const group of root.children || []) {
    for (const tagLeaf of group.children || []) {
      tagLeaf._tagPath = tagLeaf.path;
      tagLeaf._subPath = "";
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

// ---- tabs ----

function setupTabs() {
  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`panel-${btn.dataset.tab}`).classList.add("active");
      if (btn.dataset.tab === "treemap") renderTreemap();
    });
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
      renderBreadcrumb();
      renderTreemap();
    });
    el.appendChild(crumb);
  });
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
  renderBreadcrumb();
  renderTreemap();
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

function renderTreemap() {
  const svg = document.getElementById("treemap-svg");
  if (!svg.clientWidth) return; // hidden tab, nothing to measure yet
  svg.innerHTML = "";
  const w = svg.clientWidth, h = svg.clientHeight;
  svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

  const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
  defs.innerHTML = HATCH_PATTERN_SVG;
  svg.appendChild(defs);

  const children = CURRENT_NODE.children || [];
  const rects = [];
  squarify(children, 0, 0, w, h, rects);

  for (const r of rects) {
    const node = r.node;
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");

    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
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
      const hatch = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      hatch.setAttribute("x", r.x);
      hatch.setAttribute("y", r.y);
      hatch.setAttribute("width", Math.max(r.w, 0));
      hatch.setAttribute("height", Math.max(r.h, 0));
      hatch.setAttribute("fill", "url(#hatch)");
      hatch.style.pointerEvents = "none";
      g.appendChild(hatch);
    }

    if (r.w > 40 && r.h > 14) {
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", r.x + 4);
      label.setAttribute("y", r.y + 14);
      label.classList.add("tm-label");
      label.textContent = truncateLabel(node.name, r.w);
      g.appendChild(label);
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

function showTooltip(ev, node) {
  const tooltip = document.getElementById("tooltip");
  tooltip.classList.remove("hidden");
  const wrap = document.getElementById("panel-treemap").getBoundingClientRect();
  tooltip.style.left = (ev.clientX - wrap.left + 12) + "px";
  tooltip.style.top = (ev.clientY - wrap.top + 12) + "px";

  if (isGroup(node)) {
    tooltip.innerHTML = `<strong>${node.name}</strong><br>${fmtBytes(nodeValue(node))}` +
      (isDrillable(node) ? " (click to drill in)" : "");
  } else {
    tooltip.innerHTML =
      `<strong>${node.name}</strong><br>` +
      `${node.data_type}<br>` +
      `${fmtBytes(node.value)}<br>` +
      `<span class="basis-chip basis-${node.basis}">${node.basis}</span>` +
      (isDrillable(node) ? " (click to drill in)" : "");
  }
}

function hideTooltip() {
  document.getElementById("tooltip").classList.add("hidden");
}

// ---- list view ----
// Note: the list/type-summary tabs still reflect only the top-level tag
// entries from /api/report, not the full lazily-drilled tree -- deep
// member-level rows would need every array/UDT expanded eagerly, which is
// exactly what the lazy /api/node design avoids. Treemap is the place for
// infinite-depth browsing; list/type-summary stay a top-level rollup.

function renderList() {
  const tbody = document.querySelector("#list-table tbody");
  const rows = [...REPORT.entries].sort((a, b) => {
    const { key, dir } = SORT_STATE;
    if (typeof a[key] === "string") return a[key].localeCompare(b[key]) * dir;
    return (a[key] - b[key]) * dir;
  });

  tbody.innerHTML = "";
  for (const e of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML =
      `<td>${e.path}</td>` +
      `<td>${e.data_type}</td>` +
      `<td>${e.category}</td>` +
      `<td class="num">${e.bytes.toLocaleString()}</td>` +
      `<td class="num">${e.pct_of_total.toFixed(2)}%</td>` +
      `<td><span class="basis-chip basis-${e.basis}">${e.basis}</span></td>`;
    tbody.appendChild(tr);
  }

  document.querySelectorAll("#list-table th").forEach(th => {
    th.onclick = () => {
      const key = th.dataset.sort;
      SORT_STATE.dir = SORT_STATE.key === key ? -SORT_STATE.dir : -1;
      SORT_STATE.key = key;
      renderList();
    };
  });
}

// ---- type summary ----

function renderTypeSummary() {
  const el = document.getElementById("type-summary");
  el.innerHTML = "";
  const maxPct = Math.max(...REPORT.type_summary.map(t => t.pct_of_total), 1);
  for (const t of REPORT.type_summary) {
    const row = document.createElement("div");
    row.className = "type-row";
    row.innerHTML =
      `<div class="type-swatch" style="background:${colorForType(t.data_type)}"></div>` +
      `<div class="type-name">${t.data_type}</div>` +
      `<div class="type-bar-wrap"><div class="type-bar" style="width:${(t.pct_of_total / maxPct) * 100}%"></div></div>` +
      `<div class="type-bytes">${fmtBytes(t.bytes)} (${t.pct_of_total.toFixed(2)}%)</div>`;
    el.appendChild(row);
  }
}

main();
