from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

input_file = Path("data/raw/PS_20174392719_1491204439457_log.csv")
output_dir = Path("reports/eda")
output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_file)

print("EDA REPORT")
print("-" * 40)
print("Dataset shape:", df.shape)
print("\nFraud counts:")
print(df["isFraud"].value_counts())
print("\nFraud percentage:")
print((df["isFraud"].value_counts(normalize=True) * 100).round(4))
print("\nTransaction types:")
print(df["type"].value_counts())
print("\nTransaction amount summary:")
print(df["amount"].describe())

fraud_counts = df["isFraud"].value_counts().sort_index()
plt.figure(figsize=(7, 5))
fraud_counts.plot(kind="bar")
plt.title("Legitimate vs Fraud Transactions")
plt.xlabel("Fraud label (0 = Legitimate, 1 = Fraud)")
plt.ylabel("Number of transactions")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(output_dir / "fraud_distribution.png")
plt.close()

fraud_by_type = df.groupby("type")["isFraud"].sum().sort_values(ascending=False)
plt.figure(figsize=(8, 5))
fraud_by_type.plot(kind="bar")
plt.title("Fraud Transactions by Transaction Type")
plt.xlabel("Transaction type")
plt.ylabel("Number of fraud transactions")
plt.xticks(rotation=30)
plt.tight_layout()
plt.savefig(output_dir / "fraud_by_type.png")
plt.close()

plt.figure(figsize=(8, 5))
plt.hist(df.loc[df["isFraud"] == 0, "amount"], bins=50, alpha=0.7, label="Legitimate")
plt.hist(df.loc[df["isFraud"] == 1, "amount"], bins=50, alpha=0.7, label="Fraud")
plt.title("Transaction Amount Distribution")
plt.xlabel("Transaction amount")
plt.ylabel("Frequency")
plt.legend()
plt.tight_layout()
plt.savefig(output_dir / "fraud_amount_distribution.png")
plt.close()

print("\nEDA charts saved to:", output_dir)
for file in sorted(output_dir.glob("*.png")):
    print(file)
