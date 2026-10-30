-- DuckDB CLI: duckdb < sql/analysis.sql
-- First run scripts/build_data.py with default raw/ directory.
CREATE OR REPLACE VIEW clean_trips AS
SELECT *, date_diff('second',tpep_pickup_datetime,tpep_dropoff_datetime)/60.0 AS minutes
FROM read_parquet('raw/yellow_tripdata_2025-01.parquet')
WHERE tpep_pickup_datetime >= TIMESTAMP '2025-01-01'
 AND tpep_pickup_datetime < TIMESTAMP '2025-02-01'
 AND date_diff('second',tpep_pickup_datetime,tpep_dropoff_datetime)/60.0 BETWEEN 1 AND 180
 AND trip_distance BETWEEN 0.1 AND 100
 AND total_amount BETWEEN 1 AND 500 AND fare_amount > 0
 AND PULocationID IN (SELECT LocationID FROM read_csv_auto('raw/taxi_zone_lookup.csv') WHERE Borough NOT IN ('Unknown','N/A') AND Zone IS NOT NULL)
 AND DOLocationID IN (SELECT LocationID FROM read_csv_auto('raw/taxi_zone_lookup.csv') WHERE Borough NOT IN ('Unknown','N/A') AND Zone IS NOT NULL);

-- Recorded demand, not unique riders or unmet requests.
SELECT hour(tpep_pickup_datetime) AS hour, count(*) AS pickups
FROM clean_trips GROUP BY 1 ORDER BY 1;

-- Historical route reference, not a fitted ML forecast.
SELECT PULocationID, DOLocationID, count(*) AS trips,
 median(total_amount) AS median_total_usd,
 quantile_cont(total_amount,0.25) AS fare_q25,
 quantile_cont(total_amount,0.75) AS fare_q75,
 median(minutes) AS median_minutes
FROM clean_trips GROUP BY 1,2 HAVING count(*) >= 30 ORDER BY trips DESC;
