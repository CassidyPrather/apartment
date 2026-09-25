// Imports every object package built by blender/lib/build_object.py: reads
// blender/lib/objects/<name>/manifest.json, makes the Mochie materials (opaque, or
// translucent via Transparent mode), configures the FBX with material remaps, and saves
// Assets/Apartment/Prefabs/<name>.prefab with static flags and colliders.
// Apartment > Build Apartment Scene then drops each prefab on the shell marker
// place_<name> when one exists.

using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

public static class ObjectImporter
{
    [System.Serializable]
    class MaterialSpec { public string atlas; public string mode = "opaque"; public float alpha = 1f; public bool tiled; }

    // JsonUtility can't read dictionaries, so the materials object is parsed by hand below.
    [System.Serializable]
    class Manifest { public string name; public string fbx; public string collider = "box"; public bool @static = true; }

    // Only these keep colliders; everything else is walk-through so the small rooms are easy
    // to move around in (the walls, floors and drawer handles keep theirs elsewhere).
    static readonly HashSet<string> Solid = new HashSet<string> { "kitchen_cabinets", "fridge", "range" };

    static string ObjectsDir => Path.GetFullPath(Path.Combine(Application.dataPath, "..", "blender", "lib", "objects"));

    // Only packages whose FBX, manifest or textures changed since their prefab was saved.
    [MenuItem("Apartment/Import Objects")]
    public static void ImportChanged() => ImportAll(false);

    [MenuItem("Apartment/Import Objects (All)")]
    public static void ImportEverything() => ImportAll(true);

    static void ImportAll(bool all)
    {
        if (!Directory.Exists(ObjectsDir))
            return;
        FilingCabinetSetup.ConfigureTextures();
        int n = 0;
        foreach (var dir in Directory.GetDirectories(ObjectsDir))
        {
            var path = Path.Combine(dir, "manifest.json");
            if (!File.Exists(path))
                continue;
            var json = File.ReadAllText(path);
            if (!all && UpToDate(json, path))
                continue;
            try
            {
                Import(json);
                n++;
            }
            catch (System.Exception e)                                   // a package mid-build
            {
                Debug.LogWarning($"[ObjectImporter] skipped {Path.GetFileName(dir)}: {e.Message}");
            }
        }
        AssetDatabase.SaveAssets();
        Debug.Log($"[ObjectImporter] done ({n} imported)");
    }

    static bool UpToDate(string json, string manifestPath)
    {
        var man = JsonUtility.FromJson<Manifest>(json);
        var prefab = Path.Combine(Application.dataPath, "..", $"Assets/Apartment/Prefabs/{man.name}.prefab");
        if (!File.Exists(prefab))
            return false;
        var saved = File.GetLastWriteTimeUtc(prefab);
        var inputs = new List<string> { manifestPath, Path.Combine(Application.dataPath, "..", man.fbx) };
        foreach (var spec in ParseMaterials(json).Values)
            inputs.AddRange(Directory.GetFiles(Path.Combine(Application.dataPath, "Apartment", "Textures"), spec.atlas + "_*.png"));
        foreach (var f in inputs)
            if (File.Exists(f) && File.GetLastWriteTimeUtc(f) > saved)
                return false;
        return true;
    }

    static void Import(string json)
    {
        var man = JsonUtility.FromJson<Manifest>(json);
        var mats = new Dictionary<string, Material>();
        foreach (var kv in ParseMaterials(json))
        {
            var spec = kv.Value;
            if (spec.tiled)
                SetRepeat(spec.atlas);
            if (spec.mode == "transparent")
                mats[kv.Key] = FilingCabinetSetup.ShellMat(kv.Key, spec.atlas, spec.alpha);
            else if (spec.mode == "cutout")
                mats[kv.Key] = CutoutMat(kv.Key, spec.atlas, spec.alpha);
            else
                mats[kv.Key] = FilingCabinetSetup.Mat(kv.Key, spec.atlas, Color.white);
        }
        FilingCabinetSetup.ConfigureModels(mats, new[] { man.name });

        var go = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>(man.fbx));
        try
        {
            foreach (var r in go.GetComponentsInChildren<MeshRenderer>())
            {
                if (man.@static || man.name.StartsWith("door_"))           // doors stay put now
                    GameObjectUtility.SetStaticEditorFlags(r.gameObject,
                        StaticEditorFlags.ContributeGI | StaticEditorFlags.BatchingStatic |
                        StaticEditorFlags.OccluderStatic | StaticEditorFlags.OccludeeStatic |
                        StaticEditorFlags.ReflectionProbeStatic);
                if (!Solid.Contains(man.name))                       // walk-through, so moving around is easy
                    continue;
                if (man.collider == "box")
                    FilingCabinetSetup.FitCollider(r.gameObject, r);
                else if (man.collider == "mesh")
                    r.gameObject.AddComponent<MeshCollider>();
            }
            PrefabUtility.SaveAsPrefabAsset(go, $"Assets/Apartment/Prefabs/{man.name}.prefab");
        }
        finally
        {
            Object.DestroyImmediate(go);
        }
    }

    // Alpha-tested foliage and the like: Mochie's Cutout mode, alpha = the cutoff.
    // No blending, so overlapping cards never sort wrong.
    static Material CutoutMat(string name, string atlas, float cutoff)
    {
        var mat = FilingCabinetSetup.Mat(name, atlas, Color.white);
        mat.SetFloat("_Cutoff", cutoff);
        mat.SetInt("_BlendMode", 1);
        Mochie.StandardEditor.SetBlendMode(mat);
        EditorUtility.SetDirty(mat);
        return mat;
    }

    static void SetRepeat(string atlas)
    {
        foreach (var suffix in new[] { "_albedo", "_mask", "_emission" })
        {
            var imp = AssetImporter.GetAtPath($"Assets/Apartment/Textures/{atlas}{suffix}.png") as TextureImporter;
            if (imp != null && imp.wrapMode != TextureWrapMode.Repeat)
            {
                imp.wrapMode = TextureWrapMode.Repeat;
                imp.SaveAndReimport();
            }
        }
    }

    // "materials": { "<name>": { ...MaterialSpec... }, ... }
    static Dictionary<string, MaterialSpec> ParseMaterials(string json)
    {
        var result = new Dictionary<string, MaterialSpec>();
        int i = json.IndexOf("\"materials\"");
        if (i < 0)
            return result;
        i = json.IndexOf('{', i);
        int depth = 0, start = i;
        for (int j = i; j < json.Length; j++)
        {
            if (json[j] == '{') depth++;
            else if (json[j] == '}' && --depth == 0) { json = json.Substring(start + 1, j - start - 1); break; }
        }
        int k = 0;
        while ((k = json.IndexOf('"', k)) >= 0)
        {
            int end = json.IndexOf('"', k + 1);
            string key = json.Substring(k + 1, end - k - 1);
            int o = json.IndexOf('{', end), c = json.IndexOf('}', o);
            result[key] = JsonUtility.FromJson<MaterialSpec>(json.Substring(o, c - o + 1));
            k = c + 1;
        }
        return result;
    }
}
