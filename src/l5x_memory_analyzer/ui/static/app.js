// Vanilla JS/SVG squarified treemap -- no external deps by design, since this
// runs on engineering workstations that are frequently airgapped OT networks.

let REPORT = null;
let CURRENT_NODE = null; // node currently shown as the treemap root
let NODE_STACK = [];     // ancestors of CURRENT_NODE, for the breadcrumb
let SORT_STATE = { key: "bytes", dir: -1 };

async function main() {
  const res = await fetch("/api/report");
  REPORT = await res.json();

  document.getElementById("file-info").textContent =
    `${REPORT.file_name}  (Schema ${REPORT.schema_revision}, Software ${REPORT.software_revision})`;

  const pct = REPORT.budget_bytes ? (REPORT.total_bytes / REPORT.budget_bytes) * 100 : 0;
  const fill = document.getElementById("budget-bar-fill");
  fill.style.width = `${Math.min(pct, 100)}%`;
  if (pct > 100) fill.classList.add("over");
  document.getElementById("budget-label").textContent =
    `${fmtBytes(REPORT.total_bytes)} / ${fmtBytes(REPORT.budget_bytes)} (${pct.toFixed(2)}%)`;

  if (REPORT.errors && REPORT.errors.length) {
    const el = document.getElementById("errors-footer");
    el.classList.remove("hidden");
    el.textContent = `${REPORT.errors.length} tag(s) could not be sized: ` +
      REPORT.errors.slice(0, 5).map(e => `${e.path} (${e.message})`).join("; ") +
      (REPORT.errors.length > 5 ? ` ...and ${REPORT.errors.length - 5} more` : "");
  }

  CURRENT_NODE = REPORT.hierarchy;
  NODE_STACK = [];

  setupTabs();
  setupTreemapResize();
  renderBreadcrumb();
  renderTreemap();
  renderList();
  renderTypeSummary();
}

function fmtBytes(n) {
  if (n == null) return "-";
  if (n >= 1024 * 1024) return (n / (1024 * 1024)).toFixed(2) + " MB";
  if (n >= 1024) return (n / 1024).toFixed(1) + " KB";
  return n + " B";
}

function nodeValue(node) {
  if (typeof node.value === "number") return node.value;
  if (!node.children) return 0;
  return node.children.reduce((s, c) => s + nodeValue(c), 0);
}

function isLeaf(node) {
  return !node.children;
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

function drillInto(node) {
  if (isLeaf(node)) return;
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

function renderTreemap() {
  const svg = document.getElementById("treemap-svg");
  if (!svg.clientWidth) return; // hidden tab, nothing to measure yet
  svg.innerHTML = "";
  const w = svg.clientWidth, h = svg.clientHeight;
  svg.setAttribute("viewBox", `0 0 ${w} ${h}`);

  const children = CURRENT_NODE.children || [];
  const rects = [];
  squarify(children, 0, 0, w, h, rects);

  const tooltip = document.getElementById("tooltip");

  for (const r of rects) {
    const node = r.node;
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");

    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    rect.setAttribute("x", r.x);
    rect.setAttribute("y", r.y);
    rect.setAttribute("width", Math.max(r.w, 0));
    rect.setAttribute("height", Math.max(r.h, 0));
    rect.classList.add("tm-rect");
    if (isLeaf(node)) {
      rect.style.fill = basisColor(node.basis);
    } else {
      rect.classList.add("group");
    }
    rect.addEventListener("click", () => drillInto(node));
    rect.addEventListener("mousemove", ev => showTooltip(ev, node));
    rect.addEventListener("mouseleave", hideTooltip);
    g.appendChild(rect);

    if (r.w > 40 && r.h > 14) {
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", r.x + 4);
      label.setAttribute("y", r.y + 14);
      label.classList.add("tm-label");
      if (isLeaf(node)) label.classList.add("leaf");
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

function basisColor(basis) {
  return {
    KNOWN: "#3d9a5a",
    ASSUMED: "#d9a531",
    FITTED: "#e07b2c",
    UNKNOWN: "#c0392b",
  }[basis] || "#888";
}

function showTooltip(ev, node) {
  const tooltip = document.getElementById("tooltip");
  tooltip.classList.remove("hidden");
  const wrap = document.getElementById("panel-treemap").getBoundingClientRect();
  tooltip.style.left = (ev.clientX - wrap.left + 12) + "px";
  tooltip.style.top = (ev.clientY - wrap.top + 12) + "px";

  if (isLeaf(node)) {
    tooltip.innerHTML =
      `<strong>${node.name}</strong><br>` +
      `${node.data_type}<br>` +
      `${fmtBytes(node.value)}<br>` +
      `<span class="basis-chip basis-${node.basis}">${node.basis}</span> ${node.tier}`;
  } else {
    tooltip.innerHTML = `<strong>${node.name}</strong><br>${fmtBytes(nodeValue(node))} (click to drill in)`;
  }
}

function hideTooltip() {
  document.getElementById("tooltip").classList.add("hidden");
}

// ---- list view ----

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
      `<div class="type-name">${t.data_type}</div>` +
      `<div class="type-bar-wrap"><div class="type-bar" style="width:${(t.pct_of_total / maxPct) * 100}%"></div></div>` +
      `<div class="type-bytes">${fmtBytes(t.bytes)} (${t.pct_of_total.toFixed(2)}%)</div>`;
    el.appendChild(row);
  }
}

main();
