#!/usr/bin/env python3
"""
Implementation Validation Script

This script validates that all the enhanced Jarvis components can be imported
and instantiated correctly, providing a quick smoke test of the implementation.
"""

import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

class ImplementationValidator:
    """Validates the enhanced Jarvis implementation."""
    
    def __init__(self):
        self.results = {}
        self.total_checks = 0
        self.passed_checks = 0
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks."""
        print("🔍 Validating Enhanced Jarvis Implementation")
        print("=" * 50)
        
        validation_checks = [
            ("Plugin Registry Components", self.validate_plugin_registry),
            ("Context Management Components", self.validate_context_management),
            ("Orchestration Components", self.validate_orchestration),
            ("Code Consciousness Components", self.validate_code_consciousness),
            ("Integration Points", self.validate_integration),
            ("Test Framework", self.validate_test_framework)
        ]
        
        for check_name, check_func in validation_checks:
            print(f"\n📋 Checking {check_name}...")
            try:
                result = check_func()
                self.results[check_name] = result
                
                if result["success"]:
                    print(f"✅ {check_name}: PASSED ({result['components_checked']} components)")
                else:
                    print(f"❌ {check_name}: FAILED")
                    for error in result["errors"][:3]:
                        print(f"   Error: {error}")
                        
            except Exception as e:
                print(f"💥 {check_name}: CRASHED - {e}")
                self.results[check_name] = {
                    "success": False,
                    "components_checked": 0,
                    "errors": [str(e)]
                }
        
        # Generate summary
        summary = self.generate_summary()
        self.print_summary(summary)
        
        return {
            "results": self.results,
            "summary": summary
        }
    
    def validate_plugin_registry(self) -> Dict[str, Any]:
        """Validate plugin registry components."""
        components = [
            ("UnifiedPluginRegistry", "jarvis.jarvis.plugins.registry.unified_registry", "UnifiedPluginRegistry"),
            ("RelationshipMapper", "jarvis.jarvis.plugins.registry.relationship_mapper", "RelationshipMapper"),
            ("CapabilityAnalyzer", "jarvis.jarvis.plugins.registry.capability_analyzer", "CapabilityAnalyzer"),
            ("UsageAnalytics", "jarvis.jarvis.plugins.registry.usage_analytics", "UsageAnalytics"),
            ("EnhancedPluginManager", "jarvis.jarvis.plugins.enhanced_manager", "EnhancedPluginManager")
        ]
        
        return self._validate_components(components)
    
    def validate_context_management(self) -> Dict[str, Any]:
        """Validate context management components."""
        components = [
            ("ContextManager", "jarvis.jarvis.core.context.context_manager", "ContextManager"),
            ("ConversationState", "jarvis.jarvis.core.context.conversation_state", "ConversationState"),
            ("ToolStateTracker", "jarvis.jarvis.core.context.tool_state_tracker", "ToolStateTracker"),
            ("UserPreferenceEngine", "jarvis.jarvis.core.context.user_preference_engine", "UserPreferenceEngine"),
            ("SessionMemory", "jarvis.jarvis.core.context.session_memory", "SessionMemory"),
            ("ContextAPI", "jarvis.jarvis.core.context.context_api", "ContextAPI"),
            ("RAGMemoryIntegration", "jarvis.jarvis.core.context.rag_integration", "RAGMemoryIntegration")
        ]
        
        return self._validate_components(components)
    
    def validate_orchestration(self) -> Dict[str, Any]:
        """Validate orchestration components."""
        components = [
            ("SystemOrchestrator", "jarvis.jarvis.core.orchestration.orchestrator", "SystemOrchestrator"),
            ("ToolChainDetector", "jarvis.jarvis.core.orchestration.tool_chain_detector", "ToolChainDetector"),
            ("ContextAwareSelector", "jarvis.jarvis.core.orchestration.context_aware_selector", "ContextAwareSelector")
        ]
        
        return self._validate_components(components)
    
    def validate_code_consciousness(self) -> Dict[str, Any]:
        """Validate code consciousness components."""
        components = [
            ("CodeConsciousnessSystem", "jarvis.jarvis.core.consciousness.consciousness_system", "CodeConsciousnessSystem"),
            ("CodebaseRAG", "jarvis.jarvis.core.consciousness.codebase_rag", "CodebaseRAG")
        ]
        
        return self._validate_components(components)
    
    def validate_integration(self) -> Dict[str, Any]:
        """Validate integration points."""
        integration_checks = []
        errors = []
        
        try:
            # Check if we can import the main agent
            from jarvis.jarvis.core.agent import JarvisAgent
            integration_checks.append("JarvisAgent import")
        except ImportError as e:
            errors.append(f"Cannot import JarvisAgent: {e}")
        
        try:
            # Check plugin manager integration
            from jarvis.jarvis.plugins.manager import PluginManager
            integration_checks.append("PluginManager import")
        except ImportError as e:
            errors.append(f"Cannot import PluginManager: {e}")
        
        try:
            # Check if enhanced components can work together
            from jarvis.jarvis.plugins.registry.unified_registry import UnifiedPluginRegistry
            from jarvis.jarvis.core.context.context_manager import ContextManager
            
            # Try to create instances
            registry = UnifiedPluginRegistry()
            context_manager = ContextManager()
            integration_checks.append("Component instantiation")
            
        except Exception as e:
            errors.append(f"Component integration failed: {e}")
        
        return {
            "success": len(errors) == 0,
            "components_checked": len(integration_checks),
            "errors": errors,
            "checks_passed": integration_checks
        }
    
    def validate_test_framework(self) -> Dict[str, Any]:
        """Validate test framework components."""
        test_files = [
            "tests/enhanced/__init__.py",
            "tests/enhanced/test_plugin_registry.py",
            "tests/enhanced/test_context_management.py",
            "tests/enhanced/test_enhanced_integration.py",
            "tests/enhanced/test_registry_integration.py",
            "tests/enhanced/test_registry_performance.py"
        ]

        errors = []
        found_files = []

        for test_file in test_files:
            test_path = project_root / test_file
            if test_path.exists():
                found_files.append(test_file)

                # Just check if file exists and is readable, don't try to import
                try:
                    with open(test_path, 'r') as f:
                        content = f.read()
                    if len(content) > 0:
                        # File exists and has content
                        pass
                    else:
                        errors.append(f"Test file {test_file} is empty")
                except Exception as e:
                    errors.append(f"Cannot read {test_file}: {e}")
            else:
                errors.append(f"Test file not found: {test_file}")

        # Check if we have the test runner scripts
        test_runners = ["run_tests.py", "validate_implementation.py"]
        for runner in test_runners:
            runner_path = project_root / runner
            if runner_path.exists():
                found_files.append(runner)
            else:
                errors.append(f"Test runner not found: {runner}")

        return {
            "success": len(errors) == 0,
            "components_checked": len(found_files),
            "errors": errors,
            "files_found": found_files
        }
    
    def _validate_components(self, components: List[Tuple[str, str, str]]) -> Dict[str, Any]:
        """Validate a list of components."""
        errors = []
        successful_imports = []
        
        for component_name, module_path, class_name in components:
            try:
                # Try to import the module
                module = __import__(module_path, fromlist=[class_name])
                
                # Try to get the class
                component_class = getattr(module, class_name)
                
                # Try to instantiate (with minimal args)
                if component_name == "ContextAPI":
                    # ContextAPI needs a context manager
                    from jarvis.jarvis.core.context.context_manager import ContextManager
                    context_manager = ContextManager()
                    instance = component_class(context_manager)
                elif component_name == "RAGMemoryIntegration":
                    # RAGMemoryIntegration needs a context manager
                    from jarvis.jarvis.core.context.context_manager import ContextManager
                    context_manager = ContextManager()
                    instance = component_class(context_manager)
                elif component_name == "CodebaseRAG":
                    # CodebaseRAG needs a path
                    instance = component_class(Path("/tmp"))
                elif component_name == "SystemOrchestrator":
                    # SystemOrchestrator needs a context manager
                    from jarvis.jarvis.core.context.context_manager import ContextManager
                    context_manager = ContextManager()
                    instance = component_class(context_manager)
                elif component_name == "CodeConsciousnessSystem":
                    # CodeConsciousnessSystem needs a codebase path
                    import tempfile
                    temp_dir = Path(tempfile.mkdtemp())
                    instance = component_class(temp_dir, enable_safe_modifications=False)
                else:
                    # Most components can be instantiated without args
                    instance = component_class()
                
                successful_imports.append(component_name)
                
            except ImportError as e:
                errors.append(f"Cannot import {component_name} from {module_path}: {e}")
            except AttributeError as e:
                errors.append(f"Cannot find class {class_name} in {module_path}: {e}")
            except Exception as e:
                errors.append(f"Cannot instantiate {component_name}: {e}")
        
        return {
            "success": len(errors) == 0,
            "components_checked": len(successful_imports),
            "errors": errors,
            "successful_imports": successful_imports
        }
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary."""
        total_components = sum(result.get("components_checked", 0) for result in self.results.values())
        successful_validations = sum(1 for result in self.results.values() if result.get("success", False))
        total_validations = len(self.results)
        total_errors = sum(len(result.get("errors", [])) for result in self.results.values())
        
        return {
            "total_validations": total_validations,
            "successful_validations": successful_validations,
            "failed_validations": total_validations - successful_validations,
            "total_components": total_components,
            "total_errors": total_errors,
            "success_rate": (successful_validations / max(total_validations, 1)) * 100
        }
    
    def print_summary(self, summary: Dict[str, Any]) -> None:
        """Print validation summary."""
        print("\n" + "=" * 50)
        print("📊 VALIDATION SUMMARY")
        print("=" * 50)
        
        print(f"🔍 Validation Categories: {summary['successful_validations']}/{summary['total_validations']} passed")
        print(f"🧩 Components Checked: {summary['total_components']}")
        print(f"❌ Total Errors: {summary['total_errors']}")
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['success_rate'] == 100:
            print("\n🎉 ALL VALIDATIONS PASSED! 🎉")
            print("✅ Implementation is ready for testing!")
        elif summary['success_rate'] >= 80:
            print("\n✅ Most validations passed!")
            print("⚠️  Some minor issues found - check details above")
        else:
            print("\n⚠️  Multiple validation failures!")
            print("❌ Implementation needs attention before testing")

def main():
    """Main entry point."""
    try:
        validator = ImplementationValidator()
        results = validator.validate_all()
        
        # Exit with appropriate code
        success_rate = results["summary"]["success_rate"]
        if success_rate == 100:
            print("\n🚀 Ready to run comprehensive tests with: python run_tests.py")
            sys.exit(0)
        else:
            print("\n⚠️  Fix validation issues before running full tests")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Validation crashed: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
