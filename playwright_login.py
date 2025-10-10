#!/usr/bin/env python3
"""
Use Playwright to login to Z.AI and get a real authenticated token
"""

import os
import sys
import json
import time
import asyncio
from playwright.async_api import async_playwright

async def login_with_playwright():
    """Login to Z.AI using Playwright and extract token"""
    
    EMAIL = os.getenv("ZAI_EMAIL", "developer@pixelium.uk")
    PASSWORD = os.getenv("ZAI_PASSWORD", "developer123?")
    
    print("="*70)
    print("🎭 Z.AI Login with Playwright - REAL BROWSER SESSION")
    print("="*70)
    print()
    print(f"📧 Email: {EMAIL}")
    print(f"🔑 Password: {'*' * len(PASSWORD)}")
    print()
    
    async with async_playwright() as p:
        # Launch browser
        print("🚀 Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        # Go directly to auth page
        print("📍 Navigating directly to auth page...")
        await page.goto('https://chat.z.ai/auth', timeout=60000)
        
        # Wait for the page to be fully loaded (SPA)
        print("⏳ Waiting for SPA to load...")
        await page.wait_for_load_state('networkidle', timeout=30000)
        await page.wait_for_timeout(5000)
        
        # Take screenshot
        await page.screenshot(path='/tmp/z_ai_page.png')
        print("📸 Screenshot saved to /tmp/z_ai_page.png")
        
        # Look for email/password fields
        print("🔍 Looking for login form...")
        email_selectors = [
            'input[type="email"]',
            'input[name="email"]',
            'input[placeholder*="email" i]',
            'input[placeholder*="Email" i]',
            '#email',
            '[name="username"]'
        ]
        
        password_selectors = [
            'input[type="password"]',
            'input[name="password"]',
            '#password'
        ]
        
        email_field = None
        for selector in email_selectors:
            try:
                email_field = await page.wait_for_selector(selector, timeout=3000)
                if email_field:
                    print(f"✅ Found email field: {selector}")
                    break
            except:
                continue
        
        password_field = None
        for selector in password_selectors:
            try:
                password_field = await page.wait_for_selector(selector, timeout=3000)
                if password_field:
                    print(f"✅ Found password field: {selector}")
                    break
            except:
                continue
        
        if not email_field or not password_field:
            print("❌ Could not find login fields!")
            print("📄 Page content:")
            content = await page.content()
            print(content[:1000])
            await browser.close()
            return None
        
        # Fill in credentials
        print("✍️ Filling in credentials...")
        await email_field.fill(EMAIL)
        await password_field.fill(PASSWORD)
        await page.wait_for_timeout(1000)
        
        # Take screenshot before submit
        await page.screenshot(path='/tmp/z_ai_filled.png')
        print("📸 Screenshot saved to /tmp/z_ai_filled.png")
        
        # Find and click submit button
        print("🔍 Looking for submit button...")
        submit_selectors = [
            'button[type="submit"]',
            'button:has-text("Sign in")',
            'button:has-text("Log in")',
            'button:has-text("Login")',
            'input[type="submit"]',
            '[type="submit"]'
        ]
        
        for selector in submit_selectors:
            try:
                submit_btn = await page.wait_for_selector(selector, timeout=3000)
                if submit_btn:
                    print(f"✅ Found submit button: {selector}")
                    await submit_btn.click()
                    break
            except:
                continue
        
        # Wait for navigation/login
        print("⏳ Waiting for login to complete...")
        try:
            await page.wait_for_url('**/chat.z.ai/**', timeout=15000)
            print("✅ Login navigation detected!")
        except:
            print("⚠️ No URL change, checking for success indicators...")
        
        await page.wait_for_timeout(3000)
        
        # Take screenshot after login
        await page.screenshot(path='/tmp/z_ai_logged_in.png')
        print("📸 Screenshot saved to /tmp/z_ai_logged_in.png")
        
        # Extract tokens from cookies and localStorage
        print("🔑 Extracting authentication token...")
        
        # Method 1: Cookies
        cookies = await context.cookies()
        print(f"📦 Found {len(cookies)} cookies")
        
        token = None
        for cookie in cookies:
            if 'token' in cookie['name'].lower() or 'auth' in cookie['name'].lower():
                print(f"  🍪 Cookie: {cookie['name']} = {cookie['value'][:50]}...")
                if not token:
                    token = cookie['value']
        
        # Method 2: localStorage
        local_storage = await page.evaluate('''() => {
            let items = {};
            for (let i = 0; i < localStorage.length; i++) {
                let key = localStorage.key(i);
                items[key] = localStorage.getItem(key);
            }
            return items;
        }''')
        
        print(f"💾 LocalStorage items: {list(local_storage.keys())}")
        for key, value in local_storage.items():
            if 'token' in key.lower() or 'auth' in key.lower():
                print(f"  💾 {key} = {str(value)[:50]}...")
                if not token:
                    token = value
        
        # Method 3: Check for Authorization header in network requests
        print("🌐 Monitoring network requests for auth tokens...")
        
        captured_token = []
        
        async def capture_request(request):
            headers = request.headers
            if 'authorization' in headers:
                auth = headers['authorization']
                if auth.startswith('Bearer '):
                    captured_token.append(auth.replace('Bearer ', ''))
                    print(f"  🎯 Captured Authorization header: {auth[:50]}...")
        
        page.on('request', capture_request)
        
        # Trigger a request by navigating or interacting
        await page.reload()
        await page.wait_for_timeout(3000)
        
        if captured_token:
            token = captured_token[0]
        
        # Method 4: sessionStorage
        session_storage = await page.evaluate('''() => {
            let items = {};
            for (let i = 0; i < sessionStorage.length; i++) {
                let key = sessionStorage.key(i);
                items[key] = sessionStorage.getItem(key);
            }
            return items;
        }''')
        
        print(f"📦 SessionStorage items: {list(session_storage.keys())}")
        for key, value in session_storage.items():
            if 'token' in key.lower() or 'auth' in key.lower():
                print(f"  📦 {key} = {str(value)[:50]}...")
                if not token:
                    token = value
        
        await browser.close()
        
        if token:
            print()
            print("="*70)
            print("✅ SUCCESS! Extracted authentication token:")
            print("="*70)
            print(f"Token: {token[:100]}...")
            print("="*70)
            return token
        else:
            print()
            print("="*70)
            print("❌ Could not extract token")
            print("="*70)
            return None

async def test_token(token):
    """Test the extracted token with a real API call"""
    import requests
    import uuid
    
    print()
    print("="*70)
    print("🧪 Testing extracted token with real API call...")
    print("="*70)
    print()
    
    chat_url = "https://chat.z.ai/api/v1/chats/new"
    test_message = "What is 2+2? Answer in one short sentence."
    
    headers = {
        "accept": "*/*",
        "authorization": f"Bearer {token}",
        "content-type": "application/json",
        "origin": "https://chat.z.ai",
        "referer": "https://chat.z.ai/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "x-fe-version": "prod-fe-1.0.70"
    }
    
    message_id = str(uuid.uuid4())
    timestamp = int(time.time())
    
    payload = {
        "chat": {
            "id": "",
            "title": "Playwright Token Test",
            "models": ["glm-4.5v"],
            "params": {},
            "history": {
                "messages": {
                    message_id: {
                        "id": message_id,
                        "parentId": None,
                        "childrenIds": [],
                        "role": "user",
                        "content": test_message,
                        "timestamp": timestamp,
                        "models": ["glm-4.5v"]
                    }
                },
                "currentId": message_id
            },
            "messages": [{
                "id": message_id,
                "parentId": None,
                "childrenIds": [],
                "role": "user",
                "content": test_message,
                "timestamp": timestamp,
                "models": ["glm-4.5v"]
            }],
            "tags": [],
            "flags": [],
            "features": [],
            "mcp_servers": [],
            "enable_thinking": False,
            "timestamp": timestamp
        }
    }
    
    try:
        response = requests.post(chat_url, headers=headers, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            chat_id = data.get('id')
            print(f"✅ Chat created successfully!")
            print(f"Chat ID: {chat_id}")
            print()
            
            # Try completion
            print("🚀 Trying completion...")
            completion_url = "https://chat.z.ai/api/chat/completions"
            completion_payload = {
                "model": "glm-4.5v",
                "messages": [{"role": "user", "content": test_message}],
                "stream": False,
                "chatId": chat_id,
                "parentMessageId": message_id
            }
            
            comp_response = requests.post(completion_url, headers=headers, json=completion_payload, timeout=45)
            print(f"Status: {comp_response.status_code}")
            
            if comp_response.status_code == 200:
                result = comp_response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0].get('message', {}).get('content', '')
                    if content:
                        print()
                        print("="*70)
                        print("✅ ASSISTANT RESPONSE:")
                        print("="*70)
                        print(content)
                        print("="*70)
                        print()
                        print("🎉 FULL SUCCESS WITH PLAYWRIGHT TOKEN!")
            else:
                print(f"Completion response: {comp_response.text[:500]}")
        else:
            print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    token = await login_with_playwright()
    
    if token:
        # Save token to file
        with open('/tmp/z_ai_token.txt', 'w') as f:
            f.write(token)
        print(f"💾 Token saved to /tmp/z_ai_token.txt")
        
        # Test the token
        await test_token(token)
    else:
        print("❌ Failed to get token")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
