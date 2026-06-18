from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import date
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .jsonl_utils import filter_records_by_dates, read_jsonl, record_key


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class UnknownPlayerError(ValueError):
    pass


@dataclass(frozen=True)
class ModelBundle:
    feature_name: str
    training_run: Path
    player_name_to_id: dict[str, int]
    norm_params: dict[str, np.ndarray]
    pl_metrics: dict[str, Any] | None
    plusdc_metrics: dict[str, Any] | None
    deep_metrics_path: Path | None
    deep_model_path: Path | None


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def load_json(path: Path, *, missing_ok: bool = False) -> dict[str, Any] | None:
    if not path.exists():
        if missing_ok:
            return None
        raise FileNotFoundError(f"JSON file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_deep_artifact(training_run: Path) -> tuple[Path | None, Path | None]:
    candidates = []
    for metrics_path in training_run.glob("Deep/*/deep_metrics.json"):
        metrics = load_json(metrics_path, missing_ok=True) or {}
        score = metrics.get("best_val_ll", metrics.get("val_likelihood", float("-inf")))
        try:
            score_value = float(score)
        except (TypeError, ValueError):
            score_value = float("-inf")
        candidates.append((score_value, metrics_path))

    if not candidates:
        return None, None
    candidates.sort(key=lambda item: item[0], reverse=True)
    best_metrics = candidates[0][1]
    best_model = best_metrics.parent / "best_model.pt"
    return best_metrics, best_model if best_model.exists() else None


def load_model_bundle(
    *,
    feature_name: str = "MI_PP_TS_dim66",
    training_run: Path | None = None,
) -> ModelBundle:
    training_run = training_run or (
        PROJECT_ROOT
        / "training_results"
        / feature_name
        / "history_num_3_bad_player_bound1"
        / "rep1"
    )

    split_info = load_json(training_run / "split_info.json")
    if split_info is None:
        raise FileNotFoundError(f"missing split_info.json under {training_run}")

    norm_path = training_run / "norm_params.npz"
    if not norm_path.exists():
        raise FileNotFoundError(f"missing norm_params.npz under {training_run}")
    norm_npz = np.load(norm_path)
    norm_params = {
        "feat_min": norm_npz["feat_min"],
        "feat_max": norm_npz["feat_max"],
        "is_one_hot": norm_npz["is_one_hot"],
    }

    player_name_to_id = {
        str(name): int(player_id)
        for name, player_id in split_info.get("player_name_to_id", {}).items()
    }
    deep_metrics_path, deep_model_path = find_deep_artifact(training_run)

    return ModelBundle(
        feature_name=feature_name,
        training_run=training_run,
        player_name_to_id=player_name_to_id,
        norm_params=norm_params,
        pl_metrics=load_json(training_run / "PL" / "PL_metrics.json", missing_ok=True),
        plusdc_metrics=load_json(
            training_run / "PlusDC" / "PlusDC_metrics.json", missing_ok=True
        ),
        deep_metrics_path=deep_metrics_path,
        deep_model_path=deep_model_path,
    )


def normalize_covariate(covariate: list[float] | np.ndarray, norm_params: dict[str, np.ndarray]) -> np.ndarray:
    vector = np.asarray(covariate, dtype=float).copy()
    feat_min = norm_params["feat_min"]
    feat_max = norm_params["feat_max"]
    is_one_hot = norm_params["is_one_hot"].astype(bool)
    if vector.shape[0] != feat_min.shape[0]:
        raise ValueError(
            f"covariate dimension {vector.shape[0]} does not match model dimension {feat_min.shape[0]}"
        )

    feat_range = feat_max - feat_min
    zero_mask = feat_range == 0
    feat_range_safe = feat_range.copy()
    feat_range_safe[zero_mask] = 1.0
    scale_mask = (~is_one_hot) & (~zero_mask)

    vector[scale_mask] = -1.0 + 2.0 * (
        (vector[scale_mask] - feat_min[scale_mask]) / feat_range_safe[scale_mask]
    )
    vector[zero_mask & (~is_one_hot)] = 0.0
    vector = np.round(vector, 3)
    vector[np.isclose(vector, 0.0)] = 0.0
    return vector


def player_model_id(bundle: ModelBundle, record: dict[str, Any], prefix: str) -> int:
    name = str(record.get(f"{prefix}_name", "") or "")
    if name in bundle.player_name_to_id:
        return bundle.player_name_to_id[name]
    raise UnknownPlayerError(f"unknown player for trained model: {name!r}")


def linear_probability(
    metrics: dict[str, Any],
    player1_id: int,
    player2_id: int,
    x1_norm: np.ndarray,
    x2_norm: np.ndarray,
    *,
    use_v: bool,
) -> dict[str, Any]:
    u = np.asarray(metrics["u"], dtype=float)
    if player1_id >= len(u) or player2_id >= len(u):
        raise UnknownPlayerError(
            f"player ids {player1_id}, {player2_id} exceed u dimension {len(u)}"
        )

    u1 = float(u[player1_id])
    u2 = float(u[player2_id])
    x1_component = 0.0
    x2_component = 0.0
    if use_v:
        v = np.asarray(metrics["v"], dtype=float)
        x1_component = float(np.dot(v, x1_norm))
        x2_component = float(np.dot(v, x2_norm))

    score_diff = (u1 + x1_component) - (u2 + x2_component)
    return {
        "p_player1_wins": sigmoid(score_diff),
        "p_player2_wins": sigmoid(-score_diff),
        "score_diff": score_diff,
        "components": {
            "u1": u1,
            "u2": u2,
            "x1_effect": x1_component,
            "x2_effect": x2_component,
        },
    }


def _parse_deep_hparams(metrics_path: Path) -> dict[str, float | int]:
    name = metrics_path.parent.name
    match = re.search(
        r"hidden(?P<hidden_num>\d+)_dim(?P<hidden_dim>\d+).*_dropout(?P<dropout>[0-9.]+)",
        name,
    )
    if not match:
        raise ValueError(f"cannot parse deep hyperparameters from {name!r}")
    return {
        "hidden_num": int(match.group("hidden_num")),
        "hidden_dim": int(match.group("hidden_dim")),
        "dropout": float(match.group("dropout")),
    }


def deep_probability(
    bundle: ModelBundle,
    player1_id: int,
    player2_id: int,
    x1_norm: np.ndarray,
    x2_norm: np.ndarray,
) -> dict[str, Any]:
    if bundle.deep_metrics_path is None or bundle.deep_model_path is None:
        raise FileNotFoundError(f"no Deep model artifact found under {bundle.training_run}")

    try:
        import torch
        from packages.deep_algorithm import RankNetWithU_mean
    except ImportError as exc:
        raise RuntimeError(
            "Deep predictions require torch and the research model package. "
            "Install requirements.txt in the Python environment used for prediction."
        ) from exc

    metrics = load_json(bundle.deep_metrics_path)
    if metrics is None or "u" not in metrics:
        raise ValueError(f"Deep metrics missing u: {bundle.deep_metrics_path}")

    hparams = _parse_deep_hparams(bundle.deep_metrics_path)
    u = np.asarray(metrics["u"], dtype=float)
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

    with torch.no_grad():
        features = torch.tensor(np.stack([x1_norm, x2_norm]), dtype=torch.float32)
        f_scores = model.f(features).reshape(-1).numpy()

    u1 = float(u[player1_id])
    u2 = float(u[player2_id])
    f1 = float(f_scores[0])
    f2 = float(f_scores[1])
    score_diff = (u1 + f1) - (u2 + f2)
    return {
        "p_player1_wins": sigmoid(score_diff),
        "p_player2_wins": sigmoid(-score_diff),
        "score_diff": score_diff,
        "components": {"u1": u1, "u2": u2, "f1": f1, "f2": f2},
    }


def predict_record(
    record: dict[str, Any],
    bundle: ModelBundle,
    *,
    include_deep: bool = False,
) -> dict[str, Any]:
    player1_id = player_model_id(bundle, record, "player1")
    player2_id = player_model_id(bundle, record, "player2")
    x1_norm = normalize_covariate(record["player1_covariate"], bundle.norm_params)
    x2_norm = normalize_covariate(record["player2_covariate"], bundle.norm_params)

    probabilities: dict[str, Any] = {}
    if bundle.pl_metrics is not None:
        probabilities["BT"] = linear_probability(
            bundle.pl_metrics, player1_id, player2_id, x1_norm, x2_norm, use_v=False
        )
    if bundle.plusdc_metrics is not None:
        probabilities["PlusDC"] = linear_probability(
            bundle.plusdc_metrics, player1_id, player2_id, x1_norm, x2_norm, use_v=True
        )
    if include_deep:
        probabilities["DHR"] = deep_probability(
            bundle, player1_id, player2_id, x1_norm, x2_norm
        )

    return {
        "match_key": record_key(record),
        "date": record.get("date"),
        "player1_name": record.get("player1_name"),
        "player2_name": record.get("player2_name"),
        "player1_model_id": player1_id,
        "player2_model_id": player2_id,
        "probabilities": probabilities,
    }


def predict_file(
    *,
    input_path: Path,
    output_path: Path,
    feature_name: str = "MI_PP_TS_dim66",
    training_run: Path | None = None,
    include_deep: bool = False,
    skip_unknown: bool = False,
    limit: int | None = None,
    target_date: date | None = None,
) -> dict[str, Any]:
    bundle = load_model_bundle(feature_name=feature_name, training_run=training_run)
    records = read_jsonl(input_path)
    if target_date is not None:
        records = filter_records_by_dates(records, {target_date})
    if limit is not None:
        records = records[:limit]

    predictions = []
    skipped = []
    for record in records:
        try:
            predictions.append(predict_record(record, bundle, include_deep=include_deep))
        except UnknownPlayerError as exc:
            if not skip_unknown:
                raise
            skipped.append({"match_key": record_key(record), "reason": str(exc)})

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "feature_name": feature_name,
        "training_run": str(bundle.training_run),
        "target_date": target_date.isoformat() if target_date else None,
        "include_deep": include_deep,
        "predictions": predictions,
        "skipped": skipped,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return payload
