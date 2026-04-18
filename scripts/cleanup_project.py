"""Project cleanup helper.

Moves known non-essential artifacts into `_archive/<timestamp>/` to reduce clutter.
Does NOT touch:
- `.buildozer/` (kept for faster rebuilds)
- `data/` (kept as requested)

Usage:
    python3 scripts/cleanup_project.py            # safe: archive
    python3 scripts/cleanup_project.py --hard     # delete instead of archive

You can re-run safely; it creates a new timestamped archive each time.
"""

from __future__ import annotations

import glob
import os
import argparse
import shutil
from dataclasses import dataclass
from datetime import datetime


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass(frozen=True)
class MoveResult:
    moved: list[tuple[str, str]]
    missing: list[str]
    kept: list[str]


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _rel(path: str) -> str:
    try:
        return os.path.relpath(path, ROOT)
    except Exception:
        return path


def _safe_move(src: str, dst_dir: str, moved: list[tuple[str, str]], missing: list[str]) -> None:
    src_abs = src if os.path.isabs(src) else os.path.join(ROOT, src)
    if not os.path.exists(src_abs):
        missing.append(_rel(src_abs))
        return

    _ensure_dir(dst_dir)
    dst_abs = os.path.join(dst_dir, os.path.basename(src_abs))

    # Avoid overwriting: add suffix if needed.
    if os.path.exists(dst_abs):
        base = os.path.basename(src_abs)
        stem, ext = os.path.splitext(base)
        i = 2
        while True:
            cand = os.path.join(dst_dir, f"{stem}__{i}{ext}")
            if not os.path.exists(cand):
                dst_abs = cand
                break
            i += 1

    shutil.move(src_abs, dst_abs)
    moved.append((_rel(src_abs), _rel(dst_abs)))


def _safe_delete(src: str, deleted: list[str], missing: list[str]) -> None:
    src_abs = src if os.path.isabs(src) else os.path.join(ROOT, src)
    if not os.path.exists(src_abs):
        missing.append(_rel(src_abs))
        return
    try:
        if os.path.isdir(src_abs) and not os.path.islink(src_abs):
            shutil.rmtree(src_abs)
        else:
            os.remove(src_abs)
        deleted.append(_rel(src_abs))
    except Exception:
        # Fall back to archive if delete fails? Keep behavior predictable: just record as missing-like.
        missing.append(_rel(src_abs))


def _delete_pycache_and_pyc() -> int:
    deleted = 0
    # __pycache__ dirs
    for path in glob.glob(os.path.join(ROOT, "**", "__pycache__"), recursive=True):
        try:
            shutil.rmtree(path)
            deleted += 1
        except Exception:
            pass

    # loose .pyc files
    for path in glob.glob(os.path.join(ROOT, "**", "*.pyc"), recursive=True):
        # Don’t traverse into .buildozer platform too aggressively; still safe but can be huge.
        if "/.buildozer/" in path.replace("\\", "/"):
            continue
        try:
            os.remove(path)
            deleted += 1
        except Exception:
            pass

    return deleted


def _prune_bin_apks(archive_dir: str, hard: bool, moved: list[tuple[str, str]], deleted: list[str], missing: list[str], kept: list[str]) -> None:
    bin_dir = os.path.join(ROOT, "bin")
    if not os.path.isdir(bin_dir):
        missing.append(_rel(bin_dir))
        return

    apks = sorted(glob.glob(os.path.join(bin_dir, "*.apk")), key=lambda p: os.path.getmtime(p), reverse=True)
    if not apks:
        return

    keep_apk = apks[0]
    kept.append(_rel(keep_apk))

    to_archive = apks[1:]
    dst_dir = os.path.join(archive_dir, "bin_old")

    for apk in to_archive:
        if hard:
            _safe_delete(apk, deleted, missing)
        else:
            _safe_move(apk, dst_dir, moved, missing)

        # Handle associated signature sidecars if present
        for ext in (".idsig", ".sig"):
            sidecar = apk + ext
            if os.path.exists(sidecar):
                if hard:
                    _safe_delete(sidecar, deleted, missing)
                else:
                    _safe_move(sidecar, dst_dir, moved, missing)


def run(*, hard: bool = False) -> MoveResult:
    archive_root = os.path.join(ROOT, "_archive", _ts())
    if not hard:
        _ensure_dir(archive_root)

    moved: list[tuple[str, str]] = []
    deleted: list[str] = []
    missing: list[str] = []
    kept: list[str] = []

    # 1) Archive bulky analysis/recovery folders
    to_archive_dirs = [
        "apk_mod",
        "decompiled_output",
        "extracted_apk_0_1_34",
        "extracted_apk_0_1_34_tmp",
        "installed_apk_from_device",
        "reconstructed_from_apk",
        "tmp_apk_analysis",
        "tmp_repack",
        "build_logs",
    ]
    for d in to_archive_dirs:
        if hard:
            _safe_delete(d, deleted, missing)
        else:
            _safe_move(d, archive_root, moved, missing)

    # 2) Archive loose logs / pid files / scratch
    to_archive_files = [
        ".buildozer_build.log",
        "crash_log.txt",
        "kivy_app.log",
        ".desktop_app_bak.pid",
        "logcat.pid",
        "1",
    ]
    # include device logs
    to_archive_files.extend(sorted(glob.glob(os.path.join(ROOT, "device_log_*.log"))))

    for f in to_archive_files:
        if hard:
            _safe_delete(f, deleted, missing)
        else:
            _safe_move(f, archive_root, moved, missing)

    # 3) Prune bin/ (keep newest APK only)
    _prune_bin_apks(archive_root, hard, moved, deleted, missing, kept)

    # 4) Delete python caches (regenerates automatically)
    deleted_count = _delete_pycache_and_pyc()
    kept.append(f"deleted_pycache_and_pyc={deleted_count}")

    if hard and deleted:
        kept.append(f"deleted_artifacts={len(deleted)}")

    return MoveResult(moved=moved, missing=missing, kept=kept)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean up local build/test artifacts.")
    parser.add_argument(
        "--hard",
        action="store_true",
        help="Delete artifacts instead of archiving to _archive/. Never touches .buildozer/ or data/.",
    )
    args = parser.parse_args()

    res = run(hard=bool(args.hard))
    print("Cleanup complete.")
    print("Kept:")
    for k in res.kept:
        print(" -", k)
    print("Moved:")
    for s, d in res.moved:
        print(f" - {s} -> {d}")
