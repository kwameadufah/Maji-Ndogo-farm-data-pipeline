"""
field_data_processor.py

This module defines the FieldDataProcessor class, which encapsulates the entire 
data pipeline for ingesting, cleaning, and preparing the Maji Ndogo farm survey data.
Configuration details are loaded via the config_params dictionary passed during 
initialization.
"""

### START FUNCTION
import pandas as pd
from data_ingestion import create_db_engine, query_data, read_from_web_CSV
import logging

# Ensure logging is configured (standard practice for modules)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class FieldDataProcessor:

    def __init__(self, config_params, logging_level="INFO"):  # Make sure to add this line, passing in config_params to the class
        self.db_path = config_params['db_path']
        self.sql_query = config_params['sql_query']
        self.columns_to_rename = config_params['columns_to_rename']
        self.values_to_rename = config_params['values_to_rename']
        self.weather_map_data = config_params['weather_mapping_csv']

        self.initialize_logging(logging_level)
        self.df = None
        self.engine = None

    # This method enables logging in the class.
    def initialize_logging(self, logging_level):
        """
        Sets up logging for this instance of FieldDataProcessor.
        """
        logger_name = __name__ + ".FieldDataProcessor"
        self.logger = logging.getLogger(logger_name)
        self.logger.propagate = False  # Prevents log messages from being propagated to the root logger

        # Set logging level
        if logging_level.upper() == "DEBUG":
            log_level = logging.DEBUG
        elif logging_level.upper() == "INFO":
            log_level = logging.INFO
        elif logging_level.upper() == "NONE":  # Option to disable logging
            self.logger.disabled = True
            return
        else:
            log_level = logging.INFO  # Default to INFO

        self.logger.setLevel(log_level)

        # Only add handler if not already added to avoid duplicate messages
        if not self.logger.handlers:
            ch = logging.StreamHandler()  # Create console handler
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

        # Use self.logger.info(), self.logger.debug(), etc.


    # let's focus only on this part from now on
    def ingest_sql_data(self):
        self.engine = create_db_engine(self.db_path)
        self.df = query_data(self.engine, self.sql_query)
        self.logger.info("Sucessfully loaded data.")
        return self.df

    def rename_columns(self):
        # 1. Extract the columns to rename from the configuration
        column1, column2 = list(self.columns_to_rename.keys())[0], list(self.columns_to_rename.values())[0]

        # 2. Temporarily rename one of the columns to avoid a naming conflict
        temp_name = "__temp_name_for_swap__"
        while temp_name in self.df.columns:
            temp_name += "_"

        # 3. Perform the swap
        self.df = self.df.rename(columns={column1: temp_name, column2: column1})
        self.df = self.df.rename(columns={temp_name: column2})

        # 5. Log the action
        self.logger.info(f"Swapped columns: {column1} with {column2}")

    def apply_corrections(self, column_name='Crop_type', abs_column='Elevation'):
        self.df[abs_column] = self.df[abs_column].abs()
        # Strip stray spaces first ('tea ' -> 'tea'), then fix the known misspellings.
        self.df[column_name] = self.df[column_name].str.strip()
        self.df[column_name] = self.df[column_name].apply(lambda crop: self.values_to_rename.get(crop, crop))

    def weather_station_mapping(self):
        # 1. Read the mapping data from the web CSV
        weather_map_df = read_from_web_CSV(self.weather_map_data)

        # 2. MERGE
        self.df = pd.merge(self.df, weather_map_df,
                           on='Field_ID',
                           how='left')

        self.logger.info("Weather station data successfully mapped and merged.")


    def process(self):
        self.ingest_sql_data()
        self.rename_columns()
        self.apply_corrections()
        self.weather_station_mapping()
        self.df = self.df.drop(columns="Unnamed: 0", errors='ignore') # Added errors='ignore' in case column doesn't exist

        self.logger.info("Data processing pipeline completed successfully.")
        return self.df

## END FUNCTION