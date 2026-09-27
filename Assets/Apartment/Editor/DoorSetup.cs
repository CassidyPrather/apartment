// Swinging doors: every hinged door leaf gets a synced DoorSwing (click to open or shut,
// with a creak and a latch), a trigger collider to click, and a spatial AudioSource.
// Leaves stay in the bake as light blockers in their default position (so closets stay
// dark), but are lit by the Light Volumes and probes, so they look right at any angle.
// Apartment > Setup Doors; Build Apartment Scene runs it.

using System.Linq;
using UdonSharpEditor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class DoorSetup
{
    const float IN = 0.0254f * ApartmentSetup.WorldScale;

    // Hinged doors: package instance name, a plan point near it (to tell copies apart), and
    // the side its leaf swings into (plan direction, the room it opens into).
    static readonly (string package, Vector2 near, Vector2 swing, string label)[] Doors =
    {
        ("door_bedroom", new Vector2(136.4f, 153.5f), new Vector2(1, 0), "bedroom"),        // into the bedroom
        ("door_laundry", new Vector2(208.8f, 196.5f), new Vector2(1, 0), "laundry"),        // into the hall
        ("door_laundry", new Vector2(214.0f, 200.1f), new Vector2(0, 1), "bathroom"),       // into the bath
        ("door_laundry", new Vector2(136.4f, 194.0f), new Vector2(1, 0), "dining closet"),  // into the closet
        ("door_entry", new Vector2(-3.0f, 180.5f), new Vector2(1, 0), "front"),             // into the apartment
        ("door_entry", new Vector2(212.5f, -3.0f), new Vector2(0, 1), "patio"),             // into the bedroom
    };

    [MenuItem("Apartment/Setup Doors")]
    public static void Setup()
    {
        if (NightSetup.EnsureProgram("DoorSwing"))
        {
            Debug.LogWarning("[DoorSetup] created the Udon program asset; run again once UdonSharp finishes compiling");
            return;
        }
        var opens = Clips("doorOpen");
        var closes = Clips("doorClose");
        var packages = Object.FindObjectsOfType<Transform>(true)
            .Where(t => t.parent != null && t.parent.name == "apartment").ToArray();
        int n = 0;
        foreach (var d in Doors)
        {
            var near = Plan(d.near.x, d.near.y);
            var door = packages.Where(t => t.name == d.package)
                .OrderBy(t => (new Vector2(t.position.x, t.position.z) - near).sqrMagnitude).FirstOrDefault();
            var leaf = door == null ? null : door.GetComponentsInChildren<Transform>(true).FirstOrDefault(t => t.name.EndsWith("_leaf"));
            if (leaf == null || (new Vector2(door.position.x, door.position.z) - near).magnitude > 12f * IN)
            {
                Debug.LogWarning($"[DoorSetup] no {d.package} leaf near plan {d.near}");
                continue;
            }
            foreach (var c in leaf.GetComponents<Component>().Where(c => c is AudioSource || c is Collider || c is DoorSwing || c is VRC.Udon.UdonBehaviour).ToArray())
                Object.DestroyImmediate(c);

            // closed = the turn that lays the leaf in the opening; open = 90 degrees from it,
            // toward the room it swings into
            // the frame: every renderer of the door but the leaf (Unity's missing components
            // aren't C# null, so no ?? here)
            var frameParts = door.GetComponentsInChildren<Renderer>(true)
                .Where(fr => !fr.transform.IsChildOf(leaf) && !fr.name.EndsWith("_grab")).ToArray();
            if (frameParts.Length == 0)
            {
                Debug.LogWarning($"[DoorSetup] {d.package} near plan {d.near} has no frame");
                continue;
            }
            var opening = frameParts.Select(fr => fr.bounds).Aggregate((x, y) => { x.Encapsulate(y); return x; }).center;
            var swing = new Vector3(-d.swing.x, 0f, -d.swing.y);                // plan -> Unity
            var start = leaf.localRotation;
            Quaternion closed = start, open = start;
            float best = float.MaxValue;
            foreach (var turn in new[] { 0f, 90f, -90f, 180f })
            {
                leaf.localRotation = start * Quaternion.Euler(0f, turn, 0f);
                float off = (LeafCentre(leaf) - opening).magnitude;
                if (off < best) { best = off; closed = leaf.localRotation; }
            }
            foreach (var turn in new[] { 90f, -90f })
            {
                leaf.localRotation = closed * Quaternion.Euler(0f, turn, 0f);
                if (Vector3.Dot(LeafCentre(leaf) - opening, swing) > 0f) open = leaf.localRotation;
            }
            bool startsOpen = Quaternion.Angle(start, closed) > 45f;
            leaf.localRotation = start;

            // lit live (it moves) but still blocks light in the bake where it stands by default
            var r = leaf.GetComponent<MeshRenderer>();
            if (r != null)
            {
                GameObjectUtility.SetStaticEditorFlags(leaf.gameObject, StaticEditorFlags.ContributeGI);
                r.receiveGI = ReceiveGI.LightProbes;
            }
            var box = leaf.gameObject.AddComponent<BoxCollider>();
            box.isTrigger = true;
            var mf = leaf.GetComponent<MeshFilter>();
            if (mf != null && mf.sharedMesh != null) { box.center = mf.sharedMesh.bounds.center; box.size = mf.sharedMesh.bounds.size; }

            var a = leaf.gameObject.AddComponent<AudioSource>();
            a.playOnAwake = false;
            a.spatialBlend = 1f;
            a.volume = 0.6f;
            a.rolloffMode = AudioRolloffMode.Logarithmic;
            a.minDistance = 1f;
            a.maxDistance = 12f;
            a.dopplerLevel = 0f;

            var s = UdonSharpUndo.AddComponent<DoorSwing>(leaf.gameObject);
            s.closedRotation = closed;
            s.openRotation = open;
            s.isOpen = startsOpen;
            s.sound = a;
            s.openClips = opens;
            s.closeClips = closes;
            s.InteractionText = startsOpen ? "Close" : "Open";
            UdonSharpEditorUtility.CopyProxyToUdon(s);
            n++;
        }
        EditorSceneManager.MarkSceneDirty(UnityEngine.SceneManagement.SceneManager.GetActiveScene());
        Debug.Log($"[DoorSetup] {n} swinging doors set up");
    }

    static Vector2 Plan(float x, float y) => new Vector2(-x * IN, -y * IN);

    static Vector3 LeafCentre(Transform leaf)
    {
        var r = leaf.GetComponent<Renderer>();
        return r != null ? r.bounds.center : leaf.position;
    }

    static AudioClip[] Clips(string prefix) => AssetDatabase.FindAssets(prefix + " t:AudioClip", new[] { "Assets/Apartment/Audio/Doors" })
        .Select(g => AssetDatabase.LoadAssetAtPath<AudioClip>(AssetDatabase.GUIDToAssetPath(g))).ToArray();
}
