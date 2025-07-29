# System Integration Points - Jarvis Architecture Enhancement

## Overview

This document defines how the new System Integration & Source Code Consciousness components will integrate with the existing Jarvis architecture while maintaining backward compatibility and zero-disruption deployment.

## Current Architecture Analysis

### Existing Core Components

**Current Flow**:
```
User Input → ConversationManager → JarvisAgent → PluginManager → Tools → Response
                ↓
            SpeechManager ← RAGService ← ToolRegistry
```

**Key Integration Points**:
1. **JarvisAgent** (`jarvis/core/agent.py`) - Main orchestration point
2. **PluginManager** (`jarvis/plugins/manager.py`) - Tool lifecycle management
3. **ToolRegistry** (`jarvis/tools/registry.py`) - Tool registration and retrieval
4. **ConversationManager** (`jarvis/core/conversation.py`) - Conversation state
5. **RAGService** (`jarvis/tools/rag_service.py`) - Memory and knowledge

## Integration Strategy

### 1. Enhanced Plugin Registry Integration

**Integration Point**: `jarvis/plugins/manager.py`

**Current Implementation**:
<augment_code_snippet path="jarvis/jarvis/plugins/manager.py" mode="EXCERPT">
````python
class PluginManager:
    def __init__(self, auto_discover: bool = True, plugin_directories: Optional[List[str]] = None):
        self.discovery = PluginDiscovery(plugin_directories)
        self._loaded_plugins: Dict[str, PluginBase] = {}
        self._plugin_tools: Dict[str, List[BaseTool]] = {}
        self._disabled_plugins: Set[str] = set()
````
</augment_code_snippet>

**Enhanced Integration**:
```python
class PluginManager:
    def __init__(self, auto_discover: bool = True, plugin_directories: Optional[List[str]] = None):
        # Existing initialization
        self.discovery = PluginDiscovery(plugin_directories)
        self._loaded_plugins: Dict[str, PluginBase] = {}
        self._plugin_tools: Dict[str, List[BaseTool]] = {}
        self._disabled_plugins: Set[str] = set()
        
        # NEW: Enhanced registry integration
        self.unified_registry = UnifiedPluginRegistry()
        self.relationship_mapper = RelationshipMapper()
        self.capability_analyzer = CapabilityAnalyzer()
        self.usage_analytics = UsageAnalytics()
```

**Integration Method**: Composition over inheritance
- Add new components as attributes
- Extend existing methods with enhanced functionality
- Maintain all existing public APIs
- Add new optional parameters with defaults

### 2. Context Management Integration

**Integration Point**: `jarvis/core/conversation.py`

**Current Implementation**:
<augment_code_snippet path="jarvis/jarvis/core/conversation.py" mode="EXCERPT">
````python
def __init__(self, config: ConversationConfig, speech_manager: SpeechManager, agent: JarvisAgent, mcp_client=None):
    self.config = config
    self.speech_manager = speech_manager
    self.agent = agent
    self.mcp_client = mcp_client
    
    self.state = ConversationState.IDLE
    self.last_activity_time = time.time()
    self.conversation_active = False
````
</augment_code_snippet>

**Enhanced Integration**:
```python
def __init__(self, config: ConversationConfig, speech_manager: SpeechManager, 
             agent: JarvisAgent, mcp_client=None, enable_enhanced_context=True):
    # Existing initialization
    self.config = config
    self.speech_manager = speech_manager
    self.agent = agent
    self.mcp_client = mcp_client
    
    self.state = ConversationState.IDLE
    self.last_activity_time = time.time()
    self.conversation_active = False
    
    # NEW: Enhanced context management (optional)
    if enable_enhanced_context:
        self.context_manager = ContextManager()
        self.enhanced_state_tracking = True
    else:
        self.context_manager = None
        self.enhanced_state_tracking = False
```

**Integration Hooks**:
- Hook into existing conversation lifecycle methods
- Extend state change notifications
- Add context updates to existing flows
- Maintain backward compatibility with feature flags

### 3. Agent Orchestration Integration

**Integration Point**: `jarvis/core/agent.py`

