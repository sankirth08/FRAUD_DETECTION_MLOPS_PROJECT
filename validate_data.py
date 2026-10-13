from pathlib import Path
import pandas as pd

file_path = Path("data/raw/PS_20174392719_1491204439457_log.csv")

required_columns = [
    "step", "type", "amount", "nameOrig",
    "oldbalanceOrg", "newbalanceOrig", "nameDest",
    "oldbalanceDest", "newbalanceDest",
    "isFraud", "isFlaggedFraud"
]

if not file_path.exists():
    raise FileNotFoundError(f"Dataset not found: {file_path}")

df = pd.read_csv(file_path)

print("DATA VALIDATION REPORT")
print("-" * 40)
print("Dataset path:", file_path)
print("Dataset shape:", df.shape)

missing_columns = [col for col in required_columns if col not in df.columns]
print("Missing required columns:", missing_columns)
print("Missing values:", int(df.isnull().sum().sum()))
print("Duplicate raw rows:", int(df.duplicated().sum()))
print("Invalid fraud labels:", int((~df["isFraud"].isin([0, 1])).sum()) if "isFraud" in df.columns else "Cannot check")
print("Transaction types:", df["type"].value_counts().to_dict() if "type" in df.columns else "Cannot check")

if missing_columns:
    print("VALIDATION FAILED: required columns are missing.")
elif df.empty:
    print("VALIDATION FAILED: dataset is empty.")
elif "isFraud" in df.columns and not df["isFraud"].isin([0, 1]).all():
    print("VALIDATION FAILED: fraud labels must be 0 or 1.")
else:
    print("VALIDATION PASSED: required columns and fraud labels are valid.")
