class OrderManager {
    constructor() {
        this.orderForm = document.getElementById('order-parameters-form');
        this.initializeForm();
        this.setupEventListeners();
    }

    initializeForm() {
        this.orderForm.innerHTML = `
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-dark-200">Units</label>
                    <input type="text" name="units" 
                           class="w-full p-3 bg-dark-800/50 rounded-xl border border-dark-700 
                                  text-white focus:border-primary-500 focus:ring-2 
                                  focus:ring-primary-500/20 focus:outline-none transition-all duration-300">
                </div>
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-dark-200">Instrument</label>
                    <input type="text" name="instrument" 
                           class="w-full p-3 bg-dark-800/50 rounded-xl border border-dark-700 
                                  text-white focus:border-primary-500 focus:ring-2 
                                  focus:ring-primary-500/20 focus:outline-none transition-all duration-300">
                </div>
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-dark-200">Order Type</label>
                    <select name="type" 
                            class="w-full p-3 bg-dark-800/50 rounded-xl border border-dark-700 
                                   text-white focus:border-primary-500 focus:ring-2 
                                   focus:ring-primary-500/20 focus:outline-none transition-all duration-300">
                        <option value="MARKET">Market</option>
                        <option value="LIMIT">Limit</option>
                        <option value="STOP">Stop</option>
                    </select>
                </div>
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-dark-200">Price</label>
                    <input type="text" name="price" 
                           class="w-full p-3 bg-dark-800/50 rounded-xl border border-dark-700 
                                  text-white focus:border-primary-500 focus:ring-2 
                                  focus:ring-primary-500/20 focus:outline-none transition-all duration-300">
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-dark-200">Take Profit</label>
                    <input type="text" name="take_profit_price" 
                           class="w-full p-3 bg-dark-800/50 rounded-xl border border-dark-700 
                                  text-white focus:border-primary-500 focus:ring-2 
                                  focus:ring-primary-500/20 focus:outline-none transition-all duration-300">
                </div>
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-dark-200">Stop Loss</label>
                    <input type="text" name="stop_loss_price" 
                           class="w-full p-3 bg-dark-800/50 rounded-xl border border-dark-700 
                                  text-white focus:border-primary-500 focus:ring-2 
                                  focus:ring-primary-500/20 focus:outline-none transition-all duration-300">
                </div>
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-dark-200">Guaranteed Stop Loss</label>
                    <input type="text" name="guaranteed_stop_loss_price" 
                           class="w-full p-3 bg-dark-800/50 rounded-xl border border-dark-700 
                                  text-white focus:border-primary-500 focus:ring-2 
                                  focus:ring-primary-500/20 focus:outline-none transition-all duration-300">
                </div>
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-dark-200">Trailing Stop Distance</label>
                    <input type="text" name="trailing_stop_loss_distance" 
                           class="w-full p-3 bg-dark-800/50 rounded-xl border border-dark-700 
                                  text-white focus:border-primary-500 focus:ring-2 
                                  focus:ring-primary-500/20 focus:outline-none transition-all duration-300">
                </div>
            </div>

            <button type="submit" 
                    class="w-full py-3 px-4 rounded-xl font-medium transition-all duration-300
                           bg-gradient-to-r from-primary-600 to-secondary-600 
                           hover:from-primary-500 hover:to-secondary-500
                           focus:ring-2 focus:ring-primary-500/20 focus:outline-none group">
                <div class="flex items-center justify-center space-x-2">
                    <span>Submit Order</span>
                    <i class="fas fa-arrow-right transition-transform group-hover:translate-x-1"></i>
                </div>
            </button>
        `;
    }

