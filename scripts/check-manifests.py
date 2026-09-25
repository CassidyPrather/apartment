#!/usr/bin/env python3
"""Validates the committed package manifests under Packages/*/package.json.

The VPM listing copies each package.json into the listing verbatim, so a
malformed manifest ships broken metadata to every consumer; cheaper to catch
it here. VRChat's own vendored packages (com.vrchat.*) are skipped -- they are
not ours to lint.
"""

import json
import re
import subprocess
import sys

# Bare X.Y.Z plus an optional prerelease tag; the VPM resolver understands
# nothing fancier.
SEMVER = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?$")
REVERSE_DNS = re.compile(r"^[a-z0-9]+(\.[a-z0-9-]+)+$")


def tracked_manifests():
    out = subprocess.run(
        ["git", "ls-files", "--", "Packages"],
        capture_output=True, text=True, check=True,
    ).stdout
    return [
        path for path in out.splitlines()
        if re.fullmatch(r"Packages/[^/]+/package\.json", path)
        and not path.startswith("Packages/com.vrchat.")
    ]


def main():
    problems = []
    manifests = tracked_manifests()
    for path in manifests:
        directory = path.split("/")[1]
        try:
            with open(path, encoding="utf-8") as handle:
                manifest = json.load(handle)
        except json.JSONDecodeError as error:
            problems.append(f"{path}: not valid JSON ({error})")
            continue

        name = manifest.get("name", "")
        if name != directory:
            problems.append(
                f"{path}: name {name!r} does not match its directory {directory!r}"
            )
        if not REVERSE_DNS.fullmatch(name):
            problems.append(f"{path}: name {name!r} is not lowercase reverse-DNS")
        if not SEMVER.fullmatch(manifest.get("version", "")):
            problems.append(
                f"{path}: version {manifest.get('version')!r} is not semver"
            )
        if not manifest.get("unity"):
            problems.append(f"{path}: missing \"unity\" (the minimum editor version)")
        if not manifest.get("license"):
            problems.append(
                f"{path}: missing \"license\" (the listing propagates it; "
                "this repo's default is AGPL-3.0-or-later)"
            )
        if not manifest.get("author", {}).get("name"):
            problems.append(f"{path}: missing author.name")

    for problem in problems:
        print(f"check-manifests: {problem}", file=sys.stderr)
    if not problems:
        count = len(manifests)
        print(f"check-manifests: ok ({count} manifest{'s' if count != 1 else ''})")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
