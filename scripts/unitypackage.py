#!/usr/bin/env python3
"""Builds a .unitypackage from a package directory. Stdlib only, on purpose:
the alternative is a third-party GitHub Action, and vendoring a build system
to make a tarball is how listings end up unbuildable in five years.

A .unitypackage is a gzipped tar with one directory per asset, named by the
asset's GUID, holding `pathname` (where the asset lands on import), the
asset's `.meta`, and -- for files, not folders -- the asset bytes themselves
as `asset`. Unity re-homes everything by pathname on import, and because GUIDs
travel with the package, cross-asset references survive the trip.

Usage: unitypackage.py <package-directory> <output.unitypackage>
"""

import gzip
import io
import re
import sys
import tarfile
from pathlib import Path

GUID = re.compile(r"^guid: ([0-9a-f]{32})\s*$", re.MULTILINE)


def visible(path):
    """Mirrors Unity's import rules: hidden entries and `~` folders are not assets."""
    return not any(
        part.startswith(".") or part.endswith("~") for part in path.parts
    )


def add_entry(tar, name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    # Fixed metadata so an unchanged package rebuilds byte-for-byte.
    info.mtime = 0
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    tar.addfile(info, io.BytesIO(data))


def main():
    if len(sys.argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    package_dir = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    package_id = package_dir.name

    metas = sorted(
        path for path in package_dir.rglob("*.meta")
        if visible(path.relative_to(package_dir))
    )
    if not metas:
        print(f"unitypackage: no .meta files under {package_dir}", file=sys.stderr)
        return 1

    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as tar:
        for meta in metas:
            subject = meta.with_suffix("")
            if not subject.exists():
                print(f"unitypackage: stale meta {meta}", file=sys.stderr)
                return 1

            meta_bytes = meta.read_bytes()
            match = GUID.search(meta_bytes.decode("utf-8", errors="replace"))
            if not match:
                print(f"unitypackage: no guid in {meta}", file=sys.stderr)
                return 1
            guid = match.group(1)

            relative = subject.relative_to(package_dir).as_posix()
            pathname = f"Packages/{package_id}/{relative}"
            add_entry(tar, f"{guid}/pathname", pathname.encode())
            add_entry(tar, f"{guid}/asset.meta", meta_bytes)
            if subject.is_file():
                add_entry(tar, f"{guid}/asset", subject.read_bytes())

    out_path.parent.mkdir(parents=True, exist_ok=True)
    # mtime=0 for the same reproducibility reason as the tar entries.
    with open(out_path, "wb") as handle:
        with gzip.GzipFile(fileobj=handle, mode="wb", mtime=0) as compressed:
            compressed.write(buffer.getvalue())
    return 0


if __name__ == "__main__":
    sys.exit(main())
