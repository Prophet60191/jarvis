#!/usr/bin/env python3
"""
Jarvis Performance Benchmarking System

Comprehensive benchmarking suite for testing tool calls, prompts, and system performance.
Enables systematic optimization through iterative testing and measurement.
"""

import asyncio
import time
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkTest:
    """Individual benchmark test definition."""
    name: str
    query: str
    expected_tool: Optional[str] = None
    expected_response_type: str = "text"
    timeout_seconds: float = 30.0
    category: str = "general"
    complexity: str = "simple"  # simple, moderate, complex

@dataclass
class BenchmarkResult:
    """Result of a single benchmark test."""
    test_name: str
    query: str
    success: bool
    response: str
    execution_time: float
    tool_used: Optional[str]
    error_message: Optional[str]
    timestamp: str
    metadata: Dict[str, Any]

@dataclass
class BenchmarkSuite:
    """Complete benchmark suite results."""
    suite_name: str
    timestamp: str
    total_tests: int
    successful_tests: int
    failed_tests: int
    avg_execution_time: float
    total_execution_time: float
    results: List[BenchmarkResult]
    system_info: Dict[str, Any]

class JarvisBenchmark:
    """
    Comprehensive benchmarking system for Jarvis performance testing.
    """
    
    def __init__(self, results_dir: str = "benchmark_results"):
        """Initialize the benchmark system."""
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        # Initialize Jarvis components (will be set when running)
        self.agent = None
        self.conversation_manager = None
        self.config = None
        
        # Define comprehensive test suite
        self.test_suites = {
            "quick": self._create_quick_test_suite(),
            "comprehensive": self._create_comprehensive_test_suite(),
            "tool_focused": self._create_tool_focused_test_suite(),
            "performance": self._create_performance_test_suite(),
            "rag_focused": self._create_rag_focused_test_suite(),
            "integration": self._create_integration_test_suite(),
            "stress": self._create_stress_test_suite(),
            "progressive": self._create_progressive_test_suite()
        }
        
        logger.info(f"Benchmark system initialized. Results will be saved to: {self.results_dir}")
    
    def _create_quick_test_suite(self) -> List[BenchmarkTest]:
        """Create a quick test suite for rapid iteration."""
        return [
            BenchmarkTest("time_query", "What time is it?", "get_current_time", "text", 5.0, "instant", "simple"),
            BenchmarkTest("greeting", "Hello", None, "text", 3.0, "instant", "simple"),
            BenchmarkTest("status", "How are you?", None, "text", 3.0, "instant", "simple"),
            BenchmarkTest("simple_question", "What is Python?", None, "text", 10.0, "adaptive", "moderate"),
            BenchmarkTest("complex_task", "Analyze my code files", None, "text", 30.0, "complex", "complex")
        ]
    
    def _create_comprehensive_test_suite(self) -> List[BenchmarkTest]:
        """Create comprehensive test suite covering ALL Jarvis functionality."""
        return [
            # === INSTANT RESPONSE TESTS (Simple queries) ===
            BenchmarkTest("time_query", "What time is it?", "get_current_time", "text", 5.0, "instant", "simple"),
            BenchmarkTest("time_query_alt", "Tell me the current time", "get_current_time", "text", 5.0, "instant", "simple"),
            BenchmarkTest("greeting_hello", "Hello", None, "text", 3.0, "instant", "simple"),
            BenchmarkTest("greeting_hi", "Hi there", None, "text", 3.0, "instant", "simple"),
            BenchmarkTest("status_check", "How are you?", None, "text", 3.0, "instant", "simple"),
            BenchmarkTest("status_working", "Are you working?", None, "text", 3.0, "instant", "simple"),

            # === USER PROFILE SYSTEM TESTS ===
            BenchmarkTest("profile_get_name", "What is my name?", "get_my_name", "text", 5.0, "user_profile", "simple"),
            BenchmarkTest("profile_set_name", "My name is TestUser", "set_my_name", "text", 5.0, "user_profile", "simple"),
            BenchmarkTest("profile_pronouns", "My pronouns are they/them", "set_my_pronouns", "text", 5.0, "user_profile", "simple"),
            BenchmarkTest("profile_show", "Show my profile", "show_my_profile", "text", 5.0, "user_profile", "simple"),
            BenchmarkTest("profile_enable_name", "Allow Jarvis to use my name", "enable_name_usage", "text", 5.0, "user_profile", "simple"),
            BenchmarkTest("profile_disable_name", "Don't use my name", "disable_name_usage", "text", 5.0, "user_profile", "simple"),
            BenchmarkTest("profile_clear", "Clear my profile", "clear_my_profile", "text", 5.0, "user_profile", "simple"),

            # === RAG & MEMORY SYSTEM TESTS ===
            BenchmarkTest("memory_remember", "Remember that I like coffee", "remember_fact", "text", 10.0, "rag_memory", "moderate"),
            BenchmarkTest("memory_search_conversations", "What did we talk about yesterday?", "search_conversations", "text", 10.0, "rag_memory", "moderate"),
            BenchmarkTest("memory_search_documents", "Search my documents for Python information", "search_documents", "text", 10.0, "rag_memory", "moderate"),
            BenchmarkTest("memory_search_all", "Search all my information about machine learning", "search_all_memory", "text", 15.0, "rag_memory", "moderate"),
            BenchmarkTest("memory_long_term", "What do you know about my preferences?", "search_long_term_memory", "text", 15.0, "rag_memory", "moderate"),
            BenchmarkTest("memory_intelligent", "Find information about my work projects", "search_long_term_memory_intelligent", "text", 15.0, "rag_memory", "moderate"),

            # === UI & SYSTEM CONTROL TESTS ===
            BenchmarkTest("ui_open_jarvis", "Open settings", "open_jarvis_ui", "text", 10.0, "ui_system", "moderate"),
            BenchmarkTest("ui_close_jarvis", "Close settings", "close_jarvis_ui", "text", 5.0, "ui_system", "simple"),
            BenchmarkTest("ui_jarvis_status", "Show system status", "show_jarvis_status", "text", 5.0, "ui_system", "simple"),
            BenchmarkTest("ui_open_rag", "Open vault", "open_rag_manager", "text", 10.0, "ui_system", "moderate"),
            BenchmarkTest("ui_close_rag", "Close vault", "close_rag_manager", "text", 5.0, "ui_system", "simple"),
            BenchmarkTest("ui_rag_status", "Show vault status", "show_rag_status", "text", 5.0, "ui_system", "simple"),
            BenchmarkTest("logs_open", "Open logs", "open_logs_terminal", "text", 10.0, "ui_system", "moderate"),
            BenchmarkTest("logs_close", "Close logs", "close_logs_terminal", "text", 5.0, "ui_system", "simple"),
            BenchmarkTest("logs_status", "Show logs status", "show_logs_status", "text", 5.0, "ui_system", "simple"),

            # === DEVELOPMENT TOOLS TESTS ===
            BenchmarkTest("dev_aider_status", "Is Aider working?", "check_aider_status", "text", 10.0, "development", "moderate"),
            BenchmarkTest("dev_aider_edit", "Use Aider to fix this code", "aider_code_edit", "text", 30.0, "development", "complex"),
            BenchmarkTest("dev_aider_refactor", "Refactor my project with Aider", "aider_project_refactor", "text", 45.0, "development", "complex"),

            # === WEB AUTOMATION TESTS ===
            BenchmarkTest("web_lavague_status", "Is web automation working?", "check_lavague_status", "text", 10.0, "web_automation", "moderate"),
            BenchmarkTest("web_automation", "Automate clicking the login button", "web_automation_task", "text", 30.0, "web_automation", "complex"),
            BenchmarkTest("web_scraping", "Get the title from google.com", "web_scraping_task", "text", 25.0, "web_automation", "complex"),
            BenchmarkTest("web_form_fill", "Fill out the contact form", "web_form_filling", "text", 35.0, "web_automation", "complex"),

            # === TESTING FRAMEWORK TESTS ===
            BenchmarkTest("test_validate_system", "Is the test system ready?", "validate_test_system", "text", 10.0, "testing", "moderate"),
            BenchmarkTest("test_list_available", "What tests are available?", "list_available_tests", "text", 10.0, "testing", "moderate"),
            BenchmarkTest("test_run_robot", "Run the basic tests", "run_robot_tests", "text", 60.0, "testing", "complex"),
            BenchmarkTest("test_check_results", "Check test results", "check_test_results", "text", 10.0, "testing", "moderate"),

            # === ADAPTIVE COMPLEXITY TESTS ===
            BenchmarkTest("adaptive_simple_question", "What is artificial intelligence?", None, "text", 15.0, "adaptive", "moderate"),
            BenchmarkTest("adaptive_explanation", "Explain how computers work", None, "text", 15.0, "adaptive", "moderate"),
            BenchmarkTest("adaptive_comparison", "Compare Python and JavaScript", None, "text", 20.0, "adaptive", "moderate"),
            BenchmarkTest("adaptive_analysis", "Analyze the pros and cons of remote work", None, "text", 25.0, "adaptive", "moderate"),

            # === COMPLEX INTEGRATION TESTS ===
            BenchmarkTest("complex_multi_tool", "Remember my name is John, then search for information about my preferences", None, "text", 30.0, "complex", "complex"),
            BenchmarkTest("complex_workflow", "Open the vault, search my documents, and remember what you find", None, "text", 45.0, "complex", "complex"),
            BenchmarkTest("complex_development", "Check if Aider is working, then help me refactor some code", None, "text", 60.0, "complex", "complex"),
            BenchmarkTest("complex_full_system", "Show my profile, search my memory for work projects, open logs, and give me a summary", None, "text", 60.0, "complex", "complex"),
        ]
    
    def _create_tool_focused_test_suite(self) -> List[BenchmarkTest]:
        """Create test suite focused on tool selection and execution across all categories."""
        return [
            # Core system tools
            BenchmarkTest("tool_time", "What time is it?", "get_current_time", "text", 5.0, "tools", "simple"),
            BenchmarkTest("tool_system_status", "Show system status", "show_jarvis_status", "text", 5.0, "tools", "simple"),

            # User profile tools
            BenchmarkTest("tool_profile_name", "What is my name?", "get_my_name", "text", 5.0, "tools", "simple"),
            BenchmarkTest("tool_profile_set", "My name is TestUser", "set_my_name", "text", 5.0, "tools", "simple"),
            BenchmarkTest("tool_profile_show", "Show my profile", "show_my_profile", "text", 5.0, "tools", "simple"),

            # RAG and memory tools
            BenchmarkTest("tool_memory_remember", "Remember I like pizza", "remember_fact", "text", 10.0, "tools", "moderate"),
            BenchmarkTest("tool_memory_search", "Search my conversations", "search_conversations", "text", 10.0, "tools", "moderate"),
            BenchmarkTest("tool_memory_documents", "Search my documents", "search_documents", "text", 10.0, "tools", "moderate"),

            # UI and system control tools
            BenchmarkTest("tool_ui_open", "Open settings", "open_jarvis_ui", "text", 10.0, "tools", "moderate"),
            BenchmarkTest("tool_logs_open", "Open logs", "open_logs_terminal", "text", 10.0, "tools", "moderate"),
            BenchmarkTest("tool_rag_open", "Open vault", "open_rag_manager", "text", 10.0, "tools", "moderate"),

            # Development tools
            BenchmarkTest("tool_aider_status", "Is Aider working?", "check_aider_status", "text", 10.0, "tools", "moderate"),
            BenchmarkTest("tool_aider_edit", "Use Aider to edit code", "aider_code_edit", "text", 30.0, "tools", "complex"),

            # Web automation tools
            BenchmarkTest("tool_web_status", "Is web automation working?", "check_lavague_status", "text", 10.0, "tools", "moderate"),
            BenchmarkTest("tool_web_scrape", "Scrape information from a website", "web_scraping_task", "text", 25.0, "tools", "complex"),

            # Testing tools
            BenchmarkTest("tool_test_validate", "Is the test system ready?", "validate_test_system", "text", 10.0, "tools", "moderate"),
            BenchmarkTest("tool_test_list", "What tests are available?", "list_available_tests", "text", 10.0, "tools", "moderate"),
        ]
    
    def _create_performance_test_suite(self) -> List[BenchmarkTest]:
        """Create test suite focused on performance measurement."""
        return [
            # Stress test with repeated simple queries
            BenchmarkTest("perf_time_1", "What time is it?", "get_current_time", "text", 2.0, "performance", "simple"),
            BenchmarkTest("perf_time_2", "Tell me the time", "get_current_time", "text", 2.0, "performance", "simple"),
            BenchmarkTest("perf_time_3", "Current time please", "get_current_time", "text", 2.0, "performance", "simple"),
            BenchmarkTest("perf_greeting_1", "Hello", None, "text", 2.0, "performance", "simple"),
            BenchmarkTest("perf_greeting_2", "Hi", None, "text", 2.0, "performance", "simple"),
            BenchmarkTest("perf_status_1", "How are you?", None, "text", 2.0, "performance", "simple"),
            BenchmarkTest("perf_status_2", "Are you okay?", None, "text", 2.0, "performance", "simple"),
        ]

    def _create_rag_focused_test_suite(self) -> List[BenchmarkTest]:
        """Create test suite focused on RAG and memory system functionality."""
        return [
            # Basic memory operations
            BenchmarkTest("rag_remember_simple", "Remember that I like coffee", "remember_fact", "text", 10.0, "rag", "moderate"),
            BenchmarkTest("rag_remember_complex", "Remember that I work as a software engineer at TechCorp and prefer Python over JavaScript", "remember_fact", "text", 15.0, "rag", "moderate"),

            # Search operations
            BenchmarkTest("rag_search_conversations", "What did we discuss about programming?", "search_conversations", "text", 15.0, "rag", "moderate"),
            BenchmarkTest("rag_search_documents", "Find information about machine learning in my documents", "search_documents", "text", 15.0, "rag", "moderate"),
            BenchmarkTest("rag_search_all", "Search everything for information about my work projects", "search_all_memory", "text", 20.0, "rag", "moderate"),
            BenchmarkTest("rag_search_long_term", "What do you know about my preferences and habits?", "search_long_term_memory", "text", 20.0, "rag", "moderate"),
            BenchmarkTest("rag_search_intelligent", "Find all information related to my career and professional development", "search_long_term_memory_intelligent", "text", 25.0, "rag", "complex"),

            # RAG UI operations
            BenchmarkTest("rag_ui_open", "Open the vault interface", "open_rag_manager", "text", 10.0, "rag", "moderate"),
            BenchmarkTest("rag_ui_status", "Show vault status", "show_rag_status", "text", 5.0, "rag", "simple"),
            BenchmarkTest("rag_ui_close", "Close the vault", "close_rag_manager", "text", 5.0, "rag", "simple"),

            # Complex RAG workflows
            BenchmarkTest("rag_workflow_remember_search", "Remember that I'm learning React, then search for what you know about my learning", None, "text", 30.0, "rag", "complex"),
            BenchmarkTest("rag_workflow_comprehensive", "Open vault, search my documents for Python tutorials, remember what you find, then close vault", None, "text", 45.0, "rag", "complex"),
        ]

    def _create_integration_test_suite(self) -> List[BenchmarkTest]:
        """Create test suite focused on multi-tool integration and workflows."""
        return [
            # Profile + Memory integration
            BenchmarkTest("integration_profile_memory", "Set my name to John, then remember I like Python programming", None, "text", 20.0, "integration", "moderate"),
            BenchmarkTest("integration_memory_profile", "Search my memory for my name and preferences", None, "text", 15.0, "integration", "moderate"),

            # UI + System integration
            BenchmarkTest("integration_ui_system", "Open settings, show system status, then close settings", None, "text", 25.0, "integration", "moderate"),
            BenchmarkTest("integration_logs_status", "Open logs, show system status, then show logs status", None, "text", 20.0, "integration", "moderate"),

            # Development workflow integration
            BenchmarkTest("integration_dev_workflow", "Check if Aider is working, then check test system status", None, "text", 20.0, "integration", "moderate"),
            BenchmarkTest("integration_full_dev", "Check Aider status, validate test system, then list available tests", None, "text", 30.0, "integration", "complex"),

            # RAG + Profile integration
            BenchmarkTest("integration_rag_profile", "Show my profile, then search my memory for personal information", None, "text", 25.0, "integration", "moderate"),
            BenchmarkTest("integration_comprehensive", "Set my name, remember my job, search my documents, and show my profile", None, "text", 45.0, "integration", "complex"),

            # Web + Memory integration
            BenchmarkTest("integration_web_memory", "Check web automation status, then remember that I use web automation", None, "text", 25.0, "integration", "moderate"),

            # Full system integration
            BenchmarkTest("integration_full_system", "Show system status, open vault, search my memory, show my profile, and open logs", None, "text", 60.0, "integration", "complex"),
        ]

    def _create_stress_test_suite(self) -> List[BenchmarkTest]:
        """Create test suite for stress testing and performance consistency."""
        return [
            # Rapid-fire simple queries
            BenchmarkTest("stress_time_1", "What time is it?", "get_current_time", "text", 3.0, "stress", "simple"),
            BenchmarkTest("stress_time_2", "Tell me the time", "get_current_time", "text", 3.0, "stress", "simple"),
            BenchmarkTest("stress_time_3", "Current time please", "get_current_time", "text", 3.0, "stress", "simple"),
            BenchmarkTest("stress_time_4", "What's the time now?", "get_current_time", "text", 3.0, "stress", "simple"),
            BenchmarkTest("stress_time_5", "Time check", "get_current_time", "text", 3.0, "stress", "simple"),

            # Rapid profile queries
            BenchmarkTest("stress_name_1", "What's my name?", "get_my_name", "text", 5.0, "stress", "simple"),
            BenchmarkTest("stress_name_2", "Do you know my name?", "get_my_name", "text", 5.0, "stress", "simple"),
            BenchmarkTest("stress_name_3", "Tell me my name", "get_my_name", "text", 5.0, "stress", "simple"),

            # Rapid system queries
            BenchmarkTest("stress_status_1", "System status", "show_jarvis_status", "text", 5.0, "stress", "simple"),
            BenchmarkTest("stress_status_2", "How are you?", None, "text", 3.0, "stress", "simple"),
            BenchmarkTest("stress_status_3", "Are you working?", None, "text", 3.0, "stress", "simple"),

            # Memory stress tests
            BenchmarkTest("stress_memory_1", "Remember I like coffee", "remember_fact", "text", 10.0, "stress", "moderate"),
            BenchmarkTest("stress_memory_2", "Remember I work in tech", "remember_fact", "text", 10.0, "stress", "moderate"),
            BenchmarkTest("stress_memory_3", "Remember I use Python", "remember_fact", "text", 10.0, "stress", "moderate"),

            # Complex operation stress
            BenchmarkTest("stress_complex_1", "Search all my information about work", "search_all_memory", "text", 20.0, "stress", "complex"),
            BenchmarkTest("stress_complex_2", "Open vault and show status", None, "text", 15.0, "stress", "moderate"),
            BenchmarkTest("stress_complex_3", "Check all system components", None, "text", 25.0, "stress", "complex"),
        ]

    def _create_progressive_test_suite(self) -> List[BenchmarkTest]:
        """Create progressive test suite that builds from simple to complex, testing every component."""
        return [
            # === LEVEL 1: BASIC FUNCTIONALITY ===
            BenchmarkTest("prog_01_time", "What time is it?", "get_current_time", "text", 5.0, "progressive", "simple"),
            BenchmarkTest("prog_02_greeting", "Hello", None, "text", 3.0, "progressive", "simple"),
            BenchmarkTest("prog_03_status", "How are you?", None, "text", 3.0, "progressive", "simple"),

            # === LEVEL 2: USER PROFILE SYSTEM ===
            BenchmarkTest("prog_04_set_name", "My name is TestUser", "set_my_name", "text", 5.0, "progressive", "simple"),
            BenchmarkTest("prog_05_get_name", "What is my name?", "get_my_name", "text", 5.0, "progressive", "simple"),
            BenchmarkTest("prog_06_set_pronouns", "My pronouns are they/them", "set_my_pronouns", "text", 5.0, "progressive", "simple"),
            BenchmarkTest("prog_07_show_profile", "Show my profile", "show_my_profile", "text", 5.0, "progressive", "simple"),

            # === LEVEL 3: MEMORY SYSTEM BASICS ===
            BenchmarkTest("prog_08_remember_fact", "Remember that I like coffee", "remember_fact", "text", 10.0, "progressive", "moderate"),
            BenchmarkTest("prog_09_remember_work", "Remember that I work as a software engineer", "remember_fact", "text", 10.0, "progressive", "moderate"),
            BenchmarkTest("prog_10_search_memory", "What do you remember about me?", "search_long_term_memory", "text", 15.0, "progressive", "moderate"),

            # === LEVEL 4: UI AND SYSTEM CONTROL ===
            BenchmarkTest("prog_11_system_status", "Show system status", "show_jarvis_status", "text", 5.0, "progressive", "simple"),
            BenchmarkTest("prog_12_open_logs", "Open logs", "open_logs_terminal", "text", 10.0, "progressive", "moderate"),
            BenchmarkTest("prog_13_logs_status", "Show logs status", "show_logs_status", "text", 5.0, "progressive", "simple"),
            BenchmarkTest("prog_14_open_vault", "Open vault", "open_rag_manager", "text", 10.0, "progressive", "moderate"),
            BenchmarkTest("prog_15_vault_status", "Show vault status", "show_rag_status", "text", 5.0, "progressive", "simple"),

            # === LEVEL 5: ADVANCED MEMORY OPERATIONS ===
            BenchmarkTest("prog_16_search_conversations", "Search my conversations for programming topics", "search_conversations", "text", 15.0, "progressive", "moderate"),
            BenchmarkTest("prog_17_search_documents", "Search my documents for technical information", "search_documents", "text", 15.0, "progressive", "moderate"),
            BenchmarkTest("prog_18_search_all", "Search all my information about work and preferences", "search_all_memory", "text", 20.0, "progressive", "moderate"),
            BenchmarkTest("prog_19_intelligent_search", "Find everything related to my professional development", "search_long_term_memory_intelligent", "text", 25.0, "progressive", "complex"),

            # === LEVEL 6: DEVELOPMENT TOOLS ===
            BenchmarkTest("prog_20_aider_status", "Is Aider working?", "check_aider_status", "text", 10.0, "progressive", "moderate"),
            BenchmarkTest("prog_21_test_system", "Is the test system ready?", "validate_test_system", "text", 10.0, "progressive", "moderate"),
            BenchmarkTest("prog_22_list_tests", "What tests are available?", "list_available_tests", "text", 10.0, "progressive", "moderate"),

            # === LEVEL 7: WEB AUTOMATION ===
            BenchmarkTest("prog_23_web_status", "Is web automation working?", "check_lavague_status", "text", 10.0, "progressive", "moderate"),
            BenchmarkTest("prog_24_web_scraping", "Get the title from example.com", "web_scraping_task", "text", 25.0, "progressive", "complex"),

            # === LEVEL 8: INTEGRATION WORKFLOWS ===
            BenchmarkTest("prog_25_profile_memory", "Show my profile and search my memory", None, "text", 25.0, "progressive", "moderate"),
            BenchmarkTest("prog_26_ui_workflow", "Open settings, show status, then close settings", None, "text", 25.0, "progressive", "moderate"),
            BenchmarkTest("prog_27_memory_workflow", "Remember I like Python, then search for my programming preferences", None, "text", 30.0, "progressive", "complex"),

            # === LEVEL 9: ADVANCED DEVELOPMENT ===
            BenchmarkTest("prog_28_aider_edit", "Use Aider to help with code editing", "aider_code_edit", "text", 30.0, "progressive", "complex"),
            BenchmarkTest("prog_29_run_tests", "Run basic system tests", "run_robot_tests", "text", 60.0, "progressive", "complex"),

            # === LEVEL 10: FULL SYSTEM INTEGRATION ===
            BenchmarkTest("prog_30_comprehensive", "Show my profile, search my memory, open vault, check system status, and summarize everything", None, "text", 60.0, "progressive", "complex"),
        ]
    
    async def initialize_jarvis(self):
        """Initialize Jarvis components for testing."""
        try:
            from jarvis.config import JarvisConfig
            from jarvis.core.agent import JarvisAgent
            from jarvis.core.conversation import ConversationManager
            from jarvis.core.speech import SpeechManager
            
            logger.info("Initializing Jarvis components for benchmarking...")
            
            # Load configuration
            self.config = JarvisConfig.from_env()
            logger.info("✅ Configuration loaded")
            
            # Initialize agent
            self.agent = JarvisAgent(self.config.llm, self.config.agent)
            
            # Get tools for agent
            from jarvis.tools import get_langchain_tools
            tools = get_langchain_tools()
            self.agent.initialize(tools=tools)
            logger.info(f"✅ Agent initialized with {len(tools)} tools")
            
            # Initialize speech manager (minimal for testing)
            self.speech_manager = SpeechManager(self.config.audio)
            logger.info("✅ Speech manager initialized")
            
            # Initialize conversation manager with fast path routing
            try:
                from jarvis.core.routing import SmartConversationManager
                logger.info("🚀 Using Smart Conversation Manager with fast path routing for benchmarks")
                self.conversation_manager = SmartConversationManager(
                    self.config,  # Pass full config
                    self.speech_manager,
                    self.agent,
                    None  # No MCP client needed for benchmarking
                )
                logger.info("✅ Fast path routing enabled for benchmarks - should fix timeout issues!")
            except ImportError as e:
                logger.warning(f"⚠️ Fast path routing import failed: {e}")
                self.conversation_manager = ConversationManager(
                    self.config.conversation,
                    self.speech_manager,
                    self.agent,
                    None  # No MCP client needed for benchmarking
                )
            except Exception as e:
                logger.error(f"⚠️ Fast path routing initialization failed: {e}")
                logger.error(f"Exception type: {type(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                logger.warning("Falling back to original ConversationManager")
                self.conversation_manager = ConversationManager(
                    self.config.conversation,
                    self.speech_manager,
                    self.agent,
                    None  # No MCP client needed for benchmarking
                )
            logger.info("✅ Conversation manager initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Jarvis components: {e}")
            return False
    
    async def run_single_test(self, test: BenchmarkTest) -> BenchmarkResult:
        """Run a single benchmark test through the complete LLM workflow."""
        logger.info(f"Running test: {test.name} - '{test.query}'")

        start_time = time.time()
        timestamp = datetime.now().isoformat()

        try:
            # CRITICAL: Test the complete workflow - prompt → LLM → tool selection → execution
            print(f"\n🧪 TESTING: {test.name}")
            print(f"📝 Prompt: '{test.query}'")
            print(f"🎯 Expected Tool: {test.expected_tool or 'Any'}")
            print(f"⏱️  Timeout: {test.timeout_seconds}s")

            # Run through the complete conversation manager workflow
            if self.conversation_manager:
                # Use conversation manager for complete workflow testing
                response = await asyncio.wait_for(
                    self.conversation_manager.process_command(test.query),
                    timeout=test.timeout_seconds
                )
            else:
                # Fallback to direct agent testing
                response = await asyncio.wait_for(
                    self.agent.process_input(test.query),
                    timeout=test.timeout_seconds
                )

            execution_time = time.time() - start_time

            # Extract tool information if available
            tool_used = self._extract_tool_used(response)

            # Determine success
            success = self._evaluate_test_success(test, response, tool_used, execution_time)

            # Print immediate feedback for iterative improvement
            print(f"💬 Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            print(f"🔧 Tool Used: {tool_used or 'None detected'}")
            print(f"⏱️  Time: {execution_time:.2f}s")
            print(f"✅ Success: {success}")

            if not success:
                print(f"❌ Issues detected:")
                if not response or response.strip() == "":
                    print(f"   - Empty response")
                if "error" in response.lower() or "sorry" in response.lower():
                    print(f"   - Error in response")
                if test.expected_tool and tool_used != test.expected_tool:
                    print(f"   - Wrong tool: expected {test.expected_tool}, got {tool_used}")
                if execution_time > test.timeout_seconds * 0.8:
                    print(f"   - Slow execution: {execution_time:.2f}s (target: <{test.timeout_seconds}s)")

            result = BenchmarkResult(
                test_name=test.name,
                query=test.query,
                success=success,
                response=response[:200] + "..." if len(response) > 200 else response,
                execution_time=execution_time,
                tool_used=tool_used,
                error_message=None,
                timestamp=timestamp,
                metadata={
                    "expected_tool": test.expected_tool,
                    "category": test.category,
                    "complexity": test.complexity,
                    "timeout": test.timeout_seconds,
                    "full_response": response  # Store full response for analysis
                }
            )

            logger.info(f"✅ {test.name}: {execution_time:.2f}s - {'SUCCESS' if success else 'PARTIAL'}")
            return result
            
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            logger.warning(f"⏰ {test.name}: TIMEOUT after {execution_time:.2f}s")
            
            return BenchmarkResult(
                test_name=test.name,
                query=test.query,
                success=False,
                response="",
                execution_time=execution_time,
                tool_used=None,
                error_message=f"Timeout after {test.timeout_seconds}s",
                timestamp=timestamp,
                metadata={
                    "expected_tool": test.expected_tool,
                    "category": test.category,
                    "complexity": test.complexity,
                    "timeout": test.timeout_seconds
                }
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ {test.name}: ERROR - {str(e)}")
            
            return BenchmarkResult(
                test_name=test.name,
                query=test.query,
                success=False,
                response="",
                execution_time=execution_time,
                tool_used=None,
                error_message=str(e),
                timestamp=timestamp,
                metadata={
                    "expected_tool": test.expected_tool,
                    "category": test.category,
                    "complexity": test.complexity,
                    "timeout": test.timeout_seconds
                }
            )
    
    def _extract_tool_used(self, response: str) -> Optional[str]:
        """Extract which tool was used from the response (enhanced for fast path detection)."""
        # Enhanced heuristics that work with fast path routing
        tool_indicators = {
            "get_current_time": ["time", "clock", "PM", "AM", "it's", "the time is"],
            "get_my_name": ["name is", "your name", "my name", "i'm"],
            "remember_fact": ["remembered", "I'll remember", "noted", "got it"],
            "open_logs_terminal": ["logs", "terminal", "opened", "debug"],
            "analyze_file": ["analysis", "analyzed", "code review"],
            "show_my_profile": ["profile", "your profile", "about you"],
            "show_jarvis_status": ["status", "working", "ready", "system"],
            "search_long_term_memory": ["remember", "recall", "memory", "know about"],
        }

        response_lower = response.lower()

        # Special case for time responses - if it contains time format, it used get_current_time
        import re
        time_pattern = r'\d{1,2}:\d{2}\s*(AM|PM|am|pm)'
        if re.search(time_pattern, response):
            return "get_current_time"

        # Check other indicators
        for tool, indicators in tool_indicators.items():
            if any(indicator in response_lower for indicator in indicators):
                return tool

        return None
    
    def _evaluate_test_success(self, test: BenchmarkTest, response: str, tool_used: Optional[str], execution_time: float) -> bool:
        """Evaluate if a test was successful."""
        # Basic success criteria
        if not response or response.strip() == "":
            return False
        
        if "error" in response.lower() or "sorry" in response.lower():
            return False
        
        # Check expected tool usage
        if test.expected_tool and tool_used != test.expected_tool:
            return False
        
        # Check performance targets based on complexity
        performance_targets = {
            "simple": 5.0,
            "moderate": 15.0,
            "complex": 30.0
        }
        
        target_time = performance_targets.get(test.complexity, 30.0)
        if execution_time > target_time:
            return False
        
        return True

    async def run_test_suite(self, suite_name: str = "quick") -> BenchmarkSuite:
        """Run a complete test suite."""
        if suite_name not in self.test_suites:
            raise ValueError(f"Unknown test suite: {suite_name}. Available: {list(self.test_suites.keys())}")

        tests = self.test_suites[suite_name]
        logger.info(f"🚀 Running {suite_name} test suite with {len(tests)} tests")

        start_time = time.time()
        results = []

        print(f"\n🚀 STARTING {suite_name.upper()} BENCHMARK SUITE")
        print(f"{'='*80}")
        print(f"This will test the complete LLM workflow: Prompt → Tool Selection → Execution → Response")
        print(f"Watch for optimization opportunities as each test completes...")
        print(f"{'='*80}")

        for i, test in enumerate(tests, 1):
            print(f"\n⏳ Running test {i}/{len(tests)}: {test.name}")

            result = await self.run_single_test(test)
            results.append(result)

            # Provide real-time feedback for optimization
            self.provide_real_time_feedback(result, i, len(tests))

            # Show progress summary every 5 tests
            if i % 5 == 0 or i == len(tests):
                current_success_rate = (sum(1 for r in results if r.success) / len(results)) * 100
                self.show_progress_summary(i, len(tests), current_success_rate)

            # Small delay between tests to avoid overwhelming the system
            await asyncio.sleep(1.0)  # Increased delay for better observation

        total_time = time.time() - start_time
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = len(results) - successful_tests

        if results:
            avg_execution_time = statistics.mean(r.execution_time for r in results)
        else:
            avg_execution_time = 0.0

        suite_result = BenchmarkSuite(
            suite_name=suite_name,
            timestamp=datetime.now().isoformat(),
            total_tests=len(results),
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            avg_execution_time=avg_execution_time,
            total_execution_time=total_time,
            results=results,
            system_info=self._get_system_info()
        )

        # Save results
        self._save_results(suite_result)

        # Print summary
        self._print_summary(suite_result)

        return suite_result

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmarking context."""
        import platform
        try:
            import psutil
            cpu_count = psutil.cpu_count()
            memory_gb = round(psutil.virtual_memory().total / (1024**3), 2)
        except ImportError:
            cpu_count = "unknown"
            memory_gb = "unknown"

        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": cpu_count,
            "memory_gb": memory_gb,
            "llm_model": self.config.llm.model if self.config else "unknown",
            "timestamp": datetime.now().isoformat()
        }

    def _save_results(self, suite_result: BenchmarkSuite):
        """Save benchmark results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{suite_result.suite_name}_{timestamp}.json"
        filepath = self.results_dir / filename

        # Convert to dict for JSON serialization
        data = asdict(suite_result)

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"📊 Results saved to: {filepath}")

    def _print_summary(self, suite_result: BenchmarkSuite):
        """Print benchmark summary."""
        print(f"\n🎯 BENCHMARK RESULTS: {suite_result.suite_name.upper()}")
        print("=" * 60)
        print(f"Total Tests: {suite_result.total_tests}")
        print(f"Successful: {suite_result.successful_tests} ({suite_result.successful_tests/suite_result.total_tests*100:.1f}%)")
        print(f"Failed: {suite_result.failed_tests} ({suite_result.failed_tests/suite_result.total_tests*100:.1f}%)")
        print(f"Average Execution Time: {suite_result.avg_execution_time:.2f}s")
        print(f"Total Suite Time: {suite_result.total_execution_time:.2f}s")

        # Category breakdown
        categories = {}
        for result in suite_result.results:
            category = result.metadata.get("category", "unknown")
            if category not in categories:
                categories[category] = {"total": 0, "success": 0, "avg_time": []}

            categories[category]["total"] += 1
            if result.success:
                categories[category]["success"] += 1
            categories[category]["avg_time"].append(result.execution_time)

        print(f"\n📊 CATEGORY BREAKDOWN:")
        for category, stats in categories.items():
            success_rate = stats["success"] / stats["total"] * 100
            avg_time = statistics.mean(stats["avg_time"])
            print(f"  {category.upper()}: {stats['success']}/{stats['total']} ({success_rate:.1f}%) - {avg_time:.2f}s avg")

        # Show failed tests
        failed_tests = [r for r in suite_result.results if not r.success]
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for result in failed_tests:
                reason = result.error_message or "Performance/Response issue"
                print(f"  {result.test_name}: {reason} ({result.execution_time:.2f}s)")

        # Show slowest tests
        slowest_tests = sorted(suite_result.results, key=lambda r: r.execution_time, reverse=True)[:3]
        print(f"\n⏱️  SLOWEST TESTS:")
        for result in slowest_tests:
            status = "✅" if result.success else "❌"
            print(f"  {status} {result.test_name}: {result.execution_time:.2f}s")

    def generate_optimization_suggestions(self, suite_result: BenchmarkSuite) -> List[str]:
        """Generate specific, actionable optimization suggestions based on LLM workflow results."""
        suggestions = []

        # Analyze failed tests with detailed feedback
        failed_tests = [r for r in suite_result.results if not r.success]
        timeout_tests = [r for r in failed_tests if "timeout" in (r.error_message or "").lower()]

        if timeout_tests:
            suggestions.append(f"🔧 TIMEOUT ISSUE: {len(timeout_tests)} tests timed out")
            suggestions.append(f"   → Immediate fix: Increase timeout limits in config")
            suggestions.append(f"   → Root cause: Optimize LLM response time or tool execution")

            # Identify which categories are timing out
            timeout_categories = [r.metadata.get("category", "unknown") for r in timeout_tests]
            for category in set(timeout_categories):
                count = timeout_categories.count(category)
                suggestions.append(f"   → {category} category: {count} timeouts - focus optimization here")

        # Analyze LLM prompt → tool selection issues
        wrong_tool_tests = []
        for result in failed_tests:
            expected = result.metadata.get("expected_tool")
            actual = result.tool_used
            if expected and actual and expected != actual:
                wrong_tool_tests.append((result, expected, actual))

        if wrong_tool_tests:
            suggestions.append(f"🎯 TOOL SELECTION ISSUE: {len(wrong_tool_tests)} tests used wrong tools")
            for result, expected, actual in wrong_tool_tests[:3]:  # Show first 3
                suggestions.append(f"   → '{result.query}' used {actual} instead of {expected}")
            suggestions.append(f"   → Fix: Improve tool descriptions and LLM prompting")
            suggestions.append(f"   → Fix: Reduce number of tools presented to LLM")

        # Analyze empty/error responses (LLM issues)
        empty_responses = [r for r in failed_tests if not r.response or r.response.strip() == ""]
        error_responses = [r for r in failed_tests if "error" in r.response.lower() or "sorry" in r.response.lower()]

        if empty_responses:
            suggestions.append(f"💬 EMPTY RESPONSE ISSUE: {len(empty_responses)} tests returned empty responses")
            suggestions.append(f"   → Fix: Check LLM model availability and configuration")
            suggestions.append(f"   → Fix: Verify conversation manager is properly initialized")

        if error_responses:
            suggestions.append(f"❌ ERROR RESPONSE ISSUE: {len(error_responses)} tests returned error messages")
            for result in error_responses[:2]:  # Show first 2
                suggestions.append(f"   → '{result.query}': {result.response[:50]}...")
            suggestions.append(f"   → Fix: Debug specific tool implementations")

        # Performance analysis by category with specific targets
        categories = {}
        for result in suite_result.results:
            category = result.metadata.get("category", "unknown")
            if category not in categories:
                categories[category] = []
            categories[category].append(result.execution_time)

        performance_targets = {
            "instant": 1.0,
            "progressive": 2.0,
            "user_profile": 3.0,
            "rag_memory": 5.0,
            "ui_system": 5.0,
            "tools": 8.0,
            "development": 15.0,
            "web_automation": 20.0,
            "integration": 15.0,
            "complex": 25.0
        }

        for category, times in categories.items():
            if not times:
                continue
            avg_time = statistics.mean(times)
            target = performance_targets.get(category, 10.0)

            if avg_time > target:
                suggestions.append(f"⏱️  PERFORMANCE ISSUE: {category} averaging {avg_time:.2f}s (target: <{target}s)")

                if category == "instant":
                    suggestions.append(f"   → CRITICAL: Implement fast path routing for simple queries")
                    suggestions.append(f"   → Add direct handlers for time, greetings, status queries")
                elif category in ["user_profile", "rag_memory"]:
                    suggestions.append(f"   → Optimize database queries and caching")
                elif category == "tools":
                    suggestions.append(f"   → Reduce tool count presented to LLM")
                    suggestions.append(f"   → Improve tool selection prompting")
                elif category in ["development", "web_automation"]:
                    suggestions.append(f"   → These are inherently slow - consider async processing")
                else:
                    suggestions.append(f"   → Profile and optimize {category} operations")

        # Success rate analysis
        success_rate = suite_result.successful_tests / suite_result.total_tests * 100
        if success_rate < 80:
            suggestions.append(f"📊 LOW SUCCESS RATE: {success_rate:.1f}% - system needs significant optimization")
            suggestions.append(f"   → Priority: Fix the {len(failed_tests)} failing tests first")
        elif success_rate < 95:
            suggestions.append(f"📈 MODERATE SUCCESS RATE: {success_rate:.1f}% - fine-tuning needed")

        # Specific improvement workflow
        if suggestions:
            suggestions.append(f"")
            suggestions.append(f"🔄 RECOMMENDED OPTIMIZATION WORKFLOW:")
            suggestions.append(f"   1. Fix timeout issues first (affects {len(timeout_tests)} tests)")
            suggestions.append(f"   2. Implement fast path routing for simple queries")
            suggestions.append(f"   3. Optimize tool selection and descriptions")
            suggestions.append(f"   4. Run benchmark again to measure improvement")
            suggestions.append(f"   5. Repeat with next highest-impact issue")

        return suggestions

    def provide_real_time_feedback(self, result: BenchmarkResult, test_number: int, total_tests: int):
        """Provide real-time feedback during testing for immediate optimization insights."""

        print(f"\n{'='*60}")
        print(f"TEST {test_number}/{total_tests} COMPLETED: {result.test_name}")
        print(f"{'='*60}")

        # Show the complete workflow
        print(f"📝 PROMPT GIVEN TO LLM:")
        print(f"   '{result.query}'")
        print(f"")
        print(f"🤖 LLM WORKFLOW RESULT:")
        print(f"   Response: {result.response}")
        print(f"   Tool Used: {result.tool_used or 'None detected'}")
        print(f"   Execution Time: {result.execution_time:.2f}s")
        print(f"   Success: {'✅ YES' if result.success else '❌ NO'}")

        # Immediate optimization feedback
        if not result.success:
            print(f"\n🔧 IMMEDIATE OPTIMIZATION OPPORTUNITIES:")

            expected_tool = result.metadata.get("expected_tool")
            if expected_tool and result.tool_used != expected_tool:
                print(f"   • TOOL SELECTION: Expected {expected_tool}, got {result.tool_used}")
                print(f"     → Improve tool descriptions")
                print(f"     → Reduce tool count for LLM")

            if result.execution_time > result.metadata.get("timeout", 30) * 0.8:
                print(f"   • PERFORMANCE: {result.execution_time:.2f}s is too slow")
                print(f"     → Add fast path for simple queries")
                print(f"     → Optimize tool execution")

            if not result.response or "error" in result.response.lower():
                print(f"   • RESPONSE QUALITY: Empty or error response")
                print(f"     → Check tool implementation")
                print(f"     → Verify LLM model availability")

        else:
            print(f"\n✅ SUCCESS FACTORS:")
            print(f"   • Correct tool selection: {result.tool_used}")
            print(f"   • Good response time: {result.execution_time:.2f}s")
            print(f"   • Quality response generated")

        # Category-specific feedback
        category = result.metadata.get("category", "unknown")
        complexity = result.metadata.get("complexity", "unknown")

        print(f"\n📊 CONTEXT:")
        print(f"   Category: {category}")
        print(f"   Complexity: {complexity}")

        if category == "instant" and result.execution_time > 1.0:
            print(f"   ⚠️  INSTANT queries should be <1s - this took {result.execution_time:.2f}s")
        elif category == "progressive" and not result.success:
            print(f"   ⚠️  PROGRESSIVE test failure affects system building complexity")

        print(f"\n💡 NEXT STEPS:")
        if not result.success:
            print(f"   1. Note this specific failure for optimization")
            print(f"   2. Continue testing to identify patterns")
            print(f"   3. Prioritize fixes based on impact")
        else:
            print(f"   1. This workflow is working well")
            print(f"   2. Use as reference for similar queries")

        print(f"{'='*60}")

    def show_progress_summary(self, completed_tests: int, total_tests: int, current_success_rate: float):
        """Show progress summary during testing."""

        progress_percent = (completed_tests / total_tests) * 100

        print(f"\n📈 PROGRESS SUMMARY")
        print(f"{'─'*40}")
        print(f"Tests Completed: {completed_tests}/{total_tests} ({progress_percent:.1f}%)")
        print(f"Current Success Rate: {current_success_rate:.1f}%")

        if current_success_rate < 50:
            print(f"🚨 LOW SUCCESS RATE - Major optimization needed")
        elif current_success_rate < 80:
            print(f"⚠️  MODERATE SUCCESS RATE - Some optimization needed")
        else:
            print(f"✅ GOOD SUCCESS RATE - System performing well")

        print(f"{'─'*40}")
        print(f"Continue testing to identify all optimization opportunities...")
        print(f"")

# CLI interface and utility functions
async def run_benchmark_cli():
    """CLI interface for running benchmarks."""
    import argparse

    parser = argparse.ArgumentParser(description="Jarvis Performance Benchmarking System")
    parser.add_argument("--suite", choices=["quick", "comprehensive", "tool_focused", "performance"],
                       default="quick", help="Test suite to run")
    parser.add_argument("--results-dir", default="benchmark_results", help="Directory for results")
    parser.add_argument("--iterations", type=int, default=1, help="Number of iterations to run")

    args = parser.parse_args()

    benchmark = JarvisBenchmark(args.results_dir)

    # Initialize Jarvis
    print("🔧 Initializing Jarvis components...")
    if not await benchmark.initialize_jarvis():
        print("❌ Failed to initialize Jarvis components")
        return

    print("✅ Jarvis components initialized")

    # Run benchmark iterations
    all_results = []
    for i in range(args.iterations):
        if args.iterations > 1:
            print(f"\n🔄 Running iteration {i+1}/{args.iterations}")

        results = await benchmark.run_test_suite(args.suite)
        all_results.append(results)

        # Generate optimization suggestions
        suggestions = benchmark.generate_optimization_suggestions(results)
        if suggestions:
            print(f"\n💡 OPTIMIZATION SUGGESTIONS:")
            for suggestion in suggestions:
                print(f"  {suggestion}")

        if i < args.iterations - 1:
            print(f"\n⏸️  Waiting 5 seconds before next iteration...")
            await asyncio.sleep(5)

    # If multiple iterations, show comparison
    if len(all_results) > 1:
        print(f"\n📈 ITERATION COMPARISON:")
        print("-" * 40)
        for i, result in enumerate(all_results):
            success_rate = result.successful_tests / result.total_tests * 100
            print(f"Iteration {i+1}: {success_rate:.1f}% success, {result.avg_execution_time:.2f}s avg")

if __name__ == "__main__":
    asyncio.run(run_benchmark_cli())
