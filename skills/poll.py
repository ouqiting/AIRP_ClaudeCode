"""Poll bridge server for new input, exit when found. Used by bash loop."""
import urllib.request
import json
import time
import sys

URL = "http://localhost:8765/api/pending"
INTERVAL = 30

while True:
    try:
        r = urllib.request.urlopen(URL, timeout=5)
        data = json.loads(r.read())
        if data.get("pending"):
            print("INPUT_READY")
            sys.exit(0)
    except Exception:
        pass
    time.sleep(INTERVAL)
