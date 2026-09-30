// Lights and night mode (PC). Each light source is a Light Volumes Point Light Volume
// (runtime light with a baked shadow map) toggled by a synced LightSwitch; a DayNight
// switch dims the baked daylight to night and swaps in a starry sky. The lightmap bake
// is daylight only on PC (LightingSetup); Quest gets its own lights-on bake instead.
// Apartment > Setup Lights And Night; Build Apartment Scene runs it.
//
// Positions are plan inches (shell_layout.py), at the world's build scale.

using System.IO;
using System.Linq;
using UdonSharp;
using UdonSharpEditor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using VRCLightVolumes;

public static class NightSetup
{
    const float IN = 0.0254f * ApartmentSetup.WorldScale;
    static Vector3 U(float x, float y, float z) => new Vector3(-x * IN, z * IN, -y * IN);

    // light: fixture object (for its glowing glass), glow material, light positions,
    // range (m), intensity, shadows; switch: position, the wall normal in plan
    // (dx, dy), label.
    static readonly (string name, string fixture, string glowMat, Vector3[] lights, float range, float intensity,
        Vector3 sw, Vector2 normal, string label)[] Sources =
    {
        ("dining_table_light", "ceiling_light_bar", "ceiling_light_bar_lens",
            new[] { new Vector3(68f, 235f, 96.5f) }, 6f, 14f, new Vector3(8f, 180.4f, 48f), new Vector2(0, -1), "Table light"),
        ("dining_door_light", "ceiling_dome_light", "ceiling_dome_light_diffuser",
            new[] { new Vector3(67f, 152f, 101.5f) }, 6f, 14f, new Vector3(13f, 180.4f, 48f), new Vector2(0, -1), "Doorway light"),
        ("hall_light", "ceiling_dome_light", "ceiling_dome_light_diffuser",
            new[] { new Vector3(229f, 183.5f, 101.5f) }, 5f, 11f, new Vector3(247.6f, 135.5f, 48f), new Vector2(-1, 0), "Hall light"),
        ("bath_light", "bath_fixtures", "bath_fixtures_glow",
            new[] { new Vector3(179.5f, 227.1f, 80f), new Vector3(223.8f, 249.2f, 102f) }, 5f, 9f,
            new Vector3(249.5f, 202.6f, 48f), new Vector2(0, 1), "Bathroom light"),
        ("bedroom_lamp", "floor_lamp", "floor_lamp_glow",
            new[] { new Vector3(262f, 42f, 72f) }, 7f, 5f, new Vector3(0, 0, 0), Vector2.zero, "Lamp"),
    };
    // Soft sources near walls: light name -> (source size m, intensity, all-round); see
    // Setup. The bath's lights shine all round: in that small room a spot's cone edge drew
    // a hard dark arc on the wall above the vanity and along the tops of the walls.
    static readonly System.Collections.Generic.Dictionary<string, (float size, float intensity, bool point)> Soft =
        new System.Collections.Generic.Dictionary<string, (float, float, bool)>
        {
            ["bedroom_lamp_0"] = (1.2f, 0.7f, true),    // all-round so the spill over the bowl reaches the desk (a 95 deg spot up left it dark); dimmer than the spot was
            ["bath_light_0"] = (1.2f, 1.7f, true),
            ["bath_light_1"] = (1.2f, 0.4f, true),
            ["hall_light_0"] = (1.2f, 0.4f, true),               // the narrow hall's walls sit right by it
        };
    // Sources whose switch is a real toggle on the surveyed wall plates (wall_plates package,
    // positions.json): the lever object rocks about its local X, up = on, +40 deg = off.
    // The table light's switch wasn't found in the captures, so it keeps its own plate.
    static readonly System.Collections.Generic.Dictionary<string, string> Levers =
        new System.Collections.Generic.Dictionary<string, string>
        {
            ["dining_door_light"] = "wall_plates_lever_entry",       // the one toggle by the entry
            ["hall_light"] = "wall_plates_lever_bedback_1",          // bedroom back wall 3-gang (which one: EST)
            ["bath_light"] = "wall_plates_lever_bath_1",             // tub-stub 3-gang, west toggle (EST)
        };

    // A click target over a real lever: a trigger box, rotated with the plate.
    internal static GameObject LeverHost(string name, Transform parent, Transform lever)
    {
        var host = new GameObject(name);
        host.transform.SetParent(parent, false);
        host.transform.SetPositionAndRotation(lever.position, lever.rotation);
        var box = host.AddComponent<BoxCollider>();
        box.isTrigger = true;
        box.size = new Vector3(0.07f, 0.1f, 0.08f);
        return host;
    }

