#!/usr/bin/env bash
# Every file Unity can see needs a committed .meta, and every committed .meta
# must still point at something -- half-orphaned metas are how GUID references
# rot. Unity only generates metas locally, so git is where the check belongs.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

# Paths Unity imports: everything under Assets/, and everything inside a
# package directory under Packages/. Hidden entries (leading dot) and folders
# ending in ~ are invisible to Unity and exempt; files directly under
# Packages/ (manifests, lockfiles) are configuration, not assets.
candidates=$(git ls-files -- Assets Packages \
    | grep -vE '(^|/)\.[^/]*(/|$)' \
    | grep -vE '(^|/)[^/]*~(/|$)' \
    | grep -vE '^Packages/[^/]+$' \
    || true)

if [ -z "$candidates" ]; then
    echo "check-meta: nothing tracked under Assets/ or Packages/*/; nothing to do"
    exit 0
fi

files=$(printf '%s\n' "$candidates" | grep -v '\.meta$' || true)
metas=$(printf '%s\n' "$candidates" | grep '\.meta$' || true)

# Directories are implicit in git; every ancestor below Assets/ or the package
# root needs a folder meta of its own.
dirs=$(printf '%s\n' "$files" \
    | awk -F/ '{p=$1; for (i = 2; i < NF; i++) {p = p "/" $i; print p}}' \
    | grep -vE '^(Assets|Packages)$' \
    | grep -vE '^Packages/[^/]+$' \
    | sort -u || true)

status=0

# Anything visible without a matching meta?
wanted=$(printf '%s\n%s\n' "$files" "$dirs" | sed '/^$/d' | sed 's/$/.meta/' | sort -u)
missing=$(comm -23 <(printf '%s\n' "$wanted") <(printf '%s\n' "$metas" | sort -u))
if [ -n "$missing" ]; then
    echo "check-meta: missing .meta files (open the project in Unity to generate, then commit them):"
    printf '%s\n' "$missing" | sed 's/^/  /'
    status=1
fi

# Any meta whose subject is gone?
while IFS= read -r meta; do
    [ -z "$meta" ] && continue
    target=${meta%.meta}
    if ! printf '%s\n' "$files" | grep -qxF "$target" \
        && ! printf '%s\n' "$files" | grep -q "^$(printf '%s' "$target" | sed 's/[].[^$*\\]/\\&/g')/"; then
        echo "check-meta: stale meta (its subject is no longer tracked): $meta"
        status=1
    fi
done <<< "$metas"

[ "$status" -eq 0 ] && echo "check-meta: ok"
exit "$status"
