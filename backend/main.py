"""
IITIAN AI - Main Backend Entrypoint
Supports direct pure Python server or FastAPI if available.
"""

import sys
from backend.config import HOST, PORT

def main():
    try:
        import uvicorn
        from fastapi import FastAPI
        # If FastAPI & Uvicorn are available, we can also expose an ASGI app
        print("Starting IITIAN with native server engine...")
        from backend.server import run_server
        run_server(HOST, PORT)
    except ImportError:
        from backend.server import run_server
        run_server(HOST, PORT)

if __name__ == "__main__":
    main()
