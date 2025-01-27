class NavigationManager {
    constructor() {
        this.menuToggle = document.getElementById('menu-toggle');
        this.sidebar = document.getElementById('sidebar');
        this.socialBtn = document.getElementById('social-btn');
        this.backtestBtn = document.getElementById('backtest-btn');
        this.mainBtn = document.getElementById('main-btn');
        
        this.setupEventListeners();
        this.setupResizeHandler();
    }

    setupEventListeners() {
        if (this.menuToggle) {
            this.menuToggle.addEventListener('click', () => this.toggleSidebar());
        }

        if (this.socialBtn) {
            this.socialBtn.addEventListener('click', () => this.navigate('/social'));
        }

        if (this.backtestBtn) {
            this.backtestBtn.addEventListener('click', () => this.navigate('/backtest'));
        }

        if (this.mainBtn) {
            this.mainBtn.addEventListener('click', () => this.navigate('/'));
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
}

document.addEventListener('DOMContentLoaded', () => {
    window.navigationManager = new NavigationManager();
});