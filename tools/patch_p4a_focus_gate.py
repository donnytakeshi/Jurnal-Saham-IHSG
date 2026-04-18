#!/usr/bin/env python3
"""Patch python-for-android SDL2 bootstrap focus gate.

Some Android devices briefly lose window focus during app startup.
In certain p4a SDL2 bootstrap versions, `LoadLibraries.onPostExecute()` only
launches the native/Python thread when the Activity has focus, which can
prevent Python from ever starting.

This script makes the patch reproducible by:
- Removing `mActivity.mHasFocus &&` from the launch condition (only within the
  'Launch app...' block).
- Injecting a verbose log before `resumeNativeThread()` to confirm execution.

It patches both the bootstrap source and any already-created dist source.
It is designed to be idempotent.
"""

from __future__ import annotations

import glob
import os
import re
from pathlib import Path


def _candidate_files(repo_root: Path) -> list[Path]:
    patterns = [
        ".buildozer/android/platform/python-for-android/pythonforandroid/bootstraps/sdl2/build/src/main/java/org/kivy/android/PythonActivity.java",
        ".buildozer/android/platform/build-*/dists/*/src/main/java/org/kivy/android/PythonActivity.java",
    ]

    files: list[Path] = []
    for pattern in patterns:
        for match in glob.glob(str(repo_root / pattern)):
            p = Path(match)
            if p.is_file():
                files.append(p)

    # Deduplicate while preserving order
    seen: set[Path] = set()
    unique: list[Path] = []
    for p in files:
        rp = p.resolve()
        if rp not in seen:
            seen.add(rp)
            unique.append(p)
    return unique


def _patch_python_activity(java_path: Path) -> bool:
    original = java_path.read_text(encoding="utf-8", errors="replace")

    marker = "// Launch app if that hasn't been done yet:"
    start = original.find(marker)
    if start == -1:
        return False

    # Limit patch scope to the launch block to avoid unintended edits.
    after = original[start:]
    end_marker = "mActivity.resumeNativeThread();"
    end_pos = after.find(end_marker)
    if end_pos == -1:
        return False

    # Extend to include the line containing resumeNativeThread();
    end_pos += len(end_marker)
    block = after[:end_pos]

    patched_block = block

    # Remove focus gate if present in the launch condition.
    patched_block = re.sub(
        r"\bmActivity\.mHasFocus\s*&&\s*", "", patched_block
    )

    # Inject log line right before resumeNativeThread() (idempotent).
    if "Launching native thread" not in patched_block:
        # Use the indentation of the resumeNativeThread() line.
        m = re.search(r"(?m)^(\s*)mActivity\.resumeNativeThread\(\);", patched_block)
        indent = m.group(1) if m else ""
        log_line = (
            f'{indent}Log.v(TAG, "Launching native thread (hasFocus=" + '
            f'mActivity.mHasFocus + ", state=" + mActivity.mCurrentNativeState + ")");\n'
        )
        patched_block = re.sub(
            r"(?m)^(\s*)mActivity\.resumeNativeThread\(\);",
            lambda mm: f"{log_line}{mm.group(0)}",
            patched_block,
            count=1,
        )

    if patched_block == block:
        return False

    updated = original[:start] + patched_block + original[start + len(block) :]
    java_path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    candidates = _candidate_files(repo_root)

    if not candidates:
        print("[patch_p4a_focus_gate] No candidate PythonActivity.java files found yet.")
        print("[patch_p4a_focus_gate] (This is normal on a fresh repo before the first Android build.)")
        return 0

    changed_any = False
    for path in candidates:
        try:
            changed = _patch_python_activity(path)
        except Exception as e:  # pragma: no cover
            print(f"[patch_p4a_focus_gate] ERROR patching {path}: {e}")
            continue

        if changed:
            changed_any = True
            print(f"[patch_p4a_focus_gate] Patched: {path}")
        else:
            print(f"[patch_p4a_focus_gate] Already OK / not applicable: {path}")

    if not changed_any:
        print("[patch_p4a_focus_gate] No changes were necessary.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
