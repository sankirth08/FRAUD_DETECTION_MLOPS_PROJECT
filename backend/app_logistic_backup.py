from pathlib import Path
import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent

model = joblib.load(BASE_DIR / "fraud_model.pkl")
scaler = joblib.load(BASE_DIR / "scaler.pkl")
feature_names = joblib.load(BASE_DIR / "feature_names.pkl")

THRESHOLD = 0.8

if len(feature_names) != scaler.n_features_in_:
    raise RuntimeError("Feature names do not match the scaler.")

if model.n_features_in_ != len(feature_names):
    raise RuntimeError("Model input features do not match feature names.")

app = FastAPI(title="Fraud Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Transaction(BaseModel):
    step: int = Field(gt=0)
    type: str
    amount: float = Field(ge=0)
    oldbalanceOrg: float = Field(ge=0)
    newbalanceOrig: float = Field(ge=0)
    oldbalanceDest: float = Field(ge=0)
    newbalanceDest: float = Field(ge=0)


@app.get("/")
def home():
    return {"message": "Fraud Detection API is running"}


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": type(model).__name__,
        "feature_count": len(feature_names),
        "threshold": THRESHOLD,
    }


@app.post("/predict")
def predict(transaction: Transaction):
    valid_types = [
        "CASH_IN",
        "CASH_OUT",
        "DEBIT",
        "PAYMENT",
        "TRANSFER",
    ]

    transaction_type = transaction.type.strip().upper()

    if transaction_type not in valid_types:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid transaction type. Choose from: {valid_types}",
        )

    input_data = pd.DataFrame([{
        "step": transaction.step,
        "amount": transaction.amount,
        "oldbalanceOrg": transaction.oldbalanceOrg,
        "newbalanceOrig": transaction.newbalanceOrig,
        "oldbalanceDest": transaction.oldbalanceDest,
        "newbalanceDest": transaction.newbalanceDest,
        "type": transaction_type,
    }])

    input_data = pd.get_dummies(
        input_data,
        columns=["type"],
        dtype=int,
    )

    input_data = input_data.reindex(
        columns=feature_names,
        fill_value=0,
    )

    scaled_data = scaler.transform(input_data)
    probability = float(model.predict_proba(scaled_data)[0][1])
    prediction = int(probability >= THRESHOLD)

    return {
        "fraud_prediction": prediction,
        "fraud_probability": probability,
        "threshold": THRESHOLD,
        "result": "Fraud" if prediction else "Legitimate",
        "model": type(model).__name__,
    }
