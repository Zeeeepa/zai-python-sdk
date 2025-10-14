/**
 * Z.AI Token Extractor Bookmarklet
 * 
 * How to use:
 * 1. Create a new bookmark in your browser
 * 2. Copy the entire "javascript:(function(){..." code below
 * 3. Paste it as the bookmark URL
 * 4. Navigate to https://chat.z.ai/
 * 5. Click the bookmark to extract your token
 */

// BOOKMARKLET CODE (copy everything below as ONE LINE):
javascript:(function(){
  if(window.location.hostname !== "chat.z.ai") {
    alert("🚀 This code is for chat.z.ai");
    window.open("https://chat.z.ai", "_blank");
    return;
  }
  
  function getZaiToken() {
    // Method 1: Check localStorage for token
    const localToken = localStorage.getItem("token");
    if(localToken) {
      console.log("✅ Found token in localStorage");
      return localToken;
    }
    
    // Method 2: Check sessionStorage
    const sessionToken = sessionStorage.getItem("token");
    if(sessionToken) {
      console.log("✅ Found token in sessionStorage");
      return sessionToken;
    }
    
    // Method 3: Check for auth-related items
    const authKeys = ["auth_token", "access_token", "jwt", "bearer"];
    for(const key of authKeys) {
      const val = localStorage.getItem(key) || sessionStorage.getItem(key);
      if(val) {
        console.log(`✅ Found token as '${key}'`);
        return val;
      }
    }
    
    // Method 4: Check all localStorage keys
    console.log("🔍 Searching all localStorage keys...");
    for(let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      const value = localStorage.getItem(key);
      if(value && value.startsWith("eyJ")) { // JWT tokens start with eyJ
        console.log(`✅ Found JWT-like token in '${key}'`);
        return value;
      }
    }
    
    // Method 5: Parse cookies
    const cookies = document.cookie.split(';');
    for(const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if(value && value.startsWith("eyJ")) {
        console.log(`✅ Found JWT-like token in cookie '${name}'`);
        return value;
      }
    }
    
    alert("❌ Z.AI access_token not found!\n\nPlease make sure you're logged in to chat.z.ai");
    return null;
  }
  
  async function copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch(err) {
      console.error("❌ Failed to copy to clipboard:", err);
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.style.position = "fixed";
      textarea.style.opacity = "0";
      document.body.appendChild(textarea);
      textarea.focus();
      textarea.select();
      const success = document.execCommand("copy");
      document.body.removeChild(textarea);
      return success;
    }
  }
  
  async function validateToken(token) {
    try {
      const response = await fetch("https://chat.z.ai/api/v1/auths/", {
        headers: {
          "authorization": `Bearer ${token}`
        }
      });
      
      if(response.ok) {
        const data = await response.json();
        console.log("✅ Token validated:", data);
        return data;
      } else {
        console.error("❌ Token validation failed:", response.status);
        return null;
      }
    } catch(err) {
      console.error("❌ Validation error:", err);
      return null;
    }
  }
  
  const token = getZaiToken();
  if(!token) return;
  
  console.log("🔑 Token found:", token.substring(0, 50) + "...");
  
  // Validate token
  validateToken(token).then((userData) => {
    if(userData) {
      const role = userData.role || "unknown";
      const email = userData.email || "unknown";
      const name = userData.name || "unknown";
      
      copyToClipboard(token).then((success) => {
        if(success) {
          alert(`🎉 Z.AI Token Copied!\n\n✅ Role: ${role}\n📧 Email: ${email}\n👤 Name: ${name}\n\nToken copied to clipboard!`);
        } else {
          prompt("🔰 Z.AI access_token:", token);
        }
      });
    } else {
      alert("⚠️ Token found but validation failed.\n\nThe token might be expired or invalid.");
    }
  });
})();


/**
 * FORMATTED VERSION FOR MANUAL EXECUTION (in browser console):
 */

// Just paste this in the browser console at chat.z.ai:
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

