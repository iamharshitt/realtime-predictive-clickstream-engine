import pickle
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

# Initialize the FastAPI Application
app = FastAPI(title="Real-Time ML Inference Engine")

# Load our pre-trained model file into memory
with open("ml_model.pkl", "rb") as f:
    model = pickle.load(f)

# Define what incoming data should look like (Data Validation)
class TransactionEvent(BaseModel):
    action: str
    device: str
    price: float

# Helper function to encode text features exactly how our model learned them
def encode_features(action: str, device: str):
    action_map = {"view": 0, "add_to_cart": 1, "purchase": 2}
    device_map = {"Desktop": 0, "Mobile": 1, "Tablet": 2}
    
    return action_map.get(action, 0), device_map.get(device, 0)

@app.get("/")
def home():
    return {"status": "ML Service is Online & Serving Predictions"}

@app.post("/predict")
def predict_risk(event: TransactionEvent):
    # 1. Convert text to numerical flags
    action_enc, device_enc = encode_features(event.action, event.device)
    
    # 2. Format input for model: [[action, device, price]]
    features = np.array([[action_enc, device_enc, event.price]])
    
    # 3. Predict probability scores for each class
    # [Probability of Low, Probability of High, Probability of Completed]
    probabilities = model.predict_proba(features)[0]
    
    # Let's extract the probability of it being a "High Intent/Risk" action (Class 1)
    high_intent_score = float(probabilities[1])
    
    return {
        "calculated_risk_score": round(high_intent_score, 4),
        "model_version": "v1.0.0"
    }