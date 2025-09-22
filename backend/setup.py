#!/usr/bin/env python3
"""
Setup script for Vietnamese AI Dubbing Backend
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"[SETUP] {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[OK] {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("Setting up Vietnamese AI Dubbing Backend")
    print("=" * 50)

    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("[ERROR] Python 3.8+ is required")
        sys.exit(1)

    print(f"[OK] Python {python_version.major}.{python_version.minor}.{python_version.micro}")

    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        print("[PACKAGE] Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv venv", "Create virtual environment"):
            sys.exit(1)

    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/Mac
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"

    # Upgrade pip
    if not run_command(f"{pip_cmd} install --upgrade pip", "Upgrade pip"):
        sys.exit(1)

    # Install dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Install Python dependencies"):
        sys.exit(1)

    # Run tests to verify installation
    print("[TEST] Running tests to verify installation...")
    try:
        result = subprocess.run([python_cmd, "-m", "pytest", "tests/", "-v"], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] All tests passed!")
        else:
            print("[WARNING]  Some tests failed, but installation completed:")
            print(result.stdout)
            print(result.stderr)
    except Exception as e:
        print(f"[WARNING]  Could not run tests: {e}")
        print("This is normal if pytest is not configured yet.")

    print("\n" + "=" * 50)
    print("[SUCCESS] Backend setup completed successfully!")
    print("[NOTE] To start the backend server:")
    print(f"   {python_cmd} main.py")
    print("[WEB] API will be available at: http://localhost:8000")
    print("[DOCS] API documentation: http://localhost:8000/docs")
    print("=" * 50)

if __name__ == "__main__":
    main()