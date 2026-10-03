// Puts USharpVideo (Assets/USharpVideo, MIT) on the living-room TV: the player's own
// screen quad is laid over the wall_tv's `wall_tv_screen` panel, and the controls go on the
// center wall beside the TV at hand height. Apartment > Setup TV Video; Build Apartment
// Scene runs it too.

using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class VideoSetup
{
    const float IN = 0.0254f * ApartmentSetup.WorldScale;   // inches, at the world's build scale
    const string PlayerPrefab = "Assets/USharpVideo/USharpVideo.prefab";

    // Controls panel: plan (x, y, z) inches on the center wall's living-room face, and width.
    // South of the TV, between it and the media hutch: north of the TV are the wall heater
    // and the thermostat (wall_plates living_thermostat at y 108.2).
    static readonly Vector3 ControlsSpot = new Vector3(134f, 38f, 46f);
    const float ControlsWidth = 0.5f;

    [MenuItem("Apartment/Setup TV Video")]
    public static void Setup()
    {
        var old = GameObject.Find("tv_video_player");
        if (old != null)
            Object.DestroyImmediate(old);

        // The package has a wall_tv inside a wall_tv, so GameObject.Find("wall_tv") can return the
        // inner one with no screen: start from the screen and take its outermost wall_tv.
        var screen = Object.FindObjectsOfType<Transform>().FirstOrDefault(t => t.name == "wall_tv_screen");
        if (screen == null)
        {
            Debug.LogWarning("[VideoSetup] no wall_tv_screen in the scene");
            return;
        }
        Transform tv = screen.parent;
        for (var t = screen.parent; t != null; t = t.parent)
            if (t.name == "wall_tv")
                tv = t;

        // Package objects face local +Z in Unity (Blender's -Y front).
        var normal = tv.rotation * Vector3.forward;
        var b = screen.GetComponent<Renderer>().bounds;
        float height = b.size.y;
        float width = Vector3.ProjectOnPlane(b.size, Vector3.up).magnitude;   // the axis along the wall

        var player = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(PlayerPrefab));
        player.name = "tv_video_player";
        player.transform.SetPositionAndRotation(b.center, Quaternion.LookRotation(-normal));
        player.transform.localScale = Vector3.one;

        // The player's quad is visible from its -Z side, so it looks back along -normal.
        var quad = player.transform.Find("VideoScreen");
        quad.SetPositionAndRotation(b.center + normal * 0.002f, Quaternion.LookRotation(-normal));
        quad.localScale = new Vector3(width, height, 1f);
        var quadRenderer = quad.GetComponent<MeshRenderer>();
        quadRenderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        quadRenderer.receiveGI = ReceiveGI.LightProbes;
        GameObjectUtility.SetStaticEditorFlags(quad.gameObject, 0);

        var controls = (RectTransform)player.transform.Find("ControlsUI");
        var spot = new Vector3(-ControlsSpot.x * IN, ControlsSpot.z * IN, -ControlsSpot.y * IN) + normal * 0.01f;
        controls.SetPositionAndRotation(spot, Quaternion.LookRotation(-normal));
        float s = ControlsWidth / Mathf.Max(1f, controls.rect.width);
        controls.localScale = new Vector3(s, s, s);

        // Speakers: the TV's own, in its bezel (no sound bar in the apartment). The prefab's
        // video-mode source was nearly 2D and its stream L/R pair sat 3.5 m apart, inside the
        // walls; all three become fully 3D point-ish sources at the screen, L and R at its edges.
        var audio = player.transform.Find("AudioSources");
        audio.position = b.center + normal * 0.05f;
        var right = Vector3.Cross(Vector3.up, -normal).normalized;     // a viewer's right, facing the TV
        foreach (var src in audio.GetComponentsInChildren<AudioSource>(true))
        {
            float side = src.name.EndsWith("L") ? -1f : src.name.EndsWith("R") ? 1f : 0f;
            src.transform.position = b.center + normal * 0.05f + right * side * (width / 2f - 0.05f);
            src.spatialBlend = 1f;
            src.spread = 0f;
            src.dopplerLevel = 0f;
            var spatial = src.GetComponent<VRC.SDK3.Components.VRCSpatialAudioSource>();
            if (spatial == null)
                continue;
            spatial.EnableSpatialization = true;
            spatial.UseAudioSourceVolumeCurve = false;   // VRChat's inverse-square falloff
            spatial.Gain = 10f;
            spatial.Near = 3.5f;                       // full volume out to the couch (~3 m); a 0.5 m plateau left it 30 dB down there
            spatial.Far = 14f;                         // fades out across the apartment
            spatial.VolumetricRadius = 0.25f;           // a TV-sized source, not a point
            EditorUtility.SetDirty(spatial);
        }

        EditorSceneManager.MarkSceneDirty(player.scene);
        Debug.Log($"[VideoSetup] player on the TV: screen {width:F3} x {height:F3} m");
    }
}
