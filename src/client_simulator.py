import requests
from flask import Flask, request, jsonify
import sys
import threading
import time

app = Flask(__name__)

BROKER_URL = "http://localhost:5002"
MY_PORT = 6000
MY_URL = f"http://localhost:{MY_PORT}/callback"

@app.route('/callback', methods=['POST'])
def callback():
    data = request.json
    print(f"\n[CLIENT] Received update: {data}")
    return jsonify({"status": "received"})

def register_subscription(topic):
    # Wait a bit for server to start
    time.sleep(2)
    try:
        print(f"[CLIENT] Subscribing to {topic}...")
        resp = requests.post(f"{BROKER_URL}/subscribe", json={
            "topic": topic,
            "callback_url": MY_URL
        })
        print(f"[CLIENT] Subscription response: {resp.json()}")
    except Exception as e:
        print(f"[CLIENT] Failed to subscribe: {e}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        topic = sys.argv[1]
        threading.Thread(target=register_subscription, args=(topic,)).start()
        
    print(f"[CLIENT] Listening on port {MY_PORT}...")
    # Use 0.0.0.0 to ensure it listens on all interfaces, including localhost
    app.run(host='0.0.0.0', port=MY_PORT)
