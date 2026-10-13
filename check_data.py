
import pandas as pd

file_path = "data/raw/PS_20174392719_1491204439457_log.csv"

df = pd.read_csv(file_path)

print("Dataset loaded successfully!")
print("Dataset shape:", df.shape)

print("\nFirst five rows:")
print(df.head())

print("\nMissing values:")
print(df.isnull().sum())

print("\nFraud counts:")
print(df["isFraud"].value_counts().sort_index())

print("\nFraud percentage:")
print((df["isFraud"].value_counts(normalize=True).sort_index() * 100).round(4))

print("\nDuplicate rows:")
print(df.duplicated().sum())

print("\nTransaction types:")
print(df["type"].value_counts())

print("\nTransaction amount statistics:")
print(df["amount"].describe())

print("\nData checking completed!")