# input_handler.py

from words import trading_keywords, endpoint_phrases

def is_trading_related(user_input):
    # Convert the user's input to lowercase
    user_input = user_input.lower()

    # Check if any of the trading keywords are in the user's input
    for keyword in trading_keywords:
        if keyword in user_input:
            return True

def handle_input(user_input, endpoint_phrases):
    # Check for trading-related input first
    if not is_trading_related(user_input):
        return "non_trading_input"
    
    # Then check for specific commands, as specified in endpoint_phrases
    for command, phrase_list in endpoint_phrases.items():
        for phrase in phrase_list:
            if phrase in user_input:
                return command
    # If no specific command was found, consider it a general trading inquiry
    return "general_trading_inquiry"
