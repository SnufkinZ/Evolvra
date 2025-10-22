import json
import os
from openai import AsyncOpenAI
from qdrant_client import models

# 假设你的数据库客户端已经初始化
from database import redis_client, qdrant_client, db
from system_tools import get_current_time

class GlobalWorkspace:
    def __init__(self, user_id: str):
        self.user_id = user_id
        
        # --- 数据库与服务客户端 ---
        self.redis = redis_client
        self.qdrant = qdrant_client
        self.mongo_personas = db.get_collection("personas")
        self.mongo_emotions = db.get_collection("emotions")
        self.mongo_main_memory = db.get_collection("main_memory")

        # --- 新增: OpenAI 客户端 ---
        # 它会自动从环境变量中读取 OPENAI_API_KEY
        self.openai_client = AsyncOpenAI() 
        
        # --- 新增: Qdrant Collection Name ---
        # 将集合名称定义在这里，方便未来修改
        self.qdrant_relevant_memory = f"memories-{self.user_id}"

        # --- 用户状态 (这些只是临时容器, 真实数据在数据库中) ---
        self.persona: dict = {}
        self.context: list = []
        self.emotion: dict = {}
        self.main_memory: list = []
        self.working_memory: list = [] # V2: 名字改为 'working_memory' 更清晰
    
    # ... (你其他的 save 和 load 方法保持不变) ...

    async def save_persona_to_Mongo(self):
        """将当前persona保存到MongoDB"""
        await self.mongo_personas.update_one(
            {"user_id": self.user_id},
            {"$set": {"user_id":self.user_id, "persona": self.persona}},
            upsert=True
        )

    async def save_main_memory_to_Mongo(self):
        """将当前main_memory保存到MongoDB"""
        await self.mongo_main_memory.update_one(
            {"user_id": self.user_id},
            {"$set": {"user_id":self.user_id, "memories": self.main_memory}},
            upsert=True
        )

    async def load(self):
        """
        V2: [核心方法] 从数据库加载用户的完整状态到这个对象中。
        在处理每个请求的最开始调用。
        """
        # 1. 加载 Persona (不常变，直接读Mongo)
        persona_data = await self.mongo_personas.find_one({"user_id": self.user_id})
        if persona_data:
            persona_data.pop("_id", None)  # 移除 MongoDB 自动添加的 _id 字段
            self.persona = persona_data
        else:
            self.persona = {
                "user_id": self.user_id,
                "name": "Evolvra",
                "age": 18,
                "gender": "female",
                "description": "You are a young girl who loves adventures and exploring new things.",
                "traits": ["curious", "brave", "kind"],
                "background": "You grew up in a small village but dreams of seeing the world.",
                "goals": ["Travel the world", "Make new friends", "Learn about different cultures"]
            }
            # 修复: 之前这里的调用缺少 await
            await self.save_persona_to_Mongo()

        # 2. 加载 Emotion (长期记忆, Mongo为主, Redis为缓存)
        emotion_cache = await self.redis.get(f"user:{self.user_id}:emotion")
        if emotion_cache:
            self.emotion = json.loads(emotion_cache)
        else:
            emotion_data = await self.mongo_emotions.find_one({"user_id": self.user_id})
            if emotion_data:
                emotion_data.pop("_id", None)
                self.emotion = emotion_data
            else:
                self.emotion = {"mood": "happy", "confidence": 0.6, "energy": 10, "heartfelt": "You was born in this world!"}
            await self.redis.set(f"user:{self.user_id}:emotion", json.dumps(self.emotion), ex=3600) 

        # 3. 加载当前对话上下文 (短期记忆, 只存在于Redis)
        context_data = await self.redis.get(f"user:{self.user_id}:context")
        self.context = json.loads(context_data) if context_data else []
        # self.context = []  # 每次新请求开始时清空上下文, ONLY FOR TESTING PURPOSES!!!!!!!!!!!!!!!!!!!

        # 4. Load main_memory
        main_memory_cache = await self.redis.get(f"user:{self.user_id}:main_memory")
        if main_memory_cache:
            self.main_memory = json.loads(main_memory_cache)
        else:
            main_memory_data_doc = await self.mongo_main_memory.find_one({"user_id": self.user_id})
            if main_memory_data_doc and "memories" in main_memory_data_doc:
                self.main_memory = main_memory_data_doc["memories"]
            else:
                print(f"No main memory found for new user {self.user_id}. Initializing.")
                current_time = get_current_time()
                default_memory = [
                    f"{current_time}: Today is my birthday ^_^",
                    f"{current_time}: Energy represents the maximum number of thinking steps I can take."
                ]
                self.main_memory = default_memory
                await self.save_main_memory_to_Mongo() 
            await self.redis.set(f"user:{self.user_id}:main_memory", json.dumps(self.main_memory), ex=3600)

            # --- 新增: 检查并创建 Qdrant Collection ---
        try:
            # 尝试获取集合信息，如果不存在会抛出异常
            await self.qdrant.get_collection(collection_name=self.qdrant_relevant_memory)
            print(f"Qdrant collection '{self.qdrant_relevant_memory}' already exists.")
        except Exception:
            print(f"Qdrant collection '{self.qdrant_relevant_memory}' not found. Creating...")
            # 创建集合
            await self.qdrant.create_collection(
                collection_name=self.qdrant_relevant_memory,
                vectors_config=models.VectorParams(
                    size=1536,  # OpenAI text-embedding-3-small 的维度
                    distance=models.Distance.COSINE
                ),
            )
            print(f"Collection '{self.qdrant_relevant_memory}' created successfully.")
        # --- 新增结束 ---

        print(f"Workspace for user {self.user_id} loaded.")
        return self

    async def save(self):
        """
        V2: [核心方法] 将当前对象中的状态保存回数据库。
        在处理每个请求结束后调用。
        """
        pipe = self.redis.pipeline()
        pipe.set(f"user:{self.user_id}:emotion", json.dumps(self.emotion))
        pipe.set(f"user:{self.user_id}:main_memory", json.dumps(self.main_memory))
        await self.mongo_emotions.update_one(
            {"user_id": self.user_id},
            {"$set": self.emotion},
            upsert=True
        )
        await self.mongo_main_memory.update_one(
            {"user_id": self.user_id},
            {"$set": {"memories": self.main_memory}},
            upsert=True
        )
        await pipe.execute()

        if self.context:
            await self.redis.set(f"user:{self.user_id}:context", json.dumps(self.context), ex=1800)
            print(f"Context for user {self.user_id} saved with {len(self.context)} messages.")
        else:
            await self.redis.delete(f"user:{self.user_id}:context")
            
        print(f"Workspace for user {self.user_id} saved.")

    # --- 私有辅助方法 ---
    async def _get_embedding(self, text: str) -> list[float]:
        """使用OpenAI模型为文本创建embedding向量"""
        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    # --- 核心操作方法 ---
    async def add_relevant_memories_to_work(self, user_message: str, top_k: int = 5):
        """
        从Qdrant中搜索相关记忆并更新工作记忆 (working_memory)。
        """
        print(f"Searching for memories related to: '{user_message}'")
        try:
            # 1. 将用户输入文本转换为向量
            query_vector = await self._get_embedding(user_message)

            # 2. 使用正确的 .search() 方法和参数进行搜索
            search_result = await self.qdrant.search(
                collection_name=self.qdrant_relevant_memory,
                query_vector=query_vector,
                limit=top_k
            )

            # 3. 从搜索结果中提取记忆内容
            # Qdrant返回的每个hit都有一个payload，我们假设记忆文本存储在payload的'text'字段中
            relevant_memories = [
                hit.payload['text'] for hit in search_result if 'text' in hit.payload
            ]
            
            # 4. 将提取到的记忆列表赋值给工作记忆
            self.working_memory = relevant_memories
            print(f"Found {len(self.working_memory)} relevant memories.")

        except Exception as e:
            print(f"An error occurred during memory search: {e}")
            # 出错时，将工作记忆清空，避免使用错误或过时的信息
            self.working_memory = []

    # ... (你其他的 add_to_context, get_context 等方法保持不变) ...

    def add_to_context(self, message: dict):
        self.context.append(message)

    def get_context(self) -> list:
        return self.context

    def clear_context(self):
        self.context = []

    def set_emotion(self, mood: str, confidence: float, energy: float, heartfelt: str = ""):
        self.emotion['mood'] = mood
        self.emotion['confidence'] = confidence
        self.emotion['energy'] = energy
        self.emotion['heartfelt'] = heartfelt
    
    def get_emotion(self) -> dict:
        return self.emotion