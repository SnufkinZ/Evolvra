from database import tasks_collection, redis_client, qdrant_client

##--- test mongodb ---
# tasks_collection.insert_one({"title":"Fuck World", "priority":1})
# print(tasks_collection.find_one({"title":"Fuck World"}))

##--- test redis ---
# import asyncio
# from redis.asyncio import from_url

# async def main():
#     await redis_client.set("foo", "bar")
#     print(await redis_client.get("foo"))

# asyncio.run(main())

##--- test Qdrant ---
# from qdrant_client import QdrantClient, models


# qdrant_client.create_collection(
#     collection_name="{collection_name}",
#     vectors_config=models.VectorParams(size=100, distance=models.Distance.COSINE),
# )

