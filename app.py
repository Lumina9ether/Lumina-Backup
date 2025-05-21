from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
import uuid
import json
import re
from datetime import datetime
from google.cloud import texttospeech

app = Flask(__name__)
CORS(app)

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "lumina-voice-ai.json"
tts_client = texttospeech.TextToSpeechClient()

MEMORY_FILE = "memory.json"

PACKAGE_DETAILS = {
    "spark": (
        "🌟 **Lumina Spark** is a 48-hour self-paced digital starter kit. It includes:\n"
        "- Brand and niche setup templates\n"
        "- A one-page AI funnel system\n"
        "- Pre-written email and caption scripts\n"
        "- Video walkthroughs and automations\n"
        "Spark is perfect for creators or side-hustlers launching fast with zero tech overwhelm."
    ),
    "ignite": (
        "🔥 **Lumina Ignite** is our 7-day guided experience for entrepreneurs who want accountability.\n"
        "- Daily Zoom sessions and hands-on setup\n"
        "- Templates + coaching to finish your website, funnel, emails, and product\n"
        "- Group momentum to launch with confidence\n"
        "This is for you if you need a push and a plan to launch *now*."
    ),
    "sovereign": (
        "👑 **Lumina Sovereign** is our done-for-you elite package.\n"
        "- We build your entire digital business system (branding, funnel, automations, voice)\n"
        "- Custom AI content, landing pages, lead system, and email setup\n"
        "- 1:1 onboarding and system handoff\n"
        "If you're ready to operate like a CEO and let Lumina do the heavy lifting, this is for you."
    )
}

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def check_missing_memory(memory):
    missing = []
    if not memory["personal"].get("name"):
        missing.append("name")
    if not memory["business"].get("goal"):
        missing.append("goal")
    if not memory["preferences"].get("voice_style"):
        missing.append("voice_style")
    return missing

def update_timeline_from_text(text, memory):
    keywords = ["mark today as", "record", "log", "note", "milestone"]
    if any(k in text.lower() for k in keywords):
        match = re.search(r"(?:mark today as|record|log|note|milestone):?\s*(.+)", text, re.IGNORECASE)
        if match:
            event = match.group(1).strip()
            today = datetime.now().strftime("%Y-%m-%d")
            timeline = memory.get("timeline", [])
            timeline.append({"date": today, "event": event})
            memory["timeline"] = timeline
    return memory

def update_memory_from_text(text, memory):
    if "my name is" in text.lower():
        name = re.search(r"my name is ([a-zA-Z ,.'-]+)", text, re.IGNORECASE)
        if name:
            memory["personal"]["name"] = name.group(1).strip()
    if "my goal is" in text.lower():
        goal = re.search(r"my goal is (.+)", text, re.IGNORECASE)
        if goal:
            memory["business"]["goal"] = goal.group(1).strip()
    if "speak in" in text.lower():
        style = re.search(r"speak in (.+)", text, re.IGNORECASE)
        if style:
            memory["preferences"]["voice_style"] = style.group(1).strip()
    return memory

def detect_funnel_entry(text):
    lowered = text.lower()
    if any(kw in lowered for kw in ["i'm just looking", "what is this", "not sure", "thinking about"]):
        return "explorer"
    elif any(kw in lowered for kw in ["how do i start", "help me", "learn", "understand"]):
        return "curious"
    elif any(kw in lowered for kw in ["i'm ready", "get started", "invest", "sign up"]):
        return "ready"
    elif any(kw in lowered for kw in ["buy", "purchase", "checkout"]):
        return "buyer"
    elif any(kw in lowered for kw in ["need support", "have an issue", "need help"]):
        return "support"
    return "explorer"
