"""
User Preference Learning Engine

Learns and adapts to user behavior patterns, preferences, and usage habits
to provide personalized experiences and intelligent recommendations.
"""

import time
import logging
import statistics
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import threading
import json

logger = logging.getLogger(__name__)

class PreferenceType(Enum):
    """Types of user preferences that can be learned."""
    TOOL_PREFERENCE = "tool_preference"           # Preferred tools for tasks
    INTERACTION_STYLE = "interaction_style"      # Communication preferences
    RESPONSE_FORMAT = "response_format"          # Preferred response formats
    TIMING_PREFERENCE = "timing_preference"      # Preferred interaction times
    COMPLEXITY_LEVEL = "complexity_level"        # Preferred detail level
    WORKFLOW_PATTERN = "workflow_pattern"        # Common workflow sequences
    ERROR_HANDLING = "error_handling"            # Error handling preferences
    NOTIFICATION_STYLE = "notification_style"    # Notification preferences

class ConfidenceLevel(Enum):
    """Confidence levels for learned preferences."""
    LOW = "low"           # < 0.3
    MEDIUM = "medium"     # 0.3 - 0.7
    HIGH = "high"         # 0.7 - 0.9
    VERY_HIGH = "very_high"  # > 0.9

@dataclass
class UserPreference:
    """Represents a learned user preference."""
    user_id: str
    preference_type: PreferenceType
    preference_key: str
    preference_value: Any
    confidence: float = 0.0
    
    # Learning metadata
    evidence_count: int = 0
    first_observed: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    
    # Context information
    contexts: List[Dict[str, Any]] = field(default_factory=list)
    success_rate: float = 1.0
    
    # Temporal patterns
    usage_times: List[float] = field(default_factory=list)
    usage_frequency: float = 0.0
    
    def get_confidence_level(self) -> ConfidenceLevel:
        """Get confidence level category."""
        if self.confidence < 0.3:
            return ConfidenceLevel.LOW
        elif self.confidence < 0.7:
            return ConfidenceLevel.MEDIUM
        elif self.confidence < 0.9:
            return ConfidenceLevel.HIGH
        else:
            return ConfidenceLevel.VERY_HIGH
    
    def update_confidence(self, success: bool = True, weight: float = 1.0) -> None:
        """Update confidence based on new evidence."""
        self.evidence_count += 1
        self.last_updated = time.time()
        
        # Update success rate
        if self.evidence_count == 1:
            self.success_rate = 1.0 if success else 0.0
        else:
            # Running average
            self.success_rate = (self.success_rate * (self.evidence_count - 1) + (1.0 if success else 0.0)) / self.evidence_count
        
        # Update confidence using evidence count and success rate
        evidence_factor = min(self.evidence_count / 10.0, 1.0)  # Max confidence from evidence at 10 observations
        success_factor = self.success_rate
        
        self.confidence = (evidence_factor * success_factor * weight)
        self.confidence = min(self.confidence, 1.0)  # Cap at 1.0

@dataclass
class UserProfile:
    """Complete user profile with all learned preferences."""
    user_id: str
    preferences: Dict[str, UserPreference] = field(default_factory=dict)
    interaction_count: int = 0
    first_interaction: float = field(default_factory=time.time)
    last_interaction: float = field(default_factory=time.time)
    
    # Behavioral patterns
    common_tasks: List[str] = field(default_factory=list)
    preferred_times: List[int] = field(default_factory=list)  # Hours of day
    session_patterns: Dict[str, Any] = field(default_factory=dict)
    
    def get_preference(self, preference_type: PreferenceType, key: str) -> Optional[UserPreference]:
        """Get a specific preference."""
        pref_key = f"{preference_type.value}:{key}"
        return self.preferences.get(pref_key)
    
    def get_preferences_by_type(self, preference_type: PreferenceType) -> List[UserPreference]:
        """Get all preferences of a specific type."""
        prefix = f"{preference_type.value}:"
        return [pref for key, pref in self.preferences.items() if key.startswith(prefix)]

