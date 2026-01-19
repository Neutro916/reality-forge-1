import React, { useState, useEffect, useRef } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { Audio } from 'expo-av';
import * as Haptics from 'expo-haptics';
import Svg, { Circle } from 'react-native-svg';
import { useAppStore, PATTERNS } from '../stores/appStore';

export default function BreatheScreen() {
  const {
    isRunning, currentPattern, cycles, totalTime, totalWaves,
    currentPhase, phaseTime, settings,
    startSession, stopSession, updateSession, setCurrentPattern
  } = useAppStore();

  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const phaseIndexRef = useRef(0);
  const timeInPhaseRef = useRef(0);
  const cyclesRef = useRef(0);
  const totalTimeRef = useRef(0);
  const totalWavesRef = useRef(0);

  // Start 528 Hz audio
  const startAudio = async () => {
    try {
      // In production, load a 528 Hz tone file
      // For now, we'll skip the actual audio
      console.log('528 Hz audio would play here');
    } catch (e) {
      console.log('Audio error:', e);
    }
  };

  const stopAudio = async () => {
    if (sound) {
      await sound.stopAsync();
      await sound.unloadAsync();
      setSound(null);
    }
  };

  // Vibration patterns
  const triggerVibration = (phase: string) => {
    if (!settings.vib) return;

    switch (phase) {
      case 'inhale':
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
        break;
      case 'hold':
      case 'rest':
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
        break;
      case 'exhale':
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
        break;
    }
  };

  // Build phases from pattern
  const buildPhases = () => {
    const p = currentPattern;
    const phases: Array<{ name: string; duration: number; key: string }> = [];

    if (p.inhale > 0) phases.push({ name: 'INHALE', duration: p.inhale, key: 'inhale' });
    if (p.hold > 0) phases.push({ name: 'HOLD', duration: p.hold, key: 'hold' });
    if (p.exhale > 0) phases.push({ name: 'EXHALE', duration: p.exhale, key: 'exhale' });
    if (p.rest > 0) phases.push({ name: 'REST', duration: p.rest, key: 'rest' });

    return phases;
  };

  // Start breath session
  const handleStart = () => {
    startSession();
    phaseIndexRef.current = 0;
    timeInPhaseRef.current = 0;
    cyclesRef.current = 0;
    totalTimeRef.current = 0;
    totalWavesRef.current = 0;

    if (settings.audio) {
      startAudio();
    }

    const phases = buildPhases();

    intervalRef.current = setInterval(() => {
      const phase = phases[phaseIndexRef.current];
      const remaining = phase.duration - timeInPhaseRef.current;

      updateSession(
        cyclesRef.current,
        totalTimeRef.current,
        totalWavesRef.current,
        phase.key,
        remaining
      );

      if (timeInPhaseRef.current === 0) {
        triggerVibration(phase.key);
      }

      totalWavesRef.current += 528;
      totalTimeRef.current++;
      timeInPhaseRef.current++;

      if (timeInPhaseRef.current >= phase.duration) {
        timeInPhaseRef.current = 0;
        phaseIndexRef.current++;

        if (phaseIndexRef.current >= phases.length) {
          phaseIndexRef.current = 0;
          cyclesRef.current++;
        }
      }
    }, 1000);
  };

  // Stop breath session
  const handleStop = () => {
    stopSession();
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    stopAudio();
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      stopAudio();
    };
  }, []);

  const formatTime = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, '0')}`;
  };

  const formatNumber = (n: number) => {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return n.toString();
  };

  // Get circle scale based on phase
  const getCircleScale = () => {
    switch (currentPhase) {
      case 'inhale': return 1.15;
      case 'exhale': return 0.85;
      default: return 1;
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Sacred Geometry + Breath Circle */}
      <View style={styles.geometryContainer}>
        {settings.geo && (
          <Svg style={styles.flowerSvg} viewBox="0 0 200 200">
            <Circle cx="100" cy="100" r="30" fill="none" stroke="#FFD700" strokeWidth="0.5" opacity={isRunning ? 0.5 : 0.2} />
            <Circle cx="100" cy="70" r="30" fill="none" stroke="#FFD700" strokeWidth="0.5" opacity={isRunning ? 0.5 : 0.2} />
            <Circle cx="126" cy="85" r="30" fill="none" stroke="#FFD700" strokeWidth="0.5" opacity={isRunning ? 0.5 : 0.2} />
            <Circle cx="126" cy="115" r="30" fill="none" stroke="#FFD700" strokeWidth="0.5" opacity={isRunning ? 0.5 : 0.2} />
            <Circle cx="100" cy="130" r="30" fill="none" stroke="#FFD700" strokeWidth="0.5" opacity={isRunning ? 0.5 : 0.2} />
            <Circle cx="74" cy="115" r="30" fill="none" stroke="#FFD700" strokeWidth="0.5" opacity={isRunning ? 0.5 : 0.2} />
            <Circle cx="74" cy="85" r="30" fill="none" stroke="#FFD700" strokeWidth="0.5" opacity={isRunning ? 0.5 : 0.2} />
          </Svg>
        )}

        <View style={[
          styles.breathCircle,
          { transform: [{ scale: getCircleScale() }] }
        ]}>
          <Text style={styles.phaseLabel}>{currentPhase.toUpperCase()}</Text>
          <Text style={styles.phaseCount}>{phaseTime}</Text>
        </View>
      </View>

      {/* Wave Display */}
      {settings.wave && (
        <View style={styles.waveDisplay}>
          <Text style={styles.waveTitle}>WAVE MATHEMATICS</Text>
          <Text style={styles.waveFormula}>
            <Text style={styles.waveHz}>528 Hz</Text> × {totalTime % 60}s = <Text style={styles.waveResult}>{formatNumber(totalWaves)}</Text> waves
          </Text>
        </View>
      )}

      {/* Session Stats */}
      <View style={styles.statsRow}>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{cycles}</Text>
          <Text style={styles.statLabel}>Cycles</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{formatTime(totalTime)}</Text>
          <Text style={styles.statLabel}>Time</Text>
        </View>
        <View style={styles.stat}>
          <Text style={styles.statValue}>{formatNumber(totalWaves)}</Text>
          <Text style={styles.statLabel}>Waves</Text>
        </View>
      </View>

      {/* Control Button */}
      <TouchableOpacity
        style={[styles.button, isRunning && styles.buttonStop]}
        onPress={isRunning ? handleStop : handleStart}
      >
        <Text style={styles.buttonText}>{isRunning ? 'Stop' : 'Begin'}</Text>
      </TouchableOpacity>

      {/* Pattern List */}
      <View style={styles.patternSection}>
        <Text style={styles.sectionTitle}>BREATH PATTERN</Text>
        {PATTERNS.map((pattern, index) => (
          <TouchableOpacity
            key={index}
            style={[
              styles.patternItem,
              currentPattern.name === pattern.name && styles.patternSelected
            ]}
            onPress={() => setCurrentPattern(pattern)}
          >
            <View style={styles.patternInfo}>
              <Text style={styles.patternName}>{pattern.name}</Text>
              <Text style={styles.patternDesc}>{pattern.desc}</Text>
            </View>
            <Text style={styles.patternTiming}>{pattern.timing}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <View style={{ height: 100 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    alignItems: 'center',
    padding: 20,
  },
  geometryContainer: {
    width: 250,
    height: 250,
    alignItems: 'center',
    justifyContent: 'center',
    marginVertical: 20,
  },
  flowerSvg: {
    position: 'absolute',
    width: '100%',
    height: '100%',
  },
  breathCircle: {
    width: 160,
    height: 160,
    borderRadius: 80,
    borderWidth: 2,
    borderColor: '#FFD700',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'rgba(255, 215, 0, 0.05)',
  },
  phaseLabel: {
    fontSize: 14,
    color: '#FFD700',
    fontWeight: '600',
    letterSpacing: 2,
    marginBottom: 5,
  },
  phaseCount: {
    fontSize: 42,
    color: '#fff',
    fontWeight: '700',
  },
  waveDisplay: {
    backgroundColor: '#141418',
    borderRadius: 15,
    padding: 15,
    alignItems: 'center',
    marginVertical: 15,
    borderWidth: 1,
    borderColor: 'rgba(255, 215, 0, 0.1)',
  },
  waveTitle: {
    fontSize: 10,
    color: '#FFD700',
    letterSpacing: 1,
    marginBottom: 5,
  },
  waveFormula: {
    fontSize: 14,
    color: '#fff',
  },
  waveHz: {
    color: '#FFD700',
  },
  waveResult: {
    color: '#00d4aa',
    fontWeight: '700',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 25,
    marginVertical: 20,
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 20,
    color: '#FFD700',
    fontWeight: '700',
  },
  statLabel: {
    fontSize: 10,
    color: 'rgba(255, 255, 255, 0.5)',
    marginTop: 3,
  },
  button: {
    paddingVertical: 15,
    paddingHorizontal: 50,
    backgroundColor: '#FFD700',
    borderRadius: 30,
    marginVertical: 20,
  },
  buttonStop: {
    backgroundColor: '#ff4444',
  },
  buttonText: {
    fontSize: 16,
    color: '#070709',
    fontWeight: '600',
  },
  patternSection: {
    width: '100%',
    marginTop: 20,
  },
  sectionTitle: {
    fontSize: 12,
    color: '#FFD700',
    fontWeight: '600',
    letterSpacing: 1,
    marginBottom: 15,
  },
  patternItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: '#141418',
    borderRadius: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
  },
  patternSelected: {
    borderColor: '#FFD700',
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
  },
  patternInfo: {
    flex: 1,
  },
  patternName: {
    fontSize: 14,
    color: '#fff',
    fontWeight: '600',
    marginBottom: 2,
  },
  patternDesc: {
    fontSize: 11,
    color: 'rgba(255, 255, 255, 0.5)',
  },
  patternTiming: {
    fontSize: 12,
    color: '#FFD700',
  },
});
