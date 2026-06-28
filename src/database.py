import sqlite3
from src.config import DB_PATH

def init_db():
    """Creates a table to store test results if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Створюємо таблицю експериментів
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            kp REAL,                  -- PID proportional coefficient
            ki REAL,                  -- PID integrating coefficient
            kd REAL,                  -- PID derivative coefficient
            fitness_version TEXT,     -- Version of our fitness function (e.g., 'v1.0')
            fitness_score REAL,       -- Final flight quality assessment
            status TEXT,              -- Status: 'success', 'failed', etc.
            csv_filename TEXT         -- Link to the raw CSV file of this test log
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"The database was successfully initialized at the path: {DB_PATH}")

def save_experiment_result(kp, ki, kd, fitness_version, fitness_score, status, csv_filename):
    """A function to save the result of a new test to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO test_results (kp, ki, kd, fitness_version, fitness_score, status, csv_filename)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (kp, ki, kd, fitness_version, fitness_score, status, csv_filename))
    
    conn.commit()
    conn.close()
    print("The experiment result has been successfully saved in SQL!")