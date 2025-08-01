"""
Real Jarvis Integration Test

Tests the optimized system with actual Jarvis agent and tools for
tool creation and complex coding tasks.
"""

import os
import sys
import time
import asyncio
import logging
from datetime import datetime

# Add jarvis to path
sys.path.insert(0, os.path.join(os.getcwd(), 'jarvis'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RealJarvisIntegrationTest:
    """Test optimized system with real Jarvis components."""
    
    def __init__(self):
        """Initialize integration test."""
        self.agent = None
        self.mcp_tools = []
        self.config = None
        
        print("🔗 Real Jarvis Integration Test")
        print("=" * 40)
    
    async def initialize_real_components(self):
        """Initialize real Jarvis components."""
        try:
            print("🚀 Initializing Real Jarvis Components...")
            
            # Import and initialize configuration
            from jarvis.config import get_config
            self.config = get_config()
            print(f"✅ Config loaded: {self.config.llm.model}")
            
            # Initialize MCP tools
            print("🔧 Loading MCP tools...")
            try:
                from jarvis.core.mcp_tool_integration import initialize_mcp_tools
                self.mcp_tools = await initialize_mcp_tools()
                print(f"✅ Loaded {len(self.mcp_tools)} MCP tools")
            except Exception as e:
                print(f"⚠️  MCP tools not available: {e}")
                self.mcp_tools = []
            
            # Initialize agent
            print("🧠 Initializing Jarvis Agent...")
            try:
                from jarvis.core.agent import JarvisAgent

                # Use the actual config objects directly
                self.agent = JarvisAgent(self.config.llm, self.config.agent)

                # Initialize with tools
                if self.mcp_tools:
                    self.agent.initialize(self.mcp_tools)
                else:
                    self.agent.initialize([])

                print("✅ Real Jarvis Agent initialized")

            except Exception as e:
                print(f"⚠️  Agent initialization failed: {e}")
                import traceback
                traceback.print_exc()
                self.agent = None
            
            return True
            
        except Exception as e:
            print(f"❌ Component initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_tool_creation_with_real_agent(self):
        """Test tool creation using real Jarvis agent."""
        print("\n🔧 Testing Tool Creation with Real Agent")
        print("-" * 40)
        
        if not self.agent:
            print("❌ No agent available - using fallback")
            return False
        
        try:
            # Test 1: Simple function creation
            print("\n🧪 Test 1: Simple Function Creation")
            query = "Create a Python function that calculates the factorial of a number. Include error handling and documentation."
            
            print(f"Query: {query}")
            
            start_time = time.time()
            result = await self.agent.process_input(query)
            processing_time = time.time() - start_time
            
            # Extract response content
            if hasattr(result, 'content'):
                response = result.content
            elif isinstance(result, str):
                response = result
            else:
                response = str(result)
            
            print(f"Response: {response[:200]}...")
            print(f"Processing time: {processing_time*1000:.1f}ms")
            
            # Validate response
            has_function = "def " in response or "function" in response.lower()
            has_factorial = "factorial" in response.lower()
            reasonable_time = processing_time < 30.0
            
            test1_success = has_function and has_factorial and reasonable_time
            print(f"Test 1 Result: {'✅ PASSED' if test1_success else '❌ FAILED'}")
            
            # Test 2: Complex tool creation
            print("\n🧪 Test 2: Complex Tool Creation")
            query2 = "Create a Python script that can read CSV files, perform data analysis, and generate visualizations. Include proper error handling and make it modular."
            
            print(f"Query: {query2}")
            
            start_time = time.time()
            result2 = await self.agent.process_input(query2)
            processing_time2 = time.time() - start_time
            
            if hasattr(result2, 'content'):
                response2 = result2.content
            elif isinstance(result2, str):
                response2 = result2
            else:
                response2 = str(result2)
            
            print(f"Response: {response2[:200]}...")
            print(f"Processing time: {processing_time2*1000:.1f}ms")
            
            # Validate complex response
            has_csv = "csv" in response2.lower()
            has_analysis = "analysis" in response2.lower() or "pandas" in response2.lower()
            has_visualization = "plot" in response2.lower() or "chart" in response2.lower() or "matplotlib" in response2.lower()
            reasonable_time2 = processing_time2 < 45.0
            
            test2_success = has_csv and (has_analysis or has_visualization) and reasonable_time2
            print(f"Test 2 Result: {'✅ PASSED' if test2_success else '❌ FAILED'}")
            
            return test1_success and test2_success
            
        except Exception as e:
            print(f"❌ Tool creation test failed: {e}")
            return False
    
    async def test_complex_coding_with_real_agent(self):
        """Test complex coding tasks with real agent."""
        print("\n💻 Testing Complex Coding with Real Agent")
        print("-" * 40)
        
        if not self.agent:
            print("❌ No agent available - using fallback")
            return False
        
        try:
            # Test: Web scraper development
            print("\n🧪 Test: Web Scraper Development")
            query = """
            Create a complete web scraper that:
            1. Scrapes product information from e-commerce sites
            2. Handles rate limiting and errors gracefully
            3. Saves data to CSV format
            4. Includes a command-line interface
            
            Provide the complete working code with proper structure.
            """
            
            print(f"Query: {query.strip()}")
            
            start_time = time.time()
            result = await self.agent.process_input(query)
            processing_time = time.time() - start_time
            
            if hasattr(result, 'content'):
                response = result.content
            elif isinstance(result, str):
                response = result
            else:
                response = str(result)
            
            print(f"Response: {response[:300]}...")
            print(f"Processing time: {processing_time*1000:.1f}ms")
            
            # Validate web scraper response
            has_scraper = "scraper" in response.lower() or "scraping" in response.lower()
            has_requests = "requests" in response.lower() or "urllib" in response.lower()
            has_csv = "csv" in response.lower()
            has_error_handling = "try" in response.lower() or "except" in response.lower()
            reasonable_time = processing_time < 60.0
            
            scraper_success = has_scraper and (has_requests or has_csv) and reasonable_time
            print(f"Web Scraper Test: {'✅ PASSED' if scraper_success else '❌ FAILED'}")
            
            return scraper_success
            
        except Exception as e:
            print(f"❌ Complex coding test failed: {e}")
            return False
    
    async def test_optimized_routing_with_real_processing(self):
        """Test optimized routing combined with real processing."""
        print("\n⚡ Testing Optimized Routing + Real Processing")
        print("-" * 40)
        
        try:
            # Import optimized components
            from jarvis.core.classification.smart_classifier import get_smart_classifier
            classifier = get_smart_classifier()
            
            test_queries = [
                {
                    "query": "Hello there",
                    "expected_complexity": "instant",
                    "max_time": 0.1
                },
                {
                    "query": "Create a calculator function",
                    "expected_complexity": "complex_multi_step",
                    "max_time": 30.0
                }
            ]
            
            results = []
            
            for test in test_queries:
                print(f"\n🔍 Testing: {test['query']}")
                
                # Step 1: Classify with optimized system
                classification = classifier.classify_query(test['query'])
                print(f"   Classification: {classification.complexity.value} (confidence: {classification.confidence:.2f})")
                
                # Step 2: Process based on classification
                start_time = time.time()
                
                if classification.complexity.value == "instant":
                    # Handle instantly
                    response = "Hello! I'm here to help you."
                    processing_time = time.time() - start_time
                    
                elif self.agent and classification.complexity.value in ["complex_multi_step", "simple_reasoning"]:
                    # Use real agent
                    result = await self.agent.process_input(test['query'])
                    processing_time = time.time() - start_time
                    
                    if hasattr(result, 'content'):
                        response = result.content
                    else:
                        response = str(result)
                else:
                    # Fallback
                    response = f"I understand you want help with: {test['query']}"
                    processing_time = time.time() - start_time
                
                print(f"   Response: {response[:100]}...")
                print(f"   Processing time: {processing_time*1000:.1f}ms")
                
                # Validate
                complexity_correct = classification.complexity.value == test['expected_complexity']
                time_acceptable = processing_time <= test['max_time']
                has_response = len(response) > 10
                
                test_passed = complexity_correct and time_acceptable and has_response
                results.append(test_passed)
                
                print(f"   Result: {'✅ PASSED' if test_passed else '❌ FAILED'}")
            
            overall_success = all(results)
            print(f"\nOptimized Routing Test: {'✅ PASSED' if overall_success else '❌ FAILED'}")
            
            return overall_success
            
        except Exception as e:
            print(f"❌ Optimized routing test failed: {e}")
            return False
    
    def generate_integration_report(self, tool_creation_success, coding_success, routing_success):
        """Generate comprehensive integration report."""
        print("\n" + "=" * 60)
        print("📋 REAL JARVIS INTEGRATION REPORT")
        print("=" * 60)
        
        print(f"Agent Available: {'✅' if self.agent else '❌'}")
        print(f"MCP Tools Loaded: {len(self.mcp_tools)}")
        print(f"Configuration: {'✅' if self.config else '❌'}")
        
        print("\n📊 Test Results:")
        print(f"  {'✅' if tool_creation_success else '❌'} Tool Creation with Real Agent")
        print(f"  {'✅' if coding_success else '❌'} Complex Coding Tasks")
        print(f"  {'✅' if routing_success else '❌'} Optimized Routing + Real Processing")
        
        overall_success = tool_creation_success and coding_success and routing_success
        
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if overall_success:
            print("🎉 REAL JARVIS INTEGRATION SUCCESSFUL!")
            print("✅ Optimized performance framework working")
            print("✅ Real agent and tools integrated")
            print("✅ Tool creation capabilities confirmed")
            print("✅ Complex coding tasks working")
            print("🚀 READY FOR PRODUCTION DEPLOYMENT!")
        else:
            print("⚠️  INTEGRATION PARTIALLY SUCCESSFUL")
            print("The optimization framework is working, but some")
            print("real agent capabilities need refinement.")
        
        return overall_success


async def main():
    """Run real Jarvis integration test."""
    tester = RealJarvisIntegrationTest()
    
    try:
        # Initialize components
        components_ready = await tester.initialize_real_components()
        
        if not components_ready:
            print("❌ Component initialization failed")
            return False
        
        # Run tests
        tool_creation_success = await tester.test_tool_creation_with_real_agent()
        coding_success = await tester.test_complex_coding_with_real_agent()
        routing_success = await tester.test_optimized_routing_with_real_processing()
        
        # Generate report
        overall_success = tester.generate_integration_report(
            tool_creation_success, coding_success, routing_success
        )
        
        return overall_success
        
    except Exception as e:
        print(f"\n💥 INTEGRATION TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🔗 Starting Real Jarvis Integration Test...")
    success = asyncio.run(main())
    exit(0 if success else 1)
