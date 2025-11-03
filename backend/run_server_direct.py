# -*- coding: utf-8 -*-
"""Run server directly without uvicorn reload"""
import sys
sys.path.insert(0, 'C:/Users/natha/AWS_HACKATHON2025/backend')

if __name__ == "__main__":
    import uvicorn
    from app.main import app

    print("Starting server on port 8001 (without reload)...")
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
