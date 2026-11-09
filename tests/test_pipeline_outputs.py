"""
Data checks for the outputs of src/run_pipeline.py.

Run the pipeline first, then the tests:
    python src/run_pipeline.py
    pytest -v
"""
from pathlib import Path

import pandas as pd
import pytest

OUTPUTS = Path(__file__).resolve().parent.parent / "outputs"
FIELD_FILE = OUTPUTS / "field_test_file.csv"
WEATHER_FILE = OUTPUTS / "weather_test_file.csv"

FIELD_COLUMNS = {
    "Field_ID", "Elevation", "Latitude", "Longitude", "Location", "Slope",
    "Rainfall", "Min_temperature_C", "Max_temperature_C", "Ave_temps",
    "Soil_fertility", "Soil_type", "pH", "Pollution_level", "Plot_size",
    "Annual_yield", "Crop_type", "Standard_yield", "Weather_station",
}
WEATHER_MEASUREMENTS = {"Pollution_level", "Rainfall", "Temperature"}
VALID_CROPS = {"cassava", "tea", "wheat", "potato", "banana", "coffee", "rice", "maize"}


@pytest.fixture(scope="module")
def field_df():
    if not FIELD_FILE.exists():
        pytest.skip(f"{FIELD_FILE} not found. Run python src/run_pipeline.py first.")
    return pd.read_csv(FIELD_FILE)


@pytest.fixture(scope="module")
def weather_means():
    if not WEATHER_FILE.exists():
        pytest.skip(f"{WEATHER_FILE} not found. Run python src/run_pipeline.py first.")
    return pd.read_csv(WEATHER_FILE, index_col=0)


def test_field_shape(field_df):
    assert field_df.shape == (5654, 19)


def test_field_columns(field_df):
    assert set(field_df.columns) == FIELD_COLUMNS


def test_elevation_is_non_negative(field_df):
    assert (field_df["Elevation"] >= 0).all()


def test_crop_types_are_valid(field_df):
    assert set(field_df["Crop_type"].unique()) <= VALID_CROPS


def test_rainfall_is_positive(field_df):
    assert (field_df["Rainfall"] > 0).all()


def test_every_field_has_a_weather_station(field_df):
    assert field_df["Weather_station"].notna().all()
    assert set(field_df["Weather_station"].unique()) == {0, 1, 2, 3, 4}


def test_weather_means_layout(weather_means):
    assert weather_means.index.name == "Weather_station_ID"
    assert set(weather_means.columns) == WEATHER_MEASUREMENTS
    assert len(weather_means) == 5


def test_weather_means_complete(weather_means):
    assert weather_means.notna().all().all()
    assert (weather_means["Rainfall"] > 0).all()
