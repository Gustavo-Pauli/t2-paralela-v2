import requests
import concurrent.futures
from flask import Flask, jsonify

app = Flask(__name__)

QUOTE_SERVICE_URL = "http://localhost:5003"
SHARD_ROUTER_URL = "http://localhost:5010"

def fetch_quote(symbol):
    try:
        resp = requests.get(f"{QUOTE_SERVICE_URL}/quote/{symbol}", timeout=2)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Quote fetch failed: {e}")
    return {"error": "Quote unavailable"}

def fetch_history(symbol):
    try:
        resp = requests.get(f"{SHARD_ROUTER_URL}/transactions/{symbol}?limit=10", timeout=2)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"History fetch failed: {e}")
    return []

@app.route('/combined/<symbol>', methods=['GET'])
def get_combined_data(symbol):
    # Scatter: Launch tasks in parallel
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_quote = executor.submit(fetch_quote, symbol)
        future_history = executor.submit(fetch_history, symbol)
        
        # Gather: Wait for results
        quote_data = future_quote.result()
        history_data = future_history.result()
        
    return jsonify({
        "symbol": symbol,
        "current_quote": quote_data,
        "history": history_data
    })

if __name__ == '__main__':
    app.run(port=5020, debug=True)
