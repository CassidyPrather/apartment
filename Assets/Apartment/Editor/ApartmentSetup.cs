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
        var shellInst = (GameObject)PrefabUtility.InstantiatePrefab(
            AssetDatabase.LoadAssetAtPath<GameObject>(Root + "/Prefabs/apartment_shell.prefab"));
        var spot = shellInst.transform.Find("place_filing_cabinet_set");
        var set = (GameObject)PrefabUtility.InstantiatePrefab(
            AssetDatabase.LoadAssetAtPath<GameObject>(Root + "/Prefabs/filing_cabinet_set.prefab"));
        set.transform.SetPositionAndRotation(spot.position, spot.rotation);

        var world = AssetDatabase.FindAssets("VRCWorld t:Prefab");
        if (world.Length > 0)
        {
            var vw = (GameObject)PrefabUtility.InstantiatePrefab(
                AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(world[0])));
            // Living room, just inside the entry, facing into the room.
            vw.transform.SetPositionAndRotation(new Vector3(-1.2f, 0f, -3.9f), Quaternion.Euler(0, 200f, 0));
        }
        var sun = new GameObject("temp_light").AddComponent<Light>();
        sun.type = LightType.Directional;
        sun.intensity = 0.8f;
        sun.transform.rotation = Quaternion.Euler(55, 30, 0);
        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
        RenderSettings.ambientLight = new Color(0.55f, 0.55f, 0.57f);
        EditorSceneManager.SaveScene(scene, Root + "/Scenes/apartment.unity");
        AssetDatabase.SaveAssets();
        Debug.Log("[ApartmentSetup] done");
    }
}
