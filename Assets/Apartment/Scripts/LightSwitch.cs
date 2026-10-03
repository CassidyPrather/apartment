// A wall (or lamp) switch for one light source, synced for everyone. It fades the
// fixture's Point Light Volumes and turns its glowing glass on and off.

using UdonSharp;
using UnityEngine;
using VRC.SDKBase;
using VRCLightVolumes;

[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]
public class LightSwitch : UdonSharpBehaviour
{
    public PointLightVolumeInstance[] lights;
    public Renderer[] glows;               // fixture renderers whose glass glows
    public int[] glowSlots;                // material slot of the glowing glass on each
    public Color glowColor = Color.white;
    public Transform toggle;               // the switch lever/knob, flipped when on
    public Quaternion onRotation = Quaternion.Euler(-12f, 0f, 0f);    // the lever's local pose when on
    public Quaternion offRotation = Quaternion.Euler(12f, 0f, 0f);    // ...and when off
    public float fadeSeconds = 0.25f;

    [UdonSynced] public bool isOn;

    float weight;
    float[] fullIntensity;                 // each light's authored intensity, scaled by the fade
    MaterialPropertyBlock block;

    void Start()
    {
        block = new MaterialPropertyBlock();
        fullIntensity = new float[lights.Length];
        for (int i = 0; i < lights.Length; i++)
            if (lights[i] != null) fullIntensity[i] = lights[i].Intensity;
        weight = isOn ? 1f : 0f;
        Apply(true);
    }

    public override void Interact()
    {
        Networking.SetOwner(Networking.LocalPlayer, gameObject);
        isOn = !isOn;
        RequestSerialization();
        Apply(false);
    }

    public override void OnDeserialization() => Apply(false);

    void Apply(bool instant)
    {
        if (instant) weight = isOn ? 1f : 0f;
        SetLights();
        for (int i = 0; i < glows.Length; i++)
        {
            if (glows[i] == null) continue;
            glows[i].GetPropertyBlock(block, glowSlots[i]);
            block.SetColor("_EmissionColor", isOn ? glowColor : Color.black);
            glows[i].SetPropertyBlock(block, glowSlots[i]);
        }
        if (toggle != null)
            toggle.localRotation = isOn ? onRotation : offRotation;
        if (!instant) StartTick();
    }

    // Runs only while moving: a per-frame Update on every idle door or switch costs Udon time each
    // frame (it adds up on Quest), so movement ticks itself one frame at a time instead.
    bool ticking;

    void StartTick()
    {
        if (ticking) return;
        ticking = true;
        SendCustomEventDelayedFrames(nameof(_Tick), 1);
    }

    public void _Tick()
    {
        float target = isOn ? 1f : 0f;
        weight = Mathf.MoveTowards(weight, target, Time.deltaTime / Mathf.Max(0.01f, fadeSeconds));
        SetLights();
        if (weight == target) { ticking = false; return; }
        SendCustomEventDelayedFrames(nameof(_Tick), 1);
    }

    // Light Volumes 3's SetWeight is only a render priority, so the fade scales the intensity.
    void SetLights()
    {
        for (int i = 0; i < lights.Length; i++)
            if (lights[i] != null) lights[i].SetIntensity(fullIntensity[i] * weight);
    }
}
