import json
from openai import AsyncOpenAI
from typing import List
from qdrant_client import models # Import the models for filtering
from database import redis_client, qdrant_client, MEMORY_COLLECTION_NAME # Import Qdrant client


class Emotion:
    def __init__(self, user_id: str, max_steps: int = 5):
        self.user_id = user_id
        self.max_steps = max_steps

        # --- Redis for Caching and Emotion ---
    async def get_emotion_state(self) -> dict:
        """Gets the current emotion state from the Redis cache."""
        state = await redis_client.get(f"user:{self.user_id}:emotion")
        return json.loads(state) if state else {"mood": "neutral", "confidence": 0.5}

    async def save_emotion_state(self, state: dict):
        """Saves the emotion state to the Redis cache with a 24h expiration."""
        await redis_client.set(f"user:{self.user_id}:emotion", json.dumps(state), ex=86400)

    async def update_emotion(self, feedback: str):
        """Updates the emotion state based on feedback."""
        current_state = await self.get_emotion_state()
        # Simple heuristic: positive feedback increases confidence, negative decreases
        if "good" in feedback or "great" in feedback:
            current_state["confidence"] = min(1.0, current_state["confidence"] + 0.1)
            current_state["mood"] = "happy"
        elif "bad" in feedback or "terrible" in feedback:
            current_state["confidence"] = max(0.0, current_state["confidence"] - 0.1)
            current_state["mood"] = "sad"
        else:
            current_state["mood"] = "neutral"
        await self.save_emotion_state(current_state)
        if current_state["mood"] == "angry" & current_state["mood"]["grade"]> 0.7:
            self.max_steps += 2
