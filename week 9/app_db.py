import pandas as pd
from pathlib import Path

BASE_PATH = Path("../Week 9/DATA")

def get_table_from_csv(name):
    path = BASE_PATH / f"{name}.csv"
    return pd.read_csv(path)