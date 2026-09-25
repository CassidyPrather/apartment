// Builds the apartment scene from the Blender shell export: shell materials (Mochie,
// tiling), import settings, colliders, and the furniture sets dropped on the shell's
// place_* markers. Rerun after any shell re-export: Apartment > Build Apartment Scene.
//
// Lighting is not set up here yet: the scene has a temporary sun until the lighting
// milestone (baked lightmaps, Light Volumes, reflection probes).

using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class ApartmentSetup
{
    const string Root = "Assets/Apartment";
    // The whole apartment is built 1.2x real size so avatars fit through the doorways.
    // Lighting, video and the view captures scale their inch coordinates by the same factor.
    public const float WorldScale = 1.2f;

    [MenuItem("Apartment/Build Apartment Scene")]
    public static void Build()
    {
        FilingCabinetSetup.ConfigureTextures();
        var mats = new Dictionary<string, Material>
        {
            // Keys are the Blender material names in apartment_shell.fbx.
            ["shell_wall"] = FilingCabinetSetup.Mat("shell_wall", "shell_wall", Color.white),
            ["shell_ceiling"] = FilingCabinetSetup.Mat("shell_ceiling", "shell_ceiling", Color.white),
            ["shell_trim"] = FilingCabinetSetup.Mat("shell_trim", "shell_trim", Color.white),
            ["shell_carpet"] = FilingCabinetSetup.Mat("shell_carpet", "shell_carpet", Color.white),
            ["shell_vinyl"] = FilingCabinetSetup.Mat("shell_vinyl", "shell_vinyl", Color.white),
            // Placeholder until the made-up exterior exists.
            ["shell_glass"] = FilingCabinetSetup.PlainMat("shell_glass", new Color(0.62f, 0.72f, 0.82f)),
        };
        FilingCabinetSetup.ConfigureModels(mats, new[] { "apartment_shell" });

        var shell = (GameObject)PrefabUtility.InstantiatePrefab(
            AssetDatabase.LoadAssetAtPath<GameObject>(Root + "/Models/apartment_shell.fbx"));
        try
        {
            foreach (var r in shell.GetComponentsInChildren<MeshRenderer>())
            {
                GameObjectUtility.SetStaticEditorFlags(r.gameObject,
                    StaticEditorFlags.ContributeGI | StaticEditorFlags.BatchingStatic | StaticEditorFlags.OccluderStatic |
                    StaticEditorFlags.OccludeeStatic | StaticEditorFlags.ReflectionProbeStatic);
                if (!r.name.Contains("glass") && !r.name.Contains("trim"))
                    r.gameObject.AddComponent<MeshCollider>();          // walls, floors, ceiling
            }
            PrefabUtility.SaveAsPrefabAsset(shell, Root + "/Prefabs/apartment_shell.prefab");
        }
        finally
        {
            Object.DestroyImmediate(shell);
        }

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        var root = new GameObject("apartment").transform;
        root.localScale = Vector3.one * WorldScale;
        var shellInst = (GameObject)PrefabUtility.InstantiatePrefab(
            AssetDatabase.LoadAssetAtPath<GameObject>(Root + "/Prefabs/apartment_shell.prefab"));
        shellInst.transform.SetParent(root, false);
        var spot = shellInst.transform.Find("place_filing_cabinet_set");
        var set = (GameObject)PrefabUtility.InstantiatePrefab(
            AssetDatabase.LoadAssetAtPath<GameObject>(Root + "/Prefabs/filing_cabinet_set.prefab"));
        PlaceOn(set.transform, spot, root);

        // Every other object package with a marker in the shell goes on its marker.
        foreach (Transform t in shellInst.transform)
        {
            if (!t.name.StartsWith("place_") || t.name == "place_filing_cabinet_set")
                continue;
            var name = t.name.Substring(6);
            int copy = name.IndexOf("__");                            // place_<name>__<n>: another copy
            if (copy > 0)
                name = name.Substring(0, copy);
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{Root}/Prefabs/{name}.prefab");
            if (prefab == null)
                continue;
            var inst = (GameObject)PrefabUtility.InstantiatePrefab(prefab);
            PlaceOn(inst.transform, t, root);
            if (t.name == "place_door_laundry__bath")
                OpenLeaf(inst.transform, -90f);                         // the bathroom door stands open
        }

        var world = AssetDatabase.FindAssets("VRCWorld t:Prefab");
        if (world.Length > 0)
        {
            var vw = (GameObject)PrefabUtility.InstantiatePrefab(
                AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(world[0])));
            // Living room, just inside the entry, facing into the room.
            vw.transform.SetPositionAndRotation(new Vector3(-1.2f, 0f, -3.9f) * WorldScale, Quaternion.Euler(0, 200f, 0));
        }
        VideoSetup.Setup();
        MirrorSetup.Setup();
        EditorSceneManager.SaveScene(scene, Root + "/Scenes/apartment.unity");
        AtlasSetup.Run();                                          // draw calls: shared atlases
        NightSetup.Setup();                                        // after the atlas step (it reads material slots)
        AudioSetup.Setup();
        EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene());
        LightingSetup.Setup();
        AssetDatabase.SaveAssets();
        Debug.Log("[ApartmentSetup] done");
    }

    // Parent under the scaled root at the marker's pose, so the item scales with the shell.
    static void PlaceOn(Transform item, Transform marker, Transform root)
    {
        item.SetParent(root, false);
        item.localPosition = root.InverseTransformPoint(marker.position);
        item.localRotation = Quaternion.Inverse(root.rotation) * marker.rotation;
    }

    // Hinged leaves have their origin on the hinge pin and swing about their local up axis.
    static void OpenLeaf(Transform door, float degrees)
    {
        foreach (var t in door.GetComponentsInChildren<Transform>())
            if (t.name.EndsWith("_leaf"))
                t.localRotation = t.localRotation * Quaternion.Euler(0f, degrees, 0f);
    }
}
