class BacktestManager {
    constructor() {
        this.elements = {
            strategyForm: document.getElementById('strategyForm'),
            strategyList: document.getElementById('strategyList'),
            backtestResults: document.getElementById('backtestResults'),
            assistantResponse: document.getElementById('assistantResponse'),
            searchInput: document.getElementById('searchStrategies'),
            loadingIndicator: document.getElementById('loading-indicator'),
            plotContainer: document.getElementById('plot-container'),
            strategyCode: document.getElementById('strategyCode'),
            indicatorSelect: document.getElementById('indicatorSelect')
        };

        this.setupEventListeners();
        this.loadSavedStrategies();
        this.loadStrategyFromLocalStorage();
        this.initializeCodeEditor();
        this.loadIndicators();
        this.setupAiAgentButton();
    }

    setupAiAgentButton() {
        const aiAgentBtn = document.getElementById('aiAgentBtn');

        aiAgentBtn.addEventListener('click', async () => {
            const strategyCode = this.elements.strategyCode.value;
            if (!strategyCode) {
                this.showNotification('Please enter your strategy code.', 'error');
                return;
            }
    
            this.showNotification('Sending code to AI agent for processing...', 'info');
    
            try {
                const response = await axios.post('/api/v1/querystrategyagent', { prompt: strategyCode });
                const data = response.data;
    
                if (data.error) {
                    throw new Error(data.error);
                }
    
                // Update the strategy code editor with the AI's response
                this.elements.strategyCode.value = data.response;
                this.showNotification('AI response received and code updated.', 'success');
            } catch (error) {
                this.showNotification(error.message, 'error');
            }
        });
    }

