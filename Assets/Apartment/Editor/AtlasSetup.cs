// Draw-call pass: merges the per-object materials into a few shared texture atlases.
// Static batching only merges renderers that share a material, so ~70 small materials
// meant ~70 batches. This packs every opaque, non-tiling material's albedo / packed mask
// / emission into 4096 atlases (grouped by shader setup), remaps the meshes' UV0 onto
// them, and merges each renderer's submeshes that end up on the same material.
//
// Left alone: tiling surfaces (walls, floors), transparent and cutout materials, the
// video screens, and the photo-derived art atlases (gitignored; they must never be copied
// into a committed atlas). UV2 (lightmaps) is untouched.
//
// Apartment > Atlas Materials; Build Apartment Scene runs it before the lighting setup.
// Outputs (generated, committed through LFS) go to Assets/Apartment/Atlased/.

using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

public static class AtlasSetup
{
    const string Out = "Assets/Apartment/Atlased";
    const int AtlasSize = 4096;
    const int Pad = 8;

    // Photo-derived art (gitignored textures) and textures a script swaps at runtime.
    static readonly HashSet<string> Excluded = new HashSet<string>
    {
        "own_art", "living_wall_art", "bedroom_fixtures", "desk_computer",
        "media_hutch_art", "cassette_player_art",
        "VideoScreen", "wall_tv_screen",
    };

    class Entry { public Texture albedo, mask, emission; public Rect rect; public int area; }

    [MenuItem("Apartment/Atlas Materials")]
    public static void Run()
    {
        // Start clean: the scene was just rebuilt from the source prefabs.
        if (AssetDatabase.IsValidFolder(Out))
            AssetDatabase.DeleteAsset(Out);
        Directory.CreateDirectory(Out);
        Directory.CreateDirectory(Out + "/Meshes");
        AssetDatabase.Refresh();
        var renderers = Object.FindObjectsOfType<MeshRenderer>()
            .Where(r => r.GetComponent<MeshFilter>() != null && r.GetComponent<MeshFilter>().sharedMesh != null).ToList();

        // 1. Which materials can be atlased, grouped by everything that must match to share one.
        var groups = new Dictionary<string, List<Material>>();
        foreach (var m in renderers.SelectMany(r => r.sharedMaterials).Where(m => m != null).Distinct())
        {
            if (!Atlasable(m))
                continue;
            var key = GroupKey(m);
            if (!groups.TryGetValue(key, out var list))
                groups[key] = list = new List<Material>();
            list.Add(m);
        }

        // 2. Pack each group (splitting into several atlases when one would overflow).
        var remap = new Dictionary<Material, (Material mat, Rect rect)>();
        int atlasIndex = 0;
        foreach (var kv in groups.OrderBy(k => k.Key))
        {
            bool emissive = kv.Value[0].IsKeywordEnabled("_EMISSION_ON");
            // One entry per distinct albedo: materials sharing a texture set share a rect.
            var entries = new Dictionary<Texture, Entry>();
            foreach (var m in kv.Value)
            {
                var a = m.GetTexture("_MainTex");
                if (!entries.ContainsKey(a))
                    entries[a] = new Entry
                    {
                        albedo = a, mask = m.GetTexture("_PackedMap"),
                        emission = emissive ? m.GetTexture("_EmissionMap") : null,
                        area = a.width * a.height,
                    };
            }
            foreach (var chunk in Chunks(entries.Values.OrderByDescending(e => e.area).ToList()))
            {
                var name = $"atlas_{atlasIndex++}";
                var mat = BuildAtlas(name, chunk, kv.Value[0], emissive);
                foreach (var m in kv.Value)
                {
                    var e = chunk.FirstOrDefault(c => c.albedo == m.GetTexture("_MainTex"));
                    if (e != null)
                        remap[m] = (mat, e.rect);
                }
            }
        }

        // 3. Remap the meshes and merge submeshes that now share a material.
        var meshCache = new Dictionary<string, Mesh>();
        int before = 0, after = 0;
        foreach (var r in renderers)
        {
            var mats = r.sharedMaterials;
            before += mats.Length;
            if (!mats.Any(m => m != null && remap.ContainsKey(m)))
            {
                after += mats.Length;
                continue;
            }
            var mf = r.GetComponent<MeshFilter>();
            var src = mf.sharedMesh;
            var newMats = mats.Select(m => m != null && remap.ContainsKey(m) ? remap[m].mat : m).ToArray();
            var key = src.GetInstanceID() + ":" + string.Join(",", mats.Select(m => m ? m.GetInstanceID() : 0));
            if (!meshCache.TryGetValue(key, out var mesh))
            {
                mesh = Remap(src, mats, remap, out var merged);
                AssetDatabase.CreateAsset(mesh, $"{Out}/Meshes/{Sanitize(r.name)}_{meshCache.Count}.asset");
                meshCache[key] = mesh;
            }
            var unique = newMats.Distinct().ToArray();
            mf.sharedMesh = mesh;
            r.sharedMaterials = unique;
            after += unique.Length;
        }
        AssetDatabase.SaveAssets();
        var scene = EditorSceneManager.GetActiveScene();
        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        int matCount = renderers.SelectMany(x => x.sharedMaterials).Where(m => m != null).Distinct().Count();
        Debug.Log($"[AtlasSetup] {remap.Count} materials into {atlasIndex} atlases; submeshes {before} -> {after}; scene materials now {matCount}");
    }

