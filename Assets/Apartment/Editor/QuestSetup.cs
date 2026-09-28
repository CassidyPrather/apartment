// The mobile (Quest and iOS) scene: a copy of the PC scene with the lamps baked in and no
// night mode (no switchable Point Light Volumes, no day/night switch), baked on its own.
// Apartment > Build Quest Scene copies the current PC scene, strips night mode and starts
// its bake; it bakes on any build target (switch to Android or iOS only to upload).

using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class QuestSetup
{
    public const string PcScene = "Assets/Apartment/Scenes/apartment.unity";
    public const string QuestScene = "Assets/Apartment/Scenes/apartment_quest.unity";

    // The mobile scene, or any scene opened while building for a mobile platform.
    public static bool IsMobileScene()
    {
        var target = EditorUserBuildSettings.activeBuildTarget;
        return EditorSceneManager.GetActiveScene().path == QuestScene
            || target == BuildTarget.Android || target == BuildTarget.iOS;
    }

    [MenuItem("Apartment/Build Quest Scene")]
    public static void Build()
    {
        EditorSceneManager.SaveOpenScenes();
        if (EditorSceneManager.GetActiveScene().path != PcScene)
            EditorSceneManager.OpenScene(PcScene);
        EditorSceneManager.SaveScene(EditorSceneManager.GetActiveScene(), QuestScene, true);   // save a copy
        var scene = EditorSceneManager.OpenScene(QuestScene);

        foreach (var t in Object.FindObjectsOfType<Transform>(true).Where(t => t.name == "lights_and_night").ToArray())
            Object.DestroyImmediate(t.gameObject);
        LightingSetup.Setup();                       // the room lamps baked in (IsMobileScene)
        EditorSceneManager.SaveScene(scene);
        Debug.Log("[QuestSetup] Quest scene rebuilt from the PC scene; baking");
        LightingSetup.Bake();
    }
}
