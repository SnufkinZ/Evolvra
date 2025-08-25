import requests
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


def get_weather(latitude, longitude):
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m")
    data = response.json()
    return data['current']['temperature_2m']

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


tools = [{
    "type": "function",
    "name": "get_weather",
    "description": "Get current temperature for provided coordinates in celsius.",
    "parameters": {
        "type": "object",
        "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
        },
        "required": ["latitude", "longitude"],
        "additionalProperties": False
    },
    "strict": True
}]

input_messages = [{"role": "user", "content": "What's the weather like in Paris today?"}]

response = client.responses.create(
    model="gpt-4.1",
    input= input_messages,
    tools=tools,
)

print("Response from model:")
print(response)

tool_call = response.output[0]
args = json.loads(tool_call.arguments) # type: ignore

print("Tool call arguments:")
print(args)

result = get_weather(args["latitude"], args["longitude"])

print("Function result:")
print(result)

input_messages.append(tool_call)  # append model's function call message
input_messages.append({                               # append result message
    "type": "function_call_output",
    "call_id": tool_call.call_id,
    "output": str(result)
})

print("Input messages after appending function call and result:")
print(input_messages)

response_2 = client.responses.create(
    model="gpt-4.1",
    input=input_messages,
    tools=tools,
)

print("Final response from model:")
print(response_2)
print(response_2.output_text)