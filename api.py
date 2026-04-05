from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pickle
import numpy as np
import os
from datetime import datetime

app = FastAPI(
    title="🛡️ FraudShield API",
    description="Real-time multi-domain fraud detection API",
    version="2.0"
)

# Load models
models = {}
scalers = {}
for key in ["credit_card", "debit_card", "insurance", "loan"]:
    model_path  = f"models/{key}_model.pkl"
    scaler_path = f"models/{key}_scaler.pkl"
    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            models[key] = pickle.load(f)
    if os.path.exists(scaler_path):
        with open(scaler_path, "rb") as f:
            scalers[key] = pickle.load(f)

# ── Request Models ─────────────────────────────────────────────────────────────
class CreditCardTransaction(BaseModel):
    time: float
    amount: float
    v1: float; v2: float; v3: float; v4: float; v5: float
    v6: float; v7: float; v8: float; v9: float; v10: float
    v11: float; v12: float; v13: float; v14: float; v15: float
    v16: float; v17: float; v18: float; v19: float; v20: float
    v21: float; v22: float; v23: float; v24: float; v25: float
    v26: float; v27: float; v28: float

class DebitCardTransaction(BaseModel):
    amount: float
    balance_before: float
    balance_after: float
    transaction_hour: float
    day_of_week: float
    merchant_category: float
    distance_from_home: float
    foreign_transaction: float
    online_transaction: float
    pin_used: float

class InsuranceClaim(BaseModel):
    claim_amount: float
    premium_amount: float
    policy_age_months: float
    num_claims_history: float
    incident_severity: float
    witnesses: float
    police_report: float
    vehicle_age: float
    driver_age: float
    time_to_claim_days: float

class LoanApplication(BaseModel):
    loan_amount: float
    annual_income: float
    credit_score: float
    employment_years: float
    debt_to_income: float
    num_open_accounts: float
    num_late_payments: float
    loan_purpose: float
    collateral_value: float
    co_applicant: float

# ── Response Helper ────────────────────────────────────────────────────────────
def predict(model_key: str, features: list):
    if model_key not in models:
        raise HTTPException(status_code=503, detail=f"Model '{model_key}' not loaded")
    model  = models[model_key]
    scaler = scalers.get(model_key)
    X = np.array(features).reshape(1, -1)
    if scaler:
        X = scaler.transform(X)
    pred  = int(model.predict(X)[0])
    proba = float(model.predict_proba(X)[0][1])
    risk  = "HIGH" if proba > 0.7 else "MEDIUM" if proba > 0.4 else "LOW"
    return {
        "prediction": "FRAUD" if pred == 1 else "LEGITIMATE",
        "fraud_probability": round(proba * 100, 2),
        "risk_level": risk,
        "action": "BLOCK" if pred == 1 else "APPROVE",
        "timestamp": datetime.now().isoformat(),
        "model": model_key
    }

# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {
        "name": "FraudShield API",
        "version": "2.0",
        "endpoints": ["/predict/credit-card", "/predict/debit-card", "/predict/insurance", "/predict/loan"],
        "models_loaded": list(models.keys())
    }

@app.get("/health")
def health():
    return {"status": "healthy", "models_loaded": len(models), "timestamp": datetime.now().isoformat()}

@app.post("/predict/credit-card")
def predict_credit_card(txn: CreditCardTransaction):
    features = [txn.v1,txn.v2,txn.v3,txn.v4,txn.v5,txn.v6,txn.v7,
                txn.v8,txn.v9,txn.v10,txn.v11,txn.v12,txn.v13,txn.v14,
                txn.v15,txn.v16,txn.v17,txn.v18,txn.v19,txn.v20,txn.v21,
                txn.v22,txn.v23,txn.v24,txn.v25,txn.v26,txn.v27,txn.v28,
                txn.amount, txn.time]
    return predict("credit_card", features)

@app.post("/predict/debit-card")
def predict_debit_card(txn: DebitCardTransaction):
    features = [txn.amount, txn.balance_before, txn.balance_after,
                txn.transaction_hour, txn.day_of_week, txn.merchant_category,
                txn.distance_from_home, txn.foreign_transaction,
                txn.online_transaction, txn.pin_used]
    return predict("debit_card", features)

@app.post("/predict/insurance")
def predict_insurance(claim: InsuranceClaim):
    features = [claim.claim_amount, claim.premium_amount, claim.policy_age_months,
                claim.num_claims_history, claim.incident_severity, claim.witnesses,
                claim.police_report, claim.vehicle_age, claim.driver_age,
                claim.time_to_claim_days]
    return predict("insurance", features)

@app.post("/predict/loan")
def predict_loan(application: LoanApplication):
    features = [application.loan_amount, application.annual_income,
                application.credit_score, application.employment_years,
                application.debt_to_income, application.num_open_accounts,
                application.num_late_payments, application.loan_purpose,
                application.collateral_value, application.co_applicant]
    return predict("loan", features)
