# User Profile System

The User Profile System enables Jarvis to remember and use personal information like your name, pronouns, and preferences to provide a more personalized experience.

## Overview

The User Profile System provides:

- **Name Storage**: Remember your name and preferred name
- **Pronoun Support**: Store and use your preferred pronouns
- **Privacy Controls**: Full control over what information is stored and used
- **Voice Commands**: Natural language profile management
- **Persistent Storage**: Information persists across all Jarvis sessions
- **PII Exclusion**: Names are explicitly NOT treated as sensitive PII

## Architecture

### Core Components

```
jarvis/jarvis/core/user_profile.py
├── UserProfile                  # Data structure for profile information
├── UserProfileManager          # Profile storage and management
└── Global Functions            # Convenience functions for common operations

jarvis/jarvis/tools/plugins/user_profile_tool.py
├── set_my_name()              # Voice command to set name
├── get_my_name()              # Voice command to get name
├── set_my_pronouns()          # Voice command to set pronouns
├── show_my_profile()          # Voice command to show profile
├── enable_name_usage()        # Voice command to enable name usage
├── disable_name_usage()       # Voice command to disable name usage
└── clear_my_profile()         # Voice command to clear profile
```

### Data Storage

Profile information is stored in `~/.jarvis/user_profile.json`:

```json
{
  "name": "Jose",
  "preferred_name": "Jose",
  "pronouns": null,
  "timezone": null,
  "location": null,
  "language": "en",
  "privacy_level": "standard",
  "allow_name_storage": true,
  "allow_preference_storage": true,
  "created_at": "2025-07-28T21:05:16.622258",
  "updated_at": "2025-07-28T21:07:43.061106",
  "version": "1.0"
}
```

## Voice Commands

### Setting Your Name

| Command | Action | Example Response |
|---------|--------|------------------|
| "My name is John" | Sets your name | "Perfect! I'll remember that your name is John. Nice to meet you, John!" |
| "Call me Sarah" | Sets preferred name | "Perfect! I'll remember that your name is Sarah, and I'll call you Sarah." |
| "I'm David, but call me Dave" | Sets full name and preferred name | "Perfect! I'll remember that your name is David, and I'll call you Dave. Nice to meet you, Dave!" |
| "Set my name to Jennifer" | Sets your name | "Perfect! I'll remember that your name is Jennifer." |

### Getting Your Name

| Command | Action | Example Response |
|---------|--------|------------------|
| "What's my name?" | Returns stored name | "I know you as Jose." |
| "Do you know my name?" | Returns stored name | "I know you as Jose. Your full name is Jose." |
| "What do you call me?" | Returns preferred name | "I know you as Jose." |
| "Who am I?" | Returns stored name | "I know you as Jose." |

### Setting Pronouns

| Command | Action | Example Response |
|---------|--------|------------------|
| "My pronouns are he/him" | Sets pronouns | "Got it! I'll use he/him pronouns when referring to you." |
| "Use she/her pronouns for me" | Sets pronouns | "Got it! I'll use she/her pronouns when referring to you." |
| "I use they/them pronouns" | Sets pronouns | "Got it! I'll use they/them pronouns when referring to you." |

### Profile Management

| Command | Action |
|---------|--------|
| "Show my profile" | Displays all stored profile information |
| "What do you know about me?" | Shows profile summary |
| "What information do you have stored?" | Lists stored data |
| "Clear my profile" | Removes all profile information |

### Privacy Controls

| Command | Action |
|---------|--------|
| "Allow Jarvis to use my name" | Enables name usage in conversations |
| "Don't use my name" | Disables name usage while keeping it stored |
| "Enable name storage" | Allows name storage and usage |
| "Disable name storage" | Prevents name storage |

## Programming Interface

### Basic Usage

```python
from jarvis.core.user_profile import get_user_profile_manager

# Get the manager
manager = get_user_profile_manager()

# Set user's name
manager.set_name("Jose", "Jose")

# Get user's name
name = manager.get_name()
print(f"User's name: {name}")

# Check if name usage is allowed
if manager.is_name_usage_allowed():
    print(f"Hello, {name}!")
else:
    print("Hello there!")
```

### Advanced Usage

```python
# Get full profile
profile = manager.get_profile()
print(f"Name: {profile.name}")
print(f"Preferred: {profile.preferred_name}")
print(f"Pronouns: {profile.pronouns}")
print(f"Privacy level: {profile.privacy_level}")

# Update multiple fields
manager.update_profile(
    name="Jose",
    pronouns="he/him",
    privacy_level="standard"
)

# Set privacy level
manager.set_privacy_level("full")  # minimal, standard, full

# Export profile
profile_data = manager.export_profile()

# Import profile
manager.import_profile(profile_data)

# Clear all data
manager.clear_profile()
```

### Convenience Functions

```python
from jarvis.core.user_profile import get_user_name, set_user_name

# Quick name operations
name = get_user_name()
set_user_name("Jose", "Jose")
```

## UserProfile Data Structure

