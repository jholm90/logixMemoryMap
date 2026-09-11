// Vanilla JS/SVG squarified treemap -- no external deps by design, since this
// runs on engineering workstations that are frequently airgapped OT networks.
//
// Infinite-depth lazy drill-down (2026-08-20): a node's .children is
// only populated when the user actually drills into it, via /api/node --
// never masks a large array or deep UDT nesting just because materializing
// the whole tree up front would be enormous. Color is reserved for data
// type; confidence is shown as solid (KNOWN) vs. diagonal-hatch overlay
// (anything else) instead.

let REPORT = null;
let CURRENT_NODE = null; // node currently shown as the treemap root
let NODE_STACK = [];     // ancestors of CURRENT_NODE, for the breadcrumb
let SORT_STATE = { key: "bytes", dir: -1 };
let SPLIT_OPEN = false;  // 2026-08-27: List/Type Summary docked
                         // alongside the treemap, always-available toggle
let NEST_DEPTH = 2;      // how many levels to nest inside each tile (1..10).
                         // Replaced the old two-state "2 levels deep"
                         // checkbox: depth is a range, not a boolean.
                         // Defaults to 2: one level shows only what you
                         // already picked, and the point of a treemap is
                         // seeing what is inside without clicking first.
let DEF_MODE = "definition";  // or "instance" -- see renderNodeActions
let NAV_HISTORY = [];    // every location visited, for the Back button --
                         // distinct from NODE_STACK, which is only the
                         // ANCESTOR chain. Going "back" after a sideways
                         // sibling jump or a breadcrumb click cannot be
                         // recovered from ancestors alone.

async function main() {
  setupTabs();
  setupSplitDock();
  setupDepthStepper();
  setupBackButton();
  setupErrorsBanner();
  setupColumnResize();
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
    // Show the exact block counts as well as the rounded MB. "1.00 MB /
    // 2.00 MB" hides the number the controller actually reports on its
    // Capacity tab, which is what a user cross-checks against.
    label.textContent =
      `${fmtBytes(REPORT.total_bytes)} / ${fmtBytes(REPORT.budget_bytes)} (${pct.toFixed(2)}%)${archNote}` +
      `  ·  ${fmtBlocks(REPORT.total_bytes)} / ${fmtBlocks(REPORT.budget_bytes)} blocks`;
  } else {
    // (2026-08-20): capacity is part-number specific, don't fake a
    // number for a processor type we don't have real data for.
    fill.style.width = "0%";
    fill.classList.remove("over");
    label.textContent =
      `${fmtBytes(REPORT.total_bytes)} (${fmtBlocks(REPORT.total_bytes)} blocks) used ` +
      `-- budget unknown for processor "${REPORT.processor_type || "?"}"`;
  }

  renderErrors();

  CURRENT_NODE = REPORT.hierarchy;
  annotateTagPaths(CURRENT_NODE);
  NODE_STACK = [];
  NAV_HISTORY = [];
  // A newly loaded file starts at the root, on the treemap, in the default
  // definition reading -- carrying the previous file's tab or type-view
  // over showed the new file through the old file's lens.
  DEF_MODE = "definition";
  const treemapBtn = document.querySelector('.tab-btn[data-tab="treemap"]');
  if (treemapBtn && !treemapBtn.classList.contains("active")) treemapBtn.click();

  renderCurrentLevel();
}

// Re-renders everything that depends on CURRENT_NODE -- called after any
// navigation (drill in, breadcrumb click, sibling jump) so the List and
// Type Summary tabs (and their docked twins, see setupSplitDock) stay in
// sync with wherever the treemap is, even when they're not the active tab.
function renderCurrentLevel(recordHistory = true) {
  if (recordHistory === false) { /* Back already restored the location */ }
  document.getElementById("back-btn").disabled = NAV_HISTORY.length === 0;
  // Any move to a different level clears the list filter. Carrying it
  // across would hide rows at the new location with no visible cause.
  clearListFilters();
  // The cross-reference is per-type, so it belongs to the node you were
  // on, not the one you just moved to.
  resetXref();
  renderBreadcrumb();
  renderNodeActions();
  renderTreemap();
  renderList();
  renderTypeSummary();
  syncXrefTab();
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
  // Walks the WHOLE initial tree, not a fixed two levels. The hierarchy is
  // not always 3 deep: _nest_programs_under_tasks inserts a "Task: Y" level
  // above "Program: X", and a program with routines gets a "Routines"
  // subgroup under that -- so a real tag leaf can sit 4 or 5 levels down.
  // The old fixed root->group->leaf walk left every one of those without a
  // _tagPath, so drilling one requested /api/node?tag=&path= (both empty)
  // and got a 404. That is why array drill-down worked on a file with no
  // task nesting and failed on one with it.
  //
  // Any node that has no children of its own is a lazy-expansion candidate
  // and needs its own path, whatever depth it sits at.
  const visit = node => {
    if (!node.children) {
      node._tagPath = node.path;
      node._subPath = "";
      return;
    }
    for (const child of node.children) visit(child);
  };
  for (const group of root.children || []) visit(group);
}

// Errors get their own tab, a count in the tab label, and a compact fixed
// banner. The old footer was a single long line of concatenated messages
// that scrolled away with the page and was unreadable past the second item.
function renderErrors() {
  const errors = (REPORT && REPORT.errors) || [];
  const banner = document.getElementById("errors-banner");
  const tabBtn = document.getElementById("errors-tab-btn");
  const detail = document.getElementById("errors-detail");

  tabBtn.textContent = `${errors.length} Error${errors.length === 1 ? "" : "s"}`;
  tabBtn.classList.toggle("has-errors", errors.length > 0);

  if (!errors.length) {
    banner.classList.add("hidden");
    detail.innerHTML = `<p class="errors-empty">Nothing went unpriced in this file.</p>`;
    return;
  }

  // Banner stays short on purpose -- a count and an invitation, not detail.
  banner.classList.remove("hidden");
  banner.textContent =
    `${errors.length} item${errors.length === 1 ? "" : "s"} could not be priced — click for detail`;

  // Grouped by the leading path segment, so 40 variations of one underlying
  // gap read as one heading rather than 40 unrelated lines.
  const groups = {};
  for (const e of errors) {
    const key = (e.path || "").split("/")[0] || "other";
    (groups[key] = groups[key] || []).push(e);
  }
  detail.innerHTML = Object.entries(groups)
    .sort((a, b) => b[1].length - a[1].length)
    .map(([key, items]) =>
      `<section class="error-group">` +
      `<h3>${key} <span class="error-count">${items.length}</span></h3>` +
      `<table class="error-table"><tbody>` +
      items.map(e =>
        `<tr><td class="error-path">${e.path}</td><td class="error-msg">${e.message}</td></tr>`
      ).join("") +
      `</tbody></table></section>`
    ).join("");
}

function fmtBlocks(n) {
  return n == null ? "-" : Math.round(n).toLocaleString();
}

