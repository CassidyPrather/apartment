---
name: splat-from-scan
description: Turn Cassidy's iPhone 15 Pro LiDAR captures (SplatKing LidarSeries zips with a COLMAP model, or Polycam raw-data exports with keyframes/) into a Gaussian splat .ply on the local RTX 3080 with Brush, as spatial reference for modeling. Use when Cassidy shares a scan zip or a splat .ply and asks for a splat, or wants to measure or view a scanned object or room in 3D.
---

# Splat From Scan

First run: the bedroom filing cabinet (`Reference/cabinet test.zip`, 2026-09-24).
Splats are reference only. They never enter the repo or ship in the world (repo
`SKILL.md`, References and Privacy). Everything below lives in `Reference/`, which is
git-ignored.

## Tools

- **Brush** v0.3.0: `%LOCALAPPDATA%\Programs\brush\brush_app.exe`. A WebGPU trainer
  that needs no CUDA toolkit (the system `nvcc` is an old 11.3; ignore it). If it's
  missing, download `brush-app-x86_64-pc-windows-msvc.zip` from the ArthurBrussee/brush
  GitHub releases, check it against the `.sha256` asset, and unzip it there.
- **Converter**: `polycam_to_nerfstudio.py` next to this file. It needs Python 3.12
  (`python`) with numpy and Pillow.
- In PowerShell 5.1, `Invoke-WebRequest` without `-UseBasicParsing` fails in
  non-interactive mode, so use `curl` from Bash for downloads.

## 1. Intake

Identify the room from a contact sheet of about 16 frames spread across the capture, not a
handful. Room scans wander into neighboring rooms, and 4 frames once got a
living/kitchen scan labeled as the bedroom.

**Which app made it?** List the zip first.

- **SplatKing `LidarSeries_*`** (the best capture so far, the living/dining room and kitchen on 2026-09-25):
  it already holds `COLMAP_Text_Model/` (ARKit LiDAR poses, one PINHOLE camera,
  1920x1440 images, a LiDAR `points3D.txt` in metric y-up). Skip the converter and pass
  that folder straight to Brush. The poses aren't bundle-adjusted, so still run a
  reprojection check with `check_colmap.py` (living/kitchen 0.45, bathroom 0.57). SplatKing `Video_*` zips are dual-lens
  video with no poses or depth. They need a full COLMAP solve and have no metric scale,
  so ask before starting one.
- **Polycam raw data**: continue below.

1. A Polycam raw export holds `keyframes/` with
   `images`, `cameras`, `depth` (16-bit PNG, millimeters, 256x192), `confidence`
   (0/54/255), and usually `corrected_images` and `corrected_cameras` (bundle-adjusted,
   which the converter prefers). If the zip holds a mesh (.glb/.obj) or only
   photos instead, it's a different export. Ask Cassidy to re-export with
   "Raw Data" from Polycam, or fall back to COLMAP on the photos.
2. Extract to `Reference/<object>-splat/polycam/`.

## 2. Convert

```
python .claude/skills/splat-from-scan/polycam_to_nerfstudio.py Reference/<object>-splat/polycam Reference/<object>-splat/dataset
```

This writes `transforms.json` (ARKit poses are already OpenGL convention, so they're
used as is), copies the images, and back-projects up to 3000 high-confidence LiDAR points
per frame into `points3d.ply` to seed the splat.

Read the **alignment ratio** it prints before training. It compares reprojected cloud
colors with the photos against a shuffled baseline. The cabinet scored 0.49. Above
about 0.65 means poses and depth disagree (wrong convention, or a capture where ARKit
tracking broke). Don't train on it. Look at `world_mapping_status` and
`tracking_segment` in the camera JSONs for the bad frames.

**Drift in long room scans without `corrected_cameras`** (Polycam bedroom, 1818
frames, ratio 0.76): nearby frames agree but frames hundreds apart don't. The fix
I tried, with COLMAP 4.2 CUDA (`%LOCALAPPDATA%\Programs\colmap\COLMAP.bat`), was:
all frames (every third frame is too sparse for close-range low-texture shots),
`--SiftExtraction.peak_threshold 0.003`, per-frame ARKit intrinsics written into the
DB and held fixed, pairs built from sequential neighbors plus ARKit-proximity loop
pairs, then `global_mapper` (outlier frames flung far) or `pose_prior_mapper` with
ARKit positions in `pose_priors` (about 25 min on CPU). `colmap_to_polycam.py` writes the
result back as `corrected_cameras`. Neither mapper got the floater rate below 15%
(the cabinet has 1%), so it didn't pay off. The floaters were probably scene changes,
not poses. **Recommend a re-capture with SplatKing LiDAR mode instead.** It tracked the
same room cleanly. Note that COLMAP 4 leaves the `matches` table empty, so count inliers in
`two_view_geometries`.

