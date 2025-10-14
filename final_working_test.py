#!/usr/bin/env python3
"""
FINAL WORKING TEST - Gets actual AI response!
Uses the correct two-step process:
1. Create chat via /api/v1/chats/new
2. Get completion via /api/chat/completions with chatId
"""

import requests
import json
import uuid
import time

def get_guest_token():
    """Get guest token from Z.AI"""
    url = "https://chat.z.ai/api/v1/auths/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get('token', '')
    return None

def main():
    print("=" * 70)
    print("🚀 Z.AI FINAL WORKING TEST - Gets Actual AI Response!")
    print("=" * 70)
    print()
    
    # Step 1: Get token
    print("🔐 Step 1: Getting authentication token...")
    token = get_guest_token()
    
    if not token:
        print("❌ Failed to get token")
        return
    
    print(f"✅ Token: {token[:50]}...")
    print()
    
    # Step 2: Create chat
    print("📝 Step 2: Creating chat...")
    message = "What is your model? Answer in one short sentence."
    print(f"📤 Question: '{message}'")
    print()
    
    chat_url = "https://chat.z.ai/api/v1/chats/new"
    message_id = str(uuid.uuid4())
    timestamp = int(time.time())
    
    chat_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Origin": "https://chat.z.ai",
        "Referer": "https://chat.z.ai/",
        "X-FE-Version": "prod-fe-1.0.142"
    }
    
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
                        "content": message,
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
                "content": message,
                "timestamp": timestamp,
                "models": ["glm-4.5v"]
            }],
            "tags": []
        }
    }
    
    try:
        chat_response = requests.post(chat_url, headers=chat_headers, json=chat_payload, timeout=30)
        
        if chat_response.status_code != 200:
            print(f"❌ Failed to create chat: {chat_response.status_code}")
            print(chat_response.text[:500])
            return
        
        chat_data = chat_response.json()
        chat_id = chat_data.get('id')
        current_message_id = chat_data['chat']['history']['currentId']
        
        print(f"✅ Chat created: {chat_id}")
        print(f"✅ Message ID: {current_message_id}")
        print()
        
        # Step 3: Get completion using chatId
        print("📥 Step 3: Getting AI response...")
        print("💬 AI Response:")
        print("-" * 70)
        
        completion_url = "https://chat.z.ai/api/chat/completions"
        
        completion_payload = {
            "model": "glm-4.5v",
            "messages": [
                {"role": "user", "content": message}
            ],
            "stream": False,
            "chatId": chat_id,
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
            
            # Extract the assistant's reply
            if 'choices' in result_data and len(result_data['choices']) > 0:
                content = result_data['choices'][0].get('message', {}).get('content', '')
                
                if content:
                    print(content)
                    print("-" * 70)
                    print()
                    print("=" * 70)
                    print("✅ SUCCESS! Got actual AI response!")
                    print("=" * 70)
                    print()
                    print(f"📊 Response length: {len(content)} characters")
                    print(f"📝 AI said: {content}")
                    print()
                    print("This proves:")
                    print("  ✅ Authentication works")
                    print("  ✅ Chat creation works")
                    print("  ✅ Completion endpoint works")
                    print("  ✅ Getting real AI-generated responses!")
                    print()
                else:
                    print("⚠️  No content in response")
            else:
                print("⚠️  Unexpected response format")
                print(json.dumps(result_data, indent=2)[:500])
        else:
            print(f"❌ Completion failed: {completion_response.status_code}")
            print(completion_response.text[:500])
            
    except Exception as e:
        import traceback
        print(f"❌ Error: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()

