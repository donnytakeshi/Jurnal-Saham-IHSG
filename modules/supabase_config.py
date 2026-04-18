"""Centralized Supabase configuration loader.

On desktop / Streamlit, values are usually provided via environment
variables:

- SUPABASE_URL
- SUPABASE_ANON_KEY

On Android (Kivy), environment variables are not always propagated
reliably. To make configuration portable, this helper also supports
reading from a small JSON file packaged with the app.

Supported JSON files (first match wins):
- supabase_config_local.json  (recommended for local/dev, ignored by git)
- supabase_config.json        (generic fallback)

JSON structure example:

{
  "SUPABASE_URL": "https://xxxxx.supabase.co",
  "SUPABASE_ANON_KEY": "ey...your_anon_key..."
}

Both keys are safe to embed in a client app (anon key), but you may
still treat them as semi-secret and avoid committing actual values to
public repos if you prefer.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Tuple


def _load_from_env() -> Tuple[str, str]:
    """Load Supabase config from environment variables.

    Returns (url, key); empty strings if not set.
    """
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_ANON_KEY", "").strip()
    return url, key


def _load_from_json() -> Tuple[str, str]:
    """Load Supabase config from a JSON file near the project root.

    This is primarily for Android builds where environment variables
    are not reliably available at runtime.
    """
    try:
        here = Path(__file__).resolve()
        # Project root = two levels up from modules/ (../..)
        project_root = here.parent.parent
    except Exception:
        return "", ""

    candidates = [
        project_root / "supabase_config_local.json",
        project_root / "supabase_config.json",
    ]

    for path in candidates:
        try:
            if not path.is_file():
                continue
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f) or {}
            # Accept both upper-case and lower-case keys
            url = (
                data.get("SUPABASE_URL")
                or data.get("supabase_url")
                or ""
            )
            key = (
                data.get("SUPABASE_ANON_KEY")
                or data.get("supabase_anon_key")
                or ""
            )
            url = str(url or "").strip()
            key = str(key or "").strip()
            if url and key:
                return url, key
        except Exception:
            # Ignore JSON/IO errors and try next candidate
            continue

    return "", ""


def get_supabase_config() -> Tuple[str, str]:
    """Return (supabase_url, supabase_anon_key).

    Preference order:
    1. Environment variables (SUPABASE_URL, SUPABASE_ANON_KEY)
    2. JSON config file (supabase_config_local.json / supabase_config.json)

    If nothing is found, returns ("", "").
    """
    url, key = _load_from_env()
    if url and key:
        return url, key

    url, key = _load_from_json()
    return url, key
