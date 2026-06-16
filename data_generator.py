import time
import random
import json
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer

fake = Faker()

PRODUCTS = {
    "Laptop": (800, 1500),
    "Smartphone": (400, 1000),
    "Headphones": (50, 250),
    "Smart Watch": (150, 400),
    "Keyboard": (30, 120)
}
ACTIONS = ["view", "add_to_cart", "purchase"]

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
TOPIC_NAME = 'ecommerce-events'

def generate_clickstream_event():
    product_name = random.choice(list(PRODUCTS.keys()))
    price_range = PRODUCTS[product_name]
    price = round(random.uniform(price_range[0], price_range[1]), 2)
    
    return {
        "user_id": f"user_{random.randint(10000, 99999)}",
        "ip_address": fake.ipv4(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "product": product_name,
        "price": price,
        "action": random.choice(ACTIONS),
        "device": random.choice(["Mobile", "Desktop", "Tablet"])
    }

if __name__ == "__main__":
    print(f"🚀 Pushing live data into Kafka topic '{TOPIC_NAME}'... Press Ctrl+C to stop.")
    try:
        while True:
            live_event = generate_clickstream_event()
            producer.send(TOPIC_NAME, value=live_event)
            print(f"📦 Sent to Kafka: {live_event['user_id']} - {live_event['action']} - {live_event['product']}")
            time.sleep(random.uniform(0.2, 1.0))
    except KeyboardInterrupt:
        print("\n🛑 Generator stopped.")
    finally:
        producer.close()