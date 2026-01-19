/**
 * PEMF Forge - Session History Module
 * Domain: 07_TRANSCEND - Consciousness & Frequencies
 *
 * This module handles session tracking, history storage,
 * statistics calculation, and data export.
 */

const PEMFHistory = {
    // Storage key
    STORAGE_KEY: 'pemf_session_history',

    // Current session data
    currentSession: null,

    /**
     * Start a new session
     */
    startSession(protocol, settings) {
        this.currentSession = {
            id: 'session-' + Date.now(),
            startTime: new Date().toISOString(),
            endTime: null,
            duration: 0,
            protocol: protocol ? {
                id: protocol.id,
                name: protocol.name,
                category: protocol.category
            } : null,
            settings: {
                frequency: settings.frequency,
                intensity: settings.intensity,
                waveform: settings.waveform,
                targetDuration: settings.targetDuration
            },
            steps: [],
            completed: false,
            notes: ''
        };

        console.log('Session started:', this.currentSession.id);
        return this.currentSession;
    },

    /**
     * Record a step change during session
     */
    recordStep(frequency, intensity, waveform, timestamp) {
        if (!this.currentSession) return;

        this.currentSession.steps.push({
            time: timestamp || new Date().toISOString(),
            frequency,
            intensity,
            waveform
        });
    },

    /**
     * End current session
     */
    endSession(completed = true) {
        if (!this.currentSession) return null;

        this.currentSession.endTime = new Date().toISOString();
        this.currentSession.completed = completed;

        // Calculate actual duration
        const start = new Date(this.currentSession.startTime);
        const end = new Date(this.currentSession.endTime);
        this.currentSession.duration = Math.round((end - start) / 1000 / 60); // Duration in minutes

        // Save session
        this.saveSession(this.currentSession);

        const session = this.currentSession;
        this.currentSession = null;

        console.log('Session ended:', session.id, 'Duration:', session.duration, 'min');
        return session;
    },

    /**
     * Cancel current session (don't save)
     */
    cancelSession() {
        const session = this.currentSession;
        this.currentSession = null;
        console.log('Session cancelled');
        return session;
    },

    /**
     * Add notes to last session
     */
    addNotes(sessionId, notes) {
        const sessions = this.getAllSessions();
        const session = sessions.find(s => s.id === sessionId);

        if (session) {
            session.notes = notes;
            this.saveSessions(sessions);
            return true;
        }
        return false;
    },

    /**
     * Save session to storage
     */
    saveSession(session) {
        const sessions = this.getAllSessions();
        sessions.unshift(session); // Add to beginning

        // Limit storage (keep last 500 sessions)
        const maxSessions = 500;
        if (sessions.length > maxSessions) {
            sessions.length = maxSessions;
        }

        this.saveSessions(sessions);
    },

    /**
     * Get all sessions from storage
     */
    getAllSessions() {
        try {
            const stored = localStorage.getItem(this.STORAGE_KEY);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Error loading sessions:', error);
            return [];
        }
    },

    /**
     * Save sessions array to storage
     */
    saveSessions(sessions) {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(sessions));
        } catch (error) {
            console.error('Error saving sessions:', error);
        }
    },

    /**
     * Get sessions by time period
     */
    getSessionsByPeriod(period) {
        const sessions = this.getAllSessions();
        const now = new Date();
        let cutoffDate;

        switch (period) {
            case 'week':
                cutoffDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
                break;
            case 'month':
                cutoffDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
                break;
            case 'year':
                cutoffDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
                break;
            case 'all':
            default:
                return sessions;
        }

        return sessions.filter(s => new Date(s.startTime) >= cutoffDate);
    },

    /**
     * Calculate statistics
     */
    getStatistics(period = 'all') {
        const sessions = this.getSessionsByPeriod(period);

        if (sessions.length === 0) {
            return {
                totalSessions: 0,
                totalMinutes: 0,
                averageDuration: 0,
                streakDays: 0,
                mostUsedProtocol: null,
                frequencyBreakdown: {},
                dailyStats: []
            };
        }

        // Total sessions and minutes
        const totalSessions = sessions.length;
        const totalMinutes = sessions.reduce((sum, s) => sum + (s.duration || 0), 0);
        const averageDuration = Math.round(totalMinutes / totalSessions);

        // Calculate streak
        const streakDays = this.calculateStreak(sessions);

        // Most used protocol
        const protocolCounts = {};
        sessions.forEach(s => {
            if (s.protocol && s.protocol.name) {
                protocolCounts[s.protocol.name] = (protocolCounts[s.protocol.name] || 0) + 1;
            }
        });

        let mostUsedProtocol = null;
        let maxCount = 0;
        for (const [name, count] of Object.entries(protocolCounts)) {
            if (count > maxCount) {
                maxCount = count;
                mostUsedProtocol = name;
            }
        }

        // Frequency breakdown
        const frequencyBreakdown = {
            delta: 0,
            theta: 0,
            alpha: 0,
            beta: 0,
            gamma: 0
        };

        sessions.forEach(s => {
            const freq = s.settings?.frequency || 0;
            if (freq < 3) frequencyBreakdown.delta++;
            else if (freq < 8) frequencyBreakdown.theta++;
            else if (freq < 12) frequencyBreakdown.alpha++;
            else if (freq < 30) frequencyBreakdown.beta++;
            else frequencyBreakdown.gamma++;
        });

        // Daily stats for chart
        const dailyStats = this.getDailyStats(sessions);

        return {
            totalSessions,
            totalMinutes,
            averageDuration,
            streakDays,
            mostUsedProtocol,
            frequencyBreakdown,
            dailyStats
        };
    },

    /**
     * Calculate consecutive day streak
     */
    calculateStreak(sessions) {
        if (sessions.length === 0) return 0;

        // Get unique session dates
        const dates = [...new Set(
            sessions.map(s => new Date(s.startTime).toDateString())
        )].sort((a, b) => new Date(b) - new Date(a));

        if (dates.length === 0) return 0;

        // Check if most recent is today or yesterday
        const today = new Date().toDateString();
        const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toDateString();

        if (dates[0] !== today && dates[0] !== yesterday) {
            return 0;
        }

        // Count consecutive days
        let streak = 1;
        for (let i = 0; i < dates.length - 1; i++) {
            const current = new Date(dates[i]);
            const next = new Date(dates[i + 1]);
            const diffDays = (current - next) / (24 * 60 * 60 * 1000);

            if (diffDays === 1) {
                streak++;
            } else {
                break;
            }
        }

        return streak;
    },

    /**
     * Get daily statistics for chart
     */
    getDailyStats(sessions) {
        const dailyMap = new Map();

        // Group by date
        sessions.forEach(s => {
            const date = new Date(s.startTime).toLocaleDateString();
            const existing = dailyMap.get(date) || { sessions: 0, minutes: 0 };
            existing.sessions++;
            existing.minutes += s.duration || 0;
            dailyMap.set(date, existing);
        });

        // Convert to array, sorted by date
        const stats = [];
        dailyMap.forEach((value, key) => {
            stats.push({
                date: key,
                sessions: value.sessions,
                minutes: value.minutes
            });
        });

        return stats.sort((a, b) => new Date(a.date) - new Date(b.date)).slice(-14); // Last 14 days
    },

    /**
     * Delete a session
     */
    deleteSession(sessionId) {
        const sessions = this.getAllSessions();
        const filtered = sessions.filter(s => s.id !== sessionId);
        this.saveSessions(filtered);
    },

    /**
     * Clear all history
     */
    clearHistory() {
        try {
            localStorage.removeItem(this.STORAGE_KEY);
            console.log('History cleared');
            return true;
        } catch (error) {
            console.error('Error clearing history:', error);
            return false;
        }
    },

    /**
     * Export history to JSON
     */
    exportHistory() {
        const sessions = this.getAllSessions();
        const stats = this.getStatistics('all');

        const exportData = {
            exportDate: new Date().toISOString(),
            statistics: stats,
            sessions: sessions
        };

        const dataStr = JSON.stringify(exportData, null, 2);
        const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

        const exportName = `pemf_history_${new Date().toISOString().split('T')[0]}.json`;

        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportName);
        linkElement.click();
    },

    /**
     * Export history to CSV
     */
    exportHistoryCSV() {
        const sessions = this.getAllSessions();

        const headers = ['Date', 'Time', 'Duration (min)', 'Protocol', 'Frequency (Hz)', 'Intensity (%)', 'Waveform', 'Completed', 'Notes'];

        const rows = sessions.map(s => {
            const date = new Date(s.startTime);
            return [
                date.toLocaleDateString(),
                date.toLocaleTimeString(),
                s.duration || 0,
                s.protocol?.name || 'Manual',
                s.settings?.frequency || 0,
                s.settings?.intensity || 0,
                s.settings?.waveform || 'sine',
                s.completed ? 'Yes' : 'No',
                (s.notes || '').replace(/"/g, '""')
            ];
        });

        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
        ].join('\n');

        const dataUri = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent);
        const exportName = `pemf_history_${new Date().toISOString().split('T')[0]}.csv`;

        const linkElement = document.createElement('a');
        linkElement.setAttribute('href', dataUri);
        linkElement.setAttribute('download', exportName);
        linkElement.click();
    },

    /**
     * Import history from JSON
     */
    importHistory(jsonString, merge = true) {
        try {
            const imported = JSON.parse(jsonString);

            if (!imported.sessions || !Array.isArray(imported.sessions)) {
                throw new Error('Invalid format: expected sessions array');
            }

            if (merge) {
                const existing = this.getAllSessions();
                const existingIds = new Set(existing.map(s => s.id));

                // Add non-duplicate sessions
                const newSessions = imported.sessions.filter(s => !existingIds.has(s.id));
                const merged = [...existing, ...newSessions];

                // Sort by date, newest first
                merged.sort((a, b) => new Date(b.startTime) - new Date(a.startTime));

                this.saveSessions(merged);
                console.log(`Imported ${newSessions.length} new sessions`);
            } else {
                this.saveSessions(imported.sessions);
                console.log(`Replaced history with ${imported.sessions.length} sessions`);
            }

            return true;
        } catch (error) {
            console.error('Error importing history:', error);
            return false;
        }
    },

    /**
     * Get recent sessions for display
     */
    getRecentSessions(limit = 10) {
        return this.getAllSessions().slice(0, limit);
    },

    /**
     * Format duration for display
     */
    formatDuration(minutes) {
        if (minutes < 60) {
            return `${minutes} min`;
        }
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
    },

    /**
     * Format date for display
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffDays = Math.floor((now - date) / (24 * 60 * 60 * 1000));

        if (diffDays === 0) {
            return 'Today';
        } else if (diffDays === 1) {
            return 'Yesterday';
        } else if (diffDays < 7) {
            return date.toLocaleDateString('en-US', { weekday: 'long' });
        } else {
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        }
    }
};

// Make available globally
window.PEMFHistory = PEMFHistory;
