#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Complete Integration
Enhanced wake word detection with MCP tools and RAG memory system

USAGE: python start_jarvis.py
"""

import sys
import logging
import time
sys.path.append('jarvis')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from jarvis.config import get_config
from jarvis.core.speech import SpeechManager
import requests
import json
from datetime import datetime

# Import MCP tools and RAG tools for enhanced functionality
from jarvis.core.mcp_tool_integration import initialize_mcp_tools
from jarvis.tools import plugin_manager
import asyncio

# Global variables to store tools
mcp_tools = []
rag_tools = []


def classify_intent(command):
    """Classify user intent using research-based NLP patterns."""
    cmd_lower = command.lower().strip()

    # SEARCH INTENT - User wants to retrieve information
    search_indicators = [
        'what are my', 'what do i like', 'what do i prefer', 'do i like', 'do i prefer',
        'search my', 'search for', 'find my', 'look up my', 'tell me about my',
        'what do you remember', 'do you remember', 'what have i told you',
        'my preferences', 'what kind of', 'which do i prefer', 'what is my favorite',
        'what sports do i', 'what books do i', 'what music do i', 'what food do i'
    ]

    # STORE INTENT - User wants to save information
    store_indicators = [
        'remember that', 'remember this', 'i like', 'i prefer', 'i love', 'i enjoy',
        'my favorite is', 'my favorite color is', 'i want', 'i need', 'i usually', 'i always', 'i typically',
        'i think', 'i believe', 'i feel', 'note that', 'save that'
    ]

    # Check for search intent first (more specific)
    if any(indicator in cmd_lower for indicator in search_indicators):
        return 'SEARCH'

    # Check for store intent
    if any(indicator in cmd_lower for indicator in store_indicators):
        return 'STORE'

    # Default to general conversation
    return 'GENERAL'


def extract_entities(command):
    """Extract topic entities from command using NLP techniques."""
    cmd_lower = command.lower().strip()

    # Dynamic preference categories (completely unbiased and expandable)
    categories = {
        'food': ['food', 'eat', 'meal', 'restaurant', 'cuisine', 'dish', 'snack', 'cooking'],
        'drink': ['coffee', 'tea', 'drink', 'beverage', 'juice', 'water', 'soda', 'wine', 'beer'],
        'music': ['music', 'song', 'artist', 'band', 'album', 'genre', 'playlist', 'concert'],
        'entertainment': ['movie', 'film', 'show', 'series', 'tv', 'cinema', 'actor', 'netflix'],
        'reading': ['book', 'read', 'author', 'novel', 'story', 'literature', 'magazine'],
        'visual': ['color', 'colour', 'blue', 'red', 'green', 'yellow', 'purple', 'art'],
        'sports': ['sport', 'game', 'team', 'player', 'football', 'basketball', 'exercise'],
        'travel': ['travel', 'trip', 'vacation', 'destination', 'country', 'city', 'hotel'],
        'activities': ['hobby', 'activity', 'interest', 'pastime', 'recreation', 'gaming'],
        'technology': ['tech', 'computer', 'software', 'app', 'phone', 'gadget'],
        'fashion': ['clothes', 'style', 'fashion', 'brand', 'outfit', 'shopping'],
        'weather': ['weather', 'season', 'temperature', 'climate', 'sunny', 'rainy']
    }

    # Find matching categories
    found_entities = []
    for category, keywords in categories.items():
        if any(keyword in cmd_lower for keyword in keywords):
            found_entities.append(category)

    # Extract specific items mentioned (cleaned)
    words = cmd_lower.split()
    specific_items = []
    skip_words = {'what', 'are', 'my', 'preferences', 'like', 'prefer', 'kind', 'do', 'for', 'the', 'of'}
    for word in words:
        # Clean punctuation and filter
        clean_word = word.strip('.,!?;:')
        if len(clean_word) > 2 and clean_word not in skip_words:
            specific_items.append(clean_word)

    return {
        'categories': found_entities,
        'specific_items': specific_items[:3]  # Limit to 3 most relevant
    }





def extract_search_query(command):
    """Extract the actual search query from various command patterns."""
    cmd_lower = command.lower().strip()

    # Handle "what are my X" patterns
    if 'what are my' in cmd_lower:
        parts = cmd_lower.split('what are my')
        if len(parts) > 1:
            return parts[1].strip().replace('?', '')

    # Handle "what do i like about X" patterns
    if 'what do i like' in cmd_lower:
        if 'about' in cmd_lower:
            parts = cmd_lower.split('about')
            if len(parts) > 1:
                return parts[1].strip().replace('?', '')
        else:
            return cmd_lower.replace('what do i like', '').strip().replace('?', '')

    # Handle "do you remember X" patterns
    if 'do you remember' in cmd_lower:
        parts = cmd_lower.split('do you remember')
        if len(parts) > 1:
            query = parts[1].strip().replace('?', '')
            # Remove common filler words
            query = query.replace('about', '').replace('what i said about', '').strip()
            return query

    # Handle "search for X" patterns
    if 'search' in cmd_lower:
        for pattern in ['search my', 'search for', 'search conversations for', 'search memories for']:
            if pattern in cmd_lower:
                parts = cmd_lower.split(pattern)
                if len(parts) > 1:
                    return parts[1].strip().replace('?', '')

    # Handle "tell me about my X" patterns
    if 'tell me about my' in cmd_lower:
        parts = cmd_lower.split('tell me about my')
        if len(parts) > 1:
            return parts[1].strip().replace('?', '')

    # Extract key topics dynamically from categories (no hardcoded bias)
    from itertools import chain
    all_category_keywords = list(chain.from_iterable(categories.values()))
    for keyword in all_category_keywords:
        if keyword in cmd_lower and len(keyword) > 3:  # Avoid short words
            return keyword

    # Fallback: return the whole command cleaned up
    return cmd_lower.replace('?', '').strip()


def extract_memory_content(command):
    """Extract the content that should be stored in memory."""
    cmd_lower = command.lower().strip()

    # Handle explicit remember commands
    if 'remember that' in cmd_lower:
        return cmd_lower.split('remember that')[1].strip()
    elif 'remember this' in cmd_lower:
        return cmd_lower.split('remember this')[1].strip()
    elif 'remember:' in cmd_lower:
        return cmd_lower.split('remember:')[1].strip()

    # Handle preference declarations - keep the full statement
    preference_starters = ['i like', 'i prefer', 'i love', 'i enjoy', 'my favorite']
    for starter in preference_starters:
        if cmd_lower.startswith(starter):
            return command.strip()  # Keep original capitalization

    # Handle opinion/fact statements
    fact_starters = ['i think', 'i believe', 'i feel', 'in my opinion']
    for starter in fact_starters:
        if cmd_lower.startswith(starter):
            return command.strip()

    # Default: store the whole command
    return command.strip()


def format_search_results(query, results):
    """Format search results in a natural, conversational way for ANY topic."""
    if not results:
        return f"I don't have any information about {query} in my memory."

    # Extract the main topic from the query
    topic = extract_topic_from_query(query)

    # Filter results to find relevant preferences/information
    relevant_prefs = []
    for result in results:
        content = result.page_content.strip()
        content_lower = content.lower()

        # Skip irrelevant system/test data
        if any(skip_term in content_lower for skip_term in [
            'test_plugin', 'plugin:', 'capabilities:', 'tools:', '__new_agent__',
            'readme.md', 'pyproject.toml', 'jarvis/__init__.py'
        ]):
            continue

        # For specific topic searches, use flexible matching
        if topic:
            # Check for topic match (exact or related terms)
            topic_variations = [topic]
            if topic == 'music':
                topic_variations.extend(['song', 'artist', 'band', 'album', 'genre'])
            elif topic == 'food':
                topic_variations.extend(['eat', 'meal', 'restaurant', 'cuisine'])
            elif topic == 'visual':
                topic_variations.extend(['color', 'colour'])
            elif topic == 'reading':
                topic_variations.extend(['book', 'novel', 'story', 'read', 'fiction'])
            elif topic == 'sports':
                topic_variations.extend(['sport', 'game', 'tennis', 'football', 'playing'])
            elif topic == 'activities':
                topic_variations.extend(['hobby', 'activity', 'playing', 'tennis'])

            topic_found = any(var in content_lower for var in topic_variations)
            pref_found = any(pref_indicator in content_lower for pref_indicator in [
                'i like', 'i prefer', 'i love', 'i enjoy', 'my favorite', 'i want', 'i need'
            ])

            # Include if BOTH topic and preference are found
            if topic_found and pref_found:
                relevant_prefs.append(content)
                print(f"✅ Found relevant: {content[:50]}...")
            else:
                print(f"❌ Skipped (topic:{topic_found}, pref:{pref_found}): {content[:50]}...")
        else:
            # General preference search
            if any(pref_indicator in content_lower for pref_indicator in [
                'i like', 'i prefer', 'i love', 'i enjoy', 'my favorite', 'i want', 'i need'
            ]):
                relevant_prefs.append(content)

    # Format the response naturally
    if not relevant_prefs:
        return f"I searched my memory for '{query}' but didn't find any relevant personal information. You may not have told me about this yet."

    if len(relevant_prefs) == 1:
        return f"Based on what you've told me: {relevant_prefs[0]}"
    else:
        response = f"Here's what I know about your {topic if topic else query}:\n"
        for pref in relevant_prefs[:3]:  # Limit to top 3 results
            if len(pref) > 150:
                pref = pref[:150] + "..."
            response += f"• {pref}\n"
        return response.strip()


def extract_topic_from_query(query):
    """Extract the main topic from a search query."""
    query_lower = query.lower().strip()

    # Remove common question words and patterns
    cleaned_query = query_lower
    for pattern in ['what are my', 'what do i', 'do i like', 'preferences', 'preference']:
        cleaned_query = cleaned_query.replace(pattern, '').strip()

    # Extract meaningful topic words and clean punctuation
    topic_words = cleaned_query.split()

    # Filter out common words and clean punctuation
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'about', 'kind', 'like'}
    meaningful_words = []
    for word in topic_words:
        # Remove punctuation
        clean_word = word.strip('.,!?;:').lower()
        if clean_word not in stop_words and len(clean_word) > 2:
            meaningful_words.append(clean_word)

    # Return the first meaningful word as the topic
    return meaningful_words[0] if meaningful_words else None

def simple_ai_response(command, ollama_url, model_name):
    """Get AI response using direct Ollama API call with MCP tools (synchronous)"""
    try:
        # Check if this is a time-related request - use MCP time server
        if any(word in command.lower() for word in ['time', 'clock', 'hour', 'minute']):
            try:
                # Use MCP time tools if available
                for tool in mcp_tools:
                    if 'time' in tool.name.lower() and 'current_time' in tool.name.lower():
                        result = tool._run({})
                        return f"The current time is {result}."

                # Fallback to simple datetime if MCP not available
                from datetime import datetime
                now = datetime.now()
                current_time = now.strftime("%I:%M %p")
                return f"The current time is {current_time}."
            except Exception as e:
                print(f"❌ Time tool error: {e}")
                # Fallback to simple datetime
                from datetime import datetime
                now = datetime.now()
                current_time = now.strftime("%I:%M %p")
                return f"The current time is {current_time}."

        # Use research-based intent classification
        intent = classify_intent(command)
        entities = extract_entities(command)

        if intent == 'SEARCH':
            try:
                # Build search query optimized for vector similarity (longer queries work better)
                query_parts = []
                if entities['categories']:
                    # Use preference-style queries that match stored format
                    for category in entities['categories']:
                        query_parts.append(f"I like {category}")

                # Create multiple search strategies
                search_queries = []
                if query_parts:
                    search_queries.extend(query_parts)

                # Add the original command as a search query too
                search_queries.append(command.lower().strip())

                # Add category-specific searches
                if entities['categories']:
                    for category in entities['categories']:
                        search_queries.append(category)

                print(f"🔍 Search strategies: {search_queries}")
                print(f"🔍 Intent: {intent}, Entities: {entities}")

                # Try to use RAG system directly
                try:
                    from jarvis.tools.rag_memory_manager import RAGMemoryManager
                    from jarvis.config import get_config

                    config = get_config()
                    rag_manager = RAGMemoryManager(config)

                    # Try multiple search strategies (based on debug findings)
                    all_results = []
                    for search_query in search_queries:
                        try:
                            query_results = rag_manager.vector_store.similarity_search(search_query, k=5)
                            print(f"🔍 Search '{search_query}': {len(query_results)} results")
                            all_results.extend(query_results)

                            # Show first few results for debugging
                            for i, result in enumerate(query_results[:2]):
                                content = result.page_content[:60]
                                print(f"  {i+1}. {content}...")

                        except Exception as e:
                            print(f"❌ Search error for '{search_query}': {e}")

                    # Remove duplicates while preserving order
                    seen = set()
                    results = []
                    for result in all_results:
                        content_hash = hash(result.page_content)
                        if content_hash not in seen:
                            seen.add(content_hash)
                            results.append(result)

                    print(f"📊 Total unique results: {len(results)}")

                    # Check if we found relevant results
                    main_topic = entities['categories'][0] if entities['categories'] else 'preferences'
                    relevant_found = any(main_topic.lower() in r.page_content.lower() for r in results)

                    if not relevant_found and entities['categories']:
                        print(f"🔍 No {main_topic} results found, trying broader search...")
                        broader_queries = [
                            f"i like {main_topic}",
                            f"i prefer {main_topic}",
                            f"my favorite {main_topic}",
                            f"{main_topic} preference"
                        ]
                        for broader_query in broader_queries:
                            broader_results = rag_manager.vector_store.similarity_search(broader_query, k=5)
                            if broader_results:
                                results.extend(broader_results)
                                print(f"🔍 Broader search '{broader_query}' found: {len(broader_results)} results")
                                for i, result in enumerate(broader_results[:3]):
                                    print(f"    {i+1}. {result.page_content[:60]}...")
                                break

                    # Filter out irrelevant results (test data, plugin info, etc.)
                    filtered_results = []
                    for result in results:
                        content = result.page_content.lower()
                        # Skip test data and plugin information
                        if any(skip_term in content for skip_term in ['test_plugin', 'plugin:', 'capabilities:', 'tools:', '__new_agent__']):
                            continue
                        # Keep relevant personal information (completely unbiased)
                        if any(keep_term in content for keep_term in [main_topic.lower(), 'i like', 'i prefer', 'my favorite']):
                            filtered_results.append(result)

                    results = filtered_results[:3]  # Keep top 3 relevant results

                    if results:
                        return format_search_results(main_topic, results)
                    else:
                        return f"I searched my memory for '{main_topic}' but didn't find any relevant information. You may not have told me about this yet."

                except Exception as rag_error:
                    print(f"❌ Direct RAG error: {rag_error}")
                    return "I don't have access to conversation memory right now. The RAG system may not be initialized."

            except Exception as e:
                print(f"❌ RAG search error: {e}")
                return "I encountered an error searching my memory. Please try again."

        elif intent == 'STORE':
            try:
                # Extract what to remember with metadata
                memory_text = extract_memory_content(command)
                categories = entities['categories']
                print(f"💾 Storing memory: '{memory_text}' with categories: {categories}")

                # Store in RAG system
                try:
                    from jarvis.tools.rag_memory_manager import RAGMemoryManager
                    from jarvis.config import get_config

                    config = get_config()
                    rag_manager = RAGMemoryManager(config)
                    rag_manager.add_conversational_memory(memory_text)

                    return f"I'll remember that: {memory_text}"

                except Exception as rag_error:
                    print(f"❌ Memory storage error: {rag_error}")
                    return "I had trouble storing that memory, but I'll try to remember it for this conversation."

            except Exception as e:
                print(f"❌ Remember error: {e}")
                return "I encountered an error trying to remember that. Please try again."

        # Check if this is a filesystem-related request - use MCP filesystem server
        elif any(word in command.lower() for word in ['list', 'files', 'directory', 'folder', 'desktop', 'documents']):
            try:
                # Use MCP filesystem tools if available
                for tool in mcp_tools:
                    if 'filesystem' in tool.name.lower() and 'list_directory' in tool.name.lower():
                        # Try to determine the path from the command
                        if 'desktop' in command.lower():
                            path = '/Users/josed/Desktop'
                        elif 'documents' in command.lower():
                            path = '/Users/josed/Documents'
                        else:
                            path = '/Users/josed'  # Default to home directory

                        result = tool._run({'path': path})
                        return f"Here are the files in {path}:\n{result[:300]}..."

                # Fallback response if MCP not available
                return "I can help you list files, but I need access to the filesystem tools. Please specify which directory you'd like to explore."
            except Exception as e:
                print(f"❌ Filesystem tool error: {e}")
                return "I encountered an error accessing the filesystem. Please try again."

        # For other requests, use AI with context
        system_prompt = f"""You are Jarvis, a helpful AI assistant. You have access to these tools:
