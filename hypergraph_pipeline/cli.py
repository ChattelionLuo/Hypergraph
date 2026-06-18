from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .crawler import prepare_daily_crawl, run_match_information_crawler
from .jsonl_utils import extract_player_links, read_jsonl, write_jsonl
from .predict import predict_file
from .site import build_static_site
from .sofascore_api import (
    BrowserConfig,
    crawl_match_information_api,
    crawl_match_information_browser_api,
    diagnose_live_access,
)
from .training import TrainingConfig, run_metrics, run_training


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hypergraph daily ATP pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare-crawl", help="Prepare daily crawl inputs")
    prepare.add_argument("--date", type=parse_date, default=date.today())
    prepare.add_argument("--include-previous-day", action="store_true")
    prepare.add_argument("--source-date-links", type=Path)
    prepare.add_argument("--historical-match-information", type=Path)
    prepare.add_argument("--output-dir", type=Path)
    prepare.add_argument(
        "--conditions",
        nargs="*",
        help="Optional SofaScore conditions to keep, for example FT or NS.",
    )

    crawl = subparsers.add_parser("crawl-match-info", help="Run Selenium match crawler")
    crawl.add_argument("--input", type=Path, required=True)
    crawl.add_argument("--output", type=Path, required=True)
    crawl.add_argument("--error", type=Path, required=True)
    crawl.add_argument("--driver-type", default="local")
    crawl.add_argument("--stealth-level", default="minimal")

    crawl_api = subparsers.add_parser(
        "crawl-match-info-api",
        help="Fetch match information through SofaScore JSON endpoints",
    )
    crawl_api.add_argument("--input", type=Path, required=True)
    crawl_api.add_argument("--output", type=Path, required=True)
    crawl_api.add_argument("--error", type=Path, required=True)
    crawl_api.add_argument("--limit", type=int)
    crawl_api.add_argument("--delay-seconds", type=float, default=0.0)

    crawl_browser_api = subparsers.add_parser(
        "crawl-match-info-browser-api",
        help="Fetch SofaScore JSON endpoints through a browser session",
    )
    crawl_browser_api.add_argument("--input", type=Path, required=True)
    crawl_browser_api.add_argument("--output", type=Path, required=True)
    crawl_browser_api.add_argument("--error", type=Path, required=True)
    crawl_browser_api.add_argument("--limit", type=int)
    crawl_browser_api.add_argument("--delay-seconds", type=float, default=0.0)
    crawl_browser_api.add_argument("--page-wait-seconds", type=float, default=3.0)
    crawl_browser_api.add_argument("--user-data-dir", type=Path)
    crawl_browser_api.add_argument("--profile-directory")
    crawl_browser_api.add_argument("--debugger-address")
    crawl_browser_api.add_argument("--proxy-server")
    crawl_browser_api.add_argument("--headful", action="store_true")
    crawl_browser_api.add_argument("--load-images", action="store_true")

    diagnose = subparsers.add_parser(
        "diagnose-live-access",
        help="Check SofaScore page/API access with the configured browser session",
    )
    diagnose.add_argument(
        "--match-url",
        default="https://www.sofascore.com/tennis/match/wsf2-wsf1/RvebsyMBb#id:14023146",
    )
    diagnose.add_argument("--user-data-dir", type=Path)
    diagnose.add_argument("--profile-directory")
    diagnose.add_argument("--debugger-address")
    diagnose.add_argument("--proxy-server")
    diagnose.add_argument("--headful", action="store_true")
    diagnose.add_argument("--wait-seconds", type=float, default=4.0)

    players = subparsers.add_parser("extract-players", help="Extract player links")
    players.add_argument("--input", type=Path, required=True)
    players.add_argument("--output", type=Path, required=True)

    predict = subparsers.add_parser("predict", help="Generate model probabilities")
    predict.add_argument("--input", type=Path, required=True)
    predict.add_argument("--output", type=Path, required=True)
    predict.add_argument("--feature-name", default="MI_PP_TS_dim66")
    predict.add_argument("--training-run", type=Path)
    predict.add_argument("--include-deep", action="store_true")
    predict.add_argument("--skip-unknown", action="store_true")
    predict.add_argument("--limit", type=int)
    predict.add_argument("--date", type=parse_date)

    site = subparsers.add_parser("build-site", help="Build static website")
    site.add_argument("--predictions", type=Path, required=True)
    site.add_argument("--output-dir", type=Path)

    train = subparsers.add_parser("train-models", help="Run or print model training")
    train.add_argument("--feature-name", default="MI_PP_TS_dim66")
    train.add_argument("--sim-id", type=int, default=1)
    train.add_argument("--history-num", type=int, default=3)
    train.add_argument("--bad-player-bound", type=int, default=1)
    train.add_argument("--lr", type=float, default=0.001)
    train.add_argument("--bs", type=int, default=32)
    train.add_argument("--dropout-p", type=float, default=0.0)
    train.add_argument("--hidden-num", type=int, default=3)
    train.add_argument("--hidden-dim", type=int, default=16)
    train.add_argument("--weight-decay", type=float, default=0.0001)
    train.add_argument("--dry-run", action="store_true")

    metrics = subparsers.add_parser("aggregate-metrics", help="Run or print metrics aggregation")
    metrics.add_argument("--rep-start", type=int, default=1)
    metrics.add_argument("--rep-end", type=int, default=30)
    metrics.add_argument("--feature-name", default="ALL")
    metrics.add_argument("--dry-run", action="store_true")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "prepare-crawl":
        summary = prepare_daily_crawl(
            target_date=args.date,
            include_previous_day=args.include_previous_day,
            source_date_links=args.source_date_links,
            historical_match_information=args.historical_match_information,
            output_dir=args.output_dir,
            conditions=set(args.conditions) if args.conditions else None,
        )
        print(json.dumps(summary.as_dict(), indent=2, ensure_ascii=False))
    elif args.command == "crawl-match-info":
        run_match_information_crawler(
            input_path=args.input,
            output_path=args.output,
            error_path=args.error,
            driver_type=args.driver_type,
            stealth_level=args.stealth_level,
        )
    elif args.command == "crawl-match-info-api":
        summary = crawl_match_information_api(
            input_path=args.input,
            output_path=args.output,
            error_path=args.error,
            limit=args.limit,
            delay_seconds=args.delay_seconds,
        )
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    elif args.command == "crawl-match-info-browser-api":
        summary = crawl_match_information_browser_api(
            input_path=args.input,
            output_path=args.output,
            error_path=args.error,
            limit=args.limit,
            delay_seconds=args.delay_seconds,
            page_wait_seconds=args.page_wait_seconds,
            browser_config=BrowserConfig(
                headless=not args.headful,
                user_data_dir=args.user_data_dir,
                profile_directory=args.profile_directory,
                debugger_address=args.debugger_address,
                proxy_server=args.proxy_server,
                disable_images=not args.load_images,
            ),
        )
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    elif args.command == "diagnose-live-access":
        result = diagnose_live_access(
            match_url=args.match_url,
            user_data_dir=args.user_data_dir,
            profile_directory=args.profile_directory,
            debugger_address=args.debugger_address,
            proxy_server=args.proxy_server,
            headless=not args.headful,
            wait_seconds=args.wait_seconds,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.command == "extract-players":
        records = read_jsonl(args.input)
        count = write_jsonl(args.output, extract_player_links(records))
        print(json.dumps({"output": str(args.output), "players": count}, indent=2))
    elif args.command == "predict":
        payload = predict_file(
            input_path=args.input,
            output_path=args.output,
            feature_name=args.feature_name,
            training_run=args.training_run,
            include_deep=args.include_deep,
            skip_unknown=args.skip_unknown,
            limit=args.limit,
            target_date=args.date,
        )
        print(
            json.dumps(
                {
                    "output": str(args.output),
                    "predictions": len(payload["predictions"]),
                    "skipped": len(payload["skipped"]),
                },
                indent=2,
            )
        )
    elif args.command == "build-site":
        status = build_static_site(
            predictions_path=args.predictions,
            output_dir=args.output_dir,
        )
        print(json.dumps(status, indent=2, ensure_ascii=False))
    elif args.command == "train-models":
        payload = run_training(
            TrainingConfig(
                feature_name=args.feature_name,
                sim_id=args.sim_id,
                history_num=args.history_num,
                bad_player_bound=args.bad_player_bound,
                lr=args.lr,
                batch_size=args.bs,
                dropout_p=args.dropout_p,
                hidden_num=args.hidden_num,
                hidden_dim=args.hidden_dim,
                weight_decay=args.weight_decay,
            ),
            dry_run=args.dry_run,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    elif args.command == "aggregate-metrics":
        payload = run_metrics(
            rep_start=args.rep_start,
            rep_end=args.rep_end,
            feature_name=args.feature_name,
            dry_run=args.dry_run,
        )
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        parser.error(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
