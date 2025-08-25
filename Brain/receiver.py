import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

messages = [
    {
        "role": "user", 
        "content": "I will go to the supermarket tomorrow morning to buy groceries."
    },
]
def Startup(list<string> message):       
        print("Evolvra is starting up...")
        thinking = True
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        while thinking:
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=message,
                functions=[add_task_function], 
                function_call="auto"
            )
            if response.choices[0].finish_reason == "add_task":
                print(f"Task to be added.")
            if response.choices[0].finish_reason == "add_goal":
                print("Goal to be added.")
            if response.choices[0].finish_reason == "reschedule_task":
                print("Task to be rescheduled.")
            if response.choices[0].finish_reason == "all_done":
                print("Thinking and processing is done.")
                thinking = False
                break
            else:
                print("Unexpected outcome, continuing to think...")

    