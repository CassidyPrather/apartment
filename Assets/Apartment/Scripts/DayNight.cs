// Day/night switch, synced for everyone. Day is the baked daylight. Night dims the
// baked lightmap and reflections (a global the apartment's Mochie shader reads), the
// room Light Volumes (so avatars and moving things darken too) and the outdoor
// backdrop, and shows the starry sky. The room lamps are separate LightSwitches.

using UdonSharp;
using UnityEngine;
using VRC.SDKBase;
using VRCLightVolumes;

[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]
public class DayNight : UdonSharpBehaviour
{
    public LightVolumeInstance[] roomVolumes;
    public float nightVolumeIntensity = 0.07f;
    public Color nightTint = new Color(0.07f, 0.09f, 0.18f);   // baked light at night
    public Renderer[] exterior;                               // the painted outdoor backdrop
    public Color nightExterior = new Color(0.10f, 0.13f, 0.28f);
    public GameObject stars;                                  // the night sky dome
    public Material daySkybox;
    public Material nightSkybox;
    public Material exteriorDay;                              // the backdrop's material by day
    public Material exteriorNight;                            // ...and at night (starry sky glow)

    [UdonSynced] public bool night;

    int nightId, tintId;
    MaterialPropertyBlock block;

    void Start()
    {
        nightId = VRCShader.PropertyToID("_Udon_ApartmentNight");
        tintId = VRCShader.PropertyToID("_Udon_ApartmentNightTint");
        block = new MaterialPropertyBlock();
        Apply();
    }

    public override void Interact()
    {
        Networking.SetOwner(Networking.LocalPlayer, gameObject);
        night = !night;
        RequestSerialization();
        Apply();
    }

    public override void OnDeserialization() => Apply();

    void Apply()
    {
        VRCShader.SetGlobalFloat(nightId, night ? 1f : 0f);
        VRCShader.SetGlobalVector(tintId, new Vector4(nightTint.r, nightTint.g, nightTint.b, 1f));
        foreach (var v in roomVolumes)
            if (v != null) v.SetIntensity(night ? nightVolumeIntensity : 1f);
        foreach (var r in exterior)
        {
            if (r == null) continue;
            if (exteriorDay != null && exteriorNight != null)
            {
                var mats = r.sharedMaterials;
                for (int i = 0; i < mats.Length; i++)
                    if (mats[i] == exteriorDay || mats[i] == exteriorNight)
                        mats[i] = night ? exteriorNight : exteriorDay;
                r.sharedMaterials = mats;
            }
            r.GetPropertyBlock(block);
            block.SetColor("_Color", night ? nightExterior : Color.white);
            r.SetPropertyBlock(block);
        }
        if (stars != null) stars.SetActive(night);
        if (daySkybox != null && nightSkybox != null)
            RenderSettings.skybox = night ? nightSkybox : daySkybox;
    }
}