// ---- confidence as a measured PERCENTAGE (#confidence bar) ----
//
// A single KNOWN/FITTED/ASSUMED badge is misleading on any aggregate,
// because weakest()-style propagation lets one small unmeasured term label
// a node that is overwhelmingly measured. A real case: a String_L010[100]
// array is 1,600 bytes of KNOWN element cost plus a 12-byte FITTED
// one-time array_base -- 99.3% measured, yet it reads simply "FITTED".
//
// So confidence is reported the way the bytes actually divide: what share
// of this subtree's bytes rests on each basis. Leaves still show their own
// single basis, which is exactly what a leaf's percentage degenerates to.
// Byte-weighted confidence over a subtree.
//
// Two things this deliberately does NOT do, both of which it used to.
//
// It does not report 0% for a node that occupies no bytes. A BIT alias
// member is zero bytes because its storage belongs to the hidden backing
// SINT it points at -- there is nothing uncertain about it, and printing
// "0% measured" against it read as a hole in the model when the real
// answer is that the question does not apply. knownPct is null in that
// case and callers render it as such.
//
// It does not let the answer depend on what happens to be loaded. Drill
// children arrive lazily, so walking `n.children` gave a node one answer
// before you expanded it and a different one after -- the reported
// "0% fitted that becomes 100% fitted once you visit it and come back".
// A node that still has unexpanded children now uses the subtree summary
// the server sent with it, which is computed over the whole subtree and
// is the same answer either way.
function confidenceBreakdown(node) {
  const acc = { KNOWN: 0, FITTED: 0, ASSUMED: 0, UNKNOWN: 0 };
  const add = (key, bytes) => {
    const k = (key || "UNKNOWN").toUpperCase();
    acc[k in acc ? k : "UNKNOWN"] += bytes;
  };
  const visit = n => {
    const kids = n.children;
    if (kids && kids.length) {
      for (const k of kids) visit(k);
      return;
    }
    // Unexpanded but drillable: trust the server's subtree summary rather
    // than the node's own single rolled-up basis, which is only the
    // weakest tier present and says nothing about the mix.
    if (n.confidence && n.confidence.total) {
      for (const k of ["KNOWN", "FITTED", "ASSUMED", "UNKNOWN"]) {
        add(k, n.confidence[k] || 0);
      }
      return;
    }
    add(n.basis, nodeValue(n));
  };
  visit(node);
  const total = acc.KNOWN + acc.FITTED + acc.ASSUMED + acc.UNKNOWN;
  return { ...acc, total, knownPct: total ? (acc.KNOWN / total) * 100 : null };
}

// A tag of a UDT/AOI type gets a link to the definition that declares it.
// Knowing an instance costs 12KB is rarely the end of the question -- the
// next one is always "what is in it", and that lives on the definition.
function definitionLinkHtml(node) {
  if (!node || !node.data_type) return "";
  const names = (REPORT && REPORT.type_names) || [];
  if (!names.includes(node.data_type)) return "";
  const path = (node.path || node._tagPath || "");
  if (path.startsWith("udt_definitions/") || path.startsWith("aoi_definitions/")) return "";
  const isAoi = (REPORT.aoi_names || []).includes(node.data_type);
  return `<span class="def-link" data-def-type="${escapeHtml(node.data_type)}">` +
    `${isAoi ? "AOI DEFINITION" : "UDT DEFINITION"}: ${escapeHtml(node.data_type)}</span>`;
}

function wireDefinitionLinks(scope) {
  (scope || document).querySelectorAll("[data-def-type]").forEach(el => {
    el.onclick = ev => {
      ev.stopPropagation();
      navigateToDefinition(el.dataset.defType);
    };
  });
}

function navigateToDefinition(typeName) {
  const wanted = [`udt_definitions/${typeName}`, `aoi_definitions/${typeName}`];
  const chain = findChain(REPORT && REPORT.hierarchy,
    n => wanted.includes(n.path || n._tagPath));
  if (chain) navigateToChain(chain);
}

function confidenceBarHtml(node) {
  const c = confidenceBreakdown(node);
  // Zero bytes is not low confidence. Say why it is zero instead.
  if (!c.total) {
    return node.alias_of
      ? `<div class="conf-label">no storage of its own &mdash; alias of ` +
        `${escapeHtml(node.alias_of)}` +
        (node.alias_bit != null ? `, bit ${node.alias_bit}` : "") + `</div>`
      : `<div class="conf-label">no storage &mdash; nothing to measure</div>`;
  }
  const seg = (v, cls) => v > 0
    ? `<span class="conf-seg ${cls}" style="width:${(v / c.total) * 100}%"></span>` : "";
  return `<div class="conf-bar">${seg(c.KNOWN, "conf-known")}${seg(c.FITTED, "conf-fitted")}` +
    `${seg(c.ASSUMED, "conf-assumed")}${seg(c.UNKNOWN, "conf-unknown")}</div>` +
    `<div class="conf-label">${c.knownPct.toFixed(1)}% measured` +
    (c.FITTED ? ` · ${((c.FITTED / c.total) * 100).toFixed(1)}% fitted` : "") +
    (c.ASSUMED ? ` · ${((c.ASSUMED / c.total) * 100).toFixed(1)}% assumed` : "") +
    `</div>`;
}

// A group node has no data_type, but "(group)" tells the user nothing.
// Name the kind of container it actually is.
function groupKind(node) {
  const n = node.name || "";
  if (n === "root") return "Controller";
  if (n.startsWith("Task: ")) return "Task";
  if (n.startsWith("Program: ")) return "Program";
  if (n === "Routines") return "Routine folder";
  if (n === "Program Tags") return "Tag folder";
  if (n === "Controller Tags") return "Tag scope";
  if (n === "Type Definitions") return "User-Defined Data Types";
  if (n === "Modules") return "I/O modules";
  if (n === "Axis Definitions") return "Axis pool";
  if (n === "Add-On Instructions") return "Add-On Instruction";
  if (n === "User-Defined Data Types") return "User-Defined Data Type";
  if (n === "Project Overhead") return "Project overhead";
  if (n === "Alarm Conditions") return "Alarm scope";
  return "Folder";
}

// Task schedule type for the treeview description line.
function taskInfoFor(node) {
  if (!REPORT || !REPORT.task_info || !node.name.startsWith("Task: ")) return null;
  return REPORT.task_info[node.name.slice("Task: ".length)] || null;
}

function programTagCountFor(node) {
  if (!REPORT || !REPORT.program_tag_counts || !node.name.startsWith("Program: ")) return null;
  // The group name carries a trailing "(unscheduled)" marker on programs no
  // task schedules; the count is keyed by the bare program name.
  const bare = node.name.slice("Program: ".length).replace(/\s*\(unscheduled\)$/, "");
  const n = REPORT.program_tag_counts[bare];
  return n == null ? null : n;
}

// An array tag should say so in its own label -- "Motors" and "Motors[64]"
// are very different things to find in a memory map.
// Tag, type and member names come out of the L5X, so they are file
// content rather than anything this app controls, and several of these
// labels are built with innerHTML. Escape before interpolating.
function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

function displayName(node) {
  const dims = node.dimensions || node.dims;
  if (Array.isArray(dims) && dims.length) return `${node.name}[${dims.join(",")}]`;
  if (typeof node.array_length === "number") return `${node.name}[${node.array_length}]`;
  return node.name;
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
  // A ladder routine is always drillable -- into its rungs -- even though the
  // backend hierarchy marks it as a leaf.
  if (node.data_type === "RLL" && node.path) {
    const rc = rungCountFor(node);
    return rc == null ? true : rc > 0;
  }
  return !!(node.children || node.has_children);
}

