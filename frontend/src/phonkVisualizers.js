// Phonk & Beat Visualizer Presets Library (714 Pro-Level Unique Curated FX Styles)
// 102 Distinct Presets for each of the 7 mood categories (Zero Duplicates).
// Each preset has distinct mathematical formulations, unique geometry, and animation behavior.

export const MOOD_VISUALIZER_INFO = {
  romantic: {
    title: 'Romantic & Love Beat Reactors',
    desc: 'Glowing heartbeat pulse, floating radiating hearts, cupid halos aur warm golden romance auras.',
    defaultId: 'romantic_auto'
  },
  sad: {
    title: 'Melancholy & Sad Beat Reactors',
    desc: 'Falling rain streaks, tear ripples on drops, shattered glass fragments aur cold dark noir ripples.',
    defaultId: 'sad_auto'
  },
  devotional: {
    title: 'Sacred Divine & Bhakti Beat Reactors',
    desc: 'Expanding golden chakra rays, Sudarshan chakra, temple diya flame pulse aur celestial aarti halos.',
    defaultId: 'devotional_auto'
  },
  lofi: {
    title: 'Cozy Lo-Fi & Chill Beat Reactors',
    desc: 'Rotating vinyl record grooves, vintage cassette spool, midnight star dust aur lavender waveforms.',
    defaultId: 'lofi_auto'
  },
  party: {
    title: 'Party & EDM Rave Beat Reactors',
    desc: 'Concert rave lasers, high-voltage plasma arcs, bass shockwaves aur 360° club strobe cannons.',
    defaultId: 'party_auto'
  },
  acoustic: {
    title: 'Acoustic & Indie Beat Reactors',
    desc: 'Analog sine oscilloscope ribbons, six-string guitar vibrations, campfire embers aur dewdrop ripples.',
    defaultId: 'acoustic_auto'
  },
  phonk: {
    title: 'Phonk, Drift & 808 Beat Reactors',
    desc: 'Trap Nation 3-lobe core, 360° radial reactor, Tokyo drift camera vibration, JDM gauges aur 3D synth grid.',
    defaultId: 'phonk_auto'
  }
};

export const PHONK_VISUALIZER_CATEGORIES = [
  { id: 'all', label: 'All Mood FX' },
  { id: 'romantic', label: 'Romantic / Love' },
  { id: 'sad', label: 'Sad / Dard' },
  { id: 'devotional', label: 'Bhakti / Devotional' },
  { id: 'lofi', label: 'Lo-Fi / Chill' },
  { id: 'party', label: 'Party / Rave' },
  { id: 'acoustic', label: 'Acoustic / Indie' },
  { id: 'phonk', label: 'Phonk / Drift' }
];

