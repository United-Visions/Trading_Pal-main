class AccountManager {
    constructor() {
        this.balanceElement = document.getElementById('user-balance');
        this.leverageElement = document.getElementById('user-leverage');
        this.openPositionsElement = document.getElementById('user-open-positions');
        this.openTradesElement = document.getElementById('user-open-trades');
        this.availableMarginElement = document.getElementById('user-available-margin');
        this.plElement = document.getElementById('user-pl');
        
        this.startAccountUpdates();
    }

    async updateAccountDetails() {
        try {
            const response = await axios.get('/api/v1/account_details');
            const accountData = response.data;

            if (accountData.error) {
                console.error('Error fetching account details:', accountData.error);
                return;
            }

            const account = accountData.account;
            
            // Update DOM elements with account information
            this.balanceElement.textContent = `Balance: ${account.balance}`;
            this.leverageElement.textContent = `Leverage: ${account.marginRate}`;
            this.openPositionsElement.textContent = `Open Positions: ${account.openPositionCount}`;
            this.openTradesElement.textContent = `Open Trades: ${account.openTradeCount}`;
            this.availableMarginElement.textContent = `Available Margin: ${account.marginAvailable}`;
            this.plElement.textContent = `Profit/Loss: ${account.pl}`;

        } catch (error) {
            console.error('Error updating account details:', error);
        }
    }

    startAccountUpdates() {
        // Initial update
        this.updateAccountDetails();
        
        // Update every minute
        setInterval(() => this.updateAccountDetails(), 600000);
    }
}

// Initialize account manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.accountManager = new AccountManager();
});
