import logging
from google.cloud import bigquery

log = logging.getLogger(__name__)

SCHEMA = [
    bigquery.SchemaField("chapter_id",   "STRING",  mode="NULLABLE"),
    bigquery.SchemaField("chapter_name", "STRING",  mode="NULLABLE"),
    bigquery.SchemaField("city",         "STRING",  mode="NULLABLE"),
    bigquery.SchemaField("state",        "STRING",  mode="NULLABLE"),
    bigquery.SchemaField("longitude",    "FLOAT64", mode="NULLABLE"),
    bigquery.SchemaField("latitude",     "FLOAT64", mode="NULLABLE"),
]


def load_to_bigquery(rows: list[dict], project_id: str,dataset_id: str,table_id: str) -> None:
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    client.create_dataset(
        bigquery.Dataset(f"{project_id}.{dataset_id}"),
        exists_ok=True
    )

    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    job = client.load_table_from_json(rows,table_ref,job_config=job_config)
    job.result()
    log.info(f"Loaded {len(rows)} rows → {table_ref}")
