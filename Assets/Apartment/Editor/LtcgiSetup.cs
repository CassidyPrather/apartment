// LTCGI (Packages/at.pimaker.ltcgi, MIT, _pi_) lights the room from the TV picture: an
// area light shaped like the screen, coloured by the playing video, on every LTCGI-enabled
// material (Mochie Standard has the hook). USharpVideo feeds it through LTCGI's adapter
// (LTCGI copies it into Assets/_pi_/_LTCGI-Adapters when it finds USharpVideo).
// Diffuse comes from LTCGI's shadowmap: a lightmap bake with only the screen emitting, so
// furniture and walls shadow it, and an LTCGI Light Volume baked in the same pass carries the
// TV's light onto avatars and moving things. LTCGI's own bake command stops on a modal
// dialog, so BakeShadowmap() below does the same preparation without it (adapted from
// LTCGI_ControllerBake.cs, MIT) and hands over to LTCGI's own completion step;
// LightingSetup.Bake runs it before the normal bake.
// PC only: Android/iOS builds turn the material keyword off and the Quest scene drops the
// controller. Apartment > Setup LTCGI; Build Apartment Scene runs it too.

using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using pi.LTCGI;
using UdonSharp;
using UdonSharpEditor;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

public static class LtcgiSetup
{
    const string ControllerPrefab = "Packages/at.pimaker.ltcgi/LTCGI Controller.prefab";
    const string BlitCrtGuid = "802e4542fd374664aa4d0858e525b454";      // LTCGI_BlitCRT.asset
    const string Black1pxGuid = "68718da77206620438ca14e29cefa6fb";     // black1px.png
    public const string RootName = "ltcgi";

    [MenuItem("Apartment/Setup LTCGI")]
    public static void Setup()
    {
        foreach (var old in Object.FindObjectsOfType<LTCGI_Controller>(true))
            Object.DestroyImmediate(old.gameObject);

        var player = GameObject.Find("tv_video_player");
        var screen = player != null ? player.transform.Find("VideoScreen") : null;
        var adapterType = TypeNamed("LTCGI_USharpVideoAdapter");
        var playerType = TypeNamed("USharpVideoPlayer");
        if (screen == null || adapterType == null || playerType == null)
        {
            Debug.LogWarning("[LtcgiSetup] needs the TV video player and LTCGI's USharpVideo adapter (Assets/_pi_/_LTCGI-Adapters)");
            return;
        }

        var root = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(ControllerPrefab));
        root.name = RootName;
        var controller = root.GetComponent<LTCGI_Controller>();

        // The adapter hands the player's current video texture to LTCGI's blit CRT.
        var crt = AssetDatabase.LoadAssetAtPath<CustomRenderTexture>(AssetDatabase.GUIDToAssetPath(BlitCrtGuid));
        var adapterGo = new GameObject("LTCGI_USharpVideoAdapter");
        adapterGo.transform.SetParent(root.transform, false);
        adapterGo.transform.SetPositionAndRotation(player.transform.position, player.transform.rotation);
        var adapter = (UdonSharpBehaviour)UdonSharpUndo.AddComponent(adapterGo, adapterType);
        var handler = player.GetComponentsInChildren<MonoBehaviour>(true).FirstOrDefault(m => m.GetType().Name == "VideoScreenHandler");
        var standby = handler != null ? handler.GetType().GetField("standbyTexture")?.GetValue(handler) as Texture : null;
        adapterType.GetField("VideoPlayer").SetValue(adapter, player.GetComponent(playerType));
        adapterType.GetField("CRT").SetValue(adapter, crt);
        adapterType.GetField("StandbyTexture").SetValue(adapter,
            standby != null ? standby : AssetDatabase.LoadAssetAtPath<Texture2D>(AssetDatabase.GUIDToAssetPath(Black1pxGuid)));
        UdonSharpEditorUtility.CopyProxyToUdon(adapter);
        controller.VideoTexture = crt;
        controller.ConfiguredAdapter = adapterGo;

