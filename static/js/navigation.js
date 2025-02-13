class NavigationManager {
    constructor() {
        this.menuToggle = document.getElementById('menu-toggle');
        this.sidebar = document.getElementById('sidebar');
        this.chartsTab = document.getElementById('charts-tab');
        this.chartsContainer = document.getElementById('charts-container');
        this.closeChartsBtn = document.getElementById('close-charts');
        
        this.setupEventListeners();
        this.setupResizeHandler();
        this.setupChartHandlers();
    }

    setupChartHandlers() {
        console.log('Setting up chart handlers');
        
        if (this.chartsTab) {
            this.chartsTab.addEventListener('click', () => {
                console.log('Charts tab clicked');
                if (this.chartsContainer) {
                    const isHidden = this.chartsContainer.classList.contains('hidden');
                    
                    if (isHidden) {
                        this.chartsContainer.classList.remove('hidden');
                        this.chartsContainer.classList.add('w-full');
                        if (window.chartManager) {
                            window.chartManager.initializeChart();
                        }
                    } else {
                        this.chartsContainer.classList.add('hidden');
                        this.chartsContainer.classList.remove('w-full');
                    }
                } else {
                    console.error('Charts container not found');
                }
            });
        }

        if (this.closeChartsBtn) {
            this.closeChartsBtn.addEventListener('click', () => {
                console.log('Close charts clicked');
                this.chartsContainer.classList.add('hidden');
                this.chartsContainer.classList.remove('w-full');
            });
        }
    }

    setupResizeHandler() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                if (window.innerWidth >= 1024) {
                    this.sidebar.classList.remove('-translate-x-full');
                }
            }, 250);
        });
    }

    setupEventListeners() {
        if (this.menuToggle) {
            this.menuToggle.addEventListener('click', () => this.toggleSidebar());
        }

        document.addEventListener('click', (e) => this.handleOutsideClick(e));
    }

    toggleSidebar() {
        this.sidebar.classList.toggle('-translate-x-full');
    }

    handleOutsideClick(e) {
        if (window.innerWidth < 1024) {
            const isOutside = !this.sidebar?.contains(e.target) && !this.menuToggle?.contains(e.target);
            if (isOutside && !this.sidebar?.classList.contains('-translate-x-full')) {
                this.sidebar.classList.add('-translate-x-full');
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing NavigationManager');
    window.navigationManager = new NavigationManager();
});