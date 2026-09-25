#ifndef APARTMENT_NIGHT_INCLUDED
#define APARTMENT_NIGHT_INCLUDED
// Apartment world addition (not part of Mochie): the day/night switch dims the baked
// lightmap and reflections at runtime (Udon can't swap lightmaps). Set by the
// DayNight UdonSharp script with VRCShader.SetGlobal*. Unset globals are 0, so
// _Udon_ApartmentNight = 0 means plain day lighting.
// Mochie's per-material Light Volume settings (its bundled LightVolumes.cginc declared
// them; the package's own include doesn't).
float3 lightVolumeL0;
float3 lightVolumeL1r;
float3 lightVolumeL1g;
float3 lightVolumeL1b;
float3 lvSpec;
int _LightVolumesToggle;
float _LightVolumeStrength;
int _AdditiveLightVolumesToggle;
float _AdditiveLightVolumeStrength;
int _LightVolumeSpecularity;
float _LightVolumeSpecularityStrength;
float _LightVolumeBias;

uniform float _Udon_ApartmentNight;          // 0 = day, 1 = night
uniform float4 _Udon_ApartmentNightTint;     // rgb multiplier on baked light at full night

float3 ApartmentNightDim(float3 baked){
    return lerp(baked, baked * _Udon_ApartmentNightTint.rgb, saturate(_Udon_ApartmentNight));
}
#endif
