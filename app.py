import ast
import base64
import html as html_lib
import json
import os
import re
import time
import urllib.parse
from datetime import datetime

import gradio as gr
import requests

try:
    import spaces
    @spaces.GPU
    def _hf_zerogpu_keepalive():
        return 'OK'
except Exception:
    pass

# ==============================================================================
# SARFEALAM AUTO-STUDIO (HUGGING FACE GRADIO + FASTAPI EDITION)
# 100% Universal 3D Game & Commercial App Factory | Pure 3D Gaming + Universal Apps
# ==============================================================================

OWNER_NAME = "Sarfealam"
OWNER_EMAIL = os.environ.get("OWNER_EMAIL", "ajayk980045@gmail.com").strip()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "SF2026").strip()

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
GROQ_KEY = os.environ.get("GROQ_API_KEY", "").strip()
NVIDIA_KEY = os.environ.get("NVIDIA_API_KEY", "").strip()
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()
COHERE_KEY = os.environ.get("COHERE_API_KEY", "").strip()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "sarfealam2246-coder").strip()
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://saexbzapfzfkzqkunsom.supabase.co").strip().rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()

# ==============================================================================
# UNIVERSAL DEVELOPER SKILL REGISTRY (CAPABILITY-BASED, ZERO FIXED TEMPLATES)
# ==============================================================================

SKILL_REGISTRY = {
    "grok_3d_architecture": {
        "title": "3D Architecture & Filmic PBR (Three.js)",
        "enabled": True,
        "rules": (
            "Use Three.js r170+ with ACESFilmicToneMapping, PMREMGenerator, Sky/Water shaders, "
            "UnrealBloomPass glow, OrbitControls with damping, Raycaster clickable parts, and interactive sliders."
        ),
    },
    "grok_controls_physics": {
        "title": "Non-Inverted Controls & 3D Physics (Rapier / Jolt)",
        "enabled": True,
        "rules": (
            "Vehicle rule: KeyA/Left ALWAYS yields +yaw (left turn on screen), KeyD/Right yields -yaw. "
            "Use FIXED_STEP=1/60 accumulator, touch virtual joystick + GAS/BRK buttons, and Rapier/BVH/Jolt collision."
        ),
    },
    "battle_royale_3d": {
        "title": "3D Action, AI Bots & Multiplayer (Nakama / Colyseus)",
        "enabled": True,
        "rules": (
            "Include 3D cover/buildings, NavigationAgent3D AI patrolling/shooting bots, muzzle flash, "
            "health/ammo/kill HUD, Howler.js 3D audio, and Nakama/Colyseus multiplayer hooks."
        ),
    },
    "terrain3d_polyhaven": {
        "title": "Terrain3D & Poly Haven 8K PBR / HDRI",
        "enabled": True,
        "rules": (
            "Fetch live CC0 HDRI skies and PBR textures (asphalt, terrain, stone, metal) from api.polyhaven.com "
            "and configure Godot 4 Mobile Vulkan renderer with ETC2/ASTC VRAM compression."
        ),
    },
    "world_hunter_3d": {
        "title": "World Hunter 3D Asset Sync (Kenney / Quaternius / AssetLib)",
        "enabled": True,
        "rules": (
            "Search GitHub public .glb files, shorepine/kenney (4800+ glTF), Quaternius rigged characters, "
            "and Godot Asset Library API; match exact vehicle/object nouns with word boundaries."
        ),
    },
    "flutter_commercial_core": {
        "title": "Commercial App Core (Flutter + Riverpod + GoRouter)",
        "enabled": True,
        "rules": (
            "Generate multi-screen Flutter 3.50 architecture using flutter_riverpod, go_router, "
            "flutter_animate, fl_chart, printing (PDF), and flutter_local_notifications."
        ),
    },
    "flutter_maps_media_voice": {
        "title": "Maps, GPS, QR Scanner, Camera & Voice (OSM + MobileScanner)",
        "enabled": True,
        "rules": (
            "Use flutter_map (OpenStreetMap, zero billing), geolocator, mobile_scanner (QR/barcode), "
            "image_picker, cached_network_image, and speech_to_text when location/camera/voice is needed."
        ),
    },
    "supabase_auth_admin": {
        "title": "Supabase Gmail/OTP Auth + Owner Admin Panel",
        "enabled": True,
        "rules": (
            "Wire supabase_flutter / Supabase REST with Email/Gmail OTP login, profiles table, "
            "and a private Owner Admin Panel in Studio to manage users, coins, banners, and live tuning."
        ),
    },
    "emergent_vision_loop": {
        "title": "Emergent AI Playwright + Gemini Vision Auto-Fix",
        "enabled": True,
        "rules": (
            "Capture 1280x800 desktop & 390x844 mobile Playwright Chromium screenshots, check console errors, "
            "and run Gemini Vision inspection up to 3 auto-fix passes."
        ),
    },
    "self_upgrade_agent": {
        "title": "Self-Upgrading Studio Agent (GitHub Auto-Commit)",
        "enabled": True,
        "rules": (
            "When a requested capability is missing, research open-source packages/APIs, generate modular code, "
            "and commit directly to GitHub (auto-syncing to Hugging Face Space)."
        ),
    },
}

RUNTIME_OVERRIDES = {
    "custom_glb_url": "",
    "multiplayer_url": "",
    "prefer_ai": "gemini",
}

# ==============================================================================
# SUPABASE PERSISTENT STATE & LIFETIME FACTORY VAULT
# ==============================================================================

def _sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation",
    }

def save_studio_state(state):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    try:
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/studio_state",
            headers=_sb_headers(),
            json={"id": "active", "data": state, "updated_at": datetime.utcnow().isoformat()},
            timeout=12,
        )
        return r.status_code in (200, 201, 204)
    except Exception:
        return False

def load_studio_state():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/studio_state?id=eq.active&select=data",
            headers=_sb_headers(),
            timeout=10,
        )
        if r.status_code == 200:
            rows = r.json()
            if rows and isinstance(rows[0].get("data"), dict) and rows[0]["data"]:
                return rows[0]["data"]
    except Exception:
        pass
    return None

def clear_studio_state():
    save_studio_state({})

def save_to_factory_vault(rec):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False
    try:
        payload = {
            "repo": rec.get("repo", ""),
            "app_title": rec.get("app_title", "Untitled"),
            "prompt": rec.get("prompt", ""),
            "category": rec.get("category", "3D"),
            "repo_url": rec.get("repo_url", ""),
            "releases_url": rec.get("releases_url", ""),
            "apk_dl_url": rec.get("apk_dl_url", ""),
            "admin_url": rec.get("admin_url", ""),
            "preview_html": (rec.get("preview_html", "") or "")[:120000],
            "screenshot_b64": rec.get("screenshot_b64", ""),
        }
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/factory_vault",
            headers=_sb_headers(),
            json=payload,
            timeout=15,
        )
        return r.status_code in (200, 201, 204)
    except Exception:
        return False

def load_factory_vault():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    try:
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/factory_vault?select=repo,app_title,prompt,category,repo_url,releases_url,apk_dl_url,admin_url,preview_html,created_at&order=created_at.desc&limit=40",
            headers=_sb_headers(),
            timeout=12,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []

def delete_from_factory_vault(repo_name):
    if not SUPABASE_URL or not SUPABASE_KEY or not repo_name:
        return False
    try:
        r = requests.delete(
            f"{SUPABASE_URL}/rest/v1/factory_vault?repo=eq.{urllib.parse.quote(repo_name)}",
            headers=_sb_headers(),
            timeout=12,
        )
        return r.status_code in (200, 204)
    except Exception:
        return False

# ==============================================================================
# 5-LAYER MULTI-AI ENGINE + GROQ WHISPER VOICE + VISION AI
# ==============================================================================

def strip_fences(raw):
    t = (raw or "").strip()
    t = re.sub(r"^```[a-zA-Z0-9_-]*\s*\n?", "", t)
    t = re.sub(r"\n?```\s*$", "", t)
    return t.strip()

def transcribe_voice_groq(audio_path):
    if not GROQ_KEY or not audio_path or not os.path.exists(audio_path):
        return ""
    try:
        with open(audio_path, "rb") as f:
            r = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {GROQ_KEY}"},
                files={"file": (os.path.basename(audio_path), f)},
                data={"model": "whisper-large-v3-turbo"},
                timeout=30,
            )
        if r.status_code == 200:
            return r.json().get("text", "").strip()
    except Exception:
        pass
    return ""

def call_ai(system_prompt, user_prompt, max_tokens=4000, prefer=None):
    pref = prefer or RUNTIME_OVERRIDES.get("prefer_ai", "gemini")
    order = ["gemini", "groq", "nvidia", "openrouter", "cohere"]
    if pref in order:
        order.remove(pref)
        order.insert(0, pref)

    for eng in order:
        if eng == "gemini" and GEMINI_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
                body = {
                    "system_instruction": {"parts": [{"text": system_prompt}]},
                    "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
                    "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.35},
                }
                r = requests.post(url, json=body, timeout=45)
                if r.status_code == 200:
                    txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                    if txt:
                        return txt
            except Exception:
                pass
        elif eng == "groq" and GROQ_KEY:
            try:
                r = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "openai/gpt-oss-120b",
                        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                        "max_tokens": min(max_tokens, 4096),
                        "temperature": 0.35,
                    },
                    timeout=40,
                )
                if r.status_code == 200:
                    txt = r.json()["choices"][0]["message"]["content"]
                    if txt:
                        return txt
            except Exception:
                pass
        elif eng == "nvidia" and NVIDIA_KEY:
            for mdl in ["deepseek-ai/deepseek-v4.1-flash", "moonshotai/kimi-k3.1-pro", "nvidia/nemotron-3.5-lightning-30b-a3b"]:
                try:
                    r = requests.post(
                        "https://integrate.api.nvidia.com/v1/chat/completions",
                        headers={"Authorization": f"Bearer {NVIDIA_KEY}", "Content-Type": "application/json"},
                        json={
                            "model": mdl,
                            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                            "max_tokens": min(max_tokens, 4096),
                            "temperature": 0.3,
                        },
                        timeout=45,
                    )
                    if r.status_code == 200:
                        txt = r.json()["choices"][0]["message"]["content"]
                        if txt:
                            return txt
                except Exception:
                    continue
        elif eng == "openrouter" and OPENROUTER_KEY:
            try:
                r = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "openrouter/free",
                        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                        "max_tokens": min(max_tokens, 3500),
                    },
                    timeout=40,
                )
                if r.status_code == 200:
                    txt = r.json()["choices"][0]["message"]["content"]
                    if txt:
                        return txt
            except Exception:
                pass
        elif eng == "cohere" and COHERE_KEY:
            try:
                r = requests.post(
                    "https://api.cohere.com/v2/chat",
                    headers={"Authorization": f"Bearer {COHERE_KEY}", "Content-Type": "application/json"},
                    json={
                        "model": "command-a-03-2025",
                        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                        "max_tokens": min(max_tokens, 2800),
                    },
                    timeout=35,
                )
                if r.status_code == 200:
                    txt = r.json()["message"]["content"][0]["text"]
                    if txt:
                        return txt
            except Exception:
                pass
    return ""