## 3. Train

Run from Bash in the background (it prints nothing until it exits) and watch for
checkpoints with Monitor:

```
cd Reference/<object>-splat && mkdir -p output
"$LOCALAPPDATA/Programs/brush/brush_app.exe" dataset --eval-split-every 10 --export-path output --export-every 10000
```

- Cabinet timing: 150 frames at 1024x768, 30k steps, 16 minutes, 1.46M splats,
  344 MB .ply. The first 10k steps take about 5 min, and later ones about 6 min per 10k.
  Growth stops at 15k, so `--total-steps 15000` roughly halves the time for a small object.
- `--with-viewer` opens a live window if Cassidy wants to watch.
- The GPU has 10 GB. The cabinet peaked around 5 GB. For rooms, pass
  `--max-splats 3000000`. The SplatKing living/kitchen (627 frames at 1920x1440) hit that cap by
  10k steps and took about 12.5 min per 10k.
- **Check the GPU is free before training** (`nvidia-smi`). The `stream.rs` panic below
  is a Windows driver reset (System log event 4101, "nvlddmkm stopped responding").
  On 2026-09-25 it was caused by another session's headless Blender agents all rendering
  Eevee on the GPU (9.4 GB and 94% load with Brush stopped). Ask the other session to
  pause GPU work instead of killing its processes. On a shared GPU, use
  `--max-splats 2000000 --max-resolution 1440 --export-every 2500`. The bedroom
  (773 frames) then ran 15k steps in 21 min at about 7.5 GB.
- Brush v0.3.0 can crash mid-run with a cubecl/wgpu `stream.rs` panic (the living/kitchen
  run did just after 20k). Keep `--export-every 10000` so a checkpoint survives. Growth
  stops at 15k, so a 20k checkpoint is close to final.

## 4. Check and hand over

- The export is `output/export_30000.ply` (y-up, meters, SH degree 3). Look at it
  before calling it done: open it in Brush (`brush_app.exe <ply>`) or superspl.at/editor.
  Headless Brush doesn't log eval metrics, so the viewer is the check.
- The capture includes the room around the object. Crop in SuperSplat if needed.
- Tell Cassidy the path, splat count, time taken, and anything that looks wrong
  (floaters, blurry sides the scan didn't cover).

## Viewing in a browser

`ply_to_splat.py <in.ply> <out.splat> [max_splats]` shrinks a Brush .ply about 7x (SH
dropped). `Reference/splat-viewer/` holds a local viewer (gaussian-splats-3d 0.4.7 +
three 0.170 from jsdelivr). Serve it with `python -m http.server 8765 --bind 127.0.0.1`.
Keep it local: these are captures of Cassidy's home. `place_rooms.py` there bakes each room
into the shell_layout.py frame using apartment-91's survey transforms
(`Reference/<room>_survey/`), crops each room to its footprint, and cuts at 96 in for a
dollhouse view. Headless check: Edge with `--remote-debugging-port`, then wait for
`window.__splatReady` before taking the screenshot (`--virtual-time-budget` freezes the
viewer's workers).

## Using a splat as reference

- ARKit poses are metric, so distances in the splat or in `points3d.ply` are real
  meters. That's useful for dimensions without a tape value: record them in
  `blender/lib/dimensions.py` (in inches) with the existing `SCAN` provenance, which
  ranks below `TAPE` and above `SPEC` and `EST`. Measure between well-defined edges,
  and cross-check one value against a known `SPEC` width (the cabinet capture agreed
  with the router's to within 1.3%).
- Render stills from angles the photos don't cover to support the
  `model-from-photos` skill. Stills stay in `Reference/` like photos.
- Never import a splat into Unity for the world. VRChat has no built-in splat
  renderer, and a million splats would be far over the Quest budget.
