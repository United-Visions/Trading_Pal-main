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
        this.brokerToggles = document.querySelectorAll('.broker-toggle');
        this.loadingIndicator = document.getElementById('loading-indicator');
        
        // State
        this.currentBroker = localStorage.getItem('selectedBroker') || 'oanda';
        this.isInitialized = false;
        
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
        
        // Load settings on startup
        this.loadBrokerSettings();
        
        this.isInitialized = true;
        console.log('UserConfigManager initialized');
    }

    initializeEventListeners() {
        // Modal controls
        this.settingsBtn.addEventListener('click', () => {
            console.log('Opening settings modal');
            this.showModal();
        });

        this.closeSettings.addEventListener('click', () => {
            console.log('Closing settings modal');
            this.hideModal();
        });

        // Broker selection
        this.brokerSelect.addEventListener('change', () => {
            const selectedBroker = this.brokerSelect.value;
            this.toggleBrokerFields(selectedBroker);
        });

        // Form submission
        this.brokerSettingsForm.addEventListener('submit', this.handleSubmit);

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
    }

    showModal() {
        this.settingsModal.classList.remove('hidden');
        this.settingsModal.classList.add('flex');
        this.loadBrokerSettings();
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
            console.log('Broker settings loaded:', response.data);
            const settings = response.data;
            
            this.populateForm(settings);
            
            // Update connection status if available
            if (settings.status) {
                this.updateConnectionStatus(settings.status);
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
        e.preventDefault();
        console.log('Submitting broker settings');
        this.showLoading();
        
        const selectedBroker = this.brokerSelect.value;
        const settings = this.getFormData(selectedBroker);
        
        try {
            if (!this.validateSettings(settings)) {
                throw new Error('Please fill in all required fields');
            }
            
            const response = await axios.post('/api/v1/broker/settings', settings);
            console.log('Settings saved:', response.data);
            
            this.showSuccess('Settings saved successfully');
            
            // Update local state
            this.currentBroker = selectedBroker;
            localStorage.setItem('selectedBroker', selectedBroker);
            
            // Delay hide modal to show success message
            setTimeout(() => this.hideModal(), 1000);
            
            // Reload account details
            await this.reloadAccountDetails();
            
        } catch (error) {
            console.error('Failed to save settings:', error);
            this.showError(error.response?.data?.error || 'Failed to save settings');
        } finally {
            this.hideLoading();
        }
    }

    getFormData(selectedBroker) {
        return {
            broker_type: selectedBroker,
            settings: selectedBroker === 'oanda' ? {
                api_key: document.getElementById('oanda-api-key').value,
                account_id: document.getElementById('oanda-account-id').value
            } : {
                api_key: document.getElementById('alpaca-api-key').value,
                api_secret: document.getElementById('alpaca-api-secret').value
            }
        };
    }

    validateSettings(settings) {
        const { broker_type, settings: brokerSettings } = settings;
        
        if (broker_type === 'oanda') {
            return brokerSettings.api_key && brokerSettings.account_id;
        } else {
            return brokerSettings.api_key && brokerSettings.api_secret;
        }
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

    updateConnectionStatus(status) {
        const statusIndicator = document.createElement('div');
        statusIndicator.className = `text-sm ${status === 'connected' ? 'text-green-500' : 'text-red-500'}`;
        statusIndicator.textContent = `Status: ${status}`;
        this.brokerSettingsForm.insertBefore(statusIndicator, this.brokerSettingsForm.firstChild);
    }
}

// Initialize user config manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.userConfigManager = new UserConfigManager();
});

// Export for global access
window.loadBrokerSettings = () => window.userConfigManager.loadBrokerSettings();