**Current Tool Execution Flow**:
<augment_code_snippet path="jarvis/jarvis/core/agent.py" mode="EXCERPT">
````python
async def process_input(self, user_input: str, fresh_agent_executor=None, fresh_llm=None) -> str:
    logger.info(f"🔍 AGENT DEBUG: Processing input: '{user_input}'")

    if fresh_agent_executor:
        logger.info(f"🔍 AGENT DEBUG: Using fresh agent executor with {len(self.tools)} tools")
        response = await fresh_agent_executor.ainvoke({"input": user_input})
        output = response.get("output", "I'm sorry, I couldn't process that request.")
````
</augment_code_snippet>

**Enhanced Integration**:
```python
async def process_input(self, user_input: str, fresh_agent_executor=None, 
                       fresh_llm=None, enable_orchestration=True) -> str:
    logger.info(f"🔍 AGENT DEBUG: Processing input: '{user_input}'")
    
    # NEW: Orchestration layer (optional)
    if enable_orchestration and hasattr(self, 'orchestrator'):
        context = self.context_manager.get_current_context() if hasattr(self, 'context_manager') else None
        orchestration_plan = self.orchestrator.should_orchestrate(user_input, context)
        
        if orchestration_plan:
            logger.info(f"🎭 ORCHESTRATION: Using orchestrated execution")
            return await self.orchestrator.execute_plan(orchestration_plan)
    
    # Existing execution path (unchanged)
    if fresh_agent_executor:
        logger.info(f"🔍 AGENT DEBUG: Using fresh agent executor with {len(self.tools)} tools")
        response = await fresh_agent_executor.ainvoke({"input": user_input})
        output = response.get("output", "I'm sorry, I couldn't process that request.")
```

### 4. RAG System Integration

**Integration Point**: `jarvis/tools/rag_service.py`

**Current RAG Architecture**:
<augment_code_snippet path="jarvis/jarvis/tools/rag_service.py" mode="EXCERPT">
````python
class RAGService:
    def __init__(self, config):
        self.config = config
        self.document_llm = ChatOllama(model=config.rag.document_llm_model)
        self.embeddings = OllamaEmbeddings(model=config.llm.model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.rag.chunk_size,
            chunk_overlap=config.rag.chunk_overlap
        )
````
</augment_code_snippet>

**Enhanced Integration**:
```python
class RAGService:
    def __init__(self, config, enable_code_consciousness=True):
        # Existing initialization
        self.config = config
        self.document_llm = ChatOllama(model=config.rag.document_llm_model)
        self.embeddings = OllamaEmbeddings(model=config.llm.model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.rag.chunk_size,
            chunk_overlap=config.rag.chunk_overlap
        )
        
        # NEW: Code consciousness integration (optional)
        if enable_code_consciousness:
            self.codebase_rag = CodebaseRAG(config)
            self.semantic_code_index = SemanticCodeIndex()
            self.code_consciousness_enabled = True
        else:
            self.code_consciousness_enabled = False
```

## Integration Patterns

### 1. Decorator Pattern for Enhanced Functionality

**Tool Execution Enhancement**:
```python
def enhanced_tool_execution(original_method):
    """Decorator to add orchestration and analytics to tool execution."""
    @wraps(original_method)
    async def wrapper(self, *args, **kwargs):
        # Pre-execution: analytics and orchestration
        if hasattr(self, 'unified_registry'):
            self.unified_registry.track_tool_start(self.name)
        
        # Execute original method
        result = await original_method(self, *args, **kwargs)
        
        # Post-execution: analytics and learning
        if hasattr(self, 'unified_registry'):
            self.unified_registry.track_tool_completion(self.name, result)
        
        return result
    return wrapper
```

### 2. Observer Pattern for Event Integration

**Plugin Lifecycle Events**:
```python
class PluginLifecycleObserver:
    def on_plugin_loaded(self, plugin_name: str, plugin_instance: PluginBase):
        """Called when a plugin is successfully loaded."""
        if hasattr(self, 'unified_registry'):
            self.unified_registry.analyze_plugin_capabilities(plugin_name, plugin_instance)
    
    def on_plugin_unloaded(self, plugin_name: str):
        """Called when a plugin is unloaded."""
        if hasattr(self, 'unified_registry'):
            self.unified_registry.remove_plugin_relationships(plugin_name)
```

### 3. Adapter Pattern for Legacy Compatibility

