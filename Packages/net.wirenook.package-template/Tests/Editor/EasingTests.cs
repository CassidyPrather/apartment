// Sample tests. The same file runs two ways: under `dotnet test` via
// scripts/test.sh (headless, no Unity) and in the editor via
// Window > General > Test Runner (EditMode). Classic asserts only -- the Unity
// Test Framework vendors NUnit 3, and NUnit 4 dropped them, so the classic API
// is the overlap that keeps both runners honest.

using NUnit.Framework;

namespace Wirenook.PackageTemplate.Tests
{
    public class EasingTests
    {
        [Test]
        public void clamp01_pins_values_outside_the_unit_interval()
        {
            Assert.AreEqual(0f, Easing.Clamp01(-3f));
            Assert.AreEqual(1f, Easing.Clamp01(2f));
        }

        [Test]
        public void clamp01_leaves_the_unit_interval_alone()
        {
            Assert.AreEqual(0.25f, Easing.Clamp01(0.25f));
        }

        [Test]
        public void lerp_lands_midway_at_half()
        {
            Assert.AreEqual(5f, Easing.Lerp(0f, 10f, 0.5f), 1e-6f);
        }

        [Test]
        public void lerp_clamps_rather_than_extrapolates()
        {
            Assert.AreEqual(10f, Easing.Lerp(0f, 10f, 1.5f), 1e-6f);
            Assert.AreEqual(0f, Easing.Lerp(0f, 10f, -0.5f), 1e-6f);
        }

        [Test]
        public void smooth_step_agrees_with_linear_at_the_endpoints_and_midpoint()
        {
            Assert.AreEqual(0f, Easing.SmoothStep(0f), 1e-6f);
            Assert.AreEqual(0.5f, Easing.SmoothStep(0.5f), 1e-6f);
            Assert.AreEqual(1f, Easing.SmoothStep(1f), 1e-6f);
        }

        [Test]
        public void ease_out_cubic_never_reverses_over_the_unit_interval()
        {
            // Monotonicity is the property callers actually rely on: an easing
            // curve that doubles back reads as jitter on whatever it drives.
            float previous = Easing.EaseOutCubic(0f);
            for (int i = 1; i <= 100; i++)
            {
                float current = Easing.EaseOutCubic(i / 100f);
                Assert.GreaterOrEqual(current, previous);
                previous = current;
            }
        }
    }
}
