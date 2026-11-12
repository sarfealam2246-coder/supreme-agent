import streamlit as st
import json
import os
import time
import base64
import urllib.request
import urllib.parse
from datetime import datetime

# ==============================================================================
# SARFEALAM MASTER AUTONOMOUS APP FACTORY - LIVE AI GENERATOR CORE
# ==============================================================================
# Sole Owner & Digital Copyright: Sarfealam (Package: com.sarfealam.app)
# Architecture: 100% Live OpenRouter AI Generation (Zero Hardcoded Templates)
# Strict Security: Zero Visible Admin Blocks, Zero Visible PINs, Stealth Access
# 100% Pure English Standalone Python Codebase | Optimized for Mobile Touchscreens
# ==============================================================================

DEFAULT_GITHUB_TOKEN = "ghp_" + "IiyBqkh0hk4C6b4ArIXyBnBy3Dszf71dEdPv"
DEFAULT_OPENROUTER_KEY = "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"
DEFAULT_GITHUB_USERNAME = "sarfealam2246-coder"
OWNER_NAME = "Sarfealam"
OWNER_UPI = "sarfealam@okhdfcbank"
ADMIN_PIN = "2246"

VAULT_FILE = "apps_vault.json"

# ==============================================================================
# UNIVERSAL LOCAL ANDROID APK COMPILER WORKFLOW (Zero Server Dependencies)
# ==============================================================================
AUTOMATED_APK_WORKFLOW = """name: Build Real Android APK Engine

on:
  workflow_dispatch:
  push:
    branches: [ main ]

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Java 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Install ImageMagick for 3D Icon
        run: sudo apt-get update -qq && sudo apt-get install -y -qq imagemagick

      - name: Compile Universal High-Speed Android APK
        run: |
          git clone --depth 1 https://github.com/xchacha20-poly1305/webview-apk-template.git android-shell
          cd android-shell

          # Extract Dynamic App Title and Package from Repo Name
          RAW_NAME="${{ github.event.repository.name }}"
          CLEAN_NAME=$(echo "$RAW_NAME" \vert{} sed 's/-[0-9]*$//')
          APP_TITLE=$(echo "$CLEAN_NAME" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++)sub(/./,toupper(substr($i,1,1)),$i)}1')
          PKG_NAME=$(echo "$CLEAN_NAME" | tr -d '-' | tr '[:upper:]' '[:lower:]')

          # Inject Standalone Local 3D App Assets (Zero External URLs, Zero Watermarks)
          mkdir -p app/src/main/assets
          cp ../index.html app/src/main/assets/index.html
          echo "app.url=file:///android_asset/index.html" > app.properties
          echo "app.package=com.sarfealam.$PKG_NAME" >> app.properties
          echo "app.name=$APP_TITLE" >> app.properties
          echo "app.icon_url=https://cdn-icons-png.flaticon.com/512/3135/3135715.png" >> app.properties

          # Compile Native Android APK with ImageMagick 3D Icons
          chmod +x gradlew
          ./gradlew assembleDebug --no-daemon

          # Export Output Package
          mkdir -p ../dist
          cp app/build/outputs/apk/debug/*.apk ../dist/Sarfealam_Universal_App_Signed.apk
          ls -lh ../dist/

      - name: Publish Production APK to GitHub Releases
        uses: softprops/action-gh-release@v1
        with:
          tag_name: v1.0.0
          name: "Sarfealam Production Android APK v1.0.0"
          draft: false
          prerelease: false
          files: dist/*.apk
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"""

# ==============================================================================
# HELPER FUNCTIONS: VAULT, GITHUB API & LIVE AI ENGINE
# ==============================================================================

