---
name: apartment
description: VRChat world recreating Cassidy's apartment — Unity world project at root, Worlds SDK via VPM, modeled from scratch in Blender by Claude, PC + Quest, AGPL with a linking exception
---

# apartment

Unity 2022.3 VRChat world project at the repository root; a world *project*,
not a package, so nothing here is redistributed through VPM. The Worlds SDK
(`com.vrchat.worlds`) is pinned in `Packages/vpm-manifest.json`, installed by
the VPM client (or the vendored bootstrapper), and never enters git. Code is AGPL-3.0-or-later with the
VRChat/Unity linking exception in `LICENSE_ADDENDUM`.

Claude does all of the production work: modeling, UV mapping, texturing, and
placing everything in Unity. Cassidy directs and reviews. That makes visual
verification the core of the workflow. Claude cannot claim something looks
right without having looked at it.

## Repo Map

- `Assets/` — the world: scenes, models, materials, audio. Blender exports land here.
- `Assets/Apartment/` — our content: `Models/` (FBX exports), `Textures/` (GIMP atlases),
  `Materials/`, `Prefabs/`, `Scripts/` (UdonSharp), `Editor/` (the `Apartment/...` setup
  menu items that rebuild materials, prefabs and test scenes from the exports), `Scenes/`.
- `blender/lib/` — Python build scripts (run headless with `blender -b -P` or through the Blender MCP).
- `blender/assets/` — committed `.blend` sources (LFS).
- `blender/out/` — generated renders, contact sheets, QA JSON; gitignored and always regenerable.
- `Reference/` — floor plan estimates, measurements, apartment photos. Local-only and gitignored. See Privacy.
- `Packages/com.vrchat.core.bootstrap/` — VRChat's resolver bootstrapper, vendored byte-for-byte. Don't touch.
- `Packages/.gitignore` — allowlist inversion keeping resolver-installed packages out of git. Load-bearing.
- `ProjectSettings/` — pinned Unity project configuration (`ProjectVersion.txt` names the editor build).
- `scripts/` — the checks and builds; CI runs these same scripts, nothing else.
- `.github/workflows/ci-cd.yml` — lint-and-test on push/PR.
- `.githooks/pre-commit` — the fast checks; opt in with `git config core.hooksPath .githooks`.
- `Website/index.html` — placeholder package page; unthemed, unpublished, awaiting a future pass.
- `CREDITS.md` — intake ledger for everything third-party, plus the parody brand ledger.

## Commands

```bash
scripts/check-meta.sh          # every visible file has a committed .meta
scripts/check-manifests.py     # package.json sanity across Packages/
scripts/format.sh --check      # dotnet-format over the CI-visible C#
scripts/test.sh                # headless NUnit run of Runtime/Core + Tests
```

## References

`Reference/` grows over time. It holds photos now, and later more photos, video,
and possibly gaussian splats. All of it is local-only.

- Measurements beat estimates, and estimates beat guesses. Until tape-measured values
  arrive, build from `floor-plan-estimates.md` and mark those values as
  estimates in the dimensions data file. When real measurements land, update the data file
  and rebuild.
- Splats and video are spatial reference. Use them for proportions,
  placement, and extracting stills. They never ship, just like photos.
- When new references arrive, check whether they contradict built work, and
  list any conflicts in the next milestone review.
- If an object needs a view the references don't cover, ask Cassidy for a
  shot instead of inventing detail, and keep building the parts you can.
- The first references are a trial run for the process itself. When a
  milestone teaches something (a better verification camera, a texture
  recipe, a budget number), update this file in that milestone's commit.

## Privacy

The world is modeled on a real home, and the published world must not identify
it or anyone connected to it.

- Full reference photos never enter the repository; they stay in `Reference/`.
  Textures may use photo pixels (see Modeling From Scratch), but only as
  processed texture material, never as a stand-in for the original photo.
- The street address, complex name, and floor plan name never appear in
  committed files, in-world text, object names, or commit messages. Use
  neutral names instead, for example "the apartment", "bedroom", "north wall".
- In-world content carries no PII: no real names, faces, mail, documents,
  personal photos, screen contents, or views out the windows that could identify the location.
- Repo metadata is exempt: Cassidy's name and email in the copyright,
  authorship, and descriptions stay as they are.
- If you find PII already committed, stop, flag it to Cassidy, and propose the scrub.
  Don't just work around it.

## Branding

Real products get parody brands. No real brand ever appears in the world.

