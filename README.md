# Maji Ndogo farm data pipeline

A tested Python pipeline that turns a messy farm survey database and free-text weather station logs into clean, analysis-ready tables. I built it during the ALX Data Science program (2025) as the Maji Ndogo agriculture integrated project.

**Skills:** Python, pandas, SQL (SQLite via SQLAlchemy), regular expressions, object-oriented design, logging, pytest

## The problem

Maji Ndogo is a fictional country whose agriculture ministry wants to know which crops grow best where. The survey data arrived with problems that would quietly break any analysis:

- Two columns, `Crop_type` and `Annual_yield`, had swapped names.
- Elevation had negative values.
- Crop names were misspelled (`cassaval`, `wheatn`, `teaa`) or had trailing spaces.
- Weather readings came as free-text messages in several formats and languages, for example `Temp. Reading [2023-05-23 09:41:36]: Current 14.53 C.`

## What the pipeline does

```
SQLite survey database ─► FieldDataProcessor ─► cleaned field table (5,654 fields)
                              │  join 4 tables in SQL
                              │  swap the mislabeled columns back
                              │  fix elevation signs and crop names
                              └─ attach each field's weather station

Weather station logs ───► WeatherDataProcessor ─► mean rainfall, temperature and
                              │  regex extraction of each reading     pollution per station
                              └─ group and average by station
```

| File | Role |
|---|---|
| `src/data_ingestion.py` | Database connection, SQL queries and CSV loading, with logging and error handling |
| `src/field_data_processor.py` | `FieldDataProcessor` class: ingest, clean and merge the field survey |
| `src/weather_data_processor.py` | `WeatherDataProcessor` class: parse weather messages and compute station means |
| `src/run_pipeline.py` | Runs both processors and writes the outputs |
| `tests/test_pipeline_outputs.py` | 8 pytest checks on shape, columns, value ranges and completeness |
| `notebooks/` | The three working notebooks: ingestion and cleaning, EDA and validation, refactoring into modules |

All settings (SQL query, file paths, renaming rules, regex patterns) live in one `config_params` dictionary, so the same classes can run on new survey extracts without code changes.

## Run it

```bash
pip install -r requirements.txt
python src/run_pipeline.py
pytest -v
```

Expected result: `8 passed`.

## Data

The survey database and weather files in `data/` are the synthetic Maji Ndogo dataset that ALX and ExploreAI provide for training. The project brief and the starter structure of the modules come from the course. I wrote the implementation and made the cleaning decisions.

---

Prince Adufah · [adufah.com](https://adufah.com) · [LinkedIn](https://www.linkedin.com/in/princeadufah)