        // The light-emitting quad: exactly the TV's picture (the player's own screen quad),
        // hidden; LTCGI reads its corners.
        var quad = GameObject.CreatePrimitive(PrimitiveType.Quad);
        Object.DestroyImmediate(quad.GetComponent<Collider>());
        quad.name = "ltcgi_tv_screen";
        quad.transform.SetParent(adapterGo.transform, true);
        quad.transform.SetPositionAndRotation(screen.position, screen.rotation);
        quad.transform.localScale = Vector3.one;
        var s = screen.lossyScale;
        quad.transform.localScale = new Vector3(s.x / quad.transform.lossyScale.x, s.y / quad.transform.lossyScale.y, 1f);
        var qr = quad.GetComponent<MeshRenderer>();
        qr.enabled = false;
        GameObjectUtility.SetStaticEditorFlags(quad, 0);
        var ltcgi = quad.AddComponent<LTCGI_Screen>();
        ltcgi.ColorMode = ColorMode.Texture;
        ltcgi.TextureIndex = 0;
        ltcgi.Diffuse = true;
        ltcgi.Specular = true;
        ltcgi.DiffuseFromLm = true;           // shadowed diffuse from the shadowmap bake
        ltcgi.LightmapChannel = 1;
        ltcgi.AffectAvatars = true;
        ltcgi.AffectLightVolumes = true;