```python
@dataclass
class UserProfile:
    # Personal Information
    name: Optional[str] = None
    preferred_name: Optional[str] = None
    pronouns: Optional[str] = None
    
    # Preferences
    timezone: Optional[str] = None
    location: Optional[str] = None
    language: str = "en"
    
    # Privacy Settings
    privacy_level: str = "standard"  # minimal, standard, full
    allow_name_storage: bool = True
    allow_preference_storage: bool = True
    
    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    version: str = "1.0"
```

## Privacy Approach

### Names Are NOT PII

The system explicitly treats names as personal information, not sensitive PII:

- **Safe to Store**: Names are stored and used for personalization
- **Not Filtered**: Names are excluded from PII detection systems
- **User Controlled**: Users have full control over name usage
- **Transparent**: Clear about what information is stored and how it's used

### Privacy Levels

1. **Minimal**: Store only essential information
2. **Standard**: Store name and basic preferences (recommended)
3. **Full**: Store detailed personalization data

### User Controls

- **Enable/Disable**: Full control over name storage and usage
- **Clear Profile**: Easy removal of all stored information
- **Transparency**: Always show what information is stored
- **Consent**: Explicit user consent for information storage

## Integration with Jarvis

### System Prompt Enhancement

The system prompt is updated to use personalization:

```
👤 PERSONALIZATION:
- Use the user's name when you know it to make conversations more personal
- Check user profile information to provide personalized responses
- Names are NOT considered PII - they should be stored and used freely
- Respect user privacy preferences about name usage
```

### PII Filter Exclusion

Names are explicitly excluded from PII filtering:

```python
# PII Detection (excludes names - names are allowed and encouraged)
pii_indicators = [
    'ssn', 'social security', 'credit card', 'password', 'pin',
    'bank account', 'routing number', 'driver license', 'passport'
]
# Note: Names are explicitly NOT filtered as PII
```

## Configuration

### Environment Variables

```bash
# Enable user profile system
export JARVIS_ENABLE_USER_PROFILE=true

# Allow name storage
export JARVIS_ALLOW_NAME_STORAGE=true

# Set privacy level
export JARVIS_PRIVACY_LEVEL=standard
```

### Config File Integration

```python
@dataclass
class GeneralConfig:
    # User profile settings
    enable_user_profile: bool = True
    allow_name_storage: bool = True
    privacy_level: str = "standard"  # minimal, standard, full
```

## Setup and Management

### Interactive Setup

Use the setup script for guided configuration:

```bash
python setup_user_profile.py
```

Features:
- Set name and preferred name
- Configure pronouns
- Set privacy level
- Enable/disable name usage
- View current profile
- Clear profile data

### Voice Setup

After starting Jarvis:

1. Say: "My name is [Your Name]"
2. Say: "My pronouns are [your pronouns]"
3. Say: "Show my profile" to verify

### Manual Setup

```python
from jarvis.core.user_profile import get_user_profile_manager

manager = get_user_profile_manager()
manager.set_name("Jose", "Jose")
manager.set_pronouns("he/him")
manager.set_privacy_level("standard")
```

## Usage Examples

### Personalized Conversations

```
User: "My name is Jose"
Jarvis: "Perfect! I'll remember that your name is Jose. Nice to meet you, Jose!"

User: "What's the weather like?"
Jarvis: "Hi Jose! Let me check the weather for you..."

User: "What's my name?"
Jarvis: "I know you as Jose."
```

### Privacy Controls

```
User: "Don't use my name"
Jarvis: "Understood. I won't use your name in conversations anymore, though I'll keep it stored in case you want to re-enable this feature later."

User: "Allow Jarvis to use my name"
Jarvis: "Perfect! I can now store and use your name in our conversations. This helps me provide more personalized responses."
```

## Troubleshooting

### Common Issues

1. **Profile not saving**
   - Check write permissions to `~/.jarvis/` directory
   - Verify disk space availability

2. **Name not being used**
   - Check if name usage is enabled: `show_my_profile()`
   - Verify name is set: `get_my_name()`

3. **Import errors**
   - Ensure `jarvis.core.user_profile` is in Python path
   - Check for missing dependencies

### Debug Commands

```python
# Check profile status
from jarvis.core.user_profile import get_user_profile_manager
manager = get_user_profile_manager()
profile = manager.get_profile()
print(f"Name: {profile.name}")
print(f"Allowed: {profile.allow_name_storage}")

# Check file existence
import os
profile_file = os.path.expanduser("~/.jarvis/user_profile.json")
print(f"Profile file exists: {os.path.exists(profile_file)}")
```

## Best Practices

1. **Respect Privacy**: Always provide clear controls over personal information
2. **Be Transparent**: Show users what information is stored
3. **Provide Fallbacks**: Handle cases where profile information is unavailable
4. **Use Appropriately**: Use names to enhance experience, not overwhelm
5. **Secure Storage**: Store profile data securely with appropriate permissions
6. **Regular Updates**: Keep profile information current and relevant

## See Also

- [Desktop Applications Guide](DESKTOP_APPLICATIONS.md) - Desktop app integration
- [Application Manager](APPLICATION_MANAGER.md) - Process lifecycle management
- [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md) - Creating profile-aware tools
