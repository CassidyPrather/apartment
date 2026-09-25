"""Run texture builders from gimp_textures.py in a headless GIMP (no window, no MCP).

    python blender/lib/textures/gimp_headless.py shell_trim router [--timeout 600]

Each call starts its own gimp-console process (brushes and fonts load, which the pencil
strokes and SVG logo text need), so several can run in parallel (one per
object agent). Prints GIMP's output and exits non-zero if GIMP fails or times out.
"""

import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCRIPT = os.path.join(HERE, "gimp_textures.py")


def gimp_console():
    for c in (shutil.which("gimp-console-3"), r"C:\Program Files\GIMP 3\bin\gimp-console-3.exe",
              "/usr/bin/gimp-console-3"):
        if c and os.path.exists(c):
            return c
    raise SystemExit("gimp-console-3 not found")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("builders", nargs="*", help="function names in gimp_textures.py")
    ap.add_argument("--object", help="build objects/<name>/textures.py (its build() function)")
    ap.add_argument("--timeout", type=int, default=600)
    a = ap.parse_args()
    calls = "; ".join(f"G[{b!r}]()" for b in a.builders)
    if a.object:
        obj = os.path.join(HERE, "..", "objects", a.object, "textures.py")
        # the object's texture script runs with the shared helpers already in its globals
        calls += f"; exec(open({obj!r}, encoding='utf-8').read(), G); G['build']()"
    if not calls.strip("; "):
        ap.error("name a builder or --object")
    code = (f"G = {{'ROOT': {ROOT!r}, 'RUN': False, 'SHOW': False}}; "
            f"exec(open({SCRIPT!r}, encoding='utf-8').read(), G); {calls.strip('; ')}")
    cmd = [gimp_console(), "-i", "--batch-interpreter=python-fu-eval",
           "-b", code, "--quit"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=a.timeout)
    except subprocess.TimeoutExpired:
        sys.exit(f"GIMP timed out after {a.timeout}s")
    sys.stdout.write(r.stdout)
    sys.stderr.write(r.stderr)
    if r.returncode != 0 or "Traceback" in r.stderr + r.stdout:
        sys.exit(r.returncode or 1)


if __name__ == "__main__":
    main()
