from pathlib import Path
import pandas as pd

input_file = Path("data/processed/cleaned_transactions.csv")
output_file = Path("data/processed/featured_transactions.csv")

if not input_file.exists():
    raise FileNotFoundError(f"Cleaned dataset not found: {input_file}")

df = pd.read_csv(input_file)

print("Input shape:", df.shape)

required = [
    "step", "type", "amount", "oldbalanceOrg",
    "newbalanceOrig", "oldbalanceDest",
    "newbalanceDest", "isFraud"
]

missing = [col for col in required if col not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

df["balance_diff_orig"] = (
    df["oldbalanceOrg"] - df["newbalanceOrig"]
)

df["balance_diff_dest"] = (
    df["newbalanceDest"] - df["oldbalanceDest"]
)

df = pd.get_dummies(df, columns=["type"], dtype=int)

output_file.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_file, index=False)

print("Output shape:", df.shape)
print("Feature columns:", df.columns.tolist())
print("Missing values:", int(df.isnull().sum().sum()))
print("Saved to:", output_file)
