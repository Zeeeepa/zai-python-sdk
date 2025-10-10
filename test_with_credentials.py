#!/usr/bin/env python3
"""
Test Z.AI API with ACTUAL CREDENTIALS - No more guest tokens!
"""

import os
import sys
import json
import time
import uuid
import requests

print("="*70)
print("🔐 Z.AI API Test - WITH REAL CREDENTIALS")
print("="*70)
print()

# Get credentials from environment
EMAIL = os.getenv("ZAI_EMAIL", "developer@pixelium.uk")
PASSWORD = os.getenv("ZAI_PASSWORD", "developer123?")
API_KEY = os.getenv("ZAI_API_KEY", "deb21352b03a40d59eb80c330dadc530.YajyK4xUtogbCVGR")

print(f"📧 Email: {EMAIL}")
print(f"🔑 Using API Key: {API_KEY[:20]}...")
print()

# Step 1: Login with credentials
print("="*70)
print("🔐 Step 1: Logging in with credentials...")
print("="*70)

login_url = "https://chat.z.ai/api/v1/auths/signin"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Origin": "https://chat.z.ai",
    "Referer": "https://chat.z.ai/"
}

login_payload = {
    "email": EMAIL,
    "password": PASSWORD
}

try:
    login_response = requests.post(login_url, headers=headers, json=login_payload, timeout=15)
    print(f"Status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        auth_data = login_response.json()
        print("✅ Login successful!")
        print(f"Response keys: {list(auth_data.keys())}")
        
        # Try to extract token
        token = auth_data.get("token") or auth_data.get("access_token") or auth_data.get("jwt")
        
        if token:
            print(f"✅ Got authenticated token: {token[:30]}...")
        else:
            print("⚠️ No token in response, trying API key...")
            token = API_KEY
            
    else:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text[:500]}")
        print()
        print("⚠️ Trying API key directly...")
        token = API_KEY
        
except Exception as e:
    print(f"❌ Login error: {e}")
    print("⚠️ Trying API key directly...")
    token = API_KEY

print()

# Step 2: Create chat with authenticated token
print("="*70)
print("💬 Step 2: Creating chat with authenticated token...")
print("="*70)
print()

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

message_id = str(uuid.uuid4())
timestamp = int(time.time())

chat_payload = {
    "chat": {
        "id": "",
        "title": "API Test - Authenticated",
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
    chat_response = requests.post(chat_url, headers=chat_headers, json=chat_payload, timeout=30)
    
    print(f"Status: {chat_response.status_code}")
    print()
    
    if chat_response.status_code == 200:
        chat_data = chat_response.json()
        print("✅ Chat created!")
        print(f"Chat ID: {chat_data.get('id')}")
        print()
        
        # Step 3: Get completion
        print("="*70)
        print("💬 Step 3: Getting completion with authenticated token...")
        print("="*70)
        print()
        
        actual_chat_id = chat_data.get('id')
        current_message_id = chat_data['chat']['history']['currentId']
        
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
        
        print(f"🚀 Requesting completion (authenticated user)...")
        completion_response = requests.post(
            completion_url,
            headers=chat_headers,
            json=completion_payload,
            timeout=45
        )
        
        print(f"Status: {completion_response.status_code}")
        print()
        
        if completion_response.status_code == 200:
            result_data = completion_response.json()
            
            # Extract the assistant's reply
            if 'choices' in result_data and len(result_data['choices']) > 0:
                content = result_data['choices'][0].get('message', {}).get('content', '')
                if content:
                    print("="*70)
                    print("✅ ASSISTANT RESPONSE (AUTHENTICATED):")
                    print("="*70)
                    print(content)
                    print("="*70)
                    print()
                    print("🎉 SUCCESS! Got real response with credentials!")
                else:
                    print("⚠️ No content in completion")
                    print(json.dumps(result_data, indent=2, ensure_ascii=False)[:1000])
            else:
                print("⚠️ Unexpected completion format:")
                print(json.dumps(result_data, indent=2, ensure_ascii=False)[:1000])
        else:
            print(f"❌ Completion failed: {completion_response.status_code}")
            print(f"Response: {completion_response.text[:1000]}")
    else:
        print(f"❌ Chat creation failed: {chat_response.status_code}")
        print(f"Response: {chat_response.text[:1000]}")
        
except Exception as e:
    import traceback
    print(f"❌ Error: {e}")
    print(traceback.format_exc())

print()
print("="*70)
print("✅ Test Complete!")
print("="*70)

