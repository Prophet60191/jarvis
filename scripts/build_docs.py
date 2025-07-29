#!/usr/bin/env python3
"""
Documentation Build Script for Enhanced Jarvis Features

This script builds comprehensive documentation for the enhanced system integration
features using Sphinx with automatic API documentation generation.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentationBuilder:
    """Builds comprehensive documentation for enhanced Jarvis features."""
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.docs_dir = self.project_root / "docs"
        self.build_dir = self.docs_dir / "_build"
        self.api_dir = self.docs_dir / "api"
        self.source_dir = self.project_root / "jarvis"
        
        # Documentation configuration
        self.sphinx_opts = [
            "-b", "html",  # Build HTML
            "-E",          # Don't use saved environment
            "-a",          # Write all files
            "-j", "auto",  # Use multiple processes
        ]
    
    def clean_build_directory(self) -> None:
        """Clean the build directory."""
        logger.info("🧹 Cleaning build directory...")
        
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            logger.info(f"   Removed: {self.build_dir}")
        
        # Also clean API docs directory
        if self.api_dir.exists():
            shutil.rmtree(self.api_dir)
            logger.info(f"   Removed: {self.api_dir}")
    
    def generate_api_documentation(self) -> bool:
        """Generate API documentation using sphinx-apidoc."""
        logger.info("📚 Generating API documentation...")
        
        try:
            # Create API directory
            self.api_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate API docs for core modules
            api_modules = [
                ("jarvis.core", "Core Components"),
                ("jarvis.plugins", "Plugin System"),
                ("jarvis.tools", "Tools and Utilities"),
                ("jarvis.audio", "Audio Management"),
                ("jarvis.ui", "User Interface"),
                ("jarvis.utils", "Utilities")
            ]
            
            for module_path, title in api_modules:
                module_dir = self.source_dir / module_path.replace("jarvis.", "")
                if not module_dir.exists():
                    logger.warning(f"   Module directory not found: {module_dir}")
                    continue
                
                # Generate API docs for this module
                output_file = self.api_dir / f"{module_path.replace('.', '_')}.rst"
                
                cmd = [
                    sys.executable, "-m", "sphinx.ext.apidoc",
                    "-f",  # Force overwrite
                    "-e",  # Put each module on separate page
                    "-T",  # Don't create table of contents
                    "-M",  # Put module documentation before submodule
                    "-o", str(self.api_dir),
                    str(module_dir),
                    "--separate"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"   Failed to generate API docs for {module_path}: {result.stderr}")
                    continue
                
                logger.info(f"   Generated API docs for {module_path}")
            
            # Create main API index
            self._create_api_index()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate API documentation: {e}")
            return False
    
    def _create_api_index(self) -> None:
        """Create the main API index file."""
        api_index_content = """API Reference
=============

This section provides detailed API documentation for all enhanced Jarvis components.

Core Components
---------------

.. toctree::
   :maxdepth: 2

   jarvis_core

Plugin System
-------------

.. toctree::
   :maxdepth: 2

   jarvis_plugins

Tools and Utilities
-------------------

.. toctree::
   :maxdepth: 2

   jarvis_tools

Audio Management
----------------

.. toctree::
   :maxdepth: 2

   jarvis_audio

User Interface
--------------

.. toctree::
   :maxdepth: 2

   jarvis_ui

Utilities
---------

.. toctree::
   :maxdepth: 2

   jarvis_utils

Enhanced Features API
---------------------

Enhanced Plugin Registry
~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: jarvis.plugins.registry.unified_registry
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: jarvis.plugins.registry.relationship_mapper
   :members:
   :undoc-members:
   :show-inheritance:

Context Management
~~~~~~~~~~~~~~~~~~

.. automodule:: jarvis.core.context.context_manager
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: jarvis.core.context.conversation_state
   :members:
   :undoc-members:
   :show-inheritance:

Smart Orchestration
~~~~~~~~~~~~~~~~~~~

.. automodule:: jarvis.core.orchestration.orchestrator
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: jarvis.core.orchestration.tool_chain_detector
   :members:
   :undoc-members:
   :show-inheritance:

Code Consciousness
~~~~~~~~~~~~~~~~~~

.. automodule:: jarvis.core.consciousness.codebase_rag
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: jarvis.core.consciousness.semantic_index
   :members:
   :undoc-members:
   :show-inheritance:

Monitoring System
~~~~~~~~~~~~~~~~~

.. automodule:: scripts.monitoring.enhanced_monitoring
   :members:
   :undoc-members:
   :show-inheritance:
