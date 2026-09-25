// Builds the filing cabinet set from the Blender exports: texture import settings,
// FBX material remaps, per-item prefabs, the drawer grab handles, the set prefab,
// and a test scene. Rerun after any re-export: Apartment > Build Filing Cabinet Set.
//
// Inputs come from blender/lib (build_filing_cabinet_set.py): one FBX per item in
// Assets/Apartment/Models, atlases in Assets/Apartment/Textures, and marker empties
// in filing_cabinet.fbx (filing_cabinet_drawer_N_grab at each pull, place_<item>
// where each item sits on the top).

using System.Collections.Generic;
using System.IO;
using UdonSharp;
using UdonSharpEditor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using VRC.SDK3.Components;

public static class FilingCabinetSetup
{
    const string Root = "Assets/Apartment";
    const string Models = Root + "/Models";
    const string Textures = Root + "/Textures";
    const string Materials = Root + "/Materials";
    const string Prefabs = Root + "/Prefabs";
    const string Scenes = Root + "/Scenes";
    // Mochie's Quest-grade standard shader (vendored in Assets/Mochie, MIT). It reads
    // VRC Light Volumes, additive volumes on lightmapped surfaces included, and falls
    // back to Unity light probes when a scene has no volumes.
    const string ShaderName = "Mochie/Standard Mobile";
    const string MochieDfg = "Assets/Mochie/Unity/Textures/dfg-multiscatter.exr";

    // dimensions.CABINET["drawer_travel"] (22 in, estimate).
    const float DrawerTravel = 22f * 0.0254f;

    static readonly string[] Items = { "router", "modem", "vr_headset" };

    const StaticEditorFlags StaticFlags = StaticEditorFlags.ContributeGI | StaticEditorFlags.BatchingStatic |
                                          StaticEditorFlags.OccluderStatic | StaticEditorFlags.OccludeeStatic |
                                          StaticEditorFlags.ReflectionProbeStatic;

    [MenuItem("Apartment/Build Filing Cabinet Set")]
    public static void Build()
    {
        foreach (var dir in new[] { Materials, Prefabs, Scenes })
            Directory.CreateDirectory(dir);
        if (EnsureProgramAsset())
        {
            Debug.LogWarning("[FilingCabinetSetup] Created the SlidingDrawer program asset; " +
                             "run Apartment > Build Filing Cabinet Set again once UdonSharp finishes compiling.");
            return;
        }
        ConfigureTextures();
        var mats = BuildMaterials();
        ConfigureModels(mats);
        var itemPrefabs = new Dictionary<string, GameObject>();
        foreach (var item in Items)
            itemPrefabs[item] = BuildStaticItem(item, withCollider: true);
        itemPrefabs["cable_stubs"] = BuildStaticItem("cable_stubs", withCollider: false);
        var cabinet = BuildCabinet();
        var set = BuildSet(cabinet, itemPrefabs);
        BuildTestScene(set);
        AssetDatabase.SaveAssets();
        Debug.Log("[FilingCabinetSetup] done");
    }

    // --- textures ---------------------------------------------------------------

