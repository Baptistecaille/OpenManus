#!/usr/bin/env python3
"""
OpenManus Frontend - FastAPI web interface for OpenManus agent.

Usage:
    python frontend_app.py

The frontend will be available at:
    - http://0.0.0.0:8000 (default)
    - Or custom host/port from config.toml
"""

import uvicorn
from frontend_app import app

if __name__ == "__main__":
    import sys
    print("=" * 60)
    print("OpenManus Frontend")
    print("=" * 60)
    print("\nStarting web server...")
    print("The frontend will be available at http://0.0.0.0:8000")
    print("\nPress Ctrl+C to stop the server\n")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
