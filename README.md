# PatchSmith — LLM Patch Note Writer  
Built for the Topics in CS Course Assignment (LLM App)

PatchSmith is a lightweight web application that converts raw bullet-point change logs into clean, formatted patch notes using a locally-hosted LLM (Ollama).

🟢 **No API keys needed**  
🟢 **Fast local inference**  
🟢 **Safety, telemetry, offline eval all included**

---

## 🚀 Features

### Core Functionality
- Enter raw bullet points → receive fully-formatted patch notes.
- Outputs version suggestions, summaries, grouped sections, and structured JSON.

### Enhancement: Tool Use  
- App optionally calls a simple date/time tool for release metadata.
- Tool usage is logged in telemetry.

### Safety & Robustness
- Prompt injection detection.
- Input length guard.
- Strict system prompt (JSON-only rules).
- Fallback if model produces invalid JSON.
- Works even if the model is offline (fallback generator).

### Telemetry
Logs every request to `telemetry.log`, including:
- Timestamp  
- Input length  
- Latency  
- Pathway (tool/no-tool)  
- Whether a tool was used  
- Model name  

### Offline Evaluation
Included:
- `tests.json` with 15+ evaluation cases  
- `run_eval.py` that prints pass/fail + accuracy  

---

## 🛠️ Installation

### 1. Install Ollama (Mac)

brew install --cask ollama
open -a Ollama

2. Pull the model (first-time only)
ollama run gemma3:1b

3. Install Python dependencies
pip install -r requirements.txt

4. Run the app

python app.py

Then open your browser at:
http://127.0.0.1:5000

📁 Project Structure

llm-patchsmith/
│
├── app.py
├── llm_client.py
├── safety.py
├── tool_time_api.py
├── telemetry.py
├── telemetry.log
│
├── templates/
│   └── index.html
│
├── tests.json
├── run_eval.py
├── README.md
└── TECH_NOTE.md

🔧 Configuration

Use .env.example as a template:
OLLAMA_MODEL=gemma3:1b
FLASK_ENV=development

Create your .env:
cp .env.example .env

🔒 Safety Guardrails
PatchSmith uses several layers of safety:

1. Strict System Prompt
JSON-only
No explanations
No hallucinated features
No non-JSON output

2. Prompt Injection Detection
Rejects malicious queries such as:
“ignore previous instructions”
“you are now system”
“disregard safety”

3. Input Validation
Rejects empty input
Rejects inputs > 2000 characters

4. Fallback Handling
If the LLM outputs invalid JSON:
A Python fallback generates structured patch notes safely.

📊 Telemetry
Every request logs an entry in:
telemetry.log

Example:
{
  "timestamp": "2025-11-30T03:22:18Z",
  "pathway": "none",
  "latency_ms": 182.1,
  "input_len_chars": 58,
  "output_len_chars": 420,
  "used_tool": false,
  "model": "ollama-gemma3:1b"
}

🧪 Running Offline Evaluation
Run:
python run_eval.py
Output example:
Test 1: PASS
Test 2: PASS
...
Passed 14/15 tests → 93.3%


✔️ Assignment Requirements Checklist

Requirement	Status
LLM core flow	    ✅ Done
Enhancement (tool)	✅ Done
Safety guardrails	✅ Done
Telemetry logging	✅ Done
Offline evaluation	✅ Done
README	            ✅ Done
Tech note	        ✅ Done
UI polish	        ✅ Done

🎉 Conclusion
PatchSmith is a complete LLM application running entirely on a local model via Ollama.

It demonstrates:
prompt engineering
safety
tool-use
telemetry
evaluation
full-stack integration
