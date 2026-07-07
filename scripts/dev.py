#!/usr/bin/env python3
"""Cross-platform dev task runner for instrument-cluster.

Dependency-free (standard library only) so it behaves the same on Windows,
macOS, and Linux — Python is already a prerequisite. Prefer the Makefile
wrapper on Unix (`make dev`), or call directly:

    python scripts/dev.py setup     # create venv, install backend + frontend deps
    python scripts/dev.py dev       # run API (:8000) + Vite dev server (:5173)
    python scripts/dev.py build     # build the frontend to frontend/dist
    python scripts/dev.py run       # build if needed, then serve everything from Flask
    python scripts/dev.py test      # backend pytest + frontend vitest
    python scripts/dev.py lint      # ruff + eslint + tsc
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV = ROOT / ".venv"
MIN_PYTHON = (3, 11)


def fail(message: str) -> "NoReturn":  # type: ignore[valid-type]
    print(f"\n[dev.py] ERROR: {message}\n", file=sys.stderr)
    raise SystemExit(1)


def venv_python() -> str:
    exe = VENV / ("Scripts" if os.name == "nt" else "bin") / (
        "python.exe" if os.name == "nt" else "python"
    )
    return str(exe)


def require(tool: str) -> str:
    path = shutil.which(tool)
    if not path:
        fail(f"'{tool}' was not found on PATH. Please install it and re-run.")
    return path


def check_prereqs(need_node: bool) -> None:
    if sys.version_info < MIN_PYTHON:
        fail(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required, found {sys.version.split()[0]}.")
    if need_node:
        require("node")
        require("npm")


def run(cmd: list[str], cwd: Path, env: dict | None = None) -> None:
    printable = " ".join(cmd)
    print(f"[dev.py] $ {printable}  (cwd={cwd.relative_to(ROOT)})")
    result = subprocess.run(cmd, cwd=str(cwd), env=env)
    if result.returncode != 0:
        fail(f"command failed ({result.returncode}): {printable}")


def ensure_setup() -> None:
    if not Path(venv_python()).exists():
        fail("Python venv not found. Run:  python scripts/dev.py setup")
    if not (FRONTEND / "node_modules").exists():
        fail("frontend/node_modules not found. Run:  python scripts/dev.py setup")


# ---- commands -------------------------------------------------------------
def cmd_setup(_args: argparse.Namespace) -> None:
    check_prereqs(need_node=True)
    if not Path(venv_python()).exists():
        run([sys.executable, "-m", "venv", str(VENV)], cwd=ROOT)
    run([venv_python(), "-m", "pip", "install", "--upgrade", "pip"], cwd=ROOT)
    run([venv_python(), "-m", "pip", "install", "-r", "dev-requirements.txt"], cwd=BACKEND)
    run([require("npm"), "install"], cwd=FRONTEND)
    print("\n[dev.py] setup complete. Next:  python scripts/dev.py dev\n")


def cmd_build(_args: argparse.Namespace) -> None:
    check_prereqs(need_node=True)
    ensure_setup()
    run([require("npm"), "run", "build"], cwd=FRONTEND)


def cmd_run(_args: argparse.Namespace) -> None:
    check_prereqs(need_node=True)
    ensure_setup()
    if not (FRONTEND / "dist" / "index.html").exists():
        cmd_build(_args)
    print("[dev.py] serving on http://127.0.0.1:8000  (Ctrl-C to stop)")
    run([venv_python(), "-m", "app"], cwd=BACKEND)


def cmd_dev(_args: argparse.Namespace) -> None:
    check_prereqs(need_node=True)
    ensure_setup()
    print("[dev.py] starting API (:8000) and Vite dev server (:5173). Ctrl-C to stop both.")
    backend = subprocess.Popen([venv_python(), "-m", "app"], cwd=str(BACKEND))
    frontend = subprocess.Popen([require("npm"), "run", "dev"], cwd=str(FRONTEND))
    procs = [backend, frontend]
    try:
        while all(p.poll() is None for p in procs):
            time.sleep(0.3)
    except KeyboardInterrupt:
        pass
    finally:
        for p in procs:
            if p.poll() is None:
                p.terminate()
        for p in procs:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()


def cmd_test(_args: argparse.Namespace) -> None:
    check_prereqs(need_node=True)
    ensure_setup()
    run([venv_python(), "-m", "pytest"], cwd=BACKEND)
    run([require("npm"), "run", "test"], cwd=FRONTEND)


def cmd_lint(_args: argparse.Namespace) -> None:
    check_prereqs(need_node=True)
    ensure_setup()
    run([venv_python(), "-m", "ruff", "check", "."], cwd=BACKEND)
    run([require("npm"), "run", "lint"], cwd=FRONTEND)
    run([require("npm"), "run", "typecheck"], cwd=FRONTEND)


COMMANDS = {
    "setup": cmd_setup,
    "dev": cmd_dev,
    "build": cmd_build,
    "run": cmd_run,
    "test": cmd_test,
    "lint": cmd_lint,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="instrument-cluster dev task runner")
    parser.add_argument("command", choices=sorted(COMMANDS), help="task to run")
    args = parser.parse_args()
    COMMANDS[args.command](args)


if __name__ == "__main__":
    main()
