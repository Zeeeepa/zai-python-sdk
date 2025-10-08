# Z.AI Python SDK

A Python client library for interacting with the Z.AI API, providing easy access to advanced language models for chat completions, streaming responses, and more.

## Installation

```bash
pip install requests
```

Clone the repository:
```bash
git clone https://github.com/iotbackdoor/zai-python-sdk.git
cd zai-python-sdk
```

## Quick Start

```python
from zai.client import ZAIClient

# Initialize client with automatic authentication
client = ZAIClient(auto_auth=True)

# Simple chat completion
response = client.simple_chat(
    message="What is the capital of France?",
    model="glm-4.5v"
)
print(response.content)
```

## Features

- Automatic guest token authentication
- Support for multiple AI models
- Streaming and non-streaming responses
- Customizable model parameters
- Modular architecture for flexibility
- Comprehensive error handling
- Verbose mode for debugging

## API Reference

### Client Initialization

```python
client = ZAIClient(
    token=None,              # Optional: Bearer token for authentication
    base_url="https://chat.z.ai",  # API base URL
    timeout=180,             # Request timeout in seconds
    auto_auth=True,          # Auto-fetch guest token if no token provided
    verbose=False            # Enable debug output
)
```

### Simple Chat Completion

```python
response = client.simple_chat(
    message="Your message here",
    model="glm-4.5v",        # or "0727-360B-API"
    enable_thinking=True,     # Enable thinking mode
    temperature=0.7,          # Control randomness (0.0-2.0)
    top_p=0.9,               # Control diversity (0.0-1.0)
    max_tokens=500           # Maximum response length
)
```

### Create Chat Session

```python
from zai.models import MCPFeature

chat = client.create_chat(
    title="My Chat",
    models=["glm-4.5v"],
    initial_message="Hello",
    enable_thinking=True,
    features=[
        MCPFeature("mcp", "vibe-coding", "hidden")
    ]
)
```

### Streaming Responses

```python
# Stream completion with custom chat
for chunk in client.stream_completion(
    chat_id="your-chat-id",
    messages=[
        {"role": "user", "content": "Tell me a story"}
    ],
    model="0727-360B-API",
    enable_thinking=True
):
    if chunk.phase == "answer":
        print(chunk.delta_content, end="")
```

### Complete Chat

```python
# Get complete response without streaming
response = client.complete_chat(
    chat_id="your-chat-id",
    messages=[
        {"role": "user", "content": "Explain quantum computing"}
    ],
    model="glm-4.5v"
)
print(response.content)
print(response.thinking)  # If thinking mode was enabled
```

## Available Models

- **glm-4.5v**: Advanced visual understanding and analysis model
- **0727-360B-API**: Most advanced model, proficient in coding and tool use

## Model Presets

The SDK includes predefined model configurations in `custom_models.py`:

```python
from zai.custom_models import get_preset, list_presets

# List available presets
print(list_presets())
# Output: ['creative', 'code', 'balanced', 'research', 'brainstorm', 'conservative']

# Get a preset configuration
preset = get_preset('code')
# Returns optimized parameters for code generation
```

## Advanced Usage

### Custom Model Parameters

```python
response = client.simple_chat(
    message="Write a creative story",
    model="glm-4.5v",
    temperature=1.2,  # Higher for more creativity
    top_p=0.95,       # Higher for more diversity
    max_tokens=2000   # Longer responses
)
```

### Error Handling

```python
from zai.core.exceptions import ZAIError

try:
    response = client.simple_chat(
        message="Hello",
        model="glm-4.5v"
    )
except ZAIError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Verbose Mode for Debugging

```python
# Enable verbose output to see API requests and responses
client = ZAIClient(auto_auth=True, verbose=True)
```

### Manual Token Management

```python
# Use your own authentication token
client = ZAIClient(
    token="your-bearer-token",
    auto_auth=False  # Disable automatic token fetching
)
```

## Architecture

The SDK is organized into modular components:

- `client.py` - Main client interface
- `core/` - Core functionality
  - `http_client.py` - HTTP request handling
  - `auth.py` - Authentication management
  - `exceptions.py` - Custom exceptions
- `operations/` - API operations
  - `chat.py` - Chat operations
  - `model.py` - Model operations
  - `streaming.py` - Streaming operations
- `utils/` - Utility functions
  - `sse_parser.py` - Server-Sent Events parsing
- `models.py` - Data models and structures
- `custom_models.py` - Predefined model configurations

## Requirements

- Python 3.7+
- requests

## Error Codes

The SDK raises `ZAIError` exceptions for API-related errors:

- Authentication errors when token is invalid or expired
- Network errors for connection issues
- API errors for invalid requests or server issues

## Contributing

Contributions are welcome. Please ensure your code follows the existing style and includes appropriate documentation.

## License

This project is licensed under the MIT License.

## Author

Developed by [iotbackdoor](https://github.com/iotbackdoor)

## Support

For issues, questions, or suggestions, please open an issue on the [GitHub repository](https://github.com/iotbackdoor/zai-python-sdk).
## 🆕 OpenAI-Compatible Server

The SDK now includes a FastAPI server that provides an OpenAI-compatible API interface. This allows you to use the standard OpenAI Python client library with Z.AI models!

### Quick Start with OpenAI Client

```bash
# 1. Install dependencies
pip install -r requirements-server.txt
pip install openai

