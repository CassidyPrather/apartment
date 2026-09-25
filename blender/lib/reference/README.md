# Capture tools

Scripts for turning a phone LiDAR capture (Polycam raw export: `keyframes/` with
images, depth, confidence, corrected cameras) and a Gaussian splat trained from it
into measurements and comparisons. Captures stay in `Reference/` (local-only); these
scripts only read them. First versions from the filing cabinet milestone; run with the
system Python from inside the capture folder.

1. `capture_fuse.py <capture> cloud.npz`: fuse high-confidence depth into a colored point cloud (ARKit world, metres).
2. `capture_floor_top.py`: fit the floor plane and find the furniture's top plane and rectangle (`frame.npz`).
3. `capture_frame.py`: build the furniture-local frame (`cabframe.npz`: x right, y back, z up, front found by colour).
   The frame is mirrored as saved; consumers flip x (`x = -u[s_ax]`). Check handedness before trusting a new frame.
4. `capture_orthophoto.py <capture> out.png front|right|top u0 u1 v0 v1 [res] [offset]`: true-scale orthophoto of a
   plane from the posed photos (median of the frames facing it, depth-tested for occlusion).
5. `capture_sheet.py <capture> out.png x y z radius`: contact sheet of the frames that see a point.
6. `capture_cams.py <capture> cams.json [stem suffixes]`: capture cameras in the furniture-local (= Blender) frame.
   Render the model from these in Blender, then `capture_compare.py` makes photo | render | overlay rows.
7. `splat_headset_views.py`: splat Gaussians in an item's local frame as top/side/front orthos, to lay the model's
   ortho renders over.

Verified against a known size: the router's published width matched the fused cloud to 1.3%.
