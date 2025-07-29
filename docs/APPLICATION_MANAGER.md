# Application Manager System

The Application Manager provides robust lifecycle management for Jarvis desktop applications, ensuring reliable startup, shutdown, and restart operations.

## Overview

The Application Manager system consists of:

- **AppProcess**: Represents and manages individual application processes
- **DesktopAppManager**: Coordinates multiple applications and their lifecycles
- **Signal Handling**: Proper SIGTERM/SIGINT handling for graceful shutdown
- **Process Group Management**: Prevents zombie processes and ensures clean termination

## Architecture

### Core Components

```
jarvis/jarvis/utils/app_manager.py
├── AppProcess                    # Individual process management
├── DesktopAppManager            # Multi-app coordination
└── Global Instance              # Singleton pattern for system-wide access
```

### Key Features

1. **Process Group Management**
   - Applications start in new process groups
   - Graceful termination with SIGTERM to entire group
   - Force kill fallback with SIGKILL

2. **Lifecycle Tracking**
   - Process state monitoring
   - Start time tracking
   - Health checks and validation

3. **Thread Safety**
   - Lock-based synchronization
   - Safe concurrent operations
   - Atomic state changes

4. **Error Recovery**
   - Comprehensive error handling
   - Automatic cleanup on failures
   - Graceful degradation

## Usage

### Basic Usage

```python
from jarvis.utils.app_manager import get_app_manager

# Get the global manager instance
app_manager = get_app_manager()

# Register an application
app_manager.register_app(
    name="vault",
    script_path="/path/to/rag_app.py",
    args=["--panel", "main"]
)

# Start the application
if app_manager.start_app("vault"):
    print("Vault started successfully")

# Check if running
if app_manager.is_app_running("vault"):
    print("Vault is currently running")

# Stop the application
if app_manager.stop_app("vault"):
    print("Vault stopped successfully")
```

### Advanced Usage

```python
# Get detailed status
status = app_manager.get_app_status("vault")
print(f"Running: {status['running']}")
print(f"PID: {status['pid']}")
print(f"Start time: {status['start_time']}")

# Force stop if needed
app_manager.stop_app("vault", force=True)

# Stop all managed applications
app_manager.stop_all_apps()
```

## AppProcess Class

### Initialization

```python
app = AppProcess(
    name="vault",
    script_path="/path/to/rag_app.py",
    args=["--panel", "main"]
)
```

### Methods

#### `start() -> bool`
Starts the application process with proper session handling.

```python
if app.start():
    print(f"Started {app.name} with PID {app.pid}")
```

#### `is_running() -> bool`
Checks if the process is still alive.

```python
if app.is_running():
    print("Process is active")
```

#### `terminate_gracefully(timeout: float = 5.0) -> bool`
Attempts graceful termination with SIGTERM.

```python
if app.terminate_gracefully():
    print("Process terminated gracefully")
else:
    print("Graceful termination failed")
```

#### `force_kill() -> bool`
Force kills the process and all children.

```python
app.force_kill()  # Last resort
```

### Process Group Management

Applications are started with `start_new_session=True`:

```python
self.process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    stdin=subprocess.PIPE,
    start_new_session=True,  # Creates new process group
    cwd=os.path.dirname(self.script_path)
)
```

This ensures:
- Clean separation from parent process
- Proper signal propagation to child processes
- Prevention of zombie processes

## DesktopAppManager Class

### Registration

```python
def register_app(self, name: str, script_path: str, args: List[str] = None) -> bool:
    """Register an application for management."""
```

### Lifecycle Management

```python
def start_app(self, name: str) -> bool:
    """Start an application, ensuring clean state."""

def stop_app(self, name: str, force: bool = False) -> bool:
    """Stop an application gracefully or forcefully."""

def is_app_running(self, name: str) -> bool:
    """Check if an application is running."""
```

### Status Monitoring

```python
def get_app_status(self, name: str) -> Dict:
    """Get detailed status of an application."""
    return {
        "registered": True,
        "running": app.is_running(),
        "pid": app.pid,
        "start_time": app.start_time,
        "script_path": app.script_path
    }
```

## Signal Handling

### Application-Level Handlers

Desktop applications must implement signal handlers:

```python
import signal
import sys

def signal_handler(signum, frame):
    print(f"\n🛑 App received signal {signum}, shutting down...")
    try:
        webview.destroy()  # Clean up resources
    except:
        pass
    sys.exit(0)

# Register handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
```

### Manager-Level Termination

The AppManager sends signals to process groups:

