/* ==============================================
   CONFIG
   ============================================== */
const CSV_MEMBERS_URL =
  "https://docs.google.com/spreadsheets/d/e/2PACX-1vSSkwYDqcXFlO-Q8KEl_hiMOr222RMC7i0F_5aTtOgAkY8m_DXoqnamrW-tONRVq0zTc886s2P-fNM7/pub?output=csv";

const CSV_BATTLES_URL =
  "https://docs.google.com/spreadsheets/d/e/2PACX-1vSSkwYDqcXFlO-Q8KEl_hiMOr222RMC7i0F_5aTtOgAkY8m_DXoqnamrW-tONRVq0zTc886s2P-fNM7/pub?gid=962278236&single=true&output=csv";

/** Prahy pro vizuální pásma (barvení procent v tabulce) */
const GOOD_FROM = 70;   // 70–100 % = good
const WARN_FROM = 30;   // 30–69 % = warn

/** Barvy donutů */
const COLORS = {
  participation: "#8EC5FF", // světle modrá
  offense: "#FF6B6B",       // červená
  defense: "#34D399",       // zelená
  track: "rgba(0,0,0,0.82)" // černý track pro „nevyplněnou“ část
};

/* ==============================================
   STATE
   ============================================== */
let membersRows = [];
let battlesMeta = [];
let siegeIds = [];

let playerStats = {}; // {nick: {partRate, offRate, offWins, defRate, defWins}}

let leftSort  = { field: "partRate",  dir: "desc" }; // výchozí: řadit dle % Participation
let rightSort = { field: "nickname", dir: "asc"  };  // pravá tabulka

// Multi-selekce (chips)
let selectedSiegeIds = new Set(); // výchozí vyplníme ALL po načtení
let lastChipIndex = null;         // pro Shift-range

/* ==============================================
   HELPERS
   ============================================== */
function toNum(v) {
  if (v === undefined || v === null) return null;
  const s = String(v).trim().toUpperCase();
  if (s === "" || s === "X") return null;
  const n = Number(s);
  return Number.isFinite(n) ? n : null;
}

function pct(v) {
  if (v === null || v === undefined || Number.isNaN(v)) return "0.00%";
  return `${v.toFixed(2)}%`;
}

function bandClass(p) {
  if (p === null || Number.isNaN(p)) return "";
  if (p === 0) return "val-zero";
  if (p < WARN_FROM) return "val-bad";
  if (p < GOOD_FROM) return "val-warn";
  return "val-good";
}

function uniqueNicknames(rows) {
  const set = new Set();
  rows.forEach(r => r.Nickname && set.add(String(r.Nickname).trim()));
  return Array.from(set);
}

function detectSiegeIdsFromHeaders(rows) {
  if (!rows.length) return [];
  const ids = new Set();
  Object.keys(rows[0]).forEach(k => {
    const m = k.match(/^Off_won_(\d+)$/i) || k.match(/^Def_won_(\d+)$/i);
    if (m) ids.add(Number(m[1]));
  });
  return Array.from(ids).sort((a, b) => a - b);
}

function compareValues(a, b, dir = "asc") {
  const mul = dir === "desc" ? -1 : 1;
  if (a === b) return 0;
  if (a === null || a === undefined) return 1 * mul;
  if (b === null || b === undefined) return -1 * mul;
  if (typeof a === "string" || typeof b === "string") {
    return a.toString().localeCompare(b.toString(), undefined, { numeric: true }) * mul;
  }
  return (a < b ? -1 : 1) * mul;
}

function toggleDir(d) { return d === "asc" ? "desc" : "asc"; }

/* Aktivní seznam ID pro výpočty (když není nic vybráno, bereme ALL) */
function getActiveSiegeIds() {
  return (selectedSiegeIds.size > 0) ? Array.from(selectedSiegeIds).sort((a,b) => a-b)
                                     : Array.from(siegeIds);
}

/* ==============================================
   LOADERS
   ============================================== */
