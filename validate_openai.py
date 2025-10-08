#!/usr/bin/env python3
"""
Validation script to test OpenAI client compatibility with Z.AI.

This script validates that the OpenAI Python client can successfully
interact with Z.AI through the proxy server.

Usage:
    1. Start the server: python openai_proxy_server.py
    2. Run validation: python validate_openai.py
"""

import sys
import time

try:
    from openai import OpenAI
except ImportError:
    print("❌ Error: openai package not installed")
    print("   Install with: pip install openai")
    sys.exit(1)


def validate_openai_compatibility():
    """Validate OpenAI client works with Z.AI."""
    
    print("=" * 70)
    print("🧪 VALIDATION: OpenAI Client with Z.AI Backend")
    print("=" * 70)
    
    # Initialize OpenAI client pointing to Z.AI proxy
    print("\n📍 Connecting to Z.AI proxy at http://localhost:7000/v1")
    client = OpenAI(
        base_url="http://localhost:7000/v1",
        api_key="dummy-key"  # Can be any string for testing
    )
    
    # Test 1: Health check via models list
    print("\n" + "=" * 70)
    print("Test 1: List Available Models")
    print("=" * 70)
    try:
        models = client.models.list()
        print(f"✅ SUCCESS: Found {len(models.data)} models")
        print("\n📋 Available models:")
        for model in models.data:
            print(f"   • {model.id} (owned by: {model.owned_by})")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("\n💡 Make sure the server is running:")
        print("   python openai_proxy_server.py")
        return False
    
    # Test 2: Simple chat completion (your exact use case)
    print("\n" + "=" * 70)
    print("Test 2: Chat Completion - Non-Streaming")
    print("=" * 70)
    print("📝 Request:")
    print('   model="glm-4.5"')
    print('   messages=[{"role": "user", "content": "What is your model name?"}]')
    
    try:
        response = client.chat.completions.create(
            model="glm-4.5",
            messages=[
                {"role": "user", "content": "What is your model name?"}
            ]
        )
        
        print("\n✅ SUCCESS: Received response")
        print(f"\n📦 Response Object:")
        print(f"   ID: {response.id}")
        print(f"   Model: {response.model}")
        print(f"   Created: {response.created}")
        print(f"   Object: {response.object}")
        print(f"\n💬 Assistant Reply:")
        print(f"   {response.choices[0].message.content}")
        print(f"\n📊 Token Usage:")
        if response.usage:
            print(f"   Prompt tokens: {response.usage.prompt_tokens}")
            print(f"   Completion tokens: {response.usage.completion_tokens}")
            print(f"   Total tokens: {response.usage.total_tokens}")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Streaming response
    print("\n" + "=" * 70)
    print("Test 3: Chat Completion - Streaming")
    print("=" * 70)
    print("📝 Request:")
    print('   model="glm-4.5"')
    print('   stream=True')
    
    try:
        stream = client.chat.completions.create(
            model="glm-4.5",
            messages=[
                {"role": "user", "content": "Count from 1 to 5"}
            ],
            stream=True
        )
        
        print("\n✅ SUCCESS: Streaming started")
        print("\n💬 Streaming Response:")
        print("   ", end="", flush=True)
        
        chunk_count = 0
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                chunk_count += 1
        
        print(f"\n\n📊 Received {chunk_count} chunks")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Model name mapping
    print("\n" + "=" * 70)
    print("Test 4: Model Name Mapping (gpt-4 → Z.AI model)")
    print("=" * 70)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # This should be mapped to Z.AI model
            messages=[
                {"role": "user", "content": "Say 'Hello from Z.AI!'"}
            ],
            max_tokens=50
        )
        
        print("✅ SUCCESS: Model mapping works")
        print(f"   Requested: gpt-4")
        print(f"   Response model: {response.model}")
        print(f"   Reply: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ VALIDATION COMPLETE: All tests passed!")
    print("=" * 70)
    print("\n🎉 OpenAI client successfully works with Z.AI backend!")
    print("\n📝 Example usage in your code:")
    print("""
    from openai import OpenAI
    
    client = OpenAI(
        base_url="http://localhost:7000/v1",
        api_key="your-z-ai-api-key"  # Optional
    )
    
    response = client.chat.completions.create(
        model="glm-4.5",
        messages=[{"role": "user", "content": "What is your model name?"}]
    )
    
    print(response.choices[0].message.content)
    """)
    
    return True


if __name__ == "__main__":
    try:
        success = validate_openai_compatibility()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

