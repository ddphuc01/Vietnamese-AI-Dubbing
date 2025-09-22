#!/usr/bin/env python3
"""
Script to run both FastAPI backend and React frontend simultaneously
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# --- Configuration ---
# Use Path(__file__).parent to get the directory where the script is located
ROOT_DIR = Path(__file__).parent.resolve()
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
PYTHON_CMD = sys.executable
NPM_CMD = "npm" # Assuming npm is in the system's PATH

def check_requirements():
    """Check if required tools are installed"""
    print("Checking requirements...")

    # Check Python
    try:
        result = subprocess.run([PYTHON_CMD, "--version"], capture_output=True, text=True, check=True)
        print(f"[OK] Python: {result.stdout.strip()}")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("[ERROR] Python not found or not working. Please install Python 3.8+")
        return False

    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        print(f"[OK] Node.js: {result.stdout.strip()}")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("[ERROR] Node.js not found. Please install Node.js 18+")
        return False
    
    # Check npm
    try:
        result = subprocess.run([NPM_CMD, "--version"], capture_output=True, text=True, check=True)
        print(f"[OK] npm: {result.stdout.strip()}")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(f"[ERROR] {NPM_CMD} not found. Please install npm.")
        return False

    return True

def start_backend():
    """Start FastAPI backend using subprocesses with specified cwd"""
    print("[START] Starting FastAPI backend...")

    if not BACKEND_DIR.exists():
        print(f"[ERROR] Backend directory not found at: {BACKEND_DIR}")
        return None

    try:
        # Define paths for venv and python executable
        if os.name == 'nt':  # Windows
            venv_python = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
            pip_cmd = BACKEND_DIR / "venv" / "Scripts" / "pip.exe"
        else:  # Unix/Linux/Mac
            venv_python = BACKEND_DIR / "venv" / "bin" / "python"
            pip_cmd = BACKEND_DIR / "venv" / "bin" / "pip"

        # Create virtual environment if it doesn't exist
        if not (BACKEND_DIR / "venv").exists():
            print("[PACKAGE] Creating virtual environment...")
            subprocess.run([PYTHON_CMD, "-m", "venv", "venv"], check=True, cwd=BACKEND_DIR)

        # Install dependencies if requirements.txt exists
        requirements_path = BACKEND_DIR / "requirements.txt"
        if requirements_path.exists():
            print("[PACKAGE] Installing backend dependencies...")
            subprocess.run([str(pip_cmd), "install", "-r", "requirements.txt"], check=True, cwd=BACKEND_DIR)
        else:
            print("[WARN] requirements.txt not found, skipping dependency installation.")

        # Start backend server
        print(f"[INFO] Starting backend server with {venv_python}")
        backend_process = subprocess.Popen(
            [str(venv_python), "main.py"],
            cwd=BACKEND_DIR
        )

        print(f"[OK] FastAPI backend started on http://localhost:8000")
        return backend_process

    except Exception as e:
        print(f"[ERROR] Failed to start backend: {e}")
        return None

def start_frontend():
    """Start React frontend using subprocesses with specified cwd"""
    print("[FRONTEND] Starting React frontend...")

    if not FRONTEND_DIR.exists():
        print(f"[ERROR] Frontend directory not found at {FRONTEND_DIR}")
        return None

    try:
        # Install frontend dependencies if node_modules doesn't exist
        if not (FRONTEND_DIR / "node_modules").exists():
            print("[PACKAGE] Installing frontend dependencies...")
            # Use shell=True for npm on Windows
            shell_on_windows = True if os.name == 'nt' else False
            subprocess.run([NPM_CMD, "install"], check=True, cwd=FRONTEND_DIR, shell=shell_on_windows)
        else:
            print("[PACKAGE] Frontend dependencies already installed, skipping setup...")

        # Start frontend development server
        print("[INFO] Starting frontend development server...")
        # Use shell=True for npm on Windows
        shell_on_windows = True if os.name == 'nt' else False
        frontend_process = subprocess.Popen(
            [NPM_CMD, "run", "dev"],
            cwd=FRONTEND_DIR,
            shell=shell_on_windows
        )

        print("[OK] React frontend started on http://localhost:5173 (or next available port)")
        return frontend_process

    except Exception as e:
        print(f"[ERROR] Failed to start frontend: {e}")
        return None

def main():
    """Main function to run both servers"""
    print("Vietnamese AI Dubbing - Development Environment")
    print("=" * 50)

    if not check_requirements():
        print("\n[ERROR] Requirements check failed. Please install missing dependencies.")
        sys.exit(1)

    print("\n[INFO] Starting both backend and frontend servers...")

    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("[ERROR] Failed to start backend. Exiting.")
        sys.exit(1)

    # Wait a bit for backend to initialize
    time.sleep(5)

    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("[ERROR] Failed to start frontend. Exiting.")
        # Terminate backend process if frontend fails to start
        backend_process.terminate()
        backend_process.wait()
        sys.exit(1)

    print("\n" + "=" * 50)
    print("[SUCCESS] Both servers are running!")
    print(f"[FRONTEND] Frontend: http://localhost:5173")
    print(f"[API] Backend API: http://localhost:8000")
    print(f"[DOCS] API Documentation: http://localhost:8000/docs")
    print("=" * 50)
    print("[INFO] Press Ctrl+C to stop both servers.")

    try:
        # Wait for frontend process to exit
        frontend_process.wait()

    except KeyboardInterrupt:
        print("\n[STOP] KeyboardInterrupt received. Shutting down servers...")

    finally:
        # Terminate both processes
        print("[STOP] Terminating frontend process...")
        frontend_process.terminate()
        frontend_process.wait()
        print("[STOP] Terminating backend process...")
        backend_process.terminate()
        backend_process.wait()
        print("[OK] Both servers stopped successfully.")

if __name__ == "__main__":
    main()
