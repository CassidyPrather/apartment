// A bypass closet door leaf, synced for everyone: click it to slide it across to the other
// half of the opening (past the other leaf, on its own track) or back. Lives on the leaf,
// with a trigger collider.

using UdonSharp;
using UnityEngine;
using VRC.SDKBase;

[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]
public class SlidingDoor : UdonSharpBehaviour
{
    public Vector3 closedPosition;          // local (parent space)
    public Vector3 openPosition;
    public AudioSource sound;
    public AudioClip[] openClips;
    public AudioClip[] closeClips;
    public float seconds = 1.1f;

    [UdonSynced] public bool isOpen;

    float t;

    void Start()
    {
        t = isOpen ? 1f : 0f;
        transform.localPosition = isOpen ? openPosition : closedPosition;
        Label();
    }

    public override void Interact()
    {
        Networking.SetOwner(Networking.LocalPlayer, gameObject);
        isOpen = !isOpen;
        RequestSerialization();
        Begin();
    }

    public override void OnDeserialization()
    {
        if (Time.timeSinceLevelLoad < 8f)
        {
            // just joined: the leaf was already here, so snap to it silently
            t = isOpen ? 1f : 0f;
            transform.localPosition = isOpen ? openPosition : closedPosition;
            Label();
            return;
        }
        Begin();
    }

    void Begin()
    {
        Label();
        var clips = isOpen ? openClips : closeClips;
        if (sound != null && clips != null && clips.Length > 0)
            sound.PlayOneShot(clips[Random.Range(0, clips.Length)]);
    }

    void Update()
    {
        float target = isOpen ? 1f : 0f;
        if (t == target) return;
        t = Mathf.MoveTowards(t, target, Time.deltaTime / Mathf.Max(0.05f, seconds));
        transform.localPosition = Vector3.Lerp(closedPosition, openPosition, t * t * (3f - 2f * t));
    }

    void Label() => InteractionText = isOpen ? "Close" : "Open";
}
