import os
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client import AsyncQdrantClient, models # Import Qdrant classes
from dotenv import load_dotenv

load_dotenv()

# --- NoSQL DB Client (MongoDB) ---
# --- Connection Config ---
# MONGO_URI = "mongodb://localhost:27017/"
# DB_NAME = "evolvra_db"


# --- Global Async Client Instance ---
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["EvolvraMainMemory"]

# --- Collections ---
users_collection = db["users"]
tasks_collection = db["tasks"]
goals_collection = db["goals"]
persona_collection = db["persona"]
user_profiles_collection = db["user_profiles"]

# --- Redis Client ---
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# --- Vector DB Client (Qdrant) ---
# It's recommended to use the standard http client for cloud connections
QDRANT_CLUSTER_URL = os.getenv("QDRANT_CLUSTER_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
if QDRANT_CLUSTER_URL and QDRANT_API_KEY:
    try:
        qdrant_client = AsyncQdrantClient(
            url=QDRANT_CLUSTER_URL,
            api_key=QDRANT_API_KEY,
            timeout=30
        )
    except Exception as e:
        print(f"Error initializing Qdrant client: {e}")
else:
    print("QDRANT_CLUSTER_URL or QDRANT_API_KEY not set in environment variables.")
    
'''
We have to tell Qdrant the size of the vectors we'll be storing 
(1536 for OpenAI's text-embedding-3-small model) 
and the distance metric to use for calculating similarity 
(Cosine is standard for text embeddings).
'''