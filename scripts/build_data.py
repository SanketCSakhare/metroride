"""Rebuild the public, aggregate-only MetroRide data snapshot."""
import argparse, hashlib, json, urllib.request
from pathlib import Path
import pandas as pd

SOURCE = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet'
ZONES = 'https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv'

def clean(df, known):
    df = df.copy()
    df['minutes'] = (df.tpep_dropoff_datetime-df.tpep_pickup_datetime).dt.total_seconds()/60
    valid = (df.tpep_pickup_datetime.ge('2025-01-01') & df.tpep_pickup_datetime.lt('2025-02-01')
             & df.minutes.between(1,180) & df.trip_distance.between(.1,100)
             & df.total_amount.between(1,500) & df.fare_amount.gt(0)
             & df.PULocationID.isin(known) & df.DOLocationID.isin(known))
    return df.loc[valid].copy()

def build(raw, output):
    raw.mkdir(parents=True, exist_ok=True)
    for name, url in [('yellow_tripdata_2025-01.parquet',SOURCE),('taxi_zone_lookup.csv',ZONES)]:
        if not (raw/name).exists(): urllib.request.urlretrieve(url,raw/name)
    zones = pd.read_csv(raw/'taxi_zone_lookup.csv').dropna(subset=['Zone','Borough'])
    zones = zones.loc[~zones.Borough.isin(['Unknown','N/A'])]
    source = raw/'yellow_tripdata_2025-01.parquet'
    columns=['tpep_pickup_datetime','tpep_dropoff_datetime','PULocationID','DOLocationID','trip_distance','total_amount','fare_amount']
    original = pd.read_parquet(source, columns=columns)
    df=clean(original, set(zones.LocationID))
    df['hour']=df.tpep_pickup_datetime.dt.hour
    df['weekday']=df.tpep_pickup_datetime.dt.dayofweek
    routes=df.groupby(['PULocationID','DOLocationID']).agg(n=('total_amount','size'),fare=('total_amount','median'),minutes=('minutes','median'),miles=('trip_distance','median'))
    qs=df.groupby(['PULocationID','DOLocationID']).total_amount.quantile([.25,.75]).unstack()
    routes['low']=qs[.25];routes['high']=qs[.75]
    routes=routes.loc[routes.n.ge(30)].reset_index().round(2)
    byzone=df.groupby('PULocationID').agg(n=('total_amount','size'),fare=('total_amount','median')).round(2)
    zone_records=[]
    for z in zones.itertuples():
        if z.LocationID in byzone.index:
            s=byzone.loc[z.LocationID]
            zone_records.append({'id':int(z.LocationID),'name':z.Zone,'borough':z.Borough,'n':int(s.n),'fare':float(s.fare)})
    payload={'meta':{'period':'January 2025','timezone':'America/New_York','source':SOURCE,'zone_source':ZONES,'source_page':'https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'raw_rows':len(original),'valid_rows':len(df),'excluded_rows':len(original)-len(df),'route_minimum':30,'retained_routes':len(routes),'currency':'USD','median_fare':round(float(df.total_amount.median()),2),'median_minutes':round(float(df.minutes.median()),2),'median_miles':round(float(df.trip_distance.median()),2),'total_charged':round(float(df.total_amount.sum()),2)},'zones':zone_records,'routes':[{'pu':int(r.PULocationID),'do':int(r.DOLocationID),'n':int(r.n),'fare':float(r.fare),'low':float(r.low),'high':float(r.high),'minutes':float(r.minutes),'miles':float(r.miles)} for r in routes.itertuples()], 'hourly':[int(x) for x in df.groupby('hour').size().reindex(range(24),fill_value=0)],'heatmap':[[int(x) for x in df.loc[df.weekday.eq(d)].groupby('hour').size().reindex(range(24),fill_value=0)] for d in range(7)],'daily':[{'date':str(d),'n':int(n)} for d,n in df.groupby(df.tpep_pickup_datetime.dt.date).size().items()]}
    output.mkdir(parents=True,exist_ok=True)
    (output/'data.json').write_text(json.dumps(payload,separators=(',',':')))
    df.groupby(['PULocationID','DOLocationID']).size().rename('trips').reset_index().to_csv(output/'route_counts.csv',index=False)
    print(json.dumps(payload['meta'],indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raw-dir',type=Path,default=Path('raw'));p.add_argument('--output',type=Path,default=Path('dist'));a=p.parse_args();build(a.raw_dir,a.output)