class UserPreferenceEngine:
    """
    Engine for learning and managing user preferences.
    
    This component observes user behavior and learns preferences
    to provide personalized experiences and recommendations.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the user preference engine.
        
        Args:
            storage_path: Optional path for preference storage
        """
        self.storage_path = storage_path
        
        # User profiles
        self._user_profiles: Dict[str, UserProfile] = {}
        
        # Learning configuration
        self.min_evidence_threshold = 3
        self.confidence_decay_rate = 0.95  # Daily decay rate
        self.max_preferences_per_type = 50
        
        # Pattern detection
        self._interaction_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._temporal_patterns: Dict[str, List[float]] = defaultdict(list)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Load existing preferences
        if self.storage_path:
            self._load_preferences()
        
        logger.info("UserPreferenceEngine initialized")
    
    def learn_preference(self, user_id: str, preference_type: PreferenceType,
                        preference_key: str, preference_value: Any,
                        confidence: float = 1.0, context: Dict[str, Any] = None,
                        success: bool = True) -> None:
        """
        Learn a user preference from observed behavior.
        
        Args:
            user_id: User identifier
            preference_type: Type of preference
            preference_key: Preference key/identifier
            preference_value: Preference value
            confidence: Initial confidence weight
            context: Optional context information
            success: Whether the preference led to success
        """
        with self._lock:
            # Ensure user profile exists
            if user_id not in self._user_profiles:
                self._user_profiles[user_id] = UserProfile(user_id=user_id)
            
            profile = self._user_profiles[user_id]
            profile.interaction_count += 1
            profile.last_interaction = time.time()
            
            # Create preference key
            pref_key = f"{preference_type.value}:{preference_key}"
            
            # Update or create preference
            if pref_key in profile.preferences:
                preference = profile.preferences[pref_key]
                preference.preference_value = preference_value
                preference.update_confidence(success, confidence)
                
                # Add context
                if context:
                    preference.contexts.append(context)
                    # Keep only recent contexts
                    if len(preference.contexts) > 10:
                        preference.contexts = preference.contexts[-10:]
                
                # Update usage times
                preference.usage_times.append(time.time())
                if len(preference.usage_times) > 100:
                    preference.usage_times = preference.usage_times[-100:]
                
            else:
                # Create new preference
                preference = UserPreference(
                    user_id=user_id,
                    preference_type=preference_type,
                    preference_key=preference_key,
                    preference_value=preference_value,
                    confidence=confidence,
                    evidence_count=1,
                    contexts=[context] if context else [],
                    success_rate=1.0 if success else 0.0,
                    usage_times=[time.time()]
                )
                
                profile.preferences[pref_key] = preference
            
            # Update behavioral patterns
            self._update_behavioral_patterns(user_id, preference_type, preference_key, context)
            
            logger.debug(f"Learned preference for {user_id}: {preference_type.value}:{preference_key}")
    
    def get_user_preferences(self, user_id: str, 
                           preference_type: Optional[PreferenceType] = None,
                           min_confidence: float = 0.0) -> List[UserPreference]:
        """
        Get user preferences, optionally filtered by type and confidence.
        
        Args:
            user_id: User identifier
            preference_type: Optional preference type filter
            min_confidence: Minimum confidence threshold
            
        Returns:
            List[UserPreference]: List of matching preferences
        """
        with self._lock:
            if user_id not in self._user_profiles:
                return []
            
            profile = self._user_profiles[user_id]
            preferences = []
            
            for preference in profile.preferences.values():
                # Filter by type if specified
                if preference_type and preference.preference_type != preference_type:
                    continue
                
                # Filter by confidence
                if preference.confidence < min_confidence:
                    continue
                
                preferences.append(preference)
            
            # Sort by confidence (descending)
            preferences.sort(key=lambda p: p.confidence, reverse=True)
            
            return preferences
    
    def get_preference_recommendation(self, user_id: str, preference_type: PreferenceType,
                                    context: Dict[str, Any] = None) -> Optional[UserPreference]:
        """
        Get the best preference recommendation for a user and context.
        
        Args:
            user_id: User identifier
            preference_type: Type of preference needed
            context: Optional context for recommendation
            
        Returns:
            Optional[UserPreference]: Best matching preference or None
        """
        preferences = self.get_user_preferences(
            user_id, preference_type, min_confidence=0.3
        )
        
        if not preferences:
            return None
        
        # If no context, return highest confidence preference
        if not context:
            return preferences[0]
        
        # Score preferences based on context similarity
        scored_preferences = []
        
        for preference in preferences:
            context_score = self._calculate_context_similarity(preference.contexts, context)
            combined_score = preference.confidence * 0.7 + context_score * 0.3
            scored_preferences.append((preference, combined_score))
        
        # Return best scoring preference
        scored_preferences.sort(key=lambda x: x[1], reverse=True)
        return scored_preferences[0][0]
    
    def predict_user_behavior(self, user_id: str, 
                            current_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Predict user behavior based on learned patterns.
        
        Args:
            user_id: User identifier
            current_context: Current context information
            
        Returns:
            Dict[str, Any]: Behavior predictions
        """
        with self._lock:
            if user_id not in self._user_profiles:
                return {"error": "User profile not found"}
            
            profile = self._user_profiles[user_id]
            predictions = {}
            
            # Predict preferred tools
            tool_preferences = self.get_user_preferences(user_id, PreferenceType.TOOL_PREFERENCE)
            if tool_preferences:
                predictions["likely_tools"] = [
                    (pref.preference_value, pref.confidence) 
                    for pref in tool_preferences[:5]
                ]
            
            # Predict interaction style
            style_preferences = self.get_user_preferences(user_id, PreferenceType.INTERACTION_STYLE)
            if style_preferences:
                predictions["interaction_style"] = style_preferences[0].preference_value
            
            # Predict preferred response format
            format_preferences = self.get_user_preferences(user_id, PreferenceType.RESPONSE_FORMAT)
            if format_preferences:
                predictions["response_format"] = format_preferences[0].preference_value
            
            # Predict timing patterns
            current_hour = time.localtime().tm_hour
            if profile.preferred_times:
                time_score = self._calculate_time_preference_score(current_hour, profile.preferred_times)
                predictions["time_preference_score"] = time_score
            
            # Predict workflow patterns
            workflow_preferences = self.get_user_preferences(user_id, PreferenceType.WORKFLOW_PATTERN)
            if workflow_preferences:
                predictions["likely_workflows"] = [
                    pref.preference_value for pref in workflow_preferences[:3]
                ]
            
            return predictions
    
    def adapt_to_feedback(self, user_id: str, preference_type: PreferenceType,
                         preference_key: str, feedback_score: float,
                         context: Dict[str, Any] = None) -> None:
        """
        Adapt preferences based on user feedback.
        
        Args:
            user_id: User identifier
            preference_type: Type of preference
            preference_key: Preference key
            feedback_score: Feedback score (0.0 to 1.0)
            context: Optional context information
        """
        with self._lock:
            if user_id not in self._user_profiles:
                return
            
            profile = self._user_profiles[user_id]
            pref_key = f"{preference_type.value}:{preference_key}"
            
            if pref_key in profile.preferences:
                preference = profile.preferences[pref_key]
                
                # Update confidence based on feedback
                success = feedback_score > 0.5
                weight = abs(feedback_score - 0.5) * 2  # Convert to 0-1 weight
                
                preference.update_confidence(success, weight)
                
                # Add feedback context
                if context:
                    feedback_context = {**context, "feedback_score": feedback_score}
                    preference.contexts.append(feedback_context)
                
                logger.debug(f"Adapted preference {pref_key} based on feedback: {feedback_score}")
    
    def get_user_profile_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get a summary of a user's profile and preferences.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict[str, Any]: Profile summary
        """
        with self._lock:
            if user_id not in self._user_profiles:
                return {"error": "User profile not found"}
            
            profile = self._user_profiles[user_id]
            
            # Count preferences by type
            preference_counts = defaultdict(int)
            high_confidence_prefs = 0
            
            for preference in profile.preferences.values():
                preference_counts[preference.preference_type.value] += 1
                if preference.confidence > 0.7:
                    high_confidence_prefs += 1
            
            # Calculate profile maturity
            days_active = (profile.last_interaction - profile.first_interaction) / (24 * 3600)
            maturity_score = min(days_active / 30.0, 1.0)  # Mature after 30 days
            
            return {
                "user_id": user_id,
                "interaction_count": profile.interaction_count,
                "days_active": days_active,
                "maturity_score": maturity_score,
                "total_preferences": len(profile.preferences),
                "high_confidence_preferences": high_confidence_prefs,
                "preference_counts": dict(preference_counts),
                "common_tasks": profile.common_tasks[:10],
                "preferred_times": profile.preferred_times
            }
    
    def decay_preferences(self, user_id: str) -> None:
        """
        Apply time-based decay to user preferences.
        
        Args:
            user_id: User identifier
        """
        with self._lock:
            if user_id not in self._user_profiles:
                return
            
            profile = self._user_profiles[user_id]
            current_time = time.time()
            
            for preference in profile.preferences.values():
                # Calculate days since last update
                days_since_update = (current_time - preference.last_updated) / (24 * 3600)
                
                # Apply exponential decay
                decay_factor = self.confidence_decay_rate ** days_since_update
                preference.confidence *= decay_factor
                
                # Remove very low confidence preferences
                if preference.confidence < 0.1:
                    # Mark for removal (will be cleaned up separately)
                    preference.confidence = 0.0
    
    def cleanup_low_confidence_preferences(self, user_id: str) -> int:
        """
        Remove low confidence preferences for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            int: Number of preferences removed
        """
        with self._lock:
            if user_id not in self._user_profiles:
                return 0
            
            profile = self._user_profiles[user_id]
            
            # Find preferences to remove
            to_remove = [
                key for key, pref in profile.preferences.items()
                if pref.confidence < 0.1
            ]
            
            # Remove them
            for key in to_remove:
                del profile.preferences[key]
            
            logger.debug(f"Cleaned up {len(to_remove)} low confidence preferences for {user_id}")
            return len(to_remove)
    
    def export_preferences_data(self) -> Dict[str, Any]:
        """Export preferences data for persistence."""
        with self._lock:
            return {
                "user_profiles": {
                    user_id: {
                        "user_id": profile.user_id,
                        "interaction_count": profile.interaction_count,
                        "first_interaction": profile.first_interaction,
                        "last_interaction": profile.last_interaction,
                        "common_tasks": profile.common_tasks,
                        "preferred_times": profile.preferred_times,
                        "session_patterns": profile.session_patterns,
                        "preferences": {
                            key: {
                                **pref.__dict__,
                                "preference_type": pref.preference_type.value
                            }
                            for key, pref in profile.preferences.items()
                        }
                    }
                    for user_id, profile in self._user_profiles.items()
                }
            }
    
    def load_preferences_data(self, data: Dict[str, Any]) -> None:
        """Load preferences data from persistence."""
        with self._lock:
            self._user_profiles.clear()
            
            for user_id, profile_data in data.get("user_profiles", {}).items():
                # Create profile
                profile = UserProfile(
                    user_id=profile_data["user_id"],
                    interaction_count=profile_data.get("interaction_count", 0),
                    first_interaction=profile_data.get("first_interaction", time.time()),
                    last_interaction=profile_data.get("last_interaction", time.time()),
                    common_tasks=profile_data.get("common_tasks", []),
                    preferred_times=profile_data.get("preferred_times", []),
                    session_patterns=profile_data.get("session_patterns", {})
                )
                
                # Load preferences
                for key, pref_data in profile_data.get("preferences", {}).items():
                    pref_data["preference_type"] = PreferenceType(pref_data["preference_type"])
                    preference = UserPreference(**pref_data)
                    profile.preferences[key] = preference
                
                self._user_profiles[user_id] = profile
            
            logger.info(f"Loaded preferences for {len(self._user_profiles)} users")
    
    def _update_behavioral_patterns(self, user_id: str, preference_type: PreferenceType,
                                  preference_key: str, context: Dict[str, Any] = None) -> None:
        """Update behavioral patterns based on new preference data."""
        profile = self._user_profiles[user_id]
        
        # Update common tasks
        if preference_type == PreferenceType.TOOL_PREFERENCE:
            if preference_key not in profile.common_tasks:
                profile.common_tasks.append(preference_key)
            # Keep only top 20 tasks
            if len(profile.common_tasks) > 20:
                profile.common_tasks = profile.common_tasks[-20:]
        
        # Update preferred times
        current_hour = time.localtime().tm_hour
        profile.preferred_times.append(current_hour)
        if len(profile.preferred_times) > 100:
            profile.preferred_times = profile.preferred_times[-100:]
    
    def _calculate_context_similarity(self, stored_contexts: List[Dict[str, Any]], 
                                    current_context: Dict[str, Any]) -> float:
        """Calculate similarity between stored contexts and current context."""
        if not stored_contexts:
            return 0.0
        
        similarities = []
        
        for stored_context in stored_contexts[-5:]:  # Check last 5 contexts
            similarity = 0.0
            total_keys = set(stored_context.keys()) | set(current_context.keys())
            
            if not total_keys:
                continue
            
            matching_keys = 0
            for key in total_keys:
                if key in stored_context and key in current_context:
                    if stored_context[key] == current_context[key]:
                        matching_keys += 1
            
            similarity = matching_keys / len(total_keys)
            similarities.append(similarity)
        
        return statistics.mean(similarities) if similarities else 0.0
    
    def _calculate_time_preference_score(self, current_hour: int, preferred_times: List[int]) -> float:
        """Calculate how well current time matches user's preferred times."""
        if not preferred_times:
            return 0.5  # Neutral score
        
        # Count occurrences of each hour
        hour_counts = Counter(preferred_times)
        total_interactions = len(preferred_times)
        
        # Get preference score for current hour
        current_hour_count = hour_counts.get(current_hour, 0)
        preference_score = current_hour_count / total_interactions
        
        return preference_score
    
    def _save_preferences(self) -> None:
        """Save preferences to storage."""
        if not self.storage_path:
            return
        
        try:
            data = self.export_preferences_data()
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug("Saved user preferences to storage")
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
    
    def _load_preferences(self) -> None:
        """Load preferences from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            self.load_preferences_data(data)
            logger.debug("Loaded user preferences from storage")
        except FileNotFoundError:
            logger.debug("No existing preferences file found")
        except Exception as e:
            logger.error(f"Failed to load preferences: {e}")
