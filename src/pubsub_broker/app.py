import requests
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# In-memory subscription storage: { "topic": [ "url1", "url2" ] }
subscriptions = {}

def notify_subscriber(url, message):
    try:
        requests.post(url, json=message, timeout=1)
    except Exception as e:
        print(f"Failed to notify {url}: {e}")

@app.route('/subscribe', methods=['POST'])
def subscribe():
    data = request.json
    topic = data.get('topic')
    callback_url = data.get('callback_url')
    
    if not topic or not callback_url:
        return jsonify({"error": "Missing topic or callback_url"}), 400
        
    if topic not in subscriptions:
        subscriptions[topic] = []
    
    if callback_url not in subscriptions[topic]:
        subscriptions[topic].append(callback_url)
        
    return jsonify({"status": "subscribed", "topic": topic, "callback_url": callback_url})

@app.route('/publish', methods=['POST'])
def publish():
    data = request.json
    topic = data.get('topic')
    message = data.get('message')
    
    if not topic or not message:
        return jsonify({"error": "Missing topic or message"}), 400
        
    subscribers = subscriptions.get(topic, [])
    
    # Notify subscribers (could be async, but for simplicity we do it in threads or sequentially)
    # Using threads to avoid blocking the publisher
    for url in subscribers:
        threading.Thread(target=notify_subscriber, args=(url, message)).start()
        
    return jsonify({"status": "published", "subscriber_count": len(subscribers)})

if __name__ == '__main__':
    app.run(port=5002, debug=True)
