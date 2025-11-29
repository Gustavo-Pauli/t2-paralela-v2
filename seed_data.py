import requests
import time
import random

ROUTER_URL = "http://localhost:5010"

SYMBOLS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]

def seed():
    print("Seeding historical data...")
    for _ in range(20):
        symbol = random.choice(SYMBOLS)
        price = round(random.uniform(100, 3000), 2)
        timestamp = time.time() - random.randint(0, 10000)
        
        try:
            requests.post(f"{ROUTER_URL}/transaction", json={
                "symbol": symbol,
                "price": price,
                "timestamp": timestamp
            })
            print(f"Inserted {symbol} at {price}")
        except Exception as e:
            print(f"Failed to insert: {e}")

if __name__ == "__main__":
    seed()
