import os
import json
import requests
import psycopg2
from dotenv import load_dotenv
from kafka import KafkaConsumer

# Load variables from secure .env file
load_dotenv()
DB_URI = os.getenv("SUPABASE_DB_URL")

if not DB_URI or "PASTE_YOUR" in DB_URI:
    raise ValueError("❌ Error: Please configure your valid SUPABASE_DB_URL inside the .env file.")

# Connect to Cloud Database
db_conn = psycopg2.connect(DB_URI)
cursor = db_conn.cursor()

# Create table and instantly send execution commit over network map
cursor.execute("""
CREATE TABLE IF NOT EXISTS processed_clicks (
    user_id TEXT,
    ip_address TEXT,
    timestamp TEXT,
    product TEXT,
    price REAL,
    action TEXT,
    device TEXT,
    is_high_value INTEGER,
    risk_score REAL
);
""")
db_conn.commit()
print("🗄️ Cloud PostgreSQL Database Table Initialized via Supabase.")

# Setup Consumer
consumer = KafkaConsumer(
    'ecommerce-events', bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest', value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

ML_API_URL = "http://127.0.0.1:8000/predict"
print("🏭 Stream Processor Online. Pushing data directly to the cloud...")

try:
    for message in consumer:
        event = message.value
        is_high_value = 1 if event['price'] > 800 else 0
        
        payload = {"action": event['action'], "device": event['device'], "price": event['price']}
        
        try:
            response = requests.post(ML_API_URL, json=payload, timeout=0.5)
            ai_score = response.json().get("calculated_risk_score", 0.0)
        except Exception:
            ai_score = 0.10  # Fallback
            
        # Write to Supabase Table
        cursor.execute("""
        INSERT INTO processed_clicks VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (event['user_id'], event['ip_address'], event['timestamp'], 
              event['product'], event['price'], event['action'], event['device'], 
              is_high_value, ai_score))
        
        db_conn.commit()  # Forces Cloud Database Write
        print(f"🚀 Cloud Pushed: {event['user_id']} | ML Score: {ai_score}")

except KeyboardInterrupt:
    print("\n🛑 Processor stopped.")
finally:
    cursor.close()
    db_conn.close()