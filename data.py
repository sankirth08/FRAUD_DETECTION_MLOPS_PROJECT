
import pandas as pd
from pathlib import Path

file_path = Path(
    r"D:\ml project\fraud-detection-mlops\data\raw\PS_20174392719_1491204439457_log.csv"
)

if file_path.exists():
    df = pd.read_csv(file_path, nrows=1000)

    print("Dataset loaded successfully!")
    print("Rows and columns:", df.shape)
    print("\nColumn names:")
    print(df.columns.tolist())
    print("\nFirst five rows:")
    print(df.head())
    print("\nMissing values:")
    print(df.isnull().sum())
    print("\nFraud counts:")
    print(df["isFraud"].value_counts())
else:
    print("CSV file not found. Check the file name and location.")