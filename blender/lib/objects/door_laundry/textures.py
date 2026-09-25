"""Uses the shared "doors" atlas; its generator lives in objects/door_bedroom/textures.py."""
exec(open(os.path.join(ROOT, "blender", "lib", "objects", "door_bedroom", "textures.py"),
          encoding="utf-8").read())