function loadMembersCSV() {
  return new Promise((resolve, reject) => {
    Papa.parse(CSV_MEMBERS_URL, {
      download: true,
      header: true,
      skipEmptyLines: true,
      dynamicTyping: false,
      complete: res => {
        membersRows = (res.data || []).filter(r => r.Nickname && String(r.Nickname).trim() !== "");
        siegeIds = detectSiegeIdsFromHeaders(membersRows);
        resolve();
      },
      error: reject
    });
  });
}

function loadBattlesCSV() {
  return new Promise((resolve, reject) => {
    Papa.parse(CSV_BATTLES_URL, {
      download: true,
      header: true,
      skipEmptyLines: true,
      dynamicTyping: false,
      complete: res => {
        battlesMeta = res.data || [];
        resolve();
      },
      error: reject
    });
  });
}

/* ==============================================
   DONUT CHARTS – čisté, barevné
   ============================================== */
function donutOptions(value, color) {
  return {
    type: "doughnut",
    data: {
      labels: ["value", "track"],
      datasets: [
        {
          data: [value, 100 - value],
          backgroundColor: [color, COLORS.track], // barevná část + černý track
          borderWidth: 0,
          borderRadius: 8,
          hoverBackgroundColor: [color, COLORS.track],
          hoverOffset: 0
        }
      ]
    },
    options: {
  responsive: true,
  maintainAspectRatio: true,  // <- bylo false
  aspectRatio: 1,             // <- přidáno: přesný čtverec
  rotation: -90,
  circumference: 360,
  cutout: "76%",
  animation: { duration: 500 },
  plugins: {
    legend: { display: false },
    tooltip: { enabled: false }
  }
},

    plugins: [
      // číslo uprostřed
      {
        id: "centerText",
        beforeDraw(chart) {
          const { width, height, ctx } = chart;
          ctx.save();
          ctx.font = `800 ${Math.round(height * 0.19)}px Inter, system-ui, sans-serif`;
          ctx.fillStyle = "#EAF2FF";
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillText(`${Math.round(value)}%`, width / 2, height / 2);
          ctx.restore();
        }
      }
    ]
  };
}

function drawDonutChart(elementId, value, color) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.innerHTML = "";
  const canvas = document.createElement("canvas");
  el.appendChild(canvas);
  const ctx = canvas.getContext("2d");
  const existing = Chart.getChart(canvas);
  if (existing) existing.destroy();
  new Chart(ctx, donutOptions(value, color));
}

/* ==============================================
   GUILD AGGREGATES (s filtrem)
   ============================================== */
function calculateGuildStats(activeIds = siegeIds) {
  if (!activeIds || activeIds.length === 0) {
    return { participation: 0, offenseWinRate: 0, defenseWinRate: 0 };
  }

  let offW = 0, offL = 0, defW = 0, defL = 0;

  for (const row of membersRows) {
    for (const id of activeIds) {
      const ow = toNum(row[`Off_won_${id}`]), ol = toNum(row[`Off_lost_${id}`]);
      const dw = toNum(row[`Def_won_${id}`]), dl = toNum(row[`Def_lost_${id}`]);
      if (ow !== null) offW += ow;
      if (ol !== null) offL += ol;
      if (dw !== null) defW += dw;
      if (dl !== null) defL += dl;
    }
  }
  const offTot = offW + offL;
  const defTot = defW + defL;

  const offenseWinRate = offTot > 0 ? (offW / offTot) * 100 : 0;
  const defenseWinRate = defTot > 0 ? (defW / defTot) * 100 : 0;

  // participation – průměr min(útoky,10)/10 přes hráče a odehrané siege (jen offense, žádné 'X')
  const nicks = uniqueNicknames(membersRows);
  let sum = 0, den = 0;
  for (const nick of nicks) {
    const r = membersRows.find(x => String(x.Nickname).trim() === nick);
    if (!r) continue;
    let score = 0, played = 0;
    for (const id of activeIds) {
      const ow = toNum(r[`Off_won_${id}`]);
      const ol = toNum(r[`Off_lost_${id}`]);
      if (ow === null || ol === null) continue; // benched → nezapočítávat
      const total = ow + ol;
      score += total > 0 ? Math.min(total, 10) / 10 : 0;
      played += 1;
    }
    if (played > 0) { sum += (score / played); den += 1; }
  }
  const participation = den > 0 ? (sum / den) * 100 : 0;

  return { participation, offenseWinRate, defenseWinRate };
}

