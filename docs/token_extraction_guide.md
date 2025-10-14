# 🔐 Z.AI Token Extraction Guide

Complete guide for extracting authentication tokens from Z.AI using multiple methods.

## 📋 Table of Contents

1. [JavaScript Bookmarklet (Easiest)](#javascript-bookmarklet)
2. [Browser Console Method](#browser-console-method)
3. [Playwright Automation](#playwright-automation)
4. [Manual Extraction](#manual-extraction)

---

## 🔖 JavaScript Bookmarklet

The **easiest and fastest** way to extract your Z.AI token!

### How to Use:

1. **Create a Bookmark:**
   - Right-click your bookmarks bar
   - Click "Add page" or "New bookmark"
   
2. **Copy the Bookmarklet:**
   ```javascript
   javascript:(function(){if(window.location.hostname!=="chat.z.ai"){alert("🚀 This code is for chat.z.ai");window.open("https://chat.z.ai","_blank");return;}function getZaiToken(){const localToken=localStorage.getItem("token");if(localToken){console.log("✅ Found token in localStorage");return localToken;}const sessionToken=sessionStorage.getItem("token");if(sessionToken){console.log("✅ Found token in sessionStorage");return sessionToken;}const authKeys=["auth_token","access_token","jwt","bearer"];for(const key of authKeys){const val=localStorage.getItem(key)||sessionStorage.getItem(key);if(val){console.log(`✅ Found token as '${key}'`);return val;}}console.log("🔍 Searching all localStorage keys...");for(let i=0;i<localStorage.length;i++){const key=localStorage.key(i);const value=localStorage.getItem(key);if(value&&value.startsWith("eyJ")){console.log(`✅ Found JWT-like token in '${key}'`);return value;}}const cookies=document.cookie.split(';');for(const cookie of cookies){const[name,value]=cookie.trim().split('=');if(value&&value.startsWith("eyJ")){console.log(`✅ Found JWT-like token in cookie '${name}'`);return value;}}alert("❌ Z.AI access_token not found!\n\nPlease make sure you're logged in to chat.z.ai");return null;}async function copyToClipboard(text){try{await navigator.clipboard.writeText(text);return true;}catch(err){console.error("❌ Failed to copy to clipboard:",err);const textarea=document.createElement("textarea");textarea.value=text;textarea.style.position="fixed";textarea.style.opacity="0";document.body.appendChild(textarea);textarea.focus();textarea.select();const success=document.execCommand("copy");document.body.removeChild(textarea);return success;}}async function validateToken(token){try{const response=await fetch("https://chat.z.ai/api/v1/auths/",{headers:{"authorization":`Bearer ${token}`}});if(response.ok){const data=await response.json();console.log("✅ Token validated:",data);return data;}else{console.error("❌ Token validation failed:",response.status);return null;}}catch(err){console.error("❌ Validation error:",err);return null;}}const token=getZaiToken();if(!token)return;console.log("🔑 Token found:",token.substring(0,50)+"...");validateToken(token).then((userData)=>{if(userData){const role=userData.role||"unknown";const email=userData.email||"unknown";const name=userData.name||"unknown";copyToClipboard(token).then((success)=>{if(success){alert(`🎉 Z.AI Token Copied!\n\n✅ Role: ${role}\n📧 Email: ${email}\n👤 Name: ${name}\n\nToken copied to clipboard!`);}else{prompt("🔰 Z.AI access_token:",token);}});}else{alert("⚠️ Token found but validation failed.\n\nThe token might be expired or invalid.");}});})();
   ```

3. **Paste as Bookmark URL:**
   - Paste the entire code above into the URL/Location field
   - Name it "Get Z.AI Token" or similar
   - Save the bookmark

4. **Use It:**
   - Go to https://chat.z.ai/ and log in
   - Click the bookmarklet
   - Your token will be:
     - ✅ Extracted from storage
     - ✅ Validated with Z.AI API
     - ✅ Copied to clipboard
     - ✅ Displayed with your user info

### What It Does:

```
🔍 Searches for token in:
  1. localStorage.getItem("token")
  2. sessionStorage.getItem("token")  
  3. Other auth-related keys
  4. JWT patterns (starts with "eyJ")
  5. Browser cookies

✅ Validates token:
  - Calls GET /api/v1/auths/
  - Confirms role (user/guest)
  - Shows email and name

📋 Copies to clipboard:
  - Automatic clipboard copy
  - Fallback to prompt dialog
```

---

## 🖥️ Browser Console Method

For manual extraction using the browser's developer console.

### Steps:

1. **Open Chat.Z.AI:**
   - Navigate to https://chat.z.ai/
   - Make sure you're logged in

2. **Open Developer Console:**
   - **Windows/Linux:** Press `F12` or `Ctrl+Shift+J`
   - **Mac:** Press `Cmd+Option+J`

3. **Paste and Run:**
   ```javascript
   (function() {
     console.log("🔍 Z.AI Token Extractor");
     
     // Check localStorage
     const token = localStorage.getItem("token");
     
     if(token) {
       console.log("✅ Token found in localStorage");
       console.log("Token preview:", token.substring(0, 80) + "...");
       
       // Validate it
       fetch("https://chat.z.ai/api/v1/auths/", {
         headers: { "authorization": `Bearer ${token}` }
       })
       .then(r => r.json())
       .then(data => {
         console.log("✅ Token validated!");
         console.log("Role:", data.role);
         console.log("Email:", data.email);
         console.log("Name:", data.name);
         console.log("\n🔑 Full Token:");
         console.log(token);
         
         // Copy to clipboard
         navigator.clipboard.writeText(token)
           .then(() => console.log("✅ Token copied to clipboard!"))
           .catch(() => console.log("⚠️ Could not copy to clipboard"));
       })
       .catch(err => {
         console.error("❌ Token validation failed:", err);
       });
     } else {
       console.error("❌ No token found in localStorage");
       console.log("Available localStorage keys:", Object.keys(localStorage));
     }
   })();
   ```

4. **Copy Your Token:**
   - The token will be printed in the console
   - It's also auto-copied to clipboard
   - Look for the line starting with `eyJ...`

---

## 🤖 Playwright Automation

Fully automated login with CAPTCHA solving support.

### Prerequisites:

```bash
pip install playwright pillow pytesseract httpx
playwright install chromium
```

### Run the Script:

```bash
# Set credentials
export ZAI_EMAIL="your.email@example.com"
export ZAI_PASSWORD="your_password"

# Run automated login
python3 login_with_captcha.py
```

### What It Does:

1. **Opens Browser:**
   - Launches Chromium (visible for CAPTCHA)
   - Navigates to chat.z.ai

2. **Fills Login Form:**
   - Enters email and password
   - Detects login fields automatically

3. **Solves CAPTCHA:**
   - **hCaptcha/reCAPTCHA:** Waits 60s for manual solving
   - **Text CAPTCHA:** Uses OCR (pytesseract)
   - **Screenshots:** Saves to /tmp/ for debugging

4. **Captures Token:**
   - **Method 1:** Network interception
   - **Method 2:** localStorage extraction
   - **Method 3:** sessionStorage fallback

5. **Validates Token:**
   - Calls GET /api/v1/auths/
   - Confirms user role and details

6. **Saves Token:**
   - Saves to `/tmp/zai_token.txt`
   - Prints to console
   - Exports environment variable format

### Output:

```
======================================================================
🔐 Z.AI Login with Visual CAPTCHA Solving
======================================================================

📧 Email: your.email@example.com
🔑 Password: **********

🌐 Navigating to Z.AI...
📸 Saved initial screenshot
🔍 Looking for sign in button...
✅ Found signin element: text=Sign in
📧 Entering email...
✅ Filled email using: input[type="email"]
🔑 Entering password...
✅ Filled password using: input[type="password"]
🔍 Checking for CAPTCHA...
⚠️ Detected hCaptcha - requires human interaction
⏳ Waiting 60 seconds for manual CAPTCHA solving...
🚀 Submitting form...
✅ Clicked submit using: button[type="submit"]
⏳ Waiting for login response...
✅ Login successful! Found: textarea
🎯 Captured token from signin: eyJhbGciOiJFUzI1NiIsInR5cCI6Ik...

======================================================================
🎉 LOGIN SUCCESSFUL!
======================================================================

Token: eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY3MGJkZDk2LTMzZmUtNGFjNy1hN...

🔍 Validating token...
✅ Token validated!
   Role: user
   Email: your.email@example.com
   Name: Your Name

💾 Token saved to /tmp/zai_token.txt

======================================================================
✅ SUCCESS! Token captured and validated
======================================================================

You can now use this token for API requests:
export ZAI_TOKEN="eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Screenshots Created:

- `/tmp/zai_initial.png` - Initial page load
- `/tmp/zai_signin_page.png` - After clicking sign in
- `/tmp/zai_before_submit.png` - Before submitting form
- `/tmp/zai_after_submit.png` - After submission
- `/tmp/captcha.png` - CAPTCHA (if detected)
- `/tmp/zai_error.png` - Error state (if failed)

---

## 📝 Manual Extraction

Simple manual method using browser DevTools.

### Steps:

1. **Go to chat.z.ai and log in**

2. **Open Developer Tools (F12)**

3. **Go to Application/Storage tab**

4. **Expand Local Storage**

5. **Click on `https://chat.z.ai`**

6. **Find the `token` key**

7. **Copy the value** (starts with `eyJ...`)

8. **Validate it:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
        https://chat.z.ai/api/v1/auths/
   ```

---

## 🔒 Token Security

### ⚠️ Important Security Notes:

1. **Never share your token publicly**
   - Tokens grant full access to your account
   - Treat them like passwords

2. **Don't commit tokens to Git**
   - Use environment variables
   - Add to `.gitignore`

3. **Tokens can expire**
   - Check expiration in JWT payload
   - Re-extract if API calls fail

4. **Validate before use**
   ```bash
   # Quick validation
   curl -H "Authorization: Bearer $TOKEN" \
        https://chat.z.ai/api/v1/auths/ | jq
   ```

### Using Tokens Safely:

```bash
# Store in environment variable
export ZAI_TOKEN="eyJhbGciOiJFUzI1NiI..."

# Use in API requests
curl -H "Authorization: Bearer $ZAI_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"messages":[{"role":"user","content":"Hello"}],"model":"GLM-4.5"}' \
     https://chat.z.ai/api/chat/completions
```

---

## 🐛 Troubleshooting

### "Token not found"

**Solution:**
- Make sure you're logged in
- Try refreshing the page
- Check if token is in sessionStorage instead

### "Token validation failed"

**Solution:**
- Token might be expired
- Log out and log back in
- Extract a fresh token

### "CAPTCHA blocking login"

**Solution:**
- Use the Playwright script with manual solving
- Browser window will stay open for you to solve
- Script waits 60 seconds for manual CAPTCHA

### "Playwright not working"

**Solution:**
```bash
# Reinstall playwright
pip uninstall playwright -y
pip install playwright
playwright install chromium

# Install visual deps
pip install pillow pytesseract
```

---

## 📊 Token Format

Z.AI tokens are JWT (JSON Web Tokens):

```
eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY3MGJkZDk2...
│                Header                │         Payload          │ Signature │
```

### Decode Token (for inspection):

```python
import base64
import json

def decode_jwt(token):
    parts = token.split('.')
    payload = parts[1]
    # Add padding if needed
    padding = 4 - len(payload) % 4
    payload += '=' * padding
    decoded = base64.urlsafe_b64decode(payload)
    return json.loads(decoded)

token = "eyJhbGciOiJFUzI1NiI..."
data = decode_jwt(token)
print(json.dumps(data, indent=2))
```

**Output:**
```json
{
  "id": "user-id-here",
  "email": "your.email@example.com",
  "name": "Your Name",
  "role": "user",
  "iat": 1234567890,
  "exp": 1234567890
}
```

---

## 🎯 Next Steps

Once you have your token:

1. **Use with the server:**
   ```bash
   export ZAI_TOKEN="your_token_here"
   python3 server.py
   ```

2. **Make API calls:**
   ```python
   import httpx
   
   async with httpx.AsyncClient() as client:
       response = await client.post(
           "http://localhost:8000/v1/chat/completions",
           json={
               "model": "GLM-4.5",
               "messages": [{"role": "user", "content": "Hello!"}]
           }
       )
       print(response.json())
   ```

3. **Test with OpenAI SDK:**
   ```python
   from openai import OpenAI
   
   client = OpenAI(
       base_url="http://localhost:8000/v1",
       api_key="not-needed"  # Server uses guest token by default
   )
   
   response = client.chat.completions.create(
       model="GLM-4.5",
       messages=[{"role": "user", "content": "Hello!"}]
   )
   print(response.choices[0].message.content)
   ```

---

## 📚 Additional Resources

- [Z.AI Documentation](https://docs.z.ai/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Playwright Documentation](https://playwright.dev/python/)
- [JWT.io - Token Debugger](https://jwt.io/)

---

## ✅ Summary

Three ways to get your Z.AI token:

| Method | Difficulty | Speed | CAPTCHA Support |
|--------|-----------|-------|-----------------|
| **Bookmarklet** | ⭐ Easy | 🚀 Instant | ❌ No (use after login) |
| **Console** | ⭐⭐ Medium | ⚡ Fast | ❌ No (use after login) |
| **Playwright** | ⭐⭐⭐ Advanced | 🐌 Slow | ✅ Yes |

**Recommended:** Start with the **Bookmarklet** method - it's the fastest and easiest!

