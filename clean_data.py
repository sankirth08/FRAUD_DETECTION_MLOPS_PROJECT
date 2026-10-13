import os
import pandas as pd

input_file = "data/raw/PS_20174392719_1491204439457_log.csv"
output_file = "data/processed/cleaned_transactions.csv"

required_columns = [
    "step", "type", "amount", "nameOrig",
    "oldbalanceOrg", "newbalanceOrig", "nameDest",
    "oldbalanceDest", "newbalanceDest",
    "isFraud", "isFlaggedFraud"
]

df = pd.read_csv(input_file)

print("Original dataset shape:", df.shape)

missing_columns = [c for c in required_columns if c not in df.columns]
if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

df = df.dropna()
df = df.drop_duplicates()

print("Rows after removing missing values and duplicates:", len(df))

df = df.drop(columns=["nameOrig", "nameDest", "isFlaggedFraud"])

os.makedirs(os.path.dirname(output_file), exist_ok=True)
df.to_csv(output_file, index=False)

print("Cleaned dataset shape:", df.shape)
print("Missing values remaining:", int(df.isnull().sum().sum()))
print("Duplicate rows remaining:", int(df.duplicated().sum()))
print("Saved cleaned dataset to:", output_file)
