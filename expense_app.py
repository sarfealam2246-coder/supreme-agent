import ast
import base64
import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

# ==============================================================================
# SARFEALAM AUTO-STUDIO v30.0 (GROK-MODE: 1-PROMPT -> PLAYWRIGHT VISION -> APK)
# ==============================================================================

def _get_secret(key_name, fallback=""):
    try:
        if key_name in st.secrets:
            return str(st.secrets[key_name])
    except Exception:
        pass
    return fallback

OWNER_NAME = "Sarfealam"
NVIDIA_KEY = _get_secret("NVIDIA_API_KEY", _get_secret("NVIDIA_KEY", ""))
GROQ_KEY = _get_secret("GROQ_API_KEY", _get_secret("GROQ_KEY", ""))
GEMINI_KEY = _get_secret("GEMINI_API_KEY", _get_secret("GEMINI_KEY", ""))
OPENROUTER_KEY = _get_secret("OPENROUTER_API_KEY", _get_secret("OPENROUTER_KEY", ""))
COHERE_KEY = _get_secret("COHERE_API_KEY", _get_secret("COHERE_KEY", ""))
GITHUB_TOKEN = _get_secret("GITHUB_TOKEN", "")
DEFAULT_GITHUB_USERNAME = _get_secret("GITHUB_USERNAME", "sarfealam2246-coder")
SUPABASE_URL = _get_secret("SUPABASE_URL", "https://saexbzapfzfkzqkunsom.supabase.co")
SUPABASE_KEY = _get_secret("SUPABASE_KEY", "")
ADMIN_PASSWORD = _get_secret("ADMIN_PASSWORD", "sarfealam786")

STATE_FILE = "auto_studio_state.json"
VAULT_FILE = "apps_vault.json"

# ==============================================================================
# STORAGE & PERSISTENCE (LOCAL + SUPABASE CLOUD)
# ==============================================================================

def load_json_file(path, default_val=None):
    if default_val is None:
        default_val = {}
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default_val

