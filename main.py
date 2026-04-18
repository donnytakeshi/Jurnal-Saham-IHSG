"""Android entrypoint for Jurnal Saham IHSG (Kivy).

Buildozer/p4a expects a `main.py` at project root.
This delegates to the Kivy UI in `desktop_app_bak.py`.

Run (desktop):
  python3 main.py
"""

from __future__ import annotations

import os
import runpy


def main() -> None:
  # Ensure Kivy uses a writable home directory on Android.
  # (Prevents non-fatal PermissionError when Kivy tries to copy its icon set.)
  try:
    def _normalize_android_base(path: str) -> str:
      p = path.rstrip("/")
      if p.endswith("/app"):
        return os.path.dirname(p)
      return p

    def _is_writable_dir(path: str) -> bool:
      try:
        os.makedirs(path, exist_ok=True)
        test_file = os.path.join(path, ".__write_test__")
        with open(test_file, "w", encoding="utf-8") as f:
          f.write("ok")
        os.remove(test_file)
        return True
      except Exception:
        return False

    bases: list[str] = []
    android_private = os.environ.get("ANDROID_PRIVATE")
    if android_private:
      bases.append(_normalize_android_base(android_private))
    android_argument = os.environ.get("ANDROID_ARGUMENT")
    if android_argument:
      bases.append(_normalize_android_base(android_argument))
    existing_home = os.environ.get("HOME")
    if existing_home:
      bases.append(existing_home)
    bases.append(os.getcwd())

    chosen_base: str | None = None
    for candidate in bases:
      if not candidate:
        continue
      if _is_writable_dir(candidate):
        chosen_base = candidate
        break

    if chosen_base:
      kivy_home = os.path.join(chosen_base, ".kivy")
      os.makedirs(os.path.join(kivy_home, "icon"), exist_ok=True)

      # Force override: p4a bootstrap may set HOME to the extracted app dir
      # (`.../files/app`) which can be permission-restricted for Kivy's icon copy.
      os.environ["HOME"] = chosen_base
      os.environ["KIVY_HOME"] = kivy_home
      os.environ.setdefault("KIVY_NO_ARGS", "1")
  except Exception:
    pass

  # On Android, python-for-android commonly strips .py sources and keeps .pyc.
  # `run_module` works for both .py (desktop) and .pyc (Android).
  try:
    from desktop_app_final import MainApp
    MainApp().run()
  except Exception as e_final:
    print(f"[INFO] Gagal menjalankan desktop_app_final.py: {e_final}\nFallback ke desktop_app_bak.py...")
    try:
      from desktop_app_bak import MainStockbitApp
      MainStockbitApp().run()
    except Exception:
      # Fallback to runpy for desktop compatibility
      import runpy
      runpy.run_module("desktop_app_bak", run_name="__main__")


if __name__ == "__main__":
    main()
