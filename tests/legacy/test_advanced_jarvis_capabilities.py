"""
Advanced Capabilities Testing for Optimized Jarvis

Tests the most critical advanced features:
1. Making and Saving Tools (tool creation, plugin system integration)
2. Complex Coding Tasks (multi-step development workflows)
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


class AdvancedCapabilitiesTest:
    """Test advanced Jarvis capabilities with optimized system."""
    
    def __init__(self):
        """Initialize advanced testing suite."""
        self.test_results = {}
        self.created_files = []
        self.start_time = datetime.now()
        
        print("🚀 Advanced Jarvis Capabilities Testing")
        print("=" * 50)
        print("Testing: Tool Creation & Complex Coding Tasks")
        print("=" * 50)
    
    async def test_tool_creation_and_saving(self):
        """Test creating and saving new tools."""
        print("\n🔧 Phase 1: Tool Creation and Saving")
        print("-" * 40)
        
        try:
            from jarvis.core.optimized_controller import get_optimized_controller
            controller = get_optimized_controller()
            
            # Test 1: Create a simple utility tool
            print("\n🧪 Test 1: Creating a Simple Utility Tool")
            tool_creation_query = """
            Create a Python tool that can calculate the factorial of a number. 
            The tool should be saved as a reusable function that I can call later.
            Make sure it handles edge cases and includes proper documentation.
            """
            
            print(f"Query: {tool_creation_query.strip()}")
            
            start_time = time.time()
            result = await controller.process_query(tool_creation_query)
            processing_time = time.time() - start_time
            
            print(f"Response: {result.response}")
            print(f"Processing time: {processing_time*1000:.1f}ms")
            print(f"Complexity: {result.complexity.value}")
            print(f"Tools used: {result.tools_used}")
            print(f"Budget met: {'✅' if result.performance_budget_met else '❌'}")
            
            # Validate tool creation response
            tool_creation_success = (
                "factorial" in result.response.lower() and
                ("def " in result.response or "function" in result.response.lower()) and
                processing_time < 10.0 and
                result.performance_budget_met
            )
            
            print(f"Tool Creation Test 1: {'✅ PASSED' if tool_creation_success else '❌ FAILED'}")
            
            # Test 2: Create a more complex tool with file operations
            print("\n🧪 Test 2: Creating a File Processing Tool")
            complex_tool_query = """
            Create a Python tool that can read a CSV file, analyze the data, 
            and generate a summary report with statistics. The tool should:
            1. Read CSV files safely
            2. Calculate basic statistics (mean, median, mode)
            3. Generate a formatted report
            4. Save the report to a new file
            Save this as a reusable tool I can use for data analysis.
            """
            
            print(f"Query: {complex_tool_query.strip()}")
            
            start_time = time.time()
            result2 = await controller.process_query(complex_tool_query)
            processing_time2 = time.time() - start_time
            
            print(f"Response: {result2.response[:200]}...")
            print(f"Processing time: {processing_time2*1000:.1f}ms")
            print(f"Complexity: {result2.complexity.value}")
            print(f"Tools used: {result2.tools_used}")
            print(f"Budget met: {'✅' if result2.performance_budget_met else '❌'}")
            
            # Validate complex tool creation
            complex_tool_success = (
                "csv" in result2.response.lower() and
                ("statistics" in result2.response.lower() or "analysis" in result2.response.lower()) and
                processing_time2 < 15.0 and
                result2.performance_budget_met
            )
            
            print(f"Tool Creation Test 2: {'✅ PASSED' if complex_tool_success else '❌ FAILED'}")
            
            # Test 3: Tool saving and retrieval
            print("\n🧪 Test 3: Tool Saving and Retrieval")
            save_tool_query = """
            Save the factorial tool we just created so I can use it in future conversations.
            Make sure it's properly stored in the tool system.
            """
            
            start_time = time.time()
            result3 = await controller.process_query(save_tool_query)
            processing_time3 = time.time() - start_time
            
            print(f"Response: {result3.response}")
            print(f"Processing time: {processing_time3*1000:.1f}ms")
            
            tool_saving_success = (
                ("saved" in result3.response.lower() or "stored" in result3.response.lower()) and
                processing_time3 < 5.0
            )
            
            print(f"Tool Saving Test: {'✅ PASSED' if tool_saving_success else '❌ FAILED'}")
            
            # Overall tool creation assessment
            overall_tool_success = tool_creation_success and complex_tool_success and tool_saving_success
            self.test_results["tool_creation_and_saving"] = overall_tool_success
            
            print(f"\n✅ Tool Creation & Saving: {'PASSED' if overall_tool_success else 'FAILED'}")
            
        except Exception as e:
            print(f"❌ Tool Creation & Saving: FAILED - {e}")
            self.test_results["tool_creation_and_saving"] = False
    
    async def test_complex_coding_tasks(self):
        """Test complex multi-step coding workflows."""
        print("\n💻 Phase 2: Complex Coding Tasks")
        print("-" * 40)
        
        try:
            from jarvis.core.optimized_controller import get_optimized_controller
            controller = get_optimized_controller()
            
            # Test 1: Multi-step web scraper development
            print("\n🧪 Test 1: Multi-Step Web Scraper Development")
            web_scraper_query = """
            I need you to create a complete web scraper that:
            1. Scrapes product information from a sample e-commerce site
            2. Extracts product names, prices, and ratings
            3. Stores the data in a CSV file
            4. Includes error handling and rate limiting
            5. Has a command-line interface
            
            Walk me through each step and create the complete solution.
            """
            
            print(f"Query: {web_scraper_query.strip()}")
            
            start_time = time.time()
            result = await controller.process_query(web_scraper_query)
            processing_time = time.time() - start_time
            
            print(f"Response: {result.response[:300]}...")
            print(f"Processing time: {processing_time*1000:.1f}ms")
            print(f"Complexity: {result.complexity.value}")
            print(f"Tools used: {result.tools_used}")
            print(f"Budget met: {'✅' if result.performance_budget_met else '❌'}")
            
            # Validate web scraper development
            web_scraper_success = (
                result.complexity.value == "complex_multi_step" and
                ("scraper" in result.response.lower() or "scraping" in result.response.lower()) and
                ("csv" in result.response.lower() or "data" in result.response.lower()) and
                processing_time < 20.0 and
                result.performance_budget_met
            )
            
            print(f"Web Scraper Development: {'✅ PASSED' if web_scraper_success else '❌ FAILED'}")
            
            # Test 2: Data analysis pipeline
            print("\n🧪 Test 2: Data Analysis Pipeline Development")
            data_pipeline_query = """
            Create a complete data analysis pipeline that:
            1. Reads data from multiple CSV files
            2. Cleans and preprocesses the data
            3. Performs statistical analysis
            4. Creates visualizations (charts and graphs)
            5. Generates an automated report
            6. Exports results in multiple formats (PDF, Excel, JSON)
            
            Include proper error handling, logging, and make it modular.
            """
            
            print(f"Query: {data_pipeline_query.strip()}")
            
            start_time = time.time()
            result2 = await controller.process_query(data_pipeline_query)
            processing_time2 = time.time() - start_time
            
            print(f"Response: {result2.response[:300]}...")
            print(f"Processing time: {processing_time2*1000:.1f}ms")
            print(f"Complexity: {result2.complexity.value}")
            print(f"Tools used: {result2.tools_used}")
            print(f"Budget met: {'✅' if result2.performance_budget_met else '❌'}")
            
            # Validate data pipeline development
            data_pipeline_success = (
                result2.complexity.value == "complex_multi_step" and
                ("analysis" in result2.response.lower() or "pipeline" in result2.response.lower()) and
                ("visualization" in result2.response.lower() or "chart" in result2.response.lower()) and
                processing_time2 < 20.0 and
                result2.performance_budget_met
            )
            
            print(f"Data Pipeline Development: {'✅ PASSED' if data_pipeline_success else '❌ FAILED'}")
            
            # Test 3: API development with database integration
            print("\n🧪 Test 3: API Development with Database Integration")
            api_development_query = """
            Build a complete REST API that:
            1. Uses Flask or FastAPI framework
            2. Connects to a SQLite database
            3. Has CRUD operations for a 'tasks' table
            4. Includes authentication and validation
            5. Has proper error handling and logging
            6. Includes API documentation
            7. Has unit tests
            
            Create the complete project structure and all necessary files.
            """
            
            print(f"Query: {api_development_query.strip()}")
            
            start_time = time.time()
            result3 = await controller.process_query(api_development_query)
            processing_time3 = time.time() - start_time
            
            print(f"Response: {result3.response[:300]}...")
            print(f"Processing time: {processing_time3*1000:.1f}ms")
            print(f"Complexity: {result3.complexity.value}")
            print(f"Tools used: {result3.tools_used}")
            print(f"Budget met: {'✅' if result3.performance_budget_met else '❌'}")
            
            # Validate API development
            api_development_success = (
                result3.complexity.value == "complex_multi_step" and
                ("api" in result3.response.lower() or "flask" in result3.response.lower() or "fastapi" in result3.response.lower()) and
                ("database" in result3.response.lower() or "sqlite" in result3.response.lower()) and
                processing_time3 < 20.0 and
                result3.performance_budget_met
            )
            
            print(f"API Development: {'✅ PASSED' if api_development_success else '❌ FAILED'}")
            
            # Test 4: Code optimization and refactoring
            print("\n🧪 Test 4: Code Optimization and Refactoring")
            optimization_query = """
            I have a slow Python script that processes large datasets. 
            Help me optimize it by:
            1. Analyzing the current performance bottlenecks
            2. Implementing parallel processing
            3. Adding memory optimization techniques
            4. Using more efficient algorithms
            5. Adding performance monitoring
            6. Creating benchmarks to measure improvements
            
            Show me the before and after code with performance comparisons.
            """
            
            start_time = time.time()
            result4 = await controller.process_query(optimization_query)
            processing_time4 = time.time() - start_time
            
            print(f"Response: {result4.response[:300]}...")
            print(f"Processing time: {processing_time4*1000:.1f}ms")
            print(f"Complexity: {result4.complexity.value}")
            print(f"Tools used: {result4.tools_used}")
            
            optimization_success = (
                ("optimization" in result4.response.lower() or "performance" in result4.response.lower()) and
                ("parallel" in result4.response.lower() or "efficient" in result4.response.lower()) and
                processing_time4 < 15.0
            )
            
            print(f"Code Optimization: {'✅ PASSED' if optimization_success else '❌ FAILED'}")
            
            # Overall complex coding assessment
            overall_coding_success = (
                web_scraper_success and 
                data_pipeline_success and 
                api_development_success and 
                optimization_success
            )
            
            self.test_results["complex_coding_tasks"] = overall_coding_success
            
            print(f"\n✅ Complex Coding Tasks: {'PASSED' if overall_coding_success else 'FAILED'}")
            
        except Exception as e:
            print(f"❌ Complex Coding Tasks: FAILED - {e}")
            self.test_results["complex_coding_tasks"] = False
    
    async def test_integration_workflow(self):
        """Test end-to-end workflow combining tool creation and coding."""
        print("\n🔄 Phase 3: Integration Workflow Test")
        print("-" * 40)
        
        try:
            from jarvis.core.optimized_controller import get_optimized_controller
            controller = get_optimized_controller()
            
            # Test complete workflow: Create tool → Use tool → Enhance tool
            workflow_query = """
            Let's do a complete development workflow:
            1. Create a simple calculator tool with basic operations
            2. Test the calculator tool with some examples
            3. Enhance it to include scientific functions
            4. Save the enhanced version for future use
            5. Create documentation for the tool
            
            Walk me through each step and show the results.
            """
            
            print(f"Workflow Query: {workflow_query.strip()}")
            
            start_time = time.time()
            result = await controller.process_query(workflow_query)
            processing_time = time.time() - start_time
            
            print(f"Response: {result.response[:400]}...")
            print(f"Processing time: {processing_time*1000:.1f}ms")
            print(f"Complexity: {result.complexity.value}")
            print(f"Tools used: {result.tools_used}")
            print(f"Budget met: {'✅' if result.performance_budget_met else '❌'}")
            
            # Validate integration workflow
            workflow_success = (
                result.complexity.value == "complex_multi_step" and
                ("calculator" in result.response.lower() or "tool" in result.response.lower()) and
                ("workflow" in result.response.lower() or "step" in result.response.lower()) and
                processing_time < 25.0 and
                result.performance_budget_met
            )
            
            self.test_results["integration_workflow"] = workflow_success
            
            print(f"Integration Workflow: {'✅ PASSED' if workflow_success else '❌ FAILED'}")
            
        except Exception as e:
            print(f"❌ Integration Workflow: FAILED - {e}")
            self.test_results["integration_workflow"] = False
    
    def generate_advanced_test_report(self):
        """Generate comprehensive report for advanced capabilities."""
        print("\n" + "=" * 60)
        print("📋 ADVANCED CAPABILITIES TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        
        print(f"Test Duration: {datetime.now() - self.start_time}")
        print(f"Total Advanced Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📊 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"  {status} {test_name.replace('_', ' ').title()}")
        
        # Critical capabilities assessment
        tool_creation_works = self.test_results.get("tool_creation_and_saving", False)
        complex_coding_works = self.test_results.get("complex_coding_tasks", False)
        
        print(f"\n🎯 CRITICAL CAPABILITIES ASSESSMENT:")
        print(f"  {'✅' if tool_creation_works else '❌'} Tool Creation & Saving")
        print(f"  {'✅' if complex_coding_works else '❌'} Complex Coding Tasks")
        
        if tool_creation_works and complex_coding_works:
            print("\n🎉 ALL CRITICAL CAPABILITIES WORKING!")
            print("   ✅ Jarvis can create and save tools")
            print("   ✅ Jarvis can handle complex coding workflows")
            print("   ✅ Performance targets met for advanced tasks")
            print("   🚀 READY FOR PRODUCTION USE!")
        else:
            print("\n⚠️  SOME CRITICAL CAPABILITIES NEED ATTENTION")
        
        return all(self.test_results.values())


async def main():
    """Run advanced capabilities testing."""
    tester = AdvancedCapabilitiesTest()
    
    try:
        # Run advanced capability tests
        await tester.test_tool_creation_and_saving()
        await tester.test_complex_coding_tasks()
        await tester.test_integration_workflow()
        
        # Generate comprehensive report
        success = tester.generate_advanced_test_report()
        
        return success
        
    except Exception as e:
        print(f"\n💥 ADVANCED TESTING ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Starting Advanced Capabilities Testing...")
    success = asyncio.run(main())
    exit(0 if success else 1)
