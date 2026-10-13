
import pandas as pd
import matplotlib.pyplot as plt
import os

file_path = "data/processed/cleaned_transactions.csv"

df = pd.read_csv(file_path)

print("Dataset shape:", df.shape)

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset information:")
print(df.info())

print("\nFraud distribution:")
print(df["isFraud"].value_counts())

print("\nFraud percentage:")
print(df["isFraud"].value_counts(normalize=True) * 100)

print("\nTransaction types:")
print(df["type"].value_counts())

print("\nAverage transaction amount:")
print(df.groupby("isFraud")["amount"].mean())

print("\nFraud count by transaction type:")
print(pd.crosstab(df["type"], df["isFraud"]))

os.makedirs("reports/figures", exist_ok=True)

df["isFraud"].value_counts().sort_index().plot(
    kind="bar",
    title="Fraud vs Non-Fraud Transactions"
)
plt.xlabel("isFraud (0 = Non-Fraud, 1 = Fraud)")
plt.ylabel("Number of Transactions")
plt.tight_layout()
plt.savefig("reports/figures/fraud_distribution.png")
plt.close()

df.groupby("type")["amount"].mean().plot(
    kind="bar",
    title="Average Transaction Amount by Type"
)
plt.xlabel("Transaction Type")
plt.ylabel("Average Amount")
plt.tight_layout()
plt.savefig("reports/figures/average_transaction_amount.png")
plt.close()

print("\nEDA completed successfully!")
print("Charts saved in reports/figures/")