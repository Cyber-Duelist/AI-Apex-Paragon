import logging
import os

print("=== INITIALIZING LOGGER ===")

# 1. Define the exact path where the log file will live
log_file_path = "week_06/production_python/app.log"

# 2. Configure the root logging system
logging.basicConfig(
    level=logging.DEBUG, # This ensures we capture everything from DEBUG and above
    # The format string dictates exactly how the log line will look
    # %(levelname)-8s adds spacing so the severity levels align perfectly
    format="%(asctime)s - %(levelname)-8s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file_path),  # Handler 1: Write to the file
        logging.StreamHandler()              # Handler 2: Print to the console
    ]
)

# 3. Create a professional logger instance named after the current file
logger = logging.getLogger(__name__)

# 4. Fire the test logs across all 5 severity levels
logger.debug("App starting up")
logger.info("Config loaded successfully")
logger.warning("DB_PATH not found in environment")
logger.error("Failed to connect to database")
logger.critical("Application cannot start")