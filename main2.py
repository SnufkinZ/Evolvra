from fastapi import FastAPI
from brain import AIBrain, ToolRegistry # Assume ToolRegistry is in brain now
from logic import macro_operations # A new module to load/save macros from DB

# --- 1. Create a SINGLE, GLOBAL instance of the ToolRegistry ---
# This object will be shared across all API requests.
tool_registry_instance = ToolRegistry()

# --- 2. Create a startup event function ---
# This async function will run automatically ONE TIME when the server starts.
async def startup_event():
    print("--- Server is starting up... ---")
    
    # Register your hard-coded atomic tools
    # tool_registry_instance.register_atomic_tool(...) 
    
    # Load all AI-created macros from the database
    print("Loading AI-created macro tools from database...")
    all_macros = await macro_operations.get_all_macros() # A function to get all macros from MongoDB
    for macro in all_macros:
        # Assuming register_macro_tool is now synchronous since it just adds to a dict
        tool_registry_instance.register_macro_tool(macro['name'], macro['description'], macro['workflow'])
    
    print(f"--- Startup complete. {len(all_macros)} macros loaded. ---")

# --- 3. Register the event with the FastAPI app ---
app = FastAPI(
    title="Evolvra AI Personal Secretary API",
    on_startup=[startup_event] # Pass the function here
)

# --- 4. Pass the single instance to the AIBrain ---
# The AIBrain is also often best as a singleton
brain_instance = AIBrain(tool_registry=tool_registry_instance)


@app.post("/process-message")
async def process_message_endpoint(user_input: UserMessage):
    # This endpoint now uses the pre-initialized brain and tool registry
    ai_reply = await brain_instance.run_agent_loop(user_input.message)
    return AIResponse(response=ai_reply)