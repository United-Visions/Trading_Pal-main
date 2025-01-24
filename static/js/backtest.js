class BacktestManager {
    constructor() {
        this.strategyForm = document.getElementById('strategyForm');
        this.strategyList = document.getElementById('strategyList');
        this.backtestResults = document.getElementById('backtestResults');
        this.assistantResponse = document.getElementById('assistantResponse');
        this.searchInput = document.getElementById('searchStrategies');
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.plotContainer = document.getElementById('plot-container');
        
        this.setupEventListeners();
        this.loadSavedStrategies();
        this.loadStrategyFromLocalStorage();
    }

    setupEventListeners() {
        this.strategyForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.searchInput.addEventListener('input', () => this.filterStrategies());
    }

    async loadSavedStrategies() {
        try {
            const response = await axios.get('/get_strategies');
            const strategies = response.data;
            
            this.strategyList.innerHTML = '';
            strategies.forEach(strategy => {
                const li = document.createElement('li');
                li.textContent = strategy.strategyName;
                li.addEventListener('click', () => this.loadStrategy(strategy));
                this.strategyList.appendChild(li);
            });
        } catch (error) {
            console.error('Error loading strategies:', error);
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        const formData = {
            strategyName: document.getElementById('strategyName').value,
            authorName: document.getElementById('authorName').value,
            strategyCode: document.getElementById('strategyCode').value,
            currencyPair: document.getElementById('currencyPair').value,
            timeFrame: document.getElementById('timeFrame').value
        };

        this.showLoadingIndicator();

        try {
            const response = await axios.post('/backtest_strategy', formData);
            const data = response.data;

            if (data.error) {
                this.backtestResults.innerHTML = `
                    <div class="text-red-500">Error: ${data.error}</div>
                `;
            } else {
                this.backtestResults.classList.remove('hidden');
                this.backtestResults.innerHTML = `
                    <h2 class="text-xl font-bold mb-4">Backtest Results</h2>
                    <ul class="space-y-2">
                        ${Object.entries(data.backtestResults).map(([key, value]) => 
                            `<li>${key}: ${value}</li>`
                        ).join('')}
                    </ul>
                `;

                // Update assistant response
                this.assistantResponse.textContent = data.gptResponse;

                // Display plot
                this.displayPlot(data.plotUrl);
            }
        } catch (error) {
            console.error('Error:', error);
            this.backtestResults.innerHTML = `
                <div class="text-red-500">Error: ${error.message}</div>
            `;
        } finally {
            this.hideLoadingIndicator();
        }
    }

    displayPlot(plotUrl) {
        this.plotContainer.innerHTML = `<img src="${plotUrl}" alt="Backtest Plot" class="w-full h-auto">`;
    }

    async executeStrategy(e) {
        e.preventDefault();
        const formData = {
            instrument: document.getElementById('currencyPair').value,
            granularity: document.getElementById('timeFrame').value,
            count: 1000,
            strategy_code: document.getElementById('strategyCode').value
        };

        this.showLoadingIndicator();

        try {
            const response = await axios.post('/api/v1/execute_strategy', formData);
            const data = response.data;

            if (data.error) {
                this.backtestResults.innerHTML = `
                    <div class="text-red-500">Error: ${data.error}</div>
                `;
            } else {
                this.backtestResults.classList.remove('hidden');
                this.backtestResults.innerHTML = `
                    <h2 class="text-xl font-bold mb-4">Strategy Execution Results</h2>
                    <ul class="space-y-2">
                        ${Object.entries(data.strategyResults).map(([key, value]) => 
                            `<li>${key}: ${value}</li>`
                        ).join('')}
                    </ul>
                `;
            }
        } catch (error) {
            console.error('Error:', error);
            this.backtestResults.innerHTML = `
                <div class="text-red-500">Error: ${error.message}</div>
            `;
        } finally {
            this.hideLoadingIndicator();
        }
    }

    loadStrategy(strategy) {
        // Match exact functionality from old backtest.html
        document.getElementById('strategyName').value = strategy.strategyName;
        document.getElementById('authorName').value = strategy.authorName;
        document.getElementById('strategyCode').value = strategy.strategyCode;
        document.getElementById('currencyPair').value = strategy.currencyPair;
        document.getElementById('timeFrame').value = strategy.timeFrame;
    }

    loadStrategyFromLocalStorage() {
        const strategyData = JSON.parse(localStorage.getItem('strategyData'));
        if (strategyData) {
            document.getElementById('strategyName').value = strategyData.name;
            document.getElementById('authorName').value = 'AI Assistant';
            document.getElementById('strategyCode').value = strategyData.code;
            document.getElementById('currencyPair').value = strategyData.currency_pair;
            document.getElementById('timeFrame').value = strategyData.timeframe;
            localStorage.removeItem('strategyData');
        }
    }

    filterStrategies() {
        const searchTerm = this.searchInput.value.toLowerCase();
        const items = this.strategyList.getElementsByTagName('li');
        
        Array.from(items).forEach(item => {
            const text = item.textContent.toLowerCase();
            item.style.display = text.includes(searchTerm) ? '' : 'none';
        });
    }

    showLoadingIndicator() {
        this.loadingIndicator.style.display = 'flex';
    }

    hideLoadingIndicator() {
        this.loadingIndicator.style.display = 'none';
    }
}

// Initialize backtest manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.backtestManager = new BacktestManager();
});
