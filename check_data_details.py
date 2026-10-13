import pandas as pd
from pathlib import Path

file_path = Path("data/raw/PS_20174392719_1491204439457_log-selected-columns.csv")

df = pd.read_csv(file_path, nrows=10)

print("Shape:", df.shape)
print("\nFirst 10 rows:")
print(df.to_string())
print("\nMissing values:")
print(df.isnull().sum())
print("\nColumn names:")
print(df.columns.tolist())
