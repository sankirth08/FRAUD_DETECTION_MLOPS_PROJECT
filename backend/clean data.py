
import os
import pandas as pd

input_file = "data/raw/PS_20174392719_1491204439457_log.csv"
output_file = "data/processed/cleaned_transactions.csv"

df = pd.read_csv(input_file)

print("Original dataset shape:", df.shape)

required_columns = [
    "step",
    "type",
    "amount",
    "nameOrig",
    "oldbalanceOrg",
    "newbalanceOrig",
    "nameDest",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
    "isFlaggedFraud"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing columns: {missing_columns}")

missing_values_before = df.isnull().sum().sum()
print("Missing values before cleaning:", missing_values_before)

df = df.dropna().copy()

numeric_columns = [
    "step",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "isFraud",
    "isFlaggedFraud"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="raise")

if (df["amount"] < 0).any():
    raise ValueError("Negative transaction amounts found.")

if not df["isFraud"].isin([0, 1]).all():
    raise ValueError("Invalid fraud labels found.")

valid_types = [
    "PAYMENT",
    "TRANSFER",
    "CASH_OUT",
    "DEBIT",
    "CASH_IN"
]

if not df["type"].isin(valid_types).all():
    raise ValueError("Invalid transaction types found.")

# Remove columns that will not be used for training
df = df.drop(
    columns=["nameOrig", "nameDest", "isFlaggedFraud"]
)

# Remove duplicate rows after selecting the final columns
rows_before_duplicates = len(df)

df = df.drop_duplicates()

duplicates_removed = rows_before_duplicates - len(df)

# Create the output directory
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Save the cleaned dataset
df.to_csv(output_file, index=False)

print("\nData cleaning completed successfully!")
print("Cleaned dataset shape:", df.shape)
print("Duplicate rows removed:", duplicates_removed)
print("Missing values remaining:", df.isnull().sum().sum())
print("Duplicate rows remaining:", df.duplicated().sum())
print("Fraud transactions:", int(df["isFraud"].sum()))
print("Non-fraud transactions:", int((df["isFraud"] == 0).sum()))
print("Saved cleaned dataset to:", output_file)