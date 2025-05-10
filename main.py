import os
import logging
from dotenv import load_dotenv

from utils.extract import extract_data
from utils.transform import transform_data
from utils.load import load_to_csv, load_to_postgres, load_to_gsheets

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

TOTAL_PAGES_TO_SCRAPE = 50
CSV_OUTPUT_FILENAME = "products.csv"

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GSHEETS_CREDENTIALS_PATH = "genuine-axle-457903-s7-8390e8582491.json"
WORKSHEET_NAME = "Products"

DB_CONNECTION_STRING = os.getenv("DATABASE_URL")
logging.info(f"DEBUG_ENV: DATABASE_URL read from env is: {DB_CONNECTION_STRING}")
POSTGRES_TABLE_NAME = "products"
POSTGRES_IF_EXISTS = 'replace'

LOAD_TARGETS = {
    "csv": True,
    "google_sheets": True,
    "postgres": True
}

def main():
    logging.info("=== Starting ETL Pipeline ===")

    logging.info("--- Stage 1: Extracting Data ---")
    df_raw = extract_data(total_pages=TOTAL_PAGES_TO_SCRAPE)
    if df_raw.empty:
        logging.error("Extraction failed or returned no data. Stopping pipeline.")
        return

    logging.info(f"Extraction successful. Raw data shape: {df_raw.shape}")

    logging.info("--- Stage 2: Transforming Data ---")
    df_clean = transform_data(df_raw)
    if df_clean.empty:
        logging.warning("Transformation resulted in an empty DataFrame. Check cleaning logic.")

    logging.info(f"Transformation successful. Cleaned data shape: {df_clean.shape}")

    logging.info("--- Stage 3: Loading Data ---")
    load_success_summary = {}

    if LOAD_TARGETS.get("csv", False):
        logging.info("Loading data to CSV...")
        success = load_to_csv(df_clean, CSV_OUTPUT_FILENAME)
        load_success_summary["CSV"] = success
        logging.info(f"CSV Load Status: {'Success' if success else 'Failed'}")

    if LOAD_TARGETS.get("google_sheets", False):
        if SPREADSHEET_ID:
            logging.info("Loading data to Google Sheets...")
            success = load_to_gsheets(df_clean, SPREADSHEET_ID, GSHEETS_CREDENTIALS_PATH, WORKSHEET_NAME)
            load_success_summary["Google Sheets"] = success
            logging.info(f"Google Sheets Load Status: {'Success' if success else 'Failed'}")
        else:
            logging.warning("Skipping Google Sheets load: SPREADSHEET_ID is not set.")

    if LOAD_TARGETS.get("postgres", False):
        if DB_CONNECTION_STRING:
            logging.info("Loading data to PostgreSQL...")
            success = load_to_postgres(df_clean, DB_CONNECTION_STRING, POSTGRES_TABLE_NAME, POSTGRES_IF_EXISTS)
            load_success_summary["PostgreSQL"] = success
            logging.info(f"PostgreSQL Load Status: {'Success' if success else 'Failed'}")
        else:
            logging.warning("Skipping PostgreSQL load: DATABASE_URL is not set.")

    logging.info("--- Load Summary ---")
    for target, status in load_success_summary.items():
        logging.info(f"{target}: {'OK' if status else 'FAIL'}")

    logging.info("=== ETL Pipeline Finished ===")

if __name__ == "__main__":
    print("DEBUG: Skrip dimulai.")
    main()