// Ambient sound and the utility panel: looping spatial sounds for the appliances and the
// outdoors (synthesised by tools/synth_audio.py), and a breaker panel on the bedroom's back
// wall with a local "ambient sound" breaker and the project's GitHub link as copyable text.
// Apartment > Setup Audio; Build Apartment Scene runs it.

using System.Linq;
using UdonSharpEditor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.UI;

public static class AudioSetup
{
    const float IN = 0.0254f * ApartmentSetup.WorldScale;
    static Vector3 U(float x, float y, float z) => new Vector3(-x * IN, z * IN, -y * IN);

    const string GitHubUrl = "https://github.com/CassidyPrather/apartment";

    // clip, position (plan inches), volume, min/max distance (m), start offset (s), cycles on/off
    static readonly (string clip, Vector3 pos, float volume, float min, float max, float offset, bool cycle)[] Sounds =
    {
        ("pc_fan", new Vector3(151f, 17f, 39f), 0.22f, 0.4f, 5f, 0f, false),        // the tower on the desk
        ("fridge", new Vector3(116.25f, 270f, 60f), 0.28f, 0.6f, 7f, 0f, false),
        ("bath_fan", new Vector3(223.8f, 249.2f, 104f), 0.3f, 0.6f, 4.5f, 0f, false),   // the bath's fan/light
        ("portable_ac", new Vector3(12.5f, 131f, 20f), 0.35f, 0.6f, 8f, 0f, true),
        ("outside", new Vector3(-14f, 90f, 55f), 0.25f, 1.5f, 12f, 0f, false),     // past the west windows
        ("outside", new Vector3(73f, -14f, 55f), 0.25f, 1.5f, 12f, 13f, false),    // the living room's south window
        ("outside", new Vector3(215f, -14f, 55f), 0.25f, 1.5f, 12f, 27f, false),   // the bedroom window and patio door
    };

    // The real breaker panel (wall_plates package, positions.json): a flush cover painted the
    // wall colour on the bedroom's back wall under the flower print, with an 8 x 20.5 in inner
    // door at x 170.5..178.5, z 30..50.5, its face 0.22 in off the wall (y 158.18). The
    // utility UI is the panel's directory card on that door, the ambient breaker below it.
    const float PanelX0 = 170.5f, PanelX1 = 178.5f, PanelY = 158.18f, PanelZ0 = 30f, PanelZ1 = 50.5f;
    const float CardW = 6.4f, CardH = 9.6f, CardZ = 44.6f;       // card centre height (in)

    [MenuItem("Apartment/Setup Audio")]
    public static void Setup()
    {
        if (NightSetup.EnsureProgram("AmbientSound") | NightSetup.EnsureProgram("AudioToggle") | NightSetup.EnsureProgram("ApplianceSwitch"))
        {
            Debug.LogWarning("[AudioSetup] created Udon program assets; run again once UdonSharp finishes compiling");
            return;
        }
        foreach (var old in Object.FindObjectsOfType<Transform>(true).Where(t => t.name == "audio").ToArray())
            Object.DestroyImmediate(old.gameObject);
        var root = new GameObject("audio");
        var spatialType = System.AppDomain.CurrentDomain.GetAssemblies()
            .Select(a => a.GetType("VRC.SDK3.Components.VRCSpatialAudioSource")).FirstOrDefault(t => t != null);

        var sources = new System.Collections.Generic.List<AudioSource>();
        foreach (var s in Sounds)
        {
            var clip = AssetDatabase.LoadAssetAtPath<AudioClip>($"Assets/Apartment/Audio/{s.clip}.wav");
            var go = new GameObject("sound_" + s.clip);
            go.transform.SetParent(root.transform, false);
            go.transform.position = U(s.pos.x, s.pos.y, s.pos.z);
            var a = go.AddComponent<AudioSource>();
            a.clip = clip;
            a.loop = true;
            a.playOnAwake = false;                   // AmbientSound starts it at its offset
            a.volume = s.volume;
            a.spatialBlend = 1f;
            a.rolloffMode = AudioRolloffMode.Logarithmic;
            a.minDistance = s.min;
            a.maxDistance = s.max;
            a.dopplerLevel = 0f;
            a.priority = 200;
            // VRChat adds its own spatialiser with a 40 m falloff unless told to use ours.
            if (spatialType != null)
            {
                var so = new SerializedObject(go.AddComponent(spatialType));
                void Set(string n, System.Action<SerializedProperty> f) { var p = so.FindProperty(n); if (p != null) f(p); }
                Set("EnableSpatialization", p => p.boolValue = true);
                Set("UseAudioSourceVolumeCurve", p => p.boolValue = true);
                Set("Near", p => p.floatValue = s.min);
                Set("Far", p => p.floatValue = s.max);
                Set("Gain", p => p.floatValue = 0f);
                so.ApplyModifiedPropertiesWithoutUndo();
            }
            var amb = UdonSharpUndo.AddComponent<AmbientSound>(go);
            amb.source = a;
            amb.startOffset = s.offset;
            amb.cycle = s.cycle;
            UdonSharpEditorUtility.CopyProxyToUdon(amb);
            sources.Add(a);
        }

        BreakerPanel(root.transform, sources.ToArray());
        ApplianceSwitches(root.transform);
        ImportSettings();
        EditorSceneManager.MarkSceneDirty(root.scene);
        Debug.Log($"[AudioSetup] {sources.Count} ambient sounds and the breaker panel set up");
    }

