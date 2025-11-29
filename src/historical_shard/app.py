import sqlite3
import sys
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_FILE = "shard.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, symbol TEXT, price REAL, timestamp REAL)''')
    conn.commit()
    conn.close()

@app.route('/transaction', methods=['POST'])
def add_transaction():
    data = request.json
    symbol = data.get('symbol')
    price = data.get('price')
    timestamp = data.get('timestamp')
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (symbol, price, timestamp) VALUES (?, ?, ?)", (symbol, price, timestamp))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "saved", "shard": DB_FILE})

@app.route('/transactions/<symbol>', methods=['GET'])
def get_transactions(symbol):
    limit = request.args.get('limit', 10)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT symbol, price, timestamp FROM transactions WHERE symbol=? ORDER BY timestamp DESC LIMIT ?", (symbol, limit))
    rows = c.fetchall()
    conn.close()
    
    result = [{"symbol": r[0], "price": r[1], "timestamp": r[2]} for r in rows]
    return jsonify(result)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python app.py <port> <db_file>")
        sys.exit(1)
        
    port = int(sys.argv[1])
    DB_FILE = sys.argv[2]
    init_db()
    app.run(port=port, debug=True)
