# From the code you provided, let me extract the exact signature algorithm

import hmac
import hashlib
import time

def generate_signature_v1(message_text: str, request_id: str, timestamp_ms: int, user_id: str, secret: str = "junjie") -> str:
    """Original version from code"""
    r = str(timestamp_ms)
    e = f"requestId,{request_id},timestamp,{timestamp_ms},user_id,{user_id}"
    t = message_text or ""
    i = f"{e}|{t}|{r}"

    window_index = timestamp_ms // (5 * 60 * 1000)
    root_key = (secret or "junjie").encode("utf-8")
    derived_hex = hmac.new(root_key, str(window_index).encode("utf-8"), hashlib.sha256).hexdigest()
    signature = hmac.new(derived_hex.encode("utf-8"), i.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature

def generate_signature_v2(message_text: str, request_id: str, timestamp_ms: int, user_id: str, secret: str = "junjie") -> str:
    """Try different window calculation (5 ** 60 ** 1000 from comments)"""
    r = str(timestamp_ms)
    e = f"requestId,{request_id},timestamp,{timestamp_ms},user_id,{user_id}"
    t = message_text or ""
    i = f"{e}|{t}|{r}"

    # Note the ** (power) instead of * in the comment
    window_index = timestamp_ms // (5 ** 60 ** 1000)  # This would be HUGE
    root_key = (secret or "junjie").encode("utf-8")
    derived_hex = hmac.new(root_key, str(window_index).encode("utf-8"), hashlib.sha256).hexdigest()
    signature = hmac.new(derived_hex.encode("utf-8"), i.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature

def generate_signature_v3(message_text: str, request_id: str, timestamp_ms: int, user_id: str, secret: str = "junjie") -> str:
    """Try without the final timestamp"""
    e = f"requestId,{request_id},timestamp,{timestamp_ms},user_id,{user_id}"
    t = message_text or ""
    i = f"{e}|{t}"  # No final |{timestamp_ms}

    window_index = timestamp_ms // (5 * 60 * 1000)
    root_key = (secret or "junjie").encode("utf-8")
    derived_hex = hmac.new(root_key, str(window_index).encode("utf-8"), hashlib.sha256).hexdigest()
    signature = hmac.new(derived_hex.encode("utf-8"), i.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature

def generate_signature_v4(message_text: str, request_id: str, timestamp_ms: int, user_id: str, secret: str = "junjie") -> str:
    """Try seconds instead of milliseconds for window"""
    r = str(timestamp_ms)
    e = f"requestId,{request_id},timestamp,{timestamp_ms},user_id,{user_id}"
    t = message_text or ""
    i = f"{e}|{t}|{r}"

    timestamp_sec = timestamp_ms // 1000
    window_index = timestamp_sec // (5 * 60)  # 5 minute windows in seconds
    root_key = (secret or "junjie").encode("utf-8")
    derived_hex = hmac.new(root_key, str(window_index).encode("utf-8"), hashlib.sha256).hexdigest()
    signature = hmac.new(derived_hex.encode("utf-8"), i.encode("utf-8"), hashlib.sha256).hexdigest()
    return signature

# Test all versions
timestamp_ms = int(time.time() * 1000)
request_id = "test-request-id"
user_id = "guest"
message = "What is your model?"

print("Testing different signature algorithms:")
print("=" * 70)
print(f"Timestamp: {timestamp_ms}")
print(f"Request ID: {request_id}")
print(f"User ID: {user_id}")
print(f"Message: {message}")
print()

sig1 = generate_signature_v1(message, request_id, timestamp_ms, user_id)
print(f"V1 (original):           {sig1}")

sig2 = generate_signature_v2(message, request_id, timestamp_ms, user_id)
print(f"V2 (power operator):     {sig2}")

sig3 = generate_signature_v3(message, request_id, timestamp_ms, user_id)
print(f"V3 (no final timestamp): {sig3}")

sig4 = generate_signature_v4(message, request_id, timestamp_ms, user_id)
print(f"V4 (seconds window):     {sig4}")

print()
print("Let's also check the window_index values:")
print(f"V1 window: {timestamp_ms // (5 * 60 * 1000)}")
print(f"V4 window: {(timestamp_ms // 1000) // (5 * 60)}")
