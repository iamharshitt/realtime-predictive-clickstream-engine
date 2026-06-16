from kafka import KafkaConsumer
import json

# Connect to Kafka and listen to our topic from the very beginning
consumer = KafkaConsumer(
    'ecommerce-events',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest', # Read older messages if we just started
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

print("🎧 Listening for messages from Kafka... (Waiting for data)")
for message in consumer:
    event = message.value
    print(f"📥 Successfully pulled from Kafka: {event}")