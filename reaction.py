import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from Brain.Functions import defination
from operation_library import task_operations, goal_operations

load_dotenv()

def classification(message):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    input_messages = [
            {
                "role": "system", 
                "content": "You are a function call planner. Please determine which functions need to be called based on user input (multiple functions are also acceptable), and list the function names and parameters of each function. "
                "Output JSON format, such as: {\"calls\": [{\"function\": \"add_task\", \"arguments\": {...}}, ...]}"
            },
            {
                "role": "user", 
                "content": message
            }
        ]
    response = client.responses.create(
        model="gpt-4.1",
        input= input_messages,
        tools= defination.classification_tool
    )
    print("Response from model:")
    print(response.output)
    return response.output

def reaction(message):
    loop = True
    while loop:
        response = classification(message)[0]
        function = json.loads(response.function)
        if function=="add_task":
            arguments = json.loads(response.arguments)
            task_operations.add_task(arguments)
        elif function=="add_goal":
            arguments = json.loads(response.arguments)
            goal_operations.add_goal(arguments)
        elif function=="edit_task":
            arguments = json.loads(response.arguments)
            task_operations.edit_task(arguments)
        elif function=="edit_goal":
            arguments = json.loads(response.arguments)
            goal_operations.edit_goal(arguments)
        elif function=="End":
            loop = False
        else:
            response.append("Sorry, there is no such function.")
        message.append(response)
    return message