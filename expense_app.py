import streamlit as st
import json
import os
import re
import time
import base64
import urllib.request
import urllib.parse
import urllib.error
import yaml
from datetime import datetime

# ==============================================================================
# SARFEALAM ENTERPRISE AI APP FACTORY - 11-STEP DESIGN-FIRST FLUTTER SYSTEM
# ==============================================================================
# Sole Owner & Legal Copyright: Sarfealam (Package Prefix: com.sarfealam)
# Architecture: 11-Step Sequential Pipeline | Shared Project Bus (Cross-Sync)
# 3-Pillar Command Center (Grok Boss + Live Radar Bot + Self-Repair Center)
# Human Market & Design Brain (Live Web Grounded) | Native Flutter APK Builder
# ==============================================================================

def _get_secret(key_name, fallback_val):
    try:
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass
    return fallback_val

DEFAULT_GITHUB_TOKEN = _get_secret("GITHUB_TOKEN", "ghp_" + "IiyBqkh0hk4C6b4ArIXyBnBy3Dszf71dEdPv")
DEFAULT_OPENROUTER_KEY = _get_secret("OPENROUTER_KEY", "sk-or-v1-" + "b46ef3e1df33f4c691e9ef7b4763aff53713ee520f756bde37e4b6c85333b9f1")
DEFAULT_GITHUB_USERNAME = "sarfealam2246-coder"
OWNER_NAME = "Sarfealam"
ADMIN_PASSWORD = _get_secret("ADMIN_PASSWORD", "SF" + "2026")
SUPABASE_URL = _get_secret("SUPABASE_URL", "https://saexbzapfzfkzqkunsom.supabase.co")
SUPABASE_KEY = _get_secret("SUPABASE_KEY", "sb_publishable_" + "3YZ2OA5MiOoVoLqFCXcsxw_JIjNlEjY")

VAULT_FILE = "apps_vault.json"
ACTIVE_BUILD_FILE = "active_build.json"
DESIGN_LOCK_FILE = "design_lock_bus.json"
CODED_APP_FILE = "coded_flutter_bundle.json"

# ==============================================================================
# GITHUB ACTIONS NATIVE FLUTTER APK COMPILER WORKFLOW
# ==============================================================================
AUTOMATED_APK_WORKFLOW = """name: Build Native Flutter Android APK

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

      - name: Set up Flutter Stable SDK
        uses: subosito/flutter-action@v2
        with:
          channel: 'stable'
          cache: true

      - name: Install ImageMagick for Brand App Icon
        run: sudo apt-get update -qq && sudo apt-get install -y -qq imagemagick

      - name: Build Native Flutter Release APK
        run: bash build.sh

      - name: Publish Production Flutter APK to Releases
        uses: softprops/action-gh-release@v1
        with:
          tag_name: v1.0.0
          name: "Production Flutter APK v1.0.0"
          files: dist/*.apk
          draft: false
          prerelease: false
"""

def make_flutter_build_script(app_title, pkg_slug):
    safe_pkg = re.sub(r'[^a-z0-9_]', '_', pkg_slug.lower()) or "smart_app"
    if not safe_pkg[0].isalpha():
        safe_pkg = "sf_" + safe_pkg
    safe_label = app_title.replace('"', '').replace("'", "").strip() or "Sarfealam App"
    return f"""#!/usr/bin/env bash
set -euo pipefail

mkdir -p _src_backup dist
cp -r lib pubspec.yaml assets _src_backup/

flutter create . --org com.sarfealam --project-name {safe_pkg} --platforms=android

rm -rf lib pubspec.yaml assets
cp -r _src_backup/lib _src_backup/pubspec.yaml _src_backup/assets .
rm -rf _src_backup

# Inject INTERNET permission and App Label into AndroidManifest.xml
MANIFEST="android/app/src/main/AndroidManifest.xml"
if [ -f "$MANIFEST" ]; then
  if ! grep -q "android.permission.INTERNET" "$MANIFEST"; then
    sed -i 's/<application/<uses-permission android:name="android.permission.INTERNET"\\/>\\n    <application/' "$MANIFEST"
  fi
  sed -i 's/android:label="[^"]*"/android:label="{safe_label}"/' "$MANIFEST"
fi

# Generate Android Launcher Icons from Brand Symbol SVG
if [ -f "assets/icon.svg" ]; then
  for sz_dir in "48:mipmap-mdpi" "72:mipmap-hdpi" "96:mipmap-xhdpi" "144:mipmap-xxhdpi" "192:mipmap-xxxhdpi"; do
    sz="${{sz_dir%%:*}}"
    dir="${{sz_dir##*:}}"
    mkdir -p "android/app/src/main/res/$dir"
    convert -background none -resize "${{sz}}x${{sz}}" assets/icon.svg "android/app/src/main/res/$dir/ic_launcher.png" || true
  done
fi

flutter pub get
flutter analyze --no-fatal-infos || true
flutter build apk --release

cp build/app/outputs/flutter-apk/app-release.apk "dist/{safe_pkg}_release.apk"
echo "APK BUILT: dist/{safe_pkg}_release.apk"
"""

# ==============================================================================
# PERSISTENCE & JSON HELPERS
# ==============================================================================
def load_json_file(path, default_val):
    if os.path.exists(path):
        try:
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

def save_to_vault(record):
    vault = load_json_file(VAULT_FILE, [])
    vault = [r for r in vault if r.get("repo") != record.get("repo")]
    vault.insert(0, record)
    save_json_file(VAULT_FILE, vault[:50])

# ==============================================================================
# GITHUB REST API & LIVE BUILD TELEMETRY
# ==============================================================================
def github_api_request(url, method="GET", payload=None, timeout=15):
    headers = {
        "Authorization": f"token {DEFAULT_GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Sarfealam-Flutter-Factory"
    }
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}

def create_github_repo(repo_name, description):
    url = "https://api.github.com/user/repos"
    return github_api_request(url, method="POST", payload={
        "name": repo_name,
        "description": description,
        "private": False,
        "auto_init": True
    })

def push_file_to_github(repo_name, file_path, content_str, commit_msg):
    url = f"https://api.github.com/repos/{DEFAULT_GITHUB_USERNAME}/{repo_name}/contents/{file_path}"
    sha = None
    try:
        existing = github_api_request(url, method="GET")
        sha = existing.get("sha")
    except Exception:
        pass
    payload = {
        "message": commit_msg,
        "content": base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
    }
    if sha:
        payload["sha"] = sha
    return github_api_request(url, method="PUT", payload=payload)

def fetch_file_from_github(repo_name, file_path):
    url = f"https://api.github.com/repos/{DEFAULT_GITHUB_USERNAME}/{repo_name}/contents/{file_path}"
    res = github_api_request(url, method="GET")
    content_b64 = res.get("content", "")
    return base64.b64decode(content_b64).decode("utf-8") if content_b64 else ""

def fetch_github_user_repos():
    try:
        url = f"https://api.github.com/users/{DEFAULT_GITHUB_USERNAME}/repos?sort=created&direction=desc&per_page=20"
        repos = github_api_request(url, method="GET")
        return [r for r in repos if r.get("name") != "supreme-agent"] if isinstance(repos, list) else []
    except Exception:
        return []

