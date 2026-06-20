from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .jsonl_utils import read_jsonl
from .predict import (
    ModelBundle,
    _parse_deep_hparams,
    linear_probability,
    load_json,
    load_model_bundle,
    normalize_covariate,
    sigmoid,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DemoConfig:
    feature_name: str = "MI_PP_TS_dim66"
    training_run: Path | None = None
    processed_path: Path | None = None
    raw_match_path: Path | None = None
    output_path: Path = PROJECT_ROOT / "docs" / "data" / "demo_predictions.json"
    start_date: date = date(2024, 6, 1)
    end_date: date = date(2025, 9, 1)
    include_deep: bool = True
    max_matches: int | None = None


def parse_project_date(value: str) -> date:
    return datetime.strptime(value, "%d/%m/%y").date()


def display_date(value: date) -> str:
    return value.strftime("%d %b %Y")


def raw_match_key(match_date: str, player1: str, player2: str) -> tuple[str, str, str]:
    return (match_date, player1.strip(), player2.strip())


def build_raw_match_index(raw_match_path: Path) -> dict[tuple[str, str, str], dict[str, Any]]:
    index: dict[tuple[str, str, str], dict[str, Any]] = {}
    for record in read_jsonl(raw_match_path, missing_ok=True):
        date_value = str(record.get("date", "") or "")
        player1 = str(record.get("player1_name", "") or "")
        player2 = str(record.get("player2_name", "") or "")
        if not date_value or not player1 or not player2:
            continue
        index[raw_match_key(date_value, player1, player2)] = record
    return index


def split_competition(raw_record: dict[str, Any] | None) -> tuple[str, str]:
    if raw_record is None:
        return "ATP Tour", ""
    competition = str(raw_record.get("Competition", "") or "")
    if competition:
        parts = [part.strip() for part in competition.split(",") if part.strip()]
        if len(parts) >= 2:
            return ", ".join(parts[1:-1]) or parts[-2], parts[-1]
    return str(raw_record.get("ATP_competition", "") or "ATP Tour"), ""


def safe_log_loss(probability: float, outcome: int) -> float:
    eps = 1e-12
    p = min(max(probability, eps), 1.0 - eps)
    return -(outcome * math.log(p) + (1 - outcome) * math.log(1.0 - p))


def summarize_metrics(rows: list[dict[str, Any]], model_names: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for model in model_names:
        scored = [row for row in rows if model in row["models"]]
        if not scored:
            continue
        correct = [1 if row["models"][model]["correct"] else 0 for row in scored]
        brier = [row["models"][model]["brier"] for row in scored]
        log_loss = [row["models"][model]["log_loss"] for row in scored]
        confidence = [row["models"][model]["confidence"] for row in scored]
        summary[model] = {
            "matches": len(scored),
            "accuracy": float(np.mean(correct)),
            "brier": float(np.mean(brier)),
            "log_loss": float(np.mean(log_loss)),
            "average_confidence": float(np.mean(confidence)),
        }
    return summary


def best_deep_model(bundle: ModelBundle):
    if bundle.deep_metrics_path is None or bundle.deep_model_path is None:
        raise FileNotFoundError(f"No DHR artifacts found under {bundle.training_run}")

    try:
        import torch
        from packages.deep_algorithm import RankNetWithU_mean
    except ImportError as exc:
        raise RuntimeError(
            "DHR demo generation requires PyTorch. Use Python 3.9/3.11 with torch installed."
        ) from exc

    metrics = load_json(bundle.deep_metrics_path)
    if metrics is None:
        raise ValueError(f"Cannot read {bundle.deep_metrics_path}")
    u = np.asarray(metrics["u"], dtype=float)
    hparams = _parse_deep_hparams(bundle.deep_metrics_path)
    d = len(bundle.norm_params["feat_min"])
    model = RankNetWithU_mean(
        len(u),
        d,
        hidden_dim=int(hparams["hidden_dim"]),
        num_layers=int(hparams["hidden_num"]),
        dropout_p=float(hparams["dropout"]),
        mean=np.zeros(d),
        u_init=u,
    )
    state = torch.load(bundle.deep_model_path, map_location="cpu")
    model.load_state_dict(state)
    model.eval()
    return model, u, str(bundle.deep_metrics_path.parent.name)


def add_model_result(
    row: dict[str, Any],
    model_name: str,
    probability: float,
    score_diff: float,
    outcome: int,
) -> None:
    player1 = row["players"]["player1"]
    player2 = row["players"]["player2"]
    predicted_player1 = probability >= 0.5
    brier = (probability - outcome) ** 2
    row["models"][model_name] = {
        "p_player1": probability,
        "p_player2": 1.0 - probability,
        "score_diff": score_diff,
        "confidence": abs(probability - 0.5) * 2.0,
        "predicted_winner": player1 if predicted_player1 else player2,
        "correct": bool(predicted_player1 == bool(outcome)),
        "brier": brier,
        "log_loss": safe_log_loss(probability, outcome),
    }


def build_demo_predictions(config: DemoConfig) -> dict[str, Any]:
    processed_path = config.processed_path or (
        PROJECT_ROOT
        / "data"
        / "datasets_processed"
        / config.feature_name
        / "match_player_information_numerized_filled_engineered_vectorized.jsonl"
    )
    raw_match_path = config.raw_match_path or (
        PROJECT_ROOT
        / "sofascore_crawler"
        / "data"
        / "match"
        / "final_all_2016_2025_match_information.jsonl"
    )
    training_run = config.training_run or (
        PROJECT_ROOT
        / "training_results"
        / config.feature_name
        / "history_num_3_bad_player_bound1"
        / "rep1"
    )
    bundle = load_model_bundle(feature_name=config.feature_name, training_run=training_run)
    raw_index = build_raw_match_index(raw_match_path)

    records: list[dict[str, Any]] = []
    normalized_pairs: list[tuple[np.ndarray, np.ndarray, int, int]] = []
    for record in read_jsonl(processed_path):
        match_date = parse_project_date(record["date"])
        if not (config.start_date <= match_date < config.end_date):
            continue
        if config.max_matches is not None and len(records) >= config.max_matches:
            break

        player1 = str(record["player1_name"])
        player2 = str(record["player2_name"])
        if player1 not in bundle.player_name_to_id or player2 not in bundle.player_name_to_id:
            continue

        raw_record = raw_index.get(raw_match_key(record["date"], player1, player2))
        tournament, round_name = split_competition(raw_record)
        player1_id = bundle.player_name_to_id[player1]
        player2_id = bundle.player_name_to_id[player2]
        x1_norm = normalize_covariate(record["player1_covariate"], bundle.norm_params)
        x2_norm = normalize_covariate(record["player2_covariate"], bundle.norm_params)
        outcome = 1 if record["player1_final_score"] > record["player2_final_score"] else 0

        row = {
            "id": f"{match_date.isoformat()}::{player1}::{player2}",
            "date": match_date.isoformat(),
            "date_label": display_date(match_date),
            "tournament": tournament,
            "round": round_name,
            "surface": (raw_record or {}).get("Ground type", ""),
            "href": (raw_record or {}).get("href"),
            "players": {"player1": player1, "player2": player2},
            "score": {
                "player1_sets": int(record["player1_final_score"]),
                "player2_sets": int(record["player2_final_score"]),
                "label": f"{record['player1_final_score']}-{record['player2_final_score']}",
            },
            "actual_winner": player1 if outcome else player2,
            "outcome_player1": outcome,
            "models": {},
        }

        if bundle.pl_metrics is not None:
            bt = linear_probability(
                bundle.pl_metrics,
                player1_id,
                player2_id,
                x1_norm,
                x2_norm,
                use_v=False,
            )
            add_model_result(row, "BT", bt["p_player1_wins"], bt["score_diff"], outcome)

        if bundle.plusdc_metrics is not None:
            plusdc = linear_probability(
                bundle.plusdc_metrics,
                player1_id,
                player2_id,
                x1_norm,
                x2_norm,
                use_v=True,
            )
            add_model_result(
                row,
                "PlusDC",
                plusdc["p_player1_wins"],
                plusdc["score_diff"],
                outcome,
            )

        records.append(row)
        normalized_pairs.append((x1_norm, x2_norm, player1_id, player2_id))

    deep_artifact = None
    if config.include_deep and records:
        model, u, deep_artifact = best_deep_model(bundle)
        import torch

        features = np.vstack(
            [feature for x1, x2, _, _ in normalized_pairs for feature in (x1, x2)]
        )
        with torch.no_grad():
            f_scores = (
                model.f(torch.tensor(features, dtype=torch.float32))
                .reshape(-1)
                .detach()
                .cpu()
                .numpy()
            )

        for idx, row in enumerate(records):
            _, _, player1_id, player2_id = normalized_pairs[idx]
            f1 = float(f_scores[2 * idx])
            f2 = float(f_scores[2 * idx + 1])
            score_diff = (float(u[player1_id]) + f1) - (float(u[player2_id]) + f2)
            add_model_result(
                row,
                "DHR",
                sigmoid(score_diff),
                score_diff,
                int(row["outcome_player1"]),
            )

    model_names = ["DHR", "PlusDC", "BT"] if config.include_deep else ["PlusDC", "BT"]
    available_models = [name for name in model_names if any(name in row["models"] for row in records)]
    metrics = summarize_metrics(records, available_models)
    by_month: dict[str, dict[str, Any]] = defaultdict(lambda: {"matches": 0})
    for row in records:
        month = row["date"][:7]
        by_month[month]["matches"] += 1
        for model_name in available_models:
            if model_name in row["models"]:
                by_month[month].setdefault(model_name, []).append(
                    1 if row["models"][model_name]["correct"] else 0
                )

    monthly = []
    for month, values in sorted(by_month.items()):
        entry: dict[str, Any] = {"month": month, "matches": values["matches"]}
        for model_name in available_models:
            if model_name in values:
                entry[model_name] = float(np.mean(values[model_name]))
        monthly.append(entry)

    highlights = sorted(
        [
            row
            for row in records
            if "DHR" in row["models"]
            and row["models"]["DHR"]["confidence"] >= 0.55
        ],
        key=lambda row: row["models"]["DHR"]["confidence"],
        reverse=True,
    )[:10]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project": "Hypergraph ATP Match Lab",
        "feature_name": config.feature_name,
        "training_run": str(training_run),
        "deep_artifact": deep_artifact,
        "period": {
            "label": "ATP test season demo",
            "start": config.start_date.isoformat(),
            "end_exclusive": config.end_date.isoformat(),
            "description": "Matches from Jun 2024 through Aug 2025, held out from the training window.",
        },
        "models": {
            "DHR": {
                "name": "Deep Heterogeneous Ranking",
                "short": "DHR",
                "description": "Intrinsic player utility plus nonlinear match-context effects.",
            },
            "PlusDC": {
                "name": "PlusDC",
                "short": "PlusDC",
                "description": "Linear covariate-assisted Bradley-Terry style ranking.",
            },
            "BT": {
                "name": "Bradley-Terry",
                "short": "BT",
                "description": "Classical player-strength-only baseline.",
            },
        },
        "feature_groups": [
            {"name": "Match Information", "code": "MI", "dimensions": 17},
            {"name": "Player Profile", "code": "PP", "dimensions": 15},
            {"name": "Technical Statistics", "code": "TS", "dimensions": 34},
        ],
        "summary": {
            "matches": len(records),
            "players": len(
                {player for row in records for player in row["players"].values()}
            ),
            "metrics": metrics,
            "monthly_accuracy": monthly,
        },
        "highlights": highlights,
        "matches": records,
    }

    config.output_path.parent.mkdir(parents=True, exist_ok=True)
    config.output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return payload