    internal static Transform FindLever(string name) =>
        Object.FindObjectsOfType<Transform>(true).FirstOrDefault(t => t.name == name);

    static readonly Vector3 DayNightSwitch = new Vector3(18f, 180.4f, 48f);

    [MenuItem("Apartment/Setup Lights And Night")]
    public static void Setup()
    {
        foreach (var old in Object.FindObjectsOfType<Transform>(true).Where(t => t.name == "lights_and_night").ToArray())
            Object.DestroyImmediate(old.gameObject);
        if (QuestSetup.IsMobileScene())
        {
            Debug.Log("[NightSetup] Quest target: lights-on bake, no night mode");
            return;
        }
        if (EnsureProgram("LightSwitch") | EnsureProgram("DayNight"))
        {
            Debug.LogWarning("[NightSetup] created Udon program assets; run again once UdonSharp finishes compiling");
            return;
        }
        var root = new GameObject("lights_and_night");
        var plate = FilingCabinetSetup.PlainMat("switch_plate", new Color(0.92f, 0.91f, 0.88f));

        foreach (var s in Sources)
        {
            var group = new GameObject(s.name).transform;
            group.SetParent(root.transform, false);
            // Ceiling fixtures shine down in a wide cone (an all-round point light just under
            // the ceiling blew out a disc on it); the torchiere's bowl shines up.
            bool up = s.name == "bedroom_lamp";
            // Lights near a wall (the torchiere by the east wall, the vanity light over the
            // mirror) blew a bright disc onto it. Light Volumes falls off as I*s^2/(d^2+s^2),
            // so a wall right by the light always gets close to the full intensity I: these
            // get a big source (s) and a low intensity, keeping the room's light the same while
            // the wall beside them peaks around 1 instead of blowing out.
            var instances = s.lights.Select((p, i) => Soft.TryGetValue($"{s.name}_{i}", out var soft)
                ? MakeLight($"{s.name}_{i}", group, U(p.x, p.y, p.z), s.range, soft.intensity, up, soft.size, soft.point)
                : MakeLight($"{s.name}_{i}", group, U(p.x, p.y, p.z), s.range, s.intensity, up, 0.16f)).ToArray();

            // The fixture instance nearest the first light owns the glowing glass.
            var target = U(s.lights[0].x, s.lights[0].y, s.lights[0].z);
            var glow = Object.FindObjectsOfType<MeshRenderer>()
                .Where(r => r.sharedMaterials.Any(m => m != null && m.name == s.glowMat))
                .OrderBy(r => (r.bounds.ClosestPoint(target) - target).sqrMagnitude).FirstOrDefault();
            int slot = glow != null ? System.Array.FindIndex(glow.sharedMaterials, m => m != null && m.name == s.glowMat) : 0;

            GameObject host;
            if (s.normal == Vector2.zero)
            {
                // Switch on the fixture itself (the torchiere): a small knob on the pole.
                var lamp = Object.FindObjectsOfType<MeshRenderer>().FirstOrDefault(r => r.name.StartsWith(s.fixture) && !r.name.Contains("glow"));
                host = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
                host.name = s.name + "_switch";
                host.transform.SetParent(group, false);
                var b = lamp != null ? lamp.bounds : new Bounds(target, Vector3.one * 0.1f);
                host.transform.position = new Vector3(b.center.x, 1.0f * ApartmentSetup.WorldScale, b.center.z);
                host.transform.localScale = new Vector3(0.035f, 0.02f, 0.035f);
                host.transform.rotation = Quaternion.Euler(90f, 0f, 0f);
                host.GetComponent<MeshRenderer>().sharedMaterial = FilingCabinetSetup.PlainMat("lamp_knob", new Color(0.1f, 0.1f, 0.1f));
            }
            else if (Levers.TryGetValue(s.name, out var leverName) && FindLever(leverName) != null)
                host = LeverHost(s.name + "_switch", group, FindLever(leverName));
            else
                host = WallSwitch(s.name + "_switch", group, U(s.sw.x, s.sw.y, s.sw.z), s.normal, plate);

            var sw = UdonSharpUndo.AddComponent<LightSwitch>(host);
            sw.lights = instances;
            sw.glows = glow != null ? new Renderer[] { glow } : new Renderer[0];
            sw.glowSlots = new[] { slot };
            sw.glowColor = Color.white;
            var realLever = Levers.TryGetValue(s.name, out var ln) ? FindLever(ln) : null;
            if (realLever != null)
            {
                sw.toggle = realLever;
                sw.onRotation = realLever.localRotation;
                sw.offRotation = realLever.localRotation * Quaternion.Euler(40f, 0f, 0f);
            }
            else
                sw.toggle = host.transform.childCount > 0 ? host.transform.GetChild(0) : null;
            sw.InteractionText = s.label;
            UdonSharpEditorUtility.CopyProxyToUdon(sw);
        }

        // Day/night switch beside the room switches by the entry.
        var dn = WallSwitch("day_night_switch", root.transform, U(DayNightSwitch.x, DayNightSwitch.y, DayNightSwitch.z), new Vector2(0, -1),
                            FilingCabinetSetup.PlainMat("day_night_plate", new Color(0.25f, 0.3f, 0.5f)));
        var dayNight = UdonSharpUndo.AddComponent<DayNight>(dn);
        dayNight.roomVolumes = Object.FindObjectsOfType<LightVolumeInstance>().Where(v => v.name.StartsWith("volume_")).ToArray();
        dayNight.exterior = Object.FindObjectsOfType<MeshRenderer>().Where(r => r.name.StartsWith("exterior_view") || r.name == "exterior_ground").Cast<Renderer>().ToArray();
        dayNight.InteractionText = "Day / night";
        UdonSharpEditorUtility.CopyProxyToUdon(dayNight);
        NightSky(dayNight);

        EditorSceneManager.MarkSceneDirty(root.scene);
        Debug.Log($"[NightSetup] {Sources.Length} light sources, switches and day/night set up");
    }

