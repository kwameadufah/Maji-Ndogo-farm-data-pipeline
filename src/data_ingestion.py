"""
This module provides a robust set of helper functions for data ingestion 
and connection management for the Maji Ndogo project.

It includes functions for:
1. Creating and testing a database engine connection using SQLAlchemy.
2. Querying data from a connected database and returning a Pandas DataFrame.
3. Reading data directly from a CSV file hosted on a web URL.

These functions are designed with exception handling and logging to ensure 
pipeline reliability and provide clear feedback on errors.
"""
# Necessary Imports
import pandas as pd
from sqlalchemy import create_engine, text
import logging

# Set up basic logging (required by your function code)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

### START FUNCTION

def create_db_engine(db_path):
    """
    Creates and tests a SQLAlchemy engine connection to an SQLite database.

    Args:
        db_path (str): The connection string for the database (e.g., 'sqlite:///path/to/db.db').

    Returns:
        sqlalchemy.engine.base.Engine: The created database engine object.

    Raises:
        ImportError: If the SQLAlchemy package is not installed.
        Exception: If the engine creation or connection test fails.
    """
    try:
        engine = create_engine(db_path)
        # Test connection
        with engine.connect() as conn:
            pass
        # test if the database engine was created successfully
        logger.info("Database engine created successfully.")
        return engine # Return the engine object if it all works well
    except ImportError as e: #If we get an ImportError, inform the user SQLAlchemy is not installed
        logger.error("SQLAlchemy is required to use this function. Please install it first.")
        raise e
    except Exception as e:# If we fail to create an engine inform the user
        logger.error(f"Failed to create database engine. Error: {e}")
        raise e

def query_data(engine, sql_query):
    """
    Executes an SQL query using a SQLAlchemy engine and returns the result as a Pandas DataFrame.

    Args:
        engine (sqlalchemy.engine.base.Engine): The database engine object.
        sql_query (str): The SQL query string to be executed.

    Returns:
        pd.DataFrame: A DataFrame containing the results of the query.

    Raises:
        ValueError: If the query returns an empty DataFrame.
        Exception: If any other error occurs during the querying process.
    """
    try:
        with engine.connect() as connection:
            df = pd.read_sql_query(text(sql_query), connection)
        if df.empty:
            # Log a message or handle the empty DataFrame scenario as needed
            msg = "The query returned an empty DataFrame."
            logger.error(msg)
            raise ValueError(msg)
        logger.info("Query executed successfully.")
        return df
    except ValueError as e:
        logger.error(f"SQL query failed. Error: {e}")
        raise e
    except Exception as e:
        logger.error(f"An error occurred while querying the database. Error: {e}")
        raise e

def read_from_web_CSV(URL):
    """
    Reads a CSV file directly from a web URL into a Pandas DataFrame.

    Args:
        URL (str): The full URL pointing to the raw CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the data from the CSV file.

    Raises:
        pd.errors.EmptyDataError: If the URL does not point to a valid or non-empty CSV file.
        Exception: If any other error occurs during file reading (e.g., connection issue).
    """
    try:
        df = pd.read_csv(URL)
        logger.info("CSV file read successfully from the web.")
        return df
    except pd.errors.EmptyDataError as e:
        logger.error("The URL does not point to a valid CSV file. Please check the URL and try again.")
        raise e
    except Exception as e:
        logger.error(f"Failed to read CSV from the web. Error: {e}")
        raise e

### END FUNCTION