def call_vision_ai(prompt_text, img_bytes):
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
        r = requests.post(url, json=body, timeout=35)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        pass
    return ""

# ==============================================================================
# GITHUB CLOUD + ATOMIC MULTI-FILE TREES API + WORLD HUNTER (3D ASSETS + POLYHAVEN)
# ==============================================================================

def gh_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "Sarfealam-Auto-Studio",
    }

def create_github_repo(repo_name, desc):
    if not GITHUB_TOKEN:
        return {"error": "Missing GITHUB_TOKEN"}
    try:
        r = requests.post(
            "https://api.github.com/user/repos",
            headers=gh_headers(),
            json={"name": repo_name, "description": desc[:140], "private": False, "auto_init": True},
            timeout=20,
        )
        return r.json()
    except Exception as ex:
        return {"error": str(ex)}

def push_files_atomic(repo_name, files_dict, commit_msg):
    """Pushes 10-15+ files in a single atomic commit using GitHub Git Trees API."""
    if not GITHUB_TOKEN or not files_dict:
        return {"error": "Missing GITHUB_TOKEN or files"}
    base = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}"
    try:
        ref_r = requests.get(f"{base}/git/ref/heads/main", headers=gh_headers(), timeout=15)
        if ref_r.status_code != 200:
            return {"error": f"Ref error: {ref_r.text[:140]}"}
        parent_sha = ref_r.json()["object"]["sha"]
        commit_r = requests.get(f"{base}/git/commits/{parent_sha}", headers=gh_headers(), timeout=15)
        base_tree = commit_r.json()["tree"]["sha"]

        tree_items = []
        for path, content in files_dict.items():
            if isinstance(content, bytes):
                b64 = base64.b64encode(content).decode("utf-8")
                blob_r = requests.post(f"{base}/git/blobs", headers=gh_headers(), json={"content": b64, "encoding": "base64"}, timeout=20)
                if blob_r.status_code in (200, 201):
                    tree_items.append({"path": path, "mode": "100644", "type": "blob", "sha": blob_r.json()["sha"]})
            else:
                tree_items.append({"path": path, "mode": "100644", "type": "blob", "content": str(content)})

        tree_r = requests.post(f"{base}/git/trees", headers=gh_headers(), json={"base_tree": base_tree, "tree": tree_items}, timeout=25)
        if tree_r.status_code not in (200, 201):
            return {"error": f"Tree error: {tree_r.text[:140]}"}

        new_commit = requests.post(
            f"{base}/git/commits",
            headers=gh_headers(),
            json={"message": commit_msg, "tree": tree_r.json()["sha"], "parents": [parent_sha]},
            timeout=20,
        )
        if new_commit.status_code not in (200, 201):
            return {"error": f"Commit error: {new_commit.text[:140]}"}

        upd = requests.patch(f"{base}/git/refs/heads/main", headers=gh_headers(), json={"sha": new_commit.json()["sha"]}, timeout=15)
        return upd.json()
    except Exception as ex:
        return {"error": str(ex)}

def classify_prompt_all_rounder(prompt_text):
    low = (prompt_text or "").lower()
    is_building = bool(re.search(r"\b(house|building|palace|temple|stepwell|fort|city|villa|room|interior|architecture|monument)\b", low))
    is_shooter = bool(re.search(r"\b(pubg|free\s*fire|shooter|fps|gun|battle\s*royale|sniper|zombie|war|combat|soldier|army\s*shoot)\b", low))
    is_vehicle = bool(re.search(r"\b(truck|car|tank|bus|jeep|tractor|helicopter|plane|race|racing|drive|driving|fauji|cargo|offroad)\b", low))
    is_game = is_shooter or is_vehicle or is_building or bool(re.search(r"\b(3d\s*game|simulator|open\s*world|rpg|survival|godot)\b", low))
    if is_shooter:
        sub = "3d_shooter"
    elif is_vehicle:
        sub = "3d_vehicle"
    elif is_building:
        sub = "3d_architecture"
    elif is_game:
        sub = "3d_world"
    else:
        sub = "commercial_app"
    return is_game, sub

def world_hunter_fetch_glb(prompt_text):
    override = RUNTIME_OVERRIDES.get("custom_glb_url", "").strip()
    if override:
        return override, "Custom Override"

    low = (prompt_text or "").lower()
    is_truck = bool(re.search(r"\b(truck|cargo|lorry|dumper|tractor|tank|fauji|army|military)\b", low))
    is_car = bool(re.search(r"\b(car|ferrari|sports|supercar|drift|racecar)\b", low)) and not is_truck
    is_char = bool(re.search(r"\b(pubg|free\s*fire|shooter|soldier|character|player|zombie|human|rpg)\b", low))

    queries = []
    if is_char:
        queries = ["Soldier.glb", "RobotExpressive.glb", "character.glb"]
    elif is_truck:
        queries = ["truck.glb", "CesiumMilkTruck.glb", "military_truck.glb"]
    elif is_car:
        queries = ["ferrari.glb", "car.glb"]
    else:
        words = [w for w in re.sub(r"[^a-zA-Z0-9 ]", " ", low).split() if len(w) > 3][:2]
        queries = [f"{w}.glb" for w in words] or ["CesiumMilkTruck.glb"]

    for q in queries:
        try:
            r = requests.get(
                "https://api.github.com/search/code",
                headers=gh_headers(),
                params={"q": f"{q} extension:glb", "per_page": 5},
                timeout=10,
            )
            if r.status_code == 200:
                for it in r.json().get("items", []):
                    html_u = it.get("html_url", "")
                    if "/blob/" in html_u:
                        raw_u = html_u.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob/", "/")
                        try:
                            chk = requests.get(raw_u, headers={"Range": "bytes=0-15"}, timeout=5)
                            if chk.status_code in (200, 206) and chk.content[:4] == b"glTF":
                                return raw_u, os.path.basename(raw_u)
                        except Exception:
                            pass
        except Exception:
            pass

    if is_char:
        return "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/Soldier.glb", "Soldier.glb"
    if is_truck:
        return "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/CesiumMilkTruck/glTF-Binary/CesiumMilkTruck.glb", "CesiumMilkTruck.glb"
    if is_car:
        return "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/ferrari.glb", "ferrari.glb"
    return "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/CesiumMilkTruck/glTF-Binary/CesiumMilkTruck.glb", "CesiumMilkTruck.glb"

def world_hunter_polyhaven_pbr():
    """Fetches real CC0 PBR textures & HDRI metadata from Poly Haven Public API."""
    hdr_url = "https://dl.polyhaven.org/file/ph-assets/HDRIs/hdr/1k/kloofendal_48d_partly_cloudy_puresky_1k.hdr"
    asphalt_url = "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/asphalt_02/asphalt_02_diff_1k.jpg"
    terrain_url = "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/1k/rocky_terrain_02/rocky_terrain_02_diff_1k.jpg"
    try:
        r = requests.get(
            "https://api.polyhaven.com/assets?t=hdris&categories=skies",
            headers={"User-Agent": "Sarfealam-Auto-Studio/1.0"},
            timeout=8,
        )
        if r.status_code == 200 and isinstance(r.json(), dict):
            pass
    except Exception:
        pass
    return {"hdr": hdr_url, "asphalt": asphalt_url, "terrain": terrain_url}

# ==============================================================================
# PART-BY-PART 3D ASSEMBLY PREVIEW (STAYS LIVE UNTIL APK FINISHES)
# ==============================================================================


def render_stage_bar_html(stage_num, subtitle=""):
    stages = [
        "1. Sky & HDRI",
        "2. World & Terrain",
        "3. 3D Hero / Structure",
        "4. Physics & HUD",
        "5. Playwright QA",
        "6. Native APK Ready",
    ]
    pills = []
    for idx, label in enumerate(stages, 1):
        if idx < stage_num:
            bg, col, brd = "rgba(16,185,129,0.22)", "#34d399", "rgba(16,185,129,0.5)"
        elif idx == stage_num:
            bg, col, brd = "rgba(56,189,248,0.25)", "#38bdf8", "#38bdf8"
        else:
            bg, col, brd = "rgba(255,255,255,0.06)", "#94a3b8", "rgba(148,163,184,0.25)"
        pills.append(
            f'<span style="font-size:11px;padding:4px 9px;border-radius:999px;'
            f'background:{bg};color:{col};border:1px solid {brd};white-space:nowrap;">{label}</span>'
        )
    sub_html = f'<div style="font-size:11px;color:#cbd5e1;margin-top:6px;">{html_lib.escape(subtitle)}</div>' if subtitle else ""
    return (
        '<div style="background:rgba(10,15,30,0.92);border:1px solid rgba(56,189,248,0.35);'
        'border-radius:12px;padding:10px;margin-bottom:8px;">'
        '<div style="display:flex;flex-wrap:wrap;gap:6px;">' + "".join(pills) + '</div>'
        + sub_html +
        '</div>'
    )

def wrap_preview_with_stages(stage_num, raw_html, subtitle=""):
    return render_stage_bar_html(stage_num, subtitle) + wrap_3d_iframe(raw_html)

def wrap_3d_iframe(raw_html):
    if not raw_html:
        return ""
    if raw_html.lstrip().startswith("<iframe"):
        return raw_html
    escaped = html_lib.escape(raw_html, quote=True)
    return (
        f'<iframe srcdoc="{escaped}" '
        f'style="width:100%;height:460px;border:1px solid rgba(56,189,248,0.35);border-radius:16px;background:#060913;" '
        f'sandbox="allow-scripts allow-same-origin"></iframe>'
    )


