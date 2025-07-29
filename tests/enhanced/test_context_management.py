"""
Test suite for Context Management System

Tests the ContextManager, ConversationState, ToolStateTracker,
UserPreferenceEngine, and SessionMemory components.
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from tests.enhanced import EnhancedTestBase, TEST_CONFIG

# Mock context management components
class MockContextManager:
    """Mock implementation for testing."""
    
    def __init__(self):
        self.contexts = {}
        self.sessions = {}
        self.preferences = {}
    
    def get_current_context(self, session_id: str = "default") -> Dict[str, Any]:
        return self.contexts.get(session_id, {})
    
    def update_context(self, session_id: str, updates: Dict[str, Any]) -> None:
        if session_id not in self.contexts:
            self.contexts[session_id] = {}
        self.contexts[session_id].update(updates)
    
    def create_session(self, session_id: str) -> None:
        self.sessions[session_id] = {
            'created_at': time.time(),
            'last_activity': time.time(),
            'active': True
        }
        self.contexts[session_id] = {}
    
    def clear_session(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)
        self.contexts.pop(session_id, None)

class MockConversationState:
    """Mock conversation state tracker."""
    
    def __init__(self):
        self.state = {
            'current_topic': None,
            'intent_history': [],
            'active_tools': set(),
            'conversation_flow': []
        }
    
    def update_topic(self, topic: str) -> None:
        self.state['current_topic'] = topic
    
    def add_intent(self, intent: str) -> None:
        self.state['intent_history'].append(intent)
    
    def activate_tool(self, tool_name: str) -> None:
        self.state['active_tools'].add(tool_name)
    
    def deactivate_tool(self, tool_name: str) -> None:
        self.state['active_tools'].discard(tool_name)

class TestContextManager(EnhancedTestBase):
    """Test suite for ContextManager."""
    
    @pytest.fixture
    def context_manager(self):
        """Create a test context manager instance."""
        return MockContextManager()
    
    def test_context_creation_and_retrieval(self, context_manager):
        """Test context creation and retrieval."""
        session_id = "test_session"
        
        # Create session
        context_manager.create_session(session_id)
        
        # Get initial context (should be empty)
        context = context_manager.get_current_context(session_id)
        assert context == {}
        
        # Update context
        test_context = {
            'user_id': 'test_user',
            'current_topic': 'file_operations',
            'preferences': {'theme': 'dark'}
        }
        context_manager.update_context(session_id, test_context)
        
        # Retrieve updated context
        updated_context = context_manager.get_current_context(session_id)
        assert updated_context['user_id'] == 'test_user'
        assert updated_context['current_topic'] == 'file_operations'
        assert updated_context['preferences']['theme'] == 'dark'
    
    def test_multiple_session_isolation(self, context_manager):
        """Test that multiple sessions are properly isolated."""
        session1 = "session_1"
        session2 = "session_2"
        
        # Create two sessions
        context_manager.create_session(session1)
        context_manager.create_session(session2)
        
        # Update contexts with different data
        context_manager.update_context(session1, {'user': 'user1', 'topic': 'topic1'})
        context_manager.update_context(session2, {'user': 'user2', 'topic': 'topic2'})
        
        # Verify isolation
        context1 = context_manager.get_current_context(session1)
        context2 = context_manager.get_current_context(session2)
        
        assert context1['user'] == 'user1'
        assert context2['user'] == 'user2'
        assert context1['topic'] != context2['topic']
    
    def test_session_cleanup(self, context_manager):
        """Test session cleanup functionality."""
        session_id = "cleanup_test_session"
        
        # Create and populate session
        context_manager.create_session(session_id)
        context_manager.update_context(session_id, {'test_data': 'value'})
        
        # Verify session exists
        assert session_id in context_manager.sessions
        assert session_id in context_manager.contexts
        
        # Clear session
        context_manager.clear_session(session_id)
        
        # Verify cleanup
        assert session_id not in context_manager.sessions
        assert session_id not in context_manager.contexts
    
    @pytest.mark.benchmark
    def test_context_retrieval_performance(self, context_manager, benchmark):
        """Benchmark context retrieval performance."""
        session_id = "performance_test"
        
        # Create session with substantial context data
        context_manager.create_session(session_id)
        large_context = {
            'conversation_history': [f"message_{i}" for i in range(100)],
            'user_preferences': {f"pref_{i}": f"value_{i}" for i in range(50)},
            'tool_states': {f"tool_{i}": {'active': True} for i in range(20)}
        }
        context_manager.update_context(session_id, large_context)
        
        # Benchmark retrieval
        def retrieve_context():
            return context_manager.get_current_context(session_id)
        
        result = benchmark(retrieve_context)
        assert result is not None
        assert len(result['conversation_history']) == 100
        
        # Verify performance threshold
        assert benchmark.stats['mean'] < TEST_CONFIG['performance_thresholds']['context_retrieval']

class TestConversationState(EnhancedTestBase):
    """Test suite for ConversationState."""
    
    @pytest.fixture
    def conversation_state(self):
        """Create a test conversation state instance."""
        return MockConversationState()
    
    def test_topic_tracking(self, conversation_state):
        """Test conversation topic tracking."""
        # Initial state
        assert conversation_state.state['current_topic'] is None
        
        # Update topic
        conversation_state.update_topic('file_management')
        assert conversation_state.state['current_topic'] == 'file_management'
        
        # Change topic
        conversation_state.update_topic('web_search')
        assert conversation_state.state['current_topic'] == 'web_search'
    
    def test_intent_history_tracking(self, conversation_state):
        """Test intent history tracking."""
        # Initial state
        assert len(conversation_state.state['intent_history']) == 0
        
        # Add intents
        conversation_state.add_intent('search_files')
        conversation_state.add_intent('open_file')
        conversation_state.add_intent('edit_file')
        
        # Verify history
        history = conversation_state.state['intent_history']
        assert len(history) == 3
        assert history[0] == 'search_files'
        assert history[-1] == 'edit_file'
    
    def test_active_tool_tracking(self, conversation_state):
        """Test active tool tracking."""
        # Initial state
        assert len(conversation_state.state['active_tools']) == 0
        
        # Activate tools
        conversation_state.activate_tool('file_manager')
        conversation_state.activate_tool('text_editor')
        
        # Verify active tools
        active_tools = conversation_state.state['active_tools']
        assert 'file_manager' in active_tools
        assert 'text_editor' in active_tools
        assert len(active_tools) == 2
        
        # Deactivate tool
        conversation_state.deactivate_tool('file_manager')
        assert 'file_manager' not in conversation_state.state['active_tools']
        assert 'text_editor' in conversation_state.state['active_tools']

class TestToolStateTracker(EnhancedTestBase):
    """Test suite for ToolStateTracker."""
    
    @pytest.fixture
    def tool_state_tracker(self):
        """Create a mock tool state tracker."""
        tracker = Mock()
        tracker.tool_states = {}
        
        def track_tool_execution(tool_name, state, context=None):
            if tool_name not in tracker.tool_states:
                tracker.tool_states[tool_name] = []
            
            tracker.tool_states[tool_name].append({
                'state': state,
                'context': context,
                'timestamp': time.time()
            })
        
        def get_tool_state(tool_name):
            states = tracker.tool_states.get(tool_name, [])
            return states[-1] if states else None
        
        def get_active_tools():
            active = []
            for tool_name, states in tracker.tool_states.items():
                if states and states[-1]['state'] == 'active':
                    active.append(tool_name)
            return active
        
        tracker.track_tool_execution = track_tool_execution
        tracker.get_tool_state = get_tool_state
        tracker.get_active_tools = get_active_tools
        return tracker
    
    def test_tool_state_tracking(self, tool_state_tracker):
        """Test tool state tracking functionality."""
        tool_name = 'test_tool'
        
        # Track tool states
        tool_state_tracker.track_tool_execution(tool_name, 'initializing')
        tool_state_tracker.track_tool_execution(tool_name, 'active')
        tool_state_tracker.track_tool_execution(tool_name, 'completed')
        
        # Verify state tracking
        current_state = tool_state_tracker.get_tool_state(tool_name)
        assert current_state is not None
        assert current_state['state'] == 'completed'
    
    def test_active_tools_detection(self, tool_state_tracker):
        """Test active tools detection."""
        # Set up multiple tools with different states
        tool_state_tracker.track_tool_execution('tool1', 'active')
        tool_state_tracker.track_tool_execution('tool2', 'completed')
        tool_state_tracker.track_tool_execution('tool3', 'active')
        tool_state_tracker.track_tool_execution('tool4', 'error')
        
        # Get active tools
        active_tools = tool_state_tracker.get_active_tools()
        
        assert 'tool1' in active_tools
        assert 'tool3' in active_tools
        assert 'tool2' not in active_tools
        assert 'tool4' not in active_tools
        assert len(active_tools) == 2

class TestUserPreferenceEngine(EnhancedTestBase):
    """Test suite for UserPreferenceEngine."""
    
    @pytest.fixture
    def preference_engine(self):
        """Create a mock user preference engine."""
        engine = Mock()
        engine.preferences = {}
        engine.interaction_patterns = {}
        
        def learn_preference(user_id, preference_type, value, confidence=1.0):
            if user_id not in engine.preferences:
                engine.preferences[user_id] = {}
            
            engine.preferences[user_id][preference_type] = {
                'value': value,
                'confidence': confidence,
                'learned_at': time.time()
            }
        
        def get_user_preferences(user_id):
            return engine.preferences.get(user_id, {})
        
        def track_interaction_pattern(user_id, pattern_type, data):
            if user_id not in engine.interaction_patterns:
                engine.interaction_patterns[user_id] = {}
            
            if pattern_type not in engine.interaction_patterns[user_id]:
                engine.interaction_patterns[user_id][pattern_type] = []
            
            engine.interaction_patterns[user_id][pattern_type].append({
                'data': data,
                'timestamp': time.time()
            })
        
        engine.learn_preference = learn_preference
        engine.get_user_preferences = get_user_preferences
        engine.track_interaction_pattern = track_interaction_pattern
        return engine
    
    def test_preference_learning(self, preference_engine):
        """Test user preference learning."""
        user_id = 'test_user'
        
        # Learn preferences
        preference_engine.learn_preference(user_id, 'response_style', 'detailed', 0.8)
        preference_engine.learn_preference(user_id, 'tool_preference', 'file_manager', 0.9)
        
        # Retrieve preferences
        preferences = preference_engine.get_user_preferences(user_id)
        
        assert 'response_style' in preferences
        assert preferences['response_style']['value'] == 'detailed'
        assert preferences['response_style']['confidence'] == 0.8
        
        assert 'tool_preference' in preferences
        assert preferences['tool_preference']['value'] == 'file_manager'
    
    def test_interaction_pattern_tracking(self, preference_engine):
        """Test interaction pattern tracking."""
        user_id = 'pattern_user'
        
        # Track interaction patterns
        preference_engine.track_interaction_pattern(
            user_id, 'tool_usage', {'tool': 'file_manager', 'duration': 30}
        )
        preference_engine.track_interaction_pattern(
            user_id, 'tool_usage', {'tool': 'web_search', 'duration': 45}
        )
        preference_engine.track_interaction_pattern(
            user_id, 'query_type', {'type': 'file_operation', 'complexity': 'simple'}
        )
        
        # Verify patterns were tracked
        patterns = preference_engine.interaction_patterns[user_id]
        
        assert 'tool_usage' in patterns
        assert len(patterns['tool_usage']) == 2
        assert patterns['tool_usage'][0]['data']['tool'] == 'file_manager'
        
        assert 'query_type' in patterns
        assert len(patterns['query_type']) == 1

class TestSessionMemory(EnhancedTestBase):
    """Test suite for SessionMemory."""
    
    @pytest.fixture
    def session_memory(self):
        """Create a mock session memory system."""
        memory = Mock()
        memory.sessions = {}
        
        def store_session_data(session_id, key, data):
            if session_id not in memory.sessions:
                memory.sessions[session_id] = {}
            memory.sessions[session_id][key] = data
        
        def retrieve_session_data(session_id, key):
            return memory.sessions.get(session_id, {}).get(key)
        
        def clear_session(session_id):
            memory.sessions.pop(session_id, None)
        
        def get_session_size(session_id):
            session_data = memory.sessions.get(session_id, {})
            # Mock size calculation
            return len(str(session_data))
        
        memory.store_session_data = store_session_data
        memory.retrieve_session_data = retrieve_session_data
        memory.clear_session = clear_session
        memory.get_session_size = get_session_size
        return memory
    
    def test_session_data_storage_and_retrieval(self, session_memory):
        """Test session data storage and retrieval."""
        session_id = 'test_session'
        
        # Store data
        session_memory.store_session_data(session_id, 'user_name', 'John Doe')
        session_memory.store_session_data(session_id, 'preferences', {'theme': 'dark'})
        
        # Retrieve data
        user_name = session_memory.retrieve_session_data(session_id, 'user_name')
        preferences = session_memory.retrieve_session_data(session_id, 'preferences')
        
        assert user_name == 'John Doe'
        assert preferences['theme'] == 'dark'
        
        # Test non-existent data
        missing_data = session_memory.retrieve_session_data(session_id, 'non_existent')
        assert missing_data is None
    
    def test_session_isolation(self, session_memory):
        """Test that session data is properly isolated."""
        session1 = 'session_1'
        session2 = 'session_2'
        
        # Store different data in each session
        session_memory.store_session_data(session1, 'data', 'session1_data')
        session_memory.store_session_data(session2, 'data', 'session2_data')
        
        # Verify isolation
        data1 = session_memory.retrieve_session_data(session1, 'data')
        data2 = session_memory.retrieve_session_data(session2, 'data')
        
        assert data1 == 'session1_data'
        assert data2 == 'session2_data'
        assert data1 != data2
    
    def test_session_cleanup(self, session_memory):
        """Test session cleanup functionality."""
        session_id = 'cleanup_session'
        
        # Store data
        session_memory.store_session_data(session_id, 'temp_data', 'temporary')
        
        # Verify data exists
        assert session_memory.retrieve_session_data(session_id, 'temp_data') == 'temporary'
        
        # Clear session
        session_memory.clear_session(session_id)
        
        # Verify cleanup
        assert session_memory.retrieve_session_data(session_id, 'temp_data') is None
    
    @pytest.mark.benchmark
    def test_session_memory_performance(self, session_memory, benchmark):
        """Benchmark session memory performance."""
        session_id = 'performance_session'
        
        # Store substantial amount of data
        for i in range(100):
            session_memory.store_session_data(
                session_id, f'key_{i}', f'value_{i}' * 100
            )
        
        # Benchmark retrieval
        def retrieve_data():
            return session_memory.retrieve_session_data(session_id, 'key_50')
        
        result = benchmark(retrieve_data)
        assert result is not None
        
        # Verify performance threshold
        assert benchmark.stats['mean'] < TEST_CONFIG['performance_thresholds']['context_retrieval']
