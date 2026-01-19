import { create } from 'zustand';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Breath Pattern Type
export interface BreathPattern {
  name: string;
  timing: string;
  inhale: number;
  hold: number;
  exhale: number;
  rest: number;
  desc: string;
  isCustom?: boolean;
  phases?: Array<{ type: string; time: number; name: string }>;
}

// Note Type
export interface Note {
  id: number;
  day: number;
  date: string;
  pattern: string;
  duration: string;
  reflection: string;
  energy: number;
}

// Custom Pattern Type
export interface CustomPattern {
  id: number;
  name: string;
  timing: string;
  phases: Array<{ type: string; time: number; name: string }>;
  createdAt: string;
}

// Settings Type
interface Settings {
  audio: boolean;
  vib: boolean;
  geo: boolean;
  wave: boolean;
}

// Store State
interface AppState {
  // Navigation
  activeTab: string;
  setActiveTab: (tab: string) => void;

  // User Progress
  day: number;
  streak: number;
  xp: number;
  tasks: boolean[];

  // Session
  isRunning: boolean;
  currentPattern: BreathPattern;
  cycles: number;
  totalTime: number;
  totalWaves: number;
  currentPhase: string;
  phaseTime: number;

  // Data
  customPatterns: CustomPattern[];
  notes: Note[];
  settings: Settings;

  // Actions
  loadState: () => Promise<void>;
  saveState: () => Promise<void>;
  toggleTask: (index: number) => void;
  advanceDay: () => void;
  setCurrentPattern: (pattern: BreathPattern) => void;
  startSession: () => void;
  stopSession: () => void;
  updateSession: (cycles: number, time: number, waves: number, phase: string, phaseTime: number) => void;
  saveCustomPattern: (pattern: CustomPattern) => void;
  deleteCustomPattern: (id: number) => void;
  saveNote: (note: Note) => void;
  toggleSetting: (key: keyof Settings) => void;
}

// Default Patterns
export const PATTERNS: BreathPattern[] = [
  { name: "Box Breathing", timing: "4-4-4-4", inhale: 4, hold: 4, exhale: 4, rest: 4, desc: "Foundation for focus" },
  { name: "Trinity", timing: "3-3-3", inhale: 3, hold: 3, exhale: 3, rest: 0, desc: "Body-Mind-Soul alignment" },
  { name: "Tesla", timing: "3-6-9", inhale: 3, hold: 6, exhale: 9, rest: 0, desc: "Universal frequency" },
  { name: "4-7-8 Calm", timing: "4-7-8", inhale: 4, hold: 7, exhale: 8, rest: 0, desc: "Nervous system reset" },
  { name: "Coherence", timing: "5-0-5", inhale: 5, hold: 0, exhale: 5, rest: 0, desc: "Heart-brain sync" },
  { name: "Power Breath", timing: "2-0-2", inhale: 2, hold: 0, exhale: 2, rest: 0, desc: "Energy activation" },
  { name: "Kundalini", timing: "4-16-8", inhale: 4, hold: 16, exhale: 8, rest: 0, desc: "Deep awakening" },
  { name: "Golden Ratio", timing: "5-8-13", inhale: 5, hold: 8, exhale: 13, rest: 0, desc: "Fibonacci flow" },
];

// Create Store
export const useAppStore = create<AppState>((set, get) => ({
  // Initial State
  activeTab: 'home',
  day: 1,
  streak: 1,
  xp: 0,
  tasks: [false, false, false],
  isRunning: false,
  currentPattern: PATTERNS[0],
  cycles: 0,
  totalTime: 0,
  totalWaves: 0,
  currentPhase: 'ready',
  phaseTime: 0,
  customPatterns: [],
  notes: [],
  settings: {
    audio: true,
    vib: true,
    geo: true,
    wave: true,
  },

  // Navigation
  setActiveTab: (tab) => set({ activeTab: tab }),

  // Load from AsyncStorage
  loadState: async () => {
    try {
      const saved = await AsyncStorage.getItem('realityforge528');
      if (saved) {
        const parsed = JSON.parse(saved);
        set({
          day: parsed.day || 1,
          streak: parsed.streak || 1,
          xp: parsed.xp || 0,
          tasks: parsed.tasks || [false, false, false],
          settings: { ...get().settings, ...parsed.settings },
        });
      }

      const patterns = await AsyncStorage.getItem('rf528_custom_patterns');
      if (patterns) {
        set({ customPatterns: JSON.parse(patterns) });
      }

      const notes = await AsyncStorage.getItem('rf528_notes');
      if (notes) {
        set({ notes: JSON.parse(notes) });
      }
    } catch (e) {
      console.error('Failed to load state:', e);
    }
  },

  // Save to AsyncStorage
  saveState: async () => {
    try {
      const { day, streak, xp, tasks, settings, customPatterns, notes } = get();

      await AsyncStorage.setItem('realityforge528', JSON.stringify({
        day, streak, xp, tasks, settings,
      }));

      await AsyncStorage.setItem('rf528_custom_patterns', JSON.stringify(customPatterns));
      await AsyncStorage.setItem('rf528_notes', JSON.stringify(notes));
    } catch (e) {
      console.error('Failed to save state:', e);
    }
  },

  // Tasks
  toggleTask: (index) => {
    const tasks = [...get().tasks];
    tasks[index] = !tasks[index];

    let xp = get().xp;
    if (tasks[index]) {
      xp += [50, 30, 20][index];
    }

    set({ tasks, xp });
    get().saveState();
  },

  advanceDay: () => {
    const { day, streak } = get();
    set({
      day: Math.min(90, day + 1),
      streak: streak + 1,
      tasks: [false, false, false],
    });
    get().saveState();
  },

  // Session
  setCurrentPattern: (pattern) => set({ currentPattern: pattern }),

  startSession: () => set({
    isRunning: true,
    cycles: 0,
    totalTime: 0,
    totalWaves: 0,
    currentPhase: 'ready',
    phaseTime: 0,
  }),

  stopSession: () => set({
    isRunning: false,
    currentPhase: 'ready',
    phaseTime: 0,
  }),

  updateSession: (cycles, time, waves, phase, phaseTime) => set({
    cycles,
    totalTime: time,
    totalWaves: waves,
    currentPhase: phase,
    phaseTime,
  }),

  // Custom Patterns
  saveCustomPattern: (pattern) => {
    const patterns = [...get().customPatterns, pattern];
    set({ customPatterns: patterns });
    get().saveState();
  },

  deleteCustomPattern: (id) => {
    const patterns = get().customPatterns.filter(p => p.id !== id);
    set({ customPatterns: patterns });
    get().saveState();
  },

  // Notes
  saveNote: (note) => {
    const notes = [note, ...get().notes];
    set({ notes });
    get().saveState();
  },

  // Settings
  toggleSetting: (key) => {
    const settings = { ...get().settings };
    settings[key] = !settings[key];
    set({ settings });
    get().saveState();
  },
}));