    static bool Atlasable(Material m)
    {
        if (Excluded.Contains(m.name) || m.renderQueue != 2000)
            return false;
        var a = m.GetTexture("_MainTex");
        if (a == null || a.wrapMode == TextureWrapMode.Repeat || a.width > AtlasSize / 2)
            return false;
        var p = m.GetTexture("_PackedMap");
        return p == null || p.wrapMode != TextureWrapMode.Repeat;
    }

    static string GroupKey(Material m)
    {
        var kw = string.Join(",", m.shaderKeywords.OrderBy(k => k));
        return $"{m.shader.name}|{kw}|{m.GetInt("_LightVolumeSpecularity")}|{m.GetColor("_Color")}|{m.globalIlluminationFlags}";
    }

    // Greedy split by area so each chunk fits one atlas with room for packing slack.
    static IEnumerable<List<Entry>> Chunks(List<Entry> entries)
    {
        long budget = (long)AtlasSize * AtlasSize;       // power-of-two cells tile exactly
        var cur = new List<Entry>(); long used = 0;
        foreach (var e in entries)
        {
            if (used + e.area > budget && cur.Count > 0)
            {
                yield return cur;
                cur = new List<Entry>(); used = 0;
            }
            cur.Add(e); used += e.area;
        }
        if (cur.Count > 0)
            yield return cur;
    }

    static Material BuildAtlas(string name, List<Entry> chunk, Material template, bool emissive)
    {
        // Each cell keeps the texture's power-of-two size; the image is drawn Pad pixels
        // smaller inside it so the cells tile the atlas exactly.
        var padded = chunk.Select(e => Pixels(e.albedo, true, e.albedo.width - 2 * Pad, e.albedo.height - 2 * Pad)).ToArray();
        // Smallest power-of-two atlas the tiles fit in (a mostly-empty 4096 wastes memory).
        // Smallest atlas that fits, trying each size as a 2:1 strip before the full square.
        Vector2Int[] pos = null; int size = 256, rows = 256;
        for (; size <= AtlasSize && pos == null; size *= 2)
            foreach (var r in new[] { size / 2, size })
                if ((pos = Place(chunk, size, r)) != null) { rows = r; break; }
        size /= 2;
        if (pos == null) throw new System.Exception($"[AtlasSetup] {name} overflowed");
        int w = size, h = rows;
        var albedo = Filled(w, h, new Color32(128, 128, 128, 255));
        var mask = Filled(w, h, new Color32(0, 0, 0, 30));
        var emis = emissive ? Filled(w, h, new Color32(0, 0, 0, 255)) : null;
        for (int i = 0; i < chunk.Count; i++)
        {
            var e = chunk[i];
            // pos is the padded cell; the real image sits Pad pixels inside it.
            int tw = e.albedo.width - 2 * Pad, th = e.albedo.height - 2 * Pad;
            int x0 = pos[i].x + Pad, y0 = pos[i].y + Pad;
            Blit(albedo, w, h, padded[i], tw, th, x0, y0);
            if (e.mask != null) Blit(mask, w, h, Pixels(e.mask, false, tw, th), tw, th, x0, y0);
            if (emis != null && e.emission != null) Blit(emis, w, h, Pixels(e.emission, true, tw, th), tw, th, x0, y0);
            e.rect = new Rect((float)x0 / w, (float)y0 / h, (float)tw / w, (float)th / h);
        }
        var mat = new Material(template) { name = name };
        mat.SetTexture("_MainTex", Save(albedo, w, h, $"{Out}/{name}_albedo.png", true));
        mat.SetTexture("_PackedMap", Save(mask, w, h, $"{Out}/{name}_mask.png", false));
        if (emis != null)
            mat.SetTexture("_EmissionMap", Save(emis, w, h, $"{Out}/{name}_emission.png", true));
        else
            mat.SetTexture("_EmissionMap", null);
        var path = $"{Out}/{name}.mat";
        AssetDatabase.DeleteAsset(path);
        AssetDatabase.CreateAsset(mat, path);
        return mat;
    }

