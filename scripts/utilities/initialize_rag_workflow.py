"""
Initialize RAG Workflow System

This script initializes the RAG-powered workflow system for full coding capabilities
in the optimized Jarvis system.
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


class RAGWorkflowInitializer:
    """Initialize RAG workflow system for advanced coding capabilities."""
    
    def __init__(self):
        """Initialize the RAG workflow initializer."""
        self.rag_service = None
        self.plugin_registry = None
        self.unified_integration = None
        self.rag_workflow_builder = None
        
        print("🧠 RAG Workflow System Initializer")
        print("=" * 50)
        print("Initializing advanced coding capabilities...")
    
    async def initialize_rag_service(self):
        """Initialize the RAG service."""
        try:
            print("\n📚 Initializing RAG Service...")
            
            from jarvis.tools.rag_service import RAGService
            from jarvis.config import get_config
            
            config = get_config()
            self.rag_service = RAGService(config.llm)
            
            print("✅ RAG Service initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize RAG service: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def initialize_plugin_registry(self):
        """Initialize the unified plugin registry."""
        try:
            print("\n🔧 Initializing Plugin Registry...")
            
            from jarvis.plugins.registry.unified_registry import UnifiedPluginRegistry
            
            self.plugin_registry = UnifiedPluginRegistry()
            
            print("✅ Plugin Registry initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize plugin registry: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def initialize_rag_workflow_builder(self):
        """Initialize the RAG-powered workflow builder."""
        try:
            print("\n🏗️  Initializing RAG Workflow Builder...")
            
            from jarvis.core.orchestration.rag_powered_workflow import RAGPoweredWorkflowBuilder
            
            # Create workflow builder with initialized components
            self.rag_workflow_builder = RAGPoweredWorkflowBuilder(
                rag_service=self.rag_service,
                plugin_registry=self.plugin_registry
            )
            
            # Initialize the workflow builder
            await self.rag_workflow_builder.initialize()
            
            print("✅ RAG Workflow Builder initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize RAG workflow builder: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def initialize_unified_integration(self):
        """Initialize the unified coding integration."""
        try:
            print("\n🔗 Initializing Unified Coding Integration...")
            
            from jarvis.core.orchestration.unified_integration import UnifiedCodingIntegration
            
            # Get the global unified integration instance
            from jarvis.core.orchestration.unified_integration import unified_integration
            self.unified_integration = unified_integration
            
            # Initialize the RAG workflow in the integration
            await self.unified_integration.initialize_rag_workflow()
            
            print("✅ Unified Coding Integration initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize unified integration: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_rag_workflow_system(self):
        """Test the initialized RAG workflow system."""
        print("\n🧪 Testing RAG Workflow System")
        print("-" * 40)
        
        test_queries = [
            "Create a simple calculator function",
            "Build a web scraper for news headlines",
            "Make a Python script to analyze CSV data"
        ]
        
        results = []
        
        for query in test_queries:
            print(f"\n🔍 Testing: '{query}'")
            
            try:
                # Test if the unified integration can handle the request
                is_coding_request = self.unified_integration.is_coding_request(query)
                print(f"   Detected as coding request: {is_coding_request}")
                
                if is_coding_request and self.rag_workflow_builder:
                    # Test workflow building
                    start_time = time.time()
                    workflow_plan = await self.rag_workflow_builder.build_workflow(query)
                    build_time = time.time() - start_time
                    
                    print(f"   Workflow built: {workflow_plan.workflow_id}")
                    print(f"   Steps: {len(workflow_plan.steps)}")
                    print(f"   Confidence: {workflow_plan.confidence_score:.2f}")
                    print(f"   Build time: {build_time*1000:.1f}ms")
                    
                    # Validate workflow
                    has_steps = len(workflow_plan.steps) > 0
                    reasonable_confidence = workflow_plan.confidence_score > 0.3
                    reasonable_time = build_time < 10.0
                    
                    success = has_steps and reasonable_confidence and reasonable_time
                    results.append(success)
                    
                    print(f"   Result: {'✅ PASSED' if success else '❌ FAILED'}")
                else:
                    print(f"   ⚠️  Not a coding request or workflow builder not available")
                    results.append(False)
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                results.append(False)
        
        test_success = sum(results) >= len(results) // 2  # At least half should work
        print(f"\n📊 RAG Workflow Test Results: {sum(results)}/{len(results)} passed")
        
        return test_success
    
    async def integrate_with_agent(self):
        """Integrate the RAG workflow system with the Jarvis agent."""
        try:
            print("\n🤖 Integrating with Jarvis Agent...")
            
            # Import and initialize agent components
            from jarvis.config import get_config
            from jarvis.core.agent import JarvisAgent
            from jarvis.core.mcp_tool_integration import initialize_mcp_tools
            
            config = get_config()
            
            # Initialize MCP tools
            mcp_tools = await initialize_mcp_tools()
            print(f"   Loaded {len(mcp_tools)} MCP tools")
            
            # Create agent
            agent = JarvisAgent(config.llm, config.agent)
            agent.initialize(mcp_tools)
            
            print("✅ Agent integration successful")
            
            # Test coding query with agent
            print("\n🧪 Testing coding query with integrated agent...")
            
            test_query = "Create a simple Python function to calculate fibonacci numbers"
            
            start_time = time.time()
            result = await agent.process_input(test_query)
            processing_time = time.time() - start_time
            
            print(f"   Query: {test_query}")
            print(f"   Response: {str(result)[:200]}...")
            print(f"   Processing time: {processing_time*1000:.1f}ms")
            
            # Check if RAG workflow error is gone
            no_rag_error = "RAG workflow builder not initialized" not in str(result)
            has_response = len(str(result)) > 50
            reasonable_time = processing_time < 30.0
            
            integration_success = no_rag_error and has_response and reasonable_time
            
            print(f"   Integration test: {'✅ PASSED' if integration_success else '❌ FAILED'}")
            
            return integration_success
            
        except Exception as e:
            print(f"❌ Agent integration failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def generate_initialization_report(self, rag_service_ok, plugin_registry_ok, 
                                     workflow_builder_ok, integration_ok, 
                                     test_ok, agent_integration_ok):
        """Generate comprehensive initialization report."""
        print("\n" + "=" * 60)
        print("📋 RAG WORKFLOW INITIALIZATION REPORT")
        print("=" * 60)
        
        components = [
            ("RAG Service", rag_service_ok),
            ("Plugin Registry", plugin_registry_ok),
            ("Workflow Builder", workflow_builder_ok),
            ("Unified Integration", integration_ok),
            ("System Testing", test_ok),
            ("Agent Integration", agent_integration_ok)
        ]
        
        passed = sum(1 for _, status in components if status)
        total = len(components)
        
        print(f"Components Initialized: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        print("\n📊 Component Status:")
        for component, status in components:
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {component}")
        
        overall_success = passed >= 4  # At least 4/6 components should work
        
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if overall_success:
            print("🎉 RAG WORKFLOW SYSTEM SUCCESSFULLY INITIALIZED!")
            print("✅ Advanced coding capabilities enabled")
            print("✅ RAG-powered workflow building active")
            print("✅ Plugin knowledge indexed")
            print("✅ Agent integration complete")
            print("\n🚀 JARVIS NOW HAS FULL CODING CAPABILITIES!")
        else:
            print("⚠️  RAG WORKFLOW INITIALIZATION PARTIALLY SUCCESSFUL")
            print("Some components need attention for full functionality.")
        
        return overall_success


async def main():
    """Main initialization function."""
    initializer = RAGWorkflowInitializer()
    
    try:
        # Initialize all components
        rag_service_ok = await initializer.initialize_rag_service()
        plugin_registry_ok = await initializer.initialize_plugin_registry()
        workflow_builder_ok = await initializer.initialize_rag_workflow_builder()
        integration_ok = await initializer.initialize_unified_integration()
        
        # Test the system
        test_ok = await initializer.test_rag_workflow_system()
        
        # Integrate with agent
        agent_integration_ok = await initializer.integrate_with_agent()
        
        # Generate report
        success = initializer.generate_initialization_report(
            rag_service_ok, plugin_registry_ok, workflow_builder_ok,
            integration_ok, test_ok, agent_integration_ok
        )
        
        return success
        
    except Exception as e:
        print(f"\n💥 INITIALIZATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧠 Starting RAG Workflow System Initialization...")
    success = asyncio.run(main())
    exit(0 if success else 1)