/* ==============================================
   PLAYER OVERVIEW (LEVÁ TABULKA) – s filtrem
   ============================================== */
function computePlayerStats(activeIds = siegeIds) {
  playerStats = {};
  const nicks = uniqueNicknames(membersRows);

  if (!activeIds || activeIds.length === 0) {
    // když není nic vybráno → samé nuly (přehledně prázdný filtr)
    nicks.forEach(nick => {
      playerStats[nick] = { partRate:0, offRate:0, offWins:0, defRate:0, defWins:0 };
    });
    return;
  }

  for (const nick of nicks) {
    const r = membersRows.find(x => String(x.Nickname).trim() === nick);
    let offW = 0, offL = 0, defW = 0, defL = 0;

    // Participation
    let partSum = 0;
    let partPlayed = 0;

    for (const id of activeIds) {
      const ow = toNum(r[`Off_won_${id}`]), ol = toNum(r[`Off_lost_${id}`]);
      const dw = toNum(r[`Def_won_${id}`]), dl = toNum(r[`Def_lost_${id}`]);

      if (ow !== null) offW += ow;
      if (ol !== null) offL += ol;
      if (dw !== null) defW += dw;
      if (dl !== null) defL += dl;

      if (ow !== null && ol !== null) {
        const total = ow + ol;
        partSum += total > 0 ? Math.min(total, 10) / 10 : 0;
        partPlayed += 1;
      }
    }

    const offTot = offW + offL;
    const defTot = defW + defL;

    playerStats[nick] = {
      partRate: partPlayed > 0 ? (partSum / partPlayed) * 100 : 0,
      offRate:  offTot > 0 ? (offW / offTot) * 100 : 0,
      offWins:  offW,
      defRate:  defTot > 0 ? (defW / defTot) * 100 : 0,
      defWins:  defW
    };
  }
}

function renderLeftTable() {
  const table = document.getElementById("playerOverviewTable");
  const thead = table.querySelector("thead");
  const tbody = table.querySelector("tbody");
  tbody.innerHTML = "";

  // sloupce včetně % Participation (druhý)
  thead.innerHTML = `
    <tr>
      <th data-field="nickname">Nickname</th>
      <th data-field="partRate">% Participation</th>
      <th data-field="offRate">% Off W-rate</th>
      <th data-field="offWins"># Off won</th>
      <th data-field="defRate">% Def W-rate</th>
      <th data-field="defWins"># Def won</th>
    </tr>
  `;
  attachLeftHeaderSortHandlers();
  applyLeftSortIndicators();

  let rows = Object.entries(playerStats).map(([nickname, s]) => ({ nickname, ...s }));
  rows.sort((a, b) => compareValues(a[leftSort.field], b[leftSort.field], leftSort.dir));

  for (const r of rows) {
    const tr = document.createElement("tr");

    const tdNick = document.createElement("td");
    tdNick.textContent = r.nickname;

    const tdPart = document.createElement("td");
    tdPart.textContent = pct(r.partRate);
    tdPart.className = bandClass(r.partRate);

    const tdOffR = document.createElement("td");
    tdOffR.textContent = pct(r.offRate);
    tdOffR.className = bandClass(r.offRate);

    const tdOffW = document.createElement("td");
    tdOffW.textContent = r.offWins.toString();
    tdOffW.className = "num";

    const tdDefR = document.createElement("td");
    tdDefR.textContent = pct(r.defRate);
    tdDefR.className = bandClass(r.defRate);

    const tdDefW = document.createElement("td");
    tdDefW.textContent = r.defWins.toString();
    tdDefW.className = "num";

    tr.append(tdNick, tdPart, tdOffR, tdOffW, tdDefR, tdDefW);
    tbody.appendChild(tr);
  }
}