"""
        
        api_index_file = self.api_dir / "index.rst"
        api_index_file.write_text(api_index_content)
        logger.info("   Created API index file")
    
    def create_feature_documentation(self) -> None:
        """Create documentation for enhanced features."""
        logger.info("📝 Creating feature documentation...")
        
        features_dir = self.docs_dir / "features"
        features_dir.mkdir(parents=True, exist_ok=True)
        
        # Create feature documentation files
        features = [
            ("plugin_registry", "Enhanced Plugin Registry", """
Enhanced Plugin Registry
========================

The Enhanced Plugin Registry provides intelligent metadata and relationship tracking
for all tools and plugins in the Jarvis system.

.. enhanced-feature:: Plugin Registry
   :status: In Development
   :version: 2.0.0
   :complexity: High

Key Features
-----------

- **Automatic Capability Detection**: Analyzes plugins to determine their capabilities
- **Relationship Mapping**: Tracks which tools work well together
- **Usage Analytics**: Monitors plugin performance and usage patterns
- **Intelligent Recommendations**: Suggests optimal tool combinations

Architecture
-----------

The plugin registry consists of several key components:

.. code-block:: python

   from jarvis.plugins.registry import UnifiedPluginRegistry
   
   registry = UnifiedPluginRegistry()
   
   # Register a plugin with enhanced metadata
   registry.register_plugin("my_plugin", enhanced_metadata)
   
   # Find plugins by capability
   file_plugins = registry.find_plugins_by_capability("file_operations")
   
   # Get related plugins
   related = registry.get_related_plugins("my_plugin")

Usage Examples
-------------

Basic Plugin Registration
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from jarvis.plugins.registry import UnifiedPluginRegistry, EnhancedPluginMetadata
   
   registry = UnifiedPluginRegistry()
   
   metadata = EnhancedPluginMetadata(
       name="file_manager",
       capabilities={"file_operations", "data_processing"},
       performance_profile=PerformanceProfile(
           avg_execution_time=0.5,
           memory_usage_mb=10.0,
           success_rate=0.95
       )
   )
   
   registry.register_plugin("file_manager", metadata)

Capability-Based Search
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Find all plugins that can handle file operations
   file_plugins = registry.find_plugins_by_capability("file_operations")
   
   # Find plugins for web operations
   web_plugins = registry.find_plugins_by_capability("web_operations")

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Update usage statistics
   registry.update_usage_statistics("file_manager", 0.3, True)
   
   # Get performance summary
   stats = registry.get_usage_statistics("file_manager")
   print(f"Success rate: {stats.success_rate:.1%}")
   print(f"Average time: {stats.avg_execution_time:.2f}s")

API Reference
------------

See :doc:`../api/jarvis_plugins` for detailed API documentation.
"""),
            
            ("context_management", "Context Management System", """
Context Management System
========================

The Context Management System provides shared context and conversation state
management across all interactions with Jarvis.

.. enhanced-feature:: Context Management
   :status: Planned
   :version: 2.0.0
   :complexity: Medium

Overview
-------

The context management system maintains conversation state, user preferences,
and tool execution context across sessions, enabling more intelligent and
personalized interactions.

Key Components
-------------

- **ContextManager**: Central coordination of all context data
- **ConversationState**: Tracks conversation flow and topics
- **ToolStateTracker**: Monitors active tools and their states
- **UserPreferenceEngine**: Learns and adapts to user behavior
- **SessionMemory**: Manages session-specific data storage

Usage Examples
-------------

Basic Context Management
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from jarvis.core.context import ContextManager
   
   context_manager = ContextManager()
   
   # Get current context
   context = context_manager.get_current_context()
   
   # Update context with new information
   context_manager.update_context({
       'current_topic': 'file_management',
       'user_intent': 'organize_files'
   })

Session Management
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Create a new session
   session_id = "user_session_123"
   context_manager.create_session(session_id)
   
   # Store session-specific data
   context_manager.store_session_data(session_id, 'preferences', {
       'response_style': 'detailed',
       'preferred_tools': ['file_manager', 'text_editor']
   })
   
   # Retrieve session data
   preferences = context_manager.retrieve_session_data(session_id, 'preferences')

User Preference Learning
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from jarvis.core.context import UserPreferenceEngine
   
   preference_engine = UserPreferenceEngine()
   
   # Learn user preferences
   preference_engine.learn_preference(
       user_id="user123",
       preference_type="response_style", 
       value="concise",
       confidence=0.8
   )
   
   # Get learned preferences
   preferences = preference_engine.get_user_preferences("user123")

API Reference
------------

See :doc:`../api/jarvis_core` for detailed API documentation.
"""),
            
            ("tool_orchestration", "Smart Tool Orchestration", """
