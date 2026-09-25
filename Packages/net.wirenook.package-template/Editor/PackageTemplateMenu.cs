// Editor-only glue. This assembly may use UnityEditor and, once you declare
// the dependency, the VRChat SDK; scripts/test.sh never compiles it, so the
// editor is where it gets exercised.

using UnityEditor;
using UnityEngine;

namespace Wirenook.PackageTemplate.Editor
{
    public static class PackageTemplateMenu
    {
        // Exists to prove the Editor assembly compiles and to mark where
        // editor tooling goes; replace it with your own entry points.
        [MenuItem("Tools/Wirenook/Log Package Version")]
        private static void LogVersion()
        {
            var info = UnityEditor.PackageManager.PackageInfo.FindForAssembly(
                typeof(PackageTemplateMenu).Assembly);
            Debug.Log(info == null
                ? "Package Template: no package info found (moved out of Packages/?)"
                : $"{info.displayName} {info.version}");
        }
    }
}
