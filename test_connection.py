import os
import asyncio
import redis.asyncio as redis
from motor.motor_asyncio import AsyncIOMotorClient
from qdrant_client import QdrantClient
from dotenv import load_dotenv

load_dotenv()

# --- Your Existing Client Setup Code ---

# --- NoSQL DB Client (MongoDB) ---
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client["EvolvraMainMemory"]

# --- Redis Client ---
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# --- Vector DB Client (Qdrant) ---
QDRANT_CLUSTER_URL = os.getenv("QDRANT_CLUSTER_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
qdrant_client = None # Initialize as None
if QDRANT_CLUSTER_URL and QDRANT_API_KEY:
    try:
        qdrant_client = QdrantClient(
            url=QDRANT_CLUSTER_URL,
            api_key=QDRANT_API_KEY,
            timeout=30
        )
    except Exception as e:
        print(f"Error initializing Qdrant client: {e}")
else:
    print("QDRANT_CLUSTER_URL or QDRANT_API_KEY not set in environment variables.")


# --- Testing Functions ---

async def test_mongodb_connection():
    """Tests the MongoDB connection by fetching server info."""
    try:
        await client.server_info()
        print("✅ MongoDB connection successful.")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")

async def test_redis_connection():
    """Tests the Redis connection using the PING command."""
    try:
        response = await redis_client.ping()
        if response:
            print("✅ Redis connection successful.")
        else:
            print("❌ Redis connection failed: Did not receive PONG.")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")

def test_qdrant_connection():
    """Tests the Qdrant connection by listing collections."""
    if not qdrant_client:
        print("❌ Qdrant client not initialized.")
        return
    try:
        # This is a lightweight operation to check connectivity
        qdrant_client.get_collections()
        print("✅ Qdrant connection successful.")
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")

async def main():
    """Runs all database connection tests."""
    print("--- Running Database Connection Tests ---")
    await test_mongodb_connection()
    await test_redis_connection()
    test_qdrant_connection() # This client is not async, so no await
    print("---------------------------------------")

    # Important: Close connections when your application shuts down
    # For this test script, we can close them here.
    await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())