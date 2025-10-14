#!/usr/bin/env python3
"""Test all signature variations against Z.AI API"""

import requests
import json
import uuid
import time
import hmac
import hashlib
from urllib.parse import urlencode

def get_guest_token():
    """Get guest token"""
    url = "https://chat.z.ai/api/v1/auths/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('token', '')
    return None

def generate_signature_v1(message_text, request_id, timestamp_ms, user_id, secret="junjie"):
    """Original from code"""
    r = str(timestamp_ms)
    e = f"requestId,{request_id},timestamp,{timestamp_ms},user_id,{user_id}"
    t = message_text or ""
    i = f"{e}|{t}|{r}"
    window_index = timestamp_ms // (5 * 60 * 1000)
    root_key = secret.encode("utf-8")
    derived_hex = hmac.new(root_key, str(window_index).encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.new(derived_hex.encode("utf-8"), i.encode("utf-8"), hashlib.sha256).hexdigest()

def generate_signature_v3(message_text, request_id, timestamp_ms, user_id, secret="junjie"):
    """Without final timestamp"""
    e = f"requestId,{request_id},timestamp,{timestamp_ms},user_id,{user_id}"
    t = message_text or ""
    i = f"{e}|{t}"
    window_index = timestamp_ms // (5 * 60 * 1000)
    root_key = secret.encode("utf-8")
    derived_hex = hmac.new(root_key, str(window_index).encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.new(derived_hex.encode("utf-8"), i.encode("utf-8"), hashlib.sha256).hexdigest()

def generate_signature_v4(message_text, request_id, timestamp_ms, user_id, secret="junjie"):
    """Seconds-based window"""
    r = str(timestamp_ms)
    e = f"requestId,{request_id},timestamp,{timestamp_ms},user_id,{user_id}"
    t = message_text or ""
    i = f"{e}|{t}|{r}"
    timestamp_sec = timestamp_ms // 1000
    window_index = timestamp_sec // (5 * 60)
    root_key = secret.encode("utf-8")
    derived_hex = hmac.new(root_key, str(window_index).encode("utf-8"), hashlib.sha256).hexdigest()
    return hmac.new(derived_hex.encode("utf-8"), i.encode("utf-8"), hashlib.sha256).hexdigest()

def test_signature(version_name, sig_func, token, message):
    """Test a signature function"""
    chat_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())
    timestamp_ms = int(time.time() * 1000)
    user_id = "guest"
    
    signature = sig_func(message, request_id, timestamp_ms, user_id)
    
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
        "X-FE-Version": "prod-fe-1.0.142",
        "X-Signature": signature,
        "Origin": "https://chat.z.ai",
        "Referer": f"https://chat.z.ai/c/{chat_id}",
    }
    
    payload = {
        "stream": True,
        "model": "0727-360B-API",
        "messages": [{"role": "user", "content": message}],
        "params": {},
        "features": {"image_generation": False, "web_search": False, "enable_thinking": False},
        "background_tasks": {"title_generation": False, "tags_generation": False},
        "mcp_servers": [],
        "variables": {},
        "model_item": {"id": "0727-360B-API", "name": "GLM-4.5", "owned_by": "z.ai"},
        "chat_id": chat_id,
        "id": str(uuid.uuid4())
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.status_code, response.text[:200]
    except Exception as e:
        return -1, str(e)[:200]

# Main test
print("="*70)
print("🔍 Testing All Signature Variations")
print("="*70)

token = get_guest_token()
if not token:
    print("❌ Failed to get token")
    exit(1)

print(f"✅ Got token: {token[:50]}...")
print()

message = "What is your model?"
versions = [
    ("V1 - Original", generate_signature_v1),
    ("V3 - No Final Timestamp", generate_signature_v3),
    ("V4 - Seconds Window", generate_signature_v4),
]

for version_name, sig_func in versions:
    print(f"Testing {version_name}...")
    status, response = test_signature(version_name, sig_func, token, message)
    
    if status == 200:
        print(f"  ✅ SUCCESS! Status: {status}")
        print(f"  Response: {response}")
        break
    else:
        print(f"  ❌ Failed - Status: {status}")
        print(f"  Error: {response}")
    print()

print("="*70)
