#!/usr/bin/env python3
"""
Use Playwright to capture Z.AI's actual API behavior
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright

EMAIL = os.getenv("ZAI_EMAIL", "developer@pixelium.uk")
PASSWORD = os.getenv("ZAI_PASSWORD", "developer123?")

async def capture_zai_traffic():
    """Capture real Z.AI traffic using Playwright"""
    
    print("="*70)
    print("🔍 CAPTURING Z.AI TRAFFIC WITH PLAYWRIGHT")
    print("="*70)
    print()
    
    # Store captured requests
    api_requests = []
    
    async with async_playwright() as p:
        # Launch browser with network tracking (headless for server environment)
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Capture all requests
        async def handle_request(request):
            if 'chat.z.ai/api' in request.url:
                api_requests.append({
                    'method': request.method,
                    'url': request.url,
                    'headers': dict(request.headers),
                    'post_data': request.post_data if request.method == 'POST' else None,
                    'timestamp': None
                })
                print(f"📤 {request.method} {request.url}")
        
        # Capture all responses
        async def handle_response(response):
            if 'chat.z.ai/api' in response.url:
                try:
                    body = await response.text()
                    print(f"📥 {response.status} {response.url}")
                    print(f"   Body preview: {body[:200]}")
                except:
                    pass
        
        page.on('request', handle_request)
        page.on('response', handle_response)
        
        # Navigate to Z.AI
        print("🌐 Navigating to Z.AI...")
        await page.goto('https://chat.z.ai/', wait_until='networkidle')
        await asyncio.sleep(2)
        
        # Click sign in
        print("🔐 Logging in...")
        try:
            await page.click('text=Sign in', timeout=5000)
            await asyncio.sleep(1)
            
            # Fill email
            await page.fill('input[type="email"]', EMAIL)
            await asyncio.sleep(0.5)
            
            # Fill password
            await page.fill('input[type="password"]', PASSWORD)
            await asyncio.sleep(0.5)
            
            # Click submit
            await page.click('button[type="submit"]')
            await asyncio.sleep(5)
            
            print("✅ Logged in, waiting for chat interface...")
            
        except Exception as e:
            print(f"⚠️ Login flow error (might already be logged in): {e}")
        
        # Wait for chat interface
        await asyncio.sleep(3)
        
        # Try to send a message
        print("📝 Sending test message...")
        try:
            # Find and fill textarea
            await page.fill('textarea', 'What is your model name?')
            await asyncio.sleep(1)
            
            # Click send button
            await page.click('button[type="submit"]', timeout=5000)
            
            print("✅ Message sent, capturing response...")
            
            # Wait for response
            await asyncio.sleep(15)
            
        except Exception as e:
            print(f"⚠️ Message send error: {e}")
        
        # Save captured requests
        print()
        print("="*70)
        print("💾 SAVING CAPTURED TRAFFIC")
        print("="*70)
        print()
        
        output_file = '/tmp/zai_captured_traffic.json'
        with open(output_file, 'w') as f:
            json.dump(api_requests, f, indent=2)
        
        print(f"✅ Saved {len(api_requests)} API requests to {output_file}")
        print()
        
        # Print summary
        print("📊 CAPTURED ENDPOINTS:")
        unique_endpoints = set(req['url'] for req in api_requests)
        for endpoint in sorted(unique_endpoints):
            print(f"  - {endpoint}")
        
        print()
        print("🎯 Check the browser window and captured traffic!")
        print("Press Enter to close...")
        
        # Keep browser open for manual inspection
        await asyncio.sleep(30)
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(capture_zai_traffic())
