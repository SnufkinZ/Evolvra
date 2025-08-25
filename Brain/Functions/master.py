import requests
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import defination

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

classification("I will go to the supermarket tomorrow morning to buy groceries, I want to become a chef!")