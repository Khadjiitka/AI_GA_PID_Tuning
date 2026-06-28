import os
import pandas as pd
from src.config import RAW_DATA_DIR, TELEMETRY_COLUMNS

def load_telemetry_csv(filename):
    """Uploads a separate test CSV file in the format DataFrame."""
    file_path = os.path.join(RAW_DATA_DIR, filename)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {filename} not found in the folder {RAW_DATA_DIR}")
        
    # We read the CSV. If the headers are missing, we pass them from the config through names
    df = pd.read_csv(file_path)
    return df