/**
 * PEMF Forge - Authentication & Cloud Sync Module
 * Domain: 07_TRANSCEND - Consciousness & Frequencies
 *
 * Handles user authentication, profile management, and
 * cross-device data synchronization for Android & iOS.
 */

const PEMFAuth = {
    // Current user state
    currentUser: null,
    isAuthenticated: false,

    // API Configuration (configure with your backend)
    API_BASE: 'https://api.pemfforge.app', // Replace with your API

    // Storage keys
    STORAGE_KEYS: {
        user: 'pemf_user',
        token: 'pemf_auth_token',
        refreshToken: 'pemf_refresh_token',
        lastSync: 'pemf_last_sync'
    },

    // Event callbacks
    callbacks: {
        onLogin: null,
        onLogout: null,
        onSyncStart: null,
        onSyncComplete: null,
        onSyncError: null
    },

    /**
     * Initialize authentication
     */
    init() {
        this.loadStoredUser();
        this.setupEventListeners();
        this.checkAuthState();
        this.setupPWA();
    },

    /**
     * Setup form event listeners
     */
    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.auth-tab').forEach(tab => {
            tab.addEventListener('click', () => this.switchTab(tab.dataset.tab));
        });

        // Login form
        document.getElementById('loginForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.login();
        });

        // Signup form
        document.getElementById('signupForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.signup();
        });

        // Forgot password form
        document.getElementById('forgotForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.resetPassword();
        });

        // Forgot password link
        document.getElementById('forgotPassword')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showForgotForm();
        });

        // Back to login
        document.getElementById('backToLogin')?.addEventListener('click', () => {
            this.switchTab('login');
        });

        // Password visibility toggles
        document.querySelectorAll('.toggle-password').forEach(btn => {
            btn.addEventListener('click', (e) => this.togglePasswordVisibility(e.currentTarget));
        });

        // Password strength checker
        document.getElementById('signupPassword')?.addEventListener('input', (e) => {
            this.checkPasswordStrength(e.target.value);
        });

        // Social login buttons
        document.getElementById('googleLogin')?.addEventListener('click', () => this.socialLogin('google'));
        document.getElementById('googleSignup')?.addEventListener('click', () => this.socialLogin('google'));
        document.getElementById('appleLogin')?.addEventListener('click', () => this.socialLogin('apple'));
        document.getElementById('appleSignup')?.addEventListener('click', () => this.socialLogin('apple'));
    },

    /**
     * Switch between login/signup tabs
     */
    switchTab(tab) {
        // Update tabs
        document.querySelectorAll('.auth-tab').forEach(t => {
            t.classList.toggle('active', t.dataset.tab === tab);
        });

        // Update forms
        document.querySelectorAll('.auth-form').forEach(form => {
            form.classList.remove('active');
        });

        const formId = tab + 'Form';
        document.getElementById(formId)?.classList.add('active');
    },

    /**
     * Show forgot password form
     */
    showForgotForm() {
        document.querySelectorAll('.auth-form').forEach(form => form.classList.remove('active'));
        document.querySelectorAll('.auth-tab').forEach(tab => tab.classList.remove('active'));
        document.getElementById('forgotForm')?.classList.add('active');
    },

    /**
     * Toggle password visibility
     */
    togglePasswordVisibility(button) {
        const input = button.parentElement.querySelector('input');
        const eyeOpen = button.querySelector('.eye-open');
        const eyeClosed = button.querySelector('.eye-closed');

        if (input.type === 'password') {
            input.type = 'text';
            eyeOpen?.classList.add('hidden');
            eyeClosed?.classList.remove('hidden');
        } else {
            input.type = 'password';
            eyeOpen?.classList.remove('hidden');
            eyeClosed?.classList.add('hidden');
        }
    },

    /**
     * Check password strength
     */
    checkPasswordStrength(password) {
        const strengthFill = document.querySelector('.strength-fill');
        const strengthText = document.querySelector('.strength-text');

        if (!strengthFill || !strengthText) return;

        let strength = 0;
        let label = 'Too weak';

        // Length check
        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;

        // Character variety
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;

        // Update UI
        strengthFill.className = 'strength-fill';

        if (strength <= 1) {
            strengthFill.classList.add('weak');
            label = 'Weak';
        } else if (strength <= 2) {
            strengthFill.classList.add('fair');
            label = 'Fair';
        } else if (strength <= 3) {
            strengthFill.classList.add('good');
            label = 'Good';
        } else {
            strengthFill.classList.add('strong');
            label = 'Strong';
        }

        strengthText.textContent = label;
    },

    /**
     * Login with email/password
     */
    async login() {
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        const remember = document.getElementById('rememberMe').checked;

        if (!email || !password) {
            this.showToast('Please fill in all fields', 'error');
            return;
        }

        this.setLoading(true);

        try {
            // For demo: simulate API call
            // In production, replace with actual API call
            const response = await this.simulateLogin(email, password);

            if (response.success) {
                this.handleLoginSuccess(response.user, response.token, remember);
            } else {
                this.showToast(response.error || 'Login failed', 'error');
            }
        } catch (error) {
            this.showToast('Connection error. Please try again.', 'error');
            console.error('Login error:', error);
        } finally {
            this.setLoading(false);
        }
    },

    /**
     * Signup with email/password
     */
    async signup() {
        const name = document.getElementById('signupName').value;
        const email = document.getElementById('signupEmail').value;
        const password = document.getElementById('signupPassword').value;
        const confirm = document.getElementById('signupConfirm').value;
        const agreed = document.getElementById('agreeTerms').checked;

        // Validation
        if (!name || !email || !password || !confirm) {
            this.showToast('Please fill in all fields', 'error');
            return;
        }

        if (password !== confirm) {
            this.showToast('Passwords do not match', 'error');
            return;
        }

        if (password.length < 8) {
            this.showToast('Password must be at least 8 characters', 'error');
            return;
        }

        if (!agreed) {
            this.showToast('Please agree to the Terms of Service', 'error');
            return;
        }

        this.setLoading(true);

        try {
            // For demo: simulate API call
            const response = await this.simulateSignup(name, email, password);

            if (response.success) {
                this.handleLoginSuccess(response.user, response.token, true);
            } else {
                this.showToast(response.error || 'Signup failed', 'error');
            }
        } catch (error) {
            this.showToast('Connection error. Please try again.', 'error');
            console.error('Signup error:', error);
        } finally {
            this.setLoading(false);
        }
    },

    /**
     * Reset password
     */
    async resetPassword() {
        const email = document.getElementById('resetEmail').value;

        if (!email) {
            this.showToast('Please enter your email', 'error');
            return;
        }

        this.setLoading(true);

        try {
            // Simulate API call
            await this.delay(1500);
            this.showToast('Password reset link sent to your email', 'success');
            this.switchTab('login');
        } catch (error) {
            this.showToast('Error sending reset link', 'error');
        } finally {
            this.setLoading(false);
        }
    },

    /**
     * Social login (Google/Apple)
     */
    async socialLogin(provider) {
        this.setLoading(true);

        try {
            if (provider === 'google') {
                // In production: implement Google OAuth
                // For demo: simulate
                const response = await this.simulateSocialLogin('google');
                if (response.success) {
                    this.handleLoginSuccess(response.user, response.token, true);
                }
            } else if (provider === 'apple') {
                // In production: implement Apple Sign-In
                // For demo: simulate
                const response = await this.simulateSocialLogin('apple');
                if (response.success) {
                    this.handleLoginSuccess(response.user, response.token, true);
                }
            }
        } catch (error) {
            this.showToast(`${provider} login failed`, 'error');
            console.error('Social login error:', error);
        } finally {
            this.setLoading(false);
        }
    },

    /**
     * Handle successful login
     */
    handleLoginSuccess(user, token, remember) {
        this.currentUser = user;
        this.isAuthenticated = true;

        // Store credentials
        if (remember) {
            localStorage.setItem(this.STORAGE_KEYS.user, JSON.stringify(user));
            localStorage.setItem(this.STORAGE_KEYS.token, token);
        } else {
            sessionStorage.setItem(this.STORAGE_KEYS.user, JSON.stringify(user));
            sessionStorage.setItem(this.STORAGE_KEYS.token, token);
        }

        this.showToast('Welcome back, ' + user.name + '!', 'success');

        // Trigger sync
        this.syncData();

        // Callback
        if (this.callbacks.onLogin) {
            this.callbacks.onLogin(user);
        }

        // Redirect to main app
        setTimeout(() => {
            window.location.href = 'index.html';
        }, 1000);
    },

    /**
     * Logout user
     */
    logout() {
        this.currentUser = null;
        this.isAuthenticated = false;

        // Clear storage
        Object.values(this.STORAGE_KEYS).forEach(key => {
            localStorage.removeItem(key);
            sessionStorage.removeItem(key);
        });

        if (this.callbacks.onLogout) {
            this.callbacks.onLogout();
        }

        this.showToast('Logged out successfully', 'success');

        // Redirect to login
        window.location.href = 'login.html';
    },

    /**
     * Load stored user on init
     */
    loadStoredUser() {
        const storedUser = localStorage.getItem(this.STORAGE_KEYS.user) ||
                          sessionStorage.getItem(this.STORAGE_KEYS.user);
        const token = localStorage.getItem(this.STORAGE_KEYS.token) ||
                     sessionStorage.getItem(this.STORAGE_KEYS.token);

        if (storedUser && token) {
            try {
                this.currentUser = JSON.parse(storedUser);
                this.isAuthenticated = true;
            } catch (e) {
                console.error('Error parsing stored user:', e);
            }
        }
    },

    /**
     * Check auth state and redirect if needed
     */
    checkAuthState() {
        const isLoginPage = window.location.pathname.includes('login.html');

        if (this.isAuthenticated && isLoginPage) {
            // Already logged in, redirect to app
            window.location.href = 'index.html';
        }
    },

    /**
     * Sync data with cloud
     */
    async syncData() {
        if (!this.isAuthenticated) return;

        if (this.callbacks.onSyncStart) {
            this.callbacks.onSyncStart();
        }

        try {
            // Get local data
            const localHistory = localStorage.getItem('pemf_session_history');
            const localProtocols = localStorage.getItem('pemf_custom_protocols');
            const localSettings = localStorage.getItem('pemf_settings');

            // In production: sync with API
            // For demo: simulate sync
            await this.delay(1000);

            // Update last sync time
            localStorage.setItem(this.STORAGE_KEYS.lastSync, new Date().toISOString());

            if (this.callbacks.onSyncComplete) {
                this.callbacks.onSyncComplete();
            }

            console.log('Data synced successfully');
        } catch (error) {
            console.error('Sync error:', error);
            if (this.callbacks.onSyncError) {
                this.callbacks.onSyncError(error);
            }
        }
    },

    /**
     * Get sync status
     */
    getSyncStatus() {
        const lastSync = localStorage.getItem(this.STORAGE_KEYS.lastSync);
        if (!lastSync) return { synced: false, lastSync: null };

        return {
            synced: true,
            lastSync: new Date(lastSync),
            timeAgo: this.getTimeAgo(new Date(lastSync))
        };
    },

    /**
     * Get time ago string
     */
    getTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);

        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return Math.floor(seconds / 60) + ' min ago';
        if (seconds < 86400) return Math.floor(seconds / 3600) + ' hours ago';
        return Math.floor(seconds / 86400) + ' days ago';
    },

    // ==================== Simulation Methods (Replace with real API) ====================

    /**
     * Simulate login API call
     */
    async simulateLogin(email, password) {
        await this.delay(1500);

        // Demo: accept any email with password "demo1234"
        if (password === 'demo1234' || password.length >= 8) {
            return {
                success: true,
                user: {
                    id: 'user_' + Date.now(),
                    email: email,
                    name: email.split('@')[0],
                    avatar: null,
                    createdAt: new Date().toISOString()
                },
                token: 'demo_token_' + Math.random().toString(36).substr(2)
            };
        }

        return {
            success: false,
            error: 'Invalid email or password'
        };
    },

    /**
     * Simulate signup API call
     */
    async simulateSignup(name, email, password) {
        await this.delay(1500);

        return {
            success: true,
            user: {
                id: 'user_' + Date.now(),
                email: email,
                name: name,
                avatar: null,
                createdAt: new Date().toISOString()
            },
            token: 'demo_token_' + Math.random().toString(36).substr(2)
        };
    },

    /**
     * Simulate social login
     */
    async simulateSocialLogin(provider) {
        await this.delay(1500);

        return {
            success: true,
            user: {
                id: 'user_' + Date.now(),
                email: `demo@${provider}.com`,
                name: `${provider.charAt(0).toUpperCase() + provider.slice(1)} User`,
                avatar: null,
                provider: provider,
                createdAt: new Date().toISOString()
            },
            token: 'demo_token_' + Math.random().toString(36).substr(2)
        };
    },

    // ==================== Utility Methods ====================

    /**
     * Show loading state
     */
    setLoading(loading) {
        const buttons = document.querySelectorAll('.auth-submit-btn, .social-btn');
        buttons.forEach(btn => {
            btn.disabled = loading;
            if (loading) {
                btn.style.opacity = '0.7';
            } else {
                btn.style.opacity = '1';
            }
        });
    },

    /**
     * Delay helper
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    /**
     * Show toast notification
     */
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
    },

    /**
     * Register event callback
     */
    on(event, callback) {
        const key = 'on' + event.charAt(0).toUpperCase() + event.slice(1);
        if (this.callbacks.hasOwnProperty(key)) {
            this.callbacks[key] = callback;
        }
    },

    // ==================== PWA Support ====================

    /**
     * Setup PWA install prompt
     */
    setupPWA() {
        let deferredPrompt;

        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;

            // Show install banner
            const banner = document.getElementById('installBanner');
            if (banner) {
                banner.classList.remove('hidden');
            }
        });

        document.getElementById('installBtn')?.addEventListener('click', async () => {
            if (deferredPrompt) {
                deferredPrompt.prompt();
                const { outcome } = await deferredPrompt.userChoice;
                console.log('Install outcome:', outcome);
                deferredPrompt = null;
                document.getElementById('installBanner')?.classList.add('hidden');
            }
        });

        document.getElementById('dismissInstall')?.addEventListener('click', () => {
            document.getElementById('installBanner')?.classList.add('hidden');
        });
    }
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    PEMFAuth.init();
});

// Make available globally
window.PEMFAuth = PEMFAuth;
