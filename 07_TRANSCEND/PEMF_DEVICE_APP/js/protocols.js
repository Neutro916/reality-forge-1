/**
 * PEMF Forge - Treatment Protocols Module
 * Domain: 07_TRANSCEND - Consciousness & Frequencies
 *
 * This module contains pre-defined PEMF treatment protocols
 * based on research and common therapeutic applications.
 */

const PEMFProtocols = {
    // Default protocols library
    defaultProtocols: [
        {
            id: 'schumann-grounding',
            name: 'Schumann Resonance Grounding',
            category: 'healing',
            description: 'Earth\'s natural electromagnetic frequency for grounding and overall wellness. Promotes cellular coherence and stress reduction.',
            totalDuration: 20,
            steps: [
                { frequency: 7.83, duration: 20, intensity: 50, waveform: 'sine' }
            ],
            benefits: ['Stress reduction', 'Improved sleep', 'Cellular coherence', 'Grounding'],
            isDefault: true
        },
        {
            id: 'mid-range-relaxation',
            name: '8-12 Hz Relaxation',
            category: 'sleep',
            description: 'Mid-range frequencies for relaxation. Ideal for pre-sleep preparation.',
            totalDuration: 30,
            steps: [
                { frequency: 12, duration: 5, intensity: 40, waveform: 'sine' },
                { frequency: 10, duration: 15, intensity: 45, waveform: 'sine' },
                { frequency: 8, duration: 10, intensity: 40, waveform: 'sine' }
            ],
            benefits: ['Relaxation', 'Meditation aid', 'Anxiety reduction', 'Mental clarity'],
            isDefault: true
        },
        {
            id: 'energy-boost',
            name: 'Morning Energy Boost',
            category: 'energy',
            description: 'Energizing protocol using 14-20 Hz range to increase alertness and mental clarity.',
            totalDuration: 15,
            steps: [
                { frequency: 14.1, duration: 5, intensity: 55, waveform: 'square' },
                { frequency: 20, duration: 7, intensity: 60, waveform: 'square' },
                { frequency: 15, duration: 3, intensity: 50, waveform: 'sine' }
            ],
            benefits: ['Increased energy', 'Mental alertness', 'Focus', 'Motivation'],
            isDefault: true
        },
        {
            id: '23hz-focus',
            name: '23 Hz Focus & Alertness',
            category: 'focus',
            description: 'Custom 23 Hz frequency preset. Use for sustained focus and mental energy.',
            totalDuration: 25,
            steps: [
                { frequency: 10, duration: 5, intensity: 45, waveform: 'sine' },
                { frequency: 23, duration: 15, intensity: 50, waveform: 'square' },
                { frequency: 14, duration: 5, intensity: 45, waveform: 'sine' }
            ],
            benefits: ['Sustained focus', 'Mental clarity', 'Cognitive enhancement', 'Alertness without anxiety'],
            isDefault: true
        },
        {
            id: '23hz-quick',
            name: '23 Hz Quick Boost',
            category: 'energy',
            description: 'Quick 10-minute session at 23 Hz for instant mental energy and focus.',
            totalDuration: 10,
            steps: [
                { frequency: 23, duration: 10, intensity: 50, waveform: 'square' }
            ],
            benefits: ['Quick energy', 'Instant focus', 'Mental activation', 'Afternoon fatigue relief'],
            isDefault: true
        },
        {
            id: 'deep-tissue-repair',
            name: 'Deep Tissue Repair',
            category: 'healing',
            description: 'Multi-frequency protocol targeting cellular repair and tissue regeneration.',
            totalDuration: 30,
            steps: [
                { frequency: 2, duration: 10, intensity: 60, waveform: 'pulse' },
                { frequency: 10, duration: 10, intensity: 55, waveform: 'sine' },
                { frequency: 73, duration: 10, intensity: 50, waveform: 'sawtooth' }
            ],
            benefits: ['Tissue repair', 'Reduced inflammation', 'Accelerated healing', 'Pain reduction'],
            isDefault: true
        },
        {
            id: 'pain-relief',
            name: 'General Pain Relief',
            category: 'pain',
            description: 'Targeted pain relief protocol using frequencies known to reduce pain signals.',
            totalDuration: 20,
            steps: [
                { frequency: 10, duration: 5, intensity: 50, waveform: 'sine' },
                { frequency: 40, duration: 10, intensity: 55, waveform: 'pulse' },
                { frequency: 7.83, duration: 5, intensity: 45, waveform: 'sine' }
            ],
            benefits: ['Pain reduction', 'Muscle relaxation', 'Anti-inflammatory', 'Circulation boost'],
            isDefault: true
        },
        {
            id: 'joint-inflammation',
            name: 'Joint & Inflammation',
            category: 'pain',
            description: 'Specialized protocol for joint pain and inflammatory conditions.',
            totalDuration: 25,
            steps: [
                { frequency: 3, duration: 8, intensity: 45, waveform: 'pulse' },
                { frequency: 7.83, duration: 9, intensity: 50, waveform: 'sine' },
                { frequency: 10, duration: 8, intensity: 55, waveform: 'sine' }
            ],
            benefits: ['Reduced joint pain', 'Anti-inflammatory', 'Improved mobility', 'Cartilage support'],
            isDefault: true
        },
        {
            id: 'deep-sleep',
            name: 'Deep Sleep Induction',
            category: 'sleep',
            description: 'Gradually descending frequencies from 10 Hz down to 2 Hz for sleep.',
            totalDuration: 45,
            steps: [
                { frequency: 10, duration: 10, intensity: 40, waveform: 'sine' },
                { frequency: 7.83, duration: 10, intensity: 35, waveform: 'sine' },
                { frequency: 4, duration: 15, intensity: 30, waveform: 'sine' },
                { frequency: 2, duration: 10, intensity: 25, waveform: 'sine' }
            ],
            benefits: ['Deep sleep', 'Sleep quality', 'Melatonin support', 'Recovery'],
            isDefault: true
        },
        {
            id: 'focus-concentration',
            name: 'Focus & Concentration',
            category: 'focus',
            description: '14-18 Hz frequency protocol for enhanced cognitive performance and sustained focus.',
            totalDuration: 25,
            steps: [
                { frequency: 14, duration: 5, intensity: 50, waveform: 'sine' },
                { frequency: 18, duration: 15, intensity: 55, waveform: 'square' },
                { frequency: 12, duration: 5, intensity: 45, waveform: 'sine' }
            ],
            benefits: ['Enhanced focus', 'Mental clarity', 'Productivity', 'Cognitive performance'],
            isDefault: true
        },
        {
            id: 'high-frequency',
            name: '30-40 Hz High Frequency',
            category: 'focus',
            description: 'High-frequency 30-40 Hz protocol for peak mental performance.',
            totalDuration: 20,
            steps: [
                { frequency: 30, duration: 5, intensity: 45, waveform: 'sine' },
                { frequency: 40, duration: 10, intensity: 50, waveform: 'sine' },
                { frequency: 35, duration: 5, intensity: 45, waveform: 'sine' }
            ],
            benefits: ['Peak performance', 'Insight', 'Memory', 'Higher cognition'],
            isDefault: true
        },
        {
            id: 'bone-healing',
            name: 'Bone Healing Support',
            category: 'healing',
            description: 'Specific frequencies shown to support bone regeneration and fracture healing.',
            totalDuration: 30,
            steps: [
                { frequency: 7, duration: 10, intensity: 60, waveform: 'pulse' },
                { frequency: 15, duration: 10, intensity: 55, waveform: 'square' },
                { frequency: 72, duration: 10, intensity: 50, waveform: 'sawtooth' }
            ],
            benefits: ['Bone density', 'Fracture healing', 'Calcium absorption', 'Osteoblast activity'],
            isDefault: true
        },
        {
            id: 'muscle-recovery',
            name: 'Post-Workout Recovery',
            category: 'energy',
            description: 'Optimized for post-exercise muscle recovery and reduced soreness.',
            totalDuration: 20,
            steps: [
                { frequency: 10, duration: 5, intensity: 50, waveform: 'sine' },
                { frequency: 3, duration: 10, intensity: 55, waveform: 'pulse' },
                { frequency: 7.83, duration: 5, intensity: 45, waveform: 'sine' }
            ],
            benefits: ['Muscle recovery', 'Reduced soreness', 'Lactic acid clearance', 'Circulation'],
            isDefault: true
        },
        {
            id: 'migraine-relief',
            name: 'Migraine Relief',
            category: 'pain',
            description: 'Gentle frequencies targeting migraine and headache relief.',
            totalDuration: 30,
            steps: [
                { frequency: 0.5, duration: 10, intensity: 30, waveform: 'sine' },
                { frequency: 4, duration: 10, intensity: 35, waveform: 'sine' },
                { frequency: 7.83, duration: 10, intensity: 40, waveform: 'sine' }
            ],
            benefits: ['Headache relief', 'Tension reduction', 'Vascular regulation', 'Relaxation'],
            isDefault: true
        }
    ],

    // Storage key for custom protocols
    STORAGE_KEY: 'pemf_custom_protocols',

    /**
     * Get all protocols (default + custom)
     */
    getAllProtocols() {
        const customProtocols = this.getCustomProtocols();
        return [...this.defaultProtocols, ...customProtocols];
    },

    /**
     * Get protocols by category
     */
    getByCategory(category) {
        if (category === 'all') {
            return this.getAllProtocols();
        }
        return this.getAllProtocols().filter(p => p.category === category);
    },

    /**
     * Get a specific protocol by ID
     */
    getById(id) {
        return this.getAllProtocols().find(p => p.id === id);
    },

    /**
     * Get custom protocols from localStorage
     */
    getCustomProtocols() {
        try {
            const stored = localStorage.getItem(this.STORAGE_KEY);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Error loading custom protocols:', error);
            return [];
        }
    },

    /**
     * Save a custom protocol
     */
    saveCustomProtocol(protocol) {
        const customProtocols = this.getCustomProtocols();

        // Generate ID if not provided
        if (!protocol.id) {
            protocol.id = 'custom-' + Date.now();
        }

        // Calculate total duration
        protocol.totalDuration = protocol.steps.reduce((sum, step) => sum + step.duration, 0);
        protocol.isDefault = false;

        // Check if updating existing
        const existingIndex = customProtocols.findIndex(p => p.id === protocol.id);
        if (existingIndex >= 0) {
            customProtocols[existingIndex] = protocol;
        } else {
            customProtocols.push(protocol);
        }

        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(customProtocols));
            return true;
        } catch (error) {
            console.error('Error saving custom protocol:', error);
            return false;
        }
    },

    /**
     * Delete a custom protocol
     */
    deleteCustomProtocol(id) {
        const customProtocols = this.getCustomProtocols();
        const filtered = customProtocols.filter(p => p.id !== id);

        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(filtered));
            return true;
        } catch (error) {
            console.error('Error deleting custom protocol:', error);
            return false;
        }
    },

    /**
     * Export protocols to JSON
     */
    exportProtocols() {
        const protocols = this.getCustomProtocols();
        const dataStr = JSON.stringify(protocols, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);

        const exportName = `pemf_protocols_${new Date().toISOString().split('T')[0]}.json`;

        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportName);
        linkElement.click();
    },

    /**
     * Import protocols from JSON
     */
    importProtocols(jsonString) {
        try {
            const imported = JSON.parse(jsonString);

            if (!Array.isArray(imported)) {
                throw new Error('Invalid format: expected array');
            }

            const customProtocols = this.getCustomProtocols();

            imported.forEach(protocol => {
                // Validate required fields
                if (!protocol.name || !protocol.steps || !protocol.category) {
                    console.warn('Skipping invalid protocol:', protocol);
                    return;
                }

                // Generate new ID to avoid conflicts
                protocol.id = 'imported-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
                protocol.isDefault = false;
                protocol.totalDuration = protocol.steps.reduce((sum, step) => sum + step.duration, 0);

                customProtocols.push(protocol);
            });

            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(customProtocols));
            return true;
        } catch (error) {
            console.error('Error importing protocols:', error);
            return false;
        }
    },

    /**
     * Get category display info
     */
    getCategoryInfo(category) {
        const categories = {
            healing: { name: 'Healing', color: '#00f5d4', icon: '✚' },
            energy: { name: 'Energy', color: '#ffbe0b', icon: '⚡' },
            sleep: { name: 'Sleep', color: '#7b2cbf', icon: '🌙' },
            pain: { name: 'Pain Relief', color: '#ff006e', icon: '💆' },
            focus: { name: 'Focus', color: '#00d4ff', icon: '🎯' },
            custom: { name: 'Custom', color: '#a0a0b0', icon: '⚙' }
        };
        return categories[category] || categories.custom;
    },

    /**
     * Get frequency info
     */
    getFrequencyInfo(frequency) {
        const frequencyRanges = [
            { min: 0.1, max: 3, name: 'Very Low', description: '0.1-3 Hz range' },
            { min: 3, max: 10, name: 'Low', description: '3-10 Hz range' },
            { min: 10, max: 30, name: 'Medium', description: '10-30 Hz range' },
            { min: 30, max: 100, name: 'High', description: '30-100 Hz range' }
        ];

        // Special frequencies
        const specialFreqs = {
            7.83: { name: 'Schumann Resonance', description: 'Earth\'s fundamental frequency' },
            23: { name: 'Custom Preset', description: '23 Hz frequency' }
        };

        // Check for special frequency
        if (specialFreqs[frequency]) {
            return specialFreqs[frequency];
        }

        // Find range
        const range = frequencyRanges.find(r => frequency >= r.min && frequency < r.max);
        return range || { name: 'Custom', description: 'User-defined frequency' };
    }
};

// Make available globally
window.PEMFProtocols = PEMFProtocols;
