"""
Context-Aware Tool Selection

Implements intelligent tool selection based on conversation context,
user preferences, and historical usage patterns.
"""

import time
import logging
import statistics
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import threading

logger = logging.getLogger(__name__)

class SelectionStrategy(Enum):
    """Strategies for tool selection."""
    CONTEXT_BASED = "context_based"        # Based on conversation context
    PREFERENCE_BASED = "preference_based"  # Based on user preferences
    PERFORMANCE_BASED = "performance_based"  # Based on tool performance
    HYBRID = "hybrid"                      # Combination of strategies
    LEARNING_BASED = "learning_based"      # Based on learned patterns

class ContextWeight(Enum):
    """Weight levels for context factors."""
    LOW = 0.2
    MEDIUM = 0.5
    HIGH = 0.8
    CRITICAL = 1.0

@dataclass
class SelectionCriteria:
    """Criteria for tool selection."""
    required_capabilities: Set[str] = field(default_factory=set)
    preferred_tools: List[str] = field(default_factory=list)
    excluded_tools: List[str] = field(default_factory=list)
    
    # Context factors
    conversation_topic: Optional[str] = None
    user_intent: Optional[str] = None
    current_phase: Optional[str] = None
    
    # Performance requirements
    max_execution_time: Optional[float] = None
    min_success_rate: Optional[float] = None
    
    # User preferences
    user_id: Optional[str] = None
    preferred_interaction_style: Optional[str] = None
    
    # Constraints
    resource_constraints: Dict[str, Any] = field(default_factory=dict)
    time_constraints: Optional[float] = None

@dataclass
class ToolScore:
    """Score for a tool selection candidate."""
    tool_name: str
    total_score: float = 0.0
    
    # Component scores
    context_score: float = 0.0
    preference_score: float = 0.0
    performance_score: float = 0.0
    capability_score: float = 0.0
    
    # Metadata
    reasoning: List[str] = field(default_factory=list)
    confidence: float = 0.0
    
    def add_reasoning(self, reason: str) -> None:
        """Add reasoning for the score."""
        self.reasoning.append(reason)
    
    def calculate_total_score(self, weights: Dict[str, float] = None) -> None:
        """Calculate total score from component scores."""
        if weights is None:
            weights = {
                "context": 0.3,
                "preference": 0.2,
                "performance": 0.3,
                "capability": 0.2
            }
        
        self.total_score = (
            self.context_score * weights.get("context", 0.3) +
            self.preference_score * weights.get("preference", 0.2) +
            self.performance_score * weights.get("performance", 0.3) +
            self.capability_score * weights.get("capability", 0.2)
        )
        
        # Calculate confidence based on score distribution
        scores = [self.context_score, self.preference_score, 
                 self.performance_score, self.capability_score]
        non_zero_scores = [s for s in scores if s > 0]
        
        if non_zero_scores:
            self.confidence = min(statistics.mean(non_zero_scores), 1.0)
        else:
            self.confidence = 0.0

