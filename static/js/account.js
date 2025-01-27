class AccountManager {
    constructor() {
        this.accountElements = {
            balance: document.getElementById('user-balance'),
            leverage: document.getElementById('user-leverage'),
            positions: document.getElementById('user-open-positions'),
            trades: document.getElementById('user-open-trades'),
            margin: document.getElementById('user-available-margin'),
            pl: document.getElementById('user-pl')
        };
        
        // Initialize broker toggles with animation support
        this.brokerToggles = document.querySelectorAll('.broker-toggle');
        this.currentBroker = localStorage.getItem('selectedBroker') || 'oanda';
        
        // Settings modal elements
        this.settingsModal = document.getElementById('settings-modal');
        this.settingsBtn = document.getElementById('settings-btn');
        this.closeSettingsBtn = document.getElementById('close-settings');
        
        this.initializeEventListeners();
        this.loadAccountDetails();
        
        // Auto-refresh with fade transition
        setInterval(() => this.loadAccountDetails(), 30000);
        
        this.checkSession();
        setInterval(() => this.checkSession(), 60000);
    }

    initializeEventListeners() {
        this.brokerToggles.forEach(toggle => {
            toggle.addEventListener('click', () => {
                const broker = toggle.id.split('-')[0];
                this.switchBroker(broker);
            });
        });

        this.settingsBtn.addEventListener('click', () => {
            gsap.to(this.settingsModal, {
                display: 'flex',
                opacity: 1,
                duration: 0.3,
                ease: 'power2.out'
            });
        });

        this.closeSettingsBtn.addEventListener('click', () => this.hideSettingsModal());
        
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) this.hideSettingsModal();
        });
    }

    hideSettingsModal() {
        gsap.to(this.settingsModal, {
            opacity: 0,
            duration: 0.3,
            ease: 'power2.in',
            onComplete: () => {
                this.settingsModal.style.display = 'none';
            }
        });
    }

    showLoading() {
        const loadingIndicator = document.getElementById('account-loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.classList.remove('hidden');
        }
    }

    hideLoading() {
        const loadingIndicator = document.getElementById('account-loading-indicator');
        if (loadingIndicator) {
            loadingIndicator.classList.add('hidden');
        }
    }

    async switchBroker(broker) {
        if (broker !== this.currentBroker) {
            this.showLoading();
            try {
                // Update UI first
                this.updateBrokerBadge(broker);
                this.clearAccountDetails();

                // Switch broker and load new details
                this.currentBroker = broker;
                localStorage.setItem('selectedBroker', broker);
                await this.loadAccountDetails();

                // Update broker toggle states
                this.updateBrokerToggles();

            } catch (error) {
                console.error('Error switching broker:', error);
                this.showError('Failed to switch broker');
            } finally {
                this.hideLoading();
            }
        }
    }

    updateBrokerBadge(broker) {
        const badge = document.getElementById('broker-badge');
        if (badge) {
            badge.textContent = broker.toUpperCase();
            badge.className = `px-2 py-0.5 text-xs rounded-full ${
                broker === 'oanda' ? 
                'bg-primary-500/20 text-primary-300' : 
                'bg-secondary-500/20 text-secondary-300'
            }`;
        }
    }

    clearAccountDetails() {
        Object.values(this.accountElements).forEach(el => {
            if (el) el.textContent = '--';
        });
    }

    async loadAccountDetails() {
        try {
            const response = await axios.get(`/api/v1/account_details?broker=${this.currentBroker}`);
            const data = response.data;
            
            if (data.error || !data.account) {
                throw new Error(data.error || 'Invalid account data');
            }

            this.updateAccountDisplay(data.account);
            
        } catch (error) {
            if (error.response?.data?.need_configuration) {
                this.displayError('Please configure your broker settings');
                gsap.to(this.settingsModal, {
                    display: 'flex',
                    opacity: 1,
                    duration: 0.3
                });
            } else {
                this.displayError(error.response?.data?.error || 'Failed to load account details');
            }
        }
    }

    updateAccountDisplay(data) {
        if (!data) return;

        const updateElement = (element, value, prefix = '', suffix = '') => {
            const currentValue = parseFloat(element.textContent.split(' ')[1]) || 0;
            const parsedValue = parseFloat(value);
            if (isNaN(parsedValue)) {
                element.textContent = `${prefix}--${suffix}`;
                return;
            }
            gsap.to({value: currentValue}, {
                value: parsedValue,
                duration: 1,
                ease: 'power2.out',
                onUpdate: function() {
                    element.textContent = `${prefix}${this.targets()[0].value.toFixed(2)}${suffix}`;
                }
            });
        };

        updateElement(this.accountElements.balance, data.balance, 'Balance: ', ' USD');
        updateElement(this.accountElements.leverage, data.marginRate || 0, 'Leverage: ', 'x');
        
        gsap.to(this.accountElements.positions, {
            textContent: `Open Positions: ${data.openPositionCount || 0}`,
            duration: 0.3,
            ease: 'power2.out'
        });
        
        gsap.to(this.accountElements.trades, {
            textContent: `Open Trades: ${data.openTradeCount || 0}`,
            duration: 0.3,
            ease: 'power2.out'
        });
        
        updateElement(this.accountElements.margin, data.marginAvailable, 'Available Margin: ', ' USD');
        updateElement(this.accountElements.pl, data.pl, 'Profit/Loss: ', ' USD');
    }

    async checkSession() {
        try {
            const response = await axios.get('/auth/session/check');
            if (response.data.authenticated) {
                if (response.data.selected_broker) {
                    this.currentBroker = response.data.selected_broker;
                    localStorage.setItem('selectedBroker', this.currentBroker);
                    this.updateBrokerToggle();
                }
                await this.loadAccountDetails();
            } else {
                window.location.href = '/auth/login';
            }
        } catch (error) {
            if (error.response?.status === 401) {
                window.location.href = '/auth/login';
            }
        }
    }

    displayError(message) {
        // Safely clear account values first
        if (this.accountElements) {
            Object.values(this.accountElements).forEach(element => {
                if (element && element.textContent) {
                    const label = element.textContent.split(':')[0] || '';
                    element.textContent = label ? `${label}: --` : '--';
                }
            });
        }
        
        // Show error notification
        const notification = document.createElement('div');
        notification.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }
}

// Initialize account manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.accountManager = new AccountManager();
});

// Make loadAccountDetails available globally for broker toggle
window.loadAccountDetails = () => window.accountManager.loadAccountDetails();