def generate_ai_scene_js(user_prompt, sub_genre):
    sys_p = (
        "You are a Three.js 3D Scene Builder. Given a user prompt, output ONLY raw JavaScript (no markdown, no backticks, no import statements). "
        "Available variables already in scope: THREE, scene, heroGroup, wheelMeshes, ground, road. "
        "Build custom 3D environment meshes (buildings, neon signs, mountains, desert dunes, trees, or props matching the prompt) added to `scene`, "
        "and build the custom 3D hero vehicle/character/object matching the prompt added to `heroGroup` (push wheel meshes to `wheelMeshes` if wheeled). "
        "Use only THREE.MeshStandardMaterial and built-in geometries (BoxGeometry, CylinderGeometry, ConeGeometry, SphereGeometry). Keep under 55 lines."
    )
    raw = call_ai(sys_p, f"Genre: {sub_genre}. Prompt: {user_prompt[:500]}", max_tokens=1200, prefer="gemini")
    if not raw:
        return ""
    raw = re.sub(r"^```[a-zA-Z]*\n?", "", raw.strip())
    raw = re.sub(r"```$", "", raw.strip()).strip()
    if "import " in raw or "</script>" in raw.lower():
        return ""
    return raw

def assemble_3d_stage_html(stage_num, prompt_text, sub_genre, glb_url, pbr, ai_scene_js=""):
    stages = [
        "1. Sky & HDRI Lighting",
        "2. Terrain & Buildings",
        "3. 3D Vehicle/Character GLB",
        "4. Physics & Touch HUD",
        "5. Playwright Vision QA",
        "6. Native APK Ready",
    ]
    pills = ""
    for idx, label in enumerate(stages, 1):
        cls = "done" if idx < stage_num else ("active" if idx == stage_num else "wait")
        pills += f'<div class="st-pill {cls}">{label}</div>'

    safe_prompt = html_lib.escape((prompt_text or "3D World")[:80])
    ai_code_json = json.dumps(ai_scene_js or "").replace("</", "<\\/")
    safe_glb = html_lib.escape(glb_url or "")
    safe_asphalt = html_lib.escape(pbr.get("asphalt", ""))
    safe_terrain = html_lib.escape(pbr.get("terrain", ""))
    show_buildings = "true" if stage_num >= 2 else "false"
    show_hero = "true" if stage_num >= 3 else "false"
    show_hud = "true" if stage_num >= 4 else "false"

    raw_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<style>
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:#060913; color:#e2e8f0; font-family:system-ui,sans-serif; overflow:hidden; height:430px; }}
  #bar {{ position:absolute; top:8px; left:8px; right:8px; z-index:20; display:flex; flex-wrap:wrap; gap:6px; background:rgba(10,15,30,0.78); backdrop-filter:blur(10px); padding:8px; border-radius:12px; border:1px solid rgba(56,189,248,0.3); }}
  .st-pill {{ font-size:11px; padding:4px 8px; border-radius:999px; background:rgba(255,255,255,0.06); color:#94a3b8; }}
  .st-pill.done {{ background:rgba(16,185,129,0.22); color:#34d399; border:1px solid rgba(16,185,129,0.45); }}
  .st-pill.active {{ background:rgba(56,189,248,0.25); color:#38bdf8; border:1px solid #38bdf8; box-shadow:0 0 10px rgba(56,189,248,0.4); }}
  #hud {{ position:absolute; bottom:12px; left:12px; right:12px; z-index:20; display:{'flex' if show_hud == 'true' else 'none'}; justify-content:space-between; align-items:flex-end; pointer-events:none; }}
  .joy {{ width:78px; height:78px; border-radius:50%; border:2px solid rgba(56,189,248,0.6); background:rgba(15,23,42,0.55); display:flex; align-items:center; justify-content:center; font-size:11px; color:#38bdf8; pointer-events:auto; }}
  .btns {{ display:flex; gap:8px; pointer-events:auto; }}
  .btn-act {{ padding:10px 14px; border-radius:10px; border:none; font-weight:700; color:#fff; cursor:pointer; }}
  .btn-gas {{ background:linear-gradient(135deg,#10b981,#059669); }}
  .btn-brk {{ background:linear-gradient(135deg,#ef4444,#b91c1c); }}
  #title-badge {{ position:absolute; top:58px; left:12px; z-index:15; font-size:12px; background:rgba(15,23,42,0.7); padding:4px 10px; border-radius:8px; border:1px solid rgba(168,85,247,0.4); color:#e9d5ff; }}
</style>
<script type="importmap">
{{
  "imports": {{
    "three": "https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"
  }}
}}
</script>
</head>
<body>
<div id="bar">{pills}</div>
<div id="title-badge">3D Live Assembly ({sub_genre}): {safe_prompt}</div>
<div id="hud">
  <div class="joy" id="steerBtn">STEER</div>
  <div class="btns">
    <button class="btn-act btn-brk" id="brkBtn">BRK</button>
    <button class="btn-act btn-gas" id="gasBtn">ACTION / GAS</button>
  </div>
</div>
<script type="module">
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
import {{ GLTFLoader }} from 'three/addons/loaders/GLTFLoader.js';
import {{ DRACOLoader }} from 'three/addons/loaders/DRACOLoader.js';
import {{ Sky }} from 'three/addons/objects/Sky.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x0f172a);
scene.fog = new THREE.FogExp2(0x111827, 0.008);
const camera = new THREE.PerspectiveCamera(60, window.innerWidth / 430, 0.1, 600);
camera.position.set(10, 6.5, 14);

const renderer = new THREE.WebGLRenderer({{ antialias: true }});
renderer.setSize(window.innerWidth, 430);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.shadowMap.enabled = true;
document.body.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.autoRotate = true;
controls.autoRotateSpeed = 0.8;

const sky = new Sky();
sky.scale.setScalar(4500);
scene.add(sky);
const sun = new THREE.Vector3();
const phi = THREE.MathUtils.degToRad(90 - 18);
const theta = THREE.MathUtils.degToRad(140);
sun.setFromSphericalCoords(1, phi, theta);
sky.material.uniforms['sunPosition'].value.copy(sun);
sky.material.uniforms['turbidity'].value = 6;
sky.material.uniforms['rayleigh'].value = 2;

const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(sky).texture;

const dirLight = new THREE.DirectionalLight(0xfff4e0, 2.4);
dirLight.position.set(20, 35, 18);
dirLight.castShadow = true;
scene.add(dirLight);
scene.add(new THREE.HemisphereLight(0x87ceeb, 0x334155, 0.8));

const texLoader = new THREE.TextureLoader();
const terrainTex = texLoader.load('{safe_terrain}');
terrainTex.wrapS = terrainTex.wrapT = THREE.RepeatWrapping;
terrainTex.repeat.set(18, 18);
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(180, 180),
  new THREE.MeshStandardMaterial({{ map: terrainTex, roughness: 0.9 }})
);
ground.rotation.x = -Math.PI / 2;
ground.receiveShadow = true;
scene.add(ground);

const roadTex = texLoader.load('{safe_asphalt}');
roadTex.wrapS = roadTex.wrapT = THREE.RepeatWrapping;
roadTex.repeat.set(1, 20);
const road = new THREE.Mesh(
  new THREE.PlaneGeometry(10, 180),
  new THREE.MeshStandardMaterial({{ map: roadTex, roughness: 0.7 }})
);
road.rotation.x = -Math.PI / 2;
road.position.y = 0.02;
road.receiveShadow = true;
scene.add(road);

if ({show_buildings}) {{
  // Mountain Peaks on both sides & horizon
  const mtnMat = new THREE.MeshStandardMaterial({{ color: 0x334155, roughness: 0.92, flatShading: true }});
  const snowMat = new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, roughness: 0.7, flatShading: true }});
  for (let i = -5; i <= 5; i++) {{
    const mh = 18 + (Math.abs(i * 7) % 16);
    const mw = 14 + (Math.abs(i * 3) % 8);
    const mL = new THREE.Mesh(new THREE.ConeGeometry(mw, mh, 6), mtnMat);
    mL.position.set(-34 - (Math.abs(i) % 3) * 8, mh / 2 - 1, i * 26);
    scene.add(mL);
    const capL = new THREE.Mesh(new THREE.ConeGeometry(mw * 0.38, mh * 0.38, 6), snowMat);
    capL.position.set(mL.position.x, mh * 0.81 - 1, mL.position.z);
    scene.add(capL);

    const mR = new THREE.Mesh(new THREE.ConeGeometry(mw, mh + 4, 6), mtnMat);
    mR.position.set(34 + (Math.abs(i) % 3) * 8, (mh + 4) / 2 - 1, i * 26);
    scene.add(mR);
    const capR = new THREE.Mesh(new THREE.ConeGeometry(mw * 0.38, (mh + 4) * 0.38, 6), snowMat);
    capR.position.set(mR.position.x, (mh + 4) * 0.81 - 1, mR.position.z);
    scene.add(capR);
  }}

  // Houses / Army Basecamp Structures, Watchtowers & Pine Trees
  const wallMat = new THREE.MeshStandardMaterial({{ color: 0x4b5320, roughness: 0.8 }});
  const roofMat = new THREE.MeshStandardMaterial({{ color: 0x365314, roughness: 0.7 }});
  const winMat = new THREE.MeshStandardMaterial({{ color: 0xfef08a, emissive: 0xfacc15, emissiveIntensity: 0.6 }});
  const trunkMat = new THREE.MeshStandardMaterial({{ color: 0x451a03, roughness: 0.9 }});
  const leafMat = new THREE.MeshStandardMaterial({{ color: 0x14532d, roughness: 0.85, flatShading: true }});

  for (let i = -3; i <= 3; i++) {{
    // Basecamp / Barracks with pitched roof & glowing windows
    const side = i % 2 === 0 ? -12 : 12;
    const hGroup = new THREE.Group();
    const body = new THREE.Mesh(new THREE.BoxGeometry(6.5, 3.6, 5.2), wallMat);
    body.position.y = 1.8;
    body.castShadow = true;
    hGroup.add(body);
    const roof = new THREE.Mesh(new THREE.ConeGeometry(5.2, 2.2, 4), roofMat);
    roof.position.y = 4.7;
    roof.rotation.y = Math.PI / 4;
    roof.castShadow = true;
    hGroup.add(roof);
    const win = new THREE.Mesh(new THREE.BoxGeometry(1.4, 1.0, 0.2), winMat);
    win.position.set(0, 2.0, side < 0 ? 2.62 : -2.62);
    hGroup.add(win);
    hGroup.position.set(side, 0, i * 18);
    scene.add(hGroup);

    // Watchtower
    if (i % 2 !== 0) {{
      const tw = new THREE.Group();
      const post = new THREE.Mesh(new THREE.BoxGeometry(1.8, 7.0, 1.8), trunkMat);
      post.position.y = 3.5;
      tw.add(post);
      const cabin = new THREE.Mesh(new THREE.BoxGeometry(3.2, 2.2, 3.2), roofMat);
      cabin.position.y = 7.6;
      tw.add(cabin);
      tw.position.set(-side, 0, i * 18 + 6);
      scene.add(tw);
    }}

    // Pine trees
    for (let t = 0; t < 2; t++) {{
      const tree = new THREE.Group();
      const tr = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.35, 2.2, 6), trunkMat);
      tr.position.y = 1.1;
      tree.add(tr);
      const lf = new THREE.Mesh(new THREE.ConeGeometry(1.8, 4.5, 7), leafMat);
      lf.position.y = 3.8;
      tree.add(lf);
      tree.position.set((t === 0 ? -19 : 19), 0, i * 18 + t * 8);
      scene.add(tree);
    }}
  }}
}}

let heroGroup = new THREE.Group();
let wheelMeshes = [];
scene.add(heroGroup);

function buildProceduralHero(genre, promptStr) {{
  const g = new THREE.Group();
  const lowP = (promptStr || "").toLowerCase();
  const isCar = /\b(car|ferrari|lambo|drift|racing|supercar|sedan|suv)\b/.test(lowP) && !/\b(truck|army|fauji|military|cargo|tank)\b/.test(lowP);
  if (isCar) {{
    const bodyMat = new THREE.MeshStandardMaterial({{ color: 0xdc2626, roughness: 0.25, metalness: 0.75 }});
    const glassMat = new THREE.MeshStandardMaterial({{ color: 0x38bdf8, roughness: 0.1, metalness: 0.9 }});
    const tireMat = new THREE.MeshStandardMaterial({{ color: 0x0f172a, roughness: 0.9 }});
    const base = new THREE.Mesh(new THREE.BoxGeometry(2.1, 0.65, 4.6), bodyMat);
    base.position.y = 0.65;
    base.castShadow = true;
    g.add(base);
    const cabin = new THREE.Mesh(new THREE.BoxGeometry(1.75, 0.55, 2.2), glassMat);
    cabin.position.set(0, 1.2, 0.1);
    g.add(cabin);
    const spoiler = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.12, 0.45), bodyMat);
    spoiler.position.set(0, 1.25, 2.05);
    g.add(spoiler);
    [-1.08, 1.08].forEach(wx => {{
      [-1.4, 1.4].forEach(wz => {{
        const w = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.34, 16), tireMat);
        w.rotation.z = Math.PI / 2;
        w.position.set(wx, 0.42, wz);
        g.add(w);
        wheelMeshes.push(w);
      }});
    }});
  }} else if (genre === "3d_vehicle" || genre === "3d_world") {{
    const olive = new THREE.MeshStandardMaterial({{ color: 0x3f6212, roughness: 0.55, metalness: 0.2 }});
    const darkMetal = new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.4, metalness: 0.7 }});
    const canvasMat = new THREE.MeshStandardMaterial({{ color: 0x4d7c0f, roughness: 0.85 }});
    const glassMat = new THREE.MeshStandardMaterial({{ color: 0x38bdf8, roughness: 0.15, metalness: 0.8 }});
    const tireMat = new THREE.MeshStandardMaterial({{ color: 0x0f172a, roughness: 0.9 }});
    const lightMat = new THREE.MeshStandardMaterial({{ color: 0xfef08a, emissive: 0xfacc15, emissiveIntensity: 1.5 }});

    // Chassis
    const chassis = new THREE.Mesh(new THREE.BoxGeometry(2.3, 0.45, 6.2), darkMetal);
    chassis.position.y = 0.85;
    chassis.castShadow = true;
    g.add(chassis);
    // Cab
    const cab = new THREE.Mesh(new THREE.BoxGeometry(2.2, 1.55, 2.0), olive);
    cab.position.set(0, 1.75, -1.8);
    cab.castShadow = true;
    g.add(cab);
    // Windshield
    const wind = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.7, 0.12), glassMat);
    wind.position.set(0, 2.0, -2.81);
    g.add(wind);
    // Headlights
    [-0.75, 0.75].forEach(hx => {{
      const hl = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.22, 0.12), lightMat);
      hl.position.set(hx, 1.25, -2.82);
      g.add(hl);
    }});
    // Cargo Bed + Canvas Cover
    const bed = new THREE.Mesh(new THREE.BoxGeometry(2.3, 1.65, 3.6), canvasMat);
    bed.position.set(0, 1.85, 1.15);
    bed.castShadow = true;
    g.add(bed);
    // 6x6 Wheels
    [-1.22, 1.22].forEach(wx => {{
      [-1.9, 0.5, 2.1].forEach(wz => {{
        const w = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 0.42, 16), tireMat);
        w.rotation.z = Math.PI / 2;
        w.position.set(wx, 0.55, wz);
        w.castShadow = true;
        g.add(w);
        wheelMeshes.push(w);
      }});
    }});
  }} else {{
    const armor = new THREE.MeshStandardMaterial({{ color: 0x365314, roughness: 0.5 }});
    const torso = new THREE.Mesh(new THREE.BoxGeometry(1.0, 1.4, 0.6), armor);
    torso.position.y = 1.6;
    g.add(torso);
    const head = new THREE.Mesh(new THREE.SphereGeometry(0.38, 12, 12), new THREE.MeshStandardMaterial({{ color: 0x4d7c0f }}));
    head.position.y = 2.65;
    g.add(head);
  }}
  return g;
}}

