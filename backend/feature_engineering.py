
import os
import pandas as pd

input_file = "data/processed/cleaned_transactions.csv"
output_file = "data/processed/featured_transactions.csv"

df = pd.read_csv(input_file)

print("Original dataset shape:", df.shape)

# Create features from transaction types
df = pd.get_dummies(
    df,
    columns=["type"],
    dtype=int
)

# Create balance difference features
df["balance_diff_orig"] = (
    df["oldbalanceOrg"] - df["newbalanceOrig"]
)

df["balance_diff_dest"] = (
    df["newbalanceDest"] - df["oldbalanceDest"]
)

# Save the featured dataset
os.makedirs("data/processed", exist_ok=True)
df.to_csv(output_file, index=False)

print("\nFeature engineering completed!")
print("Featured dataset shape:", df.shape)
print("\nFeatured columns:")
print(df.columns.tolist())
print("\nMissing values:", df.isnull().sum().sum())
print("Saved to:", output_file)