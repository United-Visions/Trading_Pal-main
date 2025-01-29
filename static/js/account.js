class AccountManager {
    constructor() {
        console.group('AccountManager Initialization');
        console.log('Starting AccountManager initialization...');
        
        this.currentBroker = localStorage.getItem('selectedBroker') || 'oanda';
        console.log('Initial broker:', this.currentBroker);
        
        // Update element IDs to match HTML
        this.accountStatusElement = document.getElementById('broker-badge');
        this.accountBalanceElement = document.getElementById('user-balance');
        this.plElement = document.getElementById('user-pl');
        this.positionsElement = document.getElementById('user-open-positions');
        this.marginElement = document.getElementById('user-available-margin');
        this.loadingIndicator = document.getElementById('loading-indicator');
        
        // Log DOM element availability
        console.log('DOM Elements loaded:', {
            accountStatus: !!this.accountStatusElement,
            accountBalance: !!this.accountBalanceElement,
            pl: !!this.plElement,
            positions: !!this.positionsElement,
            margin: !!this.marginElement,
            loadingIndicator: !!this.loadingIndicator
        });
        
        // Initialize broker toggles
        this.brokerToggles = {
            oanda: document.getElementById('oanda-toggle'),
            alpaca: document.getElementById('alpaca-toggle')
        };
        
        console.log('Broker toggles initialized:', {
            oanda: !!this.brokerToggles.oanda,
            alpaca: !!this.brokerToggles.alpaca
        });
        
        this.initialize();
        console.groupEnd();
    }

    initialize() {
        // Load initial account details
        this.loadAccountDetails();
        
        // Set up broker toggle listeners
        Object.keys(this.brokerToggles).forEach(broker => {
            if (this.brokerToggles[broker]) {
                this.brokerToggles[broker].addEventListener('click', () => {
                    this.switchBroker(broker);
                });
            }
        });
    }

    async switchBroker(broker) {
        console.group(`Switching Broker to ${broker}`);
        console.time('brokerSwitch');
        
        try {
            console.log(`Current broker: ${this.currentBroker}, New broker: ${broker}`);
            
            this.currentBroker = broker;
            localStorage.setItem('selectedBroker', broker);
            console.log('Local storage updated');
            
            this.updateBrokerToggles();
            console.log('Broker toggles updated');
            
            await this.loadAccountDetails();
            console.log('Account details reloaded for new broker');
            
        } catch (error) {
            console.error('Broker switch failed:', {
                error: error,
                targetBroker: broker,
                currentState: {
                    currentBroker: this.currentBroker,
                    accountDetails: this.accountDetails
                }
            });
            this.showError(`Failed to switch to ${broker}: ${error.message}`);
        } finally {
            console.timeEnd('brokerSwitch');
            console.groupEnd();
        }
    }

    updateBrokerToggles() {
        Object.keys(this.brokerToggles).forEach(broker => {
            const toggle = this.brokerToggles[broker];
            if (toggle) {
                toggle.classList.toggle('active', broker === this.currentBroker);
                toggle.classList.toggle('bg-trading-accent', broker === this.currentBroker);
            }
        });
    }

    showError(message) {
        const notification = document.createElement('div');
        notification.className = 'fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg z-50';
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 5000);
    }

    async loadAccountDetails() {
        console.group(`Loading Account Details for ${this.currentBroker}`);
        console.time('accountDetailsLoad');
        
        try {
            console.log('Fetching account details...');
            this.showLoading();
            
            const response = await axios.get(`/api/v1/account_details?broker=${this.currentBroker}`);
            console.log('Server response:', response.data);
            
            if (response.data.error) {
                if (response.data.need_configuration) {
                    console.log('Broker needs configuration');
                    if (window.userConfigManager) {
                        window.userConfigManager.showModal();
                    }
                }
                throw new Error(response.data.error);
            }
            
            this.accountDetails = response.data.account;
            console.log('Account details received:', this.accountDetails);
            
            this.updateAccountDisplay();
            console.log('Account display updated successfully');
            
        } catch (error) {
            console.error('Failed to load account details:', {
                error: error,
                message: error.message,
                broker: this.currentBroker,
                timestamp: new Date().toISOString()
            });
            this.showError(error.response?.data?.error || error.message);
            
            // Clear account details if load failed
            this.accountDetails = null;
            this.updateAccountDisplay();
        } finally {
            this.hideLoading();
            console.timeEnd('accountDetailsLoad');
            console.groupEnd();
        }
    }

    updateAccountDisplay() {
        console.group('Updating Account Display');
        console.log('Current account details:', this.accountDetails);
        
        if (!this.accountDetails) {
            console.warn('No account details available');
            console.groupEnd();
            return;
        }

        try {
            // Update broker badge
            if (this.accountStatusElement) {
                const status = this.currentBroker.toUpperCase();
                console.log('Updating broker badge:', status);
                this.accountStatusElement.textContent = status;
            }

            // Update balance
            if (this.accountBalanceElement) {
                let balance = '';
                if (this.currentBroker === 'oanda') {
                    balance = `${this.accountDetails.account?.balance || 0} ${this.accountDetails.account?.currency || 'USD'}`;
                } else if (this.currentBroker === 'alpaca') {
                    balance = `$${parseFloat(this.accountDetails.balance || 0).toFixed(2)}`;
                }
                console.log('Updating balance:', balance);
                this.accountBalanceElement.textContent = balance;
            }

            // Update P/L
            if (this.plElement) {
                const pl = this.currentBroker === 'oanda' 
                    ? this.accountDetails.account?.pl || '0.00'
                    : this.accountDetails.pl || '0.00';
                this.plElement.textContent = `$${parseFloat(pl).toFixed(2)}`;
            }

            // Update positions count
            if (this.positionsElement) {
                const positions = this.currentBroker === 'oanda'
                    ? this.accountDetails.account?.openPositionCount || 0
                    : this.accountDetails.openPositionCount || 0;
                this.positionsElement.textContent = positions;
            }

            // Update margin
            if (this.marginElement) {
                const margin = this.currentBroker === 'oanda'
                    ? this.accountDetails.account?.marginAvailable || 0
                    : this.accountDetails.marginAvailable || 0;
                this.marginElement.textContent = `$${parseFloat(margin).toFixed(2)}`;
            }
        } catch (error) {
            console.error('Error updating account display:', error);
        }
        
        console.groupEnd();
    }

    showLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.remove('hidden');
        }
    }

    hideLoading() {
        if (this.loadingIndicator) {
            this.loadingIndicator.classList.add('hidden');
        }
    }
}

// Initialize account manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.accountManager = new AccountManager();
});
