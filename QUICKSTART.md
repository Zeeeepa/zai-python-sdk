# 🚀 Quick Start: OpenAI Client with Z.AI

## Installation

```bash
# Install dependencies
pip install openai fastapi uvicorn requests

# Clone the repository (if not already)
git clone https://github.com/Zeeeepa/zai-python-sdk.git
cd zai-python-sdk
```

## Usage

### Step 1: Start the Proxy Server

```bash
python openai_proxy_server.py
```

You should see:
```
🚀 Starting Z.AI OpenAI-Compatible API Server...
📍 Server will run at: http://0.0.0.0:7000
📚 API Documentation: http://0.0.0.0:7000/docs
```

### Step 2: Use OpenAI Client in Your Code

**Your exact use case:**

```python
from openai import OpenAI

# Initialize client
client = OpenAI(
    base_url="http://localhost:7000/v1",
    api_key="your-z-ai-api-key"  # or any string for testing
)

# Make a request (exactly as you specified)
response = client.chat.completions.create(
    model="glm-4.5",
    messages=[
        {"role": "user", "content": "What is your model name?"}
    ]
)

# Print the response
print(response.choices[0].message.content)
```

**That's it!** No changes needed to your existing OpenAI code.

## Alternative Models

You can use any of these model names interchangeably:

```python
# These all work:
response = client.chat.completions.create(model="glm-4.5", ...)
response = client.chat.completions.create(model="glm-4.5v", ...)
response = client.chat.completions.create(model="glm-4.6", ...)

# Or use OpenAI model names (automatically mapped):
response = client.chat.completions.create(model="gpt-4", ...)
response = client.chat.completions.create(model="gpt-3.5-turbo", ...)
```

## Streaming Responses

```python
stream = client.chat.completions.create(
    model="glm-4.5",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## Validation

Run the validation script to test everything works:

```bash
# Make sure server is running in another terminal
python validate_openai.py
```

## Configuration

Set environment variables before starting the server:

```bash
export HOST="0.0.0.0"              # Server host
export PORT="7000"                  # Server port
export ZAI_BASE_URL="https://..."  # Your Z.AI API URL
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your settings
```

## API Documentation

Once the server is running, visit:
- **Interactive docs:** http://localhost:7000/docs
- **Health check:** http://localhost:7000/health
- **List models:** http://localhost:7000/v1/models

## Complete Example

```python
from openai import OpenAI

# Setup
client = OpenAI(
    base_url="http://localhost:7000/v1",
    api_key="your-api-key"
)

# Non-streaming
response = client.chat.completions.create(
    model="glm-4.5",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is your model name?"}
    ],
    temperature=0.7,
    max_tokens=100
)

print("Response:", response.choices[0].message.content)
print("Model:", response.model)
print("Tokens used:", response.usage.total_tokens if response.usage else "N/A")

# Streaming
print("\nStreaming response:")
stream = client.chat.completions.create(
    model="glm-4.5",
    messages=[{"role": "user", "content": "Count from 1 to 5"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()

# List available models
models = client.models.list()
print(f"\nAvailable models: {[m.id for m in models.data]}")
```

## Troubleshooting

**Server not starting?**
- Make sure port 7000 is not in use: `lsof -i :7000`
- Try a different port: `PORT=8000 python openai_proxy_server.py`

**Connection refused?**
- Check server is running: `curl http://localhost:7000/health`
- Check firewall settings

**Z.AI API errors?**
- Verify your Z.AI API key is valid
- Check `ZAI_BASE_URL` environment variable
- Review server logs for details

## Support

For issues or questions:
- GitHub Issues: https://github.com/Zeeeepa/zai-python-sdk/issues
- Documentation: See README.md

---

**Note:** This proxy server makes Z.AI accessible through the standard OpenAI Python client, enabling drop-in replacement for any application using OpenAI's API.

