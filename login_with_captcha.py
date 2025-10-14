#!/usr/bin/env python3
"""
Automated Z.AI Login with Visual CAPTCHA Solving
Uses Playwright + OCR/Computer Vision for CAPTCHA solving
"""

import os
import asyncio
import json
import time
from playwright.async_api import async_playwright
from PIL import Image
import io

# Login credentials
EMAIL = os.getenv("ZAI_EMAIL", "developer@pixelium.uk")
PASSWORD = os.getenv("ZAI_PASSWORD", "developer123?")

async def solve_captcha_visual(page):
    """
    Attempt to solve CAPTCHA using visual analysis
    Returns True if solved, False if failed
    """
    try:
        # Check if CAPTCHA is present
        captcha_present = await page.locator('iframe[src*="captcha"], img[alt*="captcha"], canvas[class*="captcha"]').count() > 0
        
        if not captcha_present:
            print("✅ No CAPTCHA detected")
            return True
        
        print("🔍 CAPTCHA detected, analyzing...")
        
        # Take screenshot of CAPTCHA area
        captcha_element = page.locator('iframe[src*="captcha"], img[alt*="captcha"], canvas[class*="captcha"]').first
        
        if await captcha_element.count() > 0:
            screenshot_bytes = await captcha_element.screenshot()
            
            # Save for inspection
            with open('/tmp/captcha.png', 'wb') as f:
                f.write(screenshot_bytes)
            print("📸 Saved CAPTCHA screenshot to /tmp/captcha.png")
            
            # Try to detect CAPTCHA type
            img = Image.open(io.BytesIO(screenshot_bytes))
            width, height = img.size
            print(f"   CAPTCHA size: {width}x{height}")
            
            # Check for common CAPTCHA patterns
            # 1. Click verification (hCaptcha, reCAPTCHA)
            if 'hcaptcha' in await page.content() or 'recaptcha' in await page.content():
                print("⚠️ Detected hCaptcha/reCAPTCHA - requires human interaction")
                print("   Please solve manually in the browser window...")
                
                # Wait for human to solve (30 seconds)
                print("⏳ Waiting 30 seconds for manual CAPTCHA solving...")
                await asyncio.sleep(30)
                
                return True
            
            # 2. Text-based CAPTCHA (can use OCR)
            elif width < 300 and height < 100:
                print("🔤 Detected text-based CAPTCHA")
                try:
                    import pytesseract
                    text = pytesseract.image_to_string(img)
                    print(f"   OCR Result: {text.strip()}")
                    
                    # Find input field and enter text
                    captcha_input = await page.locator('input[type="text"][placeholder*="captcha" i], input[name*="captcha" i]').first
                    if await captcha_input.count() > 0:
                        await captcha_input.fill(text.strip())
                        print("✅ Entered CAPTCHA text")
                        return True
                except:
                    print("⚠️ OCR failed, falling back to manual")
        
        return False
        
    except Exception as e:
        print(f"⚠️ CAPTCHA solving error: {e}")
        return False

