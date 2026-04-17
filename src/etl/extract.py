"""Extract: pull raw JSON from the DUCKS ArcGIS API."""
import logging
import requests

log = logging.getLogger(__name__)

# API_URL = (
#    "https://services2.arcgis.com/5I7u4SJE1vUr79JC/arcgis/rest/services"
#    "/UniversityChapters_Public/FeatureServer/0/query"
# )

PARAMS = {
    "where":     "1=1",
    "outFields": "*",
    "outSR":     "4326",
    "f":         "json",
}


def fetch_chapters(API_URL: str) -> list[dict]:
    """Fetch all DU university chapters from the ArcGIS FeatureServer."""
    log.info("Requesting DUCKS API…")
    response = requests.get(API_URL, params=PARAMS, timeout=15)
    response.raise_for_status()  # raises an error if the request failed

    data = response.json()

    if "error" in data:
        raise ValueError(f"API returned an error: {data['error']}")

    features = data.get("features", [])
    log.info(f"Fetched {len(features)} chapters")
    return features
