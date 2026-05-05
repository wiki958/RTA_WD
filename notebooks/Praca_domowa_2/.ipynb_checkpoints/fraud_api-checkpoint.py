from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import numpy as np

app = FastAPI(title="Fraud Detection API")
model = pickle.load(open('fraud_model.pkl', 'rb'))

class Transaction(BaseModel):
    amount: float
    is_electronics: int
    tx_per_minute: int

# Endpoint POST /score
@app.post("/score")
def score(transaction: Transaction):
    features = np.array([[
        transaction.amount,
        transaction.is_electronics,
        transaction.tx_per_minute
    ]])

    is_fraud = bool(model.predict(features)[0])
    fraud_probability = float(model.predict_proba(features)[0][1])

    return {
        "is_fraud": is_fraud,
        "fraud_probability": round(fraud_probability, 4)
    }
