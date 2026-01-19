/**
 * PEMF Forge - Main Application
 * Domain: 07_TRANSCEND - Consciousness & Frequencies
 * Version: 1.0.0
 *
 * Main application controller integrating all modules:
 * - Device connection (Bluetooth)
 * - Frequency/intensity control
 * - Treatment protocols
 * - Session history
 * - Safety controls
 * - Waveform visualization
 */

class PEMFApp {
    constructor() {
        // State
        this.isRunning = false;
        this.currentFrequency = 7.83;
        this.currentIntensity = 50;
        this.currentWaveform = 'sine';
        this.timerDuration = 15; // minutes
        this.timerRemaining = 15 * 60; // seconds
        this.timerInterval = null;
        this.currentProtocol = null;
        this.protocolStepIndex = 0;
        this.protocolStepTimeout = null;

        // Safety settings
        this.settings = {
            maxDuration: 60,
            maxIntensity: 100,
            cooldownPeriod: 15,
            showSafetyWarnings: true,
            autoConnect: false,
            soundAlerts: true,
            showVisualization: true
        };

        // Cooldown tracking
        this.lastSessionEnd = null;

        // Canvas for visualization
        this.canvas = null;
        this.ctx = null;
        this.animationFrame = null;

        // Initialize
        this.init();
    }

    init() {
        this.loadSettings();
        this.setupEventListeners();
        this.setupVisualization();
        this.updateUI();
        this.renderProtocols();
        this.renderHistory();
        this.checkSafetyWarning();

        // Setup Bluetooth callbacks
        PEMFBluetooth.on('connect', (deviceInfo) => this.onDeviceConnected(deviceInfo));
        PEMFBluetooth.on('disconnect', () => this.onDeviceDisconnected());
        PEMFBluetooth.on('error', (msg) => this.showToast(msg, 'error'));

        console.log('PEMF Forge initialized');
    }