- Current time: You can tell the current time using MCP time server
- Filesystem access: You can list files and directories using MCP filesystem server
- Memory search: You can search conversation history and stored memories using RAG system
- General knowledge: You can answer questions and have conversations

Available tools: {len(mcp_tools)} MCP tools + {len(rag_tools)} plugin tools loaded
Keep responses concise and helpful."""

        # Create prompt for general queries
        full_prompt = f"""System: {system_prompt}

User: {command}"""

        # Make API call to Ollama
        payload = {
            "model": model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 150
            }
        }

        response = requests.post(ollama_url, json=payload, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "I'm sorry, I couldn't process that request.").strip()
        else:
            return "I'm having trouble connecting to my AI system right now."

    except Exception as e:
        print(f"❌ AI error: {e}")
        return "I'm sorry, I had trouble processing that request."

def simple_jarvis_loop():
    """Jarvis loop with proper conversation memory"""
    print("🎯 JARVIS WITH CONVERSATION MEMORY")
    print("=" * 50)

    try:
        # Initialize components
        config = get_config()
        config.audio.mic_index = 0  # Force correct microphone

        print("📡 Initializing speech manager...")
        speech_manager = SpeechManager(config.audio)
        speech_manager.initialize()
        print("✅ Speech manager ready")

        print("🤖 Setting up AI agent with conversation memory...")
        # Initialize proper agent with conversation memory
        sys.path.insert(0, 'jarvis')  # Add jarvis package to path
        from jarvis.core.agent import JarvisAgent
        from langchain.memory import ConversationBufferMemory

        # Note: Old agent system replaced with optimized integration
        # Agent functionality now handled by optimized_integration system

        print("🔧 Initializing MCP tools...")
        # Initialize MCP tools asynchronously
        try:
            import asyncio
            global mcp_tools
            mcp_tools = asyncio.run(initialize_mcp_tools())
            print(f"✅ MCP tools loaded: {len(mcp_tools)} tools")
            for tool in mcp_tools[:5]:  # Show first 5 tools
                print(f"  • {tool.name}")
            if len(mcp_tools) > 5:
                print(f"  • ... and {len(mcp_tools) - 5} more tools")
        except Exception as e:
            print(f"⚠️ MCP tools failed to load: {e}")
            mcp_tools = []

        print("🧠 Initializing RAG tools...")
        # Initialize RAG tools for memory search
        try:
            global rag_tools
            rag_tools = plugin_manager.get_all_tools()
            rag_count = len([t for t in rag_tools if 'search' in t.name.lower() or 'remember' in t.name.lower()])
            print(f"✅ RAG tools loaded: {rag_count} memory tools from {len(rag_tools)} total plugin tools")
            for tool in rag_tools:
                if 'search' in tool.name.lower() or 'remember' in tool.name.lower():
                    print(f"  • {tool.name}")
        except Exception as e:
            print(f"⚠️ RAG tools failed to load: {e}")
            rag_tools = []

        # Initialize optimized integration system (replaces old agent processing)
        print("🚀 Initializing optimized Jarvis system...")
        from jarvis.core.integration.optimized_integration import get_optimized_integration
        optimized_integration = get_optimized_integration()
        print("✅ Optimized system ready with intelligent routing and caching")

        # Simple state management (like the working example)
        conversation_mode = False
        last_interaction_time = None
        TRIGGER_WORD = "jarvis"
        CONVERSATION_TIMEOUT = 30  # seconds
        
        print("\n🎤 Starting simple wake word loop...")
        print("Say 'jarvis' to activate!")
        print("=" * 50)
        
        while True:
            try:
                if not conversation_mode:
                    # Listen for wake word (like the working example)
                    print("🎧 Listening for wake word...")
                    
                    # Use our speech manager to listen
                    transcript = speech_manager.microphone_manager.listen_for_speech(
                        timeout=10.0, 
                        service="whisper"  # Try Whisper first
                    )
                    
                    if transcript:
                        print(f"🗣 Heard: '{transcript}'")
                        
                        # Simple wake word detection (like the working example)
                        if TRIGGER_WORD.lower() in transcript.lower():
                            print(f"🎯 WAKE WORD DETECTED! Triggered by: '{transcript}'")
                            
                            # Respond with TTS
                            speech_manager.speak_text("Yes sir?")
                            
                            # Enter conversation mode
                            conversation_mode = True
                            last_interaction_time = time.time()

                            # Start new conversation session with optimized system
                            optimized_integration.start_conversation_session()
                            print("✅ Entered conversation mode (new session started)")
                        else:
                            print("❌ Wake word not detected, continuing...")
                    else:
                        print("🔇 No speech detected, continuing...")
                        
                else:
                    # In conversation mode - listen for commands
                    print("🎤 Listening for command...")
                    
                    command = speech_manager.microphone_manager.listen_for_speech(
                        timeout=10.0,
                        service="whisper"
                    )
                    
                    if command:
                        print(f"📥 Command: '{command}'")

                        # Process command with optimized system (maintains conversation memory)
                        try:
                            print("🧠 Processing with optimized AI system...")

                            # Use optimized integration for fast, intelligent processing
                            import asyncio
                            try:
                                # Try to get existing event loop
                                loop = asyncio.get_event_loop()
                                if loop.is_running():
                                    # We're in a running loop, use thread executor
                                    import concurrent.futures
                                    with concurrent.futures.ThreadPoolExecutor() as executor:
                                        future = executor.submit(asyncio.run, optimized_integration.process_command(command))
                                        response = future.result(timeout=30.0)
                                else:
                                    # No running loop, use it directly
                                    response = loop.run_until_complete(optimized_integration.process_command(command))
                            except RuntimeError:
                                # No event loop exists, create new one
                                response = asyncio.run(optimized_integration.process_command(command))

                            print(f"🤖 Jarvis: {response}")
                            speech_manager.speak_text(response)
                        except Exception as e:
                            print(f"❌ AI processing error: {e}")
                            fallback_response = "I'm sorry, I had trouble processing that request."
                            print(f"🤖 Jarvis: {fallback_response}")
                            speech_manager.speak_text(fallback_response)

                        last_interaction_time = time.time()
                    else:
                        print("🔇 No command heard")
                    
                    # Check for timeout
                    if time.time() - last_interaction_time > CONVERSATION_TIMEOUT:
                        print("⌛ Timeout: Returning to wake word mode")
                        # Save conversation memory before ending session
                        print("💾 Conversation session ended - memory preserved")
                        conversation_mode = False
                        
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(1)  # Brief pause before retrying
                
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_jarvis_loop()