function isGroup(node) {
  // Structural group (root / scope groups) vs. a typed tag/member node.
  return node.data_type == null;
}

// Real rung count for a routine_logic leaf, keyed by the exact same
// routine.path every such leaf's own node.path already carries
// (2026-08-27: a routine needs to show how many rungs it holds).
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

// Depth and the Details split only mean anything to the treemap -- depth
// controls how many levels nest inside a tile, and the split docks a pane
// beside the SVG. On the List, Type Summary and Errors tabs they are dead
// controls that still invite a click, so they are hidden rather than left
// sitting there doing nothing.
function syncTreemapOnlyControls(tab) {
  const onTreemap = tab === "treemap";
  for (const el of [document.querySelector(".depth-stepper"),
                    document.getElementById("split-toggle")]) {
    if (el) el.hidden = !onTreemap;
  }
}

function setupTabs() {
  document.querySelectorAll(".tab-btn[data-tab]").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn[data-tab]").forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".panel").forEach(p => p.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById(`panel-${btn.dataset.tab}`).classList.add("active");
      syncTreemapOnlyControls(btn.dataset.tab);
      if (btn.dataset.tab === "treemap") renderTreemap();
      if (btn.dataset.tab === "xref") renderXref();
    });
  });
  syncTreemapOnlyControls("treemap");
}

// 2026-08-27: "Type/list should be always visible but hidden. if
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

// 2026-08-27: "the treeview shows a nice map on stuff that level, i
// think we need the option/checkbox to see two levels deep with there
// being some obvious difference between parent/children." See
// renderTreemap's nested-squarify block for the paint side; nested tiles
// get a dashed stroke + reduced opacity + smaller label so they're never
// mistaken for a same-level sibling.
// Depth is a range (1..10), not a two-state checkbox. 1 means "just this
// level", matching the old unchecked behaviour, so the default is unchanged.
function setupDepthStepper() {
  const input = document.getElementById("depth-input");
  input.value = NEST_DEPTH;
  const apply = v => {
    NEST_DEPTH = Math.max(1, Math.min(10, Number(v) || 1));
    input.value = NEST_DEPTH;
    renderTreemap();
  };
  input.addEventListener("change", () => apply(input.value));
  document.getElementById("depth-minus").addEventListener("click", () => apply(NEST_DEPTH - 1));
  document.getElementById("depth-plus").addEventListener("click", () => apply(NEST_DEPTH + 1));
}

// Back walks the actual visit history, so it also undoes a sibling jump or a
// breadcrumb click -- neither of which the ancestor stack can reverse.
function setupBackButton() {
  document.getElementById("back-btn").addEventListener("click", () => {
    const prev = NAV_HISTORY.pop();
    if (!prev) return;
    CURRENT_NODE = prev.node;
    NODE_STACK = prev.stack;
    renderCurrentLevel(false);
  });
}

function pushHistory() {
  NAV_HISTORY.push({ node: CURRENT_NODE, stack: [...NODE_STACK] });
  if (NAV_HISTORY.length > 100) NAV_HISTORY.shift();
}

function setupErrorsBanner() {
  document.getElementById("errors-banner").addEventListener("click", () => {
    const btn = document.querySelector('.tab-btn[data-tab="errors"]');
    if (btn) btn.click();
  });
}

// Drag a header edge to resize that column. Widths persist for the session
// so re-rendering the rows does not snap them back.
const COLUMN_WIDTHS = {};

function setupColumnResize() {
  for (const table of document.querySelectorAll("#list-table, #list-table-dock")) {
    table.querySelectorAll("th").forEach(th => {
      const grip = document.createElement("span");
      grip.className = "col-grip";
      grip.addEventListener("click", ev => ev.stopPropagation()); // not a sort
      grip.addEventListener("mousedown", ev => {
        ev.preventDefault();
        ev.stopPropagation();
        const startX = ev.clientX;
        const startW = th.offsetWidth;
        const onMove = e => {
          const w = Math.max(40, startW + (e.clientX - startX));
          COLUMN_WIDTHS[th.dataset.sort] = w;
          applyColumnWidths();
        };
        const onUp = () => {
          document.removeEventListener("mousemove", onMove);
          document.removeEventListener("mouseup", onUp);
        };
        document.addEventListener("mousemove", onMove);
        document.addEventListener("mouseup", onUp);
      });
      th.appendChild(grip);
    });
  }
}

function applyColumnWidths() {
  for (const table of document.querySelectorAll("#list-table, #list-table-dock")) {
    table.querySelectorAll("th").forEach(th => {
      const w = COLUMN_WIDTHS[th.dataset.sort];
      if (w) th.style.width = w + "px";
    });
  }
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
      const info = document.getElementById("file-info");
      info.textContent = `Loading ${file.name}...`;
      showProgress(`Loading ${file.name}`, "Uploading...");
      try {
        // XHR rather than fetch purely for upload progress: a real export is
        // tens of megabytes and fetch cannot report how much of it has gone.
        // Once the body is up there is no percentage to report -- the server
        // is parsing and sizing -- so the bar switches to indeterminate
        // instead of sitting frozen at 100%.
        const { status, statusText, raw } = await uploadWithProgress(formData);
        let data = null;
        // Never assume the body is JSON. A crash inside the sizing engine
        // comes back as an HTML traceback page, and parsing that as JSON
        // threw before the error could ever be shown -- leaving "Loading ..."
        // on screen with nothing else.
        try { data = JSON.parse(raw); } catch (_) { /* not JSON -- handled below */ }
        if (status < 200 || status >= 300 || data === null) {
          const detail = (data && data.error) || raw.slice(0, 300) || statusText;
          info.textContent = `Failed to load ${file.name}`;
          alert(`Failed to load ${file.name}:\n\n${detail}`);
          return;
        }
        REPORT = data;
        renderAll();
      } catch (err) {
        // Network-level failure, or the server died outright.
        info.textContent = `Failed to load ${file.name}`;
        alert(`Failed to load ${file.name}:\n\n${err}`);
      } finally {
        hideProgress();
        ev.target.value = "";
      }
    });
  }
}

function uploadWithProgress(formData) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/load");
    xhr.upload.onprogress = ev => {
      if (!ev.lengthComputable) return setProgressIndeterminate("Uploading...");
      setProgress(ev.loaded / ev.total,
        `Uploading ${fmtBytes(ev.loaded)} of ${fmtBytes(ev.total)}`);
    };
    xhr.upload.onload = () =>
      setProgressIndeterminate("Parsing and sizing on the server...");
    xhr.onload = () => resolve({
      status: xhr.status, statusText: xhr.statusText, raw: xhr.responseText || "",
    });
    xhr.onerror = () => reject(new Error("network error"));
    xhr.send(formData);
  });
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
      if (node === CURRENT_NODE) return;
      pushHistory();
      NODE_STACK = chain.slice(0, i);
      CURRENT_NODE = node;
      renderCurrentLevel();
    });

    // Sibling browser: hover a crumb to jump sideways without backing all
    // the way up and re-drilling down (2026-08-20). The parent's
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
  pushHistory();
  NODE_STACK = parentStack;
  CURRENT_NODE = sibling;
  renderCurrentLevel();
}

