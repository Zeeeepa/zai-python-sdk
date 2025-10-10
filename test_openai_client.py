#!/usr/bin/env python3
"""
Use the ACTUAL OpenAI Python client to test Z.AI
"""

import os
import sys
import time
import requests
from openai import OpenAI

EMAIL = os.getenv("ZAI_EMAIL", "developer@pixelium.uk")
PASSWORD = os.getenv("ZAI_PASSWORD", "developer123?")

# First, get a real token
print("🔐 Getting authentication token...")
login_url = "https://chat.z.ai/api/v1/auths/signin"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
}

login_response = requests.post(login_url, headers=headers, json={"email": EMAIL, "password": PASSWORD}, timeout=15)

if login_response.status_code == 200:
    auth_data = login_response.json()
    token = auth_data.get("token")
    print(f"✅ Got token: {token[:30]}...")
else:
    print(f"❌ Login failed: {login_response.status_code}")
    sys.exit(1)

print()

# Set up the client to point at Z.AI with our real token
client = OpenAI(
    api_key=token,  # Use the real authenticated token
    base_url="https://chat.z.ai/api"
)

print("="*70)
print("🔥 USING OPENAI CLIENT TO ASK: WHAT IS YOUR MODEL NAME?")
print("="*70)
print()

question = "What is your model name? Answer in one short sentence."

print(f"📝 Question: {question}")
print()

max_attempts = 30
for attempt in range(1, max_attempts + 1):
    print("="*70)
    print(f"🚀 Attempt {attempt}/{max_attempts}")
    print("="*70)
    print()
    
    try:
        response = client.chat.completions.create(
            model="glm-4.5v",
            messages=[
                {"role": "user", "content": question}
            ],
            max_tokens=100,
            temperature=0.7
        )
        
        print()
        print("="*70)
        print("✅ ✅ ✅ GOT THE FUCKING RESPONSE! ✅ ✅ ✅")
        print("="*70)
        print()
        print(f"Model: {response.model}")
        print(f"ID: {response.id}")
        print()
        print("QUESTION:")
        print(question)
        print()
        print("ANSWER:")
        print(response.choices[0].message.content)
        print()
        print("="*70)
        print()
        print("FULL RESPONSE:")
        print(response)
        print()
        print("="*70)
        print(f"✅ SUCCESS ON ATTEMPT {attempt}!")
        print("="*70)
        sys.exit(0)
        
    except Exception as e:
        print(f"⚠️ Error: {e}")
        
        if "busy" in str(e).lower():
            if attempt < max_attempts:
                wait_time = 5 + (attempt * 2)
                print(f"⏳ System busy, waiting {wait_time}s...")
                time.sleep(wait_time)
                print()
        else:
            print(f"Error type: {type(e).__name__}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response}")
            if hasattr(e, 'status_code'):
                print(f"Status code: {e.status_code}")
            if hasattr(e, 'body'):
                print(f"Body: {e.body}")
            sys.exit(1)

print()
print("="*70)
print(f"❌ Failed after {max_attempts} attempts")
print("="*70)
sys.exit(1)
