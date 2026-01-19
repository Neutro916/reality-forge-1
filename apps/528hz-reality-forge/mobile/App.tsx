import React, { useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View, Text, TouchableOpacity, SafeAreaView } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useAppStore } from './src/stores/appStore';
import HomeScreen from './src/screens/HomeScreen';
import BreatheScreen from './src/screens/BreatheScreen';
import FreestyleScreen from './src/screens/FreestyleScreen';
import NotesScreen from './src/screens/NotesScreen';
import MindScreen from './src/screens/MindScreen';

// Tab icons (using emoji for simplicity - replace with actual icons)
const tabs = [
  { id: 'home', label: 'Today', icon: '🏠' },
  { id: 'breathe', label: 'Breathe', icon: '🌬️' },
  { id: 'freestyle', label: 'Freestyle', icon: '✨' },
  { id: 'notes', label: 'Notes', icon: '📝' },
  { id: 'mind', label: 'Mind', icon: '🧠' },
];

export default function App() {
  const { activeTab, setActiveTab, loadState } = useAppStore();

  useEffect(() => {
    loadState();
  }, []);

  const renderScreen = () => {
    switch (activeTab) {
      case 'home': return <HomeScreen />;
      case 'breathe': return <BreatheScreen />;
      case 'freestyle': return <FreestyleScreen />;
      case 'notes': return <NotesScreen />;
      case 'mind': return <MindScreen />;
      default: return <HomeScreen />;
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar style="light" />

      <LinearGradient
        colors={['#070709', '#0d0d0f', '#070709']}
        style={StyleSheet.absoluteFill}
      />

      <SafeAreaView style={styles.safeArea}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.logo}>
            <Text style={styles.logoGold}>REALITY</Text>
            <Text style={styles.logoWhite}>FORGE</Text>
          </Text>
          <View style={styles.dayBadge}>
            <Text style={styles.dayText}>DAY {useAppStore.getState().day}</Text>
          </View>
        </View>

        {/* Main Content */}
        <View style={styles.content}>
          {renderScreen()}
        </View>

        {/* Tab Navigation */}
        <View style={styles.tabBar}>
          {tabs.map((tab) => (
            <TouchableOpacity
              key={tab.id}
              style={[styles.tab, activeTab === tab.id && styles.tabActive]}
              onPress={() => setActiveTab(tab.id)}
            >
              <Text style={styles.tabIcon}>{tab.icon}</Text>
              <Text style={[styles.tabLabel, activeTab === tab.id && styles.tabLabelActive]}>
                {tab.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#070709',
  },
  safeArea: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 215, 0, 0.1)',
  },
  logo: {
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 2,
  },
  logoGold: {
    color: '#FFD700',
  },
  logoWhite: {
    color: '#fff',
    fontWeight: '400',
  },
  dayBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 215, 0, 0.3)',
  },
  dayText: {
    color: '#FFD700',
    fontSize: 12,
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: 'rgba(13, 13, 15, 0.95)',
    borderTopWidth: 1,
    borderTopColor: 'rgba(255, 255, 255, 0.05)',
    paddingBottom: 5,
  },
  tab: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 10,
  },
  tabActive: {
    backgroundColor: 'rgba(255, 215, 0, 0.1)',
    borderRadius: 10,
    marginHorizontal: 5,
  },
  tabIcon: {
    fontSize: 20,
    marginBottom: 4,
  },
  tabLabel: {
    fontSize: 10,
    color: 'rgba(255, 255, 255, 0.5)',
    fontWeight: '600',
  },
  tabLabelActive: {
    color: '#FFD700',
  },
});
