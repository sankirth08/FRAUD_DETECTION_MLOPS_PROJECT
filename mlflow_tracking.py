
import pandas as pd
import mlflow
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_score, recall_score, f1_score

df = pd.read_csv(
    "data/raw/PS_20174392719_1491204439457_log.csv"
)

df = df.drop(
    columns=["nameOrig", "nameDest", "isFlaggedFraud"]
)

df = pd.get_dummies(df, columns=["type"], dtype=int)

X = df.drop("isFraud", axis=1)
y = df["isFraud"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced"
)

model.fit(X_train, y_train)

probabilities = model.predict_proba(X_test)[:, 1]
predictions = (probabilities >= 0.8).astype(int)

precision = precision_score(y_test, predictions, zero_division=0)
recall = recall_score(y_test, predictions, zero_division=0)
f1 = f1_score(y_test, predictions, zero_division=0)

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("Fraud Detection")

with mlflow.start_run():
    mlflow.log_param("model", "Logistic Regression")
    mlflow.log_param("class_weight", "balanced")
    mlflow.log_param("threshold", 0.8)
    mlflow.log_param("test_size", 0.2)

    mlflow.log_metric("precision", precision)
    mlflow.log_metric("recall", recall)
    mlflow.log_metric("f1_score", f1)

    print("Precision:", precision)
    print("Recall:", recall)
    print("F1 Score:", f1)
    print("MLflow tracking completed!")