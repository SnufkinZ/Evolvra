from fastapi import APIRouter, HTTPException
from models.task import Task
from models.chat import ChatMessage
from database import db
from main import main

router = APIRouter()

@router.post("/tasks")
async def create_task(task: Task):
    task_dict = task.dict()
    await db["tasks"].insert_one(task_dict)
    return {"msg": "Task created"}

@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = await db["tasks"].find_one({"task_id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task["_id"]=str(task["_id"])  # Convert ObjectId to string
    return task

@router.post("/ChartMessages")
async def create_chat_message(chat_message: ChatMessage):
    await main(chat_message)
    return {"msg": "Main function executed"}