class ConversationMemory:
    def __init__(self):
        # Store context information for the conversation
        self.context = {}

    def set_context(self, key, value):
        # Set specific context information
        self.context[key] = value

    def get_context(self, key):
        # Retrieve context information
        return self.context.get(key, None)

    def clear_context(self, key):
        # Clear specific context information
        if key in self.context:
            del self.context[key]

    def reset(self):
        # Clear all context data
        self.context.clear()
