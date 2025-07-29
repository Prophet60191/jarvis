# Fast/Slow Path Routing Integration Guide

## Overview
The fast/slow path routing system has been implemented to fix the timeout issues
with simple queries like "What time is it?".

## Integration Steps

### 1. Test the System
```bash
python enable_fast_path_routing.py
```

### 2. Enable in Main Application
Replace the ConversationManager with SmartConversationManager:

```python
# In your main Jarvis startup code:
from jarvis.jarvis.core.routing import SmartConversationManager

# Replace:
# conversation_manager = ConversationManager(config, tts_manager, stt_manager)

# With:
conversation_manager = SmartConversationManager(config, tts_manager, stt_manager)
```

### 3. Monitor Performance
```python
# Get routing statistics
stats = conversation_manager.get_routing_stats()
print(json.dumps(stats, indent=2))
```

## Performance Targets
- **Instant Path**: <200ms (for simple queries like time, weather)
- **Adaptive Path**: <2s (for moderate complexity queries)
- **Complex Path**: <30s (for complex operations)

## Expected Improvements
- "What time is it?" goes from 30s timeout to <200ms response
- Simple queries use fast path (no LLM overhead)
- Complex queries still get full orchestration
- Automatic fallback to original system if routing fails

## Configuration Options
```python
# Enable/disable fast path routing
conversation_manager.enable_fast_path_routing(True)

# Enable/disable performance logging
conversation_manager.enable_performance_logging(True)

# Enable/disable fallback to original system
conversation_manager.enable_fallback(True)
```
