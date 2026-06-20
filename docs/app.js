const DATA_URL = "data/demo_predictions.json";

const MODEL_COLORS = {
  DHR: "#b9852c",
  PlusDC: "#233f73",
  BT: "#346f5b",
};

const MODEL_LABELS = {
  DHR: "DHR",
  PlusDC: "PlusDC",
  BT: "BT",
};

let demoData = null;
let visibleMatches = [];

const pct = (value, digits = 1) => `${(value * 100).toFixed(digits)}%`;
const num = (value) => Number(value).toLocaleString("en-US");

function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

function modelOrder(metrics) {
  return Object.keys(metrics).sort((a, b) => metrics[b].accuracy - metrics[a].accuracy);
}

function renderHero(data) {
  const metrics = data.summary.metrics;
  setText("hero-accuracy", pct(metrics.DHR.accuracy));
  setText("hero-matches", num(data.summary.matches));
  setText("hero-players", num(data.summary.players));
  setText("hero-brier", metrics.DHR.brier.toFixed(3));
  setText("hero-period", `${data.period.description} Generated ${new Date(data.generated_at).toLocaleString()}.`);
  setText("data-stamp", `Prediction feed generated ${new Date(data.generated_at).toLocaleString()}`);
}

function renderModelCards(data) {
  const container = document.getElementById("model-cards");
  const metrics = data.summary.metrics;
  const ordered = modelOrder(metrics);
  container.innerHTML = ordered.map((model, idx) => {
    const m = metrics[model];
    const meta = data.models[model];
    return `
      <article class="model-card" style="--model-color:${MODEL_COLORS[model]}">
        <header>
          <div>
            <h3>${meta.name}</h3>
            <p class="muted">${meta.description}</p>
          </div>
          <span class="rank-badge">#${idx + 1}</span>
        </header>
        <div class="metric-stack">
          ${metricRow("Accuracy", m.accuracy, pct(m.accuracy))}
          ${metricRow("Brier", 1 - m.brier, m.brier.toFixed(3))}
          ${metricRow("Log loss", 1 - Math.min(m.log_loss, 1), m.log_loss.toFixed(3))}
          ${metricRow("Confidence", m.average_confidence, pct(m.average_confidence))}
        </div>
      </article>`;
  }).join("");
}

function metricRow(label, value, display) {
  return `
    <div class="metric-row">
      <span>${label}</span>
      <span class="bar-track"><span class="bar-fill" style="--value:${Math.max(0, Math.min(1, value)) * 100}%"></span></span>
      <span>${display}</span>
    </div>`;
}

function renderFeatureGroups(data) {
  const container = document.getElementById("feature-groups");
  container.innerHTML = data.feature_groups.map(group => `
    <div class="feature-group">
      <strong>${group.code} — ${group.name}</strong>
      <span>${group.dimensions} dims</span>
    </div>
  `).join("");
}

function renderMonthlyChart(data) {
  const container = document.getElementById("monthly-chart");
  const months = data.summary.monthly_accuracy.slice(-12);
  container.innerHTML = months.map(row => `
    <div class="month-row">
      <span>${row.month.slice(2)}</span>
      <div class="month-bars">
        ${["DHR", "PlusDC", "BT"].map(model => row[model] === undefined ? "" : `
          <div class="metric-row">
            <span>${model}</span>
            <span class="bar-track">
              <span class="bar-fill" style="--model-color:${MODEL_COLORS[model]};--value:${row[model] * 100}%"></span>
            </span>
            <span>${pct(row[model], 0)}</span>
          </div>
        `).join("")}
      </div>
    </div>
  `).join("");
}

function populateFilters(data) {
  const surfaces = Array.from(new Set(data.matches.map(m => m.surface).filter(Boolean))).sort();
  const select = document.getElementById("surface-filter");
  select.innerHTML = `<option value="all">All surfaces</option>` + surfaces.map(surface => `<option>${surface}</option>`).join("");
}