    internal static void ConfigureTextures()
    {
        foreach (var guid in AssetDatabase.FindAssets("t:Texture2D", new[] { Textures }))
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            var name = Path.GetFileNameWithoutExtension(path);
            var imp = (TextureImporter)AssetImporter.GetAtPath(path);
            bool isMask = name.EndsWith("_mask");
            // Masks are mostly flat regions and emission maps are black but for a few
            // LEDs, so they drop to 512; the hardware atlas is authored at 512.
            bool small = name.StartsWith("cabinet_hardware") || name.EndsWith("_emission") ||
                         (isMask && !name.StartsWith("cabinet_paint")) || name.StartsWith("shell_trim");
            int size = small ? 512 : 1024;
            imp.textureType = TextureImporterType.Default;
            imp.sRGBTexture = !isMask;
            imp.alphaSource = TextureImporterAlphaSource.FromInput;
            imp.alphaIsTransparency = false;
            imp.mipmapEnabled = true;
            imp.wrapMode = name.StartsWith("cabinet_paint") || name.StartsWith("shell_") ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;
            imp.anisoLevel = 2;
            imp.maxTextureSize = size;
            imp.textureCompression = TextureImporterCompression.Compressed;
            imp.crunchedCompression = false;
            imp.SetPlatformTextureSettings(new TextureImporterPlatformSettings
            {
                name = "Android", overridden = true, maxTextureSize = size,
                format = TextureImporterFormat.ASTC_6x6,
            });
            imp.SaveAndReimport();
        }
    }

    // --- materials --------------------------------------------------------------

    static Texture2D Tex(string name) =>
        AssetDatabase.LoadAssetAtPath<Texture2D>($"{Textures}/{name}.png");

    // A clean Mochie material at `name`, keeping the asset's GUID across reruns so
    // the FBX remaps and prefabs stay linked; stale properties are wiped each time.
    internal static Material MochieMat(string name)
    {
        var path = $"{Materials}/{name}.mat";
        var shader = Shader.Find(ShaderName);
        var fresh = new Material(shader) { name = name };
        var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (mat == null)
        {
            AssetDatabase.CreateAsset(fresh, path);
            mat = fresh;
        }
        else
        {
            EditorUtility.CopySerialized(fresh, mat);
            Object.DestroyImmediate(fresh);
        }
        mat.SetTexture("_DFG", AssetDatabase.LoadAssetAtPath<Texture>(MochieDfg));
        // Unused features' default textures would otherwise ride along into every build.
        mat.SetTexture("_NoiseTexSSR", null);
        mat.SetTexture("_WindNoiseTex", null);
        mat.SetInt("_BicubicSampling", 0);          // bicubic lightmaps cost too much on Quest
        mat.SetInt("_LightVolumesToggle", 1);
        mat.SetInt("_AdditiveLightVolumesToggle", 1);
        return mat;
    }

    // Mirrors the keyword half of Mochie's StandardEditor.SetKeywords for the features
    // used here, so script-built materials match what the inspector would produce.
    internal static void MochieKeywords(Material mat)
    {
        mat.shaderKeywords = new string[0];
        MaterialEditor.FixupEmissiveFlag(mat);
        bool emissive = (mat.globalIlluminationFlags & MaterialGlobalIlluminationFlags.EmissiveIsBlack) == 0;
        mat.SetInt("_SampleMetallic", mat.GetTexture("_MetallicMap") ? 1 : 0);
        mat.SetInt("_SampleRoughness", mat.GetTexture("_RoughnessMap") ? 1 : 0);
        mat.SetInt("_SampleOcclusion", mat.GetTexture("_OcclusionMap") ? 1 : 0);
        void Kw(string k, bool on) { if (on) mat.EnableKeyword(k); else mat.DisableKeyword(k); }
        Kw("_EMISSION_ON", emissive);
        Kw("_REFLECTIONS_ON", mat.GetInt("_ReflectionsToggle") == 1);
        Kw("_SPECULAR_HIGHLIGHTS_ON", mat.GetInt("_SpecularHighlightsToggle") == 1);
        Kw("_WORKFLOW_PACKED_ON", mat.GetInt("_PrimaryWorkflow") == 1);
        Kw("_BICUBIC_SAMPLING_ON", mat.GetInt("_BicubicSampling") == 1);
        EditorUtility.SetDirty(mat);
    }

    internal static Material Mat(string name, string atlas, Color tint)
    {
        var mat = MochieMat(name);
        mat.SetTexture("_MainTex", Tex(atlas + "_albedo"));
        mat.SetColor("_Color", tint);
        // Our masks: metallic in R, smoothness in A; G and B are empty, so occlusion
        // (which Mochie reads from R by default) must be switched off.
        mat.SetInt("_PrimaryWorkflow", 1);
        mat.SetTexture("_PackedMap", Tex(atlas + "_mask"));
        mat.SetInt("_SmoothnessToggle", 1);
        mat.SetInt("_MetallicChannel", 0);
        mat.SetInt("_RoughnessChannel", 3);
        mat.SetFloat("_PackedMetallicStrength", 1f);
        mat.SetFloat("_PackedRoughnessStrength", 1f);
        mat.SetFloat("_PackedOcclusionStrength", 0f);
        var emission = Tex(atlas + "_emission");
        if (emission != null)
        {
            mat.SetTexture("_EmissionMap", emission);
            mat.SetColor("_EmissionColor", Color.white);
            // Status LEDs glow in-view only; keep them out of the lightmap bake.
            mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.None;
        }
        else
        {
            mat.SetColor("_EmissionColor", Color.black);
            mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.EmissiveIsBlack;
        }
        MochieKeywords(mat);
        return mat;
    }

    static Dictionary<string, Material> BuildMaterials()
    {
        var hardware = Mat("cabinet_hardware", "cabinet_hardware", Color.white);
        // Metals are almost all reflection, so the hardware also takes speculars from
        // the Light Volumes; on dielectrics that cost buys little.
        hardware.SetInt("_LightVolumeSpecularity", 1);
        EditorUtility.SetDirty(hardware);
        return new Dictionary<string, Material>
        {
            // Keys are the Blender material names carried in the FBX files.
            ["cabinet_paint"] = Mat("cabinet_paint", "cabinet_paint", Color.white),
            ["cabinet_interior"] = Mat("cabinet_interior", "cabinet_paint", new Color(0.55f, 0.55f, 0.55f)),
            ["cabinet_hardware"] = hardware,
            ["router"] = Mat("router", "router", Color.white),
            ["modem"] = Mat("modem", "modem", Color.white),
            ["vr_headset"] = Mat("vr_headset", "vr_headset", Color.white),
            ["vr_headset_shell"] = ShellMat("vr_headset_shell", "vr_headset", 0.72f),   // vr_headset.SHELL_ALPHA
        };
    }

    // Tinted translucent plastic (the headset's visor shell): Mochie's Transparent
    // mode, premultiplied so glossy highlights stay bright over what shows through.
    internal static Material ShellMat(string name, string atlas, float alpha)
    {
        var mat = Mat(name, atlas, new Color(1f, 1f, 1f, alpha));
        mat.SetColor("_EmissionColor", Color.black);      // the LED glow lives on the internals
        mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.EmissiveIsBlack;
        MochieKeywords(mat);
        mat.SetInt("_BlendMode", 3);
        Mochie.StandardEditor.SetBlendMode(mat);
        EditorUtility.SetDirty(mat);
        return mat;
    }

    // --- models -----------------------------------------------------------------

    // models: the FBX file names to configure (without extension); null = the cabinet set's.
    internal static void ConfigureModels(Dictionary<string, Material> mats, string[] models = null)
    {
        models = models ?? new[] { "filing_cabinet", "router", "modem", "vr_headset", "cable_stubs" };
        foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { Models }))
        {
            var path = AssetDatabase.GUIDToAssetPath(guid);
            if (System.Array.IndexOf(models, Path.GetFileNameWithoutExtension(path)) < 0)
                continue;
            var imp = (ModelImporter)AssetImporter.GetAtPath(path);
            imp.globalScale = 1f;
            imp.useFileScale = true;
            imp.importAnimation = false;
            imp.importCameras = false;
            imp.importLights = false;
            imp.importBlendShapes = false;
            imp.animationType = ModelImporterAnimationType.None;
            imp.isReadable = false;
            imp.meshCompression = ModelImporterMeshCompression.Off;
            imp.importNormals = ModelImporterNormals.Import;
            LightmapUVs(imp);
            imp.addCollider = false;
            imp.materialImportMode = ModelImporterMaterialImportMode.ImportViaMaterialDescription;
            imp.materialLocation = ModelImporterMaterialLocation.InPrefab;
            foreach (var kv in mats)
                imp.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), kv.Key), kv.Value);
            imp.SaveAndReimport();
            foreach (var r in AssetDatabase.LoadAssetAtPath<GameObject>(path).GetComponentsInChildren<Renderer>())
                foreach (var m in r.sharedMaterials)
                    if (m == null || m.shader.name != ShaderName)
                        Debug.LogWarning($"[FilingCabinetSetup] {path}: {r.name} has an unmapped material {m?.name}");
        }
    }

    // Unity's unwrapper, with the margin worked out for the scene's lightmap resolution:
    // Blender's packed UV2 overlapped once small parts got only a few texels.
    internal static void LightmapUVs(ModelImporter imp)
    {
        imp.generateSecondaryUV = true;
        imp.secondaryUVMarginMethod = ModelImporterSecondaryUVMarginMethod.Calculate;
        imp.secondaryUVMinLightmapResolution = 20f;
        imp.secondaryUVMinObjectScale = 1f;
        imp.secondaryUVHardAngle = 70f;
    }

    [MenuItem("Apartment/Regenerate Lightmap UVs")]
    static void RegenerateLightmapUVs()
    {
        foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { Models }))
        {
            var imp = (ModelImporter)AssetImporter.GetAtPath(AssetDatabase.GUIDToAssetPath(guid));
            LightmapUVs(imp);
            imp.SaveAndReimport();
        }
    }

    static GameObject Instantiate(string model)
    {
        var src = AssetDatabase.LoadAssetAtPath<GameObject>($"{Models}/{model}.fbx");
        var go = (GameObject)PrefabUtility.InstantiatePrefab(src);
        go.name = model;
        return go;
    }

    internal static BoxCollider FitCollider(GameObject go, Renderer r)
    {
        var mf = r.GetComponent<MeshFilter>();
        var col = go.AddComponent<BoxCollider>();
        var b = mf.sharedMesh.bounds;
        // Bounds are in the renderer's local space; express them in go's space.
        var center = go.transform.InverseTransformPoint(r.transform.TransformPoint(b.center));
        col.center = center;
        col.size = Vector3.Scale(b.size, r.transform.lossyScale);
        return col;
    }

    static GameObject BuildStaticItem(string model, bool withCollider)
    {
        var go = Instantiate(model);
        foreach (var t in go.GetComponentsInChildren<Transform>())
            GameObjectUtility.SetStaticEditorFlags(t.gameObject, StaticFlags);
        if (withCollider)
            foreach (var r in go.GetComponentsInChildren<MeshRenderer>())
                FitCollider(r.gameObject, r);
        var prefab = PrefabUtility.SaveAsPrefabAsset(go, $"{Prefabs}/{model}.prefab");
        Object.DestroyImmediate(go);
        return prefab;
    }

    // --- cabinet with pull-out drawers ------------------------------------------

    static GameObject BuildCabinet()
    {
        var go = Instantiate("filing_cabinet");
        try
        {
            return BuildCabinet(go);
        }
        finally
        {
            Object.DestroyImmediate(go);
        }
    }

    static GameObject BuildCabinet(GameObject go)
    {
        var body = go.transform.Find("filing_cabinet_body");
        foreach (var name in new[] { "filing_cabinet_body", "corner_guard_fl", "corner_guard_fr" })
            GameObjectUtility.SetStaticEditorFlags(go.transform.Find(name).gameObject, StaticFlags);
        FitCollider(body.gameObject, body.GetComponent<MeshRenderer>());

        for (int i = 1; go.transform.Find($"filing_cabinet_drawer_{i}") != null; i++)
        {
            var drawer = go.transform.Find($"filing_cabinet_drawer_{i}");
            var grab = go.transform.Find($"filing_cabinet_drawer_{i}_grab");
            // Opening direction: from the cabinet's center out through the drawer face,
            // flattened, in the shared parent's space.
            var axis = drawer.localPosition - body.localPosition;
            axis.y = 0f;
            axis = Mathf.Abs(axis.z) > Mathf.Abs(axis.x) ? new Vector3(0, 0, Mathf.Sign(axis.z))
                                                         : new Vector3(Mathf.Sign(axis.x), 0, 0);
            // Drawer collider: the box behind the face, stopping at the face so the
            // pull stays reachable for the grab handle.
            var dr = drawer.GetComponent<MeshRenderer>();
            var b = dr.GetComponent<MeshFilter>().sharedMesh.bounds;
            var local = drawer.InverseTransformDirection(go.transform.TransformDirection(axis));
            var col = drawer.gameObject.AddComponent<BoxCollider>();
            var min = b.min; var max = b.max;
            if (local.z > 0.5f) max.z = 0f; else if (local.z < -0.5f) min.z = 0f;
            else if (local.x > 0.5f) max.x = 0f; else if (local.x < -0.5f) min.x = 0f;
            col.center = (min + max) / 2f;
            col.size = max - min;

            var rb = grab.gameObject.AddComponent<Rigidbody>();
            rb.isKinematic = true;
            rb.useGravity = false;
            var gcol = grab.gameObject.AddComponent<BoxCollider>();
            gcol.size = new Vector3(0.16f, 0.045f, 0.045f);
            var pickup = grab.gameObject.AddComponent<VRCPickup>();
            var so = new SerializedObject(pickup);
            so.FindProperty("AutoHold").enumValueIndex = 2;          // No: release lets go
            so.FindProperty("orientation").enumValueIndex = 0;       // Any
            so.FindProperty("InteractionText").stringValue = "Pull";
            so.FindProperty("proximity").floatValue = 0.4f;
            so.ApplyModifiedPropertiesWithoutUndo();
            var sd = UdonSharpUndo.AddComponent<SlidingDrawer>(grab.gameObject);
            sd.drawer = drawer;
            sd.slideAxis = axis;
            sd.maxTravel = DrawerTravel;
            sd.snapClosed = 0.01f;
            UdonSharpEditorUtility.CopyProxyToUdon(sd);
        }
        return PrefabUtility.SaveAsPrefabAsset(go, $"{Prefabs}/filing_cabinet.prefab");
    }

    // True when the asset had to be created: UdonSharp must compile it before a
    // SlidingDrawer can be added, so the caller stops and asks for a rerun.
    static bool EnsureProgramAsset()
    {
        const string path = Root + "/Scripts/SlidingDrawer.asset";
        if (AssetDatabase.LoadAssetAtPath<UdonSharpProgramAsset>(path) != null)
            return false;
        var asset = ScriptableObject.CreateInstance<UdonSharpProgramAsset>();
        asset.sourceCsScript = AssetDatabase.LoadAssetAtPath<MonoScript>(Root + "/Scripts/SlidingDrawer.cs");
        AssetDatabase.CreateAsset(asset, path);
        AssetDatabase.SaveAssets();
        UdonSharpProgramAsset.CompileAllCsPrograms(true);
        return true;
    }

    // --- set and scene ----------------------------------------------------------

    static GameObject BuildSet(GameObject cabinet, Dictionary<string, GameObject> items)
    {
        var root = new GameObject("filing_cabinet_set");
        var cab = (GameObject)PrefabUtility.InstantiatePrefab(cabinet, root.transform);
        foreach (var item in Items)
        {
            var marker = cab.transform.Find("place_" + item);
            var inst = (GameObject)PrefabUtility.InstantiatePrefab(items[item], root.transform);
            inst.transform.SetPositionAndRotation(marker.position, marker.rotation);
        }
        PrefabUtility.InstantiatePrefab(items["cable_stubs"], root.transform);   // built in cabinet space
        var prefab = PrefabUtility.SaveAsPrefabAsset(root, $"{Prefabs}/filing_cabinet_set.prefab");
        Object.DestroyImmediate(root);
        return prefab;
    }

    // Untextured, non-metallic stand-in surfaces for the test scene.
    internal static Material PlainMat(string name, Color color)
    {
        var mat = MochieMat(name);
        mat.SetColor("_Color", color);
        mat.SetFloat("_MetallicStrength", 0f);
        mat.SetFloat("_RoughnessStrength", 0.85f);
        mat.SetColor("_EmissionColor", Color.black);
        mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.EmissiveIsBlack;
        MochieKeywords(mat);
        return mat;
    }

    static void BuildTestScene(GameObject set)
    {
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        var world = AssetDatabase.FindAssets("VRCWorld t:Prefab");
        if (world.Length > 0)
        {
            var vw = (GameObject)PrefabUtility.InstantiatePrefab(
                AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(world[0])));
            vw.transform.SetPositionAndRotation(new Vector3(0, 0, 1.6f), Quaternion.Euler(0, 180, 0));
        }
        var floorMat = PlainMat("test_floor", new Color(0.42f, 0.39f, 0.36f));
        var wallMat = PlainMat("test_wall", new Color(0.86f, 0.84f, 0.8f));
        var floor = GameObject.CreatePrimitive(PrimitiveType.Cube);
        floor.name = "test_floor";
        floor.transform.SetPositionAndRotation(new Vector3(0, -0.01f, 0.5f), Quaternion.identity);
        floor.transform.localScale = new Vector3(4f, 0.02f, 4f);
        floor.GetComponent<Renderer>().sharedMaterial = floorMat;
        var wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
        wall.name = "test_wall";
        // Just behind the cabinet's back panel, wherever the current dimensions put it.
        var back = set.transform.Find("filing_cabinet/filing_cabinet_body").GetComponent<MeshFilter>().sharedMesh.bounds.min.z;
        wall.transform.SetPositionAndRotation(new Vector3(0, 1.25f, back - 0.012f), Quaternion.identity);
        wall.transform.localScale = new Vector3(4f, 2.5f, 0.02f);
        wall.GetComponent<Renderer>().sharedMaterial = wallMat;
        foreach (var g in new[] { floor, wall })
            GameObjectUtility.SetStaticEditorFlags(g, StaticFlags);

        var sun = new GameObject("test_light").AddComponent<Light>();
        sun.type = LightType.Directional;
        sun.intensity = 1.0f;
        sun.shadows = LightShadows.Soft;
        sun.transform.rotation = Quaternion.Euler(50, 150, 0);
        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
        RenderSettings.ambientLight = new Color(0.45f, 0.45f, 0.47f);

        PrefabUtility.InstantiatePrefab(set);
        EditorSceneManager.SaveScene(scene, $"{Scenes}/filing_cabinet_test.unity");
    }
}
