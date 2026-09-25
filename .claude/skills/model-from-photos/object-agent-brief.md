# Object Agent Brief

You build one object for Cassidy's VRChat apartment world, headless, in parallel with
other agents building other objects. The coordinator (the main session) handles Unity,
git, `CREDITS.md`, and placement in the room. Read `SKILL.md` at the repo root first:
its Privacy, Branding, Fidelity and budget rules apply to you.

## What you own, and what you must not touch

You own only:
- `blender/lib/objects/<name>/`: `object.py`, `textures.py`, `logos/*.svg`, and the
  generated `manifest.json`
- `Assets/Apartment/Textures/<name>_*.png` (written by your texture script)
- `Assets/Apartment/Models/<name>.fbx` (written by the build)
- `blender/out/<name>/` (renders, git-ignored) and scratch files in `Reference/<name>_work/`

Don't edit anything else: not `common.py`, `atlas_layout.py`, `gimp_textures.py`,
`dimensions.py`, the shell, Unity scripts, `SKILL.md` or `CREDITS.md`. Don't commit.
Don't use the Blender or GIMP MCPs, because those are the single live instances Cassidy
watches. Work headless only. Never kill processes by name (`taskkill /IM blender.exe`
closes Cassidy's live Blender too): if a headless run of yours hangs, stop it by its own
PID, or report it. If a shared helper is missing something, write it locally
in your package and mention it in your report.

## Commands (from the repo root, Git Bash)

```
# textures: runs objects/<name>/textures.py build() in a headless GIMP (~20-60 s)
python blender/lib/textures/gimp_headless.py --object <name>
# model: build, render turntable + checker sheets, export FBX + manifest (~10-60 s)
"/c/Program Files/Blender Foundation/Blender 5.0/blender.exe" -b --factory-startup -P blender/lib/build_object.py -- <name>
```

Add `--no-render` and/or `--no-export` while iterating. Sheets land in
`blender/out/<name>/sheet_lit.png` and `sheet_checker.png`. Look at them with Read.

## Package contract (`object.py`)

See the docstring of `blender/lib/build_object.py`. In short: `NAME`, `ATLAS` (a dict
with name, size and regions, 1024 px unless the object is small), `MATERIALS`,
`COLLIDER`, `STATIC`, `build(coll)`, `texture(objs)`, and optionally `VIEWS`. Put the
dimensions at the top of `object.py` in inches with provenance tags (TAPE, SCAN,
SPEC for the exact model's published size, EST), converted once with `m()`.

Conventions:
- Units are meters. The object's front faces -Y, Z is up, and the origin sits on
  the floor (or resting surface) at the footprint centre.
- Build with `common.Builder`: box, cylinder, prism, sweep, each tagged with an atlas
  region. In `texture()`, use `common.atlas_uvs(ob, ATLAS, planar={...}, tiled={...})`,
  then `common.collapse_materials` to map regions onto `common.atlas_material(...)`.
  `blender/lib/router.py`, `modem.py`, `vr_headset.py` and `filing_cabinet.py` are
  worked examples.
- Name objects and materials in lowercase snake_case after the thing, never a brand.
  Give translucent parts their own material with `"mode": "transparent"` and an alpha.
- Budget: most furniture and appliances need 1-4k triangles and one 1K atlas.
  Spend detail where a visitor looks.

## Textures (`textures.py`)

It runs inside GIMP with the helpers from `blender/lib/textures/gimp_textures.py`
already in scope: `Atlas`, `fill_rect`, `fill_ellipse`, `fill_round_rect`, `grain`,
`gegl`, `load`, `rectify`, `flatten_lighting`, `logo`, `add_layer_from`, `flatten`,
and `REF`/`OUT`. Define `ATLAS` (the same dict as in `object.py`, so import it or
repeat it) and a `build()` that makes `a = Atlas(ATLAS)`, fills each region, and calls
`a.save()`. Masks put metallic in R and smoothness in A. Emission goes through
`a.glow_layer()`. GIMP gotchas: colours are 0-255 tuples (the helpers convert them),
fill alpha comes from the 4th tuple value, and crop photos before any perspective warp.

Photo-derived textures are allowed and encouraged for real surfaces. Crop,
perspective-correct, flatten the lighting, and make them tile. Nothing identifying may
survive: no readable text, logos, people or reflections. Real brands become parody names
and new logos (SVG in `logos/`, drawn from scratch). Pick a silly, clearly different name.

## References

Use every reference you're given. For a splat, also use the photos it was trained
from: the splat gives 3D shape, size and placement (in metres when it came from a
LiDAR capture), and the photos give colour and fine detail. The capture tools in
`blender/lib/reference/` (README there) turn captures into orthophotos, contact sheets
and matched-camera comparisons. When the coordinator asks for a block-in, match the big
proportions and colours first and leave small details for a later pass.

## Verify before you report

Nothing is done until you've looked:
1. Open the lit and checker sheets. Look for gaps, flipped normals, stretched UVs and
   wrong colours.
2. **Side by side with the reference:** crop the object from each reference photo and
   put each crop next to a render from a similar angle (add `VIEWS` entries to match).
   Compose them into one image in `Reference/<name>_work/` and look at it. List every
   difference you see and fix what you can: proportions first, then details, then colour.
3. Repeat until the renders match the photos as closely as the references allow.

## Report back (your final message)

- Files written, triangle count, and atlas size.
- Every dimension with its provenance, and which ones are guesses.
- The parody brand name(s) and a neutral description of each logo, for the ledger
  (never the real brand).
- What still differs from the photos, and the exact extra photos or measurements
  that would fix it.
- The paths of your side-by-side comparison images.
