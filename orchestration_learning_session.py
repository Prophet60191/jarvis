#!/usr/bin/env python3
"""
Orchestration Learning Session

Runs real prompts through Jarvis and feeds the results back into the learning system
to improve orchestration decisions over time.
"""

import sys
import asyncio
import time
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Add the jarvis package to the path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

# Progressive learning prompts - start simple, get more complex
LEARNING_PROMPTS = [
    # Phase 1: Simple prompts to establish baseline
    {
        "prompt": "What time is it?",
        "expected_behavior": "single_tool",
        "expected_tools": ["get_current_time"],
        "complexity": "simple"
    },
    {
        "prompt": "Remember that I prefer using Python for data analysis projects",
        "expected_behavior": "single_tool", 
        "expected_tools": ["remember_fact"],
        "complexity": "simple"
    },
    {
        "prompt": "What did I tell you about my programming preferences?",
        "expected_behavior": "single_tool",
        "expected_tools": ["search_long_term_memory"],
        "complexity": "simple"
    },
    
    # Phase 2: Medium complexity - should trigger orchestration
    {
        "prompt": "Create a Python script that checks if a website is online",
        "expected_behavior": "orchestration",
        "expected_tools": ["aider", "open_interpreter"],
        "complexity": "medium"
    },
    {
        "prompt": "Extract the main headlines from a news website",
        "expected_behavior": "orchestration", 
        "expected_tools": ["lavague", "aider", "open_interpreter"],
        "complexity": "medium"
    },
    {
        "prompt": "Build a simple file organizer for my Downloads folder",
        "expected_behavior": "orchestration",
        "expected_tools": ["aider", "open_interpreter"],
        "complexity": "medium"
    },
    
    # Phase 3: Complex multi-agent workflows
    {
        "prompt": "Research the latest AI trends, create a summary, and build a tool to track future developments",
        "expected_behavior": "complex_orchestration",
        "expected_tools": ["rag", "lavague", "aider", "open_interpreter"],
        "complexity": "complex"
    },
    {
        "prompt": "Extract product data from an e-commerce site, analyze pricing trends, and create a monitoring dashboard",
        "expected_behavior": "complex_orchestration",
        "expected_tools": ["lavague", "aider", "open_interpreter"],
        "complexity": "complex"
    },
    {
        "prompt": "Build a comprehensive backup system, test it thoroughly, and create automated scheduling",
        "expected_behavior": "complex_orchestration",
        "expected_tools": ["aider", "open_interpreter", "robot_framework"],
        "complexity": "complex"
    }
]

