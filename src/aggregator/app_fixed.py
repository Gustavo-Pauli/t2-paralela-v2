import requests
import concurrent.futures
from flask import Flask, jsonify
import sys

app = Flask(__name__)

# Use 127.0.0.1 to avoid potential localhost resolution issues on Windows
QUOTE_SERVICE_URL = "http://127.0.0.1:5003"
SHARD_ROUTER_URL = "http://127.0.0.1:5010"

def fetch_quote(symbol):
    try:
        print(f"Fetching quote for {symbol} from {QUOTE_SERVICE_URL}...", file=sys.stderr)
        resp = requests.get(f"{QUOTE_SERVICE_URL}/quote/{symbol}", timeout=2)
        print(f"Quote response: {resp.status_code}", file=sys.stderr)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Quote fetch failed: {e}", file=sys.stderr)
    return {"error": "Quote unavailable"}

def fetch_history(symbol):
    try:
        print(f"Fetching history for {symbol} from {SHARD_ROUTER_URL}...", file=sys.stderr)
        resp = requests.get(f"{SHARD_ROUTER_URL}/transactions/{symbol}?limit=10", timeout=2)
        print(f"History response: {resp.status_code}", file=sys.stderr)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"History fetch failed: {e}", file=sys.stderr)
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
    print("Starting Fixed Aggregator on 5021...", file=sys.stderr)
    app.run(port=5021, debug=True)
