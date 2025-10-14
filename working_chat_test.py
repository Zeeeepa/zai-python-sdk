#!/usr/bin/env python3
"""
Working chat test using /api/v1/chats/new endpoint
This endpoint works WITHOUT signatures!
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
        token = data.get('token', '')
        return token
    return None

def send_chat_message(token, message):
    """Send chat using /api/v1/chats/new endpoint"""
    url = "https://chat.z.ai/api/v1/chats/new"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Origin": "https://chat.z.ai",
        "Referer": "https://chat.z.ai/",
        "X-FE-Version": "prod-fe-1.0.142"
    }
    
    message_id = str(uuid.uuid4())
    timestamp = int(time.time())
    
    payload = {
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
                "role": "user",
                "content": message
            }],
            "tags": []
        }
    }
    
    return requests.post(url, headers=headers, json=payload, timeout=30)

def get_chat_completion(token, chat_id, message_id):
    """Get completion from chat"""
    url = f"https://chat.z.ai/api/v1/chats/{chat_id}/completions"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/event-stream",
        "X-FE-Version": "prod-fe-1.0.142"
    }
    
    payload = {
        "messages": [message_id]
    }
    
    return requests.post(url, headers=headers, json=payload, stream=True, timeout=30)

def main():
    print("=" * 70)
    print("🚀 Z.AI Working Chat Test - /api/v1/chats/new Endpoint")
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
    
    # Step 2: Send message
    print("📝 Step 2: Sending question to AI...")
    message = "What is your model? Answer in one short sentence."
    print(f"📤 Question: '{message}'")
    print()
    
    response = send_chat_message(token, message)
    
    if response.status_code != 200:
        print(f"❌ Failed to create chat: {response.status_code}")
        print(response.text)
        return
    
    # Parse chat response
    chat_data = response.json()
    chat_id = chat_data.get('id')
    
    if not chat_id:
        print("❌ No chat ID in response")
        return
    
    print(f"✅ Chat created: {chat_id}")
    
    # Extract message ID
    history = chat_data.get('chat', {}).get('history', {})
    messages = history.get('messages', {})
    message_id = list(messages.keys())[0] if messages else None
    
    if not message_id:
        print("❌ No message ID found")
        return
    
    print(f"✅ Message ID: {message_id}")
    print()
    
    # Step 3: Get completion
    print("📥 Step 3: Getting AI response...")
    print("💬 AI Response:")
    print("-" * 70)
    
    completion_response = get_chat_completion(token, chat_id, message_id)
    
    if completion_response.status_code != 200:
        print(f"❌ Failed to get completion: {completion_response.status_code}")
        print(completion_response.text)
        return
    
    # Parse streaming response
    full_response = ""
    for line in completion_response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:].strip()
                
                if not data_str or data_str == '[DONE]':
                    continue
                
                try:
                    chunk = json.loads(data_str)
                    
                    # Extract content from different possible locations
                    if 'content' in chunk:
                        content = chunk['content']
                        print(content, end='', flush=True)
                        full_response += content
                    elif 'message' in chunk and 'content' in chunk['message']:
                        content = chunk['message']['content']
                        print(content, end='', flush=True)
                        full_response += content
                    elif 'delta' in chunk and 'content' in chunk['delta']:
                        content = chunk['delta']['content']
                        print(content, end='', flush=True)
                        full_response += content
                        
                except json.JSONDecodeError:
                    pass
    
    print()
    print("-" * 70)
    print()
    
    if full_response:
        print("=" * 70)
        print("✅ SUCCESS! Got actual AI response!")
        print("=" * 70)
        print()
        print(f"📊 Response length: {len(full_response)} characters")
        print(f"📝 Full response: {full_response}")
        print()
    else:
        print("⚠️  No content extracted from stream")
        print("Raw response received but parsing may need adjustment")

if __name__ == "__main__":
    main()

