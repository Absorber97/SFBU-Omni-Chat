class ContextHandler:
    def __init__(self):
        self.conversation_memory = {}
        self.user_preferences = {}
        self.session_context = {}
        
    def track_conversation(self, user_id, message):
        # Track conversation history
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = []
        self.conversation_memory[user_id].append(message)
        
    def get_relevant_context(self, user_id, query):
        # Retrieve relevant context from conversation history
        return self.conversation_memory.get(user_id, [])[-5:]  # Last 5 messages 