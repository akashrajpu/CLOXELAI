// Phonk & Beat Visualizer Presets Library (100% Unique Curated FX Styles)
// Categorized by Song Mood: Romantic, Sad, Devotional, Lo-Fi, Party, Acoustic, Phonk.
// Each preset has distinct mathematical formulations, unique geometry, and animation behavior.

export const MOOD_VISUALIZER_INFO = {
  romantic: {
    title: '💖 Romantic & Love Beat Reactors',
    desc: 'Glowing heartbeat pulse, floating radiating hearts, cupid halos aur warm golden romance auras.',
    defaultId: 'romantic_auto'
  },
  sad: {
    title: '💔 Melancholy & Sad Beat Reactors',
    desc: 'Falling rain streaks, tear ripples on drops, shattered glass fragments aur cold dark noir ripples.',
    defaultId: 'sad_auto'
  },
  devotional: {
    title: '🪔 Sacred Divine & Bhakti Beat Reactors',
    desc: 'Expanding golden chakra rays, Sudarshan chakra, temple diya flame pulse aur celestial aarti halos.',
    defaultId: 'devotional_auto'
  },
  lofi: {
    title: '🌙 Cozy Lo-Fi & Chill Beat Reactors',
    desc: 'Rotating vinyl record grooves, vintage cassette spool, midnight star dust aur lavender waveforms.',
    defaultId: 'lofi_auto'
  },
  party: {
    title: '⚡ Party & EDM Rave Beat Reactors',
    desc: 'Concert rave lasers, high-voltage plasma arcs, bass shockwaves aur 360° club strobe cannons.',
    defaultId: 'party_auto'
  },
  acoustic: {
    title: '🎸 Acoustic & Indie Beat Reactors',
    desc: 'Analog sine oscilloscope ribbons, six-string guitar vibrations, campfire embers aur dewdrop ripples.',
    defaultId: 'acoustic_auto'
  },
  phonk: {
    title: '🔥 Phonk, Drift & 808 Beat Reactors',
    desc: 'Trap Nation 3-lobe core, 360° radial reactor, Tokyo drift camera vibration, JDM gauges aur 3D synth grid.',
    defaultId: 'phonk_auto'
  }
};

export const PHONK_VISUALIZER_CATEGORIES = [
  { id: 'all', label: '🔥 All Mood FX' },
  { id: 'romantic', label: '❤️ Romantic / Love' },
  { id: 'sad', label: '💔 Sad / Dard' },
  { id: 'devotional', label: '🪔 Bhakti / Devotional' },
  { id: 'lofi', label: '🌙 Lo-Fi / Chill' },
  { id: 'party', label: '⚡ Party / Rave' },
  { id: 'acoustic', label: '🎸 Acoustic / Indie' },
  { id: 'phonk', label: '🏎️ Phonk / Drift' }
];