async function ensureChildren(node) {
  if (node.children) return node.children;

  // A ladder routine drills into its own RUNGS. Routines were previously the
  // hard floor of the tree; a routine with 400 rungs was a single opaque
  // tile. Rungs come from their own endpoint (see /api/rungs) because a
  // large program has tens of thousands of them and shipping every rung's
  // text in the main report payload would dwarf the rest of the JSON.
  if (node.data_type === "RLL" && node.path) {
    const res = await fetch(`/api/rungs?path=${encodeURIComponent(node.path)}`);
    if (!res.ok) {
      console.error("failed to load rungs", node.path, await res.text());
      return null;
    }
    const data = await res.json();
    node.children = data.rungs.map(r => ({
      name: `Rung ${r.number}`,
      value: r.value,
      data_type: "Rung",
      basis: node.basis,
      tier: node.tier,
      has_children: false,
      rung_text: r.text,
      rung_instructions: r.instructions,
      path: `${node.path}#${r.number}`,
    }));
    return node.children;
  }

  // An alarmed host tag opens into its individual conditions, from their
  // own endpoint for the same reason rungs have one: a real program has
  // hundreds to thousands of them.
  if ((node.path || node._tagPath || "").startsWith("alarms/") && !node._subPath) {
    const alarmPath = node.path || node._tagPath;
    const res = await fetch(`/api/alarms?path=${encodeURIComponent(alarmPath)}`);
    if (!res.ok) {
      console.error("failed to load alarms", alarmPath, await res.text());
      return null;
    }
    const data = await res.json();
    node.children = data.conditions.map(c => ({
      name: c.name,
      value: c.bytes,
      data_type: c.condition_type || "Alarm",
      basis: node.basis,
      tier: node.tier,
      has_children: false,
      alarm_detail: c.detail,
      alarm_severity: c.severity,
      path: `${alarmPath}/${c.name}`,
    }));
    return node.children;
  }

  if (!node.has_children) return null;

  const params = new URLSearchParams({ tag: node._tagPath || "", path: node._subPath || "" });
  // Descending below a type definition keeps whichever reading the user
  // selected. Dropping the mode here sent the deeper fetch to the
  // definition-cost branch, which has no nested path and answered 400.
  if (DEF_MODE === "instance" && (node._tagPath || "").startsWith("udt_definitions/")) {
    params.set("mode", "instance");
  }
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
    // Dimensions, alias target and the subtree confidence summary are all
    // sent by /api/node and were all being dropped here. Without
    // dimensions a drilled array member renders as a scalar -- a real
    // report: "Messages_TiltHoist.Message is also an array and it does
    // not mark the [size] anywhere" -- while displayName/confidenceBar
    // already knew what to do with them the moment they arrive.
    dimensions: c.dimensions || [],
    alias_of: c.alias_of,
    alias_bit: c.alias_bit,
    confidence: c.confidence,
    basis: c.basis,
    has_children: c.has_children,
    tier: "exact",
    _tagPath: node._tagPath,
    _subPath: (node._subPath || "") + c.segment,
  }));
  return node.children;
}

// `ancestors` are the levels BETWEEN the current view and `node` -- the
// tiles a nested (depth > 1) click passed through on its way down. Without
// them the breadcrumb jumped straight from "All" to the leaf, losing every
// level in between: a real report, "i navigated to Tags/Messages_TiltHoist
// and the path just shows 'ALL > Messages_TiltHoist'". A same-level click
// passes none and behaves exactly as before.
// How many children opening this node is about to produce, where that is
// knowable before the fetch: an array states its own dimensions, a routine
// its rung count, and an already-expanded node simply has them. Returns 0
// when the count cannot be known up front (an ordinary UDT), which is
// fine -- those are bounded by their member count and open instantly.
function expectedChildCount(node) {
  if (node.children) return node.children.length;
  const dims = node.dimensions || node.dims;
  if (Array.isArray(dims) && dims.length) return dims.reduce((a, b) => a * b, 1);
  if (node.data_type === "RLL") return rungCountFor(node) || 0;
  return 0;
}

async function drillInto(node, ancestors = []) {
  if (!isDrillable(node)) return;
  // One fetch, no countable progress inside it -- but a 5,000-element
  // array or a 900-rung routine takes long enough that silence reads as a
  // hang. Say what is happening before starting it.
  const expected = expectedChildCount(node);
  const heavy = !node.children && expected > BULK_EXPAND_THRESHOLD;
  if (heavy) {
    showProgress(`Opening ${displayName(node)}`, "");
    setProgressIndeterminate(`${expected.toLocaleString()} items to load`);
  }
  let kids;
  try {
    kids = await ensureChildren(node);
  } finally {
    if (heavy) hideProgress();
  }
  if (!kids || !kids.length) return;
  pushHistory();
  NODE_STACK.push(CURRENT_NODE, ...ancestors);
  CURRENT_NODE = node;
  renderCurrentLevel();
}

// Jump to an arbitrary node identified by an ancestor chain (root first,
// target last) rather than by drilling. Used by the cross-reference and
// the definition links, both of which previously landed on the target with
// an empty ancestor stack and so showed a one-crumb path.
async function navigateToChain(chain) {
  if (!chain || !chain.length) return;
  const target = chain[chain.length - 1];
  const kids = await ensureChildren(target);
  // A node with children becomes the view; a true leaf cannot be a
  // treemap root, so the view lands on its parent with the leaf visible
  // inside it.
  const depthShown = kids && kids.length ? chain.length : chain.length - 1;
  if (depthShown < 1) return;
  pushHistory();
  NODE_STACK = chain.slice(0, depthShown - 1);
  CURRENT_NODE = chain[depthShown - 1];
  renderCurrentLevel();
  const treemapBtn = document.querySelector('.tab-btn[data-tab="treemap"]');
  if (treemapBtn) treemapBtn.click();
}

