import pandas as pd
from pathlib import Path

file_path = Path("data/raw/PS_20174392719_1491204439457_log.csv")

df = pd.read_csv(file_path, nrows=10)

print("Dataset shape:", df.shape)
print("\nFirst 5 rows:")
print(df.head().to_string())
print("\nMissing values:")
print(df.isnull().sum())
print("\nFraud counts in these 10 rows:")
print(df["isFraud"].value_counts(dropna=False))
