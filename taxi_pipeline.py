"""DLT REST API source for NYC taxi data.

Base URL: https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api

This source fetches pages of JSON (up to `page_size` records per page)
and stops when an empty page is returned.

Usage example:
    from taxi_pipeline import nyc_taxi_source, taxi_pipeline
    src = nyc_taxi_source()
    info = taxi_pipeline.run(src)
    print(info)
"""

import dlt
import requests
from typing import Iterator, Dict, Any

BASE_URL = "https://us-central1-dlthub-analytics.cloudfunctions.net/data_engineering_zoomcamp_api"
PAGE_SIZE = 1000


@dlt.source
def nyc_taxi_source(base_url: str = BASE_URL, page_size: int = PAGE_SIZE):
    """DLT source that yields NYC taxi records from a paginated REST API.

    The API is queried with `page` and `per_page` query parameters. Pagination
    stops when an empty list/page is returned.
    """
    session = requests.Session()

    @dlt.resource(name="trips")
    def trips() -> Iterator[Dict[str, Any]]:
        page = 1
        while True:
            params = {"page": page, "per_page": page_size}
            resp = session.get(base_url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if not data:
                break
            for record in data:
                yield record
            page += 1

    return trips


# Named pipeline as requested
taxi_pipeline = dlt.pipeline(pipeline_name="taxi_pipeline")


if __name__ == "__main__":
    src = nyc_taxi_source()
    load_info = taxi_pipeline.run(src)
    print(load_info)