// Depth-first search for a node, returning the FULL chain from the root
// to it (root first, match last) rather than just the match -- the chain
// is what the breadcrumb needs.
function findChain(root, matches) {
  const walk = (node, trail) => {
    const here = [...trail, node];
    if (matches(node)) return here;
    for (const k of node.children || []) {
      const hit = walk(k, here);
      if (hit) return hit;
    }
    return null;
  };
  return root ? walk(root, []) : null;
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
// for a Program group, [DataType] for an ordinary tag/member leaf
// (2026-08-27: every tag needs [DataType] as a second line, a routine needs
// to show how many rungs it holds, and a program needs to show how many
// routines"). Returns [] when there's nothing extra to say.
// Up to two description lines under a tile's name. Every tile ends with its
// own size, because "how big is this" is the question the whole tool exists
// to answer and it was previously only visible on hover.
function subLabelFor(node) {
  const lines = [];
  if (isGroup(node)) {
    const task = taskInfoFor(node);
    if (task) {
      // Real schedule type off the L5X: CONTINUOUS / PERIODIC / EVENT.
      const bits = [task.type || "TASK"];
      if (task.type === "PERIODIC" && task.rate) bits.push(`${task.rate} ms`);
      if (task.is_safety) bits.push("safety");
      lines.push(bits.join(" · "));
    } else if (node.name.startsWith("Program: ")) {
      const r = routineCountFor(node);
      const t = programTagCountFor(node);
      const bits = [];
      if (r != null) bits.push(`${r} routine${r === 1 ? "" : "s"}`);
      if (t != null) bits.push(`${t} program tag${t === 1 ? "" : "s"}`);
      if (bits.length) lines.push(bits.join("; "));
    } else if (node.children) {
      lines.push(`${node.children.length} item${node.children.length === 1 ? "" : "s"}`);
    }
  } else if (node.data_type === "RLL") {
    const rc = rungCountFor(node);
    if (rc != null) lines.push(`${rc} rung${rc === 1 ? "" : "s"}`);
  } else if (node.alarm_detail) {
    // What the alarm actually watches is the useful line; the condition
    // type is already the [type] line every other leaf gets.
    lines.push(node.alarm_detail);
  } else if (node.data_type === "Rung") {
    // "[Rung]" restates the tile name. The instructions in it are the useful
    // second line.
    const instr = node.rung_instructions || [];
    if (instr.length) lines.push(instr.slice(0, 4).join(" "));
  } else if (node.data_type) {
    lines.push(`[${node.data_type}]`);
  }
  lines.push(fmtBytes(nodeValue(node)));
  return lines;
}

// ---- shared progress modal --------------------------------------------
//
// Anything that takes visible time needs to say so IN the UI. Both users of
// this previously showed nothing at all: a file load sat on a static
// "Loading X..." string in the header, and expanding a wide node fired
// hundreds of fetches whose only visible progress was the Flask request log
// in the terminal behind the browser.

function showProgress(title, detail) {
  const modal = document.getElementById("progress-modal");
  if (!modal) return;
  document.getElementById("progress-title").textContent = title;
  document.getElementById("progress-detail").textContent = detail || "";
  setProgress(0);
  modal.classList.remove("hidden");
}

function setProgress(fraction, detail) {
  const fill = document.getElementById("progress-fill");
  if (!fill) return;
  fill.classList.remove("indeterminate");
  fill.style.width = `${Math.max(0, Math.min(1, fraction)) * 100}%`;
  if (detail != null) document.getElementById("progress-detail").textContent = detail;
}

// No percentage available -- the server is working and will answer when it
// answers. A sweeping bar says "busy" without inventing a number.
function setProgressIndeterminate(detail) {
  const fill = document.getElementById("progress-fill");
  if (!fill) return;
  fill.style.width = "";
  fill.classList.add("indeterminate");
  if (detail != null) document.getElementById("progress-detail").textContent = detail;
}

function hideProgress() {
  const modal = document.getElementById("progress-modal");
  if (modal) modal.classList.add("hidden");
}

// Await many promises while reporting how many have settled. Used for the
// bulk child-expansion below; the count is the only honest progress signal
// available, since each fetch is atomic.
async function awaitWithProgress(promises, label) {
  let done = 0;
  const total = promises.length;
  setProgress(0, `${label} 0 / ${total}`);
  await Promise.all(promises.map(promise => promise.then(value => {
    done += 1;
    setProgress(done / total, `${label} ${done} / ${total}`);
    return value;
  })));
}

// Expanding this many children is where the wait becomes noticeable, so
// it is also where the modal earns its interruption.
const BULK_EXPAND_THRESHOLD = 100;

async function renderTreemap() {
  const svg = document.getElementById("treemap-svg");
  if (!svg.clientWidth) return; // hidden tab, nothing to measure yet
  const children = CURRENT_NODE.children || [];

  // Depth-2 mode needs every visible node's own children loaded before we
  // can lay any of it out -- fetch them all up front (they're cheap local
  // Flask JSON round-trips) rather than trying to paint incrementally.
  // Pre-load every level we are about to draw. Each level is a cheap local
  // round-trip; drawing cannot start until the geometry is known.
  if (NEST_DEPTH > 1) {
    let level = children;
    let shownModal = false;
    try {
      for (let d = 1; d < NEST_DEPTH && level.length; d++) {
        const pending = level.filter(n => isDrillable(n) && !n.children);
        if (pending.length > BULK_EXPAND_THRESHOLD) {
          if (!shownModal) {
            showProgress(
              `Expanding ${displayName(CURRENT_NODE)}`,
              "This level has more than a hundred items to open.",
            );
            shownModal = true;
          }
          await awaitWithProgress(pending.map(ensureChildren), "Opened");
        } else if (pending.length) {
          await Promise.all(pending.map(ensureChildren));
        }
        level = level.flatMap(n => n.children || []);
      }
    } finally {
      if (shownModal) hideProgress();
    }
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
    rect.style.fill = fillForNode(node);
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
      label.textContent = truncateLabel(displayName(node), r.w);
      g.appendChild(label);
      labelLinesUsed = 1;

      // Second and third lines: what it is, then how big it is.
      const subLines = subLabelFor(node);
      subLines.slice(0, 2).forEach((line, i) => {
        const minH = 28 + i * 13;
        if (r.h <= minH) return;
        const sub = document.createElementNS(svgNS, "text");
        sub.setAttribute("x", r.x + 4);
        sub.setAttribute("y", r.y + 27 + i * 13);
        sub.classList.add("tm-label", "tm-label-sub");
        sub.textContent = truncateLabel(line, r.w);
        g.appendChild(sub);
        labelLinesUsed = 2 + i;
      });
    }

    // Depth-2 nesting (2026-08-27): paint this tile's own children
    // inset inside it, visually distinct (dashed stroke, reduced opacity,
    // smaller label) so a grandchild is never mistaken for a same-level
    // sibling. Reserves the header strip the label above already used.
    if (NEST_DEPTH > 1) {
      const headerH = labelLinesUsed >= 2 ? 28 : labelLinesUsed === 1 ? 14 : 0;
      paintNested(svg, g, node, r, headerH, 1, [node]);
    }

    svg.appendChild(g);
  }
}

// Draws a tile's own children inset inside it, recursively, down to
// NEST_DEPTH. Nested tiles are visually distinct (dashed, dimmed, smaller
// label) so a grandchild is never mistaken for a sibling.
function paintNested(svg, g, node, r, headerH, depth, ancestors) {
  if (depth >= NEST_DEPTH) return;
  if (!isDrillable(node) || !node.children || !node.children.length) return;

  const svgNS = "http://www.w3.org/2000/svg";
  const inset = 3;
  const nx = r.x + inset, ny = r.y + inset + headerH;
  const nw = Math.max(r.w - 2 * inset, 0), nh = Math.max(r.h - 2 * inset - headerH, 0);
  if (nw < 8 || nh < 8) return;   // no room left to nest into

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
    crect.style.fill = fillForNode(cnode);
    crect.addEventListener("click", ev => { ev.stopPropagation(); drillInto(cnode, ancestors); });
    crect.addEventListener("mousemove", ev => showTooltip(ev, cnode));
    crect.addEventListener("mouseleave", hideTooltip);
    g.appendChild(crect);

    let usedH = 0;
    if (ir.w > 26 && ir.h > 12) {
      const clabel = document.createElementNS(svgNS, "text");
      clabel.setAttribute("x", ir.x + 3);
      clabel.setAttribute("y", ir.y + 10);
      clabel.classList.add("tm-label", "tm-label-nested");
      clabel.textContent = truncateLabel(displayName(cnode), ir.w);
      g.appendChild(clabel);
      usedH = 11;
    }
    paintNested(svg, g, cnode, ir, usedH, depth + 1, [...ancestors, cnode]);
  }
}

