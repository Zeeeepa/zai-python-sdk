#!/usr/bin/env python3
"""
Simple direct test of Z.AI API - bypasses package structure issues
"""

import sys
import json
import time
import requests

print("="*70)
print("🧪 Z.AI Direct API Test (No SDK)")
print("="*70)
print()

# Step 1: Get authentication token
print("🔐 Step 1: Getting guest authentication token...")
auth_url = "https://chat.z.ai/api/v1/auths/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

try:
    auth_response = requests.get(auth_url, headers=headers, timeout=10)
    if auth_response.status_code == 200:
        auth_data = auth_response.json()
        token = auth_data.get("token", "")
        if token:
            print(f"✅ Got token: {token[:30]}...")
        else:
            print("❌ No token in response")
            sys.exit(1)
    else:
        print(f"❌ Auth failed: {auth_response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Auth error: {e}")
    sys.exit(1)

print()

# Step 2: Create chat
print("💬 Step 2: Creating new chat...")
chat_url = "https://chat.z.ai/api/v1/chats/new"
test_message = "What is 2+2? Answer in one short sentence."

chat_headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate",
    "accept-language": "en-US,en;q=0.9",
    "authorization": f"Bearer {token}",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "origin": "https://chat.z.ai",
    "pragma": "no-cache",
    "referer": "https://chat.z.ai/",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "x-fe-version": "prod-fe-1.0.70"
}

# Build a proper Z.AI chat payload (not OpenAI format)
import uuid
chat_id = str(uuid.uuid4())
message_id = str(uuid.uuid4())
timestamp = int(time.time())

chat_payload = {
    "chat": {
        "id": "",
        "title": "API Test",
        "models": ["glm-4.5v"],
        "params": {},
        "history": {
            "messages": {
                message_id: {
                    "id": message_id,
                    "parentId": None,
                    "childrenIds": [],
                    "role": "user",
                    "content": test_message,
                    "timestamp": timestamp,
                    "models": ["glm-4.5v"]
                }
            },
            "currentId": message_id
        },
        "messages": [
            {
                "id": message_id,
                "parentId": None,
                "childrenIds": [],
                "role": "user",
                "content": test_message,
                "timestamp": timestamp,
                "models": ["glm-4.5v"]
            }
        ],
        "tags": [],
        "flags": [],
        "features": [
            {"type": "mcp", "server": "vibe-coding", "status": "hidden"},
            {"type": "mcp", "server": "ppt-maker", "status": "hidden"},
            {"type": "mcp", "server": "image-search", "status": "hidden"}
        ],
        "mcp_servers": [],
        "enable_thinking": False,
        "timestamp": timestamp
    }
}

print(f"📨 Sending: {test_message}")
print()

try:
    chat_response = requests.post(
        chat_url, 
        headers=chat_headers, 
        json=chat_payload,
        timeout=30
    )
    
    print("="*70)
    print("📥 Response Received")
    print("="*70)
    print()
    print(f"Status Code: {chat_response.status_code}")
    print()
    
    if chat_response.status_code == 200:
        try:
            chat_data = chat_response.json()
            print("📄 Chat Created Successfully!")
            print(f"Chat ID: {chat_data.get('id')}")
            print()
            
            # Step 3: Get completion
            print("="*70)
            print("💬 Step 3: Getting completion response...")
            print("="*70)
            print()
            
            actual_chat_id = chat_data.get('id')
            current_message_id = chat_data['chat']['history']['currentId']
            
            # Build completion request
            completion_url = "https://chat.z.ai/api/chat/completions"
            
            completion_payload = {
                "model": "glm-4.5v",
                "messages": [
                    {"role": "user", "content": test_message}
                ],
                "stream": False,
                "chatId": actual_chat_id,
                "parentMessageId": current_message_id
            }
            
            completion_response = requests.post(
                completion_url,
                headers=chat_headers,
                json=completion_payload,
                timeout=30
            )
            
            if completion_response.status_code == 200:
                result_data = completion_response.json()
                print("📄 Completion Response:")
                print(json.dumps(result_data, indent=2, ensure_ascii=False)[:2000])
                print()
                
                # Extract the assistant's reply
                if 'choices' in result_data and len(result_data['choices']) > 0:
                    content = result_data['choices'][0].get('message', {}).get('content', '')
                    if content:
                        print("="*70)
                        print("✅ ASSISTANT RESPONSE:")
                        print("="*70)
                        print(content)
                        print("="*70)
                    else:
                        print("⚠️ No content in completion")
                else:
                    print("⚠️ Unexpected completion format")
            else:
                print(f"❌ Completion failed: {completion_response.status_code}")
                print(f"Response: {completion_response.text[:500]}")
                
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
            print("Raw response text:")
            print(chat_response.text[:500])
    else:
        print(f"❌ Request failed: {chat_response.status_code}")
        print(f"Response: {chat_response.text[:500]}")
        
except Exception as e:
    import traceback
    print(f"❌ Request error: {e}")
    print(traceback.format_exc())
    sys.exit(1)

print()
print("="*70)
print("✅ Test Complete!")
print("="*70)
