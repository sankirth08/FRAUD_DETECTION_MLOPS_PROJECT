
import os
import time
import joblib
import pandas as pd

from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix

split_dir = "data/processed/split"

X_train = pd.read_csv(f"{split_dir}/X_train.csv")
X_test = pd.read_csv(f"{split_dir}/X_test.csv")
y_train = pd.read_csv(f"{split_dir}/y_train.csv").squeeze()
y_test = pd.read_csv(f"{split_dir}/y_test.csv").squeeze()

print("Training HistGradientBoosting model...")

start_time = time.time()

model = HistGradientBoostingClassifier(
    max_iter=100,
    learning_rate=0.1,
    random_state=42
)

model.fit(X_train, y_train)

training_time = round(time.time() - start_time, 2)

probabilities = model.predict_proba(X_test)[:, 1]

threshold = 0.9
predictions = (probabilities >= threshold).astype(int)

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, predictions))

print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))

os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/best_fraud_model.pkl")

print("\nModel saved to models/best_fraud_model.pkl")
print("Training time:", training_time, "seconds")