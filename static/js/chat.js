class ChatManager {
    constructor() {
        this.chatHistory = document.getElementById('chat-history');
        this.chatForm = document.getElementById('chat-form');
        this.userInput = document.getElementById('user-input');
        this.conversationHistory = document.getElementById('conversation-history');
        this.newChatBtn = document.getElementById('new-chat-btn');
        this.loadingIndicator = document.getElementById('loading-indicator');
        this.orderForm = document.getElementById('order-parameters-form');
        
        this.initializeEventListeners();
        this.loadConversationHistory();
    }

    initializeEventListeners() {
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.newChatBtn.addEventListener('click', () => this.startNewChat());
        
        // Auto-resize textarea
        this.userInput.addEventListener('input', () => {
            this.userInput.style.height = 'auto';
            this.userInput.style.height = this.userInput.scrollHeight + 'px';
        });

        // Handle Ctrl+Enter for submit
        this.userInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.chatForm.dispatchEvent(new Event('submit'));
            }
        });
    }

    async handleSubmit(e) {
        e.preventDefault();
        const userText = this.sanitize(this.userInput.value);
        this.userInput.value = '';
        this.userInput.style.height = 'auto';

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

            // Handle strategy creation redirect
            if (response.data.redirect === '/backtest' && response.data.data?.strategy) {
                const strategyData = response.data.data.strategy;
                
                localStorage.setItem('strategyData', JSON.stringify({
                    name: strategyData.name,
                    description: strategyData.description,
                    code: strategyData.code,
                    currency_pair: strategyData.currency_pair,
                    timeframe: strategyData.timeframe,
                    type: strategyData.type
                }));

                this.addMessage('Redirecting to backtest page...', 'system');
                
                setTimeout(() => {
                    window.location.href = '/backtest';
                }, 1500);
            }

            // Handle order creation
            if (response.data.action === 'create_order') {
                this.chatForm.style.display = 'none';
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

    addMessage(text, role) {
        const bubble = document.createElement('div');
        bubble.className = `p-4 mb-4 rounded-lg ${this.getMessageClass(role)}`;
        
        if (role === 'system') {
            bubble.innerHTML = `
                <div class="flex items-center">
                    <div class="animate-spin mr-2">
                        <i class="fas fa-circle-notch"></i>
                    </div>
                    <div>${text}</div>
                </div>
            `;
        } else {
            bubble.innerHTML = `
                <div class="flex items-start">
                    <div class="flex-shrink-0 ${role === 'user' ? 'bg-trading-accent' : 'bg-trading-medium'} rounded-full p-2">
                        <i class="fas ${role === 'user' ? 'fa-user' : 'fa-robot'}"></i>
                    </div>
                    <div class="ml-3 overflow-x-auto">
                        <pre class="message-text whitespace-pre-wrap"><code>${text}</code></pre>
                    </div>
                </div>
            `;
        }

        this.chatHistory.appendChild(bubble);
        this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
    }

    getMessageClass(role) {
        switch(role) {
            case 'user':
                return 'bg-trading-light border-l-4 border-trading-accent';
            case 'assistant':
                return 'bg-trading-medium border-l-4 border-trading-medium';
            case 'system':
                return 'bg-trading-dark border border-trading-accent';
            default:
                return 'bg-trading-medium';
        }
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

    startNewChat() {
        if (!this.chatHistory.innerHTML.trim()) return;

        const historyButton = document.createElement('button');
        historyButton.className = 'w-full flex justify-between items-center p-2 mb-2 bg-trading-medium hover:bg-trading-light rounded transition-all';
        
        const timestamp = new Date().toLocaleTimeString();
        historyButton.innerHTML = `
            <span class="flex-grow text-center">Chat ${timestamp}</span>
            <div class="flex space-x-2">
                <i class="fas fa-edit edit-icon"></i>
                <i class="fas fa-trash delete-icon"></i>
            </div>
        `;

        historyButton.dataset.history = this.chatHistory.innerHTML;
        this.setupHistoryButtonListeners(historyButton);
        this.conversationHistory.prepend(historyButton);
        this.chatHistory.innerHTML = '';
        
        this.saveConversationToStorage();
    }

    setupHistoryButtonListeners(button) {
        button.addEventListener('click', (e) => {
            if (!e.target.classList.contains('fa-edit') && 
                !e.target.classList.contains('fa-trash')) {
                this.chatHistory.innerHTML = button.dataset.history;
            }
        });

        button.querySelector('.edit-icon').addEventListener('click', () => {
            const newName = prompt('Enter a new name for this conversation:');
            if (newName) {
                button.querySelector('span').textContent = newName;
            }
        });

        button.querySelector('.delete-icon').addEventListener('click', () => {
            if (confirm('Delete this conversation?')) {
                button.remove();
            }
        });
    }

    saveConversationToStorage() {
        const conversations = Array.from(this.conversationHistory.children).map(button => ({
            name: button.querySelector('span').textContent,
            content: button.dataset.history
        }));
        localStorage.setItem('conversations', JSON.stringify(conversations));
    }

    loadConversationHistory() {
        const saved = localStorage.getItem('conversations');
        if (saved) {
            const conversations = JSON.parse(saved);
            conversations.forEach(conv => {
                const button = document.createElement('button');
                button.className = 'w-full flex justify-between items-center p-2 mb-2 bg-trading-medium hover:bg-trading-light rounded transition-all';
                button.innerHTML = `
                    <span class="flex-grow text-center">${conv.name}</span>
                    <div class="flex space-x-2">
                        <i class="fas fa-edit edit-icon"></i>
                        <i class="fas fa-trash delete-icon"></i>
                    </div>
                `;
                button.dataset.history = conv.content;
                this.setupHistoryButtonListeners(button);
                this.conversationHistory.prepend(button);
            });
        }
    }

    showLoadingIndicator() {
        this.loadingIndicator.classList.remove('hidden');
    }

    hideLoadingIndicator() {
        this.loadingIndicator.classList.add('hidden');
    }
}

// Initialize chat manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatManager = new ChatManager();
});