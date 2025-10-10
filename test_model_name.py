#!/usr/bin/env python3
"""
Ask Z.AI what its model name is - REAL FUCKING QUESTION
"""

import os
import sys
import json
import time
import uuid
import requests

EMAIL = os.getenv("ZAI_EMAIL", "developer@pixelium.uk")
PASSWORD = os.getenv("ZAI_PASSWORD", "developer123?")

print("="*70)
print("🔥 ASKING Z.AI: WHAT IS YOUR MODEL NAME?")
print("="*70)
print()

# Step 1: Login
print("🔐 Logging in...")
login_url = "https://chat.z.ai/api/v1/auths/signin"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Origin": "https://chat.z.ai",
    "Referer": "https://chat.z.ai/"
}

login_response = requests.post(login_url, headers=headers, json={"email": EMAIL, "password": PASSWORD}, timeout=15)

if login_response.status_code == 200:
    auth_data = login_response.json()
    token = auth_data.get("token")
    print(f"✅ Login successful!")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    sys.exit(1)

print()

# Prepare headers
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
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "x-fe-version": "prod-fe-1.0.70"
}

max_attempts = 20
attempt = 0

# THE ACTUAL FUCKING QUESTION
test_message = "What is your model name? Answer in one short sentence."

while attempt < max_attempts:
    attempt += 1
    
    print("="*70)
    print(f"🚀 Attempt {attempt}/{max_attempts}")
    print("="*70)
    print()
    
    # Create chat
    print("💬 Creating chat...")
    chat_url = "https://chat.z.ai/api/v1/chats/new"
    
    message_id = str(uuid.uuid4())
    timestamp = int(time.time())
    
    chat_payload = {
        "chat": {
            "id": "",
            "title": "What is your model name?",
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
            "messages": [{
                "id": message_id,
                "parentId": None,
                "childrenIds": [],
                "role": "user",
                "content": test_message,
                "timestamp": timestamp,
                "models": ["glm-4.5v"]
            }],
            "tags": [],
            "flags": [],
            "features": [],
            "mcp_servers": [],
            "enable_thinking": False,
            "timestamp": timestamp
        }
    }
    
    try:
        chat_response = requests.post(chat_url, headers=chat_headers, json=chat_payload, timeout=30)
        
        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            chat_id = chat_data.get('id')
            print(f"✅ Chat created: {chat_id}")
            
            # Get completion
            print("🎯 Asking Z.AI what its model name is...")
            print(f"📝 Question: {test_message}")
            print()
            
            completion_url = "https://chat.z.ai/api/chat/completions"
            
            completion_payload = {
                "model": "glm-4.5v",
                "messages": [{"role": "user", "content": test_message}],
                "stream": False,
                "chatId": chat_id,
                "parentMessageId": message_id
            }
            
            comp_response = requests.post(completion_url, headers=chat_headers, json=completion_payload, timeout=60)
            
            print(f"Status: {comp_response.status_code}")
            
            if comp_response.status_code == 200:
                result = comp_response.json()
                
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0].get('message', {}).get('content', '')
                    if content:
                        print()
                        print("="*70)
                        print("✅ ✅ ✅ GOT THE FUCKING RESPONSE! ✅ ✅ ✅")
                        print("="*70)
                        print()
                        print(f"QUESTION: {test_message}")
                        print()
                        print(f"ANSWER: {content}")
                        print()
                        print("="*70)
                        print()
                        print("FULL RESPONSE:")
                        print(json.dumps(result, indent=2))
                        print()
                        print("="*70)
                        print(f"✅ SUCCESS ON ATTEMPT {attempt}!")
                        print("="*70)
                        sys.exit(0)
                    else:
                        print("⚠️ Empty content, retrying...")
                else:
                    print("⚠️ Unexpected format:")
                    print(json.dumps(result, indent=2))
            else:
                print(f"⚠️ Response: {comp_response.text[:300]}")
        else:
            print(f"⚠️ Chat creation failed: {chat_response.status_code}")
            print(f"Response: {chat_response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    if attempt < max_attempts:
        wait_time = 5 + (attempt * 3)  # Longer backoff
        print(f"⏳ Waiting {wait_time}s before retry...")
        time.sleep(wait_time)
        print()

print()
print("="*70)
print(f"❌ Failed after {max_attempts} attempts - Z.AI still busy")
print("="*70)
sys.exit(1)

