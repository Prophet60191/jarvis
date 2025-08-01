#!/usr/bin/env python3
"""
Tool Creation Intelligence Test

Tests whether Jarvis understands when it lacks a specific tool and intelligently
creates that tool using available agents (Aider, Open Interpreter, etc.).
"""

import sys
import asyncio
import time
from pathlib import Path

# Add the jarvis package to the path
sys.path.insert(0, str(Path(__file__).parent / "jarvis"))

# Test prompts that require tools Jarvis doesn't have
TOOL_CREATION_TESTS = [
    {
        "prompt": "Monitor my system's disk usage and send me alerts when it's getting full",
        "missing_tool": "disk_monitor",
        "expected_behavior": "create_tool",
        "expected_workflow": ["aider", "open_interpreter"],
        "description": "Should create a disk monitoring tool"
    },
    {
        "prompt": "Automatically organize my photos by date and location",
        "missing_tool": "photo_organizer", 
        "expected_behavior": "create_tool",
        "expected_workflow": ["aider", "open_interpreter"],
        "description": "Should create a photo organization tool"
    },
    {
        "prompt": "Track my daily habits and show me progress charts",
        "missing_tool": "habit_tracker",
        "expected_behavior": "create_tool", 
        "expected_workflow": ["aider", "open_interpreter"],
        "description": "Should create a habit tracking tool"
    },
    {
        "prompt": "Backup my important files to multiple cloud services automatically",
        "missing_tool": "multi_cloud_backup",
        "expected_behavior": "create_tool",
        "expected_workflow": ["aider", "open_interpreter"],
        "description": "Should create a multi-cloud backup tool"
    },
    {
        "prompt": "Parse my email receipts and track my expenses automatically",
        "missing_tool": "expense_tracker",
        "expected_behavior": "create_tool",
        "expected_workflow": ["aider", "open_interpreter"],
        "description": "Should create an expense tracking tool"
    },
    {
        "prompt": "Monitor cryptocurrency prices and alert me about significant changes",
        "missing_tool": "crypto_monitor",
        "expected_behavior": "create_tool",
        "expected_workflow": ["lavague", "aider", "open_interpreter"],
        "description": "Should create a crypto monitoring tool (with web scraping)"
    },
    {
        "prompt": "Create a personal dashboard that shows my calendar, weather, and news",
        "missing_tool": "personal_dashboard",
        "expected_behavior": "create_tool",
        "expected_workflow": ["lavague", "aider", "open_interpreter"],
        "description": "Should create a personal dashboard tool"
    },
    {
        "prompt": "Automatically generate weekly reports from my project data",
        "missing_tool": "report_generator",
        "expected_behavior": "create_tool",
        "expected_workflow": ["aider", "open_interpreter"],
        "description": "Should create a report generation tool"
    }
]