function truncateLabel(name, widthPx) {
  const maxChars = Math.max(3, Math.floor(widthPx / 6.5));
  return name.length > maxChars ? name.slice(0, maxChars - 1) + "…" : name;
}

// Color is reserved for data type (2026-08-20) -- confidence is
// shown via the hatch overlay instead, never by recoloring.
const TYPE_COLORS = {
  SINT: "#5b8dd6", INT: "#4f7fc4", DINT: "#3d6bb0", LINT: "#2c5590",
  REAL: "#3ba17a", BOOL: "#c98a2c", BIT: "#c98a2c", STRING: "#8a5fbf",
  ALIAS: "#5c6472", TIMER: "#d1607a", COUNTER: "#c14f6b", CONTROL: "#a83f5a",
};

// Groups used to share one flat --group-fill, so MainTask, Controller Tags
// and Axis Definitions were indistinguishable blocks of the same colour at
// the root. Give each group its own hue derived from its name -- stable
// across reloads, and distinct from the type palette by being lighter.
function fillForNode(node) {
  if (!isGroup(node)) return colorForType(node.data_type);
  const name = node.name || "";
  if (name === "root") return "var(--group-fill)";
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = (hash * 37 + name.charCodeAt(i)) >>> 0;
  return `hsl(${hash % 360}, 34%, 34%)`;
}

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
// full bar means this element is half of its parent's usage
// (2026-08-27). Uses CURRENT_NODE (the treemap's current drill root), not
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

// Second bar: this node's share of the WHOLE controller, not just of its
// parent. At depth the parent share alone is misleading -- 80% of a small
// folder can be a rounding error against the controller total.
function tooltipControllerBar(node) {
  if (!REPORT || !REPORT.total_bytes) return "";
  const pct = (nodeValue(node) / REPORT.total_bytes) * 100;
  return `<div class="tooltip-bar-wrap"><div class="tooltip-bar tooltip-bar-controller" ` +
    `style="width:${Math.min(pct, 100).toFixed(1)}%"></div></div>` +
    `<div class="tooltip-bar-label">${pct.toFixed(2)}% of controller total</div>`;
}

function showTooltip(ev, node) {
  const tooltip = document.getElementById("tooltip");
  tooltip.classList.remove("hidden");

  if (isGroup(node)) {
    const routines = routineCountFor(node);
    const task = taskInfoFor(node);
    tooltip.innerHTML = `<strong>${displayName(node)}</strong><br>` +
      `<span class="text-dim-on-dark">${groupKind(node)}</span><br>` +
      `${fmtBytes(nodeValue(node))} (${fmtBlocks(nodeValue(node))} blocks)` +
      (task ? `<br>${task.type}${task.type === "PERIODIC" && task.rate ? ` @ ${task.rate} ms` : ""}` +
        `${task.priority ? `, priority ${task.priority}` : ""}` : "") +
      (routines != null ? `<br>${routines} routine${routines === 1 ? "" : "s"}` : "") +
      tooltipParentBar(node) +
      tooltipControllerBar(node) +
      confidenceBarHtml(node) +
      (isDrillable(node) ? " (click to drill in)" : "");
  } else {
    const rc = node.data_type === "RLL" ? rungCountFor(node) : null;
    tooltip.innerHTML =
      `<strong>${displayName(node)}</strong><br>` +
      (node.rung_text
        ? `<div class="rung-text">${node.rung_text.replace(/[&<>]/g, ch =>
            ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[ch]))}</div>`
        : `${node.data_type}<br>`) +
      (rc != null ? `${rc} rung${rc === 1 ? "" : "s"}<br>` : "") +
      `${fmtBytes(node.value)} (${fmtBlocks(node.value)} blocks)<br>` +
      (node.tier === "estimated" ? `<span class="tier-chip">ESTIMATED</span>` : "") +
      `<span class="basis-chip basis-${node.basis}">${node.basis}</span>` +
      jsrCallsNote(node) +
      tooltipParentBar(node) +
      tooltipControllerBar(node) +
      confidenceBarHtml(node) +
      (isDrillable(node) ? " (click to drill in)" : "");
  }

  positionTooltip(tooltip, ev);
}

// Flip the tooltip to the other side of the cursor near the right/bottom
// edge, so it never runs off screen. Measured against the VIEWPORT rather
// than the treemap pane: the pane can extend past the window, and it is the
// window edge that actually clips.
function positionTooltip(tooltip, ev) {
  const wrap = document.getElementById("treemap-main").getBoundingClientRect();
  const GAP = 12;
  const tw = tooltip.offsetWidth;
  const th = tooltip.offsetHeight;

  const flipX = ev.clientX > window.innerWidth * 0.75 || ev.clientX + GAP + tw > window.innerWidth;
  const flipY = ev.clientY > window.innerHeight * 0.75 || ev.clientY + GAP + th > window.innerHeight;

  let left = flipX ? ev.clientX - GAP - tw : ev.clientX + GAP;
  let top = flipY ? ev.clientY - GAP - th : ev.clientY + GAP;

  // Never push it off the opposite edge either.
  left = Math.max(4, Math.min(left, window.innerWidth - tw - 4));
  top = Math.max(4, Math.min(top, window.innerHeight - th - 4));

  tooltip.style.left = (left - wrap.left) + "px";
  tooltip.style.top = (top - wrap.top) + "px";
}

function hideTooltip() {
  document.getElementById("tooltip").classList.add("hidden");
}

// ---- list view ----
// Scoped to CURRENT_NODE's direct children (2026-08-20, "if im down
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
      name: displayName(c),
      // Name the container instead of the useless "(group)".
      data_type: c.data_type || groupKind(c),
      bytes,
      pct_of_total: total ? (bytes / total) * 100 : 0,
      pct_of_controller: (REPORT && REPORT.total_bytes) ? (bytes / REPORT.total_bytes) * 100 : 0,
      known_pct: confidenceBreakdown(c).knownPct,
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

// 2026-08-27: rows are now click-to-drill (same target a treemap
// tile click would drill into), matching "List should be browsable to see
// inside each element name or type."



// The per-node action strip beside the breadcrumb: a link to the type's
// definition, and on a definition itself the toggle between what the type
// costs to exist and what one instance of it occupies.
function renderNodeActions() {
  const host = document.getElementById("node-actions");
  if (!host) return;
  const node = CURRENT_NODE || {};
  const path = node.path || node._tagPath || "";
  const isDefinition = path.startsWith("udt_definitions/") || path.startsWith("aoi_definitions/");
  let html = definitionLinkHtml(node);
  if (isDefinition) {
    // A radio pair, not a checkbox. These are two readings of the same
    // type and neither is the "off" state of the other, which is exactly
    // what a lone checkbox implies.
    // An AOI is priced under the same "udt_definitions/" path as a real
    // UDT, so the path cannot tell them apart -- the declared AOI names
    // can, and labelling an AOI "UDT Size" is exactly the blurring this
    // selector exists to undo.
    const defName = path.slice(path.indexOf("/") + 1);
    const kind = (REPORT && (REPORT.aoi_names || []).includes(defName))
      || path.startsWith("aoi_definitions/") ? "AOI" : "UDT";
    const opt = (value, label) =>
      `<label class="defmode-opt"><input type="radio" name="defmode" value="${value}"` +
      `${DEF_MODE === value ? " checked" : ""}><span>${label}</span></label>`;
    html +=
      `<span class="defmode-toggle" title="Definition cost is a flat per-declared-member rate, ` +
      `so a BOOL, a DINT and a TIMER all cost the same. Instance size is what one copy occupies.">` +
      `<span class="defmode-legend">${kind} Size:</span>` +
      opt("instance", "instance") + opt("definition", "definition") +
      `</span>`;
  }
  host.innerHTML = html;
  wireDefinitionLinks(host);
  host.querySelectorAll('input[name="defmode"]').forEach(radio => {
    radio.onchange = () => {
      if (!radio.checked) return;
      DEF_MODE = radio.value;
      reloadDefinitionChildren();
    };
  });
}

