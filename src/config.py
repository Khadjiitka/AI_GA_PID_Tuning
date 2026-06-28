import os
from pathlib import Path

# We determine the project's root folder (go up one level from the src folder)
BASE_DIR = Path(__file__).resolve().parent.parent

# Paths to data folders
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports", "figures")

# Path to the database SQLite
DB_PATH = os.path.join(PROCESSED_DATA_DIR, "experiments.db")

# Drone telemetry settings (column names in CSV files)
TELEMETRY_COLUMNS = [
    "dt", "ax_raw", "ay_raw", "az_raw", 
    "gx_raw", "gy_raw", "gz_raw", 
    "ax_g", "ay_g", "az_g", 
    "gyroX_dps", "gyroY_dps", "gyroZ_dps", 
    "roll_deg", "pitch_deg", "yaw_deg"
]

# We create folders if they don’t exist on the disk yet
os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)