```python
# Send SIGTERM to process group
os.killpg(os.getpgid(self.pid), signal.SIGTERM)

# Wait for graceful shutdown
self.process.wait(timeout=timeout)

# Force kill if needed
os.killpg(os.getpgid(self.pid), signal.SIGKILL)
```

## Error Handling

### Graceful Degradation

```python
try:
    from jarvis.utils.app_manager import get_app_manager
    app_manager = get_app_manager()
except ImportError:
    # Fallback to direct process management
    app_manager = None

if app_manager:
    # Use robust manager
    app_manager.start_app("vault")
else:
    # Direct subprocess fallback
    subprocess.Popen([sys.executable, "rag_app.py"])
```

### Comprehensive Logging

```python
import logging

logger = logging.getLogger(__name__)

try:
    if app.start():
        logger.info(f"Successfully started {app.name} (PID: {app.pid})")
    else:
        logger.error(f"Failed to start {app.name}")
except Exception as e:
    logger.error(f"Error starting {app.name}: {e}")
```

## Integration with Tools

### Plugin Tool Integration

```python
@tool
def open_rag_manager(panel: str = "main") -> str:
    """Open the Vault interface."""
    try:
        app_manager = get_app_manager()
        if app_manager:
            # Use robust manager
            app_name = "vault"
            app_manager.register_app(
                name=app_name,
                script_path=str(desktop_script),
                args=["--panel", panel]
            )
            
            if app_manager.start_app(app_name):
                return f"The Vault is now open."
            else:
                return "Error opening the Vault."
        else:
            # Fallback to direct launch
            subprocess.Popen([sys.executable, str(desktop_script)])
            return "Opening Vault..."
    except Exception as e:
        return f"Error: {str(e)}"
```

## Configuration

### Environment Variables

```bash
# Enable debug logging
export JARVIS_DEBUG=true

# Custom data directory
export JARVIS_DATA_DIR=/custom/path

# Application-specific settings
export JARVIS_VAULT_PORT=8081
export JARVIS_SETTINGS_PORT=8080
```

### Config File Integration

```python
@dataclass
class GeneralConfig:
    debug: bool = False
    data_dir: Path = field(default_factory=lambda: Path.home() / ".jarvis")
    
    # Application management
    app_startup_timeout: int = 10
    app_shutdown_timeout: int = 5
    enable_process_groups: bool = True
```

## Troubleshooting

### Common Issues

1. **Applications won't start**
   - Check script paths are correct
   - Verify Python executable is accessible
   - Check for port conflicts

2. **Applications won't stop**
   - Signal handlers should resolve this
   - Check for zombie processes: `ps aux | grep jarvis`
   - Use force kill as last resort

3. **Import errors**
   - Ensure `jarvis.utils.app_manager` is in Python path
   - Fallback mechanisms should handle missing imports

### Debug Commands

```python
# Check manager status
app_manager = get_app_manager()
for name in ["vault", "settings"]:
    status = app_manager.get_app_status(name)
    print(f"{name}: {status}")

# List all processes
import psutil
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    if 'jarvis' in str(proc.info['cmdline']):
        print(f"PID {proc.info['pid']}: {proc.info['cmdline']}")
```

## Best Practices

1. **Always register applications** before starting them
2. **Use the global manager instance** for consistency
3. **Implement signal handlers** in all desktop applications
4. **Provide fallback mechanisms** for error cases
5. **Clean up resources** before process termination
6. **Use process groups** to prevent zombie processes
7. **Log operations** for debugging and monitoring

## Recent Improvements

### July 28, 2025 Updates

1. **Enhanced Process Management**
   - Added process group support
   - Implemented graceful termination with force fallback
   - Added comprehensive error handling

2. **Improved Signal Handling**
   - Fixed desktop applications to respond to SIGTERM
   - Added webview.destroy() cleanup
   - Implemented proper exit handling

3. **Better Integration**
   - Fixed import issues in plugin tools
   - Added fallback behavior for missing components
   - Enhanced error messages and user feedback

4. **Robust Path Handling**
   - Implemented dynamic path resolution
   - Added project root detection
   - Provided multiple fallback mechanisms

These improvements ensure reliable desktop application management with proper cleanup and error recovery.

## See Also

- [Desktop Applications Guide](DESKTOP_APPLICATIONS.md) - Complete guide to Jarvis desktop apps
- [User Profile System](USER_PROFILE_SYSTEM.md) - User personalization and name storage
- [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md) - Creating custom tools and plugins
