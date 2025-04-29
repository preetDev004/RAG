import os
from datetime import * 
import logging

today_date = datetime.now().strftime("%Y-%m-%d")
log_base_dir = 'logs'
log_subdir = os.path.join(log_base_dir, today_date)
os.makedirs(log_subdir, exist_ok=True)

# define the log file path
log_file_path = os.path.join(log_subdir, "api.log")

logging.basicConfig(
    level=logging.DEBUG, # set to DEBUG to capture all levels of logs (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s", # format of the log messages
    handlers=[
        logging.FileHandler(log_file_path), # output to a file
        logging.StreamHandler() # output to console (optional)
    ]
)

logger = logging.getLogger('api_logger')