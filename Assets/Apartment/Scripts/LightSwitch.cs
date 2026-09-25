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
    public float fadeSeconds = 0.25f;

    [UdonSynced] public bool isOn;

    float weight;
    MaterialPropertyBlock block;

    void Start()
    {
        block = new MaterialPropertyBlock();
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
            toggle.localRotation = Quaternion.Euler(isOn ? -12f : 12f, 0f, 0f);
    }

    void Update()
    {
        float target = isOn ? 1f : 0f;
        if (weight == target) return;
        weight = Mathf.MoveTowards(weight, target, Time.deltaTime / Mathf.Max(0.01f, fadeSeconds));
        SetLights();
    }

    void SetLights()
    {
        foreach (var l in lights)
            if (l != null) l.SetWeight(weight);
    }
}
