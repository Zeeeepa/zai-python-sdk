# Z.AI API Endpoints Discovered

## Summary

From Playwright traffic capture, we discovered the following Z.AI API endpoints:

## 1. Authentication Endpoint

```
GET https://chat.z.ai/api/v1/auths/
```

**Response (200 OK):**
```json
{
  "id": "6a30a18d-d6c7-402f-af39-4ee43fb5bb7f",
  "email": "Guest-1760396341717@guest.com",
  "name": "Guest-1760396341717",
  "role": "guest",
  "profile_image_url": "/user.png",
  "idp": "z.ai",
  "token": "eyJhbGciOiJFUzI1N..."
}
```

**Notes:**
- Automatically creates guest session if not authenticated
- Returns JWT token in response
- Guest tokens have "role": "guest"
- User tokens have "role": "user" (from previous testing)

## 2. Config Endpoint

```
GET https://chat.z.ai/api/config
```

**Response (200 OK):**
```json
{
  "status": true,
  "name": "Z",
  "version": "0.0.0",
  "default_locale": "",
  "oauth": {
    "providers": {
      "google": "google",
      "github": "github"
    }
  },
  "default_ppt_model": "0702-RL-API",
  "features": {
    "auth": true,
    "auth_trusted_head": ...
  }
}
```

**Notes:**
- Returns system configuration
- Shows available OAuth providers
- Lists enabled features
- Contains default model settings

## 3. Models List Endpoint

```
GET https://chat.z.ai/api/models
```

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": "GLM-4-6-API-V1",
      "name": "GLM-4.6",
      "owned_by": "openai",
      "openai": {
        "id": "GLM-4-6-API-V1",
        "name": "GLM-4-6-API-V1",
        "owned_by": "openai",
        "openai": {
          "id": "GLM-4-6-API-V1"
        },
        "urlIdx": 1
      },
      "urlIdx": 1
    },
    ...
  ]
}
```

**Notes:**
- Returns list of available models
- OpenAI-compatible format
- Includes model metadata
- Can be used directly for /v1/models endpoint

## 4. User Settings Endpoint

```
GET https://chat.z.ai/api/v1/users/user/settings
```

**Response (200 OK):**
```json
null
```

**Notes:**
- Returns user preferences/settings
- May be null for guest users
- Likely contains UI preferences, default models, etc.

## 5. Completion Endpoint (From Previous Testing)

```
POST https://chat.z.ai/api/chat/completions
```

**Request Headers:**
- `authorization`: Bearer {token}
- `x-fe-version`: prod-fe-1.0.70
- `content-type`: application/json

**Request Body:**
```json
{
  "model": "glm-4.5v",
  "messages": [
    {"role": "user", "content": "Your message"}
  ],
  "stream": false,
  "chatId": "uuid",
  "parentMessageId": "uuid"
}
```

**Response:**
- Success: OpenAI-compatible completion response
- Rate Limited: 400 "The system is busy. Please try again in a moment."

## 6. Chat Creation Endpoint (From Previous Testing)

```
POST https://chat.z.ai/api/v1/chats/new
```

**Request Body:**
```json
{
  "chat": {
    "id": "",
    "title": "Chat title",
    "models": ["glm-4.5v"],
    "params": {},
    "history": {
      "messages": {...},
      "currentId": "message-id"
    },
    "messages": [...],
    "tags": [],
    "flags": [],
    "features": [],
    "mcp_servers": [],
    "enable_thinking": false,
    "timestamp": 1234567890
  }
}
```

**Response (200 OK):**
```json
{
  "id": "chat-id-uuid",
  ...
}
```

## Authentication Flow

1. **Guest Token:** 
   - GET /api/v1/auths/ without credentials
   - Returns guest token automatically
   
2. **User Login:**
   - POST /api/v1/auths/signin with email/password
   - Returns user token with "role": "user"

## Key Findings

1. **Auto Guest Tokens**: Z.AI automatically provides guest tokens if not authenticated
2. **OpenAI Compatible**: Models endpoint returns OpenAI-compatible format
3. **Multiple Model IDs**: Models have multiple ID fields (id, name, openai.id)
4. **Config Available**: System config accessible via /api/config
5. **Headers Critical**: x-fe-version header appears in requests

## Next Steps

1. ✅ **Implement guest token fallback** in SDK
2. ✅ **Use /api/models endpoint** for model listing
3. ✅ **Parse config endpoint** for feature detection
4. ⏳ **Capture actual completion response** with working message
5. ⏳ **Document SSE streaming format** from live capture

