#!/usr/bin/env python3
"""Run a shell command, then refresh the local Kivy desktop preview and save a screenshot.

Usage:
  python tools/exec_and_refresh.py --cmd "<shell command>" [--wait 2]

This script is intended to be used on the developer machine (macOS) where a
local preview is shown by running `python main.py` in the project's venv.
After running the command it will restart the preview and capture
`build_logs/preview_last_command.png` so the UI reflects the latest changes.
"""
import argparse
import shlex
import subprocess
import os
import sys
import time


def run_shell(cmd: str, logfile: str):
    with open(logfile, 'wb') as f:
        proc = subprocess.Popen(cmd, shell=True, stdout=f, stderr=subprocess.STDOUT)
        proc.communicate()
        return proc.returncode


def restart_preview(venv_path='.venvsource'):
    # Kill any running preview, start a fresh preview in background, wait a bit, then screencapture
    venv_python = os.path.join(venv_path, 'bin', 'python')
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    # Kill running preview processes (best-effort)
    subprocess.run("pkill -f \"python main.py\" || true", shell=True)

    # Start preview in background (nohup so it keeps running)
    cmd = f"{shlex.quote(venv_python)} main.py >/tmp/kivy_preview.log 2>&1 &"
    subprocess.run(cmd, shell=True)

    # Wait briefly for UI to settle
    time.sleep(2)

    # Capture screenshot (macOS `screencapture`). Save to build_logs/preview_last_command.png
    os.makedirs('build_logs', exist_ok=True)
    out_png = os.path.join('build_logs', 'preview_last_command.png')
    try:
        subprocess.run(['screencapture', '-x', out_png], check=True)
    except Exception:
        # If screencapture not available, ignore
        pass
    return out_png


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--cmd', required=True, help='Shell command to run')
    p.add_argument('--wait', type=float, default=0.0, help='Seconds to wait after running command')
    p.add_argument('--venv', default='.venvsource', help='Path to virtualenv folder')
    args = p.parse_args()

    os.makedirs('build_logs', exist_ok=True)
    logfile = os.path.join('build_logs', 'last_exec_output.txt')

    rc = run_shell(args.cmd, logfile)
    if args.wait:
        time.sleep(args.wait)

    png = restart_preview(args.venv)

    print(f"Command exit code: {rc}")
    print(f"Output saved to: {logfile}")
    print(f"Preview screenshot saved to: {png}")


if __name__ == '__main__':
    main()
