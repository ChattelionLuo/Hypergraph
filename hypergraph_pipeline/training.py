from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class TrainingConfig:
    feature_name: str = "MI_PP_TS_dim66"
    sim_id: int = 1
    history_num: int = 3
    bad_player_bound: int = 1
    lr: float = 0.001
    batch_size: int = 32
    dropout_p: float = 0.0
    hidden_num: int = 3
    hidden_dim: int = 16
    weight_decay: float = 0.0001

    def training_run_dir(self) -> Path:
        return (
            PROJECT_ROOT
            / "training_results"
            / self.feature_name
            / f"history_num_{self.history_num}_bad_player_bound{self.bad_player_bound}"
            / f"rep{self.sim_id}"
        )


def build_training_command(
    config: TrainingConfig,
    *,
    python_executable: str | None = None,
) -> list[str]:
    return [
        python_executable or sys.executable,
        str(PROJECT_ROOT / "main_train_realdata.py"),
        "--sim_id",
        str(config.sim_id),
        "--lr",
        str(config.lr),
        "--bs",
        str(config.batch_size),
        "--dropout_p",
        str(config.dropout_p),
        "--hidden_num",
        str(config.hidden_num),
        "--hidden_dim",
        str(config.hidden_dim),
        "--history_num",
        str(config.history_num),
        "--bad_player_bound",
        str(config.bad_player_bound),
        "--feature_name",
        config.feature_name,
        "--weight_decay",
        str(config.weight_decay),
    ]


def run_training(
    config: TrainingConfig,
    *,
    python_executable: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    command = build_training_command(config, python_executable=python_executable)
    payload = {
        "command": command,
        "training_run": str(config.training_run_dir()),
        "dry_run": dry_run,
    }
    if dry_run:
        return payload
    subprocess.run(command, cwd=str(PROJECT_ROOT), check=True, text=True)
    return payload


def build_metrics_command(
    *,
    rep_start: int = 1,
    rep_end: int = 30,
    feature_name: str = "ALL",
    python_executable: str | None = None,
) -> list[str]:
    return [
        python_executable or sys.executable,
        str(PROJECT_ROOT / "main_optimal_metrics.py"),
        "--rep_start",
        str(rep_start),
        "--rep_end",
        str(rep_end),
        "--feature_name",
        feature_name,
    ]


def run_metrics(
    *,
    rep_start: int = 1,
    rep_end: int = 30,
    feature_name: str = "ALL",
    python_executable: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    command = build_metrics_command(
        rep_start=rep_start,
        rep_end=rep_end,
        feature_name=feature_name,
        python_executable=python_executable,
    )
    payload = {"command": command, "dry_run": dry_run}
    if dry_run:
        return payload
    subprocess.run(command, cwd=str(PROJECT_ROOT), check=True, text=True)
    return payload

