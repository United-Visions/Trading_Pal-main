/**
 * User Configuration Management
 * Handles broker settings, modal interactions, and account initialization
 * @file /static/js/user_config.js
 */

class UserConfigManager {
    constructor() {
        // DOM Elements
        this.settingsModal = document.getElementById('settings-modal');
        this.settingsBtn = document.getElementById('settings-btn');
        this.closeSettings = document.getElementById('close-settings');
        this.brokerSelect = document.getElementById('broker-select');
        this.brokerSettingsForm = document.getElementById('broker-settings-form');
        this.saveSettingsBtn = document.getElementById('save-settings-btn');
        this.brokerToggles = document.querySelectorAll('.broker-toggle');
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.editBtn = document.getElementById('edit-settings');
        
        // State
        this.currentBroker = localStorage.getItem('selectedBroker') || 'oanda';
        this.isInitialized = false;
        this.isEditMode = false;
        this.inputFields = [
            'oanda-api-key',
            'oanda-account-id',
            'alpaca-api-key',
            'alpaca-api-secret'
        ];
        this.activeBrokers = new Set();
        
        // Bind methods
        this.handleSubmit = this.handleSubmit.bind(this);
        this.loadBrokerSettings = this.loadBrokerSettings.bind(this);
        this.updateBrokerToggle = this.updateBrokerToggle.bind(this);
        
        this.initialize();
    }

    initialize() {
        // Initialize event listeners
        this.initializeEventListeners();
        
        // Set initial state
        this.updateBrokerToggle();
        
        this.isInitialized = true;
        console.log('UserConfigManager initialized');
    }
    
    loadBrokerSettingsOnStartup() {
        this.loadBrokerSettings();
    }

