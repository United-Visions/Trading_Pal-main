document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const socialBtn = document.getElementById('social-btn');
    const backtestBtn = document.getElementById('backtest-btn');

    // Toggle sidebar on mobile
    menuToggle.addEventListener('click', () => {
        sidebar.classList.toggle('-translate-x-full');
    });

    // Handle social button click
    socialBtn.addEventListener('click', () => {
        window.location.href = '/social';
    });

    // Handle backtest button click
    if (backtestBtn) {
        backtestBtn.addEventListener('click', () => {
            window.location.href = '/backtest';
        });
    }

    // Add handler for main button if it exists
    const mainBtn = document.getElementById('main-btn');
    if (mainBtn) {
        mainBtn.addEventListener('click', () => {
            window.location.href = '/';
        });
    }

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth < 1024) {  // lg breakpoint
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.add('-translate-x-full');
            }
        }
    });
});
