// The breaker panel's ambient sound switch: mutes or unmutes the world's ambient
// sounds for this player only.

using UdonSharp;
using UnityEngine;

[UdonBehaviourSyncMode(BehaviourSyncMode.None)]
public class AudioToggle : UdonSharpBehaviour
{
    public AudioSource[] sources;
    public Transform toggle;               // the breaker handle, flipped when off
    bool muted;

    public override void Interact()
    {
        muted = !muted;
        foreach (var s in sources)
            if (s != null) s.mute = muted;
        if (toggle != null)
            toggle.localRotation = Quaternion.Euler(muted ? 25f : -25f, 0f, 0f);
    }
}
