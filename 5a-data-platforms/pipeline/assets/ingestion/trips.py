"""@bruin
name: ingestion.trips
type: python
image: python:3.11
connection: duckdb-default

materialization:
  type: table
  strategy: append

columns:
  - name: pickup_datetime
    type: timestamp
    description: "When the meter was engaged"
  - name: dropoff_datetime
    type: timestamp
    description: "When the meter was disengaged"
@bruin"""

import os
import json
import urllib.request  # <--- Added this
from datetime import datetime
import pandas as pd
import io              # <--- Added this to handle the byte stream

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"


def _parse_date(s):
    return datetime.strptime(s[:10], "%Y-%m-%d").date()


def _month_range(start_date, end_date):
    start = _parse_date(start_date)
    end = _parse_date(end_date)
    months = []
    y, m = start.year, start.month
    ey, em = end.year, end.month
    while (y, m) <= (ey, em):
        months.append((y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return months


def _read_parquet(url):
    # This header makes the request look like it's coming from a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # We wrap the request in a Request object to include the headers
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req) as response:
        # Read the bytes and pass them to pandas
        return pd.read_parquet(io.BytesIO(response.read()))


def _normalize_columns(df, taxi_type):
    rename = {}
    if "tpep_pickup_datetime" in df.columns:
        rename["tpep_pickup_datetime"] = "pickup_datetime"
        rename["tpep_dropoff_datetime"] = "dropoff_datetime"
    elif "lpep_pickup_datetime" in df.columns:
        rename["lpep_pickup_datetime"] = "pickup_datetime"
        rename["lpep_dropoff_datetime"] = "dropoff_datetime"
    if "PULocationID" in df.columns:
        rename["PULocationID"] = "pickup_location_id"
    if "DOLocationID" in df.columns:
        rename["DOLocationID"] = "dropoff_location_id"
    df = df.rename(columns=rename)
    df["taxi_type"] = taxi_type
    return df


def materialize():
    start_date = os.environ["BRUIN_START_DATE"]
    end_date = os.environ["BRUIN_END_DATE"]
    
    try:
        vars_env = os.environ.get("BRUIN_VARS", "{}")
        taxi_types = json.loads(vars_env).get("taxi_types", ["yellow"])
    except:
        taxi_types = ["yellow"]

    needed = [
        "pickup_datetime",
        "dropoff_datetime",
        "pickup_location_id",
        "dropoff_location_id",
        "fare_amount",
        "payment_type",
        "taxi_type",
    ]
    frames = []

    for year, month in _month_range(start_date, end_date):
        for taxi_type in taxi_types:
            url = f"{BASE_URL}/{taxi_type}_tripdata_{year}-{month:02d}.parquet"
            try:
                print(f"Attempting to fetch: {url}")
                df = _read_parquet(url)
                df = _normalize_columns(df, taxi_type)
                df = df[[c for c in needed if c in df.columns]]
                frames.append(df)
                print(f"Successfully fetched: {url}")
            except Exception as e:
                # INSTEAD OF RAISING: We log the error and keep going
                print(f"WARNING: Skipping {url} due to error: {e}")
                continue 

    if not frames:
        print("No data was fetched for the given range.")
        return pd.DataFrame(columns=needed)

    return pd.concat(frames, ignore_index=True)