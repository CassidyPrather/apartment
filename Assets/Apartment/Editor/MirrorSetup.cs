// The bathroom vanity mirror: a glossy mirror material (reflecting the baked reflection
// probe) so it reads as a mirror at all times, plus a real VRChat mirror over it that is
// off by default and toggled locally by a small button beside it.
// Apartment > Setup Mirror; Build Apartment Scene runs it.

using System.Linq;
using UdonSharp;
using UdonSharpEditor;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class MirrorSetup
{
    const string VrcMirror = "Packages/com.vrchat.worlds/Samples/UdonExampleScene/Prefabs/VRCMirror.prefab";
    const string ToggleProgram = "Assets/Apartment/Scripts/LocalToggle.asset";

    [MenuItem("Apartment/Setup Mirror")]
    public static void Setup()
    {
        var glass = Object.FindObjectsOfType<MeshRenderer>(true).FirstOrDefault(r => r.name == "vanity_mirror");
        if (glass == null)
        {
            Debug.LogWarning("[MirrorSetup] no vanity_mirror in the scene");
            return;
        }
        foreach (var old in Object.FindObjectsOfType<Transform>(true).Where(t => t.name == "bath_mirror_toggle").ToArray())
            Object.DestroyImmediate(old.gameObject);

        // Always-on look: a smooth metallic surface reflects the room's reflection probe.
        var mat = FilingCabinetSetup.Mat("vanity_mirror_glass", "bathroom", new Color(0.82f, 0.85f, 0.86f));
        mat.SetTexture("_MainTex", null);
        mat.SetTexture("_PackedMap", null);
        mat.SetInt("_PrimaryWorkflow", 0);
        mat.SetFloat("_Metallic", 1f);
        mat.SetFloat("_Glossiness", 0.97f);
        FilingCabinetSetup.MochieKeywords(mat);
        var mats = glass.sharedMaterials;
        for (int i = 0; i < mats.Length; i++) mats[i] = mat;
        glass.sharedMaterials = mats;
        EditorUtility.SetDirty(mat);

        // The real mirror: the SDK's VRCMirror quad fitted over the glass, facing the room.
        var b = glass.bounds;
        var normal = Vector3.left;                     // the mirror hangs on the bath's west wall (plan +x = Unity -x)
        var root = new GameObject("bath_mirror_toggle");
        root.transform.SetParent(glass.transform.root, true);
        var mirror = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(VrcMirror), root.transform);
        mirror.name = "bath_vrc_mirror";
        // Just in front of the glass; the quad is visible from its local -Z side.
        mirror.transform.position = b.center + normal * (b.extents.x + 0.003f);
        mirror.transform.rotation = Quaternion.LookRotation(-normal, Vector3.up);
        var q = mirror.GetComponent<MeshFilter>().sharedMesh.bounds.size;
        mirror.transform.localScale = new Vector3(b.size.z / Mathf.Max(q.x, 1e-4f), b.size.y / Mathf.Max(q.y, 1e-4f), 1f);
        mirror.SetActive(false);                       // off until someone turns it on (local)

        // Toggle button on the wall beside the mirror.
        var button = GameObject.CreatePrimitive(PrimitiveType.Cube);
        button.name = "mirror_button";
        button.transform.SetParent(root.transform, true);
        button.transform.position = new Vector3(b.center.x - 0.012f, b.min.y + 0.12f, b.max.z + 0.07f);
        button.transform.localScale = new Vector3(0.02f, 0.07f, 0.045f);
        button.GetComponent<MeshRenderer>().sharedMaterial = FilingCabinetSetup.PlainMat("mirror_button", new Color(0.9f, 0.89f, 0.86f));
        if (AssetDatabase.LoadAssetAtPath<UdonSharpProgramAsset>(ToggleProgram) == null)
        {
            var asset = ScriptableObject.CreateInstance<UdonSharpProgramAsset>();
            asset.sourceCsScript = AssetDatabase.LoadAssetAtPath<MonoScript>("Assets/Apartment/Scripts/LocalToggle.cs");
            AssetDatabase.CreateAsset(asset, ToggleProgram);
            AssetDatabase.SaveAssets();
            UdonSharpProgramAsset.CompileAllCsPrograms(true);
        }
        var toggle = UdonSharpUndo.AddComponent<LocalToggle>(button);
        toggle.targets = new[] { mirror };
        toggle.InteractionText = "Mirror";
        UdonSharpEditorUtility.CopyProxyToUdon(toggle);

        EditorSceneManager.MarkSceneDirty(root.scene);
        Debug.Log("[MirrorSetup] bathroom mirror set up (VRC mirror off by default, local toggle)");
    }
}