    static void BreakerPanel(Transform parent, AudioSource[] sources)
    {
        var n = new Vector3(0f, 0f, 1f);             // plan -Y (south, into the bedroom) in Unity
        float cx = (PanelX0 + PanelX1) / 2, cz = (PanelZ0 + PanelZ1) / 2;
        var panel = new GameObject("breaker_panel");
        panel.transform.SetParent(parent, false);
        panel.transform.SetPositionAndRotation(U(cx, PanelY, cz), Quaternion.LookRotation(n, Vector3.up));
        var dark = FilingCabinetSetup.PlainMat("breaker_handle", new Color(0.08f, 0.08f, 0.08f));
        var paper = FilingCabinetSetup.PlainMat("panel_card", new Color(0.95f, 0.94f, 0.9f));

        // The directory card taped to the inner door.
        var card = GameObject.CreatePrimitive(PrimitiveType.Cube);
        card.name = "directory_card";
        Object.DestroyImmediate(card.GetComponent<Collider>());
        card.transform.SetParent(panel.transform, false);
        card.transform.localScale = new Vector3(CardW * IN, CardH * IN, 0.0008f);
        card.transform.localPosition = new Vector3(0f, (CardZ - cz) * IN, 0.0005f);
        card.GetComponent<MeshRenderer>().sharedMaterial = paper;

        // The ambient sound breaker: a black handle in a dark slot, low on the door.
        var slot = GameObject.CreatePrimitive(PrimitiveType.Cube);
        slot.name = "sound_breaker";
        slot.transform.SetParent(panel.transform, false);
        slot.transform.localPosition = new Vector3(0f, (34.5f - cz) * IN, 0.002f);
        slot.transform.localScale = new Vector3(1.5f * IN, 2.6f * IN, 0.004f);
        slot.GetComponent<MeshRenderer>().sharedMaterial = dark;
        var handle = GameObject.CreatePrimitive(PrimitiveType.Cube);
        handle.name = "handle";
        Object.DestroyImmediate(handle.GetComponent<Collider>());
        handle.transform.SetParent(slot.transform, false);
        handle.transform.localPosition = new Vector3(0f, 0f, 2.5f);
        handle.transform.localScale = new Vector3(0.6f, 0.22f, 5f);
        handle.transform.localRotation = Quaternion.Euler(-25f, 0f, 0f);
        handle.GetComponent<MeshRenderer>().sharedMaterial = dark;
        var toggle = UdonSharpUndo.AddComponent<AudioToggle>(slot);
        toggle.sources = sources;
        toggle.toggle = handle.transform;
        toggle.InteractionText = "Ambient sound on/off";
        UdonSharpEditorUtility.CopyProxyToUdon(toggle);

        // The card's text and the GitHub link on a world-space canvas over it.
        var font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        var cgo = new GameObject("panel_ui", typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(GraphicRaycaster));
        cgo.transform.SetParent(panel.transform, false);
        var canvas = cgo.GetComponent<Canvas>();
        canvas.renderMode = RenderMode.WorldSpace;
        var ui = cgo.GetComponent<RectTransform>();
        ui.sizeDelta = new Vector2(280f, 420f);
        float px = CardW * IN / 280f;
        ui.localScale = new Vector3(px, px, px);
        ui.localPosition = new Vector3(0f, (CardZ - cz) * IN, 0.0012f);
        ui.localRotation = Quaternion.Euler(0f, 180f, 0f);       // UI faces its -Z; the panel faces +Z
        var shape = System.AppDomain.CurrentDomain.GetAssemblies()
            .Select(a => a.GetType("VRC.SDK3.Components.VRCUiShape")).FirstOrDefault(t => t != null);
        if (shape != null) cgo.AddComponent(shape);

        Label(cgo.transform, font, "UTILITIES", 30, FontStyle.Bold, new Vector2(0f, 160f), new Vector2(260f, 44f));
        LinkField(cgo.transform, font, new Vector2(0f, 60f), new Vector2(264f, 40f));
        // Credits for the lighting tech (LTCGI's MIT terms ask for a link; the full list is
        // CREDITS.md in the repository above).
        Label(cgo.transform, font, "Lighting: VRC Light Volumes by REDSIM", 12, FontStyle.Normal, new Vector2(0f, -30f), new Vector2(264f, 20f));
        Label(cgo.transform, font, "TV glow: LTCGI by _pi_", 12, FontStyle.Normal, new Vector2(0f, -52f), new Vector2(264f, 20f));
        Label(cgo.transform, font, "github.com/PiMaker/ltcgi", 12, FontStyle.Italic, new Vector2(0f, -72f), new Vector2(264f, 20f));
        Label(cgo.transform, font, "Ambient sound", 22, FontStyle.Bold, new Vector2(0f, -150f), new Vector2(260f, 34f));
        Label(cgo.transform, font, "(breaker below)", 14, FontStyle.Italic, new Vector2(0f, -178f), new Vector2(260f, 24f));
    }

