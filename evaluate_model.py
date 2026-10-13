
import os
import time
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

DATA_FILE = "data/raw/PS_20174392719_1491204439457_log.csv"
THRESHOLD = 0.8

df = pd.read_csv(DATA_FILE)

df = df.drop(columns=["nameOrig", "nameDest", "isFlaggedFraud"])
df = pd.get_dummies(df, columns=["type"], dtype=int)

X = df.drop("isFraud", axis=1)
y = df["isFraud"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1
    ),
    "HistGradientBoosting": HistGradientBoostingClassifier(
        random_state=42
    )
}

results = []
trained_models = {}

for name, model in models.items():
    print(f"\nTraining {name}...")
    start_time = time.time()

    model.fit(X_train_scaled, y_train)

    probabilities = model.predict_proba(X_test_scaled)[:, 1]
    predictions = (probabilities >= THRESHOLD).astype(int)

    precision = precision_score(y_test, predictions, zero_division=0)
    recall = recall_score(y_test, predictions, zero_division=0)
    f1 = f1_score(y_test, predictions, zero_division=0)

    results.append({
        "model": name,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "threshold": THRESHOLD,
        "training_time_seconds": round(time.time() - start_time, 2)
    })

    trained_models[name] = model

    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")

results_df = pd.DataFrame(results)
results_df = results_df.sort_values(
    by="f1_score",
    ascending=False
)

os.makedirs("models", exist_ok=True)

results_df.to_csv("evaluation_results.csv", index=False)
results_df.to_csv("models/model_comparison.csv", index=False)

best_name = results_df.iloc[0]["model"]
best_model = trained_models[best_name]

joblib.dump(best_model, "fraud_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(list(X.columns), "feature_names.pkl")

joblib.dump(best_model, "models/best_fraud_model.pkl")
joblib.dump(scaler, "models/scaler.pkl")
joblib.dump(list(X.columns), "models/feature_names.pkl")

best_probabilities = best_model.predict_proba(X_test_scaled)[:, 1]
best_predictions = (best_probabilities >= THRESHOLD).astype(int)

print("\nModel comparison:")
print(results_df.to_string(index=False))

print(f"\nSelected production model: {best_name}")
print("Confusion matrix:")
print(confusion_matrix(y_test, best_predictions))
print(f"Production threshold: {THRESHOLD}")
print("\nProduction model and matching artifacts saved successfully.")