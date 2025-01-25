class AccountManager {
    constructor() {
        this.balanceElement = document.getElementById('user-balance');
        this.leverageElement = document.getElementById('user-leverage');
        this.positionsElement = document.getElementById('user-open-positions');
        this.tradesElement = document.getElementById('user-open-trades');
        this.marginElement = document.getElementById('user-available-margin');
        this.plElement = document.getElementById('user-pl');
        
        // Initialize broker toggle handlers
        this.brokerToggles = document.querySelectorAll('.broker-toggle');
        this.currentBroker = localStorage.getItem('selectedBroker') || 'oanda';
        
        // Initialize settings modal
        this.settingsModal = document.getElementById('settings-modal');
        this.settingsBtn = document.getElementById('settings-btn');
        this.closeSettingsBtn = document.getElementById('close-settings');
        
        this.initializeEventListeners();
        this.loadAccountDetails();
        
        // Set up auto-refresh every 30 seconds
        setInterval(() => this.loadAccountDetails(), 30000);
    }

    initializeEventListeners() {
        // Broker toggle listeners
        this.brokerToggles.forEach(toggle => {
            toggle.addEventListener('click', () => {
                const broker = toggle.id.split('-')[0];
                this.switchBroker(broker);
            });
        });

        // Settings modal listeners
        this.settingsBtn.addEventListener('click', () => {
            this.settingsModal.classList.remove('hidden');
            this.settingsModal.classList.add('flex');
        });

        this.closeSettingsBtn.addEventListener('click', () => {
            this.settingsModal.classList.add('hidden');
            this.settingsModal.classList.remove('flex');
        });

        // Close modal when clicking outside
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) {
                this.settingsModal.classList.add('hidden');
                this.settingsModal.classList.remove('flex');
            }
        });
    }

    async switchBroker(broker) {
        if (broker !== this.currentBroker) {
            this.currentBroker = broker;
            localStorage.setItem('selectedBroker', broker);
            this.updateBrokerToggle();
            await this.loadAccountDetails();
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

    async loadAccountDetails() {
        try {
            const response = await axios.get('/api/v1/account_details');
            const data = response.data.account;
            
            if (data) {
                this.balanceElement.textContent = `Balance: ${parseFloat(data.balance).toFixed(2)} USD`;
                this.leverageElement.textContent = `Leverage: ${data.marginRate || 'N/A'}`;
                this.positionsElement.textContent = `Open Positions: ${data.openPositionCount || 0}`;
                this.tradesElement.textContent = `Open Trades: ${data.openTradeCount || 0}`;
                this.marginElement.textContent = `Available Margin: ${parseFloat(data.marginAvailable).toFixed(2)} USD`;
                this.plElement.textContent = `Profit/Loss: ${parseFloat(data.pl).toFixed(2)} USD`;
            }
        } catch (error) {
            console.error('Failed to load account details:', error);
            this.displayError('Please configure your broker settings');
            this.settingsModal.classList.remove('hidden');
            this.settingsModal.classList.add('flex');
        }
    }

    displayError(message) {
        this.balanceElement.textContent = 'Balance: --';
        this.leverageElement.textContent = 'Leverage: --';
        this.positionsElement.textContent = 'Open Positions: --';
        this.tradesElement.textContent = 'Open Trades: --';
        this.marginElement.textContent = 'Available Margin: --';
        this.plElement.textContent = 'Profit/Loss: --';
        
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