class OrchestrationLearningSession:
    """Conducts learning sessions to improve Jarvis orchestration through real usage."""
    
    def __init__(self):
        self.session_results = []
        self.learning_progress = []
        self.orchestration_patterns = {}
        
    async def run_learning_session(self):
        """Run a complete learning session with progressive complexity."""
        print("🧠 Starting Orchestration Learning Session")
        print("=" * 50)
        
        # Initialize Jarvis with orchestration
        jarvis_agent = await self.initialize_jarvis_with_orchestration()
        if not jarvis_agent:
            print("❌ Failed to initialize Jarvis - cannot proceed")
            return
        
        # Run progressive learning
        for phase, prompts in self.group_prompts_by_phase().items():
            print(f"\n🎯 Learning Phase: {phase}")
            print("-" * 30)
            
            phase_results = []
            for i, prompt_data in enumerate(prompts, 1):
                print(f"\n📝 Prompt {i}/{len(prompts)}: {prompt_data['prompt']}")
                
                # Execute prompt and analyze response
                result = await self.execute_learning_prompt(jarvis_agent, prompt_data)
                phase_results.append(result)
                
                # Provide feedback to learning system
                await self.provide_learning_feedback(result)
                
                # Brief pause for processing
                await asyncio.sleep(2)
            
            # Analyze phase progress
            self.analyze_phase_progress(phase, phase_results)
        
        # Generate learning report
        self.generate_learning_report()
    
    async def initialize_jarvis_with_orchestration(self):
        """Initialize Jarvis with full orchestration capabilities."""
        try:
            from jarvis.core.agent import JarvisAgent
            from jarvis.config import LLMConfig
            from jarvis.core.orchestration.integration_layer import (
                initialize_orchestration, 
                get_orchestration_integration
            )
            
            # Create and initialize Jarvis
            config = LLMConfig()
            agent = JarvisAgent(config)
            agent.initialize(tools=[])
            
            # Initialize orchestration system
            orchestration_available = initialize_orchestration()
            
            if orchestration_available:
                integration = get_orchestration_integration()
                status = integration.get_orchestration_status()
                print(f"✅ Orchestration initialized: {status}")
            else:
                print("⚠️  Orchestration not available - will test basic functionality")
            
            return agent
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return None
    
    def group_prompts_by_phase(self) -> Dict[str, List[Dict]]:
        """Group prompts by learning phase."""
        phases = {
            "Phase 1 - Baseline": [],
            "Phase 2 - Orchestration": [], 
            "Phase 3 - Complex Workflows": []
        }
        
        for prompt_data in LEARNING_PROMPTS:
            if prompt_data["complexity"] == "simple":
                phases["Phase 1 - Baseline"].append(prompt_data)
            elif prompt_data["complexity"] == "medium":
                phases["Phase 2 - Orchestration"].append(prompt_data)
            else:
                phases["Phase 3 - Complex Workflows"].append(prompt_data)
        
        return phases
    
    async def execute_learning_prompt(self, agent, prompt_data: Dict) -> Dict[str, Any]:
        """Execute a learning prompt and analyze the response."""
        start_time = time.time()
        
        try:
            # Send prompt to Jarvis
            response = await agent.process_input(prompt_data["prompt"])
            execution_time = time.time() - start_time
            
            # Analyze orchestration behavior
            analysis = self.analyze_orchestration_response(response, prompt_data)
            
            result = {
                "prompt": prompt_data["prompt"],
                "expected_behavior": prompt_data["expected_behavior"],
                "expected_tools": prompt_data["expected_tools"],
                "complexity": prompt_data["complexity"],
                "response": response,
                "execution_time": execution_time,
                "analysis": analysis,
                "success": True,
                "timestamp": time.time()
            }
            
            # Print analysis
            print(f"⏱️  Execution time: {execution_time:.2f}s")
            print(f"🎯 Expected: {prompt_data['expected_behavior']}")
            print(f"🧠 Detected: {analysis['orchestration_type']}")
            print(f"✅ Match: {analysis['behavior_match']}")
            
            if analysis["orchestration_detected"]:
                print(f"🛠️  Tools mentioned: {', '.join(analysis['tools_mentioned'])}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Error: {e}")
            
            return {
                "prompt": prompt_data["prompt"],
                "expected_behavior": prompt_data["expected_behavior"],
                "success": False,
                "error": str(e),
                "execution_time": execution_time,
                "timestamp": time.time()
            }
    
    def analyze_orchestration_response(self, response: str, prompt_data: Dict) -> Dict[str, Any]:
        """Analyze response for orchestration intelligence."""
        response_lower = response.lower()
        
        # Check for orchestration indicators
        orchestration_indicators = {
            "planning": ["here's my plan", "i'll handle this", "let me break this down"],
            "coordination": ["first, i'll", "then, i'll", "next, i'll", "finally, i'll"],
            "tools": ["aider", "lavague", "open interpreter", "rag", "robot framework"],
            "workflow": ["workflow", "coordinate", "step by step", "sequence"]
        }
        
        found_indicators = {}
        for category, indicators in orchestration_indicators.items():
            found_indicators[category] = [ind for ind in indicators if ind in response_lower]
        
        # Determine orchestration type
        has_planning = bool(found_indicators["planning"])
        has_coordination = bool(found_indicators["coordination"])
        has_tools = bool(found_indicators["tools"])
        has_workflow = bool(found_indicators["workflow"])
        
        if has_planning and has_coordination and has_tools:
            orchestration_type = "full_orchestration"
        elif has_coordination and has_tools:
            orchestration_type = "partial_orchestration"
        elif has_tools:
            orchestration_type = "tool_awareness"
        else:
            orchestration_type = "no_orchestration"
        
        # Check behavior match
        expected = prompt_data["expected_behavior"]
        behavior_match = self.check_behavior_match(orchestration_type, expected)
        
        # Check tool mentions
        expected_tools = prompt_data.get("expected_tools", [])
        tools_mentioned = found_indicators["tools"]
        tool_match = any(tool in response_lower for tool in expected_tools)
        
        return {
            "orchestration_detected": orchestration_type != "no_orchestration",
            "orchestration_type": orchestration_type,
            "behavior_match": behavior_match,
            "found_indicators": found_indicators,
            "tools_mentioned": tools_mentioned,
            "expected_tools": expected_tools,
            "tool_match": tool_match,
            "response_quality": self.assess_response_quality(response, prompt_data)
        }
    
    def check_behavior_match(self, detected: str, expected: str) -> bool:
        """Check if detected behavior matches expected."""
        behavior_mapping = {
            "single_tool": ["no_orchestration", "tool_awareness"],
            "orchestration": ["partial_orchestration", "full_orchestration"],
            "complex_orchestration": ["full_orchestration"]
        }
        
        expected_types = behavior_mapping.get(expected, [expected])
        return detected in expected_types
    
    def assess_response_quality(self, response: str, prompt_data: Dict) -> str:
        """Assess the quality of the response."""
        response_lower = response.lower()
        
        # Quality indicators
        quality_indicators = {
            "professional": ["i'll help", "here's how", "let me", "i can"],
            "detailed": len(response) > 100,
            "structured": any(word in response_lower for word in ["first", "then", "next", "finally"]),
            "tool_specific": any(tool in response_lower for tool in prompt_data.get("expected_tools", []))
        }
        
        quality_score = sum([
            1 if quality_indicators["professional"] else 0,
            1 if quality_indicators["detailed"] else 0,
            1 if quality_indicators["structured"] else 0,
            1 if quality_indicators["tool_specific"] else 0
        ])
        
        if quality_score >= 3:
            return "high"
        elif quality_score >= 2:
            return "medium"
        else:
            return "low"
    
    async def provide_learning_feedback(self, result: Dict[str, Any]):
        """Provide feedback to the learning system."""
        if not result["success"]:
            return
        
        try:
            from jarvis.core.orchestration.integration_layer import get_orchestration_integration
            
            integration = get_orchestration_integration()
            if not integration.orchestration_available:
                return
            
            # Simulate workflow completion feedback
            workflow_id = f"learning_{int(time.time())}"
            
            # Determine success based on behavior match
            success = result["analysis"]["behavior_match"]
            
            # Create mock performance data
            if hasattr(integration, 'performance_tracker') and integration.performance_tracker:
                integration.performance_tracker.track_workflow_start(
                    workflow_id, 
                    result["complexity"]
                )
                
                integration.performance_tracker.track_workflow_completion(
                    workflow_id,
                    success,
                    result["execution_time"],
                    0 if success else 1
                )
            
            print(f"📊 Learning feedback provided: {'✅' if success else '❌'}")
            
        except Exception as e:
            print(f"⚠️  Could not provide learning feedback: {e}")
    
    def analyze_phase_progress(self, phase: str, results: List[Dict]):
        """Analyze progress for a learning phase."""
        successful_results = [r for r in results if r["success"]]
        behavior_matches = [r for r in successful_results if r["analysis"]["behavior_match"]]
        
        print(f"\n📊 {phase} Results:")
        print(f"✅ Successful responses: {len(successful_results)}/{len(results)}")
        print(f"🎯 Behavior matches: {len(behavior_matches)}/{len(successful_results)}")
        
        if successful_results:
            avg_time = sum(r["execution_time"] for r in successful_results) / len(successful_results)
            print(f"⏱️  Average response time: {avg_time:.2f}s")
            
            # Quality distribution
            quality_dist = {}
            for result in successful_results:
                quality = result["analysis"]["response_quality"]
                quality_dist[quality] = quality_dist.get(quality, 0) + 1
            
            print(f"📈 Quality distribution: {quality_dist}")
        
        self.learning_progress.append({
            "phase": phase,
            "total_prompts": len(results),
            "successful": len(successful_results),
            "behavior_matches": len(behavior_matches),
            "results": results
        })
    
    def generate_learning_report(self):
        """Generate comprehensive learning session report."""
        print("\n" + "=" * 50)
        print("🧠 ORCHESTRATION LEARNING SESSION REPORT")
        print("=" * 50)
        
        total_prompts = sum(phase["total_prompts"] for phase in self.learning_progress)
        total_successful = sum(phase["successful"] for phase in self.learning_progress)
        total_matches = sum(phase["behavior_matches"] for phase in self.learning_progress)
        
        print(f"\n📊 OVERALL LEARNING PROGRESS:")
        print(f"Total prompts processed: {total_prompts}")
        print(f"Successful responses: {total_successful}/{total_prompts} ({total_successful/total_prompts*100:.1f}%)")
        print(f"Behavior matches: {total_matches}/{total_successful} ({total_matches/total_successful*100:.1f}%)")
        
        print(f"\n📈 PHASE-BY-PHASE PROGRESS:")
        for phase_data in self.learning_progress:
            success_rate = phase_data["successful"] / phase_data["total_prompts"] * 100
            match_rate = phase_data["behavior_matches"] / max(phase_data["successful"], 1) * 100
            
            print(f"\n{phase_data['phase']}:")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Behavior Match Rate: {match_rate:.1f}%")
        
        # Learning insights
        print(f"\n🔍 LEARNING INSIGHTS:")
        
        # Check improvement across phases
        if len(self.learning_progress) >= 2:
            phase1_match_rate = self.learning_progress[0]["behavior_matches"] / max(self.learning_progress[0]["successful"], 1)
            phase3_match_rate = self.learning_progress[-1]["behavior_matches"] / max(self.learning_progress[-1]["successful"], 1)
            
            if phase3_match_rate > phase1_match_rate:
                print("✅ Orchestration intelligence improved from simple to complex prompts")
            else:
                print("⚠️  Orchestration performance declined with complexity - needs improvement")
        
        # Save learning data
        self.save_learning_data()
        print(f"\n💾 Learning session data saved to orchestration_learning_session.json")
    
    def save_learning_data(self):
        """Save learning session data for analysis."""
        learning_data = {
            "session_summary": {
                "total_prompts": sum(phase["total_prompts"] for phase in self.learning_progress),
                "total_successful": sum(phase["successful"] for phase in self.learning_progress),
                "total_matches": sum(phase["behavior_matches"] for phase in self.learning_progress),
                "session_timestamp": time.time()
            },
            "phase_progress": self.learning_progress,
            "learning_prompts": LEARNING_PROMPTS
        }
        
        with open('orchestration_learning_session.json', 'w') as f:
            json.dump(learning_data, f, indent=2, default=str)

async def main():
    """Run the orchestration learning session."""
    session = OrchestrationLearningSession()
    await session.run_learning_session()

if __name__ == "__main__":
    asyncio.run(main())
