from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'weather_data',  # Nom du topic
    bootstrap_servers='localhost:9093',  # Vérifie bien que c'est 9093
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='weather_group'
)

print("🎧 En attente de messages...")

for message in consumer:
    print(f"📩 Reçu : {message.value.decode('utf-8')}")