async def login_to_zai():
    """
    Login to Z.AI with CAPTCHA solving
    Returns the authentication token
    """
    
    print("=" * 70)
    print("🔐 Z.AI Login with Visual CAPTCHA Solving")
    print("=" * 70)
    print()
    print(f"📧 Email: {EMAIL}")
    print(f"🔑 Password: {'*' * len(PASSWORD)}")
    print()
    
    captured_token = None
    
    async with async_playwright() as p:
        # Launch browser (headless=False to see CAPTCHA)
        browser = await p.chromium.launch(
            headless=False,  # Show browser for manual CAPTCHA if needed
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        # Intercept network requests to capture token
        async def handle_response(response):
            nonlocal captured_token
            
            if 'chat.z.ai/api' in response.url:
                try:
                    # Check for signin response
                    if '/auths/signin' in response.url and response.status == 200:
                        data = await response.json()
                        token = data.get('token')
                        if token:
                            captured_token = token
                            print(f"🎯 Captured token from signin: {token[:50]}...")
                    
                    # Also check auth endpoint
                    elif '/auths/' in response.url and response.status == 200:
                        data = await response.json()
                        token = data.get('token')
                        role = data.get('role')
                        if token:
                            print(f"📡 Token type: {role}")
                            if role == 'user':
                                captured_token = token
                                print(f"✅ Captured USER token: {token[:50]}...")
                
                except Exception as e:
                    pass
        
        page.on('response', handle_response)
        
        async def extract_token_from_storage(page):
            """Extract token from localStorage/sessionStorage using JavaScript"""
            try:
                token = await page.evaluate("""
                    () => {
                        // Method 1: Check localStorage
                        const localToken = localStorage.getItem("token");
                        if(localToken) return localToken;
                        
                        // Method 2: Check sessionStorage
                        const sessionToken = sessionStorage.getItem("token");
                        if(sessionToken) return sessionToken;
                        
                        // Method 3: Check for JWT-like values
                        for(let i = 0; i < localStorage.length; i++) {
                            const key = localStorage.key(i);
                            const value = localStorage.getItem(key);
                            if(value && value.startsWith("eyJ")) {
                                return value;
                            }
                        }
                        
                        return null;
                    }
                """)
                return token
            except Exception as e:
                print(f"⚠️ Error extracting token from storage: {e}")
                return None
        
        try:
            # Navigate to Z.AI
            print("🌐 Navigating to Z.AI...")
            await page.goto('https://chat.z.ai/', wait_until='domcontentloaded', timeout=30000)
            await asyncio.sleep(2)
            
            # Take screenshot of initial page
            await page.screenshot(path='/tmp/zai_initial.png')
            print("📸 Saved initial screenshot")
            
            # Look for sign in button/link
            print("🔍 Looking for sign in button...")
            
            # Try multiple selectors
            signin_selectors = [
                'text=Sign in',
                'text=Log in',
                'text=Login',
                'button:has-text("Sign")',
                'a:has-text("Sign")',
                '[href*="signin"]',
                '[href*="login"]'
            ]
            
            signin_clicked = False
            for selector in signin_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0 and await element.is_visible():
                        print(f"✅ Found signin element: {selector}")
                        await element.click()
                        signin_clicked = True
                        await asyncio.sleep(2)
                        break
                except:
                    continue
            
            if not signin_clicked:
                print("⚠️ No signin button found, might already be on login page")
            
            # Take screenshot after clicking
            await page.screenshot(path='/tmp/zai_signin_page.png')
            print("📸 Saved signin page screenshot")
            
            # Fill in email
            print("📧 Entering email...")
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="email" i]',
                'input[id*="email" i]'
            ]
            
            email_filled = False
            for selector in email_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        await element.fill(EMAIL)
                        email_filled = True
                        print(f"✅ Filled email using: {selector}")
                        break
                except:
                    continue
            
            if not email_filled:
                print("❌ Could not find email input field")
                await page.screenshot(path='/tmp/zai_no_email_field.png')
                return None
            
            await asyncio.sleep(1)
            
            # Fill in password
            print("🔑 Entering password...")
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[id*="password" i]'
            ]
            
            password_filled = False
            for selector in password_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        await element.fill(PASSWORD)
                        password_filled = True
                        print(f"✅ Filled password using: {selector}")
                        break
                except:
                    continue
            
            if not password_filled:
                print("❌ Could not find password input field")
                await page.screenshot(path='/tmp/zai_no_password_field.png')
                return None
            
            await asyncio.sleep(1)
            
            # Take screenshot before submit
            await page.screenshot(path='/tmp/zai_before_submit.png')
            print("📸 Saved pre-submit screenshot")
            
            # Check for CAPTCHA before submitting
            print("🔍 Checking for CAPTCHA...")
            captcha_solved = await solve_captcha_visual(page)
            
            if not captcha_solved:
                print("⚠️ CAPTCHA needs manual solving")
                print("   Browser window is open - please solve the CAPTCHA")
                print("   Waiting 60 seconds...")
                await asyncio.sleep(60)
            
            # Click submit button
            print("🚀 Submitting form...")
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Sign")',
                'button:has-text("Log")',
                'input[type="submit"]',
                'button:has-text("Continue")'
            ]
            
            submit_clicked = False
            for selector in submit_selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0 and await element.is_visible():
                        await element.click()
                        submit_clicked = True
                        print(f"✅ Clicked submit using: {selector}")
                        break
                except:
                    continue
            
            if not submit_clicked:
                print("❌ Could not find submit button")
                await page.screenshot(path='/tmp/zai_no_submit_button.png')
                return None
            
            # Wait for navigation or response
            print("⏳ Waiting for login response...")
            await asyncio.sleep(5)
            
            # Take screenshot after submit
            await page.screenshot(path='/tmp/zai_after_submit.png')
            print("📸 Saved post-submit screenshot")
            
            # Check if login successful by looking for chat interface
            chat_elements = [
                'textarea',
                'input[placeholder*="message" i]',
                'div[class*="chat"]',
                'div[role="textbox"]'
            ]
            
            login_success = False
            for selector in chat_elements:
                try:
                    if await page.locator(selector).count() > 0:
                        login_success = True
                        print(f"✅ Login successful! Found: {selector}")
                        break
                except:
                    continue
            
            # If no token captured from network, try localStorage
            if login_success and not captured_token:
                print("🔍 Attempting to extract token from localStorage...")
                captured_token = await extract_token_from_storage(page)
                if captured_token:
                    print(f"✅ Extracted token from localStorage: {captured_token[:50]}...")
            
            if login_success and captured_token:
                print()
                print("=" * 70)
                print("🎉 LOGIN SUCCESSFUL!")
                print("=" * 70)
                print()
                print(f"Token: {captured_token[:80]}...")
                print()
                
                # Validate token
                print("🔍 Validating token...")
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        'https://chat.z.ai/api/v1/auths/',
                        headers={'authorization': f'Bearer {captured_token}'}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ Token validated!")
                        print(f"   Role: {data.get('role')}")
                        print(f"   Email: {data.get('email')}")
                        print(f"   Name: {data.get('name')}")
                    else:
                        print(f"⚠️ Token validation failed: {response.status_code}")
                
                # Save token
                with open('/tmp/zai_token.txt', 'w') as f:
                    f.write(captured_token)
                print()
                print("💾 Token saved to /tmp/zai_token.txt")
                
                return captured_token
            
            elif not captured_token:
                print("⚠️ Login might have succeeded but token not captured")
                print("   Check screenshots in /tmp/")
            else:
                print("❌ Login failed - no chat interface detected")
            
            # Keep browser open for inspection
            print()
            print("🔍 Browser staying open for 30 seconds for inspection...")
            await asyncio.sleep(30)
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            import traceback
            traceback.print_exc()
            await page.screenshot(path='/tmp/zai_error.png')
            
        finally:
            await browser.close()
    
    return captured_token

async def main():
    """Main entry point"""
    token = await login_to_zai()
    
    if token:
        print()
        print("=" * 70)
        print("✅ SUCCESS! Token captured and validated")
        print("=" * 70)
        print()
        print(f"Token: {token}")
        print()
        print("You can now use this token for API requests:")
        print(f'export ZAI_TOKEN="{token}"')
        return 0
    else:
        print()
        print("=" * 70)
        print("❌ FAILED to get token")
        print("=" * 70)
        print()
        print("Check screenshots in /tmp/ for debugging")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
