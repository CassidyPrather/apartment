// Renders fixed eye-height views of the apartment to blender/out/unity_views/ (git-ignored)
// so a bake or a placement change can be checked without driving the scene view.
// Apartment > Capture Views. Spots are in the layout's inches (shell_layout.py).

using System.IO;
using UnityEditor;
using UnityEngine;

public static class ViewShots
{
    const float IN = 0.0254f * ApartmentSetup.WorldScale;   // inches, at the world's build scale
    const float Eye = 62f;

    static Vector3 U(float x, float y, float z) => new Vector3(-x * IN, z * IN, -y * IN);

    // name, eye (x, y), look-at (x, y, z)
    static readonly (string name, float ex, float ey, float tx, float ty, float tz)[] Views =
    {
        ("living_to_kitchen", 100f, 20f, 40f, 260f, 40f),
        ("kitchen_to_living", 60f, 270f, 90f, 10f, 40f),
        ("entry_to_windows", 20f, 170f, 110f, 10f, 40f),
        ("bedroom", 245f, 60f, 150f, 130f, 40f),
        ("bedroom_to_window", 180f, 150f, 230f, 0f, 40f),
        ("hall", 232f, 150f, 232f, 260f, 40f),
        ("bath", 236f, 210f, 200f, 285f, 30f),
    };

    public static string OutDir =>
        Path.GetFullPath(Path.Combine(Application.dataPath, "..", "blender", "out", "unity_views"));

    [MenuItem("Apartment/Capture Views")]
    public static void Capture()
    {
        Directory.CreateDirectory(OutDir);
        var go = new GameObject("view_camera");
        var cam = go.AddComponent<Camera>();
        cam.fieldOfView = 75f;
        cam.nearClipPlane = 0.05f;
        cam.allowHDR = true;
        var rt = new RenderTexture(1280, 720, 24);
        var tex = new Texture2D(1280, 720, TextureFormat.RGB24, false);
        try
        {
            cam.targetTexture = rt;
            foreach (var v in Views)
            {
                go.transform.position = U(v.ex, v.ey, Eye);
                go.transform.LookAt(U(v.tx, v.ty, v.tz));
                cam.Render();
                RenderTexture.active = rt;
                tex.ReadPixels(new Rect(0, 0, 1280, 720), 0, 0);
                tex.Apply();
                File.WriteAllBytes(Path.Combine(OutDir, v.name + ".png"), tex.EncodeToPNG());
            }
        }
        finally
        {
            RenderTexture.active = null;
            cam.targetTexture = null;
            Object.DestroyImmediate(rt);
            Object.DestroyImmediate(tex);
            Object.DestroyImmediate(go);
        }
        Debug.Log("[ViewShots] wrote " + Views.Length + " views to " + OutDir);
    }
}