// Re-fetch the current definition node's children in the newly selected
// mode and redraw in place, so the toggle is a view switch rather than a
// navigation.
async function reloadDefinitionChildren() {
  const node = CURRENT_NODE;
  const path = node.path || node._tagPath || "";
  if (!path.startsWith("udt_definitions/") && !path.startsWith("aoi_definitions/")) return;
  const url = `/api/node?tag=${encodeURIComponent(path)}` +
    (DEF_MODE === "instance" ? "&mode=instance" : "");
  try {
    const res = await fetch(url);
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    node.children = data.children.map(c => ({ ...c, _tagPath: path, _subPath: c.segment }));
    renderCurrentLevel(false);
  } catch (err) {
    console.error("definition mode switch failed", err);
  }
}

// ---- cross-reference tab -------------------------------------------------
//
// Populated ONLY when the tab is opened. Walking every tag down through the
// member graph is real work on a wide controller, and most sessions never
// ask for it, so doing it on load would tax every file to serve a few.
let XREF_STATE = { type: null, loading: false, data: null };

function xrefTypeForNode(node) {
  if (!node) return null;
  const path = node.path || node._tagPath || "";
  if (path.startsWith("udt_definitions/")) return path.slice("udt_definitions/".length);
  if (path.startsWith("aoi_definitions/")) return path.slice("aoi_definitions/".length);
  // A plain instance node: cross-reference its declared type.
  const dt = node.data_type;
  return REPORT && REPORT.type_names && REPORT.type_names.includes(dt) ? dt : null;
}

function resetXref() {
  XREF_STATE = { type: null, loading: false, data: null };
}

// The tab only means something on a UDT or AOI, so it is HIDDEN rather
// than greyed out everywhere else -- a permanently disabled tab reads as
// a broken feature. If it disappears while it happens to be the open tab
// (navigating off a type to an ordinary tag), fall back to the treemap
// rather than leaving an empty panel with no tab selected.
function syncXrefTab() {
  const btn = document.getElementById("xref-tab-btn");
  if (!btn) return;
  const type = xrefTypeForNode(CURRENT_NODE);
  const wasActive = btn.classList.contains("active");
  btn.hidden = !type;
  btn.disabled = !type;
  btn.title = type ? `Where ${type} is used` : "Select a UDT or AOI to cross-reference";
  if (!type && wasActive) {
    const treemapBtn = document.querySelector('.tab-btn[data-tab="treemap"]');
    if (treemapBtn) treemapBtn.click();
    return;
  }
  if (wasActive) renderXref();
}

async function renderXref() {
  const el = document.getElementById("xref-detail");
  if (!el) return;
  const type = xrefTypeForNode(CURRENT_NODE);
  if (!type) {
    el.innerHTML = `<p class="errors-empty">Select a UDT or Add-On Instruction to see where it is used.</p>`;
    return;
  }
  if (XREF_STATE.type === type && XREF_STATE.data) return renderXrefTable(el, XREF_STATE.data);
  if (XREF_STATE.type === type && XREF_STATE.loading) return;

  XREF_STATE = { type, loading: true, data: null };
  el.innerHTML =
    `<p>Finding every use of <strong>${escapeHtml(type)}</strong>&hellip;</p>` +
    `<div class="xref-progress"><div></div></div>` +
    `<p class="text-dim">Walking every tag through the member graph, including nested types.</p>`;
  try {
    const res = await fetch(`/api/xref?type=${encodeURIComponent(type)}`);
    const data = await res.json();
    if (data.error) throw new Error(data.error);
    if (XREF_STATE.type !== type) return;  // navigated away mid-flight
    XREF_STATE = { type, loading: false, data };
    renderXrefTable(el, data);
  } catch (err) {
    XREF_STATE = { type, loading: false, data: null };
    el.innerHTML = `<p class="errors-empty">Cross-reference failed: ${escapeHtml(err.message)}</p>`;
  }
}

function renderXrefTable(el, data) {
  if (!data.usages.length) {
    el.innerHTML = `<p class="errors-empty">${escapeHtml(data.type)} is declared but never used by any tag.</p>`;
    return;
  }
  const rows = data.usages.map(u =>
    `<tr><td class="xref-path" data-path="${escapeHtml(u.path)}">${escapeHtml(u.path)}</td>` +
    `<td>${escapeHtml(u.scope)}</td>` +
    `<td>${u.direct ? "tag" : "member of " + escapeHtml(u.via)}</td></tr>`).join("");
  el.innerHTML =
    `<p><strong>${escapeHtml(data.type)}</strong> &mdash; ${data.count} usage` +
    `${data.count === 1 ? "" : "s"}. An array shows its [0] element; the path is navigable either way.</p>` +
    `<table><thead><tr><th>Path</th><th>Scope</th><th>Reached via</th></tr></thead><tbody>${rows}</tbody></table>`;
  el.querySelectorAll(".xref-path").forEach(td => {
    td.onclick = () => navigateToPath(td.dataset.path);
  });
}