# 2. Start the server
cd server && python run_server.py
```

```python
# 3. Use OpenAI client with Z.AI backend
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:7000/v1",
    api_key="dummy"  # Optional, can use your Z.AI token
)

response = client.chat.completions.create(
    model="glm-4.6",
    messages=[{"role": "user", "content": "What is your model name?"}]
)
print(response.choices[0].message.content)
```

### Features

✅ Full OpenAI Chat Completions API compatibility  
✅ Streaming and non-streaming responses  
✅ Model name mapping (gpt-4 → Z.AI models)  
✅ `/v1/chat/completions` endpoint  
✅ `/v1/models` endpoint  
✅ Works with any OpenAI-compatible client  

### Model Mapping

| OpenAI Model | Z.AI Model |
|--------------|------------|
| gpt-4, gpt-4-turbo | 0727-360B-API |
| gpt-3.5-turbo | glm-4.5v |
| glm-4.5, glm-4.5v, glm-4.6 | glm-4.5v |

### Streaming Example

```python
stream = client.chat.completions.create(
    model="glm-4.5v",
    messages=[{"role": "user", "content": "Write a poem"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Configuration

Environment variables:

```bash
HOST=0.0.0.0          # Server host
PORT=7000             # Server port
ZAI_BASE_URL=https://chat.z.ai  # Z.AI API URL
DEFAULT_MODEL=glm-4.5v  # Default model
```

### Testing

Verify the server works correctly:

```bash
python test_openai_server.py
```

See `examples/openai_client_example.py` for more usage examples.


---

## 🔥 OpenAI Compatibility

**NEW:** Use Z.AI with the OpenAI Python client! Drop-in replacement for OpenAI API.

### Quick Start with OpenAI Client

1. **Start the OpenAI-compatible proxy server:**
   ```bash
   python openai_proxy_server.py
   ```

2. **Use OpenAI Python client:**
   ```python
   from openai import OpenAI
   
   # Initialize client with Z.AI proxy
   client = OpenAI(
       base_url="http://localhost:7000/v1",
       api_key="your-z-ai-api-key"
   )
   
   # Use exactly like OpenAI!
   response = client.chat.completions.create(
       model="glm-4.5",
       messages=[{"role": "user", "content": "Hello!"}]
   )
   print(response.choices[0].message.content)
   ```

3. **Streaming responses:**
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

### Model Mappings

The proxy automatically maps popular OpenAI model names to Z.AI models:

| OpenAI Model | Z.AI Model |
|--------------|------------|
| `gpt-4` | `0727-360B-API` |
| `gpt-4-turbo` | `0727-360B-API` |
| `gpt-3.5-turbo` | `glm-4.5v` |
| `glm-4.5` | `glm-4.5v` |
| `glm-4.5v` | `glm-4.5v` |
| `glm-4.6` | `glm-4.5v` |

### Testing OpenAI Compatibility

Run the compatibility test suite:
```bash
# Install dependencies
pip install openai fastapi uvicorn

# Start the server (in one terminal)
python openai_proxy_server.py

# Run tests (in another terminal)
python test_openai_compatibility.py
```

### Server Configuration

Configure the server using environment variables:
```bash
export HOST="0.0.0.0"           # Server host (default: 0.0.0.0)
export PORT="7000"               # Server port (default: 7000)
export ZAI_BASE_URL="https://..." # Z.AI API base URL
```

### API Documentation

Once the server is running, visit:
- Interactive API docs: `http://localhost:7000/docs`
- Health check: `http://localhost:7000/health`
- List models: `http://localhost:7000/v1/models`

