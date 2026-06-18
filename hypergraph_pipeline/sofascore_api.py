from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .jsonl_utils import read_jsonl, sofa_match_id, write_jsonl


API_ROOT = "https://www.sofascore.com/api/v1"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class BrowserConfig:
    headless: bool = True
    user_data_dir: Path | None = None
    profile_directory: str | None = None
    disable_images: bool = True
    debugger_address: str | None = None
    proxy_server: str | None = None


def fetch_json(url: str, *, timeout: int = 30) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json,text/plain,*/*",
            "Referer": "https://www.sofascore.com/",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"SofaScore API returned HTTP {exc.code} for {url}") from exc
    return json.loads(payload)


def team_link(team: dict[str, Any]) -> str:
    return f"https://www.sofascore.com/team/tennis/{team.get('slug')}/{team.get('id')}"


def score_list(score: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for period in ("period1", "period2", "period3", "period4", "period5"):
        if period in score:
            values.append(str(score[period]))
    if "display" in score:
        values.append(str(score["display"]))
    return values


def fractional_to_decimal(value: str | None) -> str | None:
    if not value:
        return None
    if "/" not in value:
        return value
    numerator, denominator = value.split("/", 1)
    try:
        decimal_value = 1.0 + float(numerator) / float(denominator)
    except ValueError:
        return value
    return f"{decimal_value:.2f}"


def extract_full_time_odds(odds_payload: dict[str, Any] | None) -> tuple[str | None, str | None]:
    if not odds_payload:
        return None, None
    for market in odds_payload.get("markets", []):
        if market.get("marketName") != "Full time":
            continue
        home = None
        away = None
        for choice in market.get("choices", []):
            value = fractional_to_decimal(choice.get("fractionalValue"))
            if choice.get("name") == "1":
                home = value
            elif choice.get("name") == "2":
                away = value
        return home, away
    return None, None


def format_start_time(event: dict[str, Any]) -> str:
    timestamp = event.get("startTimestamp")
    if not timestamp:
        return ""
    dt = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
    return dt.strftime("%d/%m/%Y%H:%M")


def format_set_times(event: dict[str, Any]) -> list[str]:
    time_info = event.get("time", {})
    result = []
    for period, label in (("period1", "1st set"), ("period2", "2nd set"), ("period3", "3rd set")):
        seconds = time_info.get(period)
        if seconds:
            result.append(f"{label} {int(seconds) // 60}m")
    return result


def competition_label(event: dict[str, Any]) -> str:
    tournament = event.get("tournament", {})
    unique = tournament.get("uniqueTournament", {})
    points = unique.get("tennisPoints")
    if points:
        level = f"ATP {points}"
    else:
        level = tournament.get("category", {}).get("name", "ATP")
    tournament_name = tournament.get("name", "")
    round_name = event.get("roundInfo", {}).get("name", "")
    parts = ["Tennis", level, tournament_name, round_name]
    return ", ".join(str(part) for part in parts if part)


def add_statistics(record: dict[str, Any], stats_payload: dict[str, Any] | None) -> None:
    if not stats_payload:
        return
    all_period = next(
        (period for period in stats_payload.get("statistics", []) if period.get("period") == "ALL"),
        None,
    )
    if not all_period:
        return

    for group in all_period.get("groups", []):
        group_name = str(group.get("groupName", "")).strip()
        for item in group.get("statisticsItems", []):
            name = str(item.get("name", "")).strip()
            if group_name == "Games" and name == "Total won":
                name = "Total"
            if not group_name or not name:
                continue
            key = f"{group_name}_{name}"
            record[f"player1_{key}"] = item.get("home", "")
            record[f"player2_{key}"] = item.get("away", "")


def api_payload_to_match_record(
    source_record: dict[str, Any],
    event_payload: dict[str, Any],
    stats_payload: dict[str, Any] | None,
    odds_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    event = event_payload["event"]
    home = event["homeTeam"]
    away = event["awayTeam"]
    venue = event.get("venue", {})
    city = venue.get("city", {})
    country = city.get("country", {})
    home_odds, away_odds = extract_full_time_odds(odds_payload)

    record = {
        **source_record,
        "conditions": source_record.get("conditions") or event.get("status", {}).get("description"),
        "player1_link": team_link(home),
        "player2_link": team_link(away),
        "player1_name": home.get("shortName") or home.get("name"),
        "player2_name": away.get("shortName") or away.get("name"),
        "player1_conditions": event.get("homeTeamSeed"),
        "player2_conditions": event.get("awayTeamSeed"),
        "player1_score": score_list(event.get("homeScore", {})),
        "player2_score": score_list(event.get("awayScore", {})),
        "player1_odds": home_odds,
        "player2_odds": away_odds,
        "set_time": format_set_times(event),
        "Date and time": format_start_time(event),
        "Competition": competition_label(event),
        "Venue": venue.get("name", ""),
        "Location": ", ".join(
            str(part)
            for part in (city.get("name"), country.get("name"))
            if part
        ),
        "Ground type": event.get("groundType") or event.get("tournament", {}).get("uniqueTournament", {}).get("groundType"),
    }
    add_statistics(record, stats_payload)
    return record


def fetch_match_record(source_record: dict[str, Any]) -> dict[str, Any]:
    match_id = sofa_match_id(str(source_record.get("href", "") or ""))
    if not match_id:
        raise ValueError(f"cannot extract SofaScore event id from href: {source_record.get('href')!r}")

    event_payload = fetch_json(f"{API_ROOT}/event/{match_id}")
    try:
        stats_payload = fetch_json(f"{API_ROOT}/event/{match_id}/statistics")
    except RuntimeError:
        stats_payload = None
    try:
        odds_payload = fetch_json(f"{API_ROOT}/event/{match_id}/odds/1/all")
    except RuntimeError:
        odds_payload = None
    return api_payload_to_match_record(source_record, event_payload, stats_payload, odds_payload)


def crawl_match_information_api(
    *,
    input_path: Path,
    output_path: Path,
    error_path: Path,
    limit: int | None = None,
    delay_seconds: float = 0.0,
) -> dict[str, Any]:
    source_records = read_jsonl(input_path)
    if limit is not None:
        source_records = source_records[:limit]

    output_records: list[dict[str, Any]] = []
    error_records: list[dict[str, Any]] = []
    for record in source_records:
        try:
            output_records.append(fetch_match_record(record))
        except Exception as exc:
            error_record = dict(record)
            error_record["error"] = str(exc)
            error_records.append(error_record)
        if delay_seconds:
            time.sleep(delay_seconds)

    write_jsonl(output_path, output_records)
    write_jsonl(error_path, error_records)
    return {
        "input": str(input_path),
        "output": str(output_path),
        "error": str(error_path),
        "processed": len(source_records),
        "succeeded": len(output_records),
        "failed": len(error_records),
    }


def create_browser_driver(config: BrowserConfig | None = None):
    config = config or BrowserConfig()
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError as exc:
        raise RuntimeError(
            "Browser API crawling requires selenium and webdriver-manager."
        ) from exc

    import os

    options = Options()
    if config.headless:
        options.add_argument("--headless=new")
    if config.disable_images:
        options.add_argument("--disable-images")
    if config.debugger_address:
        options.debugger_address = config.debugger_address
    if config.user_data_dir is not None:
        user_data_dir = config.user_data_dir.resolve()
        user_data_dir.mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={user_data_dir}")
    if config.profile_directory:
        options.add_argument(f"--profile-directory={config.profile_directory}")
    proxy_server = config.proxy_server or os.environ.get("SOFASCORE_CHROME_PROXY_SERVER")
    if proxy_server:
        options.add_argument(f"--proxy-server={proxy_server}")
    chrome_binary = os.environ.get("CHROME_BINARY")
    if chrome_binary:
        options.binary_location = chrome_binary

    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
    service = (
        Service(executable_path=chromedriver_path)
        if chromedriver_path
        else Service(ChromeDriverManager().install())
    )
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(45)
    return driver


def browser_get_json(driver: Any, url: str) -> dict[str, Any]:
    script = """
        const path = arguments[0];
        const done = arguments[arguments.length - 1];
        fetch(path, {
            credentials: "include",
            headers: {"accept": "application/json,text/plain,*/*"}
        }).then(async (response) => {
            done({status: response.status, text: await response.text()});
        }).catch((error) => {
            done({status: 0, error: String(error)});
        });
    """
    result = driver.execute_async_script(script, url)
    if result.get("status") != 200:
        detail = result.get("error") or result.get("text")
        raise RuntimeError(f"SofaScore browser API error for {url}: {detail}")
    text = result["text"]
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"browser API response was not JSON for {url}: {text[:120]}") from exc
    if isinstance(payload, dict) and payload.get("error"):
        raise RuntimeError(f"SofaScore browser API error for {url}: {payload['error']}")
    return payload


def browser_navigate_json(driver: Any, url: str) -> dict[str, Any]:
    driver.get(url)
    text = driver.find_element("tag name", "body").text
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"browser API response was not JSON for {url}: {text[:120]}") from exc
    if isinstance(payload, dict) and payload.get("error"):
        raise RuntimeError(f"SofaScore browser API error for {url}: {payload['error']}")
    return payload


def fetch_match_record_browser(
    source_record: dict[str, Any],
    driver: Any,
    *,
    page_wait_seconds: float = 3.0,
) -> dict[str, Any]:
    match_id = sofa_match_id(str(source_record.get("href", "") or ""))
    if not match_id:
        raise ValueError(f"cannot extract SofaScore event id from href: {source_record.get('href')!r}")

    driver.get(str(source_record["href"]))
    if page_wait_seconds:
        time.sleep(page_wait_seconds)

    event_payload = browser_navigate_json(driver, f"{API_ROOT}/event/{match_id}")
    try:
        stats_payload = browser_navigate_json(driver, f"{API_ROOT}/event/{match_id}/statistics")
    except RuntimeError:
        stats_payload = None
    try:
        odds_payload = browser_navigate_json(driver, f"{API_ROOT}/event/{match_id}/odds/1/all")
    except RuntimeError:
        odds_payload = None
    return api_payload_to_match_record(source_record, event_payload, stats_payload, odds_payload)


def crawl_match_information_browser_api(
    *,
    input_path: Path,
    output_path: Path,
    error_path: Path,
    limit: int | None = None,
    delay_seconds: float = 0.0,
    page_wait_seconds: float = 3.0,
    browser_config: BrowserConfig | None = None,
) -> dict[str, Any]:
    source_records = read_jsonl(input_path)
    if limit is not None:
        source_records = source_records[:limit]

    output_records: list[dict[str, Any]] = []
    error_records: list[dict[str, Any]] = []
    driver = create_browser_driver(browser_config)
    try:
        for record in source_records:
            try:
                output_records.append(
                    fetch_match_record_browser(
                        record,
                        driver,
                        page_wait_seconds=page_wait_seconds,
                    )
                )
            except Exception as exc:
                error_record = dict(record)
                error_record["error"] = str(exc)
                error_records.append(error_record)
            if delay_seconds:
                time.sleep(delay_seconds)
    finally:
        driver.quit()

    write_jsonl(output_path, output_records)
    write_jsonl(error_path, error_records)
    return {
        "input": str(input_path),
        "output": str(output_path),
        "error": str(error_path),
        "processed": len(source_records),
        "succeeded": len(output_records),
        "failed": len(error_records),
        "mode": "browser-api",
    }


def diagnose_live_access(
    *,
    match_url: str,
    user_data_dir: Path | None = None,
    profile_directory: str | None = None,
    debugger_address: str | None = None,
    proxy_server: str | None = None,
    headless: bool = True,
    wait_seconds: float = 4.0,
) -> dict[str, Any]:
    match_id = sofa_match_id(match_url)
    if not match_id:
        raise ValueError(f"cannot extract SofaScore event id from {match_url!r}")

    config = BrowserConfig(
        headless=headless,
        user_data_dir=user_data_dir,
        profile_directory=profile_directory,
        debugger_address=debugger_address,
        proxy_server=proxy_server,
        disable_images=False,
    )
    driver = create_browser_driver(config)
    result: dict[str, Any] = {
        "match_url": match_url,
        "match_id": match_id,
        "headless": headless,
        "user_data_dir": str(user_data_dir) if user_data_dir else None,
        "profile_directory": profile_directory,
        "debugger_address": debugger_address,
        "proxy_server": proxy_server,
        "checks": {},
    }

    try:
        driver.get(match_url)
        if wait_seconds:
            time.sleep(wait_seconds)
        result["checks"]["match_page"] = {
            "url": driver.current_url,
            "title": driver.title,
            "source_length": len(driver.page_source),
            "looks_blocked": "Forbidden" in driver.page_source
            or "challenge" in driver.page_source.lower(),
        }

        for name, url in {
            "event": f"{API_ROOT}/event/{match_id}",
            "statistics": f"{API_ROOT}/event/{match_id}/statistics",
            "odds": f"{API_ROOT}/event/{match_id}/odds/1/all",
        }.items():
            try:
                payload = browser_navigate_json(driver, url)
                result["checks"][name] = {
                    "ok": True,
                    "top_level_keys": sorted(payload.keys()),
                }
            except Exception as exc:
                result["checks"][name] = {"ok": False, "error": str(exc)}
    finally:
        driver.quit()

    return result
