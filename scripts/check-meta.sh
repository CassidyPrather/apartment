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

# Any meta whose subject is gone? A subject is a tracked file or a directory
# that still holds one. Compared with comm rather than per-meta
# `printf | grep -q`: under pipefail, grep -q exiting at its first match
# SIGPIPEs printf once the list outgrows the pipe buffer, which turned live
# metas into random "stale" reports.
subjects=$(printf '%s\n%s\n' "$files" "$dirs" | sed '/^$/d' | sort -u)
stale=$(comm -23 <(printf '%s\n' "$metas" | sed '/^$/d' | sed 's/\.meta$//' | sort -u) \
    <(printf '%s\n' "$subjects"))
if [ -n "$stale" ]; then
    printf '%s\n' "$stale" | sed 's/^\(.*\)$/check-meta: stale meta (its subject is no longer tracked): \1.meta/'
    status=1
fi

[ "$status" -eq 0 ] && echo "check-meta: ok"
exit "$status"