    // ==================== Event Listeners ====================

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchView(e.target.closest('.nav-btn').dataset.view));
        });

        // Device connection
        document.getElementById('connectBtn')?.addEventListener('click', () => this.connectDevice());

        // Frequency controls
        const freqSlider = document.getElementById('frequencySlider');
        freqSlider?.addEventListener('input', (e) => this.setFrequency(parseFloat(e.target.value)));

        document.querySelectorAll('.freq-preset').forEach(btn => {
            btn.addEventListener('click', (e) => this.setFrequency(parseFloat(e.target.dataset.freq)));
        });

        // Intensity controls
        const intensitySlider = document.getElementById('intensitySlider');
        intensitySlider?.addEventListener('input', (e) => this.setIntensity(parseInt(e.target.value)));

        // Waveform selection
        document.querySelectorAll('.waveform-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.setWaveform(e.target.closest('.waveform-btn').dataset.waveform));
        });

        // Timer controls
        const timerSlider = document.getElementById('timerSlider');
        timerSlider?.addEventListener('input', (e) => this.setTimerDuration(parseInt(e.target.value)));

        document.querySelectorAll('.timer-preset').forEach(btn => {
            btn.addEventListener('click', (e) => this.setTimerDuration(parseInt(e.target.dataset.minutes)));
        });

        // Start/Stop button
        document.getElementById('startBtn')?.addEventListener('click', () => this.toggleSession());

        // Protocol creation
        document.getElementById('createProtocolBtn')?.addEventListener('click', () => this.openProtocolModal());
        document.getElementById('closeModal')?.addEventListener('click', () => this.closeProtocolModal());
        document.getElementById('cancelProtocol')?.addEventListener('click', () => this.closeProtocolModal());
        document.getElementById('protocolForm')?.addEventListener('submit', (e) => this.saveProtocol(e));
        document.getElementById('addStepBtn')?.addEventListener('click', () => this.addProtocolStep());

        // Protocol categories
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.renderProtocols(e.target.dataset.category);
            });
        });

        // History controls
        document.getElementById('historyPeriod')?.addEventListener('change', (e) => this.renderHistory(e.target.value));
        document.getElementById('exportHistory')?.addEventListener('click', () => PEMFHistory.exportHistory());

        // Settings controls
        this.setupSettingsListeners();

        // Safety modal
        document.getElementById('acceptSafety')?.addEventListener('change', (e) => {
            document.getElementById('acceptSafetyBtn').disabled = !e.target.checked;
        });
        document.getElementById('acceptSafetyBtn')?.addEventListener('click', () => this.acceptSafety());

        // Close modals on outside click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                }
            });
        });
    }

    setupSettingsListeners() {
        // Device settings
        document.getElementById('autoConnect')?.addEventListener('change', (e) => {
            this.settings.autoConnect = e.target.checked;
            this.saveSettings();
        });

        // Safety settings
        document.getElementById('maxDuration')?.addEventListener('change', (e) => {
            this.settings.maxDuration = parseInt(e.target.value);
            this.saveSettings();
        });

        document.getElementById('maxIntensity')?.addEventListener('change', (e) => {
            this.settings.maxIntensity = parseInt(e.target.value);
            this.saveSettings();
        });

        document.getElementById('cooldownPeriod')?.addEventListener('change', (e) => {
            this.settings.cooldownPeriod = parseInt(e.target.value);
            this.saveSettings();
        });

        document.getElementById('safetyWarnings')?.addEventListener('change', (e) => {
            this.settings.showSafetyWarnings = e.target.checked;
            this.saveSettings();
        });

        // Notification settings
        document.getElementById('soundAlerts')?.addEventListener('change', (e) => {
            this.settings.soundAlerts = e.target.checked;
            this.saveSettings();
        });

        // Display settings
        document.getElementById('showViz')?.addEventListener('change', (e) => {
            this.settings.showVisualization = e.target.checked;
            this.saveSettings();
        });

        // Data management
        document.getElementById('clearHistory')?.addEventListener('click', () => {
            if (confirm('Are you sure you want to clear all session history?')) {
                PEMFHistory.clearHistory();
                this.renderHistory();
                this.showToast('History cleared', 'success');
            }
        });

        document.getElementById('resetSettings')?.addEventListener('click', () => {
            if (confirm('Reset all settings to defaults?')) {
                this.resetSettings();
                this.showToast('Settings reset', 'success');
            }
        });
    }

    // ==================== Navigation ====================

    switchView(viewName) {
        // Update nav buttons
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.view === viewName);
        });

        // Update views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.toggle('active', view.id === viewName + 'View');
        });

        // Refresh view-specific content
        if (viewName === 'history') {
            this.renderHistory();
        } else if (viewName === 'protocols') {
            this.renderProtocols();
        }
    }

    // ==================== Device Connection ====================

    async connectDevice() {
        const btn = document.getElementById('connectBtn');

        if (PEMFBluetooth.isConnected) {
            PEMFBluetooth.disconnect();
            return;
        }

        btn.textContent = 'Connecting...';
        btn.disabled = true;

        // Try real Bluetooth first, fall back to simulation
        const connected = await PEMFBluetooth.connect();

        if (!connected && !PEMFBluetooth.isSupported()) {
            // Offer simulation mode
            if (confirm('Web Bluetooth not supported. Would you like to use simulation mode for testing?')) {
                PEMFBluetooth.simulateDevice();
            }
        }

        btn.disabled = false;
        this.updateConnectButton();
    }

    onDeviceConnected(deviceInfo) {
        this.updateConnectButton();
        this.updateDeviceInfo(deviceInfo);
        this.showToast('Device connected: ' + deviceInfo.name, 'success');
    }

    onDeviceDisconnected() {
        this.updateConnectButton();
        document.getElementById('deviceInfo')?.classList.add('hidden');

        if (this.isRunning) {
            this.stopSession();
            this.showToast('Session stopped: Device disconnected', 'warning');
        } else {
            this.showToast('Device disconnected', 'warning');
        }
    }

    updateConnectButton() {
        const btn = document.getElementById('connectBtn');
        if (!btn) return;

        if (PEMFBluetooth.isConnected) {
            btn.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
                Disconnect`;
        } else {
            btn.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>
                    <circle cx="12" cy="12" r="9"/>
                </svg>
                Connect PEMF Device`;
        }
    }

    updateDeviceInfo(info) {
        const container = document.getElementById('deviceInfo');
        if (!container) return;

        container.classList.remove('hidden');
        document.getElementById('deviceName').textContent = info.name || '-';
        document.getElementById('deviceBattery').textContent = info.battery || '-';
        document.getElementById('deviceFirmware').textContent = info.firmware || '-';
    }

    // ==================== Frequency Control ====================

    setFrequency(freq) {
        this.currentFrequency = Math.max(0.1, Math.min(100, freq));

        // Update slider
        const slider = document.getElementById('frequencySlider');
        if (slider) slider.value = this.currentFrequency;

        // Update display
        document.getElementById('freqDisplay').textContent = this.currentFrequency.toFixed(2);
        document.getElementById('vizFreq').textContent = this.currentFrequency.toFixed(2) + ' Hz';

        // Update device if running
        if (this.isRunning && PEMFBluetooth.isConnected) {
            PEMFBluetooth.setFrequency(this.currentFrequency);
        }
    }

    // ==================== Intensity Control ====================

    setIntensity(intensity) {
        // Apply max intensity limit
        intensity = Math.min(intensity, this.settings.maxIntensity);
        this.currentIntensity = Math.max(0, Math.min(100, intensity));

        // Update slider
        const slider = document.getElementById('intensitySlider');
        if (slider) slider.value = this.currentIntensity;

        // Update gauge
        const fill = document.getElementById('intensityFill');
        const value = document.getElementById('intensityValue');
        if (fill) fill.style.width = this.currentIntensity + '%';
        if (value) value.textContent = this.currentIntensity + '%';

        // Update viz
        document.getElementById('vizIntensity').textContent = this.currentIntensity + '%';

        // Update device if running
        if (this.isRunning && PEMFBluetooth.isConnected) {
            PEMFBluetooth.setIntensity(this.currentIntensity);
        }
    }

    // ==================== Waveform Selection ====================

    setWaveform(waveform) {
        this.currentWaveform = waveform;

        // Update buttons
        document.querySelectorAll('.waveform-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.waveform === waveform);
        });
    }

    // ==================== Timer Control ====================

    setTimerDuration(minutes) {
        // Apply max duration limit
        minutes = Math.min(minutes, this.settings.maxDuration);
        this.timerDuration = Math.max(1, Math.min(120, minutes));
        this.timerRemaining = this.timerDuration * 60;

        // Update slider
        const slider = document.getElementById('timerSlider');
        if (slider) slider.value = this.timerDuration;

        // Update presets
        document.querySelectorAll('.timer-preset').forEach(btn => {
            btn.classList.toggle('active', parseInt(btn.dataset.minutes) === this.timerDuration);
        });

        this.updateTimerDisplay();
    }

    updateTimerDisplay() {
        const mins = Math.floor(this.timerRemaining / 60);
        const secs = this.timerRemaining % 60;

        document.getElementById('timerMinutes').textContent = mins.toString().padStart(2, '0');
        document.getElementById('timerSeconds').textContent = secs.toString().padStart(2, '0');
    }

    // ==================== Session Control ====================

    toggleSession() {
        if (this.isRunning) {
            this.stopSession();
        } else {
            this.startSession();
        }
    }

    startSession() {
        // Check cooldown
        if (this.lastSessionEnd) {
            const cooldownMs = this.settings.cooldownPeriod * 60 * 1000;
            const elapsed = Date.now() - this.lastSessionEnd;
            if (elapsed < cooldownMs) {
                const remaining = Math.ceil((cooldownMs - elapsed) / 60000);
                this.showToast(`Please wait ${remaining} more minute(s) before next session`, 'warning');
                return;
            }
        }

        this.isRunning = true;
        this.timerRemaining = this.timerDuration * 60;

        // Start history tracking
        PEMFHistory.startSession(this.currentProtocol, {
            frequency: this.currentFrequency,
            intensity: this.currentIntensity,
            waveform: this.currentWaveform,
            targetDuration: this.timerDuration
        });

        // Send to device
        if (PEMFBluetooth.isConnected) {
            PEMFBluetooth.start(this.currentFrequency, this.currentIntensity, this.currentWaveform);
        }

        // Update UI
        this.updateSessionUI();

        // Start timer
        this.timerInterval = setInterval(() => this.timerTick(), 1000);

        // Start protocol steps if applicable
        if (this.currentProtocol && this.currentProtocol.steps.length > 1) {
            this.protocolStepIndex = 0;
            this.runProtocolStep();
        }

        this.showToast('Session started', 'success');
    }

    stopSession() {
        this.isRunning = false;

        // Clear timers
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        if (this.protocolStepTimeout) {
            clearTimeout(this.protocolStepTimeout);
            this.protocolStepTimeout = null;
        }

        // Stop device
        if (PEMFBluetooth.isConnected) {
            PEMFBluetooth.stop();
        }

        // End history session
        const session = PEMFHistory.endSession(this.timerRemaining <= 0);

        // Record cooldown
        this.lastSessionEnd = Date.now();

        // Reset timer
        this.timerRemaining = this.timerDuration * 60;
        this.updateTimerDisplay();

        // Update UI
        this.updateSessionUI();

        // Refresh history view
        this.renderHistory();

        this.showToast('Session ended', 'success');

        // Play sound alert
        if (this.settings.soundAlerts) {
            this.playAlert();
        }
    }

    timerTick() {
        this.timerRemaining--;
        this.updateTimerDisplay();

        // Update progress
        const progress = 1 - (this.timerRemaining / (this.timerDuration * 60));
        const fill = document.getElementById('progressFill');
        if (fill) fill.style.width = (progress * 100) + '%';

        // Session complete
        if (this.timerRemaining <= 0) {
            this.stopSession();
        }
    }

    runProtocolStep() {
        if (!this.isRunning || !this.currentProtocol) return;

        const step = this.currentProtocol.steps[this.protocolStepIndex];
        if (!step) return;

        // Apply step settings
        this.setFrequency(step.frequency);
        this.setIntensity(step.intensity);
        this.setWaveform(step.waveform);

        // Record step
        PEMFHistory.recordStep(step.frequency, step.intensity, step.waveform);

        // Schedule next step
        if (this.protocolStepIndex < this.currentProtocol.steps.length - 1) {
            this.protocolStepTimeout = setTimeout(() => {
                this.protocolStepIndex++;
                this.runProtocolStep();
            }, step.duration * 60 * 1000);
        }
    }

    updateSessionUI() {
        const startBtn = document.getElementById('startBtn');
        const progressSection = document.getElementById('sessionProgress');
        const playIcon = startBtn?.querySelector('.play');
        const stopIcon = startBtn?.querySelector('.stop');
        const btnText = startBtn?.querySelector('.btn-text');

        if (this.isRunning) {
            startBtn?.classList.add('running');
            playIcon?.classList.add('hidden');
            stopIcon?.classList.remove('hidden');
            if (btnText) btnText.textContent = 'Stop Session';
            progressSection?.classList.remove('hidden');
        } else {
            startBtn?.classList.remove('running');
            playIcon?.classList.remove('hidden');
            stopIcon?.classList.add('hidden');
            if (btnText) btnText.textContent = 'Start Session';
            progressSection?.classList.add('hidden');

            // Reset progress
            const fill = document.getElementById('progressFill');
            if (fill) fill.style.width = '0%';
        }
    }

    // ==================== Visualization ====================

    setupVisualization() {
        this.canvas = document.getElementById('waveformCanvas');
        if (!this.canvas) return;

        this.ctx = this.canvas.getContext('2d');

        // Set canvas size
        const resize = () => {
            const rect = this.canvas.getBoundingClientRect();
            this.canvas.width = rect.width * window.devicePixelRatio;
            this.canvas.height = rect.height * window.devicePixelRatio;
            this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        };

        resize();
        window.addEventListener('resize', resize);

        // Start animation
        this.animateWaveform();
    }

    animateWaveform() {
        if (!this.canvas || !this.ctx) return;

        const width = this.canvas.width / window.devicePixelRatio;
        const height = this.canvas.height / window.devicePixelRatio;
        const time = Date.now() / 1000;

        // Clear
        this.ctx.fillStyle = '#1a1a25';
        this.ctx.fillRect(0, 0, width, height);

        // Draw grid
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
        this.ctx.lineWidth = 1;

        for (let x = 0; x < width; x += 40) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, height);
            this.ctx.stroke();
        }

        for (let y = 0; y < height; y += 40) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(width, y);
            this.ctx.stroke();
        }

        // Draw waveform
        const amplitude = (this.currentIntensity / 100) * (height / 2 - 20);
        const frequency = this.currentFrequency;
        const centerY = height / 2;

        // Glow effect
        if (this.isRunning) {
            this.ctx.shadowColor = '#00d4ff';
            this.ctx.shadowBlur = 20;
        } else {
            this.ctx.shadowBlur = 0;
        }

        this.ctx.beginPath();
        this.ctx.strokeStyle = this.isRunning ? '#00d4ff' : '#505060';
        this.ctx.lineWidth = 2;

        for (let x = 0; x < width; x++) {
            const t = (x / width) * 4 * Math.PI + time * frequency * 0.5;
            let y;

            switch (this.currentWaveform) {
                case 'square':
                    y = Math.sin(t) > 0 ? -amplitude : amplitude;
                    break;
                case 'sawtooth':
                    y = ((t % (2 * Math.PI)) / Math.PI - 1) * amplitude;
                    break;
                case 'pulse':
                    y = Math.sin(t) > 0.7 ? -amplitude : amplitude * 0.1;
                    break;
                case 'sine':
                default:
                    y = Math.sin(t) * amplitude;
            }

            if (x === 0) {
                this.ctx.moveTo(x, centerY + y);
            } else {
                this.ctx.lineTo(x, centerY + y);
            }
        }

        this.ctx.stroke();
        this.ctx.shadowBlur = 0;

        // Update field strength display
        if (this.isRunning) {
            const fieldStrength = (this.currentIntensity * 0.5).toFixed(1);
            document.getElementById('vizField').textContent = fieldStrength + ' μT';
        } else {
            document.getElementById('vizField').textContent = '-- μT';
        }

        this.animationFrame = requestAnimationFrame(() => this.animateWaveform());
    }

    // ==================== Protocols ====================

    renderProtocols(category = 'all') {
        const grid = document.getElementById('protocolsGrid');
        if (!grid) return;

        const protocols = PEMFProtocols.getByCategory(category);

        grid.innerHTML = protocols.map(p => `
            <div class="protocol-card" data-id="${p.id}">
                <div class="protocol-card-header">
                    <h3>${p.name}</h3>
                    <span class="protocol-category-tag" style="background: ${PEMFProtocols.getCategoryInfo(p.category).color}">${p.category}</span>
                </div>
                <p class="protocol-card-description">${p.description}</p>
                <div class="protocol-card-meta">
                    <span>${p.totalDuration} min</span>
                    <span>${p.steps.length} step${p.steps.length > 1 ? 's' : ''}</span>
                </div>
                <div class="protocol-card-actions">
                    <button class="protocol-action-btn primary" onclick="app.loadProtocol('${p.id}')">Load</button>
                    ${!p.isDefault ? `<button class="protocol-action-btn" onclick="app.deleteProtocol('${p.id}')">Delete</button>` : ''}
                </div>
            </div>
        `).join('');
    }

    loadProtocol(id) {
        const protocol = PEMFProtocols.getById(id);
        if (!protocol) return;

        this.currentProtocol = protocol;

        // Load first step settings
        const firstStep = protocol.steps[0];
        this.setFrequency(firstStep.frequency);
        this.setIntensity(firstStep.intensity);
        this.setWaveform(firstStep.waveform);
        this.setTimerDuration(protocol.totalDuration);

        // Switch to control view
        this.switchView('control');

        this.showToast(`Loaded: ${protocol.name}`, 'success');
    }

    deleteProtocol(id) {
        if (confirm('Delete this custom protocol?')) {
            PEMFProtocols.deleteCustomProtocol(id);
            this.renderProtocols();
            this.showToast('Protocol deleted', 'success');
        }
    }

    openProtocolModal() {
        document.getElementById('protocolModal')?.classList.remove('hidden');
        document.getElementById('protocolForm')?.reset();

        // Reset steps to single step
        const stepsContainer = document.getElementById('protocolSteps');
        stepsContainer.innerHTML = `
            <div class="step-item">
                <input type="number" placeholder="Freq (Hz)" class="step-freq" min="0.1" max="100" step="0.1" value="7.83">
                <input type="number" placeholder="Duration (min)" class="step-duration" min="1" max="60" value="15">
                <input type="number" placeholder="Intensity %" class="step-intensity" min="1" max="100" value="50">
                <select class="step-waveform">
                    <option value="sine">Sine</option>
                    <option value="square">Square</option>
                    <option value="sawtooth">Sawtooth</option>
                    <option value="pulse">Pulse</option>
                </select>
                <button type="button" class="remove-step hidden">&times;</button>
            </div>
        `;
    }

    closeProtocolModal() {
        document.getElementById('protocolModal')?.classList.add('hidden');
    }

    addProtocolStep() {
        const stepsContainer = document.getElementById('protocolSteps');
        const stepCount = stepsContainer.querySelectorAll('.step-item').length;

        const stepHtml = `
            <div class="step-item">
                <input type="number" placeholder="Freq (Hz)" class="step-freq" min="0.1" max="100" step="0.1">
                <input type="number" placeholder="Duration (min)" class="step-duration" min="1" max="60">
                <input type="number" placeholder="Intensity %" class="step-intensity" min="1" max="100">
                <select class="step-waveform">
                    <option value="sine">Sine</option>
                    <option value="square">Square</option>
                    <option value="sawtooth">Sawtooth</option>
                    <option value="pulse">Pulse</option>
                </select>
                <button type="button" class="remove-step" onclick="this.closest('.step-item').remove()">&times;</button>
            </div>
        `;

        stepsContainer.insertAdjacentHTML('beforeend', stepHtml);

        // Show remove buttons if more than one step
        if (stepCount >= 1) {
            stepsContainer.querySelectorAll('.remove-step').forEach(btn => btn.classList.remove('hidden'));
        }
    }

    saveProtocol(e) {
        e.preventDefault();

        const name = document.getElementById('protocolName').value.trim();
        const category = document.getElementById('protocolCategory').value;
        const description = document.getElementById('protocolDescription').value.trim();

        // Gather steps
        const steps = [];
        document.querySelectorAll('#protocolSteps .step-item').forEach(item => {
            const freq = parseFloat(item.querySelector('.step-freq').value);
            const duration = parseInt(item.querySelector('.step-duration').value);
            const intensity = parseInt(item.querySelector('.step-intensity').value);
            const waveform = item.querySelector('.step-waveform').value;

            if (freq && duration && intensity) {
                steps.push({ frequency: freq, duration, intensity, waveform });
            }
        });

        if (!name || steps.length === 0) {
            this.showToast('Please fill in all required fields', 'error');
            return;
        }

        const protocol = {
            name,
            category,
            description,
            steps,
            benefits: []
        };

        if (PEMFProtocols.saveCustomProtocol(protocol)) {
            this.closeProtocolModal();
            this.renderProtocols();
            this.showToast('Protocol saved', 'success');
        } else {
            this.showToast('Failed to save protocol', 'error');
        }
    }

    // ==================== History ====================

    renderHistory(period = 'week') {
        const stats = PEMFHistory.getStatistics(period);
        const sessions = PEMFHistory.getSessionsByPeriod(period);

        // Update stats
        document.getElementById('totalSessions').textContent = stats.totalSessions;
        document.getElementById('totalMinutes').textContent = stats.totalMinutes;
        document.getElementById('streakDays').textContent = stats.streakDays;

        // Render chart
        this.renderHistoryChart(stats.dailyStats);

        // Render session list
        const list = document.getElementById('historyList');
        if (!list) return;

        if (sessions.length === 0) {
            list.innerHTML = '<p style="color: var(--text-muted); text-align: center; padding: 40px;">No sessions recorded yet</p>';
            return;
        }

        list.innerHTML = sessions.slice(0, 20).map(s => {
            const date = new Date(s.startTime);
            return `
                <div class="history-item">
                    <div class="history-date">
                        <span class="day">${date.getDate()}</span>
                        <span class="month">${date.toLocaleDateString('en-US', { month: 'short' })}</span>
                    </div>
                    <div class="history-details">
                        <div class="history-protocol">${s.protocol?.name || 'Manual Session'}</div>
                        <div class="history-meta">${s.settings?.frequency || 0} Hz @ ${s.settings?.intensity || 0}%</div>
                    </div>
                    <div class="history-duration">${s.duration || 0} min</div>
                </div>
            `;
        }).join('');
    }

    renderHistoryChart(dailyStats) {
        const canvas = document.getElementById('historyChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const width = canvas.offsetWidth;
        const height = canvas.offsetHeight;

        canvas.width = width * window.devicePixelRatio;
        canvas.height = height * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);

        // Clear
        ctx.fillStyle = 'transparent';
        ctx.fillRect(0, 0, width, height);

        if (dailyStats.length === 0) {
            ctx.fillStyle = '#606075';
            ctx.font = '14px Rajdhani';
            ctx.textAlign = 'center';
            ctx.fillText('No data to display', width / 2, height / 2);
            return;
        }

        // Find max value
        const maxMinutes = Math.max(...dailyStats.map(d => d.minutes), 1);

        // Draw bars
        const barWidth = (width - 40) / dailyStats.length - 8;
        const barMaxHeight = height - 40;

        dailyStats.forEach((day, i) => {
            const x = 20 + i * ((width - 40) / dailyStats.length) + 4;
            const barHeight = (day.minutes / maxMinutes) * barMaxHeight;
            const y = height - 20 - barHeight;

            // Bar gradient
            const gradient = ctx.createLinearGradient(x, y, x, y + barHeight);
            gradient.addColorStop(0, '#00d4ff');
            gradient.addColorStop(1, '#7b2cbf');

            ctx.fillStyle = gradient;
            ctx.fillRect(x, y, barWidth, barHeight);

            // Date label
            ctx.fillStyle = '#606075';
            ctx.font = '10px Rajdhani';
            ctx.textAlign = 'center';
            const label = new Date(day.date).getDate().toString();
            ctx.fillText(label, x + barWidth / 2, height - 5);
        });
    }

    // ==================== Safety ====================

    checkSafetyWarning() {
        const accepted = localStorage.getItem('pemf_safety_accepted');
        if (!accepted && this.settings.showSafetyWarnings) {
            document.getElementById('safetyModal')?.classList.remove('hidden');
        }
    }

    acceptSafety() {
        localStorage.setItem('pemf_safety_accepted', 'true');
        document.getElementById('safetyModal')?.classList.add('hidden');
    }

    // ==================== Settings ====================

    loadSettings() {
        try {
            const stored = localStorage.getItem('pemf_settings');
            if (stored) {
                this.settings = { ...this.settings, ...JSON.parse(stored) };
            }
        } catch (e) {
            console.error('Error loading settings:', e);
        }

        // Apply settings to UI
        this.applySettingsToUI();
    }

    saveSettings() {
        try {
            localStorage.setItem('pemf_settings', JSON.stringify(this.settings));
        } catch (e) {
            console.error('Error saving settings:', e);
        }
    }

    resetSettings() {
        this.settings = {
            maxDuration: 60,
            maxIntensity: 100,
            cooldownPeriod: 15,
            showSafetyWarnings: true,
            autoConnect: false,
            soundAlerts: true,
            showVisualization: true
        };
        this.saveSettings();
        this.applySettingsToUI();
    }

    applySettingsToUI() {
        const setChecked = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.checked = value;
        };

        const setValue = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.value = value;
        };

        setChecked('autoConnect', this.settings.autoConnect);
        setValue('maxDuration', this.settings.maxDuration);
        setValue('maxIntensity', this.settings.maxIntensity);
        setValue('cooldownPeriod', this.settings.cooldownPeriod);
        setChecked('safetyWarnings', this.settings.showSafetyWarnings);
        setChecked('soundAlerts', this.settings.soundAlerts);
        setChecked('showViz', this.settings.showVisualization);
    }

    // ==================== Utilities ====================

    updateUI() {
        this.setFrequency(this.currentFrequency);
        this.setIntensity(this.currentIntensity);
        this.setWaveform(this.currentWaveform);
        this.setTimerDuration(this.timerDuration);
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    playAlert() {
        // Create audio context for alert sound
        try {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioCtx.createOscillator();
            const gainNode = audioCtx.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audioCtx.destination);

            oscillator.frequency.value = 880;
            oscillator.type = 'sine';
            gainNode.gain.value = 0.1;

            oscillator.start();

            gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);

            setTimeout(() => {
                oscillator.stop();
                audioCtx.close();
            }, 500);
        } catch (e) {
            console.log('Audio alert not available');
        }
    }
}

// Initialize app when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new PEMFApp();
    window.app = app; // Make available globally for onclick handlers
});