class ContextAwareSelector:
    """
    Context-aware tool selection system.
    
    This component intelligently selects tools based on conversation context,
    user preferences, historical performance, and learned patterns.
    """
    
    def __init__(self, plugin_manager: Any = None, context_manager: Any = None):
        """
        Initialize the context-aware selector.
        
        Args:
            plugin_manager: Plugin manager for tool access
            context_manager: Context manager for context access
        """
        self.plugin_manager = plugin_manager
        self.context_manager = context_manager
        
        # Selection history and learning
        self._selection_history: List[Dict[str, Any]] = []
        self._context_patterns: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._tool_performance: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Context analysis
        self._topic_tool_mapping: Dict[str, List[str]] = defaultdict(list)
        self._intent_tool_mapping: Dict[str, List[str]] = defaultdict(list)
        self._user_tool_preferences: Dict[str, Dict[str, float]] = defaultdict(dict)
        
        # Configuration
        self.default_strategy = SelectionStrategy.HYBRID
        self.learning_rate = 0.1
        self.min_confidence_threshold = 0.3
        self.max_candidates = 10
        
        # Scoring weights
        self.scoring_weights = {
            "context": 0.3,
            "preference": 0.2,
            "performance": 0.3,
            "capability": 0.2
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        logger.info("ContextAwareSelector initialized")
    
    def select_tools(self, criteria: SelectionCriteria,
                    strategy: SelectionStrategy = None,
                    max_tools: int = 5) -> List[ToolScore]:
        """
        Select tools based on criteria and strategy.
        
        Args:
            criteria: Selection criteria
            strategy: Selection strategy to use
            max_tools: Maximum number of tools to select
            
        Returns:
            List[ToolScore]: Ranked list of tool scores
        """
        strategy = strategy or self.default_strategy
        
        with self._lock:
            # Get candidate tools
            candidates = self._get_candidate_tools(criteria)
            
            if not candidates:
                logger.warning("No candidate tools found for criteria")
                return []
            
            # Score candidates based on strategy
            scored_tools = []
            
            for tool_name in candidates:
                score = self._score_tool(tool_name, criteria, strategy)
                if score.total_score >= self.min_confidence_threshold:
                    scored_tools.append(score)
            
            # Sort by total score
            scored_tools.sort(key=lambda s: s.total_score, reverse=True)
            
            # Record selection for learning
            self._record_selection(criteria, scored_tools[:max_tools], strategy)
            
            logger.debug(f"Selected {len(scored_tools[:max_tools])} tools using {strategy.value} strategy")
            
            return scored_tools[:max_tools]
    
    def learn_from_execution(self, tool_name: str, criteria: SelectionCriteria,
                           execution_result: Dict[str, Any]) -> None:
        """
        Learn from tool execution results.
        
        Args:
            tool_name: Name of the executed tool
            criteria: Selection criteria used
            execution_result: Execution results
        """
        with self._lock:
            success = execution_result.get("success", False)
            execution_time = execution_result.get("execution_time", 0.0)
            user_rating = execution_result.get("user_rating", 0.0)
            
            # Update performance data
            if tool_name not in self._tool_performance:
                self._tool_performance[tool_name] = {
                    "success_rate": 0.0,
                    "avg_execution_time": 0.0,
                    "user_satisfaction": 0.0,
                    "usage_count": 0
                }
            
            perf = self._tool_performance[tool_name]
            count = perf["usage_count"]
            
            # Update running averages
            perf["success_rate"] = (perf["success_rate"] * count + (1.0 if success else 0.0)) / (count + 1)
            perf["avg_execution_time"] = (perf["avg_execution_time"] * count + execution_time) / (count + 1)
            
            if user_rating > 0:
                perf["user_satisfaction"] = (perf["user_satisfaction"] * count + user_rating) / (count + 1)
            
            perf["usage_count"] = count + 1
            
            # Update context patterns
            if criteria.conversation_topic:
                self._update_context_pattern(criteria.conversation_topic, tool_name, success)
            
            if criteria.user_intent:
                self._update_context_pattern(criteria.user_intent, tool_name, success)
            
            # Update user preferences
            if criteria.user_id:
                self._update_user_preference(criteria.user_id, tool_name, success, user_rating)
            
            logger.debug(f"Learned from execution: {tool_name} (success={success})")
    
    def get_tool_recommendations(self, context: Dict[str, Any],
                               user_id: Optional[str] = None,
                               limit: int = 5) -> List[str]:
        """
        Get tool recommendations based on context.
        
        Args:
            context: Current context information
            user_id: Optional user identifier
            limit: Maximum recommendations
            
        Returns:
            List[str]: Recommended tool names
        """
        # Create criteria from context
        criteria = SelectionCriteria(
            conversation_topic=context.get("topic"),
            user_intent=context.get("intent"),
            current_phase=context.get("phase"),
            user_id=user_id
        )
        
        # Get tool scores
        tool_scores = self.select_tools(criteria, max_tools=limit)
        
        # Return tool names
        return [score.tool_name for score in tool_scores]
    
    def analyze_selection_patterns(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze tool selection patterns.
        
        Args:
            user_id: Optional user identifier for user-specific analysis
            
        Returns:
            Dict[str, Any]: Selection pattern analysis
        """
        with self._lock:
            analysis = {
                "total_selections": len(self._selection_history),
                "most_common_tools": [],
                "context_patterns": {},
                "performance_summary": {}
            }
            
            # Filter by user if specified
            history = self._selection_history
            if user_id:
                history = [h for h in history if h.get("user_id") == user_id]
            
            if not history:
                return analysis
            
            # Analyze most common tools
            tool_counts = Counter()
            for selection in history:
                for tool_score in selection.get("selected_tools", []):
                    tool_counts[tool_score.tool_name] += 1
            
            analysis["most_common_tools"] = tool_counts.most_common(10)
            
            # Analyze context patterns
            topic_tools = defaultdict(Counter)
            intent_tools = defaultdict(Counter)
            
            for selection in history:
                criteria = selection.get("criteria", {})
                topic = criteria.get("conversation_topic")
                intent = criteria.get("user_intent")
                
                for tool_score in selection.get("selected_tools", []):
                    if topic:
                        topic_tools[topic][tool_score.tool_name] += 1
                    if intent:
                        intent_tools[intent][tool_score.tool_name] += 1
            
            analysis["context_patterns"] = {
                "topic_tools": {topic: dict(tools.most_common(5)) for topic, tools in topic_tools.items()},
                "intent_tools": {intent: dict(tools.most_common(5)) for intent, tools in intent_tools.items()}
            }
            
            # Performance summary
            if self._tool_performance:
                avg_success_rate = statistics.mean(
                    perf["success_rate"] for perf in self._tool_performance.values()
                )
                avg_execution_time = statistics.mean(
                    perf["avg_execution_time"] for perf in self._tool_performance.values()
                )
                
                analysis["performance_summary"] = {
                    "average_success_rate": avg_success_rate,
                    "average_execution_time": avg_execution_time,
                    "total_tools_tracked": len(self._tool_performance)
                }
            
            return analysis
    
    def get_selector_statistics(self) -> Dict[str, Any]:
        """
        Get selector statistics.
        
        Returns:
            Dict[str, Any]: Selector statistics
        """
        with self._lock:
            return {
                "selection_history_size": len(self._selection_history),
                "tracked_tools": len(self._tool_performance),
                "context_patterns": len(self._context_patterns),
                "user_preferences": len(self._user_tool_preferences),
                "default_strategy": self.default_strategy.value,
                "min_confidence_threshold": self.min_confidence_threshold,
                "scoring_weights": self.scoring_weights.copy()
            }
    
    def _get_candidate_tools(self, criteria: SelectionCriteria) -> List[str]:
        """Get candidate tools based on criteria."""
        candidates = set()
        
        # Get tools by capabilities
        if criteria.required_capabilities and self.plugin_manager:
            for capability in criteria.required_capabilities:
                if hasattr(self.plugin_manager, 'find_plugins_by_capability'):
                    plugins = self.plugin_manager.find_plugins_by_capability(capability)
                    for plugin_name in plugins:
                        tools = self.plugin_manager.get_plugin_tools(plugin_name)
                        candidates.update(tool.name for tool in tools)
        
        # Add preferred tools
        candidates.update(criteria.preferred_tools)
        
        # Remove excluded tools
        candidates -= set(criteria.excluded_tools)
        
        # If no candidates from capabilities, get all available tools
        if not candidates and self.plugin_manager:
            all_plugins = self.plugin_manager.get_loaded_plugins()
            for plugin_name in all_plugins:
                tools = self.plugin_manager.get_plugin_tools(plugin_name)
                candidates.update(tool.name for tool in tools)
        
        return list(candidates)[:self.max_candidates]
    
    def _score_tool(self, tool_name: str, criteria: SelectionCriteria,
                   strategy: SelectionStrategy) -> ToolScore:
        """Score a tool based on criteria and strategy."""
        score = ToolScore(tool_name=tool_name)
        
        # Context scoring
        if strategy in [SelectionStrategy.CONTEXT_BASED, SelectionStrategy.HYBRID]:
            score.context_score = self._calculate_context_score(tool_name, criteria)
        
        # Preference scoring
        if strategy in [SelectionStrategy.PREFERENCE_BASED, SelectionStrategy.HYBRID]:
            score.preference_score = self._calculate_preference_score(tool_name, criteria)
        
        # Performance scoring
        if strategy in [SelectionStrategy.PERFORMANCE_BASED, SelectionStrategy.HYBRID]:
            score.performance_score = self._calculate_performance_score(tool_name, criteria)
        
        # Capability scoring
        score.capability_score = self._calculate_capability_score(tool_name, criteria)
        
        # Calculate total score
        score.calculate_total_score(self.scoring_weights)
        
        return score
    
    def _calculate_context_score(self, tool_name: str, criteria: SelectionCriteria) -> float:
        """Calculate context-based score for a tool."""
        score = 0.0
        factors = 0
        
        # Topic relevance
        if criteria.conversation_topic:
            topic_score = self._context_patterns.get(criteria.conversation_topic, {}).get(tool_name, 0.0)
            score += topic_score
            factors += 1
        
        # Intent relevance
        if criteria.user_intent:
            intent_score = self._context_patterns.get(criteria.user_intent, {}).get(tool_name, 0.0)
            score += intent_score
            factors += 1
        
        # Phase appropriateness
        if criteria.current_phase:
            phase_score = self._context_patterns.get(criteria.current_phase, {}).get(tool_name, 0.0)
            score += phase_score
            factors += 1
        
        return score / max(factors, 1)
    
    def _calculate_preference_score(self, tool_name: str, criteria: SelectionCriteria) -> float:
        """Calculate preference-based score for a tool."""
        if not criteria.user_id:
            return 0.0
        
        user_prefs = self._user_tool_preferences.get(criteria.user_id, {})
        return user_prefs.get(tool_name, 0.0)
    
    def _calculate_performance_score(self, tool_name: str, criteria: SelectionCriteria) -> float:
        """Calculate performance-based score for a tool."""
        if tool_name not in self._tool_performance:
            return 0.5  # Neutral score for unknown tools
        
        perf = self._tool_performance[tool_name]
        score = 0.0
        factors = 0
        
        # Success rate
        score += perf["success_rate"]
        factors += 1
        
        # Execution time (inverse scoring - faster is better)
        if criteria.max_execution_time and perf["avg_execution_time"] > 0:
            time_score = min(criteria.max_execution_time / perf["avg_execution_time"], 1.0)
            score += time_score
            factors += 1
        
        # User satisfaction
        if perf["user_satisfaction"] > 0:
            score += perf["user_satisfaction"] / 5.0  # Assuming 5-point scale
            factors += 1
        
        return score / max(factors, 1)
    
    def _calculate_capability_score(self, tool_name: str, criteria: SelectionCriteria) -> float:
        """Calculate capability-based score for a tool."""
        if not criteria.required_capabilities:
            return 1.0  # Full score if no specific capabilities required
        
        # This would need integration with capability analysis
        # For now, return a default score
        return 0.8
    
    def _update_context_pattern(self, context_key: str, tool_name: str, success: bool) -> None:
        """Update context pattern based on tool usage."""
        if context_key not in self._context_patterns:
            self._context_patterns[context_key] = {}
        
        current_score = self._context_patterns[context_key].get(tool_name, 0.5)
        
        # Update score based on success
        if success:
            new_score = current_score + (1.0 - current_score) * self.learning_rate
        else:
            new_score = current_score - current_score * self.learning_rate
        
        self._context_patterns[context_key][tool_name] = max(0.0, min(1.0, new_score))
    
    def _update_user_preference(self, user_id: str, tool_name: str, 
                              success: bool, user_rating: float = 0.0) -> None:
        """Update user preference based on tool usage."""
        if user_id not in self._user_tool_preferences:
            self._user_tool_preferences[user_id] = {}
        
        current_pref = self._user_tool_preferences[user_id].get(tool_name, 0.5)
        
        # Calculate preference update
        if user_rating > 0:
            # Use explicit rating
            rating_score = user_rating / 5.0  # Assuming 5-point scale
            new_pref = current_pref + (rating_score - current_pref) * self.learning_rate
        else:
            # Use success as implicit rating
            if success:
                new_pref = current_pref + (1.0 - current_pref) * self.learning_rate
            else:
                new_pref = current_pref - current_pref * self.learning_rate
        
        self._user_tool_preferences[user_id][tool_name] = max(0.0, min(1.0, new_pref))
    
    def _record_selection(self, criteria: SelectionCriteria, selected_tools: List[ToolScore],
                         strategy: SelectionStrategy) -> None:
        """Record selection for learning and analysis."""
        selection_record = {
            "timestamp": time.time(),
            "criteria": {
                "conversation_topic": criteria.conversation_topic,
                "user_intent": criteria.user_intent,
                "current_phase": criteria.current_phase,
                "user_id": criteria.user_id,
                "required_capabilities": list(criteria.required_capabilities)
            },
            "selected_tools": selected_tools,
            "strategy": strategy.value
        }
        
        self._selection_history.append(selection_record)
        
        # Maintain history size
        if len(self._selection_history) > 1000:
            self._selection_history = self._selection_history[-1000:]
