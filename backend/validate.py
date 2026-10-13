
import pandas as pd

file_path = "data/raw/PS_20174392719_1491204439457_log.csv"

df = pd.read_csv(file_path)

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

print("Starting data validation...")

missing_columns = []

for column in required_columns:
    if column not in df.columns:
        missing_columns.append(column)

if missing_columns:
    print("Missing columns:", missing_columns)
else:
    print("All required columns are present.")

missing_values = df.isnull().sum().sum()

if missing_values > 0:
    print("Missing values found:", missing_values)
else:
    print("No missing values found.")

duplicate_rows = df.duplicated().sum()

if duplicate_rows > 0:
    print("Duplicate rows found:", duplicate_rows)
else:
    print("No duplicate rows found.")

if "amount" in df.columns:
    if (df["amount"] < 0).any():
        print("Invalid data: negative transaction amounts found.")
    else:
        print("Transaction amounts are valid.")

if "isFraud" in df.columns:
    invalid_labels = ~df["isFraud"].isin([0, 1])

    if invalid_labels.any():
        print("Invalid fraud labels found.")
    else:
        print("Fraud labels are valid.")

if "type" in df.columns:
    valid_types = [
        "PAYMENT",
        "TRANSFER",
        "CASH_OUT",
        "DEBIT",
        "CASH_IN"
    ]

    invalid_types = ~df["type"].isin(valid_types)

    if invalid_types.any():
        print("Invalid transaction types found.")
    else:
        print("Transaction types are valid.")

if not missing_columns and missing_values == 0 and duplicate_rows == 0:
    print("Basic data validation passed.")
else:
    print("Data validation found issues. Review the messages above.")