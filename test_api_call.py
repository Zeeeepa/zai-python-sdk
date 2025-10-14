#!/usr/bin/env python3
"""
Direct test of Z.AI SDK with OpenAI-style response format
Tests the SDK directly without needing the server
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from example.py pattern
from zai.client import ZAIClient
from zai.core.exceptions import ZAIError

print("="*70)
print("🧪 Z.AI SDK Direct API Call Test")
print("="*70)
print()

try:
    # Initialize client
    print("🔧 Initializing Z.AI Client...")
    client = ZAIClient(auto_auth=True, verbose=False)
    print(f"✅ Client initialized with token: {client.token[:20]}...")
    print()
    
    # Test question
    test_question = "What is 2+2? Answer in one short sentence."
    
    print("="*70)
    print("📨 Sending Test Request")
    print("="*70)
    print(f"Question: {test_question}")
    print()
    
    # Make API call
    print("🤖 Calling Z.AI API...")
    response = client.simple_chat(
        message=test_question,
        model="glm-4.5v",
        enable_thinking=False,
        temperature=0.7,
        max_tokens=100
    )
    
    print("="*70)
    print("✅ Response Received")
    print("="*70)
    print()
    
    # Display response in OpenAI-style format
    print("📝 Assistant Response:")
    print("-" * 70)
    if response.content:
        print(response.content)
    else:
        print("(No content)")
    print("-" * 70)
    print()
    
    # Display usage stats
    if response.usage:
        print("📊 Token Usage:")
        print(f"  • Prompt tokens: {response.usage.get('prompt_tokens', 0)}")
        print(f"  • Completion tokens: {response.usage.get('completion_tokens', 0)}")
        print(f"  • Total tokens: {response.usage.get('total_tokens', 0)}")
    print()
    
    # Show OpenAI-compatible format
    print("="*70)
    print("🔄 OpenAI-Compatible Response Format")
    print("="*70)
    print()
    
    import json
    import time
    
    openai_response = {
        "id": f"chatcmpl-{int(time.time() * 1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "glm-4.5v",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response.content
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": response.usage.get('prompt_tokens', 0) if response.usage else 0,
            "completion_tokens": response.usage.get('completion_tokens', 0) if response.usage else 0,
            "total_tokens": response.usage.get('total_tokens', 0) if response.usage else 0
        }
    }
    
    print(json.dumps(openai_response, indent=2, ensure_ascii=False))
    print()
    
    print("="*70)
    print("✅ TEST PASSED - Z.AI SDK is working correctly!")
    print("="*70)
    
except ZAIError as e:
    print(f"❌ Z.AI Error: {e}")
    sys.exit(1)
except Exception as e:
    import traceback
    print(f"❌ Unexpected error: {e}")
    print(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

