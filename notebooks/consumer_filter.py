from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='broker:9092',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

for message in consumer:
    tx = message.value
    
    if tx['amount'] > 1000:
        print(f"ALERT: transakcja {tx['tx_id']} na kwotę {tx['amount']} PLN w {tx['store']}, kategoria {tx['category']}, godzina {tx.get('hour', 'N/A')}")
    