export const PHONK_VISUALIZER_PRESETS = [
  {
    id: 'romantic_auto',
    name: "\ud83c\udfb2 Auto Love Reactor (Random Shuffle)",
    category: 'romantic',
    family: 'romantic',
    badge: '🎲',
    desc: "Automatic selection: Love gaane ke rhythm ke anusaar random floating hearts & glow styles shuffle honge!",
    tag: "AUTO DEFAULT",
    col: "#f43f5e"
  },
  {
    id: 'romantic_heart',
    name: "\ud83d\udc96 Romantic Heart Pulse Core",
    category: 'romantic',
    family: 'romantic',
    badge: '💖',
    desc: "Center Circle Logo + Glowing Heartbeat Pulse + Radiating Floating Hearts on bass drops.",
    tag: "HEART CORE",
    col: "#f43f5e"
  },
  {
    id: 'romantic_cupid_halo',
    name: "\ud83d\udc98 Cupid's Arrow Halo Orbit",
    category: 'romantic',
    family: 'romantic',
    badge: '💘',
    desc: "Dual golden cupid arrows revolving around the center logo with sparkling stardust trail.",
    tag: "CUPID HALO",
    col: "#fb7185"
  },
  {
    id: 'romantic_rose_burst',
    name: "\ud83c\udf39 Rose Petal Bloom Shockwave",
    category: 'romantic',
    family: 'romantic',
    badge: '🌹',
    desc: "Concentric rose petal petals opening outward on every heavy bass beat with soft pink aura.",
    tag: "ROSE BLOOM",
    col: "#e11d48"
  },
  {
    id: 'romantic_dual_entangled',
    name: "\ud83d\udc91 Dual Entangled Hearts Pulse",
    category: 'romantic',
    family: 'romantic',
    badge: '💑',
    desc: "Twin interlocking glowing cardioid hearts beating in syncopated rhythm with audio sub-bass.",
    tag: "TWIN HEARTS",
    col: "#ec4899"
  },
  {
    id: 'romantic_starlight_lovers',
    name: "\u2728 Starlight Lovers Orbital Halo",
    category: 'romantic',
    family: 'romantic',
    badge: '✨',
    desc: "Gentle golden celestial constellation rings orbiting center emblem with warm twilight glow.",
    tag: "STARLIGHT",
    col: "#f59e0b"
  },
  {
    id: 'romantic_crimson_velvet',
    name: "\ud83c\udf77 Crimson Velvet Bass Echo",
    category: 'romantic',
    family: 'romantic',
    badge: '🍷',
    desc: "Deep crimson velvet wave rings echoing outwards like candlelit ripples on a romantic night.",
    tag: "VELVET WAVE",
    col: "#be123c"
  },
  {
    id: 'romantic_neon_ribbon',
    name: "\ud83c\udf80 Neon Ribbon Cardioid Wave",
    category: 'romantic',
    family: 'romantic',
    badge: '🎀',
    desc: "Silky smooth neon pink silk ribbons weaving in fluid mathematical figure-8 waves.",
    tag: "NEON RIBBON",
    col: "#f472b6"
  },
  {
    id: 'romantic_sunset_kiss',
    name: "\ud83c\udf05 Sunset Kiss Golden Halo",
    category: 'romantic',
    family: 'romantic',
    badge: '🌅',
    desc: "Warm golden hour sunbeam rays and soft lens flares pulsating smoothly on vocal hooks.",
    tag: "SUNSET KISS",
    col: "#f97316"
  },
  {
    id: 'romantic_ruby_gem',
    name: "\ud83d\udc8e Ruby Gem Heart Radiance",
    category: 'romantic',
    family: 'romantic',
    badge: '💎',
    desc: "Faceted 3D ruby heart geometry refracting crimson laser sparkles on kick drum hits.",
    tag: "RUBY GEM",
    col: "#e11d48"
  },
  {
    id: 'romantic_sakura_drift',
    name: "\ud83c\udf38 Sakura Blossom Particle Drift",
    category: 'romantic',
    family: 'romantic',
    badge: '🌸',
    desc: "Delicate Japanese cherry blossom petals swirling upwards in a gentle romantic wind.",
    tag: "SAKURA",
    col: "#fbcfe8"
  },
  {
    id: 'romantic_floating_fountain',
    name: "\u26f2 Floating Hearts Fountain",
    category: 'romantic',
    family: 'romantic',
    badge: '⛲',
    desc: "Continuous stream of miniature glowing neon hearts erupting from bottom to top of screen.",
    tag: "FOUNTAIN",
    col: "#ec4899"
  },
  {
    id: 'romantic_pink_pulsar',
    name: "\ud83d\udc93 Pink Neon Glow Pulsar",
    category: 'romantic',
    family: 'romantic',
    badge: '💓',
    desc: "High-contrast neon pink perimeter ring expanding with double-thump human heartbeat timing.",
    tag: "PULSAR",
    col: "#ff2d55"
  },
  {
    id: 'romantic_eternal_mobius',
    name: "\u267e\ufe0f Eternal Romance M\u00f6bius Ring",
    category: 'romantic',
    family: 'romantic',
    badge: '♾️',
    desc: "Twisted infinity loop glowing in gradient magenta, symbolizing endless romantic devotion.",
    tag: "INFINITY",
    col: "#d946ef"
  },
  {
    id: 'romantic_velvet_shockwave',
    name: "\ud83d\udca5 Velvet Heart Bass Drop",
    category: 'romantic',
    family: 'romantic',
    badge: '💥',
    desc: "Massive heart-shaped sonic blast wave bursting outwards when the romantic chorus drops.",
    tag: "BASS BURST",
    col: "#e11d48"
  },
  {
    id: 'romantic_warm_embrace',
    name: "\ud83e\udec2 Warm Embrace Orbit",
    category: 'romantic',
    family: 'romantic',
    badge: '🫂',
    desc: "Two protective glowing golden-rose rings shielding the center logo with soothing warmth.",
    tag: "EMBRACE",
    col: "#fbbf24"
  },
  {
    id: 'romantic_shooting_star',
    name: "\ud83d\udcab Shooting Star Romance Orbit",
    category: 'romantic',
    family: 'romantic',
    badge: '💫',
    desc: "Twin celestial shooting stars tracing an infinity love path around the emblem logo.",
    tag: "SHOOTING STAR",
    col: "#fb7185"
  },
  {
    id: 'romantic_twilight_fireflies',
    name: "\ud83c\udf1f Twilight Firefly Glow",
    category: 'romantic',
    family: 'romantic',
    badge: '🌟',
    desc: "Radiant glowing warm fireflies drifting upward on soft romantic melodies.",
    tag: "FIREFLIES",
    col: "#f43f5e"
  },
  {
    id: 'romantic_aurora_veil',
    name: "\ud83c\udf0c Aurora Borealis Love Veil",
    category: 'romantic',
    family: 'romantic',
    badge: '🌌',
    desc: "Shimmering magenta and emerald northern lights curtain undulating behind center portrait.",
    tag: "AURORA",
    col: "#ec4899"
  },
  {
    id: 'romantic_golden_constellation',
    name: "\ud83c\udf20 Lovers Constellation Star Map",
    category: 'romantic',
    family: 'romantic',
    badge: '🌠',
    desc: "Astrological heart constellation connecting glowing star nodes with golden lines.",
    tag: "CONSTELLATION",
    col: "#fbbf24"
  },
  {
    id: 'romantic_lotus_pond',
    name: "\ud83e\udeb7 Floating Water Lily Bloom",
    category: 'romantic',
    family: 'romantic',
    badge: '🪷',
    desc: "Pink water lilies blossoming outward with serene concentric pond ripples on beats.",
    tag: "WATER LILY",
    col: "#fda4af"
  },
  {
    id: 'romantic_crystal_chandelier',
    name: "\ud83d\udd2e Crystal Prism Love Chandelier",
    category: 'romantic',
    family: 'romantic',
    badge: '🔮',
    desc: "Sparkling chandelier light refracts faceted rainbow heart glimmers on bass drops.",
    tag: "CRYSTAL PRISM",
    col: "#f472b6"
  },
  {
    id: 'romantic_red_thread',
    name: "\ud83e\uddf5 Red Thread of Destiny",
    category: 'romantic',
    family: 'romantic',
    badge: '🧵',
    desc: "Glowing crimson thread looping between soulmates with delicate harmonic vibrations.",
    tag: "RED THREAD",
    col: "#e11d48"
  },
  {
    id: 'romantic_venus_orbit',
    name: "\ud83e\ude90 Venus Planetary Love Orbit",
    category: 'romantic',
    family: 'romantic',
    badge: '🪐',
    desc: "Celestial Venus orbital ring adorned with sparkling pastel stardust particles.",
    tag: "VENUS ORBIT",
    col: "#f43f5e"
  },
  {
    id: 'romantic_stained_glass',
    name: "\u26ea Stained Glass Cathedral Heart",
    category: 'romantic',
    family: 'romantic',
    badge: '⛪',
    desc: "Cathedral rose window geometry casting colorful divine romantic sunbeams.",
    tag: "STAINED GLASS",
    col: "#d946ef"
  },
  {
    id: 'romantic_paris_rain',
    name: "\u2602\ufe0f Paris Rain Romance Umbrellas",
    category: 'romantic',
    family: 'romantic',
    badge: '☂️',
    desc: "Soft lavender rain glistening on cobblestone streets with romantic caf\u00e9 glow.",
    tag: "PARIS RAIN",
    col: "#a855f7"
  },
  {
    id: 'romantic_mercury_rose',
    name: "\ud83e\uddea Liquid Mercury Love Rose",
    category: 'romantic',
    family: 'romantic',
    badge: '🧪',
    desc: "Reflective chrome metallic rose petals blooming smoothly to the bassline.",
    tag: "MERCURY ROSE",
    col: "#e2e8f0"
  },
  {
    id: 'romantic_holo_matrix',
    name: "\ud83c\udf10 Holographic Heart Matrix",
    category: 'romantic',
    family: 'romantic',
    badge: '🌐',
    desc: "3D wireframe cybernetic heart rotating seamlessly with neon pink grid.",
    tag: "HOLO HEART",
    col: "#ec4899"
  },
  {
    id: 'romantic_floral_mandala',
    name: "\ud83c\udff5\ufe0f Sacred Heart Floral Mandala",
    category: 'romantic',
    family: 'romantic',
    badge: '🏵️',
    desc: "Intricate romantic botanical mandala unfolding in sync with melodious vocals.",
    tag: "FLORAL MANDALA",
    col: "#f472b6"
  },
  {
    id: 'romantic_champagne_bubbles',
    name: "\ud83e\udd42 Champagne Bubble Effervescence",
    category: 'romantic',
    family: 'romantic',
    badge: '🥂',
    desc: "Sparkling golden champagne bubbles floating gently upwards around center avatar.",
    tag: "CHAMPAGNE",
    col: "#facc15"
  },
  {
    id: 'romantic_lens_flare',
    name: "\u2600\ufe0f Golden Hour Lens Flare",
    category: 'romantic',
    family: 'romantic',
    badge: '☀️',
    desc: "Cinematic anamorphic horizontal golden flares pulsing on vocal chorus peaks.",
    tag: "LENS FLARE",
    col: "#f59e0b"
  },
  {
    id: 'romantic_swan_feather',
    name: "\ud83e\udda2 Swan Lake Feather Orbit",
    category: 'romantic',
    family: 'romantic',
    badge: '🦢',
    desc: "Pure white and pink down feathers drifting peacefully in circular lake ripples.",
    tag: "SWAN FEATHER",
    col: "#f8fafc"
  },
  {
    id: 'romantic_music_box',
    name: "\ud83c\udfbc Music Box Waltz Ring",
    category: 'romantic',
    family: 'romantic',
    badge: '🎼',
    desc: "Delicate vintage clockwork gear rings revolving to gentle romantic waltz notes.",
    tag: "MUSIC BOX",
    col: "#fbbf24"
  },
  {
    id: 'romantic_ecg_pulse',
    name: "\ud83d\udcc8 Heartbeat ECG Line Pulse",
    category: 'romantic',
    family: 'romantic',
    badge: '📈',
    desc: "High-tech cardiogram pulse line tracing romantic surges on heavy kick drum hits.",
    tag: "HEARTBEAT ECG",
    col: "#ff2d55"
  },
  {
    id: 'romantic_velvet_knot',
    name: "\ud83e\udea2 Velvet Ribbon Love Knot",
    category: 'romantic',
    family: 'romantic',
    badge: '🪢',
    desc: "Interlocking Celtic knot ribbons in ruby velvet glowing with eternal affection.",
    tag: "LOVE KNOT",
    col: "#be123c"
  },
  {
    id: 'romantic_silk_satin',
    name: "\ud83e\udde3 Silk Satin Wave Ribbon",
    category: 'romantic',
    family: 'romantic',
    badge: '🧣',
    desc: "Undulating satin fabric sheets floating weightlessly in romantic breeze.",
    tag: "SATIN WAVE",
    col: "#f472b6"
  },
  {
    id: 'romantic_diamond_bloom',
    name: "\ud83d\udc8e Diamond Facet Bloom Core",
    category: 'romantic',
    family: 'romantic',
    badge: '💎',
    desc: "Brilliant-cut diamond contours dispersing spectral rainbow refractions on beats.",
    tag: "DIAMOND BLOOM",
    col: "#38bdf8"
  },
  {
    id: 'romantic_beach_horizon',
    name: "\ud83c\udfd6\ufe0f Sunset Beach Horizon Glow",
    category: 'romantic',
    family: 'romantic',
    badge: '🏖️',
    desc: "Gentle ocean shoreline waves lapping under a fiery romantic golden sunset.",
    tag: "BEACH SUNSET",
    col: "#fb923c"
  },
  {
    id: 'romantic_sakura_cyclone',
    name: "\ud83c\udf2a\ufe0f Cherry Blossom Cyclone",
    category: 'romantic',
    family: 'romantic',
    badge: '🌪️',
    desc: "Dense vortex of pink sakura petals swirling dramatically around the center logo.",
    tag: "SAKURA VORTEX",
    col: "#f472b6"
  },
  {
    id: 'romantic_jasmine_garland',
    name: "\ud83c\udf3c Jasmine Garland Holy Halo",
    category: 'romantic',
    family: 'romantic',
    badge: '🌼',
    desc: "Fragrant white jasmine flowers strung into a sacred romantic circular garland.",
    tag: "JASMINE HALO",
    col: "#fef08a"
  },
  {
    id: 'romantic_twin_moons',
    name: "\ud83c\udf15 Celestial Twin Moons Orbit",
    category: 'romantic',
    family: 'romantic',
    badge: '🌕',
    desc: "Two gentle glowing moons reflecting silver romantic moonlight onto calm waters.",
    tag: "TWIN MOONS",
    col: "#e0e7ff"
  },
  {
    id: 'romantic_magnolia_drift',
    name: "\ud83c\udf3a Magnolia Blossom Petal Drift",
    category: 'romantic',
    family: 'romantic',
    badge: '🌺',
    desc: "Broad velvet magnolia petals falling slowly with gentle acoustic resonance.",
    tag: "MAGNOLIA",
    col: "#fda4af"
  },
  {
    id: 'romantic_letter_ink',
    name: "\ud83d\udc8c Love Letter Ink Drops",
    category: 'romantic',
    family: 'romantic',
    badge: '💌',
    desc: "Handwritten calligraphy ink ripples blooming across parchment on piano notes.",
    tag: "LETTER INK",
    col: "#be185d"
  },
  {
    id: 'romantic_balcony_arch',
    name: "\ud83c\udfdb\ufe0f Moonlit Balcony Arch Glow",
    category: 'romantic',
    family: 'romantic',
    badge: '🏛️',
    desc: "Italian marble balcony silhouette framing a starry romantic midnight sky.",
    tag: "BALCONY ARCH",
    col: "#cbd5e1"
  },
  {
    id: 'romantic_laser_cardioid',
    name: "\u26a1 Ruby Red Laser Cardioid",
    category: 'romantic',
    family: 'romantic',
    badge: '⚡',
    desc: "High-precision laser cardioid math curve drawn in real-time with sub-bass.",
    tag: "LASER CARDIOID",
    col: "#ef4444"
  },
  {
    id: 'romantic_serenader_wave',
    name: "\ud83c\udfbb Midnight Serenader Wave",
    category: 'romantic',
    family: 'romantic',
    badge: '🎻',
    desc: "Tender violin vibrato harmonic curves dancing gracefully around the emblem.",
    tag: "SERENADE WAVE",
    col: "#fb7185"
  },
  {
    id: 'romantic_candlelit_aura',
    name: "\ud83d\udd6f\ufe0f Candlelit Table Aura",
    category: 'romantic',
    family: 'romantic',
    badge: '🕯️',
    desc: "Warm intimate candlelight flickering with golden amber romantic warmth.",
    tag: "CANDLE AURA",
    col: "#f59e0b"
  },
  {
    id: 'romantic_lovers_spiral',
    name: "\ud83c\udf00 Star-Crossed Lovers Spiral",
    category: 'romantic',
    family: 'romantic',
    badge: '🌀',
    desc: "Galactic spiral arms woven of stardust embracing the center avatar portrait.",
    tag: "STAR SPIRAL",
    col: "#c084fc"
  },
  {
    id: 'romantic_pink_quartz',
    name: "\ud83d\udd2e Pink Quartz Crystal Halo",
    category: 'romantic',
    family: 'romantic',
    badge: '🔮',
    desc: "Rose quartz mineral crystals radiating soothing, unconditional love energy.",
    tag: "PINK QUARTZ",
    col: "#f472b6"
  },
  {
    id: 'romantic_meadow_breeze',
    name: "\ud83c\udf3e Lavender Meadow Breeze",
    category: 'romantic',
    family: 'romantic',
    badge: '🌾',
    desc: "Rolling purple lavender fields waving gently under soft golden hour light.",
    tag: "LAVENDER MEADOW",
    col: "#a855f7"
  },
  {
    id: 'romantic_coral_reef',
    name: "\ud83e\udeb8 Coral Reef Heart Bubble",
    category: 'romantic',
    family: 'romantic',
    badge: '🪸',
    desc: "Bioluminescent deep-sea heart bubbles rising peacefully through turquoise water.",
    tag: "CORAL BUBBLE",
    col: "#2dd4bf"
  },
  {
    id: 'romantic_filigree_locket',
    name: "\ud83d\udcff Golden Filigree Locket",
    category: 'romantic',
    family: 'romantic',
    badge: '📿',
    desc: "Vintage royal gold filigree ornamentation pulsating around the center photo.",
    tag: "FILIGREE LOCKET",
    col: "#eab308"
  },
  {
    id: 'romantic_silhouette_dance',
    name: "\ud83d\udc83 Twilight Silhouette Dance",
    category: 'romantic',
    family: 'romantic',
    badge: '💃',
    desc: "Graceful dancing silhouette ripples moving in harmony with the romantic beat.",
    tag: "DANCE SILHOUETTE",
    col: "#ec4899"
  },
  {
    id: 'romantic_amethyst_geode',
    name: "\ud83d\udc8e Amethyst Heart Geode",
    category: 'romantic',
    family: 'romantic',
    badge: '💎',
    desc: "Deep purple crystal geode cave reflecting dazzling violet light sparks.",
    tag: "AMETHYST GEODE",
    col: "#9333ea"
  },
  {
    id: 'romantic_cloud_fluff',
    name: "\u2601\ufe0f Sunset Cloud Fluff Horizon",
    category: 'romantic',
    family: 'romantic',
    badge: '☁️',
    desc: "Dreamy cotton-candy pink clouds floating along the lower third on vocals.",
    tag: "CLOUD FLUFF",
    col: "#fbcfe8"
  },
  {
    id: 'romantic_bokeh_circles',
    name: "\u2b55 Soft Bokeh Blur Circles",
    category: 'romantic',
    family: 'romantic',
    badge: '⭕',
    desc: "Creamy out-of-focus romantic light orbs pulsing gently in the background.",
    tag: "BOKEH CIRCLES",
    col: "#f43f5e"
  },
  {
    id: 'romantic_peach_blossom',
    name: "\ud83c\udf51 Peach Blossom Flutter",
    category: 'romantic',
    family: 'romantic',
    badge: '🍑',
    desc: "Soft pastel peach petals fluttering like butterflies around the center logo.",
    tag: "PEACH BLOSSOM",
    col: "#fb923c"
  },
  {
    id: 'romantic_willow_arch',
    name: "\ud83c\udf3f Whispering Willow Arch",
    category: 'romantic',
    family: 'romantic',
    badge: '🌿',
    desc: "Gentle weeping willow branches creating an intimate canopy for lovers.",
    tag: "WILLOW ARCH",
    col: "#4ade80"
  },
  {
    id: 'romantic_petal_rainstorm',
    name: "\ud83c\udf27\ufe0f Crimson Petal Rainstorm",
    category: 'romantic',
    family: 'romantic',
    badge: '🌧️',
    desc: "Dramatic shower of velvety red rose petals cascading across the screen.",
    tag: "PETAL STORM",
    col: "#be123c"
  },
  {
    id: 'romantic_angel_wings',
    name: "\ud83e\udebd Celestial Eros Angel Wings",
    category: 'romantic',
    family: 'romantic',
    badge: '🪽',
    desc: "Glowing feathered angel wings expanding outwards on soaring romantic chords.",
    tag: "EROS WINGS",
    col: "#ffffff"
  },
  {
    id: 'romantic_velvet_cushion',
    name: "\ud83d\udecb\ufe0f Velvet Cushion Bass Thump",
    category: 'romantic',
    family: 'romantic',
    badge: '🛋️',
    desc: "Plush luxury velvet ripple contours absorbing and releasing low-end sub-bass.",
    tag: "VELVET THUMP",
    col: "#9f1239"
  },
  {
    id: 'romantic_lovebird_song',
    name: "\ud83e\udd9c Lovebird Song Harmonic Wave",
    category: 'romantic',
    family: 'romantic',
    badge: '🦜',
    desc: "Twin chirping lovebird note ripples tracing intertwining harmonic arcs.",
    tag: "LOVEBIRD SONG",
    col: "#38bdf8"
  },
  {
    id: 'romantic_opalescent_shimmer',
    name: "\u2728 Opalescent Heart Shimmer",
    category: 'romantic',
    family: 'romantic',
    badge: '✨',
    desc: "Mother-of-pearl iridescent gleams shifting colors between pearl, rose, and cyan.",
    tag: "OPAL SHIMMER",
    col: "#e0e7ff"
  },
  {
    id: 'romantic_chariot_rose',
    name: "\ud83c\udfa0 Golden Chariot Rose Path",
    category: 'romantic',
    family: 'romantic',
    badge: '🎠',
    desc: "Golden royal carpet adorned with scattered rose petals and fairy sparkles.",
    tag: "CHARIOT ROSE",
    col: "#eab308"
  },
  {
    id: 'romantic_gondola_ripple',
    name: "\ud83d\udea3 Venetian Gondola Ripple",
    category: 'romantic',
    family: 'romantic',
    badge: '🚣',
    desc: "Tranquil midnight canal reflections with gentle oar ripples and warm streetlights.",
    tag: "GONDOLA RIPPLE",
    col: "#0284c7"
  },
  {
    id: 'romantic_neon_sign',
    name: "\ud83e\udea7 Neon Lovers Motel Sign",
    category: 'romantic',
    family: 'romantic',
    badge: '🪧',
    desc: "Retro 80s pink neon script humming gently with romantic vintage nostalgia.",
    tag: "NEON SIGN",
    col: "#ec4899"
  },
  {
    id: 'romantic_joy_tear',
    name: "\ud83d\udca7 Ruby Tear of Joy Drop",
    category: 'romantic',
    family: 'romantic',
    badge: '💧',
    desc: "A single radiant ruby drop creating expanding concentric ripples of happiness.",
    tag: "JOY TEAR",
    col: "#e11d48"
  },
  {
    id: 'romantic_vintage_lace',
    name: "\ud83d\udd78\ufe0f Vintage Lace Floral Mandala",
    category: 'romantic',
    family: 'romantic',
    badge: '🕸️',
    desc: "Delicate antique Victorian lace pattern framing the center logo with elegance.",
    tag: "VINTAGE LACE",
    col: "#f8fafc"
  },
  {
    id: 'romantic_butterfly_kiss',
    name: "\ud83e\udd8b Butterfly Kiss Flutter Aura",
    category: 'romantic',
    family: 'romantic',
    badge: '🦋',
    desc: "Swarm of radiant neon butterflies fluttering around the center emblem.",
    tag: "BUTTERFLY KISS",
    col: "#c084fc"
  },
  {
    id: 'romantic_starlit_promenade',
    name: "\ud83d\udc60 Starlit Promenade Light",
    category: 'romantic',
    family: 'romantic',
    badge: '👠',
    desc: "Romantic moonlit pathway lined with twinkling lanterns and gentle rose auras.",
    tag: "PROMENADE",
    col: "#fbbf24"
  },
  {
    id: 'romantic_vow_ring',
    name: "\ud83d\udc8d Golden Wedding Ring Vow",
    category: 'romantic',
    family: 'romantic',
    badge: '💍',
    desc: "Twin interlocked diamond wedding bands radiating eternal fidelity and love.",
    tag: "VOW RING",
    col: "#facc15"
  },
  {
    id: 'romantic_flame_passion',
    name: "\ud83d\udd25 Eternal Flame of Passion",
    category: 'romantic',
    family: 'romantic',
    badge: '🔥',
    desc: "Fierce yet tender crimson flame dancing in rhythm with emotional drum beats.",
    tag: "PASSION FLAME",
    col: "#ef4444"
  },
  {
    id: 'romantic_orchid_halo',
    name: "\ud83e\udebb Orchid Bloom Electric Halo",
    category: 'romantic',
    family: 'romantic',
    badge: '🪻',
    desc: "Exotic royal purple orchid petals emitting faint bioluminescent sparks.",
    tag: "ORCHID HALO",
    col: "#a855f7"
  },
  {
    id: 'romantic_garden_maze',
    name: "\ud83c\udf3f Midnight Rose Garden Maze",
    category: 'romantic',
    family: 'romantic',
    badge: '🌿',
    desc: "Intricate Victorian hedge maze blooming with hidden glowing crimson roses.",
    tag: "GARDEN MAZE",
    col: "#15803d"
  },
  {
    id: 'romantic_champagne_splash',
    name: "\ud83c\udf7e Pink Champagne Foam Splash",
    category: 'romantic',
    family: 'romantic',
    badge: '🍾',
    desc: "Festive pink champagne splash freezing in slow-motion into crystalline beads.",
    tag: "CHAMPAGNE SPLASH",
    col: "#f472b6"
  },
  {
    id: 'romantic_guitar_serenade',
    name: "\ud83c\udfb8 Sweet Serenade Guitar Ripple",
    category: 'romantic',
    family: 'romantic',
    badge: '🎸',
    desc: "Nylon string acoustic vibrato creating soft circular waves on vocal notes.",
    tag: "GUITAR SERENADE",
    col: "#ea580c"
  },
  {
    id: 'romantic_midnight_sky',
    name: "\ud83c\udf0c Velvet Midnight Sky Dust",
    category: 'romantic',
    family: 'romantic',
    badge: '🌌',
    desc: "Deep indigo night sky filled with millions of sparkling romantic stars.",
    tag: "VELVET SKY",
    col: "#312e81"
  },
  {
    id: 'romantic_sailboat_wake',
    name: "\u26f5 Golden Sunset Sailboat Wake",
    category: 'romantic',
    family: 'romantic',
    badge: '⛵',
    desc: "Peaceful sailboat gliding through golden waters leaving shimmering ripples.",
    tag: "SAILBOAT WAKE",
    col: "#f59e0b"
  },
  {
    id: 'romantic_moonlit_lagoon',
    name: "\ud83c\udfdd\ufe0f Moonlit Lagoon Water Lily",
    category: 'romantic',
    family: 'romantic',
    badge: '🏝️',
    desc: "Secluded tropical lagoon with glowing water lilies and soft ocean breeze.",
    tag: "LAGOON LILY",
    col: "#06b6d4"
  },
  {
    id: 'romantic_cupid_lyre',
    name: "\ud83e\ude95 Celestial Cupid's Lyre Chord",
    category: 'romantic',
    family: 'romantic',
    badge: '🪕',
    desc: "Golden heavenly harp strings vibrating with harmonic celestial sound waves.",
    tag: "CUPID LYRE",
    col: "#eab308"
  },
  {
    id: 'romantic_satin_canopy',
    name: "\ud83d\udecf\ufe0f Crimson Satin Bed Canopy",
    category: 'romantic',
    family: 'romantic',
    badge: '🛏️',
    desc: "Flowing royal crimson drapery billowing gently around the center portrait.",
    tag: "SATIN CANOPY",
    col: "#be123c"
  },
  {
    id: 'romantic_tiara_gem',
    name: "\ud83d\udc51 Sparkling Tiara Gem Halo",
    category: 'romantic',
    family: 'romantic',
    badge: '👑',
    desc: "Princess diamond tiara radiating brilliant crystalline sparkles on drops.",
    tag: "TIARA HALO",
    col: "#f8fafc"
  },
  {
    id: 'romantic_lantern_wish',
    name: "\ud83c\udfee Floating Lantern Love Wish",
    category: 'romantic',
    family: 'romantic',
    badge: '🏮',
    desc: "Warm glowing paper lanterns ascending gracefully into the starry night sky.",
    tag: "LANTERN WISH",
    col: "#f97316"
  },
  {
    id: 'romantic_rose_gold_spiral',
    name: "\ud83c\udf00 Rose Gold Spiral Geometry",
    category: 'romantic',
    family: 'romantic',
    badge: '🌀',
    desc: "Hypnotic logarithmic golden spiral rendered in lustrous metallic rose gold.",
    tag: "ROSE GOLD SPIRAL",
    col: "#fb7185"
  },
  {
    id: 'romantic_solar_flare',
    name: "\ud83d\udca5 Passionate Kiss Solar Flare",
    category: 'romantic',
    family: 'romantic',
    badge: '💥',
    desc: "Dazzling solar prominence arc erupting behind the logo on chorus climax.",
    tag: "SOLAR FLARE",
    col: "#f59e0b"
  },
  {
    id: 'romantic_honey_core',
    name: "\ud83c\udf6f Honeycomb Honey Love Core",
    category: 'romantic',
    family: 'romantic',
    badge: '🍯',
    desc: "Golden geometric honeycomb cells dripping with sweet golden nectar light.",
    tag: "HONEY CORE",
    col: "#eab308"
  },
  {
    id: 'romantic_dewdrop_rosebud',
    name: "\ud83d\udca7 Dewdrop on Rosebud Ripple",
    category: 'romantic',
    family: 'romantic',
    badge: '💧',
    desc: "Crystal-clear morning dewdrop magnifying vibrant red rose petals.",
    tag: "ROSE DEWDROP",
    col: "#f43f5e"
  },
  {
    id: 'romantic_cotton_candy',
    name: "\ud83c\udf6d Cotton Candy Sunset Swirl",
    category: 'romantic',
    family: 'romantic',
    badge: '🍭',
    desc: "Playful swirls of pastel pink and sky blue sugar clouds dancing in air.",
    tag: "COTTON CANDY",
    col: "#f472b6"
  },
  {
    id: 'romantic_fairy_dust',
    name: "\ud83e\uddda Enchanted Forest Fairy Dust",
    category: 'romantic',
    family: 'romantic',
    badge: '🧚',
    desc: "Magical glittering green and gold fairy dust trails circling with joy.",
    tag: "FAIRY DUST",
    col: "#84cc16"
  },
  {
    id: 'romantic_twin_swan',
    name: "\ud83e\udda2 Twin Swan Heart Reflection",
    category: 'romantic',
    family: 'romantic',
    badge: '🦢',
    desc: "Pair of graceful swans forming a perfect heart silhouette on still water.",
    tag: "TWIN SWAN",
    col: "#f8fafc"
  },
  {
    id: 'romantic_scarlet_silk',
    name: "\ud83d\udc83 Scarlet Silk Dancer Swirl",
    category: 'romantic',
    family: 'romantic',
    badge: '💃',
    desc: "Flamenco dancer's scarlet silk skirt spinning in energetic romantic passion.",
    tag: "SCARLET SILK",
    col: "#dc2626"
  },
  {
    id: 'romantic_diamond_solitaire',
    name: "\ud83d\udc8d Sparkling Diamond Solitaire",
    category: 'romantic',
    family: 'romantic',
    badge: '💍',
    desc: "Single massive engagement diamond casting intense spectral prism flashes.",
    tag: "SOLITAIRE",
    col: "#e0e7ff"
  },
  {
    id: 'romantic_harp_halo',
    name: "\ud83e\ude88 Golden Harp Melodic Halo",
    category: 'romantic',
    family: 'romantic',
    badge: '🪈',
    desc: "Angelic harp harmonics creating a soothing golden circle of tranquility.",
    tag: "HARP HALO",
    col: "#facc15"
  },
  {
    id: 'romantic_star_cluster',
    name: "\u2728 Pink Diamond Star Cluster",
    category: 'romantic',
    family: 'romantic',
    badge: '✨',
    desc: "Dense cluster of pink diamond stars twinkling brightly to the melody.",
    tag: "STAR CLUSTER",
    col: "#ec4899"
  },
  {
    id: 'romantic_quartz_vibe',
    name: "\ud83d\udd2e Rose Quartz Loving Vibration",
    category: 'romantic',
    family: 'romantic',
    badge: '🔮',
    desc: "Gentle resonant harmonic field washing over the screen with tenderness.",
    tag: "QUARTZ VIBE",
    col: "#fda4af"
  },
  {
    id: 'romantic_pearl_halo',
    name: "\ud83e\uddaa Celestial Aphrodite Pearl",
    category: 'romantic',
    family: 'romantic',
    badge: '🦪',
    desc: "Lustrous iridescent ocean pearl resting in an open seashell with rainbow glow.",
    tag: "PEARL HALO",
    col: "#f1f5f9"
  },
  {
    id: 'romantic_rendezvous',
    name: "\ud83d\udd76\ufe0f Midnight Rendezvous Shadow",
    category: 'romantic',
    family: 'romantic',
    badge: '🕶️',
    desc: "Mysterious lovers' meeting under vintage streetlight with soft rain mist.",
    tag: "RENDEZVOUS",
    col: "#64748b"
  },
  {
    id: 'romantic_fireplace',
    name: "\ud83e\udeb5 Warm Fireplace Hearth Glow",
    category: 'romantic',
    family: 'romantic',
    badge: '🪵',
    desc: "Cozy cabin stone fireplace crackling with warm amber romantic embers.",
    tag: "FIREPLACE",
    col: "#ea580c"
  },
  {
    id: 'romantic_golden_ribbons',
    name: "\ud83c\udf97\ufe0f Sweet Embrace Golden Ribbons",
    category: 'romantic',
    family: 'romantic',
    badge: '🎗️',
    desc: "Twin golden satin ribbons wrapping gently around the center emblem logo.",
    tag: "GOLDEN RIBBONS",
    col: "#fbbf24"
  },
  {
    id: 'romantic_ocean_wave',
    name: "\ud83c\udf0a Endless Romance Ocean Wave",
    category: 'romantic',
    family: 'romantic',
    badge: '🌊',
    desc: "Gentle cresting ocean waves reflecting soft lavender sunset colors.",
    tag: "OCEAN WAVE",
    col: "#38bdf8"
  },
  {
    id: 'romantic_lovers_leap',
    name: "\ud83c\udf20 Lovers Leap Cosmic Starfield",
    category: 'romantic',
    family: 'romantic',
    badge: '🌠',
    desc: "Accelerating hyperspace star tunnel leading to an eternity of togetherness.",
    tag: "LOVERS LEAP",
    col: "#a855f7"
  },
  {
    id: 'romantic_infinite_devotion',
    name: "\ud83d\udc96 Infinite Devotion Heart Core",
    category: 'romantic',
    family: 'romantic',
    badge: '💖',
    desc: "Concentric multi-layered neon heart halos expanding infinitely on final chord.",
    tag: "INFINITE DEVOTION",
    col: "#f43f5e"
  },
  {
    id: 'sad_auto',
    name: "\ud83c\udfb2 Auto Sad Reactor (Random Shuffle)",
    category: 'sad',
    family: 'sad',
    badge: '🎲',
    desc: "Automatic selection: Dard bhare gaane ke liye atmospheric rain & broken glass randomly match honge!",
    tag: "AUTO DEFAULT",
    col: "#38bdf8"
  },
  {
    id: 'sad_rain',
    name: "\ud83d\udc94 Melancholy Rain Drop Core",
    category: 'sad',
    family: 'sad',
    badge: '💔',
    desc: "Center Circle Logo + Atmospheric Rain Streaks + Tear Ripples on Bass Drops.",
    tag: "RAIN CORE",
    col: "#38bdf8"
  },
  {
    id: 'sad_broken_heart',
    name: "\ud83d\udc94 Shattered Heart Glass Shards",
    category: 'sad',
    family: 'sad',
    badge: '💔',
    desc: "Center heart shape fracturing into sharp crystalline shards on emotional vocal peaks.",
    tag: "BROKEN GLASS",
    col: "#94a3b8"
  },
  {
    id: 'sad_tear_stream',
    name: "\ud83d\udca7 Midnight Tear Drops Stream",
    category: 'sad',
    family: 'sad',
    badge: '💧',
    desc: "Slowly falling luminous blue tear streaks creating circular water ripples on bass impacts.",
    tag: "TEARS",
    col: "#60a5fa"
  },
  {
    id: 'sad_rainy_window',
    name: "\ud83e\ude9f Rainy Window Pane Droplets",
    category: 'sad',
    family: 'sad',
    badge: '🪟',
    desc: "Cinematic rain droplets racing down glass with realistic refraction and moody streetlamp glow.",
    tag: "WINDOW RAIN",
    col: "#0284c7"
  },
  {
    id: 'sad_lonely_fog',
    name: "\ud83c\udf2b\ufe0f Lonely Cold Fog Dispersion",
    category: 'sad',
    family: 'sad',
    badge: '🌫️',
    desc: "Dense cold mist and drifting fog clouds pulsing slowly around the solitary center avatar.",
    tag: "FOG MIST",
    col: "#64748b"
  },
  {
    id: 'sad_ice_shards',
    name: "\ud83e\uddca Frozen Tears Ice Shard Pulse",
    category: 'sad',
    family: 'sad',
    badge: '🧊',
    desc: "Sharp cyan frost crystals forming and cracking outward on heavy melancholy drum beats.",
    tag: "FROST ICE",
    col: "#22d3ee"
  },
  {
    id: 'sad_solitary_ripple',
    name: "\ud83c\udf0a Solitary Lake Bass Ripple",
    category: 'sad',
    family: 'sad',
    badge: '🌊',
    desc: "Deep indigo water ripples expanding across a desolate midnight lake surface.",
    tag: "WATER RIPPLE",
    col: "#3b82f6"
  },
  {
    id: 'sad_noir_shadow',
    name: "\ud83d\udda4 Noir Shadow Drizzle Pulse",
    category: 'sad',
    family: 'sad',
    badge: '🖤',
    desc: "High-contrast monochrome black & white vignette with sharp diagonal rain streaks.",
    tag: "NOIR MONO",
    col: "#e2e8f0"
  },
  {
    id: 'sad_withered_petal',
    name: "\ud83e\udd40 Withered Black Rose Drift",
    category: 'sad',
    family: 'sad',
    badge: '🥀',
    desc: "Dried dark rose petals falling in slow-motion, symbolizing lost love and memories.",
    tag: "WITHERED",
    col: "#9f1239"
  },
  {
    id: 'sad_heavy_downpour',
    name: "\u26c8\ufe0f Heavy Downpour Thunder Pulse",
    category: 'sad',
    family: 'sad',
    badge: '⛈️',
    desc: "Violent torrential rain streaks with brief subtle lightning flashes on thunderous sub-bass drops.",
    tag: "DOWNPOUR",
    col: "#0ea5e9"
  },
  {
    id: 'sad_gray_halo',
    name: "\ud83c\udf2a\ufe0f Distant Memory Gray Horizon",
    category: 'sad',
    family: 'sad',
    badge: '🌪️',
    desc: "Somber ash-gray frequency ring slowly dissipating into the dark atmospheric background.",
    tag: "GRAY HORIZON",
    col: "#475569"
  },
  {
    id: 'sad_bleeding_ink',
    name: "\ud83d\udd8b\ufe0f Bleeding Indigo Ink Vignette",
    category: 'sad',
    family: 'sad',
    badge: '🖋️',
    desc: "Dark blue watercolor ink stains blooming organically around the center emblem on bass notes.",
    tag: "INK BLEED",
    col: "#4338ca"
  },
  {
    id: 'sad_somber_echo',
    name: "\ud83d\udd15 Somber Silence Sonic Echo",
    category: 'sad',
    family: 'sad',
    badge: '🔕',
    desc: "Minimalist thin cyan perimeter line vibrating gently with sub-bass like a faint heartbeat monitor.",
    tag: "MINIMAL ECHO",
    col: "#38bdf8"
  },
  {
    id: 'sad_abandoned_lighthouse',
    name: "\ud83d\uddfc Distant Foggy Lighthouse",
    category: 'sad',
    family: 'sad',
    badge: '🗼',
    desc: "Faint sweeping beacon cutting through dense ocean fog and somber rain.",
    tag: "LIGHTHOUSE",
    col: "#64748b"
  },
  {
    id: 'sad_echoing_piano_chords',
    name: "\ud83c\udfb9 Echoing Broken Piano Waveform",
    category: 'sad',
    family: 'sad',
    badge: '🎹',
    desc: "Minor chord harmonic sound waves disintegrating into rain drops.",
    tag: "PIANO WAVE",
    col: "#94a3b8"
  },
  {
    id: 'sad_wilted_autumn_leaves',
    name: "\ud83c\udf42 Falling Autumn Dead Leaves",
    category: 'sad',
    family: 'sad',
    badge: '🍂',
    desc: "Crisp amber-brown dried leaves swirling downward in cold November breeze.",
    tag: "AUTUMN DRIFT",
    col: "#78716c"
  },
  {
    id: 'sad_shattered_clock',
    name: "\ud83d\udd70\ufe0f Fractured Timepiece Shards",
    category: 'sad',
    family: 'sad',
    badge: '🕰️',
    desc: "Broken watch gears and glass ticking in reverse with hollow bass resonance.",
    tag: "BROKEN TIME",
    col: "#475569"
  },
  {
    id: 'sad_candle_in_wind',
    name: "\ud83d\udd6f\ufe0f Flickering Candle in Wind",
    category: 'sad',
    family: 'sad',
    badge: '🕯️',
    desc: "Fragile single wax candle flame struggling against heavy rain drops on bass pulse.",
    tag: "FLICKER",
    col: "#cbd5e1"
  },
  {
    id: 'sad_ocean_abyss',
    name: "\ud83c\udf0a Midnight Ocean Abyss Wave",
    category: 'sad',
    family: 'sad',
    badge: '🌊',
    desc: "Dark midnight oceanic swell rising and falling with deep melancholic sub-bass.",
    tag: "DEEP ABYSS",
    col: "#38bdf8"
  },
  {
    id: 'sad_empty_bench',
    name: "\ud83e\ude91 Empty Park Bench Silhouette",
    category: 'sad',
    family: 'sad',
    badge: '🪑',
    desc: "Solitary wet wooden bench under a dim amber streetlamp in deserted midnight park.",
    tag: "EMPTY BENCH",
    col: "#94a3b8"
  },
  {
    id: 'sad_train_station',
    name: "\ud83d\ude89 Desolate Train Station Mist",
    category: 'sad',
    family: 'sad',
    badge: '🚉',
    desc: "Cold railway tracks disappearing into misty darkness as departing train whistle fades.",
    tag: "TRAIN STATION",
    col: "#64748b"
  },
  {
    id: 'sad_rusted_cage',
    name: "\u26d3\ufe0f Rusted Iron Cage Pulse",
    category: 'sad',
    family: 'sad',
    badge: '⛓️',
    desc: "Heavy rusted chain links clinking against iron bars on deep melancholy sub-bass.",
    tag: "IRON CAGE",
    col: "#78716c"
  },
  {
    id: 'sad_photo_burn',
    name: "\ud83d\udd25 Forgotten Photograph Burn",
    category: 'sad',
    family: 'sad',
    badge: '🔥',
    desc: "Curling black edges of burning vintage photo turning into floating smoke ash.",
    tag: "PHOTO BURN",
    col: "#f97316"
  },
  {
    id: 'sad_umbrella_blur',
    name: "\u2602\ufe0f Black Umbrella Rainy Blur",
    category: 'sad',
    family: 'sad',
    badge: '☂️',
    desc: "Lone black umbrella walking away into dark blurry city bokeh and puddles.",
    tag: "UMBRELLA BLUR",
    col: "#475569"
  },
  {
    id: 'sad_faded_memory',
    name: "\ud83d\udcfc Faded Childhood Memory Haze",
    category: 'sad',
    family: 'sad',
    badge: '📼',
    desc: "Grainy sepia wash and washed-out colors dissolving like vanishing memories.",
    tag: "FADED MEMORY",
    col: "#a8a29e"
  },
  {
    id: 'sad_snow_footsteps',
    name: "\u2744\ufe0f Vanishing Footsteps in Snow",
    category: 'sad',
    family: 'sad',
    badge: '❄️',
    desc: "Slowly filling footprints on a silent frozen path in a deserted winter forest.",
    tag: "SNOW TRACKS",
    col: "#e2e8f0"
  },
  {
    id: 'sad_mirror_fractures',
    name: "\ud83e\ude9e Shattered Mirror Fractures",
    category: 'sad',
    family: 'sad',
    badge: '🪞',
    desc: "Cracked silver mirror glass reflecting distorted sorrow on sharp impact drops.",
    tag: "SHATTERED MIRROR",
    col: "#cbd5e1"
  },
  {
    id: 'sad_tear_basin',
    name: "\ud83e\udea3 Submerged Tear Basin Ripple",
    category: 'sad',
    family: 'sad',
    badge: '🪣',
    desc: "Heavy crystal tears splashing into still dark water, creating ripple ripples.",
    tag: "TEAR BASIN",
    col: "#38bdf8"
  },
  {
    id: 'sad_ceiling_drips',
    name: "\ud83d\udca7 Leaking Ceiling Drips Echo",
    category: 'sad',
    family: 'sad',
    badge: '💧',
    desc: "Rhythmic cavernous water drops echoing in an empty cold concrete room.",
    tag: "CEILING DRIPS",
    col: "#0284c7"
  },
  {
    id: 'sad_minor_sine',
    name: "\u3030\ufe0f Minor Key Harmonic Sine Wave",
    category: 'sad',
    family: 'sad',
    badge: '〰️',
    desc: "Doleful descending sine wave vibrating with pure mournful acoustic resonance.",
    tag: "MINOR SINE",
    col: "#60a5fa"
  },
  {
    id: 'sad_november_gale',
    name: "\ud83c\udf2c\ufe0f Cold November Gale Wind",
    category: 'sad',
    family: 'sad',
    badge: '🌬️',
    desc: "Biting freezing wind sweeping dry dust and cold raindrops across the frame.",
    tag: "NOVEMBER GALE",
    col: "#94a3b8"
  },
  {
    id: 'sad_willow_weep',
    name: "\ud83c\udf3f Withered Weeping Willow Drapes",
    category: 'sad',
    family: 'sad',
    badge: '🌿',
    desc: "Drooping willow branches trailing in murky river water on sad violin notes.",
    tag: "WILLOW WEEP",
    col: "#4b5563"
  },
  {
    id: 'sad_hospital_ecg',
    name: "\ud83d\udcc9 Hospital Heart Flatline Sine",
    category: 'sad',
    family: 'sad',
    badge: '📉',
    desc: "Fading green heart monitor line settling into a flatline silence on outro.",
    tag: "HOSPITAL ECG",
    col: "#22c55e"
  },
  {
    id: 'sad_violin_snapped',
    name: "\ud83c\udfbb Snapped Violin String Vibration",
    category: 'sad',
    family: 'sad',
    badge: '🎻',
    desc: "Coiled broken steel string snapping and unravelling on heavy drum hit.",
    tag: "SNAPPED STRING",
    col: "#e11d48"
  },
  {
    id: 'sad_winter_highway',
    name: "\ud83d\udee3\ufe0f Desolate Winter Highway Glow",
    category: 'sad',
    family: 'sad',
    badge: '🛣️',
    desc: "Endless straight empty road in black-and-white blizzard with lone tail lights.",
    tag: "WINTER HIGHWAY",
    col: "#f1f5f9"
  },
  {
    id: 'sad_streetlamp_puddle',
    name: "\ud83d\udca1 Solitary Streetlamp Puddle",
    category: 'sad',
    family: 'sad',
    badge: '💡',
    desc: "Yellow sodium vapor streetlamp reflecting mournfully in wet dark asphalt.",
    tag: "STREETLAMP PUDDLE",
    col: "#facc15"
  },
  {
    id: 'sad_volcanic_ash',
    name: "\ud83c\udf0b Volcanic Ash Gray Smoke",
    category: 'sad',
    family: 'sad',
    badge: '🌋',
    desc: "Suffocating dark gray volcanic ash motes settling like sadness across the image.",
    tag: "VOLCANIC ASH",
    col: "#64748b"
  },
  {
    id: 'sad_shower_crying',
    name: "\ud83d\udebf Crying in Shower Water Flow",
    category: 'sad',
    family: 'sad',
    badge: '🚿',
    desc: "Heavy streams of clear water washing down blurred glass tile wall.",
    tag: "SHOWER CRY",
    col: "#0ea5e9"
  },
  {
    id: 'sad_diary_drift',
    name: "\ud83d\udcc4 Torn Diary Page Wind Drift",
    category: 'sad',
    family: 'sad',
    badge: '📄',
    desc: "Torn crumpled paper scraps with smudged handwriting blowing down alley.",
    tag: "DIARY DRIFT",
    col: "#e2e8f0"
  },
  {
    id: 'sad_snowfall_gloom',
    name: "\ud83c\udf28\ufe0f Silent Midnight Snowfall",
    category: 'sad',
    family: 'sad',
    badge: '🌨️',
    desc: "Heavy quiet snowflakes falling relentlessly into freezing dark silence.",
    tag: "SNOWFALL GLOOM",
    col: "#f8fafc"
  },
  {
    id: 'sad_wooden_box',
    name: "\ud83d\udce6 Hollow Wooden Box Echo",
    category: 'sad',
    family: 'sad',
    badge: '📦',
    desc: "Muffled acoustic hollow box reverberation dampening high frequencies on drops.",
    tag: "HOLLOW BOX",
    col: "#78716c"
  },
  {
    id: 'sad_porcelain_mask',
    name: "\ud83c\udfad Shattered Porcelain Doll Mask",
    category: 'sad',
    family: 'sad',
    badge: '🎭',
    desc: "Cracked theatrical mask shedding a single black tear on chorus breakdown.",
    tag: "PORCELAIN MASK",
    col: "#f1f5f9"
  },
  {
    id: 'sad_sunken_anchor',
    name: "\u2693 Sunken Titanic Iron Anchor",
    category: 'sad',
    family: 'sad',
    badge: '⚓',
    desc: "Massive rusted ship anchor resting motionless in pitch-black ocean depths.",
    tag: "SUNKEN ANCHOR",
    col: "#475569"
  },
  {
    id: 'sad_ash_silhouette',
    name: "\ud83d\udc64 Disintegrating Ash Silhouette",
    category: 'sad',
    family: 'sad',
    badge: '👤',
    desc: "Human silhouette slowly dissolving into drifting particles on sad piano chords.",
    tag: "ASH SILHOUETTE",
    col: "#94a3b8"
  },
  {
    id: 'sad_monsoon_cloud',
    name: "\u2601\ufe0f Dark Monsoon Thundercloud",
    category: 'sad',
    family: 'sad',
    badge: '☁️',
    desc: "Oppressive charcoal thunderhead rumbling with distant ominous low bass.",
    tag: "MONSOON CLOUD",
    col: "#334155"
  },
  {
    id: 'sad_muffled_sob',
    name: "\ud83d\udd07 Muffled Sob Sonic Pressure",
    category: 'sad',
    family: 'sad',
    badge: '🔇',
    desc: "Low-pass filtered audio pulse that constricts and releases like a heavy chest sigh.",
    tag: "MUFFLED SOB",
    col: "#38bdf8"
  },
  {
    id: 'sad_foghorn_ocean',
    name: "\ud83d\udea2 Distant Foghorn Ocean Vibration",
    category: 'sad',
    family: 'sad',
    badge: '🚢',
    desc: "Deep bass horn drone echoing across gray choppy coastal waves.",
    tag: "FOGHORN DRONE",
    col: "#1e293b"
  },
  {
    id: 'sad_desert_mirage',
    name: "\ud83c\udfdc\ufe0f Barren Desert Mirage Ripple",
    category: 'sad',
    family: 'sad',
    badge: '🏜️',
    desc: "Heat distortion waves shivering across an endless sun-bleached desert.",
    tag: "DESERT MIRAGE",
    col: "#d97706"
  },
  {
    id: 'sad_granite_gravestone',
    name: "\ud83e\udea6 Cold Granite Gravestone Mist",
    category: 'sad',
    family: 'sad',
    badge: '🪦',
    desc: "Weathered carved tombstone surrounded by damp moss and morning cemetery mist.",
    tag: "GRAVESTONE MIST",
    col: "#64748b"
  },
  {
    id: 'sad_unanswered_call',
    name: "\ud83d\udcf1 Unanswered Phone Call Static",
    category: 'sad',
    family: 'sad',
    badge: '📱',
    desc: "Glow of incoming call ringing out into empty room with rhythmic pulse.",
    tag: "UNANSWERED CALL",
    col: "#ef4444"
  },
  {
    id: 'sad_thorn_scratch',
    name: "\ud83e\udd40 Black Rose Thorn Scratch",
    category: 'sad',
    family: 'sad',
    badge: '🥀',
    desc: "Sharp thorny vine wrapping tightly and bruising with dark crimson droplets.",
    tag: "THORN SCRATCH",
    col: "#881337"
  },
  {
    id: 'sad_grave_wildflower',
    name: "\ud83c\udf3c Forgotten Grave Wildflower",
    category: 'sad',
    family: 'sad',
    badge: '🌼',
    desc: "Single pale dandelion blooming amidst cracked cemetery stones.",
    tag: "GRAVE WILDFLOWER",
    col: "#fef08a"
  },
  {
    id: 'sad_eyeglass_fracture',
    name: "\ud83d\udc53 Fractured Eyeglass Lens",
    category: 'sad',
    family: 'sad',
    badge: '👓',
    desc: "Spiderweb glass cracks fragmenting the view of a blurred solitary portrait.",
    tag: "EYEGLASS CRACK",
    col: "#cbd5e1"
  },
  {
    id: 'sad_attic_dust',
    name: "\ud83d\udce6 Abandoned Dusty Attic Motes",
    category: 'sad',
    family: 'sad',
    badge: '📦',
    desc: "Sunbeam through dirty attic window illuminating floating memories of the past.",
    tag: "ATTIC DUST",
    col: "#a8a29e"
  },
  {
    id: 'sad_creaking_swing',
    name: "\u26d3\ufe0f Creaking Rusted Playground Swing",
    category: 'sad',
    family: 'sad',
    badge: '⛓️',
    desc: "Empty chain swing swaying back and forth in cold autumn wind.",
    tag: "CREAKING SWING",
    col: "#64748b"
  },
  {
    id: 'sad_cave_stalactite',
    name: "\ud83d\udca7 Dripping Cave Stalactite",
    category: 'sad',
    family: 'sad',
    badge: '💧',
    desc: "Slow mineral water drop falling into black underground cavern pool.",
    tag: "CAVE DROP",
    col: "#0284c7"
  },
  {
    id: 'sad_steel_wire',
    name: "\ud83e\udea2 Cold Steel Horizon Wire",
    category: 'sad',
    family: 'sad',
    badge: '🪢',
    desc: "Taut steel cable vibrating with icy cold wind on remote mountain pass.",
    tag: "STEEL WIRE",
    col: "#94a3b8"
  },
  {
    id: 'sad_cello_drone',
    name: "\ud83c\udfbb Melancholic Cello Drone Ribbon",
    category: 'sad',
    family: 'sad',
    badge: '🎻',
    desc: "Heavy horsehair bow vibrating on bottom C-string with weeping sorrow.",
    tag: "CELLO DRONE",
    col: "#7c2d12"
  },
  {
    id: 'sad_perched_crow',
    name: "\ud83e\udd85 Solitary Perched Crow Silhouette",
    category: 'sad',
    family: 'sad',
    badge: '🦅',
    desc: "Dark raven perched on barren winter oak branch looking down at gray earth.",
    tag: "PERCHED CROW",
    col: "#18181b"
  },
  {
    id: 'sad_city_smog',
    name: "\ud83c\udfd9\ufe0f Gray Smog City Smudge",
    category: 'sad',
    family: 'sad',
    badge: '🏙️',
    desc: "Overbearing polluted city skyline suffocated in endless drizzle and exhaust.",
    tag: "CITY SMOG",
    col: "#475569"
  },
  {
    id: 'sad_flickering_motel',
    name: "\ud83c\udfe8 Flickering Neon Motel Sign",
    category: 'sad',
    family: 'sad',
    badge: '🏨',
    desc: "Buzzed broken neon 'VACANCY' letters flickering erratically in rain.",
    tag: "NEON MOTEL",
    col: "#ec4899"
  },
  {
    id: 'sad_river_whirlpool',
    name: "\ud83c\udf00 Dark River Undercurrent Swirl",
    category: 'sad',
    family: 'sad',
    badge: '🌀',
    desc: "Deep murky river vortex pulling submerged leaves down into silence.",
    tag: "RIVER VORTEX",
    col: "#0369a1"
  },
  {
    id: 'sad_shattered_chandelier',
    name: "\ud83d\udd2e Crashing Crystal Chandelier",
    category: 'sad',
    family: 'sad',
    badge: '🔮',
    desc: "Ornate crystal drops shattering on ballroom marble floor into dust.",
    tag: "CHANDELIER CRASH",
    col: "#e2e8f0"
  },
  {
    id: 'sad_red_booth',
    name: "\u260e\ufe0f Lonely Red Phone Booth",
    category: 'sad',
    family: 'sad',
    badge: '☎️',
    desc: "Weathered vintage phone booth in pouring rain with handset dangling off hook.",
    tag: "PHONE BOOTH",
    col: "#dc2626"
  },
  {
    id: 'sad_am_radio_noise',
    name: "\ud83d\udcfb Fading AM Radio White Noise",
    category: 'sad',
    family: 'sad',
    badge: '📻',
    desc: "Scratchy staticky radio broadcast fading between station frequencies.",
    tag: "AM STATIC",
    col: "#a8a29e"
  },
  {
    id: 'sad_coffee_ring',
    name: "\u2615 Stained Coffee Mug Ring",
    category: 'sad',
    family: 'sad',
    badge: '☕',
    desc: "Dark brown dried coffee stain circle on dusty wooden desk.",
    tag: "COFFEE RING",
    col: "#78350f"
  },
  {
    id: 'sad_cemetery_ivy',
    name: "\ud83c\udf43 Overgrown Cemetery Ivy",
    category: 'sad',
    family: 'sad',
    badge: '🍃',
    desc: "Creeping dark green ivy slowly covering forgotten names on stone.",
    tag: "CEMETERY IVY",
    col: "#166534"
  },
  {
    id: 'sad_tin_roof_hail',
    name: "\ud83c\udfe0 Tin Roof Hailstorm Clatter",
    category: 'sad',
    family: 'sad',
    badge: '🏠',
    desc: "Violent impact ripples hammering a rusty metal shack roof in storm.",
    tag: "TIN ROOF HAIL",
    col: "#64748b"
  },
  {
    id: 'sad_canvas_threads',
    name: "\ud83d\uddbc\ufe0f Torn Vintage Canvas Threads",
    category: 'sad',
    family: 'sad',
    badge: '🖼️',
    desc: "Shredded oil painting canvas with frayed linen threads hanging loose.",
    tag: "TORN CANVAS",
    col: "#d6d3d1"
  },
  {
    id: 'sad_hospital_corridor',
    name: "\ud83c\udfe5 Dimming Hospital Corridor",
    category: 'sad',
    family: 'sad',
    badge: '🏥',
    desc: "Sterile white hallway lights humming with lonely antiseptic silence.",
    tag: "HOSPITAL CORRIDOR",
    col: "#94a3b8"
  },
  {
    id: 'sad_bathroom_tiles',
    name: "\ud83d\udd32 Cold Porcelain Bathroom Floor",
    category: 'sad',
    family: 'sad',
    badge: '🔲',
    desc: "Chilled blue floor tiles reflecting tears under harsh bathroom mirror bulb.",
    tag: "BATHROOM TILES",
    col: "#38bdf8"
  },
  {
    id: 'sad_overcast_sky',
    name: "\u2601\ufe0f Gray Winter Overcast Clouds",
    category: 'sad',
    family: 'sad',
    badge: '☁️',
    desc: "Featureless gray cloud ceiling pressing down without a trace of blue.",
    tag: "OVERCAST SKY",
    col: "#475569"
  },
  {
    id: 'sad_burning_bridge',
    name: "\ud83c\udf09 Burning Bridges Smoke Plume",
    category: 'sad',
    family: 'sad',
    badge: '🌉',
    desc: "Thick black smoke rising from collapsed bridge timbers across dark gorge.",
    tag: "BURNING BRIDGE",
    col: "#ea580c"
  },
  {
    id: 'sad_broken_bottle',
    name: "\ud83c\udf7e Broken Glass Bottle Shards",
    category: 'sad',
    family: 'sad',
    badge: '🍾',
    desc: "Amber beer bottle shattered against alley wall glistening in gutter rain.",
    tag: "BROKEN BOTTLE",
    col: "#b45309"
  },
  {
    id: 'sad_desolate_pier',
    name: "\u2693 Desolate Pier Fog Horn",
    category: 'sad',
    family: 'sad',
    badge: '⚓',
    desc: "Wooden ocean pier stretching out into gray void with crashing surf.",
    tag: "DESOLATE PIER",
    col: "#334155"
  },
  {
    id: 'sad_empty_wardrobe',
    name: "\ud83d\udeaa Empty Wardrobe Moth Drift",
    category: 'sad',
    family: 'sad',
    badge: '🚪',
    desc: "Open wooden closet doors revealing bare hangers and drifting dust motes.",
    tag: "EMPTY WARDROBE",
    col: "#78716c"
  },
  {
    id: 'sad_wet_asphalt',
    name: "\ud83d\ude97 Wet Asphalt Headlight Blur",
    category: 'sad',
    family: 'sad',
    badge: '🚗',
    desc: "Blinding wet road reflections of oncoming high beams in pouring rain.",
    tag: "WET ASPHALT",
    col: "#fbbf24"
  },
  {
    id: 'sad_sunflower_droop',
    name: "\ud83c\udf3b Wilted Sunflower Droop",
    category: 'sad',
    family: 'sad',
    badge: '🌻',
    desc: "Heavy dried sunflower head bowed down to barren frozen dirt.",
    tag: "SUNFLOWER DROOP",
    col: "#ca8a04"
  },
  {
    id: 'sad_prison_bars',
    name: "\u26d3\ufe0f Cold Prison Iron Bars",
    category: 'sad',
    family: 'sad',
    badge: '⛓️',
    desc: "Shadows of vertical cell bars cast across damp stone floor.",
    tag: "PRISON BARS",
    col: "#475569"
  },
  {
    id: 'sad_graveyard_whisper',
    name: "\ud83c\udf2c\ufe0f Silent Graveyard Wind Whisper",
    category: 'sad',
    family: 'sad',
    badge: '🌬️',
    desc: "Eerie whistling wind sweeping through weeping willows in moonlight.",
    tag: "GRAVEYARD WIND",
    col: "#94a3b8"
  },
  {
    id: 'sad_drowning_bubbles',
    name: "\ud83e\udee7 Drowning Breath Air Bubbles",
    category: 'sad',
    family: 'sad',
    badge: '🫧',
    desc: "Cluster of silvery oxygen bubbles ascending through dark cold water.",
    tag: "DROWNING BUBBLES",
    col: "#38bdf8"
  },
  {
    id: 'sad_faded_ink_letter',
    name: "\ud83d\udcdc Faded Ink Love Letter",
    category: 'sad',
    family: 'sad',
    badge: '📜',
    desc: "Pale washed-out blue handwriting smudged by dried salty tears.",
    tag: "FADED INK",
    col: "#818cf8"
  },
  {
    id: 'sad_abandoned_doll',
    name: "\ud83e\uddf8 Abandoned Doll in Rain",
    category: 'sad',
    family: 'sad',
    badge: '🧸',
    desc: "Muddy soaked teddy bear sitting on cracked curb in thunderstorm.",
    tag: "ABANDONED DOLL",
    col: "#78716c"
  },
  {
    id: 'sad_concrete_crack',
    name: "\ud83e\uddf1 Cracked Concrete Sidewalk",
    category: 'sad',
    family: 'sad',
    badge: '🧱',
    desc: "Fractured gray pavement with tiny weeds struggling through cracks.",
    tag: "CONCRETE CRACK",
    col: "#94a3b8"
  },
  {
    id: 'sad_cold_tea_cup',
    name: "\u2615 Cold Tea on Dusty Table",
    category: 'sad',
    family: 'sad',
    badge: '☕',
    desc: "Untouched cup of tea with thin film of oil floating on cold surface.",
    tag: "COLD TEA",
    col: "#a16207"
  },
  {
    id: 'sad_solitary_smoker',
    name: "\ud83d\udeac Midnight Solitary Smoker",
    category: 'sad',
    family: 'sad',
    badge: '🚬',
    desc: "Glowing orange cigarette cherry and thin trail of smoke in dark alleyway.",
    tag: "SOLITARY SMOKER",
    col: "#f97316"
  },
  {
    id: 'sad_guitar_splinter',
    name: "\ud83c\udfb8 Broken Guitar Neck Splinter",
    category: 'sad',
    family: 'sad',
    badge: '🎸',
    desc: "Cracked acoustic wood grain and loosened tuning pegs on floor.",
    tag: "GUITAR SPLINTER",
    col: "#854d0e"
  },
  {
    id: 'sad_vanishing_ship',
    name: "\u26f5 Vanishing Ship on Gray Sea",
    category: 'sad',
    family: 'sad',
    badge: '⛵',
    desc: "Faint ship mast silhouette disappearing beyond foggy ocean horizon.",
    tag: "VANISHING SHIP",
    col: "#64748b"
  },
  {
    id: 'sad_chimney_smoke',
    name: "\ud83c\udfe0 Gray Smoke from Chimney",
    category: 'sad',
    family: 'sad',
    badge: '🏠',
    desc: "Thin wisps of woodsmoke dissolving into overcast gray winter sky.",
    tag: "CHIMNEY SMOKE",
    col: "#94a3b8"
  },
  {
    id: 'sad_stone_well',
    name: "\ud83d\udd73\ufe0f Cold Stone Well Echo",
    category: 'sad',
    family: 'sad',
    badge: '🕳️',
    desc: "Pebble falling into deep dark water well with long lonely splash delay.",
    tag: "STONE WELL",
    col: "#334155"
  },
  {
    id: 'sad_river_ice_cracks',
    name: "\ud83e\uddca Frozen River Ice Cracks",
    category: 'sad',
    family: 'sad',
    badge: '🧊',
    desc: "Spiderweb fractures spreading across black river ice on bass kick.",
    tag: "ICE CRACKS",
    col: "#67e8f9"
  },
  {
    id: 'sad_balcony_dripping',
    name: "\ud83c\udfe2 Empty Balcony Rain Drippings",
    category: 'sad',
    family: 'sad',
    badge: '🏢',
    desc: "Steady drip of water from concrete balcony edge falling into abyss.",
    tag: "BALCONY DRIP",
    col: "#38bdf8"
  },
  {
    id: 'sad_distant_whistle',
    name: "\ud83d\ude82 Distant Train Whistle Echo",
    category: 'sad',
    family: 'sad',
    badge: '🚂',
    desc: "Haunting steam train horn echoing through empty dark valley hills.",
    tag: "TRAIN WHISTLE",
    col: "#94a3b8"
  },
  {
    id: 'sad_tear_on_cheek',
    name: "\ud83d\udca7 Silent Tear on Cold Cheek",
    category: 'sad',
    family: 'sad',
    badge: '💧',
    desc: "A single glistening drop tracing down pale skin in slow motion.",
    tag: "TEAR ON CHEEK",
    col: "#60a5fa"
  },
  {
    id: 'sad_autumn_grass',
    name: "\ud83c\udf3e Withered Autumn Grass Shiver",
    category: 'sad',
    family: 'sad',
    badge: '🌾',
    desc: "Dry yellowed prairie grass stems shivering under freezing drizzle.",
    tag: "AUTUMN GRASS",
    col: "#a16207"
  },
  {
    id: 'sad_runway_fog',
    name: "\ud83d\udeec Desolated Runway Fog",
    category: 'sad',
    family: 'sad',
    badge: '🛬',
    desc: "Empty airport tarmac with lonely green centerline lights in fog.",
    tag: "RUNWAY FOG",
    col: "#4ade80"
  },
  {
    id: 'sad_watch_spring',
    name: "\u2699\ufe0f Rusted Pocket Watch Spring",
    category: 'sad',
    family: 'sad',
    badge: '⚙️',
    desc: "Unwound brass clockwork mainspring resting motionless in dust.",
    tag: "WATCH SPRING",
    col: "#ca8a04"
  },
  {
    id: 'sad_submerged_spire',
    name: "\u26ea Drowned City Submerged Spire",
    category: 'sad',
    family: 'sad',
    badge: '⛪',
    desc: "Church tower cross poking above dark flooded lake water.",
    tag: "SUBMERGED SPIRE",
    col: "#0284c7"
  },
  {
    id: 'sad_rain_curtain',
    name: "\ud83c\udf27\ufe0f Dark Horizon Rain Curtain",
    category: 'sad',
    family: 'sad',
    badge: '🌧️',
    desc: "Towering sheet of gray water moving across distant desolate plain.",
    tag: "RAIN CURTAIN",
    col: "#1e293b"
  },
  {
    id: 'sad_match_smoke',
    name: "\ud83d\udd25 Extinguished Matchstick Smoke",
    category: 'sad',
    family: 'sad',
    badge: '🔥',
    desc: "Single curling white smoke plume from a dead sulphur match.",
    tag: "MATCH SMOKE",
    col: "#e2e8f0"
  },
  {
    id: 'sad_absolute_void',
    name: "\ud83d\udd73\ufe0f Absolute Melancholy Void",
    category: 'sad',
    family: 'sad',
    badge: '🕳️',
    desc: "Total sensory dampening with faint sub-bass heartbeat echo.",
    tag: "ABSOLUTE VOID",
    col: "#0f172a"
  },
  {
    id: 'devotional_auto',
    name: "\ud83c\udfb2 Auto Bhakti Reactor (Random Shuffle)",
    category: 'devotional',
    family: 'devotional',
    badge: '🎲',
    desc: "Automatic selection: Bhakti aur mantra ke liye divine sacred chakra aur diya flame auto-shuffle honge!",
    tag: "AUTO DEFAULT",
    col: "#f59e0b"
  },
  {
    id: 'devotional_chakra',
    name: "\ud83e\ude94 Sacred Divine Aura Chakra",
    category: 'devotional',
    family: 'devotional',
    badge: '🪔',
    desc: "Center Circle Logo + Expanding Golden Chakra Rays + Diya Flame Pulse.",
    tag: "CHAKRA CORE",
    col: "#f59e0b"
  },
  {
    id: 'devotional_sudarshan',
    name: "\u2638\ufe0f Maha Sudarshan Chakra Radiance",
    category: 'devotional',
    family: 'devotional',
    badge: '☸️',
    desc: "Spinning sacred golden disc with 32 razor-sharp energy teeth emitting divine golden light.",
    tag: "SUDARSHAN",
    col: "#facc15"
  },
  {
    id: 'devotional_temple_flame',
    name: "\ud83d\udd25 Mandir Akhand Jyoti Flame",
    category: 'devotional',
    family: 'devotional',
    badge: '🔥',
    desc: "Pure golden temple brass diya flame rising and pulsing in rhythm with devotional dholak beats.",
    tag: "AKHAND JYOTI",
    col: "#ea580c"
  },
  {
    id: 'devotional_omkar_ring',
    name: "\ud83d\udd49\ufe0f Omkar Celestial Ring",
    category: 'devotional',
    family: 'devotional',
    badge: '🕉️',
    desc: "Sacred primordial OM cosmic resonance wave pulsating around the divine avatar emblem.",
    tag: "OMKAR RING",
    col: "#f59e0b"
  },
  {
    id: 'devotional_temple_bell',
    name: "\ud83d\udd14 Temple Ghanta Sonic Wave",
    category: 'devotional',
    family: 'devotional',
    badge: '🔔',
    desc: "Acoustic brass resonance rings expanding outwards simulating the deep chime of a mandir bell.",
    tag: "TEMPLE BELL",
    col: "#eab308"
  },
  {
    id: 'devotional_aarti_ripple',
    name: "\ud83e\ude94 Maha Aarti Thali Orbit Rays",
    category: 'devotional',
    family: 'devotional',
    badge: '🪔',
    desc: "Golden circular aarti lamps revolving in sacred pradakshina orbit with warm amber radiance.",
    tag: "AARTI THALI",
    col: "#f97316"
  },
  {
    id: 'devotional_lotus_bloom',
    name: "\ud83e\udeb7 Sahasrara Golden Lotus Bloom",
    category: 'devotional',
    family: 'devotional',
    badge: '🪷',
    desc: "1000-petal divine golden lotus unfolding gracefully beneath the sanctified center portrait.",
    tag: "GOLDEN LOTUS",
    col: "#fbbf24"
  },
  {
    id: 'devotional_mantra_orbit',
    name: "\ud83d\udcff Vedic Sacred Japa Orbit Ring",
    category: 'devotional',
    family: 'devotional',
    badge: '📿',
    desc: "108 glowing celestial prayer beads circulating in sacred geometric alignment on kirtan drops.",
    tag: "JAPA MALA",
    col: "#d97706"
  },
  {
    id: 'devotional_trishul_halo',
    name: "\ud83d\udd31 Mahadev Trishul Energy Aura",
    category: 'devotional',
    family: 'devotional',
    badge: '🔱',
    desc: "Cosmic electric blue & golden trishul aura emitting powerful Rudra energy pulses on damru hits.",
    tag: "TRISHUL ENERGY",
    col: "#0284c7"
  },
  {
    id: 'devotional_swarna_pushpa',
    name: "\ud83c\udf3c Swarna Pushpa Divine Shower",
    category: 'devotional',
    family: 'devotional',
    badge: '🌼',
    desc: "Shower of blessed golden marigold petals raining gently around the sanctum sanctorum.",
    tag: "FLOWER SHOWER",
    col: "#eab308"
  },
  {
    id: 'devotional_divine_surya',
    name: "\u2600\ufe0f Surya Dev Golden Rays Aura",
    category: 'devotional',
    family: 'devotional',
    badge: '☀️',
    desc: "360\u00b0 celestial solar corona radiating pure golden morning light and positive spiritual energy.",
    tag: "SURYA RAYS",
    col: "#f59e0b"
  },
  {
    id: 'devotional_kailash_mystic',
    name: "\ud83c\udfd4\ufe0f Kailash Peak Mystic Glow",
    category: 'devotional',
    family: 'devotional',
    badge: '🏔️',
    desc: "Divine ethereal blue moonlight reflecting off sacred snow peaks with shimmering celestial frost.",
    tag: "KAILASH GLOW",
    col: "#38bdf8"
  },
  {
    id: 'devotional_rudraksha_core',
    name: "\ud83d\udcff Rudraksha Sacred Mala Beads",
    category: 'devotional',
    family: 'devotional',
    badge: '📿',
    desc: "Sacred Panchmukhi Rudraksha perimeter ring pulsating with spiritual grounding frequencies.",
    tag: "RUDRAKSHA",
    col: "#92400e"
  },
  {
    id: 'devotional_shankh_wave',
    name: "\ud83d\udc1a Panchajanya Sacred Conch Wave",
    category: 'devotional',
    family: 'devotional',
    badge: '🐚',
    desc: "Spiral sound geometry reproducing the holy vibrational frequency of the sacred Shankh blast.",
    tag: "SHANKH DHUN",
    col: "#f8fafc"
  },
  {
    id: 'devotional_golden_kalash',
    name: "\ud83c\udffa Amrit Kalash Celestial Halo",
    category: 'devotional',
    family: 'devotional',
    badge: '🏺',
    desc: "Sacred Kalash with mango leaves and coconut halo radiating divine nectar and auspicious blessings.",
    tag: "AMRIT KALASH",
    col: "#f59e0b"
  },
  {
    id: 'devotional_ganga_aarti',
    name: "\ud83e\ude94 Haridwar Ganga Aarti Deepam",
    category: 'devotional',
    family: 'devotional',
    badge: '🪔',
    desc: "108 blazing oil lamps swirling in sacred clockwise circle with golden bells.",
    tag: "DEEPAM AARTI",
    col: "#f59e0b"
  },
  {
    id: 'devotional_nandi_dhun',
    name: "\ud83d\udc02 Sacred Nandi Damru Wave",
    category: 'devotional',
    family: 'devotional',
    badge: '🐂',
    desc: "Lord Shiva's divine damru rhythm pulses expanding cosmic sound waves outward.",
    tag: "DAMRU DHUN",
    col: "#eab308"
  },
  {
    id: 'devotional_garuda_wings',
    name: "\ud83e\udd85 Celestial Garuda Feather Halo",
    category: 'devotional',
    family: 'devotional',
    badge: '🦅',
    desc: "Golden divine wings fanning sacred radiance and celestial light rays.",
    tag: "GARUDA HALO",
    col: "#fbbf24"
  },
  {
    id: 'devotional_radha_krishna_flute',
    name: "\ud83e\ude88 Vaikuntha Bansuri Melodic Stream",
    category: 'devotional',
    family: 'devotional',
    badge: '🪈',
    desc: "Divine peacock feather and golden melodic note particles orbiting the avatar.",
    tag: "BANSURI VIBE",
    col: "#ca8a04"
  },
  {
    id: 'devotional_hanuman_gada',
    name: "\ud83d\udea9 Mahabali Hanuman Golden Aura",
    category: 'devotional',
    family: 'devotional',
    badge: '🚩',
    desc: "Blazing saffron aura with invulnerable protective energy shield on drops.",
    tag: "SANKAT MOCHAN",
    col: "#f97316"
  },
  {
    id: 'devotional_shiva_trinetra',
    name: "\ud83d\udc41\ufe0f Trinetra Cosmic Third-Eye Beam",
    category: 'devotional',
    family: 'devotional',
    badge: '👁️',
    desc: "Piercing divine third-eye golden beam dissolving ignorance with cosmic vibration.",
    tag: "THIRD EYE",
    col: "#e11d48"
  },
  {
    id: 'devotional_sri_yantra',
    name: "\ud83d\udcd0 Sri Yantra Sacred Geometry",
    category: 'devotional',
    family: 'devotional',
    badge: '📐',
    desc: "Interlocking sacred triangles of Sri Chakra radiating golden cosmic harmony.",
    tag: "SRI YANTRA",
    col: "#eab308"
  },
  {
    id: 'devotional_kedarnath_glow',
    name: "\u2744\ufe0f Kedarnath Temple Snow Glow",
    category: 'devotional',
    family: 'devotional',
    badge: '❄️',
    desc: "Sacred stone temple glowing through Himalayan blizzards with divine blue warmth.",
    tag: "KEDARNATH",
    col: "#38bdf8"
  },
  {
    id: 'devotional_golden_sarovar',
    name: "\ud83d\uded5 Golden Temple Sarovar Reflection",
    category: 'devotional',
    family: 'devotional',
    badge: '🛕',
    desc: "Holy Amrit Sarovar holy water reflecting shimmering 24K pure golden dome.",
    tag: "SAROVAR GLOW",
    col: "#facc15"
  },
  {
    id: 'devotional_vrindavan_peacock',
    name: "\ud83e\udd9a Vrindavan Peacock Feather Radiance",
    category: 'devotional',
    family: 'devotional',
    badge: '🦚',
    desc: "Emerald and sapphire iridescent peacock feather eye glowing on Krishna bhajan.",
    tag: "PEACOCK FEATHER",
    col: "#0284c7"
  },
  {
    id: 'devotional_tirupati_balaji',
    name: "\ud83d\udc51 Tirupati Balaji Golden Crown",
    category: 'devotional',
    family: 'devotional',
    badge: '👑',
    desc: "Magnificent diamond and ruby encrusted golden crown of Lord Venkateswara.",
    tag: "BALAJI CROWN",
    col: "#f59e0b"
  },
  {
    id: 'devotional_havan_smoke',
    name: "\ud83d\udd25 Agni Kund Vedic Havan Smoke",
    category: 'devotional',
    family: 'devotional',
    badge: '🔥',
    desc: "Fragrant ghee and sacred wood smoke rising heavenward with holy mantras.",
    tag: "HAVAN SMOKE",
    col: "#ea580c"
  },
  {
    id: 'devotional_tulsi_pradakshina',
    name: "\ud83c\udf3f Holy Tulsi Leaf Pradakshina",
    category: 'devotional',
    family: 'devotional',
    badge: '🌿',
    desc: "Sacred green Tulsi plant emitting divine healing vibrations in circle.",
    tag: "TULSI LEAVES",
    col: "#16a34a"
  },
  {
    id: 'devotional_chandan_tilak',
    name: "\ud83e\ude94 Chandan Sandalwood Tilak Rays",
    category: 'devotional',
    family: 'devotional',
    badge: '🪔',
    desc: "Cooling yellow sandalwood paste radiating soothing spiritual tranquility.",
    tag: "CHANDAN RAYS",
    col: "#fde047"
  },
  {
    id: 'devotional_dhoop_spiral',
    name: "\ud83c\udf00 Dhoop Incense Spiral Swirl",
    category: 'devotional',
    family: 'devotional',
    badge: '🌀',
    desc: "Spiraling fragrant dhoop cones filling the mandir with mystical aroma.",
    tag: "DHOOP SPIRAL",
    col: "#cbd5e1"
  },
  {
    id: 'devotional_karpur_aradhana',
    name: "\u2728 Camphor Karpur Aradhana Flame",
    category: 'devotional',
    family: 'devotional',
    badge: '✨',
    desc: "Pure white-hot camphor flame vaporizing without residue during holy aarti.",
    tag: "KARPUR FLAME",
    col: "#ffffff"
  },
  {
    id: 'devotional_mrityunjaya_ring',
    name: "\ud83d\udee1\ufe0f Maha Mrityunjaya Vibration Ring",
    category: 'devotional',
    family: 'devotional',
    badge: '🛡️',
    desc: "Invincible protective sonic shield pulsating with eternal life energy.",
    tag: "MRITYUNJAYA",
    col: "#06b6d4"
  },
  {
    id: 'devotional_gayatri_solar',
    name: "\u2600\ufe0f Gayatri Devi Solar Mandala",
    category: 'devotional',
    family: 'devotional',
    badge: '☀️',
    desc: "Sacred 24-syllable solar energetic mandala dispelling all darkness.",
    tag: "GAYATRI SOLAR",
    col: "#f59e0b"
  },
  {
    id: 'devotional_ganesha_modak',
    name: "\ud83d\udc18 Ganesha Modak Blessing Ring",
    category: 'devotional',
    family: 'devotional',
    badge: '🐘',
    desc: "Vighnaharta Lord Ganesha auspicious sweet blessing shower and modak halo.",
    tag: "GANESHA BLESSING",
    col: "#f97316"
  },
  {
    id: 'devotional_tandava_flames',
    name: "\ud83d\udd25 Shiva Tandava Cosmic Flames",
    category: 'devotional',
    family: 'devotional',
    badge: '🔥',
    desc: "Ring of cosmic fire enclosing Nataraja's supreme dance of universal creation.",
    tag: "TANDAVA FIRE",
    col: "#dc2626"
  },
  {
    id: 'devotional_navagraha_planets',
    name: "\ud83e\ude90 Navagraha 9 Cosmic Planets",
    category: 'devotional',
    family: 'devotional',
    badge: '🪐',
    desc: "Nine planetary deities rotating in sacred cosmic balance around the center.",
    tag: "NAVAGRAHA",
    col: "#a855f7"
  },
  {
    id: 'devotional_amrit_nectar',
    name: "\ud83c\udf6f Amrit Vani Divine Nectar Wave",
    category: 'devotional',
    family: 'devotional',
    badge: '🍯',
    desc: "Golden nectar of immortality overflowing like celestial waterfalls on drops.",
    tag: "AMRIT NECTAR",
    col: "#eab308"
  },
  {
    id: 'devotional_har_ki_pauri',
    name: "\ud83c\udf0a Har Ki Pauri Holy Dip Ripple",
    category: 'devotional',
    family: 'devotional',
    badge: '🌊',
    desc: "Sacred ripples of Mother Ganga washing away sins at the holy Brahma Kund.",
    tag: "HAR KI PAURI",
    col: "#38bdf8"
  },
  {
    id: 'devotional_kamadhenu_cow',
    name: "\ud83d\udc04 Kamadhenu Divine Cow Halo",
    category: 'devotional',
    family: 'devotional',
    badge: '🐄',
    desc: "Mother cow with golden horns and celestial halo showering unconditional blessings.",
    tag: "KAMADHENU",
    col: "#f8fafc"
  },
  {
    id: 'devotional_milk_abhishekam',
    name: "\ud83e\udd5b Shivalinga Milk Abhishekam",
    category: 'devotional',
    family: 'devotional',
    badge: '🥛',
    desc: "Streams of pure white milk, honey and holy water cascading over sacred Lingam.",
    tag: "ABHISHEKAM",
    col: "#ffffff"
  },
  {
    id: 'devotional_kartikeya_vel',
    name: "\u26a1 Kartikeya Vel Golden Spear",
    category: 'devotional',
    family: 'devotional',
    badge: '⚡',
    desc: "Divine warrior spear of Lord Murugan crackling with victorious divine light.",
    tag: "MURUGAN VEL",
    col: "#eab308"
  },
  {
    id: 'devotional_saraswati_veena',
    name: "\ud83c\udfb6 Saraswati Veena Musical Rays",
    category: 'devotional',
    family: 'devotional',
    badge: '🎶',
    desc: "Graceful strings of Goddess Saraswati's veena resonating with pure divine wisdom.",
    tag: "VEENA RAYS",
    col: "#facc15"
  },
  {
    id: 'devotional_lakshmi_dhan',
    name: "\ud83e\ude99 Lakshmi Dhan Varsha Gold Coins",
    category: 'devotional',
    family: 'devotional',
    badge: '🪙',
    desc: "Continuous rain of auspicious gold coins and pink lotus blossoms on beats.",
    tag: "LAKSHMI DHAN",
    col: "#f59e0b"
  },
  {
    id: 'devotional_durga_roar',
    name: "\ud83e\udd81 Durga Maa Lion Roar Shockwave",
    category: 'devotional',
    family: 'devotional',
    badge: '🦁',
    desc: "Fierce protective sonic roar of Maa Durga's lion scattering negative forces.",
    tag: "DURGA ROAR",
    col: "#ea580c"
  },
  {
    id: 'devotional_ram_setu',
    name: "\ud83e\udea8 Ram Setu Floating Stone Ripples",
    category: 'devotional',
    family: 'devotional',
    badge: '🪨',
    desc: "Sacred floating stones inscribed with 'RAM' bobbing in golden ocean waters.",
    tag: "RAM SETU",
    col: "#78716c"
  },
  {
    id: 'devotional_ayodhya_dome',
    name: "\ud83d\udea9 Ayodhya Ram Mandir Golden Dome",
    category: 'devotional',
    family: 'devotional',
    badge: '🚩',
    desc: "Magnificent Nagara architecture temple spire flying the saffron victory flag.",
    tag: "RAM MANDIR",
    col: "#f97316"
  },
  {
    id: 'devotional_chidambaram_grid',
    name: "\ud83c\udf0c Chidambaram Cosmic Dance Grid",
    category: 'devotional',
    family: 'devotional',
    badge: '🌌',
    desc: "Akasha etheric space sacred geometry pulsating with cosmic consciousness.",
    tag: "CHIDAMBARAM",
    col: "#6366f1"
  },
  {
    id: 'devotional_somnath_ocean',
    name: "\ud83c\udf0a Somnath Temple Ocean Wave",
    category: 'devotional',
    family: 'devotional',
    badge: '🌊',
    desc: "Arabian sea waves crashing against ancient eternal Jyotirlinga shrine.",
    tag: "SOMNATH WAVE",
    col: "#0284c7"
  },
  {
    id: 'devotional_mahakal_bhasma',
    name: "\ud83d\udc80 Ujjain Mahakal Bhasma Aarti",
    category: 'devotional',
    family: 'devotional',
    badge: '💀',
    desc: "Holy cremation ash sanctifying Mahakaleshwar with fierce transformative aura.",
    tag: "BHASMA AARTI",
    col: "#cbd5e1"
  },
  {
    id: 'devotional_jagannath_wheel',
    name: "\ud83c\udfa1 Puri Jagannath Rath Yatra Wheel",
    category: 'devotional',
    family: 'devotional',
    badge: '🎡',
    desc: "Massive wooden chariot wheel with radiating sacred spokes and colorful flags.",
    tag: "JAGANNATH WHEEL",
    col: "#dc2626"
  },
  {
    id: 'devotional_rameswaram_kund',
    name: "\u26f2 Rameswaram 22 Kund Holy Spray",
    category: 'devotional',
    family: 'devotional',
    badge: '⛲',
    desc: "Consecrated water droplets from 22 holy wells blessing the devotee.",
    tag: "RAMESWARAM KUND",
    col: "#38bdf8"
  },
  {
    id: 'devotional_badrinath_wave',
    name: "\ud83c\udfd4\ufe0f Badrinath Alaknanda Divine Wave",
    category: 'devotional',
    family: 'devotional',
    badge: '🏔️',
    desc: "Roaring icy waters of Alaknanda river at the feet of Lord Badri Vishal.",
    tag: "BADRINATH",
    col: "#0ea5e9"
  },
  {
    id: 'devotional_vaishno_devi',
    name: "\ud83e\uddd7 Vaishno Devi Trikuta Cave Glow",
    category: 'devotional',
    family: 'devotional',
    badge: '🧗',
    desc: "Sacred Pindies in the holy cave radiating three-fold divine Mother energy.",
    tag: "VAISHNO DEVI",
    col: "#e11d48"
  },
  {
    id: 'devotional_meenakshi_tower',
    name: "\ud83d\uded5 Meenakshi Temple Tower Halo",
    category: 'devotional',
    family: 'devotional',
    badge: '🛕',
    desc: "Soaring multi-colored Dravidian Gopuram reaching into celestial clouds.",
    tag: "MEENAKSHI",
    col: "#10b981"
  },
  {
    id: 'devotional_sai_dhuni',
    name: "\ud83d\udd25 Shirdi Sai Baba Dhuni Flame",
    category: 'devotional',
    family: 'devotional',
    badge: '🔥',
    desc: "Perpetual sacred dhuni fire turning into healing Udi ash for all devotees.",
    tag: "SAI DHUNI",
    col: "#ea580c"
  },
  {
    id: 'devotional_belur_lotus',
    name: "\ud83e\udeb7 Belur Math Lotus Dome Rays",
    category: 'devotional',
    family: 'devotional',
    badge: '🪷',
    desc: "Universal temple architecture combining all religions in one divine lotus.",
    tag: "BELUR MATH",
    col: "#fbbf24"
  },
  {
    id: 'devotional_madurai_chariot',
    name: "\ud83c\udfa0 Madurai Chariot Golden Spikes",
    category: 'devotional',
    family: 'devotional',
    badge: '🎠',
    desc: "Festival chariot bells clanging in rhythm with heavy nagaswaram drones.",
    tag: "CHARIOT SPIKES",
    col: "#eab308"
  },
  {
    id: 'devotional_kalabhairava_dog',
    name: "\ud83d\udc15 Kalabhairava Dog Companion Halo",
    category: 'devotional',
    family: 'devotional',
    badge: '🐕',
    desc: "Fierce Lord of Time riding divine vehicle with terrifying yet protective glow.",
    tag: "KALABHAIRAVA",
    col: "#475569"
  },
  {
    id: 'devotional_surya_namaskar',
    name: "\ud83e\uddd8 Surya Namaskar 12 Ray Mandala",
    category: 'devotional',
    family: 'devotional',
    badge: '🧘',
    desc: "Twelve solar postures traced in luminous gold along the perimeter ring.",
    tag: "SURYA NAMASKAR",
    col: "#f59e0b"
  },
  {
    id: 'devotional_kundalini_spiral',
    name: "\ud83d\udc0d Kundalini Serpent Energy Spiral",
    category: 'devotional',
    family: 'devotional',
    badge: '🐍',
    desc: "Coiled dormant cosmic serpent awakening and piercing through all chakras.",
    tag: "KUNDALINI SPIRAL",
    col: "#84cc16"
  },
  {
    id: 'devotional_brahma_loka',
    name: "\ud83e\udeb7 Brahma Loka Golden Lotus Seat",
    category: 'devotional',
    family: 'devotional',
    badge: '🪷',
    desc: "Four-headed Creator seated on transcendental lotus amidst cosmic nebulae.",
    tag: "BRAHMA LOKA",
    col: "#facc15"
  },
  {
    id: 'devotional_sheshnag_canopy',
    name: "\ud83d\udc0d Vishnu Sheshnag Serpent Canopy",
    category: 'devotional',
    family: 'devotional',
    badge: '🐍',
    desc: "Thousand-headed celestial snake Ananta shielding Lord Narayana on ocean.",
    tag: "SHESHNAG",
    col: "#38bdf8"
  },
  {
    id: 'devotional_matsya_avatar',
    name: "\ud83d\udc1f Matsya Avatar Sacred Ocean Wave",
    category: 'devotional',
    family: 'devotional',
    badge: '🐟',
    desc: "Golden divine horned fish guiding King Manu's boat through cosmic flood.",
    tag: "MATSYA AVATAR",
    col: "#0284c7"
  },
  {
    id: 'devotional_kurma_avatar',
    name: "\ud83d\udc22 Kurma Avatar Cosmic Mountain",
    category: 'devotional',
    family: 'devotional',
    badge: '🐢',
    desc: "Cosmic turtle supporting Mount Mandara for the churning of ocean of milk.",
    tag: "KURMA AVATAR",
    col: "#15803d"
  },
  {
    id: 'devotional_varaha_avatar',
    name: "\ud83d\udc17 Varaha Avatar Earth Lifting Halo",
    category: 'devotional',
    family: 'devotional',
    badge: '🐗',
    desc: "Divine boar lifting Mother Earth on his golden tusks from cosmic depths.",
    tag: "VARAHA AVATAR",
    col: "#78350f"
  },
  {
    id: 'devotional_narasimha_pillar',
    name: "\u26a1 Narasimha Pillar Fire Burst",
    category: 'devotional',
    family: 'devotional',
    badge: '⚡',
    desc: "Exploding stone pillar revealing the half-lion protector of Prahlad.",
    tag: "NARASIMHA PILLAR",
    col: "#ef4444"
  },
  {
    id: 'devotional_vamana_steps',
    name: "\ud83d\udc63 Vamana 3 Paced Cosmic Steps",
    category: 'devotional',
    family: 'devotional',
    badge: '👣',
    desc: "Dwarf Brahmin expanding to Trivikrama measuring entire cosmos in three steps.",
    tag: "VAMANA STEPS",
    col: "#f59e0b"
  },
  {
    id: 'devotional_parashurama_axe',
    name: "\ud83e\ude93 Parashurama Battle Axe Spark",
    category: 'devotional',
    family: 'devotional',
    badge: '🪓',
    desc: "Divine battle axe flashing with celestial lightning against tyranny.",
    tag: "PARASHURAMA AXE",
    col: "#cbd5e1"
  },
  {
    id: 'devotional_ram_kodanda',
    name: "\ud83c\udff9 Maryada Purushottam Bow Rays",
    category: 'devotional',
    family: 'devotional',
    badge: '🏹',
    desc: "Lord Rama's Kodanda bow releasing golden arrows that never miss righteousness.",
    tag: "KODANDA BOW",
    col: "#f97316"
  },
  {
    id: 'devotional_balarama_plow',
    name: "\ud83c\udf3e Balarama Golden Plow Vibration",
    category: 'devotional',
    family: 'devotional',
    badge: '🌾',
    desc: "Supreme agricultural and strength deity wielding cosmic golden plow.",
    tag: "BALARAMA PLOW",
    col: "#eab308"
  },
  {
    id: 'devotional_kalki_stallion',
    name: "\ud83d\udc0e Kalki White Stallion Speed Dust",
    category: 'devotional',
    family: 'devotional',
    badge: '🐎',
    desc: "Blazing white horse Devadatta carrying the final avatar with flaming sword.",
    tag: "KALKI STALLION",
    col: "#ffffff"
  },
  {
    id: 'devotional_govardhan_hill',
    name: "\u26f0\ufe0f Govardhan Parvat Lifting Finger",
    category: 'devotional',
    family: 'devotional',
    badge: '⛰️',
    desc: "Little finger of Sri Krishna holding Govardhan hill sheltering all Vrindavan.",
    tag: "GOVARDHAN HILL",
    col: "#0284c7"
  },
  {
    id: 'devotional_kali_mundamala',
    name: "\ud83d\udc80 Kali Maa Mundamala Energy Ring",
    category: 'devotional',
    family: 'devotional',
    badge: '💀',
    desc: "Cosmic garland of 50 Sanskrit letters dissolving ego into supreme bliss.",
    tag: "KALI MUNDAMALA",
    col: "#18181b"
  },
  {
    id: 'devotional_tara_devi',
    name: "\u2b50 Tara Devi Blue Starlight Halo",
    category: 'devotional',
    family: 'devotional',
    badge: '⭐',
    desc: "Compassionate Mother Tara guiding souls safely across the ocean of delusion.",
    tag: "TARA DEVI",
    col: "#38bdf8"
  },
  {
    id: 'devotional_tripurasundari',
    name: "\ud83c\udf3a Tripurasundari 16 Ray Mandala",
    category: 'devotional',
    family: 'devotional',
    badge: '🌺',
    desc: "Supreme beauty of the three worlds radiating transcendental crimson rays.",
    tag: "TRIPURASUNDARI",
    col: "#ec4899"
  },
  {
    id: 'devotional_bhuvaneshwari',
    name: "\ud83d\udc51 Bhuvaneshwari Cosmic Empress Glow",
    category: 'devotional',
    family: 'devotional',
    badge: '👑',
    desc: "Empress of all fourteen worlds holding noose and goad with benevolent smile.",
    tag: "BHUVANESHWARI",
    col: "#f59e0b"
  },
  {
    id: 'devotional_chhinnamasta',
    name: "\u26a1 Chhinnamasta Lightning Arc",
    category: 'devotional',
    family: 'devotional',
    badge: '⚡',
    desc: "Self-decapitated goddess drinking divine nectar of supreme non-dual awareness.",
    tag: "CHHINNAMASTA",
    col: "#ef4444"
  },
  {
    id: 'devotional_dhumavati',
    name: "\ud83d\udca8 Dhumavati Mystic Smoke Veil",
    category: 'devotional',
    family: 'devotional',
    badge: '💨',
    desc: "Grandmother goddess of smoke transmuting deepest sorrow into spiritual gold.",
    tag: "DHUMAVATI",
    col: "#64748b"
  },
  {
    id: 'devotional_bagalamukhi',
    name: "\ud83d\udfe8 Bagalamukhi Golden Stun Beam",
    category: 'devotional',
    family: 'devotional',
    badge: '🟨',
    desc: "Golden goddess stunning and silencing all enemies, speech, and negative mind.",
    tag: "BAGALAMUKHI",
    col: "#facc15"
  },
  {
    id: 'devotional_matangi',
    name: "\ud83e\udd9c Matangi Green Emerald Radiance",
    category: 'devotional',
    family: 'devotional',
    badge: '🦜',
    desc: "Outcaste goddess of music, arts and spoken word with vibrant emerald parrot.",
    tag: "MATANGI",
    col: "#10b981"
  },
  {
    id: 'devotional_kamala_lotus',
    name: "\ud83e\udeb7 Kamala Lotus Golden Shower",
    category: 'devotional',
    family: 'devotional',
    badge: '🪷',
    desc: "Tantric Lakshmi bathed by four celestial elephants with golden nectar pots.",
    tag: "KAMALA LOTUS",
    col: "#fbbf24"
  },
  {
    id: 'devotional_annapurna_nectar',
    name: "\ud83c\udf72 Annapurna Golden Ladle Nectar",
    category: 'devotional',
    family: 'devotional',
    badge: '🍲',
    desc: "Goddess of divine nourishment serving food that satisfies body, mind and soul.",
    tag: "ANNAPURNA",
    col: "#f97316"
  },
  {
    id: 'devotional_ganga_descent',
    name: "\ud83c\udf0a Ganga Avatarana Heavenly Descent",
    category: 'devotional',
    family: 'devotional',
    badge: '🌊',
    desc: "Celestial river falling from Vishnu's foot through Shiva's hair to earth.",
    tag: "GANGA DESCENT",
    col: "#38bdf8"
  },
  {
    id: 'devotional_yamuna_indigo',
    name: "\ud83d\udca7 Yamuna Dark Indigo Water Glow",
    category: 'devotional',
    family: 'devotional',
    badge: '💧',
    desc: "Mysterious dark waters of Yamuna dancing with Vrindavan lovers' footsteps.",
    tag: "YAMUNA INDIGO",
    col: "#1e1b4b"
  },
  {
    id: 'devotional_saraswati_stream',
    name: "\ud83c\udf0a Saraswati Hidden River Wave",
    category: 'devotional',
    family: 'devotional',
    badge: '🌊',
    desc: "Subterranean mythical river flowing with pure Vedic knowledge at Prayagraj.",
    tag: "SARASWATI STREAM",
    col: "#e0e7ff"
  },
  {
    id: 'devotional_narmada_kankad',
    name: "\ud83e\udea8 Narmada Kankad Stone Linga",
    category: 'devotional',
    family: 'devotional',
    badge: '🪨',
    desc: "Every pebble of river Narmada naturally formed into holy Banalinga.",
    tag: "NARMADA LINGA",
    col: "#78716c"
  },
  {
    id: 'devotional_godavari_ripple',
    name: "\ud83d\udca7 Godavari Holy Bathing Ripple",
    category: 'devotional',
    family: 'devotional',
    badge: '💧',
    desc: "Southern Ganga purifying pilgrim souls with gentle sacred river ripples.",
    tag: "GODAVARI RIPPLE",
    col: "#0284c7"
  },
  {
    id: 'devotional_kaveri_halo',
    name: "\ud83c\udf0a Kaveri Sacred South Water Halo",
    category: 'devotional',
    family: 'devotional',
    badge: '🌊',
    desc: "Agastya muni's overturned kamandalu becoming the mother of southern temples.",
    tag: "KAVERI HALO",
    col: "#0ea5e9"
  },
  {
    id: 'devotional_sindhu_current',
    name: "\ud83c\udf0a Sindhu Vedic River Current",
    category: 'devotional',
    family: 'devotional',
    badge: '🌊',
    desc: "Ancient cradle of Vedic civilization chanting Rigveda hymns across plains.",
    tag: "SINDHU CURRENT",
    col: "#38bdf8"
  },
  {
    id: 'devotional_gomati_chakra',
    name: "\ud83d\udc1a Gomati Sacred Chakra Ripple",
    category: 'devotional',
    family: 'devotional',
    badge: '🐚',
    desc: "White spiral shell stone from Dwarka bringing auspicious prosperity.",
    tag: "GOMATI CHAKRA",
    col: "#f8fafc"
  },
  {
    id: 'devotional_manasarovar_swan',
    name: "\ud83e\udda2 Manasarovar Holy Swan Orbit",
    category: 'devotional',
    family: 'devotional',
    badge: '🦢',
    desc: "Pure high-altitude sacred lake reflecting holy Kailash with royal swans.",
    tag: "MANASAROVAR",
    col: "#e0f2fe"
  },
  {
    id: 'devotional_mount_meru',
    name: "\u26f0\ufe0f Mount Meru Golden Peak",
    category: 'devotional',
    family: 'devotional',
    badge: '⛰️',
    desc: "Central cosmic mountain of Hindu cosmology anchoring all divine realms.",
    tag: "MOUNT MERU",
    col: "#facc15"
  },
  {
    id: 'devotional_kalpavriksha_tree',
    name: "\ud83c\udf33 Kalpavriksha Wish Tree Leaves",
    category: 'devotional',
    family: 'devotional',
    badge: '🌳',
    desc: "Celestial wishing tree granting all pure spiritual desires with golden dew.",
    tag: "KALPAVRIKSHA",
    col: "#15803d"
  },
  {
    id: 'devotional_chintamani_gem',
    name: "\ud83d\udc8e Chintamani Wish Gem Radiance",
    category: 'devotional',
    family: 'devotional',
    badge: '💎',
    desc: "Mythical gem fulfilling spiritual liberation shining with rainbow facets.",
    tag: "CHINTAMANI",
    col: "#38bdf8"
  },
  {
    id: 'devotional_vaikuntha_gate',
    name: "\ud83d\udeaa Vaikuntha Gatekeepers Golden Halo",
    category: 'devotional',
    family: 'devotional',
    badge: '🚪',
    desc: "Jaya and Vijaya with four arms and maces guarding transcendental doors.",
    tag: "VAIKUNTHA GATE",
    col: "#eab308"
  },
  {
    id: 'devotional_akhand_ramayan',
    name: "\ud83d\udcdc Akhand Ramayan Chanting Shockwave",
    category: 'devotional',
    family: 'devotional',
    badge: '📜',
    desc: "Unbroken 24-hour recitation creating continuous harmonic resonance field.",
    tag: "AKHAND RAMAYAN",
    col: "#f97316"
  },
  {
    id: 'devotional_sunderkand_flame',
    name: "\ud83d\udd25 Sunderkand Golden Flame Wings",
    category: 'devotional',
    family: 'devotional',
    badge: '🔥',
    desc: "Hanumanji's leap across ocean turning impossible into effortless grace.",
    tag: "SUNDERKAND",
    col: "#ea580c"
  },
  {
    id: 'devotional_chalisa_ring',
    name: "\ud83d\udcff Hanuman Chalisa 40 Chaupai Ring",
    category: 'devotional',
    family: 'devotional',
    badge: '📿',
    desc: "Forty sacred verses rotating in protective perimeter around the avatar.",
    tag: "CHALISA RING",
    col: "#f59e0b"
  },
  {
    id: 'devotional_vishwaroop_darshan',
    name: "\ud83c\udf0c Bhagavad Gita Cosmic Vishwaroop",
    category: 'devotional',
    family: 'devotional',
    badge: '🌌',
    desc: "Universal cosmic form containing all suns, stars, gods, and galaxies in one.",
    tag: "VISHWAROOP",
    col: "#a855f7"
  },
  {
    id: 'devotional_maha_yajna',
    name: "\ud83d\udd25 Maha Yajna Cosmic Fire Pillar",
    category: 'devotional',
    family: 'devotional',
    badge: '🔥',
    desc: "Pillar of divine sacred fire rising to the highest heavens with oblations.",
    tag: "MAHA YAJNA",
    col: "#dc2626"
  },
  {
    id: 'devotional_moksha_eternal',
    name: "\u2728 Moksha Divine Eternal Light",
    category: 'devotional',
    family: 'devotional',
    badge: '✨',
    desc: "Final liberation into infinite peace and divine union beyond all illusion.",
    tag: "MOKSHA ETERNAL",
    col: "#ffffff"
  },
  {
    id: 'lofi_auto',
    name: "\ud83c\udfb2 Auto Lo-Fi Reactor (Random Shuffle)",
    category: 'lofi',
    family: 'lofi',
    badge: '🎲',
    desc: "Automatic selection: Lo-Fi beats ke liye vinyl disc, cassette spool aur star dust auto-match honge!",
    tag: "AUTO DEFAULT",
    col: "#a855f7"
  },
  {
    id: 'lofi_vinyl',
    name: "\ud83c\udf19 Cozy Lo-Fi Vinyl Spin Core",
    category: 'lofi',
    family: 'lofi',
    badge: '🌙',
    desc: "Center Circle Logo + Rotating Vinyl Record Disc + Soft Lavender Starfield.",
    tag: "VINYL SPIN",
    col: "#a855f7"
  },
  {
    id: 'lofi_cassette_spool',
    name: "\ud83d\udcfc Retro Cassette Tape Reel Spool",
    category: 'lofi',
    family: 'lofi',
    badge: '📼',
    desc: "Dual magnetic tape spools revolving gently with warm analog cassette hiss dust.",
    tag: "CASSETTE REEL",
    col: "#8b5cf6"
  },
  {
    id: 'lofi_midnight_stars',
    name: "\u2728 Lavender Midnight Star Dust",
    category: 'lofi',
    family: 'lofi',
    badge: '✨',
    desc: "Drifting pastel purple and blue starfield with twinkling starlight around center frame.",
    tag: "STAR DUST",
    col: "#c084fc"
  },
  {
    id: 'lofi_rainy_cafe',
    name: "\u2615 Tokyo Night Cafe Rainy Neon",
    category: 'lofi',
    family: 'lofi',
    badge: '☕',
    desc: "Soft blurred amber cafe neon lights glowing through foggy rain streaks on glass.",
    tag: "COZY CAFE",
    col: "#f59e0b"
  },
  {
    id: 'lofi_sunset_clouds',
    name: "\u2601\ufe0f Anime Pastel Cloud Horizon",
    category: 'lofi',
    family: 'lofi',
    badge: '☁️',
    desc: "Dreamy pastel pink and lavender cloud layers drifting peacefully across sunset sky.",
    tag: "PASTEL CLOUDS",
    col: "#f472b6"
  },
  {
    id: 'lofi_vhs_tracking',
    name: "\ud83d\udcfa Vintage VHS Tape Tracking Glitch",
    category: 'lofi',
    family: 'lofi',
    badge: '📺',
    desc: "Authentic 90s VHS tape scanlines and subtle magnetic distortion on lo-fi snare hits.",
    tag: "VHS GLITCH",
    col: "#06b6d4"
  },
  {
    id: 'lofi_tea_steam',
    name: "\ud83c\udf75 Warm Green Tea Vapor Ripple",
    category: 'lofi',
    family: 'lofi',
    badge: '🍵',
    desc: "Soothing curls of fragrant matcha tea steam swirling upwards in tranquil motion.",
    tag: "TEA VAPOR",
    col: "#10b981"
  },
  {
    id: 'lofi_retro_waveform',
    name: "\ud83d\udcfb Retro Radio Waveform Ribbon",
    category: 'lofi',
    family: 'lofi',
    badge: '📻',
    desc: "Smooth curved oscilloscope sine ribbon simulating warm vacuum tube radio reception.",
    tag: "RADIO WAVE",
    col: "#a78bfa"
  },
  {
    id: 'lofi_sleepwalker_orbit',
    name: "\ud83c\udf0c Sleepwalker Celestial Orbit",
    category: 'lofi',
    family: 'lofi',
    badge: '🌌',
    desc: "Crescent moon and planetary orbit rings revolving in hypnotic midnight trance.",
    tag: "MOON ORBIT",
    col: "#6366f1"
  },
  {
    id: 'lofi_paper_airplane',
    name: "\u2708\ufe0f Origami Airplane Cloud Drift",
    category: 'lofi',
    family: 'lofi',
    badge: '✈️',
    desc: "White paper airplane gliding smoothly on gentle lo-fi bass breeze with dashed trail.",
    tag: "ORIGAMI",
    col: "#e2e8f0"
  },
  {
    id: 'lofi_city_rain',
    name: "\ud83c\udfd9\ufe0f Cyber Lofi Rainy Skyline Pulse",
    category: 'lofi',
    family: 'lofi',
    badge: '🏙️',
    desc: "Distant metropolitan skyscraper silhouette with flickering warm apartment windows.",
    tag: "LOFI SKYLINE",
    col: "#3b82f6"
  },
  {
    id: 'lofi_bonsai_tree',
    name: "\ud83e\udeb4 Zen Bonsai Tree Silhouette",
    category: 'lofi',
    family: 'lofi',
    badge: '🪴',
    desc: "Peaceful Japanese bonsai silhouette with falling cherry blossoms in meditative aura.",
    tag: "ZEN BONSAI",
    col: "#059669"
  },
  {
    id: 'lofi_twilight_lamp',
    name: "\ud83c\udfee Twilight Paper Lantern Glow",
    category: 'lofi',
    family: 'lofi',
    badge: '🏮',
    desc: "Traditional Japanese red paper lanterns swaying gently in the night breeze.",
    tag: "LANTERN",
    col: "#f43f5e"
  },
  {
    id: 'lofi_rainy_bus_stop',
    name: "\ud83d\ude8f Midnight Rainy Bus Stop",
    category: 'lofi',
    family: 'lofi',
    badge: '🚏',
    desc: "Fluorescent street lamp glowing in drizzle with gentle retro bus engine hum.",
    tag: "BUS STOP",
    col: "#818cf8"
  },
  {
    id: 'lofi_bookstore_lamp',
    name: "\ud83d\udcda Cozy Midnight Library Glow",
    category: 'lofi',
    family: 'lofi',
    badge: '📚',
    desc: "Amber study lamp glow with flying book pages drifting peacefully on low-fi beats.",
    tag: "MIDNIGHT BOOK",
    col: "#a78bfa"
  },
  {
    id: 'lofi_retro_pixel_city',
    name: "\ud83d\udc7e 8-Bit Pixel Sunset Skyline",
    category: 'lofi',
    family: 'lofi',
    badge: '👾',
    desc: "Nostalgic 16-bit pixel art skyscraper silhouettes with 80s arcade sunset.",
    tag: "PIXEL CITY",
    col: "#c084fc"
  },
  {
    id: 'lofi_cat_window',
    name: "\ud83d\udc31 Cat on Rainy Windowsill",
    category: 'lofi',
    family: 'lofi',
    badge: '🐱',
    desc: "Sleepy silhouette of cat watching rain droplets race down the glass pane.",
    tag: "PURR & CHILL",
    col: "#e879f9"
  },
  {
    id: 'lofi_polaroid_memories',
    name: "\ud83d\udcf7 Floating Polaroid Drift",
    category: 'lofi',
    family: 'lofi',
    badge: '📷',
    desc: "Nostalgic instant film photo borders floating with soft sepia flash on kick drums.",
    tag: "POLAROID",
    col: "#a855f7"
  },
  {
    id: 'lofi_cassette_pencil_rewind',
    name: "\u270f\ufe0f Cassette Tape Pencil Spool",
    category: 'lofi',
    family: 'lofi',
    badge: '✏️',
    desc: "Vintage magnetic tape winding gently around vintage yellow pencil.",
    tag: "REWIND TAPE",
    col: "#9333ea"
  },
  {
    id: 'lofi_boombox_equalizer',
    name: "\ud83d\udcfb 80s Boombox Equalizer Tape",
    category: 'lofi',
    family: 'lofi',
    badge: '📻',
    desc: "Chunky green and amber LED equalizer segments bouncing to cassette tape playback.",
    tag: "BOOMBOX EQ",
    col: "#22c55e"
  },
  {
    id: 'lofi_crt_phosphor',
    name: "\ud83d\udcfa CRT Phosphor Scanline Glow",
    category: 'lofi',
    family: 'lofi',
    badge: '📺',
    desc: "Curved glass CRT cathode ray tube glowing with green amber phosphor trails.",
    tag: "CRT PHOSPHOR",
    col: "#4ade80"
  },
  {
    id: 'lofi_walkman_foam',
    name: "\ud83c\udfa7 Walkman Foam Headphones Pulse",
    category: 'lofi',
    family: 'lofi',
    badge: '🎧',
    desc: "Classic orange foam earcups bouncing gently on vintage chrome metal band.",
    tag: "WALKMAN FOAM",
    col: "#f97316"
  },
  {
    id: 'lofi_vending_neon',
    name: "\ud83e\udd64 Vending Machine Midnight Neon",
    category: 'lofi',
    family: 'lofi',
    badge: '🥤',
    desc: "Electric blue and red canned beverage vending machine hum in quiet alleyway.",
    tag: "VENDING NEON",
    col: "#06b6d4"
  },
  {
    id: 'lofi_laundromat_glow',
    name: "\ud83e\uddfa Empty Laundromat Hum & Glow",
    category: 'lofi',
    family: 'lofi',
    badge: '🧺',
    desc: "Rotating circular front-load washing machine glass window reflecting quiet rain.",
    tag: "LAUNDROMAT",
    col: "#38bdf8"
  },
  {
    id: 'lofi_tin_roof_rain',
    name: "\ud83c\udf27\ufe0f Rain on Tin Roof Ripple",
    category: 'lofi',
    family: 'lofi',
    badge: '🌧️',
    desc: "Gentle continuous soothing patter of raindrops on rusty corrugated tin roof.",
    tag: "TIN ROOF RAIN",
    col: "#64748b"
  },
  {
    id: 'lofi_fairy_lights',
    name: "\ud83d\udca1 Cozy Bedroom Fairy Lights",
    category: 'lofi',
    family: 'lofi',
    badge: '💡',
    desc: "Twinkling warm yellow string lights draping lazily over bedroom bedpost.",
    tag: "FAIRY LIGHTS",
    col: "#facc15"
  },
  {
    id: 'lofi_dust_crackle',
    name: "\ud83c\udfb6 Vinyl Dust Crackle & Pop",
    category: 'lofi',
    family: 'lofi',
    badge: '🎶',
    desc: "Analog audio surface noise particles floating gracefully on slow jazz loops.",
    tag: "VINYL CRACKLE",
    col: "#d97706"
  },
  {
    id: 'lofi_chillhop_drums',
    name: "\ud83e\udd41 Lo-Fi Chillhop Drum Kit Wave",
    category: 'lofi',
    family: 'lofi',
    badge: '🥁',
    desc: "Muffled kick, dusty snare and swingy hi-hat waveforms undulating softly.",
    tag: "CHILLHOP DRUMS",
    col: "#a855f7"
  },
  {
    id: 'lofi_ramen_steam',
    name: "\ud83c\udf5c Steaming Ramen Bowl Vapor",
    category: 'lofi',
    family: 'lofi',
    badge: '🍜',
    desc: "Aromatic broth steam rising from ceramic ramen bowl at midnight kitchen counter.",
    tag: "RAMEN STEAM",
    col: "#ea580c"
  },
  {
    id: 'lofi_rooftop_chill',
    name: "\ud83c\udf03 Midnight Rooftop Balcony Chill",
    category: 'lofi',
    family: 'lofi',
    badge: '🌃',
    desc: "Distant city light reflections with cool night breeze over quiet apartment rooftop.",
    tag: "ROOFTOP CHILL",
    col: "#6366f1"
  },
  {
    id: 'lofi_galaxy_projector',
    name: "\ud83c\udf0c Starry Bedroom Galaxy Projector",
    category: 'lofi',
    family: 'lofi',
    badge: '🌌',
    desc: "Rotating nebula cloud waves illuminating ceiling in soft cyan and magenta.",
    tag: "GALAXY PROJECTOR",
    col: "#d946ef"
  },
  {
    id: 'lofi_guitar_loop',
    name: "\ud83c\udfb8 Soft Guitar Loop Ripple Wave",
    category: 'lofi',
    family: 'lofi',
    badge: '🎸',
    desc: "Warm chorus-drenched jazz chords washing outward like gentle lake ripples.",
    tag: "GUITAR LOOP",
    col: "#3b82f6"
  },
  {
    id: 'lofi_convenience_store',
    name: "\ud83c\udfea Japanese Convenience Store Glow",
    category: 'lofi',
    family: 'lofi',
    badge: '🏪',
    desc: "Bright welcoming 24/7 fluorescent light spilling onto deserted nighttime street.",
    tag: "CONVENIENCE STORE",
    col: "#f8fafc"
  },
  {
    id: 'lofi_shinjuku_lanterns',
    name: "\ud83c\udfee Shinjuku Alleyway Lanterns",
    category: 'lofi',
    family: 'lofi',
    badge: '🏮',
    desc: "Red izakaya lanterns glowing in foggy drizzle along narrow drinking alley.",
    tag: "IZAKAYA LANTERNS",
    col: "#ef4444"
  },
  {
    id: 'lofi_gameboy_screen',
    name: "\ud83c\udfae Retro Game Boy Screen Grid",
    category: 'lofi',
    family: 'lofi',
    badge: '🎮',
    desc: "Nostalgic 4-shade olive green dot matrix LCD screen with pixelated waves.",
    tag: "GAME BOY GRID",
    col: "#84cc16"
  },
  {
    id: 'lofi_typewriter_keys',
    name: "\u2328\ufe0f Vintage Typewriter Key Strips",
    category: 'lofi',
    family: 'lofi',
    badge: '⌨️',
    desc: "Round metal typewriter keys striking paper with satisfying mechanical clack.",
    tag: "TYPEWRITER KEYS",
    col: "#cbd5e1"
  },
  {
    id: 'lofi_coffee_drip',
    name: "\u2615 Coffee Drip Pour Ripple",
    category: 'lofi',
    family: 'lofi',
    badge: '☕',
    desc: "Slow spiral pour-over coffee dripping into glass carafe on morning jazz piano.",
    tag: "COFFEE DRIP",
    col: "#78350f"
  },
  {
    id: 'lofi_wind_chime',
    name: "\ud83c\udf90 Wind Chime Balcony Breeze",
    category: 'lofi',
    family: 'lofi',
    badge: '🎐',
    desc: "Glass furin wind chime swaying with paper strip in gentle summer night wind.",
    tag: "WIND CHIME",
    col: "#38bdf8"
  },
  {
    id: 'lofi_purple_neons',
    name: "\ud83e\udea7 Pastel Purple Neon Signs",
    category: 'lofi',
    family: 'lofi',
    badge: '🪧',
    desc: "Minimalist Japanese kanji neon tubes glowing with tranquil purple hue.",
    tag: "PURPLE NEONS",
    col: "#c084fc"
  },
  {
    id: 'lofi_study_desk',
    name: "\ud83d\udcdd Chill Study Desk Lamp",
    category: 'lofi',
    family: 'lofi',
    badge: '📝',
    desc: "Focused warm cone of amber light over open notebook and cup of pencils.",
    tag: "STUDY DESK",
    col: "#fbbf24"
  },
  {
    id: 'lofi_windshield_wipers',
    name: "\ud83d\ude97 Raindrops on Car Windshield",
    category: 'lofi',
    family: 'lofi',
    badge: '🚗',
    desc: "Rhythmic wiper blade arcs clearing blurry neon city reflections in drizzle.",
    tag: "WINDSHIELD RAIN",
    col: "#0ea5e9"
  },
  {
    id: 'lofi_tape_saturation',
    name: "\ud83d\udcfc Tape Saturation Warm Glow",
    category: 'lofi',
    family: 'lofi',
    badge: '📼',
    desc: "Soft warm harmonic distortion rounding off audio peaks like magnetic tape.",
    tag: "TAPE SATURATION",
    col: "#d97706"
  },
  {
    id: 'lofi_floppy_disk',
    name: "\ud83d\udcbe Floppy Disk 3.5 Spool Pulse",
    category: 'lofi',
    family: 'lofi',
    badge: '💾',
    desc: "Rotating magnetic shutter hub with nostalgic 90s computing aesthetic.",
    tag: "FLOPPY DISK",
    col: "#3b82f6"
  },
  {
    id: 'lofi_sleepy_sloth',
    name: "\ud83e\udda5 Sleepy Sloth Hammock Swing",
    category: 'lofi',
    family: 'lofi',
    badge: '🦥',
    desc: "Ultra slow, relaxed pendulum sway embodying total zero-stress serenity.",
    tag: "SLEEPY SLOTH",
    col: "#a8a29e"
  },
  {
    id: 'lofi_bicycle_ride',
    name: "\ud83d\udeb2 Midnight Bicycle Ride Glow",
    category: 'lofi',
    family: 'lofi',
    badge: '🚲',
    desc: "Flickering dynamo headlight illuminating quiet residential Tokyo streets.",
    tag: "BICYCLE RIDE",
    col: "#facc15"
  },
  {
    id: 'lofi_tape_counter',
    name: "\ud83d\udd22 Retro Walkman Tape Counter",
    category: 'lofi',
    family: 'lofi',
    badge: '🔢',
    desc: "Three mechanical plastic number reels spinning faithfully on playback.",
    tag: "TAPE COUNTER",
    col: "#e2e8f0"
  },
  {
    id: 'lofi_subway_passing',
    name: "\ud83d\ude87 Subway Window Passing Lights",
    category: 'lofi',
    family: 'lofi',
    badge: '🚇',
    desc: "Station tunnel pillars flashing past dark train window in hypnotic rhythm.",
    tag: "SUBWAY LIGHTS",
    col: "#f59e0b"
  },
  {
    id: 'lofi_tatami_tea',
    name: "\ud83c\udf75 Autumn Tea House Tatami",
    category: 'lofi',
    family: 'lofi',
    badge: '🍵',
    desc: "Woven straw mats smelling of cedar with afternoon sunbeams shifting slowly.",
    tag: "TATAMI TEA",
    col: "#65a30d"
  },
  {
    id: 'lofi_matcha_art',
    name: "\u2615 Matcha Latte Art Swirl",
    category: 'lofi',
    family: 'lofi',
    badge: '☕',
    desc: "Gentle steamed milk foam leaf pattern swirling inside dark ceramic bowl.",
    tag: "MATCHA ART",
    col: "#16a34a"
  },
  {
    id: 'lofi_lazy_clock',
    name: "\u23f0 Analog Clock Lazy Ticking",
    category: 'lofi',
    family: 'lofi',
    badge: '⏰',
    desc: "Smooth sweeping second hand circling silently without hurry in quiet room.",
    tag: "LAZY CLOCK",
    col: "#94a3b8"
  },
  {
    id: 'lofi_notebook_doodle',
    name: "\ud83d\udcd3 Dotted Notebook Doodle Drift",
    category: 'lofi',
    family: 'lofi',
    badge: '📓',
    desc: "Whimsical pen doodles of stars and clouds floating off graph paper.",
    tag: "NOTEBOOK DOODLE",
    col: "#6366f1"
  },
  {
    id: 'lofi_mechanical_clicks',
    name: "\u2328\ufe0f Mechanical Keyboard Click Wave",
    category: 'lofi',
    family: 'lofi',
    badge: '⌨️',
    desc: "Subtle tactile keypress ripples synchronizing with lo-fi snare clicks.",
    tag: "KEYBOARD CLICKS",
    col: "#cbd5e1"
  },
  {
    id: 'lofi_train_window_streak',
    name: "\ud83d\ude86 Rain on Train Window Streak",
    category: 'lofi',
    family: 'lofi',
    badge: '🚆',
    desc: "Horizontal raindrops swept across glass by high-speed train through countryside.",
    tag: "TRAIN WINDOW",
    col: "#38bdf8"
  },
  {
    id: 'lofi_floating_island',
    name: "\ud83c\udfdd\ufe0f Low-Poly Floating Island",
    category: 'lofi',
    family: 'lofi',
    badge: '🏝️',
    desc: "Pastel 3D floating island with single cherry blossom tree bobbing in clouds.",
    tag: "FLOATING ISLAND",
    col: "#f472b6"
  },
  {
    id: 'lofi_tape_label',
    name: "\ud83c\udff7\ufe0f Sunset Cassette Tape Label",
    category: 'lofi',
    family: 'lofi',
    badge: '🏷️',
    desc: "Hand-labeled mixtape with faded colored marker stripes and sweet title.",
    tag: "TAPE LABEL",
    col: "#fb923c"
  },
  {
    id: 'lofi_oversized_sweater',
    name: "\ud83e\uddf6 Cozy Oversized Sweater Warmth",
    category: 'lofi',
    family: 'lofi',
    badge: '🧶',
    desc: "Soft knit wool texture contour expanding with gentle comfort and peace.",
    tag: "SWEATER WARMTH",
    col: "#f472b6"
  },
  {
    id: 'lofi_toast_butter',
    name: "\ud83c\udf5e Warm Toast and Butter Glow",
    category: 'lofi',
    family: 'lofi',
    badge: '🍞',
    desc: "Golden crisp bread with melting golden butter aroma on quiet Sunday morning.",
    tag: "TOAST & BUTTER",
    col: "#eab308"
  },
  {
    id: 'lofi_sleeping_dog',
    name: "\ud83d\udc15 Sleeping Dog at Hearth Rug",
    category: 'lofi',
    family: 'lofi',
    badge: '🐕',
    desc: "Gentle rhythmic breathing of golden retriever resting chin on warm paws.",
    tag: "SLEEPING DOG",
    col: "#ca8a04"
  },
  {
    id: 'lofi_needle_drop',
    name: "\ud83e\udea1 Record Player Needle Drop",
    category: 'lofi',
    family: 'lofi',
    badge: '🪡',
    desc: "Diamond stylus settling into vinyl lead-in groove with satisfying warm pop.",
    tag: "NEEDLE DROP",
    col: "#e2e8f0"
  },
  {
    id: 'lofi_distant_thunder',
    name: "\u26c8\ufe0f Distant Thunder Lo-Fi Reverb",
    category: 'lofi',
    family: 'lofi',
    badge: '⛈️',
    desc: "Muffled rolling bass rumble miles away behind thick double-pane glass.",
    tag: "DISTANT THUNDER",
    col: "#475569"
  },
  {
    id: 'lofi_tree_leaves',
    name: "\ud83c\udf42 Autumn Tree Shaking Leaves",
    category: 'lofi',
    family: 'lofi',
    badge: '🍂',
    desc: "Golden maple canopy rustling softly in cool breeze, dropping single leaf.",
    tag: "SHAKING LEAVES",
    col: "#d97706"
  },
  {
    id: 'lofi_pillow_clouds',
    name: "\u2601\ufe0f Soft Fluffy Pillow Clouds",
    category: 'lofi',
    family: 'lofi',
    badge: '☁️',
    desc: "Volumetric cloud puffs drifting across a pastel lavender twilight sky.",
    tag: "PILLOW CLOUDS",
    col: "#e0e7ff"
  },
  {
    id: 'lofi_fridge_glow',
    name: "\ud83e\udd5b Midnight Snacking Fridge Glow",
    category: 'lofi',
    family: 'lofi',
    badge: '🥛',
    desc: "Warm yellow interior refrigerator bulb casting light across dark kitchen tiles.",
    tag: "FRIDGE GLOW",
    col: "#fef08a"
  },
  {
    id: 'lofi_synth_pad',
    name: "\ud83c\udfb9 Retro Synth Pad Sine Wave",
    category: 'lofi',
    family: 'lofi',
    badge: '🎹',
    desc: "Analog polysynth warm brass pads enveloping the screen in nostalgic lushness.",
    tag: "SYNTH PAD",
    col: "#a855f7"
  },
  {
    id: 'lofi_ceramic_steam',
    name: "\u2615 Ceramic Mug Steam Swirls",
    category: 'lofi',
    family: 'lofi',
    badge: '☕',
    desc: "Thin curling vapor trails tracing fluid patterns over hot chamomile tea.",
    tag: "CERAMIC STEAM",
    col: "#cbd5e1"
  },
  {
    id: 'lofi_photo_developing',
    name: "\ud83c\udf9e\ufe0f Polaroid Photo Developing",
    category: 'lofi',
    family: 'lofi',
    badge: '🎞️',
    desc: "Dark square photo gradually revealing soft blurred memory of sunset.",
    tag: "DEVELOPING PHOTO",
    col: "#a8a29e"
  },
  {
    id: 'lofi_floor_motes',
    name: "\u2728 Warm Wooden Floor Motes",
    category: 'lofi',
    family: 'lofi',
    badge: '✨',
    desc: "Golden dust motes dancing weightlessly in late afternoon sunlight beams.",
    tag: "FLOOR MOTES",
    col: "#f59e0b"
  },
  {
    id: 'lofi_arcade_attract',
    name: "\ud83d\udd79\ufe0f Retro Arcade Attract Mode",
    category: 'lofi',
    family: 'lofi',
    badge: '🕹️',
    desc: "Blinking 'INSERT COIN' text with retro synthesizer chords and scanlines.",
    tag: "ARCADE ATTRACT",
    col: "#06b6d4"
  },
  {
    id: 'lofi_umbrella_silk',
    name: "\u2614 Rain Patter on Umbrella Silk",
    category: 'lofi',
    family: 'lofi',
    badge: '☔',
    desc: "Taut umbrella canvas vibrating pleasantly with every falling rain impact.",
    tag: "UMBRELLA SILK",
    col: "#3b82f6"
  },
  {
    id: 'lofi_paper_boat',
    name: "\u26f5 Paper Boat in Gutter Stream",
    category: 'lofi',
    family: 'lofi',
    badge: '⛵',
    desc: "Folded newspaper boat sailing down rain gutter along mossy stone curb.",
    tag: "PAPER BOAT",
    col: "#f8fafc"
  },
  {
    id: 'lofi_postage_stamp',
    name: "\u2709\ufe0f Vintage Postage Stamp Collage",
    category: 'lofi',
    family: 'lofi',
    badge: '✉️',
    desc: "Perforated stamps from distant faraway countries framed in warm borders.",
    tag: "POSTAGE STAMPS",
    col: "#ca8a04"
  },
  {
    id: 'lofi_candle_wick',
    name: "\ud83d\udd6f\ufe0f Candle Wick Amber Flame",
    category: 'lofi',
    family: 'lofi',
    badge: '🕯️',
    desc: "Beeswax candle glowing steadily on nightstand filling room with honey scent.",
    tag: "CANDLE WICK",
    col: "#ea580c"
  },
  {
    id: 'lofi_fireflies_jar',
    name: "\ud83e\uded9 Drowsy Fireflies in Glass Jar",
    category: 'lofi',
    family: 'lofi',
    badge: '🫙',
    desc: "Gentle pulsing yellow-green bio-lanterns inside mason jar with perforated lid.",
    tag: "FIREFLIES JAR",
    col: "#84cc16"
  },
  {
    id: 'lofi_rhodes_chords',
    name: "\ud83c\udfb9 Soft Piano Rhodes Chords",
    category: 'lofi',
    family: 'lofi',
    badge: '🎹',
    desc: "Electric piano tines vibrating with lush stereo tremolo and warm chorus.",
    tag: "RHODES CHORDS",
    col: "#818cf8"
  },
  {
    id: 'lofi_film_countdown',
    name: "\ud83c\udfac Vintage Film Leader Countdown",
    category: 'lofi',
    family: 'lofi',
    badge: '🎬',
    desc: "Circular sweep countdown 3-2-1 with film grain, scratches and sprocket holes.",
    tag: "FILM LEADER",
    col: "#e2e8f0"
  },
  {
    id: 'lofi_boulevard_palms',
    name: "\ud83c\udf34 Sunset Boulevard Palm Silhouette",
    category: 'lofi',
    family: 'lofi',
    badge: '🌴',
    desc: "Feathered palm tree silhouettes against gradient violet and orange dusk sky.",
    tag: "BOULEVARD PALMS",
    col: "#ec4899"
  },
  {
    id: 'lofi_reading_nook',
    name: "\ud83d\udecb\ufe0f Cozy Beanbag Reading Nook",
    category: 'lofi',
    family: 'lofi',
    badge: '🛋️',
    desc: "Plush beanbag nestled between towering bookshelves with warm reading light.",
    tag: "READING NOOK",
    col: "#f59e0b"
  },
  {
    id: 'lofi_tent_canvas',
    name: "\u26fa Lofi Rain on Tent Canvas",
    category: 'lofi',
    family: 'lofi',
    badge: '⛺',
    desc: "Muffled acoustic tapping of midnight rain on waterproof camping tent.",
    tag: "TENT CANVAS",
    col: "#047857"
  },
  {
    id: 'lofi_tube_tv',
    name: "\ud83d\udcfa Retro Tube Television Hum",
    category: 'lofi',
    family: 'lofi',
    badge: '📺',
    desc: "15kHz high-frequency flyback transformer hum with warm static screen glow.",
    tag: "TUBE TV",
    col: "#38bdf8"
  },
  {
    id: 'lofi_wooden_balcony',
    name: "\ud83c\udfe1 Wooden Balcony Sunset Breeze",
    category: 'lofi',
    family: 'lofi',
    badge: '🏡',
    desc: "Creaking rustic porch boards with cool evening wind rustling wind chimes.",
    tag: "WOODEN BALCONY",
    col: "#92400e"
  },
  {
    id: 'lofi_cat_whiskers',
    name: "\ud83d\udc3e Sleeping Cat Whiskers Twitch",
    category: 'lofi',
    family: 'lofi',
    badge: '🐾',
    desc: "Soft purring vibration resonating gently on lo-fi sub-bass notes.",
    tag: "CAT WHISKERS",
    col: "#f472b6"
  },
  {
    id: 'lofi_dandelion_seeds',
    name: "\ud83c\udf3e Floating Dandelion Seeds",
    category: 'lofi',
    family: 'lofi',
    badge: '🌾',
    desc: "Silky white parachute seeds drifting lazily across sunny afternoon field.",
    tag: "DANDELION SEEDS",
    col: "#f8fafc"
  },
  {
    id: 'lofi_harbor_lighthouse',
    name: "\ud83d\uddfc Distant Harbor Lighthouse Beam",
    category: 'lofi',
    family: 'lofi',
    badge: '🗼',
    desc: "Slow rotating beam of amber light cutting through coastal night fog.",
    tag: "HARBOR LIGHT",
    col: "#fbbf24"
  },
  {
    id: 'lofi_bookshelf_cedar',
    name: "\ud83d\udcd6 Old Bookshelf Cedar Aroma",
    category: 'lofi',
    family: 'lofi',
    badge: '📖',
    desc: "Weathered leather bindings and yellowed paper pages breathing calm wisdom.",
    tag: "BOOKSHELF CEDAR",
    col: "#78350f"
  },
  {
    id: 'lofi_wool_scarf',
    name: "\ud83e\udde3 Wool Scarf in Autumn Breeze",
    category: 'lofi',
    family: 'lofi',
    badge: '🧣',
    desc: "Tartan plaid fringe dancing gently around center emblem on acoustic chords.",
    tag: "WOOL SCARF",
    col: "#b91c1c"
  },
  {
    id: 'lofi_quiet_streetlamp',
    name: "\ud83d\udca1 Quiet Neighborhood Streetlamp",
    category: 'lofi',
    family: 'lofi',
    badge: '💡',
    desc: "Single solitary lamp glowing over wet autumn sidewalk with zero traffic.",
    tag: "QUIET STREET",
    col: "#fde047"
  },
  {
    id: 'lofi_tram_bell',
    name: "\ud83d\ude8b Rainy Night Tram Bell",
    category: 'lofi',
    family: 'lofi',
    badge: '🚋',
    desc: "Warm yellow streetcar windows gliding past rain streaks with melodic chime.",
    tag: "TRAM BELL",
    col: "#38bdf8"
  },
  {
    id: 'lofi_lantern_float',
    name: "\ud83c\udfee Paper Lantern River Float",
    category: 'lofi',
    family: 'lofi',
    badge: '🏮',
    desc: "Glowing paper boats floating silently down dark river carrying quiet dreams.",
    tag: "LANTERN FLOAT",
    col: "#f97316"
  },
  {
    id: 'lofi_soap_bubbles',
    name: "\ud83e\udee7 Warm Bath Soap Bubble Drift",
    category: 'lofi',
    family: 'lofi',
    badge: '🫧',
    desc: "Iridescent soap bubbles floating weightlessly in steam-filled bathroom.",
    tag: "SOAP BUBBLES",
    col: "#c084fc"
  },
  {
    id: 'lofi_brush_snare',
    name: "\ud83e\udd41 Soft Lo-Fi Snare Brush Wave",
    category: 'lofi',
    family: 'lofi',
    badge: '🥁',
    desc: "Jazz wire brushes sweeping across coated snare drum head in 3/4 time.",
    tag: "BRUSH SNARE",
    col: "#a8a29e"
  },
  {
    id: 'lofi_kettle_whistle',
    name: "\ud83e\uded6 Electric Kettle Boil Steam",
    category: 'lofi',
    family: 'lofi',
    badge: '🫖',
    desc: "Gentle bubbling water and soft whistle announcing freshly steeped tea.",
    tag: "KETTLE STEAM",
    col: "#cbd5e1"
  },
  {
    id: 'lofi_watercolor_wash',
    name: "\ud83c\udfa8 Watercolor Palette Wash",
    category: 'lofi',
    family: 'lofi',
    badge: '🎨',
    desc: "Translucent cerulean and rose pigments blending softly on wet paper.",
    tag: "WATERCOLOR WASH",
    col: "#60a5fa"
  },
  {
    id: 'lofi_dial_phone',
    name: "\u260e\ufe0f Retro Dial Telephone Ring",
    category: 'lofi',
    family: 'lofi',
    badge: '☎️',
    desc: "Heavy rotary phone mechanical spin with nostalgic dual bell chime.",
    tag: "DIAL PHONE",
    col: "#dc2626"
  },
  {
    id: 'lofi_dew_sill',
    name: "\ud83c\udf43 Morning Dew on Window Sill",
    category: 'lofi',
    family: 'lofi',
    badge: '🍃',
    desc: "Crystal water spheres trembling on painted wooden sill as dawn breaks.",
    tag: "DEW SILL",
    col: "#10b981"
  },
  {
    id: 'lofi_feather_breeze',
    name: "\ud83e\udeb6 Floating Feather in Breeze",
    category: 'lofi',
    family: 'lofi',
    badge: '🪶',
    desc: "Weightless pigeon feather floating and turning in slow peaceful spirals.",
    tag: "FEATHER BREEZE",
    col: "#f8fafc"
  },
  {
    id: 'lofi_gramophone_horn',
    name: "\ud83c\udfba Vintage Gramophone Brass Horn",
    category: 'lofi',
    family: 'lofi',
    badge: '🎺',
    desc: "Polished fluted brass horn projecting warm bandpass-filtered acoustic charm.",
    tag: "GRAMOPHONE HORN",
    col: "#eab308"
  },
  {
    id: 'lofi_horizon_gradient',
    name: "\ud83c\udf05 Pastel Sunset Horizon Gradient",
    category: 'lofi',
    family: 'lofi',
    badge: '🌅',
    desc: "Seamless blend of blush pink, lavender, and midnight blue across bottom third.",
    tag: "HORIZON GRADIENT",
    col: "#f472b6"
  },
  {
    id: 'lofi_midnight_skyline',
    name: "\ud83c\udfd9\ufe0f Sleepy Town Midnight Skyline",
    category: 'lofi',
    family: 'lofi',
    badge: '🏙️',
    desc: "Small coastal town with scattered warm windows sleeping under starry sky.",
    tag: "MIDNIGHT SKYLINE",
    col: "#312e81"
  },
  {
    id: 'lofi_groove_outro',
    name: "\ud83d\udcbf Quiet Vinyl Groove Outro",
    category: 'lofi',
    family: 'lofi',
    badge: '💿',
    desc: "Tone arm resting in concentric locked run-out groove with rhythmic thump.",
    tag: "GROOVE OUTRO",
    col: "#475569"
  },
  {
    id: 'lofi_breathing_lullaby',
    name: "\ud83d\udca4 Soft Breathing Sleep Lullaby",
    category: 'lofi',
    family: 'lofi',
    badge: '💤',
    desc: "Gentle periodic luminosity wave soothing tired minds into sweet dreams.",
    tag: "SLEEP LULLABY",
    col: "#a78bfa"
  },
  {
    id: 'lofi_infinite_chill',
    name: "\ud83c\udfa7 Infinite Lo-Fi Beats to Relax",
    category: 'lofi',
    family: 'lofi',
    badge: '🎧',
    desc: "Perpetual harmonious flow of chilled rhythm, nostalgic warmth and serenity.",
    tag: "INFINITE CHILL",
    col: "#a855f7"
  },
  {
    id: 'party_auto',
    name: "\ud83c\udfb2 Auto Party Reactor (Random Shuffle)",
    category: 'party',
    family: 'party',
    badge: '🎲',
    desc: "Automatic selection: Club & EDM party ke liye lasers, shockwaves aur strobes auto-shuffle honge!",
    tag: "AUTO DEFAULT",
    col: "#00f2fe"
  },
  {
    id: 'laser_strobe',
    name: "\ud83d\udd26 Cyber Laser Stage Strobes",
    category: 'party',
    family: 'party',
    badge: '🔦',
    desc: "Rave club concert laser beams sweeping in multi-fan formations across the screen.",
    tag: "LASER BEAMS",
    col: "#00f2fe"
  },
  {
    id: 'party_shockwave_blast',
    name: "\ud83d\udca5 Multi-Ring Sonic Bass Shockwave",
    category: 'party',
    family: 'party',
    badge: '💥',
    desc: "Triple high-velocity circular sonic pressure rings expanding outward on heavy bass drops.",
    tag: "SHOCKWAVE",
    col: "#ec4899"
  },
  {
    id: 'party_neon_laser_grid',
    name: "\ud83c\udf10 Neon Club 3D Laser Ceiling Grid",
    category: 'party',
    family: 'party',
    badge: '🌐',
    desc: "Sweeping cyberpunk club ceiling laser matrix illuminating the venue in synchronized grid lines.",
    tag: "LASER GRID",
    col: "#a855f7"
  },
  {
    id: 'party_plasma_arc',
    name: "\u26a1 High-Voltage Plasma Arc Reactor",
    category: 'party',
    family: 'party',
    badge: '⚡',
    desc: "Electric tesla coil arcs leaping between electrodes with crackling violet lightning bolts.",
    tag: "PLASMA ARC",
    col: "#38bdf8"
  },
  {
    id: 'party_acid_equalizer',
    name: "\ud83d\udfe2 Acid Glow Dual Equalizer",
    category: 'party',
    family: 'party',
    badge: '🟢',
    desc: "Toxic green and electric cyan frequency towers pulsing to 140 BPM techno basslines.",
    tag: "ACID EQUALIZER",
    col: "#22c55e"
  },
  {
    id: 'party_edm_radial_ring',
    name: "\u2b55 Ultra EDM 360\u00b0 Circular Ring",
    category: 'party',
    family: 'party',
    badge: '⭕',
    desc: "360-degree dense radial audio equalizer needles exploding outward with bass frequency spikes.",
    tag: "EDM 360",
    col: "#e11d48"
  },
  {
    id: 'party_strobe_pulsar',
    name: "\ud83c\udf86 Festival Strobe Fireworks Pulsar",
    category: 'party',
    family: 'party',
    badge: '🎆',
    desc: "High-speed white and neon strobing flashes simulating mainstage Tomorrowland pyrotechnics.",
    tag: "FESTIVAL STROBE",
    col: "#fbbf24"
  },
  {
    id: 'party_bass_cannon',
    name: "\ud83d\udd0a Subwoofer Pressure Cannon",
    category: 'party',
    family: 'party',
    badge: '🔊',
    desc: "Concentric audio pressure cones vibrating violently on sub-bass drops with RGB chromatic flash.",
    tag: "BASS CANNON",
    col: "#f97316"
  },
  {
    id: 'party_equalizer_dome',
    name: "\ud83c\udf10 Neon Equalizer Dome Arena",
    category: 'party',
    family: 'party',
    badge: '🌐',
    desc: "3D hemispherical dome of pulsating audio spectrum towers creating an immersive club arena.",
    tag: "SPECTRUM DOME",
    col: "#8b5cf6"
  },
  {
    id: 'party_rainbow_strobe',
    name: "\ud83c\udf08 Spectrum Prism Laser Fan",
    category: 'party',
    family: 'party',
    badge: '🌈',
    desc: "Full-spectrum RGB rainbow laser fans spreading across the ceiling in synchronized sweep.",
    tag: "RAINBOW FAN",
    col: "#06b6d4"
  },
  {
    id: 'party_cyber_laser_fan',
    name: "\ud83e\udead Cyberpunk Multi-Beam Fan",
    category: 'party',
    family: 'party',
    badge: '🪭',
    desc: "16 high-intensity cyan laser shafts rotating in opposite directions with angular precision.",
    tag: "BEAM FAN",
    col: "#00f2fe"
  },
  {
    id: 'party_hyper_drop',
    name: "\ud83d\ude80 150 BPM Bass Drop Sonic Cone",
    category: 'party',
    family: 'party',
    badge: '🚀',
    desc: "Extreme screen-wide chromatic blast with warp-speed tunnel expansion on the main build-up drop.",
    tag: "HYPER DROP",
    col: "#f43f5e"
  },
  {
    id: 'party_acid_orbit',
    name: "\ud83e\uddea Acid Glow Dual Ring Orbit",
    category: 'party',
    family: 'party',
    badge: '🧪',
    desc: "Intersecting fluorescent yellow and ultraviolet rings spinning with intense party energy.",
    tag: "ACID ORBIT",
    col: "#eab308"
  },
  {
    id: 'party_sub_woofer_vibration',
    name: "\ud83d\udd0a 1000W Subwoofer Cone Vibration",
    category: 'party',
    family: 'party',
    badge: '🔊',
    desc: "Mechanical speaker cone punching forward with extreme air displacement rings.",
    tag: "SUB CONE",
    col: "#06b6d4"
  },
  {
    id: 'party_las_vegas_neon_strip',
    name: "\ud83c\udfb0 Cyber Neon Strip Marquee",
    category: 'party',
    family: 'party',
    badge: '🎰',
    desc: "Multi-colored blinking neon signage tube flashing in hyper-speed sync.",
    tag: "VEGAS NEON",
    col: "#ec4899"
  },
  {
    id: 'party_co2_cryo_cannon',
    name: "\ud83d\udca8 Festival CO2 Cryo Blast",
    category: 'party',
    family: 'party',
    badge: '💨',
    desc: "High-pressure white cold fog jets erupting upward on massive bass drop.",
    tag: "CRYO CANNON",
    col: "#38bdf8"
  },
  {
    id: 'party_prism_confetti_drop',
    name: "\ud83c\udf8a Holographic Laser Confetti",
    category: 'party',
    family: 'party',
    badge: '🎊',
    desc: "Thousands of reflective metallic foil flakes catching multi-colored lasers.",
    tag: "CONFETTI DROP",
    col: "#a855f7"
  },
  {
    id: 'party_rave_glowsticks',
    name: "\ud83e\ude84 Dual Neon Glowstick Trails",
    category: 'party',
    family: 'party',
    badge: '🪄',
    desc: "Neon green and electric pink trails tracing hypnotic orbital figure-8 patterns.",
    tag: "GLOWSTICKS",
    col: "#22c55e"
  },
  {
    id: 'party_flame_thrower_burst',
    name: "\ud83d\udd25 Stage Pyro Flame Cannon",
    category: 'party',
    family: 'party',
    badge: '🔥',
    desc: "Controlled concert flame bursts shooting skyward on 128 BPM build-up.",
    tag: "STAGE PYRO",
    col: "#f97316"
  },
  {
    id: 'party_tomorrowland_fireworks',
    name: "\ud83c\udf86 Tomorrowland Mainstage Fireworks",
    category: 'party',
    family: 'party',
    badge: '🎆',
    desc: "Grand finale fireworks canopy lighting up festival sky with synchronized bass.",
    tag: "MAINSTAGE PYRO",
    col: "#facc15"
  },
  {
    id: 'party_scanner_beams',
    name: "\ud83d\udd26 Moving Head Scanner Beams",
    category: 'party',
    family: 'party',
    badge: '🔦',
    desc: "Motorized arena concert moving head spotlights sweeping frantically across dancefloor.",
    tag: "SCANNER BEAMS",
    col: "#38bdf8"
  },
  {
    id: 'party_berlin_techno_grid',
    name: "\ud83e\uddf1 Berlin Underground Techno Grid",
    category: 'party',
    family: 'party',
    badge: '🧱',
    desc: "Dark industrial concrete bunker with pulsing monochromatic white strobe lasers.",
    tag: "BERLIN TECHNO",
    col: "#ffffff"
  },
  {
    id: 'party_psytrance_mandala',
    name: "\ud83c\udf00 138 BPM Psytrance Mandala",
    category: 'party',
    family: 'party',
    badge: '🌀',
    desc: "Sacred psychedelic fluorescent UV mandala spinning at blinding 138 BPM speed.",
    tag: "PSYTRANCE MANDALA",
    col: "#a855f7"
  },
  {
    id: 'party_strobe_shutter_wave',
    name: "\u26a1 Neon Strobe Shutter Wave",
    category: 'party',
    family: 'party',
    badge: '⚡',
    desc: "Linear strobe shutters firing in rolling horizontal wave across the frame.",
    tag: "STROBE SHUTTER",
    col: "#00f2fe"
  },
  {
    id: 'party_air_displacement',
    name: "\ud83d\udca8 Sub-Bass Air Displacement Rings",
    category: 'party',
    family: 'party',
    badge: '💨',
    desc: "Atmospheric shock refraction rings expanding like sound barrier sonic booms.",
    tag: "AIR DISPLACEMENT",
    col: "#38bdf8"
  },
  {
    id: 'party_earthquake_rumble',
    name: "\ud83c\udf0d Bassbin Earthquake Low Rumble",
    category: 'party',
    family: 'party',
    badge: '🌍',
    desc: "20Hz sub-audible physical vibration rattling screen borders on kick drops.",
    tag: "EARTHQUAKE BASS",
    col: "#ef4444"
  },
  {
    id: 'party_laser_tunnel_warp',
    name: "\ud83c\udf00 Laser Tunnel Warp Velocity",
    category: 'party',
    family: 'party',
    badge: '🌀',
    desc: "Enclosed cylindrical green laser cage warping viewer into hyperspace on drops.",
    tag: "LASER TUNNEL",
    col: "#22c55e"
  },
  {
    id: 'party_holo_turntables',
    name: "\ud83c\udf9b\ufe0f Holographic DJ Turntables",
    category: 'party',
    family: 'party',
    badge: '🎛️',
    desc: "Futuristic floating turntable rings spinning with virtual audio vinyl tracks.",
    tag: "HOLO TURNTABLES",
    col: "#06b6d4"
  },
  {
    id: 'party_tube_amp_overdrive',
    name: "\ud83d\udcfb Overdrive Tube Amplifier Glow",
    category: 'party',
    family: 'party',
    badge: '📻',
    desc: "Blazing orange vacuum tubes glowing hotter as master gain pushes into overdrive.",
    tag: "TUBE OVERDRIVE",
    col: "#f97316"
  },
  {
    id: 'party_whiteout_strobe',
    name: "\u26a1 Strobe Shutter Whiteout Flash",
    category: 'party',
    family: 'party',
    badge: '⚡',
    desc: "Instant blinding 1/60th second whiteout frames on thunderous snare build-ups.",
    tag: "WHITEOUT STROBE",
    col: "#ffffff"
  },
  {
    id: 'party_blacklight_uv',
    name: "\ud83d\udfe3 Ultraviolet Blacklight Rave Tube",
    category: 'party',
    family: 'party',
    badge: '🟣',
    desc: "Deep blacklight violet illumination making fluorescent colors pop and glow.",
    tag: "BLACKLIGHT UV",
    col: "#9333ea"
  },
  {
    id: 'party_confetti_blizzard',
    name: "\u2744\ufe0f Neon Confetti Blizzard Storm",
    category: 'party',
    family: 'party',
    badge: '❄️',
    desc: "High-velocity air cannon discharging endless blizzard of holographic paper foil.",
    tag: "CONFETTI BLIZZARD",
    col: "#ec4899"
  },
  {
    id: 'party_pixel_wall_matrix',
    name: "\ud83e\uddf1 LED Pixel Wall Spectrum Matrix",
    category: 'party',
    family: 'party',
    badge: '🧱',
    desc: "Gigantic concert LED backdrop displaying audio reactive block visualizer towers.",
    tag: "LED PIXEL WALL",
    col: "#3b82f6"
  },
  {
    id: 'party_sonic_cannon',
    name: "\ud83d\udd0a Electro Shockwave Sonic Cannon",
    category: 'party',
    family: 'party',
    badge: '🔊',
    desc: "Directed acoustic directional beam creating sharp conical shockfronts on beats.",
    tag: "SONIC CANNON",
    col: "#0ea5e9"
  },
  {
    id: 'party_ibiza_sunset',
    name: "\ud83c\udf05 Ibiza Sunset Beach Strobe",
    category: 'party',
    family: 'party',
    badge: '🌅',
    desc: "Balearic sunset golden rays colliding with evening club strobes and sea spray.",
    tag: "IBIZA STROBE",
    col: "#f59e0b"
  },
  {
    id: 'party_hardstyle_punch',
    name: "\ud83e\udd4a Hardstyle Kick Punch Rings",
    category: 'party',
    family: 'party',
    badge: '🥊',
    desc: "Brutal distorted reverse bass kick punches pushing camera lens back on each beat.",
    tag: "HARDSTYLE PUNCH",
    col: "#dc2626"
  },
  {
    id: 'party_synthwave_palms',
    name: "\ud83c\udf34 Synthwave Neon Palm Grid",
    category: 'party',
    family: 'party',
    badge: '🌴',
    desc: "Retro 80s outrun wireframe terrain with neon purple palm silhouettes and sun.",
    tag: "SYNTHWAVE PALMS",
    col: "#ec4899"
  },
  {
    id: 'party_kinetic_balls',
    name: "\u26aa Club Ceiling Kinetic Ball Drop",
    category: 'party',
    family: 'party',
    badge: '⚪',
    desc: "Motorized glowing LED sphere arrays undulating like ocean waves from ceiling.",
    tag: "KINETIC BALLS",
    col: "#e0e7ff"
  },
  {
    id: 'party_visor_hud',
    name: "\ud83e\udd7d Cyber Visor HUD Equalizer",
    category: 'party',
    family: 'party',
    badge: '🥽',
    desc: "Futuristic cyberpunk rave goggles displaying floating audio telemetry bars.",
    tag: "CYBER VISOR",
    col: "#00f2fe"
  },
  {
    id: 'party_radioactive_sphere',
    name: "\u2622\ufe0f Radioactive Rave Plasma Ball",
    category: 'party',
    family: 'party',
    badge: '☢️',
    desc: "Glowing glass sphere shooting electric neon tentacles towards the avatar logo.",
    tag: "PLASMA SPHERE",
    col: "#84cc16"
  },
  {
    id: 'party_laser_vortex',
    name: "\ud83c\udf2a\ufe0f Hyper-Speed Laser Vortex",
    category: 'party',
    family: 'party',
    badge: '🌪️',
    desc: "Conical swirling tornado of multi-color laser beams spinning around center.",
    tag: "LASER VORTEX",
    col: "#38bdf8"
  },
  {
    id: 'party_dual_sub_stereo',
    name: "\ud83d\udd0a Dual Subwoofer Stereo Punch",
    category: 'party',
    family: 'party',
    badge: '🔊',
    desc: "Left and right audio pressure bulges alternating with stereophonic basslines.",
    tag: "DUAL SUB STEREO",
    col: "#a855f7"
  },
  {
    id: 'party_megawatt_generator',
    name: "\u26a1 Neon Megawatt Power Generator",
    category: 'party',
    family: 'party',
    badge: '⚡',
    desc: "Industrial turbine dynamo humming with high-voltage electricity and sparks.",
    tag: "MEGAWATT DYNAMO",
    col: "#06b6d4"
  },
  {
    id: 'party_laser_harpsichord',
    name: "\ud83e\ude95 Laser Harpsichord Energy Strings",
    category: 'party',
    family: 'party',
    badge: '🪕',
    desc: "Interactive vertical laser strings plucked by audio frequencies like a harp.",
    tag: "LASER HARP",
    col: "#22d3ee"
  },
  {
    id: 'party_blackhole_suction',
    name: "\ud83d\udd73\ufe0f Bass Drop Black Hole Suction",
    category: 'party',
    family: 'party',
    badge: '🕳️',
    desc: "Gravitational lens warping space-time and pulling particles in on build-up pause.",
    tag: "BLACK HOLE BASS",
    col: "#0f172a"
  },
  {
    id: 'party_tesla_coil',
    name: "\u26a1 Electric Tesla Lightning Coil",
    category: 'party',
    family: 'party',
    badge: '⚡',
    desc: "Resonant transformer discharging 10-foot purple lightning bolts to metal cage.",
    tag: "TESLA COIL",
    col: "#c084fc"
  },
  {
    id: 'party_warehouse_truss',
    name: "\ud83c\udfd7\ufe0f Rave Warehouse Iron Truss Beams",
    category: 'party',
    family: 'party',
    badge: '🏗️',
    desc: "Heavy structural stage scaffolding bathed in pulsing red and blue spotlights.",
    tag: "WAREHOUSE TRUSS",
    col: "#475569"
  },
  {
    id: 'party_toxic_strobe',
    name: "\ud83e\uddea Toxic Green Strobe Flare",
    category: 'party',
    family: 'party',
    badge: '🧪',
    desc: "Intense neon chartreuse flashes illuminating the crowd with radioactive energy.",
    tag: "TOXIC STROBE",
    col: "#84cc16"
  },
  {
    id: 'party_dancefloor_tiles',
    name: "\ud83d\udd32 Neon Cyberpunk Dancefloor Floor",
    category: 'party',
    family: 'party',
    badge: '🔲',
    desc: "Illuminated pressure-sensitive glass tiles lighting up under dancing feet.",
    tag: "NEON DANCEFLOOR",
    col: "#ec4899"
  },
  {
    id: 'party_dnb_roller',
    name: "\ud83c\udf00 174 BPM Drum & Bass Sine Cone",
    category: 'party',
    family: 'party',
    badge: '🌀',
    desc: "High-velocity jungle breakbeats driving rapid-fire shockwave pulses.",
    tag: "174 DNB ROLLER",
    col: "#f97316"
  },
  {
    id: 'party_trance_solar',
    name: "\u2600\ufe0f Trance Uplifting Solar Corona",
    category: 'party',
    family: 'party',
    badge: '☀️',
    desc: "Euphoric melodic trance breakdown radiating heavenly golden sunlight rays.",
    tag: "TRANCE CORONA",
    col: "#fbbf24"
  },
  {
    id: 'party_dubstep_wobble',
    name: "\ud83e\udd96 Dubstep Wobble Bass Shockwave",
    category: 'party',
    family: 'party',
    badge: '🦖',
    desc: "LFO-modulated mechanical growl tearing across the screen with violent vibration.",
    tag: "WOBBLE BASS",
    col: "#10b981"
  },
  {
    id: 'party_trap_horn_blast',
    name: "\ud83c\udfba Trap 808 Distorted Horn Blast",
    category: 'party',
    family: 'party',
    badge: '🎺',
    desc: "Iconic stadium synth horn blast paired with seismic 808 sub-bass punch.",
    tag: "TRAP HORN",
    col: "#ef4444"
  },
  {
    id: 'party_melbourne_bounce',
    name: "\ud83e\udd98 Melbourne Bounce Laser Fan",
    category: 'party',
    family: 'party',
    badge: '🦘',
    desc: "Off-beat pumping basslines with synchronized jumping laser fans.",
    tag: "MELBOURNE BOUNCE",
    col: "#06b6d4"
  },
  {
    id: 'party_future_rave_arch',
    name: "\u26e9\ufe0f Future Rave Neon Archway",
    category: 'party',
    family: 'party',
    badge: '⛩️',
    desc: "David Guetta & Morten style dark futuristic cyberpunk cathedral arches.",
    tag: "FUTURE RAVE",
    col: "#38bdf8"
  },
  {
    id: 'party_bass_house_speaker',
    name: "\ud83c\udfe0 Bass House Pumping Speaker",
    category: 'party',
    family: 'party',
    badge: '🏠',
    desc: "Groovy 126 BPM low-slung house groove rattling giant wooden bass bins.",
    tag: "BASS HOUSE",
    col: "#eab308"
  },
  {
    id: 'party_dj_hologram',
    name: "\ud83d\udc64 Cybernetic DJ Hologram Core",
    category: 'party',
    family: 'party',
    badge: '👤',
    desc: "Futuristic android DJ silhouette raising hands as the stadium erupts.",
    tag: "DJ HOLOGRAM",
    col: "#00f2fe"
  },
  {
    id: 'party_xenon_flasher',
    name: "\ud83d\udca1 High-Intensity Xenon Flasher",
    category: 'party',
    family: 'party',
    badge: '💡',
    desc: "Ultra-bright aircraft warning style xenon flashes cutting through darkness.",
    tag: "XENON FLASHER",
    col: "#ffffff"
  },
  {
    id: 'party_nitrogen_geyser',
    name: "\ud83d\udca8 Neon Liquid Nitrogen Geyser",
    category: 'party',
    family: 'party',
    badge: '💨',
    desc: "Plumes of freezing white fog illuminated from within by high-power RGB LEDs.",
    tag: "NITROGEN GEYSER",
    col: "#38bdf8"
  },
  {
    id: 'party_dancefloor_scan',
    name: "\ud83c\udf08 Rainbow Prism Dancefloor Scan",
    category: 'party',
    family: 'party',
    badge: '🌈',
    desc: "Full-spectrum rainbow laser line scanning rapidly back and forth across crowd.",
    tag: "RAINBOW SCAN",
    col: "#a855f7"
  },
  {
    id: 'party_acid_303_ribbon',
    name: "\ud83c\udf9b\ufe0f 303 Acid Synth Waveform Ribbon",
    category: 'party',
    family: 'party',
    badge: '🎛️',
    desc: "Resonant squelchy Roland TB-303 filter sweeps twisting into glowing ribbon.",
    tag: "ACID 303",
    col: "#84cc16"
  },
  {
    id: 'party_ultra_pyro_wall',
    name: "\ud83d\udd25 Ultra Music Festival Pyro Wall",
    category: 'party',
    family: 'party',
    badge: '🔥',
    desc: "Continuous wall of stage flames shooting 30 feet into the night sky.",
    tag: "PYRO WALL",
    col: "#ea580c"
  },
  {
    id: 'party_flame_mortar',
    name: "\ud83c\udf86 Stage Flame Mortar Blast",
    category: 'party',
    family: 'party',
    badge: '🎆',
    desc: "Individual fireballs launching upward on every kick drum impact.",
    tag: "FLAME MORTAR",
    col: "#dc2626"
  },
  {
    id: 'party_led_wristbands',
    name: "\u2728 Strobe LED Wristband Matrix",
    category: 'party',
    family: 'party',
    badge: '✨',
    desc: "100,000 stadium crowd wristbands flashing in synchronized rainbow waves.",
    tag: "WRISTBAND MATRIX",
    col: "#ec4899"
  },
  {
    id: 'party_gas_mask_rave',
    name: "\ud83e\udd3f Cyber Rave Gas Mask Reactor",
    category: 'party',
    family: 'party',
    badge: '🤿',
    desc: "Futuristic rave respirator with dual glowing neon intake filters.",
    tag: "GAS MASK RAVE",
    col: "#06b6d4"
  },
  {
    id: 'party_bassquake_stadium',
    name: "\ud83c\udfdf\ufe0f Bassquake Stadium Shaker",
    category: 'party',
    family: 'party',
    badge: '🏟️',
    desc: "Concert stadium arena vibrating so hard that lens focus blurs on drops.",
    tag: "BASSQUAKE",
    col: "#e11d48"
  },
  {
    id: 'party_laser_spiderweb',
    name: "\ud83d\udd78\ufe0f Neon Laser Spider Web",
    category: 'party',
    family: 'party',
    badge: '🕸️',
    desc: "Intricate geometric laser web forming an impenetrable cage of neon light.",
    tag: "LASER SPIDERWEB",
    col: "#22c55e"
  },
  {
    id: 'party_rigging_grid',
    name: "\ud83c\udfd7\ufe0f Multi-Tier Concert Rigging Grid",
    category: 'party',
    family: 'party',
    badge: '🏗️',
    desc: "Complex truss grid suspending hundreds of moving lights and laser arrays.",
    tag: "RIGGING GRID",
    col: "#64748b"
  },
  {
    id: 'party_cryo_horizon',
    name: "\ud83c\udf2b\ufe0f Sub-Zero Cryo Cloud Horizon",
    category: 'party',
    family: 'party',
    badge: '🌫️',
    desc: "Dense blanket of cold dry ice smoke rolling off stage into audience.",
    tag: "CRYO HORIZON",
    col: "#e0f2fe"
  },
  {
    id: 'party_holo_dancer',
    name: "\ud83d\udc83 Holographic Geometric Dancer",
    category: 'party',
    family: 'party',
    badge: '💃',
    desc: "Wireframe 3D dancer performing fluid rave moves to the rhythm.",
    tag: "HOLO DANCER",
    col: "#f472b6"
  },
  {
    id: 'party_arc_welder_sparks',
    name: "\u26a1 Electric Arc Welder Spark Shower",
    category: 'party',
    family: 'party',
    badge: '⚡',
    desc: "Brilliant shower of golden sparks spraying across screen on build-up peak.",
    tag: "SPARK SHOWER",
    col: "#facc15"
  },
  {
    id: 'party_beacon_tower',
    name: "\ud83d\uddfc Strobe Beacon Tower Scanner",
    category: 'party',
    family: 'party',
    badge: '🗼',
    desc: "Rotating 360-degree high-power beacon light sweeping across horizon.",
    tag: "BEACON TOWER",
    col: "#38bdf8"
  },
  {
    id: 'party_distortion_clipper',
    name: "\ud83d\udcc8 Bass Distortion Wave Clipper",
    category: 'party',
    family: 'party',
    badge: '📈',
    desc: "Square-wave clipped audio waveform glowing red hot with aggressive energy.",
    tag: "WAVE CLIPPER",
    col: "#ef4444"
  },
  {
    id: 'party_fluorescent_tubes',
    name: "\ud83d\udca1 Neon Fluorescent Light Tubes",
    category: 'party',
    family: 'party',
    badge: '💡',
    desc: "Flickering colored tube lights buzzing and flashing to breakbeat rhythms.",
    tag: "FLUORESCENT TUBES",
    col: "#a855f7"
  },
  {
    id: 'party_rave_whistle',
    name: "\ud83d\udcef Rave Whistle Sonic Ripple",
    category: 'party',
    family: 'party',
    badge: '📯',
    desc: "High-frequency sonic chirp dispersing circular shockwaves on top of bass.",
    tag: "RAVE WHISTLE",
    col: "#facc15"
  },
  {
    id: 'party_alley_neon',
    name: "\ud83c\udf06 Cyberpunk Club Alley Neon",
    category: 'party',
    family: 'party',
    badge: '🌆',
    desc: "Damp alleyway walls reflecting pulsing red, cyan, and amber club signage.",
    tag: "ALLEY NEON",
    col: "#06b6d4"
  },
  {
    id: 'party_kaleidoscope_laser',
    name: "\ud83d\udd2e Laser Kaleidoscope Tunnel",
    category: 'party',
    family: 'party',
    badge: '🔮',
    desc: "Hexagonal mirror prism multiplying laser beams into infinite starry arrays.",
    tag: "KALEIDOSCOPE LASER",
    col: "#c084fc"
  },
  {
    id: 'party_speaker_excursion',
    name: "\ud83d\udd0a Subwoofer Diaphragm Extreme Excursion",
    category: 'party',
    family: 'party',
    badge: '🔊',
    desc: "High-speed camera view of rubber speaker surround flexing on 30Hz note.",
    tag: "SPEAKER EXCURSION",
    col: "#f97316"
  },
  {
    id: 'party_acid_smiley',
    name: "\ud83d\ude42 Acid Smiley Face Neon Icon",
    category: 'party',
    family: 'party',
    badge: '🙂',
    desc: "Classic 90s acid house yellow smiley face pulsing with neon halo.",
    tag: "ACID SMILEY",
    col: "#fde047"
  },
  {
    id: 'party_led_glitch',
    name: "\ud83d\udcfa LED Screen Wall Glitch Burst",
    category: 'party',
    family: 'party',
    badge: '📺',
    desc: "Digital video glitch artifacts fracturing screen on snare rolls.",
    tag: "LED GLITCH",
    col: "#00f2fe"
  },
  {
    id: 'party_tach_redline',
    name: "\ud83c\udfce\ufe0f High-BPM Tachometer Redline",
    category: 'party',
    family: 'party',
    badge: '🏎️',
    desc: "Needle buried at 10,000 RPM flashing bright red warning lights on drop.",
    tag: "TACH REDLINE",
    col: "#dc2626"
  },
  {
    id: 'party_static_discharge',
    name: "\u26a1 Electro Static Discharge Ring",
    category: 'party',
    family: 'party',
    badge: '⚡',
    desc: "Concentric ring of crackling electric blue sparks expanding outward.",
    tag: "STATIC DISCHARGE",
    col: "#38bdf8"
  },
  {
    id: 'party_stage_fog_sheet',
    name: "\ud83c\udf2b\ufe0f Stage Fog Laser Sheets",
    category: 'party',
    family: 'party',
    badge: '🌫️',
    desc: "Solid flat planes of green laser light slicing through swirling smoke.",
    tag: "LASER SHEETS",
    col: "#22c55e"
  },
  {
    id: 'party_sonic_boom_cone',
    name: "\u2708\ufe0f Sonic Boom Atmospheric Cone",
    category: 'party',
    family: 'party',
    badge: '✈️',
    desc: "Transonic vapor cloud forming and exploding behind center logo.",
    tag: "SONIC BOOM",
    col: "#e2e8f0"
  },
  {
    id: 'party_tribal_markings',
    name: "\ud83c\udfa8 Neon Tribal Festival Markings",
    category: 'party',
    family: 'party',
    badge: '🎨',
    desc: "Fluorescent body paint designs glowing brilliantly under UV lights.",
    tag: "TRIBAL NEON",
    col: "#ec4899"
  },
  {
    id: 'party_laser_chandelier',
    name: "\ud83d\udd2e Rave Party Laser Chandelier",
    category: 'party',
    family: 'party',
    badge: '🔮',
    desc: "Central ceiling fixture projecting hundreds of pin-sharp beam needles.",
    tag: "LASER CHANDELIER",
    col: "#a855f7"
  },
  {
    id: 'party_multi_color_strobe',
    name: "\ud83d\udea5 Multi-Color Strobe Cannon",
    category: 'party',
    family: 'party',
    badge: '🚥',
    desc: "High-frequency strobes alternating between cyan, magenta, and yellow.",
    tag: "MULTI STROBE",
    col: "#f43f5e"
  },
  {
    id: 'party_resonance_chamber',
    name: "\ud83c\udfdb\ufe0f Bass Resonance Chamber Wall",
    category: 'party',
    family: 'party',
    badge: '🏛️',
    desc: "Acoustically tuned resonant chamber vibrating with pure physical bass.",
    tag: "RESONANCE CHAMBER",
    col: "#7c3aed"
  },
  {
    id: 'party_cyberdeck_eq',
    name: "\ud83d\udcbb Cybernetic Cyberdeck Equalizer",
    category: 'party',
    family: 'party',
    badge: '💻',
    desc: "Hacker deck interface monitoring real-time frequency spectrum channels.",
    tag: "CYBERDECK EQ",
    col: "#10b981"
  },
  {
    id: 'party_liquid_neon',
    name: "\ud83e\uddea Liquid Neon Glow Fluid",
    category: 'party',
    family: 'party',
    badge: '🧪',
    desc: "Fluorescent viscous glowing liquid splashing in slow motion to the beat.",
    tag: "LIQUID NEON",
    col: "#06b6d4"
  },
  {
    id: 'party_blue_lightning',
    name: "\u26a1 Electric Blue Strobe Lightning",
    category: 'party',
    family: 'party',
    badge: '⚡',
    desc: "Forked lightning branches flashing across the dark club ceiling.",
    tag: "BLUE LIGHTNING",
    col: "#3b82f6"
  },
  {
    id: 'party_metal_double_bass',
    name: "\ud83e\udd41 Heavy Metal Double Bass Blast",
    category: 'party',
    family: 'party',
    badge: '🥁',
    desc: "Rapid-fire 16th note double kick drum cannons vibrating the room.",
    tag: "DOUBLE BASS",
    col: "#ef4444"
  },
  {
    id: 'party_hard_techno_bunker',
    name: "\ud83e\uddf1 Hard Techno Concrete Bunker Pulse",
    category: 'party',
    family: 'party',
    badge: '🧱',
    desc: "Raw unadorned industrial techno aesthetics with relentless 4/4 pounding.",
    tag: "TECHNO BUNKER",
    col: "#475569"
  },
  {
    id: 'party_strobe_accelerometer',
    name: "\ud83d\ude80 Neon Ring Strobe Accelerometer",
    category: 'party',
    family: 'party',
    badge: '🚀',
    desc: "Concentric strobe rings accelerating faster and faster toward the drop.",
    tag: "STROBE ACCEL",
    col: "#facc15"
  },
  {
    id: 'party_rave_horn',
    name: "\ud83d\udcef Rave Horn Audio Shockwave",
    category: 'party',
    family: 'party',
    badge: '📯',
    desc: "Jamaican sound system air horn blast reverberating over massive bassline.",
    tag: "RAVE HORN",
    col: "#ea580c"
  },
  {
    id: 'party_sound_system_wall',
    name: "\ud83e\uddf1 Stadium Sound System Wall",
    category: 'party',
    family: 'party',
    badge: '🧱',
    desc: "Towering stack of folded horn subwoofers vibrating the very earth.",
    tag: "SOUND WALL",
    col: "#1e293b"
  },
  {
    id: 'party_laser_aurora',
    name: "\ud83c\udf0c Laser Ceiling Aurora Projection",
    category: 'party',
    family: 'party',
    badge: '🌌',
    desc: "Shimmering horizontal laser curtain simulating northern lights indoors.",
    tag: "LASER AURORA",
    col: "#00f2fe"
  },
  {
    id: 'party_sparkler_cannon',
    name: "\u2728 High-Velocity Sparkler Cannon",
    category: 'party',
    family: 'party',
    badge: '✨',
    desc: "Titanium cold spark machines shooting geysers of brilliant golden fire.",
    tag: "SPARK CANNON",
    col: "#fbbf24"
  },
  {
    id: 'party_mainstage_drop',
    name: "\ud83d\ude80 Peak Energy Mainstage Drop",
    category: 'party',
    family: 'party',
    badge: '🚀',
    desc: "Total sensory convergence: lasers, cryo, fire, and screen-shaking 808 drop.",
    tag: "MAINSTAGE DROP",
    col: "#f43f5e"
  },
  {
    id: 'party_infinite_rush',
    name: "\u26a1 Infinite Rave Adrenaline Rush",
    category: 'party',
    family: 'party',
    badge: '⚡',
    desc: "Unstoppable surging party energy keeping the dancefloor moving all night.",
    tag: "INFINITE RUSH",
    col: "#00f2fe"
  },
  {
    id: 'party_cosmic_edm',
    name: "\ud83c\udf86 Cosmic EDM Ultra Reactor",
    category: 'party',
    family: 'party',
    badge: '🎆',
    desc: "Galactic festival core combining all spectrum lasers into one singularity.",
    tag: "COSMIC EDM",
    col: "#a855f7"
  },
  {
    id: 'acoustic_auto',
    name: "\ud83c\udfb2 Auto Acoustic Reactor (Random Shuffle)",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎲',
    desc: "Automatic selection: Acoustic guitar ke liye organic sine ribbon aur campfire ember auto-match honge!",
    tag: "AUTO DEFAULT",
    col: "#d97706"
  },
  {
    id: 'oscilloscope_ribbon',
    name: "\ud83c\udf0a Analog Sine Oscilloscope Ribbon",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌊',
    desc: "Smooth flowing analog sine wave ribbons curving organically around the center emblem.",
    tag: "OSCILLOSCOPE",
    col: "#38bdf8"
  },
  {
    id: 'acoustic_guitar_string',
    name: "\ud83c\udfb8 Six-String Acoustic Frequency Wave",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎸',
    desc: "Parallel vibrating golden guitar string lines displaying authentic plucked string harmonics.",
    tag: "GUITAR STRINGS",
    col: "#f59e0b"
  },
  {
    id: 'acoustic_campfire_ember',
    name: "\ud83d\udd25 Campfire Golden Ember Sparkles",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🔥',
    desc: "Warm glowing campfire embers drifting upward softly into a clear wilderness night sky.",
    tag: "CAMPFIRE",
    col: "#ea580c"
  },
  {
    id: 'acoustic_morning_dew',
    name: "\ud83c\udf43 Morning Dewdrop Circular Ripple",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🍃',
    desc: "Pristine forest water ripples reflecting emerald green leaves on delicate acoustic guitar plucks.",
    tag: "DEWDROP",
    col: "#10b981"
  },
  {
    id: 'acoustic_wood_grain',
    name: "\ud83e\udeb5 Organic Wooden Tone Ring",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪵',
    desc: "Concentric tree ring acoustic cross-section vibrating with warm natural mahogany resonance.",
    tag: "WOOD GRAIN",
    col: "#92400e"
  },
  {
    id: 'acoustic_indie_horizon',
    name: "\ud83c\udf05 Indie Folk Sunset Horizon",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌅',
    desc: "Golden indie sunset mountain ridge with serene harmonic waveforms mirroring along the base.",
    tag: "INDIE HORIZON",
    col: "#f59e0b"
  },
  {
    id: 'acoustic_misty_road',
    name: "\ud83c\udf32 Misty Forest Road Atmospheric Echo",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌲',
    desc: "Gentle pines and pine needles swaying in misty mountain wind with tranquil audio response.",
    tag: "MISTY FOREST",
    col: "#047857"
  },
  {
    id: 'acoustic_coffee_house',
    name: "\u2615 Coffee House Warm Resonance Ring",
    category: 'acoustic',
    family: 'acoustic',
    badge: '☕',
    desc: "Intimate unplugged acoustic warmth with subtle brassy rings and rich wooden undertones.",
    tag: "COFFEE HOUSE",
    col: "#b45309"
  },
  {
    id: 'acoustic_mountain_wind',
    name: "\ud83d\udca8 Mountain Breeze Sine Oscillator",
    category: 'acoustic',
    family: 'acoustic',
    badge: '💨',
    desc: "Whispering mountain winds tracing fluid, continuous undulating sine ribbons on vocal chords.",
    tag: "MOUNTAIN BREEZE",
    col: "#0284c7"
  },
  {
    id: 'acoustic_gentle_tide',
    name: "\ud83c\udfd6\ufe0f Gentle Shoreline Tide Waveform",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🏖️',
    desc: "Rhythmic ocean foam washing gently onto golden sand in sync with acoustic strumming.",
    tag: "SHORELINE",
    col: "#06b6d4"
  },
  {
    id: 'acoustic_sunbeam_glow',
    name: "\ud83c\udf24\ufe0f Golden Sunbeam Rays Halo",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌤️',
    desc: "Peaceful sun rays breaking through morning clouds with soft, heartwarming illumination.",
    tag: "SUNBEAM",
    col: "#facc15"
  },
  {
    id: 'acoustic_wooden_cajon',
    name: "\ud83e\udd41 Acoustic Wooden Cajon Beat",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🥁',
    desc: "Resonant warm wooden hollow chamber resonance with organic acoustic thump.",
    tag: "CAJON PULSE",
    col: "#b45309"
  },
  {
    id: 'acoustic_harmonica_breeze',
    name: "\ud83c\udf2c\ufe0f Appalachian Harmonica Sine",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌬️',
    desc: "Crisp rustic blues harmonica reed vibration shimmering like golden prairie grass.",
    tag: "HARMONICA",
    col: "#d97706"
  },
  {
    id: 'acoustic_violin_bow',
    name: "\ud83c\udfbb Cello & Violin Bow Resonance",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎻',
    desc: "Rich horsehair bow friction creating rich velvet string overtones.",
    tag: "CELLO BOW",
    col: "#92400e"
  },
  {
    id: 'acoustic_fingerstyle_chords',
    name: "\ud83c\udfb6 Fingerstyle Nylon Resonance",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎶',
    desc: "Delicate classical guitar pluck ripples spreading across still mountain lake.",
    tag: "FINGERSTYLE",
    col: "#ea580c"
  },
  {
    id: 'acoustic_driftwood_bonfire',
    name: "\ud83e\udeb5 Ocean Beach Driftwood Bonfire",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪵',
    desc: "Warm coastal driftwood fire with salt-air sparks dancing upward.",
    tag: "DRIFTWOOD",
    col: "#f59e0b"
  },
  {
    id: 'acoustic_autumn_stream',
    name: "\ud83c\udf42 Crisp Mountain Brook Ripple",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🍂',
    desc: "Clear mountain stream water flowing over smooth river stones on acoustic picking.",
    tag: "BROOK STREAM",
    col: "#10b981"
  },
  {
    id: 'acoustic_banjo_twang',
    name: "\ud83e\ude95 Banjo Bluegrass Pluck Sparkles",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪕',
    desc: "Crisp metallic banjo fingerpick roll notes spraying bright golden starbursts.",
    tag: "BANJO TWANG",
    col: "#f59e0b"
  },
  {
    id: 'acoustic_12_string_shimmer',
    name: "\ud83c\udfb8 12-String Acoustic Shimmer Wave",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎸',
    desc: "Chorused octave string pairs shimmering like sunlight dancing on ocean water.",
    tag: "12-STRING SHIMMER",
    col: "#38bdf8"
  },
  {
    id: 'acoustic_ukulele_strum',
    name: "\ud83c\udfdd\ufe0f Ukulele Island Strum Waveform",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🏝️',
    desc: "Sunny tropical koa wood ukulele rhythms bringing cheerful island ocean vibes.",
    tag: "UKULELE STRUM",
    col: "#10b981"
  },
  {
    id: 'acoustic_mandolin_tremolo',
    name: "\ud83e\ude95 Mandolin Tremolo Ribbon Wave",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪕',
    desc: "Rapid double-strung mandolin tremolo picking creating delicate fluttering ribbons.",
    tag: "MANDOLIN TREMOLO",
    col: "#d97706"
  },
  {
    id: 'acoustic_upright_bass',
    name: "\ud83c\udfbb Upright Bass Pluck Resonance",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎻',
    desc: "Deep wooden double bass pizzicato thump grounding the acoustic arrangement.",
    tag: "UPRIGHT BASS",
    col: "#78350f"
  },
  {
    id: 'acoustic_dobro_resonator',
    name: "\ud83c\udfb8 Resonator Dobro Metallic Ring",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎸',
    desc: "Spun aluminum cone resonator projecting sweet sliding metallic blues tone.",
    tag: "DOBRO RESONATOR",
    col: "#cbd5e1"
  },
  {
    id: 'acoustic_soundhole_rosette',
    name: "\ud83e\ude85 Acoustic Guitar Rosette Ring",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪅',
    desc: "Inlaid mother-of-pearl and wooden rosette circle framing the center logo.",
    tag: "GUITAR ROSETTE",
    col: "#fbbf24"
  },
  {
    id: 'acoustic_pine_forest_wind',
    name: "\ud83c\udf32 Pine Needle Forest Breeze",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌲',
    desc: "Evergreen canopy swaying gently in high-altitude mountain valley air.",
    tag: "PINE FOREST",
    col: "#047857"
  },
  {
    id: 'acoustic_porch_rocking_chair',
    name: "\ud83e\ude91 Rustic Porch Rocking Chair Creak",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪑',
    desc: "Soothing rhythmic wooden creak on old oak floorboards looking over pasture.",
    tag: "ROCKING CHAIR",
    col: "#92400e"
  },
  {
    id: 'acoustic_wheat_field',
    name: "\ud83c\udf3e Golden Wheat Field Waveform",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌾',
    desc: "Endless ocean of amber grain rippling in wind like musical sound waves.",
    tag: "WHEAT FIELD",
    col: "#eab308"
  },
  {
    id: 'acoustic_leather_strap',
    name: "\ud83c\udfb8 Leather Guitar Strap Resonance",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎸',
    desc: "Worn vintage leather strap contours gently holding the acoustic rhythm.",
    tag: "LEATHER STRAP",
    col: "#78350f"
  },
  {
    id: 'acoustic_cedar_chamber',
    name: "\ud83e\udeb5 Cedar Wood Acoustic Chamber",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪵',
    desc: "Warm cedar soundboard vibrations creating rich, intimate sonic enclosure.",
    tag: "CEDAR CHAMBER",
    col: "#b45309"
  },
  {
    id: 'acoustic_folk_meadow',
    name: "\ud83c\udf3c Folk Festival Meadow Breeze",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌼',
    desc: "Outdoor acoustic stage surrounded by green hills, wildflowers and smiles.",
    tag: "FOLK MEADOW",
    col: "#84cc16"
  },
  {
    id: 'acoustic_harmonic_chime',
    name: "\ud83d\udd14 Natural Guitar Harmonic Chime",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🔔',
    desc: "Pristine bell-like 12th fret natural harmonics chiming like crystal bells.",
    tag: "HARMONIC CHIME",
    col: "#e0e7ff"
  },
  {
    id: 'acoustic_slap_guitar',
    name: "\u270b Slap Guitar Percussion Wave",
    category: 'acoustic',
    family: 'acoustic',
    badge: '✋',
    desc: "Modern fingerstyle acoustic body percussion thumps creating crisp shockwaves.",
    tag: "SLAP GUITAR",
    col: "#ea580c"
  },
  {
    id: 'acoustic_room_reverb',
    name: "\ud83c\udfdb\ufe0f Room Reverb Acoustic Tail",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🏛️',
    desc: "Natural wooden barn acoustics creating warm, lingering sonic decay tails.",
    tag: "ROOM REVERB",
    col: "#a855f7"
  },
  {
    id: 'acoustic_condenser_ribbon',
    name: "\ud83c\udf99\ufe0f Vintage Condenser Ribbon Wave",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎙️',
    desc: "Large-diaphragm warm studio tube microphone capturing every breath of sound.",
    tag: "CONDENSER MIC",
    col: "#64748b"
  },
  {
    id: 'acoustic_prairie_wind',
    name: "\ud83c\udf3e Whispering Grass Prairie Wind",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌾',
    desc: "Endless tallgrass prairie swaying gently under vast expansive blue sky.",
    tag: "PRAIRIE WIND",
    col: "#ca8a04"
  },
  {
    id: 'acoustic_mountain_dulcimer',
    name: "\ud83e\ude95 Mountain Dulcimer Drone String",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪕',
    desc: "Appalachian lap dulcimer drone harmony providing ancient mountain solace.",
    tag: "MOUNTAIN DULCIMER",
    col: "#d97706"
  },
  {
    id: 'acoustic_wooden_windmill',
    name: "\ud83d\udca8 Wooden Windmill Twilight Breeze",
    category: 'acoustic',
    family: 'acoustic',
    badge: '💨',
    desc: "Rustic farm windmill turning lazily in cool evening sunset breeze.",
    tag: "WOODEN WINDMILL",
    col: "#92400e"
  },
  {
    id: 'acoustic_barn_wood_grain',
    name: "\ud83e\udeb5 Rusted Barn Wood Grain Ring",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪵',
    desc: "Century-old weathered gray barn timber textures radiating organic beauty.",
    tag: "BARN WOOD",
    col: "#78716c"
  },
  {
    id: 'acoustic_cello_overtones',
    name: "\ud83c\udfbb Acoustic Cello Rich Overtones",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎻',
    desc: "Deep resonant wood chamber overtones vibrating with velvet richness.",
    tag: "CELLO OVERTONES",
    col: "#7c2d12"
  },
  {
    id: 'acoustic_candle_wood',
    name: "\ud83d\udd6f\ufe0f Warm Amber Candle on Wood",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🕯️',
    desc: "Single candle illuminating rustic pine tabletop with gentle golden aura.",
    tag: "CANDLE WOOD",
    col: "#f59e0b"
  },
  {
    id: 'acoustic_campfire_smoke',
    name: "\ud83d\udca8 Campfire Smoke Spiral Ascent",
    category: 'acoustic',
    family: 'acoustic',
    badge: '💨',
    desc: "Fragrant pine smoke curling lazily upward toward starry wilderness night.",
    tag: "CAMPFIRE SMOKE",
    col: "#cbd5e1"
  },
  {
    id: 'acoustic_canopy_sunbeams',
    name: "\ud83c\udf32 Forest Canopy Sunbeam Shafts",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌲',
    desc: "Pillars of morning sunlight filtering down through mossy redwood trees.",
    tag: "CANOPY SUNBEAMS",
    col: "#fef08a"
  },
  {
    id: 'acoustic_pebble_stream',
    name: "\ud83e\udea8 Clear Pebble River Current",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪨',
    desc: "Crystal-clear mountain runoff flowing smoothly over rounded river pebbles.",
    tag: "PEBBLE STREAM",
    col: "#38bdf8"
  },
  {
    id: 'acoustic_maple_drift',
    name: "\ud83c\udf41 Autumn Red Maple Leaf Drift",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🍁',
    desc: "Scarlet maple leaf floating down onto still woodland pond surface.",
    tag: "MAPLE DRIFT",
    col: "#dc2626"
  },
  {
    id: 'acoustic_wildflower_halo',
    name: "\ud83c\udf38 Wild Mountain Wildflower Halo",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌸',
    desc: "Delicate bluebells, buttercups, and clover weaving circular garland halo.",
    tag: "WILDFLOWER HALO",
    col: "#f472b6"
  },
  {
    id: 'acoustic_log_cabin',
    name: "\ud83e\udeb5 Hand-Hewn Log Cabin Warmth",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪵',
    desc: "Notched pine logs glowing with fireplace warmth amidst winter mountain chill.",
    tag: "LOG CABIN",
    col: "#92400e"
  },
  {
    id: 'acoustic_ridge_sunrise',
    name: "\ud83c\udf05 Mountain Ridge Sunrise Glow",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌅',
    desc: "First light cresting blue mountain ridges with inspiring golden illumination.",
    tag: "RIDGE SUNRISE",
    col: "#fb923c"
  },
  {
    id: 'acoustic_barn_lantern',
    name: "\ud83c\udfee Rustic Farmhouse Barn Lantern",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🏮',
    desc: "Kerosene barn lantern hanging from beam casting steady yellow pool of light.",
    tag: "BARN LANTERN",
    col: "#facc15"
  },
  {
    id: 'acoustic_soundboard_grain',
    name: "\ud83c\udfb8 Acoustic Soundboard Cedar Grain",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎸',
    desc: "Straight, tight grain lines of hand-selected Sitka spruce soundboard vibrating.",
    tag: "SOUNDBOARD GRAIN",
    col: "#ea580c"
  },
  {
    id: 'acoustic_wooden_spoons',
    name: "\ud83e\udd44 Wooden Spoons Folk Rhythms",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🥄',
    desc: "Traditional clacking wooden folk percussion dancing to joyful fiddle tune.",
    tag: "WOODEN SPOONS",
    col: "#b45309"
  },
  {
    id: 'acoustic_rain_on_needles',
    name: "\ud83c\udf32 Gentle Rain on Pine Needles",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌲',
    desc: "Soft forest rain shower dripping from emerald evergreen needles to earth.",
    tag: "PINE RAIN",
    col: "#047857"
  },
  {
    id: 'acoustic_metronome_tick',
    name: "\u23f1\ufe0f Vintage Wooden Metronome Tick",
    category: 'acoustic',
    family: 'acoustic',
    badge: '⏱️',
    desc: "Polished mahogany metronome pendulum swinging steadily at 76 BPM andante.",
    tag: "WOOD METRONOME",
    col: "#78350f"
  },
  {
    id: 'acoustic_fiddle_reel',
    name: "\ud83c\udfbb Fiddle Reel Lively Jump Wave",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎻',
    desc: "Upbeat Celtic fiddle reel bouncing with lively, foot-tapping acoustic joy.",
    tag: "FIDDLE REEL",
    col: "#f59e0b"
  },
  {
    id: 'acoustic_lakeside_pier',
    name: "\u2693 Quiet Lakeside Pier Waves",
    category: 'acoustic',
    family: 'acoustic',
    badge: '⚓',
    desc: "Small clear lake ripples lapping against weathered wooden boat pilings.",
    tag: "LAKESIDE PIER",
    col: "#0284c7"
  },
  {
    id: 'acoustic_wool_blanket',
    name: "\ud83e\uddf6 Warm Wool Blanket Acoustic Glow",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🧶',
    desc: "Cozy cabin blanket wrapping around you on chilly mountain porch.",
    tag: "WOOL BLANKET",
    col: "#d97706"
  },
  {
    id: 'acoustic_valley_mist',
    name: "\ud83c\udf2b\ufe0f Morning Mist over Valley River",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌫️',
    desc: "Soft river fog rolling gently through green Appalachian mountain valley.",
    tag: "VALLEY MIST",
    col: "#94a3b8"
  },
  {
    id: 'acoustic_stove_embers',
    name: "\ud83d\udd25 Cast Iron Stove Embers Glow",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🔥',
    desc: "Potbelly cast-iron stove warming a cozy wooden room on acoustic strumming.",
    tag: "STOVE EMBERS",
    col: "#ea580c"
  },
  {
    id: 'acoustic_eucalyptus_leaves',
    name: "\ud83c\udf43 Dried Eucalyptus Leaves Breeze",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🍃',
    desc: "Fragrant silvery-blue dried leaves rustling with refreshing rustic calm.",
    tag: "EUCALYPTUS",
    col: "#10b981"
  },
  {
    id: 'acoustic_thumb_thump',
    name: "\ud83d\udc4d Fingerpicking Thumb Thump Wave",
    category: 'acoustic',
    family: 'acoustic',
    badge: '👍',
    desc: "Steady alternating Travis picking bass thump driving rhythmic foundation.",
    tag: "THUMB THUMP",
    col: "#92400e"
  },
  {
    id: 'acoustic_open_tuning',
    name: "\ud83c\udfb6 Acoustic 12-Fret Open Tuning",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎶',
    desc: "Open D-A-D-G-A-D modal tuning ringing out with lush harmonic resonance.",
    tag: "OPEN TUNING",
    col: "#38bdf8"
  },
  {
    id: 'acoustic_wind_willow',
    name: "\ud83c\udf3f Wind Blowing Through Willow",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌿',
    desc: "Long trailing willow tendrils whispering against water surface in breeze.",
    tag: "WIND WILLOW",
    col: "#65a30d"
  },
  {
    id: 'acoustic_humming_vocals',
    name: "\ud83d\udde3\ufe0f Soft Humming Vocal Harmonics",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🗣️',
    desc: "Soulful wordless acoustic humming vibration warming the background audio.",
    tag: "HUMMING VOCALS",
    col: "#f59e0b"
  },
  {
    id: 'acoustic_trail_mist',
    name: "\ud83e\udd7e Appalachian Mountain Trail Mist",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🥾',
    desc: "Foggy footpath winding through ancient rhododendron and mossy boulders.",
    tag: "TRAIL MIST",
    col: "#64748b"
  },
  {
    id: 'acoustic_canyon_echo',
    name: "\ud83c\udfdc\ufe0f Desert Canyon Acoustic Echo",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🏜️',
    desc: "Red rock sandstone canyon walls providing magnificent natural natural delay.",
    tag: "CANYON ECHO",
    col: "#c2410c"
  },
  {
    id: 'acoustic_tent_lamp',
    name: "\ud83c\udfd5\ufe0f Starlit Wilderness Tent Lamp",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🏕️',
    desc: "Small battery lantern glowing inside nylon tent under Milky Way starlight.",
    tag: "TENT LAMP",
    col: "#fef08a"
  },
  {
    id: 'acoustic_boat_dock',
    name: "\ud83d\udef6 Old Wooden Dock Tide Lapping",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🛶',
    desc: "Tied canoe bobbing gently against wooden cleats on glassy morning bayou.",
    tag: "BOAT DOCK",
    col: "#0284c7"
  },
  {
    id: 'acoustic_oar_splash',
    name: "\ud83d\udea3 Wooden Oar Splashing Lake",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🚣',
    desc: "Rhythmic paddle strokes cutting still lake water on quiet dawn crossing.",
    tag: "OAR SPLASH",
    col: "#38bdf8"
  },
  {
    id: 'acoustic_haystack_glow',
    name: "\ud83c\udf3e Sunset Prairie Haystack Glow",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌾',
    desc: "Round hay bales casting long shadows across golden harvest afternoon field.",
    tag: "HAYSTACK GLOW",
    col: "#eab308"
  },
  {
    id: 'acoustic_fiddle_double_stop',
    name: "\ud83c\udfbb Bluegrass Fiddle Double Stop",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎻',
    desc: "Soulful two-string harmony bowing crying with sweet traditional tone.",
    tag: "DOUBLE STOP",
    col: "#b45309"
  },
  {
    id: 'acoustic_nylon_shimmer',
    name: "\ud83c\udfb8 Acoustic Nylon String Shimmer",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎸',
    desc: "Warm classical guitar nylon trebles vibrating with Spanish warmth.",
    tag: "NYLON SHIMMER",
    col: "#ea580c"
  },
  {
    id: 'acoustic_d28_tone',
    name: "\ud83c\udfb8 Old Martin D-28 Tone Chamber",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎸',
    desc: "Vintage dreadnought acoustic guitar projecting booming, articulate bass notes.",
    tag: "D28 TONE",
    col: "#78350f"
  },
  {
    id: 'acoustic_pinecone_drop',
    name: "\ud83c\udf32 Pine Cone Falling in Woods",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌲',
    desc: "Soft thud of ripe pine cone landing on thick carpet of forest needles.",
    tag: "PINECONE DROP",
    col: "#854d0e"
  },
  {
    id: 'acoustic_mountain_drizzle',
    name: "\ud83c\udf26\ufe0f Soft Mountain Drizzle Drops",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌦️',
    desc: "Gentle passing rain shower illuminated by afternoon mountain sunbeams.",
    tag: "MOUNTAIN DRIZZLE",
    col: "#60a5fa"
  },
  {
    id: 'acoustic_birch_bark',
    name: "\ud83c\udf33 Birch Tree Bark Peeling Wave",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌳',
    desc: "Paper-white curled birch bark fluttering against smooth silver trunk.",
    tag: "BIRCH BARK",
    col: "#f8fafc"
  },
  {
    id: 'acoustic_acorn_impact',
    name: "\ud83c\udf30 Autumn Acorn Forest Impact",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌰',
    desc: "Crisp acoustic snap of acorn bouncing off stone on quiet forest floor.",
    tag: "ACORN IMPACT",
    col: "#a16207"
  },
  {
    id: 'acoustic_horse_trot',
    name: "\ud83d\udc0e Horse Trotting on Dirt Road",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🐎',
    desc: "Rhythmic wooden hooves clopping on packed dirt country lane at sunset.",
    tag: "HORSE TROT",
    col: "#ca8a04"
  },
  {
    id: 'acoustic_birdsong_horizon',
    name: "\ud83d\udc26 Evening Birdsong Horizon",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🐦',
    desc: "Robin and thrush twilight birdsong notes dancing across golden sky.",
    tag: "BIRDSONG HORIZON",
    col: "#fbbf24"
  },
  {
    id: 'acoustic_wooden_flute',
    name: "\ud83e\ude88 Wooden Flute Breath Tone",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪈',
    desc: "Organic breath sound through cedar native flute vibrating with peace.",
    tag: "WOODEN FLUTE",
    col: "#92400e"
  },
  {
    id: 'acoustic_cedar_chest',
    name: "\ud83d\udce6 Old Cedar Chest Antique Vibe",
    category: 'acoustic',
    family: 'acoustic',
    badge: '📦',
    desc: "Vintage heirloom chest storing quilts with fragrant cedar aroma rings.",
    tag: "CEDAR CHEST",
    col: "#78350f"
  },
  {
    id: 'acoustic_cathedral_arch',
    name: "\u26ea Acoustic Reverb Cathedral Arch",
    category: 'acoustic',
    family: 'acoustic',
    badge: '⛪',
    desc: "Soaring stone gothic vaulting reflecting pure vocal harmonies in peace.",
    tag: "CATHEDRAL ARCH",
    col: "#cbd5e1"
  },
  {
    id: 'acoustic_stone_waterfall',
    name: "\ud83c\udfde\ufe0f Gentle Brook Stone Waterfalls",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🏞️',
    desc: "Cascading crystal water splashing over smooth shale ledges into pool.",
    tag: "BROOK WATERFALL",
    col: "#38bdf8"
  },
  {
    id: 'acoustic_tea_on_stump',
    name: "\ud83e\udeb5 Warm Tea on Cedar Stump",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪵',
    desc: "Steaming enamel camping mug resting on tree stump in morning sun.",
    tag: "TEA ON STUMP",
    col: "#ea580c"
  },
  {
    id: 'acoustic_folk_ukulele',
    name: "\ud83c\udfdd\ufe0f Hand-Strummed Folk Ukulele",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🏝️',
    desc: "Warm finger strumming on solid mahogany ukulele body with sunny tone.",
    tag: "FOLK UKULELE",
    col: "#b45309"
  },
  {
    id: 'acoustic_dry_oak_leaves',
    name: "\ud83c\udf42 Rustling Dry Oak Leaves",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🍂',
    desc: "Golden brown oak foliage whispering stories in crisp November wind.",
    tag: "OAK LEAVES",
    col: "#c2410c"
  },
  {
    id: 'acoustic_marshmallow_ember',
    name: "\ud83c\udf62 Campfire Marshmallow Amber",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🍢',
    desc: "Toasting marshmallow turning golden brown over glowing wood embers.",
    tag: "MARSHMALLOW",
    col: "#f59e0b"
  },
  {
    id: 'acoustic_cabin_chimney',
    name: "\ud83c\udfe1 Quiet Mountain Cabin Chimney",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🏡',
    desc: "Warm stone chimney puffing cedar smoke into starry winter sky.",
    tag: "CABIN CHIMNEY",
    col: "#a8a29e"
  },
  {
    id: 'acoustic_aspen_trees',
    name: "\ud83c\udf33 Whispering Wind in Aspen Trees",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌳',
    desc: "Quaking golden aspen leaves shimmering like coins in mountain wind.",
    tag: "ASPEN TREES",
    col: "#facc15"
  },
  {
    id: 'acoustic_bass_double_stop',
    name: "\ud83c\udfbb Deep Acoustic Bass Double Stop",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎻',
    desc: "Resonant low octave fundamental vibrating floorboards with warmth.",
    tag: "BASS DOUBLE STOP",
    col: "#78350f"
  },
  {
    id: 'acoustic_porch_steps',
    name: "\ud83e\ude9c Old Front Porch Wooden Steps",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪜',
    desc: "Weathered cedar steps welcoming travelers home after long journeys.",
    tag: "PORCH STEPS",
    col: "#92400e"
  },
  {
    id: 'acoustic_redwood_fog',
    name: "\ud83c\udf32 Morning Fog in Redwood Forest",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌲',
    desc: "Majestic giant redwoods standing silent in rolling Pacific coastal fog.",
    tag: "REDWOOD FOG",
    col: "#047857"
  },
  {
    id: 'acoustic_wooden_chimes',
    name: "\ud83c\udf90 Wooden Chimes Swaying Breeze",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎐',
    desc: "Hollow bamboo chimes clicking softly in gentle backyard garden breeze.",
    tag: "WOODEN CHIMES",
    col: "#b45309"
  },
  {
    id: 'acoustic_finger_vibrato',
    name: "\u3030\ufe0f Gentle Finger Vibrato Sine",
    category: 'acoustic',
    family: 'acoustic',
    badge: '〰️',
    desc: "Expressive acoustic string vibrato modulating pitch with tender emotion.",
    tag: "FINGER VIBRATO",
    col: "#38bdf8"
  },
  {
    id: 'acoustic_seagull_s6',
    name: "\ud83c\udfb8 Strummed Seagull S6 Harmony",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎸',
    desc: "Wild cherry back and sides ringing out with punchy, balanced folk voice.",
    tag: "SEAGULL GUITAR",
    col: "#ea580c"
  },
  {
    id: 'acoustic_pine_sap',
    name: "\ud83d\udca7 Pine Tree Sap Amber Drop",
    category: 'acoustic',
    family: 'acoustic',
    badge: '💧',
    desc: "Golden resin teardrop glistening on fragrant evergreen bark.",
    tag: "PINE SAP",
    col: "#d97706"
  },
  {
    id: 'acoustic_hay_bale_sunset',
    name: "\ud83c\udf05 Sunset Over Hay Bale Field",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌅',
    desc: "Peaceful silhouette of rolling farm fields glowing in twilight peace.",
    tag: "HAY BALE SUNSET",
    col: "#f59e0b"
  },
  {
    id: 'acoustic_skipping_stone',
    name: "\ud83e\udea8 Clear Stream Water Skipping Stone",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪨',
    desc: "Flat river stone skipping three times across calm surface leaving concentric rings.",
    tag: "SKIPPING STONE",
    col: "#06b6d4"
  },
  {
    id: 'acoustic_dulcimer_strum',
    name: "\ud83e\ude95 Mountain Dulcimer Strum Ripple",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪕',
    desc: "Sweet crystalline quill strumming across nickel frets with folk grace.",
    tag: "DULCIMER STRUM",
    col: "#d97706"
  },
  {
    id: 'acoustic_night_owl',
    name: "\ud83e\udd89 Wilderness Night Owl Call Echo",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🦉',
    desc: "Deep hooting owl call echoing across silent moonlit pine woods.",
    tag: "NIGHT OWL",
    col: "#475569"
  },
  {
    id: 'acoustic_charcoal_ember',
    name: "\ud83d\udd25 Quiet Campfire Charcoal Ember",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🔥',
    desc: "Single glowing orange charcoal breathing with soft rhythmic warmth.",
    tag: "CHARCOAL EMBER",
    col: "#f97316"
  },
  {
    id: 'acoustic_open_g_horizon',
    name: "\ud83c\udf05 Acoustic Horizon Open G Tuning",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌅',
    desc: "Rich resonant open G chord ringing with expansive endless landscape beauty.",
    tag: "OPEN G HORIZON",
    col: "#f59e0b"
  },
  {
    id: 'acoustic_infinite_harmony',
    name: "\ud83c\udfb6 Infinite Unplugged Harmony",
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎶',
    desc: "Timeless organic acoustic resonance connecting heart, hands, and earth.",
    tag: "INFINITE HARMONY",
    col: "#d97706"
  },
  {
    id: 'phonk_auto',
    name: "\ud83c\udfb2 Auto Phonk Reactor (Random Shuffle)",
    category: 'phonk',
    family: 'trap_nation',
    badge: '🎲',
    desc: "Automatic selection: Phonk / Funk gaane ke liye Trap Nation, Tokyo Drift aur 808 reactors auto-match honge!",
    tag: "AUTO DEFAULT",
    col: "#00f2fe"
  },
  {
    id: 'trap_nation_trilobe',
    name: "\ud83d\udc51 Trap Nation Tri-Lobe Core",
    category: 'phonk',
    family: 'trap_nation',
    badge: '👑',
    desc: "Center Circle Logo + 3-Lobe Audio Bulges + Dotted Equalizer Perimeter + Neon Halo (Flagship Style).",
    tag: "TRAP NATION",
    col: "#a855f7"
  },
  {
    id: 'reactor_studio',
    name: "\u2622\ufe0f Extreme Reactor Studio",
    category: 'phonk',
    family: 'reactor',
    badge: '☢️',
    desc: "Center Circle Logo + 360\u00b0 Radial Frequency Bars + 808 Lightning & Shockwaves + Oscilloscope.",
    tag: "PRO STUDIO",
    col: "#f97316"
  },
  {
    id: 'primary',
    name: "\ud83c\udf1f Classic Tokyo Drift Shake & 808 Zoom",
    category: 'phonk',
    family: 'all',
    badge: '🌟',
    desc: "Original Tokyo drift camera vibration, 808 zoom pump & RGB chromatic flash (Zero extra shapes).",
    tag: "CLASSIC DRIFT",
    col: "#00f2fe"
  },
  {
    id: 'tachometer_jdm',
    name: "\ud83c\udfce\ufe0f JDM Drift Tachometer & 808 Boost",
    category: 'phonk',
    family: 'tachometer',
    badge: '🏎️',
    desc: "Dual RPM meter tachometer arches + boost gauge needles flashing on 808 sub-bass drops.",
    tag: "JDM BOOST",
    col: "#ef4444"
  },
  {
    id: 'monstercat_radial',
    name: "\u2b55 Monstercat 360\u00b0 Circular Ring",
    category: 'phonk',
    family: 'monstercat',
    badge: '⭕',
    desc: "Center Circle Logo + Dense 360-degree frequency bars vibrating outward with sub-bass drops.",
    tag: "360 RING",
    col: "#f43f5e"
  },
  {
    id: 'cyber_hexagon',
    name: "\ud83d\udd37 Cyber Hexagon Core",
    category: 'phonk',
    family: 'hexagon',
    badge: '🔷',
    desc: "Center Circle Logo + Dual rotating honeycomb hex shields + techno brackets expanding on drops.",
    tag: "HEX CORE",
    col: "#0ea5e9"
  },
  {
    id: 'diamond_prism',
    name: "\ud83d\udca0 Diamond Core Bass Prism",
    category: 'phonk',
    family: 'diamond',
    badge: '💠',
    desc: "Center Circle Logo + 45-degree rotating diamond frame + corner telemetry spikes & shockwave rings.",
    tag: "DIAMOND",
    col: "#06b6d4"
  },
  {
    id: 'biohazard_core',
    name: "\ud83d\udee1\ufe0f Biohazard Radioactive Core",
    category: 'phonk',
    family: 'biohazard',
    badge: '🛡️',
    desc: "Center Circle Logo + Triple biohazard arc blades rotating with radioactive neon green aura.",
    tag: "BIOHAZARD",
    col: "#22c55e"
  },
  {
    id: 'plasma_lightning',
    name: "\u26a1 Electric Plasma Arc Reactor",
    category: 'phonk',
    family: 'plasma',
    badge: '⚡',
    desc: "Center Circle Logo + High-voltage plasma lightning bolts jumping between circular orbital nodes.",
    tag: "PLASMA",
    col: "#a855f7"
  },
  {
    id: 'grid_3d_synthwave',
    name: "\ud83c\udf10 3D Synthwave Horizon & Sun",
    category: 'phonk',
    family: 'grid_3d',
    badge: '🌐',
    desc: "Center Circle Logo + Perspective wireframe neon floor grid vibrating to 808 bass + horizon sun.",
    tag: "3D GRID",
    col: "#ec4899"
  },
  {
    id: 'tunnel_warp',
    name: "\ud83c\udf00 Hyperspace Polygonal Tunnel",
    category: 'phonk',
    family: 'tunnel',
    badge: '🌀',
    desc: "Center Circle Logo + Multi-layered octagonal warp tunnel rings collapsing and expanding on drops.",
    tag: "WARP TUNNEL",
    col: "#8b5cf6"
  },
  {
    id: 'drift_hud_telemetry',
    name: "\ud83d\udca8 Tokyo Drift HUD Telemetry",
    category: 'phonk',
    family: 'drift_hud',
    badge: '💨',
    desc: "Japanese Kanji glow brackets + corner tactical telemetry + manga radial speed lines.",
    tag: "TOKYO HUD",
    col: "#10b981"
  },
  {
    id: 'equalizer_wave',
    name: "\ud83d\udcca Dual-Horizon Equalizer Bars",
    category: 'phonk',
    family: 'equalizer',
    badge: '📊',
    desc: "Mirrored top and bottom audio equalizer bars reflecting like city lights on wet asphalt.",
    tag: "EQUALIZER",
    col: "#00f2fe"
  },
  {
    id: 'starfield_warp',
    name: "\ud83d\ude80 Light Speed Starfield Accelerator",
    category: 'phonk',
    family: 'starfield',
    badge: '🚀',
    desc: "Center Circle Logo + 3D starfield streaks accelerating into hyperspace on 808 bass drops.",
    tag: "STARFIELD",
    col: "#eab308"
  },
  {
    id: 'phonk_redline_overdrive',
    name: "\ud83d\udea8 JDM Redline Overdrive HUD Ring",
    category: 'phonk',
    family: 'tachometer',
    badge: '🚨',
    desc: "Twin neon redline tachometer brackets flashing warning flares on heavy 808 sub-bass drops.",
    tag: "REDLINE",
    col: "#ef4444"
  },
  {
    id: 'phonk_kanji_neon',
    name: "\ud83c\ude32 Tokyo Kanji Drift Cyber Halo",
    category: 'phonk',
    family: 'drift_hud',
    badge: '🈲',
    desc: "Glowing Japanese kanji symbols and speed streaks flashing around the center avatar on drift turns.",
    tag: "KANJI",
    col: "#00f2fe"
  },
  {
    id: 'phonk_night_highway',
    name: "\ud83d\udee3\ufe0f Shuto Expressway Light Streaks",
    category: 'phonk',
    family: 'grid_3d',
    badge: '🛣️',
    desc: "Long-exposure Tokyo expressway tail-light speed streaks accelerating into distance.",
    tag: "HIGHWAY",
    col: "#f43f5e"
  },
  {
    id: 'phonk_wangan_midnight',
    name: "\ud83c\udfce\ufe0f Wangan Midnight 300km/h Blur",
    category: 'phonk',
    family: 'drift_hud',
    badge: '🏎️',
    desc: "Japanese highway tunnel fluorescent ceiling lights stretching into continuous lines.",
    tag: "WANGAN 300",
    col: "#ef4444"
  },
  {
    id: 'phonk_turbo_blowoff',
    name: "\ud83d\udca8 Twin-Turbo Anti-Lag Backfire",
    category: 'phonk',
    family: 'tachometer',
    badge: '💨',
    desc: "Exhaust flame bursts and boost spikes reacting to heavy 808 distortion.",
    tag: "TURBO BLOWOFF",
    col: "#f97316"
  },
  {
    id: 'phonk_akira_slide',
    name: "\ud83c\udfcd\ufe0f Neo-Tokyo Cyber Slide",
    category: 'phonk',
    family: 'grid_3d',
    badge: '🏍️',
    desc: "Iconic red motorcycle drift slide with electric tire sparks and neon brake trails.",
    tag: "AKIRA SLIDE",
    col: "#dc2626"
  },
  {
    id: 'phonk_ghost_drift',
    name: "\ud83d\udc7b Shibuya Ghost Drift Fog",
    category: 'phonk',
    family: 'drift_hud',
    badge: '👻',
    desc: "Dense tire smoke illuminated by violet street lamps on aggressive cornering.",
    tag: "GHOST DRIFT",
    col: "#8b5cf6"
  },
  {
    id: 'phonk_tach_shift_light',
    name: "\u26a1 Sequential Shift Light Flasher",
    category: 'phonk',
    family: 'tachometer',
    badge: '⚡',
    desc: "Formula drift tachometer LED ladder flashing amber-to-red at 9000 RPM.",
    tag: "SHIFT LIGHT",
    col: "#eab308"
  },
  {
    id: 'phonk_vhs_cyber_kanji',
    name: "\ud83c\ude32 90s JDM Drift Tape Scanlines",
    category: 'phonk',
    family: 'tunnel',
    badge: '🈲',
    desc: "Retro VHS tracking distortion lines with neon Japanese car tuning kanji stamps.",
    tag: "JDM VHS",
    col: "#06b6d4"
  },
  {
    id: 'phonk_distorted_cowbell',
    name: "\ud83d\udd14 Distorted 808 Cowbell Waveform",
    category: 'phonk',
    family: 'equalizer',
    badge: '🔔',
    desc: "Sharp metallic cowbell square wave cutting through deep aggressive Memphis 808 sub.",
    tag: "COWBELL BASS",
    col: "#facc15"
  },
  {
    id: 'phonk_brazilian_skull',
    name: "\ud83d\udc80 Brazilian Phonk Skull Reactor",
    category: 'phonk',
    family: 'reactor',
    badge: '💀',
    desc: "Hyper-aggressive favela funk skull emblem pulsing with violent sub-bass camera shake.",
    tag: "BRAZILIAN PHONK",
    col: "#ef4444"
  },
  {
    id: 'phonk_parking_drift',
    name: "\ud83c\udd7f\ufe0f Underground Parking Drift Ring",
    category: 'phonk',
    family: 'drift_hud',
    badge: '🅿️',
    desc: "Tight concrete pillar donuts leaving rubber tire marks and echoes of squealing tires.",
    tag: "PARKING DRIFT",
    col: "#64748b"
  },
  {
    id: 'phonk_boost_gauge',
    name: "\u23f1\ufe0f Boost Gauge Needle Overdrive",
    category: 'phonk',
    family: 'tachometer',
    badge: '⏱️',
    desc: "Circular 2.5 bar boost gauge peaking into red zone on aggressive turbo spool.",
    tag: "BOOST GAUGE",
    col: "#38bdf8"
  },
  {
    id: 'phonk_intercooler_spray',
    name: "\ud83d\udca8 Intercooler Mist Spray Blast",
    category: 'phonk',
    family: 'shockwave',
    badge: '💨',
    desc: "High-pressure nitrous/water mist spraying across front bumper on bass kick.",
    tag: "INTERCOOLER",
    col: "#67e8f9"
  },
  {
    id: 'phonk_nos_purge',
    name: "\ud83d\ude80 Nitrous Oxide Purge Jet",
    category: 'phonk',
    family: 'shockwave',
    badge: '🚀',
    desc: "Twin white plumes of cryogenic NOS shooting from hood vents with high-pressure hiss.",
    tag: "NOS PURGE",
    col: "#00f2fe"
  },
  {
    id: 'phonk_carbon_hood',
    name: "\ud83c\udfc1 Carbon Fiber Hood Resonance",
    category: 'phonk',
    family: 'hexagon',
    badge: '🏁',
    desc: "Twill weave carbon fiber pattern reflecting neon city lights with subtle vibration.",
    tag: "CARBON FIBER",
    col: "#334155"
  },
  {
    id: 'phonk_drift_gyro',
    name: "\ud83d\udcd0 Drift Angle Gyro HUD",
    category: 'phonk',
    family: 'drift_hud',
    badge: '📐',
    desc: "Tactical telemetry displaying real-time 60-degree counter-steering drift angle.",
    tag: "DRIFT GYRO",
    col: "#10b981"
  },
  {
    id: 'phonk_underglow_neon',
    name: "\u2728 Neon Underglow Asphalt Reflection",
    category: 'phonk',
    family: 'grid_3d',
    badge: '✨',
    desc: "Sizzling hot cyan and magenta chassis neon glow washing over wet blacktop.",
    tag: "UNDERGLOW",
    col: "#ec4899"
  },
  {
    id: 'phonk_manga_speedlines',
    name: "\ud83d\udca5 Manga Radial Speed Line Blast",
    category: 'phonk',
    family: 'starfield',
    badge: '💥',
    desc: "Aggressive black-and-white Initial D action speed lines converging on center avatar.",
    tag: "MANGA SPEED",
    col: "#ffffff"
  },
  {
    id: 'phonk_haruna_downhill',
    name: "\u26f0\ufe0f Mount Haruna Downhill Drift",
    category: 'phonk',
    family: 'grid_3d',
    badge: '⛰️',
    desc: "Hairpin turn gutters and downhill momentum shaking camera on every clipping point.",
    tag: "HARUNA TOUGE",
    col: "#f59e0b"
  },
  {
    id: 'phonk_rotary_2step',
    name: "\ud83d\udd25 Rotary Engine 2-Step Backfire",
    category: 'phonk',
    family: 'tachometer',
    badge: '🔥',
    desc: "Brapping 13B Wankel rotary engine shooting 3-foot blue exhaust flame fireballs.",
    tag: "ROTARY 2-STEP",
    col: "#3b82f6"
  },
  {
    id: 'phonk_shibuya_crossing',
    name: "\ud83d\udeb6 Shibuya Crossing Drift Blur",
    category: 'phonk',
    family: 'drift_hud',
    badge: '🚶',
    desc: "World-famous intersection glowing with massive neon billboards and drift smoke.",
    tag: "SHIBUYA BLUR",
    col: "#a855f7"
  },
  {
    id: 'phonk_samurai_blade',
    name: "\ud83d\udde1\ufe0f Cyberpunk Samurai Kanji Blade",
    category: 'phonk',
    family: 'hexagon',
    badge: '🗡️',
    desc: "High-frequency neon energy katana slashing through screen on heavy beat drops.",
    tag: "SAMURAI BLADE",
    col: "#06b6d4"
  },
  {
    id: 'phonk_screamer_pipe',
    name: "\ud83d\udce2 Turbo Wastegate Screamer Pipe",
    category: 'phonk',
    family: 'tachometer',
    badge: '📢',
    desc: "Open atmospheric dump pipe screaming with raw deafening exhaust sound on drop.",
    tag: "SCREAMER PIPE",
    col: "#ea580c"
  },
  {
    id: 'phonk_titanium_flame',
    name: "\ud83d\udd35 Titanium Exhaust Flame Ring",
    category: 'phonk',
    family: 'reactor',
    badge: '🔵',
    desc: "Burnt blue titanium exhaust tip spitting hot violet flame rings on deceleration.",
    tag: "TITANIUM FLAME",
    col: "#6366f1"
  },
  {
    id: 'phonk_expressway_tunnel',
    name: "\ud83d\ude87 Tokyo Expressway Tunnel Shadows",
    category: 'phonk',
    family: 'tunnel',
    badge: '🚇',
    desc: "Fluorescent ceiling strip lights strobing rapidly through underwater tunnel run.",
    tag: "TUNNEL SHADOWS",
    col: "#facc15"
  },
  {
    id: 'phonk_screen_puncher',
    name: "\ud83d\udc4a 808 Sub-Bass Screen Puncher",
    category: 'phonk',
    family: 'shockwave',
    badge: '👊',
    desc: "Violent sudden 120% scale zoom and RGB chromatic split on every heavy 808 hit.",
    tag: "SCREEN PUNCH",
    col: "#ef4444"
  },
  {
    id: 'phonk_bass_distort',
    name: "\u26a1 Distorted Phonk Bass Distortion",
    category: 'phonk',
    family: 'equalizer',
    badge: '⚡',
    desc: "Heavily saturated analog clipping buzzing with vicious underground phonk energy.",
    tag: "BASS DISTORT",
    col: "#f59e0b"
  },
  {
    id: 'phonk_oni_mask',
    name: "\ud83d\udc79 Cyber Oni Mask Core",
    category: 'phonk',
    family: 'reactor',
    badge: '👹',
    desc: "Terrifying Japanese demon mask with glowing neon fangs and glowing red eyes.",
    tag: "ONI MASK",
    col: "#dc2626"
  },
  {
    id: 'phonk_te37_blur',
    name: "\ud83d\udede Volk TE37 Rim Spin Blur",
    category: 'phonk',
    family: 'monstercat',
    badge: '🛞',
    desc: "Legendary bronze 6-spoke racing wheels spinning at 250km/h with brake disc glow.",
    tag: "TE37 BLUR",
    col: "#d97706"
  },
  {
    id: 'phonk_rev_limiter',
    name: "\ud83d\udea8 Redline Fuel Cut Rev Limiter",
    category: 'phonk',
    family: 'tachometer',
    badge: '🚨',
    desc: "Staccato machine-gun exhaust pops as tachometer bounces off the limiter.",
    tag: "REV LIMITER",
    col: "#ef4444"
  },
  {
    id: 'phonk_akihabara_night',
    name: "\ud83c\udf06 Akihabara Neon Night Grid",
    category: 'phonk',
    family: 'grid_3d',
    badge: '🌆',
    desc: "Towering anime and electronics storefront neon lights reflecting in puddles.",
    tag: "AKIHABARA NEON",
    col: "#ec4899"
  },
  {
    id: 'phonk_widebody_stance',
    name: "\ud83c\udfce\ufe0f Widebody Fender Flare Stance",
    category: 'phonk',
    family: 'hexagon',
    badge: '🏎️',
    desc: "Aggressive riveted Pandem/Rocket Bunny widebody stance hugging the asphalt.",
    tag: "WIDEBODY STANCE",
    col: "#64748b"
  },
  {
    id: 'phonk_lateral_g_meter',
    name: "\ud83d\udcca High-G Lateral Drift Meter",
    category: 'phonk',
    family: 'drift_hud',
    badge: '📊',
    desc: "Digital G-force ball rolling to 1.4G on full-lock sideways transitions.",
    tag: "G-METER",
    col: "#10b981"
  },
  {
    id: 'phonk_clutch_kick',
    name: "\ud83e\uddb6 Twin-Plate Clutch Kick Shock",
    category: 'phonk',
    family: 'shockwave',
    badge: '🦶',
    desc: "Violent transmission shock breaking rear tires loose on corner entry.",
    tag: "CLUTCH KICK",
    col: "#f97316"
  },
  {
    id: 'phonk_drifter_decals',
    name: "\ud83c\udf8c Japanese Street Drifter Decals",
    category: 'phonk',
    family: 'drift_hud',
    badge: '🎌',
    desc: "Vintage midnight runner sponsor vinyl stickers lining perimeter border.",
    tag: "DRIFT DECALS",
    col: "#f8fafc"
  },
  {
    id: 'phonk_tach_hud_arc',
    name: "\ud83c\udfce\ufe0f Cyberpunk Tachometer HUD Arc",
    category: 'phonk',
    family: 'tachometer',
    badge: '🏎️',
    desc: "Curved digital LED rev arc with numerical digital gear indicator in center.",
    tag: "TACH HUD ARC",
    col: "#00f2fe"
  },
  {
    id: 'phonk_seismic_wave',
    name: "\ud83c\udf0a Sub-Bass 808 Seismic Wave",
    category: 'phonk',
    family: 'shockwave',
    badge: '🌊',
    desc: "Full-screen horizontal seismic wave ripple rolling from bottom to top.",
    tag: "SEISMIC WAVE",
    col: "#38bdf8"
  },
  {
    id: 'phonk_license_plate',
    name: "\ud83d\udd22 Japanese License Plate Flicker",
    category: 'phonk',
    family: 'drift_hud',
    badge: '🔢',
    desc: "Angled green-on-white illuminated JDM license plate with speed camera flash.",
    tag: "LICENSE PLATE",
    col: "#4ade80"
  },
  {
    id: 'phonk_touge_fog',
    name: "\ud83c\udf32 Touge Mountain Pass Fog Drift",
    category: 'phonk',
    family: 'grid_3d',
    badge: '🌲',
    desc: "Narrow winding two-lane mountain road flanked by guardrails and thick mist.",
    tag: "TOUGE FOG",
    col: "#64748b"
  },
  {
    id: 'phonk_night_runner',
    name: "\ud83d\udee3\ufe0f Night Runner Highway Blitz",
    category: 'phonk',
    family: 'starfield',
    badge: '🛣️',
    desc: "High-speed weaving through midnight highway traffic with tail-light trails.",
    tag: "NIGHT RUNNER",
    col: "#f43f5e"
  },
  {
    id: 'phonk_turbo_surge',
    name: "\ud83d\udca8 Turbo Spool Boost Surge",
    category: 'phonk',
    family: 'tachometer',
    badge: '💨',
    desc: "High-pitched compressor whistle accelerating into deafening boost crescendo.",
    tag: "TURBO SURGE",
    col: "#38bdf8"
  },
  {
    id: 'phonk_burnout_ring',
    name: "\u2b55 Smoke Screen Tire Burnout Ring",
    category: 'phonk',
    family: 'monstercat',
    badge: '⭕',
    desc: "360-degree dense cloud of white acrid tire smoke completely filling frame.",
    tag: "BURNOUT RING",
    col: "#cbd5e1"
  },
  {
    id: 'phonk_tsuchiya_halo',
    name: "\ud83d\udc51 Drift King Tsuchiya Tribute Halo",
    category: 'phonk',
    family: 'reactor',
    badge: '👑',
    desc: "Golden racing helmet and green racing suit inspired speed halo.",
    tag: "DRIFT KING",
    col: "#22c55e"
  },
  {
    id: 'phonk_skyline_tail_lights',
    name: "\ud83d\udd34 R34 Skyline Tail Light Circles",
    category: 'phonk',
    family: 'monstercat',
    badge: '🔴',
    desc: "Four iconic glowing crimson circular tail lamps piercing through dark mist.",
    tag: "SKYLINE LIGHTS",
    col: "#ef4444"
  },
  {
    id: 'phonk_2jz_flame',
    name: "\ud83d\udd25 Supra 2JZ Flame Spit Cannon",
    category: 'phonk',
    family: 'tachometer',
    badge: '🔥',
    desc: "Legendary 3.0L inline-6 spitting basketball-sized orange exhaust fireballs.",
    tag: "2JZ FLAME",
    col: "#f97316"
  },
  {
    id: 'phonk_rx7_whistle',
    name: "\ud83d\udca8 RX-7 FD Apex Seal Whistle",
    category: 'phonk',
    family: 'tunnel',
    badge: '💨',
    desc: "Twin sequential turbochargers screaming around sequential rotary rotor pulses.",
    tag: "RX7 ROTARY",
    col: "#eab308"
  },
  {
    id: 'phonk_s15_ducktail',
    name: "\ud83d\ude97 Silvia S15 Ducktail Spoiler Wing",
    category: 'phonk',
    family: 'hexagon',
    badge: '🚗',
    desc: "Aero ducktail spoiler cutting aerodynamic vortices through tire smoke.",
    tag: "S15 DUCKTAIL",
    col: "#06b6d4"
  },
  {
    id: 'phonk_ae86_headlights',
    name: "\ud83d\udca1 AE86 Trueno Pop-up Headlight Beam",
    category: 'phonk',
    family: 'equalizer',
    badge: '💡',
    desc: "Retractable square pop-up headlight beams illuminating hairpin turn cliff.",
    tag: "AE86 TRUENO",
    col: "#fef08a"
  },
  {
    id: 'phonk_midnight_tach',
    name: "\ud83c\udfce\ufe0f Midnight Club Special Tachometer",
    category: 'phonk',
    family: 'tachometer',
    badge: '🏎️',
    desc: "340 km/h top-speed speedometer and 11,000 RPM race tachometer combination.",
    tag: "MIDNIGHT TACH",
    col: "#dc2626"
  },
  {
    id: 'phonk_daikoku_strobe',
    name: "\ud83c\udd7f\ufe0f Daikoku Futo Car Meet Strobe",
    category: 'phonk',
    family: 'grid_3d',
    badge: '🅿️',
    desc: "Famous parking area gathering of modified supercars, neon tubes, and sounds.",
    tag: "DAIKOKU FUTO",
    col: "#ec4899"
  },
  {
    id: 'phonk_bay_bridge',
    name: "\ud83c\udf09 Yokohama Bay Bridge Streaks",
    category: 'phonk',
    family: 'grid_3d',
    badge: '🌉',
    desc: "Cable-stayed bridge suspension cables bathed in blue floodlights at 200km/h.",
    tag: "BAY BRIDGE",
    col: "#3b82f6"
  },
  {
    id: 'phonk_c1_loop',
    name: "\ud83d\udd04 C1 Loop Expressway Speed Run",
    category: 'phonk',
    family: 'tunnel',
    badge: '🔄',
    desc: "Tight elevated circular highway loop winding between Tokyo skyscrapers.",
    tag: "C1 LOOP",
    col: "#10b981"
  },
  {
    id: 'phonk_kanjozoku_racer',
    name: "\ud83c\udfc1 Kanjozoku Civic Loop Racer Grid",
    category: 'phonk',
    family: 'hexagon',
    badge: '🏁',
    desc: "Osaka loop line racer with hockey mask and straight-pipe VTEC howl.",
    tag: "KANJOZOKU",
    col: "#ef4444"
  },
  {
    id: 'phonk_smoke_violet',
    name: "\ud83d\udca8 Drift Smoke Illuminated Violet",
    category: 'phonk',
    family: 'shockwave',
    badge: '💨',
    desc: "Dense tire smoke reflecting purple neon lights like a cosmic cloud.",
    tag: "VIOLET SMOKE",
    col: "#a855f7"
  },
  {
    id: 'phonk_toll_booth_blitz',
    name: "\ud83d\udee3\ufe0f Tokyo Highway Toll Booth Blitz",
    category: 'phonk',
    family: 'starfield',
    badge: '🛣️',
    desc: "Sprinting through green ETC gate without lifting foot off the throttle.",
    tag: "TOLL BOOTH",
    col: "#22c55e"
  },
  {
    id: 'phonk_brake_glow',
    name: "\ud83d\udd34 Carbon Ceramic Brake Glow Red",
    category: 'phonk',
    family: 'reactor',
    badge: '🔴',
    desc: "Brake rotors glowing cherry-red hot under heavy deceleration from 280km/h.",
    tag: "BRAKE GLOW",
    col: "#ef4444"
  },
  {
    id: 'phonk_wastegate_fire',
    name: "\ud83d\udd25 Screaming Wastegate Fire Ring",
    category: 'phonk',
    family: 'shockwave',
    badge: '🔥',
    desc: "External 44mm wastegate opening with flame blast directly into engine bay.",
    tag: "WASTEGATE FIRE",
    col: "#f97316"
  },
  {
    id: 'phonk_front_splitter',
    name: "\ud83c\udfce\ufe0f Aggressive Front Splitter Downforce",
    category: 'phonk',
    family: 'hexagon',
    badge: '🏎️',
    desc: "Carbon aerodynamic splitter scraping ground and throwing titanium sparks.",
    tag: "FRONT SPLITTER",
    col: "#64748b"
  },
  {
    id: 'phonk_gt_wing_vortex',
    name: "\ud83e\udebd GT Wing Aero Vortex Struts",
    category: 'phonk',
    family: 'drift_hud',
    badge: '🪽',
    desc: "Swan-neck carbon fiber rear wing shedding high-speed wingtip air vortices.",
    tag: "GT WING",
    col: "#38bdf8"
  },
  {
    id: 'phonk_roll_cage',
    name: "\u26d3\ufe0f Roll Cage Neon Wire Lattice",
    category: 'phonk',
    family: 'grid_3d',
    badge: '⛓️',
    desc: "Cross-braced DOM steel roll cage glowing with neon electroluminescent wire.",
    tag: "ROLL CAGE",
    col: "#ec4899"
  },
  {
    id: 'phonk_hydro_handbrake',
    name: "\ud83d\udd79\ufe0f Hydro Handbrake Lockup Shake",
    category: 'phonk',
    family: 'shockwave',
    badge: '🕹️',
    desc: "Upright hydraulic drift e-brake lever yanked hard to initiate backward entry.",
    tag: "HYDRO HANDBRAKE",
    col: "#f59e0b"
  },
  {
    id: 'phonk_eurobeat_hybrid',
    name: "\u26a1 JDM Eurobeat Phonk Hybrid Wave",
    category: 'phonk',
    family: 'equalizer',
    badge: '⚡',
    desc: "Blistering 160 BPM Eurobeat synthesizer melody fused with heavy Memphis 808.",
    tag: "EUROBEAT PHONK",
    col: "#00f2fe"
  },
  {
    id: 'phonk_distortion_clipper',
    name: "\ud83d\udcc8 808 Distortion Bass Clipper",
    category: 'phonk',
    family: 'equalizer',
    badge: '📈',
    desc: "Wavefolder and soft-clipper giving the 808 bass vicious harmonic aggression.",
    tag: "BASS CLIPPER",
    col: "#ea580c"
  },
  {
    id: 'phonk_cowbell_syncopated',
    name: "\ud83d\udd14 Cowbell Melody Syncopated Pulse",
    category: 'phonk',
    family: 'monstercat',
    badge: '🔔',
    desc: "Trill 808 cowbell melody cascading across stereo channels on drop.",
    tag: "COWBELL PULSE",
    col: "#facc15"
  },
  {
    id: 'phonk_apex_clip',
    name: "\ud83c\udfaf Drift King Apex Clipping Point",
    category: 'phonk',
    family: 'drift_hud',
    badge: '🎯',
    desc: "Rear bumper skimming within 1 inch of concrete wall clipping zone.",
    tag: "CLIPPING POINT",
    col: "#ef4444"
  },
  {
    id: 'phonk_wet_city_reflection',
    name: "\ud83c\udf27\ufe0f Wet Pavement City Reflection",
    category: 'phonk',
    family: 'grid_3d',
    badge: '🌧️',
    desc: "Rain-slicked asphalt acting as a mirror for neon cybernetic skyscrapers.",
    tag: "WET PAVEMENT",
    col: "#38bdf8"
  },
  {
    id: 'phonk_tower_skyline',
    name: "\ud83d\uddfc Tokyo Tower Silhouette Skyline",
    category: 'phonk',
    family: 'drift_hud',
    badge: '🗼',
    desc: "Iconic orange-and-white lattice radio tower standing over drifting streetcars.",
    tag: "TOKYO TOWER",
    col: "#f97316"
  },
  {
    id: 'phonk_katana_slash',
    name: "\u2694\ufe0f Cyber Katana Slash Speed Line",
    category: 'phonk',
    family: 'starfield',
    badge: '⚔️',
    desc: "Blinding white diagonal cutting streak parting the screen in two on snare hit.",
    tag: "KATANA SLASH",
    col: "#ffffff"
  },
  {
    id: 'phonk_etc_gate',
    name: "\ud83d\udfe9 Electronic Toll Collection Green Flash",
    category: 'phonk',
    family: 'drift_hud',
    badge: '🟩',
    desc: "Futuristic green laser strobe illuminating the windshield at high speed.",
    tag: "ETC FLASH",
    col: "#22c55e"
  },
  {
    id: 'phonk_twin_scroll_surge',
    name: "\ud83d\udca8 Twin Scroll Turbo Compressor Surge",
    category: 'phonk',
    family: 'tachometer',
    badge: '💨',
    desc: "Staccato flutter of compressed air echoing through aluminum intake pipe.",
    tag: "COMPRESSOR SURGE",
    col: "#06b6d4"
  },
  {
    id: 'phonk_straight_pipe',
    name: "\ud83d\udce2 Straight Pipe Exhaust Sonic Boom",
    category: 'phonk',
    family: 'shockwave',
    badge: '📢',
    desc: "Raw un-muffled 3-inch stainless steel exhaust roaring with earth-shattering volume.",
    tag: "STRAIGHT PIPE",
    col: "#ea580c"
  },
  {
    id: 'phonk_street_glow_tubes',
    name: "\ud83d\udca1 Street Glow Neon Chassis Tubes",
    category: 'phonk',
    family: 'grid_3d',
    badge: '💡',
    desc: "High-voltage neon tubes bathing the pavement in intense electric color.",
    tag: "CHASSIS GLOW",
    col: "#ec4899"
  },
  {
    id: 'phonk_rain_roost',
    name: "\ud83d\udca6 Drifting in Rain Water Roost",
    category: 'phonk',
    family: 'shockwave',
    badge: '💦',
    desc: "Rear semi-slick tires spraying twin 30-foot rooster tails of rainwater.",
    tag: "WATER ROOST",
    col: "#38bdf8"
  },
  {
    id: 'phonk_apex_kerb',
    name: "\ud83c\udfc1 Apex Kerb Shaker Vibration",
    category: 'phonk',
    family: 'shockwave',
    badge: '🏁',
    desc: "Rumble strips hammering the suspension on aggressive corner cutting.",
    tag: "KERB VIBRATION",
    col: "#facc15"
  },
  {
    id: 'phonk_police_radar',
    name: "\ud83d\udea8 Tokyo Police Radar Warning Strobe",
    category: 'phonk',
    family: 'tachometer',
    badge: '🚨',
    desc: "Red and blue police strobes reflected in rear-view mirror during high-speed getaway.",
    tag: "POLICE RADAR",
    col: "#3b82f6"
  },
  {
    id: 'phonk_speed_trap',
    name: "\ud83d\udcf8 Ghost Runner Speed Trap Flash",
    category: 'phonk',
    family: 'shockwave',
    badge: '📸',
    desc: "High-power overhead automated speed camera flash lighting up the cockpit.",
    tag: "SPEED TRAP",
    col: "#ffffff"
  },
  {
    id: 'phonk_camshaft_lope',
    name: "\u2699\ufe0f JDM Camshaft Lope Idle Shake",
    category: 'phonk',
    family: 'reactor',
    badge: '⚙️',
    desc: "Aggressive 280-degree high-lift camshafts making the engine lope and shake.",
    tag: "CAMSHAFT LOPE",
    col: "#78716c"
  },
  {
    id: 'phonk_fuel_pulse',
    name: "\u26fd High-Octane Fuel Injector Pulse",
    category: 'phonk',
    family: 'equalizer',
    badge: '⛽',
    desc: "1000cc fuel injectors spraying high-octane race fuel directly into cylinders.",
    tag: "FUEL PULSE",
    col: "#f59e0b"
  },
  {
    id: 'phonk_diffuser_vortex',
    name: "\ud83c\udf2a\ufe0f Carbon Kevlar Diffuser Vortex",
    category: 'phonk',
    family: 'tunnel',
    badge: '🌪️',
    desc: "Rear underbody venturi tunnels extracting high-velocity air in dual vortices.",
    tag: "DIFFUSER VORTEX",
    col: "#334155"
  },
  {
    id: 'phonk_warning_chime',
    name: "\ud83d\udd14 Japanese Speed Warning Chime Wave",
    category: 'phonk',
    family: 'equalizer',
    badge: '🔔',
    desc: "Nostalgic 'Ding-Dong' speed warning chime ringing at 105km/h on highway.",
    tag: "SPEED CHIME",
    col: "#fbbf24"
  },
  {
    id: 'phonk_headlight_trail',
    name: "\ud83c\udfce\ufe0f Midnight Street Racer Headlight Trail",
    category: 'phonk',
    family: 'starfield',
    badge: '🏎️',
    desc: "High-intensity HID projector beams carving white light tunnels into night.",
    tag: "HEADLIGHT TRAIL",
    col: "#e0e7ff"
  },
  {
    id: 'phonk_puddle_drift',
    name: "\ud83c\udf27\ufe0f Neon Cyber City Rain Puddle Drift",
    category: 'phonk',
    family: 'grid_3d',
    badge: '🌧️',
    desc: "Sideways car splashing through neon-lit street puddles in slow motion.",
    tag: "PUDDLE DRIFT",
    col: "#06b6d4"
  },
  {
    id: 'phonk_808_earthquake',
    name: "\ud83c\udf0d Aggressive 808 Sub-Bass Earthquake",
    category: 'phonk',
    family: 'shockwave',
    badge: '🌍',
    desc: "Maximum sub-bass saturation turning entire video frame into physical impact.",
    tag: "808 EARTHQUAKE",
    col: "#ef4444"
  },
  {
    id: 'phonk_drift_syndicate',
    name: "\ud83c\udf8c Tokyo Underground Drift Syndicate",
    category: 'phonk',
    family: 'drift_hud',
    badge: '🎌',
    desc: "Secret midnight street racing organization insignia glowing on car window.",
    tag: "DRIFT SYNDICATE",
    col: "#dc2626"
  },
  {
    id: 'phonk_overdrive_blast',
    name: "\u26a1 Hyperdrive Phonk Overdrive Blast",
    category: 'phonk',
    family: 'reactor',
    badge: '⚡',
    desc: "All reactor circuits overloaded into blinding burst of speed and neon.",
    tag: "OVERDRIVE BLAST",
    col: "#00f2fe"
  },
  {
    id: 'phonk_infinite_legend',
    name: "\ud83d\udc51 Infinite JDM Drift Legend",
    category: 'phonk',
    family: 'trap_nation',
    badge: '👑',
    desc: "The immortal spirit of Japanese touge drift racing reigning supreme forever.",
    tag: "INFINITE LEGEND",
    col: "#a855f7"
  },
];