    // Readable pixels of any texture at a given size, through a render target.
    static Color32[] Pixels(Texture src, bool srgb, int w, int h)
    {
        var rt = RenderTexture.GetTemporary(w, h, 0, RenderTextureFormat.ARGB32,
                                            srgb ? RenderTextureReadWrite.sRGB : RenderTextureReadWrite.Linear);
        Graphics.Blit(src, rt);
        var prev = RenderTexture.active;
        RenderTexture.active = rt;
        var t = new Texture2D(w, h, TextureFormat.RGBA32, false, !srgb);
        t.ReadPixels(new Rect(0, 0, w, h), 0, 0);
        t.Apply();
        RenderTexture.active = prev;
        RenderTexture.ReleaseTemporary(rt);
        var px = t.GetPixels32();
        Object.DestroyImmediate(t);
        return px;
    }

    // Buddy allocation: every tile is a power-of-two square, so splitting free squares into
    // quarters packs them with no waste. Null when they don't fit in an atlas of this size.
    static Vector2Int[] Place(List<Entry> chunk, int atlas, int rows)
    {
        var pos = new Vector2Int[chunk.Count];
        var free = new List<(int x, int y, int s)> { (0, 0, rows) };
        if (rows < atlas) free.Add((rows, 0, rows));        // a 2:1 strip is two squares side by side
        foreach (var i in Enumerable.Range(0, chunk.Count).OrderByDescending(i => chunk[i].albedo.width))
        {
            int size = chunk[i].albedo.width;
            var fit = free.Where(f => f.s >= size).OrderBy(f => f.s).ThenBy(f => f.y).ThenBy(f => f.x).ToList();
            if (fit.Count == 0) return null;
            var sq = fit[0];
            free.Remove(sq);
            while (sq.s > size)
            {
                int h2 = sq.s / 2;
                free.Add((sq.x + h2, sq.y, h2)); free.Add((sq.x, sq.y + h2, h2)); free.Add((sq.x + h2, sq.y + h2, h2));
                sq = (sq.x, sq.y, h2);
            }
            pos[i] = new Vector2Int(sq.x, sq.y);
        }
        return pos;
    }

    static Color32[] Filled(int w, int h, Color32 c)
    {
        var px = new Color32[w * h];
        for (int i = 0; i < px.Length; i++) px[i] = c;
        return px;
    }

    // Copies a w*h tile to (x0, y0) and bleeds its edge pixels out into the padding so
    // mipmaps and bilinear filtering never pick up a neighbour.
    static void Blit(Color32[] dst, int dw, int dh, Color32[] src, int w, int h, int x0, int y0)
    {
        for (int y = -Pad; y < h + Pad; y++)
        {
            int sy = Mathf.Clamp(y, 0, h - 1), dy = y0 + y;
            if (dy < 0 || dy >= dh) continue;
            for (int x = -Pad; x < w + Pad; x++)
            {
                int dx = x0 + x;
                if (dx < 0 || dx >= dw) continue;
                dst[dy * dw + dx] = src[sy * w + Mathf.Clamp(x, 0, w - 1)];
            }
        }
    }

