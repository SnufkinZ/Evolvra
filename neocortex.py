import uuid # A good way to generate unique IDs for points
import json
from openai import AsyncOpenAI
from typing import List
from qdrant_client import models # Import the models for filtering
from database import redis_client, qdrant_client, persona_collection, MEMORY_COLLECTION_NAME # Import Qdrant client

class NeocortexManager:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.openai_client = AsyncOpenAI()
        # ... other initializations ...

    # --- MongoDB for persona and system state ---
    async def get_persona(self) -> dict:
        persona = await persona_collection.find_one({"user_id": self.user_id})
        return persona

    # --- Redis for Caching and Emotion ---
    async def get_emotion_state(self) -> dict:
        """Gets the current emotion state from the Redis cache."""
        state = await redis_client.get(f"user:{self.user_id}:emotion")
        return json.loads(state) if state else {"mood": "neutral", "confidence": 0.5}

    async def save_emotion_state(self, state: dict):
        """Saves the emotion state to the Redis cache with a 24h expiration."""
        await redis_client.set(f"user:{self.user_id}:emotion", json.dumps(state), ex=86400)

    # --- Vector DB Methods using Qdrant ---
    async def add_memory(self, text_summary: str):
        """Converts a memory to a vector and upserts it into Qdrant."""
        print(f"Adding new memory to Qdrant: '{text_summary}'")
        # 1. Get the embedding vector from OpenAI (same as before)
        response = await self.openai_client.embeddings.create(
            input=text_summary,
            model="text-embedding-3-small"
        )
        vector = response.data[0].embedding

        # 2. Store it in Qdrant using "upsert"
        # "upsert" will create a new point or update an existing one with the same ID
        qdrant_client.upsert(
            collection_name=MEMORY_COLLECTION_NAME,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()), # Generate a new unique ID for the point
                    vector=vector,
                    # The payload contains all the metadata we want to store and filter on
                    payload={
                        "text": text_summary,
                        "user_id": self.user_id 
                    }
                )
            ]
        )

    async def search_memories(self, query_text: str, n_results: int = 3) -> List[str]:
        """Searches for conceptually similar memories in Qdrant."""
        print(f"Searching Qdrant for memories similar to: '{query_text}'")
        # 1. Get the embedding for the query (same as before)
        response = await self.openai_client.embeddings.create(
            input=query_text,
            model="text-embedding-3-small"
        )
        query_vector = response.data[0].embedding

        # 2. Search Qdrant for the most similar memories FOR THIS USER
        # We build a filter to ensure we only search within the current user's documents
        search_results = qdrant_client.search(
            collection_name=MEMORY_COLLECTION_NAME,
            query_vector=query_vector,
            limit=n_results,
            # IMPORTANT: This filter ensures data security and privacy
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=self.user_id),
                    )
                ]
            )
        )
        
        # The actual text is in the 'payload' of the search results
        retrieved_memories = [point.payload['text'] for point in search_results]
        print(f"Found memories in Qdrant: {retrieved_memories}")
        return retrieved_memories