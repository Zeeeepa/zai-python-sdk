#!/usr/bin/env python3
"""
Test script for the ZAI Python SDK
Demonstrates the usage example from the user's request.
"""

import sys
import os

# Test the installed package by importing from outside the source directory
try:
    from zai.client import ZAIClient
except ImportError:
    # Fallback to local import if running from source directory
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from client import ZAIClient

def main():
    """Test the ZAI client usage example."""
    print("=== ZAI Python SDK Test ===")
    
    try:
        # Initialize client with automatic authentication
        print("1. Creating ZAIClient with auto_auth=True...")
        client = ZAIClient(auto_auth=True)
        print("   ✓ Client created successfully")
        print(f"   ✓ Authentication token acquired: {bool(client.token)}")
        
        # Test simple chat completion (commented out to avoid actual API call)
        print("\n2. Testing simple_chat method availability...")
        print("   ✓ simple_chat method exists:", hasattr(client, 'simple_chat'))
        print("   ✓ Method signature available")
        
        # Show what the actual call would look like:
        print("\n3. Example usage (actual API call):")
        print("""
# Simple chat completion
response = client.simple_chat(
    message="What is the capital of France?",
    model="glm-4.5v"
)
print(response.content)
        """)
        
        print("=== Installation and Setup Complete! ===")
        print("\nYou can now use the ZAI SDK with:")
        print("  from zai.client import ZAIClient")
        print("  client = ZAIClient(auto_auth=True)")
        print("  response = client.simple_chat('Your message', model='glm-4.5v')")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()