    setupEventListeners() {
        this.elements.strategyForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.elements.searchInput.addEventListener('input', () => this.filterStrategies());
        
        const inputs = this.elements.strategyForm.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', () => this.validateInput(input));
            input.addEventListener('focus', () => this.handleInputFocus(input));
            input.addEventListener('blur', () => this.handleInputBlur(input));
        });
    }

    initializeCodeEditor() {
        const copyBtn = this.elements.strategyCode.parentElement.querySelector('.fa-copy').parentElement;
        const expandBtn = this.elements.strategyCode.parentElement.querySelector('.fa-expand').parentElement;

        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(this.elements.strategyCode.value);
            this.showNotification('Code copied to clipboard', 'success');
        });

        expandBtn.addEventListener('click', () => {
            this.toggleFullscreenEditor();
        });
    }

    toggleFullscreenEditor() {
        const editorContainer = this.elements.strategyCode.parentElement;
        const isFullscreen = editorContainer.classList.contains('fixed');

        if (isFullscreen) {
            gsap.to(editorContainer, {
                scale: 1,
                opacity: 0,
                duration: 0.3,
                onComplete: () => {
                    editorContainer.classList.remove('fixed', 'inset-4', 'z-50', 'bg-dark-900/95', 'p-6');
                    gsap.set(editorContainer, { clearProps: 'all' });
                }
            });
        } else {
            editorContainer.classList.add('fixed', 'inset-4', 'z-50', 'bg-dark-900/95', 'p-6');
            gsap.from(editorContainer, {
                scale: 0.95,
                opacity: 0,
                duration: 0.3
            });
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        if (!this.validateForm()) {
            this.showNotification('Please fill in all required fields correctly', 'error');
            return;
        }

        const formData = {
            strategyName: this.elements.strategyForm.querySelector('#strategyName').value,
            authorName: this.elements.strategyForm.querySelector('#authorName').value,
            strategyCode: this.elements.strategyCode.value,
            currencyPair: this.elements.strategyForm.querySelector('#currencyPair').value,
            timeFrame: this.elements.strategyForm.querySelector('#timeFrame').value,
            indicator: this.elements.indicatorSelect.value
        };

        this.showLoadingIndicator();

        try {
            const response = await axios.post('/api/v1/backtest_strategy', formData);
            const data = response.data;

            if (data.error) {
                throw new Error(data.error);
            }

            await this.displayResults(data);
            await this.saveStrategy(formData);
            await this.loadSavedStrategies();

        } catch (error) {
            this.showNotification(error.message, 'error');
        } finally {
            this.hideLoadingIndicator();
        }
    }
    
    validateForm() {
        let isValid = true;
        const requiredFields = ['strategyName', 'authorName', 'strategyCode', 'currencyPair', 'timeFrame'];
    
        requiredFields.forEach(fieldId => {
            const field = this.elements.strategyForm.querySelector(`#${fieldId}`);
            if (!field.value.trim()) {
                isValid = false;
                this.highlightInvalidField(field);
            } else {
                this.resetFieldValidation(field);
            }
        });
    
        return isValid;
    }
    
    highlightInvalidField(field) {
        gsap.to(field, {
            borderColor: 'rgba(239, 68, 68, 0.5)',
            duration: 0.3
        });
    }
    
    resetFieldValidation(field) {
        gsap.to(field, {
            borderColor: 'rgba(0, 144, 255, 0.5)',
            duration: 0.3
        });
    }

    async displayResults(data) {
        const results = this.elements.backtestResults;
        results.classList.remove('hidden');

        gsap.set(results, { opacity: 0, y: 20 });
        
        // Clear previous results
        const metricsContainer = results.querySelector('.grid');
        metricsContainer.innerHTML = '';

        // Add new metric cards with animations
        Object.entries(data.backtestResults).forEach(([key, value], index) => {
            const card = this.createMetricCard(key, value);
            metricsContainer.appendChild(card);
            
            gsap.from(card, {
                opacity: 0,
                y: 20,
                duration: 0.3,
                delay: index * 0.1
            });
        });

        // Update AI analysis with animation
        if (data.analysis) {
            this.elements.assistantResponse.innerHTML = marked(data.analysis);
            gsap.from(this.elements.assistantResponse, {
                opacity: 0,
                y: 20,
                duration: 0.3,
                delay: 0.3
            });
        }

        // Display plot if available
        if (data.plotUrl) {
            this.elements.plotContainer.innerHTML = `
                <img src="${data.plotUrl}" alt="Backtest Plot" class="w-full h-auto rounded-xl">
            `;
            gsap.from(this.elements.plotContainer, {
                opacity: 0,
                y: 20,
                duration: 0.3,
                delay: 0.4
            });
        }

        gsap.to(results, {
            opacity: 1,
            y: 0,
            duration: 0.3
        });
    }

    createMetricCard(key, value) {
        const card = document.createElement('div');
        card.className = 'metric-card p-4 rounded-xl bg-dark-800/30 border border-dark-700';
        
        const trend = this.getMetricTrend(key, value);
        const formattedValue = this.formatMetricValue(key, value);
        
        card.innerHTML = `
            <h3 class="text-sm font-medium text-dark-300 mb-1">${this.formatMetricName(key)}</h3>
            <div class="flex items-center space-x-2">
                <span class="text-2xl font-bold ${this.getMetricColor(key, value)}">${formattedValue}</span>
                ${trend ? `<i class="fas ${trend.icon} text-${trend.color}-500"></i>` : ""}
            </div>
        `;
        
        return card;
    }

    getMetricTrend(key, value) {
        if (typeof value !== 'number') return null;
        
        if (key.includes('return') || key.includes('profit') || key.includes('gain')) {
            return value > 0 
                ? { icon: 'fa-trending-up', color: 'success' }
                : { icon: 'fa-trending-down', color: 'danger' };
        }
        
        if (key.includes('drawdown') || key.includes('loss')) {
            return value < -10
                ? { icon: 'fa-triangle-exclamation', color: 'danger' }
                : { icon: 'fa-triangle-exclamation', color: 'warning' };
        }
        
        return null;
    }

    validateInput(input) {
        const value = input.value.trim();
        const isValid = this.validateField(input.id, value);

        gsap.to(input, {
            borderColor: isValid ? 'rgba(0, 144, 255, 0.5)' : 'rgba(239, 68, 68, 0.5)',
            duration: 0.3
        });

        return isValid;
    }

    validateField(fieldId, value) {
        if (!value) return false;

        const validators = {
            currencyPair: pair => /^[A-Z]{3}\/[A-Z]{3}$/.test(pair.toUpperCase()),
            timeFrame: tf => ['1h', '4h', '1d', '1m', '30m', 'H1', 'H4', 'D', 'M1', 'M30'].includes(tf),
            strategyCode: code => code.length > 10,
            strategyName: name => name.length >= 3,
            authorName: name => name.length >= 2
        };

        return validators[fieldId] ? validators[fieldId](value) : true;
    }

    handleInputFocus(input) {
        gsap.to(input, {
            scale: 1.02,
            duration: 0.2
        });
    }

    handleInputBlur(input) {
        gsap.to(input, {
            scale: 1,
            duration: 0.2
        });
    }

    showNotification(message, type = 'info') {
        const colors = {
            success: 'from-success-500 to-success-600',
            error: 'from-danger-500 to-danger-600',
            info: 'from-primary-500 to-primary-600'
        };

        const notification = document.createElement('div');
        notification.className = `fixed bottom-4 right-4 bg-gradient-to-r ${colors[type]} 
                                text-white px-6 py-3 rounded-xl shadow-lg z-50`;
        notification.textContent = message;

        gsap.set(notification, { opacity: 0, y: 20 });
        document.body.appendChild(notification);

        gsap.to(notification, {
            opacity: 1,
            y: 0,
            duration: 0.3,
            ease: 'power2.out'
        });

        setTimeout(() => {
            gsap.to(notification, {
                opacity: 0,
                y: 20,
                duration: 0.3,
                ease: 'power2.in',
                onComplete: () => notification.remove()
            });
        }, 5000);
    }

    async loadSavedStrategies() {
        try {
            const response = await axios.get('/api/v1/strategies');
            this.elements.strategyList.innerHTML = '';
            
            response.data.forEach((strategy, index) => {
                const item = this.createStrategyListItem(strategy);
                gsap.set(item, { opacity: 0, y: 20 });
                this.elements.strategyList.appendChild(item);
                
                gsap.to(item, {
                    opacity: 1,
                    y: 0,
                    duration: 0.3,
                    delay: index * 0.1
                });
            });
        } catch (error) {
            this.showNotification('Failed to load saved strategies', 'error');
        }
    }

    createStrategyListItem(strategy) {
        const li = document.createElement('div');
        li.className = 'strategy-card p-4 rounded-xl bg-dark-800/30 border border-dark-700 hover:bg-dark-800/50 transition-all duration-300';
        
        li.innerHTML = `
            <div class="flex justify-between items-center">
                <div class="space-y-1">
                    <h3 class="font-semibold text-primary-100">${strategy.name}</h3>
                    <p class="text-sm text-dark-400">${strategy.currency_pair} - ${strategy.time_frame}</p>
                </div>
                <div class="flex space-x-2">
                    <button class="action-button p-2 rounded-lg bg-primary-500/10 text-primary-400 
                                 hover:bg-primary-500/20 transition-all duration-300">
                        <i class="fas fa-play"></i>
                    </button>
                    <button class="action-button p-2 rounded-lg bg-danger-500/10 text-danger-400 
                                 hover:bg-danger-500/20 transition-all duration-300">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;

        li.querySelector('.fa-play').parentElement.addEventListener('click', (e) => {
            e.stopPropagation();
            this.loadStrategy(strategy);
        });

        li.querySelector('.fa-trash').parentElement.addEventListener('click', (e) => {
            e.stopPropagation();
            this.deleteStrategy(strategy.id);
        });

        return li;
    }

    async deleteStrategy(id) {
        if (!confirm('Are you sure you want to delete this strategy?')) return;
        
        try {
            await axios.delete(`/api/v1/strategy/${id}`);
            await this.loadSavedStrategies();
            this.showNotification('Strategy deleted successfully', 'success');
        } catch (error) {
            this.showNotification('Failed to delete strategy', 'error');
        }
    }

    loadStrategy(strategy) {
        const fields = {
            strategyName: strategy.name,
            authorName: strategy.authorName || 'Anonymous',
            strategyCode: strategy.algo_code,
            currencyPair: strategy.currency_pair,
            timeFrame: strategy.time_frame
        };

        Object.entries(fields).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.value = value;
                gsap.from(element, {
                    scale: 1.02,
                    duration: 0.3
                });
            }
        });
    }

    showLoadingIndicator() {
        gsap.set(this.elements.loadingIndicator, { display: 'flex', opacity: 0 });
        gsap.to(this.elements.loadingIndicator, {
            opacity: 1,
            duration: 0.3
        });
    }

    hideLoadingIndicator() {
        gsap.to(this.elements.loadingIndicator, {
            opacity: 0,
            duration: 0.3,
            onComplete: () => {
                this.elements.loadingIndicator.style.display = 'none';
            }
        });
    }

    async loadIndicators() {
        try {
            const response = await axios.get('/api/v1/indicators');
            const indicators = response.data;
            
            indicators.forEach(indicator => {
                const option = document.createElement('option');
                option.value = indicator.name;
                option.textContent = indicator.name;
                this.elements.indicatorSelect.appendChild(option);
            });
        } catch (error) {
            this.showNotification('Failed to load indicators', 'error');
        }
    }
    
    loadStrategyFromLocalStorage() {
        const strategyCode = localStorage.getItem('strategyCode');
        if (strategyCode) {
            this.elements.strategyCode.value = strategyCode;
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.backtestManager = new BacktestManager();
});