    // Power switches for the appliances that hum: each turns its sound off for whoever flips it.
    static void ApplianceSwitches(Transform root)
    {
        var plate = FilingCabinetSetup.PlainMat("switch_plate", new Color(0.92f, 0.91f, 0.88f));
        var grey = FilingCabinetSetup.PlainMat("power_button", new Color(0.62f, 0.63f, 0.66f));   // stands out on the black cases
        GameObject Sound(string clip) => root.Find("sound_" + clip)?.gameObject;

        // Bathroom fan: the middle toggle of the bath's real 3-gang plate (wall_plates), else a
        // rocker of its own beside the bathroom light switch.
        var fanLever = NightSetup.FindLever("wall_plates_lever_bath_2");
        if (fanLever != null)
        {
            var fanHost = NightSetup.LeverHost("bath_fan_switch", root, fanLever);
            var e = fanLever.localEulerAngles;
            Wire(fanHost, fanLever, "Bathroom fan", Sound("bath_fan"), e, (fanLever.localRotation * Quaternion.Euler(40f, 0f, 0f)).eulerAngles);
        }
        else
        {
            var fan = NightSetup.WallSwitch("bath_fan_switch", root, U(252.5f, 202.6f, 48f), new Vector2(0, 1), plate);
            Wire(fan, fan.transform.Find("rocker"), "Bathroom fan", Sound("bath_fan"), new Vector3(-12f, 0f, 0f), new Vector3(12f, 0f, 0f));
        }

        // Portable AC: a button near the front of its top (body top z 34, centre plan (25, 125);
        // portable_ac object.py). Its renderer's bounds take in the hose, so they won't do.
        var acButton = Button("ac_power", root, U(29f, 125f, 34.05f), Vector3.up, 1.1f, grey);
        Wire(acButton, acButton.transform, "AC power", Sound("portable_ac"), Vector3.zero, Vector3.zero);

        // PC: a power button high on the tower's front (the side toward the room, plan +Y).
        var pc = Button("pc_power", root, U(151f, 26.1f, 45.5f), new Vector3(0f, 0f, -1f), 0.7f, grey);
        Wire(pc, pc.transform, "PC power", Sound("pc_fan"), Vector3.zero, Vector3.zero);
    }

