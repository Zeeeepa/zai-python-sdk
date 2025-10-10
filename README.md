# Z.AI OpenAI-Compatible API Server

A lightweight, production-ready server that provides OpenAI-compatible endpoints for Z.AI models with automatic guest token authentication and request signing.

## Features

✅ **Automatic Authentication** - Guest token authentication with dual-layer HMAC-SHA256 signature  
✅ **OpenAI Compatible** - Drop-in replacement for OpenAI API  
✅ **Streaming Support** - Full SSE streaming implementation  
✅ **Multiple Models** - Support for GLM-4.5, GLM-4.5v, and 0727-360B-API  
✅ **Dynamic Port** - Automatic port allocation if default is in use  
✅ **Easy Deployment** - One-command deployment script  

## Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/Zeeeepa/zai-python-sdk/main/deploy.sh | bash
```

Or with custom port:

```bash
bash deploy.sh 8080
```

### Option 2: Manual Setup

```bash
# Clone repository
git clone https://github.com/Zeeeepa/zai-python-sdk.git
cd zai-python-sdk

# Install dependencies
pip install -r requirements.txt

# Start server
python3 server.py --port 8000
```

## Usage

### List Available Models

```bash
curl http://localhost:8000/v1/models
```

### Chat Completion (Non-Streaming)

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.5v",
    "messages": [
      {"role": "user", "content": "What is 2+2?"}
    ],
    "stream": false
  }'
```

### Chat Completion (Streaming)

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.5v",
    "messages": [
      {"role": "user", "content": "Count from 1 to 5"}
    ],
    "stream": true
  }'
```

### Using with OpenAI Python SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="not-needed"  # API key not required
)

response = client.chat.completions.create(
    model="glm-4.5v",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)
```

## Available Endpoints

- `GET /` - Server information
- `GET /health` - Health check
- `GET /v1/models` - List available models
- `POST /v1/chat/completions` - Chat completions (OpenAI compatible)
- `GET /docs` - Interactive API documentation

## Supported Models

| Model ID | Description |
|----------|-------------|
| `glm-4.5v` | Visual understanding model |
| `glm-4.5` | Standard language model |
| `0727-360B-API` | Advanced coding model (360B parameters) |

## Configuration

### Environment Variables

- `PORT` - Server port (default: 8000)
- `HOST` - Server host (default: 0.0.0.0)

### Command Line Arguments

```bash
python3 server.py --port 8080 --host 0.0.0.0
```

## Architecture

### Authentication Flow

1. **Get Guest Token** → Request guest authentication token from Z.AI
2. **Extract User ID** → Decode JWT to extract user_id
3. **Generate Signature** → Create dual-layer HMAC-SHA256 signature
   - Layer 1: `HMAC(secret, window_index)`
   - Layer 2: `HMAC(derived_key, canonical_string)`
4. **Build Signed Request** → Add signature to headers and query params
5. **Make Request** → Z.AI validates signature and responds

### Signature Generation

```python
canonical_string = "requestId,<id>,timestamp,<ts>,user_id,<uid>|<msg>|<ts>"
window_index = timestamp_ms // (5 * 60 * 1000)  # 5-minute windows
derived_key = HMAC-SHA256(secret, window_index)
signature = HMAC-SHA256(derived_key, canonical_string)
```

## Requirements

- Python 3.8+
- pip3
- git (for deployment script)

## Troubleshooting

### Port Already in Use

The deployment script automatically finds an available port if the default is in use.

Manual check:
```bash
lsof -i :8000
```

### Server Won't Start

Check the logs:
```bash
tail -f server.log
```

### Authentication Errors

The server uses guest token authentication automatically. If you encounter authentication errors:

1. Check internet connectivity
2. Verify Z.AI service is accessible
3. Review server logs for detailed error messages

## Development

### Project Structure

```
zai-python-sdk/
├── server.py         # Main server implementation
├── deploy.sh         # Automated deployment script
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

### Running Tests

Test the server endpoints:

```bash
# Health check
curl http://localhost:8000/health

# List models
curl http://localhost:8000/v1/models

# Test chat
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "glm-4.5v", "messages": [{"role": "user", "content": "test"}], "stream": false}'
```

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- Open an issue on GitHub
- Check the [API documentation](http://localhost:8000/docs) when server is running

## Acknowledgments

- Built on FastAPI for high performance
- Uses Z.AI's GLM models
- OpenAI API compatible for easy integration

