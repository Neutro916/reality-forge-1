import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Switch } from 'react-native';
import { useAppStore } from '../stores/appStore';

const NEURO_SKILLS = [
  {
    id: 'nkt',
    name: 'NKT',
    fullName: 'Neural Kinetic Therapy',
    icon: '🧬',
    desc: 'Manual counting during breathwork builds dedicated neural circuits.',
    timeline: ['90 days → Foundation', '4 months → Habit', '10 years → Mastery'],
  },
  {
    id: 'nlp',
    name: 'NLP',
    fullName: 'Neuro-Linguistic Programming',
    icon: '💬',
    desc: 'Daily affirmations and breath anchoring install new belief patterns.',
    timeline: ['14 days → Habit', '90 days → Identity'],
  },
  {
    id: 'bci',
    name: 'BCI',
    fullName: 'Brain-Computer Interface Training',
    icon: '🔌',
    desc: 'Breath control trains your brain to produce consistent, readable signals.',
    timeline: ['60 days → Basic control', '6 months → Bidirectional'],
  },
  {
    id: 'echo',
    name: 'Echolocation',
    fullName: 'Spatial Awareness Enhancement',
    icon: '👁️',
    desc: 'Extended focus during breath holds heightens sensory awareness.',
    timeline: ['4 months → Awareness', '10 years → Mastery'],
  },
];

export default function MindScreen() {
  const { settings, toggleSetting } = useAppStore();

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Intro */}
      <View style={styles.introCard}>
        <Text style={styles.introTitle}>THE HIDDEN SKILLS</Text>
        <Text style={styles.introText}>
          As you practice daily, you're not just breathing—you're developing advanced
          neural abilities. These skills are building silently in the background.
        </Text>
      </View>

      {/* Neuro Skills */}
      {NEURO_SKILLS.map((skill) => (
        <View key={skill.id} style={styles.skillCard}>
          <View style={styles.skillHeader}>
            <Text style={styles.skillIcon}>{skill.icon}</Text>
            <View style={styles.skillTitles}>
              <Text style={styles.skillName}>{skill.name}</Text>
              <Text style={styles.skillFullName}>{skill.fullName}</Text>
            </View>
          </View>
          <Text style={styles.skillDesc}>{skill.desc}</Text>
          <View style={styles.timeline}>
            {skill.timeline.map((t, i) => (
              <View key={i} style={styles.timelineBadge}>
                <Text style={styles.timelineText}>{t}</Text>
              </View>
            ))}
          </View>
        </View>
      ))}

      {/* Settings */}
      <View style={styles.settingsSection}>
        <Text style={styles.sectionTitle}>SETTINGS</Text>

        <View style={styles.settingGroup}>
          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>528 Hz Audio</Text>
            <Switch
              value={settings.audio}
              onValueChange={() => toggleSetting('audio')}
              trackColor={{ false: 'rgba(255,255,255,0.2)', true: '#FFD700' }}
              thumbColor="#fff"
            />
          </View>

          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Vibration</Text>
            <Switch
              value={settings.vib}
              onValueChange={() => toggleSetting('vib')}
              trackColor={{ false: 'rgba(255,255,255,0.2)', true: '#FFD700' }}
              thumbColor="#fff"
            />
          </View>

          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Sacred Geometry</Text>
            <Switch
              value={settings.geo}
              onValueChange={() => toggleSetting('geo')}
              trackColor={{ false: 'rgba(255,255,255,0.2)', true: '#FFD700' }}
              thumbColor="#fff"
            />
          </View>

          <View style={styles.settingItem}>
            <Text style={styles.settingLabel}>Wave Counter</Text>
            <Switch
              value={settings.wave}
              onValueChange={() => toggleSetting('wave')}
              trackColor={{ false: 'rgba(255,255,255,0.2)', true: '#FFD700' }}
              thumbColor="#fff"
            />
          </View>
        </View>
      </View>

      <View style={{ height: 100 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  introCard: {
    backgroundColor: 'rgba(168, 85, 247, 0.15)',
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: 'rgba(168, 85, 247, 0.3)',
  },
  introTitle: {
    fontSize: 14,
    color: '#a855f7',
    fontWeight: '600',
    marginBottom: 10,
  },
  introText: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    lineHeight: 22,
  },
  skillCard: {
    backgroundColor: '#141418',
    borderRadius: 20,
    padding: 20,
    marginBottom: 15,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
  },
  skillHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  skillIcon: {
    fontSize: 32,
    marginRight: 15,
  },
  skillTitles: {
    flex: 1,
  },
  skillName: {
    fontSize: 16,
    color: '#fff',
    fontWeight: '600',
    marginBottom: 2,
  },
  skillFullName: {
    fontSize: 11,
    color: 'rgba(255, 255, 255, 0.5)',
  },
  skillDesc: {
    fontSize: 13,
    color: 'rgba(255, 255, 255, 0.6)',
    lineHeight: 20,
    marginBottom: 12,
  },
  timeline: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  timelineBadge: {
    backgroundColor: 'rgba(0, 212, 170, 0.1)',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 15,
  },
  timelineText: {
    fontSize: 10,
    color: '#00d4aa',
  },
  settingsSection: {
    marginTop: 20,
  },
  sectionTitle: {
    fontSize: 12,
    color: '#FFD700',
    fontWeight: '600',
    letterSpacing: 1,
    marginBottom: 15,
  },
  settingGroup: {
    backgroundColor: '#141418',
    borderRadius: 15,
    padding: 5,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.05)',
  },
  settingLabel: {
    fontSize: 14,
    color: '#fff',
  },
});
