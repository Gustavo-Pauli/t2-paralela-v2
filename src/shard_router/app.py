import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuration of shards
SHARDS = [
    "http://localhost:5011",
    "http://localhost:5012"
]

def get_shard_url(symbol):
    # Simple hash-based partitioning
    shard_index = hash(symbol) % len(SHARDS)
    return SHARDS[shard_index]

@app.route('/transaction', methods=['POST'])
def route_transaction():
    data = request.json
    symbol = data.get('symbol')
    if not symbol:
        return jsonify({"error": "Symbol required"}), 400
        
    shard_url = get_shard_url(symbol)
    try:
        resp = requests.post(f"{shard_url}/transaction", json=data)
        return (resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        return jsonify({"error": f"Failed to reach shard {shard_url}: {str(e)}"}), 502

@app.route('/transactions/<symbol>', methods=['GET'])
def route_get_transactions(symbol):
    shard_url = get_shard_url(symbol)
    try:
        resp = requests.get(f"{shard_url}/transactions/{symbol}", params=request.args)
        return (resp.content, resp.status_code, resp.headers.items())
    except Exception as e:
        return jsonify({"error": f"Failed to reach shard {shard_url}: {str(e)}"}), 502

if __name__ == '__main__':
    app.run(port=5010, debug=True)