    setupEventListeners() {
        this.orderForm.addEventListener('submit', (e) => this.handleSubmit(e));
        
        const typeSelect = this.orderForm.querySelector('[name="type"]');
        typeSelect.addEventListener('change', () => this.togglePriceField(typeSelect.value));
        
        // Add input validation animations
        this.orderForm.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', () => this.validateInput(input));
        });
    }

    validateInput(input) {
        const isValid = input.value.trim() !== '';
        gsap.to(input, {
            borderColor: isValid ? 'rgba(0, 144, 255, 0.5)' : 'rgba(239, 68, 68, 0.5)',
            duration: 0.3
        });
    }

    togglePriceField(orderType) {
        const priceField = this.orderForm.querySelector('[name="price"]').parentElement;
        gsap.to(priceField, {
            opacity: orderType !== 'MARKET' ? 1 : 0.5,
            duration: 0.3
        });
        priceField.querySelector('input').disabled = orderType === 'MARKET';
    }

    async handleSubmit(e) {
        e.preventDefault();
        const formData = new FormData(this.orderForm);
        const submitButton = this.orderForm.querySelector('button[type="submit"]');
        
        const orderData = {
            order: {
                units: formData.get('units'),
                instrument: formData.get('instrument'),
                type: formData.get('type'),
                positionFill: 'DEFAULT'
            }
        };

        if (orderData.order.type !== 'MARKET') {
            if (formData.get('price')) {
                orderData.order.price = formData.get('price');
            }
        }

        this.addOrderParameters(orderData, formData);

        try {
            gsap.to(submitButton, {
                scale: 0.95,
                duration: 0.2
            });
            
            const response = await axios.post('/api/v1/create_order', orderData);
            const assistantResponse = response.data.response;
            
            gsap.to(this.orderForm, {
                opacity: 0,
                y: -20,
                duration: 0.3,
                onComplete: () => {
                    this.orderForm.style.display = 'none';
                    document.getElementById('chat-form').style.display = 'flex';
                    gsap.from(document.getElementById('chat-form'), {
                        opacity: 0,
                        y: 20,
                        duration: 0.3
                    });
                }
            });
            
            window.chatManager.addMessage(assistantResponse, 'assistant');
            
        } catch (error) {
            this.showError('Error creating order. Please try again.');
            console.error('Error creating order:', error);
        } finally {
            gsap.to(submitButton, {
                scale: 1,
                duration: 0.2
            });
        }
    }

    addOrderParameters(orderData, formData) {
        const parameters = {
            'take_profit_price': 'takeProfitOnFill',
            'stop_loss_price': 'stopLossOnFill',
            'guaranteed_stop_loss_price': 'guaranteedStopLossOnFill',
            'trailing_stop_loss_distance': 'trailingStopLossOnFill'
        };

        for (const [param, orderKey] of Object.entries(parameters)) {
            const value = formData.get(param);
            if (value) {
                orderData.order[orderKey] = {
                    price: value,
                    timeInForce: 'GTC'
                };
            }
        }
    }

    show() {
        gsap.set(this.orderForm, {
            display: 'block',
            opacity: 0,
            y: 20
        });
        gsap.to(this.orderForm, {
            opacity: 1,
            y: 0,
            duration: 0.3
        });
    }

    hide() {
        gsap.to(this.orderForm, {
            opacity: 0,
            y: -20,
            duration: 0.3,
            onComplete: () => {
                this.orderForm.style.display = 'none';
                document.getElementById('chat-form').style.display = 'flex';
            }
        });
    }

    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'fixed bottom-4 right-4 bg-gradient-to-r from-danger-500 to-danger-600 ' +
                           'text-white px-6 py-3 rounded-xl shadow-lg z-50';
        errorDiv.textContent = message;
        
        gsap.set(errorDiv, {
            opacity: 0,
            y: 20
        });
        
        document.body.appendChild(errorDiv);
        
        gsap.to(errorDiv, {
            opacity: 1,
            y: 0,
            duration: 0.3,
            ease: 'power2.out'
        });

        setTimeout(() => {
            gsap.to(errorDiv, {
                opacity: 0,
                y: 20,
                duration: 0.3,
                ease: 'power2.in',
                onComplete: () => errorDiv.remove()
            });
        }, 5000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.orderManager = new OrderManager();
});