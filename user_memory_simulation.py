#!/usr/bin/env python3
"""
User Memory Simulation Test

This script simulates a real user interacting with Jarvis, asking it to remember
various personal information and then testing recall in natural conversation patterns.
"""

import sys
import os
import time
sys.path.insert(0, '.')
os.environ['PYTHONPATH'] = '/Users/josed/Desktop/Voice App'

class UserMemorySimulator:
    def __init__(self):
        self.remember_tool = None
        self.search_tool = None
        self.conversation_search = None
        self.all_search = None
        self.setup_tools()
        
        # Track success rates for improvement measurement
        self.iteration_results = []
        
    def setup_tools(self):
        """Initialize RAG tools."""
        try:
            from jarvis.tools.plugins.rag_plugin import (
                remember_fact, 
                search_long_term_memory,
                search_conversations,
                search_all_memory
            )
            
            self.remember_tool = remember_fact
            self.search_tool = search_long_term_memory
            self.conversation_search = search_conversations
            self.all_search = search_all_memory
            
            print("✅ RAG tools initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing tools: {e}")
            raise
    
    def simulate_user_session(self, session_num):
        """Simulate a user session with memory storage and recall."""
        
        print(f"\n{'='*60}")
        print(f"🧑‍💻 USER SESSION {session_num}")
        print(f"{'='*60}")
        
        # Define user scenarios with increasing complexity
        scenarios = [
            # Session 1: Basic personal info
            {
                "memories": [
                    "Remember that my name is Alex and I'm 28 years old",
                    "I live in San Francisco and work as a software engineer",
                    "My favorite food is sushi and I love Japanese cuisine"
                ],
                "recalls": [
                    "What's my name and age?",
                    "Where do I live and what do I do for work?",
                    "What kind of food do I like?"
                ]
            },
            # Session 2: Preferences and habits
            {
                "memories": [
                    "I prefer to wake up at 6 AM and go for a morning run",
                    "My favorite programming languages are Python and JavaScript",
                    "I have a cat named Whiskers who is 3 years old"
                ],
                "recalls": [
                    "What time do I wake up and what do I do in the morning?",
                    "What programming languages do I prefer?",
                    "Tell me about my pet"
                ]
            },
            # Session 3: Complex relationships and context
            {
                "memories": [
                    "My best friend Sarah works at Google and we met in college",
                    "I'm planning a trip to Japan in December for my birthday",
                    "I'm currently learning to play guitar and practice 30 minutes daily"
                ],
                "recalls": [
                    "Who is my best friend and where does she work?",
                    "What travel plans do I have?",
                    "What musical instrument am I learning?"
                ]
            },
            # Session 4: Professional and goals
            {
                "memories": [
                    "I'm working on a machine learning project about natural language processing",
                    "My career goal is to become a senior AI engineer within 2 years",
                    "I attend a weekly tech meetup every Thursday evening"
                ],
                "recalls": [
                    "What project am I currently working on?",
                    "What are my career goals?",
                    "What regular events do I attend?"
                ]
            }
        ]
        
        # Use the appropriate scenario for this session
        scenario_index = (session_num - 1) % len(scenarios)
        scenario = scenarios[scenario_index]
        
        # Storage phase
        print(f"\n📝 STORAGE PHASE - User asking Jarvis to remember things:")
        storage_success = 0
        
        for i, memory in enumerate(scenario["memories"], 1):
            print(f"\n👤 User: \"{memory}\"")
            
            try:
                result = self.remember_tool.invoke({"fact": memory})
                if "stored" in result.lower() and "remember" in result.lower():
                    print(f"🤖 Jarvis: {result[:100]}...")
                    storage_success += 1
                    print("✅ Storage successful")
                else:
                    print(f"🤖 Jarvis: {result[:100]}...")
                    print("⚠️ Storage unclear")
            except Exception as e:
                print(f"❌ Storage failed: {e}")
        
        # Brief pause to simulate natural conversation flow
        time.sleep(1)
        
        # Recall phase
        print(f"\n🔍 RECALL PHASE - User asking Jarvis to recall information:")
        recall_success = 0
        
        for i, query in enumerate(scenario["recalls"], 1):
            print(f"\n👤 User: \"{query}\"")
            
            try:
                # Try different search methods to find the best recall
                methods = [
                    ("Long-term search", self.search_tool),
                    ("Conversation search", self.conversation_search),
                    ("All memory search", self.all_search)
                ]
                
                best_result = ""
                best_method = ""
                
                for method_name, tool in methods:
                    try:
                        result = tool.invoke({"query": query})
                        if len(result) > len(best_result) and "conversation" in result.lower():
                            best_result = result
                            best_method = method_name
                    except:
                        continue
                
                if best_result and len(best_result) > 50:
                    print(f"🤖 Jarvis ({best_method}): {best_result[:150]}...")
                    
                    # Check if the recall contains relevant information
                    query_words = query.lower().split()
                    result_lower = best_result.lower()
                    
                    # Simple relevance check
                    relevant_words = sum(1 for word in query_words if word in result_lower and len(word) > 3)
                    if relevant_words >= 1:
                        recall_success += 1
                        print("✅ Recall successful - relevant information found")
                    else:
                        print("⚠️ Recall partial - some information found")
                else:
                    print("🤖 Jarvis: I don't have specific information about that.")
                    print("❌ Recall failed")
                    
            except Exception as e:
                print(f"❌ Recall error: {e}")
        
        # Calculate session success rate
        total_operations = len(scenario["memories"]) + len(scenario["recalls"])
        successful_operations = storage_success + recall_success
        success_rate = (successful_operations / total_operations) * 100
        
        session_result = {
            "session": session_num,
            "storage_success": storage_success,
            "storage_total": len(scenario["memories"]),
            "recall_success": recall_success,
            "recall_total": len(scenario["recalls"]),
            "overall_success_rate": success_rate
        }
        
        self.iteration_results.append(session_result)
        
        print(f"\n📊 SESSION {session_num} RESULTS:")
        print(f"Storage: {storage_success}/{len(scenario['memories'])} successful")
        print(f"Recall: {recall_success}/{len(scenario['recalls'])} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        return session_result
    
    def analyze_improvement(self):
        """Analyze improvement across sessions."""
        
        print(f"\n{'='*80}")
        print("📈 IMPROVEMENT ANALYSIS")
        print(f"{'='*80}")
        
        if len(self.iteration_results) < 2:
            print("Need at least 2 sessions to analyze improvement")
            return False
        
        print("Session-by-session results:")
        for result in self.iteration_results:
            print(f"Session {result['session']}: {result['overall_success_rate']:.1f}% success rate")
        
        # Calculate improvement metrics
        first_session = self.iteration_results[0]['overall_success_rate']
        last_session = self.iteration_results[-1]['overall_success_rate']
        improvement = last_session - first_session
        
        # Calculate average improvement trend
        if len(self.iteration_results) > 2:
            improvements = []
            for i in range(1, len(self.iteration_results)):
                prev_rate = self.iteration_results[i-1]['overall_success_rate']
                curr_rate = self.iteration_results[i]['overall_success_rate']
                improvements.append(curr_rate - prev_rate)
            avg_improvement = sum(improvements) / len(improvements)
        else:
            avg_improvement = improvement
        
        print(f"\n📊 IMPROVEMENT METRICS:")
        print(f"First session success rate: {first_session:.1f}%")
        print(f"Last session success rate: {last_session:.1f}%")
        print(f"Total improvement: {improvement:+.1f}%")
        print(f"Average improvement per session: {avg_improvement:+.1f}%")
        
        # Determine if there's marked improvement
        marked_improvement = False
        
        if improvement >= 15:  # 15% or more improvement
            print("🎉 MARKED IMPROVEMENT ACHIEVED! (+15% or more)")
            marked_improvement = True
        elif improvement >= 10:  # 10-15% improvement
            print("👍 GOOD IMPROVEMENT! (+10% to +15%)")
            marked_improvement = True
        elif improvement >= 5:   # 5-10% improvement
            print("📈 MODERATE IMPROVEMENT (+5% to +10%)")
        elif improvement >= 0:   # No decline
            print("➡️ STABLE PERFORMANCE (no significant change)")
        else:
            print("📉 PERFORMANCE DECLINE (needs attention)")
        
        return marked_improvement
    
    def run_simulation(self, max_sessions=4):
        """Run the complete user memory simulation."""
        
        print("🚀 STARTING USER MEMORY SIMULATION")
        print("Simulating real user interactions with Jarvis memory system...")
        
        marked_improvement = False
        session = 1
        
        while session <= max_sessions and not marked_improvement:
            self.simulate_user_session(session)
            
            if session >= 2:  # Need at least 2 sessions to measure improvement
                marked_improvement = self.analyze_improvement()
                
                if marked_improvement:
                    print(f"\n✅ MARKED IMPROVEMENT ACHIEVED after {session} sessions!")
                    break
            
            session += 1
            
            if session <= max_sessions:
                print(f"\n⏳ Continuing to session {session} to seek further improvement...")
                time.sleep(2)  # Brief pause between sessions
        
        # Final summary
        print(f"\n{'='*80}")
        print("🏁 SIMULATION COMPLETE")
        print(f"{'='*80}")
        
        if marked_improvement:
            print("🎯 SUCCESS: Marked improvement in memory performance achieved!")
        else:
            print("📊 COMPLETE: Simulation finished - system shows consistent performance")
        
        return marked_improvement

def main():
    """Main function to run the user memory simulation."""
    
    simulator = UserMemorySimulator()
    success = simulator.run_simulation(max_sessions=4)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
