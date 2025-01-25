// Broker Toggle Logic
const brokerToggles = document.querySelectorAll('.broker-toggle');
let currentBroker = localStorage.getItem('selectedBroker') || 'oanda';

function updateBrokerToggle() {
    brokerToggles.forEach(toggle => {
        toggle.classList.remove('active', 'bg-trading-accent');
        if (toggle.id.includes(currentBroker)) {
            toggle.classList.add('active', 'bg-trading-accent');
        }
    });
}

brokerToggles.forEach(toggle => {
    toggle.addEventListener('click', async () => {
        const broker = toggle.id.split('-')[0];
        if (broker !== currentBroker) {
            currentBroker = broker;
            localStorage.setItem('selectedBroker', broker);
            updateBrokerToggle();
            await loadAccountDetails();
        }
    });
});

// Settings Modal Logic
const settingsModal = document.getElementById('settings-modal');
const settingsBtn = document.getElementById('settings-btn');
const closeSettings = document.getElementById('close-settings');
const brokerSelect = document.getElementById('broker-select');
const brokerSettingsForm = document.getElementById('broker-settings-form');

settingsBtn.addEventListener('click', () => {
    settingsModal.classList.remove('hidden');
    settingsModal.classList.add('flex');
    loadBrokerSettings();
});

closeSettings.addEventListener('click', () => {
    settingsModal.classList.add('hidden');
    settingsModal.classList.remove('flex');
});

brokerSelect.addEventListener('change', () => {
    const selectedBroker = brokerSelect.value;
    document.querySelectorAll('.oanda-fields, .alpaca-fields').forEach(el => el.classList.add('hidden'));
    document.querySelector(`.${selectedBroker}-fields`).classList.remove('hidden');
});

// Modify the loadBrokerSettings function to update account manager
async function loadBrokerSettings() {
    try {
        const response = await axios.get('/api/v1/broker/settings');
        const settings = response.data;
        
        if (settings.oanda) {
            document.getElementById('oanda-api-key').value = settings.oanda.api_key || '';
            document.getElementById('oanda-account-id').value = settings.oanda.account_id || '';
        }
        
        if (settings.alpaca) {
            document.getElementById('alpaca-api-key').value = settings.alpaca.api_key || '';
            document.getElementById('alpaca-api-secret').value = settings.alpaca.api_secret || '';
        }

        // Update account details after loading settings
        if (window.accountManager) {
            window.accountManager.loadAccountDetails();
        }
    } catch (error) {
        console.error('Failed to load broker settings:', error);
    }
}

brokerSettingsForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const selectedBroker = brokerSelect.value;
    const settings = {
        broker_type: selectedBroker,
        settings: selectedBroker === 'oanda' ? {
            api_key: document.getElementById('oanda-api-key').value,
            account_id: document.getElementById('oanda-account-id').value
        } : {
            api_key: document.getElementById('alpaca-api-key').value,
            api_secret: document.getElementById('alpaca-api-secret').value
        }
    };
    
    try {
        await axios.post('/api/v1/broker/settings', settings);
        settingsModal.classList.add('hidden');
        settingsModal.classList.remove('flex');
        await loadAccountDetails();
    } catch (error) {
        alert(error.response?.data?.error || 'Failed to save settings');
    }
});

// Initialize
updateBrokerToggle();