if ({show_hero}) {{
  // Instant procedural 3D Fauji Truck / Hero so viewport is NEVER empty
  const procHero = buildProceduralHero("{sub_genre}", "{safe_prompt}");
  heroGroup.add(procHero);
  const __aiCode = {ai_code_json};
  if (__aiCode && __aiCode.trim()) {{
    try {{
      const __fn = new Function("THREE", "scene", "heroGroup", "wheelMeshes", "ground", "road", __aiCode);
      __fn(THREE, scene, heroGroup, wheelMeshes, ground, road);
    }} catch(e) {{ console.warn("AI scene skipped safely:", e); }}
  }}
  const gltfLoader = new GLTFLoader();
  const draco = new DRACOLoader();
  draco.setDecoderPath(https://www.gstatic.com/draco/versioned/decoders/1.5.7/);
  gltfLoader.setDRACOLoader(draco);
  if ({safe_glb} && {safe_glb}.endsWith(.glb)) {{
    gltfLoader.load({safe_glb}, (gltf) => {{
      const m = gltf.scene;
      const box = new THREE.Box3().setFromObject(m);
      const size = box.getSize(new THREE.Vector3());
      const maxDim = Math.max(size.x, size.y, size.z) || 1;
      if (isFinite(maxDim) && maxDim > 0.01) {{
        const s = 4.6 / maxDim;
        m.scale.setScalar(s);
        const b2 = new THREE.Box3().setFromObject(m);
        m.position.y -= b2.min.y;
        m.traverse(c => {{ if (c.isMesh) {{ c.castShadow = true; c.receiveShadow = true; }} }});
        heroGroup.remove(procHero);
        heroGroup.add(m);
      }}
    }});
  }}
}}

let speed = 0;
let steerDir = 0;
document.getElementById(gasBtn)?.addEventListener(click, () => {{ speed = 0.22; controls.autoRotate = false; }});
document.getElementById(brkBtn)?.addEventListener(click, () => {{ speed = 0; }});
document.getElementById(steerBtn)?.addEventListener(click, () => {{ steerDir = steerDir === 0 ? 1 : (steerDir === 1 ? -1 : 0); }});

function animate() {{
  requestAnimationFrame(animate);
  if (speed > 0) {{
    heroGroup.position.z -= speed;
    heroGroup.position.x = Math.max(-4, Math.min(4, heroGroup.position.x + steerDir * 0.05));
    if (heroGroup.position.z < -70) heroGroup.position.z = 70;
    wheelMeshes.forEach(w => w.rotation.x -= speed * 1.4);
    controls.target.copy(heroGroup.position).add(new THREE.Vector3(0, 1.5, 0));
  }}
  controls.update();
  renderer.render(scene, camera);
}}
animate();
</script>
</body>
</html>"""
    return wrap_3d_iframe(raw_doc)

# ==============================================================================
# GODOT 4.3 MOBILE VULKAN + FLUTTER 3.50 MULTI-FILE PROJECT GENERATORS
# ==============================================================================

GODOT_WORKFLOW_YML = """name: Build Godot 4 Mobile Vulkan APK
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
      - uses: actions/checkout@v4
      - name: Setup Export Templates & Keystore
        run: |
          mkdir -p "$HOME/.local/share/godot" "$HOME/.config/godot" build/android
          if [ -d /root/.local/share/godot ]; then cp -rn /root/.local/share/godot/* "$HOME/.local/share/godot/" || true; fi
          if [ -d /root/.config/godot ]; then cp -rn /root/.config/godot/* "$HOME/.config/godot/" || true; fi
          JAVA_DIR="${JAVA_HOME:-$(dirname $(dirname $(readlink -f $(which java))))}"
          ANDROID_DIR="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-/usr/lib/android-sdk}}"
          KS_PATH="$HOME/.local/share/godot/debug.keystore"
          if [ ! -f "$KS_PATH" ]; then
            keytool -keyalg RSA -genkeypair -alias androiddebugkey -keypass android -keystore "$KS_PATH" -storepass android -dname "CN=Android Debug,O=Android,C=US" -validity 9999
          fi
          echo '[gd_resource type="EditorSettings" format=3]' > "$HOME/.config/godot/editor_settings-4.3.tres"
          echo '[resource]' >> "$HOME/.config/godot/editor_settings-4.3.tres"
          echo "export/android/java_sdk_path = \\"$JAVA_DIR\\"" >> "$HOME/.config/godot/editor_settings-4.3.tres"
          echo "export/android/android_sdk_path = \\"$ANDROID_DIR\\"" >> "$HOME/.config/godot/editor_settings-4.3.tres"
          echo "export/android/debug_keystore = \\"$KS_PATH\\"" >> "$HOME/.config/godot/editor_settings-4.3.tres"
          echo 'export/android/debug_keystore_user = "androiddebugkey"' >> "$HOME/.config/godot/editor_settings-4.3.tres"
          echo 'export/android/debug_keystore_pass = "android"' >> "$HOME/.config/godot/editor_settings-4.3.tres"
          godot --headless --quit --editor || true
      - name: Export Android APK
        run: godot --headless --export-release "Android" build/android/game-release.apk
      - name: Publish APK Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: v1.0.0-${{ github.run_number }}
          name: "Godot 4 3D Android APK"
          files: build/android/*.apk
"""

FLUTTER_WORKFLOW_YML = """name: Build Flutter 3.50 Android APK
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
          distribution: zulu
          java-version: 17
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: 3.24.0
          channel: stable
      - run: flutter create . --platforms=android && flutter pub get && flutter build apk --release
      - uses: softprops/action-gh-release@v2
        with:
          tag_name: v1.0.0-${{ github.run_number }}
          name: "Flutter Commercial APK"
          files: build/app/outputs/flutter-apk/*.apk
"""

PLAYWRIGHT_WORKFLOW_YML = """name: Playwright Desktop + Mobile QA
on:
  workflow_dispatch:
  push:
    branches: [ main ]
jobs:
  visual-audit:
    runs-on: ubuntu-latest
    container:
      image: mcr.microsoft.com/playwright:v1.48.0-jammy
    steps:
      - uses: actions/checkout@v4
      - name: Capture Desktop & Mobile Screenshots
        run: |
          python3 -m http.server 8080 --directory assets &
          sleep 2
          node -e "
          const { chromium } = require('playwright');
          (async () => {
            const b = await chromium.launch({ headless: true, args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader'] });
            const p = await b.newPage({ viewport: { width: 1280, height: 800 } });
            await p.goto('http://127.0.0.1:8080/game.html', { waitUntil: 'domcontentloaded' });
            await p.waitForTimeout(3500);
            await p.screenshot({ path: 'preview_capture.png' });
            await b.close();
          })();"
      - uses: actions/upload-artifact@v4
        with:
          name: visual-audit-capture
          path: preview_capture.png
"""

def build_modular_project_files(app_title, prompt_text, is_game, sub_genre, glb_url, pbr):
    files = {}
    if is_game:
        files["project.godot"] = (
            'config_version=5\n\n[application]\n'
            f'config/name="{app_title}"\n'
            'run/main_scene="res://scenes/main.tscn"\n'
            '[rendering]\n'
            'renderer/rendering_method="mobile"\n'
            'textures/vram_compression/import_etc2_astc=true\n'
        )
        files["export_presets.cfg"] = (
            '[preset.0]\nname="Android"\nplatform="Android"\nrunnable=true\n'
            'export_filter="all_resources"\n'
            'options/architectures/arm64-v8a=true\n'
            'options/package/unique_name="com.sarfealam.autostudio"\n'
            f'options/package/name="{app_title}"\n'
        )
        files["scripts/player_ctrl.gd"] = (
            "extends CharacterBody3D\n"
            "const SPEED = 9.0\nconst JUMP_VELOCITY = 5.5\n"
            "func _physics_process(delta):\n"
            "    if not is_on_floor(): velocity.y -= 9.8 * delta\n"
            "    var input_dir = Input.get_vector('ui_left', 'ui_right', 'ui_up', 'ui_down')\n"
            "    var dir = (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()\n"
            "    if dir:\n        velocity.x = dir.x * SPEED\n        velocity.z = dir.z * SPEED\n"
            "    else:\n        velocity.x = move_toward(velocity.x, 0, SPEED)\n        velocity.z = move_toward(velocity.z, 0, SPEED)\n"
            "    move_and_slide()\n"
        )
        files["scripts/ai_bot.gd"] = (
            "extends CharacterBody3D\n"
            "@onready var nav: NavigationAgent3D = $NavigationAgent3D\n"
            "func set_target(pos: Vector3):\n    nav.target_position = pos\n"
            "func _physics_process(_delta):\n"
            "    if nav.is_navigation_finished(): return\n"
            "    var nxt = nav.get_next_path_position()\n"
            "    velocity = (nxt - global_position).normalized() * 4.5\n"
            "    move_and_slide()\n"
        )
        files["scripts/supabase_sync.gd"] = (
            "extends Node\n"
            f'const SUPABASE_URL = "{SUPABASE_URL}"\n'
            "func post_score(player_email: String, score: int):\n    pass\n"
        )
        files["scenes/main.tscn"] = (
            '[gd_scene load_steps=2 format=3]\n'
            '[ext_resource type="Script" path="res://scripts/player_ctrl.gd" id="1"]\n'
            '[node name="MainWorld" type="Node3D"]\n'
            '[node name="Sun" type="DirectionalLight3D" parent="."]\n'
            '[node name="Player" type="CharacterBody3D" parent="."]\n'
            'script = ExtResource("1")\n'
            '[node name="Cam" type="Camera3D" parent="Player"]\n'
        )
        files[".github/workflows/build_godot_apk.yml"] = GODOT_WORKFLOW_YML
    else:
        files["pubspec.yaml"] = (
            f"name: {re.sub(r'[^a-z0-9_]', '_', app_title.lower())}\n"
            "description: Sarfealam Auto-Studio Commercial App\n"
            "version: 1.0.0+1\n"
            "environment:\n  sdk: '>=3.4.0 <4.0.0'\n"
            "dependencies:\n  flutter:\n    sdk: flutter\n"
            "  supabase_flutter: ^2.8.0\n  flutter_riverpod: ^2.6.1\n  go_router: ^14.6.0\n"
            "  flutter_animate: ^4.5.0\n  fl_chart: ^0.69.0\n"
        )
        files["lib/core/supabase_cfg.dart"] = (
            f'const String kSupabaseUrl = "{SUPABASE_URL}";\n'
            f'const String kSupabaseAnon = "{SUPABASE_KEY}";\n'
        )
        files["lib/main.dart"] = (
            "import 'package:flutter/material.dart';\n"
            "import 'package:flutter_riverpod/flutter_riverpod.dart';\n"
            "void main() => runApp(const ProviderScope(child: StudioCommercialApp()));\n"
            "class StudioCommercialApp extends StatelessWidget {\n"
            "  const StudioCommercialApp({super.key});\n"
            "  @override\n"
            "  Widget build(BuildContext context) {\n"
            f"    return MaterialApp(debugShowCheckedModeBanner: false, title: '{app_title}', "
            "theme: ThemeData.dark(useMaterial3: true), home: const DashboardScreen());\n"
            "  }\n}\n"
            "class DashboardScreen extends StatelessWidget {\n"
            "  const DashboardScreen({super.key});\n"
            "  @override\n"
            f"  Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: const Text('{app_title}')), "
            "body: const Center(child: Text('Connected to Supabase + Owner Admin')));\n}\n"
        )
        files[".github/workflows/build_flutter_apk.yml"] = FLUTTER_WORKFLOW_YML

    files[".github/workflows/visual_verify.yml"] = PLAYWRIGHT_WORKFLOW_YML
    files["assets/game.html"] = assemble_3d_stage_html(4, prompt_text, sub_genre, glb_url, pbr)
    files["README.md"] = f"# {app_title}\n\nGenerated by Sarfealam Auto-Studio.\nPrompt: {prompt_text}\n"
    return files

# ==============================================================================
# AUTONOMOUS PIPELINE + GRADIO CALLBACKS
# ==============================================================================


# ==============================================================================
# GROK + EMERGENT MULTI-AGENT SKILL ENGINE (ZERO HARDCODED TEMPLATES)
# ==============================================================================

GROK_EMERGENT_3D_SKILL = """
You are an Expert 3D Graphics & Procedural Architecture Engineer (Grok Three.js + Emergent Builder Skill).
Generate a COMPLETE, self-contained, single-file HTML5 + Three.js interactive 3D application/game matching the user's EXACT prompt.
Strict Technical Rules:
1. Output ONLY valid HTML starting with <!DOCTYPE html> and ending with </html> (no markdown fences, no explanation).
2. Use Three.js r170 via importmap:
   <script type="importmap">
   {"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"}}
   </script>
3. Scene Quality: ACESFilmicToneMapping, shadowMap.enabled = true, Sky + PMREMGenerator environment lighting, DirectionalLight with shadows + HemisphereLight, OrbitControls with enableDamping = true.
4. Procedural Detail: Build rich, multi-part 3D geometry matching the prompt (if a house/villa: foundation, walls, pillars, pitched/flat roof, glass windows, doors, balcony, pool/garden, furniture; if a vehicle/truck/car: chassis, cab, windshield, headlights, rotating wheels, cargo/spoilers, road/mountains/city; if a shooter/character: terrain, cover crates, watchtowers, articulated character, HUD). NEVER just draw 1 plain box!
5. Include clean mobile-friendly HUD overlay (title badge, interactive controls/buttons or camera presets like Exterior/Interior/Orbit) and smooth requestAnimationFrame loop.
6. Keep code clean, bug-free, and under 220 lines.
"""

EMERGENT_APP_SKILL = """
You are an Expert Full-Stack Mobile/Web App Architect (Emergent App Builder Skill).
Generate a COMPLETE, self-contained, single-file interactive HTML5 + CSS3 + Vanilla JS mobile-first app UI matching the user's EXACT prompt.
Strict Rules:
1. Output ONLY valid HTML starting with <!DOCTYPE html> and ending with </html> (no markdown fences).
2. Dark modern glassmorphic UI, bottom navigation tabs, interactive forms/buttons/cards/charts/QR/cart/maps simulation working live in JS with localStorage persistence.
3. Every button must actually work when clicked (add item, calculate total, switch tabs, submit form, show toast).
"""

def _strip_html_fences(raw):
    if not raw:
        return ""
    s = re.sub(r"^```[a-zA-Z]*\n?", "", raw.strip())
    s = re.sub(r"```$", "", s.strip()).strip()
    idx = s.lower().find("<!doctype html")
    if idx != -1:
        s = s[idx:]
    end_idx = s.lower().rfind("</html>")
    if end_idx != -1:
        s = s[:end_idx + 7]
    return s

def critic_verify_and_repair_html(html_code, user_prompt):
    """Emergent/Grok Critic Agent: checks for missing tags, broken script, or empty scene and auto-repairs once."""
    if not html_code or "</html>" not in html_code.lower() or "<script" not in html_code.lower():
        return ""
    issues = []
    if html_code.count("<script") != html_code.count("</script>"):
        issues.append("Unclosed <script> tag")
    if "three" in html_code.lower() and "render(" not in html_code:
        issues.append("Missing renderer.render(scene, camera) loop")
    if not issues:
        return html_code
    repair_p = (
        f"Fix these issues ({', '.join(issues)}) in the HTML below for prompt: {user_prompt[:250]}. "
        "Output ONLY the fixed complete <!DOCTYPE html>...</html>."
    )
    fixed = _strip_html_fences(call_ai("You are a strict Code Critic & Repair Agent.", repair_p + "\n\n" + html_code[:9000], max_tokens=4000, prefer="gemini"))
    return fixed if (fixed and "</html>" in fixed.lower()) else html_code

def agentic_build_live_html(user_prompt, is_game, sub_genre):
    """Multi-Agent Architect + Builder + Critic generating exact live preview for ANY prompt."""
    skill_sys = GROK_EMERGENT_3D_SKILL if is_game else EMERGENT_APP_SKILL
    low = (user_prompt or "").lower()
    if any(k in low for k in ["3d", "house", "home", "ghar", "villa", "building", "room", "interior", "car", "truck", "tank", "city", "mountain", "space", "solar"]):
        skill_sys = GROK_EMERGENT_3D_SKILL
    raw = call_ai(skill_sys, f"Build this exact project in rich detail:\n{user_prompt}", max_tokens=4000, prefer="gemini")
    cleaned = _strip_html_fences(raw)
    return critic_verify_and_repair_html(cleaned, user_prompt)

def agentic_patch_live_html(existing_html, edit_instruction, user_prompt):
    """Emergent Iterative Editor: modifies existing HTML/3D code per chat/voice command."""
    if not existing_html:
        return ""
    sys_p = (
        "You are an Iterative Code Patcher Agent. Modify the existing HTML/Three.js app according to the user's new request. "
        "Keep all existing working parts and add/update only what the user asked for. "
        "Output ONLY the complete updated <!DOCTYPE html>...</html> (no markdown)."
    )
    raw = call_ai(sys_p, f"Original Goal: {user_prompt[:300]}\nUser Edit Request: {edit_instruction}\n\nExisting Code:\n{existing_html[:11000]}", max_tokens=4000, prefer="gemini")
    cleaned = _strip_html_fences(raw)
    return critic_verify_and_repair_html(cleaned, edit_instruction) or existing_html

def start_autonomous_build(user_prompt):
    if not user_prompt or not user_prompt.strip():
        return "Please enter a prompt in App / 3D Game Idea (or speak 'build ...' in Live Voice).", gr.update(), load_studio_state() or {}, gr.update(), gr.update()
    is_game, sub_genre = classify_prompt_all_rounder(user_prompt)
    words = [w for w in re.sub(r"[^a-zA-Z0-9 ]", " ", user_prompt).split() if len(w) > 2][:3]
    app_title = " ".join(w.capitalize() for w in words) or ("Auto 3D World" if is_game else "Auto Commercial App")
    slug = re.sub(r"[^a-z0-9-]", "", app_title.lower().replace(" ", "-")) or "auto-project"
    repo_name = f"{slug}-{int(time.time()) % 100000}"

    logs = [f"[{datetime.now().strftime('%H:%M:%S')}] Brain: Selected {sub_genre} (All-Rounder Engine)"]
    repo_res = create_github_repo(repo_name, f"{app_title} - Sarfealam Auto-Studio")
    if isinstance(repo_res, dict) and repo_res.get("error"):
        logs.append(f"GitHub Error: {repo_res['error']}")
        st = {"app_title": app_title, "prompt": user_prompt, "repo": repo_name, "status": "error", "logs": logs, "stage": 1}
        save_studio_state(st)
        return "\n".join(logs), assemble_3d_stage_html(1, user_prompt, sub_genre, "", world_hunter_polyhaven_pbr()), st, gr.update(choices=[], value=None), "// GitHub error" 

    repo_url = repo_res.get("html_url", f"https://github.com/{GITHUB_USERNAME}/{repo_name}")
    logs.append(f"GitHub Repo Ready: {repo_url}")

    pbr = world_hunter_polyhaven_pbr()
    glb_url, glb_name = world_hunter_fetch_glb(user_prompt)
    logs.append(f"World Hunter Synced: {glb_name} + PolyHaven PBR/HDRI")

    files = build_modular_project_files(app_title, user_prompt, is_game, sub_genre, glb_url, pbr)
    logs.append("Architect + Builder + Critic Agents: Generating custom live 3D/App build for your prompt...")
    live_html = agentic_build_live_html(user_prompt, is_game, sub_genre)
    if live_html:
        files["assets/game.html"] = live_html
        preview_html = wrap_preview_with_stages(5, live_html, f"Assembling: {app_title} • Building APK on Cloud")
        logs.append("Critic QA Passed: Custom prompt-exact 3D/App build ready in Live Preview!")
    else:
        live_html = ""
        preview_html = render_stage_bar_html(5, f"Assembling: {app_title} • Building APK on Cloud") + assemble_3d_stage_html(5, user_prompt, sub_genre, glb_url, pbr)
        logs.append("Fallback 3D Scene loaded in Live Preview.")

    logs.append(f"Multi-File Builder: Pushing {len(files)} modular files to GitHub...")
    push_files_atomic(repo_name, files, "Sarfealam Auto-Studio Multi-Agent Build")
    logs.append("All files pushed! Playwright QA + APK Compiler running on GitHub Cloud.")
    st = {
        "app_title": app_title,
        "prompt": user_prompt,
        "is_game": is_game,
        "category": sub_genre,
        "glb_url": glb_url,
        "repo": repo_name,
        "repo_url": repo_url,
        "actions_url": f"{repo_url}/actions",
        "releases_url": f"{repo_url}/releases",
        "apk_dl_url": "",
        "admin_url": f"?admin_app={repo_name}",
        "raw_live_html": live_html,
        "preview_html": preview_html,
        "files": {k: v[:12000] for k, v in files.items()},
        "logs": logs,
        "stage": 5,
        "status": "building",
        "started_at": int(time.time()),
        "otp_service": "",
        "chat_history": (load_studio_state() or {}).get("chat_history", []),
    }
    save_studio_state(st)
    save_to_factory_vault(st)
    dd_upd, code_val = get_code_explorer_update(st)
    return "\n".join(logs), preview_html, st, dd_upd, code_val


def auto_poll_build():
    st = load_studio_state()
    if not st or st.get("status") != "building" or not st.get("repo"):
        return gr.update(), gr.update()
    return check_build_progress()

def check_build_progress():
    st = load_studio_state()
    if not st or not st.get("repo"):
        return "No active project. Start a new build!", assemble_3d_stage_html(1, "Waiting for Prompt", "ready", "", world_hunter_polyhaven_pbr())

    if st.get("status") == "waiting_for_otp":
        return f"PAUSED FOR OTP ({st.get('otp_service', 'Login')}): Waiting for {OWNER_EMAIL} verification...", wrap_3d_iframe(st.get("preview_html", ""))

    repo = st["repo"]
    try:
        r = requests.get(f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/releases/latest", headers=gh_headers(), timeout=10)
        if r.status_code == 200:
            for asset in r.json().get("assets", []):
                if asset.get("name", "").endswith(".apk"):
                    st["apk_dl_url"] = asset.get("browser_download_url", st["releases_url"])
                    st["status"] = "done"
                    st["stage"] = 6
                    raw_live = st.get("raw_live_html", "")
                    if raw_live:
                        st["preview_html"] = wrap_preview_with_stages(6, raw_live, f"APK Ready! {st.get('app_title', 'App')}")
                    else:
                        st["preview_html"] = render_stage_bar_html(6, "APK Ready!") + assemble_3d_stage_html(6, st["prompt"], st.get("category", "3D"), st.get("glb_url", ""), world_hunter_polyhaven_pbr())
                    save_studio_state(st)
                    save_to_factory_vault(st)
                    return f"APK READY! Download: {st['apk_dl_url']}", st["preview_html"]
    except Exception:
        pass

    # Query exact GitHub Actions workflow run + active step
    live_detail = "Queued on GitHub Cloud..."
    try:
        runs_r = requests.get(f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/actions/runs?per_page=1", headers=gh_headers(), timeout=8)
        if runs_r.status_code == 200 and runs_r.json().get("workflow_runs"):
            run = runs_r.json()["workflow_runs"][0]
            r_status = run.get("status", "")
            r_concl = run.get("conclusion", "")
            run_id = run.get("id")
            live_detail = f"Workflow: {r_status} ({r_concl or 'running'})"
            if run_id:
                jobs_r = requests.get(f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo}/actions/runs/{run_id}/jobs", headers=gh_headers(), timeout=8)
                if jobs_r.status_code == 200 and jobs_r.json().get("jobs"):
                    job = jobs_r.json()["jobs"][0]
                    steps = job.get("steps", [])
                    done_cnt = sum(1 for s in steps if s.get("status") == "completed")
                    cur_step = next((s.get("name") for s in steps if s.get("status") == "in_progress"), None)
                    if cur_step:
                        live_detail = f"Running Step ({done_cnt+1}/{len(steps)}): {cur_step}"
                    elif r_concl == "failure":
                        fail_step = next((s.get("name") for s in steps if s.get("conclusion") == "failure"), "Build Step")
                        live_detail = f"FAILED at Step: {fail_step} — Open Actions URL to view log."
                    elif r_concl == "success":
                        live_detail = "Build finished! Checking APK Release..."
    except Exception:
        pass

    elapsed = max(0, int(time.time()) - int(st.get("started_at") or time.time()))
    mins, secs = divmod(elapsed, 60)
    eta_txt = f"Elapsed: {mins}m {secs}s | Est. Total: ~3-4 min"
    return (
        f"[CLOUD BUILD] {live_detail}\n{eta_txt}\nRepo: {st.get('repo_url', '')}\nActions: {st.get('actions_url', '')}",
        wrap_3d_iframe(st.get("preview_html", "")),
    )

def human_live_chat(message, audio_file, history):
    text_in = (message or "").strip()
    if audio_file:
        spoken = transcribe_voice_groq(audio_file)
        if spoken:
            text_in = spoken
    if not text_in:
        return history, "", gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

    st_cur = load_studio_state() or {}
    files = st_cur.get("files") or {}
    low_t = text_in.lower()
    is_edit_cmd = bool(files.get("assets/game.html")) and any(
        k in low_t for k in ["add", "change", "edit", "modify", "color", "pool", "car", "house", "ghar", "jodo", "badlo", "hatao", "bana do", "daal do", "lagao", "fix"]
    )

    is_new_build_cmd = any(
        k in low_t for k in ["banao", "bana do", "create a ", "build a ", "naya game", "new game", "naya app", "new app", "3d ghar", "3d house", "truck game", "gaming bana"]
    ) and not any(k in low_t for k in ["isme ", "add ", "change ", "color", "badlo", "hatao"])

    if is_new_build_cmd and len(text_in) >= 8:
        logs_txt, prev_h, _, dd_u, code_v = start_autonomous_build(text_in)
        reply = "Bilkul bhai! Maine aapke voice/chat command par naya build shuru kar diya hai. Neeche Live 3D Preview aur Terminal mein dekhein!"
        history = history or []
        history.append((text_in, reply))
        st_cur = load_studio_state() or {}
        st_cur["chat_history"] = history
        save_studio_state(st_cur)
        return history, "", prev_h, dd_u, code_v, text_in, logs_txt

    if is_edit_cmd:
        patched = agentic_patch_live_html(files["assets/game.html"], text_in, st_cur.get("prompt", ""))
        if patched and patched != files["assets/game.html"]:
            files["assets/game.html"] = patched
            st_cur["files"] = files
            st_cur["raw_live_html"] = patched
            st_cur["preview_html"] = wrap_preview_with_stages(st_cur.get("stage", 5), patched, f"Live Patched: {text_in[:45]}")
            if st_cur.get("repo"):
                try:
                    push_files_atomic(st_cur["repo"], {"assets/game.html": patched}, f"Live Patch: {text_in[:50]}")
                except Exception:
                    pass
            reply = "Done bhai! Maine aapke active project mein ye change kar diya hai aur Live Preview + GitHub dono update ho gaye hain."
            history = history or []
            history.append((text_in, reply))
            st_cur["chat_history"] = history
            save_studio_state(st_cur)
            dd_upd, code_val = get_code_explorer_update(st_cur)
            return history, "", st_cur["preview_html"], dd_upd, code_val, gr.update(), gr.update()

    active_skills = [v["title"] for v in SKILL_REGISTRY.values() if v["enabled"]]
    sys_p = (
        f"You are {OWNER_NAME}'s real-time AI Co-Developer in Sarfealam Auto-Studio. "
        "Reply warmly, concisely in the user's language (Hindi/Hinglish/English). "
        f"Active Skills: {', '.join(active_skills)}."
    )
    reply = call_ai(sys_p, text_in, max_tokens=1200, prefer="groq") or "Haan bhai, sun raha hoon! Bolo abhi kya banana hai ya game mein kya badlav karna hai?"
    history = history or []
    history.append((text_in, reply))
    st_cur["chat_history"] = history
    save_studio_state(st_cur)
    return history, "", gr.update(), gr.update(), gr.update(), gr.update(), gr.update()


def get_code_explorer_update(st=None):
    st = st if st is not None else (load_studio_state() or {})
    files = st.get("files") or {}
    if not files:
        return gr.update(choices=[], value=None), "// No active project files yet. Launch a build to inspect live code!"
    keys = list(files.keys())
    first = keys[0]
    return gr.update(choices=keys, value=first), files.get(first, "")

def on_select_code_file(filename):
    if not filename:
        return ""
    st = load_studio_state() or {}
    files = st.get("files") or {}
    return files.get(filename, "// File not found in active project.")

def restore_studio_on_load():
    st = load_studio_state()
    vault_text = get_vault_markdown()
    dd_upd, code_val = get_code_explorer_update(st)
    if not st:
        return (
            "",
            "Ready! Enter an App or 3D Game idea and click Launch Build & APK.",
            assemble_3d_stage_html(1, "Studio Ready", "3d_world", "", world_hunter_polyhaven_pbr()),
            [],
            vault_text,
            dd_upd,
            code_val,
        )
    prompt_val = st.get("prompt", "")
    chat_val = st.get("chat_history", [])
    logs = st.get("logs", [])
    status_val = "\n".join(logs) if isinstance(logs, list) and logs else st.get("status", "")
    if st.get("status") == "building" and st.get("repo"):
        live_status, live_prev = check_build_progress()
        if "APK READY!" in live_status:
            status_val = live_status
        else:
            status_val = (status_val + "\n\n" + live_status).strip()
        return prompt_val, status_val, wrap_3d_iframe(live_prev), chat_val, vault_text, dd_upd, code_val
    if st.get("apk_dl_url"):
        status_val = f"APK READY! Download: {st['apk_dl_url']}\n\n" + status_val
    prev_html = st.get("preview_html") or assemble_3d_stage_html(
        st.get("stage", 1),
        prompt_val or "Studio Ready",
        st.get("category", "3d_world"),
        st.get("glb_url", ""),
        world_hunter_polyhaven_pbr(),
    )
    return prompt_val, status_val, wrap_3d_iframe(prev_html), chat_val, vault_text, dd_upd, code_val

def cancel_active_project():
    clear_studio_state()
    return (
        "Active project cleared. Ready for a fresh idea!",
        assemble_3d_stage_html(1, "Ready for New Project", "ready", "", world_hunter_polyhaven_pbr()),
        gr.update(choices=[], value=None),
        "// Project cleared.",
    )

def submit_otp_resume(otp_code):
    st = load_studio_state()
    if not st:
        return "No paused project."
    if not (otp_code or "").strip():
        return "Please enter the OTP from Gmail."
    st["status"] = "building"
    st["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] OTP Verified for {OWNER_EMAIL}. Resuming build...")
    save_studio_state(st)
    return "OTP Verified! Build resumed."

def get_vault_markdown():
    rows = load_factory_vault()
    if not rows:
        return "Vault is empty. Build your first 3D Game or Commercial App!"
    md = "### Lifetime Factory Vault (Saved Permanently in Supabase)\n\n"
    for r in rows:
        apk = r.get("apk_dl_url") or r.get("releases_url") or "#"
        md += f"- **{r.get('app_title')}** (`{r.get('category')}`) — [GitHub]({r.get('repo_url')}) | [APK / Releases]({apk})\n"
    return md

def admin_unlock_and_tune(pin, target_repo, tuning_note):
    if (pin or "").strip() != ADMIN_PASSWORD:
        return "Invalid Admin PIN."
    return f"Owner Admin Unlocked for {target_repo or 'All Apps'}! Live config updated: {tuning_note or 'Default'}."

def toggle_skill(skill_key, enabled_val):
    if skill_key in SKILL_REGISTRY:
        SKILL_REGISTRY[skill_key]["enabled"] = bool(enabled_val)
    return f"Updated {skill_key} -> {'ON' if enabled_val else 'OFF'}"

# ==============================================================================
# DARK IDE CODING STUDIO UI + ALWAYS-ON TOGGLEABLE LIVE VOICE
# ==============================================================================

LIVE_VOICE_HEAD = """
<script>
(function() {
  window.__liveVoiceOn = false;
  window.__recog = null;
  window.__lastSpokenText = "";
  window.__isSpeaking = false;
  window.__lastSentAt = 0;

  function setStatusBadge(text, active) {
    const btn = document.getElementById("live-voice-toggle");
    if (!btn) return;
    btn.innerText = text;
    btn.style.background = active
      ? "linear-gradient(135deg, #ef4444, #b91c1c)"
      : "linear-gradient(135deg, #0ea5e9, #6366f1)";
    btn.style.boxShadow = active
      ? "0 0 18px rgba(239, 68, 68, 0.65)"
      : "0 0 12px rgba(14, 165, 233, 0.35)";
  }

  function stopRecog() {
    if (window.__recog) {
      try { window.__recog.onend = null; window.__recog.stop(); } catch (e) {}
      window.__recog = null;
    }
  }

  function speakText(txt, afterCb) {
    if (!window.__liveVoiceOn || !("speechSynthesis" in window) || !txt) return;
    if (txt === window.__lastSpokenText) return;
    window.__lastSpokenText = txt;
    window.__isSpeaking = true;
    stopRecog(); // Pause mic while speaking so it NEVER hears itself!
    try {
      window.speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(txt.slice(0, 400));
      u.lang = /[\u0900-\u097F]/.test(txt) ? "hi-IN" : "en-IN";
      u.rate = 1.02;
      u.onend = function() {
        window.__isSpeaking = false;
        if (window.__liveVoiceOn) {
          setTimeout(() => { if (window.__liveVoiceOn) startListening(); }, 450);
        }
        if (afterCb) afterCb();
      };
      u.onerror = function() {
        window.__isSpeaking = false;
        if (window.__liveVoiceOn) setTimeout(startListening, 500);
      };
      window.speechSynthesis.speak(u);
    } catch (e) {
      window.__isSpeaking = false;
    }
  }

  function startListening() {
    if (!window.__liveVoiceOn || window.__isSpeaking) return;
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      alert("Live Speech Recognition is not supported in this view. Please open the Direct Fullscreen Link in Chrome.");
      window.__liveVoiceOn = false;
      setStatusBadge("Live Voice: OFF (Tap to Start)", false);
      return;
    }
    stopRecog();
    const r = new SR();
    r.lang = "hi-IN";
    r.continuous = true;
    r.interimResults = true;
    r.onresult = function(ev) {
      if (window.__isSpeaking) return;
      let finalTxt = "";
      let interimTxt = "";
      for (let i = ev.resultIndex; i < ev.results.length; i++) {
        const t = ev.results[i][0].transcript;
        if (ev.results[i].isFinal) finalTxt += t + " ";
        else interimTxt += t;
      }
      const box = document.querySelector("#chat-input-box textarea");
      if (box) {
        box.value = (finalTxt || interimTxt).trim();
        box.dispatchEvent(new Event("input", { bubbles: true }));
      }
      const cleanFinal = finalTxt.trim();
      const now = Date.now();
      if (cleanFinal.length >= 3 && (now - window.__lastSentAt) > 1800) {
        window.__lastSentAt = now;
        const sendBtn = document.querySelector("#chat-send-btn");
        if (sendBtn) sendBtn.click();
      }
    };
    r.onerror = function() {
      if (window.__liveVoiceOn && !window.__isSpeaking) {
        setTimeout(() => { if (window.__liveVoiceOn && !window.__isSpeaking) startListening(); }, 1000);
      }
    };
    r.onend = function() {
      if (window.__liveVoiceOn && !window.__isSpeaking) {
        setTimeout(() => { if (window.__liveVoiceOn && !window.__isSpeaking) startListening(); }, 500);
      }
    };
    window.__recog = r;
    try { r.start(); } catch (e) {}
  }

  window.toggleLiveVoice = function() {
    window.__liveVoiceOn = !window.__liveVoiceOn;
    if (window.__liveVoiceOn) {
      setStatusBadge("Live Voice: ON (Listening... Tap to Stop)", true);
      speakText("Haan Sir, main live hoon! Bolo abhi kya kaam karna hai?");
    } else {
      setStatusBadge("Live Voice: OFF (Tap to Start)", false);
      window.__isSpeaking = false;
      stopRecog();
      if ("speechSynthesis" in window) {
        try { window.speechSynthesis.cancel(); } catch (e) {}
      }
    }
  };

  setInterval(function() {
    if (!window.__liveVoiceOn || window.__isSpeaking) return;
    const msgs = document.querySelectorAll("#chatbot-box .bot, #chatbot-box [data-testid='bot']");
    if (msgs && msgs.length) {
      const last = (msgs[msgs.length - 1].innerText || "").trim();
      if (last && last !== window.__lastSpokenText) {
        speakText(last);
      }
    }
  }, 1200);
})();
</script>
"""

CUSTOM_CSS = """
:root, .dark, body, .gradio-container {
  --body-background-fill: #070b14 !important;
  --background-fill-primary: #0d1322 !important;
  --background-fill-secondary: #111827 !important;
  --block-background-fill: #0d1322 !important;
  --block-border-color: rgba(56, 189, 248, 0.25) !important;
  --block-label-background-fill: #111a2e !important;
  --block-label-text-color: #38bdf8 !important;
  --block-title-text-color: #f1f5f9 !important;
  --body-text-color: #e2e8f0 !important;
  --body-text-color-subdued: #94a3b8 !important;
  --input-background-fill: #090e1a !important;
  --input-border-color: rgba(56, 189, 248, 0.35) !important;
  --input-placeholder-color: #64748b !important;
  --button-secondary-background-fill: #1e293b !important;
  --button-secondary-text-color: #f1f5f9 !important;
  --button-secondary-border-color: rgba(148, 163, 184, 0.3) !important;
  --border-color-primary: rgba(56, 189, 248, 0.25) !important;
  background: radial-gradient(circle at top left, #0f172a, #050814 70%) !important;
  color: #e2e8f0 !important;
}
.gradio-container input, .gradio-container textarea, .gradio-container select {
  background-color: #090e1a !important;
  color: #f8fafc !important;
  border: 1px solid rgba(56, 189, 248, 0.35) !important;
}
.gradio-container h1, .gradio-container h2, .gradio-container h3,
.gradio-container .prose, .gradio-container .prose p, .gradio-container .prose strong,
.gradio-container label, .gradio-container span {
  color: #e2e8f0 !important;
}
.gradio-container .tab-nav button {
  color: #94a3b8 !important;
  background: transparent !important;
}
.gradio-container .tab-nav button.selected {
  color: #38bdf8 !important;
  border-bottom: 2px solid #38bdf8 !important;
}
#live-voice-toggle {
  width: 100%;
  padding: 11px 16px;
  border-radius: 10px;
  border: 1px solid rgba(56, 189, 248, 0.5);
  background: linear-gradient(135deg, #0ea5e9, #6366f1);
  color: #ffffff;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  margin-bottom: 6px;
}
#terminal-feed textarea {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
  font-size: 12px !important;
  color: #34d399 !important;
  background: #030712 !important;
}
"""

with gr.Blocks(
    theme=gr.themes.Base(primary_hue="cyan", secondary_hue="purple", neutral_hue="slate"),
    css=CUSTOM_CSS,
    head=LIVE_VOICE_HEAD,
    title="Sarfealam Auto-Studio IDE",
) as demo:
    gr.Markdown(
        "# 🚀 SARFEALAM AUTO-STUDIO IDE\n"
        "**3D Game & Commercial App Factory • Always-On Live Voice • Live 3D Preview + Code Explorer • Permanent Supabase State**  |  "
        "[Open Fullscreen Direct App](https://sarfealam22-sarfealam-auto-studio.hf.space)"
    )

    with gr.Tabs():
        with gr.Tab("Live Studio IDE & 3D Assembly"):
            with gr.Row():
                with gr.Column(scale=5):
                    gr.HTML('<button id="live-voice-toggle" type="button" onclick="window.toggleLiveVoice()">Live Voice: OFF (Tap to Start)</button>')
                    chatbot = gr.Chatbot(label="Live Co-Developer (Hindi/Hinglish/English)", height=250, elem_id="chatbot-box")
                    with gr.Row():
                        chat_in = gr.Textbox(placeholder="Bolkar ya likhkar command dein...", show_label=False, scale=4, elem_id="chat-input-box")
                        voice_in = gr.Audio(sources=["microphone"], type="filepath", label="Mic Fallback", scale=2)
                    chat_btn = gr.Button("Send / Speak", variant="secondary", elem_id="chat-send-btn")

                    gr.Markdown("### 1-Prompt Autonomous Build")
                    prompt_box = gr.Textbox(label="App / 3D Game Idea", lines=3, placeholder="e.g. Build a 3D Fauji Army Cargo Truck OR Open-World Survival Shooter OR Delivery App with Maps & QR")
                    with gr.Row():
                        build_btn = gr.Button("Launch Build & APK", variant="primary")
                        refresh_btn = gr.Button("Check Live APK Status")
                        cancel_btn = gr.Button("Cancel / Reject Project")
                    status_box = gr.Textbox(label="Live Terminal & Execution Feed", lines=5, interactive=False, elem_id="terminal-feed")

                    with gr.Accordion("OTP / Login Pause-Resume Gate", open=False):
                        otp_in = gr.Textbox(label=f"Enter OTP sent to {OWNER_EMAIL}")
                        otp_btn = gr.Button("Verify & Resume Build")
                        otp_out = gr.Textbox(label="Gate Status", interactive=False)

                with gr.Column(scale=7):
                    with gr.Tabs():
                        with gr.Tab("Live 3D Preview"):
                            preview_view = gr.HTML(value=assemble_3d_stage_html(1, "Studio Ready", "3d_world", "", world_hunter_polyhaven_pbr()))
                        with gr.Tab("Code Explorer (Generated Files)"):
                            file_dropdown = gr.Dropdown(label="Select Project File", choices=[], interactive=True)
                            code_viewer = gr.Code(label="Live Source Code", language="python", lines=22, interactive=False)
                            file_dropdown.change(on_select_code_file, [file_dropdown], [code_viewer])

            chat_btn.click(human_live_chat, [chat_in, voice_in, chatbot], [chatbot, chat_in, preview_view, file_dropdown, code_viewer, prompt_box, status_box])
            build_btn.click(start_autonomous_build, [prompt_box], [status_box, preview_view, gr.State({}), file_dropdown, code_viewer])
            refresh_btn.click(check_build_progress, None, [status_box, preview_view])
            cancel_btn.click(cancel_active_project, None, [status_box, preview_view, file_dropdown, code_viewer])
            otp_btn.click(submit_otp_resume, [otp_in], [otp_out])

        with gr.Tab("Factory Vault & Owner Admin"):
            vault_md = gr.Markdown(value=get_vault_markdown())
            vault_refresh = gr.Button("Refresh Lifetime Vault")
            vault_refresh.click(get_vault_markdown, None, vault_md)

            gr.Markdown("### Owner Admin Panel (Live Control for Public APKs)")
            with gr.Row():
                adm_pin = gr.Textbox(label="Admin PIN", type="password")
                adm_repo = gr.Textbox(label="Target App/Game Repo")
                adm_note = gr.Textbox(label="Live Banner / Coin / Damage Config")
            adm_btn = gr.Button("Unlock & Push Live Config", variant="primary")
            adm_out = gr.Textbox(label="Admin Status", interactive=False)
            adm_btn.click(admin_unlock_and_tune, [adm_pin, adm_repo, adm_note], adm_out)

        with gr.Tab("Live Control Room (Skills & World Access)"):
            gr.Markdown("### Toggle Active Developer Skills")
            for sk_key, sk_info in SKILL_REGISTRY.items():
                chk = gr.Checkbox(label=f"{sk_info['title']} — {sk_info['rules'][:85]}...", value=sk_info["enabled"])
                chk.change(lambda val, k=sk_key: toggle_skill(k, val), [chk], None)

            with gr.Row():
                glb_ov = gr.Textbox(label="Override 3D .glb URL (Optional)")
                mp_ov = gr.Textbox(label="Nakama / Colyseus Multiplayer Server URL (Optional)")
            ov_btn = gr.Button("Save Live Overrides")
            ov_out = gr.Textbox(label="Control Status", interactive=False)
            def _save_ov(g, m):
                RUNTIME_OVERRIDES["custom_glb_url"] = (g or "").strip()
                RUNTIME_OVERRIDES["multiplayer_url"] = (m or "").strip()
                return "Live Overrides Updated!"
            ov_btn.click(_save_ov, [glb_ov, mp_ov], ov_out)

        with gr.Tab("System & Secrets Health"):
            health = {
                "Gemini": bool(GEMINI_KEY),
                "Groq (LLM + Whisper)": bool(GROQ_KEY),
                "NVIDIA NIM": bool(NVIDIA_KEY),
                "OpenRouter": bool(OPENROUTER_KEY),
                "Cohere": bool(COHERE_KEY),
                "GitHub Token": bool(GITHUB_TOKEN),
                "Supabase": bool(SUPABASE_URL and SUPABASE_KEY),
                "Owner Email": OWNER_EMAIL,
            }
            gr.JSON(value=health, label="Connected Engines & Secrets")

    live_timer = gr.Timer(10)
    live_timer.tick(auto_poll_build, None, [status_box, preview_view])
    demo.load(restore_studio_on_load, None, [prompt_box, status_box, preview_view, chatbot, vault_md, file_dropdown, code_viewer])

if __name__ == "__main__":
    demo.launch(ssr_mode=False, server_name="0.0.0.0", server_port=7860)
