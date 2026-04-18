# Ducks Unlimited University Chapters ETL Pipeline

A simple ETL pipeline that extracts university chapter data from the Ducks Unlimited
ArcGIS API, transforms and cleans the data, loads it into Google BigQuery, and models
it using dbt.

---

## Architecture

DU ArcGIS API → Extract → Transform → Load → BigQuery (raw) → dbt → BigQuery (analytics)

### Flow

1. **Extract** — fetches all university chapters from the DU ArcGIS FeatureServer API
2. **Transform** — cleans whitespace, normalises ChapterID format
3. **Load** — loads cleaned data into BigQuery raw dataset
4. **dbt staging** — casts types and filters duplicates
5. **dbt mart** — creates the final analytics table

---

## Project Structure

gcp-dbt-etl/
├── src/
│ └── etl/
│ ├── init.py
│ ├── config.py # environment variable configuration
│ ├── extract.py # fetches data from DU API
│ ├── transform.py # cleans and validates records
│ ├── load.py # loads data into BigQuery
│ └── pipeline.py # orchestrates extract, transform, load
├── dbt_gcp_project/
│ ├── dbt_project.yml
│ ├── profiles.yml
│ ├── models/
│ │ ├── sources.yml
│ │ ├── staging/
│ │ │ └── stg_ducks_chapters.sql
│ │ └── marts/
│ │ └── university_chapters.sql
│ └── macros/
│ └── generate_schema_name.sql
├── tests/
│ └── test_transform.py
├── .github/
│ └── workflows/
│ └── ci.yml
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md

---

## Dataset

**Source:** Ducks Unlimited ArcGIS FeatureServer
**URL:** `https://services2.arcgis.com/5I7u4SJE1vUr79JC/arcgis/rest/services/UniversityChapters_Public/FeatureServer/0/query`

### Fields extracted

| Field          | Description                              |
| -------------- | ---------------------------------------- |
| `chapter_id`   | Unique chapter identifier e.g. `FL-0110` |
| `chapter_name` | Name of the university chapter           |
| `city`         | City where the chapter is located        |
| `state`        | US state abbreviation e.g. `FL`          |
| `longitude`    | Longitude coordinate                     |
| `latitude`     | Latitude coordinate                      |

---

## Prerequisites

- Python 3.10+
- Google Cloud account (free tier)
- A GCP project with BigQuery API enabled
- A GCP service account key file with BigQuery Data Editor and BigQuery User role

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/leela-lm/gcp-dbt-etl.git
cd gcp-dbt-etl
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up Google Cloud

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project
3. Enable the BigQuery API
4. Go to **IAM & Admin → Service Accounts → Create Service Account**
5. Assign the **BigQuery Data Editor and Bigquery user** role
6. Click **Keys → Add Key → JSON** and download the file
7. Save the file in your project root under keys folder(it is already in `.gitignore`)

### 5. Configure environment variables

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

`.env`:
GCP_PROJECT_ID=your-project-id
BQ_RAW_DATASET=ducks_raw
BQ_RAW_TABLE=ducks_chapters
GOOGLE_APPLICATION_CREDENTIALS=your-key-file.json
DUCKS_API_URL=api_url_to_be_processed

### 6. Configure dbt

Update `dbt_gcp_project/profiles.yml` with your project details:

```yaml
dbt_gcp_project:
  target: dev
  outputs:
    dev:
      dataset: "{{ env_var('BQ_RAW_DATASET') }}"
      job_execution_timeout_seconds: 300
      job_retries: 1
      keyfile: "{{ env_var('GOOGLE_APPLICATION_CREDENTIALS') }}"
      location: europe-west2
      method: service-account
      priority: interactive
      project: "{{ env_var('GCP_PROJECT_ID') }}"
      threads: 1
      type: bigquery
```

---

## Running the Pipeline

### Run the ETL pipeline

```bash
python -m src.etl.pipeline
```

This will:

- Fetch all university chapters from the DU API
- Clean and transform the data
- Load it into BigQuery under `ducks_raw.ducks_chapters`

### Run dbt models

```bash
cd dbt_gcp_project
dbt run --profiles-dir .
```

This will create:

- A staging view in `ducks_raw` dataset
- A final mart table in `ducks_analytics` dataset

---

## Running Tests

```bash
pytest tests/ -v
```

### Running linting

```bash
python -m flake8 src/ --max-line-length=120
```

---

## BigQuery Tables

### Raw table — `ducks_raw.ducks_chapters`

Loaded directly by the Python ETL pipeline.

| Column         | Type    | Description             |
| -------------- | ------- | ----------------------- |
| `chapter_id`   | STRING  | Chapter identifier      |
| `chapter_name` | STRING  | University chapter name |
| `city`         | STRING  | City                    |
| `state`        | STRING  | State abbreviation      |
| `longitude`    | FLOAT64 | Longitude coordinate    |
| `latitude`     | FLOAT64 | Latitude coordinate     |

### Staging view — `ducks_raw.stg_ducks_chapters`

Light cleaning and type casting on top of the raw table.

### Mart table — `ducks_analytics.university_chapters`

Final deduplicated analytics-ready table.

| Column         | Type    | Description                   |
| -------------- | ------- | ----------------------------- |
| `chapter_id`   | STRING  | Normalised chapter identifier |
| `chapter_name` | STRING  | Trimmed chapter name          |
| `city`         | STRING  | Trimmed city name             |
| `state`        | STRING  | Uppercased state abbreviation |
| `longitude`    | FLOAT64 | Longitude coordinate          |
| `latitude`     | FLOAT64 | Latitude coordinate           |

---

## CI/CD

The project uses GitHub Actions for CI/CD defined in `.github/workflows/ci.yml`.

### Pipeline behaviour

| Event          | Jobs that run          |
| -------------- | ---------------------- |
| Push to `main` | test-and-lint → deploy |

### Jobs

**test-and-lint**

- Installs dependencies
- Runs flake8 linting
- Runs pytest tests

**deploy** (only runs if test-and-lint passes)

- Authenticates to Google Cloud using the service account key
- Runs the ETL pipeline
- Runs dbt models

### GitHub Secrets required

Go to **Settings → Secrets and variables → Actions** and add:

| Secret            | Description                                  |
| ----------------- | -------------------------------------------- |
| `GCP_CREDENTIALS` | GCP service account key file                 |
| `GCP_PROJECT_ID`  | Your GCP project ID e.g. `ducks-etl-project` |
| `BQ_DATASET`      | BigQuery dataset name e.g. `ducks_raw`       |
| `BQ_TABLE`        | BigQuery table name e.g. `ducks_chapters`    |
| `DUCKS_API_URL`   | API URL to be processed `                    |

```

## Known Data Quality Issues

The following issues were identified in the source API and handled in the pipeline:

| Issue                         | Example                          | Handling                    |
| ----------------------------- | -------------------------------- | --------------------------- |
| Trailing whitespace in fields | `"Ruston "`                      | Stripped in `transform.py`  |
| Missing hyphen in ChapterID   | `"GA0147"` → `"GA-0147"`         | Fixed in `transform.py`     |
| Duplicate chapter             | UW-Platteville appears twice     | Deduplicated in dbt mart    |

---

## Dependencies

requests
google-cloud-bigquery
dbt-bigquery
pytest
flake8
autopep8
python-dotenv

---

## Notes

- The pipeline uses `WRITE_TRUNCATE` meaning it fully replaces the BigQuery table on every run
- BigQuery free tier allows 10GB storage and 1TB queries per month which is well within limits for this dataset
- The DU API returns all ~136 records
```
