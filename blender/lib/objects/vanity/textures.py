"""The shared `bathroom` atlas is built by objects/bathtub/textures.py; this runs the
same builder so `gimp_headless.py --object <this package>` works too."""

import os

exec(open(os.path.join(ROOT, "blender", "lib", "objects", "bathtub", "textures.py"),
          encoding="utf-8").read(), globals())
