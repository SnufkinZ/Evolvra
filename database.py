import os
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
db = client["evolvra_db"]
