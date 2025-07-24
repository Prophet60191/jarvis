import os
import logging
import time
import pyttsx3
from dotenv import load_dotenv
import speech_recognition as sr
from langchain_ollama import ChatOllama, OllamaLLM
from langchain_core.messages import HumanMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from tools.time import get_time 
from tools.video_day import video_day

load_dotenv()

MIC_INDEX = 0
TRIGGER_WORD = "jarvis"
CONVERSATION_TIMEOUT = 30  # seconds of inactivity before exiting conversation mode

# Wrap functions as LangChain tools
@tool
def get_time_tool(city: str) -> str:
    """Get the current time in a specific city."""
    return get_time(city)

@tool  
def video_day_tool() -> str:
    """Get information about video content creation today."""
    return video_day()

# LLM setup
llm = ChatOllama(model="qwen2.5:1.5b", reasoning=False)

# Tools
tools = [get_time_tool, video_day_tool]

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are Jarvis, a helpful AI assistant. You can help with time queries and video content advice."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Agent + executor
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# TTS setup
def speak_text(text: str):
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        # Try to find and set Jamie voice
        for voice in voices:
            if 'jamie' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
        
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 1.0)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        print(f"TTS Error: {e}")

# Microphone setup with fallback
def setup_microphone():
    recognizer = sr.Recognizer()
    microphone = None
    
    # Try different microphone configurations
    mic_configs = [
        ("MacBook Pro Microphone", None),
        ("Logitech BRIO", None), 
        ("C34H89x", None),
        ("System Default", 0)
    ]
    
    for mic_name, device_index in mic_configs:
        try:
            print(f"Trying {mic_name}...")
            mic = sr.Microphone(device_index=device_index) if device_index is not None else sr.Microphone()
            
            with mic as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print(f"✅ Successfully initialized {mic_name}")
            return recognizer, mic
            
        except Exception as e:
            print(f"❌ Failed to initialize {mic_name}: {e}")
            continue
    
    raise Exception("No working microphone found")

# Main conversation loop
def main():
    print("🤖 Initializing Jarvis...")
    
    try:
        recognizer, mic = setup_microphone()
        print("🎤 Microphone ready")
        print("🧠 AI model loaded")
        print("🔧 Tools available: get_time, video_day")
        print(f"\n👂 Listening for wake word: '{TRIGGER_WORD}'")
        print("Press Ctrl+C to exit\n")
        
        while True:
            try:
                # Listen for wake word
                with mic as source:
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                try:
                    text = recognizer.recognize_google(audio).lower()
                    
                    if TRIGGER_WORD in text:
                        print("🗣️ Wake word detected!")
                        speak_text("Yes sir?")
                        
                        # Enter conversation mode
                        conversation_active = True
                        last_activity = time.time()
                        
                        while conversation_active:
                            try:
                                with mic as source:
                                    print("👂 Listening...")
                                    audio = recognizer.listen(source, timeout=2, phrase_time_limit=10)
                                
                                command = recognizer.recognize_google(audio)
                                print(f"🧑 You: {command}")
                                
                                # Process with AI
                                print("🤖 Processing...")
                                response = executor.invoke({"input": command})
                                ai_response = response["output"]
                                
                                print(f"🤖 Jarvis: {ai_response}")
                                speak_text(ai_response)
                                
                                last_activity = time.time()
                                
                            except sr.WaitTimeoutError:
                                if time.time() - last_activity > CONVERSATION_TIMEOUT:
                                    print("⏰ Conversation timeout")
                                    conversation_active = False
                                continue
                                
                            except sr.UnknownValueError:
                                print("❓ Could not understand audio")
                                continue
                                
                            except Exception as e:
                                print(f"❌ Error in conversation: {e}")
                                continue
                        
                        print(f"👂 Listening for wake word: '{TRIGGER_WORD}'")
                        
                except sr.UnknownValueError:
                    pass  # No speech detected
                    
            except sr.WaitTimeoutError:
                pass  # Timeout, continue listening
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
                
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)
                
    except Exception as e:
        print(f"💥 Failed to initialize Jarvis: {e}")

if __name__ == "__main__":
    main()
