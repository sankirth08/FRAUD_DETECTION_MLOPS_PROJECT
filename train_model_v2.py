
import json
import os
import time

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    average_precision_score,
    roc_auc_score,
    confusion_matrix,
    precision_recall_curve
)

DATA_PATH = "data/raw/PS_20174392719_1491204439457_log.csv"
OUTPUT_DIR = "candidate_model"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("1. Loading dataset...")
data = pd.read_csv(DATA_PATH)

y = data["isFraud"].astype(int)

X = data[
    [
        "step",
        "type",
        "amount",
        "oldbalanceOrg",
        "newbalanceOrig",
        "oldbalanceDest",
        "newbalanceDest"
    ]
].copy()

X = pd.get_dummies(X, columns=["type"], dtype=int)

feature_names = [
    "step",
    "amount",
    "oldbalanceOrg",
    "newbalanceOrig",
    "oldbalanceDest",
    "newbalanceDest",
    "type_CASH_IN",
    "type_CASH_OUT",
    "type_DEBIT",
    "type_PAYMENT",
    "type_TRANSFER"
]

X = X.reindex(columns=feature_names, fill_value=0)

print("Dataset shape:", X.shape)
print("Fraud cases:", int(y.sum()))

print("\n2. Creating train, validation and test sets...")

X_trainval, X_test, y_trainval, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

X_train, X_val, y_train, y_val = train_test_split(
    X_trainval,
    y_trainval,
    test_size=0.25,
    random_state=42,
    stratify=y_trainval
)

print("Training rows:", len(X_train))
print("Validation rows:", len(X_val))
print("Test rows:", len(X_test))

print("\n3. Preprocessing...")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
X_test_scaled = scaler.transform(X_test)

print("\n4. Hyperparameter tuning on a training subset...")

tune_size = min(30000, len(X_train))
X_tune, _, y_tune, _ = train_test_split(
    X_train_scaled,
    y_train,
    train_size=tune_size,
    random_state=42,
    stratify=y_train
)

tuning_model = HistGradientBoostingClassifier(random_state=42)

search = RandomizedSearchCV(
    estimator=tuning_model,
    param_distributions={
        "learning_rate": [0.05, 0.1],
        "max_iter": [100, 150],
        "max_leaf_nodes": [15, 31]
    },
    n_iter=3,
    scoring="average_precision",
    cv=2,
    random_state=42,
    n_jobs=1,
    verbose=1
)

tune_weights = compute_sample_weight("balanced", y_tune)
search.fit(X_tune, y_tune, sample_weight=tune_weights)

print("Best tuning parameters:", search.best_params_)

print("\n5. Training and comparing models...")

models = {
    "Dummy Baseline": DummyClassifier(strategy="prior"),
    "Logistic Regression": LogisticRegression(
        max_iter=1000, class_weight="balanced", random_state=42
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1
    ),
    "Tuned HistGradientBoosting": HistGradientBoostingClassifier(
        **search.best_params_, random_state=42
    )
}

results = []
trained_models = {}

for name, model in models.items():
    print("\nTraining:", name)
    start = time.time()

    if name == "Tuned HistGradientBoosting":
        weights = compute_sample_weight("balanced", y_train)
        model.fit(X_train_scaled, y_train, sample_weight=weights)
    else:
        model.fit(X_train_scaled, y_train)

    probabilities = model.predict_proba(X_val_scaled)[:, 1]

    precision, recall, thresholds = precision_recall_curve(
        y_val, probabilities
    )

    f1_values = (
        2 * precision[:-1] * recall[:-1]
        / (precision[:-1] + recall[:-1] + 1e-12)
    )

    if len(thresholds) == 0:
        best_threshold = 0.5
    else:
        best_threshold = float(thresholds[np.argmax(f1_values)])

    predictions = (probabilities >= best_threshold).astype(int)

    row = {
        "model": name,
        "threshold": best_threshold,
        "precision": precision_score(
            y_val, predictions, zero_division=0
        ),
        "recall": recall_score(y_val, predictions, zero_division=0),
        "f1": f1_score(y_val, predictions, zero_division=0),
        "average_precision": average_precision_score(y_val, probabilities),
        "training_seconds": round(time.time() - start, 2)
    }

    results.append(row)
    trained_models[name] = model

    print(
        f"Validation precision={row['precision']:.4f}, "
        f"recall={row['recall']:.4f}, "
        f"F1={row['f1']:.4f}, "
        f"threshold={best_threshold:.6f}"
    )

comparison = pd.DataFrame(results).sort_values("f1", ascending=False)
comparison.to_csv(
    os.path.join(OUTPUT_DIR, "model_comparison.csv"), index=False
)

print("\n6. Selecting the best validation model...")

best_row = comparison.iloc[0]
best_name = best_row["model"]
best_model = trained_models[best_name]
best_threshold = float(best_row["threshold"])

print("Selected model:", best_name)
print("Selected validation F1:", round(float(best_row["f1"]), 4))
print("Selected threshold:", best_threshold)

print("\n7. Evaluating the selected model on the test set...")

test_probabilities = best_model.predict_proba(X_test_scaled)[:, 1]
test_predictions = (test_probabilities >= best_threshold).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_test, test_predictions, labels=[0, 1]
).ravel()

test_results = {
    "model": best_name,
    "threshold": best_threshold,
    "precision": precision_score(
        y_test, test_predictions, zero_division=0
    ),
    "recall": recall_score(y_test, test_predictions, zero_division=0),
    "f1": f1_score(y_test, test_predictions, zero_division=0),
    "accuracy": accuracy_score(y_test, test_predictions),
    "average_precision": average_precision_score(
        y_test, test_probabilities
    ),
    "roc_auc": roc_auc_score(y_test, test_probabilities),
    "true_negatives": int(tn),
    "false_positives": int(fp),
    "false_negatives": int(fn),
    "true_positives": int(tp)
}

pd.DataFrame([test_results]).to_csv(
    os.path.join(OUTPUT_DIR, "final_test_results.csv"), index=False
)

print(pd.DataFrame([test_results]).to_string(index=False))

print("\n8. Saving candidate model artifacts...")

joblib.dump(best_model, os.path.join(OUTPUT_DIR, "best_fraud_model.pkl"))
joblib.dump(scaler, os.path.join(OUTPUT_DIR, "scaler.pkl"))
joblib.dump(feature_names, os.path.join(OUTPUT_DIR, "feature_names.pkl"))

with open(os.path.join(OUTPUT_DIR, "threshold.json"), "w") as file:
    json.dump({"threshold": best_threshold}, file, indent=4)

print("\nDONE. Candidate artifacts saved in:", OUTPUT_DIR)
print("Production model files were not changed.")