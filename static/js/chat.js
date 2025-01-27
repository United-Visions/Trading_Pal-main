class ChatManager {
    constructor() {
        this.elements = {
            chatHistory: document.getElementById('chat-history'),
            chatForm: document.getElementById('chat-form'),
            userInput: document.getElementById('user-input'),
            conversationHistory: document.getElementById('conversation-history'),
            newChatBtn: document.getElementById('new-chat-btn'),
            loadingIndicator: document.getElementById('loading-indicator'),
            orderForm: document.getElementById('order-parameters-form')
        };
        
        this.initializeEventListeners();
        this.loadConversationHistory();
    }

    initializeEventListeners() {
        this.elements.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.elements.newChatBtn.addEventListener('click', () => this.startNewChat());
        
        this.elements.userInput.addEventListener('input', () => {
            gsap.to(this.elements.userInput, {
                height: 'auto',
                duration: 0.2
            });
            gsap.to(this.elements.userInput, {
                height: this.elements.userInput.scrollHeight,
                duration: 0.2
            });
        });

        this.elements.userInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.elements.chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    loadConversationHistory() {
        // Define the method to load conversation history
        console.log('Loading conversation history...');
        // Implementation here...
    }

    async handleSubmit(e) {
        e.preventDefault();
        const userText = this.sanitize(this.elements.userInput.value);
        this.elements.userInput.value = '';
        gsap.to(this.elements.userInput, {
            height: 'auto',
            duration: 0.2
        });

        if (!userText.trim()) return;

        this.addMessage(userText, 'user');
        this.showLoadingIndicator();

        try {
            const response = await axios.post('/api/v1/query', {
                message: userText
            });

            if (response.data.error) {
                this.addMessage(`Error: ${response.data.error}`, 'assistant');
                return;
            }

            const assistantText = this.sanitize(response.data.response);
            this.addMessage(assistantText, 'assistant');

            if (response.data.redirect === '/backtest' && response.data.data?.strategy) {
                const strategyData = response.data.data.strategy;
                localStorage.setItem('strategyData', JSON.stringify(strategyData));
                this.addMessage('Redirecting to backtest page...', 'system');
                
                gsap.to(this.elements.chatHistory, {
                    opacity: 0,
                    y: -20,
                    duration: 0.3,
                    onComplete: () => {
                        window.location.href = '/backtest';
                    }
                });
            }

            if (response.data.action === 'create_order') {
                gsap.to(this.elements.chatForm, {
                    display: 'none',
                    duration: 0.3
                });
                window.orderManager.show();
            }

            await this.saveConversation(userText, assistantText);

        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        } finally {
            this.hideLoadingIndicator();
        }
    }

    addMessage(text, role) {
        const bubble = document.createElement('div');
        bubble.className = `p-4 mb-4 rounded-xl ${this.getMessageClass(role)}`;
        
        if (role === 'system') {
            bubble.innerHTML = `
                <div class="flex items-center">
                    <div class="animate-spin mr-2">
                        <i class="fas fa-circle-notch text-primary-400"></i>
                    </div>
                    <div>${text}</div>
                </div>
            `;
        } else {
            bubble.innerHTML = `
                <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0 w-8 h-8 rounded-lg ${role === 'user' ? 'bg-primary-500' : 'bg-secondary-500'} 
                         flex items-center justify-center">
                        <i class="fas ${role === 'user' ? 'fa-user' : 'fa-robot'}"></i>
                    </div>
                    <div class="flex-grow overflow-x-auto">
                        <pre class="message-text whitespace-pre-wrap"><code>${text}</code></pre>
                    </div>
                </div>
            `;
        }

        gsap.set(bubble, { opacity: 0, y: 20 });
        this.elements.chatHistory.appendChild(bubble);
        this.elements.chatHistory.scrollTop = this.elements.chatHistory.scrollHeight;

        gsap.to(bubble, {
            opacity: 1,
            y: 0,
            duration: 0.3,
            ease: 'power2.out'
        });
    }

    getMessageClass(role) {
        const classes = {
            user: 'bg-dark-800/50 border-l-4 border-primary-500',
            assistant: 'bg-dark-800/30 border-l-4 border-secondary-500',
            system: 'bg-dark-800/20 border border-primary-500/20'
        };
        return classes[role] || classes.assistant;
    }

    startNewChat() {
        if (!this.elements.chatHistory.innerHTML.trim()) return;

        const historyButton = document.createElement('button');
        historyButton.className = 'w-full flex justify-between items-center p-3 mb-2 rounded-xl ' +
                                'bg-dark-800/30 hover:bg-dark-800/50 transition-all duration-300';
        
        const timestamp = new Date().toLocaleTimeString();
        historyButton.innerHTML = `
            <span class="flex-grow text-center text-dark-200">${timestamp}</span>
            <div class="flex space-x-2">
                <i class="fas fa-edit text-primary-400 edit-icon cursor-pointer"></i>
                <i class="fas fa-trash text-danger-500 delete-icon cursor-pointer"></i>
            </div>
        `;

        historyButton.dataset.history = this.elements.chatHistory.innerHTML;
        this.setupHistoryButtonListeners(historyButton);
        
        gsap.set(historyButton, { opacity: 0, y: -20 });
        this.elements.conversationHistory.prepend(historyButton);
        gsap.to(historyButton, {
            opacity: 1,
            y: 0,
            duration: 0.3
        });

        gsap.to(this.elements.chatHistory, {
            opacity: 0,
            duration: 0.3,
            onComplete: () => {
                this.elements.chatHistory.innerHTML = '';
                gsap.to(this.elements.chatHistory, {
                    opacity: 1,
                    duration: 0.3
                });
            }
        });
        
        this.saveConversationToStorage();
    }

    setupHistoryButtonListeners(button) {
        button.addEventListener('click', (e) => {
            if (!e.target.classList.contains('fa-edit') && 
                !e.target.classList.contains('fa-trash')) {
                gsap.to(this.elements.chatHistory, {
                    opacity: 0,
                    duration: 0.3,
                    onComplete: () => {
                        this.elements.chatHistory.innerHTML = button.dataset.history;
                        gsap.to(this.elements.chatHistory, {
                            opacity: 1,
                            duration: 0.3
                        });
                    }
                });
            }
        });

        button.querySelector('.edit-icon').addEventListener('click', () => {
            const newName = prompt('Enter a new name for this conversation:');
            if (newName) {
                gsap.to(button.querySelector('span'), {
                    opacity: 0,
                    duration: 0.2,
                    onComplete: () => {
                        button.querySelector('span').textContent = newName;
                        gsap.to(button.querySelector('span'), {
                            opacity: 1,
                            duration: 0.2
                        });
                    }
                });
            }
        });

        button.querySelector('.delete-icon').addEventListener('click', () => {
            if (confirm('Delete this conversation?')) {
                gsap.to(button, {
                    opacity: 0,
                    y: -20,
                    duration: 0.3,
                    onComplete: () => button.remove()
                });
            }
        });
    }

    sanitize(input) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(input).replace(/[&<>"']/g, (m) => map[m]);
    }

    async saveConversation(message, response) {
        try {
            await axios.post('/api/v1/store_conversation', {
                conversation_data: [{
                    content: message,
                    response: response,
                    timestamp: new Date().toISOString()
                }]
            });
        } catch (error) {
            console.error('Failed to save conversation:', error);
        }
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
}

document.addEventListener('DOMContentLoaded', () => {
    window.chatManager = new ChatManager();
});