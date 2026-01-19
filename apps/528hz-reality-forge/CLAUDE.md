# 528 Hz REALITY FORGE - CLAUDE CODE DOCUMENTATION

## OVERVIEW

This is **App 1 of 3** in the Reality Forge consciousness technology system.
- **App 1**: 528 Hz (GOLD theme) - Transformation/DNA - THIS APP
- **App 2**: 373 Hz (CYAN theme) - Coming
- **App 3**: 639 Hz (PINK theme) - Coming

This is the **FOUNDATION APP** - the one users master BEFORE or just after kundalini awakening.
It's meant to be simple, self-motivating, and reusable for daily practice.

## DESIGN PHILOSOPHY

- **Self-motivating**: Story-driven progression, daily quotes, XP system
- **Simple**: Easy to understand, no barrier to entry
- **Reusable**: Daily practice tool, not one-time use
- **Modern**: Clean tech aesthetic with sacred geometry
- **Not meditation**: This is BREATHWORK training for results

## FEATURES

### 1. TODAY TAB (Home)
- Daily greeting with time-aware message
- Rotating motivational quotes
- Three daily tasks with XP rewards
- Skill progress cards (NKT, NLP, BCI, Echo)
- Day streak counter

### 2. BREATHE TAB
- 8 preset breath patterns
- Sacred geometry (Flower of Life)
- Live wave counter (Hz × seconds)
- Session stats (cycles, time, total waves)
- 528 Hz audio tone
- Vibration feedback per phase

### 3. FREESTYLE TAB (7-Phase Builder)
- Custom pattern creator with up to 7 phases
- Each phase: type (inhale/hold/exhale/rest/skip) + duration
- Live preview showing timing string
- Save patterns for reuse
- Quick templates (Relaxation, Energy, Focus, Sleep)
- Use saved patterns directly in practice

### 4. NOTES TAB (Daily Protocol Journal)
- Document daily practice
- Track: pattern used, duration, reflection, energy level
- Build personal protocol history
- See patterns in what works best

### 5. MIND TAB
- 6 Neuro Skills explained:
  - **NKT** - Neural Kinetic Therapy (counting builds circuits)
  - **NLP** - Neuro-Linguistic Programming (anchoring states)
  - **BCI** - Brain-Computer Interface (signal training)
  - **Echolocation** - Spatial awareness enhancement
  - **Muscle Memory** - Procedural encoding
  - **Neuroplasticity** - Brain structure modification
- Settings for audio, vibration, geometry, wave counter

## DATA STORAGE

All data persisted in localStorage:

```javascript
// Main state
'realityforge528': {
  day: number,
  streak: number,
  xp: number,
  tasks: [boolean, boolean, boolean],
  settings: { audio, vib, geo, wave }
}

// Custom patterns
'rf528_custom_patterns': [
  {
    id: number,
    name: string,
    timing: string,  // e.g., "4-4-4-4"
    phases: [{ type, time, name }],
    createdAt: ISO string
  }
]

// Journal notes
'rf528_notes': [
  {
    id: number,
    day: number,
    date: ISO string,
    pattern: string,
    duration: string,
    reflection: string,
    energy: 1|2|3
  }
]
```

## BREATH PATTERNS (Preset)

| Name | Timing | Purpose |
|------|--------|---------|
| Box Breathing | 4-4-4-4 | Foundation for focus |
| Trinity | 3-3-3 | Body-Mind-Soul alignment |
| Tesla | 3-6-9 | Universal frequency |
| 4-7-8 Calm | 4-7-8 | Nervous system reset |
| Coherence | 5-0-5 | Heart-brain sync |
| Power Breath | 2-0-2 | Energy activation |
| Kundalini | 4-16-8 | Deep awakening |
| Golden Ratio | 5-8-13 | Fibonacci flow |

## 7-PHASE FREESTYLE BUILDER

Users can create custom patterns with up to 7 phases:
- Each phase has a TYPE: inhale, hold, exhale, rest, or skip
- Each phase has a TIME: 0-60 seconds
- Phases set to "skip" or 0 seconds are ignored
- Preview shows timing string and total cycle time

Example complex pattern:
```
Phase 1: Inhale 4s
Phase 2: Hold 4s
Phase 3: Exhale 4s
Phase 4: Hold 2s
Phase 5: Inhale 4s
Phase 6: Hold 8s
Phase 7: Exhale 8s
= "4-4-4-2-4-8-8" (34 seconds per cycle)
```

## VIBRATION PATTERNS

```
INHALE  → navigator.vibrate(100)         // 1 short pulse
HOLD    → navigator.vibrate([100,100,100]) // 2 pulses
EXHALE  → navigator.vibrate(2000)         // 2 sec continuous
REST    → navigator.vibrate([100,100,100]) // 2 pulses
```

## 528 Hz AUDIO

```javascript
const audioCtx = new AudioContext();
const oscillator = audioCtx.createOscillator();
oscillator.type = 'sine';
oscillator.frequency.setValueAtTime(528, audioCtx.currentTime);
// Gain: 0.1 (quiet background)
```

## COLOR PALETTE

| Name | Hex | Usage |
|------|-----|-------|
| Gold | #FFD700 | Primary accent, 528 Hz theme |
| Gold Light | #FFF4B8 | Highlights |
| Gold Dim | #B8860B | Secondary, borders |
| Dark | #0d0d0f | Surface background |
| Darker | #070709 | Main background |
| Surface | #141418 | Cards |
| Accent | #00d4aa | Success, positive |
| Purple | #a855f7 | Neuro section |
| Blue | #3b82f6 | Info accents |

## FONTS

- **Orbitron**: Headings, numbers, labels (tech/futuristic)
- **Exo 2**: Body text (clean, modern)

## CHAPTERS (90-Day Journey)

| # | Name | Days | Theme |
|---|------|------|-------|
| 1 | Awakening | 1-14 | Discover breath power |
| 2 | Foundation | 15-30 | Build consistency |
| 3 | Deepening | 31-45 | Inner exploration |
| 4 | Expansion | 46-60 | Expand awareness |
| 5 | Integration | 61-75 | Connect mind-body |
| 6 | Mastery | 76-90 | Embody transformation |

## DEVELOPMENT SHORTCUTS

- Press `D` key to advance day (testing)
- All state persists in localStorage
- Open in browser, use DevTools mobile emulation

## REACT NATIVE CONVERSION

Key dependencies for native:
```
expo-av          // Audio
expo-haptics     // Vibration
@react-native-firebase/database  // Group sync
zustand          // State management
react-native-svg // Sacred geometry
@react-native-async-storage/async-storage
```

## FILE STRUCTURE

```
apps/528hz-reality-forge/
├── index.html      # Complete standalone app
├── CLAUDE.md       # This documentation
└── (future)
    ├── src/
    │   ├── App.tsx
    │   ├── components/
    │   ├── screens/
    │   ├── stores/
    │   ├── hooks/
    │   └── services/
    └── assets/
```

## KEY NOTES FOR CLAUDE CODE

1. This is a BREATHWORK app, not meditation - focus on results, training, discipline
2. The app is meant to be the foundation - simple enough for anyone
3. All features should remain accessible without login/signup
4. The 7-phase freestyle builder is a key differentiator
5. Daily notes/journal helps users track what works for them
6. The neuro skills (NKT, NLP, BCI, etc.) are REAL abilities being developed
7. 528 Hz is the "miracle frequency" - DNA repair, transformation
8. Wave math (Hz × seconds) should always be visible
9. Keep the UI clean, modern, and motivating
10. This is App 1 - gold theme, 528 Hz. Apps 2 and 3 will follow similar structure