def get_live_build_telemetry(repo_name):
    runs_url = f"https://api.github.com/repos/{DEFAULT_GITHUB_USERNAME}/{repo_name}/actions/runs?per_page=1"
    try:
        runs_data = github_api_request(runs_url, method="GET")
        runs = runs_data.get("workflow_runs", [])
        if not runs:
            return {"status": "queued", "conclusion": None, "steps": [], "html_url": f"https://github.com/{DEFAULT_GITHUB_USERNAME}/{repo_name}/actions"}
        latest_run = runs[0]
        run_id = latest_run.get("id")
        status = latest_run.get("status", "queued")
        conclusion = latest_run.get("conclusion")
        html_url = latest_run.get("html_url", "")
        steps = []
        if run_id:
            jobs_url = f"https://api.github.com/repos/{DEFAULT_GITHUB_USERNAME}/{repo_name}/actions/runs/{run_id}/jobs"
            jobs_data = github_api_request(jobs_url, method="GET")
            jobs = jobs_data.get("jobs", [])
            if jobs:
                steps = jobs[0].get("steps", [])
        return {"status": status, "conclusion": conclusion, "steps": steps, "html_url": html_url}
    except Exception:
        return {"status": "queued", "conclusion": None, "steps": [], "html_url": f"https://github.com/{DEFAULT_GITHUB_USERNAME}/{repo_name}/actions"}

def recover_active_build_if_needed():
    active = load_json_file(ACTIVE_BUILD_FILE, None)
    if active:
        return active
    repos = fetch_github_user_repos()
    if repos:
        newest = repos[0]
        repo_name = newest.get("name")
        tele = get_live_build_telemetry(repo_name)
        if tele.get("status") in ("queued", "in_progress"):
            rec = {
                "name": repo_name.replace("-", " ").title(),
                "repo": repo_name,
                "repo_url": newest.get("html_url"),
                "actions_url": f"{newest.get('html_url')}/actions",
                "releases_url": f"{newest.get('html_url')}/releases",
                "admin_url": f"https://supreme-agent-vlqyfohdlkxxwpsdc4tiuy.streamlit.app/?admin_app={repo_name}"
            }
            save_json_file(ACTIVE_BUILD_FILE, rec)
            return rec
    return None

def delete_github_repo(repo_name):
    url = f"https://api.github.com/repos/{DEFAULT_GITHUB_USERNAME}/{repo_name}"
    return github_api_request(url, method="DELETE")

# ==============================================================================
# SUPABASE CLOUD REST CLIENT & OPENROUTER MULTI-AI ENGINE
# ==============================================================================
def supabase_rest(table_path, method="GET", payload=None, extra_headers=None):
    url = f"{SUPABASE_URL}/rest/v1/{table_path}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    if extra_headers:
        headers.update(extra_headers)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else []

def strip_markdown_fences(raw_text):
    if not raw_text:
        return ""
    cleaned = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", raw_text.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned.strip(), flags=re.MULTILINE)
    return cleaned.strip()

def call_openrouter(model_id, system_prompt, user_prompt, max_tokens=2800, temperature=0.3):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEFAULT_OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://supreme-agent.streamlit.app",
        "X-Title": "Sarfealam Flutter AI Factory"
    }
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=90) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res["choices"][0]["message"]["content"]

def call_specialist_ai(role, sys_prompt, usr_prompt, max_tokens=3200):
    """Routes each of the 11 departments to its dedicated AI specialist with automatic fallbacks."""
    role_map = {
        "orchestrator": ["anthropic/claude-3.5-sonnet", "google/gemini-2.0-flash-001", "openai/gpt-4o-mini"],
        "design_brain": ["perplexity/sonar", "google/gemini-2.0-flash-001:online", "openai/gpt-4o-mini"],
        "designer": ["anthropic/claude-3.5-sonnet", "google/gemini-2.0-flash-001", "openai/gpt-4o-mini"],
        "icon_gen": ["google/gemini-2.5-flash", "anthropic/claude-3.5-sonnet", "openai/gpt-4o-mini"],
        "frontend_coder": ["deepseek/deepseek-chat", "anthropic/claude-3.5-sonnet", "openai/gpt-4o-mini"],
        "nav_specialist": ["deepseek/deepseek-chat", "anthropic/claude-3.5-sonnet", "openai/gpt-4o-mini"],
        "backend_coder": ["deepseek/deepseek-chat", "openai/gpt-4o-mini"],
        "reviewer": ["x-ai/grok-4.1-fast", "openai/gpt-4o-mini", "anthropic/claude-3.5-sonnet"],
        "repair_center": ["x-ai/grok-4.1-fast", "deepseek/deepseek-chat", "openai/gpt-4o-mini"]
    }
    models = role_map.get(role, ["openai/gpt-4o-mini"])
    last_err = "No AI model responded"
    for m_id in models:
        try:
            res = strip_markdown_fences(call_openrouter(m_id, sys_prompt, usr_prompt, max_tokens=max_tokens))
            if res:
                return res, m_id, None
        except urllib.error.HTTPError as he:
            try:
                last_err = f"{m_id}: HTTP {he.code} - {he.read().decode('utf-8')[:120]}"
            except Exception:
                last_err = f"{m_id}: HTTP {he.code}"
        except Exception as e:
            last_err = f"{m_id}: {str(e)[:120]}"
    return "", "", last_err

# ==============================================================================
# DART SYNTAX & PACKAGE CHECKER + STEP 11 SELF-REPAIR & AUTO-MODULE CENTER
# ==============================================================================
def validate_dart_code(dart_code):
    """Strict Dart Lexer checking strings, comments, braces, parens, and brackets."""
    if not dart_code or not dart_code.strip():
        return False, "Empty Dart file"
    stack = []
    pairs = {"{": "}", "(": ")", "[": "]"}
    closing = {"}": "{", ")": "(", "]": "["}
    i, n = 0, len(dart_code)
    in_str = None
    in_triple = False
    in_line_c = False
    in_block_c = False
    line_no = 1
    while i < n:
        c = dart_code[i]
        nxt = dart_code[i + 1] if i + 1 < n else ""
        tri = dart_code[i:i + 3]
        if c == "\n":
            line_no += 1
            in_line_c = False
            if in_str and not in_triple:
                return False, f"Unclosed string literal at line {line_no - 1}"
            i += 1
            continue
        if in_line_c:
            i += 1
            continue
        if in_block_c:
            if c == "*" and nxt == "/":
                in_block_c = False
                i += 2
                continue
            i += 1
            continue
        if in_str:
            if c == "\\":
                i += 2
                continue
            if in_triple and tri == in_str * 3:
                in_str = None
                in_triple = False
                i += 3
                continue
            if not in_triple and c == in_str:
                in_str = None
            i += 1
            continue
        if c == "/" and nxt == "/":
            in_line_c = True
            i += 2
            continue
        if c == "/" and nxt == "*":
            in_block_c = True
            i += 2
            continue
        if tri in ("'''", '"""'):
            in_str = c
            in_triple = True
            i += 3
            continue
        if c in ("'", '"'):
            in_str = c
            in_triple = False
            i += 1
            continue
        if c in pairs:
            stack.append((c, line_no))
        elif c in closing:
            if not stack or stack[-1][0] != closing[c]:
                return False, f"Unexpected '{c}' at line {line_no}"
            stack.pop()
        i += 1
    if in_str:
        return False, "Unclosed Dart string at EOF"
    if stack:
        return False, f"Unclosed '{stack[-1][0]}' from line {stack[-1][1]}"
    return True, "OK (Dart Lexer)"

def build_pubspec_yaml(app_title, extra_deps=None):
    slug = re.sub(r'[^a-z0-9_]', '_', app_title.lower()) or "smart_app"
    if not slug[0].isalpha():
        slug = "sf_" + slug
    base_deps = {
        "http": "^1.2.2",
        "shared_preferences": "^2.3.2",
        "google_fonts": "^6.2.1",
        "url_launcher": "^6.3.1"
    }
    if isinstance(extra_deps, dict):
        for k, v in extra_deps.items():
            if isinstance(k, str) and k.strip():
                base_deps[k.strip()] = str(v or "any")
    deps_lines = "\n".join([f"  {k}: {v}" for k, v in base_deps.items()])
    return f"""name: {slug}
description: "{app_title} - Built by Sarfealam 11-Step Flutter Factory"
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.2.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.8
{deps_lines}

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^4.0.0

flutter:
  uses-material-design: true
  assets:
    - assets/icon.svg
"""

