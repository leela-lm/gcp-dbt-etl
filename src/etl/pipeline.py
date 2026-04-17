import logging
import sys
from .config import settings
from .extract  import fetch_chapters
from .transform import transform_chapters
from .load import load_to_bigquery

log = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s"
)


def run():
    try:
       log.info("Starting ETL pipeline")

       # 1.Extract
       raw_data = fetch_chapters(settings.api_url)
       log.info("Extract step completed")


       # 2. Transform
       clean_data = transform_chapters(raw_data)

       # 3. Load
       load_to_bigquery(
           rows=clean_data,
           project_id=settings.project_id,
           dataset_id=settings.raw_dataset,
           table_id=settings.raw_table,
       )

       log.info("ETL pipeline finished successfully")

    except Exception as e:
        log.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    run()
