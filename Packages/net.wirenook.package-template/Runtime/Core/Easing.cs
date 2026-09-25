// SDK-free sample logic.
//
// Anything in Runtime/Core/ is compiled by scripts/test.sh against nothing but
// the standard library and NUnit -- no Unity, no VRChat SDK. That restriction
// is the point: logic that lives here is logic CI can prove out, so a stray
// `using UnityEngine` here fails the build on purpose. Glue that needs the
// engine goes in Runtime/ proper; see SKILL.md.
//
// To add your own module:
// 1. Copy this file to a new name (e.g., Cooldown.cs) and gut the contents
// 2. Keep it engine-free -- System.* only
// 3. Add tests beside Tests/Editor/EasingTests.cs; classic NUnit asserts run
//    both headless and in the Unity Test Runner

namespace Wirenook.PackageTemplate
{
    /// <summary>Easing curves and the interval math that feeds them.</summary>
    public static class Easing
    {
        /// <summary>Pins <paramref name="t"/> to [0, 1].</summary>
        public static float Clamp01(float t)
        {
            return t < 0f ? 0f : (t > 1f ? 1f : t);
        }

        /// <summary>Linear interpolation from <paramref name="a"/> to <paramref name="b"/>; t is clamped.</summary>
        public static float Lerp(float a, float b, float t)
        {
            return a + ((b - a) * Clamp01(t));
        }

        /// <summary>Hermite ease-in-out: slow at both ends, fastest in the middle.</summary>
        public static float SmoothStep(float t)
        {
            t = Clamp01(t);
            return t * t * (3f - (2f * t));
        }

        /// <summary>Cubic ease-out: fast start, gentle landing.</summary>
        public static float EaseOutCubic(float t)
        {
            float u = 1f - Clamp01(t);
            return 1f - (u * u * u);
        }
    }
}
