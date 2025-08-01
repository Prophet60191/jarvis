"""Context module for Jarvis."""

class Context:
    """Context class for managing Jarvis session state."""
    
    def __init__(self, session_id: str):
        """Initialize a new Context.
        
        Args:
            session_id (str): Unique identifier for this context session
        """
        self.session_id = session_id
        self.state = {}
        
    def get_state(self, key: str, default=None):
        """Get a value from the context state.
        
        Args:
            key (str): Key to look up
            default: Value to return if key not found
            
        Returns:
            Value associated with key or default if not found
        """
        return self.state.get(key, default)
        
    def set_state(self, key: str, value):
        """Set a value in the context state.
        
        Args:
            key (str): Key to store value under
            value: Value to store
        """
        self.state[key] = value
        
    def to_dict(self):
        """Convert context to dictionary representation.
        
        Returns:
            dict: Dictionary containing context data
        """
        return {
            'session_id': self.session_id,
            'state': self.state
        }
