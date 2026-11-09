"""
run_pipeline.py

Runs the Maji Ndogo field and weather pipelines end to end and writes the
cleaned outputs that the tests in tests/ check:

    outputs/field_test_file.csv    cleaned, merged field survey data
    outputs/weather_test_file.csv  mean weather measurements per station

Usage (from the repository root):
    python src/run_pipeline.py
"""
from pathlib import Path

from field_data_processor import FieldDataProcessor
from weather_data_processor import WeatherDataProcessor

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUTPUTS = ROOT / "outputs"

config_params = {
    "sql_query": """
        SELECT *
        FROM geographic_features
        LEFT JOIN weather_features USING (Field_ID)
        LEFT JOIN soil_and_crop_features USING (Field_ID)
        LEFT JOIN farm_management_features USING (Field_ID)
    """,
    "db_path": f"sqlite:///{DATA / 'Maji_Ndogo_farm_survey_small.db'}",
    # Two column names were swapped at the source; switch them back.
    "columns_to_rename": {"Annual_yield": "Crop_type", "Crop_type": "Annual_yield"},
    # Misspelled crop names found during exploration.
    "values_to_rename": {"cassaval": "cassava", "wheatn": "wheat", "teaa": "tea"},
    "weather_csv_path": str(DATA / "Weather_station_data.csv"),
    "weather_mapping_csv": str(DATA / "Weather_data_field_mapping.csv"),
    # Weather stations send free-text messages; these patterns pull out the numbers.
    "regex_patterns": {
        "Rainfall": r"(\d+(\.\d+)?)\s?mm",
        "Temperature": r"(\d+(\.\d+)?)\s?C",
        "Pollution_level": r"=\s*(-?\d+(\.\d+)?)|Pollution at \s*(-?\d+(\.\d+)?)",
    },
}


def main():
    OUTPUTS.mkdir(exist_ok=True)

    field = FieldDataProcessor(config_params)
    field_df = field.process()
    field_df.to_csv(OUTPUTS / "field_test_file.csv", index=False)

    weather = WeatherDataProcessor(config_params)
    weather.process()
    weather.calculate_means().to_csv(OUTPUTS / "weather_test_file.csv")

    print(f"Field rows: {len(field_df):,}  ->  {OUTPUTS / 'field_test_file.csv'}")
    print(f"Weather stations: {weather.weather_df['Weather_station_ID'].nunique()}  ->  {OUTPUTS / 'weather_test_file.csv'}")


if __name__ == "__main__":
    main()
