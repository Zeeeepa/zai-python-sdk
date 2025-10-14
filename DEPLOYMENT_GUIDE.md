# Z.AI Python SDK - Deployment & Testing Guide

## 🎯 Overview

This guide provides complete instructions for deploying and testing the Z.AI Python SDK as an OpenAI-compatible API server.

## 📋 Prerequisites

- Python 3.7+
- pip
- git  
- curl (for testing)

## 🚀 Quick Start

### Option 1: Automated Deployment (Recommended)

```bash
# Clone and run deploy script
git clone https://github.com/Zeeeepa/zai-python-sdk.git
cd zai-python-sdk
chmod +x deploy.sh
./deploy.sh
```

The script will:
1. ✅ Check prerequisites
2. ✅ Install dependencies
3. ✅ Find available port (default: 8080)
4. ✅ Start server
5. ✅ Run health checks
6. ✅ Test chat completions
7. ✅ Show server status

### Option 2: Manual Setup

```bash
# 1. Clone repository
git clone https://github.com/Zeeeepa/zai-python-sdk.git
cd zai-python-sdk

# 2. Install dependencies  
pip3 install -r requirements.txt

# 3. Install in development mode
pip3 install -e .

# 4. Start server
python3 main.py --port 8080
```

## 🧪 Testing

### Test 1: Health Check

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Z.AI OpenAI-Compatible API",
  "port": 8080
}
```

### Test 2: List Models

```bash
curl http://localhost:8080/v1/models
```

Expected response:
```json
{
  "object": "list",
  "data": [
    {
      "id": "glm-4.5v",
      "object": "model",
      "created": 1234567890,
      "owned_by": "z.ai"
    }
  ]
}
```

### Test 3: Chat Completion

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.5v",
    "messages": [
      {"role": "user", "content": "What is 2+2?"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
  }'
```

Expected response:
```json
{
  "id": "chatcmpl-1234567890",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "glm-4.5v",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "2+2 equals 4."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 5,
    "total_tokens": 15
  }
}
```

## 💻 Using with OpenAI SDK

### Python Example

```python
from openai import OpenAI

# Configure client to use local Z.AI server
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="dummy-key"  # Not required but needed for SDK
)

# Make API call
response = client.chat.completions.create(
    model="glm-4.5v",
    messages=[
        {"role": "user", "content": "Hello! Who are you?"}
    ],
    temperature=0.7,
    max_tokens=200
)

print(response.choices[0].message.content)
```

### JavaScript/TypeScript Example

```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://localhost:8080/v1',
  apiKey: 'dummy-key'  // Not required but needed for SDK
});

const response = await client.chat.completions.create({
  model: 'glm-4.5v',
  messages: [
    { role: 'user', content: 'Hello! Who are you?' }
  ],
  temperature: 0.7,
  max_tokens: 200
});

console.log(response.choices[0].message.content);
```

## 📊 Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/v1/models` | List available models |
| POST | `/v1/chat/completions` | Chat completions |

## 🛠️ Configuration

### Environment Variables

- `PORT`: Server port (default: 8080)

### Command Line Options

```bash
python3 main.py --port 8080  # Custom port
```

## 📖 Available Models

| Model ID | Description |
|----------|-------------|
| `glm-4.5v` | GLM-4.5 Vision model |
| `0727-360B-API` | 360B parameter model |
| `GLM-4.5` | GLM-4.5 base model |

## 🔧 Server Management

### Check Server Status

```bash
ps aux | grep "python3 main.py"
```

### View Logs

```bash
tail -f server.log
```

### Stop Server

```bash
# If you have the PID file
kill $(cat .server.pid)

# Or kill by process name
pkill -f "python3 main.py"
```

### Restart Server

```bash
pkill -f "python3 main.py"
python3 main.py --port 8080 > server.log 2>&1 &
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find what's using the port
lsof -i:8080

# Use a different port
python3 main.py --port 8081
```

### Module Not Found Error

```bash
# Reinstall in development mode
pip3 install -e .
```

### Authentication Issues

The SDK uses automatic guest authentication. No API keys are required.

### Server Won't Start

Check logs:
```bash
cat server.log
```

Common issues:
- Python version < 3.7
- Missing dependencies
- Port already in use

## 📝 Response Format

### Success Response

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "glm-4.5v",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Response text"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  }
}
```

### Error Response

```json
{
  "error": {
    "message": "Error description",
    "type": "server_error",
    "code": 500
  }
}
```

## 🎯 Performance Tips

1. **Reuse connections**: Keep the server running instead of restarting
2. **Adjust timeouts**: Increase for longer responses
3. **Monitor logs**: Check server.log for issues
4. **Use appropriate models**: glm-4.5v for vision, GLM-4.5 for text

## 📚 Additional Resources

- [Z.AI Documentation](https://chat.z.ai)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [GitHub Repository](https://github.com/Zeeeepa/zai-python-sdk)

## 🤝 Support

For issues or questions:
1. Check server logs
2. Review this guide
3. Create an issue on GitHub
4. Check Z.AI documentation

## 📄 License

MIT License - See LICENSE file for details.

