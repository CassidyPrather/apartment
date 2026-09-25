# Apartment

A VRChat world recreating Cassidy's apartment: modeled in Blender from photos
and a floor plan, then furnished with the basics (a video player, VRC Light
Volumes, ambient sound). Open source wherever possible.

## Development

Requires Unity 2022.3.22f1 (see `ProjectSettings/ProjectVersion.txt`) via a VPM
client (prefer [ALCOM](https://vrc-get.anatawa12.com/en/alcom/)).
Requires [.NET SDK](https://dotnet.microsoft.com/download) 8 for headless checks.

Open: add this folder as a project in your VPM client and open it in Unity. The
Worlds SDK (`com.vrchat.worlds`) is pinned in `Packages/vpm-manifest.json`; the
client, or `vrc-get resolve`, installs it.

Test (editor): Window > General > Test Runner, EditMode tab

```bash
scripts/check-meta.sh          # every visible file has a committed .meta
scripts/check-manifests.py     # package.json sanity across Packages/
scripts/format.sh --check      # dotnet-format over the CI-visible C#
scripts/test.sh                # headless NUnit run of Runtime/Core + Tests
```

### Advanced

Pre-commit hook: `git config core.hooksPath .githooks` (runs the meta and
manifest checks)

See [docs/GETTING_STARTED.md](docs/GETTING_STARTED.md) for curated links:
tooling, docs, asset sources, and so on and so forth.

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
by way of Cassidy's vpm-package-template. Third-party assets: see
[CREDITS.md](CREDITS.md).
