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
        
        // Add validation listeners
        const inputs = this.strategyForm.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', () => this.validateInput(input));
        });
    }

    validateInput(input) {
        const value = input.value.trim();
        if (!value) {
            input.classList.add('border-red-500');
            return false;
        }

        // Additional validation for currency pair
        if (input.id === 'currencyPair') {
            const validPairs = ['USD/JPY', 'EUR/USD', 'GBP/USD', 'USD/CHF', 'AUD/USD', 'USD/CAD'];
            if (!validPairs.some(pair => value.toUpperCase().includes(pair))) {
                input.classList.add('border-red-500');
                this.showError('Invalid currency pair format. Example: USD/JPY');
                return false;
            }
        }

        // Additional validation for timeframe
        if (input.id === 'timeFrame') {
            const validTimeframes = ['1h', '4h', '1d', '1m', '30m', 'H1', 'H4', 'D', 'M1', 'M30'];
            if (!validTimeframes.some(tf => value.toLowerCase() === tf.toLowerCase())) {
                input.classList.add('border-red-500');
                this.showError('Invalid timeframe. Valid examples: 1h, 4h, 1d, 30m');
                return false;
            }
        }

        input.classList.remove('border-red-500');
        return true;
    }

    async loadSavedStrategies() {
        try {
            console.log('Loading saved strategies...');
            const response = await axios.get('/api/v1/strategies');
            this.strategyList.innerHTML = '';
            
            response.data.forEach(strategy => {
                const li = this.createStrategyListItem(strategy);
                this.strategyList.appendChild(li);
            });
            console.log('Saved strategies loaded successfully.');
        } catch (error) {
            console.error('Error loading strategies:', error);
            this.showError('Failed to load saved strategies');
        }
    }

    createStrategyListItem(strategy) {
        const li = document.createElement('li');
        li.className = 'p-3 bg-trading-dark rounded-lg hover:bg-trading-medium cursor-pointer transition-colors mb-2';
        li.innerHTML = `
            <div class="flex justify-between items-center">
                <div>
                    <h3 class="font-semibold">${strategy.name}</h3>
                    <p class="text-sm text-gray-400">${strategy.currency_pair} - ${strategy.time_frame}</p>
                </div>
                <div class="flex space-x-2">
                    <button class="backtest-btn px-2 py-1 bg-trading-accent hover:bg-trading-hover rounded">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="delete-btn px-2 py-1 bg-red-500 hover:bg-red-600 rounded">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;

        li.querySelector('.backtest-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.loadStrategy(strategy);
        });

        li.querySelector('.delete-btn').addEventListener('click', (e) => {
            e.stopPropagation();
            this.deleteStrategy(strategy.id);
        });

        return li;
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        // Validate all inputs
        const inputs = this.strategyForm.querySelectorAll('input, textarea');
        let isValid = true;
        inputs.forEach(input => {
            if (!this.validateInput(input)) isValid = false;
        });
        
        if (!isValid) {
            this.showError('Please fill in all required fields');
            return;
        }

        const formData = {
            strategyName: document.getElementById('strategyName').value,
            authorName: document.getElementById('authorName').value,
            strategyCode: document.getElementById('strategyCode').value,
            currencyPair: document.getElementById('currencyPair').value,
            timeFrame: document.getElementById('timeFrame').value
        };

        console.log('Submitting form data:', formData);
        this.showLoadingIndicator();

        try {
            const response = await axios.post('/api/v1/backtest_strategy', formData);
            const data = response.data;

            if (data.error) {
                this.showError(data.error);
                return;
            }

            console.log('Backtest results received:', data);
            this.displayBacktestResults(data);
            this.updateAssistantAnalysis(data.analysis);
            this.displayPlot(data.plotUrl);
            
            // Save strategy
            await this.saveStrategy(formData);
            await this.loadSavedStrategies();

        } catch (error) {
            console.error('Error:', error);
            this.showError(error.message);
        } finally {
            this.hideLoadingIndicator();
        }
    }

    displayBacktestResults(data) {
        this.backtestResults.classList.remove('hidden');
        this.backtestResults.innerHTML = `
            <h2 class="text-xl font-bold mb-4">Backtest Results</h2>
            <div class="grid grid-cols-2 gap-4">
                ${Object.entries(data.backtestResults).map(([key, value]) => `
                    <div class="bg-trading-dark p-4 rounded-lg">
                        <h3 class="font-semibold mb-2">${this.formatMetricName(key)}</h3>
                        <p class="text-2xl ${this.getMetricColor(key, value)}">${this.formatMetricValue(key, value)}</p>
                    </div>
                `).join('')}
            </div>
        `;
    }

    formatMetricName(key) {
        return key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
    }

    formatMetricValue(key, value) {
        if (typeof value === 'number') {
            if (key.includes('percentage') || key.includes('rate')) {
                return value.toFixed(2) + '%';
            }
            if (key.includes('ratio')) {
                return value.toFixed(3);
            }
            return value.toFixed(2);
        }
        return value;
    }

    getMetricColor(key, value) {
        if (typeof value !== 'number') return '';
        
        if (key.includes('return') || key.includes('profit') || key.includes('gain')) {
            return value > 0 ? 'text-green-500' : 'text-red-500';
        }
        
        if (key.includes('drawdown') || key.includes('loss')) {
            return value < -10 ? 'text-red-500' : 'text-yellow-500';
        }
        
        return '';
    }

    updateAssistantAnalysis(analysis) {
        this.assistantResponse.innerHTML = `
            <div class="prose prose-invert">
                ${marked(analysis)}
            </div>
        `;
    }

    displayPlot(plotUrl) {
        this.plotContainer.innerHTML = `
            <img src="${plotUrl}" alt="Backtest Plot" class="w-full h-auto rounded-lg">
        `;
    }

    async deleteStrategy(id) {
        if (!confirm('Are you sure you want to delete this strategy?')) return;
        
        try {
            console.log(`Deleting strategy with ID: ${id}`);
            await axios.delete(`/api/v1/strategy/${id}`);
            await this.loadSavedStrategies();
            console.log('Strategy deleted successfully.');
        } catch (error) {
            console.error('Error deleting strategy:', error);
            this.showError('Failed to delete strategy');
        }
    }

    async loadStrategy(strategy) {
        console.log('Loading strategy:', strategy);
        document.getElementById('strategyName').value = strategy.name;
        document.getElementById('authorName').value = strategy.authorName || 'Anonymous';
        document.getElementById('strategyCode').value = strategy.algo_code;
        document.getElementById('currencyPair').value = strategy.currency_pair;
        document.getElementById('timeFrame').value = strategy.time_frame;
    }

    loadStrategyFromLocalStorage() {
        const strategyData = JSON.parse(localStorage.getItem('strategyData'));
        if (strategyData) {
            console.log('Loading strategy from local storage:', strategyData);
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

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg';
        errorDiv.textContent = message;
        document.body.appendChild(errorDiv);
        setTimeout(() => errorDiv.remove(), 5000);
    }

    showLoadingIndicator() {
        this.loadingIndicator.classList.remove('hidden');
    }

    hideLoadingIndicator() {
        this.loadingIndicator.classList.add('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.backtestManager = new BacktestManager();
});