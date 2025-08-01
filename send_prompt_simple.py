#!/usr/bin/env python3
import requests

prompt = "Make a tool that will open Chrome"
print(f"Sending prompt: {prompt}")

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen2.5:7b-instruct",
        "prompt": prompt,
        "stream": False
    }
)

print("\nResponse:")
print(response.json()["response"])
