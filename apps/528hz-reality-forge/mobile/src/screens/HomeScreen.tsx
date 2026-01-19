import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useAppStore } from '../stores/appStore';

const QUOTES = [
  "The breath is the bridge between the conscious and unconscious mind.",
  "Every breath you take is a chance to rewire your neural pathways.",
  "528 Hz: The frequency of transformation and DNA repair.",
  "Your brain changes shape based on what you repeatedly do.",
];

const SKILLS = [
  { id: 'nkt', name: 'NKT', fullName: 'Neural Kinetic', icon: '🧬', progress: 5 },
  { id: 'nlp', name: 'NLP', fullName: 'Neuro-Linguistic', icon: '💬', progress: 7 },
  { id: 'bci', name: 'BCI', fullName: 'Brain-Computer', icon: '🔌', progress: 3 },
  { id: 'echo', name: 'ECHO', fullName: 'Spatial Sense', icon: '👁️', progress: 2 },
];

export default function HomeScreen() {
  const { day, streak, xp, tasks, toggleTask } = useAppStore();

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 17) return 'Good Afternoon';
    return 'Good Evening';
  };

  const dailyQuote = QUOTES[day % QUOTES.length];

  const TASKS = [
    { name: 'Morning Breathwork', duration: '5-10 minutes', xp: 50 },
    { name: "Read Today's Lesson", duration: '3 minutes', xp: 30 },
    { name: 'Evening Reflection', duration: '2 minutes', xp: 20 },
  ];

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* Greeting Card */}
      <View style={styles.greetingCard}>
        <Text style={styles.greetingTime}>{getGreeting()}</Text>
        <Text style={styles.greetingMessage}>Your mind is shaping reality today.</Text>
        <View style={styles.quoteBox}>
          <Text style={styles.quote}>"{dailyQuote}"</Text>
        </View>
      </View>

      {/* Today's Journey */}
      <View style={styles.journeyCard}>
        <View style={styles.journeyHeader}>
          <Text style={styles.journeyTitle}>TODAY'S PATH</Text>
          <Text style={styles.streakText}>🔥 {streak} day streak</Text>
        </View>

        {TASKS.map((task, index) => (
          <TouchableOpacity
            key={index}
            style={[styles.taskItem, tasks[index] && styles.taskCompleted]}
            onPress={() => toggleTask(index)}
          >
            <View style={[styles.taskCheck, tasks[index] && styles.taskCheckCompleted]}>
              {tasks[index] && <Text style={styles.checkmark}>✓</Text>}
            </View>
            <View style={styles.taskInfo}>
              <Text style={styles.taskName}>{task.name}</Text>
              <Text style={styles.taskDuration}>{task.duration}</Text>
            </View>
            <View style={styles.taskXp}>
              <Text style={styles.taskXpText}>+{task.xp} XP</Text>
            </View>
          </TouchableOpacity>
        ))}
      </View>

      {/* Skills Section */}
      <View style={styles.skillsSection}>
        <Text style={styles.sectionTitle}>DEVELOPING ABILITIES</Text>
        <View style={styles.skillsGrid}>
          {SKILLS.map((skill) => (
            <View key={skill.id} style={styles.skillCard}>
              <Text style={styles.skillIcon}>{skill.icon}</Text>
              <Text style={styles.skillName}>{skill.name}</Text>
              <Text style={styles.skillFullName}>{skill.fullName}</Text>
              <View style={styles.skillProgress}>
                <View style={[styles.skillProgressFill, { width: `${skill.progress}%` }]} />
              </View>
            </View>
          ))}
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
  greetingCard: {
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
    borderRadius: 20,
    padding: 25,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 215, 0, 0.2)',
  },
  greetingTime: {
    fontSize: 12,
    color: '#FFD700',
    fontWeight: '600',
    marginBottom: 5,
  },
  greetingMessage: {
    fontSize: 22,
    color: '#fff',
    fontWeight: '300',
    marginBottom: 15,
  },
  quoteBox: {
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    borderRadius: 10,
    padding: 15,
    borderLeftWidth: 3,
    borderLeftColor: '#FFD700',
  },
  quote: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    fontStyle: 'italic',
    lineHeight: 22,
  },
  journeyCard: {
    backgroundColor: '#141418',
    borderRadius: 20,
    padding: 20,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
  },
  journeyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  journeyTitle: {
    fontSize: 12,
    color: '#FFD700',
    fontWeight: '600',
    letterSpacing: 1,
  },
  streakText: {
    fontSize: 12,
    color: '#00d4aa',
  },
  taskItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    borderRadius: 12,
    marginBottom: 10,
  },
  taskCompleted: {
    opacity: 0.6,
  },
  taskCheck: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#B8860B',
    marginRight: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  taskCheckCompleted: {
    backgroundColor: '#FFD700',
    borderColor: '#FFD700',
  },
  checkmark: {
    color: '#070709',
    fontSize: 14,
    fontWeight: 'bold',
  },
  taskInfo: {
    flex: 1,
  },
  taskName: {
    fontSize: 14,
    color: '#fff',
    fontWeight: '500',
    marginBottom: 2,
  },
  taskDuration: {
    fontSize: 11,
    color: 'rgba(255, 255, 255, 0.5)',
  },
  taskXp: {
    backgroundColor: 'rgba(0, 212, 170, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 10,
  },
  taskXpText: {
    fontSize: 11,
    color: '#00d4aa',
  },
  skillsSection: {
    marginTop: 5,
  },
  sectionTitle: {
    fontSize: 12,
    color: '#FFD700',
    fontWeight: '600',
    letterSpacing: 1,
    marginBottom: 15,
  },
  skillsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -5,
  },
  skillCard: {
    width: '48%',
    backgroundColor: '#141418',
    borderRadius: 15,
    padding: 15,
    margin: '1%',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.05)',
  },
  skillIcon: {
    fontSize: 24,
    marginBottom: 10,
  },
  skillName: {
    fontSize: 14,
    color: '#fff',
    fontWeight: '600',
    marginBottom: 3,
  },
  skillFullName: {
    fontSize: 10,
    color: 'rgba(255, 255, 255, 0.5)',
    marginBottom: 10,
  },
  skillProgress: {
    height: 3,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    borderRadius: 2,
    overflow: 'hidden',
  },
  skillProgressFill: {
    height: '100%',
    backgroundColor: '#FFD700',
    borderRadius: 2,
  },
});
