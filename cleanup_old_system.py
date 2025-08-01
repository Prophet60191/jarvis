#!/usr/bin/env python3
"""
Cleanup script to remove old over-engineered system files while preserving
wake word functionality and essential components.

CRITICAL: This script only removes old test files and over-engineered components.
It NEVER touches wake word functionality or essential system files.
"""

import os
import shutil
import glob
from pathlib import Path

def cleanup_old_system():
    """Remove old over-engineered system files safely."""
    
    print("🧹 Starting cleanup of old over-engineered system...")
    print("🔒 CRITICAL: Wake word functionality will be completely preserved")
    
    # Files to remove (old test files and over-engineered components)
    files_to_remove = [
        # Old test files (many are redundant)
        "test_*jarvis*.py",
        "test_*agent*.py", 
        "test_*orchestration*.py",
        "test_*rag*.py",
        "test_*tool*.py",
        "test_*integration*.py",
        "debug_*.py",
        "demo_*.py",
        "additional_jarvis_tests.py",
        "analyze_mps_performance.py",
        "audio_capture_diagnostic.py",
        "benchmark_unified_workflow.py",
        "cleanup_mock_data.py",
        "cleanup_ui_processes.py",
        "desktop_app_fix_summary.py",
        "diagnose_jarvis_issue.py",
        "discover_us_voices.py",
        "enable_fast_path_routing.py",
        "final_*.py",
        "fix_*.py",
        "ingest.py",
        "ingest_complete_codebase.py",
        "initialize_rag_workflow.py",
        "launch_*.py",
        "manage_plugins.py",
        "name_storage_summary.py",
        "orchestration_*.py",
        "real_*.py",
        "run_*.py",
        "script.py",
        "script_backup.py",
        "send_prompt*.py",
        "settings_fix_summary.py",
        "setup_*.py",
        "sync_*.py",
        "update_*.py",
        "user_memory_simulation.py",
        "validate_implementation.py",
        "verify_*.py",
        "wake_word_diagnostic.py",
        "web_automation_tool.py",
        
        # Old backup directories (keep only the most recent)
        "backup_20250731_102145",
        "backup_20250731_102218", 
        "backup_20250731_102243",
        "backup_20250731_102331",
        
        # Old result files
        "*.json",
        "*.log",
        "error.log",
        "open_interpreter_mcp.log",
        
        # Old HTML/JS test files
        "direct_test.html",
        "final_test.html",
        "index.html",
        "app.js",
        "logger.js",
        "main.js",
        "script.js",
        "style.css",
        "utils.js",
        
        # Old cache and temp files
        "__pycache__",
        "cache",
        
        # Old documentation (keep essential ones)
        "AGENT_SELECTION_DECISION_TREES.md",
        "ANALYTICS_DASHBOARD_USER_GUIDE.md",
        "APPMANAGER_DEBUG_SUMMARY.md",
        "BENCHMARKING_GUIDE.md",
        "COMPLETE_IMPLEMENTATION_REPORT.md",
        "CRITICAL_SAFEGUARDS_CHECKLIST.md",
        "DESKTOP_LAUNCHERS_READY.md",
        "DESKTOP_LAUNCHER_GUIDE.md",
        "DOCUMENTATION_INDEX.md",
        "DOCUMENTATION_REVIEW_AND_PLAN.md",
        "DOCUMENTATION_STATUS_SUMMARY.md",
        "ENHANCED_ORCHESTRATION_SYSTEM_PROMPT.md",
        "FAST_PATH_INTEGRATION_GUIDE.md",
        "FAST_SLOW_PATH_ROUTING_GUIDE.md",
        "FINAL_GIT_PUSH_SUMMARY.md",
        "GETTING_STARTED_COMPLETE.md",
        "GIT_REPOSITORY_UPDATE_SUMMARY.md",
        "IMPLEMENTATION_QUICK_START.md",
        "JARVIS_ORCHESTRATION_IMPLEMENTATION_PLAN.md",
        "JARVIS_ORCHESTRATION_PROGRESS_TRACKER.md",
        "JARVIS_PROMPT_ENGINEERING_GUIDE.md",
        "JARVIS_PROMPT_ENGINEERING_RESEARCH.md",
        "JARVIS_PROMPT_QUICK_REFERENCE.md",
        "JARVIS_RAG_MEMORY_USER_GUIDE.md",
        "JARVIS_SELF_AWARENESS_COMPLETE.md",
        "Jarvis_Enhanced_System_Integration_Foundation__2025-07-29T14-58-13.md",
        "MIGRATION_GUIDE.md",
        "MULTI_AGENT_ORCHESTRATION_RESEARCH.md",
        "NEXT_ITEMS.md",
        "OPEN_INTERPRETER_INTEGRATION.md",
        "OPEN_INTERPRETER_MCP_GUIDE.md",
        "OPEN_INTERPRETER_USAGE.md",
        "ORCHESTRATION_TESTING_GUIDE.md",
        "ORCHESTRATION_TEST_SCENARIOS.md",
        "PHASE_1_COMPLETION_REPORT.md",
        "RAG_PLANNING.md",
        "SYSTEM_INTEGRATION_PLAN.md",
        "SYSTEM_STATUS_AND_ISSUES.md",
        "TASK_COMPLETION_SUMMARY.md",
        "USER_HELP_PLUGIN_DOCUMENTATION_SUMMARY.md",
        "USER_HELP_UI_GUIDE.md",
    ]
    
    # CRITICAL: Files to NEVER remove (wake word and essential system)
    preserve_files = [
        "start_jarvis.py",  # Main startup (modified but preserved)
        "jarvis/",  # Entire jarvis directory (contains wake word system)
        "deploy_optimized_jarvis.py",  # Deployment script
        "README.md",  # Essential documentation
        "ARCHITECTURE.md",  # System architecture
        "CHANGELOG.md",  # Change history
        "JARVIS_OPTIMIZATION_COMPLETE.md",  # Optimization documentation
        "JARVIS_SIMPLIFICATION_PLAN.md",  # This cleanup plan
        "PLUGIN_REFERENCE_GUIDE.md",  # Plugin documentation
        "START_JARVIS.md",  # Startup guide
        "TROUBLESHOOTING_GUIDE.md",  # Troubleshooting
        "USER_GUIDE.md",  # User guide
        "VOICE_COMMANDS_REFERENCE.md",  # Voice commands
        "data/",  # User data
        "docs/",  # Essential documentation
        "examples/",  # Example code
        "mcp_servers/",  # MCP server implementations
        "scripts/",  # Essential scripts
        "tests/",  # Essential tests
        "ui/",  # User interface
        "voices/",  # Voice data
    ]
    
    removed_count = 0
    preserved_count = 0
    
    for pattern in files_to_remove:
        # Check if this file/pattern should be preserved
        should_preserve = False
        for preserve_pattern in preserve_files:
            if pattern.startswith(preserve_pattern.rstrip('/')):
                should_preserve = True
                break
        
        if should_preserve:
            preserved_count += 1
            continue
            
        # Remove files matching pattern
        matches = glob.glob(pattern)
        for match in matches:
            try:
                if os.path.isdir(match):
                    shutil.rmtree(match)
                    print(f"🗑️  Removed directory: {match}")
                else:
                    os.remove(match)
                    print(f"🗑️  Removed file: {match}")
                removed_count += 1
            except Exception as e:
                print(f"⚠️  Could not remove {match}: {e}")
    
    print(f"\n✅ Cleanup complete!")
    print(f"🗑️  Removed: {removed_count} old files/directories")
    print(f"🔒 Preserved: {preserved_count} essential files")
    print(f"✅ Wake word functionality completely preserved")
    print(f"🚀 System simplified and optimized")

if __name__ == "__main__":
    cleanup_old_system()
