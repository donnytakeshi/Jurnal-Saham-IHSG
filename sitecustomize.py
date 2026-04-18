"""Runtime tweaks for packaged environments.

This module is auto-imported by Python at startup if present on sys.path.
We keep it minimal and only apply Android-specific environment fixes.
"""

from __future__ import annotations

import os


def _is_android() -> bool:
    # python-for-android sets ANDROID_ARGUMENT to the app private files dir.
    return bool(os.environ.get("ANDROID_ARGUMENT"))


def _ensure_dir(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        return


if _is_android():
    try:
        # Prefer a writable base directory for Kivy's cache/config.
        # On python-for-android, ANDROID_ARGUMENT is often `/data/user/0/<pkg>/files/app`
        # (the extracted working dir). Some devices/ROMs can block writing under this
        # path for Kivy's icon copy step. Use ANDROID_PRIVATE if available, otherwise
        # derive `/data/user/0/<pkg>/files` from the `/files/app` path.
        base = os.environ.get("ANDROID_PRIVATE") or os.environ.get("ANDROID_ARGUMENT")
        if base:
            try:
                if base.rstrip("/").endswith("/app"):
                    base = os.path.dirname(base.rstrip("/"))
            except Exception:
                pass

            kivy_home = os.path.join(base, ".kivy")
            _ensure_dir(kivy_home)
            _ensure_dir(os.path.join(kivy_home, "icon"))
            # Force override: bootstrap may set HOME/KIVY_HOME to the extracted
            # working dir (`.../files/app`) which can be non-writable for Kivy's
            # icon/logo copy step on some ROMs.
            os.environ["HOME"] = base
            os.environ["KIVY_HOME"] = kivy_home
            # Reduce noisy init work; icons are non-essential on mobile.
            os.environ.setdefault("KIVY_NO_ARGS", "1")
            try:
                print(f"[sitecustomize] ANDROID_BASE={base} KIVY_HOME={kivy_home}")
            except Exception:
                pass
    except Exception:
        pass
