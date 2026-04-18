"""Supabase session persistence helpers.

Stores refresh/access tokens locally so a locally-run app can stay logged in
without requiring OTP/magic-link on every open.

Security note: tokens grant access as the user. Treat this file like a password.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


DEFAULT_SESSION_PATH = Path("data/auth/supabase_session.json")


@dataclass
class PersistedSession:
    access_token: str
    refresh_token: str
    user_id: str
    email: Optional[str] = None
    saved_at: Optional[str] = None


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_session(path: Path = DEFAULT_SESSION_PATH) -> Optional[PersistedSession]:
    try:
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return PersistedSession(
            access_token=str(data.get("access_token") or ""),
            refresh_token=str(data.get("refresh_token") or ""),
            user_id=str(data.get("user_id") or ""),
            email=data.get("email"),
            saved_at=data.get("saved_at"),
        )
    except Exception:
        return None


def save_session_from_auth_response(
    auth_response: Any,
    path: Path = DEFAULT_SESSION_PATH,
    email: Optional[str] = None,
) -> bool:
    """Persist session tokens from a Supabase AuthResponse (sync client)."""

    try:
        session = getattr(auth_response, "session", None)
        user = getattr(auth_response, "user", None) or getattr(session, "user", None)
        access_token = getattr(session, "access_token", None)
        refresh_token = getattr(session, "refresh_token", None)
        user_id = getattr(user, "id", None)

        if not access_token or not refresh_token or not user_id:
            return False

        _ensure_parent(path)
        payload = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": str(user_id),
            "email": email or getattr(user, "email", None),
            "saved_at": datetime.now().isoformat(),
        }
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        # Best-effort permissions hardening (POSIX)
        try:
            os.chmod(path, 0o600)
        except Exception:
            pass

        return True
    except Exception:
        return False


def clear_session(path: Path = DEFAULT_SESSION_PATH) -> bool:
    try:
        if path.exists():
            path.unlink()
        return True
    except Exception:
        return False