- Replace every real brand name or logo with a silly parody name and a newly
  drawn parody logo (GIMP or Inkscape). Claude picks the names.
- This covers textures, in-world text, object/material/file names, and commit messages.
- Record each parody in the brand ledger in `CREDITS.md`: parody name, the
  object it appears on, and a neutral description. Never record the real brand. Reuse
  an existing parody name before inventing a new one so the world stays consistent.

## Modeling From Scratch

- Model and texture from scratch by default. Don't use AI-generated models
  (Hyper3D, Hunyuan, etc.) or asset store content; the Blender MCP's generation tools are off limits.
- A downloaded model is allowed when its license is compatible with this repository
  (CC0 or CC-BY; never personal-use, editorial, or unlicensed), it gets a
  `CREDITS.md` line at intake, and every real brand shape, logo, and text on it is
  replaced per Branding. If nothing with a usable license exists, model it. Textures
  are still made here (see below), never downloaded.
- Textures are made from scratch too, and the pixel work happens in GIMP 3 (logos
  are drawn as SVG in Inkscape and composited in GIMP; G'MIC is fine for filters).
  Keep the GIMP code in the repo so atlases can be regenerated.
- Builds run headless: `blender -b` for models and `blender/lib/textures/gimp_headless.py`
  for textures. Headless runs don't block each other, so objects are built in parallel
  by separate agents, each owning its own files. The coordinator reviews each finished
  object in the live Blender and GIMP through their MCPs (rebuild it there, open its
  atlas) and assembles the rooms in the live Blender, so the work stays visible on
  Cassidy's screen recordings.
- Fill the apartment coarse-to-fine: block in every room's big pieces first (shell,
  doors, built-ins, large furniture and appliances), then lighting and an uploadable
  build, then smaller objects and detail. A walkable, complete apartment beats a few
  perfect objects if time runs out.
- Splats arrive over time (another agent announces each finished training). Use both
  the splat and the photos it was trained from: the splat for 3D shape and placement,
  the photos for colour and detail.
- The apartment photos can go into textures. Crop, perspective-correct,
  make tileable, and color-match regions of them (carpet, countertop,
  wood grain) in GIMP. The finished texture must still pass the Privacy and
  Branding rules. Check every photo-derived texture at full resolution for
  reflections, people, readable text, and logos before committing it.
