"""Simple script to run the OpenAI-compatible server."""

import uvicorn
from config import config

if __name__ == "__main__":
    print(f"🚀 Starting Z.AI OpenAI-Compatible API Server...")
    print(f"📍 Server will run at: http://{config.HOST}:{config.PORT}")
    print(f"📚 API Documentation: http://{config.HOST}:{config.PORT}/docs")
    print(f"🔧 Model mappings: {config.MODEL_MAPPINGS}")
    print()
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level="info"
    )