class ToolCreationIntelligenceTest:
    """Tests Jarvis's ability to recognize missing tools and create them."""
    
    def __init__(self):
        self.test_results = []
        
    async def run_tool_creation_tests(self):
        """Run comprehensive tool creation intelligence tests."""
        print("🛠️  Testing Tool Creation Intelligence")
        print("=" * 50)
        print("Testing whether Jarvis recognizes when it needs to CREATE tools...")
        print()
        
        # Initialize Jarvis
        jarvis_agent = await self.initialize_jarvis()
        if not jarvis_agent:
            print("❌ Failed to initialize Jarvis")
            return
        
        # Run each test
        for i, test_data in enumerate(TOOL_CREATION_TESTS, 1):
            print(f"🧪 Test {i}/{len(TOOL_CREATION_TESTS)}: {test_data['description']}")
            print(f"📝 Prompt: {test_data['prompt']}")
            print("-" * 40)
            
            result = await self.test_tool_creation_scenario(jarvis_agent, test_data)
            self.test_results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(2)
            print()
        
        # Generate comprehensive report
        self.generate_tool_creation_report()
    
    async def initialize_jarvis(self):
        """Initialize Jarvis with orchestration capabilities."""
        try:
            from jarvis.core.agent import JarvisAgent
            from jarvis.config import LLMConfig
            from jarvis.core.orchestration.integration_layer import initialize_orchestration
            
            # Create and initialize Jarvis
            config = LLMConfig()
            agent = JarvisAgent(config)
            agent.initialize(tools=[])
            
            # Initialize orchestration
            orchestration_available = initialize_orchestration()
            
            print(f"✅ Jarvis initialized")
            print(f"✅ Orchestration available: {orchestration_available}")
            print()
            
            return agent
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return None
    
    async def test_tool_creation_scenario(self, agent, test_data):
        """Test a specific tool creation scenario."""
        start_time = time.time()
        
        try:
            # Send prompt to Jarvis
            response = await agent.process_input(test_data["prompt"])
            execution_time = time.time() - start_time
            
            # Analyze the response for tool creation intelligence
            analysis = self.analyze_tool_creation_response(response, test_data)
            
            # Display results
            print(f"⏱️  Response time: {execution_time:.2f}s")
            print(f"🧠 Tool creation detected: {'✅ Yes' if analysis['tool_creation_detected'] else '❌ No'}")
            print(f"🛠️  Creation approach: {analysis['creation_approach']}")
            
            if analysis['mentioned_agents']:
                print(f"🤖 Agents mentioned: {', '.join(analysis['mentioned_agents'])}")
            
            if analysis['workflow_explanation']:
                print(f"📋 Workflow explained: ✅ Yes")
            else:
                print(f"📋 Workflow explained: ❌ No")
            
            # Show response preview
            response_preview = response[:300] + "..." if len(response) > 300 else response
            print(f"💬 Response preview:")
            print(f"   {response_preview}")
            
            result = {
                "test_name": test_data["description"],
                "prompt": test_data["prompt"],
                "missing_tool": test_data["missing_tool"],
                "expected_workflow": test_data["expected_workflow"],
                "response": response,
                "execution_time": execution_time,
                "analysis": analysis,
                "success": True
            }
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Error: {e}")
            
            return {
                "test_name": test_data["description"],
                "prompt": test_data["prompt"],
                "success": False,
                "error": str(e),
                "execution_time": execution_time
            }
    
    def analyze_tool_creation_response(self, response, test_data):
        """Analyze response for tool creation intelligence."""
        response_lower = response.lower()
        
        # Look for tool creation indicators
        creation_indicators = [
            "create a tool", "build a tool", "develop a tool", "make a tool",
            "create a script", "build a script", "develop a script", "write a script",
            "create a system", "build a system", "develop a system",
            "i'll create", "i'll build", "i'll develop", "i'll write",
            "let me create", "let me build", "let me develop", "let me write"
        ]
        
        tool_creation_detected = any(indicator in response_lower for indicator in creation_indicators)
        
        # Look for workflow planning indicators
        workflow_indicators = [
            "here's my plan", "i'll handle this", "let me break this down",
            "first, i'll", "then, i'll", "next, i'll", "finally, i'll"
        ]
        
        workflow_explanation = any(indicator in response_lower for indicator in workflow_indicators)
        
        # Check for mentioned agents
        agent_keywords = {
            "aider": ["aider"],
            "open_interpreter": ["open interpreter", "interpreter"],
            "lavague": ["lavague"],
            "rag": ["rag", "knowledge base", "memory"],
            "robot_framework": ["robot framework", "testing", "automated tests"]
        }
        
        mentioned_agents = []
        for agent, keywords in agent_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                mentioned_agents.append(agent)
        
        # Determine creation approach
        if tool_creation_detected and workflow_explanation:
            creation_approach = "intelligent_orchestration"
        elif tool_creation_detected:
            creation_approach = "basic_creation"
        elif mentioned_agents:
            creation_approach = "tool_awareness"
        else:
            creation_approach = "no_creation_detected"
        
        # Check workflow match
        expected_agents = test_data["expected_workflow"]
        workflow_match = all(agent in mentioned_agents for agent in expected_agents)
        
        # Assess response quality for tool creation
        quality_indicators = {
            "understands_need": any(word in response_lower for word in ["monitor", "track", "organize", "backup", "parse", "dashboard"]),
            "proposes_solution": tool_creation_detected,
            "explains_approach": workflow_explanation,
            "mentions_tools": bool(mentioned_agents),
            "professional_tone": any(phrase in response_lower for phrase in ["i'll help", "i can", "let me", "here's how"])
        }
        
        quality_score = sum(quality_indicators.values())
        
        if quality_score >= 4:
            response_quality = "excellent"
        elif quality_score >= 3:
            response_quality = "good"
        elif quality_score >= 2:
            response_quality = "fair"
        else:
            response_quality = "poor"
        
        return {
            "tool_creation_detected": tool_creation_detected,
            "creation_approach": creation_approach,
            "workflow_explanation": workflow_explanation,
            "mentioned_agents": mentioned_agents,
            "expected_agents": expected_agents,
            "workflow_match": workflow_match,
            "response_quality": response_quality,
            "quality_indicators": quality_indicators,
            "creation_indicators_found": [ind for ind in creation_indicators if ind in response_lower]
        }
    
    def generate_tool_creation_report(self):
        """Generate comprehensive tool creation intelligence report."""
        print("=" * 50)
        print("🛠️  TOOL CREATION INTELLIGENCE REPORT")
        print("=" * 50)
        
        successful_tests = [r for r in self.test_results if r["success"]]
        
        if not successful_tests:
            print("❌ No successful tests to analyze")
            return
        
        # Overall statistics
        total_tests = len(successful_tests)
        creation_detected = len([r for r in successful_tests if r["analysis"]["tool_creation_detected"]])
        workflow_explained = len([r for r in successful_tests if r["analysis"]["workflow_explanation"]])
        intelligent_orchestration = len([r for r in successful_tests if r["analysis"]["creation_approach"] == "intelligent_orchestration"])
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"Total tests: {total_tests}")
        print(f"Tool creation detected: {creation_detected}/{total_tests} ({creation_detected/total_tests*100:.1f}%)")
        print(f"Workflow explanation provided: {workflow_explained}/{total_tests} ({workflow_explained/total_tests*100:.1f}%)")
        print(f"Intelligent orchestration: {intelligent_orchestration}/{total_tests} ({intelligent_orchestration/total_tests*100:.1f}%)")
        
        # Quality distribution
        quality_dist = {}
        for result in successful_tests:
            quality = result["analysis"]["response_quality"]
            quality_dist[quality] = quality_dist.get(quality, 0) + 1
        
        print(f"\n📈 RESPONSE QUALITY DISTRIBUTION:")
        for quality, count in sorted(quality_dist.items()):
            print(f"  {quality.capitalize()}: {count}/{total_tests} ({count/total_tests*100:.1f}%)")
        
        # Agent mention analysis
        all_mentioned_agents = []
        for result in successful_tests:
            all_mentioned_agents.extend(result["analysis"]["mentioned_agents"])
        
        from collections import Counter
        agent_mentions = Counter(all_mentioned_agents)
        
        print(f"\n🤖 AGENT MENTIONS:")
        for agent, count in agent_mentions.most_common():
            print(f"  {agent}: {count}/{total_tests} tests ({count/total_tests*100:.1f}%)")
        
        # Best performing tests
        excellent_tests = [r for r in successful_tests if r["analysis"]["response_quality"] == "excellent"]
        
        print(f"\n🌟 EXCELLENT RESPONSES ({len(excellent_tests)} tests):")
        for result in excellent_tests:
            print(f"  ✅ {result['test_name']}")
            creation_indicators = result["analysis"]["creation_indicators_found"]
            if creation_indicators:
                print(f"     Creation indicators: {', '.join(creation_indicators[:3])}")
        
        # Areas for improvement
        print(f"\n🔍 AREAS FOR IMPROVEMENT:")
        
        poor_tests = [r for r in successful_tests if r["analysis"]["response_quality"] in ["poor", "fair"]]
        if poor_tests:
            print(f"  - {len(poor_tests)} tests had poor/fair response quality")
        
        no_creation_tests = [r for r in successful_tests if not r["analysis"]["tool_creation_detected"]]
        if no_creation_tests:
            print(f"  - {len(no_creation_tests)} tests didn't detect tool creation need")
        
        no_workflow_tests = [r for r in successful_tests if not r["analysis"]["workflow_explanation"]]
        if no_workflow_tests:
            print(f"  - {len(no_workflow_tests)} tests didn't provide workflow explanations")
        
        # Success criteria assessment
        print(f"\n🎯 SUCCESS CRITERIA ASSESSMENT:")
        
        creation_rate = creation_detected / total_tests
        workflow_rate = workflow_explained / total_tests
        orchestration_rate = intelligent_orchestration / total_tests
        
        print(f"  Tool Creation Detection: {'✅ Excellent' if creation_rate >= 0.8 else '⚠️ Needs Improvement' if creation_rate >= 0.6 else '❌ Poor'} ({creation_rate*100:.1f}%)")
        print(f"  Workflow Explanation: {'✅ Excellent' if workflow_rate >= 0.8 else '⚠️ Needs Improvement' if workflow_rate >= 0.6 else '❌ Poor'} ({workflow_rate*100:.1f}%)")
        print(f"  Intelligent Orchestration: {'✅ Excellent' if orchestration_rate >= 0.7 else '⚠️ Needs Improvement' if orchestration_rate >= 0.5 else '❌ Poor'} ({orchestration_rate*100:.1f}%)")
        
        # Overall assessment
        overall_score = (creation_rate + workflow_rate + orchestration_rate) / 3
        
        print(f"\n🏆 OVERALL ASSESSMENT:")
        if overall_score >= 0.8:
            print("✅ EXCELLENT - Jarvis demonstrates strong tool creation intelligence!")
        elif overall_score >= 0.6:
            print("⚠️ GOOD - Jarvis shows tool creation awareness but needs refinement")
        else:
            print("❌ NEEDS IMPROVEMENT - Tool creation intelligence requires significant work")
        
        print(f"   Overall Score: {overall_score*100:.1f}%")
        
        # Save detailed results
        import json
        with open('tool_creation_intelligence_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'creation_detected': creation_detected,
                    'workflow_explained': workflow_explained,
                    'intelligent_orchestration': intelligent_orchestration,
                    'overall_score': overall_score
                },
                'detailed_results': self.test_results
            }, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to tool_creation_intelligence_results.json")

async def main():
    """Run the tool creation intelligence tests."""
    tester = ToolCreationIntelligenceTest()
    await tester.run_tool_creation_tests()

if __name__ == "__main__":
    asyncio.run(main())
