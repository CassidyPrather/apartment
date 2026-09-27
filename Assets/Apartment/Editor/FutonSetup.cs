// The futon's switch: one synced FutonToggle that swaps the futon package's two states
// (laid out flat, rolled in its sack by a wall), with a trigger collider fitted to each.
// The futon is toggled at runtime, so it isn't in the lightmap: the Light Volumes light it.
// Apartment > Setup Futon; Build Apartment Scene runs it.

using System.Linq;
using UdonSharpEditor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class FutonSetup
{
    [MenuItem("Apartment/Setup Futon")]
    public static void Setup()
    {
        if (NightSetup.EnsureProgram("FutonToggle"))
        {
            Debug.LogWarning("[FutonSetup] created the Udon program asset; run again once UdonSharp finishes compiling");
            return;
        }
        var flat = Object.FindObjectsOfType<MeshRenderer>(true).FirstOrDefault(r => r.name == "futon_flat");
        var rolled = Object.FindObjectsOfType<MeshRenderer>(true).FirstOrDefault(r => r.name == "futon_rolled");
        if (flat == null || rolled == null)
        {
            Debug.LogWarning("[FutonSetup] no futon in the scene (import the futon package first)");
            return;
        }
        foreach (var old in Object.FindObjectsOfType<Transform>(true).Where(t => t.name == "futon_toggle").ToArray())
            Object.DestroyImmediate(old.gameObject);

        foreach (var r in new[] { flat, rolled })
        {
            GameObjectUtility.SetStaticEditorFlags(r.gameObject, 0);
            r.receiveGI = ReceiveGI.LightProbes;
            r.gameObject.SetActive(true);                      // for the bounds below
        }
        var go = new GameObject("futon_toggle");
        go.transform.SetParent(flat.transform.parent, false);
        go.transform.SetPositionAndRotation(Vector3.zero, Quaternion.identity);
        go.transform.localScale = Vector3.one;
        var hit = go.AddComponent<BoxCollider>();
        hit.isTrigger = true;
        var t = UdonSharpUndo.AddComponent<FutonToggle>(go);
        t.flat = flat.gameObject;
        t.stored = rolled.gameObject;
        t.hit = hit;
        (t.flatCenter, t.flatSize) = Local(go.transform, flat.bounds);
        (t.storedCenter, t.storedSize) = Local(go.transform, rolled.bounds);
        t.laidOut = false;                                    // put away by default
        UdonSharpEditorUtility.CopyProxyToUdon(t);
        flat.gameObject.SetActive(false);
        hit.center = t.storedCenter;
        hit.size = t.storedSize;

        EditorSceneManager.MarkSceneDirty(go.scene);
        Debug.Log("[FutonSetup] futon toggle set up (rolled up by default)");
    }

    static (Vector3, Vector3) Local(Transform space, Bounds b)
    {
        var c = space.InverseTransformPoint(b.center);
        var s = space.InverseTransformVector(b.size);
        return (c, new Vector3(Mathf.Abs(s.x), Mathf.Abs(s.y), Mathf.Abs(s.z)));
    }
}