Smart Tool Orchestration
========================

The Smart Tool Orchestration system provides intelligent tool chaining and
coordination for complex multi-step tasks.

.. enhanced-feature:: Tool Orchestration
   :status: Planned
   :version: 2.0.0
   :complexity: High

Overview
-------

The orchestration system automatically detects optimal tool chains, resolves
conflicts, and coordinates tool execution for complex user requests.

Key Features
-----------

- **Automatic Chain Detection**: Identifies optimal tool sequences
- **Context-Aware Selection**: Chooses tools based on conversation context
- **Conflict Resolution**: Handles tool dependencies and conflicts
- **Learning Engine**: Improves tool selection over time
- **Performance Optimization**: Caches and optimizes common patterns

Architecture
-----------

.. code-block:: python

   from jarvis.core.orchestration import SystemOrchestrator
   
   orchestrator = SystemOrchestrator()
   
   # Create orchestration plan
   plan = orchestrator.orchestrate_request("analyze my files and create summary")
   
   # Execute the plan
   result = orchestrator.execute_plan(plan)

Usage Examples
-------------

Basic Orchestration
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from jarvis.core.orchestration import SystemOrchestrator
   from jarvis.core.context import ContextManager
   
   orchestrator = SystemOrchestrator()
   context_manager = ContextManager()
   
   # Get current context
   context = context_manager.get_current_context()
   
   # Create orchestration plan
   plan = orchestrator.orchestrate_request(
       "find all Python files and check for security issues",
       context
   )
   
   # Execute plan with monitoring
   result = orchestrator.execute_plan(plan)
   print(f"Execution completed in {result.execution_time:.2f}s")

Tool Chain Suggestions
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get tool chain suggestions
   suggestions = orchestrator.suggest_tool_chain(
       intent="file_analysis",
       context=context
   )
   
   for suggestion in suggestions:
       print(f"Chain: {' -> '.join(suggestion.tool_names)}")
       print(f"Confidence: {suggestion.confidence:.1%}")

Performance Monitoring
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Monitor orchestration performance
   with orchestrator.monitor_performance() as monitor:
       result = orchestrator.execute_plan(plan)
       
   print(f"Orchestration took {monitor.duration_ms:.1f}ms")
   print(f"Tools used: {len(monitor.tools_executed)}")

API Reference
------------

See :doc:`../api/jarvis_core` for detailed API documentation.
"""),
            
            ("code_consciousness", "Source Code Consciousness", """
Source Code Consciousness
========================

The Source Code Consciousness system enables deep understanding of the Jarvis
codebase through semantic indexing and natural language queries.

.. enhanced-feature:: Code Consciousness
   :status: Planned
   :version: 2.0.0
   :complexity: Very High

Overview
-------

This system provides Jarvis with the ability to understand its own implementation,
navigate code semantically, and suggest safe modifications.

Key Capabilities
---------------

- **Semantic Code Indexing**: Understands code structure and relationships
- **Natural Language Queries**: Search code using plain English
- **Dependency Analysis**: Maps code dependencies and relationships
- **Safe Modification**: Suggests and validates code changes
- **Architectural Understanding**: Maintains knowledge of system patterns

Architecture
-----------

.. code-block:: python

   from jarvis.core.consciousness import CodeConsciousnessSystem
   
   consciousness = CodeConsciousnessSystem()
   
   # Index the codebase
   consciousness.index_codebase("./jarvis")
   
   # Query code semantically
   results = consciousness.query_code("find functions that handle user input")

Usage Examples
-------------

Code Indexing
~~~~~~~~~~~~

.. code-block:: python

   from jarvis.core.consciousness import CodeConsciousnessSystem
   
   consciousness = CodeConsciousnessSystem()
   
   # Index the entire codebase
   consciousness.index_codebase("./jarvis")
   
   # Index specific modules
   consciousness.index_module("jarvis/core/agent.py")

Semantic Code Search
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Search for specific functionality
   results = consciousness.query_code("plugin loading mechanism")
   
   for result in results:
       print(f"File: {result.file_path}")
       print(f"Function: {result.function_name}")
       print(f"Relevance: {result.relevance_score:.2f}")
       print(f"Code: {result.code_snippet}")

Dependency Analysis
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get dependency graph for a function
   deps = consciousness.get_code_dependencies("JarvisAgent.process_input")
   
   print(f"Direct dependencies: {len(deps.direct_dependencies)}")
   print(f"Transitive dependencies: {len(deps.transitive_dependencies)}")

