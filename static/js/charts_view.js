class ChartManager {
    constructor() {
        this.activePair = 'EUR-USD';
        this.chart = null;
        this.dataUpdateInterval = 1000;
        this.updateInterval = null;
        this.isInitialized = false;
        this.container = null;
        this.loadingEl = null;
        this.errorEl = null;
        this.pairInfoEl = null;
        
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }

        // Clean up on page unload
        window.addEventListener('beforeunload', () => this.cleanup());
    }

    initialize() {
        // Get DOM elements
        this.container = document.getElementById('charts-container');
        this.loadingEl = document.getElementById('chart-loading');
        this.errorEl = document.getElementById('chart-error');
        this.pairInfoEl = document.getElementById('chart-pair-info');
        
        if (!this.container || !this.loadingEl || !this.errorEl || !this.pairInfoEl) {
            console.error('Required chart elements not found');
            return;
        }

        // Setup event listeners
        document.getElementById('charts-tab')?.addEventListener('click', () => this.show());
        document.getElementById('close-charts')?.addEventListener('click', () => this.hide());
        document.getElementById('retry-chart')?.addEventListener('click', () => this.retry());

        // Initialize chart
        this.initializeChart();
    }

    show() {
        if (this.container) {
            this.container.classList.remove('hidden');
            this.container.classList.add('flex');
            if (!this.chart) {
                this.initializeChart();
            }
        }
    }

    hide() {
        if (this.container) {
            this.container.classList.remove('flex');
            this.container.classList.add('hidden');
        }
    }

    showLoading() {
        if (this.loadingEl) {
            this.loadingEl.classList.remove('hidden');
            this.loadingEl.classList.add('flex');
        }
    }

    hideLoading() {
        if (this.loadingEl) {
            this.loadingEl.classList.remove('flex');
            this.loadingEl.classList.add('hidden');
        }
    }

    showError(message) {
        if (this.errorEl) {
            const messageEl = document.getElementById('chart-error-message');
            if (messageEl) {
                messageEl.textContent = message || 'Unable to load chart data';
            }
            this.errorEl.classList.remove('hidden');
            this.errorEl.classList.add('flex');
        }
    }

    hideError() {
        if (this.errorEl) {
            this.errorEl.classList.remove('flex');
            this.errorEl.classList.add('hidden');
        }
    }

    retry() {
        this.hideError();
        this.initializeChart();
    }

    cleanup() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
        this.isInitialized = false;
    }

    async initializeChart() {
        try {
            const container = document.getElementById('activeChart');
            const canvas = document.getElementById('chartCanvas');
            
            if (!canvas || !container) {
                console.error('Required chart elements not found');
                return;
            }

            // Set canvas size to match container
            canvas.style.width = '100%';
            canvas.style.height = '100%';
            canvas.width = container.offsetWidth;
            canvas.height = container.offsetHeight;

            const ctx = canvas.getContext('2d');
            if (!ctx) {
                console.error('Could not get canvas context');
                return;
            }

            // Register required Chart.js components
            Chart.register(Chart.TimeScale);
            Chart.register(Chart.LinearScale);
            Chart.register(Chart.LineController);
            Chart.register(Chart.PointElement);
            Chart.register(Chart.LineElement);
            Chart.register(Chart.Legend);
            Chart.register(Chart.Tooltip);
            
            this.chart = new Chart(ctx, this.getChartConfig());
            console.log('Chart initialized successfully');

            // Handle resize
            window.addEventListener('resize', () => {
                if (this.chart) {
                    canvas.width = container.offsetWidth;
                    canvas.height = container.offsetHeight;
                    this.chart.resize();
                }
            });

            await this.startDataFeed();

        } catch (error) {
            console.error('Chart initialization error:', error);
        }
    }

    getChartConfig() {
        return {
            type: 'line',
            data: {
                datasets: [
                    {
                        label: `${this.activePair} Price`,
                        data: [],
                        borderColor: '#0090ff',
                        backgroundColor: 'rgba(0, 144, 255, 0.1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.2,
                        fill: true,
                        cubicInterpolationMode: 'monotone',
                        order: 1,  // Display on top
                        segment: {
                            borderColor: (ctx) => {
                                if (!ctx.p0 || !ctx.p1) return '#0090ff';
                                // Green if price is going up, red if going down
                                return ctx.p0.parsed.y < ctx.p1.parsed.y ? 
                                    'rgba(0, 255, 144, 0.8)' : 
                                    'rgba(255, 72, 72, 0.8)';
                            }
                        },
                        spanGaps: true
                    },
                    {
                        label: 'Price Range',
                        data: [],
                        backgroundColor: (ctx) => {
                            if (!ctx.raw) return 'rgba(0, 144, 255, 0.05)';
                            const point = ctx.chart.data.datasets[0].data[ctx.dataIndex];
                            if (!point) return 'rgba(0, 144, 255, 0.05)';
                            const nextPoint = ctx.chart.data.datasets[0].data[ctx.dataIndex + 1];
                            if (!nextPoint) return 'rgba(0, 144, 255, 0.05)';
                            // Green gradient if price is going up, red if down
                            return point.y < nextPoint.y ?
                                'rgba(0, 255, 144, 0.1)' :
                                'rgba(255, 72, 72, 0.1)';
                        },
                        borderColor: 'rgba(0, 144, 255, 0.2)',
                        borderWidth: 1,
                        pointRadius: 0,
                        fill: true,
                        order: 2,  // Display behind price line
                        spanGaps: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                layout: {
                    padding: {
                        top: 20,
                        right: 20,
                        bottom: 20,
                        left: 20
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute',
                            displayFormats: {
                                minute: 'HH:mm',
                                hour: 'HH:mm',
                                day: 'MMM d'
                            },
                            tooltipFormat: 'yyyy MMM d, HH:mm:ss',
                            parser: 'yyyy-MM-dd HH:mm:ss'
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false,
                            tickLength: 10
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            maxRotation: 0,
                            padding: 10,
                            font: {
                                size: 11,
                                family: "'Inter', sans-serif"
                            }
                        },
                        border: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        adapters: {
                            date: {
                                zone: 'UTC'
                            }
                        }
                    },
                    y: {
                        position: 'right',
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false,
                            tickLength: 10
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)',
                            padding: 10,
                            callback: function(value) {
                                return value.toFixed(5);
                            },
                            font: {
                                size: 11,
                                family: "'Inter', sans-serif"
                            }
                        },
                        border: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: 'rgba(255, 255, 255, 0.8)',
                        bodyColor: 'rgba(255, 255, 255, 0.8)',
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false,
                        titleFont: {
                            size: 12,
                            family: "'Inter', sans-serif"
                        },
                        bodyFont: {
                            size: 12,
                            family: "'Inter', sans-serif"
                        },
                        callbacks: {
                            title: function(context) {
                                const time = new Date(context[0].parsed.x);
                                return time.toLocaleString('en-US', {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric',
                                    hour: '2-digit',
                                    minute: '2-digit',
                                    second: '2-digit',
                                    hour12: false,
                                    timeZone: 'UTC'
                                });
                            },
                            label: function(context) {
                                const datasetLabel = context.dataset.label;
                                if (datasetLabel === 'Price Range') {
                                    const point = context.raw;
                                    const change = ((point.close - point.open) / point.open * 100).toFixed(3);
                                    const direction = change > 0 ? '▲' : change < 0 ? '▼' : '►';
                                    const color = change > 0 ? '🟢' : change < 0 ? '🔴' : '⚪';
                                    return [
                                        `${color} Change: ${direction} ${Math.abs(change)}%`,
                                        `High: ${point.y[1].toFixed(5)}`,
                                        `Low: ${point.y[0].toFixed(5)}`,
                                        `Open: ${point.open.toFixed(5)}`,
                                        `Close: ${point.close.toFixed(5)}`
                                    ];
                                }
                                const value = context.parsed.y.toFixed(5);
                                const prevValue = context.parsed.x > 0 ? 
                                    context.dataset.data[context.dataIndex - 1]?.y : null;
                                if (prevValue !== null) {
                                    const change = ((value - prevValue) / prevValue * 100).toFixed(3);
                                    const direction = change > 0 ? '▲' : change < 0 ? '▼' : '►';
                                    const color = change > 0 ? '🟢' : change < 0 ? '🔴' : '⚪';
                                    return [
                                        `${datasetLabel}: ${value}`,
                                        `${color} Change: ${direction} ${Math.abs(change)}%`
                                    ];
                                }
                                return `${datasetLabel}: ${value}`;
                            }
                        }
                    }
                }
            }
        };
    }

    async fetchData() {
        if (!this.isInitialized) return;
        
        try {
            this.showLoading();
            this.hideError();
            
            const response = await fetch(`/api/chart_data/${this.activePair}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            if (!result || !result.data || !Array.isArray(result.data) || result.data.length === 0) {
                throw new Error('No data available');
            }
            
            // Update metadata display if available
            if (result.metadata) {
                const lastUpdate = new Date(result.metadata.last_update);
                const formattedUpdate = lastUpdate.toLocaleString('en-US', {
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                    hour12: false
                });
                console.log(`Last update: ${formattedUpdate} - ${result.metadata.count} points`);
            }
            
            await this.updateChartWithData(result.data);
            this.hideLoading();
            
            // Update pair info with data type
            if (this.pairInfoEl) {
                const dataType = result.metadata?.type === 'real-time' ? '(Real-time)' : '';
                this.pairInfoEl.textContent = `${this.activePair.replace('-', '/')} ${dataType}`;
            }
        } catch (error) {
            console.error('Error fetching chart data:', error);
            this.hideLoading();
            this.showError(error.message);
            
            // Clear update interval if we can't fetch data
            if (this.updateInterval) {
                clearInterval(this.updateInterval);
                this.updateInterval = null;
            }
            
            // Try to reconnect after delay
            setTimeout(() => {
                if (!this.updateInterval && !document.hidden) {
                    console.log('Attempting to reconnect...');
                    this.startDataFeed();
                }
            }, 5000);
        }
    }

    updateChartWithData(data) {
        if (!this.chart || !Array.isArray(data) || data.length === 0) {
            console.warn('Invalid chart data received');
            return;
        }

        try {
            // Sort data by timestamp
            data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

            // Process price line data
            const priceData = data.map(entry => ({
                x: new Date(entry.timestamp),
                y: parseFloat(entry.price)
            })).filter(point => !isNaN(point.y));

            // Process price range data
            const rangeData = data.map(entry => {
                const high = parseFloat(entry.high);
                const low = parseFloat(entry.low);
                if (isNaN(high) || isNaN(low)) return null;
                return {
                    x: new Date(entry.timestamp),
                    y: [low, high],
                    open: parseFloat(entry.open),
                    close: parseFloat(entry.close)
                };
            }).filter(point => point !== null);

            if (priceData.length === 0) {
                console.warn('No valid price data points');
                return;
            }

            // Update datasets
            this.chart.data.datasets[0].data = priceData;
            this.chart.data.datasets[1].data = rangeData;

            // Get all price values for scaling
            const allPrices = [
                ...priceData.map(p => p.y),
                ...rangeData.map(p => p.y[0]), // lows
                ...rangeData.map(p => p.y[1])  // highs
            ];

            // Update time scale
            const times = priceData.map(p => p.x);
            this.chart.options.scales.x.min = Math.min(...times);
            this.chart.options.scales.x.max = Math.max(...times);

            // Update price scale with padding
            const minPrice = Math.min(...allPrices);
            const maxPrice = Math.max(...allPrices);
            const padding = (maxPrice - minPrice) * 0.1;
            this.chart.options.scales.y.min = minPrice - padding;
            this.chart.options.scales.y.max = maxPrice + padding;

            // Update without animation for performance
            this.chart.update('none');

            console.log(`Updated chart with ${priceData.length} price points and ${rangeData.length} range points`);
        } catch (error) {
            console.error('Error updating chart data:', error);
            this.showError('Failed to update chart data');
        }
    }

    async startDataFeed() {
        try {
            // Clear existing interval if any
            if (this.updateInterval) {
                clearInterval(this.updateInterval);
                this.updateInterval = null;
            }

            // Set initialized flag before fetching data
            this.isInitialized = true;

            // Initial data fetch
            await this.fetchData();

            // Start interval only if initial fetch was successful and no error is showing
            if (!this.errorEl?.classList.contains('flex')) {
                this.updateInterval = setInterval(() => {
                    if (!document.hidden) { // Only fetch if page is visible
                        this.fetchData().catch(error => {
                            console.error('Error in data feed interval:', error);
                        });
                    }
                }, this.dataUpdateInterval);

                // Handle page visibility changes
                document.addEventListener('visibilitychange', () => {
                    if (!document.hidden && !this.updateInterval) {
                        // Restart interval if page becomes visible and interval was cleared
                        this.updateInterval = setInterval(() => {
                            this.fetchData().catch(error => {
                                console.error('Error in data feed interval:', error);
                            });
                        }, this.dataUpdateInterval);
                    }
                });
            }
        } catch (error) {
            console.error('Error starting data feed:', error);
            this.showError('Failed to start data feed');
            this.isInitialized = false;
        }
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
        this.isInitialized = false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.chartManager = new ChartManager();
});