- Allowed non-art dependencies: a video player and VRC Light Volumes, plus any
  shaders they need (Mochie's shaders, for Light Volumes). Each goes through the intake rules below.
- Views out the windows show a made-up exterior, built from scratch like
  everything else and resembling nothing identifiable.

### Fidelity

Match the real apartment as closely as the references allow: architecture,
furniture, fixtures, and décor. Get the proportions, placement, materials, and wear right.
Where the real thing carries PII or a brand, change only that detail (see
Privacy and Branding) and keep the rest faithful. Where the Quest budget
forces a simplification, keep the silhouette and color and spend the detail
where a visitor looks.

### Separate Pieces

Each object is its own mesh, FBX, and prefab: the router on the cabinet is not part
of the cabinet. Items that rest on furniture are placed with `place_<item>` marker
empties exported from the furniture's FBX, and a set prefab puts them together.

### Interactive Furniture

If it moves in the real apartment, it moves in the world: drawers pull out,
cabinet and closet doors swing, and so on. Default to grab-and-pull (a VRC Pickup
on an invisible handle driving the part along its travel, synced) rather than
click-to-toggle. Drawers use `Assets/Apartment/Scripts/SlidingDrawer.cs`; the grab
handle's position comes from a `<part>_grab` marker empty exported with the model.
Moving parts are not static and get colliders that move with them.

### Source of Truth, Case by Case

Pick per object and record the choice in the object's script or `.blend`:

- **Scripted** (`blender/lib/`): anything driven by measurements or repeated
  structure, such as walls, floors, ceilings, door and window openings, trim, cabinets,
  counters, and shelving. Dimensions live in one data file, so a corrected tape
  measurement rebuilds everything downstream.
- **Hand-built `.blend`** (`blender/assets/`, via the Blender MCP): organic or
  one-off pieces where a script would fight the shape, such as upholstered furniture,
  bedding, and plants.
- When in doubt, start scripted. Converting a script to a hand-edited file is easy, and going the other way is not.

### Conventions

- Measurements arrive in feet and inches. Blender and Unity work in meters (1 unit = 1 m).
  Convert once, in the data file.
- Blender is Z-up, Unity is Y-up. Export FBX with transforms applied, so every
  object arrives at scale 1 with a zero rotation.
- Objects, materials, and textures use lowercase `snake_case` names that describe the thing
  (`kitchen_counter_north`), never a brand.
- Every mesh gets clean UVs, with a checker-texture pass before any real texture
  goes on, and a second UV channel for lightmaps.

## Platforms and Budgets

The world targets both PC and Quest (Android). Every change must work on both.

- Every material uses a shader that supports VRC Light Volumes and falls back to Unity
  light probes when a scene has none. Today that's `Mochie/Standard Mobile`
  (vendored in `Assets/Mochie/`), which also runs on Quest. VRChat's own mobile
  shaders ignore Light Volumes, so don't use them. When Mochie updates, re-vendor
  the same subset and check which Light Volumes version its `LightVolumes.cginc` matches.
- No real-time lights. Static surfaces use baked lightmaps, and anything that moves
  (drawers, avatars, pickups) is lit by Light Volumes.
- Keep the Android upload well under VRChat's size limit. Prefer texture
  atlases, sensible texture resolutions (1K by default, 2K when you can justify it),
  and crunch/ASTC compression.
- Keep draw calls and materials low: share materials, merge static geometry, and
  mark static objects static.
- Yardstick: the filing cabinet set (cabinet, router, modem, headset, cable stubs)
  is about 11k triangles, 6 materials, and 8 MB of ASTC texture memory on Android.
  Masks and emission maps are capped at 512 px.
- The video player has to use a backend that works on Quest.

## Visual Verification

Nothing that changes art or the scene is committed until Claude has looked at it.

1. **Blender:** render the change from the fixed verification cameras
   (defined in `blender/lib/`) into a contact sheet in `blender/out/`. Look at
   it, and where it helps, compare it side by side with the reference photos.
   Photos are for comparison only and never go into outputs you plan to commit.
2. **UVs:** render with a checker texture and look for stretching,
   seams in visible places, and inconsistent texel density.
3. **Materials:** do a lit render and check color, roughness, and scale against the reference.
4. **Unity:** check the Scene/Game view from the matching viewpoints via the Unity MCP.
   The console must be free of new errors and warnings, and the scene must be checked on
   both the PC and Android build targets.
5. The Unity editor is the acceptance gate. This is a static world, so what the editor shows is
   what VRChat shows, for the most part. Cassidy tests in-client when it suits
   them, and milestones never wait on it. For anything the editor can't show
   faithfully (video playback, Quest performance, mirror/shader quirks), add a
   "check in VRChat" item to the milestone review.
6. If a result looks wrong, fix it and verify again. If you can't tell whether it
   is right, stop and show Cassidy the screenshots instead of guessing.

## Git Workflow

- Commit directly to `main` after each verified milestone. A milestone is one
  coherent, visually checked step, such as "bedroom walls and openings" or "kitchen
  counters UV'd and textured".
- Before committing, run the Commands above and require them to pass. Review the staged
  files for photos, PII, and real brands. The Privacy and Branding rules
  are commit gates.
- Binary art goes through Git LFS (`.gitattributes`). Check that new binary
  types are covered before you commit them.
- Never push unless Cassidy asks.

## Milestone Reviews

After each milestone commit, publish a review artifact so Cassidy can check the
work asynchronously. Each artifact is a private claude.ai page (Artifact tool)
titled `Milestone NN: <name>` and contains:

- What changed and why, the commit hash, and which objects were scripted and which were hand-built.
- The verification renders: contact sheets, the UV checker pass, lit renders, and
  Unity views. Label each one with its camera or viewpoint.
- Budget notes: triangle counts, texture sizes, material count, and any Quest concerns.
- Parody brands introduced, if any.
- Open questions and known issues, including anything that doesn't match the reference yet.

Never put full reference photos or other PII in a review artifact;
photo-derived textures are fine. Compare against
the reference in words instead ("counter reads darker than the photo").

Keep going with the next milestone after publishing. Treat Cassidy's feedback
(artifact comments or chat) as the top priority for the next milestone, and fix
it before starting new work.

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

- Every third-party inclusion gets a `CREDITS.md` line at intake: source,
  author, license, and URL. Prefer CC0.
- Open source first; proprietary assets never enter this repository.
- The linking exception in `LICENSE_ADDENDUM` is load-bearing legal text. Don't reword it casually.
