#!/usr/bin/env python3
"""
Test script to demonstrate OpenAI compatibility with Z.AI.

This script shows how to use the OpenAI Python client with the Z.AI proxy server.

Prerequisites:
    pip install openai

Usage:
    1. Start the proxy server: python openai_proxy_server.py
    2. Run this test: python test_openai_compatibility.py
"""

import os
import sys

try:
    from openai import OpenAI
except ImportError:
    print("❌ Error: openai package not installed")
    print("   Install with: pip install openai")
    sys.exit(1)


def test_openai_compatibility():
    """Test OpenAI compatibility with Z.AI proxy."""
    
    # Get API key from environment
    api_key = os.getenv("ZAI_API_KEY", "your-api-key-here")
    
    if api_key == "your-api-key-here":
        print("⚠️  Warning: Using placeholder API key")
        print("   Set your actual API key: export ZAI_API_KEY='your-key'")
        print("")
    
    # Initialize OpenAI client with Z.AI proxy
    client = OpenAI(
        base_url="http://localhost:7000/v1",
        api_key=api_key,
    )
    
    print("🧪 Testing OpenAI compatibility with Z.AI\n")
    print("=" * 60)
    
    # Test 1: List available models
    print("\n📋 Test 1: List Available Models")
    print("-" * 60)
    try:
        models = client.models.list()
        print(f"✅ Found {len(models.data)} models:")
        for model in models.data[:3]:
            print(f"   - {model.id} (owned by: {model.owned_by})")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Simple completion (non-streaming)
    print("\n💬 Test 2: Simple Chat Completion (Non-Streaming)")
    print("-" * 60)
    try:
        response = client.chat.completions.create(
            model="glm-4.5",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from Z.AI!' in a creative way."}
            ],
            temperature=0.7,
            max_tokens=100,
        )
        print(f"✅ Response received:")
        print(f"   Model: {response.model}")
        print(f"   Content: {response.choices[0].message.content}")
        print(f"   Finish reason: {response.choices[0].finish_reason}")
        if response.usage:
            print(f"   Usage: {response.usage}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Streaming completion
    print("\n🌊 Test 3: Streaming Chat Completion")
    print("-" * 60)
    try:
        stream = client.chat.completions.create(
            model="glm-4.5",
            messages=[
                {"role": "user", "content": "Count from 1 to 5, one number per line."}
            ],
            stream=True,
        )
        
        print("✅ Streaming response:")
        print("   ", end="", flush=True)
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 4: Using GPT-4 model name (mapped to Z.AI model)
    print("\n🔄 Test 4: Model Name Mapping (gpt-4 → Z.AI model)")
    print("-" * 60)
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # This will be mapped to Z.AI's model
            messages=[
                {"role": "user", "content": "What model are you?"}
            ],
            max_tokens=50,
        )
        print(f"✅ Response with model mapping:")
        print(f"   Requested model: gpt-4")
        print(f"   Response model: {response.model}")
        print(f"   Content: {response.choices[0].message.content[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ All tests passed successfully!")
    print("\n💡 You can now use OpenAI client with Z.AI:")
    print("""
    from openai import OpenAI
    
    client = OpenAI(
        base_url="http://localhost:7000/v1",
        api_key="your-z-ai-api-key"
    )
    
    response = client.chat.completions.create(
        model="glm-4.5",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)
    """)
    
    return True


if __name__ == "__main__":
    try:
        success = test_openai_compatibility()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

