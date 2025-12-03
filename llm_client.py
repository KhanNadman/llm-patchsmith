# llm_client.py

import os
import json
import requests
from typing import Dict, Any
from dotenv import load_dotenv
from safety import SYSTEM_PROMPT

# Load environment variables
load_dotenv()

# Name of the local Ollama model, e.g. "gemma3:1b"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")

# This is what app.py logs as model_name in telemetry
MODEL_NAME = f"ollama-{OLLAMA_MODEL}"

OLLAMA_URL = "http://localhost:11434/api/chat"


def _clean_json_text(text: str) -> str:
    """
    Sometimes models wrap JSON in ```json ... ``` fences.
    Strip those if present.
    """
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _local_fallback_struct(bullets: str) -> Dict[str, Any]:
    """
    Local heuristic fallback if the LLM output isn't valid JSON or Ollama fails.
    Groups bullet points into sections based on simple keyword rules.
    """
    lines = [
        line.strip("- ").strip()
        for line in bullets.splitlines()
        if line.strip()
    ]

    new_features = []
    improvements = []
    bug_fixes = []
    other = []

    for line in lines:
        lower = line.lower()
        if any(w in lower for w in ("fix", "fixed", "bug", "issue", "error", "crash")):
            bug_fixes.append(line)
        elif any(w in lower for w in ("add", "added", "new", "introduc")):
            new_features.append(line)
        elif any(w in lower for w in ("improv", "optimiz", "faster", "performance", "speed")):
            improvements.append(line)
        else:
            other.append(line)

    sections = []
    if new_features:
        sections.append({"title": "New Features", "items": new_features})
    if improvements:
        sections.append({"title": "Improvements", "items": improvements})
    if bug_fixes:
        sections.append({"title": "Bug Fixes", "items": bug_fixes})
    if other:
        sections.append({"title": "Other Changes", "items": other})

    summary = (
        "This release includes {} change(s) across new features, "
        "improvements, and fixes."
    ).format(len(lines))

    return {
        "version_suggestion": "0.1.0",
        "summary": summary,
        "sections": sections,
        "needs_date": True,
    }


def generate_patch_struct(bullets: str) -> Dict[str, Any]:
    """
    Call a local Ollama model to turn bullet points into a JSON structure
    for patch notes.

    If anything goes wrong (Ollama not running, bad JSON, etc.),
    fall back to a local heuristic generator so the app still works.
    """
    user_msg = (
        "Here are the raw changes as bullet points. "
        "Do NOT invent additional changes.\n\n"
        f"{bullets}\n\n"
        "Remember:\n"
        "- Respond ONLY with valid JSON.\n"
        '- JSON keys: \"version_suggestion\", \"summary\", \"sections\", \"needs_date\".'
    )

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        "stream": False,
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        content = data.get("message", {}).get("content", "")
        cleaned = _clean_json_text(content)
        return json.loads(cleaned)

    except Exception as e:
        print(f"[llm_client] Ollama call failed or invalid JSON, using fallback: {e}")
        return _local_fallback_struct(bullets)
