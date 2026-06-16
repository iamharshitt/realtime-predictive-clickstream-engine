import json
import sqlite3
import requests
from kafka import KafkaConsumer

# Connect to database
db_conn = sqlite3.connect('analytics.db', isolation_level=None)
cursor = db_conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS processed_clicks (
    user_id TEXT, ip_address TEXT, timestamp TEXT, product TEXT, 
    price REAL, action TEXT, device TEXT, is_high_value INTEGER, risk_score REAL
)
""")

consumer = KafkaConsumer(
    'ecommerce-events', bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest', value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

ML_API_URL = "http://127.0.0.1:8000/predict"
print("🏭 Stream Processor Online. Communicating with live ML Microservice...")

try:
    for message in consumer:
        event = message.value
        is_high_value = 1 if event['price'] > 800 else 0
        
        # --- NEW: LIVE MACHINE LEARNING INFERENCE ---
        # Prepare the payload for our FastAPI server
        payload = {
            "action": event['action'],
            "device": event['device'],
            "price": event['price']
        }
        
        try:
            # Hit our local microservice to fetch a real-time predictive score
            response = requests.post(ML_API_URL, json=payload, timeout=0.5)
            ai_score = response.json().get("calculated_risk_score", 0.0)
        except Exception as e:
            print(f"⚠️ ML Service unreachable, falling back to baseline. Error: {e}")
            ai_score = 0.10 # Fallback default
            
        # Write to our analytical data store
        cursor.execute("""
        INSERT INTO processed_clicks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (event['user_id'], event['ip_address'], event['timestamp'], 
              event['product'], event['price'], event['action'], event['device'], 
              is_high_value, ai_score))
        
        print(f"🧠 [AI EVALUATION] User: {event['user_id']} | Price: ${event['price']} | ML Score: {ai_score}")

except KeyboardInterrupt:
    print("\n🛑 Processor stopped.")
finally:
    db_conn.close()