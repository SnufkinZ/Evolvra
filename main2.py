from fastapi import FastAPI, Depends
from api.models import UserMessage, AIResponse
from api.dependencies import get_brain
from brain2 import Brain

app = FastAPI()

@app.post("/process-message", response_model=AIResponse)
async def process_message_endpoint(
    user_input: UserMessage,
    # This is the magic. FastAPI sees this and runs the entire
    # dependency chain: get_current_user -> get_task_repo -> get_brain
    brain: Brain = Depends(get_brain)
):
    """
    Receives a message and a ready-to-use, personalized Brain instance.
    """
    # The 'brain' instance is already configured for the current user.
    # Its internal TaskRepository already knows the user_id.
    ai_reply = await brain.process_user_message(user_input.message)
    
    return AIResponse(response=ai_reply)