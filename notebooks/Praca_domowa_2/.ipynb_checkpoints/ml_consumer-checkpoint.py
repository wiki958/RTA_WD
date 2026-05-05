from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime
import json, requests

consumer = KafkaConsumer('transactions', bootstrap_servers='broker:9092',
    auto_offset_reset='earliest', group_id='ml-scoring',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')))

alert_producer = KafkaProducer(bootstrap_servers='broker:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'))

API_URL = "http://localhost:8001/score"

print("Konsument uruchomiony, czekam na transakcje...\n")

for msg in consumer:
    tx = msg.value

    # 1. Wyciągnij cechy
    amount         = tx.get('amount', 0)
    is_electronics = tx.get('is_electronics', 0)
    tx_per_minute  = tx.get('tx_per_minute', 5)

    timestamp = tx.get('timestamp', datetime.utcnow().isoformat())
    try:
        hour = datetime.fromisoformat(timestamp).hour
    except Exception:
        hour = datetime.utcnow().hour

    features = {
        "amount": amount,
        "is_electronics": is_electronics,
        "tx_per_minute": tx_per_minute
    }

    # 2. Odpytaj API
    try:
        r = requests.post(API_URL, json=features, timeout=2)
        result = r.json()
    except Exception as e:
        print(f"[ERROR] Brak odpowiedzi z API: {e}")
        continue

    is_fraud          = result.get('is_fraud', False)
    fraud_probability = result.get('fraud_probability', 0.0)

    # 3. Alert jeśli fraud
    if is_fraud:
        alert = {
            "transaction_id":    tx.get('transaction_id', 'N/A'),
            "timestamp":         timestamp,
            "hour":              hour,
            "amount":            amount,
            "is_electronics":    is_electronics,
            "tx_per_minute":     tx_per_minute,
            "fraud_probability": fraud_probability
        }

        alert_producer.send('alerts', value=alert)
        alert_producer.flush()

        print(f" ALERT | id={alert['transaction_id']} | "
              f"amount={amount:.2f} | prob={fraud_probability:.2f} | "
              f"hour={hour}h | elektronika={'TAK' if is_electronics else 'NIE'}")
    else:
        print(f"   OK    | id={tx.get('transaction_id', 'N/A')} | "
              f"amount={amount:.2f} | prob={fraud_probability:.2f}")
