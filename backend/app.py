
import json
import joblib
import pandas as pd

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "candidate_model"

model = joblib.load(MODEL_DIR / "best_fraud_model.pkl")
scaler = joblib.load(MODEL_DIR / "scaler.pkl")
feature_names = joblib.load(MODEL_DIR / "feature_names.pkl")

with open(MODEL_DIR / "threshold.json", "r") as file:
    threshold = json.load(file)["threshold"]

app = FastAPI(title="Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Transaction(BaseModel):
    step: int = Field(ge=1)
    type: str
    amount: float = Field(ge=0)
    oldbalanceOrg: float = Field(ge=0)
    newbalanceOrig: float = Field(ge=0)
    oldbalanceDest: float = Field(ge=0)
    newbalanceDest: float = Field(ge=0)

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": type(model).__name__,
        "feature_count": len(feature_names),
        "threshold": threshold,
    }

@app.post("/predict")
def predict(transaction: Transaction):
    allowed_types = {
        "CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"
    }

    if transaction.type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported transaction type",
        )

    values = {
        "step": transaction.step,
        "amount": transaction.amount,
        "oldbalanceOrg": transaction.oldbalanceOrg,
        "newbalanceOrig": transaction.newbalanceOrig,
        "oldbalanceDest": transaction.oldbalanceDest,
        "newbalanceDest": transaction.newbalanceDest,
        "type_CASH_IN": int(transaction.type == "CASH_IN"),
        "type_CASH_OUT": int(transaction.type == "CASH_OUT"),
        "type_DEBIT": int(transaction.type == "DEBIT"),
        "type_PAYMENT": int(transaction.type == "PAYMENT"),
        "type_TRANSFER": int(transaction.type == "TRANSFER"),
    }

    features = pd.DataFrame(
        [[values[name] for name in feature_names]],
        columns=feature_names,
    )

    scaled_features = scaler.transform(features)
    probability = float(model.predict_proba(scaled_features)[0, 1])
    prediction = int(probability >= threshold)

    return {
        "fraud_prediction": prediction,
        "fraud_probability": probability,
        "threshold": threshold,
        "result": "Fraud" if prediction else "Legitimate",
        "model": type(model).__name__,
    }