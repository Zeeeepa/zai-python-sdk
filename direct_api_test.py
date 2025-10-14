#!/usr/bin/env python3
"""
Direct API call to Z.AI to get actual response
Bypasses the buggy server.py and goes straight to Z.AI
"""

import requests
import json
import uuid
import time
import hmac
import hashlib
from urllib.parse import urlencode

def generate_signature(message_text: str, request_id: str, timestamp_ms: int, user_id: str, secret: str = "junjie") -> str:
    """Dual-layer HMAC-SHA256 signature."""
    r = str(timestamp_ms)
    e = f"requestId,{request_id},timestamp,{timestamp_ms},user_id,{user_id}"
    t = message_text or ""
    i = f"{e}|{t}|{r}"

    window_index = timestamp_ms // (5 * 60 * 1000)
    root_key = (secret or "junjie").encode("utf-8")
    derived_hex = hmac.new(root_key, str(window_index).encode("utf-8"), hashlib.sha256).hexdigest()
    signature = hmac.new(derived_hex.encode("utf-8"), i.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature

def get_guest_token():
    """Get guest token from Z.AI"""
    url = "https://chat.z.ai/api/v1/auths/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Origin": "https://chat.z.ai",
        "Referer": "https://chat.z.ai/"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        token = data.get('token', '')
        print(f"✅ Got token: {token[:50]}...")
        return token
    else:
        print(f"❌ Failed to get token: {response.status_code}")
        return None

def send_chat_request(token, message):
    """Send chat request directly to Z.AI"""
    chat_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())
    timestamp_ms = int(time.time() * 1000)
    user_id = "guest"
    
    # Generate signature
    signature = generate_signature(message, request_id, timestamp_ms, user_id)
    
    # Build URL with query parameters
    query_params = {
        "timestamp": timestamp_ms,
        "requestId": request_id,
        "user_id": user_id,
        "token": token or "",
        "current_url": f"https://chat.z.ai/c/{chat_id}",
        "pathname": f"/c/{chat_id}",
        "signature_timestamp": timestamp_ms,
    }
    url = f"https://chat.z.ai/api/chat/completions?{urlencode(query_params)}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/event-stream",
        "Origin": "https://chat.z.ai",
        "Referer": f"https://chat.z.ai/c/{chat_id}",
        "X-FE-Version": "prod-fe-1.0.142",
        "X-Signature": signature,
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }
    
    payload = {
        "stream": True,
        "model": "0727-360B-API",  # GLM-4.5
        "messages": [
            {"role": "user", "content": message}
        ],
        "params": {},
        "features": {
            "image_generation": False,
            "web_search": False,
            "auto_web_search": False,
            "preview_mode": False,
            "flags": [],
            "features": [],
            "enable_thinking": False
        },
        "background_tasks": {
            "title_generation": False,
            "tags_generation": False
        },
        "mcp_servers": [],
        "variables": {},
        "model_item": {
            "id": "0727-360B-API",
            "name": "GLM-4.5",
            "owned_by": "z.ai"
        },
        "chat_id": chat_id,
        "id": str(uuid.uuid4())
    }
    
    print(f"\n📤 Sending question: '{message}'")
    print(f"🔄 Waiting for response...\n")
    
    response = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        return None
    
    print("💬 AI Response:")
    print("-" * 70)
    
    # Parse streaming response
    full_response = ""
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                
                if data_str == '[DONE]' or not data_str:
                    continue
                
                try:
                    chunk = json.loads(data_str)
                    if chunk.get('type') == 'chat:completion':
                        data = chunk.get('data', {})
                        delta_content = data.get('delta_content', '')
                        
                        if delta_content:
                            print(delta_content, end='', flush=True)
                            full_response += delta_content
                            
                except json.JSONDecodeError:
                    pass
    
    print("\n" + "-" * 70)
    print(f"\n✅ Total response length: {len(full_response)} characters")
    
    return full_response

def main():
    print("=" * 70)
    print("🚀 Direct Z.AI API Test - Real Response Verification")
    print("=" * 70)
    print()
    
    # Get token
    print("🔐 Step 1: Getting authentication token...")
    token = get_guest_token()
    
    if not token:
        print("❌ Failed to get token. Exiting.")
        return
    
    print("✅ Token acquired successfully!")
    
    # Send question
    print("\n📝 Step 2: Sending question to AI...")
    response = send_chat_request(token, "What is your model?")
    
    if response:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Got actual AI response!")
        print("=" * 70)
        print()
        print("This proves:")
        print("  ✅ Authentication works")
        print("  ✅ API connection works")
        print("  ✅ Z.AI is responding")
        print("  ✅ Getting real AI-generated content")
        print()
    else:
        print("\n❌ Failed to get response")

if __name__ == "__main__":
    main()
