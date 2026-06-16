import pickle
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Real-Time ML Inference Engine")

try:
    with open("ml_model.pkl", "rb") as f:
        model = pickle.load(f)
except FileNotFoundError:
    print("⚠️ 'ml_model.pkl' not found. Please run 'python train_model.py' first!")
    model = None

class TransactionEvent(BaseModel):
    action: str
    device: str
    price: float

def encode_features(action: str, device: str):
    action_map = {"view": 0, "add_to_cart": 1, "purchase": 2}
    device_map = {"Desktop": 0, "Mobile": 1, "Tablet": 2}
    return action_map.get(action, 0), device_map.get(device, 0)

@app.get("/")
def home():
    return {"status": "ML Service is Online & Serving Predictions"}

@app.post("/predict")
def predict_risk(event: TransactionEvent):
    if not model:
        return {"calculated_risk_score": 0.15, "note": "Baseline default used"}
        
    action_enc, device_enc = encode_features(event.action, event.device)
    features = np.array([[action_enc, device_enc, event.price]])
    probabilities = model.predict_proba(features)[0]
    high_intent_score = float(probabilities[1])
    
    return {
        "calculated_risk_score": round(high_intent_score, 4),
        "model_version": "v1.0.0"
    }