    static GameObject Button(string name, Transform parent, Vector3 pos, Vector3 normal, float sizeIn, Material mat)
    {
        var go = GameObject.CreatePrimitive(PrimitiveType.Cylinder);
        go.name = name;
        go.transform.SetParent(parent, false);
        go.transform.SetPositionAndRotation(pos, Quaternion.FromToRotation(Vector3.up, normal));
        go.transform.localScale = new Vector3(sizeIn * IN, 0.003f, sizeIn * IN);
        go.GetComponent<MeshRenderer>().sharedMaterial = mat;
        Object.DestroyImmediate(go.GetComponent<Collider>());
        var box = go.AddComponent<BoxCollider>();                  // easier to point at than the thin disc
        box.size = new Vector3(1.6f, 6f, 1.6f);
        return go;
    }

    static void Wire(GameObject host, Transform toggle, string label, GameObject sound, Vector3 onEuler, Vector3 offEuler)
    {
        var sw = UdonSharpUndo.AddComponent<ApplianceSwitch>(host);
        sw.running = sound != null ? new[] { sound } : new GameObject[0];
        sw.toggle = toggle == host.transform ? null : toggle;
        sw.onEuler = onEuler;
        sw.offEuler = offEuler;
        sw.InteractionText = label;
        UdonSharpEditorUtility.CopyProxyToUdon(sw);
    }

    static Text Label(Transform parent, Font font, string text, int size, FontStyle style, Vector2 pos, Vector2 box)
    {
        var go = new GameObject("label", typeof(RectTransform), typeof(Text));
        go.transform.SetParent(parent, false);
        var rt = go.GetComponent<RectTransform>();
        rt.anchoredPosition = pos;
        rt.sizeDelta = box;
        var t = go.GetComponent<Text>();
        t.font = font;
        t.text = text;
        t.fontSize = size;
        t.fontStyle = style;
        t.alignment = TextAnchor.MiddleCenter;
        t.color = new Color(0.12f, 0.12f, 0.12f);
        return t;
    }

    static void LinkField(Transform parent, Font font, Vector2 pos, Vector2 box)
    {
        var go = new GameObject("github_link", typeof(RectTransform), typeof(Image), typeof(InputField));
        go.transform.SetParent(parent, false);
        var rt = go.GetComponent<RectTransform>();
        rt.anchoredPosition = pos;
        rt.sizeDelta = box;
        go.GetComponent<Image>().color = new Color(0.97f, 0.97f, 0.95f);
        var t = Label(go.transform, font, GitHubUrl, 11, FontStyle.Normal, Vector2.zero, box - new Vector2(10f, 4f));
        t.supportRichText = false;
        t.color = new Color(0.1f, 0.25f, 0.6f);
        var field = go.GetComponent<InputField>();
        field.textComponent = t;
        field.text = GitHubUrl;
        field.lineType = InputField.LineType.SingleLine;
    }

    // Small, mono, compressed: the loops are background hums.
    static void ImportSettings()
    {
        foreach (var g in AssetDatabase.FindAssets("t:AudioClip", new[] { "Assets/Apartment/Audio" }))
        {
            var path = AssetDatabase.GUIDToAssetPath(g);
            var imp = (AudioImporter)AssetImporter.GetAtPath(path);
            var s = imp.defaultSampleSettings;
            s.loadType = AudioClipLoadType.CompressedInMemory;
            s.compressionFormat = AudioCompressionFormat.Vorbis;
            s.quality = 0.45f;
            imp.defaultSampleSettings = s;
            imp.forceToMono = true;
            imp.loadInBackground = true;
            imp.SaveAndReimport();
        }
    }
}
