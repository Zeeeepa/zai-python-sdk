#!/usr/bin/env python3
"""
Z.AI OpenAI-Compatible API Server
Provides OpenAI-style API endpoints using Z.AI backend
"""

import sys
import os
import json
import time
import logging
from typing import Dict, Any, List
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading
import signal

# Import Z.AI SDK (installed package)
try:
    from zai import ZAIClient, ZAIError
except ImportError as e:
    print(f"Error: Could not import Z.AI SDK. Please install it with: pip install -e .")
    print(f"Details: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global Z.AI client
zai_client = None
server_port = 8080


class OpenAIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OpenAI-compatible API"""
    
    def log_message(self, format, *args):
        """Override to use logger instead of stderr"""
        logger.info(format % args)
    
    def send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_error_response(self, message: str, status_code: int = 500):
        """Send error response"""
        error_data = {
            "error": {
                "message": message,
                "type": "server_error",
                "code": status_code
            }
        }
        self.send_json_response(error_data, status_code)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.handle_health_check()
        elif parsed_path.path == '/v1/models':
            self.handle_list_models()
        else:
            self.send_error_response(f"Unknown endpoint: {parsed_path.path}", 404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/v1/chat/completions':
            self.handle_chat_completions()
        else:
            self.send_error_response(f"Unknown endpoint: {parsed_path.path}", 404)
    
    def handle_health_check(self):
        """Health check endpoint"""
        self.send_json_response({
            "status": "healthy",
            "service": "Z.AI OpenAI-Compatible API",
            "port": server_port
        })
    
    def handle_list_models(self):
        """List available models endpoint"""
        models = [
            {
                "id": "glm-4.5v",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "z.ai",
                "permission": [],
                "root": "glm-4.5v",
                "parent": None
            },
            {
                "id": "0727-360B-API",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "z.ai",
                "permission": [],
                "root": "0727-360B-API",
                "parent": None
            },
            {
                "id": "GLM-4.5",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "z.ai",
                "permission": [],
                "root": "GLM-4.5",
                "parent": None
            }
        ]
        
        response_data = {
            "object": "list",
            "data": models
        }
        
        self.send_json_response(response_data)
    
    def handle_chat_completions(self):
        """Handle chat completions endpoint"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            request_data = json.loads(body.decode())
            
            logger.info(f"📨 Received request: model={request_data.get('model', 'default')}, "
                       f"messages={len(request_data.get('messages', []))}")
            
            # Extract parameters
            messages = request_data.get('messages', [])
            model = request_data.get('model', 'glm-4.5v')
            temperature = request_data.get('temperature', 0.7)
            max_tokens = request_data.get('max_tokens', 1000)
            stream = request_data.get('stream', False)
            
            if not messages:
                self.send_error_response("No messages provided", 400)
                return
            
            # Get last user message
            user_message = ""
            for msg in reversed(messages):
                if msg.get('role') == 'user':
                    user_message = msg.get('content', '')
                    break
            
            if not user_message:
                self.send_error_response("No user message found", 400)
                return
            
            # Call Z.AI
            logger.info(f"🤖 Calling Z.AI with message: {user_message[:50]}...")
            
            response = zai_client.simple_chat(
                message=user_message,
                model=model,
                enable_thinking=False,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Format OpenAI-style response
            openai_response = {
                "id": f"chatcmpl-{int(time.time() * 1000)}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response.content
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": response.usage.get('prompt_tokens', 0) if response.usage else 0,
                    "completion_tokens": response.usage.get('completion_tokens', 0) if response.usage else 0,
                    "total_tokens": response.usage.get('total_tokens', 0) if response.usage else 0
                }
            }
            
            logger.info(f"✅ Response generated successfully")
            logger.info(f"📝 Content preview: {response.content[:100]}...")
            
            self.send_json_response(openai_response)
            
        except ZAIError as e:
            logger.error(f"❌ Z.AI Error: {e}")
            self.send_error_response(str(e), 500)
        except Exception as e:
            logger.error(f"❌ Server Error: {e}", exc_info=True)
            self.send_error_response(str(e), 500)


def initialize_client():
    """Initialize Z.AI client"""
    global zai_client
    
    logger.info("🔧 Initializing Z.AI client...")
    
    try:
        zai_client = ZAIClient(auto_auth=True, verbose=False)
        logger.info(f"✅ Client initialized with token: {zai_client.token[:20]}...")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize client: {e}")
        return False


def run_server(port: int = 8080):
    """Run HTTP server"""
    global server_port
    server_port = port
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, OpenAIHandler)
    
    logger.info(f"")
    logger.info(f"{'='*70}")
    logger.info(f"🚀 Z.AI OpenAI-Compatible API Server")
    logger.info(f"{'='*70}")
    logger.info(f"")
    logger.info(f"📍 Server running on: http://localhost:{port}")
    logger.info(f"")
    logger.info(f"📚 Available endpoints:")
    logger.info(f"   • GET  /health              - Health check")
    logger.info(f"   • GET  /v1/models           - List available models")
    logger.info(f"   • POST /v1/chat/completions - Chat completions")
    logger.info(f"")
    logger.info(f"💡 OpenAI API usage example:")
    logger.info(f"   base_url = 'http://localhost:{port}/v1'")
    logger.info(f"")
    logger.info(f"🧪 Test with curl:")
    logger.info(f"   curl http://localhost:{port}/health")
    logger.info(f"")
    logger.info(f"{'='*70}")
    logger.info(f"")
    
    # Graceful shutdown handler
    def signal_handler(sig, frame):
        logger.info("\n🛑 Shutting down server...")
        httpd.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
    finally:
        httpd.server_close()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Z.AI OpenAI-Compatible API Server')
    parser.add_argument('--port', type=int, default=8080, help='Port to run server on (default: 8080)')
    args = parser.parse_args()
    
    # Initialize client
    if not initialize_client():
        logger.error("Failed to initialize Z.AI client. Exiting.")
        sys.exit(1)
    
    # Run server
    run_server(args.port)


if __name__ == "__main__":
    main()
