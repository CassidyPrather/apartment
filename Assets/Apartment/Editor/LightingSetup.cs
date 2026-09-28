// Lighting for the apartment scene: baked ceiling lights per room, a baked daylight sun,
// box-projected reflection probes, one VRC Light Volume per room (drives dynamic
// objects and avatars), and Quest-friendly lightmap settings. No real-time lights.
// Apartment > Setup Lighting builds it; Apartment > Bake Lighting bakes lightmaps,
// probes and Light Volumes together.
//
// Room boxes and fixture spots are in the layout's inches (shell_layout.py); fixture
// positions are estimates until the room captures place the real ones.

using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class LightingSetup
{
    const float IN = 0.0254f * ApartmentSetup.WorldScale;   // inches, at the world's build scale

    // name, x0, x1, y0, y1 (inches), ceiling light spot (x, y), light intensity
    static readonly (string name, float x0, float x1, float y0, float y1, float lx, float ly, float intensity)[] Rooms =
    {
        ("living", 0f, 134f, 0f, 120f, 67f, 70f, 0.8f),
        ("dining", 0f, 134f, 120f, 186f, 67f, 152f, 0.7f),
        ("kitchen", 0f, 134f, 186f, 286f, 68f, 235f, 0.9f),
        ("bedroom", 138.75f, 274.6f, 0f, 158.4f, 262f, 42f, 0.8f),     // lit by the torchiere, high in its corner
        ("hall", 211.2f, 247.7f, 130.35f, 197.75f, 229f, 183.5f, 0.5f),
        ("bath", 171.3f, 274.6f, 202.5f, 286f, 222.9f, 249.2f, 0.8f),
        ("laundry", 171.3f, 206.45f, 163.15f, 197.75f, 189f, 181f, 0.3f),
        ("closet", 252.45f, 274.6f, 135.1f, 197.75f, 263.5f, 166f, 0.25f),
    };
    const float CeilingIn = 108f;

    // Window openings (shell_layout.py): on the west or south wall, the span along it, sill
    // to head, and the plan depth the skylight sits at (in the wall, outside the blinds;
    // the patio door's is inside, clear of its shadow slab, over the glass upper half).
    static readonly (bool west, float a0, float a1, float z0, float z1, float depth)[] Windows =
    {
        (true, 42.5f, 77.25f, 26.5f, 85f, -3f),
        (true, 101.75f, 136.5f, 26.5f, 85f, -3f),
        (false, 38.5f, 108.5f, 26.5f, 85f, -3f),
        (false, 171.25f, 205.45f, 26.5f, 85f, -3f),
        (false, 212.5f, 249f, 42f, 78f, 0.5f),
    };
    const float SkylightIntensity = 3f;
    // Volumes stop short of the walls: padding pulled in-wall voxels (black) into them.
    // Anything inside a wall's thickness (closed door leaves, jambs) blends from the light
    // probe grid instead, which sits inside the rooms only.
    const float VolumePadIn = -4f;        // inset: voxels on a wall face bake half-occluded (dark)
    const float ProbeSpacing = 0.9f, ProbeInset = 0.15f;
    static readonly float[] ProbeHeights = { 0.3f * ApartmentSetup.WorldScale, 1.3f * ApartmentSetup.WorldScale, 2.3f * ApartmentSetup.WorldScale };

    static Vector3 U(float xIn, float yIn, float zIn) => new Vector3(-xIn * IN, zIn * IN, -yIn * IN);

    [MenuItem("Apartment/Setup Lighting")]
    public static void Setup()
    {
        var scene = EditorSceneManager.GetActiveScene();
        var old = GameObject.Find("lighting");
        if (old != null) Object.DestroyImmediate(old);
        var temp = GameObject.Find("temp_light");
        if (temp != null) Object.DestroyImmediate(temp);
        // A fresh manager too: the old one keeps the deleted volumes registered and then
        // counts no active volumes, which switches Light Volumes off for everything.
        var oldManager = GameObject.Find("Light Volume Manager");
        if (oldManager != null) Object.DestroyImmediate(oldManager);
        foreach (var t in Object.FindObjectsOfType<Transform>())      // volumes from an earlier run
            if (t != null && t.name.StartsWith("volume_"))
                Object.DestroyImmediate(t.gameObject);
        var root = new GameObject("lighting");

        // Warm white as the eye sees it: Mathf.CorrelatedColorTemperatureToRGB gives a linear
        // value that reads deep orange once baked and bounced around off-white walls.
        var warm = new Color(1f, 0.89f, 0.77f);
        // PC bakes daylight only: the lamps are switchable Point Light Volumes (NightSetup).
        // Quest has no night mode, so its own bake keeps the lamps baked in.
        bool quest = QuestSetup.IsMobileScene();
        foreach (var r in Rooms)
        {
            var go = new GameObject("light_" + r.name);
            go.transform.SetParent(root.transform);
            go.transform.position = U(r.lx, r.ly, CeilingIn - 6f);
            var l = go.AddComponent<Light>();
            go.SetActive(quest);
            l.type = LightType.Point;
            l.lightmapBakeType = LightmapBakeType.Baked;
            l.color = warm;
            l.intensity = r.intensity;
            l.range = 6f;
            l.shadows = LightShadows.Soft;
            l.shadowRadius = 0.15f;

            // Reflection probe: box-projected over the room.
            var pgo = new GameObject("probe_" + r.name);
            pgo.transform.SetParent(root.transform);
            var size = new Vector3((r.x1 - r.x0) * IN, CeilingIn * IN, (r.y1 - r.y0) * IN);
            pgo.transform.position = U((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2, 60f);
            var p = pgo.AddComponent<ReflectionProbe>();
            p.mode = UnityEngine.Rendering.ReflectionProbeMode.Baked;
            p.boxProjection = true;
            // Padded past the walls so door leaves and jambs in a wall's thickness
            // don't fall outside every probe and reflect the default blue skybox.
            p.size = size + new Vector3(2 * 6f * IN, 0f, 2 * 6f * IN);
            p.center = new Vector3(0, (CeilingIn / 2 - 60f) * IN, 0);
            p.resolution = 128;
            p.importance = 1;

            // Light Volume: created through the package's own menu so it registers
            // with the manager, then fitted to the room.
            Selection.activeGameObject = root;
            EditorApplication.ExecuteMenuItem("GameObject/Light Volume");
            var vol = Selection.activeGameObject;
            vol.name = "volume_" + r.name;
            vol.transform.SetParent(root.transform, false);
            vol.transform.position = U((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2, CeilingIn / 2);
            vol.transform.rotation = Quaternion.identity;
            vol.transform.localScale = size + new Vector3(2 * VolumePadIn * IN, 0f, 2 * VolumePadIn * IN);
            foreach (var c in vol.GetComponents<Component>())
            {
                var so = new SerializedObject(c);
                var vpu = so.FindProperty("VoxelsPerUnit");
                if (vpu != null) vpu.floatValue = 4f;
                var bake = so.FindProperty("Bake");
                if (bake != null) bake.boolValue = true;
                so.ApplyModifiedPropertiesWithoutUndo();
            }
        }

        // Light probes on a grid inside each room: the fallback for anything outside the
        // volumes, blended by the Light Volume manager.
        var probeGo = new GameObject("light_probes");
        probeGo.transform.SetParent(root.transform);
        var positions = new List<Vector3>();
        foreach (var r in Rooms)
        {
            Vector3 a = U(r.x0, r.y0, 0f), b = U(r.x1, r.y1, 0f);
            float xa = Mathf.Min(a.x, b.x) + ProbeInset, xb = Mathf.Max(a.x, b.x) - ProbeInset;
            float za = Mathf.Min(a.z, b.z) + ProbeInset, zb = Mathf.Max(a.z, b.z) - ProbeInset;
            int nx = Mathf.Max(2, Mathf.CeilToInt((xb - xa) / ProbeSpacing) + 1);
            int nz = Mathf.Max(2, Mathf.CeilToInt((zb - za) / ProbeSpacing) + 1);
            for (int i = 0; i < nx; i++)
                for (int k = 0; k < nz; k++)
                    foreach (var h in ProbeHeights)
                        positions.Add(new Vector3(Mathf.Lerp(xa, xb, i / (nx - 1f)), h, Mathf.Lerp(za, zb, k / (nz - 1f))));
        }
        probeGo.AddComponent<LightProbeGroup>().probePositions = positions.ToArray();

        // Daylight: a baked sun from the south-west, so the windows and outside read as day.
        var sun = new GameObject("sun").AddComponent<Light>();
        sun.transform.SetParent(root.transform);
        sun.type = LightType.Directional;
        sun.lightmapBakeType = LightmapBakeType.Baked;
        sun.color = new Color(1f, 0.97f, 0.93f);
        sun.intensity = 1.4f;
        sun.shadows = LightShadows.Soft;
        sun.transform.rotation = Quaternion.Euler(40f, 150f, 0f);

        // Skylight: the sky seen through each window, as a soft baked rectangle light in the
        // opening shining in through the blinds. Without the lamps baked in, the sun's patch
        // and the ambient alone left the rooms dim by day.
        var sky = new Color(0.86f, 0.92f, 1f);
        foreach (var w in Windows)
        {
            var go = new GameObject("skylight");
            go.transform.SetParent(root.transform);
            float a = (w.a0 + w.a1) / 2, h = (w.z0 + w.z1) / 2;
            go.transform.position = w.west ? U(w.depth, a, h) : U(a, w.depth, h);
            go.transform.rotation = Quaternion.LookRotation(w.west ? Vector3.left : Vector3.back, Vector3.up);
            var l = go.AddComponent<Light>();
            l.type = LightType.Rectangle;
            l.lightmapBakeType = LightmapBakeType.Baked;
            l.areaSize = new Vector2((w.a1 - w.a0) * IN, (w.z1 - w.z0) * IN);
            l.color = sky;
            l.intensity = SkylightIntensity;
            l.range = 8f;
        }

        // The sky backdrop and the big ground plane stay out of the lightmap (they'd waste
        // most of it); probes light them instead.
        foreach (var r in Object.FindObjectsOfType<MeshRenderer>())
        {
            if (r.name == "exterior_view" || r.name == "exterior_view_ground" || r.name == "exterior_view_foliage")
            {
                var flags = GameObjectUtility.GetStaticEditorFlags(r.gameObject) & ~StaticEditorFlags.ContributeGI;
                GameObjectUtility.SetStaticEditorFlags(r.gameObject, flags);
                r.receiveGI = ReceiveGI.LightProbes;
            }
        }

        // The entry and patio doors move, so they don't block baked light; a shadow-only slab
        // in each opening stops the sun leaking through what looks like a solid door.
        // Thin slabs on the wall's outer face, behind the leaf: a blocker inside the wall
        // thickness shadowed the door leaf itself (dark blotches on the panels).
        foreach (var (name, x0, x1, y0, y1) in new[] { ("door_blocker_entry", -6.5f, -6f, 144.5f, 180.5f),
                                                       ("door_blocker_patio", 212.5f, 249f, -6.5f, -6f) })
        {
            var blk = GameObject.CreatePrimitive(PrimitiveType.Cube);
            blk.name = name;
            blk.transform.SetParent(root.transform);
            Object.DestroyImmediate(blk.GetComponent<Collider>());
            blk.transform.position = U((x0 + x1) / 2, (y0 + y1) / 2, 40f);
            blk.transform.localScale = new Vector3((x1 - x0) * IN, 80f * IN, (y1 - y0) * IN);
            var br = blk.GetComponent<MeshRenderer>();
            br.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.ShadowsOnly;
            GameObjectUtility.SetStaticEditorFlags(blk, StaticEditorFlags.ContributeGI);
        }

        // Small detailed static objects get more lightmap texels: at the room rate a 30 mm rail
        // (the filing cabinet's top rail) gets under one texel and bleeds the dark interior.
        foreach (var r in Object.FindObjectsOfType<MeshRenderer>())
        {
            if (!GameObjectUtility.GetStaticEditorFlags(r.gameObject).HasFlag(StaticEditorFlags.ContributeGI))
                continue;
            var size = r.bounds.size;
            float big = Mathf.Max(size.x, Mathf.Max(size.y, size.z));
            r.scaleInLightmap = big < 1.0f ? 4f : big < 2.0f ? 2f : 1f;
            if (r.name.StartsWith("door_"))
                r.scaleInLightmap = Mathf.Max(r.scaleInLightmap, 2f);   // big flat faces, seen up close
        }

        // Light fixtures sit right at their baked light, so their own meshes threw big
        // unrealistic shadows (the kitchen light bar); they don't cast in the bake.
        foreach (var r in Object.FindObjectsOfType<MeshRenderer>())
            if (r.name.StartsWith("ceiling_light_bar") || r.name.StartsWith("ceiling_dome_light") || r.name.StartsWith("floor_lamp")
                || r.name == "bath_fixtures")        // the vanity bar and ceiling light (its towel and grab bars threw odd dark marks)
                r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        // Clear glass lets the sun and skylights through.
        foreach (var r in Object.FindObjectsOfType<MeshRenderer>())
            if (r.name == "window_units_glass")
                r.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;

        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
        RenderSettings.ambientSkyColor = new Color(0.6f, 0.62f, 0.66f);     // near-neutral: a bluer sky tinted everything by the windows
        RenderSettings.ambientEquatorColor = new Color(0.45f, 0.44f, 0.42f);
        RenderSettings.ambientGroundColor = new Color(0.25f, 0.24f, 0.22f);

        var ls = new LightingSettings
        {
            name = "apartment_lighting",
            lightmapper = LightingSettings.Lightmapper.ProgressiveCPU,   // the GPU one hung and skipped the Light Volume probes
            bakedGI = true,
            realtimeGI = false,
            lightmapResolution = 20f,
            lightmapPadding = 8,           // 4 let neighbouring charts bleed onto chart edges (pink strip on a door)
            lightmapMaxSize = 2048,
            directionalityMode = LightmapsMode.NonDirectional,
            lightmapCompression = LightmapCompression.NormalQuality,
            mixedBakeMode = MixedLightingMode.IndirectOnly,
            directSampleCount = 32,
            indirectSampleCount = 256,
            environmentSampleCount = 128,
            maxBounces = 3,
            filteringMode = LightingSettings.FilterMode.Auto,
            ao = true,
            aoMaxDistance = 0.6f,
        };
        const string lsPath = "Assets/Apartment/Scenes/apartment_lighting.lighting";
        AssetDatabase.DeleteAsset(lsPath);
        AssetDatabase.CreateAsset(ls, lsPath);
        Lightmapping.lightingSettings = ls;

        // The day/night switch dims the room volumes, which were just rebuilt: point it at
        // the new ones (NightSetup runs first and linked the old ones).
        foreach (var dn in Object.FindObjectsOfType<DayNight>(true))
        {
            dn.roomVolumes = Object.FindObjectsOfType<VRCLightVolumes.LightVolumeInstance>().Where(v => v.name.StartsWith("volume_")).ToArray();
            UdonSharpEditor.UdonSharpEditorUtility.CopyProxyToUdon(dn);
        }

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        Debug.Log("[LightingSetup] done");
    }

    [MenuItem("Apartment/Bake Lighting")]
    public static void Bake()
    {
        EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene());
        Lightmapping.bakeCompleted -= AfterBake;
        Lightmapping.bakeCompleted += AfterBake;
        Lightmapping.BakeAsync();
        Debug.Log("[LightingSetup] bake started");
    }

    // Occlusion culling: interior walls hide most of the apartment from any one spot (a big
    // saving on Quest). Glass and cutout foliage must not occlude, or the windows would hide
    // the outdoor backdrop. Cells are sized for small rooms so doorways stay open.
    [MenuItem("Apartment/Bake Occlusion")]
    public static void BakeOcclusion()
    {
        int cleared = 0;
        foreach (var r in Object.FindObjectsOfType<MeshRenderer>())
        {
            var flags = GameObjectUtility.GetStaticEditorFlags(r.gameObject);
            if ((flags & StaticEditorFlags.OccluderStatic) == 0)
                continue;
            if (r.sharedMaterials.Any(m => m != null && m.renderQueue >= 2450))       // alpha-test or transparent
            {
                GameObjectUtility.SetStaticEditorFlags(r.gameObject, flags & ~StaticEditorFlags.OccluderStatic);
                cleared++;
            }
        }
        // Room-sized objects (the ceiling, floors, and the packages built in plan coordinates
        // like the wall-art sets) were being culled from inside the rooms they cover. They gain
        // nothing from culling, so they're always drawn; the ceiling and floors don't occlude.
        int huge = 0;
        foreach (var r in Object.FindObjectsOfType<MeshRenderer>())
        {
            var flags = GameObjectUtility.GetStaticEditorFlags(r.gameObject);
            var sz = r.bounds.size;
            bool flat = r.name.Contains("ceiling") || r.name.Contains("floor");
            if (Mathf.Max(sz.x, sz.z) > 3f || flat)
            {
                flags &= ~StaticEditorFlags.OccludeeStatic;
                if (flat) flags &= ~StaticEditorFlags.OccluderStatic;
                GameObjectUtility.SetStaticEditorFlags(r.gameObject, flags);
                huge++;
            }
        }
        StaticOcclusionCulling.smallestOccluder = 0.25f;
        StaticOcclusionCulling.smallestHole = 0.2f;
        StaticOcclusionCulling.backfaceThreshold = 100f;
        StaticOcclusionCulling.Compute();
        var scene = EditorSceneManager.GetActiveScene();
        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        Debug.Log($"[LightingSetup] occlusion baked ({cleared} see-through renderers kept as occludees only, {huge} room-sized always drawn)");
    }

    // The Light Volumes package queues its atlas packing after a bake, and the queued job
    // doesn't always run (the volumes then stay switched off). Once the package has saved
    // its volume textures, pack the atlas ourselves and save the scene when it's done.
    static void AfterBake()
    {
        Lightmapping.bakeCompleted -= AfterBake;
        int frames = 0;
        void Wait()
        {
            if (++frames < 30)
                return;                                     // let the package save its textures first
            EditorApplication.update -= Wait;
            var manager = Object.FindObjectsOfType<MonoBehaviour>().FirstOrDefault(m => m.GetType().Name == "LightVolumeManager");
            if (manager == null)
                return;
            foreach (var asm in System.AppDomain.CurrentDomain.GetAssemblies())
            {
                var gen = asm.GetType("VRCLightVolumes.LightVolumeManagerTools")?.GetMethod("GenerateAtlas", new[] { manager.GetType() });
                if (gen == null)
                    continue;
                gen.Invoke(null, new object[] { manager });
                break;
            }
            double deadline = EditorApplication.timeSinceStartup + 120;
            void SaveWhenPacked()
            {
                var atlas = new SerializedObject(manager).FindProperty("LightVolumeAtlas").objectReferenceValue;
                if (atlas == null && EditorApplication.timeSinceStartup < deadline)
                    return;
                EditorApplication.update -= SaveWhenPacked;
                EditorSceneManager.MarkSceneDirty(manager.gameObject.scene);
                EditorSceneManager.SaveScene(manager.gameObject.scene);
                Debug.Log(atlas != null ? "[LightingSetup] bake done, Light Volume atlas packed" : "[LightingSetup] Light Volume atlas didn't pack");
                BakeOcclusion();
            }
            EditorApplication.update += SaveWhenPacked;
        }
        EditorApplication.update += Wait;
    }
}
