#!/usr/bin/env python3
"""
Wrapper script to run the OpenAI-compatible server.
This ensures proper Python path setup.
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Now import and run uvicorn
import uvicorn

if __name__ == "__main__":
    from server.config import config
    
    print(f"🚀 Starting Z.AI OpenAI-Compatible API Server...")
    print(f"📍 Server will run at: http://{config.HOST}:{config.PORT}")
    print(f"📚 API Documentation: http://{config.HOST}:{config.PORT}/docs")
    print(f"🔧 Model mappings:")
    for openai_model, zai_model in config.MODEL_MAPPINGS.items():
        print(f"   {openai_model} → {zai_model}")
    print()
    
    uvicorn.run(
        "server.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
        log_level="info"
    )

