import os
import subprocess
import sys
import time
from pathlib import Path

SKILLS_DIR = Path(__file__).parent
STYLES_DIR = SKILLS_DIR / "styles"
PENDING_FILE = STYLES_DIR / ".pending"
INPUT_FILE = STYLES_DIR / "input.txt"
PORT = 8765

def kill_python_processes():
    """Kill all python processes related to skills (server.py, poll.py, handler.py)."""
    print("[1/3] Killing leftover python processes...")
    current_pid = str(os.getpid()) # 获取当前脚本的 PID
    
    try:
        # 使用 wmic 查找，直接在 WQL 语句中排除 cleanup.py
        result = subprocess.run(
            ["wmic", "process", "where",
             "CommandLine like '%skills%' and CommandLine not like '%cleanup.py%' and Name='python.exe'",
             "get", "ProcessId,CommandLine", "/format:csv"],
            capture_output=True, text=True, timeout=10
        )
        killed = 0
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line or "Node" in line or "CommandLine" in line:
                continue
            parts = line.split(",")
            if len(parts) >= 3:
                pid = parts[-1].strip()
                cmd = parts[-2].strip() if len(parts) > 2 else ""
                
                # 双重保险：确保不会杀死自己
                if pid.isdigit() and pid != current_pid:
                    subprocess.run(["taskkill", "/PID", pid, "/F"],
                                   capture_output=True, timeout=10)
                    short_cmd = cmd[:60] + "..." if len(cmd) > 60 else cmd
                    print(f"       Killed PID {pid}  ({short_cmd})")
                    killed += 1
        if killed == 0:
            print("       No leftover python processes found.")
    except Exception as e:
        print(f"       Error: {e}")

def free_port():
    """Kill any process listening on the configured port."""
    print(f"\n[2/3] Checking port {PORT}...")
    current_pid = str(os.getpid())
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True, timeout=10
        )
        killed = 0
        for line in result.stdout.splitlines():
            if f":{PORT}" in line and "LISTENING" in line:
                parts = line.split()
                pid = parts[-1]
                # 确保获取到的是数字，且不是系统进程0，也不是自己
                if pid.isdigit() and pid != "0" and pid != current_pid:
                    subprocess.run(["taskkill", "/PID", pid, "/F"],
                                   capture_output=True, timeout=10)
                    print(f"       Killed process on port {PORT} (PID {pid})")
                    killed += 1
        if killed == 0:
            print(f"       Port {PORT} is free.")
    except Exception as e:
        print(f"       Error: {e}")

def clear_pending():
    """Remove .pending file and clear input.txt."""
    print("\n[3/3] Cleaning pending residuals...")
    try:
        if PENDING_FILE.exists():
            PENDING_FILE.unlink()
            print("       Removed .pending file.")
        else:
            print("       No .pending file found.")

        if INPUT_FILE.exists():
            INPUT_FILE.write_text("", encoding="utf-8")
            print("       Cleared input.txt.")
        else:
            print("       No input.txt found.")
    except Exception as e:
        print(f"       Failed to clean residuals: {e}")

def main():
    print()
    print("=" * 44)
    print("  RP Bridge Cleanup")
    print("=" * 44)
    print()

    kill_python_processes()
    free_port()
    
    # 缓冲 1 秒，等待系统释放文件和端口锁
    time.sleep(1)
    
    clear_pending()

    print()
    print("=" * 44)
    print("  Cleanup complete. All clear.")
    print("=" * 44)
    print()
    sys.exit(0)

if __name__ == "__main__":
    main()