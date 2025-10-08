"""
Example of using the OpenAI client with Z.AI OpenAI-compatible server.

Install required package:
    pip install openai

Start the server first:
    cd server && python run_server.py
"""

from openai import OpenAI

# Initialize OpenAI client pointing to local Z.AI server
client = OpenAI(
    base_url="http://localhost:7000/v1",  # Point to local server
    api_key="dummy-key"  # Can be any string, or use your Z.AI token
)


def example_simple_completion():
    """Example: Simple chat completion."""
    print("\n=== Simple Chat Completion ===")
    
    response = client.chat.completions.create(
        model="glm-4.6",  # or "gpt-4", "gpt-3.5-turbo"
        messages=[
            {"role": "user", "content": "What is your model name?"}
        ]
    )
    
    print(f"Response: {response.choices[0].message.content}")
    print(f"Model: {response.model}")
    print(f"Tokens used: {response.usage.total_tokens}")


def example_streaming_completion():
    """Example: Streaming chat completion."""
    print("\n=== Streaming Chat Completion ===")
    
    stream = client.chat.completions.create(
        model="glm-4.5v",
        messages=[
            {"role": "user", "content": "Write a short poem about AI"}
        ],
        stream=True
    )
    
    print("Response: ", end="")
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()


def example_conversation():
    """Example: Multi-turn conversation."""
    print("\n=== Multi-turn Conversation ===")
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the capital of France?"},
    ]
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    
    print(f"User: {messages[1]['content']}")
    print(f"Assistant: {response.choices[0].message.content}")


def example_list_models():
    """Example: List available models."""
    print("\n=== Available Models ===")
    
    models = client.models.list()
    
    print("Available models:")
    for model in models.data:
        print(f"  - {model.id}")


def example_with_parameters():
    """Example: Chat completion with custom parameters."""
    print("\n=== Chat with Custom Parameters ===")
    
    response = client.chat.completions.create(
        model="glm-4.5",
        messages=[
            {"role": "user", "content": "Tell me a creative story in one sentence"}
        ],
        temperature=1.2,  # Higher temperature for more creativity
        max_tokens=100,
        top_p=0.95
    )
    
    print(f"Response: {response.choices[0].message.content}")


if __name__ == "__main__":
    print("Z.AI OpenAI-Compatible Client Examples")
    print("=" * 50)
    
    try:
        # Run examples
        example_simple_completion()
        example_list_models()
        example_with_parameters()
        example_conversation()
        example_streaming_completion()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the server is running:")
        print("  cd server && python run_server.py")

