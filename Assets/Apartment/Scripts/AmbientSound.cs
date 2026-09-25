// A looping ambient sound (local, unsynced). Starts at its own offset so copies of the
// same loop don't play in step, and can cycle on and off with a fade (the portable AC).

using UdonSharp;
using UnityEngine;

[UdonBehaviourSyncMode(BehaviourSyncMode.None)]
public class AmbientSound : UdonSharpBehaviour
{
    public AudioSource source;
    public float startOffset;
    public bool cycle;
    public float onSeconds = 150f;
    public float offSeconds = 240f;
    public float fadeSeconds = 2f;

    float volume, timer, level;
    bool running;

    void Start()
    {
        volume = source.volume;
        if (source.clip != null) source.time = startOffset % source.clip.length;
        running = true;
        level = 1f;
        timer = cycle ? Random.Range(0f, onSeconds) : 0f;      // not everyone's AC in step
        source.Play();
    }

    void Update()
    {
        if (!cycle) return;
        timer += Time.deltaTime;
        if (timer >= (running ? onSeconds : offSeconds))
        {
            timer = 0f;
            running = !running;
            if (running) source.Play();
        }
        level = Mathf.MoveTowards(level, running ? 1f : 0f, Time.deltaTime / Mathf.Max(0.01f, fadeSeconds));
        source.volume = volume * level;
        if (!running && level <= 0f && source.isPlaying) source.Stop();
    }
}