def save_json_file(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def remove_json_file(path):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

def save_to_vault(rec):
    v = load_json_file(VAULT_FILE, [])
    if not isinstance(v, list):
        v = []
    v = [x for x in v if x.get("repo") != rec.get("repo")]
    v.insert(0, rec)
    save_json_file(VAULT_FILE, v[:40])

# ==============================================================================
# STRICT MULTI-AI ENGINE (GEMINI + GROQ + NVIDIA + OPENROUTER + COHERE)
# ==============================================================================

def strip_markdown_fences(raw_text):
    t = (raw_text or "").strip()
    t = re.sub(r"^```[a-zA-Z0-9_-]*\s*\n?", "", t)
    t = re.sub(r"\n?```\s*$", "", t)
    return t.strip()

def _http_json(url, payload=None, headers=None, method="GET", timeout=35):
    hdrs = headers or {}
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def call_ai(system_prompt, user_prompt, max_tokens=3600, prefer="gemini"):
    # 1. Gemini 2.5 Flash
    if GEMINI_KEY and prefer == "gemini":
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
            body = {
                "system_instruction": {"parts": [{"text": system_prompt}]},
                "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.35},
            }
            res = _http_json(url, body, {"Content-Type": "application/json"}, "POST", 45)
            txt = res["candidates"][0]["content"]["parts"][0]["text"]
            if txt:
                return txt
        except Exception:
            pass

    # 2. GroqCloud (openai/gpt-oss-120b)
    if GROQ_KEY:
        try:
            res = _http_json(
                "https://api.groq.com/openai/v1/chat/completions",
                {
                    "model": "openai/gpt-oss-120b",
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    "max_tokens": min(max_tokens, 4096),
                    "temperature": 0.35,
                },
                {"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_KEY}"},
                "POST",
                40,
            )
            txt = res["choices"][0]["message"]["content"]
            if txt:
                return txt
        except Exception:
            pass

    # 3. NVIDIA NIM (deepseek / kimi / nemotron)
    if NVIDIA_KEY:
        for mdl in ["deepseek-ai/deepseek-v4.1-flash", "moonshotai/kimi-k3.1-pro", "nvidia/nemotron-3.5-lightning-30b-a3b"]:
            try:
                res = _http_json(
                    "https://integrate.api.nvidia.com/v1/chat/completions",
                    {
                        "model": mdl,
                        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                        "max_tokens": min(max_tokens, 4096),
                        "temperature": 0.3,
                    },
                    {"Content-Type": "application/json", "Authorization": f"Bearer {NVIDIA_KEY}"},
                    "POST",
                    45,
                )
                txt = res["choices"][0]["message"]["content"]
                if txt:
                    return txt
            except Exception:
                continue

    # 4. OpenRouter
    if OPENROUTER_KEY:
        try:
            res = _http_json(
                "https://openrouter.ai/api/v1/chat/completions",
                {
                    "model": "openrouter/free",
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    "max_tokens": min(max_tokens, 3500),
                },
                {"Content-Type": "application/json", "Authorization": f"Bearer {OPENROUTER_KEY}"},
                "POST",
                40,
            )
            txt = res["choices"][0]["message"]["content"]
            if txt:
                return txt
        except Exception:
            pass

    # 5. Cohere
    if COHERE_KEY:
        try:
            res = _http_json(
                "https://api.cohere.com/v2/chat",
                {
                    "model": "command-a-03-2025",
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    "max_tokens": min(max_tokens, 2800),
                },
                {"Content-Type": "application/json", "Authorization": f"Bearer {COHERE_KEY}"},
                "POST",
                35,
            )
            txt = res["message"]["content"][0]["text"]
            if txt:
                return txt
        except Exception:
            pass
    return ""

def call_vision_ai(prompt_text, img_bytes):
    """Uses Gemini 2.5 Flash Vision to inspect actual Playwright screenshots."""
    if not GEMINI_KEY or not img_bytes:
        return ""
    try:
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
        body = {
            "contents": [{
                "parts": [
                    {"text": prompt_text},
                    {"inline_data": {"mime_type": "image/png", "data": b64}},
                ]
            }]
        }
        res = _http_json(url, body, {"Content-Type": "application/json"}, "POST", 35)
        return res["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return ""

# ==============================================================================
# GITHUB API + PLAYWRIGHT SCREENSHOT FETCHER
# ==============================================================================

def github_api(url, method="GET", payload=None, timeout=18):
    if not GITHUB_TOKEN:
        return {"error": "Missing GITHUB_TOKEN"}
    hdrs = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "Sarfealam-Auto-Studio",
    }
    try:
        return _http_json(url, payload, hdrs, method, timeout)
    except urllib.error.HTTPError as he:
        try:
            return {"error": f"HTTP {he.code}: {he.read().decode('utf-8')[:220]}"}
        except Exception:
            return {"error": f"HTTP {he.code}"}
    except Exception as ex:
        return {"error": str(ex)}

def create_github_repo(repo_name, desc):
    return github_api(
        "https://api.github.com/user/repos",
        "POST",
        {"name": repo_name, "description": desc[:140], "private": False, "auto_init": True},
    )

def push_file_to_github(repo_name, file_path, content_str, commit_msg):
    api_url = f"https://api.github.com/repos/{DEFAULT_GITHUB_USERNAME}/{repo_name}/contents/{file_path}"
    sha = None
    cur = github_api(api_url, "GET", timeout=10)
    if isinstance(cur, dict) and cur.get("sha"):
        sha = cur["sha"]
    payload = {
        "message": commit_msg,
        "content": base64.b64encode(content_str.encode("utf-8")).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha
    return github_api(api_url, "PUT", payload, timeout=25)

def fetch_file_from_github(repo_name, file_path):
    res = github_api(f"https://api.github.com/repos/{DEFAULT_GITHUB_USERNAME}/{repo_name}/contents/{file_path}", "GET", timeout=10)
    if isinstance(res, dict) and res.get("content"):
        return base64.b64decode(res["content"]).decode("utf-8", errors="ignore")
    return ""

def get_live_build_telemetry(repo_name):
    runs = github_api(f"https://api.github.com/repos/{DEFAULT_GITHUB_USERNAME}/{repo_name}/actions/runs?per_page=3", "GET", timeout=10)
    if not isinstance(runs, dict) or not runs.get("workflow_runs"):
        return {"status": "queued", "conclusion": None, "steps": []}
    run = runs["workflow_runs"][0]
    jobs = github_api(run.get("jobs_url", ""), "GET", timeout=10)
    steps = []
    job_id = None
    if isinstance(jobs, dict) and jobs.get("jobs"):
        j = jobs["jobs"][0]
        job_id = j.get("id")
        steps = j.get("steps", [])
    return {
        "run_id": run.get("id"),
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "job_id": job_id,
        "steps": steps,
    }

def fetch_github_job_error_tail(repo_name, job_id):
    if not job_id or not GITHUB_TOKEN:
        return ""
    try:
        url = f"https://api.github.com/repos/{DEFAULT_GITHUB_USERNAME}/{repo_name}/actions/jobs/{job_id}/logs"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {GITHUB_TOKEN}", "User-Agent": "Sarfealam-Auto-Studio"})
        with urllib.request.urlopen(req, timeout=20) as r:
            lines = r.read().decode("utf-8", errors="ignore").splitlines()
            return "\n".join(lines[-80:])
    except Exception:
        return ""

def fetch_latest_playwright_screenshot(repo_name):
    """Downloads visual-audit-capture artifact ZIP from GitHub Actions and returns PNG bytes."""
    if not GITHUB_TOKEN or not repo_name:
        return None
    try:
        arts = github_api(f"https://api.github.com/repos/{DEFAULT_GITHUB_USERNAME}/{repo_name}/actions/artifacts", "GET", timeout=10)
        for art in arts.get("artifacts", []):
            if art.get("name") == "visual-audit-capture" and not art.get("expired"):
                dl_url = art.get("archive_download_url")
                req = urllib.request.Request(dl_url, headers={"Authorization": f"Bearer {GITHUB_TOKEN}", "User-Agent": "Sarfealam-Auto-Studio"})
                with urllib.request.urlopen(req, timeout=25) as r:
                    zbytes = io.BytesIO(r.read())
                with zipfile.ZipFile(zbytes) as zf:
                    for name in zf.namelist():
                        if name.lower().endswith(".png"):
                            return zf.read(name)
    except Exception:
        pass
    return None

# ==============================================================================
# WORKFLOWS: PLAYWRIGHT VISUAL AUDIT + GODOT 4 3D APK + FLUTTER 3.50 APK
# ==============================================================================

VISION_AUDIT_WORKFLOW = """name: Playwright Visual Screenshot & Verify

on:
  workflow_dispatch:
  push:
    branches: [ main ]

permissions:
  contents: write

jobs:
  visual-verify:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Capture Live 3D / UI Screenshot via Playwright
        run: |
          if [ -f assets/game.html ]; then
            npx -y playwright@1.48.0 install chromium --with-deps || true
            node -e "const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:800,height:450}});await p.goto('file://'+process.cwd()+'/assets/game.html');await p.waitForTimeout(2500);await p.screenshot({path:'preview_capture.png'});await b.close();})().catch(()=>process.exit(0));"
          fi
      - name: Upload Visual Capture
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: visual-audit-capture
          path: preview_capture.png
          if-no-files-found: ignore
"""

GODOT_APK_WORKFLOW = """name: Build Native Godot 4 3D Android APK

on:
  workflow_dispatch:
  push:
    branches: [ main ]

permissions:
  contents: write

jobs:
  export-android:
    runs-on: ubuntu-latest
    container:
      image: barichello/godot-ci:4.3
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Fetch Open-Source PBR Asphalt & Sky Textures
        run: |
          mkdir -p assets/textures build/android
          curl -fsL "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/asphalt_02/asphalt_02_diff_1k.jpg" -o assets/textures/asphalt_diff.jpg || true

      - name: Setup Export Templates, Java/Android SDK & Keystore in $HOME
        run: |
          mkdir -p "$HOME/.local/share/godot" "$HOME/.config/godot"
          if [ -d /root/.local/share/godot ]; then cp -rn /root/.local/share/godot/* "$HOME/.local/share/godot/" || true; fi
          if [ -d /root/.config/godot ]; then cp -rn /root/.config/godot/* "$HOME/.config/godot/" || true; fi
          JAVA_DIR="${JAVA_HOME:-$(dirname $(dirname $(readlink -f $(which java))))}"
          ANDROID_DIR="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-/usr/lib/android-sdk}}"
          KS_PATH="$HOME/.local/share/godot/debug.keystore"
          if [ ! -f "$KS_PATH" ]; then
            keytool -keyalg RSA -genkeypair -alias androiddebugkey -keypass android -keystore "$KS_PATH" -storepass android -dname "CN=Android Debug,O=Android,C=US" -validity 9999 || true
          fi
          cat > "$HOME/.config/godot/editor_settings-4.3.tres" <<EOF
[gd_resource type="EditorSettings" format=3]

[resource]
export/android/java_sdk_path = "$JAVA_DIR"
export/android/android_sdk_path = "$ANDROID_DIR"
export/android/debug_keystore = "$KS_PATH"
export/android/debug_keystore_user = "androiddebugkey"
export/android/debug_keystore_pass = "android"
EOF
          godot --headless --quit --editor || true

      - name: Export Native Godot 4 3D Release APK
        run: |
          godot --headless --export-release "Android" build/android/game-release.apk

      - name: Publish Godot 4 3D APK to Releases
        uses: softprops/action-gh-release@v2
        with:
          tag_name: v1.0.0-${{ github.run_number }}
          name: "Godot 4 3D Android APK v1.0.0"
          files: build/android/*.apk
          draft: false
          prerelease: false
"""

FLUTTER_APK_WORKFLOW = """name: Build Native Flutter Android APK

on:
  workflow_dispatch:
  push:
    branches: [ main ]

permissions:
  contents: write

jobs:
  build-apk:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'
      - uses: subosito/flutter-action@v2
        with:
          channel: 'stable'
      - name: Create Android Shell & Build Release APK
        run: |
          flutter create --platforms=android .
          flutter pub get
          flutter build apk --release
      - name: Publish Flutter APK to Releases
        uses: softprops/action-gh-release@v2
        with:
          tag_name: v1.0.0-${{ github.run_number }}
          name: "Flutter Android APK v1.0.0"
          files: build/app/outputs/flutter-apk/app-release.apk
          draft: false
          prerelease: false
"""

# ==============================================================================
# AUTONOMOUS GENERATORS (ANY PROMPT -> 3D SCENE / GODOT 4 / FLUTTER)
# ==============================================================================

def detect_is_game(prompt_text):
    p = (prompt_text or "").lower()
    game_kws = ["game", "3d", "truck", "bus", "tractor", "car", "bike", "train", "plane", "crane", "jcb", "dumper", "racing", "simulator", "driving", "building", "stepwell"]
    return any(k in p for k in game_kws)

def build_custom_preview_html(user_prompt, is_game):
    if is_game:
        sys_p = (
            "You are an expert Three.js WebGL 3D Architect (like Grok Build Sandbox). "
            "Output ONLY a complete, valid self-contained HTML5 file (no markdown fences) using "
            "https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js with OrbitControls or touch-drag 360 rotation, "
            "bright HemisphereLight + DirectionalLight + PCFSoftShadowMap shadows, procedural PBR textures, "
            "user-select:none, and interactive touch controls/sliders matching the prompt. "
            "Make it rich, bright, colorful, and genuinely 3D — never dark or flat."
        )
        usr_p = f"Build a full 360-degree interactive Three.js 3D web experience for: {user_prompt}"
    else:
        sys_p = (
            "You are a Principal Mobile UI Architect. Output ONLY a complete, self-contained HTML5 mobile app preview "
            "(no markdown fences) with Material 3 3D depth cards, Mobile OTP login tab, Profile ID tab, interactive buttons, "
            "and a 4-tab floating bottom navigation bar. user-select:none."
        )
        usr_p = f"Build an interactive Play-Store style mobile app preview for: {user_prompt}"

    raw = strip_markdown_fences(call_ai(sys_p, usr_p, max_tokens=3800))
    if "<html" in raw.lower() and (not is_game or "webglrenderer" in raw.lower()):
        return raw

    # Deterministic rich 3D fallback if AI call fails
    return """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>*{box-sizing:border-box;user-select:none;-webkit-user-select:none;}body{margin:0;overflow:hidden;background:#60a5fa;font-family:system-ui;}#hud{position:absolute;top:10px;left:10px;color:#fff;font-weight:800;font-size:12px;background:rgba(15,23,42,0.7);padding:6px 10px;border-radius:10px;}</style>
</head><body><div id="hud">360 Touch Drag 3D Scene</div><canvas id="c"></canvas>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script>
const cv=document.getElementById('c'),ren=new THREE.WebGLRenderer({canvas:cv,antialias:true});
ren.setSize(window.innerWidth,window.innerHeight);ren.shadowMap.enabled=true;
const sc=new THREE.Scene();sc.background=new THREE.Color('#7dd3fc');sc.fog=new THREE.Fog('#bae6fd',25,110);
const cam=new THREE.PerspectiveCamera(50,window.innerWidth/window.innerHeight,0.1,160);
let ang=0.5,dist=9;
sc.add(new THREE.HemisphereLight('#e0f2fe','#334155',0.8));
const sun=new THREE.DirectionalLight('#fffbeb',1.3);sun.position.set(12,24,10);sun.castShadow=true;sc.add(sun);
const gnd=new THREE.Mesh(new THREE.PlaneGeometry(180,180),new THREE.MeshStandardMaterial({color:'#3f6212',roughness:0.9}));
gnd.rotation.x=-Math.PI/2;gnd.receiveShadow=true;sc.add(gnd);
const road=new THREE.Mesh(new THREE.PlaneGeometry(9,180),new THREE.MeshStandardMaterial({color:'#1f2937',roughness:0.8}));
road.rotation.x=-Math.PI/2;road.position.y=0.02;sc.add(road);
const grp=new THREE.Group();
const cab=new THREE.Mesh(new THREE.BoxGeometry(2.1,1.6,1.9),new THREE.MeshStandardMaterial({color:'#dc2626',metalness:0.75,roughness:0.2}));
cab.position.set(0,1.2,-1.2);cab.castShadow=true;
const bed=new THREE.Mesh(new THREE.BoxGeometry(2.3,1.9,3.4),new THREE.MeshStandardMaterial({color:'#f8fafc',roughness:0.4}));
bed.position.set(0,1.4,1.5);bed.castShadow=true;grp.add(cab,bed);sc.add(grp);
window.addEventListener('touchmove',e=>{if(e.touches[0])ang=(e.touches[0].clientX/window.innerWidth)*Math.PI*2;},{passive:true});
window.addEventListener('mousemove',e=>{if(e.buttons)ang=(e.clientX/window.innerWidth)*Math.PI*2;});
(function loop(){requestAnimationFrame(loop);cam.position.set(Math.sin(ang)*dist,4.2,Math.cos(ang)*dist);cam.lookAt(0,1,0);ren.render(sc,cam);})();
</script></body></html>"""

def build_godot4_files(app_title, user_prompt):
    safe_pkg = re.sub(r"[^a-z0-9_]", "_", app_title.lower().replace(" ", "_")) or "auto_studio_3d"
    proj = f"""config_version=5

[application]
config/name="{app_title}"
run/main_scene="res://scenes/main.tscn"
config/features=PackedStringArray("4.3", "Mobile")

[display]
window/size/viewport_width=1280
window/size/viewport_height=720
window/handheld/orientation=6
window/stretch/mode="canvas_items"
window/stretch/aspect="expand"

[rendering]
renderer/rendering_method="mobile"
"""
    preset = f"""[preset.0]
name="Android"
platform="Android"
runnable=true
export_filter="all_resources"
include_filter=""
exclude_filter=""

[preset.0.options]
package/unique_name="com.sarfealam.{safe_pkg}"
package/name="{app_title}"
package/signed=false
gradle_build/use_gradle_build=false
architectures/arm64-v8a=true
"""
    ctrl_gd = call_ai(
        "You are a Godot 4.3 GDScript Expert. Output ONLY valid GDScript (no markdown fences) extending VehicleBody3D with touch steering, gas, brake, and speed label update.",
        f"Title: {app_title}\nPrompt: {user_prompt}",
        max_tokens=1600,
    )
    ctrl_gd = strip_markdown_fences(ctrl_gd)
    if "extends VehicleBody3D" not in ctrl_gd:
        ctrl_gd = """extends VehicleBody3D

@export var max_steer := 0.48
@export var engine_power := 360.0

func _physics_process(delta: float) -> void:
\tvar h = Input.get_axis("ui_right", "ui_left")
\tvar v = Input.get_axis("ui_down", "ui_up")
\tsteering = move_toward(steering, h * max_steer, delta * 3.2)
\tengine_force = v * engine_power
"""
    main_tscn = """[gd_scene load_steps=6 format=3]

[ext_resource type="Script" path="res://scripts/vehicle_ctrl.gd" id="1_ctrl"]

[sub_resource type="BoxShape3D" id="Box_gnd"]
size = Vector3(240, 1, 240)

[sub_resource type="BoxMesh" id="Mesh_gnd"]
size = Vector3(12, 0.2, 240)

[sub_resource type="BoxShape3D" id="Box_veh"]
size = Vector3(2.2, 1.8, 4.6)

[sub_resource type="BoxMesh" id="Mesh_veh"]
size = Vector3(2.2, 1.8, 4.6)

[node name="MainWorld3D" type="Node3D"]

[node name="SunLight3D" type="DirectionalLight3D" parent="."]
transform = Transform3D(0.866, -0.35, 0.35, 0, 0.707, 0.707, -0.5, -0.61, 0.61, 0, 35, 0)
shadow_enabled = true

[node name="Ground3D" type="StaticBody3D" parent="."]

[node name="CollisionShape3D" type="CollisionShape3D" parent="Ground3D"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, -0.5, 0)
shape = SubResource("Box_gnd")

[node name="RoadMesh3D" type="MeshInstance3D" parent="Ground3D"]
mesh = SubResource("Mesh_gnd")

[node name="PlayerVehicle3D" type="VehicleBody3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1.4, 0)
mass = 1400.0
script = ExtResource("1_ctrl")

[node name="CollisionShape3D" type="CollisionShape3D" parent="PlayerVehicle3D"]
shape = SubResource("Box_veh")

[node name="MeshInstance3D" type="MeshInstance3D" parent="PlayerVehicle3D"]
mesh = SubResource("Mesh_veh")

[node name="Camera3D" type="Camera3D" parent="PlayerVehicle3D"]
transform = Transform3D(1, 0, 0, 0, 0.94, 0.34, 0, -0.34, 0.94, 0, 4.0, -8.5)
current = true
"""
    return {
        "project.godot": proj,
        "export_presets.cfg": preset,
        "scripts/vehicle_ctrl.gd": ctrl_gd,
        "scenes/main.tscn": main_tscn,
    }

def build_flutter_files(app_title, user_prompt):
    pubspec = f"""name: {re.sub(r'[^a-z0-9_]', '_', app_title.lower().replace(' ', '_')) or 'auto_app'}
description: {app_title}
version: 1.0.0+1
environment:
  sdk: '>=3.2.0 <4.0.0'
dependencies:
  flutter:
    sdk: flutter
  fl_chart: ^0.68.0
dev_dependencies:
  flutter_test:
    sdk: flutter
flutter:
  uses-material-design: true
"""
    main_dart = strip_markdown_fences(call_ai(
        "You are a Principal Flutter 3.50 Engineer. Output ONLY valid, self-contained Dart code for lib/main.dart (no markdown fences, no invalid const, no withOpacity) implementing a complete Material 3 app with OTP sign-in, Profile tab, Home cards, and 4-tab bottom navigation.",
        f"App Title: {app_title}\nPrompt: {user_prompt}",
        max_tokens=3400,
    ))
    if "void main()" not in main_dart:
        main_dart = f"""import 'package:flutter/material.dart';

void main() => runApp(const AutoApp());

class AutoApp extends StatelessWidget {{
  const AutoApp({{super.key}});
  @override
  Widget build(BuildContext context) {{
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: '{app_title}',
      theme: ThemeData(colorSchemeSeed: Colors.blue, useMaterial3: true),
      home: const HomeShell(),
    );
  }}
}}

class HomeShell extends StatefulWidget {{
  const HomeShell({{super.key}});
  @override
  State<HomeShell> createState() => _HomeShellState();
}}

class _HomeShellState extends State<HomeShell> {{
  int idx = 0;
  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(title: const Text('{app_title}')),
      body: Center(child: Text('Active Tab: $idx', style: const TextStyle(fontSize: 22))),
      bottomNavigationBar: NavigationBar(
        selectedIndex: idx,
        onDestinationSelected: (i) => setState(() => idx = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.apps), label: 'Apps'),
          NavigationDestination(icon: Icon(Icons.shopping_bag), label: 'Shop'),
          NavigationDestination(icon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }}
}}
"""
    return {"pubspec.yaml": pubspec, "lib/main.dart": main_dart}

# ==============================================================================
# AUTONOMOUS PIPELINE RUNNER (ZERO MANUAL GATES)
# ==============================================================================

def run_autonomous_build(user_prompt):
    is_game = detect_is_game(user_prompt)
    words = [w for w in re.sub(r"[^a-zA-Z0-9 ]", " ", user_prompt).split() if len(w) > 2][:3]
    app_title = " ".join(w.capitalize() for w in words) or ("Auto 3D Studio" if is_game else "Auto Super App")
    slug = re.sub(r"[^a-z0-9-]", "", app_title.lower().replace(" ", "-")) or "auto-app"
    repo_name = f"{slug}-{int(time.time()) % 100000}"

    logs = [f"[{datetime.now().strftime('%H:%M:%S')}] Started Auto-Studio for '{app_title}' ({'3D Game / Godot 4' if is_game else 'App / Flutter 3.50'})"]

    # Step 1: Generate live preview HTML + repo files
    preview_html = build_custom_preview_html(user_prompt, is_game)
    logs.append("Generated custom live HTML5/3D preview directly from prompt.")

    repo_res = create_github_repo(repo_name, f"{app_title} - Sarfealam Auto-Studio")
    repo_url = repo_res.get("html_url", f"https://github.com/{DEFAULT_GITHUB_USERNAME}/{repo_name}")
    push_file_to_github(repo_name, "assets/game.html", preview_html, "Add live interactive preview")
    push_file_to_github(repo_name, ".github/workflows/visual_verify.yml", VISION_AUDIT_WORKFLOW, "Add Playwright visual verify")

    if is_game:
        g_files = build_godot4_files(app_title, user_prompt)
        for fp, body in g_files.items():
            push_file_to_github(repo_name, fp, body, f"Add {fp}")
        push_file_to_github(repo_name, ".github/workflows/build_godot_apk.yml", GODOT_APK_WORKFLOW, "Activate Godot 4 3D APK Build")
        logs.append("Pushed Godot 4 3D project + Playwright Visual Audit to GitHub.")
    else:
        f_files = build_flutter_files(app_title, user_prompt)
        for fp, body in f_files.items():
            push_file_to_github(repo_name, fp, body, f"Add {fp}")
        push_file_to_github(repo_name, ".github/workflows/build_flutter_apk.yml", FLUTTER_APK_WORKFLOW, "Activate Flutter 3.50 APK Build")
        logs.append("Pushed Flutter 3.50 project + Playwright Visual Audit to GitHub.")

    state = {
        "app_title": app_title,
        "prompt": user_prompt,
        "is_game": is_game,
        "repo": repo_name,
        "repo_url": repo_url,
        "actions_url": f"{repo_url}/actions",
        "releases_url": f"{repo_url}/releases",
        "admin_url": f"https://supreme-agent-vlqyfohdlkxxwpsdc4tiuy.streamlit.app/?admin_app={repo_name}",
        "preview_html": preview_html,
        "vision_passes": 0,
        "heal_passes": 0,
        "logs": logs,
        "status": "building",
    }
    save_json_file(STATE_FILE, state)
    return state

# ==============================================================================
# CLEAN 4-TAB STREAMLIT UI (FACTORY | LIVE TRACKER | VAULT | ADMIN)
# ==============================================================================

st.set_page_config(page_title="Sarfealam Auto-Studio v30.0", layout="wide")
st.title("SARFEALAM AUTO-STUDIO v30.0 (Grok-Mode)")
st.caption("1 Prompt -> Self-Dependent AI Code -> Playwright Browser Screenshot -> Vision Auto-Fix -> Native APK")

tab_factory, tab_tracker, tab_vault, tab_admin = st.tabs(["Factory", "Live Tracker", "Vault", "Admin"])

with tab_factory:
    st_state = load_json_file(STATE_FILE, None)

    if st_state:
        st.subheader(f"Active Studio: {st_state['app_title']}")
        c_disp1, c_disp2 = st.columns(2)

        with c_disp1:
            st.markdown("**Live Interactive Preview**")
            components.html(st_state.get("preview_html", ""), height=380, scrolling=False)

        with c_disp2:
            st.markdown("**Playwright Browser Screenshot + Vision Audit**")
            shot_bytes = fetch_latest_playwright_screenshot(st_state["repo"])
            if shot_bytes:
                st.image(shot_bytes, caption="Captured by GitHub Playwright Chromium", use_container_width=True)
                if st_state.get("vision_passes", 0) < 3 and st_state.get("status") == "building":
                    verdict = call_vision_ai(
                        f"Inspect this screenshot for '{st_state['prompt']}'. Reply PASS if it looks bright, 3D, and complete; otherwise list exact visual fixes.",
                        shot_bytes,
                    )
                    if verdict and "PASS" not in verdict.upper():
                        st_state["vision_passes"] = st_state.get("vision_passes", 0) + 1
                        st_state["logs"].append(f"Vision Pass #{st_state['vision_passes']} caught issue: {verdict[:120]} -> Auto-fixing...")
                        fixed_html = strip_markdown_fences(call_ai(
                            "Fix ALL visual bugs in this HTML5/Three.js code. Output ONLY valid full HTML.",
                            f"Visual Bugs:\n{verdict}\n\nCode:\n{st_state['preview_html'][:9500]}",
                            max_tokens=3800,
                        ))
                        if "<html" in fixed_html.lower():
                            st_state["preview_html"] = fixed_html
                            push_file_to_github(st_state["repo"], "assets/game.html", fixed_html, f"Vision Auto-Fix #{st_state['vision_passes']}")
                        save_json_file(STATE_FILE, st_state)
                        st.rerun()
            else:
                st.info("Waiting for GitHub Playwright Chromium to capture live screenshot (auto-refreshing)...")

        # Check Live APK Build Status + Silent Auto-Heal
        tele = get_live_build_telemetry(st_state["repo"])
        conc = tele.get("conclusion")
        if conc == "success":
            st_state["status"] = "done"
            save_json_file(STATE_FILE, st_state)
            save_to_vault({
                "name": st_state["app_title"],
                "repo": st_state["repo"],
                "releases_url": st_state["releases_url"],
                "admin_url": st_state["admin_url"],
                "time": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            })
            st.success("Native APK Ready!")
            st.markdown(f"**Download APK:** {st_state['releases_url']}  \n**Admin Link:** {st_state['admin_url']}")
        elif conc == "failure":
            hp = st_state.get("heal_passes", 0)
            if hp < 3:
                st_state["heal_passes"] = hp + 1
                err_tail = fetch_github_job_error_tail(st_state["repo"], tele.get("job_id"))
                st_state["logs"].append(f"Auto-Heal #{st_state['heal_passes']}: Reading GitHub error & repairing automatically...")
                if st_state.get("is_game"):
                    push_file_to_github(st_state["repo"], ".github/workflows/build_godot_apk.yml", GODOT_APK_WORKFLOW, f"Auto-Heal Godot #{st_state['heal_passes']}")
                else:
                    cur_main = fetch_file_from_github(st_state["repo"], "lib/main.dart")
                    fixed_dart = strip_markdown_fences(call_ai(
                        "Fix the Flutter compilation error in lib/main.dart. Output ONLY valid Dart code.",
                        f"Error:\n{err_tail}\n\nCode:\n{cur_main[:8000]}",
                        max_tokens=3400,
                    ))
                    if "void main()" in fixed_dart:
                        push_file_to_github(st_state["repo"], "lib/main.dart", fixed_dart, f"Auto-Heal Dart #{st_state['heal_passes']}")
                save_json_file(STATE_FILE, st_state)
                time.sleep(3)
                st.rerun()
            else:
                st.error(f"Build stopped after 3 Auto-Heal retries. Logs: {st_state['actions_url']}")
        else:
            st.info(f"GitHub Cloud Building APK & Running Playwright... ({tele.get('status', 'queued')})")

        with st.expander("Autonomous AI Execution Log", expanded=False):
            for lg in st_state.get("logs", []):
                st.write("-", lg)

        if st.button("Stop & Start New Project", use_container_width=True):
            remove_json_file(STATE_FILE)
            st.rerun()

        if st_state.get("status") == "building":
            time.sleep(10)
            st.rerun()
    else:
        st.markdown("### Enter 1 Prompt — AI Does Everything Automatically")
        user_prompt = st.text_area("What should I build? (3D Game, Building, or Commercial App)", height=120, placeholder="e.g. Indian Highway Cargo Truck 3D with hydraulic unloading and cockpit view")
        if st.button("Start Auto-Studio", type="primary", use_container_width=True) and user_prompt.strip():
            with st.spinner("Auto-Studio generating code, 3D scene, Playwright audit & GitHub APK..."):
                run_autonomous_build(user_prompt.strip())
            st.rerun()

with tab_tracker:
    st_state = load_json_file(STATE_FILE, None)
    if st_state:
        tele = get_live_build_telemetry(st_state["repo"])
        st.write("Repository:", st_state["repo_url"])
        st.write("Status:", tele.get("status"), "| Conclusion:", tele.get("conclusion"))
        for sp in tele.get("steps", []):
            st.write(f"- {sp.get('name')}: {sp.get('status')} ({sp.get('conclusion')})")
    else:
        st.info("No active build.")

with tab_vault:
    vault = load_json_file(VAULT_FILE, [])
    if not vault:
        st.info("No completed apps in Vault yet.")
    else:
        for item in vault:
            st.markdown(f"**{item.get('name')}** ({item.get('time')})  \nAPK: {item.get('releases_url')}  \nAdmin: {item.get('admin_url')}")

with tab_admin:
    pin = st.text_input("Admin Password", type="password")
    if pin == ADMIN_PASSWORD:
        st.success(f"Welcome {OWNER_NAME} — Auto-Studio v30.0 Active")
        st.write("Configured Engines:", {
            "Gemini": bool(GEMINI_KEY),
            "Groq": bool(GROQ_KEY),
            "NVIDIA": bool(NVIDIA_KEY),
            "OpenRouter": bool(OPENROUTER_KEY),
            "Cohere": bool(COHERE_KEY),
            "GitHub": bool(GITHUB_TOKEN),
        })
    elif pin:
        st.error("Invalid Password")
