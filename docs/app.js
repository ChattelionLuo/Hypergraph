const DATA_URL = "data/demo_predictions.json";

const MODEL_COLORS = {
  DHR: "#b7832d",
  PlusDC: "#1f3d6d",
  BT: "#2c6b57",
};

const MODEL_COPY = {
  DHR: {
    title: "Adagietto",
    short: "Adagietto",
    copy: "Highest-performing signal in the demo window.",
  },
  PlusDC: {
    title: "Largo",
    short: "Largo",
    copy: "Context-aware benchmark with a transparent linear form.",
  },
  BT: {
    title: "Lento",
    short: "Lento",
    copy: "Player-strength benchmark used as the reference point.",
  },
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

function selectedProbability(result) {
  return Math.max(result.p_player1, result.p_player2);
}

function selectedSide(result, match) {
  return result.p_player1 >= result.p_player2 ? match.players.player1 : match.players.player2;
}

function renderHero(data) {
  const metrics = data.summary.metrics;
  setText("hero-accuracy", pct(metrics.DHR.accuracy));
  setText("hero-matches", num(data.summary.matches));
  setText("hero-players", num(data.summary.players));
  setText("data-stamp", `Demo feed - ${new Date(data.generated_at).toLocaleDateString()}`);
}

function renderModelCards(data) {
  const container = document.getElementById("model-cards");
  const metrics = data.summary.metrics;
  const ordered = modelOrder(metrics);
  container.innerHTML = ordered.map((model, idx) => {
    const m = metrics[model];
    const meta = MODEL_COPY[model];
    return `
      <article class="model-card" style="--model-color:${MODEL_COLORS[model]}">
        <header>
          <div>
            <h3>${meta.title}</h3>
            <p>${meta.copy}</p>
          </div>
          <span class="rank-badge">${model}</span>
        </header>
        <div class="metric-stack">
          ${metricRow("Accuracy", m.accuracy, pct(m.accuracy))}
          ${metricRow("Calibration", 1 - m.brier, pct(1 - m.brier))}
        </div>
        <p class="match-note">Rank ${idx + 1} across ${num(m.matches)} evaluated matches.</p>
      </article>`;
  }).join("");
}

function metricRow(label, value, display) {
  return `
    <div class="metric-row">
      <span>${label}</span>
      <span class="bar-track"><span class="bar-fill" style="width:${Math.max(0, Math.min(1, value)) * 100}%"></span></span>
      <span>${display}</span>
    </div>`;
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
    const pick = selectedSide(result, match);
    const pickProb = selectedProbability(result);
    const cls = result.correct ? "correctness" : "correctness miss";
    return `
      <div class="forecast-row" style="--model-color:${MODEL_COLORS[model]}">
        <span class="model-name">${MODEL_COPY[model].short}</span>
        <div class="forecast-main">
          <div class="forecast-pick"><span>${pick}</span></div>
          <div class="prob-track" aria-label="${model} probability for ${pick}">
            <span class="prob-fill" style="width:${pickProb * 100}%"></span>
          </div>
        </div>
        <span class="prob-value">${pct(pickProb, 0)}</span>
        <span class="${cls}">${result.correct ? "hit" : "miss"}</span>
      </div>`;
  }).join("");
}

function matchDetailsMarkup(match) {
  const rows = ["DHR", "PlusDC", "BT"].map(model => {
    const result = match.models[model];
    if (!result) return "";
    return `<div class="detail-model"><strong>${MODEL_COPY[model].short}</strong><span>${match.players.player1} ${pct(result.p_player1, 0)} / ${match.players.player2} ${pct(result.p_player2, 0)}</span></div>`;
  }).join("");
  return `
    <div class="match-details">
      <div class="detail-meta">${match.date_label} / ${match.surface || "Surface n/a"} / ${match.round || "Tour match"}</div>
      <div class="detail-meta">${match.tournament}<br>Actual: ${match.actual_winner}<br>Score ${match.score.label}</div>
      ${rows}
    </div>`;
}

function matchCard(match) {
  const p1Winner = match.actual_winner === match.players.player1;
  return `
    <article class="match-card">
      <div class="match-head">
        <div class="match-date">${match.date_label}</div>
        <div class="players">
          <span class="${p1Winner ? "winner" : ""}">${match.players.player1}</span>
          <span class="${!p1Winner ? "winner" : ""}">${match.players.player2}</span>
        </div>
        <span class="details-toggle" title="Match details">&raquo;</span>
        ${matchDetailsMarkup(match)}
      </div>
      <div class="model-probs">${modelProbabilityMarkup(match)}</div>
    </article>`;
}

function renderHighlights(data) {
  const container = document.getElementById("highlight-strip");
  const highlights = data.highlights.slice(0, 3);
  container.innerHTML = highlights.map(match => {
    const result = match.models.DHR;
    const pickProb = selectedProbability(result);
    return `
      <article class="highlight-card">
        <small>${match.date_label} / ${match.surface || "ATP"}</small>
        <h3>${match.players.player1} vs ${match.players.player2}</h3>
        <p>${result.predicted_winner} / ${pct(pickProb, 0)} model probability.</p>
        <span class="${result.correct ? "correctness" : "correctness miss"}">${result.correct ? "Hit" : "Miss"}</span>
      </article>`;
  }).join("");
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
    matches.sort((a, b) => selectedProbability(b.models.DHR) - selectedProbability(a.models.DHR));
  } else if (sort === "upsets") {
    matches.sort((a, b) => Number(a.models.DHR?.correct ?? true) - Number(b.models.DHR?.correct ?? true));
  } else {
    matches.sort((a, b) => b.date.localeCompare(a.date));
  }

  visibleMatches = matches.slice(0, 48);
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
  renderHighlights(demoData);
  renderModelCards(demoData);
  populateFilters(demoData);
  applyMatchFilters();

  ["search-input", "surface-filter", "sort-filter"].forEach(id => {
    document.getElementById(id).addEventListener("input", applyMatchFilters);
  });
}

init().catch(error => {
  document.body.insertAdjacentHTML("afterbegin", `<div class="load-error">Could not load prediction feed: ${error}</div>`);
});
