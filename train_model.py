
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, classification_report

df = pd.read_csv("data/raw/PS_20174392719_1491204439457_log.csv")

print("Original dataset shape:", df.shape)

df = df.drop(columns=["nameOrig", "nameDest", "isFlaggedFraud"])

df = pd.get_dummies(df, columns=["type"], dtype=int)

X = df.drop("isFraud", axis=1)
y = df["isFraud"]

print("\nFeatures shape:", X.shape)
print("Target shape:", y.shape)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining rows:", len(X_train))
print("Testing rows:", len(X_test))

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = LogisticRegression(max_iter=1000, class_weight="balanced")

model.fit(X_train, y_train)

y_probability = model.predict_proba(X_test)[:, 1]

y_pred = (y_probability >= 0.8).astype(int)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

joblib.dump(model, "fraud_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(list(df.drop("isFraud", axis=1).columns), "feature_names.pkl")

print("\nModel saved successfully!")