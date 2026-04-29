"""
实时输入监听器
阻塞轮询 /api/pending，检测到用户输入后立即返回。
用法：python wait_for_input.py [timeout_seconds]
输出：用户输入文本（stdout）；超时则输出 TIMEOUT
"""
import sys
import time
import urllib.request
from pathlib import Path

PENDING_URL = "http://localhost:8765/api/pending"
INPUT_FILE = Path(__file__).parent / "styles" / "input.txt"
POLL_INTERVAL = 1  # 秒


def check_pending():
    try:
        resp = urllib.request.urlopen(PENDING_URL, timeout=5)
        data = resp.read().decode("utf-8")
        return '"pending":true' in data or '"pending": true' in data
    except Exception:
        return False


def main():
    timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    start = time.time()

    while True:
        elapsed = time.time() - start
        if elapsed >= timeout:
            print("TIMEOUT", flush=True)
            sys.exit(1)

        if check_pending():
            time.sleep(0.3)
            try:
                text = INPUT_FILE.read_text(encoding="utf-8").strip()
                if text:
                    print(text, flush=True)
                    sys.exit(0)
            except Exception:
                pass

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