function attachLeftHeaderSortHandlers() {
  const table = document.getElementById("playerOverviewTable");
  const ths = table.querySelectorAll("thead th");
  ths.forEach(th => {
    th.style.cursor = "pointer";
    th.addEventListener("click", () => {
      const field = th.dataset.field;
      if (!field) return;
      if (leftSort.field === field) leftSort.dir = toggleDir(leftSort.dir);
      else { leftSort.field = field; leftSort.dir = "desc"; }
      renderLeftTable();
    });
  });
}

function applyLeftSortIndicators() {
  const table = document.getElementById("playerOverviewTable");
  const ths = table.querySelectorAll("thead th");
  ths.forEach(th => {
    const base = th.textContent.replace(/[▲▼]\s*$/, "").trim();
    const field = th.dataset.field;
    if (field === leftSort.field) th.textContent = `${base} ${leftSort.dir === "desc" ? "▼" : "▲"}`;
    else th.textContent = base;
  });
}

/* ==============================================
   RIGHT TABLE (SIEGE DETAIL)
   ============================================== */
function ensureDateRangeSpan() {
  const container = document.querySelector(".siege-details .filters");
  if (!container) return;
  let span = document.getElementById("siegeDateRange");
  if (!span) {
    span = document.createElement("span");
    span.id = "siegeDateRange";
    span.style.marginLeft = "auto";
    span.style.opacity = ".8";
    container.appendChild(span);
  }
}

function setRightTableHeader() {
  const thead = document.querySelector("#siegeDetailsTable thead");
  thead.innerHTML = `
    <tr>
      <th data-field="nickname">Nickname</th>
      <th data-field="offWon">Offense Won</th>
      <th data-field="offLost">Offense Lost</th>
      <th data-field="defWon">Defense Won</th>
      <th data-field="defLost">Defense Lost</th>
    </tr>
  `;
  attachRightHeaderSortHandlers();
  applyRightSortIndicators();
}

function attachRightHeaderSortHandlers() {
  const ths = document.querySelectorAll("#siegeDetailsTable thead th");
  ths.forEach(th => {
    th.style.cursor = "pointer";
    th.addEventListener("click", () => {
      const field = th.dataset.field;
      if (!field) return;
      if (rightSort.field === field) rightSort.dir = toggleDir(rightSort.dir);
      else { rightSort.field = field; rightSort.dir = "desc"; }
      const id = Number(document.getElementById("siegeSelect")?.value);
      populateSiegeDetailsTable(id);
      applyRightSortIndicators();
    });
  });
}

function applyRightSortIndicators() {
  const ths = document.querySelectorAll("#siegeDetailsTable thead th");
  ths.forEach(th => {
    const base = th.textContent.replace(/[▲▼]\s*$/, "").trim();
    const field = th.dataset.field;
    if (field === rightSort.field) th.textContent = `${base} ${rightSort.dir === "desc" ? "▼" : "▲"}`;
    else th.textContent = base;
  });
}

function populateSiegeSelect() {
  const siegeSelect = document.getElementById("siegeSelect");
  if (!siegeSelect) return;

  ensureDateRangeSpan();
  setRightTableHeader();

  siegeSelect.innerHTML = "";
  let options = [];

  if (Array.isArray(battlesMeta) && battlesMeta.length && battlesMeta[0]["Siege ID"]) {
    options = battlesMeta
      .map(r => {
        const id = Number(String(r["Siege ID"]).trim());
        const start = r["Start"] ? String(r["Start"]).trim() : "";
        return { id, label: start ? `Siege #${id} — ${start}` : `Siege #${id}` };
      })
      .filter(o => Number.isFinite(o.id))
      .sort((a, b) => b.id - a.id);
  } else {
    options = siegeIds.map(id => ({ id, label: `Siege #${id}` })).sort((a, b) => b.id - a.id);
  }

  if (!options.length) {
    const op = document.createElement("option");
    op.value = "";
    op.textContent = "No sieges found";
    siegeSelect.appendChild(op);
    return;
  }

  for (const o of options) {
    const op = document.createElement("option");
    op.value = String(o.id);
    op.textContent = o.label;
    siegeSelect.appendChild(op);
  }

  siegeSelect.onchange = () => {
    const id = Number(siegeSelect.value);
    populateSiegeDetailsTable(id);
    updateSiegeMetaStrip(id);
  };

  const first = options[0].id;
  siegeSelect.value = String(first);
  populateSiegeDetailsTable(first);
  updateSiegeMetaStrip(first);
}

