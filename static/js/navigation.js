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

    setupEventListeners() {
        if (this.menuToggle) {
            this.menuToggle.addEventListener('click', () => this.toggleSidebar());
        }

        if (this.chartsTab) {
            this.chartsTab.addEventListener('click', () => this.toggleChartsView());
        }

        document.addEventListener('click', (e) => this.handleOutsideClick(e));
    }

    toggleSidebar() {
        const isHidden = this.sidebar.classList.contains('-translate-x-full');
        
        gsap.to(this.sidebar, {
            x: isHidden ? '0%' : '-100%',
            duration: 0.3,
            ease: 'power2.inOut'
        });

        if (isHidden) {
            gsap.from(this.sidebar, {
                opacity: 0,
                duration: 0.3
            });
        }
    }

    handleOutsideClick(e) {
        if (window.innerWidth < 1024) {
            const isOutside = !this.sidebar?.contains(e.target) && !this.menuToggle?.contains(e.target);
            if (isOutside && !this.sidebar?.classList.contains('-translate-x-full')) {
                gsap.to(this.sidebar, {
                    x: '-100%',
                    duration: 0.3,
                    ease: 'power2.inOut'
                });
            }
        }
    }

    navigate(path) {
        gsap.to('body', {
            opacity: 0,
            duration: 0.3,
            onComplete: () => {
                window.location.href = path;
            }
        });
    }

    setupResizeHandler() {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                if (window.innerWidth >= 1024) {
                    gsap.set(this.sidebar, {
                        x: '0%',
                        clearProps: 'all'
                    });
                }
            }, 250);
        });
    }

    setupChartHandlers() {
        const chartsTab = document.getElementById('charts-tab');
        const chartsContainer = document.getElementById('charts-container');
        const closeChartsBtn = document.getElementById('close-charts');

        if (chartsTab) {
            chartsTab.addEventListener('click', () => {
                console.log('Charts tab clicked');  // Debug log
                const container = document.getElementById('charts-container');
                const currentWidth = container.style.width;
                
                if (currentWidth === '0px' || !currentWidth) {
                    container.style.width = '50%';
                    if (window.chartManager) {
                        window.chartManager.refreshCharts?.();
                    }
                } else {
                    container.style.width = '0px';
                }
            });
        }

        if (closeChartsBtn) {
            closeChartsBtn.addEventListener('click', () => {
                console.log('Close charts clicked');  // Debug log
                chartsContainer.style.width = '0px';
            });
        }
    }

    toggleChartsView() {
        if (this.chartsContainer.classList.contains('w-0')) {
            this.openChartsView();
        } else {
            this.closeChartsView();
        }
    }

    openChartsView() {
        // Use a more modest default width
        this.chartsContainer.style.width = '400px';
        // Trigger chart refresh
        if (window.chartManager) {
            window.chartManager.updateChart();
        }
    }

    closeChartsView() {
        this.chartsContainer.classList.remove('w-[600px]');
        this.chartsContainer.classList.add('w-0');
    }
}

// Initialize navigation
document.addEventListener('DOMContentLoaded', () => {
    window.navigationManager = new NavigationManager();
});