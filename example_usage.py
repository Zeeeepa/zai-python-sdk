#!/usr/bin/env python3
"""
Example: Using OpenAI client with Z.AI (your exact use case)

Prerequisites:
    1. pip install openai
    2. python openai_proxy_server.py (in another terminal)

Then run:
    python example_usage.py
"""

from openai import OpenAI

# Initialize OpenAI client pointing to Z.AI proxy
client = OpenAI(
    base_url="http://localhost:7000/v1",
    api_key="your-z-ai-api-key"  # Use your actual Z.AI API key
)

# Your exact use case - make a simple request
print("🔄 Making request to Z.AI via OpenAI client...")
print("   Model: glm-4.5")
print("   Message: What is your model name?")
print()

response = client.chat.completions.create(
    model="glm-4.5",
    messages=[
        {"role": "user", "content": "What is your model name?"}
    ]
)

print("✅ Response received!")
print()
print("📦 Full response object:")
print(response)
print()
print("💬 Message content:")
print(response.choices[0].message.content)
print()
print(f"📊 Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")