    static PointLightVolumeInstance MakeLight(string name, Transform parent, Vector3 pos, float range, float intensity, bool up, float sourceSize, bool point = false)
    {
        Selection.activeGameObject = parent.gameObject;
        EditorApplication.ExecuteMenuItem("GameObject/Point Light Volume");
        var go = Selection.activeGameObject;
        go.name = name;
        go.transform.SetParent(parent, false);
        go.transform.position = pos;
        go.transform.rotation = Quaternion.LookRotation(up ? Vector3.up : Vector3.down, Vector3.forward);
        var inst = go.GetComponent<PointLightVolumeInstance>();
        var so = new SerializedObject(inst);
        so.FindProperty("Range").floatValue = range;
        so.FindProperty("Intensity").floatValue = intensity;
        so.FindProperty("Color").colorValue = new Color(1f, 0.87f, 0.72f);
        // A source the size of the shade: a tiny point just under the ceiling blew out a
        // bright disc on it (inverse-square hotspot).
        so.FindProperty("LightSourceSize").floatValue = sourceSize;
        // The bathroom's lights sit a few inches from its walls with 1.2 m soft sources: their
        // shadow maps turned the vanity bar into black blobs on the wall, and in a room that
        // small the shadows add nothing.
        so.FindProperty("Shadows").boolValue = !name.StartsWith("bath_light");
        so.FindProperty("LightType").intValue = point ? 0 : 1;                  // point or spot
        so.FindProperty("Angle").floatValue = (up ? 95f : 150f) * Mathf.Deg2Rad;                // a torchiere bowl throws a narrower cone up
        var falloff = so.FindProperty("Falloff");
        if (falloff != null) falloff.floatValue = 0.5f;
        so.FindProperty("IsDynamic").boolValue = false;
        so.ApplyModifiedPropertiesWithoutUndo();
        // The package's own sync (as its menu item does) derives the runtime values.
        var sync = System.AppDomain.CurrentDomain.GetAssemblies()
            .Select(a => a.GetType("VRCLightVolumes.PointLightVolumeEditorUtility")).FirstOrDefault(t => t != null)
            ?.GetMethod("Sync", System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic);
        sync?.Invoke(null, new object[] { inst, false, true, false });
        return inst;
    }

