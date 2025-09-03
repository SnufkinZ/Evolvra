from motor.motor_asyncio import AsyncIOMotorClient

# --- Connection Config ---
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "evolvra_db"

# --- Global Async Client Instance ---
client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

# --- Collections ---
users_collection = db["users"]
tasks_collection = db["tasks"]
goals_collection = db["goals"]
user_profiles_collection = db["user_profiles"]