**Legacy Tool Adapter**:
```python
class LegacyToolAdapter:
    """Adapter to make legacy tools work with enhanced registry."""
    
    def __init__(self, legacy_tool: BaseTool):
        self.legacy_tool = legacy_tool
        self.enhanced_metadata = self._generate_metadata()
    
    def _generate_metadata(self) -> EnhancedPluginMetadata:
        """Generate enhanced metadata from legacy tool."""
        return EnhancedPluginMetadata(
            name=self.legacy_tool.name,
            capabilities=self._infer_capabilities(),
            performance_profile=PerformanceProfile(),
            # ... other fields with defaults
        )
```

## Configuration Integration

### Enhanced Configuration Schema

**Extending Existing Config**:
```python
@dataclass
class EnhancedJarvisConfig(JarvisConfig):
    # Existing configuration fields remain unchanged
    
    # NEW: Enhanced system configuration
    orchestration: OrchestrationConfig = field(default_factory=OrchestrationConfig)
    context_management: ContextConfig = field(default_factory=ContextConfig)
    code_consciousness: CodeConsciousnessConfig = field(default_factory=CodeConsciousnessConfig)
    enhanced_registry: RegistryConfig = field(default_factory=RegistryConfig)

@dataclass
class OrchestrationConfig:
    enabled: bool = True
    max_chain_length: int = 5
    orchestration_timeout: float = 30.0
    learning_enabled: bool = True
    
@dataclass
class ContextConfig:
    enabled: bool = True
    session_timeout: int = 3600
    max_context_size: int = 10000
    preference_learning: bool = True
```

### Feature Flag Integration

**Gradual Feature Rollout**:
```python
class FeatureFlags:
    def __init__(self, config: JarvisConfig):
        self.config = config
        
    def is_orchestration_enabled(self) -> bool:
        return getattr(self.config, 'orchestration', {}).get('enabled', False)
    
    def is_context_management_enabled(self) -> bool:
        return getattr(self.config, 'context_management', {}).get('enabled', False)
    
    def is_code_consciousness_enabled(self) -> bool:
        return getattr(self.config, 'code_consciousness', {}).get('enabled', False)
```

## Database Integration

### Schema Extensions

**Extending Existing ChromaDB**:
```python
class EnhancedRAGMemoryManager(RAGMemoryManager):
    def __init__(self, config):
        super().__init__(config)
        
        # NEW: Additional collections for enhanced features
        self.plugin_metadata_collection = self._create_collection("plugin_metadata")
        self.context_collection = self._create_collection("conversation_contexts")
        self.code_collection = self._create_collection("codebase_index")
    
    def _create_collection(self, name: str):
        """Create a new ChromaDB collection if it doesn't exist."""
        try:
            return self.vector_store._client.get_collection(name)
        except:
            return self.vector_store._client.create_collection(name)
```

### Migration Strategy

**Database Migration**:
```python
class DatabaseMigration:
    def __init__(self, rag_manager: RAGMemoryManager):
        self.rag_manager = rag_manager
    
    def migrate_to_enhanced_schema(self):
        """Migrate existing data to enhanced schema."""
        # 1. Create new collections
        self._create_enhanced_collections()
        
        # 2. Migrate existing plugin data
        self._migrate_plugin_metadata()
        
        # 3. Initialize relationship data
        self._initialize_relationships()
        
        # 4. Verify migration
        self._verify_migration()
```

## API Integration Points

### REST API Extensions

**Enhanced Plugin Management API**:
```python
# Extend existing plugin management endpoints
@app.route('/api/plugins/<plugin_name>/metadata', methods=['GET'])
def get_enhanced_plugin_metadata(plugin_name: str):
    """Get enhanced metadata for a plugin."""
    registry = get_unified_registry()
    metadata = registry.get_plugin_metadata(plugin_name)
    return jsonify(metadata.to_dict())

@app.route('/api/plugins/<plugin_name>/relationships', methods=['GET'])
def get_plugin_relationships(plugin_name: str):
    """Get relationships for a plugin."""
    registry = get_unified_registry()
    relationships = registry.get_related_plugins(plugin_name)
    return jsonify(relationships)
```

### WebSocket Integration

