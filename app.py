# app.py

import time
from dotenv import load_dotenv
from flask import Flask, render_template, request

from safety import is_prompt_injection
from llm_client import generate_patch_struct, MODEL_NAME
from tool_time_api import get_release_date_iso
from telemetry import log_request

load_dotenv()

app = Flask(__name__)

# Input length guard
MAX_INPUT_CHARS = 2000


def format_patch_notes(struct: dict, release_date: str | None) -> str:
    """
    Turn the JSON structure from the LLM into pretty text patch notes.
    """
    version = struct.get("version_suggestion", "0.0.1")
    summary = struct.get("summary", "").strip()
    sections = struct.get("sections", [])

    header = f"Release v{version}"
    if release_date:
        header += f" — {release_date}"

    lines = [header, "", "Summary", f"- {summary}", ""]

    for sec in sections:
        title = (sec.get("title") or "").strip()
        items = sec.get("items") or []
        if not title or not items:
            continue
        lines.append(title)
        for it in items:
            lines.append(f"- {it}")
        lines.append("")

    return "\n".join(lines).strip()


def _validate_bullets(text: str) -> str | None:
    if not text:
        return "Please paste your bullet-point changes."
    if len(text) > MAX_INPUT_CHARS:
        return f"Input too long (> {MAX_INPUT_CHARS} characters). Please shorten it."
    if is_prompt_injection(text):
        return (
            "Your input looks like prompt injection. "
            "I must follow my safety rules and cannot process this."
        )
    return None


def _generate_notes_and_log(text: str) -> str:
    start = time.time()
    used_tool = False

    # 1) Call LLM to turn bullets into JSON structure
    struct = generate_patch_struct(text)

    # 2) Decide whether to call the external tool for date
    needs_date = bool(struct.get("needs_date", True))
    release_date = None

    if needs_date:
        release_date = get_release_date_iso()
        used_tool = release_date is not None

    # 3) Turn JSON into human-readable patch notes text
    notes = format_patch_notes(struct, release_date)

    end = time.time()
    latency_ms = (end - start) * 1000

    # 4) Telemetry log
    log_request(
        pathway="tool" if used_tool else "none",
        latency_ms=latency_ms,
        input_len=len(text),
        output_len=len(notes) if notes else 0,
        used_tool=used_tool,
        model_name=MODEL_NAME,
    )

    return notes


@app.route("/", methods=["GET", "POST"])
def index():
    bullets = ""
    patch_notes = None
    error = None

    if request.method == "POST":
        bullets = request.form.get("bullets", "").strip()

        # === Safety / validation ===
        error = _validate_bullets(bullets)
        if not error:
            try:
                patch_notes = _generate_notes_and_log(bullets)
            except Exception as e:
                error = f"Something went wrong generating patch notes: {e}"

    return render_template(
        "index.html",
        bullets=bullets,
        patch_notes=patch_notes,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True)
