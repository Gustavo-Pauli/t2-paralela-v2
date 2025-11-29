import random
import time
from flask import Flask, jsonify, request

app = Flask(__name__)

# Configuration to simulate failures
FAILURE_MODE = False
DELAY_SECONDS = 0

@app.route('/price/<symbol>', methods=['GET'])
def get_price(symbol):
    global FAILURE_MODE, DELAY_SECONDS
    
    if FAILURE_MODE:
        return jsonify({"error": "External service unavailable"}), 500
    
    if DELAY_SECONDS > 0:
        time.sleep(DELAY_SECONDS)
        
    # Simulate a price
    price = round(random.uniform(10.0, 1000.0), 2)
    return jsonify({"symbol": symbol, "price": price})

@app.route('/config', methods=['POST'])
def configure():
    global FAILURE_MODE, DELAY_SECONDS
    data = request.json
    FAILURE_MODE = data.get('failure_mode', FAILURE_MODE)
    DELAY_SECONDS = data.get('delay_seconds', DELAY_SECONDS)
    return jsonify({"status": "updated", "failure_mode": FAILURE_MODE, "delay_seconds": DELAY_SECONDS})

if __name__ == '__main__':
    app.run(port=5001, debug=True)