export const PHONK_VISUALIZER_PRESETS = [
  // ============================================================================
  // ❤️ ROMANTIC / LOVE (22 Curated Unique FX)
  // ============================================================================
  {
    id: 'romantic_auto',
    name: '🎲 Auto Love Reactor (Random Shuffle)',
    category: 'romantic',
    family: 'romantic',
    badge: '🎲',
    desc: 'Automatic selection: Love gaane ke rhythm ke anusaar random floating hearts & glow styles shuffle honge!',
    tag: 'AUTO DEFAULT',
    col: '#f43f5e'
  },
  {
    id: 'romantic_heart',
    name: '💖 Romantic Heart Pulse Core',
    category: 'romantic',
    family: 'romantic',
    badge: '💖',
    desc: 'Center Circle Logo + Glowing Heartbeat Pulse + Radiating Floating Hearts on bass drops.',
    tag: 'HEART CORE',
    col: '#f43f5e'
  },
  {
    id: 'romantic_cupid_halo',
    name: "💘 Cupid's Arrow Halo Orbit",
    category: 'romantic',
    family: 'romantic',
    badge: '💘',
    desc: 'Dual golden cupid arrows revolving around the center logo with sparkling stardust trail.',
    tag: 'CUPID HALO',
    col: '#fb7185'
  },
  {
    id: 'romantic_rose_burst',
    name: '🌹 Rose Petal Bloom Shockwave',
    category: 'romantic',
    family: 'romantic',
    badge: '🌹',
    desc: 'Concentric rose petal petals opening outward on every heavy bass beat with soft pink aura.',
    tag: 'ROSE BLOOM',
    col: '#e11d48'
  },
  {
    id: 'romantic_dual_entangled',
    name: '💑 Dual Entangled Hearts Pulse',
    category: 'romantic',
    family: 'romantic',
    badge: '💑',
    desc: 'Twin interlocking glowing cardioid hearts beating in syncopated rhythm with audio sub-bass.',
    tag: 'TWIN HEARTS',
    col: '#ec4899'
  },
  {
    id: 'romantic_starlight_lovers',
    name: '✨ Starlight Lovers Orbital Halo',
    category: 'romantic',
    family: 'romantic',
    badge: '✨',
    desc: 'Gentle golden celestial constellation rings orbiting center emblem with warm twilight glow.',
    tag: 'STARLIGHT',
    col: '#f59e0b'
  },
  {
    id: 'romantic_crimson_velvet',
    name: '🍷 Crimson Velvet Bass Echo',
    category: 'romantic',
    family: 'romantic',
    badge: '🍷',
    desc: 'Deep crimson velvet wave rings echoing outwards like candlelit ripples on a romantic night.',
    tag: 'VELVET WAVE',
    col: '#be123c'
  },
  {
    id: 'romantic_neon_ribbon',
    name: '🎀 Neon Ribbon Cardioid Wave',
    category: 'romantic',
    family: 'romantic',
    badge: '🎀',
    desc: 'Silky smooth neon pink silk ribbons weaving in fluid mathematical figure-8 waves.',
    tag: 'NEON RIBBON',
    col: '#f472b6'
  },
  {
    id: 'romantic_sunset_kiss',
    name: '🌅 Sunset Kiss Golden Halo',
    category: 'romantic',
    family: 'romantic',
    badge: '🌅',
    desc: 'Warm golden hour sunbeam rays and soft lens flares pulsating smoothly on vocal hooks.',
    tag: 'SUNSET KISS',
    col: '#f97316'
  },
  {
    id: 'romantic_ruby_gem',
    name: '💎 Ruby Gem Heart Radiance',
    category: 'romantic',
    family: 'romantic',
    badge: '💎',
    desc: 'Faceted 3D ruby heart geometry refracting crimson laser sparkles on kick drum hits.',
    tag: 'RUBY GEM',
    col: '#e11d48'
  },
  {
    id: 'romantic_sakura_drift',
    name: '🌸 Sakura Blossom Particle Drift',
    category: 'romantic',
    family: 'romantic',
    badge: '🌸',
    desc: 'Delicate Japanese cherry blossom petals swirling upwards in a gentle romantic wind.',
    tag: 'SAKURA',
    col: '#fbcfe8'
  },
  {
    id: 'romantic_floating_fountain',
    name: '⛲ Floating Hearts Fountain',
    category: 'romantic',
    family: 'romantic',
    badge: '⛲',
    desc: 'Continuous stream of miniature glowing neon hearts erupting from bottom to top of screen.',
    tag: 'FOUNTAIN',
    col: '#ec4899'
  },
  {
    id: 'romantic_pink_pulsar',
    name: '💓 Pink Neon Glow Pulsar',
    category: 'romantic',
    family: 'romantic',
    badge: '💓',
    desc: 'High-contrast neon pink perimeter ring expanding with double-thump human heartbeat timing.',
    tag: 'PULSAR',
    col: '#ff2d55'
  },
  {
    id: 'romantic_eternal_mobius',
    name: '♾️ Eternal Romance Möbius Ring',
    category: 'romantic',
    family: 'romantic',
    badge: '♾️',
    desc: 'Twisted infinity loop glowing in gradient magenta, symbolizing endless romantic devotion.',
    tag: 'INFINITY',
    col: '#d946ef'
  },
  {
    id: 'romantic_velvet_shockwave',
    name: '💥 Velvet Heart Bass Drop',
    category: 'romantic',
    family: 'romantic',
    badge: '💥',
    desc: 'Massive heart-shaped sonic blast wave bursting outwards when the romantic chorus drops.',
    tag: 'BASS BURST',
    col: '#e11d48'
  },
  {
    id: 'romantic_warm_embrace',
    name: '🫂 Warm Embrace Orbit',
    category: 'romantic',
    family: 'romantic',
    badge: '🫂',
    desc: 'Two protective glowing golden-rose rings shielding the center logo with soothing warmth.',
    tag: 'EMBRACE',
    col: '#fbbf24'
  },
  {
    id: 'romantic_shooting_star',
    name: '💫 Shooting Star Romance Orbit',
    category: 'romantic',
    family: 'romantic',
    badge: '💫',
    desc: 'Twin celestial shooting stars tracing an infinity love path around the emblem logo.',
    tag: 'SHOOTING STAR',
    col: '#fb7185'
  },
  {
    id: 'romantic_twilight_fireflies',
    name: '🌟 Twilight Firefly Glow',
    category: 'romantic',
    family: 'romantic',
    badge: '🌟',
    desc: 'Radiant glowing warm fireflies drifting upward on soft romantic melodies.',
    tag: 'FIREFLIES',
    col: '#f43f5e'
  },
  {
    id: 'romantic_aurora_veil',
    name: '🌌 Aurora Borealis Love Veil',
    category: 'romantic',
    family: 'romantic',
    badge: '🌌',
    desc: 'Shimmering magenta and emerald northern lights curtain undulating behind center portrait.',
    tag: 'AURORA',
    col: '#ec4899'
  },
  {
    id: 'romantic_golden_constellation',
    name: '🌠 Lovers Constellation Star Map',
    category: 'romantic',
    family: 'romantic',
    badge: '🌠',
    desc: 'Astrological heart constellation connecting glowing star nodes with golden lines.',
    tag: 'CONSTELLATION',
    col: '#fbbf24'
  },
  {
    id: 'romantic_lotus_pond',
    name: '🪷 Floating Water Lily Bloom',
    category: 'romantic',
    family: 'romantic',
    badge: '🪷',
    desc: 'Pink water lilies blossoming outward with serene concentric pond ripples on beats.',
    tag: 'WATER LILY',
    col: '#fda4af'
  },
  {
    id: 'romantic_crystal_chandelier',
    name: '🔮 Crystal Prism Love Chandelier',
    category: 'romantic',
    family: 'romantic',
    badge: '🔮',
    desc: 'Sparkling chandelier light refracts faceted rainbow heart glimmers on bass drops.',
    tag: 'CRYSTAL PRISM',
    col: '#f472b6'
  },

  // ============================================================================
  // 💔 SAD / DARD / BROKEN (20 Curated Unique FX)
  // ============================================================================
  {
    id: 'sad_auto',
    name: '🎲 Auto Sad Reactor (Random Shuffle)',
    category: 'sad',
    family: 'sad',
    badge: '🎲',
    desc: 'Automatic selection: Dard bhare gaane ke liye atmospheric rain & broken glass randomly match honge!',
    tag: 'AUTO DEFAULT',
    col: '#38bdf8'
  },
  {
    id: 'sad_rain',
    name: '💔 Melancholy Rain Drop Core',
    category: 'sad',
    family: 'sad',
    badge: '💔',
    desc: 'Center Circle Logo + Atmospheric Rain Streaks + Tear Ripples on Bass Drops.',
    tag: 'RAIN CORE',
    col: '#38bdf8'
  },
  {
    id: 'sad_broken_heart',
    name: '💔 Shattered Heart Glass Shards',
    category: 'sad',
    family: 'sad',
    badge: '💔',
    desc: 'Center heart shape fracturing into sharp crystalline shards on emotional vocal peaks.',
    tag: 'BROKEN GLASS',
    col: '#94a3b8'
  },
  {
    id: 'sad_tear_stream',
    name: '💧 Midnight Tear Drops Stream',
    category: 'sad',
    family: 'sad',
    badge: '💧',
    desc: 'Slowly falling luminous blue tear streaks creating circular water ripples on bass impacts.',
    tag: 'TEARS',
    col: '#60a5fa'
  },
  {
    id: 'sad_rainy_window',
    name: '🪟 Rainy Window Pane Droplets',
    category: 'sad',
    family: 'sad',
    badge: '🪟',
    desc: 'Cinematic rain droplets racing down glass with realistic refraction and moody streetlamp glow.',
    tag: 'WINDOW RAIN',
    col: '#0284c7'
  },
  {
    id: 'sad_lonely_fog',
    name: '🌫️ Lonely Cold Fog Dispersion',
    category: 'sad',
    family: 'sad',
    badge: '🌫️',
    desc: 'Dense cold mist and drifting fog clouds pulsing slowly around the solitary center avatar.',
    tag: 'FOG MIST',
    col: '#64748b'
  },
  {
    id: 'sad_ice_shards',
    name: '🧊 Frozen Tears Ice Shard Pulse',
    category: 'sad',
    family: 'sad',
    badge: '🧊',
    desc: 'Sharp cyan frost crystals forming and cracking outward on heavy melancholy drum beats.',
    tag: 'FROST ICE',
    col: '#22d3ee'
  },
  {
    id: 'sad_solitary_ripple',
    name: '🌊 Solitary Lake Bass Ripple',
    category: 'sad',
    family: 'sad',
    badge: '🌊',
    desc: 'Deep indigo water ripples expanding across a desolate midnight lake surface.',
    tag: 'WATER RIPPLE',
    col: '#3b82f6'
  },
  {
    id: 'sad_noir_shadow',
    name: '🖤 Noir Shadow Drizzle Pulse',
    category: 'sad',
    family: 'sad',
    badge: '🖤',
    desc: 'High-contrast monochrome black & white vignette with sharp diagonal rain streaks.',
    tag: 'NOIR MONO',
    col: '#e2e8f0'
  },
  {
    id: 'sad_withered_petal',
    name: '🥀 Withered Black Rose Drift',
    category: 'sad',
    family: 'sad',
    badge: '🥀',
    desc: 'Dried dark rose petals falling in slow-motion, symbolizing lost love and memories.',
    tag: 'WITHERED',
    col: '#9f1239'
  },
  {
    id: 'sad_heavy_downpour',
    name: '⛈️ Heavy Downpour Thunder Pulse',
    category: 'sad',
    family: 'sad',
    badge: '⛈️',
    desc: 'Violent torrential rain streaks with brief subtle lightning flashes on thunderous sub-bass drops.',
    tag: 'DOWNPOUR',
    col: '#0ea5e9'
  },
  {
    id: 'sad_gray_halo',
    name: '🌪️ Distant Memory Gray Horizon',
    category: 'sad',
    family: 'sad',
    badge: '🌪️',
    desc: 'Somber ash-gray frequency ring slowly dissipating into the dark atmospheric background.',
    tag: 'GRAY HORIZON',
    col: '#475569'
  },
  {
    id: 'sad_bleeding_ink',
    name: '🖋️ Bleeding Indigo Ink Vignette',
    category: 'sad',
    family: 'sad',
    badge: '🖋️',
    desc: 'Dark blue watercolor ink stains blooming organically around the center emblem on bass notes.',
    tag: 'INK BLEED',
    col: '#4338ca'
  },
  {
    id: 'sad_somber_echo',
    name: '🔕 Somber Silence Sonic Echo',
    category: 'sad',
    family: 'sad',
    badge: '🔕',
    desc: 'Minimalist thin cyan perimeter line vibrating gently with sub-bass like a faint heartbeat monitor.',
    tag: 'MINIMAL ECHO',
    col: '#38bdf8'
  },
  {
    id: 'sad_abandoned_lighthouse',
    name: '🗼 Distant Foggy Lighthouse',
    category: 'sad',
    family: 'sad',
    badge: '🗼',
    desc: 'Faint sweeping beacon cutting through dense ocean fog and somber rain.',
    tag: 'LIGHTHOUSE',
    col: '#64748b'
  },
  {
    id: 'sad_echoing_piano_chords',
    name: '🎹 Echoing Broken Piano Waveform',
    category: 'sad',
    family: 'sad',
    badge: '🎹',
    desc: 'Minor chord harmonic sound waves disintegrating into rain drops.',
    tag: 'PIANO WAVE',
    col: '#94a3b8'
  },
  {
    id: 'sad_wilted_autumn_leaves',
    name: '🍂 Falling Autumn Dead Leaves',
    category: 'sad',
    family: 'sad',
    badge: '🍂',
    desc: 'Crisp amber-brown dried leaves swirling downward in cold November breeze.',
    tag: 'AUTUMN DRIFT',
    col: '#78716c'
  },
  {
    id: 'sad_shattered_clock',
    name: '🕰️ Fractured Timepiece Shards',
    category: 'sad',
    family: 'sad',
    badge: '🕰️',
    desc: 'Broken watch gears and glass ticking in reverse with hollow bass resonance.',
    tag: 'BROKEN TIME',
    col: '#475569'
  },
  {
    id: 'sad_candle_in_wind',
    name: '🕯️ Flickering Candle in Wind',
    category: 'sad',
    family: 'sad',
    badge: '🕯️',
    desc: 'Fragile single wax candle flame struggling against heavy rain drops on bass pulse.',
    tag: 'FLICKER',
    col: '#cbd5e1'
  },
  {
    id: 'sad_ocean_abyss',
    name: '🌊 Midnight Ocean Abyss Wave',
    category: 'sad',
    family: 'sad',
    badge: '🌊',
    desc: 'Dark midnight oceanic swell rising and falling with deep melancholic sub-bass.',
    tag: 'DEEP ABYSS',
    col: '#38bdf8'
  },

  // ============================================================================
  // 🪔 DEVOTIONAL / BHAKTI (22 Curated Unique FX)
  // ============================================================================
  {
    id: 'devotional_auto',
    name: '🎲 Auto Bhakti Reactor (Random Shuffle)',
    category: 'devotional',
    family: 'devotional',
    badge: '🎲',
    desc: 'Automatic selection: Bhakti aur mantra ke liye divine sacred chakra aur diya flame auto-shuffle honge!',
    tag: 'AUTO DEFAULT',
    col: '#f59e0b'
  },
  {
    id: 'devotional_chakra',
    name: '🪔 Sacred Divine Aura Chakra',
    category: 'devotional',
    family: 'devotional',
    badge: '🪔',
    desc: 'Center Circle Logo + Expanding Golden Chakra Rays + Diya Flame Pulse.',
    tag: 'CHAKRA CORE',
    col: '#f59e0b'
  },
  {
    id: 'devotional_sudarshan',
    name: '☸️ Maha Sudarshan Chakra Radiance',
    category: 'devotional',
    family: 'devotional',
    badge: '☸️',
    desc: 'Spinning sacred golden disc with 32 razor-sharp energy teeth emitting divine golden light.',
    tag: 'SUDARSHAN',
    col: '#facc15'
  },
  {
    id: 'devotional_temple_flame',
    name: '🔥 Mandir Akhand Jyoti Flame',
    category: 'devotional',
    family: 'devotional',
    badge: '🔥',
    desc: 'Pure golden temple brass diya flame rising and pulsing in rhythm with devotional dholak beats.',
    tag: 'AKHAND JYOTI',
    col: '#ea580c'
  },
  {
    id: 'devotional_omkar_ring',
    name: '🕉️ Omkar Celestial Ring',
    category: 'devotional',
    family: 'devotional',
    badge: '🕉️',
    desc: 'Sacred primordial OM cosmic resonance wave pulsating around the divine avatar emblem.',
    tag: 'OMKAR RING',
    col: '#f59e0b'
  },
  {
    id: 'devotional_temple_bell',
    name: '🔔 Temple Ghanta Sonic Wave',
    category: 'devotional',
    family: 'devotional',
    badge: '🔔',
    desc: 'Acoustic brass resonance rings expanding outwards simulating the deep chime of a mandir bell.',
    tag: 'TEMPLE BELL',
    col: '#eab308'
  },
  {
    id: 'devotional_aarti_ripple',
    name: '🪔 Maha Aarti Thali Orbit Rays',
    category: 'devotional',
    family: 'devotional',
    badge: '🪔',
    desc: 'Golden circular aarti lamps revolving in sacred pradakshina orbit with warm amber radiance.',
    tag: 'AARTI THALI',
    col: '#f97316'
  },
  {
    id: 'devotional_lotus_bloom',
    name: '🪷 Sahasrara Golden Lotus Bloom',
    category: 'devotional',
    family: 'devotional',
    badge: '🪷',
    desc: '1000-petal divine golden lotus unfolding gracefully beneath the sanctified center portrait.',
    tag: 'GOLDEN LOTUS',
    col: '#fbbf24'
  },
  {
    id: 'devotional_mantra_orbit',
    name: '📿 Vedic Sacred Japa Orbit Ring',
    category: 'devotional',
    family: 'devotional',
    badge: '📿',
    desc: '108 glowing celestial prayer beads circulating in sacred geometric alignment on kirtan drops.',
    tag: 'JAPA MALA',
    col: '#d97706'
  },
  {
    id: 'devotional_trishul_halo',
    name: '🔱 Mahadev Trishul Energy Aura',
    category: 'devotional',
    family: 'devotional',
    badge: '🔱',
    desc: 'Cosmic electric blue & golden trishul aura emitting powerful Rudra energy pulses on damru hits.',
    tag: 'TRISHUL ENERGY',
    col: '#0284c7'
  },
  {
    id: 'devotional_swarna_pushpa',
    name: '🌼 Swarna Pushpa Divine Shower',
    category: 'devotional',
    family: 'devotional',
    badge: '🌼',
    desc: 'Shower of blessed golden marigold petals raining gently around the sanctum sanctorum.',
    tag: 'FLOWER SHOWER',
    col: '#eab308'
  },
  {
    id: 'devotional_divine_surya',
    name: '☀️ Surya Dev Golden Rays Aura',
    category: 'devotional',
    family: 'devotional',
    badge: '☀️',
    desc: '360° celestial solar corona radiating pure golden morning light and positive spiritual energy.',
    tag: 'SURYA RAYS',
    col: '#f59e0b'
  },
  {
    id: 'devotional_kailash_mystic',
    name: '🏔️ Kailash Peak Mystic Glow',
    category: 'devotional',
    family: 'devotional',
    badge: '🏔️',
    desc: 'Divine ethereal blue moonlight reflecting off sacred snow peaks with shimmering celestial frost.',
    tag: 'KAILASH GLOW',
    col: '#38bdf8'
  },
  {
    id: 'devotional_rudraksha_core',
    name: '📿 Rudraksha Sacred Mala Beads',
    category: 'devotional',
    family: 'devotional',
    badge: '📿',
    desc: 'Sacred Panchmukhi Rudraksha perimeter ring pulsating with spiritual grounding frequencies.',
    tag: 'RUDRAKSHA',
    col: '#92400e'
  },
  {
    id: 'devotional_shankh_wave',
    name: '🐚 Panchajanya Sacred Conch Wave',
    category: 'devotional',
    family: 'devotional',
    badge: '🐚',
    desc: 'Spiral sound geometry reproducing the holy vibrational frequency of the sacred Shankh blast.',
    tag: 'SHANKH DHUN',
    col: '#f8fafc'
  },
  {
    id: 'devotional_golden_kalash',
    name: '🏺 Amrit Kalash Celestial Halo',
    category: 'devotional',
    family: 'devotional',
    badge: '🏺',
    desc: 'Sacred Kalash with mango leaves and coconut halo radiating divine nectar and auspicious blessings.',
    tag: 'AMRIT KALASH',
    col: '#f59e0b'
  },
  {
    id: 'devotional_ganga_aarti',
    name: '🪔 Haridwar Ganga Aarti Deepam',
    category: 'devotional',
    family: 'devotional',
    badge: '🪔',
    desc: '108 blazing oil lamps swirling in sacred clockwise circle with golden bells.',
    tag: 'DEEPAM AARTI',
    col: '#f59e0b'
  },
  {
    id: 'devotional_nandi_dhun',
    name: '🐂 Sacred Nandi Damru Wave',
    category: 'devotional',
    family: 'devotional',
    badge: '🐂',
    desc: "Lord Shiva's divine damru rhythm pulses expanding cosmic sound waves outward.",
    tag: 'DAMRU DHUN',
    col: '#eab308'
  },
  {
    id: 'devotional_garuda_wings',
    name: '🦅 Celestial Garuda Feather Halo',
    category: 'devotional',
    family: 'devotional',
    badge: '🦅',
    desc: 'Golden divine wings fanning sacred radiance and celestial light rays.',
    tag: 'GARUDA HALO',
    col: '#fbbf24'
  },
  {
    id: 'devotional_radha_krishna_flute',
    name: '🪈 Vaikuntha Bansuri Melodic Stream',
    category: 'devotional',
    family: 'devotional',
    badge: '🪈',
    desc: 'Divine peacock feather and golden melodic note particles orbiting the avatar.',
    tag: 'BANSURI VIBE',
    col: '#ca8a04'
  },
  {
    id: 'devotional_hanuman_gada',
    name: '🚩 Mahabali Hanuman Golden Aura',
    category: 'devotional',
    family: 'devotional',
    badge: '🚩',
    desc: 'Blazing saffron aura with invulnerable protective energy shield on drops.',
    tag: 'SANKAT MOCHAN',
    col: '#f97316'
  },
  {
    id: 'devotional_shiva_trinetra',
    name: '👁️ Trinetra Cosmic Third-Eye Beam',
    category: 'devotional',
    family: 'devotional',
    badge: '👁️',
    desc: 'Piercing divine third-eye golden beam dissolving ignorance with cosmic vibration.',
    tag: 'THIRD EYE',
    col: '#e11d48'
  },

  // ============================================================================
  // 🌙 LO-FI / CHILL VIBES (20 Curated Unique FX)
  // ============================================================================
  {
    id: 'lofi_auto',
    name: '🎲 Auto Lo-Fi Reactor (Random Shuffle)',
    category: 'lofi',
    family: 'lofi',
    badge: '🎲',
    desc: 'Automatic selection: Lo-Fi beats ke liye vinyl disc, cassette spool aur star dust auto-match honge!',
    tag: 'AUTO DEFAULT',
    col: '#a855f7'
  },
  {
    id: 'lofi_vinyl',
    name: '🌙 Cozy Lo-Fi Vinyl Spin Core',
    category: 'lofi',
    family: 'lofi',
    badge: '🌙',
    desc: 'Center Circle Logo + Rotating Vinyl Record Disc + Soft Lavender Starfield.',
    tag: 'VINYL SPIN',
    col: '#a855f7'
  },
  {
    id: 'lofi_cassette_spool',
    name: '📼 Retro Cassette Tape Reel Spool',
    category: 'lofi',
    family: 'lofi',
    badge: '📼',
    desc: 'Dual magnetic tape spools revolving gently with warm analog cassette hiss dust.',
    tag: 'CASSETTE REEL',
    col: '#8b5cf6'
  },
  {
    id: 'lofi_midnight_stars',
    name: '✨ Lavender Midnight Star Dust',
    category: 'lofi',
    family: 'lofi',
    badge: '✨',
    desc: 'Drifting pastel purple and blue starfield with twinkling starlight around center frame.',
    tag: 'STAR DUST',
    col: '#c084fc'
  },
  {
    id: 'lofi_rainy_cafe',
    name: '☕ Tokyo Night Cafe Rainy Neon',
    category: 'lofi',
    family: 'lofi',
    badge: '☕',
    desc: 'Soft blurred amber cafe neon lights glowing through foggy rain streaks on glass.',
    tag: 'COZY CAFE',
    col: '#f59e0b'
  },
  {
    id: 'lofi_sunset_clouds',
    name: '☁️ Anime Pastel Cloud Horizon',
    category: 'lofi',
    family: 'lofi',
    badge: '☁️',
    desc: 'Dreamy pastel pink and lavender cloud layers drifting peacefully across sunset sky.',
    tag: 'PASTEL CLOUDS',
    col: '#f472b6'
  },
  {
    id: 'lofi_vhs_tracking',
    name: '📺 Vintage VHS Tape Tracking Glitch',
    category: 'lofi',
    family: 'lofi',
    badge: '📺',
    desc: 'Authentic 90s VHS tape scanlines and subtle magnetic distortion on lo-fi snare hits.',
    tag: 'VHS GLITCH',
    col: '#06b6d4'
  },
  {
    id: 'lofi_tea_steam',
    name: '🍵 Warm Green Tea Vapor Ripple',
    category: 'lofi',
    family: 'lofi',
    badge: '🍵',
    desc: 'Soothing curls of fragrant matcha tea steam swirling upwards in tranquil motion.',
    tag: 'TEA VAPOR',
    col: '#10b981'
  },
  {
    id: 'lofi_retro_waveform',
    name: '📻 Retro Radio Waveform Ribbon',
    category: 'lofi',
    family: 'lofi',
    badge: '📻',
    desc: 'Smooth curved oscilloscope sine ribbon simulating warm vacuum tube radio reception.',
    tag: 'RADIO WAVE',
    col: '#a78bfa'
  },
  {
    id: 'lofi_sleepwalker_orbit',
    name: '🌌 Sleepwalker Celestial Orbit',
    category: 'lofi',
    family: 'lofi',
    badge: '🌌',
    desc: 'Crescent moon and planetary orbit rings revolving in hypnotic midnight trance.',
    tag: 'MOON ORBIT',
    col: '#6366f1'
  },
  {
    id: 'lofi_paper_airplane',
    name: '✈️ Origami Airplane Cloud Drift',
    category: 'lofi',
    family: 'lofi',
    badge: '✈️',
    desc: 'White paper airplane gliding smoothly on gentle lo-fi bass breeze with dashed trail.',
    tag: 'ORIGAMI',
    col: '#e2e8f0'
  },
  {
    id: 'lofi_city_rain',
    name: '🏙️ Cyber Lofi Rainy Skyline Pulse',
    category: 'lofi',
    family: 'lofi',
    badge: '🏙️',
    desc: 'Distant metropolitan skyscraper silhouette with flickering warm apartment windows.',
    tag: 'LOFI SKYLINE',
    col: '#3b82f6'
  },
  {
    id: 'lofi_bonsai_tree',
    name: '🪴 Zen Bonsai Tree Silhouette',
    category: 'lofi',
    family: 'lofi',
    badge: '🪴',
    desc: 'Peaceful Japanese bonsai silhouette with falling cherry blossoms in meditative aura.',
    tag: 'ZEN BONSAI',
    col: '#059669'
  },
  {
    id: 'lofi_twilight_lamp',
    name: '🏮 Twilight Paper Lantern Glow',
    category: 'lofi',
    family: 'lofi',
    badge: '🏮',
    desc: 'Traditional Japanese red paper lanterns swaying gently in the night breeze.',
    tag: 'LANTERN',
    col: '#f43f5e'
  },
  {
    id: 'lofi_rainy_bus_stop',
    name: '🚏 Midnight Rainy Bus Stop',
    category: 'lofi',
    family: 'lofi',
    badge: '🚏',
    desc: 'Fluorescent street lamp glowing in drizzle with gentle retro bus engine hum.',
    tag: 'BUS STOP',
    col: '#818cf8'
  },
  {
    id: 'lofi_bookstore_lamp',
    name: '📚 Cozy Midnight Library Glow',
    category: 'lofi',
    family: 'lofi',
    badge: '📚',
    desc: 'Amber study lamp glow with flying book pages drifting peacefully on low-fi beats.',
    tag: 'MIDNIGHT BOOK',
    col: '#a78bfa'
  },
  {
    id: 'lofi_retro_pixel_city',
    name: '👾 8-Bit Pixel Sunset Skyline',
    category: 'lofi',
    family: 'lofi',
    badge: '👾',
    desc: 'Nostalgic 16-bit pixel art skyscraper silhouettes with 80s arcade sunset.',
    tag: 'PIXEL CITY',
    col: '#c084fc'
  },
  {
    id: 'lofi_cat_window',
    name: '🐱 Cat on Rainy Windowsill',
    category: 'lofi',
    family: 'lofi',
    badge: '🐱',
    desc: 'Sleepy silhouette of cat watching rain droplets race down the glass pane.',
    tag: 'PURR & CHILL',
    col: '#e879f9'
  },
  {
    id: 'lofi_polaroid_memories',
    name: '📷 Floating Polaroid Drift',
    category: 'lofi',
    family: 'lofi',
    badge: '📷',
    desc: 'Nostalgic instant film photo borders floating with soft sepia flash on kick drums.',
    tag: 'POLAROID',
    col: '#a855f7'
  },
  {
    id: 'lofi_cassette_pencil_rewind',
    name: '✏️ Cassette Tape Pencil Spool',
    category: 'lofi',
    family: 'lofi',
    badge: '✏️',
    desc: 'Vintage magnetic tape winding gently around vintage yellow pencil.',
    tag: 'REWIND TAPE',
    col: '#9333ea'
  },

  // ============================================================================
  // ⚡ PARTY / HIGH ENERGY / RAVE (20 Curated Unique FX)
  // ============================================================================
  {
    id: 'party_auto',
    name: '🎲 Auto Party Reactor (Random Shuffle)',
    category: 'party',
    family: 'party',
    badge: '🎲',
    desc: 'Automatic selection: Club & EDM party ke liye lasers, shockwaves aur strobes auto-shuffle honge!',
    tag: 'AUTO DEFAULT',
    col: '#00f2fe'
  },
  {
    id: 'laser_strobe',
    name: '🔦 Cyber Laser Stage Strobes',
    category: 'party',
    family: 'party',
    badge: '🔦',
    desc: 'Rave club concert laser beams sweeping in multi-fan formations across the screen.',
    tag: 'LASER BEAMS',
    col: '#00f2fe'
  },
  {
    id: 'party_shockwave_blast',
    name: '💥 Multi-Ring Sonic Bass Shockwave',
    category: 'party',
    family: 'party',
    badge: '💥',
    desc: 'Triple high-velocity circular sonic pressure rings expanding outward on heavy bass drops.',
    tag: 'SHOCKWAVE',
    col: '#ec4899'
  },
  {
    id: 'party_neon_laser_grid',
    name: '🌐 Neon Club 3D Laser Ceiling Grid',
    category: 'party',
    family: 'party',
    badge: '🌐',
    desc: 'Sweeping cyberpunk club ceiling laser matrix illuminating the venue in synchronized grid lines.',
    tag: 'LASER GRID',
    col: '#a855f7'
  },
  {
    id: 'party_plasma_arc',
    name: '⚡ High-Voltage Plasma Arc Reactor',
    category: 'party',
    family: 'party',
    badge: '⚡',
    desc: 'Electric tesla coil arcs leaping between electrodes with crackling violet lightning bolts.',
    tag: 'PLASMA ARC',
    col: '#38bdf8'
  },
  {
    id: 'party_acid_equalizer',
    name: '🟢 Acid Glow Dual Equalizer',
    category: 'party',
    family: 'party',
    badge: '🟢',
    desc: 'Toxic green and electric cyan frequency towers pulsing to 140 BPM techno basslines.',
    tag: 'ACID EQUALIZER',
    col: '#22c55e'
  },
  {
    id: 'party_edm_radial_ring',
    name: '⭕ Ultra EDM 360° Circular Ring',
    category: 'party',
    family: 'party',
    badge: '⭕',
    desc: '360-degree dense radial audio equalizer needles exploding outward with bass frequency spikes.',
    tag: 'EDM 360',
    col: '#e11d48'
  },
  {
    id: 'party_strobe_pulsar',
    name: '🎆 Festival Strobe Fireworks Pulsar',
    category: 'party',
    family: 'party',
    badge: '🎆',
    desc: 'High-speed white and neon strobing flashes simulating mainstage Tomorrowland pyrotechnics.',
    tag: 'FESTIVAL STROBE',
    col: '#fbbf24'
  },
  {
    id: 'party_bass_cannon',
    name: '🔊 Subwoofer Pressure Cannon',
    category: 'party',
    family: 'party',
    badge: '🔊',
    desc: 'Concentric audio pressure cones vibrating violently on sub-bass drops with RGB chromatic flash.',
    tag: 'BASS CANNON',
    col: '#f97316'
  },
  {
    id: 'party_equalizer_dome',
    name: '🌐 Neon Equalizer Dome Arena',
    category: 'party',
    family: 'party',
    badge: '🌐',
    desc: '3D hemispherical dome of pulsating audio spectrum towers creating an immersive club arena.',
    tag: 'SPECTRUM DOME',
    col: '#8b5cf6'
  },
  {
    id: 'party_rainbow_strobe',
    name: '🌈 Spectrum Prism Laser Fan',
    category: 'party',
    family: 'party',
    badge: '🌈',
    desc: 'Full-spectrum RGB rainbow laser fans spreading across the ceiling in synchronized sweep.',
    tag: 'RAINBOW FAN',
    col: '#06b6d4'
  },
  {
    id: 'party_cyber_laser_fan',
    name: '🪭 Cyberpunk Multi-Beam Fan',
    category: 'party',
    family: 'party',
    badge: '🪭',
    desc: '16 high-intensity cyan laser shafts rotating in opposite directions with angular precision.',
    tag: 'BEAM FAN',
    col: '#00f2fe'
  },
  {
    id: 'party_hyper_drop',
    name: '🚀 150 BPM Bass Drop Sonic Cone',
    category: 'party',
    family: 'party',
    badge: '🚀',
    desc: 'Extreme screen-wide chromatic blast with warp-speed tunnel expansion on the main build-up drop.',
    tag: 'HYPER DROP',
    col: '#f43f5e'
  },
  {
    id: 'party_acid_orbit',
    name: '🧪 Acid Glow Dual Ring Orbit',
    category: 'party',
    family: 'party',
    badge: '🧪',
    desc: 'Intersecting fluorescent yellow and ultraviolet rings spinning with intense party energy.',
    tag: 'ACID ORBIT',
    col: '#eab308'
  },
  {
    id: 'party_sub_woofer_vibration',
    name: '🔊 1000W Subwoofer Cone Vibration',
    category: 'party',
    family: 'party',
    badge: '🔊',
    desc: 'Mechanical speaker cone punching forward with extreme air displacement rings.',
    tag: 'SUB CONE',
    col: '#06b6d4'
  },
  {
    id: 'party_las_vegas_neon_strip',
    name: '🎰 Cyber Neon Strip Marquee',
    category: 'party',
    family: 'party',
    badge: '🎰',
    desc: 'Multi-colored blinking neon signage tube flashing in hyper-speed sync.',
    tag: 'VEGAS NEON',
    col: '#ec4899'
  },
  {
    id: 'party_co2_cryo_cannon',
    name: '💨 Festival CO2 Cryo Blast',
    category: 'party',
    family: 'party',
    badge: '💨',
    desc: 'High-pressure white cold fog jets erupting upward on massive bass drop.',
    tag: 'CRYO CANNON',
    col: '#38bdf8'
  },
  {
    id: 'party_prism_confetti_drop',
    name: '🎊 Holographic Laser Confetti',
    category: 'party',
    family: 'party',
    badge: '🎊',
    desc: 'Thousands of reflective metallic foil flakes catching multi-colored lasers.',
    tag: 'CONFETTI DROP',
    col: '#a855f7'
  },
  {
    id: 'party_rave_glowsticks',
    name: '🪄 Dual Neon Glowstick Trails',
    category: 'party',
    family: 'party',
    badge: '🪄',
    desc: 'Neon green and electric pink trails tracing hypnotic orbital figure-8 patterns.',
    tag: 'GLOWSTICKS',
    col: '#22c55e'
  },
  {
    id: 'party_flame_thrower_burst',
    name: '🔥 Stage Pyro Flame Cannon',
    category: 'party',
    family: 'party',
    badge: '🔥',
    desc: 'Controlled concert flame bursts shooting skyward on 128 BPM build-up.',
    tag: 'STAGE PYRO',
    col: '#f97316'
  },

  // ============================================================================
  // 🎸 ACOUSTIC / INDIE (18 Curated Unique FX)
  // ============================================================================
  {
    id: 'acoustic_auto',
    name: '🎲 Auto Acoustic Reactor (Random Shuffle)',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎲',
    desc: 'Automatic selection: Acoustic guitar ke liye organic sine ribbon aur campfire ember auto-match honge!',
    tag: 'AUTO DEFAULT',
    col: '#d97706'
  },
  {
    id: 'oscilloscope_ribbon',
    name: '🌊 Analog Sine Oscilloscope Ribbon',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌊',
    desc: 'Smooth flowing analog sine wave ribbons curving organically around the center emblem.',
    tag: 'OSCILLOSCOPE',
    col: '#38bdf8'
  },
  {
    id: 'acoustic_guitar_string',
    name: '🎸 Six-String Acoustic Frequency Wave',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎸',
    desc: 'Parallel vibrating golden guitar string lines displaying authentic plucked string harmonics.',
    tag: 'GUITAR STRINGS',
    col: '#f59e0b'
  },
  {
    id: 'acoustic_campfire_ember',
    name: '🔥 Campfire Golden Ember Sparkles',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🔥',
    desc: 'Warm glowing campfire embers drifting upward softly into a clear wilderness night sky.',
    tag: 'CAMPFIRE',
    col: '#ea580c'
  },
  {
    id: 'acoustic_morning_dew',
    name: '🍃 Morning Dewdrop Circular Ripple',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🍃',
    desc: 'Pristine forest water ripples reflecting emerald green leaves on delicate acoustic guitar plucks.',
    tag: 'DEWDROP',
    col: '#10b981'
  },
  {
    id: 'acoustic_wood_grain',
    name: '🪵 Organic Wooden Tone Ring',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪵',
    desc: 'Concentric tree ring acoustic cross-section vibrating with warm natural mahogany resonance.',
    tag: 'WOOD GRAIN',
    col: '#92400e'
  },
  {
    id: 'acoustic_indie_horizon',
    name: '🌅 Indie Folk Sunset Horizon',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌅',
    desc: 'Golden indie sunset mountain ridge with serene harmonic waveforms mirroring along the base.',
    tag: 'INDIE HORIZON',
    col: '#f59e0b'
  },
  {
    id: 'acoustic_misty_road',
    name: '🌲 Misty Forest Road Atmospheric Echo',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌲',
    desc: 'Gentle pines and pine needles swaying in misty mountain wind with tranquil audio response.',
    tag: 'MISTY FOREST',
    col: '#047857'
  },
  {
    id: 'acoustic_coffee_house',
    name: '☕ Coffee House Warm Resonance Ring',
    category: 'acoustic',
    family: 'acoustic',
    badge: '☕',
    desc: 'Intimate unplugged acoustic warmth with subtle brassy rings and rich wooden undertones.',
    tag: 'COFFEE HOUSE',
    col: '#b45309'
  },
  {
    id: 'acoustic_mountain_wind',
    name: '💨 Mountain Breeze Sine Oscillator',
    category: 'acoustic',
    family: 'acoustic',
    badge: '💨',
    desc: 'Whispering mountain winds tracing fluid, continuous undulating sine ribbons on vocal chords.',
    tag: 'MOUNTAIN BREEZE',
    col: '#0284c7'
  },
  {
    id: 'acoustic_gentle_tide',
    name: '🏖️ Gentle Shoreline Tide Waveform',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🏖️',
    desc: 'Rhythmic ocean foam washing gently onto golden sand in sync with acoustic strumming.',
    tag: 'SHORELINE',
    col: '#06b6d4'
  },
  {
    id: 'acoustic_sunbeam_glow',
    name: '🌤️ Golden Sunbeam Rays Halo',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌤️',
    desc: 'Peaceful sun rays breaking through morning clouds with soft, heartwarming illumination.',
    tag: 'SUNBEAM',
    col: '#facc15'
  },
  {
    id: 'acoustic_wooden_cajon',
    name: '🥁 Acoustic Wooden Cajon Beat',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🥁',
    desc: 'Resonant warm wooden hollow chamber resonance with organic acoustic thump.',
    tag: 'CAJON PULSE',
    col: '#b45309'
  },
  {
    id: 'acoustic_harmonica_breeze',
    name: '🌬️ Appalachian Harmonica Sine',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🌬️',
    desc: 'Crisp rustic blues harmonica reed vibration shimmering like golden prairie grass.',
    tag: 'HARMONICA',
    col: '#d97706'
  },
  {
    id: 'acoustic_violin_bow',
    name: '🎻 Cello & Violin Bow Resonance',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎻',
    desc: 'Rich horsehair bow friction creating rich velvet string overtones.',
    tag: 'CELLO BOW',
    col: '#92400e'
  },
  {
    id: 'acoustic_fingerstyle_chords',
    name: '🎶 Fingerstyle Nylon Resonance',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🎶',
    desc: 'Delicate classical guitar pluck ripples spreading across still mountain lake.',
    tag: 'FINGERSTYLE',
    col: '#ea580c'
  },
  {
    id: 'acoustic_driftwood_bonfire',
    name: '🪵 Ocean Beach Driftwood Bonfire',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🪵',
    desc: 'Warm coastal driftwood fire with salt-air sparks dancing upward.',
    tag: 'DRIFTWOOD',
    col: '#f59e0b'
  },
  {
    id: 'acoustic_autumn_stream',
    name: '🍂 Crisp Mountain Brook Ripple',
    category: 'acoustic',
    family: 'acoustic',
    badge: '🍂',
    desc: 'Clear mountain stream water flowing over smooth river stones on acoustic picking.',
    tag: 'BROOK STREAM',
    col: '#10b981'
  },

  // ============================================================================
  // 🔥 PHONK / FUNK / DRIFT (24 Curated Unique FX)
  // ============================================================================
  {
    id: 'phonk_auto',
    name: '🎲 Auto Phonk Reactor (Random Shuffle)',
    category: 'phonk',
    family: 'trap_nation',
    badge: '🎲',
    desc: 'Automatic selection: Phonk / Funk gaane ke liye Trap Nation, Tokyo Drift aur 808 reactors auto-match honge!',
    tag: 'AUTO DEFAULT',
    col: '#00f2fe'
  },
  {
    id: 'trap_nation_trilobe',
    name: '👑 Trap Nation Tri-Lobe Core',
    category: 'phonk',
    family: 'trap_nation',
    badge: '👑',
    desc: 'Center Circle Logo + 3-Lobe Audio Bulges + Dotted Equalizer Perimeter + Neon Halo (Flagship Style).',
    tag: 'TRAP NATION',
    col: '#a855f7'
  },
  {
    id: 'reactor_studio',
    name: '☢️ Extreme Reactor Studio',
    category: 'phonk',
    family: 'reactor',
    badge: '☢️',
    desc: 'Center Circle Logo + 360° Radial Frequency Bars + 808 Lightning & Shockwaves + Oscilloscope.',
    tag: 'PRO STUDIO',
    col: '#f97316'
  },
  {
    id: 'primary',
    name: '🌟 Classic Tokyo Drift Shake & 808 Zoom',
    category: 'phonk',
    family: 'all',
    badge: '🌟',
    desc: 'Original Tokyo drift camera vibration, 808 zoom pump & RGB chromatic flash (Zero extra shapes).',
    tag: 'CLASSIC DRIFT',
    col: '#00f2fe'
  },
  {
    id: 'tachometer_jdm',
    name: '🏎️ JDM Drift Tachometer & 808 Boost',
    category: 'phonk',
    family: 'tachometer',
    badge: '🏎️',
    desc: 'Dual RPM meter tachometer arches + boost gauge needles flashing on 808 sub-bass drops.',
    tag: 'JDM BOOST',
    col: '#ef4444'
  },
  {
    id: 'monstercat_radial',
    name: '⭕ Monstercat 360° Circular Ring',
    category: 'phonk',
    family: 'monstercat',
    badge: '⭕',
    desc: 'Center Circle Logo + Dense 360-degree frequency bars vibrating outward with sub-bass drops.',
    tag: '360 RING',
    col: '#f43f5e'
  },
  {
    id: 'cyber_hexagon',
    name: '🔷 Cyber Hexagon Core',
    category: 'phonk',
    family: 'hexagon',
    badge: '🔷',
    desc: 'Center Circle Logo + Dual rotating honeycomb hex shields + techno brackets expanding on drops.',
    tag: 'HEX CORE',
    col: '#0ea5e9'
  },
  {
    id: 'diamond_prism',
    name: '💠 Diamond Core Bass Prism',
    category: 'phonk',
    family: 'diamond',
    badge: '💠',
    desc: 'Center Circle Logo + 45-degree rotating diamond frame + corner telemetry spikes & shockwave rings.',
    tag: 'DIAMOND',
    col: '#06b6d4'
  },
  {
    id: 'biohazard_core',
    name: '🛡️ Biohazard Radioactive Core',
    category: 'phonk',
    family: 'biohazard',
    badge: '🛡️',
    desc: 'Center Circle Logo + Triple biohazard arc blades rotating with radioactive neon green aura.',
    tag: 'BIOHAZARD',
    col: '#22c55e'
  },
  {
    id: 'plasma_lightning',
    name: '⚡ Electric Plasma Arc Reactor',
    category: 'phonk',
    family: 'plasma',
    badge: '⚡',
    desc: 'Center Circle Logo + High-voltage plasma lightning bolts jumping between circular orbital nodes.',
    tag: 'PLASMA',
    col: '#a855f7'
  },
  {
    id: 'grid_3d_synthwave',
    name: '🌐 3D Synthwave Horizon & Sun',
    category: 'phonk',
    family: 'grid_3d',
    badge: '🌐',
    desc: 'Center Circle Logo + Perspective wireframe neon floor grid vibrating to 808 bass + horizon sun.',
    tag: '3D GRID',
    col: '#ec4899'
  },
  {
    id: 'tunnel_warp',
    name: '🌀 Hyperspace Polygonal Tunnel',
    category: 'phonk',
    family: 'tunnel',
    badge: '🌀',
    desc: 'Center Circle Logo + Multi-layered octagonal warp tunnel rings collapsing and expanding on drops.',
    tag: 'WARP TUNNEL',
    col: '#8b5cf6'
  },
  {
    id: 'drift_hud_telemetry',
    name: '💨 Tokyo Drift HUD Telemetry',
    category: 'phonk',
    family: 'drift_hud',
    badge: '💨',
    desc: 'Japanese Kanji glow brackets + corner tactical telemetry + manga radial speed lines.',
    tag: 'TOKYO HUD',
    col: '#10b981'
  },
  {
    id: 'equalizer_wave',
    name: '📊 Dual-Horizon Equalizer Bars',
    category: 'phonk',
    family: 'equalizer',
    badge: '📊',
    desc: 'Mirrored top and bottom audio equalizer bars reflecting like city lights on wet asphalt.',
    tag: 'EQUALIZER',
    col: '#00f2fe'
  },
  {
    id: 'starfield_warp',
    name: '🚀 Light Speed Starfield Accelerator',
    category: 'phonk',
    family: 'starfield',
    badge: '🚀',
    desc: 'Center Circle Logo + 3D starfield streaks accelerating into hyperspace on 808 bass drops.',
    tag: 'STARFIELD',
    col: '#eab308'
  },
  {
    id: 'phonk_redline_overdrive',
    name: '🚨 JDM Redline Overdrive HUD Ring',
    category: 'phonk',
    family: 'tachometer',
    badge: '🚨',
    desc: 'Twin neon redline tachometer brackets flashing warning flares on heavy 808 sub-bass drops.',
    tag: 'REDLINE',
    col: '#ef4444'
  },
  {
    id: 'phonk_kanji_neon',
    name: '🈲 Tokyo Kanji Drift Cyber Halo',
    category: 'phonk',
    family: 'drift_hud',
    badge: '🈲',
    desc: 'Glowing Japanese kanji symbols and speed streaks flashing around the center avatar on drift turns.',
    tag: 'KANJI',
    col: '#00f2fe'
  },
  {
    id: 'phonk_night_highway',
    name: '🛣️ Shuto Expressway Light Streaks',
    category: 'phonk',
    family: 'grid_3d',
    badge: '🛣️',
    desc: 'Long-exposure Tokyo expressway tail-light speed streaks accelerating into distance.',
    tag: 'HIGHWAY',
    col: '#f43f5e'
  },
  {
    id: 'phonk_wangan_midnight',
    name: '🏎️ Wangan Midnight 300km/h Blur',
    category: 'phonk',
    family: 'drift_hud',
    badge: '🏎️',
    desc: 'Japanese highway tunnel fluorescent ceiling lights stretching into continuous lines.',
    tag: 'WANGAN 300',
    col: '#ef4444'
  },
  {
    id: 'phonk_turbo_blowoff',
    name: '💨 Twin-Turbo Anti-Lag Backfire',
    category: 'phonk',
    family: 'tachometer',
    badge: '💨',
    desc: 'Exhaust flame bursts and boost spikes reacting to heavy 808 distortion.',
    tag: 'TURBO BLOWOFF',
    col: '#f97316'
  },
  {
    id: 'phonk_akira_slide',
    name: '🏍️ Neo-Tokyo Cyber Slide',
    category: 'phonk',
    family: 'grid_3d',
    badge: '🏍️',
    desc: 'Iconic red motorcycle drift slide with electric tire sparks and neon brake trails.',
    tag: 'AKIRA SLIDE',
    col: '#dc2626'
  },
  {
    id: 'phonk_ghost_drift',
    name: '👻 Shibuya Ghost Drift Fog',
    category: 'phonk',
    family: 'drift_hud',
    badge: '👻',
    desc: 'Dense tire smoke illuminated by violet street lamps on aggressive cornering.',
    tag: 'GHOST DRIFT',
    col: '#8b5cf6'
  },
  {
    id: 'phonk_tach_shift_light',
    name: '⚡ Sequential Shift Light Flasher',
    category: 'phonk',
    family: 'tachometer',
    badge: '⚡',
    desc: 'Formula drift tachometer LED ladder flashing amber-to-red at 9000 RPM.',
    tag: 'SHIFT LIGHT',
    col: '#eab308'
  },
  {
    id: 'phonk_vhs_cyber_kanji',
    name: '🈲 90s JDM Drift Tape Scanlines',
    category: 'phonk',
    family: 'tunnel',
    badge: '🈲',
    desc: 'Retro VHS tracking distortion lines with neon Japanese car tuning kanji stamps.',
    tag: 'JDM VHS',
    col: '#06b6d4'
  }
];