    initializeEventListeners() {
        // Modal controls
        if (this.settingsBtn) {
            this.settingsBtn.addEventListener('click', () => {
                console.log('Opening settings modal');
                this.showModal();
            });
        }

        if (this.closeSettings) {
            this.closeSettings.addEventListener('click', () => {
                console.log('Closing settings modal');
                this.hideModal();
            });
        }

        // Broker selection
        if (this.brokerSelect) {
            this.brokerSelect.addEventListener('change', () => {
                const selectedBroker = this.brokerSelect.value;
                this.toggleBrokerFields(selectedBroker);
            });
        }

        // Form submission
        if (this.brokerSettingsForm) {
            this.brokerSettingsForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleSubmit(e);
            });
        }

        // Broker toggles
        this.brokerToggles.forEach(toggle => {
            toggle.addEventListener('click', async () => {
                const broker = toggle.id.split('-')[0];
                await this.switchBroker(broker);
            });
        });

        // Click outside modal to close
        window.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.hideModal();
            }
        });

        // Handle escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.settingsModal.classList.contains('hidden')) {
                this.hideModal();
            }
        });

        // Add edit button listener
        if (this.editBtn) {
            this.editBtn.addEventListener('click', () => {
                this.toggleEditMode();
            });
        }
    }

    showModal() {
        this.settingsModal.classList.remove('hidden');
        this.settingsModal.classList.add('flex');
        this.isEditMode = false;
        this.loadBrokerSettings();
        
        // Ensure inputs are disabled and save button is hidden initially
        this.inputFields.forEach(id => {
            const input = document.getElementById(id);
            if (input) input.disabled = true;
        });
        if (this.saveSettingsBtn) {
            this.saveSettingsBtn.style.display = 'none';
        }
    }

    hideModal() {
        this.settingsModal.classList.add('hidden');
        this.settingsModal.classList.remove('flex');
    }

    toggleBrokerFields(selectedBroker) {
        console.log(`Toggling fields for broker: ${selectedBroker}`);
        document.querySelectorAll('.oanda-fields, .alpaca-fields').forEach(el => {
            el.classList.add('hidden');
        });
        document.querySelector(`.${selectedBroker}-fields`).classList.remove('hidden');
    }

    async loadBrokerSettings() {
        console.log('Loading broker settings');
        this.showLoading();
        
        try {
            const response = await axios.get('/api/v1/broker/settings');
            const settings = response.data.settings;
            
            // Update fields for both brokers
            if (settings.oanda) {
                document.getElementById('oanda-api-key').value = settings.oanda.api_key;
                document.getElementById('oanda-account-id').value = settings.oanda.account_id;
            }
            
            if (settings.alpaca) {
                document.getElementById('alpaca-api-key').value = settings.alpaca.api_key;
                document.getElementById('alpaca-api-secret').value = settings.alpaca.api_secret;
            }
            
            // Update market badges
            this.updateMarketBadges(settings);
            if (window.accountManager && window.accountManagerInitialized) {
                window.accountManager.updateBrokerToggles();
            }
        } catch (error) {
            console.error('Failed to load broker settings:', error);
            this.showError('Failed to load broker settings');
        } finally {
            this.hideLoading();
        }
    }

    populateForm(settings) {
        if (settings.oanda) {
            document.getElementById('oanda-api-key').value = settings.oanda.api_key || '';
            document.getElementById('oanda-account-id').value = settings.oanda.account_id || '';
        }
        
        if (settings.alpaca) {
            document.getElementById('alpaca-api-key').value = settings.alpaca.api_key || '';
            document.getElementById('alpaca-api-secret').value = settings.alpaca.api_secret || '';
        }
    }

    async handleSubmit(e) {
        if (!this.isEditMode) {
            e.preventDefault();
            return;
        }
        console.log('Submitting broker settings');
        this.showLoading();
        
        const selectedBroker = this.brokerSelect.value;
        const settings = this.getFormData(selectedBroker);
        
        try {
            if (!this.validateSettings(settings)) {
                throw new Error('Please fill in all required fields');
            }
            
            const response = await axios.post('/api/v1/broker/settings', {
                broker_type: selectedBroker,
                settings: settings
            });
            
            console.log('Settings saved:', response.data);
            
            if (response.data.status === 'connected') {
                this.showSuccess('Settings saved and connected successfully');
                this.updateBrokerToggle();
                await this.reloadAccountDetails();
                setTimeout(() => this.hideModal(), 1500);
            } else {
                throw new Error(response.data.error || 'Failed to connect to broker');
            }
            
        } catch (error) {
            console.error('Failed to save settings:', error);
            this.showError(error.response?.data?.error || error.message);
        } finally {
            this.hideLoading();
        }
    }

    getFormData(selectedBroker) {
        let settings = {};
        
        if (selectedBroker === 'oanda') {
            settings = {
                api_key: document.getElementById('oanda-api-key').value,
                account_id: document.getElementById('oanda-account-id').value
            };
        } else {
            settings = {
                api_key: document.getElementById('alpaca-api-key').value,
                api_secret: document.getElementById('alpaca-api-secret').value
            };
        }
        
        return settings;
    }

    validateSettings(settings) {
        return Object.values(settings).every(value => value && value.trim() !== '');
    }

    async switchBroker(broker) {
        if (broker !== this.currentBroker) {
            console.log(`Switching broker to: ${broker}`);
            this.currentBroker = broker;
            localStorage.setItem('selectedBroker', broker);
            this.updateBrokerToggle();
            await this.reloadAccountDetails();
        }
    }

    updateBrokerToggle() {
        this.brokerToggles.forEach(toggle => {
            toggle.classList.remove('active', 'bg-trading-accent');
            if (toggle.id.includes(this.currentBroker)) {
                toggle.classList.add('active', 'bg-trading-accent');
            }
        });
    }

    updateBrokerToggles() {
        this.brokerToggles.forEach(toggle => {
            const brokerType = toggle.id.split('-')[0];
            const isConfigured = this.activeBrokers.has(brokerType);
            
            toggle.classList.toggle('opacity-50', !isConfigured);
            toggle.disabled = !isConfigured;
            
            if (brokerType === this.currentBroker) {
                toggle.classList.add('bg-primary-600');
            } else {
                toggle.classList.remove('bg-primary-600');
            }
        });
    }

    async reloadAccountDetails() {
        console.log('Reloading account details');
        if (window.accountManager) {
            await window.accountManager.loadAccountDetails();
        }
    }

    showLoading() {
        this.loadingIndicator.classList.remove('hidden');
    }

    hideLoading() {
        this.loadingIndicator.classList.add('hidden');
    }

    showError(message) {
        const notification = document.createElement('div');
        notification.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }

    showSuccess(message) {
        const notification = document.createElement('div');
        notification.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }

    updateConnectionStatus(broker, status) {
        const statusIndicator = document.createElement('div');
        statusIndicator.className = `text-sm ${status === 'connected' ? 'text-green-500' : 'text-red-500'}`;
        statusIndicator.textContent = `Status: ${status}`;
        this.brokerSettingsForm.insertBefore(statusIndicator, this.brokerSettingsForm.firstChild);
    }

    toggleEditMode() {
        this.isEditMode = !this.isEditMode;
        
        // Update UI elements
        this.editBtn.innerHTML = this.isEditMode ? 
            '<i class="fas fa-times"></i>' : 
            '<i class="fas fa-edit"></i>';
            
        // Enable/disable and show/hide fields based on broker type
        ['oanda', 'alpaca'].forEach(broker => {
            const fields = this.getBrokerFields(broker);
            fields.forEach(field => {
                const input = document.getElementById(field);
                if (input) {
                    input.disabled = !this.isEditMode;
                    if (this.isEditMode) {
                        input.type = 'text';  // Show actual values when editing
                    } else {
                        input.type = 'password';  // Mask when not editing
                    }
                }
            });
        });
        
        this.saveSettingsBtn.style.display = this.isEditMode ? 'block' : 'none';
    }

    getBrokerFields(broker) {
        return broker === 'oanda' ? 
            ['oanda-api-key', 'oanda-account-id'] :
            ['alpaca-api-key', 'alpaca-api-secret'];
    }

    updateMarketBadges(settings) {
        const badges = document.querySelectorAll('.market-badge');
        badges.forEach(badge => {
            const market = badge.dataset.market;
            const isSupported = this.isMarketSupported(market, settings);
            badge.classList.toggle('opacity-50', !isSupported);
        });
    }

    isMarketSupported(market, settings) {
        return Object.values(settings).some(config => 
            config.supported_markets?.includes(market)
        );
    }

    maskCredential(value) {
        if (!value) return '';
        return '•'.repeat(Math.min(value.length, 20));
    }
}

// Initialize user config manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.userConfigManager = new UserConfigManager();
    window.userConfigManager.loadBrokerSettingsOnStartup();
});

// Export for global access
window.loadBrokerSettings = () => window.userConfigManager.loadBrokerSettings();
