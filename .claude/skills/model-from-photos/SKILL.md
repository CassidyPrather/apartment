---
name: model-from-photos
description: The apartment world's current build pipeline - object packages built headless in Blender, textures in headless GIMP, then Unity import / scene build / bake / Quest rebuild, render checks and commit. Use when modelling or fixing any object from the reference photos and captures, or when rebuilding the Unity scene.
---

# Model From Photos: the pipeline

The rules (Privacy, Branding, Fidelity, budgets, git) are in the repo `SKILL.md`. This
file is the mechanics. Parallel object agents get `object-agent-brief.md`.

## 1. Evidence first

- Photos: `Reference/IMG_*.jpg`, `PXL_*.jpg`. Capture frames:
  `Reference/lidarseries-splat/*/COLMAP_Text_Model/images/wide_*.jpg`. Per-object work
  folders `Reference/<name>_work/` often already hold crops and photo|render|overlay
  sheets (`sbs_*.jpg`); look there before re-deriving anything.
- `Read` downsamples; crop at full resolution with PIL (use `r'C:/...'` paths in
  `python -c`, never `$TEMP` with backslashes).
- Model only what the evidence shows. Tag every dimension SCAN / PHOTO / TAPE / EST in
  the package docstring. List gaps as exact photo requests.

## 2. Build an object package

`blender/lib/objects/<name>/object.py` (+ `textures.py`, `logos/*.svg`). Contract in
`blender/lib/build_object.py`'s docstring. Plan-coordinate packages sit on a marker at
(0,0,0) in `shell_layout.py` PLACES; `<pkg>__<suffix>` places another copy.

```bash
"/c/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b --factory-startup \
  -P blender/lib/build_object.py -- <name> [--no-render]      # FBX + manifest + blender/out/<name>/
python blender/lib/textures/gimp_headless.py --object <name>   # atlas PNGs
"/c/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b --factory-startup --python-expr \
  "STEPS={'render':False,'export':True}; __file__=r'C:/Source/apartment/blender/lib/build_shell.py'; exec(open(__file__).read())"
```
Rebuild the shell whenever PLACES changes (the markers live in the shell FBX). After a
texture run, check the PNG mtimes: a Unity file lock makes writes fail silently.

Gotchas:
- `common.Builder.to_object()` orients normals as if pieces were closed: open bowls
  (sinks, tubs) come out inside out and Unity culls them. Add a pass that faces the
  bowl's faces toward an eye above it (`vanity`, `kitchen_cabinets._face_bowls_up`).
- Unity culls back faces; thin sheets (liners, cloth) need both windings.
- Transparent parts: a second material `{"mode": "transparent", "alpha": a}` in
  MATERIALS, a region aliased in the atlas, `collapse_materials` mapping to it.
- Fully metallic greys mirror the brown room; worn steel reads right at metallic ~0.6.
- Organic things (cloth, plushes, futon) are modelled or simulated in the live Blender
  MCP and saved to `blender/assets/<name>.blend`; the package appends from it.
  Cloth: collision objects must be visible; recreate the object to rerun a cached sim;
  `create_grid(x_segments=n)` gives n+1 verts per row; solidify side decides what pokes
  through a layer on top; lift a top layer off the one below with a smoothed push, never
  per-vertex (it tears).

## 3. Unity (UnityMCP, port 8080; the user runs /mcp if it dropped)

Order, each waited on in `%LOCALAPPDATA%/Unity/Editor/Editor.log` (menu calls time out
or disconnect during domain reloads; that is normal):
1. `Apartment/Import Objects`: count `[ObjectImporter] done` lines BEFORE the call and
   wait for a NEW one. Building before it lands gives 0-vertex atlased meshes or misses
   new prefabs (check with a 0-vertex count over `apartment`'s MeshFilters).
2. `Apartment/Build Apartment Scene`: wait for a new `[ApartmentSetup] done`; check the
   `[DoorSetup]` door count.
3. `Apartment/Bake Lighting`: wait for a new `occlusion baked` (~3-4 min). Never edit C#
   during a bake.
4. After committing the PC scene: `Apartment/Build Quest Scene` (another bake), commit
   `apartment_quest*`, then reopen `Assets/Apartment/Scenes/apartment.unity`.

Render checks via `execute_code` (plan inches -> Unity: `U(x,y,z) = (-x*S, z*S, -y*S)`,
`S = 0.0254*1.2`): a temp Camera + RenderTexture, `ReadPixels`, write PNGs to
`blender/out/<dir>/`, destroy everything. Set `cam.useOcclusionCulling = false` if the
scene changed since the last bake. Write `UnityEngine.Object`, not `Object`. Raycast with
temporary MeshColliders to find what a pixel is (filter to your colliders).
Hard edges on probe-lit moving parts are Light Volume boundaries (see
`LightingSetup.OpenEdges`), not textures.

## 4. Ship

- `git add -A -- . ':!<untracked junk>'`; the pre-commit hook runs the checks.
- Before any push: `git log origin/main..main --name-only --format=` must list none of
  the gitignored photo albedos (bedroom_fixtures, living_wall_art, desk_computer,
  own_art, media_hutch_art, cassette_player_art).
- Parody names go in the `CREDITS.md` ledger. VRChat uploads only when asked.
