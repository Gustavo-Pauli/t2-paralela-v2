import time
import requests
from flask import Flask, jsonify

app = Flask(__name__)

EXTERNAL_PROVIDER_URL = "http://localhost:5001"
BROKER_URL = "http://localhost:5002"

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=10):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failures = 0
        self.last_failure_time = 0
        self.last_success_price = {} # Cache for fallback

    def call(self, symbol):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                print("Circuit Breaker: Switching to HALF_OPEN")
            else:
                print("Circuit Breaker: OPEN. Returning fallback.")
                return self.fallback(symbol)

        try:
            # In HALF_OPEN, we try once. If it fails, we go back to OPEN.
            response = requests.get(f"{EXTERNAL_PROVIDER_URL}/price/{symbol}", timeout=2)
            response.raise_for_status()
            data = response.json()
            
            # Success! Reset breaker
            self.reset()
            self.last_success_price[symbol] = data['price']
            return data['price']
            
        except Exception as e:
            print(f"External call failed: {e}")
            self.record_failure()
            return self.fallback(symbol)

    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.state == "HALF_OPEN":
            self.state = "OPEN"
            print("Circuit Breaker: HALF_OPEN call failed. Switching back to OPEN.")
        elif self.failures >= self.failure_threshold:
            self.state = "OPEN"
            print("Circuit Breaker: Threshold reached. Switching to OPEN.")

    def reset(self):
        self.failures = 0
        self.state = "CLOSED"
        print("Circuit Breaker: Call successful. Switching to CLOSED.")

    def fallback(self, symbol):
        # Return last known price or a default
        return self.last_success_price.get(symbol, 0.0)

breaker = CircuitBreaker()

@app.route('/quote/<symbol>', methods=['GET'])
def get_quote(symbol):
    price = breaker.call(symbol)
    
    # Publish update to broker (fire and forget)
    try:
        requests.post(f"{BROKER_URL}/publish", json={
            "topic": symbol,
            "message": {"symbol": symbol, "price": price, "timestamp": time.time()}
        }, timeout=0.5)
    except:
        pass # Ignore broker failures for now
        
    return jsonify({
        "symbol": symbol, 
        "price": price, 
        "circuit_state": breaker.state,
        "source": "external" if breaker.state == "CLOSED" else "cache/fallback"
    })

@app.route('/health/circuit', methods=['GET'])
def circuit_status():
    return jsonify({"state": breaker.state, "failures": breaker.failures})

if __name__ == '__main__':
    app.run(port=5003, debug=True)