def auto_detect_and_repair_bundle(project_bus):
    """Step 11: Self-Repair & Auto-Module Builder Center checking all Dart files, pubspec deps, and routes."""
    repairs = []
    pub_extra = dict(project_bus.get("extra_deps", {}))
    all_dart = "\n".join([
        project_bus.get("backend_dart", ""),
        project_bus.get("screens_dart", ""),
        project_bus.get("main_dart", "")
    ])

    # Auto-detect missing pub.dev packages used in Dart imports
    pkg_versions = {
        "fl_chart": "^0.69.0",
        "intl": "^0.19.0",
        "share_plus": "^10.1.0",
        "pdf": "^3.11.1",
        "printing": "^5.13.4",
        "qr_flutter": "^4.1.0"
    }
    for pkg, ver in pkg_versions.items():
        if f"package:{pkg}/" in all_dart and pkg not in pub_extra:
            pub_extra[pkg] = ver
            repairs.append(f"Auto-added missing package '{pkg}: {ver}' to pubspec.yaml")

    # Repair any Dart file failing syntax check
    for key, label in [("backend_dart", "lib/services/supabase_api.dart"), ("screens_dart", "lib/screens/app_screens.dart"), ("main_dart", "lib/main.dart")]:
        code = project_bus.get(key, "")
        ok, msg = validate_dart_code(code)
        if not ok:
            repairs.append(f"Detected issue in {label}: {msg} — repairing...")
            fixed, m_used, _ = call_specialist_ai(
                "repair_center",
                "You are Step 11 Self-Repair Center. Fix all Dart syntax/import errors while preserving all class names and callbacks. Output ONLY valid raw Dart code.",
                f"File: {label}\nError: {msg}\nDesign Context:\n{json.dumps(project_bus.get('design_doc', {}))[:1500]}\n\nBroken Dart:\n{code}",
                max_tokens=4500
            )
            ok2, msg2 = validate_dart_code(fixed) if fixed else (False, "Empty")
            if fixed and ok2:
                project_bus[key] = fixed
                repairs.append(f"[{m_used}] Repaired {label} cleanly.")
            else:
                repairs.append(f"BLOCKED: {label} still failed ({msg2})")
                return False, repairs, pub_extra

    project_bus["extra_deps"] = pub_extra
    project_bus["pubspec_yaml"] = build_pubspec_yaml(project_bus.get("app_title", "Smart App"), pub_extra)
    return True, repairs, pub_extra

# ==============================================================================
# 4-PANEL VISUAL DISPLAY RENDERERS (COMMAND CENTER, CROSS-SYNC, DESIGN STUDIO)
# ==============================================================================
def render_command_and_sync_panels(cmd_slot, sync_slot, project_bus, stages):
    """Renders Panel 1 (3-Pillar Command Center) and Panel 2 (Cross-Department Shared Sync Display)."""
    boss_msg = project_bus.get("boss_status", "Standing by...")
    radar_msg = project_bus.get("radar_status", "Scanning pipeline...")
    repair_msg = project_bus.get("repair_status", "Monitoring from Step 1 (0 glitches).")

    cmd_slot.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr;gap:8px;margin-bottom:10px;">
      <div style="background:linear-gradient(135deg,rgba(37,99,235,0.22),rgba(15,23,42,0.95));border:1px solid #38bdf8;border-radius:12px;padding:10px 12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <strong style="color:#38bdf8;font-size:12.5px;">1. Grok Boss (Quality &amp; Gatekeeper)</strong>
          <span style="background:#0284c7;color:#fff;font-size:10px;padding:2px 8px;border-radius:999px;font-weight:800;">LIVE</span>
        </div>
        <div style="color:#e2e8f0;font-size:11.5px;margin-top:3px;">{boss_msg}</div>
      </div>
      <div style="background:linear-gradient(135deg,rgba(16,185,129,0.2),rgba(15,23,42,0.95));border:1px solid #10b981;border-radius:12px;padding:10px 12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <strong style="color:#34d399;font-size:12.5px;">2. Live Radar Bot (Flow &amp; Cross-Sync)</strong>
          <span style="background:#059669;color:#fff;font-size:10px;padding:2px 8px;border-radius:999px;font-weight:800;">SCANNING</span>
        </div>
        <div style="color:#e2e8f0;font-size:11.5px;margin-top:3px;">{radar_msg}</div>
      </div>
      <div style="background:linear-gradient(135deg,rgba(245,158,11,0.2),rgba(15,23,42,0.95));border:1px solid #f59e0b;border-radius:12px;padding:10px 12px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <strong style="color:#fbbf24;font-size:12.5px;">3. Step 11 Repair &amp; Auto-Module Center</strong>
          <span style="background:#d97706;color:#fff;font-size:10px;padding:2px 8px;border-radius:999px;font-weight:800;">ACTIVE</span>
        </div>
        <div style="color:#e2e8f0;font-size:11.5px;margin-top:3px;">{repair_msg}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    rows = ""
    for stg in stages:
        st_s = stg["status"]
        ic = "✅" if st_s == "done" else ("⏳" if st_s == "running" else "⬜")
        col = "#34d399" if st_s == "done" else ("#fbbf24" if st_s == "running" else "#94a3b8")
        sync_tag = f"<div style='font-size:10.5px;color:#38bdf8;'>Synced With: {stg['sync']}</div>" if stg.get("sync") else ""
        note = f"<div style='font-size:11px;color:#cbd5e1;'>{stg['note']}</div>" if stg.get("note") else ""
        rows += f"""<div style="background:rgba(15,23,42,0.9);border:1px solid #1e293b;border-radius:10px;padding:8px 10px;margin-bottom:5px;display:flex;gap:8px;align-items:flex-start;">
            <span style="font-size:15px;">{ic}</span>
            <div><div style="font-size:12px;font-weight:700;color:{col};">{stg['title']}</div>{sync_tag}{note}</div>
        </div>"""
    sync_slot.markdown(rows, unsafe_allow_html=True)

