import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

MONGO_URI = "mongodb://localhost:27017/"

# We put all operations unctions into an async main function
async def main():
    try:
        # 1. Create an async client instance
        client = AsyncIOMotorClient(MONGO_URI)

        # 2. Check the connection
        await client.admin.command('ping')
        #If the last line does not raise an exception, next line will be executed.
        print("✅ MongoDB async connection successful!")

        # 3. Select the database and collection
        db = client["evolvra_db"]
        print(f"✅ Successfully selected database: '{db.name}'")
        
        tasks_collection = db["task"]
        print(f"✅ Successfully selected collection: '{tasks_collection.name}'")

    except ConnectionFailure as e:
        print(f"❌ Could not connect to MongoDB: {e}")
    except Exception as e:
        print(f"❗ An error occurred: {e}")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())