    static Texture2D Save(Color32[] px, int size, int rows, string path, bool srgb)
    {
        var t = new Texture2D(size, rows, TextureFormat.RGBA32, false, !srgb);
        t.SetPixels32(px);
        t.Apply();
        File.WriteAllBytes(path, t.EncodeToPNG());
        Object.DestroyImmediate(t);
        AssetDatabase.ImportAsset(path);
        var imp = (TextureImporter)AssetImporter.GetAtPath(path);
        imp.sRGBTexture = srgb;
        // Masks and emission maps are mostly flat, so they import at half the atlas size, as
        // the per-object ones did (512 for 1024 albedos). UVs are normalised, so it just works.
        bool half = path.EndsWith("_mask.png") || path.EndsWith("_emission.png");
        int max = half ? Mathf.Max(256, size / 2) : size;
        imp.maxTextureSize = max;
        imp.mipmapEnabled = true;
        imp.wrapMode = TextureWrapMode.Clamp;
        // Same compression the per-object textures used: DXT1 for colour, DXT5 for the mask
        // (smoothness lives in alpha). BC7 would double the memory for little gain.
        imp.textureCompression = TextureImporterCompression.Compressed;
        imp.alphaSource = srgb ? TextureImporterAlphaSource.None : TextureImporterAlphaSource.FromInput;
        imp.crunchedCompression = true;                            // smaller download; same DXT in memory
        imp.compressionQuality = 60;
        imp.SetPlatformTextureSettings(new TextureImporterPlatformSettings
        {
            name = "Android", overridden = true, maxTextureSize = max,
            format = TextureImporterFormat.ASTC_6x6,
        });
        imp.SaveAndReimport();
        return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
    }

    // Copy of the mesh with UV0 of every atlased submesh moved into its rect, vertices
    // split per submesh (a vertex shared by two submeshes can't sit in two rects), and
    // submeshes that now share a material merged.
    static Mesh Remap(Mesh src, Material[] mats, Dictionary<Material, (Material mat, Rect rect)> remap, out int merged)
    {
        var verts = new List<Vector3>(); var norms = new List<Vector3>(); var tans = new List<Vector4>();
        var uv0 = new List<Vector2>(); var uv1 = new List<Vector2>(); var cols = new List<Color>();
        var sv = src.vertices; var sn = src.normals; var st = src.tangents; var su0 = new List<Vector2>(); var su1 = new List<Vector2>();
        src.GetUVs(0, su0); src.GetUVs(1, su1);
        var sc = src.colors;
        var byMat = new Dictionary<Material, List<int>>();
        var order = new List<Material>();
        for (int s = 0; s < src.subMeshCount && s < mats.Length; s++)
        {
            var m = mats[s];
            bool at = m != null && remap.ContainsKey(m);
            var target = at ? remap[m].mat : m;
            var rect = at ? remap[m].rect : new Rect(0, 0, 1, 1);
            if (!byMat.TryGetValue(target, out var tris)) { byMat[target] = tris = new List<int>(); order.Add(target); }
            var map = new Dictionary<int, int>();
            foreach (var i in src.GetTriangles(s))
            {
                if (!map.TryGetValue(i, out var ni))
                {
                    ni = verts.Count; map[i] = ni;
                    verts.Add(sv[i]);
                    if (sn.Length > 0) norms.Add(sn[i]);
                    if (st.Length > 0) tans.Add(st[i]);
                    if (sc.Length > 0) cols.Add(sc[i]);
                    var uv = su0.Count > 0 ? su0[i] : Vector2.zero;
                    if (at) uv = new Vector2(rect.x + Mathf.Clamp01(uv.x) * rect.width, rect.y + Mathf.Clamp01(uv.y) * rect.height);
                    uv0.Add(uv);
                    if (su1.Count > 0) uv1.Add(su1[i]);
                }
                tris.Add(ni);
            }
        }
        var mesh = new Mesh { name = src.name + "_atlased" };
        mesh.indexFormat = verts.Count > 65000 ? UnityEngine.Rendering.IndexFormat.UInt32 : UnityEngine.Rendering.IndexFormat.UInt16;
        mesh.SetVertices(verts);
        if (norms.Count == verts.Count) mesh.SetNormals(norms);
        if (tans.Count == verts.Count) mesh.SetTangents(tans);
        if (cols.Count == verts.Count) mesh.SetColors(cols);
        mesh.SetUVs(0, uv0);
        if (uv1.Count == verts.Count) mesh.SetUVs(1, uv1);
        mesh.subMeshCount = order.Count;
        for (int i = 0; i < order.Count; i++)
            mesh.SetTriangles(byMat[order[i]], i);
        mesh.RecalculateBounds();
        merged = src.subMeshCount - order.Count;
        return mesh;
    }

    static string Sanitize(string s) => new string(s.Select(c => char.IsLetterOrDigit(c) || c == '_' ? c : '_').ToArray());
}
