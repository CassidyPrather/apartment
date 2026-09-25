// Grab-and-pull drawer (filing cabinet and the like).
//
// Setup, all under one cabinet root:
//   cabinet_root
//     drawer        the visible drawer mesh, pull included; moves along slideAxis
//     drawer_grab   this script + VRC Pickup + Rigidbody (kinematic, no gravity)
//                   + BoxCollider (not a trigger) wrapped around the visible pull
// The grab handle is a sibling of the drawer, never its child, so the pickup
// system can carry it freely; both must share a parent because every position
// here is in that parent's local space. No mesh on the handle and no VRC Object
// Sync: only the open distance is synced, and each client re-seats the handle.
//
// While held, the handle's offset from its closed spot is projected onto
// slideAxis and clamped to [0, maxTravel]; the drawer follows. On release the
// handle snaps back onto the pull. Last grabber wins: a player who loses
// ownership mid-pull is made to drop.

using UdonSharp;
using UnityEngine;
using VRC.SDK3.Components;
using VRC.SDKBase;

[UdonBehaviourSyncMode(BehaviourSyncMode.Continuous)]
public class SlidingDrawer : UdonSharpBehaviour
{
    [Tooltip("The moving drawer; must share this handle's parent.")]
    public Transform drawer;

    [Tooltip("Opening direction in the shared parent's local space; normalized at Start.")]
    public Vector3 slideAxis = Vector3.forward;

    [Tooltip("Full-open travel in meters.")]
    public float maxTravel = 0.6f;

    [Tooltip("Openings under this (meters) snap shut on release.")]
    public float snapClosed = 0.01f;

    // Open distance in meters, owner-authored; interpolated for everyone else.
    [UdonSynced(UdonSyncMode.Linear)] private float open;

    private VRCPickup pickup;
    private Vector3 axis;
    private Vector3 closedDrawerPos;
    private Vector3 closedHandlePos;
    private Quaternion handleRot;
    private bool held;
    private bool ready;

    private void Start()
    {
        if (drawer == null || drawer.parent != transform.parent)
        {
            Debug.LogError("[SlidingDrawer] " + name + ": drawer must be set and share this handle's parent.");
            return;
        }

        pickup = GetComponent<VRCPickup>();
        axis = slideAxis.normalized;

        // Scene is authored closed: record both closed poses in the shared parent space.
        closedDrawerPos = drawer.localPosition;
        closedHandlePos = transform.localPosition;
        handleRot = transform.localRotation;
        ready = true;
        Apply();
    }

    public override void OnPickup()
    {
        held = true;
        if (!Networking.IsOwner(gameObject))
            Networking.SetOwner(Networking.LocalPlayer, gameObject);
    }

    public override void OnDrop()
    {
        held = false;
        if (open < snapClosed)
            open = 0f;
        Apply();
        if (Networking.IsOwner(gameObject))
            RequestSerialization();
    }

    public override void OnDeserialization()
    {
        if (!held)
            Apply();
    }

    // After the pickup system has moved the handle this frame.
    public override void PostLateUpdate()
    {
        if (!ready)
            return;

        if (held)
        {
            if (!Networking.IsOwner(gameObject))
            {
                // Someone else grabbed it; their pull is authoritative.
                if (pickup != null)
                    pickup.Drop();
                held = false;
                Apply();
                return;
            }

            float d = Vector3.Dot(transform.localPosition - closedHandlePos, axis);
            open = Mathf.Clamp(d, 0f, maxTravel);
            drawer.localPosition = closedDrawerPos + axis * open;
            return;
        }

        // Not held here: follow the (interpolated) synced value and keep the
        // handle seated on the pull against physics drift.
        Apply();
    }

    private void Apply()
    {
        if (!ready)
            return;
        Vector3 offset = axis * open;
        drawer.localPosition = closedDrawerPos + offset;
        transform.localPosition = closedHandlePos + offset;
        transform.localRotation = handleRot;
    }
}
