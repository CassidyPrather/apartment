// An appliance's power switch, local to each player: turns its ambient sound (and
// anything else that shows it running) on and off just for the person who flips it.
// Used for the bathroom fan, the portable AC and the PC.

using UdonSharp;
using UnityEngine;

[UdonBehaviourSyncMode(BehaviourSyncMode.None)]
public class ApplianceSwitch : UdonSharpBehaviour
{
    public GameObject[] running;           // sound objects (AmbientSound) and indicators, active while on
    public Transform toggle;               // rocker, tilted when on
    public Vector3 onEuler = new Vector3(-12f, 0f, 0f);
    public Vector3 offEuler = new Vector3(12f, 0f, 0f);

    bool isOn = true;

    public override void Interact()
    {
        isOn = !isOn;
        foreach (var g in running)
            if (g != null) g.SetActive(isOn);
        if (toggle != null) toggle.localRotation = Quaternion.Euler(isOn ? onEuler : offEuler);
    }
}
