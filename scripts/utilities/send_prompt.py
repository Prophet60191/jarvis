#!/usr/bin/env python3
from langchain_ollama import ChatOllama
from jarvis.jarvis.config import JarvisConfig

config = JarvisConfig()
llm = ChatOllama(
    model=config.llm.model,
    temperature=config.llm.temperature
)

prompt = "I need a tool that opens Chrome. Please create and implement this tool in the Jarvis system."
print("Sending prompt to LLM:", prompt)
response = llm.invoke(prompt)
print("\nResponse:", response.content)
