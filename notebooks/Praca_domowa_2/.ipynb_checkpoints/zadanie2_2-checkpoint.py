import requests

BASE_URL = "http://localhost:8001/score"

# Test normalna transakcja
r = requests.post(BASE_URL,
    json={"amount": 150, "is_electronics": 0, "tx_per_minute": 3})
print("Normalna:    ", r.json())

# Test podejrzana transakcja
r = requests.post(BASE_URL,
    json={"amount": 5500, "is_electronics": 1, "tx_per_minute": 12})
print("Podejrzana:  ", r.json())