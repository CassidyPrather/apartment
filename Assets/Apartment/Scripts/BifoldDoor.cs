// One pair of a bifold door, synced for everyone: click the lead leaf (the one with the
// knob) to fold the pair open or shut. The outer leaf swings about its jamb pin; the lead
// leaf rides on the fold and turns the other way, so its free edge runs back along the
// track, as a real bifold does. Lives on the lead leaf, with a trigger collider.

using UdonSharp;
using UnityEngine;
using VRC.SDKBase;

[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]
public class BifoldDoor : UdonSharpBehaviour
{
    public Transform outer;                 // hinged on the jamb
    public Transform inner;                 // the lead leaf, pinned at the fold (this object)
    public Vector3 outerPin;                // closed local positions (parent space)
    public Vector3 innerPin;
    public Quaternion outerClosed;
    public Quaternion innerClosed;
    public float openDegrees = 80f;         // signed: the side the fold swings out to
    public AudioSource sound;
    public AudioClip[] openClips;
    public AudioClip[] closeClips;
    public float seconds = 0.8f;

    [UdonSynced] public bool isOpen;

    float t;
    bool latchPending;

    void Start()
    {
        t = isOpen ? 1f : 0f;
        Pose(t);
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
            // just joined: the pair was already like this, so snap to it silently
            t = isOpen ? 1f : 0f;
            Pose(t);
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
            latchPending = true;
        }
    }

    void Update()
    {
        float target = isOpen ? 1f : 0f;
        if (t == target) return;
        t = Mathf.MoveTowards(t, target, Time.deltaTime / Mathf.Max(0.05f, seconds));
        Pose(t * t * (3f - 2f * t));
        if (t <= 0f && latchPending)
        {
            latchPending = false;
            Play(closeClips);
        }
    }

    void Pose(float k)
    {
        float a = openDegrees * k;
        Quaternion turn = Quaternion.AngleAxis(a, Vector3.up);
        outer.localRotation = turn * outerClosed;
        outer.localPosition = outerPin;
        inner.localPosition = outerPin + turn * (innerPin - outerPin);
        inner.localRotation = Quaternion.AngleAxis(-a, Vector3.up) * innerClosed;
    }

    void Play(AudioClip[] clips)
    {
        if (sound == null || clips == null || clips.Length == 0) return;
        sound.PlayOneShot(clips[Random.Range(0, clips.Length)]);
    }

    void Label() => InteractionText = isOpen ? "Close" : "Open";
}
