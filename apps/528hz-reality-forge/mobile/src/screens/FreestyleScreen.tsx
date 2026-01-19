import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

// TODO: Implement full 7-phase builder
// This is a placeholder - copy logic from web version

export default function FreestyleScreen() {
  return (
    <ScrollView style={styles.container}>
      <View style={styles.placeholder}>
        <Text style={styles.icon}>✨</Text>
        <Text style={styles.title}>Freestyle Builder</Text>
        <Text style={styles.desc}>
          Create custom breath patterns with up to 7 phases.
          {'\n\n'}
          Implementation needed: Copy 7-phase builder logic from web version.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  placeholder: {
    backgroundColor: '#141418',
    borderRadius: 20,
    padding: 40,
    alignItems: 'center',
    marginTop: 50,
  },
  icon: {
    fontSize: 48,
    marginBottom: 20,
  },
  title: {
    fontSize: 20,
    color: '#FFD700',
    fontWeight: '600',
    marginBottom: 15,
  },
  desc: {
    fontSize: 14,
    color: 'rgba(255, 255, 255, 0.6)',
    textAlign: 'center',
    lineHeight: 22,
  },
});
