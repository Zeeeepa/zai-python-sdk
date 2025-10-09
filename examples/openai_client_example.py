"""
Example: Using Z.AI with OpenAI Python Client
Run the openai_standalone_server.py first!
"""
from openai import OpenAI
import sys

def main():
    print("="*60)
    print("Z.AI + OpenAI Client Example")
    print("="*60)
    
    # Initialize client
    client = OpenAI(
        base_url="http://localhost:7000/v1",
        api_key="dummy"  # Any value works
    )
    
    try:
        # Test 1: List models
        print("\n📋 Available Models:")
        models = client.models.list()
        for model in models.data:
            print(f"  - {model.id}")
        
        # Test 2: Simple chat
        print("\n💬 Test 1: Simple Chat (glm-4.5)")
        response = client.chat.completions.create(
            model="glm-4.5",
            messages=[
                {"role": "user", "content": "Say 'Hello from Z.AI!'"}
            ]
        )
        print(f"Response: {response.choices[0].message.content}")
        print(f"Tokens: {response.usage.total_tokens}")
        
        # Test 3: Different model
        print("\n🤖 Test 2: Different Model (gpt-4)")
        response2 = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "What is 5+3?"}
            ]
        )
        print(f"Response: {response2.choices[0].message.content}")
        
        # Test 4: Streaming
        print("\n📡 Test 3: Streaming Response")
        print("Question: Count to 5")
        print("Response: ", end="", flush=True)
        
        stream = client.chat.completions.create(
            model="glm-4.5",
            messages=[
                {"role": "user", "content": "Count to 5, one number per line"}
            ],
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()
        
        print("\n✅ All tests passed!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure the server is running:")
        print("   python openai_standalone_server.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