// Best effort: jump to the owning tag, which is always a real node in the
// loaded hierarchy. Deeper member segments are a drill the tree already
// knows how to do from there.
function navigateToPath(path) {
  const tagPath = path.split(/[.[]/)[0];
  const chain = findChain(REPORT && REPORT.hierarchy,
    n => (n.path || n._tagPath) === tagPath);
  if (chain) navigateToChain(chain);
}

// ---- list filters (name / type) -----------------------------------------
//
// Partial match by default, with * as a wildcard, because both are what a
// tag name actually needs: "hoist" should find TiltHoistCmd, and
// "*Timer*Dn" should find the one member you remember the shape of.
//
// The filter is scoped to the List tab ONLY and is cleared on any
// navigation. A filter that survived a drill would silently hide rows at
// the new level, and a treemap that quietly stopped summing to its parent
// because a filter was left on somewhere else is a worse bug than no
// filter at all.
const LIST_FILTERS = { name: "", data_type: "" };

function filterRegex(pattern) {
  const trimmed = String(pattern || "").trim();
  if (!trimmed) return null;
  // Escape everything regex-special, then turn the escaped \* back into
  // a wildcard. Substring semantics, so no anchors unless the user wrote
  // them as wildcards.
  const body = trimmed
    .replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
    .replace(/\\\*/g, ".*");
  try {
    return new RegExp(body, "i");
  } catch {
    return null;
  }
}

function filtersActive() {
  return Boolean(LIST_FILTERS.name || LIST_FILTERS.data_type);
}

function applyListFilters(rows) {
  const rxName = filterRegex(LIST_FILTERS.name);
  const rxType = filterRegex(LIST_FILTERS.data_type);
  if (!rxName && !rxType) return rows;
  return rows.filter(r =>
    (!rxName || rxName.test(String(r.name || ""))) &&
    (!rxType || rxType.test(String(r.data_type || ""))));
}

function clearListFilters() {
  LIST_FILTERS.name = "";
  LIST_FILTERS.data_type = "";
  document.querySelectorAll(".filter-popup").forEach(el => el.remove());
}

function setupFilterButtons(table) {
  table.querySelectorAll(".funnel-btn").forEach(btn => {
    const key = btn.dataset.filter;
    btn.classList.toggle("active", Boolean(LIST_FILTERS[key]));
    btn.onclick = ev => {
      ev.stopPropagation();  // the header itself sorts; the funnel must not
      const existing = btn.parentElement.querySelector(".filter-popup");
      document.querySelectorAll(".filter-popup").forEach(el => el.remove());
      if (existing) return;
      const pop = document.createElement("div");
      pop.className = "filter-popup";
      pop.innerHTML =
        `<input type="text" value="${escapeHtml(LIST_FILTERS[key])}" ` +
        `placeholder="${key === "name" ? "e.g. hoist or *Timer*Dn" : "e.g. DINT or *STRING*"}">` +
        `<div class="filter-hint">Partial match. * matches anything.</div>` +
        `<div class="filter-actions"><button type="button" data-act="clear">Clear</button></div>`;
      pop.addEventListener("click", e => e.stopPropagation());
      const input = pop.querySelector("input");
      input.addEventListener("input", () => {
        LIST_FILTERS[key] = input.value;
        renderList();
      });
      input.addEventListener("keydown", e => {
        if (e.key === "Escape") { document.querySelectorAll(".filter-popup").forEach(el => el.remove()); }
      });
      pop.querySelector('[data-act="clear"]').onclick = () => {
        LIST_FILTERS[key] = "";
        pop.remove();
        renderList();
      };
      btn.parentElement.appendChild(pop);
      input.focus();
      input.select();
    };
  });
}

document.addEventListener("click", () => {
  document.querySelectorAll(".filter-popup").forEach(el => el.remove());
});

function renderListInto(tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;
  const tbody = table.querySelector("tbody");
  const rows = applyListFilters(currentLevelRows()).sort((a, b) => {
    const { key, dir } = SORT_STATE;
    if (typeof a[key] === "string") return String(a[key]).localeCompare(String(b[key])) * dir;
    // A null (no-storage row) sorts as zero rather than producing NaN,
    // which compares false both ways and leaves the order arbitrary.
    return ((a[key] || 0) - (b[key] || 0)) * dir;
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
    // Confidence as a measured share of bytes, not a single badge -- see
    // confidenceBreakdown for why a badge misleads on any aggregate.
    // known_pct is null for a row that occupies no bytes (a BIT alias, an
    // unmodeled module): there is nothing to be confident ABOUT, and the
    // bar used to throw outright on reaching one.
    const conf = e.known_pct == null
      ? `<div class="conf-cell"><span class="conf-pct text-dim">no storage</span></div>`
      : `<div class="conf-cell"><div class="conf-bar conf-bar-sm">` +
        `<span class="conf-seg conf-known" style="width:${e.known_pct}%"></span>` +
        `<span class="conf-seg conf-fitted" style="width:${100 - e.known_pct}%"></span>` +
        `</div><span class="conf-pct">${e.known_pct.toFixed(0)}%</span>` +
        (e.basis ? `<span class="basis-chip basis-${e.basis}">${e.basis}</span>` : "") +
        (e.tier === "estimated" ? `<span class="tier-chip">ESTIMATED</span>` : "") +
        `</div>`;
    tr.innerHTML =
      `<td>${escapeHtml(e.name)}${subNote}</td>` +
      `<td>${escapeHtml(e.data_type)}</td>` +
      `<td class="num">${Math.round(e.bytes).toLocaleString()}</td>` +
      `<td class="num">${e.pct_of_total.toFixed(2)}%</td>` +
      `<td class="num">${e.pct_of_controller.toFixed(2)}%</td>` +
      `<td>${conf}</td>`;
    tbody.appendChild(tr);
  }

  table.querySelectorAll("th").forEach(th => {
    // Which column is sorted, and which way. Without this the table is
    // sorted by something invisible and the only way to find out is to
    // click a header and watch what moves.
    const key = th.dataset.sort;
    const active = key === SORT_STATE.key;
    th.classList.toggle("sorted", active);
    th.classList.toggle("sorted-asc", active && SORT_STATE.dir === 1);
    th.classList.toggle("sorted-desc", active && SORT_STATE.dir === -1);
    th.setAttribute("aria-sort", active
      ? (SORT_STATE.dir === 1 ? "ascending" : "descending") : "none");
    let caret = th.querySelector(".sort-caret");
    if (!caret) {
      caret = document.createElement("span");
      caret.className = "sort-caret";
      th.appendChild(caret);
    }
    caret.textContent = active ? (SORT_STATE.dir === 1 ? " \u25B2" : " \u25BC") : "";
    th.onclick = () => {
      SORT_STATE.dir = SORT_STATE.key === key ? -SORT_STATE.dir : -1;
      SORT_STATE.key = key;
      renderList();
    };
    applyColumnWidths();
  });
  setupFilterButtons(table);
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
    const key = c.data_type || groupKind(c);
    totals[key] = (totals[key] || 0) + nodeValue(c);
  }
  const grandTotal = Object.values(totals).reduce((s, v) => s + v, 0);
  // Two denominators, because they answer different questions. % of parent
  // says how this type dominates the level you are looking at; % of
  // controller says whether that matters at all against the whole file.
  // Showing only the first makes a 200-byte type look like 90% of
  // something.
  const controllerTotal = (REPORT && REPORT.hierarchy ? nodeValue(REPORT.hierarchy) : 0) || grandTotal;
  const rows = Object.entries(totals)
    .map(([data_type, bytes]) => ({
      data_type, bytes,
      pct_of_total: grandTotal ? (bytes / grandTotal) * 100 : 0,
      pct_of_controller: controllerTotal ? (bytes / controllerTotal) * 100 : 0,
    }))
    .sort((a, b) => b.bytes - a.bytes);

  const maxPct = Math.max(...rows.map(t => t.pct_of_total), 1);
  for (const t of rows) {
    const row = document.createElement("div");
    row.className = "type-row";
    // type-name is a bounded, ellipsis-truncated flex item now
    // (2026-08-27: the type summary has to stay readable with very long tag
    // and UDT names) -- the full name is always
    // available via the title attribute on hover.
    row.innerHTML =
      `<div class="type-swatch" style="background:${colorForType(t.data_type)}"></div>` +
      `<div class="type-name" title="${escapeHtml(t.data_type)}">${escapeHtml(t.data_type)}</div>` +
      `<div class="type-bar-wrap"><div class="type-bar" style="width:${(t.pct_of_total / maxPct) * 100}%"></div></div>` +
      `<div class="type-bytes">${fmtBytes(t.bytes)} (${t.pct_of_total.toFixed(2)}% here` +
      `<span class="type-pct-controller"> &middot; ${t.pct_of_controller.toFixed(2)}% of controller</span>)</div>`;
    el.appendChild(row);
  }
}

main();
