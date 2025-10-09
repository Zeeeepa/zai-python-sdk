# Z.AI Python SDK

A Python client library for interacting with the Z.AI API, providing easy access to advanced language models for chat completions, streaming responses, and more.


## 🚀 One-Command Deployment (EXANOKE Format)

Deploy the entire SDK with a single command:

```bash
curl -fsSL https://raw.githubusercontent.com/Zeeeepa/zai-python-sdk/main/zai_deploy_simple.sh -o zai_deploy.sh
bash zai_deploy.sh main
```

Or deploy a specific branch:

```bash
curl -fsSL https://raw.githubusercontent.com/Zeeeepa/zai-python-sdk/codegen-bot/exanoke-deployment-script-1760018725/zai_deploy_simple.sh -o zai_deploy.sh
bash zai_deploy.sh codegen-bot/exanoke-deployment-script-1760018725
```

### What the Deployment Script Does

- ✅ **Auto-installs** system dependencies (git, python3, pip, venv)
- ✅ **Clones repository** to `/opt/zai-python-sdk`
- ✅ **Sets up** Python virtual environment
- ✅ **Installs** all requirements
- ✅ **Creates** systemd service for production
- ✅ **Generates** OpenAI test client (`test_openai_client.py`) in your current directory
- ✅ **Runs** automated tests and displays results
- ✅ **Provides** comprehensive usage information

### Auto-Generated Test Client

After deployment, test with the OpenAI-compatible client created in your directory:

```python
# The script creates test_openai_client.py for you
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:7000/v1",
    api_key="test-api-key"
)

response = client.completions.create(
    model="glm-4.5V",
    prompt="What is your model name?"
)
print(response)
```

Run it:
```bash
python3 test_openai_client.py
```

---

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
