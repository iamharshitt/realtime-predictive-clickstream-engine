import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# --- SIMULATE HISTORICAL TRAINING DATA ---
# Let's create dummy historical data for training:
# Features: [Action_Encoded, Device_Encoded, Price]
# Action mapping: 0=view, 1=add_to_cart, 2=purchase
# Device mapping: 0=Desktop, 1=Mobile, 2=Tablet

X_train = np.array([
    [0, 0, 100.0],  # View, Desktop, cheap item -> Low interest (0)
    [1, 1, 1200.0], # Add to cart, Mobile, expensive item -> High intent/Risk (1)
    [2, 0, 850.0],  # Purchase, Desktop, expensive -> Completed (2)
    [0, 2, 50.0],   # View, Tablet, cheap -> Low interest (0)
    [1, 1, 950.0],  # Add to cart, Mobile, expensive -> High intent/Risk (1)
    [0, 0, 1400.0], # View, Desktop, expensive -> Mid interest (0)
    [1, 0, 1100.0], # Add to cart, Desktop, expensive -> High intent/Risk (1)
    [2, 1, 150.0]   # Purchase, Mobile, cheap -> Completed (2)
])

# Labels: 0 = Low Risk, 1 = High Conversion Intent / System Exposure, 2 = Completed Transaction
y_train = np.array([0, 1, 2, 0, 1, 0, 1, 2])

print("🤖 Training the production Machine Learning model...")
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

# Save the trained model to a file using pickle (Serialization)
with open("ml_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("💾 Model successfully trained and saved as 'ml_model.pkl'!")