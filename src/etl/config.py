"""Centralised config — loaded once from environment variables."""
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    project_id: str = os.environ["GCP_PROJECT_ID"]
    raw_dataset: str = os.environ["BQ_RAW_DATASET"]
    raw_table: str = os.environ["BQ_RAW_TABLE"]
    api_url: str = os.environ["DUCKS_API_URL"]


settings = Settings()
