# memory/workspace.py
class Memory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.is_initialized = False
        # Initialize with default/empty values
        self.persona = {}
        self.emotion_state = {"mood": "neutral", "confidence": 0.5}

    async def initialize(self):
        """The slow part: Loads all user-specific data from the database."""
        if self.is_initialized:
            return
            
        print(f"--- LAZY LOADING WORKSPACE for user {self.user_id} from DB ---")
        # --- Perform all the expensive DB calls here ---
        # self.persona = await user_profile_operations.get_persona(self.user_id)
        # self.emotion_state = await emotion_operations.get_emotion(self.user_id)
        
        self.is_initialized = True