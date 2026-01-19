/**
 * PEMF Forge - Bluetooth Device Connection Module
 * Domain: 07_TRANSCEND - Consciousness & Frequencies
 *
 * This module handles Web Bluetooth API connection to PEMF devices.
 * Supports generic PEMF devices and can be extended for specific manufacturers.
 */

const PEMFBluetooth = {
    // Connection state
    device: null,
    server: null,
    service: null,
    characteristics: {},
    isConnected: false,
    isConnecting: false,

    // Device identification
    deviceInfo: {
        name: null,
        battery: null,
        firmware: null,
        manufacturer: null
    },

    // UUIDs for PEMF device services (generic - can be customized per device)
    UUIDS: {
        // Generic PEMF Service
        pemfService: '0000fff0-0000-1000-8000-00805f9b34fb',
        // Control characteristic (write frequency, intensity, waveform)
        controlChar: '0000fff1-0000-1000-8000-00805f9b34fb',
        // Status characteristic (read device status)
        statusChar: '0000fff2-0000-1000-8000-00805f9b34fb',
        // Notification characteristic (receive updates)
        notifyChar: '0000fff3-0000-1000-8000-00805f9b34fb',
        // Battery service (standard)
        batteryService: '0000180f-0000-1000-8000-00805f9b34fb',
        batteryLevel: '00002a19-0000-1000-8000-00805f9b34fb',
        // Device Info service (standard)
        deviceInfoService: '0000180a-0000-1000-8000-00805f9b34fb',
        firmwareRevision: '00002a26-0000-1000-8000-00805f9b34fb',
        manufacturerName: '00002a29-0000-1000-8000-00805f9b34fb'
    },

    // Event callbacks
    callbacks: {
        onConnect: null,
        onDisconnect: null,
        onStatusUpdate: null,
        onError: null,
        onBatteryUpdate: null
    },

    /**
     * Check if Web Bluetooth is supported
     */
    isSupported() {
        return 'bluetooth' in navigator;
    },

    /**
     * Request and connect to a PEMF device
     */
    async connect() {
        if (!this.isSupported()) {
            this.handleError('Web Bluetooth is not supported in this browser. Please use Chrome, Edge, or Opera.');
            return false;
        }

        if (this.isConnecting) {
            console.log('Connection already in progress');
            return false;
        }

        this.isConnecting = true;
        this.updateConnectionStatus('connecting');

        try {
            // Request device with PEMF-related services
            this.device = await navigator.bluetooth.requestDevice({
                filters: [
                    // Filter by name patterns common in PEMF devices
                    { namePrefix: 'PEMF' },
                    { namePrefix: 'Pulse' },
                    { namePrefix: 'Magnetic' },
                    { namePrefix: 'EMF' },
                    { namePrefix: 'Therapy' }
                ],
                optionalServices: [
                    this.UUIDS.pemfService,
                    this.UUIDS.batteryService,
                    this.UUIDS.deviceInfoService
                ],
                // Accept any device if filters don't match
                acceptAllDevices: false
            }).catch(async () => {
                // If no device matches filters, try accepting all devices
                return await navigator.bluetooth.requestDevice({
                    acceptAllDevices: true,
                    optionalServices: [
                        this.UUIDS.pemfService,
                        this.UUIDS.batteryService,
                        this.UUIDS.deviceInfoService
                    ]
                });
            });

            if (!this.device) {
                throw new Error('No device selected');
            }

            console.log('Device selected:', this.device.name);
            this.deviceInfo.name = this.device.name || 'Unknown PEMF Device';

            // Listen for disconnection
            this.device.addEventListener('gattserverdisconnected', () => {
                this.handleDisconnect();
            });

            // Connect to GATT server
            this.server = await this.device.gatt.connect();
            console.log('Connected to GATT server');

            // Try to get services
            await this.discoverServices();

            this.isConnected = true;
            this.isConnecting = false;
            this.updateConnectionStatus('connected');

            if (this.callbacks.onConnect) {
                this.callbacks.onConnect(this.deviceInfo);
            }

            return true;

        } catch (error) {
            this.isConnecting = false;
            this.handleError('Connection failed: ' + error.message);
            this.updateConnectionStatus('disconnected');
            return false;
        }
    },

    /**
     * Discover and setup device services
     */
    async discoverServices() {
        try {
            // Try to get PEMF service
            try {
                this.service = await this.server.getPrimaryService(this.UUIDS.pemfService);
                console.log('PEMF service found');

                // Get control characteristic
                try {
                    this.characteristics.control = await this.service.getCharacteristic(this.UUIDS.controlChar);
                    console.log('Control characteristic found');
                } catch (e) {
                    console.log('Control characteristic not found');
                }

                // Get status characteristic
                try {
                    this.characteristics.status = await this.service.getCharacteristic(this.UUIDS.statusChar);
                    console.log('Status characteristic found');
                } catch (e) {
                    console.log('Status characteristic not found');
                }

                // Get notification characteristic
                try {
                    this.characteristics.notify = await this.service.getCharacteristic(this.UUIDS.notifyChar);
                    await this.characteristics.notify.startNotifications();
                    this.characteristics.notify.addEventListener('characteristicvaluechanged', (event) => {
                        this.handleNotification(event.target.value);
                    });
                    console.log('Notifications enabled');
                } catch (e) {
                    console.log('Notification characteristic not found');
                }
            } catch (e) {
                console.log('PEMF service not found - device may use different UUIDs');
            }

            // Try to get battery level
            try {
                const batteryService = await this.server.getPrimaryService(this.UUIDS.batteryService);
                const batteryChar = await batteryService.getCharacteristic(this.UUIDS.batteryLevel);
                const batteryValue = await batteryChar.readValue();
                this.deviceInfo.battery = batteryValue.getUint8(0) + '%';

                // Subscribe to battery updates
                await batteryChar.startNotifications();
                batteryChar.addEventListener('characteristicvaluechanged', (event) => {
                    this.deviceInfo.battery = event.target.value.getUint8(0) + '%';
                    if (this.callbacks.onBatteryUpdate) {
                        this.callbacks.onBatteryUpdate(this.deviceInfo.battery);
                    }
                });
            } catch (e) {
                this.deviceInfo.battery = 'N/A';
            }

            // Try to get device info
            try {
                const deviceInfoService = await this.server.getPrimaryService(this.UUIDS.deviceInfoService);

                try {
                    const firmwareChar = await deviceInfoService.getCharacteristic(this.UUIDS.firmwareRevision);
                    const firmwareValue = await firmwareChar.readValue();
                    this.deviceInfo.firmware = new TextDecoder().decode(firmwareValue);
                } catch (e) {
                    this.deviceInfo.firmware = 'N/A';
                }

                try {
                    const manufacturerChar = await deviceInfoService.getCharacteristic(this.UUIDS.manufacturerName);
                    const manufacturerValue = await manufacturerChar.readValue();
                    this.deviceInfo.manufacturer = new TextDecoder().decode(manufacturerValue);
                } catch (e) {
                    this.deviceInfo.manufacturer = 'Unknown';
                }
            } catch (e) {
                this.deviceInfo.firmware = 'N/A';
                this.deviceInfo.manufacturer = 'Unknown';
            }

        } catch (error) {
            console.error('Error discovering services:', error);
        }
    },

    /**
     * Disconnect from device
     */
    disconnect() {
        if (this.device && this.device.gatt.connected) {
            this.device.gatt.disconnect();
        }
        this.handleDisconnect();
    },

    /**
     * Handle disconnection
     */
    handleDisconnect() {
        this.isConnected = false;
        this.isConnecting = false;
        this.device = null;
        this.server = null;
        this.service = null;
        this.characteristics = {};
        this.deviceInfo = {
            name: null,
            battery: null,
            firmware: null,
            manufacturer: null
        };

        this.updateConnectionStatus('disconnected');

        if (this.callbacks.onDisconnect) {
            this.callbacks.onDisconnect();
        }
    },

    /**
     * Send control command to device
     * @param {number} frequency - Frequency in Hz
     * @param {number} intensity - Intensity 0-100
     * @param {string} waveform - Waveform type
     * @param {boolean} active - Start/stop
     */
    async sendCommand(frequency, intensity, waveform, active) {
        if (!this.isConnected) {
            console.log('Not connected to device');
            return false;
        }

        // Encode waveform type
        const waveformCodes = {
            'sine': 0x01,
            'square': 0x02,
            'sawtooth': 0x03,
            'pulse': 0x04
        };

        // Create command packet
        // Format: [CMD, FREQ_HIGH, FREQ_LOW, INTENSITY, WAVEFORM, ACTIVE]
        const freqInt = Math.round(frequency * 100); // Encode as fixed-point
        const packet = new Uint8Array([
            0x01, // Command type: SET_PARAMS
            (freqInt >> 8) & 0xFF, // Frequency high byte
            freqInt & 0xFF, // Frequency low byte
            Math.round(intensity), // Intensity 0-100
            waveformCodes[waveform] || 0x01, // Waveform type
            active ? 0x01 : 0x00 // Active flag
        ]);

        if (this.characteristics.control) {
            try {
                await this.characteristics.control.writeValue(packet);
                console.log('Command sent:', { frequency, intensity, waveform, active });
                return true;
            } catch (error) {
                this.handleError('Failed to send command: ' + error.message);
                return false;
            }
        } else {
            // Simulate command if no real characteristic
            console.log('Simulated command:', { frequency, intensity, waveform, active });
            return true;
        }
    },

    /**
     * Start PEMF output
     */
    async start(frequency, intensity, waveform) {
        return await this.sendCommand(frequency, intensity, waveform, true);
    },

    /**
     * Stop PEMF output
     */
    async stop() {
        return await this.sendCommand(0, 0, 'sine', false);
    },

    /**
     * Update frequency during session
     */
    async setFrequency(frequency) {
        if (!this.isConnected) return false;

        // Send frequency update command
        const freqInt = Math.round(frequency * 100);
        const packet = new Uint8Array([
            0x02, // Command type: SET_FREQUENCY
            (freqInt >> 8) & 0xFF,
            freqInt & 0xFF
        ]);

        if (this.characteristics.control) {
            try {
                await this.characteristics.control.writeValue(packet);
                return true;
            } catch (error) {
                console.error('Failed to update frequency:', error);
                return false;
            }
        }
        return true;
    },

    /**
     * Update intensity during session
     */
    async setIntensity(intensity) {
        if (!this.isConnected) return false;

        const packet = new Uint8Array([
            0x03, // Command type: SET_INTENSITY
            Math.round(intensity)
        ]);

        if (this.characteristics.control) {
            try {
                await this.characteristics.control.writeValue(packet);
                return true;
            } catch (error) {
                console.error('Failed to update intensity:', error);
                return false;
            }
        }
        return true;
    },

    /**
     * Read device status
     */
    async readStatus() {
        if (!this.isConnected || !this.characteristics.status) {
            return null;
        }

        try {
            const value = await this.characteristics.status.readValue();
            return this.parseStatus(value);
        } catch (error) {
            console.error('Failed to read status:', error);
            return null;
        }
    },

    /**
     * Parse status data from device
     */
    parseStatus(dataView) {
        try {
            return {
                isActive: dataView.getUint8(0) === 0x01,
                frequency: dataView.getUint16(1) / 100,
                intensity: dataView.getUint8(3),
                waveform: dataView.getUint8(4),
                temperature: dataView.getUint8(5), // Device temperature
                runtime: dataView.getUint16(6) // Current session runtime in seconds
            };
        } catch (error) {
            return null;
        }
    },

    /**
     * Handle notification from device
     */
    handleNotification(dataView) {
        const status = this.parseStatus(dataView);
        if (status && this.callbacks.onStatusUpdate) {
            this.callbacks.onStatusUpdate(status);
        }
    },

    /**
     * Handle errors
     */
    handleError(message) {
        console.error('Bluetooth Error:', message);
        if (this.callbacks.onError) {
            this.callbacks.onError(message);
        }
    },

    /**
     * Update UI connection status
     */
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connectionStatus');
        if (!statusElement) return;

        const dot = statusElement.querySelector('.status-dot');
        const text = statusElement.querySelector('.status-text');

        dot.className = 'status-dot ' + status;

        const statusTexts = {
            'connected': 'Connected',
            'connecting': 'Connecting...',
            'disconnected': 'Disconnected'
        };

        text.textContent = statusTexts[status] || 'Unknown';
    },

    /**
     * Register event callback
     */
    on(event, callback) {
        if (this.callbacks.hasOwnProperty('on' + event.charAt(0).toUpperCase() + event.slice(1))) {
            this.callbacks['on' + event.charAt(0).toUpperCase() + event.slice(1)] = callback;
        }
    },

    /**
     * Simulate device for testing (when no real device available)
     */
    simulateDevice() {
        this.isConnected = true;
        this.deviceInfo = {
            name: 'Simulated PEMF Device',
            battery: '85%',
            firmware: 'v1.0.0 (Simulated)',
            manufacturer: 'Reality Forge'
        };

        this.updateConnectionStatus('connected');

        if (this.callbacks.onConnect) {
            this.callbacks.onConnect(this.deviceInfo);
        }

        console.log('Simulated device connected');
        return true;
    }
};

// Make available globally
window.PEMFBluetooth = PEMFBluetooth;
