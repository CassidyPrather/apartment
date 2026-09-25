#!/usr/bin/env bash
# Builds every committed package into dist/ as both a VPM .zip and a
# .unitypackage. CI runs this same script on release, so it stays the single
# source of truth for artifact layout and naming.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

rm -rf dist/packages
mkdir -p dist/packages

built=0
for manifest in $(git ls-files -- Packages | grep -E '^Packages/[^/]+/package\.json$'); do
    directory=$(dirname "$manifest")
    id=$(basename "$directory")
    case "$id" in
        # Vendored VRChat material is not ours to publish.
        com.vrchat.*) continue ;;
    esac

    version=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["version"])' "$manifest")

    zip_path="dist/packages/$id-$version.zip"
    (cd "$directory" && zip -qr "../../$zip_path" .)
    scripts/unitypackage.py "$directory" "dist/packages/$id-$version.unitypackage"

    for artifact in "$zip_path" "dist/packages/$id-$version.unitypackage"; do
        echo "built: $artifact ($(wc -c < "$artifact") bytes)"
    done
    built=$((built + 1))
done

if [ "$built" -eq 0 ]; then
    echo "build-packages: no committed packages under Packages/; nothing to release" >&2
    exit 1
fi
