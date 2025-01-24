class ChatManager {
    constructor() {
        this.chatHistory = document.getElementById('chat-history');
        this.chatForm = document.getElementById('chat-form');
        this.userInput = document.getElementById('user-input');
        this.conversationHistory = document.getElementById('conversation-history');
        this.newChatBtn = document.getElementById('new-chat-btn');
        this.loadingOverlay = document.getElementById('loading-overlay');
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.newChatBtn.addEventListener('click', () => this.startNewChat());
        
        // Add missing functionality from old chat.html
        this.chatHistory = document.getElementById('chat-history');
        this.conversationHistory = document.getElementById('conversation-history');
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

    async handleSubmit(e) {
        e.preventDefault();
        const userText = this.sanitize(this.userInput.value);
        this.userInput.value = '';

        if (!userText.trim()) return;

        this.addMessage(userText, 'user');

        if (userText.toLowerCase().includes('create a trading strategy')) {
            this.showLoadingIndicator();
            try {
                const response = await axios.post('/api/v1/query', {
                    message: userText
                });

                const assistantText = this.sanitize(response.data.response);
                this.addMessage(assistantText, 'assistant');
                
                // Navigate to backtest page with strategy details
                const strategyData = response.data.data;
                this.navigateToBacktestPage(strategyData);

            } catch (error) {
                console.error('Error:', error);
                this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
            } finally {
                this.hideLoadingIndicator();
            }
            return;
        }

        try {
            const response = await axios.post('/api/v1/query', {
                message: userText
            });

            // Handle both direct responses and tool-assisted responses
            const assistantText = this.sanitize(response.data.response);
            this.addMessage(assistantText, 'assistant');
            
            // Store the conversation
            await this.saveConversation(userText, assistantText);

        } catch (error) {
            console.error('Error:', error);
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    }

    addMessage(text, role) {
        const bubble = document.createElement('div');
        bubble.className = `${role}-message`;
        bubble.innerHTML = `
            <div class="${role}-bubble">
                <pre class="message-text"><code>${text}</code></pre>
            </div>
        `;
        this.chatHistory.appendChild(bubble);
        this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
    }

    async saveConversation(message, response) {
        try {
            await axios.post('/api/v1/store_conversation', {
                user_id: 1, // This should be dynamic based on logged in user
                conversation_data: [
                    { content: message, response: response }
                ]
            });
        } catch (error) {
            console.error('Failed to save conversation:', error);
        }
    }

    startNewChat() {
        const chatHistoryContent = this.chatHistory.innerHTML;
        if (!chatHistoryContent.trim()) return;

        const historyButton = document.createElement('button');
        historyButton.className = 'history-button w-full flex justify-between items-center p-2 mb-2 bg-trading-medium hover:bg-trading-light rounded transition-all';
        
        const timestamp = new Date().toLocaleTimeString();
        historyButton.innerHTML = `
            <span class="flex-grow text-center">Conversation ${timestamp}</span>
            <div class="flex space-x-2">
                <i class="fas fa-edit edit-icon"></i>
                <i class="fas fa-trash delete-icon"></i>
            </div>
        `;

        historyButton.dataset.history = chatHistoryContent;
        
        this.setupHistoryButtonListeners(historyButton);
        this.conversationHistory.prepend(historyButton);
        this.chatHistory.innerHTML = '';
    }

    setupHistoryButtonListeners(button) {
        const editIcon = button.querySelector('.edit-icon');
        const deleteIcon = button.querySelector('.delete-icon');

        button.addEventListener('click', (e) => {
            if (!e.target.classList.contains('fa-edit') && 
                !e.target.classList.contains('fa-trash')) {
                this.chatHistory.innerHTML = button.dataset.history;
            }
        });

        editIcon.addEventListener('click', (e) => {
            const newName = prompt('Enter a new name for the conversation:');
            if (newName) {
                button.querySelector('span').textContent = newName;
            }
        });

        deleteIcon.addEventListener('click', () => {
            if (confirm('Are you sure you want to delete this conversation?')) {
                button.remove();
            }
        });
    }

    showLoadingIndicator() {
        this.loadingOverlay.style.display = 'block';
    }

    hideLoadingIndicator() {
        this.loadingOverlay.style.display = 'none';
    }

    navigateToBacktestPage(strategyData) {
        // Store strategy data in local storage
        localStorage.setItem('strategyData', JSON.stringify(strategyData));
        // Navigate to backtest page
        window.location.href = '/backtest';
    }
}

// Initialize chat manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatManager = new ChatManager();
});
