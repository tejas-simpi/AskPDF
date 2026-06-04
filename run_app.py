"""Run both the FastAPI backend and React frontend for development."""
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path


def main():
    """Start the FastAPI server and print instructions."""
    project_root = Path(__file__).parent

    # Check if frontend is built
    frontend_dir = project_root / "frontend"
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run(
            ["npm", "install"],
            cwd=str(frontend_dir),
            check=True,
            shell=True,
        )

    print("=" * 60)
    print("🚀 AskPDF — Development Setup")
    print("=" * 60)
    print()
    print("Start these two commands in separate terminals:")
    print()
    print("  1. Backend (FastAPI):")
    print(f"     python server.py")
    print()
    print("  2. Frontend (React + Vite):")
    print(f"     cd frontend && npm run dev")
    print()
    print("Then open: http://localhost:5173")
    print("=" * 60)
    print()
    print("Starting FastAPI server...")
    print()

    # Start FastAPI server
    try:
        subprocess.run(
            [sys.executable, str(project_root / "server.py")],
            check=True,
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
