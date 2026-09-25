# VPM Package Template

Cassidy's opinionated template for VRChat avatars, worlds, and the VPM packages
that ship them. Enter at your own peril.

## Development

Requires Unity 2022.3.22f1 (see `ProjectSettings/ProjectVersion.txt`) via a VPM
client (prefer [ALCOM](https://vrc-get.anatawa12.com/en/alcom/)).
Requires [.NET SDK](https://dotnet.microsoft.com/download) 8 for headless checks.

Open: add this folder as a project in your VPM client, add the SDK you picked
in Template Setup, then open in Unity

Test (editor): Window > General > Test Runner, EditMode tab

```bash
scripts/check-meta.sh          # every visible file has a committed .meta
scripts/check-manifests.py     # package.json sanity across Packages/
scripts/format.sh --check      # dotnet-format over the CI-visible C#
scripts/test.sh                # headless NUnit run of Runtime/Core + Tests
scripts/build-packages.sh      # VPM .zip + .unitypackage per package -> dist/
```

### Advanced

Pre-commit hook: `git config core.hooksPath .githooks` (runs the meta and
manifest checks)

Release:

1. Bump `version` in the package's `package.json`
2. Commit and push
3. Create a GitHub release tagged with that version — CI attaches the `.zip`
   and `.unitypackage` for every package whose version matches the tag
4. Add the repository to your listing's `githubRepos`
   ([CassidyPrather/vpm](https://github.com/CassidyPrather/vpm)) once; every
   later release is picked up from the release assets automatically

## Template Setup

1. **Create a new repository** from this template on GitHub (click "Use this
   template")

2. **Clone your new repository** and navigate to it

3. **Pick a flavor.** The four supported shapes are avatar *project*, world
   *project* (yours alone, nothing redistributable), avatar *package*, and
   world *package* (a redistributable under `Packages/`). Whichever you pick,
   add the matching SDK to the project via your VPM client:
   `com.vrchat.avatars` or `com.vrchat.worlds` — never both; they refuse to
   coexist.

4. **Project, not package?** Gut the package scaffolding:
   - Delete `Packages/net.wirenook.package-template/`
   - Remove the `!net.wirenook.package-template` line from `Packages/.gitignore`
   - Remove `net.wirenook.package-template` from `testables` in
     `Packages/manifest.json`
   - Delete the `build-and-publish` job from `.github/workflows/ci-cd.yml`,
     plus `scripts/build-packages.sh` and `scripts/unitypackage.py`
   - Everything else stays: the checks and headless tests degrade cleanly to
     "nothing to do" until you give them something, and the meta check earns
     its keep on `Assets/` alone

5. **Package? Rename the sample** everywhere its name is hardcoded:
   - The `Packages/net.wirenook.package-template/` directory itself
   - `package.json`: `name`, `displayName`, `description`, and `author`
   - Both `.asmdef` file names and their `name` fields, and the Tests asmdef's
     reference to the Runtime assembly
   - The `!net.wirenook.package-template` line in `Packages/.gitignore`
   - The `testables` entry in `Packages/manifest.json`
   - Declare the SDK in `vpmDependencies`, e.g.
     `"com.vrchat.avatars": "^3.7.0"`

6. **Vendored proprietary assets** — keep or strip:
   - Keep: create a *private* repository for the assets and mount it:
     `git submodule add <private-remote> Assets/Vendor`. Open Unity once,
     commit the generated `Assets/Vendor.meta`, and from then on
     `git clone --recurse-submodules` Just Works. See Vendored assets below.
   - Strip: delete the Vendored assets section from this README. That's it —
     the mechanism is git itself, so there is nothing else to remove.

7. **Update the README**: replace the title and description, remove or
   customize this Template Setup section

8. **Verify everything works**:

   ```bash
   scripts/check-meta.sh
   scripts/check-manifests.py
   scripts/test.sh
   scripts/build-packages.sh
   ```

### Replacing the demo

The sample package exists so the template ships exercised, not because it is
precious. Its full blast radius, in gutting order:

1. `Runtime/Core/Easing.cs` — replace wholesale. Keep the shape: pure C#, no
   UnityEngine, no SDK. Everything in `Runtime/Core/` is compiled by
   `scripts/test.sh` against nothing but the standard library and NUnit, so a
   stray engine reference there fails CI — that is the fence working, not a
   bug.
2. `Tests/Editor/EasingTests.cs` — rewrite against your logic. Stick to the
   classic asserts; the same files run under `dotnet test` in CI and the Unity
   Test Runner in the editor.
3. `Editor/PackageTemplateMenu.cs` — demo-specific; replace or delete.
4. `Runtime/` outside `Core/` is where MonoBehaviours and SDK-facing glue go.
   CI compiles none of it, the editor all of it.

Nothing else references the demo.

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for curated links:
tooling, docs, avatar frameworks, asset sources, and so on and so forth.

## Vendored assets

Proprietary assets — store purchases, licensed packs — must never be published
in this repository. They live in a *private* repository mounted as a submodule
at `Assets/Vendor`; clone with `--recurse-submodules` and they Just Work.
Because `.unitypackage` imports preserve GUIDs, anyone who imports their own
licensed copy of the same pack gets the same GUIDs — so references from
committed prefabs and scenes into vendored assets survive for people who can't
see your submodule at all.

Clones without access still open fine: git leaves `Assets/Vendor` empty and
Unity shrugs. CI clones without submodules on purpose — it is the standing
proof that nothing tracked *requires* the private half. Record each pack in
[CREDITS.md](CREDITS.md), license column included, even though the bytes stay
private.

## Legal

Copyright 2026 Cassidy Prather <cassidy@wirenook.net>

Everything in this repository henceforth is licensed under
[AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html) (See `LICENSE`) unless
otherwise specified.

As a special exception, the copyright holders give permission to link this
Program with the VRChat SDK and with Unity Technologies' proprietary engine
components, and to convey the resulting work under terms of your choice,
provided that you also convey the Corresponding Source of this Program under
the terms of the GNU Affero General Public License version 3 in all other
respects. (This exception also in `LICENSE_ADDENDUM`.)

## Credits

Descended from https://github.com/vrchat-community/template-package
([VRCHAT DISTRO LICENSE FILE](https://github.com/vrchat-community/template-package/blob/d9cf13fe9f56867cbf7315a4dbbf1901bc1537ec/Packages/com.vrchat.core.bootstrap/License.md))

Vendored third-party material is inventoried in [CREDITS.md](CREDITS.md).
