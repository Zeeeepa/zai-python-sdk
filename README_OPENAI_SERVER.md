# OpenAI-Compatible Server for Z.AI

Transform Z.AI into an OpenAI-compatible API server! Use the OpenAI Python client to interact with Z.AI models.

## 🚀 Quick Start

### Option 1: Standalone Server (Recommended)
No SDK installation needed!

```bash
# Install dependencies
pip install fastapi uvicorn requests pydantic

# Run the server
python openai_standalone_server.py
```

Server will start at `http://localhost:7000`

### Option 2: SDK Wrapper Servers
Requires SDK installation:

```bash
# Install SDK
pip install -e .

# Run either server
python openai_sdk_server.py
# OR
python openai_wrapper_server.py
```

## 📖 Usage with OpenAI Client

```python
from openai import OpenAI

# Initialize client
client = OpenAI(
    base_url="http://localhost:7000/v1",
    api_key="dummy"  # Any value works
)

# Chat completion
response = client.chat.completions.create(
    model="glm-4.5",
    messages=[
        {"role": "user", "content": "What is your name?"}
    ]
)

print(response.choices[0].message.content)
```

## 🎯 Features

✅ **OpenAI-compatible endpoints:**
- `/v1/chat/completions` - Chat completions
- `/v1/models` - List available models  
- `/health` - Health check
- `/` - API information

✅ **Model mappings:**
```python
"gpt-4" → "0727-360B-API"
"gpt-4-turbo" → "0727-360B-API"
"gpt-3.5-turbo" → "glm-4.5v"
"glm-4.5" → "glm-4.5v"
"glm-4.5v" → "glm-4.5v"
"glm-4.6" → "GLM-4-6-API-V1"
```

✅ **Both streaming and non-streaming responses**

## 📝 Advanced Examples

### Streaming Response
```python
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Count to 5"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### List Available Models
```python
models = client.models.list()
for model in models.data:
    print(f"- {model.id}")
```

### Using Different Models
```python
# Use GLM-4.5V (vision model)
response = client.chat.completions.create(
    model="glm-4.5v",
    messages=[{"role": "user", "content": "Explain AI"}]
)

# Use 360B model
response = client.chat.completions.create(
    model="gpt-4-turbo",  # Maps to 0727-360B-API
    messages=[{"role": "user", "content": "Write code"}]
)
```

## 🔧 Configuration

### Change Server Port
Edit the file and modify:
```python
uvicorn.run(app, host="0.0.0.0", port=7000)  # Change 7000 to your port
```

### Add Custom Models
Add to `MODEL_MAPPINGS`:
```python
MODEL_MAPPINGS = {
    "your-model-name": "zai-model-id",
    ...
}
```

## 🐛 Troubleshooting

**Issue: "Module not found" errors**
- Use `openai_standalone_server.py` - it has no SDK dependencies

**Issue: Port already in use**
- Change the port in the server file or kill existing process:
  ```bash
  lsof -ti:7000 | xargs kill -9
  ```

**Issue: Authentication errors**
- The server auto-authenticates with Z.AI
- No API keys needed!

## 📊 Server Comparison

| Server | Dependencies | Import Complexity | Status |
|--------|-------------|-------------------|--------|
| `openai_standalone_server.py` | Minimal | None | ✅ **Recommended** |
| `openai_sdk_server.py` | SDK + FastAPI | Medium | ✅ Working |
| `openai_wrapper_server.py` | SDK + FastAPI | Medium | ✅ Working |

## 🌐 API Documentation

Once running, visit:
- **Interactive docs**: http://localhost:7000/docs
- **API schema**: http://localhost:7000/openapi.json
- **Health check**: http://localhost:7000/health

## 💡 Use Cases

- Drop-in replacement for OpenAI API
- Integrate Z.AI into existing OpenAI-based projects
- Test applications with free Z.AI models
- Build multi-model applications
- Prototype with different LLMs

## 🔒 Security Note

This server is designed for local development. For production:
- Add authentication middleware
- Use HTTPS
- Implement rate limiting
- Add request validation
- Monitor API usage

## 📚 More Examples

See the `/examples` directory for:
- Async usage
- Error handling
- Custom parameters
- Multi-turn conversations
- Function calling patterns

---

**Made with ❤️ for the Z.AI community**