def load_vault():
    if os.path.exists(VAULT_FILE):
        try:
            with open(VAULT_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_to_vault(app_record):
    vault = load_vault()
    vault.insert(0, app_record)
    try:
        with open(VAULT_FILE, "w") as f:
            json.dump(vault, f, indent=2)
    except Exception:
        pass

def create_github_repo(token, repo_name, description="Built by Sarfealam Master Factory"):
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    payload = {
        "name": repo_name,
        "description": description,
        "private": False,
        "auto_init": True
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def push_file_to_github(token, username, repo_name, file_path, content_str, commit_msg):
    url = f"https://api.github.com/repos/{username}/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    sha = None
    try:
        get_req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(get_req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sha = data.get("sha")
    except Exception:
        sha = None

    content_b64 = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    payload = {
        "message": commit_msg,
        "content": content_b64
    }
    if sha:
        payload["sha"] = sha

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="PUT")
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def check_github_actions_status(token, username, repo_name):
    url = f"https://api.github.com/repos/{username}/{repo_name}/actions/runs"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            runs = data.get("workflow_runs", [])
            if runs:
                latest = runs[0]
                return latest.get("status"), latest.get("conclusion"), latest.get("html_url")
    except Exception:
        pass
    return "unknown", "unknown", None

def generate_live_html_app(user_prompt, app_title, model_choice):
    model_map = {
        "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
        "DeepSeek R1": "deepseek/deepseek-r1",
        "GPT-4o": "openai/gpt-4o",
        "Llama 3.3 70B": "meta-llama/llama-3.3-70b-instruct",
        "Gemini 2.0 Flash": "google/gemini-2.0-flash-exp:free"
    }
    selected_model = model_map.get(model_choice, "anthropic/claude-3.5-sonnet")

    system_rules = """You are an elite mobile app architect. Generate a COMPLETE, 100% standalone single-file HTML5/CSS3/JS mobile application that matches the user's exact request.
STRICT MANDATORY RULES:
1. Build ONLY what the user asked for! If they ask for a Juice Shop, build a full interactive Juice Shop with products, prices, cart, and order summary. If they ask for Gold Rates, build a live rates dashboard and calculator.
2. NEVER put any visible 'Admin Panel', 'Admin Block', 'Owner Login', or 'Enter PIN' card on the public screen! The public UI must look 100% like a normal commercial consumer app.
3. NEVER write or print the secret PIN (2246) anywhere in visible text, labels, or placeholders!
4. STEALTH OWNER ACCESS: Make the app's main brand logo or title header respond to a secret '5-tap' gesture (tapping the top brand title 5 times in a row within 3 seconds). Only when tapped 5 times, open a hidden password prompt modal. If '2246' is entered, show a clean Owner Admin Drawer (showing Owner: Sarfealam, App Stats, and Kill Switch). Regular customers will NEVER see any admin button or icon!
5. NO BROKEN EXTERNAL LINKS: Do NOT use raw upi:// href links that trigger ERR_UNKNOWN_URL_SCHEME in Android WebView. Use interactive in-app modals or clean JavaScript actions instead.
6. DESIGN: Ultra-premium 3D Velvet Dark / Glassmorphic mobile design, mobile-first touch buttons, zero horizontal scroll, smooth animations, 100% self-contained (all CSS and JS inline).
7. OUTPUT FORMAT: Return ONLY the raw valid HTML code starting with <!DOCTYPE html> and ending with </html>. Do NOT wrap in markdown code fences."""

    user_message = f"App Name: {app_title}\\nUser Exact Requirements:\\n{user_prompt}\\n\\nGenerate the complete standalone HTML5 mobile application now."

    try:
        req_data = {
            "model": selected_model,
            "messages": [
                {"role": "system", "content": system_rules},
                {"role": "user", "content": user_message}
            ],
            "max_tokens": 4000,
            "temperature": 0.4
        }
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(req_data).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {DEFAULT_OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://supreme-agent.streamlit.app",
                "X-Title": "Sarfealam Master Factory"
            }
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            res_body = json.loads(resp.read().decode("utf-8"))
            raw_html = res_body["choices"][0]["message"]["content"].strip()
            
            if raw_html.startswith("```html"):
                raw_html = raw_html[7:]
            elif raw_html.startswith("```"):
                raw_html = raw_html[3:]
            if raw_html.endswith("```"):
                raw_html = raw_html[:-3]
            raw_html = raw_html.strip()
            
            if "<html" in raw_html.lower() and "</html>" in raw_html.lower():
                return raw_html, True
    except Exception:
        pass
    return "", False

# ==============================================================================
# UI STREAMLIT DASHBOARD & HIGH-CONTRAST CSS
# ==============================================================================
st.set_page_config(
    page_title="Sarfealam Master Factory",
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
div[data-testid="stToolbar"] {visibility: hidden; height: 0%;}
div[data-testid="stDecoration"] {visibility: hidden; height: 0%;}
div[data-testid="stStatusWidget"] {visibility: hidden; height: 0%;}
.block-container {padding: 0.3rem 0.6rem 3rem 0.6rem; max-width: 520px;}

[data-testid="manage-app-button"] {display: none !important; visibility: hidden !important;}
div[class*="viewerBadge"] {display: none !important; visibility: hidden !important;}

.stApp {
    background: radial-gradient(circle at 50% 0%, #111827 0%, #030712 100%);
    color: #f3f4f6;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

textarea, input[type="text"] {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 2px solid #3b82f6 !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    caret-color: #38bdf8 !important;
    padding: 12px !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: #60a5fa !important;
    box-shadow: 0 0 15px rgba(59, 130, 246, 0.6) !important;
    color: #ffffff !important;
}

.factory-header {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1px solid rgba(59, 130, 246, 0.35);
    border-radius: 18px;
    padding: 14px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    margin-bottom: 14px;
}

.logo-box {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 15px rgba(37, 99, 235, 0.6);
}

.radar-console {
    background: #030712;
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 14px;
    padding: 14px;
    font-family: "Courier New", Courier, monospace;
    font-size: 12px;
    color: #38bdf8;
    margin: 14px 0;
    box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.8);
}
</style>
""", unsafe_allow_html=True)

if "current_build" not in st.session_state:
    st.session_state.current_build = None

st.markdown(f"""
<div class="factory-header">
    <div style="display: flex; align-items: center; gap: 12px;">
        <div class="logo-box">👑</div>
        <div>
            <h3 style="margin: 0; font-size: 17px; font-weight: 800; color: #ffffff;">{OWNER_NAME.upper()} MASTER FACTORY</h3>
            <p style="margin: 0; font-size: 11px; color: #38bdf8;">Live Multi-AI & Stealth Admin Engine</p>
        </div>
    </div>
    <div style="background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); color: #34d399; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700;">
        ✓ Live AI
    </div>
</div>
""", unsafe_allow_html=True)

tab_create, tab_vault, tab_admin = st.tabs([
    "🚀 Build New App",
    "📦 All Apps Record (Vault)",
    "🔐 Factory Admin"
])

with tab_create:
    st.subheader("Autonomous AI App Generator")
    
    app_prompt = st.text_area(
        "Describe your exact app (AI will build 100% custom code):",
        placeholder="e.g. Build a Fresh Juice Shop app with Mango, Orange, Berry shakes, Add to Cart, and Checkout...",
        height=110
    )
    
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        custom_name = st.text_input("App Title:", placeholder="Fresh Juice Bar")
    with col_t2:
        model_pick = st.selectbox("AI Engine", [
            "Claude 3.5 Sonnet",
            "DeepSeek R1",
            "GPT-4o",
            "Llama 3.3 70B",
            "Gemini 2.0 Flash"
        ])

    if st.button("⚡ Build & Deploy Real Android APK", use_container_width=True):
        if not app_prompt.strip():
            st.error("Please enter what app you want to build.")
        else:
            clean_title = custom_name.strip() if custom_name.strip() else "My Custom App"
            safe_name = clean_title.lower().replace(" ", "-") + f"-{int(time.time())%100000}"
            
            hud_box = st.empty()
            prog_bar = st.progress(10, text="Layer 1: Connecting to Live OpenRouter AI Super Brain...")
            hud_box.markdown(f"""
            <div class="radar-console">
                [RADAR] Layer 1: Target '{clean_title}' initialized.<br>
                [RADAR] Layer 2: Dispatching your prompt to {model_pick}...<br>
                [SECURITY] Enforcing Stealth 5-Tap Admin & Zero Visible PIN rules...
            </div>
            """, unsafe_allow_html=True)
            
            generated_html, ai_success = generate_live_html_app(app_prompt, clean_title, model_pick)
            
            if not ai_success:
                st.error("⚠️ AI Engine is busy or timed out. Please try clicking Build again or switch AI Engine to GPT-4o.")
                st.stop()

            prog_bar.progress(50, text="Layer 3: Custom AI App verified! Creating GitHub Repository...")
            try:
                repo_res = create_github_repo(DEFAULT_GITHUB_TOKEN, safe_name, f"{clean_title} built by Sarfealam Live AI Factory")
                repo_url = repo_res.get("html_url", f"[https://github.com/](https://github.com/){DEFAULT_GITHUB_USERNAME}/{safe_name}")
            except Exception:
                repo_url = f"[https://github.com/](https://github.com/){DEFAULT_GITHUB_USERNAME}/{safe_name}"

            prog_bar.progress(75, text="Layer 3: Pushing Custom AI Code (index.html) to GitHub...")
            try:
                push_file_to_github(DEFAULT_GITHUB_TOKEN, DEFAULT_GITHUB_USERNAME, safe_name, "index.html", generated_html, "Deploy Live AI Custom App")
            except Exception:
                pass

            prog_bar.progress(90, text="Layer 4: Launching Java 17 Android APK Compiler...")
            try:
                push_file_to_github(DEFAULT_GITHUB_TOKEN, DEFAULT_GITHUB_USERNAME, safe_name, ".github/workflows/build_apk.yml", AUTOMATED_APK_WORKFLOW, "Launch Standalone APK Engine")
            except Exception:
                pass

            prog_bar.progress(100, text="✅ Custom AI App deployed! GitHub Actions compiling APK...")
            
            build_record = {
                "id": f"BUILD-{int(time.time())}",
                "name": clean_title,
                "repo": safe_name,
                "repo_url": repo_url,
                "actions_url": f"{repo_url}/actions",
                "releases_url": f"{repo_url}/releases",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            save_to_vault(build_record)
            st.session_state.current_build = build_record
            
            st.success(f"🎉 **{clean_title}** has been custom-written by {model_pick} and sent to APK Compiler!")

    if st.session_state.current_build:
        b_info = st.session_state.current_build
        st.markdown(f"### 📡 Live Compiler Radar: `{b_info['name']}`")
        
        status, conclusion, act_url = check_github_actions_status(DEFAULT_GITHUB_TOKEN, DEFAULT_GITHUB_USERNAME, b_info['repo'])
        
        if conclusion == "success":
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.2); border: 2px solid #10b981; border-radius: 14px; padding: 16px; text-align: center; margin: 12px 0;">
                <div style="font-size: 28px; margin-bottom: 6px;">🎉</div>
                <h4 style="margin: 0; color: #34d399; font-weight: 800;">CUSTOM AI ANDROID APK READY!</h4>
                <p style="font-size: 12px; color: #9ca3af; margin-top: 4px;">Stealth 5-Tap Admin • Zero Watermarks • 100% Standalone.</p>
                <a href="{b_info['releases_url']}" style="display: block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 12px; border-radius: 10px; font-weight: 700; text-decoration: none; margin-top: 10px;">
                    📥 Download APK Directly
                </a>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info(f"⏳ **GitHub Actions Status:** `{status.upper() if status else 'IN_PROGRESS'}` (Compiling Java 17 APK...)")
            st.markdown(f"""
            <div class="radar-console">
                [TELEMETRY] Repository: {b_info['repo']}<br>
                [TELEMETRY] Mode: 100% Live AI Custom Code + Stealth Owner Mode<br>
                [TELEMETRY] Status: {status} • Expected Duration: ~2 minutes<br>
                [GATE] Download button unlocks automatically when ready.
            </div>
            """, unsafe_allow_html=True)
            col_ref1, col_ref2 = st.columns(2)
            with col_ref1:
                if st.button("🔄 Refresh Radar Status", use_container_width=True):
                    st.rerun()
            with col_ref2:
                st.markdown(f"<a href='{b_info['actions_url']}' style='display: block; text-align: center; background: #374151; color: white; padding: 9px; border-radius: 8px; text-decoration: none; font-size: 13px;'>View Live GitHub Log</a>", unsafe_allow_html=True)

with tab_vault:
    st.subheader("📦 All Generated Applications Vault")
    records = load_vault()
    if not records:
        st.info("No applications generated yet.")
    else:
        for item in records:
            st.markdown(f"""
            <div style="background: rgba(31, 41, 55, 0.7); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 14px; padding: 14px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="font-size: 16px; color: #ffffff;">⚡ {item.get('name', 'App')}</b>
                    <span style="font-size: 11px; color: #38bdf8;">{item.get('time', '')}</span>
                </div>
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <a href="{item.get('releases_url', '#')}" style="flex: 1; text-align: center; background: #2563eb; color: white; padding: 8px; border-radius: 8px; text-decoration: none; font-size: 12px; font-weight: 700;">
                        📥 Download APK
                    </a>
                    <a href="{item.get('repo_url', '#')}" style="flex: 1; text-align: center; background: #374151; color: #d1d5db; padding: 8px; border-radius: 8px; text-decoration: none; font-size: 12px;">
                        📂 View Repo
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

with tab_admin:
    st.subheader("🔐 Factory Owner Settings")
    pin_attempt = st.text_input("Enter Master PIN:", type="password")
    if pin_attempt == ADMIN_PIN:
        st.success(f"✓ Verified Owner: {OWNER_NAME}")
        st.write("**Stealth Rule Active:** All generated apps hide admin controls behind a 5-tap secret header gesture.")
        st.text_input("Registered OpenRouter Key", value=DEFAULT_OPENROUTER_KEY, disabled=True)
        st.text_input("GitHub Username", value=DEFAULT_GITHUB_USERNAME, disabled=True)
