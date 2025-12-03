# tool_time_api.py

import requests
from datetime import datetime

WORLD_TIME_URL = "https://worldtimeapi.org/api/timezone/America/Toronto"

def get_release_date_iso() -> str | None:
    """
    Calls an external API (worldtimeapi.org) to fetch current date/time.
    Returns date as 'YYYY-MM-DD' string or None on error.
    """
    try:
        resp = requests.get(WORLD_TIME_URL, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        dt_str = data.get("datetime")
        if not dt_str:
            return None
        # dt_str like '2025-11-30T20:15:32.123456-05:00'
        dt = datetime.fromisoformat(dt_str.split(".")[0])
        return dt.date().isoformat()
    except Exception:
        return None
