# OpenAI Compatibility Implementation Notes

## Overview

This document describes how the OpenAI compatibility layer was implemented for Z.AI Python SDK.

## Architecture

### Components

1. **`openai_proxy_server.py`** - Standalone FastAPI server
   - Self-contained, no complex dependencies
   - Translates OpenAI API calls to Z.AI format
   - Handles authentication and model mapping

2. **`validate_openai.py`** - Comprehensive test suite
   - Tests model listing
   - Tests chat completions (streaming & non-streaming)
   - Tests model name mappings
   - Validates error handling

3. **`example_usage.py`** - Simple usage example
   - Shows exact use case from requirements
   - Ready to run demonstration

4. **`QUICKSTART.md`** - Step-by-step guide
   - Installation instructions
   - Configuration options
   - Troubleshooting tips

## Key Implementation Details

### 1. Z.AI API Endpoint

```python
BASE_URL = "https://chat.z.ai"
ENDPOINT = "/api/chat/completions"
```

### 2. Required Headers

Z.AI requires browser-like headers to prevent bot detection:

```python
headers = {
    "accept": "*/*",
    "authorization": f"Bearer {token}",
    "content-type": "application/json",
    "referer": "https://chat.z.ai/",
    "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
```

### 3. Payload Structure

Z.AI expects a more complex payload than standard OpenAI:

```python
payload = {
    "stream": bool,
    "model": "glm-4.5v",
    "messages": [{"role": "user", "content": "..."}],
    "params": {
        "temperature": 0.7,
        "top_p": 1.0,
        "max_tokens": 100
    },
    "features": {
        "image_generation": False,
        "web_search": False,
        "auto_web_search": False,
        "preview_mode": True,
        "flags": [],
        "thinking": {"enabled": True, "budget_tokens": 0}
    },
    "variables": {},
    "model_item": {
        "id": "glm-4.5v",
        "name": "glm-4.5v"
    },
    "chat_id": "uuid-string"
}
```

### 4. Model Name Mappings

The proxy automatically maps popular OpenAI model names:

| OpenAI Model | Z.AI Model |
|--------------|------------|
| `gpt-4` | `0727-360B-API` |
| `gpt-4-turbo` | `0727-360B-API` |
| `gpt-3.5-turbo` | `glm-4.5v` |
| `glm-4.5` | `glm-4.5v` |
| `glm-4.5v` | `glm-4.5v` |
| `glm-4.6` | `glm-4.5v` |

### 5. Authentication

Two authentication methods are supported:

#### Method 1: User Token (Recommended)
```python
client = OpenAI(
    base_url="http://localhost:7000/v1",
    api_key="your-z-ai-token-from-localstorage"
)
```

To get your token:
1. Visit https://chat.z.ai
2. Open DevTools (F12)
3. Go to Application → Local Storage → https://chat.z.ai
4. Copy the `token` value

#### Method 2: Guest Token (Automatic)
```python
client = OpenAI(
    base_url="http://localhost:7000/v1",
    api_key="dummy-key"  # Server auto-fetches guest token
)
```

The server will automatically call Z.AI's guest auth endpoint:
```python
POST /api/v1/auths/
{"action": "guest"}
```

### 6. Response Transformation

#### Non-Streaming Response

Z.AI response is transformed to OpenAI format:

**Z.AI Response:**
```json
{
  "choices": [{
    "message": {"content": "Hello!"}
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 5,
    "total_tokens": 15
  }
}
```

**OpenAI Format:**
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "glm-4.5",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Hello!"
    },
    "finish_reason": "stop"
  }],
  "usage": {...}
}
```

#### Streaming Response

Z.AI sends SSE events that are transformed to OpenAI streaming chunks:

**Z.AI Event:**
```
data: {"choices":[{"delta":{"content":"Hello"}}]}
```

**OpenAI Chunk:**
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion.chunk",
  "created": 1234567890,
  "model": "glm-4.5",
  "choices": [{
    "index": 0,
    "delta": {"content": "Hello"},
    "finish_reason": null
  }]
}
```

## Configuration

### Environment Variables

```bash
HOST=0.0.0.0          # Server host
PORT=7000             # Server port
ZAI_BASE_URL=https://chat.z.ai  # Z.AI API URL
```

### Custom Model Mappings

Edit `Config.MODEL_MAPPINGS` in `openai_proxy_server.py`:

```python
MODEL_MAPPINGS = {
    "gpt-4": "0727-360B-API",
    "custom-model": "z-ai-model-name"
}
```

## Testing

### Run Validation Suite

```bash
# Terminal 1: Start server
python openai_proxy_server.py

# Terminal 2: Run tests
python validate_openai.py
```

### Manual Testing

```bash
# Health check
curl http://localhost:7000/health

# List models
curl http://localhost:7000/v1/models

# Chat completion
curl -X POST http://localhost:7000/v1/chat/completions \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.5",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

## Troubleshooting

### Issue: 401 Unauthorized

**Cause:** Invalid or expired API token

**Solution:**
1. Get fresh token from https://chat.z.ai local storage
2. Or let server auto-fetch guest token (may have limitations)

### Issue: Connection Refused

**Cause:** Server not running

**Solution:**
```bash
python openai_proxy_server.py
```

### Issue: Streaming Doesn't Work

**Cause:** May need to handle Z.AI's specific SSE format

**Solution:** Check server logs for parsing errors:
```bash
python openai_proxy_server.py 2>&1 | tee server.log
```

## Performance Considerations

1. **Connection Pooling**: The server uses `requests.Session()` for connection reuse
2. **Timeout**: Default timeout is 60 seconds for long-running completions
3. **Streaming**: Streams are processed line-by-line to minimize latency

## Security Notes

1. **API Keys**: Never commit API keys to version control
2. **Guest Tokens**: Guest tokens have rate limits and may expire
3. **HTTPS**: In production, use HTTPS reverse proxy (nginx, Caddy)
4. **CORS**: Server allows all origins - restrict in production

## Future Improvements

1. **Caching**: Add response caching for repeated queries
2. **Rate Limiting**: Implement rate limiting per API key
3. **Metrics**: Add Prometheus metrics for monitoring
4. **Load Balancing**: Support multiple Z.AI backend endpoints
5. **WebSocket**: Consider WebSocket for lower latency streaming

## References

- OpenAI API Docs: https://platform.openai.com/docs/api-reference
- Z.AI Website: https://chat.z.ai
- FastAPI Docs: https://fastapi.tiangolo.com
- Python OpenAI Client: https://github.com/openai/openai-python

## License

This implementation follows the same license as the Z.AI Python SDK.

## Contributors

- Original Z.AI SDK: [iotbackdoor](https://github.com/iotbackdoor)
- OpenAI Compatibility Layer: Codegen AI

---

**Last Updated:** 2025-10-08  
**Version:** 1.0.0

