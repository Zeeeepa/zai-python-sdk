#!/usr/bin/env python3
"""
Test script to verify actual OpenAI API responses from Z.AI server
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("=" * 70)
    print("🧪 Test 1: Health Check")
    print("=" * 70)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"\n✅ Status: {response.status_code}")
    print(f"📦 Response: {response.json()}\n")
    return response.status_code == 200

def test_models():
    """Test models endpoint"""
    print("=" * 70)
    print("🧪 Test 2: List Models")
    print("=" * 70)
    
    response = requests.get(f"{BASE_URL}/v1/models")
    data = response.json()
    
    print(f"\n✅ Status: {response.status_code}")
    print(f"📋 Available Models:")
    for model in data.get('data', []):
        print(f"   - {model['id']}")
    print()
    return response.status_code == 200

def test_chat_streaming():
    """Test streaming chat completion"""
    print("=" * 70)
    print("🧪 Test 3: Chat Completion (Streaming)")
    print("=" * 70)
    
    payload = {
        "model": "GLM-4.5",
        "messages": [
            {"role": "user", "content": "Count from 1 to 5, separated by commas."}
        ],
        "stream": True,
        "max_tokens": 100
    }
    
    print(f"\n📤 Request:")
    print(f"   Model: {payload['model']}")
    print(f"   Message: {payload['messages'][0]['content']}")
    print(f"\n💬 AI Response (streaming):")
    print("   ", end="", flush=True)
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            stream=True,
            timeout=30
        )
        
        full_response = ""
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]  # Remove 'data: ' prefix
                    
                    if data_str == '[DONE]':
                        print("\n\n✅ Stream complete!\n")
                        break
                    
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get('choices', [{}])[0].get('delta', {})
                        content = delta.get('content', '')
                        
                        if content:
                            print(content, end="", flush=True)
                            full_response += content
                    except json.JSONDecodeError:
                        pass
        
        if full_response:
            print(f"\n📊 Total characters received: {len(full_response)}")
            return True
        else:
            print("\n❌ No response received")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_chat_non_streaming():
    """Test non-streaming chat completion"""
    print("=" * 70)
    print("🧪 Test 4: Chat Completion (Non-Streaming)")
    print("=" * 70)
    
    payload = {
        "model": "GLM-4.5",
        "messages": [
            {"role": "user", "content": "What is 2+2? Answer with just the number."}
        ],
        "stream": False,
        "max_tokens": 50
    }
    
    print(f"\n📤 Request:")
    print(f"   Model: {payload['model']}")
    print(f"   Message: {payload['messages'][0]['content']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            message = data.get('choices', [{}])[0].get('message', {})
            content = message.get('content', '')
            usage = data.get('usage', {})
            
            print(f"\n💬 AI Response: {content}")
            print(f"\n📊 Usage Stats:")
            print(f"   - Prompt tokens: {usage.get('prompt_tokens', 0)}")
            print(f"   - Completion tokens: {usage.get('completion_tokens', 0)}")
            print(f"   - Total tokens: {usage.get('total_tokens', 0)}")
            print()
            return True
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def test_openai_sdk():
    """Test with OpenAI Python SDK"""
    print("=" * 70)
    print("🧪 Test 5: OpenAI SDK Compatibility")
    print("=" * 70)
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url=f"{BASE_URL}/v1",
            api_key="not-needed"
        )
        
        print("\n📤 Sending request via OpenAI SDK...")
        
        response = client.chat.completions.create(
            model="GLM-4.5",
            messages=[
                {"role": "user", "content": "Say 'Hello from OpenAI SDK!' in one sentence."}
            ],
            max_tokens=100
        )
        
        print(f"\n💬 AI Response: {response.choices[0].message.content}")
        print(f"\n📊 Usage: {response.usage}")
        print()
        return True
        
    except ImportError:
        print("\n⚠️  OpenAI SDK not installed")
        print("   Install with: pip install openai\n")
        return None
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🚀 Z.AI OpenAI Server - Live API Response Test")
    print("=" * 70)
    print()
    
    # Wait for server to be ready
    print("⏳ Checking server status...")
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!\n")
                break
        except:
            time.sleep(1)
    else:
        print("❌ Server is not responding!")
        print("   Start the server with: ./start.sh\n")
        return
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("List Models", test_models()))
    results.append(("Streaming Chat", test_chat_streaming()))
    results.append(("Non-Streaming Chat", test_chat_non_streaming()))
    
    sdk_result = test_openai_sdk()
    if sdk_result is not None:
        results.append(("OpenAI SDK", sdk_result))
    
    # Summary
    print("=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    print()
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}: {name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Server is working correctly!\n")
    else:
        print("\n⚠️  Some tests failed. Check server logs for details.\n")
    
    print("=" * 70)

if __name__ == "__main__":
    main()

