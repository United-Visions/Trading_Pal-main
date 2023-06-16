import requests
import json
import csv
openai_api_key = "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"  # replace with your actual OpenAI API key
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai_api_key}",
}
data = {
    "model": "gpt-3.5-turbo-0613",
    "messages": [
        {"role": "user", "content": "What is the weather like in Boston?"}
    ],
    "functions": [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    ]
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, data=json.dumps(data))

# Convert the response to a string
response_str = json.dumps(response.json(), indent=4)

# Write the response to a text file
with open("output.txt", "w") as f:
    f.write(response_str)