**Real-time Updates**:
```python
class EnhancedWebSocketHandler:
    def __init__(self, websocket):
        self.websocket = websocket
        self.orchestrator = SystemOrchestrator()
    
    async def handle_orchestrated_request(self, message):
        """Handle request with orchestration updates."""
        # Send orchestration plan
        plan = self.orchestrator.create_plan(message['input'])
        await self.websocket.send(json.dumps({
            'type': 'orchestration_plan',
            'plan': plan.to_dict()
        }))
        
        # Execute with progress updates
        async for update in self.orchestrator.execute_with_updates(plan):
            await self.websocket.send(json.dumps({
                'type': 'execution_update',
                'update': update
            }))
```

## Testing Integration

### Test Infrastructure Extensions

**Enhanced Test Base Classes**:
```python
class EnhancedJarvisTestCase(unittest.TestCase):
    def setUp(self):
        # Standard test setup
        self.config = get_test_config()
        self.agent = JarvisAgent(self.config.llm)
        
        # Enhanced test setup
        self.unified_registry = UnifiedPluginRegistry()
        self.context_manager = ContextManager()
        self.orchestrator = SystemOrchestrator()
    
    def assert_orchestration_plan(self, plan: OrchestrationPlan, expected_tools: List[str]):
        """Assert that orchestration plan contains expected tools."""
        actual_tools = [step.tool_name for step in plan.tool_chain]
        self.assertEqual(actual_tools, expected_tools)
```

### Integration Test Scenarios

**End-to-End Integration Tests**:
```python
class TestSystemIntegration(EnhancedJarvisTestCase):
    def test_enhanced_plugin_loading(self):
        """Test that plugins load with enhanced metadata."""
        # Load a test plugin
        plugin_manager = EnhancedPluginManager()
        success = plugin_manager.load_plugin("test_plugin", TestPlugin)
        
        # Verify enhanced metadata was created
        metadata = plugin_manager.unified_registry.get_plugin_metadata("test_plugin")
        self.assertIsNotNone(metadata)
        self.assertGreater(len(metadata.capabilities), 0)
    
    def test_context_aware_orchestration(self):
        """Test that orchestration uses context for tool selection."""
        # Set up context
        context = Context(conversation_context=ConversationContext(current_topic="file_operations"))
        
        # Request orchestration
        plan = self.orchestrator.orchestrate_request("list my files", context)
        
        # Verify file-related tools were selected
        tool_names = [step.tool_name for step in plan.tool_chain]
        self.assertIn("list_files", tool_names)
```

## Monitoring Integration

### Metrics Collection

**Enhanced Metrics**:
```python
class EnhancedMetricsCollector:
    def __init__(self):
        self.orchestration_metrics = OrchestrationMetrics()
        self.context_metrics = ContextMetrics()
        self.consciousness_metrics = ConsciousnessMetrics()
    
    def collect_orchestration_metrics(self, plan: OrchestrationPlan, result: ExecutionResult):
        """Collect metrics from orchestration execution."""
        self.orchestration_metrics.record_execution(
            plan_complexity=len(plan.tool_chain),
            execution_time=result.execution_time,
            success_rate=result.success,
            tool_chain=plan.tool_chain
        )
```

### Health Checks

**System Health Monitoring**:
```python
class EnhancedHealthChecker:
    def __init__(self, jarvis_app):
        self.jarvis_app = jarvis_app
    
    def check_enhanced_systems(self) -> Dict[str, bool]:
        """Check health of enhanced systems."""
        return {
            'unified_registry': self._check_registry_health(),
            'context_manager': self._check_context_health(),
            'orchestrator': self._check_orchestration_health(),
            'code_consciousness': self._check_consciousness_health()
        }
```

## Deployment Integration

### Gradual Rollout Strategy

**Feature Flag Deployment**:
```python
class DeploymentManager:
    def __init__(self):
        self.feature_flags = FeatureFlags()
    
    def deploy_phase_1(self):
        """Deploy enhanced plugin registry."""
        self.feature_flags.enable('enhanced_registry')
        self._verify_deployment('enhanced_registry')
    
    def deploy_phase_2(self):
        """Deploy context management."""
        if self._is_phase_1_stable():
            self.feature_flags.enable('context_management')
            self._verify_deployment('context_management')
    
    def rollback_if_needed(self):
        """Rollback if performance degrades."""
        if self._performance_degraded():
            self.feature_flags.disable_all_enhanced_features()
            self._verify_rollback()
```

This integration design ensures that all new functionality can be added incrementally without disrupting the existing system, while providing clear upgrade paths and rollback mechanisms.
