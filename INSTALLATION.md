# Z.AI OpenAI-Compatible API - Installation Guide

Complete guide for installing and running the Z.AI OpenAI-Compatible API server.

## 🚀 Quick Start (One Command)

### Method 1: Direct Install (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/Zeeeepa/zai-python-sdk/main/install.sh | bash
```

### Method 2: Install from Specific Branch

```bash
curl -fsSL https://raw.githubusercontent.com/Zeeeepa/zai-python-sdk/codegen-bot/openai-compat-api-1759886538/install.sh -o install.sh
bash install.sh codegen-bot/openai-compat-api-1759886538
```

### Method 3: Manual Setup

```bash
# Download the setup script
curl -fsSL https://raw.githubusercontent.com/Zeeeepa/zai-python-sdk/main/setup_and_deploy.sh -o setup_and_deploy.sh

# Run it
bash setup_and_deploy.sh
```

---

## 📋 What the Script Does

The installation script will:

1. ✅ **Check Configuration** - Load existing or prompt for new settings
2. ✅ **Install Dependencies** - FastAPI, uvicorn, requests, pydantic, openai
3. ✅ **Check Port** - Ensure port 7000 (default) is available
4. ✅ **Configure Server** - Auto-generate configured server file
5. ✅ **Start Server** - Launch in background
6. ✅ **Run Tests** - Execute OpenAI API calls
7. ✅ **Monitor** - Continuously monitor server health

---

## ⚙️ Configuration

On first run, you'll be prompted for:

### Server Configuration
- **Host**: `0.0.0.0` (default) - Server bind address
- **Port**: `7000` (default) - Server port

### Z.AI API Configuration
- **API Key**: (optional) - Leave empty for guest authentication
- **Base URL**: `https://z.hhgzs.com/api/v1` (default)

### Model Configuration
- **Default Model**: `glm-4.5v` (recommended)
  - Options: `glm-4.5v`, `GLM-4-6-API-V1`, `0727-360B-API`

### Advanced Settings
- **Timeout**: `180` seconds (default)
- **Max Retries**: `3` (default)
- **Log Level**: `info` (default)

Configuration is saved to `.env.zai` and reused on subsequent runs.

---

## 🎯 Usage After Installation

### Using with OpenAI Python Client

```python
from openai import OpenAI

# Initialize client
client = OpenAI(
    base_url="http://localhost:7000/v1",
    api_key="dummy"  # Any value works
)

# Make a request
response = client.chat.completions.create(
    model="glm-4.5v",
    messages=[
        {"role": "user", "content": "What is your model name?"}
    ]
)

print(response.choices[0].message.content)
```

### Available Endpoints

- **Chat Completions**: `POST http://localhost:7000/v1/chat/completions`
- **List Models**: `GET http://localhost:7000/v1/models`
- **Health Check**: `GET http://localhost:7000/health`
- **API Docs**: `http://localhost:7000/docs`

---

## 🔧 Management Commands

### View Server Logs
```bash
tail -f server_output.log
```

### Check Server Status
```bash
curl http://localhost:7000/health
```

### Stop Server
```bash
kill $(cat .server.pid)
```

### Restart Server
```bash
bash setup_and_deploy.sh
```

### Reconfigure
```bash
rm .env.zai
bash setup_and_deploy.sh
```

---

## 📊 Example Output

```
============================================================
🚀 Z.AI OpenAI-Compatible API - Complete Setup
============================================================

📋 Step 1: Configuration Setup
============================================================
✅ Found existing configuration
  - Server: 0.0.0.0:7000
  - Z.AI URL: https://z.hhgzs.com/api/v1
  - Default Model: glm-4.5v

📦 Step 2: Installing Dependencies
============================================================
✅ All dependencies installed

🔍 Step 3: Checking Port Availability
============================================================
✅ Port 7000 is available

🔧 Step 4: Configuring Server
============================================================
✅ Server configured

🚀 Step 5: Starting Server
============================================================
Server PID: 12345
✅ Server is running!

💬 Step 6: Testing with Real OpenAI Client
============================================================

Test 1: Listing Available Models
Available models:
  • gpt-4
  • gpt-4-turbo
  • gpt-3.5-turbo
  • glm-4.5
  • glm-4.5v
  • glm-4.6

Test 2: Simple Chat Completion
Question: What is your model name? Reply in one sentence.

✅ SUCCESS! Got response from Z.AI:
============================================================
I am GLM-4.5V, an AI assistant.
============================================================

Model Used: glm-4.5v
Finish Reason: stop
Tokens: 25 (prompt: 10, completion: 15)

============================================================
🎉 All tests passed!
============================================================

📊 Step 7: Server Status
============================================================
✅ DEPLOYMENT SUCCESSFUL!

Server Information:
  • PID: 12345
  • URL: http://0.0.0.0:7000
  • Docs: http://0.0.0.0:7000/docs
  • Health: http://0.0.0.0:7000/health
  • Config: .env.zai
  • Logs: server_output.log

🔄 Server is running in background...
✅ Server alive - Requests: 6 - 12:34:56
```

---

## 🐛 Troubleshooting

### Port Already in Use
Script will automatically detect and offer to kill the existing process.

### Network Errors
If you see connection timeouts:
- Check your internet connection
- Verify Z.AI API is accessible
- Try with a different network

### Authentication Errors
- Leave API Key empty to use guest authentication
- Check if Z.AI API is available at the configured URL

### Server Won't Start
Check logs:
```bash
cat server_output.log
```

---

## 📚 Additional Resources

- **Full Documentation**: [README_OPENAI_SERVER.md](./README_OPENAI_SERVER.md)
- **Quick Start Guide**: [QUICKSTART.md](./QUICKSTART.md)
- **Implementation Notes**: [IMPLEMENTATION_NOTES.md](./IMPLEMENTATION_NOTES.md)
- **GitHub Repository**: https://github.com/Zeeeepa/zai-python-sdk

---

## 💡 Tips

1. **Configuration Reuse**: Your settings are saved in `.env.zai` and automatically loaded on restart
2. **Background Running**: Server runs in background - you can close the terminal and it keeps running
3. **Auto-Monitoring**: Script monitors server health and reports request count
4. **Easy Restart**: Just run the script again to restart with saved configuration
5. **Model Mapping**: Use familiar model names like `gpt-4` - they're automatically mapped to Z.AI models

---

## ✨ Features

- ✅ One-command installation
- ✅ Interactive configuration
- ✅ Automatic dependency management
- ✅ Port conflict resolution
- ✅ Configuration persistence
- ✅ Automated testing
- ✅ Health monitoring
- ✅ Detailed logging
- ✅ Background execution
- ✅ Easy management commands

---

**Ready to use! Your Z.AI OpenAI-compatible API is now running!** 🎉
