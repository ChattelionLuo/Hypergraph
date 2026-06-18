from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Iterable


Record = dict[str, Any]


def read_jsonl(path: str | Path, *, missing_ok: bool = False) -> list[Record]:
    jsonl_path = Path(path)
    if not jsonl_path.exists():
        if missing_ok:
            return []
        raise FileNotFoundError(f"JSONL file not found: {jsonl_path}")

    records: list[Record] = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{jsonl_path}:{line_number} is not valid JSON: {exc}"
                ) from exc
            if not isinstance(obj, dict):
                raise ValueError(f"{jsonl_path}:{line_number} is not a JSON object")
            records.append(obj)
    return records


def write_jsonl(path: str | Path, records: Iterable[Record], *, append: bool = False) -> int:
    jsonl_path = Path(path)
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    count = 0
    with jsonl_path.open(mode, encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count


def sofa_match_id(href: str | None) -> str | None:
    if not href:
        return None
    match = re.search(r"#id:(\d+)", href)
    return match.group(1) if match else None


def record_key(record: Record) -> str:
    href = str(record.get("href", "") or "")
    match_id = sofa_match_id(href)
    if match_id:
        return f"sofascore:{match_id}"
    if href and href != "error":
        return f"href:{href}"

    players = (
        str(record.get("player1_name", "") or ""),
        str(record.get("player2_name", "") or ""),
        str(record.get("date", "") or record.get("Date and time", "") or ""),
    )
    if any(players):
        return "players:" + "|".join(players)

    return "json:" + json.dumps(record, sort_keys=True, ensure_ascii=False)


def dedupe_records(
    records: Iterable[Record],
    *,
    key_fn: Callable[[Record], str] = record_key,
) -> list[Record]:
    seen: set[str] = set()
    deduped: list[Record] = []
    for record in records:
        key = key_fn(record)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def parse_match_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    if value is None:
        raise ValueError("date value is missing")

    text = str(value).strip()
    for fmt in ("%d/%m/%y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"unsupported date format: {text!r}")


def filter_records_by_dates(
    records: Iterable[Record],
    target_dates: set[date],
    *,
    date_key: str = "date",
) -> list[Record]:
    filtered: list[Record] = []
    for record in records:
        try:
            record_date = parse_match_date(record.get(date_key))
        except ValueError:
            continue
        if record_date in target_dates:
            filtered.append(record)
    return filtered


def validate_required_keys(records: Iterable[Record], required_keys: Iterable[str]) -> None:
    keys = list(required_keys)
    for index, record in enumerate(records, start=1):
        missing = [key for key in keys if key not in record]
        if missing:
            raise ValueError(f"record {index} is missing required keys: {missing}")


def extract_player_links(records: Iterable[Record]) -> list[Record]:
    players: dict[str, str] = {}
    for record in records:
        for prefix in ("player1", "player2"):
            name = str(record.get(f"{prefix}_name", "") or "").strip()
            link = str(record.get(f"{prefix}_link", "") or "").strip()
            if name and link and link != "error":
                players[name] = link

    return [
        {"player_name": player_name, "player_link": player_link}
        for player_name, player_link in sorted(players.items())
    ]

