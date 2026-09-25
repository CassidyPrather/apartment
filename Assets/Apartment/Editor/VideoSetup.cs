// Puts USharpVideo (Assets/USharpVideo, MIT) on the living-room TV: the player's own
// screen quad is laid over the wall_tv's `wall_tv_screen` panel, and the controls go on the
// center wall beside the TV at hand height. Apartment > Setup TV Video; Build Apartment
// Scene runs it too.

using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class VideoSetup
{
    const float IN = 0.0254f;
    const string PlayerPrefab = "Assets/USharpVideo/USharpVideo.prefab";

    // Controls panel: plan (x, y, z) inches on the center wall's living-room face, and width.
    static readonly Vector3 ControlsSpot = new Vector3(134f, 106f, 46f);
    const float ControlsWidth = 0.5f;

    [MenuItem("Apartment/Setup TV Video")]
    public static void Setup()
    {
        var old = GameObject.Find("tv_video_player");
        if (old != null)
            Object.DestroyImmediate(old);

        var tv = GameObject.Find("wall_tv");
        Transform screen = null;
        if (tv != null)
            foreach (var t in tv.GetComponentsInChildren<Transform>())
                if (t.name == "wall_tv_screen")
                    screen = t;
        if (screen == null)
        {
            Debug.LogWarning("[VideoSetup] no wall_tv with a wall_tv_screen child in the scene");
            return;
        }

        // Package objects face local +Z in Unity (Blender's -Y front).
        var normal = tv.transform.rotation * Vector3.forward;
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

        // Speakers at the TV.
        player.transform.Find("AudioSources").position = b.center + normal * 0.05f;

        EditorSceneManager.MarkSceneDirty(player.scene);
        Debug.Log($"[VideoSetup] player on the TV: screen {width:F3} x {height:F3} m");
    }
}
