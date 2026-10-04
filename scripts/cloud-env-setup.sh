#!/usr/bin/env bash
# Environment setup for cloud (Linux, root) sessions: paste into the environment's
# "Setup script" field, or run it by hand. Idempotent; a re-run skips what is installed.
#
# Installs what the repo's headless work needs:
#   - .NET SDK 8        scripts/test.sh and scripts/format.sh (the CI checks)
#   - Blender 5.0.x     blender/lib/build_object.py, build_shell.py (`blender -b -P ...`)
#   - GIMP 3.0.x        blender/lib/textures/gimp_headless.py (`gimp-console-3`)
#   - numpy + Pillow    system Python helpers (crops, atlas checks, splat converters)
#   - Git LFS content   blender/assets/*.blend etc. (checkouts here skip LFS smudging)
#
# Not installed: Unity and the Blender/GIMP/Unity MCP servers. Unity needs a licensed
# editor and the VPM-installed Worlds SDK, so the Unity half of the pipeline (import,
# scene build, bake, Quest rebuild, render checks) stays a local-machine job. The
# object-package and texture steps do run here, headless, without the MCPs.
set -euo pipefail

BLENDER_VERSION="${BLENDER_VERSION:-5.0.1}"
BLENDER_SHA256="${BLENDER_SHA256:-8019580ee1b7262e505f4196a00237ccf743c88d205b38d34201510676e60b09}"
GIMP_VERSION="${GIMP_VERSION:-3.0.8}"

log() { printf '\n==> %s\n' "$*"; }
SUDO=""; [ "$(id -u)" -eq 0 ] || SUDO="sudo"

REPO="$(git -C "$(dirname "$(readlink -f "$0")")" rev-parse --show-toplevel 2>/dev/null || true)"
[ -n "$REPO" ] || REPO="$(git rev-parse --show-toplevel 2>/dev/null || true)"

export DEBIAN_FRONTEND=noninteractive

# --- system packages ---------------------------------------------------------------
# Blender's headless build still links X11/GL client libraries; xvfb gives GIMP a display
# if a plug-in ever wants one; xz-utils unpacks the Blender tarball.
log "apt packages"
$SUDO apt-get update -qq
$SUDO apt-get install -y -qq --no-install-recommends \
    ca-certificates curl xz-utils git git-lfs xvfb \
    dotnet-sdk-8.0 \
    libgl1 libegl1 libxi6 libxkbcommon0 libsm6 libxrender1 libxxf86vm1 libxfixes3 \
    libxcursor1 libxrandr2 libxinerama1

# --- Python helpers ----------------------------------------------------------------
log "python: numpy, Pillow"
python3 -m pip install --quiet --break-system-packages numpy pillow 2>/dev/null \
    || python3 -m pip install --quiet numpy pillow

# --- Blender -----------------------------------------------------------------------
if [ ! -x /opt/blender/blender ] || ! /opt/blender/blender -b --version 2>/dev/null | grep -q "Blender ${BLENDER_VERSION%.*}"; then
    log "Blender ${BLENDER_VERSION}"
    tmp="$(mktemp -d)"
    curl -fsSL -o "$tmp/blender.tar.xz" \
        "https://download.blender.org/release/Blender${BLENDER_VERSION%.*}/blender-${BLENDER_VERSION}-linux-x64.tar.xz"
    echo "${BLENDER_SHA256}  $tmp/blender.tar.xz" | sha256sum -c -
    $SUDO rm -rf /opt/blender
    $SUDO mkdir -p /opt/blender
    $SUDO tar -xJf "$tmp/blender.tar.xz" -C /opt/blender --strip-components=1
    rm -rf "$tmp"
fi
$SUDO ln -sf /opt/blender/blender /usr/local/bin/blender

# --- GIMP 3 (headless) ---------------------------------------------------------------
# Ubuntu 24.04 only packages GIMP 2.10; gimp_textures.py needs the 3.0 API (Gimp/Gegl via
# gi). The upstream AppImage is unpacked rather than mounted (no FUSE needed). AppRun sets
# up the bundled libraries and Python, so the wrapper goes through it rather than calling
# the inner binary directly.
if [ ! -x /opt/gimp/AppRun ] || ! /opt/gimp/AppRun gimp-console-3 --version 2>/dev/null | grep -q "$GIMP_VERSION"; then
    log "GIMP ${GIMP_VERSION}"
    tmp="$(mktemp -d)"
    curl -fsSL -o "$tmp/gimp.AppImage" \
        "https://download.gimp.org/gimp/v${GIMP_VERSION%.*}/linux/GIMP-${GIMP_VERSION}-x86_64.AppImage"
    chmod +x "$tmp/gimp.AppImage"
    (cd "$tmp" && ./gimp.AppImage --appimage-extract >/dev/null)
    $SUDO rm -rf /opt/gimp
    $SUDO mv "$tmp/squashfs-root" /opt/gimp
    rm -rf "$tmp"
fi
$SUDO tee /usr/local/bin/gimp-console-3 >/dev/null <<'EOF'
#!/bin/sh
exec /opt/gimp/AppRun gimp-console-3 "$@"
EOF
$SUDO chmod +x /usr/local/bin/gimp-console-3

# --- repo: LFS content and hooks ---------------------------------------------------------
if [ -n "$REPO" ]; then
    cd "$REPO"
    log "git lfs (blend sources, models, textures, audio; ~180 MB)"
    git lfs install --local >/dev/null
    # Non-fatal: a session still works on scripts and C# without the binaries.
    git lfs pull || echo "warning: git lfs pull failed; blender/assets/*.blend are still pointer files"
    git config core.hooksPath .githooks
fi

# --- smoke test ----------------------------------------------------------------------
log "versions"
dotnet --version
blender -b --factory-startup --python-expr "import bpy; print('bpy', bpy.app.version_string)" 2>&1 | grep -E "^bpy|Blender [0-9]"
gimp-console-3 -i --batch-interpreter=python-fu-eval \
    -b "from gi.repository import Gimp; print('GIMP', Gimp.version())" --quit 2>&1 | grep -E "^GIMP"
python3 -c "import numpy, PIL; print('numpy', numpy.__version__, 'Pillow', PIL.__version__)"
log "setup complete"
