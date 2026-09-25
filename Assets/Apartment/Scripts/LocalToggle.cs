// Local (per-player, unsynced) on/off switch: Interact flips the targets' active state.
// Used for the bathroom mirror, which is off by default so it costs nothing until
// someone wants it.

using UdonSharp;
using UnityEngine;

[UdonBehaviourSyncMode(BehaviourSyncMode.None)]
public class LocalToggle : UdonSharpBehaviour
{
    public GameObject[] targets;

    public override void Interact()
    {
        foreach (var t in targets)
            if (t != null)
                t.SetActive(!t.activeSelf);
    }
}