function modelProbabilityMarkup(match) {
  return ["DHR", "PlusDC", "BT"].map(model => {
    const result = match.models[model];
    if (!result) return "";
    const cls = result.correct ? "correctness" : "correctness miss";
    return `
      <div class="prob-row" style="--model-color:${MODEL_COLORS[model]}">
        <span>${MODEL_LABELS[model]}</span>
        <span class="prob-track"><span class="prob-fill" style="--prob:${result.p_player1 * 100}%"></span></span>
        <span>${pct(result.p_player1, 0)}</span>
      </div>
      <div class="prob-row">
        <span></span>
        <small>${result.predicted_winner}</small>
        <span class="${cls}">${result.correct ? "hit" : "miss"}</span>
      </div>`;
  }).join("");
}

function matchCard(match) {
  const dhr = match.models.DHR;
  const p1Winner = match.actual_winner === match.players.player1;
  return `
    <article class="match-card">
      <div class="match-topline">
        <div>
          <div class="match-meta">${match.date_label} · ${match.surface || "Surface n/a"} · ${match.round || "Tour match"}</div>
          <div class="players">
            <span class="${p1Winner ? "winner" : ""}">${match.players.player1}</span>
            <span class="${!p1Winner ? "winner" : ""}">${match.players.player2}</span>
          </div>
        </div>
        <div class="match-meta">${match.tournament}<br>Actual: ${match.actual_winner}<br>Score ${match.score.label}</div>
      </div>
      <div class="model-probs">${modelProbabilityMarkup(match)}</div>
      ${dhr ? `<p class="muted">DHR confidence ${pct(dhr.confidence, 0)} · ${dhr.predicted_winner}</p>` : ""}
    </article>`;
}

function renderHighlights(data) {
  const container = document.getElementById("highlight-strip");
  const highlights = data.highlights.slice(0, 3);
  container.innerHTML = highlights.map(match => `
    <article class="highlight-card">
      <small>${match.date_label} · ${match.surface || "ATP"}</small>
      <h3>${match.players.player1} vs ${match.players.player2}</h3>
      <p>DHR called <strong>${match.models.DHR.predicted_winner}</strong> with ${pct(match.models.DHR.confidence, 0)} confidence.</p>
      <span class="${match.models.DHR.correct ? "correctness" : "correctness miss"}">${match.models.DHR.correct ? "Correct" : "Missed"}</span>
    </article>
  `).join("");
}

function applyMatchFilters() {
  const query = document.getElementById("search-input").value.trim().toLowerCase();
  const surface = document.getElementById("surface-filter").value;
  const sort = document.getElementById("sort-filter").value;
  let matches = demoData.matches.filter(match => {
    const haystack = [
      match.players.player1,
      match.players.player2,
      match.tournament,
      match.round,
      match.surface,
      match.date_label,
    ].join(" ").toLowerCase();
    return (!query || haystack.includes(query)) && (surface === "all" || match.surface === surface);
  });

  if (sort === "dhr-confidence") {
    matches.sort((a, b) => (b.models.DHR?.confidence ?? 0) - (a.models.DHR?.confidence ?? 0));
  } else if (sort === "dhr-probability") {
    matches.sort((a, b) => (b.models.DHR?.p_player1 ?? 0) - (a.models.DHR?.p_player1 ?? 0));
  } else if (sort === "upsets") {
    matches.sort((a, b) => Number(a.models.DHR?.correct ?? true) - Number(b.models.DHR?.correct ?? true));
  } else {
    matches.sort((a, b) => b.date.localeCompare(a.date));
  }

  visibleMatches = matches.slice(0, 60);
  renderPredictionList();
}

function renderPredictionList() {
  const container = document.getElementById("prediction-list");
  container.innerHTML = visibleMatches.map(matchCard).join("");
}

async function init() {
  const response = await fetch(DATA_URL);
  demoData = await response.json();
  renderHero(demoData);
  renderModelCards(demoData);
  renderFeatureGroups(demoData);
  renderMonthlyChart(demoData);
  renderHighlights(demoData);
  populateFilters(demoData);
  applyMatchFilters();

  ["search-input", "surface-filter", "sort-filter"].forEach(id => {
    document.getElementById(id).addEventListener("input", applyMatchFilters);
  });
}

init().catch(error => {
  document.body.insertAdjacentHTML("afterbegin", `<div class="load-error">Could not load prediction feed: ${error}</div>`);
});
