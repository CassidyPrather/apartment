# Credits

Contents, unless otherwise specified, AGPLv3: [LICENSE](LICENSE).
VRChat/Unity linking exception: [LICENSE_ADDENDUM](LICENSE_ADDENDUM).

| Asset | Source | Author | License |
| --- | --- | --- | --- | --- |
| `Packages/com.vrchat.core.bootstrap/` | VRChat's package bootstrapper, vendored unmodified from <https://github.com/vrchat-community/template-package> | VRChat | [VRCHAT DISTRO LICENSE FILE](Packages/com.vrchat.core.bootstrap/License.md) |
| `Assets/Mochie/` | Mochie's Unity Shaders v1.76 (free package), subset: Standard shaders, shared includes, editor UI, lookup textures. Modified for the apartment's night mode: `Standard Shader/StandardDefines.cginc` includes the Light Volumes 3.0 package's `LightVolumes.cginc` instead of the bundled copy, `StandardLighting.cginc` dims baked light and reflections at night, and `Common/ApartmentNight.cginc` is new. Left out: water/glass/rain textures, the GIF tool and `csc.rsp`, a proprietary header font (Century Gothic), and a Patreon logo; the editor falls back without them. <https://github.com/MochiesCode/Mochies-Unity-Shaders> | MochiesCode | MIT ([Assets/Mochie/LICENSE.txt](Assets/Mochie/LICENSE.txt)); bundles VRC Light Volumes' `LightVolumes.cginc` (MIT, REDSIM) |
| `Assets/USharpVideo/` | USharpVideo v1.0.1 (UdonSharp video player), subset: player, UI, shaders, styles, icons (Feather, MIT); files unmodified. Left out: the Examples folder (demo scene, lightmaps, sample buttons). <https://github.com/MerlinVR/USharpVideo> | Merlin | MIT ([Assets/USharpVideo/LICENSE.txt](Assets/USharpVideo/LICENSE.txt)) |
| `Assets/Apartment/Audio/Doors/` | Door sounds `doorOpen_1/2.ogg`, `doorClose_1-4.ogg` from Kenney's RPG Audio pack, unmodified. <https://kenney.nl/assets/rpg-audio> | Kenney (kenney.nl) | CC0 1.0 |

## Parody Brand Ledger

Every real brand in the apartment is replaced in-world by a parody. Reuse these
names before inventing new ones. Real brands are never recorded here.