        SetMaterials(IsPc(EditorUserBuildSettings.activeBuildTarget));
        controller.UpdateMaterials();
        AddVolume();
        Debug.Log("[LtcgiSetup] TV light set up (LTCGI)");
    }

    // The LTCGI Light Volume over the open living/dining/kitchen space the TV faces. It lives
    // under LightingSetup's "lighting" root because that setup replaces the Light Volume
    // manager (and so every registration); LightingSetup.Setup calls this at its end.
    const string VolumeName = "ltcgi_volume";
    public static void AddVolume()
    {
        foreach (var t in Object.FindObjectsOfType<Transform>(true).Where(t => t.name == VolumeName).ToArray())
            Object.DestroyImmediate(t.gameObject);
        var lighting = GameObject.Find("lighting");
        var lvType = TypeNamed("LightVolumeLTCGI");
        if (Object.FindObjectOfType<LTCGI_Controller>() == null || lighting == null || lvType == null)
            return;
        var go = new GameObject(VolumeName);
        go.transform.SetParent(lighting.transform, false);
        const float IN = 0.0254f * ApartmentSetup.WorldScale;
        float x0 = 4f, x1 = 130f, y0 = 4f, y1 = 282f, h = 108f;      // plan inches, inside the walls
        go.transform.position = new Vector3(-(x0 + x1) / 2 * IN, h / 2 * IN, -(y0 + y1) / 2 * IN);
        go.transform.localScale = new Vector3((x1 - x0) * IN, h * IN, (y1 - y0) * IN);
        var volume = (VRCLightVolumes.LightVolumeInstance)UdonSharpUndo.AddComponent(go, lvType);
        volume.IsAdditive = true;
        volume.IsDynamic = false;
        volume.Bake = true;
        volume.VoxelsPerUnit = 3f;
        VRCLightVolumes.LightVolumeTools.ApplyRuntimeState(volume, false);
        var asm = typeof(VRCLightVolumes.LightVolumeTools).Assembly;
        asm.GetType("VRCLightVolumes.LightVolumeSceneSetup")
            .GetMethod("OnboardHierarchy", BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public)
            .Invoke(null, new object[] { go, null, true });
        asm.GetType("VRCLightVolumes.LightVolumeManagerEditorBackend")
            .GetMethod("CopyProxyToUdon", BindingFlags.Static | BindingFlags.NonPublic | BindingFlags.Public)
            .Invoke(null, new object[] { volume });
    }

    // LTCGI's shadowmap bake minus its "don't touch the scene" dialog: lights, reflection
    // probes, ambient and every material's emission off, the screen quad a lightmap emitter
    // (red = channel 1), bake, then LTCGI's BakeComplete (copies the lightmaps into
    // Assets/LTCGI-Generated, records each renderer's lightmap offset, saves the LTCGI Light
    // Volume's textures, restores the scene). Returns false when there's nothing to bake.
    public static bool BakeShadowmap(Action then)
    {
        var ctrl = Object.FindObjectOfType<LTCGI_Controller>();
        var screens = Object.FindObjectsOfType<LTCGI_Screen>().Where(s => s.enabled && s.LightmapChannel != 0).ToArray();
        if (ctrl == null || screens.Length == 0 || Lightmapping.isRunning)
            return false;
        const BindingFlags F = BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.Public;
        var T = typeof(LTCGI_Controller);

        ctrl.UpdateMaterials();
        Lightmapping.giWorkflowMode = Lightmapping.GIWorkflowMode.OnDemand;

        var keys = new List<Material>();
        var vals = new List<MaterialGlobalIlluminationFlags>();
        foreach (var r in Object.FindObjectsOfType<Renderer>())
            foreach (var m in r.sharedMaterials)
                if (m != null && !keys.Contains(m))
                {
                    keys.Add(m);
                    vals.Add(m.globalIlluminationFlags);
                    m.globalIlluminationFlags = MaterialGlobalIlluminationFlags.EmissiveIsBlack;
                }
        T.GetField("bakeMaterialReset_key", F).SetValue(ctrl, keys);
        T.GetField("bakeMaterialReset_val", F).SetValue(ctrl, vals);

        var resets = new Dictionary<GameObject, LTCGI_BakeReset>();
        LTCGI_BakeReset Reset(GameObject go)
        {
            if (!resets.TryGetValue(go, out var r))
                resets[go] = r = go.AddComponent<LTCGI_BakeReset>();
            return r;
        }
        foreach (var l in Object.FindObjectsOfType<Light>())
            if (l.gameObject.activeSelf) { l.gameObject.SetActive(false); Reset(l.gameObject).Reenable = true; }
        foreach (var p in Object.FindObjectsOfType<ReflectionProbe>())
            if (p.gameObject.activeSelf) { p.gameObject.SetActive(false); Reset(p.gameObject).Reenable = true; }

        T.GetField("previousAmbientMode", F).SetValue(ctrl, RenderSettings.ambientMode);
        T.GetField("previousAmbientIntensity", F).SetValue(ctrl, RenderSettings.ambientIntensity);
        T.GetField("previousAmbientColor", F).SetValue(ctrl, RenderSettings.ambientSkyColor);
        RenderSettings.ambientMode = AmbientMode.Flat;
        RenderSettings.ambientIntensity = 0f;
        RenderSettings.ambientSkyColor = Color.black;

        foreach (var scr in screens)
        {
            var rend = scr.GetComponent<MeshRenderer>();
            if (rend == null) continue;
            float k = ctrl.LightmapIntensity * scr.LightmapIntensity;
            var col = scr.LightmapChannel == 1 ? new Color(k, 0, 0, 1) : scr.LightmapChannel == 2 ? new Color(0, k, 0, 1) : new Color(0, 0, k, 1);
            var mat = new Material(Shader.Find("Standard"));
            mat.SetColor("_EmissionColor", col);
            mat.EnableKeyword("_EMISSION");
            mat.doubleSidedGI = scr.DoubleSided;
            mat.globalIlluminationFlags = MaterialGlobalIlluminationFlags.BakedEmissive;
            var flags = GameObjectUtility.GetStaticEditorFlags(rend.gameObject);
            var r = Reset(rend.gameObject);
            r.ResetData = true;
            r.Materials = rend.sharedMaterials;
            r.Flags = flags;
            r.ShadowCastingMode = rend.shadowCastingMode;
            if (rend.shadowCastingMode == ShadowCastingMode.Off || rend.shadowCastingMode == ShadowCastingMode.ShadowsOnly)
                rend.shadowCastingMode = ShadowCastingMode.On;
            rend.sharedMaterials = new[] { mat };
            GameObjectUtility.SetStaticEditorFlags(rend.gameObject, flags | StaticEditorFlags.ContributeGI);
            if (!rend.enabled) { rend.enabled = true; r.DisableRendererComponents = new Renderer[] { rend }; }
        }

        ctrl.bakeInProgress = true;
        EditorSceneManager.MarkSceneDirty(ctrl.gameObject.scene);
        EditorSceneManager.SaveOpenScenes();
        if (!AssetDatabase.IsValidFolder("Assets/LTCGI-Generated"))
            AssetDatabase.CreateFolder("Assets", "LTCGI-Generated");

        // LTCGI's completion copies the LTCGI volume's textures, so wait for Light Volumes to
        // bake them (it does so on its own after a lightmap bake) before handing over.
        var lvType = TypeNamed("LightVolumeLTCGI");
        var volumes = lvType == null ? new VRCLightVolumes.LightVolumeInstance[0]
            : Object.FindObjectsOfType(lvType).Cast<VRCLightVolumes.LightVolumeInstance>().ToArray();
        var before = volumes.Select(v => v.Texture0).ToArray();
        void Done()
        {
            Lightmapping.bakeCompleted -= Done;
            double deadline = EditorApplication.timeSinceStartup + 120;
            void Wait()
            {
                bool ready = volumes.Select((v, i) => v != null && v.Texture0 != null && v.Texture0 != before[i]).All(b => b);
                if (!ready && EditorApplication.timeSinceStartup < deadline)
                    return;
                EditorApplication.update -= Wait;
                if (!ready)
                    Debug.LogWarning("[LtcgiSetup] the LTCGI Light Volume did not rebake; its avatar light may be stale");
                T.GetMethod("BakeComplete", F).Invoke(ctrl, null);
                Debug.Log("[LtcgiSetup] shadowmap baked");
                then?.Invoke();
            }
            EditorApplication.update += Wait;
        }
        Lightmapping.bakeCompleted += Done;
        Lightmapping.BakeAsync();
        Debug.Log("[LtcgiSetup] shadowmap bake started");
        return true;
    }

    static bool IsPc(BuildTarget t) =>
        t == BuildTarget.StandaloneWindows || t == BuildTarget.StandaloneWindows64 || t == BuildTarget.StandaloneLinux64 || t == BuildTarget.StandaloneOSX;

    // Material multiplier on LTCGI's light. Unit brightness barely showed next to the baked
    // room light; 4 puts the shadowmapped walls and floor on par with what the LTCGI Light
    // Volume gives avatars (the volume doesn't use this).
    const float Strength = 4f;

    // Every scene material whose shader has the LTCGI hook (Mochie's "LTCGI"="_LTCGI" tag).
    public static int SetMaterials(bool on)
    {
        int n = 0;
        var mats = Object.FindObjectsOfType<Renderer>(true).SelectMany(r => r.sharedMaterials)
            .Where(m => m != null && m.GetTag("LTCGI", false) == "_LTCGI").Distinct();
        foreach (var m in mats)
        {
            m.SetFloat("_LTCGI", on ? 1f : 0f);
            m.SetFloat("_LTCGIStrength", Strength);
            if (on) m.EnableKeyword("LTCGI"); else m.DisableKeyword("LTCGI");
            EditorUtility.SetDirty(m);
            n++;
        }
        return n;
    }

    static Type TypeNamed(string name) => AppDomain.CurrentDomain.GetAssemblies()
        .SelectMany(a => { try { return a.GetTypes(); } catch { return Array.Empty<Type>(); } })
        .FirstOrDefault(t => t.Name == name && typeof(UdonSharpBehaviour).IsAssignableFrom(t));

    // Switching to Android/iOS turns LTCGI off on the shared materials; back to PC turns it on.
    class PlatformSwitch : IActiveBuildTargetChanged
    {
        public int callbackOrder => 0;
        public void OnActiveBuildTargetChanged(BuildTarget previous, BuildTarget current)
        {
            int n = SetMaterials(IsPc(current));
            AssetDatabase.SaveAssets();
            Debug.Log($"[LtcgiSetup] {current}: LTCGI {(IsPc(current) ? "on" : "off")} on {n} materials");
        }
    }
}
