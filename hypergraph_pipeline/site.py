from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hypergraph ATP Predictions</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; color: #172033; background: #f6f8fb; }
    header { background: #101828; color: white; padding: 32px 40px; }
    main { padding: 28px 40px; }
    .card { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 8px 24px rgba(16,24,40,.08); }
    table { border-collapse: collapse; width: 100%; background: white; }
    th, td { border-bottom: 1px solid #e6e9ef; padding: 10px 8px; text-align: left; }
    th { color: #475467; font-size: 13px; }
    .prob { font-variant-numeric: tabular-nums; }
    .tag { display: inline-block; padding: 4px 8px; border-radius: 999px; background: #e0ecff; color: #1849a9; }
  </style>
</head>
<body>
  <header>
    <h1>Hypergraph ATP Predictions</h1>
    <p>Deep ranking models that separate player skill from nonlinear match context.</p>
  </header>
  <main>
    <section class="card">
      <span class="tag">DHR vs BT vs PlusDC</span>
      <p>This dashboard is generated from the daily SofaScore data pipeline. It displays outcome probabilities produced by the trained statistical ranking models.</p>
      <p id="status">Loading latest predictions...</p>
    </section>
    <section class="card">
      <h2>Latest predictions</h2>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Player 1</th>
            <th>Player 2</th>
            <th>BT P1</th>
            <th>PlusDC P1</th>
            <th>DHR P1</th>
          </tr>
        </thead>
        <tbody id="prediction-body"></tbody>
      </table>
    </section>
  </main>
  <script>
    function pct(value) {
      if (value === null || value === undefined) return "-";
      return (100 * value).toFixed(1) + "%";
    }
    fetch("data/latest_predictions.json")
      .then(response => response.json())
      .then(data => {
        document.getElementById("status").textContent =
          "Generated " + data.generated_at + " from " + data.training_run;
        const body = document.getElementById("prediction-body");
        body.innerHTML = "";
        for (const row of data.predictions || []) {
          const probs = row.probabilities || {};
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td>${row.date || ""}</td>
            <td>${row.player1_name || ""}</td>
            <td>${row.player2_name || ""}</td>
            <td class="prob">${pct(probs.BT && probs.BT.p_player1_wins)}</td>
            <td class="prob">${pct(probs.PlusDC && probs.PlusDC.p_player1_wins)}</td>
            <td class="prob">${pct(probs.DHR && probs.DHR.p_player1_wins)}</td>`;
          body.appendChild(tr);
        }
      })
      .catch(error => {
        document.getElementById("status").textContent = "No prediction file is available yet: " + error;
      });
  </script>
</body>
</html>
"""


def build_static_site(*, predictions_path: Path, output_dir: Path | None = None) -> dict[str, Any]:
    if not predictions_path.exists():
        raise FileNotFoundError(f"prediction file not found: {predictions_path}")

    output_dir = output_dir or (PROJECT_ROOT / "website")
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(predictions_path, data_dir / "latest_predictions.json")
    (output_dir / "index.html").write_text(INDEX_HTML, encoding="utf-8")

    status = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "predictions_source": str(predictions_path),
        "site_dir": str(output_dir),
    }
    (data_dir / "pipeline_status.json").write_text(
        json.dumps(status, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return status