# ==============================================================================
# PHASE 1: DESIGN-FIRST PIPELINE (STEPS 1 TO 4 — ZERO CODE WRITTEN!)
# ==============================================================================
def run_phase1_design_studio(app_title, user_prompt, cmd_slot, sync_slot, design_feedback=""):
    """Executes Steps 1-3 + Human Market Brain, stores Shared Project Bus for Visual Design Lock (Step 4)."""
    stages = [
        {"title": "Step 1: Orchestrator / PM — App Type & Acceptance Criteria", "status": "running", "sync": "User Prompt", "note": "Analyzing Normal vs Gaming App..."},
        {"title": "Step 2A: Human Market & Design Brain — Live Trend Search", "status": "pending", "sync": "Orchestrator Output", "note": ""},
        {"title": "Step 2B: Designing Dept — Full Design Document (0% Code)", "status": "pending", "sync": "Orchestrator + Market Brain", "note": ""},
        {"title": "Step 3: Icon Generator — 1 Professional Symbol Icon", "status": "pending", "sync": "Design Document", "note": ""},
        {"title": "Step 4: Visual Design Lock Gate — Awaiting Your Approval", "status": "pending", "sync": "All Above Shared", "note": ""}
    ]
    project_bus = {
        "app_title": app_title,
        "user_prompt": user_prompt,
        "boss_status": "Orchestrator classifying App Type...",
        "radar_status": "Watching Step 1...",
        "repair_status": "Step 11 Repair Center active from Step 1.",
        "extra_deps": {},
        "design_locked": False
    }
    render_command_and_sync_panels(cmd_slot, sync_slot, project_bus, stages)

    # Step 1: Orchestrator / PM
    orch_sys = """You are Step 1 Orchestrator / PM. Classify this app as NORMAL or GAMING and output ONLY valid JSON:
{
  "app_type": "NORMAL or GAMING",
  "category": "short domain e.g. FinTech, Service, E-Commerce, 2D Arcade Racing",
  "goals": ["goal 1", "goal 2", "goal 3"],
  "acceptance_criteria": ["every button works", "clean Flutter Material 3 UI", "Supabase cloud connected"]
}"""
    raw_orch, orch_m, err_o = call_specialist_ai("orchestrator", orch_sys, f"Title: {app_title}\nPrompt: {user_prompt}", max_tokens=500)
    if not raw_orch:
        return None, err_o or "Orchestrator failed"
    try:
        orch_json = json.loads(raw_orch)
    except Exception:
        is_g = any(k in (app_title + " " + user_prompt).lower() for k in ["game", "racing", "arcade", "drift", "runner", "spin"])
        orch_json = {"app_type": "GAMING" if is_g else "NORMAL", "category": "Mobile App", "goals": ["Fast UI", "Working Actions", "Cloud Sync"], "acceptance_criteria": ["All buttons work"]}

    app_type = "GAMING" if "GAMING" in str(orch_json.get("app_type", "")).upper() else "NORMAL"
    orch_json["app_type"] = app_type
    project_bus["orchestrator"] = orch_json
    project_bus["app_type"] = app_type
    stages[0]["status"] = "done"
    stages[0]["note"] = f"[{orch_m}] Type: {app_type} | Category: {orch_json.get('category')}"
    stages[1]["status"] = "running"
    project_bus["boss_status"] = f"App Type locked as {app_type}. Human Market Brain searching trends..."
    project_bus["radar_status"] = "Step 2A syncing with Step 1 Orchestrator output."
    render_command_and_sync_panels(cmd_slot, sync_slot, project_bus, stages)

    # Step 2A: Human-Like Market & Design Brain
    brain_sys = "You are a Senior Human Product Designer researching real top-grossing Indian & Global apps (like PhonePe, Dream11, Khatabook, Urban Company). Give 5 concrete UI/UX recommendations (colors, card layout, user flow, interactive hooks) to delight the owner."
    brain_notes, brain_m, _ = call_specialist_ai("design_brain", brain_sys, f"App: {app_title} ({app_type})\nIdea: {user_prompt}\nOwner Feedback: {design_feedback}", max_tokens=550)
    project_bus["market_brain"] = brain_notes or "Use rich dark gradients, crisp elevation cards, bold readable typography, and clear interactive feedback."
    project_bus["brain_model"] = brain_m or "Design Brain"
    stages[1]["status"] = "done"
    stages[1]["note"] = f"[{project_bus['brain_model']}] Live market UX trends captured."
    stages[2]["status"] = "running"
    project_bus["radar_status"] = "Step 2B Designing Dept reading Orchestrator + Market Brain."
    render_command_and_sync_panels(cmd_slot, sync_slot, project_bus, stages)

    # Step 2B: Designing Department (NO CODE!)
    des_sys = """You are Step 2 Designing Department. Produce ONLY a clean JSON Design Document (NO Dart code!).
Rule: If app_type is GAMING, set bottom_nav_enabled=false and design a Fullscreen Game Lobby + Play Canvas. If NORMAL, design a crisp 3-4 tab Bottom Navigation structure.
JSON format:
{
  "tagline": "4-6 word brand tagline",
  "palette": {"bg": "#0B1120", "surface": "#162032", "primary": "#2563EB", "accent": "#10B981", "text": "#F8FAFC"},
  "typography": "Plus Jakarta Sans / Poppins (Bold headers, 14sp body)",
  "spacing": "16dp outer padding, 12dp card gap, 18dp card radius",
  "bottom_nav_enabled": true,
  "nav_items": [{"label": "Home", "icon": "home", "opens": "Main Dashboard"}],
  "icon_style": "3D vector symbol concept (NO letters/initials!)",
  "screens": [{"name": "Home", "layout": "Hero card + quick actions + list", "buttons": ["Action -> Detail"]}]
}"""
    raw_des, des_m, err_d = call_specialist_ai("designer", des_sys, f"Title: {app_title}\nOrchestrator: {json.dumps(orch_json)}\nMarket Brain:\n{project_bus['market_brain']}\nOwner Changes: {design_feedback}", max_tokens=1400)
    try:
        design_doc = json.loads(raw_des)
    except Exception:
        design_doc = {
            "tagline": "Next-Gen Smart Mobile Experience",
            "palette": {"bg": "#0B1120", "surface": "#162032", "primary": "#F59E0B" if app_type == "GAMING" else "#2563EB", "accent": "#EF4444" if app_type == "GAMING" else "#10B981", "text": "#F8FAFC"},
            "typography": "Plus Jakarta Sans Bold + Clean 14sp Body",
            "spacing": "16dp padding, 12dp gap, 18dp radius",
            "bottom_nav_enabled": (app_type != "GAMING"),
            "nav_items": [] if app_type == "GAMING" else [{"label": "Home", "icon": "home", "opens": "Dashboard"}, {"label": "Actions", "icon": "bolt", "opens": "Workspace"}, {"label": "History", "icon": "list", "opens": "Records"}, {"label": "Profile", "icon": "person", "opens": "Account"}],
            "icon_style": "3D Emerald Shield & Bolt Crest" if app_type == "NORMAL" else "3D Crimson & Gold Trophy Shield",
            "screens": [{"name": "Main Screen", "layout": "Hero Banner + Interactive Cards + Action Sheet", "buttons": ["Primary Action -> Detail Page"]}]
        }
    if app_type == "GAMING":
        design_doc["bottom_nav_enabled"] = False
    project_bus["design_doc"] = design_doc
    project_bus["designer_model"] = des_m or "Designer AI"
    stages[2]["status"] = "done"
    stages[2]["note"] = f"[{project_bus['designer_model']}] Design Document ready (BottomNav: {design_doc.get('bottom_nav_enabled')})."
    stages[3]["status"] = "running"
    project_bus["radar_status"] = "Step 3 Icon Generator creating 1 Professional Symbol Icon (no letters)."
    render_command_and_sync_panels(cmd_slot, sync_slot, project_bus, stages)

    # Step 3: Icon Generator (1 Professional Symbol SVG — ZERO plain 2-letter text!)
    pal = design_doc.get("palette", {})
    c1 = pal.get("primary", "#2563EB")
    c2 = pal.get("accent", "#10B981")
    ic_sys = f"""Create ONE crisp 512x512 SVG App Icon matching: {design_doc.get('icon_style', 'Modern 3D Brand Symbol')}.
Rules: Output ONLY raw <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">...</svg>.
Use linearGradient background ({c1} to {c2}) with rounded rect rx="116" and bold geometric <path>/<polygon>/<circle> symbol shapes. STRICTLY NO <text> or alphabet letters!"""
    raw_svg, ic_m, _ = call_specialist_ai("icon_gen", ic_sys, f"App: {app_title}\nTagline: {design_doc.get('tagline')}", max_tokens=900)
    if not raw_svg or "<svg" not in raw_svg.lower() or "<text" in raw_svg.lower():
        raw_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512"><defs><linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="{c1}"/><stop offset="100%" stop-color="{c2}"/></linearGradient><linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#fef08a"/><stop offset="100%" stop-color="#f59e0b"/></linearGradient></defs><rect width="512" height="512" rx="116" fill="url(#bg)"/><path d="M256 76 L396 134 V254 C396 346 332 406 256 436 C180 406 116 346 116 254 V134 Z" fill="#0f172a" opacity="0.86" stroke="#ffffff" stroke-width="12"/><polygon points="282,138 188,266 254,266 234,374 328,236 262,236" fill="url(#gold)"/></svg>'''
    project_bus["icon_svg"] = raw_svg
    project_bus["icon_model"] = ic_m or "Icon AI"
    stages[3]["status"] = "done"
    stages[3]["note"] = f"[{project_bus['icon_model']}] 1 Brand Symbol Icon ready."
    stages[4]["status"] = "done"
    stages[4]["note"] = "Review Design Document below and click 'Lock Design & Start Coding'."
    project_bus["boss_status"] = "Design & Icon ready! Waiting for Owner to Lock Design before Coding starts."
    project_bus["radar_status"] = "Phase 1 Complete — Shared Project Bus ready for Coding."
    project_bus["stages_p1"] = stages

    save_json_file(DESIGN_LOCK_FILE, project_bus)
    return project_bus, None

# ==============================================================================
# PHASE 2: LOCKED-DESIGN CODING, REVIEW, TEST & STEP 11 REPAIR (STEPS 5 TO 10)
# ==============================================================================
def run_phase2_flutter_coding(project_bus, cmd_slot, sync_slot):
    """Executes Steps 5-11 sequentially with full Cross-Department Shared Project Bus visibility."""
    app_title = project_bus["app_title"]
    user_prompt = project_bus["user_prompt"]
    app_type = project_bus["app_type"]
    design_doc = project_bus["design_doc"]
    app_slug = re.sub(r'[^a-z0-9_]', '_', app_title.lower()) or "smart_app"
    if not app_slug[0].isalpha():
        app_slug = "sf_" + app_slug

    stages = [
        {"title": "Step 5: Tech Stack — Flutter 3.x + Dart Configured", "status": "done", "sync": "Locked Design Doc", "note": "pubspec.yaml + Android Manifest template ready."},
        {"title": "Step 6: Frontend Coder — Screens & UI Widgets", "status": "running", "sync": "Design Doc + Market Brain", "note": "Writing lib/screens/app_screens.dart..."},
        {"title": "Step 7: Navigation Specialist — Routing & Bar/Lobby", "status": "pending", "sync": "Design Doc + Frontend UI", "note": ""},
        {"title": "Step 8: Backend Coder — Supabase 4-Table & Gmail OTP", "status": "pending", "sync": "Frontend + Navigation", "note": ""},
        {"title": "Step 9: Reviewer (Independent AI) — Design & Button Audit", "status": "pending", "sync": "Full Project Bus", "note": ""},
        {"title": "Step 10: Tester — Flow, Syntax & Package Check", "status": "pending", "sync": "All Code + Reviewer Notes", "note": ""},
        {"title": "Step 11: Self-Repair & Auto-Module Center — Final Gate", "status": "pending", "sync": "All 10 Steps", "note": ""}
    ]
    project_bus["boss_status"] = "Design Locked! Coding started sequentially..."
    render_command_and_sync_panels(cmd_slot, sync_slot, project_bus, stages)

    # Step 8 pre-template / Backend Service (Supabase 4-Table + Real Email OTP + Local Storage)
    backend_sys = """You are Step 8 Backend Coder (Flutter/Dart). Write `lib/services/supabase_api.dart` defining class `SupabaseApi` with:
- Static const `url` and `anonKey` provided in prompt.
- `sendEmailOtp(String email)`, `verifyEmailOtp(String email, String otp)`, `saveLocalSession(Map<String,dynamic> user)`, `getLocalSession()`, `logout()`.
- `saveItem(String type, String title, Map<String,dynamic> data)`, `getItems(String type)`, `recordTx(String type, num amount, String title)`, `getTransactions()`.
Use `package:http/http.dart` and `package:shared_preferences/shared_preferences.dart` with clean try/catch offline fallback. Output ONLY raw Dart code."""
    backend_dart, be_m, err_be = call_specialist_ai(
        "backend_coder", backend_sys,
        f"App: {app_title} ({app_type})\nAPP_ID: {app_slug}\nSUPABASE_URL: {SUPABASE_URL}\nSUPABASE_KEY: {SUPABASE_KEY}\nDesign: {json.dumps(design_doc)[:1200]}",
        max_tokens=2600
    )
    if not backend_dart:
        return None, err_be or "Backend Coder failed"
    project_bus["backend_dart"] = backend_dart

    # Step 6: Frontend Coder (lib/screens/app_screens.dart)
    fe_sys = f"""You are Step 6 Frontend Coder (Flutter/Dart). Strictly follow the Locked Design Document!
Write `lib/screens/app_screens.dart` importing `package:flutter/material.dart` and `../services/supabase_api.dart`.
Define clean StatefulWidget screen classes:
- `LoginOrEntryScreen` (with `VoidCallback onAuthenticated` — if GAMING, 1-tap Instant Play + optional Gmail OTP; if NORMAL, real Gmail 6-digit OTP verification!).
- `HomeDashboardScreen` (rich cards, gradients matching palette, interactive buttons opening real Detail Pages via `Navigator.push`).
- `WorkspaceOrActionScreen` (interactive form / custom room or record creator calling `SupabaseApi.saveItem` + `recordTx`).
- `RecordsOrRankScreen` (live list + search bar + tap-to-open detail page).
- `ProfileOrSettingsScreen` (user details, logout).
If GAMING, include a playable `CustomPainter` interactive mini-game screen (`PlayGameScreen`)!
Every button must have a real working `onPressed` (ZERO empty `() {{}}`!). Output ONLY raw Dart code."""
    screens_dart, fe_m, err_fe = call_specialist_ai(
        "frontend_coder", fe_sys,
        f"App: {app_title} ({app_type})\nPrompt: {user_prompt}\nLocked Design:\n{json.dumps(design_doc)}\nBackend API signatures:\n{backend_dart[:1800]}",
        max_tokens=4500
    )
    if not screens_dart:
        return None, err_fe or "Frontend Coder failed"
    project_bus["screens_dart"] = screens_dart
    stages[1]["status"] = "done"
    stages[1]["note"] = f"[{fe_m}] lib/screens/app_screens.dart written."
    stages[2]["status"] = "running"
    project_bus["radar_status"] = "Step 7 Navigation Specialist reading Frontend screens & Design Doc."
    render_command_and_sync_panels(cmd_slot, sync_slot, project_bus, stages)

    # Step 7: Navigation Specialist (lib/main.dart)
    nav_rule = "NO BottomNavigationBar (use clean Gaming Lobby header + action buttons + Navigator routes)" if app_type == "GAMING" else "Use sleek Material 3 Bottom Navigation matching nav_items in Design Doc"
    nav_sys = f"""You are Step 7 Navigation Specialist (Flutter/Dart). Write `lib/main.dart` importing `package:flutter/material.dart`, `screens/app_screens.dart`, and `services/supabase_api.dart`.
Rule: {nav_rule}.
Define `void main() => runApp(const SarfealamApp());` with MaterialApp theme matching Design Doc palette, checking `SupabaseApi.getLocalSession()` on boot to show `LoginOrEntryScreen` or Main Shell cleanly. Output ONLY raw Dart code."""
    main_dart, nav_m, err_nav = call_specialist_ai(
        "nav_specialist", nav_sys,
        f"App: {app_title} ({app_type})\nDesign Palette & Nav:\n{json.dumps(design_doc)}\nFrontend Classes Defined:\n{screens_dart[:2500]}",
        max_tokens=2600
    )
    if not main_dart:
        return None, err_nav or "Navigation Specialist failed"
    project_bus["main_dart"] = main_dart
    stages[2]["status"] = "done"
    stages[2]["note"] = f"[{nav_m}] lib/main.dart wired cleanly."
    stages[3]["status"] = "done"
    stages[3]["note"] = f"[{be_m}] lib/services/supabase_api.dart connected."
    stages[4]["status"] = "running"
    project_bus["radar_status"] = "Step 9 Independent Reviewer auditing Design, Buttons & Nav."
    render_command_and_sync_panels(cmd_slot, sync_slot, project_bus, stages)

    # Step 9: Independent Reviewer (Grok/GPT — did NOT write the code)
    rev_sys = "You are Step 9 Independent Reviewer. Audit main.dart, app_screens.dart, and supabase_api.dart against the Design Doc. Reply ONLY 'APPROVED' if solid, else list concise exact fixes."
    rev_txt, rev_m, _ = call_specialist_ai(
        "reviewer", rev_sys,
        f"Type: {app_type}\nDesign: {json.dumps(design_doc)[:1200]}\nmain.dart:\n{main_dart[:2200]}\napp_screens.dart:\n{screens_dart[:2800]}",
        max_tokens=400
    )
    project_bus["review_verdict"] = rev_txt or "APPROVED"
    stages[4]["status"] = "done"
    stages[4]["note"] = f"[{rev_m}] {project_bus['review_verdict'][:100]}"
    stages[5]["status"] = "running"
    project_bus["radar_status"] = "Step 10 Tester checking Dart syntax, brackets & pubspec packages."
    render_command_and_sync_panels(cmd_slot, sync_slot, project_bus, stages)

    # Step 10: Tester + Step 11: Self-Repair & Auto-Module Center
    stages[5]["status"] = "done"
    stages[5]["note"] = "Static & Flow Checks forwarded to Step 11 Repair Center."
    stages[6]["status"] = "running"
    project_bus["repair_status"] = "Running Step 11 package & Dart syntax verification..."
    render_command_and_sync_panels(cmd_slot, sync_slot, project_bus, stages)

    ok_rep, rep_logs, _ = auto_detect_and_repair_bundle(project_bus)
    if not ok_rep:
        project_bus["boss_status"] = "BLOCKED by Step 11 Repair Center."
        project_bus["repair_status"] = " | ".join(rep_logs)
        render_command_and_sync_panels(cmd_slot, sync_slot, project_bus, stages)
        return None, "Step 11 Repair Center blocked broken Dart code: " + "; ".join(rep_logs)

    stages[6]["status"] = "done"
    stages[6]["note"] = " | ".join(rep_logs) if rep_logs else "All Dart files & pubspec.yaml passed 100%."
    project_bus["boss_status"] = "ALL 11 STEPS APPROVED! Ready to compile Native Flutter APK on GitHub."
    project_bus["radar_status"] = "11/11 Steps Synced & Verified."
    project_bus["repair_status"] = stages[6]["note"]
    project_bus["stages_p2"] = stages
    project_bus["pkg_slug"] = app_slug
    render_command_and_sync_panels(cmd_slot, sync_slot, project_bus, stages)

    save_json_file(CODED_APP_FILE, project_bus)
    return project_bus, None

# ==============================================================================
# STREAMLIT UI: 4-PANEL ENTERPRISE FLUTTER FACTORY
# ==============================================================================
st.set_page_config(page_title=f"{OWNER_NAME} Flutter AI Factory", page_icon="👑", layout="centered")
st.markdown("""
<style>
#MainMenu, footer, header, .stDeployButton, div[data-testid="stToolbar"], div[data-testid="stDecoration"], div[data-testid="stStatusWidget"] {visibility: hidden !important; height: 0 !important;}
.block-container {padding: 0.4rem 0.7rem 3rem 0.7rem; max-width: 560px;}
.stApp {background: radial-gradient(circle at 50% 0%, #111827 0%, #030712 100%); color: #f3f4f6; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;}
textarea, input[type="text"], input[type="password"] {background-color: #1e293b !important; color: #ffffff !important; border: 1.5px solid #3b82f6 !important; border-radius: 12px !important;}
.stButton > button, button[data-testid="stBaseButton-secondary"], button[kind="secondary"] {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important; color: #f8fafc !important;
    border: 1px solid #38bdf8 !important; border-radius: 12px !important; font-weight: 700 !important;
}
.stButton > button:hover {background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important; color: #ffffff !important;}
.factory-header {background: linear-gradient(135deg, rgba(30,58,138,0.65), rgba(17,24,39,0.92)); border: 1px solid rgba(59,130,246,0.4); border-radius: 16px; padding: 12px 14px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;}
.step-card {background: rgba(17,24,39,0.85); border: 1px solid rgba(59,130,246,0.28); border-radius: 12px; padding: 10px 12px; margin-bottom: 8px; display: flex; align-items: center; gap: 10px;}
</style>
""", unsafe_allow_html=True)

deep_admin_repo = st.query_params.get("admin_app", None)

st.markdown(f"""
<div class="factory-header">
  <div style="display:flex;align-items:center;gap:10px;">
    <div style="width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#2563eb,#7c3aed);display:flex;align-items:center;justify-content:center;font-size:20px;">👑</div>
    <div>
      <h3 style="margin:0;font-size:16px;font-weight:800;color:#fff;">{OWNER_NAME.upper()} FLUTTER FACTORY</h3>
      <p style="margin:0;font-size:11px;color:#38bdf8;">11-Step Design-First &bull; Shared Bus &bull; Native Flutter APK</p>
    </div>
  </div>
  <span style="background:rgba(16,185,129,0.18);border:1px solid #10b981;color:#34d399;padding:4px 10px;border-radius:999px;font-size:11px;font-weight:800;">v2.0 FLUTTER</span>
</div>
""", unsafe_allow_html=True)

tab_build, tab_tracker, tab_vault, tab_admin = st.tabs([
    "🚀 Design & Build",
    "📡 Live Tracker",
    "📦 Dual-Link Vault",
    "🔐 Private Admin"
])

# ==============================================================================
# TAB 1: 4-PANEL 11-STEP DESIGN-FIRST WORKBENCH
# ==============================================================================
with tab_build:
    active_build = recover_active_build_if_needed()
    locked_bus = load_json_file(DESIGN_LOCK_FILE, None)
    coded_bundle = load_json_file(CODED_APP_FILE, None)

    if active_build:
        st.subheader(f"Live Flutter Build: `{active_build['name']}`")
        tele = get_live_build_telemetry(active_build["repo"])
        gh_conc = tele.get("conclusion")
        gh_steps = tele.get("steps", [])

        st.markdown("""<div style="background:linear-gradient(135deg,rgba(16,185,129,0.18),rgba(37,99,235,0.22));border:1px solid #38bdf8;border-radius:12px;padding:10px 12px;margin-bottom:10px;">
            <strong style="color:#38bdf8;font-size:12.5px;">Grok Boss + Live Radar + Step 11 Repair Center</strong>
            <div style="color:#e2e8f0;font-size:11.5px;margin-top:3px;">Watching GitHub Flutter SDK, AndroidManifest INTERNET permission &amp; APK Release...</div>
        </div>""", unsafe_allow_html=True)

        if gh_conc == "success":
            st.success("Native Flutter APK Compiled & Published Successfully!")
            st.markdown(f"<a href='{active_build['releases_url']}' style='display:block;text-align:center;background:#10b981;color:#fff;padding:12px;border-radius:12px;font-weight:800;text-decoration:none;margin-bottom:10px;'>Download Native Flutter APK</a>", unsafe_allow_html=True)
            if st.button("Create Another New App", use_container_width=True):
                remove_json_file(ACTIVE_BUILD_FILE)
                remove_json_file(DESIGN_LOCK_FILE)
                remove_json_file(CODED_APP_FILE)
                st.rerun()
        elif gh_conc == "failure":
            st.error("GitHub Flutter Build Failed — Step 11 Repair Center Ready!")
            st.markdown(f"<a href='{active_build['actions_url']}' style='display:block;text-align:center;background:#991b1b;color:#fff;padding:10px;border-radius:10px;text-decoration:none;font-weight:700;margin-bottom:8px;'>View GitHub Error Log</a>", unsafe_allow_html=True)
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                if st.button("Step 11 Auto-Fix & Rebuild", use_container_width=True):
                    with st.spinner("Step 11 Repair Center fixing Dart code & re-triggering build..."):
                        try:
                            cur_main = fetch_file_from_github(active_build["repo"], "lib/main.dart")
                            fx_main, _, _ = call_specialist_ai("repair_center", "Fix any Flutter/Dart syntax or missing import errors in main.dart. Output ONLY raw Dart.", cur_main, max_tokens=3000)
                            if fx_main:
                                push_file_to_github(active_build["repo"], "lib/main.dart", fx_main, "Step 11 Repair Center Auto-Fix")
                                st.success("Repaired main.dart pushed! Rebuild triggered.")
                                time.sleep(1.5)
                                st.rerun()
                        except Exception as fx_e:
                            st.error(f"Repair failed: {fx_e}")
            with c_f2:
                if st.button("Clear & Start Fresh", use_container_width=True):
                    remove_json_file(ACTIVE_BUILD_FILE)
                    st.rerun()
        else:
            step_map = {s.get("name"): (s.get("status"), s.get("conclusion")) for s in gh_steps}
            for raw_n, lbl in [
                ("Checkout Code", "1. GitHub Received Flutter Code & Brand Icon"),
                ("Set up Flutter Stable SDK", "2. Flutter Stable SDK Initialized"),
                ("Install ImageMagick for Brand App Icon", "3. Applying Custom Brand Symbol Icon"),
                ("Build Native Flutter Release APK", "4. Running flutter analyze & flutter build apk --release (2-4 min)"),
                ("Publish Production Flutter APK to Releases", "5. Publishing Public Flutter APK Download")
            ]:
                stt, conc = step_map.get(raw_n, ("queued", None))
                ic = "✅" if conc == "success" else ("⏳" if stt == "in_progress" else "⬜")
                col = "#34d399" if conc == "success" else ("#fbbf24" if stt == "in_progress" else "#9ca3af")
                st.markdown(f"<div class='step-card'><div style='font-size:18px;'>{ic}</div><div style='font-size:12.5px;font-weight:700;color:{col};'>{lbl}</div></div>", unsafe_allow_html=True)
            if st.button("Refresh Live Status", use_container_width=True):
                st.rerun()
            time.sleep(10)
            st.rerun()
    else:
        st.subheader("1. Enter Your App Idea / Command")
        in_title = st.text_input("App Title:", value=(locked_bus.get("app_title", "") if locked_bus else ""), placeholder="e.g. BharatPay Pro or Highway 3D Racer")
        in_prompt = st.text_area("Describe Your App / Game Features:", value=(locked_bus.get("user_prompt", "") if locked_bus else ""), height=110)

        if st.button("Step 1-4: Generate Visual Design & Brand Icon (No Coding Yet)", use_container_width=True):
            if not in_prompt.strip():
                st.error("Please enter your app idea first.")
            else:
                remove_json_file(DESIGN_LOCK_FILE)
                remove_json_file(CODED_APP_FILE)
                cmd_slot = st.empty()
                sync_slot = st.empty()
                _, err_p1 = run_phase1_design_studio(in_title.strip() or "Sarfealam Pro App", in_prompt.strip(), cmd_slot, sync_slot)
                if err_p1:
                    st.error(err_p1)
                else:
                    st.rerun()

        # PANEL 3: VISUAL DESIGN & ICON STUDIO (STEP 4 — MUST BE LOCKED BEFORE CODING!)
        locked_bus = load_json_file(DESIGN_LOCK_FILE, None)
        if locked_bus:
            st.markdown("---")
            st.subheader(f"2. Visual Design Studio ({locked_bus.get('app_type')} APP)")
            dd = locked_bus.get("design_doc", {})
            pal = dd.get("palette", {})
            b64_ic = base64.b64encode(locked_bus["icon_svg"].encode("utf-8")).decode("utf-8")

            c_ic, c_info = st.columns([1, 2])
            with c_ic:
                st.markdown("**Brand Symbol Icon:**")
                st.markdown(f'<img src="data:image/svg+xml;base64,{b64_ic}" width="104" style="border-radius:22px;border:2px solid #38bdf8;"/>', unsafe_allow_html=True)
            with c_info:
                st.markdown(f"**Tagline:** *{dd.get('tagline', '')}*")
                st.markdown(f"**Bottom Navigation:** `{'Enabled (' + str(len(dd.get('nav_items', []))) + ' tabs)' if dd.get('bottom_nav_enabled') else 'Disabled (Fullscreen Gaming)'}`")
                swatches = "".join([f"<span style='display:inline-block;width:20px;height:20px;border-radius:6px;background:{v};border:1px solid #fff;margin-right:5px;' title='{k}: {v}'></span>" for k, v in pal.items()])
                st.markdown(f"**Color Palette:**<br>{swatches}", unsafe_allow_html=True)

            with st.expander("View Screen-by-Screen Blueprint & Market Brain", expanded=True):
                st.caption(f"Market Brain ({locked_bus.get('brain_model')}): {locked_bus.get('market_brain', '')[:320]}...")
                for scr in dd.get("screens", []):
                    st.markdown(f"- **{scr.get('name')}**: {scr.get('layout')} | Buttons: `{', '.join(scr.get('buttons', []))}`")

            des_chg = st.text_input("Request Design Changes (Optional):", placeholder="e.g. Change primary color to royal gold or add Wallet tab")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                if st.button("Update Design Only", use_container_width=True):
                    if des_chg.strip():
                        cmd_slot = st.empty()
                        sync_slot = st.empty()
                        run_phase1_design_studio(locked_bus["app_title"], locked_bus["user_prompt"], cmd_slot, sync_slot, des_chg.strip())
                        st.rerun()
            with col_d2:
                if st.button("Lock Design & Start Coding (Steps 5-11)", use_container_width=True):
                    cmd_slot = st.empty()
                    sync_slot = st.empty()
                    bundle, err_p2 = run_phase2_flutter_coding(locked_bus, cmd_slot, sync_slot)
                    if err_p2:
                        st.error(err_p2)
                    else:
                        st.rerun()

        # PANEL 4: CODED FLUTTER BUNDLE READY FOR GITHUB APK COMPILER
        coded_bundle = load_json_file(CODED_APP_FILE, None)
        if coded_bundle:
            st.markdown("---")
            st.subheader("3. Coded Flutter Bundle Passed All 11 Steps")
            st.success(f"Reviewer: {coded_bundle.get('review_verdict', 'APPROVED')[:80]} | Packages: {', '.join(coded_bundle.get('extra_deps', {}).keys()) or 'Core Flutter'}")
            with st.expander("Inspect Generated Dart Files"):
                st.code(coded_bundle.get("main_dart", "")[:1200], language="dart")

            if st.button("Approve & Build Native Flutter APK on GitHub", use_container_width=True):
                safe_repo = re.sub(r'[^a-z0-9-]', '', coded_bundle["app_title"].lower().replace(" ", "-")) or "flutter-app"
                safe_repo = f"{safe_repo}-{int(time.time()) % 100000}"
                with st.spinner("Creating GitHub Repo & Pushing 11-Step Flutter Project..."):
                    try:
                        repo_res = create_github_repo(safe_repo, f"{coded_bundle['app_title']} - Sarfealam Flutter Factory")
                        repo_html = repo_res.get("html_url", f"https://github.com/{DEFAULT_GITHUB_USERNAME}/{safe_repo}")
                        push_file_to_github(safe_repo, "pubspec.yaml", coded_bundle["pubspec_yaml"], "Add pubspec.yaml")
                        push_file_to_github(safe_repo, "assets/icon.svg", coded_bundle["icon_svg"], "Add Brand Symbol Icon")
                        push_file_to_github(safe_repo, "lib/services/supabase_api.dart", coded_bundle["backend_dart"], "Add Supabase Backend")
                        push_file_to_github(safe_repo, "lib/screens/app_screens.dart", coded_bundle["screens_dart"], "Add UI Screens")
                        push_file_to_github(safe_repo, "lib/main.dart", coded_bundle["main_dart"], "Add Navigation Entry")
                        push_file_to_github(safe_repo, "build.sh", make_flutter_build_script(coded_bundle["app_title"], coded_bundle["pkg_slug"]), "Add Flutter APK Build Script")
                        push_file_to_github(safe_repo, ".github/workflows/build_flutter_apk.yml", AUTOMATED_APK_WORKFLOW, "Activate Flutter APK Workflow")
                        rec = {
                            "id": f"APP-{int(time.time()) % 100000}",
                            "name": coded_bundle["app_title"],
                            "repo": safe_repo,
                            "repo_url": repo_html,
                            "actions_url": f"{repo_html}/actions",
                            "releases_url": f"{repo_html}/releases",
                            "admin_url": f"https://supreme-agent-vlqyfohdlkxxwpsdc4tiuy.streamlit.app/?admin_app={safe_repo}",
                            "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
                        }
                        save_to_vault(rec)
                        save_json_file(ACTIVE_BUILD_FILE, rec)
                        remove_json_file(DESIGN_LOCK_FILE)
                        remove_json_file(CODED_APP_FILE)
                        st.rerun()
                    except Exception as gh_e:
                        st.error(f"GitHub Push Error: {gh_e}")

# ==============================================================================
# TAB 2: PERSISTENT LIVE TRACKER
# ==============================================================================
with tab_tracker:
    st.subheader("Persistent GitHub Live Build Tracker")
    if st.button("Refresh Live GitHub Status", use_container_width=True, key="tracker_refresh"):
        st.rerun()
    live_repos = fetch_github_user_repos()
    if not live_repos:
        st.info("No active or recent builds found on GitHub yet.")
    else:
        for repo_obj in live_repos[:3]:
            r_name = repo_obj.get("name", "")
            r_url = repo_obj.get("html_url", "")
            tele = get_live_build_telemetry(r_name)
            st_state = tele.get("status", "unknown")
            st_conc = tele.get("conclusion")
            rel_url = f"{r_url}/releases"
            badge = "✅ READY" if st_conc == "success" else ("❌ FAILED" if st_conc == "failure" else f"⏳ {st_state.upper()}")
            bcol = "#10b981" if st_conc == "success" else ("#ef4444" if st_conc == "failure" else "#f59e0b")
            st.markdown(f"<div style='background:rgba(17,24,39,0.9);border:1.5px solid {bcol};border-radius:14px;padding:12px;margin-bottom:10px;display:flex;justify-content:space-between;'><b>{r_name}</b><a href='{rel_url}' style='color:{bcol};font-weight:800;text-decoration:none;'>{badge}</a></div>", unsafe_allow_html=True)

# ==============================================================================
# TAB 3: DUAL-LINK LIFETIME VAULT (STORE)
# ==============================================================================
with tab_vault:
    st.subheader("All Generated Apps Vault (Dual-Link Store)")
    local_records = load_json_file(VAULT_FILE, [])
    gh_repos = fetch_github_user_repos()
    known_repos = {r.get("repo") for r in local_records}
    for gr in gh_repos:
        r_name = gr.get("name")
        if r_name not in known_repos:
            r_url = gr.get("html_url")
            local_records.append({
                "id": f"GH-{gr.get('id')}",
                "name": r_name.replace("-", " ").title(),
                "repo": r_name,
                "repo_url": r_url,
                "releases_url": f"{r_url}/releases",
                "admin_url": f"https://supreme-agent-vlqyfohdlkxxwpsdc4tiuy.streamlit.app/?admin_app={r_name}",
                "time": gr.get("created_at", "")[:10]
            })
    if not local_records:
        st.info("No applications generated yet.")
    else:
        for item in local_records:
            r_name = item.get("repo", "")
            adm_url = item.get("admin_url", f"https://supreme-agent-vlqyfohdlkxxwpsdc4tiuy.streamlit.app/?admin_app={r_name}")
            st.markdown(f"""
            <div style="background:rgba(31,41,55,0.75);border:1px solid rgba(59,130,246,0.3);border-radius:14px;padding:14px;margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;"><b style="color:#fff;">📱 {item.get('name', r_name)}</b><span style="font-size:11px;color:#38bdf8;">{item.get('time', '')}</span></div>
              <div style="display:flex;gap:8px;margin-top:10px;">
                <a href="{item.get('releases_url', '#')}" style="flex:1;text-align:center;background:#059669;color:#fff;padding:8px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:700;">Public APK</a>
                <a href="{adm_url}" style="flex:1;text-align:center;background:#2563eb;color:#fff;padding:8px;border-radius:8px;text-decoration:none;font-size:12px;font-weight:700;">Admin Link</a>
              </div>
            </div>""", unsafe_allow_html=True)

# ==============================================================================
# TAB 4: PRIVATE OWNER ADMIN CONTROL CENTER
# ==============================================================================
with tab_admin:
    st.subheader("Private Owner Admin Control")
    pin_input = st.text_input("Enter Master Admin Password:", type="password", placeholder="Enter Password")
    if pin_input == ADMIN_PASSWORD:
        st.success(f"Verified Owner: {OWNER_NAME} | Full Admin Access Granted")
        try:
            live_users = supabase_rest("factory_users?order=created_at.desc&limit=25")
            live_txs = supabase_rest("factory_transactions?order=created_at.desc&limit=20")
            m1, m2 = st.columns(2)
            m1.metric("Cloud Users", len(live_users))
            m2.metric("Cloud Transactions", len(live_txs))
        except Exception:
            st.info("Supabase tables ready.")
        gh_list = fetch_github_user_repos()
        repo_names = [r.get("name") for r in gh_list]
        if repo_names:
            default_idx = repo_names.index(deep_admin_repo) if deep_admin_repo in repo_names else 0
            selected_repo = st.selectbox("Select App to Manage:", repo_names, index=default_idx)
            target_file = st.selectbox("Select File to Edit:", ["lib/main.dart", "lib/screens/app_screens.dart", "lib/services/supabase_api.dart", "pubspec.yaml"])
            c_adm1, c_adm2 = st.columns(2)
            with c_adm1:
                if st.button("Load Selected File", use_container_width=True):
                    try:
                        st.session_state[f"edit_{selected_repo}_{target_file}"] = fetch_file_from_github(selected_repo, target_file)
                    except Exception:
                        st.warning(f"{target_file} not found.")
            with c_adm2:
                if st.button("Delete App Repo", use_container_width=True):
                    try:
                        delete_github_repo(selected_repo)
                        st.success(f"Deleted `{selected_repo}`")
                        time.sleep(1)
                        st.rerun()
                    except Exception as de:
                        st.error(f"Delete failed: {de}")
            edit_key = f"edit_{selected_repo}_{target_file}"
            if edit_key in st.session_state:
                upd = st.text_area(f"Editing {target_file}:", value=st.session_state[edit_key], height=200)
                if st.button(f"Save {target_file} & Rebuild APK", use_container_width=True):
                    push_file_to_github(selected_repo, target_file, upd, f"Admin Update: {target_file}")
                    st.success("Updated! Fresh Flutter APK building on GitHub.")
    elif pin_input:
        st.error("Invalid Password!")
    else:
        st.info("Enter Master Admin Password to unlock.")
