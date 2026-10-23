// Cupboards and drawers that open, with their contents inside.
// - Cabinet doors: every <pkg>_door_<id> with a <pkg>_door_<id>_out marker in front of it
//   (origin on the hinge pin) gets a synced DoorSwing that turns it ~100 degrees toward the
//   marker; silent, with a trigger collider to click.
// - Drawers: every <pkg>_drawer_<id> with a <pkg>_drawer_<id>_grab marker at its pull gets a
//   SlidingDrawer grab handle on the marker (VRC Pickup, kinematic Rigidbody), sliding out
//   along the horizontal axis from the drawer's centre toward the pull.
// - Drawer contents: <drawer name>_contents objects (separate contents packages) move under
//   their drawer so they ride along.
// Moving parts are lit live (Light Volumes, probes) and left out of the bake entirely, so the
// cabinet interiors bake as if open instead of black.
// Apartment > Setup Cabinets; Build Apartment Scene runs it after the doors.

using System.Linq;
using UdonSharpEditor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using VRC.SDK3.Components;

public static class CabinetSetup
{
    const float SwingDegrees = 100f;
    const float TravelFraction = 0.75f;          // of the drawer's depth

    [MenuItem("Apartment/Setup Cabinets")]
    public static void Setup()
    {
        if (NightSetup.EnsureProgram("DoorSwing") | NightSetup.EnsureProgram("SlidingDrawer"))
        {
            Debug.LogWarning("[CabinetSetup] created the Udon program asset; run again once UdonSharp finishes compiling");
            return;
        }
        var root = Object.FindObjectsOfType<Transform>(true).FirstOrDefault(t => t.name == "apartment" && t.parent == null);
        if (root == null)
        {
            Debug.LogWarning("[CabinetSetup] no apartment root in the open scene");
            return;
        }
        var all = root.GetComponentsInChildren<Transform>(true);
        var byName = all.GroupBy(t => t.name).ToDictionary(g => g.Key, g => g.First());

        // contents first: reparenting needs the prefab instances unpacked
        int contents = 0;
        foreach (var c in all.Where(t => t.name.EndsWith("_contents") && t.name.Contains("_drawer_")).ToArray())
        {
            var drawerName = c.name.Substring(0, c.name.Length - "_contents".Length);
            if (!byName.TryGetValue(drawerName, out var drawer) || drawer.GetComponent<Renderer>() == null)
            {
                Debug.LogWarning($"[CabinetSetup] {c.name}: no drawer {drawerName}");
                continue;
            }
            Unpack(c);
            Unpack(drawer);
            c.SetParent(drawer, true);
            MakeMoving(c);
            contents++;
        }
        // what stays behind in a contents package (cupboard shelves, closets) is static clutter,
        // even when the package's manifest is non-static for the sake of its drawer contents
        foreach (var pkg in all.Where(t => t.parent == root && t.name.EndsWith("_contents")))
            foreach (var r in pkg.GetComponentsInChildren<MeshRenderer>(true))
                GameObjectUtility.SetStaticEditorFlags(r.gameObject,
                    StaticEditorFlags.ContributeGI | StaticEditorFlags.BatchingStatic | StaticEditorFlags.OccluderStatic |
                    StaticEditorFlags.OccludeeStatic | StaticEditorFlags.ReflectionProbeStatic);

        int doors = 0;
        foreach (var leaf in all.Where(t => t.name.Contains("_door_") && !t.name.EndsWith("_out")).ToArray())
        {
            var outMark = leaf.parent != null ? leaf.parent.Find(leaf.name + "_out") : null;
            if (outMark == null) continue;
            var r = leaf.GetComponent<Renderer>();
            if (r == null) continue;
            var start = leaf.localRotation;
            var c0 = r.bounds.center;
            var toward = outMark.position - c0;
            Quaternion open = start;
            float best = float.MinValue;
            foreach (var turn in new[] { SwingDegrees, -SwingDegrees })
            {
                leaf.localRotation = start * Quaternion.Euler(0f, turn, 0f);
                float d = Vector3.Dot(r.bounds.center - c0, toward);
                if (d > best) { best = d; open = leaf.localRotation; }
            }
            leaf.localRotation = start;
            MakeMoving(leaf);
            var box = leaf.gameObject.AddComponent<BoxCollider>();
            box.isTrigger = true;
            var mf = leaf.GetComponent<MeshFilter>();
            if (mf != null && mf.sharedMesh != null) { box.center = mf.sharedMesh.bounds.center; box.size = mf.sharedMesh.bounds.size; }
            var s = UdonSharpUndo.AddComponent<DoorSwing>(leaf.gameObject);
            s.closedRotation = start;
            s.openRotation = open;
            s.isOpen = false;
            s.seconds = 0.6f;
            s.InteractionText = "Open";
            UdonSharpEditorUtility.CopyProxyToUdon(s);
            doors++;
        }

        int drawers = 0;
        foreach (var drawer in all.Where(t => t.name.Contains("_drawer_") && !t.name.EndsWith("_grab") && !t.name.EndsWith("_contents")).ToArray())
        {
            var grab = drawer.parent != null ? drawer.parent.Find(drawer.name + "_grab") : null;
            if (grab == null) continue;
            var r = drawer.GetComponent<Renderer>();
            if (r == null) continue;
            var parent = drawer.parent;
            // opening direction: drawer centre -> pull, flattened and snapped to the parent's
            // major horizontal axis
            var axis = parent.InverseTransformDirection(grab.position - r.bounds.center);
            axis.y = 0f;
            axis = Mathf.Abs(axis.z) > Mathf.Abs(axis.x) ? new Vector3(0, 0, Mathf.Sign(axis.z)) : new Vector3(Mathf.Sign(axis.x), 0, 0);
            var worldAxis = parent.TransformDirection(axis).normalized;
            var size = r.bounds.size;
            float depth = Mathf.Abs(size.x * worldAxis.x) + Mathf.Abs(size.y * worldAxis.y) + Mathf.Abs(size.z * worldAxis.z);
            MakeMoving(drawer);
            foreach (var c in grab.GetComponents<Component>().Where(c => c is Collider || c is Rigidbody || c is VRCPickup
                         || c is VRC.Udon.UdonBehaviour || c is UdonSharp.UdonSharpBehaviour).ToArray())
                Object.DestroyImmediate(c);
            var rb = grab.gameObject.AddComponent<Rigidbody>();
            rb.isKinematic = true;
            rb.useGravity = false;
            var gcol = grab.gameObject.AddComponent<BoxCollider>();
            gcol.size = grab.InverseTransformVector(Vector3.one * 0.07f);
            gcol.size = new Vector3(Mathf.Abs(gcol.size.x), Mathf.Abs(gcol.size.y), Mathf.Abs(gcol.size.z));
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
            sd.maxTravel = TravelFraction * depth / Mathf.Max(1e-4f, parent.lossyScale.x);
            sd.snapClosed = 0.01f;
            UdonSharpEditorUtility.CopyProxyToUdon(sd);
            drawers++;
        }
        EditorSceneManager.MarkSceneDirty(UnityEngine.SceneManagement.SceneManager.GetActiveScene());
        Debug.Log($"[CabinetSetup] {doors} cabinet doors, {drawers} drawers, {contents} drawer contents set up");
    }

    // Moving: out of the bake and static batching, lit by Light Volumes/probes, no solid colliders.
    static void MakeMoving(Transform t)
    {
        foreach (var x in t.GetComponentsInChildren<Transform>(true))
        {
            GameObjectUtility.SetStaticEditorFlags(x.gameObject, 0);
            var r = x.GetComponent<MeshRenderer>();
            if (r != null) r.receiveGI = ReceiveGI.LightProbes;
            foreach (var c in x.GetComponents<Collider>().ToArray())
                Object.DestroyImmediate(c);
        }
    }

    static void Unpack(Transform t)
    {
        var inst = PrefabUtility.GetOutermostPrefabInstanceRoot(t.gameObject);
        if (inst != null)
            PrefabUtility.UnpackPrefabInstance(inst, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
    }
}
