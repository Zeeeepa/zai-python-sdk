#!/usr/bin/env python3
"""
Test script for Z.AI OpenAI-compatible server
"""

import os
import sys
import time
import json
import requests

# Server configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_models():
    """Test models list endpoint"""
    print("🔍 Testing /v1/models endpoint...")
    response = requests.get(f"{BASE_URL}/v1/models")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Found {len(data.get('data', []))} models:")
    for model in data.get('data', [])[:5]:  # Show first 5
        print(f"  - {model.get('id')}: {model.get('name', 'N/A')}")
    print()

def test_completion(stream=False):
    """Test chat completion endpoint"""
    mode = "streaming" if stream else "non-streaming"
    print(f"🔍 Testing {mode} completion...")
    
    payload = {
        "model": "GLM-4.5",
        "messages": [
            {"role": "user", "content": "What is 2+2? Answer in one sentence."}
        ],
        "stream": stream
    }
    
    if stream:
        # Streaming request
        with requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, stream=True) as response:
            print(f"Status: {response.status_code}")
            print("Response stream:")
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    print(f"  {line_str}")
                    if line_str.startswith("data: ") and line_str != "data: [DONE]":
                        try:
                            chunk = json.loads(line_str[6:])
                            if 'choices' in chunk and chunk['choices']:
                                delta = chunk['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    print(f"    Content: {delta['content']}")
                        except:
                            pass
    else:
        # Non-streaming request
        response = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response:")
            print(f"  ID: {data.get('id')}")
            print(f"  Model: {data.get('model')}")
            if 'choices' in data and data['choices']:
                message = data['choices'][0].get('message', {})
                print(f"  Content: {message.get('content', 'N/A')}")
        else:
            print(f"Error: {response.text}")
    print()

def main():
    """Run all tests"""
    print("=" * 70)
    print("🧪 Z.AI OpenAI Server Test Suite")
    print("=" * 70)
    print(f"📍 Base URL: {BASE_URL}")
    print()
    
    try:
        # Test health
        test_health()
        
        # Test models
        test_models()
        
        # Test non-streaming completion
        test_completion(stream=False)
        
        # Test streaming completion
        test_completion(stream=True)
        
        print("=" * 70)
        print("✅ All tests completed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