Code Modification Suggestions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get improvement suggestions
   suggestions = consciousness.suggest_improvements("jarvis/core/agent.py")
   
   for suggestion in suggestions:
       print(f"Type: {suggestion.modification_type}")
       print(f"Description: {suggestion.description}")
       print(f"Risk Level: {suggestion.risk_level}")

API Reference
------------

See :doc:`../api/jarvis_core` for detailed API documentation.
""")
        ]
        
        for filename, title, content in features:
            feature_file = features_dir / f"{filename}.rst"
            feature_file.write_text(content.strip())
            logger.info(f"   Created: {filename}.rst")
    
    def build_documentation(self, output_format: str = "html") -> bool:
        """Build the documentation using Sphinx."""
        logger.info(f"🔨 Building documentation ({output_format})...")
        
        try:
            # Prepare build command
            cmd = [
                sys.executable, "-m", "sphinx.cmd.build"
            ] + self.sphinx_opts + [
                "-b", output_format,
                str(self.docs_dir),
                str(self.build_dir / output_format)
            ]
            
            # Run Sphinx build
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Documentation built successfully!")
                logger.info(f"   Output: {self.build_dir / output_format}")
                return True
            else:
                logger.error(f"❌ Documentation build failed:")
                logger.error(result.stderr)
                return False
                
        except Exception as e:
            logger.error(f"Failed to build documentation: {e}")
            return False
    
    def serve_documentation(self, port: int = 8000) -> None:
        """Serve the built documentation locally."""
        html_dir = self.build_dir / "html"
        
        if not html_dir.exists():
            logger.error("HTML documentation not found. Build it first with --build")
            return
        
        logger.info(f"🌐 Serving documentation at http://localhost:{port}")
        logger.info("   Press Ctrl+C to stop the server")
        
        try:
            import http.server
            import socketserver
            import os
            
            os.chdir(html_dir)
            
            with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
                httpd.serve_forever()
                
        except KeyboardInterrupt:
            logger.info("📴 Documentation server stopped")
        except Exception as e:
            logger.error(f"Failed to serve documentation: {e}")
    
    def check_documentation_health(self) -> bool:
        """Check documentation health and completeness."""
        logger.info("🔍 Checking documentation health...")
        
        issues = []
        
        # Check if key files exist
        key_files = [
            self.docs_dir / "index.rst",
            self.docs_dir / "conf.py",
            self.api_dir / "index.rst"
        ]
        
        for file_path in key_files:
            if not file_path.exists():
                issues.append(f"Missing file: {file_path}")
        
        # Check if build directory exists and has content
        html_dir = self.build_dir / "html"
        if html_dir.exists():
            html_files = list(html_dir.glob("*.html"))
            if len(html_files) < 5:  # Should have at least index + a few pages
                issues.append(f"Too few HTML files generated: {len(html_files)}")
        else:
            issues.append("HTML build directory not found")
        
        # Report results
        if issues:
            logger.warning("⚠️  Documentation health issues found:")
            for issue in issues:
                logger.warning(f"   - {issue}")
            return False
        else:
            logger.info("✅ Documentation health check passed")
            return True

def main():
    """Main entry point for the documentation builder."""
    parser = argparse.ArgumentParser(description="Build Jarvis Enhanced Documentation")
    parser.add_argument("--clean", action="store_true", help="Clean build directory first")
    parser.add_argument("--api", action="store_true", help="Generate API documentation")
    parser.add_argument("--build", action="store_true", help="Build documentation")
    parser.add_argument("--serve", action="store_true", help="Serve documentation locally")
    parser.add_argument("--check", action="store_true", help="Check documentation health")
    parser.add_argument("--all", action="store_true", help="Run all steps (clean, api, build)")
    parser.add_argument("--port", type=int, default=8000, help="Port for serving docs")
    parser.add_argument("--format", default="html", help="Output format (html, pdf, epub)")
    
    args = parser.parse_args()
    
    # If no specific action, default to --all
    if not any([args.clean, args.api, args.build, args.serve, args.check, args.all]):
        args.all = True
    
    builder = DocumentationBuilder()
    success = True
    
    try:
        if args.all or args.clean:
            builder.clean_build_directory()
        
        if args.all or args.api:
            builder.create_feature_documentation()
            if not builder.generate_api_documentation():
                success = False
        
        if args.all or args.build:
            if not builder.build_documentation(args.format):
                success = False
        
        if args.check:
            if not builder.check_documentation_health():
                success = False
        
        if args.serve:
            builder.serve_documentation(args.port)
        
        if success:
            logger.info("🎉 Documentation build completed successfully!")
        else:
            logger.error("❌ Documentation build completed with errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("📴 Documentation build interrupted")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
