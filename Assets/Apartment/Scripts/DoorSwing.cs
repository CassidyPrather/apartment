// A hinged door leaf that swings open and shut when clicked, synced for everyone, with an
// opening creak and a closing latch. Lives on the leaf itself (origin on the hinge pin),
// with a trigger collider so it can be clicked but never blocks anyone walking.

using UdonSharp;
using UnityEngine;
using VRC.SDKBase;

[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]
public class DoorSwing : UdonSharpBehaviour
{
    public Quaternion closedRotation;
    public Quaternion openRotation;
    public AudioSource sound;
    public AudioClip[] openClips;
    public AudioClip[] closeClips;
    public float seconds = 0.9f;

    [UdonSynced] public bool isOpen;

    float t;                    // 0 closed .. 1 open
    bool latchPending;

    void Start()
    {
        t = isOpen ? 1f : 0f;
        transform.localRotation = isOpen ? openRotation : closedRotation;
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
            // just joined: this is the state the door was already in, so snap to it silently
            t = isOpen ? 1f : 0f;
            transform.localRotation = isOpen ? openRotation : closedRotation;
            Label();
            return;
        }
        Begin();
    }

    void Begin()
    {
        Label();
        if (isOpen)
        {
            latchPending = false;
            Play(openClips);
        }
        else
        {
            latchPending = true;                     // the latch clicks as it shuts
        }
    }

    void Update()
    {
        float target = isOpen ? 1f : 0f;
        if (t == target) return;
        t = Mathf.MoveTowards(t, target, Time.deltaTime / Mathf.Max(0.05f, seconds));
        float e = t * t * (3f - 2f * t);             // ease in and out
        transform.localRotation = Quaternion.Slerp(closedRotation, openRotation, e);
        if (t <= 0f && latchPending)
        {
            latchPending = false;
            Play(closeClips);
        }
    }

    void Play(AudioClip[] clips)
    {
        if (sound == null || clips == null || clips.Length == 0) return;
        sound.PlayOneShot(clips[Random.Range(0, clips.Length)]);
    }

    void Label() => InteractionText = isOpen ? "Close" : "Open";
}
