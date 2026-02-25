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
from datetime import datetime
import pandas as pd

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
    return pd.read_parquet(url)


def _normalize_columns(df, taxi_type):
    # Yellow: tpep_pickup_datetime, tpep_dropoff_datetime, PULocationID, DOLocationID
    # Green:  lpep_pickup_datetime, lpep_dropoff_datetime, PULocationID, DOLocationID
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
    taxi_types = json.loads(os.environ["BRUIN_VARS"]).get("taxi_types", ["yellow"])

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
                df = _read_parquet(url)
                df = _normalize_columns(df, taxi_type)
                df = df[[c for c in needed if c in df.columns]]
                frames.append(df)
            except Exception as e:
                raise RuntimeError(f"Failed to fetch {url}: {e}") from e

    if not frames:
        return pd.DataFrame(columns=needed)

    final_dataframe = pd.concat(frames, ignore_index=True)

    # Return datetime columns as ISO strings so ingestr/PyArrow never see a timestamp type
    # (avoids "Timezone database not found" on Windows when ingestr normalizes the payload).
    for col in ("pickup_datetime", "dropoff_datetime"):
        if col not in final_dataframe.columns:
            continue
        ser = final_dataframe[col]
        if hasattr(ser.dtype, "tz") and ser.dtype.tz is not None:
            ser = pd.to_datetime(ser.astype("int64"), unit="ns")
        final_dataframe[col] = pd.to_datetime(ser).dt.strftime("%Y-%m-%d %H:%M:%S").astype(str)
    return final_dataframe