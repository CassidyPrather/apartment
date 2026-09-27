// The futon, synced for everyone: click it to lay it out on the living room floor, or to
// roll it back into its sack by the wall. One trigger collider follows whichever state shows,
// so it can be clicked but never blocks anyone walking.

using UdonSharp;
using UnityEngine;
using VRC.SDKBase;

[UdonBehaviourSyncMode(BehaviourSyncMode.Manual)]
public class FutonToggle : UdonSharpBehaviour
{
    public GameObject flat;
    public GameObject stored;             // rolled up in its sack
    public BoxCollider hit;                // trigger on this object, fitted to each state
    public Vector3 flatCenter, flatSize, storedCenter, storedSize;

    [UdonSynced] public bool laidOut;

    void Start() => Apply();

    public override void Interact()
    {
        Networking.SetOwner(Networking.LocalPlayer, gameObject);
        laidOut = !laidOut;
        RequestSerialization();
        Apply();
    }

    public override void OnDeserialization() => Apply();

    void Apply()
    {
        flat.SetActive(laidOut);
        stored.SetActive(!laidOut);
        hit.center = laidOut ? flatCenter : storedCenter;
        hit.size = laidOut ? flatSize : storedSize;
        InteractionText = laidOut ? "Roll up the futon" : "Lay out the futon";
    }
}
