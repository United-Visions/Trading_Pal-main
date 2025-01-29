class ChartManager {
    constructor() {
        this.activePair = null;
        this.activeTimeframe = '1m';
        this.chartType = 'candlestick';
        this.marketType = 'forex';
        this.chart = null;
        this.candleSeries = null;
        this.updateInterval = null;
        this.ws = null;
        this.interval = null;
        this.currentData = {
            forex: {},
            crypto: {}
        };
        
        this.pairs = {
            forex: ['EUR/USD', 'GBP/USD'],
            crypto: ['BTC/USD', 'ETH/USD']
        };

        this.timeframes = {
            '1h': '1 Hour',
            '4h': '4 Hours', 
            '1d': '1 Day'
        };

        this.colors = {
            background: '#1a1a1a',
            grid: '#333333',
            text: '#ffffff',
            up: '#26a69a',
            down: '#ef5350',
            line: '#2962ff'
        };
        
        this.initializeUI();
        this.initializeWebSocket();
        this.setupEventListeners();
        
        this.dataServer = 'http://localhost:4000';
        this.updateInterval = null;
        this.feedReaders = {};
        this.rssReader = null;
        this.dataUpdateInterval = 1000; // 1 second update interval
        this.lastUpdate = {};
        this.errorCount = 0;
        this.maxErrors = 3;
    }

    initializeWebSocket() {
        this.ws = new WebSocket('wss://socket.polygon.io/forex');
        
        this.ws.onopen = () => {
            // Authenticate immediately on connection
            const auth_msg = {
                "action": "auth",
                "params": POLYGON_API_KEY
            };
            this.ws.send(JSON.stringify(auth_msg));
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (Array.isArray(data)) {
                data.forEach(msg => this.handleMessage(msg));
            } else {
                this.handleMessage(data);
            }
        };

        this.ws.onclose = () => {
            console.log('WebSocket closed, attempting to reconnect...');
            setTimeout(() => this.initializeWebSocket(), 5000);
        };
    }

    handleMessage(msg) {
        if (msg.ev === 'status' && msg.status === 'auth_success') {
            // Subscribe to forex and crypto feeds after authentication
            if (this.activePair) {
                const subscribeMsg = {
                    "action": "subscribe",
                    "params": this.marketType === 'forex' ? 
                        `C.${this.activePair.replace('/', '-')}` :
                        `XT.${this.activePair.replace('/', '-')}`
                };
                this.ws.send(JSON.stringify(subscribeMsg));
            }
        }
        else if ((msg.ev === 'C' || msg.ev === 'XT') && this.chart) {
            this.updateChartWithData(msg);
        }
    }

    initializeUI() {
        const select = document.getElementById('timeframeSelect');
        select.innerHTML = '';
        
        Object.entries(this.timeframes).forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            select.appendChild(option);
        });

        this.updatePairSelect(this.marketType);
        this.initializeChart();
    }

    initializeChart() {
        try {
            const canvas = document.getElementById('chartCanvas');
            if (!canvas) {
                console.error('Chart canvas element not found');
                return;
            }

            const ctx = canvas.getContext('2d');
            if (!ctx) {
                console.error('Failed to get canvas context');
                return;
            }

            // Create chart configuration
            const chartConfig = {
                type: 'line', // Changed from candlestick to line initially
                data: {
                    datasets: [{
                        label: this.activePair || 'No pair selected',
                        data: [],
                        borderColor: this.colors.line,
                        backgroundColor: this.colors.background,
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: this.activeTimeframe === '1h' ? 'minute' : 'hour'
                            },
                            grid: {
                                color: this.colors.grid
                            }
                        },
                        y: {
                            grid: {
                                color: this.colors.grid
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                color: this.colors.text
                            }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: this.colors.background,
                            titleColor: this.colors.text,
                            bodyColor: this.colors.text,
                            borderColor: this.colors.grid,
                            borderWidth: 1
                        }
                    },
                    interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    }
                }
            };

            if (this.chart) {
                this.chart.destroy();
            }

            this.chart = new Chart(ctx, chartConfig);
            console.log('Chart initialized successfully');
        } catch (error) {
            console.error('Chart initialization failed:', error);
        }
    }

    async fetchHistoricalData() {
        try {
            const response = await fetch(`/charts/api/historical/${this.marketType}/${this.activePair}/${this.activeTimeframe}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Failed to fetch historical data:', error);
            return null;
        }
    }

    handleConnectionFailure() {
        console.log('WebSocket connection failed, switching to historical data');
        this.fetchHistoricalData().then(data => {
            if (data) {
                this.updateChartWithHistoricalData(data);
            }
        });
    }

    async startFeedReader(market, pair) {
        if (this.feedReaders[`${market}-${pair}`]) {
            clearInterval(this.feedReaders[`${market}-${pair}`]);
        }

        const updateChart = async () => {
            try {
                const response = await fetch(`${this.dataServer}/api/feed/${market}/${pair}`);
                if (!response.ok) throw new Error('Feed fetch failed');
                
                const data = await response.json();
                this.updateChartWithFeedData(data);
            } catch (error) {
                console.error('Feed update error:', error);
            }
        };

        // Initial update
        await updateChart();
        
        // Set up interval for updates
        this.feedReaders[`${market}-${pair}`] = setInterval(updateChart, 1000);
    }

    updateChartWithFeedData(data) {
        if (!this.chart || !data.length) return;

        const chartData = data.map(item => ({
            x: new Date(item.timestamp),
            y: item.price
        }));

        const dataset = this.chart.data.datasets[0];
        dataset.data = chartData;
        this.chart.update('quiet');
    }

    createSeries(type = 'line') {
        if (this.chart) {
            this.chart.destroy();
        }

        const chartConfig = {
            type: type,
            data: {
                datasets: [{
                    label: this.activePair || 'No pair selected',
                    data: [],
                    borderColor: this.colors.line,
                    backgroundColor: type === 'line' ? 'transparent' : this.colors.background,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: this.getTimeUnit()
                        },
                        grid: {
                            color: this.colors.grid
                        }
                    },
                    y: {
                        grid: {
                            color: this.colors.grid
                        }
                    }
                }
            }
        };

        const canvas = document.getElementById('chartCanvas');
        this.chart = new Chart(canvas, chartConfig);
        
        // Start feed reader for current pair
        if (this.activePair) {
            this.startFeedReader(this.marketType, this.activePair);
        }
    }

    getTimeUnit() {
        switch(this.activeTimeframe) {
            case '1h': return 'minute';
            case '4h': return 'hour';
            case '1d': return 'day';
            default: return 'hour';
        }
    }

    refreshCharts() {
        if (this.activePair && this.chart) {
            this.updateChart();
        }
    }

    updateChart() {
        if (!this.activePair) return;

        const endpoint = `/charts/api/data/${this.marketType}`;
        
        fetch(endpoint)
            .then(response => response.json())
            .then(data => {
                if (!data[this.activePair]) return;

                const chartData = data[this.activePair].map(bar => ({
                    time: new Date(bar.timestamp).getTime() / 1000,
                    open: bar.open,
                    high: bar.high,
                    low: bar.low,
                    close: bar.close,
                    volume: bar.volume
                }));

                this.candleSeries.setData(chartData);
            })
            .catch(console.error);
    }

    updateChartWithData(data) {
        if (!this.chart || !this.activePair) return;

        const price = data.ev === 'C' ? 
            (parseFloat(data.a) + parseFloat(data.b)) / 2 : // Forex midpoint
            parseFloat(data.p); // Crypto price

        const newData = {
            x: new Date(data.t),
            y: price
        };

        const dataset = this.chart.data.datasets[0];
        dataset.data.push(newData);

        // Keep only last 1000 points
        if (dataset.data.length > 1000) {
            dataset.data.shift();
        }

        this.chart.update('quiet');
    }

    setupEventListeners() {
        // Market type selection
        document.getElementById('forexTab').addEventListener('click', () => this.switchMarket('forex'));
        document.getElementById('cryptoTab').addEventListener('click', () => this.switchMarket('crypto'));

        // Pair selection
        document.getElementById('pairSelect').addEventListener('change', (e) => {
            this.activePair = e.target.value;
            if (this.activePair) {
                this.createSeries(this.chartType);
                this.startDataUpdates();
            }
        });

        // Timeframe selection
        document.getElementById('timeframeSelect').addEventListener('change', (e) => {
            this.activeTimeframe = e.target.value;
            if (this.activePair) {
                this.updateChart();
            }
        });

        // Chart type selection
        document.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const type = e.currentTarget.dataset.type;
                this.switchChartType(type);
            });
        });
    }

    switchChartType(type) {
        this.chartType = type;
        document.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.classList.toggle('bg-blue-600', btn.dataset.type === type);
            btn.classList.toggle('bg-dark-700', btn.dataset.type !== type);
        });
        if (this.activePair) {
            this.createSeries(type);
            this.updateChart();
        }
    }

    startDataUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        this.updateChart();
        this.updateInterval = setInterval(() => this.updateChart(), 1000);
    }

    switchMarket(marketType) {
        this.marketType = marketType;
        this.updatePairSelect(marketType);
        this.activePair = null;
        
        // Update UI
        const isForex = marketType === 'forex';
        document.getElementById('forexTab').className = 
            `px-4 py-2 rounded-lg text-white flex-1 ${isForex ? 'bg-blue-600' : 'bg-gray-700'}`;
        document.getElementById('cryptoTab').className = 
            `px-4 py-2 rounded-lg text-white flex-1 ${!isForex ? 'bg-blue-600' : 'bg-gray-700'}`;
    }

    toggleFullscreen(enable) {
        this.isFullscreen = enable;
        const fullscreenEl = document.getElementById('fullscreen-chart');
        
        if (enable) {
            fullscreenEl.classList.remove('hidden');
            document.getElementById('fullscreen-title').textContent = this.activePair;
            this.createChart('fullscreen-chart-container', this.activePair, true);
        } else {
            fullscreenEl.classList.add('hidden');
        }
    }

    updatePairSelect(marketType) {
        const select = document.getElementById('pairSelect');
        select.innerHTML = '<option value="">Select Pair</option>';
        
        this.pairs[marketType].forEach(pair => {
            const option = document.createElement('option');
            option.value = pair;
            option.textContent = pair;
            select.appendChild(option);
        });
    }
    
    cleanup() {
        // Clean up feed readers
        Object.values(this.feedReaders).forEach(interval => clearInterval(interval));
        this.feedReaders = {};
        if (this.rssReader) {
            clearInterval(this.rssReader);
            this.rssReader = null;
        }
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }

    async initializeFeed() {
        try {
            if (this.activePair && this.marketType) {
                const feedUrl = `${this.dataServer}/rss/${this.marketType}/${this.activePair.replace('/', '-')}`;
                this.startFeedPolling(feedUrl);
            }
        } catch (error) {
            console.error('Feed initialization error:', error);
            this.handleFeedError();
        }
    }

    startFeedPolling(feedUrl) {
        if (this.rssReader) {
            clearInterval(this.rssReader);
        }

        this.rssReader = setInterval(async () => {
            try {
                const response = await fetch(feedUrl);
                if (!response.ok) throw new Error('Feed fetch failed');
                
                const data = await response.json();
                this.updateChartWithFeedData(data);
                this.errorCount = 0; // Reset error count on successful update
            } catch (error) {
                console.error('Feed polling error:', error);
                this.handleFeedError();
            }
        }, this.dataUpdateInterval);
    }

    handleFeedError() {
        this.errorCount++;
        if (this.errorCount >= this.maxErrors) {
            console.error('Max feed errors reached, falling back to REST API');
            this.fallbackToRestApi();
        }
    }

    async fallbackToRestApi() {
        clearInterval(this.rssReader);
        const apiUrl = `${this.dataServer}/api/feed/${this.marketType}/${this.activePair.replace('/', '-')}`;
        
        try {
            const response = await fetch(apiUrl);
            if (!response.ok) throw new Error('API fetch failed');
            
            const data = await response.json();
            this.updateChartWithFeedData(data);
        } catch (error) {
            console.error('REST API fallback error:', error);
        }
    }

    updateChartWithFeedData(data) {
        if (!this.chart || !data.length) return;

        const chartData = data.map(item => ({
            x: new Date(item.timestamp),
            y: parseFloat(item.price),
            volume: parseFloat(item.volume)
        }));

        const dataset = this.chart.data.datasets[0];
        dataset.data = chartData;
        this.chart.update('quiet');
    }
}

// Initialize after loading required libraries
document.addEventListener('DOMContentLoaded', () => {
    // Load required libraries
    const scripts = [
        'https://cdn.jsdelivr.net/npm/chart.js',
        'https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns',
        'https://cdn.jsdelivr.net/npm/chartjs-plugin-crosshair'
    ];

    Promise.all(scripts.map(src => {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }))
    .then(() => {
        window.chartManager = new ChartManager();
    })
    .catch(console.error);
});
