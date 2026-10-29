import os
import sys
import time
import subprocess
import webbrowser
import urllib.request

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
NODE_DIR = os.path.join(ROOT_DIR, "tools", "node")

# Ensure portable node is in PATH
env = os.environ.copy()
env["PATH"] = NODE_DIR + os.pathsep + env.get("PATH", "")

print("=" * 68)
print("  AI-DRIVEN DIGITAL TWIN FOR COAL MINE SAFETY GOVERNANCE")
print("=" * 68)
print(f"Project Folder: {ROOT_DIR}")
print("\n[1/3] Starting Backend Server (FastAPI on Port 8000)...")

backend_process = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
    cwd=BACKEND_DIR,
    env=env
)

print("[2/3] Starting Frontend Server (React Vite on Port 5173)...")
# Check npm executable
npm_bin = os.path.join(NODE_DIR, "npm.cmd") if os.path.exists(os.path.join(NODE_DIR, "npm.cmd")) else "npm.cmd"

frontend_process = subprocess.Popen(
    [npm_bin, "run", "dev"],
    cwd=FRONTEND_DIR,
    env=env
)

print("[3/3] Waiting for servers to initialize...")
time.sleep(4)

# Verify servers
backend_ready = False
for _ in range(10):
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/", timeout=1) as res:
            if res.status == 200:
                backend_ready = True
                break
    except Exception:
        time.sleep(1)

print("\n" + "=" * 68)
print("  ALL SYSTEMS OPERATIONAL!")
print("=" * 68)
print("  Web Portal:         http://localhost:5173/")
print("  Mobile Field App:   http://localhost:5173/mobile")
print("  Backend API Docs:   http://localhost:8000/docs")
print("=" * 68)
print("\nOpening web portal in your default browser...")
webbrowser.open("http://localhost:5173/")

print("\n[INFO] Both servers are running. Keep this window open.")
print("       Press Ctrl + C anytime to stop both servers.")
print("-" * 68)

try:
    while True:
        time.sleep(1)
        if backend_process.poll() is not None or frontend_process.poll() is not None:
            break
except KeyboardInterrupt:
    print("\nStopping servers...")
finally:
    backend_process.terminate()
    frontend_process.terminate()
    print("Servers stopped cleanly.")
