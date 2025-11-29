import subprocess
import time
import sys
import os

# Paths to service scripts
BASE_DIR = os.path.join("src")
SERVICES = [
    {"name": "External Provider", "cmd": ["python", os.path.join(BASE_DIR, "external_provider", "app.py")]},
    {"name": "PubSub Broker",     "cmd": ["python", os.path.join(BASE_DIR, "pubsub_broker", "app.py")]},
    {"name": "Quote Service",     "cmd": ["python", os.path.join(BASE_DIR, "quote_service", "app.py")]},
    {"name": "Shard 1",           "cmd": ["python", os.path.join(BASE_DIR, "historical_shard", "app.py"), "5011", "shard1.db"]},
    {"name": "Shard 2",           "cmd": ["python", os.path.join(BASE_DIR, "historical_shard", "app.py"), "5012", "shard2.db"]},
    {"name": "Shard Router",      "cmd": ["python", os.path.join(BASE_DIR, "shard_router", "app.py")]},
    {"name": "Aggregator",        "cmd": ["python", os.path.join(BASE_DIR, "aggregator", "app.py")]},
]

processes = []

def start_services():
    print("Starting services...")
    for service in SERVICES:
        print(f"Launching {service['name']}...")
        # Use creationflags=subprocess.CREATE_NEW_CONSOLE on Windows to open new windows
        # or just run in background. For visibility, let's run in background but pipe output?
        # Actually, for a demo, separate windows are nice, but might be annoying to close.
        # Let's run them as subprocesses and kill them on exit.
        p = subprocess.Popen(service["cmd"], cwd=os.getcwd())
        processes.append(p)
        time.sleep(1) # Wait a bit for startup

    print("\nAll services started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    start_services()
