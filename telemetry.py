# telemetry.py

import json
from datetime import datetime, timezone

LOG_FILE = "telemetry.log"

def log_request(pathway: str,
                latency_ms: float,
                input_len: int,
                output_len: int,
                used_tool: bool,
                model_name: str,
                tokens_in: int | None = None,
                tokens_out: int | None = None,
                cost_usd: float | None = None):
    """
    pathway: "tool" if external API was used, else "none"
    """
    entry = {
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "pathway": pathway,
        "latency_ms": latency_ms,
        "input_len_chars": input_len,
        "output_len_chars": output_len,
        "used_tool": used_tool,
        "model": model_name,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": cost_usd
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