    // A white wall plate with a small rocker; the plate faces into the room along `normal`.
    internal static GameObject WallSwitch(string name, Transform parent, Vector3 pos, Vector2 normal, Material mat)
    {
        var n = new Vector3(-normal.x, 0f, -normal.y);       // plan -> Unity (x mirrored, y -> -z)
        var host = GameObject.CreatePrimitive(PrimitiveType.Cube);
        host.name = name;
        host.transform.SetParent(parent, false);
        host.transform.rotation = Quaternion.LookRotation(n, Vector3.up);
        host.transform.position = pos + n * 0.004f;
        host.transform.localScale = new Vector3(0.07f, 0.115f, 0.008f);
        host.GetComponent<MeshRenderer>().sharedMaterial = mat;
        var rocker = GameObject.CreatePrimitive(PrimitiveType.Cube);
        rocker.name = "rocker";
        Object.DestroyImmediate(rocker.GetComponent<Collider>());
        rocker.transform.SetParent(host.transform, false);
        rocker.transform.localPosition = new Vector3(0f, 0f, 0.8f);
        rocker.transform.localScale = new Vector3(0.3f, 0.35f, 1.2f);
        rocker.GetComponent<MeshRenderer>().sharedMaterial = mat;
        return host;
    }

    // Night sky: the backdrop's glowing sky swaps to a generated starry version of its own
    // emission map (same atlas layout), via the DayNight's material property block.
    static void NightSky(DayNight dayNight)
    {
        var exterior = dayNight.exterior.FirstOrDefault(r => r.name == "exterior_view");
        if (exterior == null) return;
        var mat = exterior.sharedMaterials.FirstOrDefault(m => m != null && m.name == "exterior_view");
        var dayEmission = mat != null ? mat.GetTexture("_EmissionMap") as Texture2D : null;
        if (dayEmission == null) return;
        const string path = "Assets/Apartment/Textures/exterior_view_night_emission.png";
        var src = Readable(dayEmission);
        var px = src.GetPixels32();
        var rng = new System.Random(4217);
        int w = src.width, h = src.height;
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
            {
                var c = px[y * w + x];
                if (c.r + c.g + c.b < 30) continue;               // not sky
                float t = (float)y / h;
                px[y * w + x] = new Color32((byte)(6 + 10 * t), (byte)(9 + 14 * t), (byte)(24 + 30 * t), 255);
            }
        for (int k = 0; k < w * h / 900; k++)
        {
            int x = rng.Next(w), y = rng.Next(h), i = y * w + x;
            if (px[i].b < 20) continue;
            byte v = (byte)rng.Next(150, 255);
            px[i] = new Color32(v, v, (byte)Mathf.Min(255, v + 20), 255);
        }
        var night = new Texture2D(w, h, TextureFormat.RGBA32, false);
        night.SetPixels32(px);
        File.WriteAllBytes(path, night.EncodeToPNG());
        Object.DestroyImmediate(night);
        Object.DestroyImmediate(src);
        AssetDatabase.ImportAsset(path);
        var imp = (TextureImporter)AssetImporter.GetAtPath(path);
        imp.mipmapEnabled = true;
        imp.textureCompression = TextureImporterCompression.Compressed;
        imp.SaveAndReimport();
        var nightMat = new Material(mat) { name = "exterior_view_night" };
        nightMat.SetTexture("_EmissionMap", AssetDatabase.LoadAssetAtPath<Texture2D>(path));
        const string matPath = "Assets/Apartment/Materials/exterior_view_night.mat";
        AssetDatabase.DeleteAsset(matPath);
        AssetDatabase.CreateAsset(nightMat, matPath);
        dayNight.daySkybox = null;
        dayNight.nightSkybox = null;
        dayNight.exteriorDay = mat;
        dayNight.exteriorNight = nightMat;
        UdonSharpEditorUtility.CopyProxyToUdon(dayNight);
    }

    static Texture2D Readable(Texture2D t)
    {
        var rt = RenderTexture.GetTemporary(t.width, t.height, 0, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
        Graphics.Blit(t, rt);
        var prev = RenderTexture.active; RenderTexture.active = rt;
        var r = new Texture2D(t.width, t.height, TextureFormat.RGBA32, false);
        r.ReadPixels(new Rect(0, 0, t.width, t.height), 0, 0); r.Apply();
        RenderTexture.active = prev; RenderTexture.ReleaseTemporary(rt);
        return r;
    }

    internal static bool EnsureProgram(string script)
    {
        string path = $"Assets/Apartment/Scripts/{script}.asset";
        if (AssetDatabase.LoadAssetAtPath<UdonSharpProgramAsset>(path) != null) return false;
        var asset = ScriptableObject.CreateInstance<UdonSharpProgramAsset>();
        asset.sourceCsScript = AssetDatabase.LoadAssetAtPath<MonoScript>($"Assets/Apartment/Scripts/{script}.cs");
        AssetDatabase.CreateAsset(asset, path);
        AssetDatabase.SaveAssets();
        UdonSharpProgramAsset.CompileAllCsPrograms(true);
        return true;
    }
}
