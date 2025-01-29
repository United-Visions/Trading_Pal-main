now lets do this for scripts that has over 400 lines dont edit the file directly, just provide the full function, route, and or sections that need to be updated like this function name of existing function"def get_broker" then the full function implemented like so "    def get_broker(self, broker_type=None):
        """Get a specific broker or the current broker"""
        try:
            if not self.brokers:
                raise ValueError("No brokers initialized. Please configure broker credentials.")
                
            if broker_type and broker_type in self.brokers:
                return self.brokers[broker_type]
                
            if self.current_broker and self.current_broker in self.brokers:
                return self.brokers[self.current_broker]
            
            # Prioritize Oanda if available
            if 'oanda' in self.brokers:
                return self.brokers['oanda']
            
            # Default to first available broker
            if self.brokers:
                first_broker = next(iter(self.brokers.values()))
                return first_broker
            
            raise ValueError("No available brokers found")
        
        except Exception as e:
            print(f"Error getting broker: {e}")
            raise
" with any new imports and pip installs bellow if needed for new functions and routes then just tell me what file to add it with the full funtion follow these instructions moving forward, but for smaller files, provide the full script editing the file directly. using the tool.