function populateSiegeDetailsTable(id) {
  const tbody = document.querySelector("#siegeDetailsTable tbody");
  if (!tbody) return;
  tbody.innerHTML = "";

  const rows = uniqueNicknames(membersRows).map(nickname => {
    const r = membersRows.find(x => String(x.Nickname).trim() === nickname) || {};
    const ow = toNum(r[`Off_won_${id}`]);
    const ol = toNum(r[`Off_lost_${id}`]);
    const dw = toNum(r[`Def_won_${id}`]);
    const dl = toNum(r[`Def_lost_${id}`]);
    return { nickname, offWon: ow, offLost: ol, defWon: dw, defLost: dl };
  });

  rows.sort((a, b) => compareValues(a[rightSort.field], b[rightSort.field], rightSort.dir));

  for (const r of rows) {
    const tr = document.createElement("tr");
    const cells = [r.nickname, r.offWon, r.offLost, r.defWon, r.defLost];

    cells.forEach((val, idx) => {
      const td = document.createElement("td");
      if (idx === 0) {
        td.textContent = val; // nickname
      } else if (val === null) {
        const chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = "x";
        td.appendChild(chip);
      } else {
        td.textContent = String(val);
        td.className = "num";
      }
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  }
  applyRightSortIndicators();
}

function updateSiegeMetaStrip(id) {
  const el = document.getElementById("siegeDateRange");
  if (!el) return;
  const row = battlesMeta.find(x => Number(String(x["Siege ID"]).trim()) === Number(id));
  if (!row) { el.textContent = ""; return; }
  const start = row["Start"]?.toString().trim() ?? "";
  const end   = row["End"]?.toString().trim()   ?? "";
  const rank  = row["Rank"]?.toString().trim()  ?? "";
  const parts = [];
  if (start && end) parts.push(`${start} – ${end}`);
  else if (start) parts.push(start);
  if (rank) parts.push(`Rank ${rank}`);
  el.textContent = parts.join(" • ");
}

/* ==============================================
   MULTI-SELECT BAR (chips) – pro agregáty & levou tabulku
   ============================================== */
function buildSiegeMultiSelectBar() {
  const header = document.querySelector("header");
  if (!header) return;

  // vytvoř kontejner (pokud už neexistuje)
  let bar = document.getElementById("siegeMultiBar");
  if (bar) bar.remove();
  bar = document.createElement("div");
  bar.id = "siegeMultiBar";
  bar.className = "multi-siege-bar";

  // položky: preferuj Battles_Stats (ID + Start), fallback na čisté ID
  let items = [];
  if (Array.isArray(battlesMeta) && battlesMeta.length && battlesMeta[0]["Siege ID"]) {
    items = battlesMeta
      .map(r => {
        const id = Number(String(r["Siege ID"]).trim());
        const date = r["Start"] ? String(r["Start"]).trim() : "";
        return Number.isFinite(id) ? { id, date } : null;
      })
      .filter(Boolean)
      .sort((a, b) => a.id - b.id); // ⬅️ NOVĚ: vzestupně (S#1, S#2, S#3…)
  } else {
    items = siegeIds
      .map(id => ({ id, date: "" }))
      .sort((a, b) => a.id - b.id); // ⬅️ NOVĚ: vzestupně
  }

  // akční chipy
  const allBtn = document.createElement("button");
  allBtn.className = "seg-chip action";
  allBtn.dataset.role = "all";
  allBtn.textContent = "All";
  bar.appendChild(allBtn);

  const clearBtn = document.createElement("button");
  clearBtn.className = "seg-chip action";
  clearBtn.dataset.role = "clear";
  clearBtn.dataset.role = "clear";
  clearBtn.textContent = "Clear";
  bar.appendChild(clearBtn);

  // chips pro jednotlivé sieges (už vzestupně)
  items.forEach((it, idx) => {
    const btn = document.createElement("button");
    btn.className = "seg-chip siege";
    btn.dataset.id = String(it.id);
    btn.dataset.index = String(idx);
    btn.title = "Click: single • Ctrl/Cmd: multi • Shift: range";
    btn.innerHTML = it.date ? `S#${it.id} <span class="chip-date">${it.date}</span>` : `S#${it.id}`;
    bar.appendChild(btn);
  });

  // vložíme bar do headeru (pod řádkem s donuty/„header-row“)
  const headerRow = header.querySelector(".header-row");
  if (headerRow) header.insertBefore(bar, headerRow.nextSibling);
  else header.appendChild(bar);

  // výchozí – ALL selected
  selectedSiegeIds = new Set(siegeIds);
  lastChipIndex = null;
  updateChipSelectionUI(bar);
  attachChipHandlers(bar, items);
}


function attachChipHandlers(bar, items) {
  bar.addEventListener("click", (e) => {
    const btn = e.target.closest(".seg-chip");
    if (!btn) return;

    const role = btn.dataset.role || "";
    if (role === "all") {
      selectedSiegeIds = new Set(siegeIds);
      lastChipIndex = null;
      updateChipSelectionUI(bar);
      updateAggregatesForSelection();
      return;
    }
    if (role === "clear") {
      selectedSiegeIds.clear();
      lastChipIndex = null;
      updateChipSelectionUI(bar);
      updateAggregatesForSelection();
      return;
    }

    // běžný siege chip
    const id = Number(btn.dataset.id);
    const idx = Number(btn.dataset.index);
    const multi = e.ctrlKey || e.metaKey;
    const range = e.shiftKey;

    if (range && lastChipIndex !== null) {
      // vyber souvislý interval mezi lastChipIndex a idx
      const [a, b] = [Math.min(lastChipIndex, idx), Math.max(lastChipIndex, idx)];
      for (let i = a; i <= b; i++) selectedSiegeIds.add(items[i].id);
    } else if (multi) {
      // toggle daného chipu
      if (selectedSiegeIds.has(id)) selectedSiegeIds.delete(id);
      else selectedSiegeIds.add(id);
      lastChipIndex = idx;
    } else {
      // single – jen tento chip
      selectedSiegeIds = new Set([id]);
      lastChipIndex = idx;
    }

    updateChipSelectionUI(bar);
    updateAggregatesForSelection();
  });
}

function updateChipSelectionUI(bar) {
  const siegeButtons = bar.querySelectorAll(".seg-chip.siege");
  siegeButtons.forEach(btn => {
    const id = Number(btn.dataset.id);
    if (selectedSiegeIds.size === 0) {
      btn.classList.remove("selected");
    } else {
      btn.classList.toggle("selected", selectedSiegeIds.has(id));
    }
  });
}

/* Přepočítá donuty + levou tabulku dle výběru chips */
function updateAggregatesForSelection() {
  const active = getActiveSiegeIds();

  // Donuty
  const g = calculateGuildStats(active);
  drawDonutChart("guildParticipationChart", g.participation, COLORS.participation);
  drawDonutChart("guildOffenseWinRateChart", g.offenseWinRate, COLORS.offense);
  drawDonutChart("guildDefenseWinRateChart", g.defenseWinRate, COLORS.defense);

  // Levá tabulka
  computePlayerStats(active);
  renderLeftTable();
}

/* ==============================================
   INIT
   ============================================== */
async function initDashboard() {
  try {
    await loadMembersCSV();
    await loadBattlesCSV();

    // postav lištu chips (multi-selekce)
    buildSiegeMultiSelectBar();

    // výpočty a render podle výchozího výběru (ALL)
    updateAggregatesForSelection();

    // Pravá tabulka + výběr single siege (nezávislé na chips)
    populateSiegeSelect();
  } catch (e) {
    console.error(e);
    document.body.innerHTML =
      "<h1 style='padding:24px;font-family:sans-serif;color:#fff'>Error loading dashboard. Open console for details.</h1>";
  }
}

document.addEventListener("DOMContentLoaded", initDashboard);
