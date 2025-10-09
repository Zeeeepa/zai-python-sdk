"""
Test script to verify OpenAI-compatible server works correctly.
This tests the exact usage pattern from the user's example.
"""

import sys
import time
import subprocess
import requests
from threading import Thread


def start_server():
    """Start the server in a separate process."""
    print("🚀 Starting server...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "7000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Give server time to start
    time.sleep(3)
    return process


def test_health_check():
    """Test server health endpoint."""
    print("\n1️⃣ Testing health check...")
    response = requests.get("http://localhost:7000/health")
    assert response.status_code == 200
    print("✅ Health check passed")


def test_models_list():
    """Test models list endpoint."""
    print("\n2️⃣ Testing models list...")
    response = requests.get("http://localhost:7000/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    print(f"✅ Models list passed - found {len(data['data'])} models")
    print(f"   Available models: {[m['id'] for m in data['data'][:5]]}")


def test_chat_completion():
    """Test chat completion endpoint (non-streaming)."""
    print("\n3️⃣ Testing chat completion (non-streaming)...")
    response = requests.post(
        "http://localhost:7000/v1/chat/completions",
        json={
            "model": "glm-4.6",
            "messages": [
                {"role": "user", "content": "What is your model name?"}
            ],
            "stream": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    assert len(data["choices"]) > 0
    assert "message" in data["choices"][0]
    content = data["choices"][0]["message"]["content"]
    print(f"✅ Chat completion passed")
    print(f"   Response: {content[:100]}...")


def test_streaming_completion():
    """Test streaming chat completion."""
    print("\n4️⃣ Testing streaming completion...")
    response = requests.post(
        "http://localhost:7000/v1/chat/completions",
        json={
            "model": "glm-4.5v",
            "messages": [
                {"role": "user", "content": "Say 'Hello, World!'"}
            ],
            "stream": True
        },
        stream=True
    )
    
    assert response.status_code == 200
    chunks = []
    for line in response.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: ') and not line_str.endswith('[DONE]'):
                chunks.append(line_str)
    
    assert len(chunks) > 0
    print(f"✅ Streaming completion passed - received {len(chunks)} chunks")


def test_with_openai_client():
    """Test with actual OpenAI client library."""
    print("\n5️⃣ Testing with OpenAI client library...")
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url="http://localhost:7000/v1",
            api_key="test-key"
        )
        
        # Test the exact pattern from user's example
        response = client.chat.completions.create(
            model="glm-4.6",
            messages=[
                {"role": "user", "content": "What is your model name?"}
            ]
        )
        
        assert response.choices[0].message.content
        print(f"✅ OpenAI client test passed")
        print(f"   Response: {response.choices[0].message.content[:100]}...")
        
    except ImportError:
        print("⚠️  OpenAI package not installed, skipping OpenAI client test")
        print("   Install with: pip install openai")


def run_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("Testing Z.AI OpenAI-Compatible Server")
    print("="*60)
    
    server_process = None
    try:
        # Start server
        server_process = start_server()
        
        # Run tests
        test_health_check()
        test_models_list()
        test_chat_completion()
        test_streaming_completion()
        test_with_openai_client()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\n✨ The server is working correctly!")
        print("   You can now use it with the OpenAI client library.")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    finally:
        # Stop server
        if server_process:
            print("\n🛑 Stopping server...")
            server_process.terminate()
            server_process.wait()
    
    return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

