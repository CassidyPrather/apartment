// LTCGI (Packages/at.pimaker.ltcgi, MIT, _pi_) lights the room from the TV picture: an
// area light shaped like the screen, coloured by the playing video, on every LTCGI-enabled
// material (Mochie Standard has the hook). USharpVideo feeds it through LTCGI's adapter
// (LTCGI copies it into Assets/_pi_/_LTCGI-Adapters when it finds USharpVideo). Diffuse is
// LTCGI's realtime LTC diffuse, not its shadowmap bake: that bake stops on a modal dialog,
// and the TV faces into the open living/dining/kitchen space with every walled room behind
// the screen, so nothing needs its occlusion. Avatars with LTCGI-aware shaders are lit too.
// PC only: Android/iOS builds turn the material keyword off and the Quest scene drops the
// controller. Apartment > Setup LTCGI; Build Apartment Scene runs it too.

using System;
using System.Linq;
using pi.LTCGI;
using UdonSharp;
using UdonSharpEditor;
using UnityEditor;
using UnityEditor.Build;
using UnityEngine;
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
        ltcgi.DiffuseFromLm = false;          // realtime LTC diffuse (see the header)
        ltcgi.LightmapChannel = 0;
        ltcgi.AffectAvatars = true;

        SetMaterials(IsPc(EditorUserBuildSettings.activeBuildTarget));
        controller.UpdateMaterials();
        Debug.Log("[LtcgiSetup] TV light set up (LTCGI)");
    }

    static bool IsPc(BuildTarget t) =>
        t == BuildTarget.StandaloneWindows || t == BuildTarget.StandaloneWindows64 || t == BuildTarget.StandaloneLinux64 || t == BuildTarget.StandaloneOSX;

    // LTCGI treats the picture as unit brightness, which barely shows next to the baked room
    // light; a real screen at night reads much stronger.
    const float Strength = 6f;

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
