from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .jsonl_utils import (
    dedupe_records,
    extract_player_links,
    filter_records_by_dates,
    read_jsonl,
    record_key,
    write_jsonl,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DailyCrawlerSummary:
    target_date: str
    output_dir: str
    source_links: str
    date_links: str
    new_match_links: str
    match_information: str
    player_links: str
    total_links_for_date: int
    new_links_to_crawl: int
    existing_match_records: int

    def as_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


def default_daily_dir(target_date: date) -> Path:
    return PROJECT_ROOT / "data" / "daily" / target_date.isoformat()


def prepare_daily_crawl(
    *,
    target_date: date,
    include_previous_day: bool = False,
    source_date_links: Path | None = None,
    historical_match_information: Path | None = None,
    output_dir: Path | None = None,
    conditions: set[str] | None = None,
) -> DailyCrawlerSummary:
    source_date_links = source_date_links or (
        PROJECT_ROOT / "sofascore_crawler" / "all_ATP_competition_year_date_links.jsonl"
    )
    historical_match_information = historical_match_information or (
        PROJECT_ROOT
        / "sofascore_crawler"
        / "data"
        / "match"
        / "final_all_2016_2025_match_information.jsonl"
    )
    output_dir = output_dir or default_daily_dir(target_date)
    output_dir.mkdir(parents=True, exist_ok=True)

    target_dates = {target_date}
    if include_previous_day:
        target_dates.add(target_date - timedelta(days=1))

    all_links = read_jsonl(source_date_links)
    day_links = filter_records_by_dates(all_links, target_dates)
    if conditions is not None:
        day_links = [
            record
            for record in day_links
            if str(record.get("conditions", "") or "") in conditions
        ]
    day_links = dedupe_records(day_links)

    historical_records = read_jsonl(historical_match_information, missing_ok=True)
    seen_match_keys = {record_key(record) for record in historical_records}
    new_links = [
        record
        for record in day_links
        if record_key(record) not in seen_match_keys
        and record.get("href")
        and record.get("href") != "error"
    ]

    date_links_path = output_dir / "date_links.jsonl"
    new_links_path = output_dir / "new_match_links.jsonl"
    match_information_path = output_dir / "match_information.jsonl"
    player_links_path = output_dir / "player_links.jsonl"

    write_jsonl(date_links_path, day_links)
    write_jsonl(new_links_path, new_links)

    existing_daily_match_records = read_jsonl(match_information_path, missing_ok=True)
    player_links = extract_player_links([*historical_records, *existing_daily_match_records])
    write_jsonl(player_links_path, player_links)

    summary = DailyCrawlerSummary(
        target_date=target_date.isoformat(),
        output_dir=str(output_dir),
        source_links=str(source_date_links),
        date_links=str(date_links_path),
        new_match_links=str(new_links_path),
        match_information=str(match_information_path),
        player_links=str(player_links_path),
        total_links_for_date=len(day_links),
        new_links_to_crawl=len(new_links),
        existing_match_records=len(historical_records),
    )
    (output_dir / "crawler_summary.json").write_text(
        json.dumps(summary.as_dict(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def run_match_information_crawler(
    *,
    input_path: Path,
    output_path: Path,
    error_path: Path,
    driver_type: str = "local",
    stealth_level: str = "minimal",
    python_executable: str | None = None,
) -> subprocess.CompletedProcess[str]:
    crawler_script = (
        PROJECT_ROOT
        / "sofascore_crawler"
        / "sofascore_selenium_step4_get_match_information_V5.py"
    )
    cmd = [
        python_executable or sys.executable,
        str(crawler_script),
        "--input",
        str(input_path),
        "--output",
        str(output_path),
        "--error",
        str(error_path),
        "--driver_type",
        driver_type,
        "--stealth_level",
        stealth_level,
    ]
    return subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT / "sofascore_crawler"),
        check=True,
        text=True,
    )

