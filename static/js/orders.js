class OrderManager {
    constructor() {
        this.orderForm = document.getElementById('order-parameters-form');
        this.initializeForm();
        this.setupEventListeners();
    }

    initializeForm() {
        // Create the form structure
        this.orderForm.innerHTML = `
            <div class="grid grid-cols-2 gap-4 mb-4">
                <div class="flex flex-col">
                    <label class="mb-2 text-sm">Units:</label>
                    <input type="text" name="units" class="p-2 bg-trading-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-trading-accent">
                </div>
                <div class="flex flex-col">
                    <label class="mb-2 text-sm">Instrument:</label>
                    <input type="text" name="instrument" class="p-2 bg-trading-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-trading-accent">
                </div>
                <div class="flex flex-col">
                    <label class="mb-2 text-sm">Order Type:</label>
                    <input type="text" name="type" class="p-2 bg-trading-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-trading-accent">
                </div>
                <div class="flex flex-col">
                    <label class="mb-2 text-sm">Price:</label>
                    <input type="text" name="price" class="p-2 bg-trading-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-trading-accent">
                </div>
                <div class="flex flex-col">
                    <label class="mb-2 text-sm">Take Profit Price:</label>
                    <input type="text" name="take_profit_price" class="p-2 bg-trading-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-trading-accent">
                </div>
                <div class="flex flex-col">
                    <label class="mb-2 text-sm">Stop Loss Price:</label>
                    <input type="text" name="stop_loss_price" class="p-2 bg-trading-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-trading-accent">
                </div>
                <div class="flex flex-col">
                    <label class="mb-2 text-sm">Guaranteed Stop Loss Price:</label>
                    <input type="text" name="guaranteed_stop_loss_price" class="p-2 bg-trading-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-trading-accent">
                </div>
                <div class="flex flex-col">
                    <label class="mb-2 text-sm">Trailing Stop Loss Distance:</label>
                    <input type="text" name="trailing_stop_loss_distance" class="p-2 bg-trading-dark rounded-lg focus:outline-none focus:ring-2 focus:ring-trading-accent">
                </div>
            </div>
            <button type="submit" class="w-full px-4 py-2 bg-trading-accent hover:bg-trading-hover rounded-lg transition-colors">
                Submit Order
            </button>
        `;
    }

    setupEventListeners() {
        this.orderForm.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    async handleSubmit(e) {
        e.preventDefault();
        const formData = new FormData(this.orderForm);
        
        const orderData = {
            order: {
                units: formData.get('units'),
                instrument: formData.get('instrument'),
                type: formData.get('type'),
                positionFill: 'DEFAULT'
            }
        };

        // Add conditional order parameters
        if (orderData.order.type !== 'MARKET') {
            if (formData.get('price')) {
                orderData.order.price = formData.get('price');
            }
            
            if (formData.get('take_profit_price')) {
                orderData.order.takeProfitOnFill = {
                    timeInForce: 'GTC',
                    price: formData.get('take_profit_price')
                };
            }

            if (formData.get('stop_loss_price')) {
                orderData.order.stopLossOnFill = {
                    timeInForce: 'GTC',
                    price: formData.get('stop_loss_price')
                };
            }

            if (formData.get('guaranteed_stop_loss_price')) {
                orderData.order.guaranteedStopLossOnFill = {
                    timeInForce: 'GTC',
                    price: formData.get('guaranteed_stop_loss_price')
                };
            }

            if (formData.get('trailing_stop_loss_distance')) {
                orderData.order.trailingStopLossOnFill = {
                    distance: formData.get('trailing_stop_loss_distance')
                };
            }
        }

        // Validate required fields
        const requiredFields = ['units', 'instrument', 'type'];
        for (const field of requiredFields) {
            if (!orderData.order[field]) {
                window.chatManager.addMessage(`Error: Missing required field ${field}`, 'assistant');
                return;
            }
        }

        try {
            const response = await axios.post('/api/v1/create_order', orderData);
            const assistantResponse = response.data.response;
            
            // Hide order form and show chat form
            this.orderForm.style.display = 'none';
            document.getElementById('chat-form').style.display = 'flex';
            
            // Add response to chat
            window.chatManager.addMessage(assistantResponse, 'assistant');
        } catch (error) {
            console.error('Error creating order:', error);
            window.chatManager.addMessage('Error creating order. Please try again.', 'assistant');
        }
    }

    show() {
        document.getElementById('chat-form').style.display = 'none';
        this.orderForm.style.display = 'block';
    }

    hide() {
        this.orderForm.style.display = 'none';
        document.getElementById('chat-form').style.display = 'flex';
    }
}

// Initialize order manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.orderManager = new OrderManager();
});
