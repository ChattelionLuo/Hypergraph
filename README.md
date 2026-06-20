# Hypergraph ATP Prediction Pipeline

This project contains the research code and operational scaffold for daily ATP
tennis data collection, model training, probability prediction, and website
publication.

## Daily pipeline commands

Prepare daily SofaScore match links from the existing tournament/date index:

```powershell
python run_daily_pipeline.py prepare-crawl --date 2025-06-28 --conditions FT
```

Fetch match metadata through a browser-backed SofaScore JSON crawl:

```powershell
python run_daily_pipeline.py crawl-match-info-browser-api `
  --input .\data\daily\2025-06-28\date_links.jsonl `
  --output .\data\daily\2025-06-28\match_information_browser_api.jsonl `
  --error .\data\daily\2025-06-28\match_information_browser_api_error.jsonl
```

Generate model probabilities from saved BT/PL and PlusDC artifacts:

```powershell
python run_daily_pipeline.py predict `
  --input .\data\datasets_processed\MI_PP_TS_dim66\match_player_information_numerized_filled_engineered_vectorized.jsonl `
  --output .\data\daily\2025-06-28\predictions.json `
  --feature-name MI_PP_TS_dim66 `
  --date 2025-06-28 `
  --skip-unknown
```

Build the static website:

```powershell
python run_daily_pipeline.py build-site `
  --predictions .\data\daily\2025-06-28\predictions.json `
  --output-dir .\website
```

Preview training and metrics commands:

```powershell
python run_daily_pipeline.py train-models --feature-name MI_PP_TS_dim66 --sim-id 1 --dry-run
python run_daily_pipeline.py aggregate-metrics --rep-start 1 --rep-end 1 --feature-name MI_PP_TS_dim66 --dry-run
```

## Crawler configuration

The patched Selenium crawlers no longer contain embedded proxy credentials or
Linux-only Chrome paths. Use environment variables instead:

```powershell
$env:CHROME_BINARY = "C:\Path\To\chrome.exe"
$env:CHROMEDRIVER_PATH = "C:\Path\To\chromedriver.exe"
$env:SOFASCORE_PROXY_URL = "http://user:password@host:port"
```

Specific proxy slots are also supported:

```powershell
$env:SOFASCORE_PROXY1_URL = "http://user:password@host:port"
```

## Recovering live SofaScore access

If fresh headless sessions receive 403 responses, use a persistent, visible
Chrome profile. This lets you warm up a normal browser session and reuse its
cookies/session state for daily crawling.

```powershell
python run_daily_pipeline.py diagnose-live-access `
  --headful `
  --user-data-dir .\.browser_profiles\sofascore `
  --wait-seconds 60
```

If the visible browser shows a challenge or consent page, resolve it manually
during the wait window. Then retry the same command. Once `event`,
`statistics`, and/or `odds` checks are `ok: true`, run the crawler with the same
profile:

```powershell
python run_daily_pipeline.py crawl-match-info-browser-api `
  --headful `
  --user-data-dir .\.browser_profiles\sofascore `
  --input .\data\daily\2025-06-28\date_links.jsonl `
  --output .\data\daily\2025-06-28\match_information_browser_api.jsonl `
  --error .\data\daily\2025-06-28\match_information_browser_api_error.jsonl `
  --delay-seconds 10 `
  --page-wait-seconds 8
```

Use slow daily scheduling, persistent profiles, and explicit backoff rather than
creating many fresh headless sessions.

If ChromeDriver-created browsers are still blocked, attach to a normal Chrome
session that you start yourself:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --user-data-dir="$PWD\.browser_profiles\sofascore-manual"
```

Open SofaScore in that browser and confirm the site works normally. Then attach
the pipeline to it:

```powershell
python run_daily_pipeline.py diagnose-live-access --debugger-address 127.0.0.1:9222
python run_daily_pipeline.py crawl-match-info-browser-api `
  --debugger-address 127.0.0.1:9222 `
  --input .\data\daily\2025-06-28\date_links.jsonl `
  --output .\data\daily\2025-06-28\match_information_browser_api.jsonl `
  --error .\data\daily\2025-06-28\match_information_browser_api_error.jsonl
```

If your institution or data provider gives you an authorized proxy, pass it to
Chrome:

```powershell
python run_daily_pipeline.py diagnose-live-access --proxy-server http://host:port
```

## Notes

- Direct local requests to some SofaScore JSON endpoints may return 403. The
  browser-backed API crawler is the preferred daily mode because it first opens
  the match page and then reads JSON endpoints through the browser session.
- Deep/DHR prediction requires `torch` in the active Python environment. BT/PL
  and PlusDC probabilities work without Torch.
- `website\index.html` reads `website\data\latest_predictions.json` and can be
  served with any static file server.

## Flagship website

The GitHub Pages-ready flagship site lives in `docs/`:

- `docs/index.html` — presentation layer
- `docs/styles.css` and `docs/app.js` — website styling/interactions
- `docs/data/demo_predictions.json` — separated model prediction feed
- `docs/assets/` — research figures used by the site

Generate the demo feed from the held-out ATP test period:

```powershell
py -3.9 run_daily_pipeline.py build-demo-data --output .\docs\data\demo_predictions.json
```

Serve locally:

```powershell
python -m http.server 8000 --directory docs
```

For GitHub Pages, set the repository Pages source to `main` / `docs`.