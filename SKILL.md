---
name: apartment
description: VRChat world recreating Cassidy's apartment — Unity world project at root, Worlds SDK via VPM, Blender-modeled, AGPL with a linking exception
---

# apartment

Unity 2022.3 VRChat world project at the repository root; a world *project*,
not a package, so nothing here is redistributed through VPM. The Worlds SDK
(`com.vrchat.worlds`) is pinned in `Packages/vpm-manifest.json`, installed by
the VPM client (or the vendored bootstrapper), and never enters git. Code is AGPL-3.0-or-later with the
VRChat/Unity linking exception in `LICENSE_ADDENDUM`.

## Repo Map

- `Assets/` — the world: scenes, models, materials, audio. Blender exports land here.
- `Packages/com.vrchat.core.bootstrap/` — VRChat's resolver bootstrapper, vendored byte-for-byte. Don't touch.
- `Packages/.gitignore` — allowlist inversion keeping resolver-installed packages out of git. Load-bearing.
- `ProjectSettings/` — pinned Unity project configuration (`ProjectVersion.txt` names the editor build).
- `scripts/` — the checks and builds; CI runs these same scripts, nothing else.
- `.github/workflows/ci-cd.yml` — lint-and-test on push/PR.
- `.githooks/pre-commit` — the fast checks; opt in with `git config core.hooksPath .githooks`.
- `Website/index.html` — placeholder package page; unthemed, unpublished, awaiting a future pass.
- `CREDITS.md` — intake ledger for everything third-party.

## Commands

```bash
scripts/check-meta.sh          # every visible file has a committed .meta
scripts/check-manifests.py     # package.json sanity across Packages/
scripts/format.sh --check      # dotnet-format over the CI-visible C#
scripts/test.sh                # headless NUnit run of Runtime/Core + Tests
```

## The SDK Boundary

- The VRChat SDK and Unity are proprietary; the repository must stay clonable,
  checkable, and testable without either installed.
- `Packages/*/Runtime/Core/` is engine-free C#. `scripts/test.sh` compiles it
  with plain dotnet against NUnit alone, so a `using UnityEngine` in Core is a
  CI failure, not a style nit. Engine and SDK glue lives outside Core and is
  exercised in the editor instead.
- Tests use classic NUnit asserts only: the same files must pass `dotnet test`
  and the editor's Test Runner, and the classic API is the overlap.
- Never weaken the `Packages/.gitignore` allowlist; it is what makes committing
  non-redistributable material structurally impossible.

## House Rules

- Every asset gets a `CREDITS.md` line at intake — source, author, license, URL. CC0 first.
- Open source first; proprietary assets never enter this repository.
- The linking exception in `LICENSE_ADDENDUM` is load-bearing legal text. Don't reword it casually.
