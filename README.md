# MetroRide — Open-data mobility lab

A ride-hailing portfolio project by **Sanket Sakhare**. Explore demand, compare historical route fares and save simulated ride requests, using real New York City taxi records.

**[Open the app](https://metroride-sanket.kindape14.chatgpt.site)** · The hosted app is owner-private. Anyone with the source can run it locally.

## Business problem

A mobility analyst needs to understand where recorded trips start, when pickups concentrate, and what customers historically paid for a particular route. MetroRide connects these questions to a working customer-facing trip planner.

Uber is a ride-hailing platform; self-drive rentals are a different business. This project implements a taxi-backed ride-hailing prototype, not rental inventory management or an Uber production clone.

## What works

- Hourly pickup chart, busiest pickup zones and weekday/hour heatmap.
- Directed zone-to-zone fare lookup: median, observed interquartile range, median journey time and distance, plus the supporting trip count.
- Evidence threshold of 30 trips; unsupported routes return an explicit empty state.
- Pickup/destination swapping, local demo trip storage, restore and removal.
- Source and methodology view with exclusions and downloadable route-count CSV.
- Responsive interface, labelled inputs, keyboard focus and accessible chart descriptions.
- Reproducible Python pipeline, SQL equivalents and automated validation.

## Actual dataset results

January 2025, NYC TLC yellow taxis, pickup timestamps in New York local time:

| Measure | Value |
|---|---:|
| Original trip records | 3,475,226 |
| Retained trips | 3,206,120 |
| Excluded records | 269,106 |
| Supported directed routes (30+ trips) | 4,980 |
| Median recorded total fare | $20.35 |
| Median duration | 11.68 minutes |
| Median distance | 1.70 miles |
| Busiest pickup hour | 18:00–18:59, 230,908 trips |
| Busiest pickup zone | Midtown Center, 159,905 trips |

**Example:** Midtown Center → JFK Airport has 1,451 qualifying trips, a median total of $97.13 and a $86.69–$98.03 interquartile range. These are recorded taxi totals, not Uber quotes.

The evening pickup concentration is a useful starting point for a staffing investigation. It cannot establish a driver shortage: supply, rejected requests and waiting times are not in this dataset. Compare supply with recorded demand before making fleet allocation decisions.

## Source and data terms

- [NYC TLC official trip data portal](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)
- [January 2025 yellow taxi Parquet](https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet)
- [Official taxi zone lookup](https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv)
- [NYC Open Data terms of use](https://opendata.cityofnewyork.us/overview/#termsofuse)

This is publicly available government data. Original dataset rights and terms remain with the provider; no software licence is asserted over TLC records. TLC warns that vendor submissions may be inaccurate or incomplete. Raw trip records are downloaded on demand and are excluded from Git; the app ships aggregate outputs only.

Source file SHA-256: `9af277e4c0d3f9deb30644da822981e1e7df6af58313170fd3aa8a474485488a`.

## Reproduce

Python 3.10+ and Node.js 18+ are sufficient. No paid API or API key is required.

```bash
git clone https://github.com/SanketCSakhare/metroride.git
cd metroride
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build_data.py
python -m http.server 8000 --directory dist
```

Open `http://localhost:8000`. Opening `index.html` directly with `file://` will not load JSON in browsers. The pipeline downloads approximately 59 MB and processes the full month; it does not sample rows. Optional arguments: `--raw-dir /path/to/raw --output /path/to/dist`.

Optional DuckDB SQL:

```bash
duckdb < sql/analysis.sql
```

## Cleaning and definitions

One row is one vendor-reported trip. Retain a row only when all conditions hold:

1. Pickup is on/after 1 January and before 1 February 2025.
2. Duration is between 1 and 180 minutes, inclusive.
3. Distance is between 0.1 and 100 miles, inclusive.
4. Total amount is $1–$500, inclusive, with a positive base fare.
5. Both zone IDs join to the official lookup with a known zone and borough label (including the EWR label).

A failing row is counted once in total exclusions. These are project plausibility rules, not TLC validation standards. They intentionally exclude short, long, free, refunded or unknown-location trips and therefore change population coverage. No unique trip identifier exists: identical rows are retained rather than silently treating them as duplicate submissions.

Route statistics pool the month and are directional. Fare is `total_amount`, which includes recorded extras, tolls, taxes and tips; cash tips generally are not recorded. The 25th–75th percentile range is observed variation, not a confidence or prediction interval. Trip time, fare and mileage medians are computed separately.

Hourly counts and zone ranks represent recorded activity, not latent demand, unique customers or fleet utilisation. The heatmap sums all occurrences of each weekday; January has unequal weekday counts. No GPS map, current quote, future forecast or causal claim is provided. January 2025 is fixed for reproducibility, not presented as the latest available data.

## Validation

```bash
node --check dist/app.js
node --test tests/core.test.js
python -m unittest discover -s tests -p 'test_*.py'
```

Tests check directed route lookup, insufficient evidence, corrupt saved data, local persistence and storage failures; snapshot totals reconcile across hourly, weekday/hour, daily and zone aggregates; route percentiles, sample sizes and date coverage are checked. Browser checks cover the rendered overview, supported fare lookup and local save/remove flow. No unexecuted production claim is implied.

## Architecture

```text
Official Parquet + zone CSV -> pandas cleaning/aggregation
                            -> data.json + route_counts.csv
                            -> HTML/CSS/JavaScript browser app
                            -> localStorage (simulated trips only)
```

`dist/` is the complete deployable static app. `scripts/` contains data preparation, `sql/` equivalent business queries and `tests/` validation. The app needs no JavaScript build step. Google Fonts is optional; system fallback fonts work without it.

## Boundaries and next steps

Bookings are simulations stored in this browser. There is no dispatch, payment, authentication or backend order store. Data is taxi data, not private Uber data. A production extension would require a serviceable-zone model, verified current fare logic, actual vehicle supply, a transactional booking backend, location privacy controls and operating permissions. Predictive modelling would need a time-separated holdout and honest error reporting; no ML accuracy is invented here.