| Parody | Appears on | Description |
| --- | --- | --- |
| tadpole link | `router` (lid wordmark) | Lowercase wordmark with a tadpole glyph. Logo: `blender/lib/textures/logos/tadpole_link.svg` |
| Motorboat | `modem` (LED strip badge) | Speedboat and wake inside a ring. Logo: `blender/lib/textures/logos/motorboat.svg` |
| squintscreen | `vr_headset` (strap badge) | Lowercase wordmark with a smile arc on a round badge. Logo: `blender/lib/textures/logos/squintscreen.svg` |
| tumblewump | `washer_dryer` (control strip) | Round porthole outline holding three tumbling bubbles, with a lowercase italic bold wordmark. Logo: `blender/lib/objects/washer_dryer/logos/tumblewump.svg` |
| Noodle Goblin | `floor_boxes` (noodle-cup case) | A green grinning cup with three grey steam curls beside a bold red two-line wordmark on a white rounded panel. Logo: `blender/lib/objects/floor_boxes/logos/noodle_goblin.svg` |
| Crunchums | `floor_boxes` (snack-bar wrappers) | A wobbly golden bar with a small smile beside a red rounded lowercase wordmark on a white oval. Logo: `blender/lib/objects/floor_boxes/logos/crunchums.svg` |
| Moonpouch | `hanging_bags` (tan hobo bag print) | An all-over repeat of small dark-brown crescent moons alternating with dots on tan; no letters or wordmark. Pattern painted in `textures.py`, no SVG. |
| Mage Night-Light | `media_hutch` | Red-brown box; a long silver sword with a glowing night-light bulb pommel; dark condensed title outlined in cream; "FOR 1-4 NAPPERS". |
| WHIZ-ISH | `media_hutch` | Small black rectangular publisher badge with white lettering. |
| Avaloaf | `media_hutch` | Grey stone-wall box; a bread loaf wearing a knight's helmet; gold engraved title. |
| One Desk Dungeon | `media_hutch` | Dark grey brick box; outlined white condensed title; a small flame. |
| Mascarpone | `media_hutch` | Dark red box, thin gold frame, gold script title. |
| Maiden's Quiche | `media_hutch` | Pale blue box; maroon band with a gold whisk emblem. |
| Dunno Now | `media_hutch` | Dark teal box; pale condensed title; a play-button circle. |
| Tragedy Hula-Hooper | `media_hutch` | Black box; nine small cartoon figures twirling coloured hoops. |
| SLOTHS | `media_hutch` | Black marbled box; big white title; a grey disc. |
| Sushi No-Party | `media_hutch` | Red wave-pattern box; a happy and a sulking rice ball; a round white chicken. |
| Tragic Maze | `media_hutch` | White box; tan square with a green maze; red "NAP OF THE YEAR" pawn trophy. |
| EXIT-ish: The Professor's Lost Keys | `media_hutch` | Dark upright box; candle glow and a planet over a desk; teal-framed title. |
| COSMOSS | `media_hutch` | White vertical lettering on a blue side band. |
| Deceptiscone | `media_hutch` | Dark red box; cream serif title; a scone. |
| Sidereal Confusion | `media_hutch` | Navy starfield; thin wide-spaced white title; a yellow "?". |
| Dixit Didn't | `media_hutch` | Tan-to-blue whimsical box; doorway, tower and rabbit silhouettes; ornate teal title. |
| Raptoast | `media_hutch` | Olive box; an explorer with binoculars; a green dinosaur holding toast. |
| Valiant Snores | `media_hutch` | Ochre framed box; two warriors in nightcaps; red shield title. |
| The Mild Unknown Tarot | `media_hutch` | Black deck box; rainbow ring behind a white mandala. |
| Quinoa | `media_hutch` | Cream box, red border; a pagoda silhouette; gold 3D title; a bowl of grains. |
| Mellow & Yawnzee | `media_hutch` | Yellow-green brush-stroke hills; red serif title. |
| Tigers & Euphemisms | `media_hutch` | Blue glazed-brick box; a striped cat relief; gold title. |
| Tiny Frowns (+ Villain-agers, Fortune Cookie) | `media_hutch` | Sky-and-meadow boxes; a frowning timber-frame house; wooden signboard title. |
| EGG | `media_hutch` | Red shield badge with white "EGG". |
| Spirit Eyeland / Greater Than Gnomes | `media_hutch` | Birch-ply organiser box with finger joints and an engraved arched title. |
| Battletuck / CATNAP | `media_hutch` | Black box; a stocky mech tucked under a red blanket; white title with a gold triangle; yellow badge. |
| Decent: Journeys in the Mildly Dim | `media_hutch` | Blue-teal box; a small adventurer; pale blue title. |
| Blood Bowl of Soup | `media_hutch` | Black box; an armoured helmet over a steaming soup bowl; white serif title. |
| Iconoclutter (Castle Splash, Bathtubgrounds, Level Snax, Lunch Break) | `media_hutch` | Dark purple/navy boxes; red slash behind an italic logo; one cartoon hero each. |
| Book spines (Sherapy, Slightly Dampened, Awakened Cods, Prune, House of Leeks, Teach Yourself SQUEAL...) | `media_hutch` | Plain coloured spines with invented titles, no author names. |
| Humdinger / Mini Mumbler | `cassette_player` | Orange ring holding a curly "H" whose uprights are two tape reels; orange bold italic model name. |
