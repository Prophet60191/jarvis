#!/usr/bin/env python3
import requests
import json

prompt = "You are Jarvis, an AI assistant. I need you to create a tool that will open Google Chrome on macOS. Please create this tool and implement it in the Jarvis system."

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:7b-instruct",
        "prompt": prompt,
        "stream": False
    }
)

print("Response status:", response.status_code)
print("\nResponse content:")
print(json.dumps(response.json(), indent=2))
