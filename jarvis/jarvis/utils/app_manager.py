#!/usr/bin/env python3
"""
Robust Desktop Application Manager for Jarvis.

This module provides proper lifecycle management for desktop applications,
ensuring they can be opened, closed, and reopened reliably.
"""

import os
import sys
import time
import signal
import logging
import subprocess
import threading
from typing import Dict, Optional, List
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class AppProcess:
    """Represents a managed application process."""
    
    def __init__(self, name: str, script_path: str, args: List[str] = None):
        self.name = name
        self.script_path = script_path
        self.args = args or []
        self.process: Optional[subprocess.Popen] = None
        self.pid: Optional[int] = None
        self.start_time: Optional[float] = None
        
    def is_running(self) -> bool:
        """Check if the process is still running."""
        if not self.process:
            return False
            
        # Check if process is still alive
        poll_result = self.process.poll()
        if poll_result is not None:
            # Process has terminated
            self.process = None
            self.pid = None
            return False
            
        return True
    
    def start(self) -> bool:
        """Start the application process."""
        try:
            if self.is_running():
                logger.warning(f"Process {self.name} is already running")
                return True
            
            # Build command
            cmd = [sys.executable, self.script_path] + self.args
            
            logger.info(f"Starting {self.name}: {' '.join(cmd)}")
            
            # Start process with proper session handling
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                start_new_session=True,  # Create new process group
                cwd=os.path.dirname(self.script_path)
            )
            
            self.pid = self.process.pid
            self.start_time = time.time()
            
            # Give process time to start
            time.sleep(1)
            
            if self.is_running():
                logger.info(f"Successfully started {self.name} (PID: {self.pid})")
                return True
            else:
                logger.error(f"Failed to start {self.name} - process died immediately")
                return False
                
        except Exception as e:
            logger.error(f"Error starting {self.name}: {e}")
            return False
    
    def terminate_gracefully(self, timeout: float = 5.0) -> bool:
        """Terminate the process gracefully with timeout."""
        if not self.is_running():
            return True
            
        try:
            logger.info(f"Gracefully terminating {self.name} (PID: {self.pid})")
            
            # Send SIGTERM to the process group
            if hasattr(os, 'killpg'):
                try:
                    os.killpg(os.getpgid(self.pid), signal.SIGTERM)
                except (OSError, ProcessLookupError):
                    # Fallback to direct process termination
                    self.process.terminate()
            else:
                self.process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.process.wait(timeout=timeout)
                logger.info(f"Process {self.name} terminated gracefully")
                self.process = None
                self.pid = None
                return True
            except subprocess.TimeoutExpired:
                logger.warning(f"Process {self.name} didn't terminate gracefully within {timeout}s")
                return False
                
        except Exception as e:
            logger.error(f"Error during graceful termination of {self.name}: {e}")
            return False
    
    def force_kill(self) -> bool:
        """Force kill the process and all children."""
        if not self.pid:
            return True
            
        try:
            logger.warning(f"Force killing {self.name} (PID: {self.pid})")
            
            # Kill process group if possible
            if hasattr(os, 'killpg'):
                try:
                    os.killpg(os.getpgid(self.pid), signal.SIGKILL)
                except (OSError, ProcessLookupError):
                    pass
            
            # Kill direct process
            if self.process:
                self.process.kill()
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass
            
            # Use psutil to kill any remaining processes
            if PSUTIL_AVAILABLE:
                self._kill_related_processes()
            
            self.process = None
            self.pid = None
            logger.info(f"Force killed {self.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error force killing {self.name}: {e}")
            return False
    
    def _kill_related_processes(self):
        """Kill any processes related to this application using psutil."""
        if not PSUTIL_AVAILABLE:
            return
            
        try:
            script_name = os.path.basename(self.script_path)
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and script_name in ' '.join(cmdline):
                        logger.info(f"Killing related process: PID {proc.info['pid']}")
                        proc.kill()
                        proc.wait(timeout=1)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    continue
        except Exception as e:
            logger.error(f"Error killing related processes: {e}")


class DesktopAppManager:
    """Manages desktop application lifecycle."""
    
    def __init__(self):
        self.apps: Dict[str, AppProcess] = {}
        self.lock = threading.Lock()
    
    def register_app(self, name: str, script_path: str, args: List[str] = None) -> bool:
        """Register an application for management."""
        try:
            if not os.path.exists(script_path):
                logger.error(f"Script not found: {script_path}")
                return False
            
            with self.lock:
                self.apps[name] = AppProcess(name, script_path, args)
                logger.info(f"Registered app: {name}")
                return True
                
        except Exception as e:
            logger.error(f"Error registering app {name}: {e}")
            return False
    
    def start_app(self, name: str) -> bool:
        """Start an application, ensuring any existing instance is closed first."""
        try:
            with self.lock:
                if name not in self.apps:
                    logger.error(f"App not registered: {name}")
                    return False
                
                app = self.apps[name]
                
                # Ensure clean state
                if app.is_running():
                    logger.info(f"App {name} is already running, stopping it first")
                    self.stop_app(name)
                    time.sleep(1)  # Give time for cleanup
                
                return app.start()
                
        except Exception as e:
            logger.error(f"Error starting app {name}: {e}")
            return False
    
    def stop_app(self, name: str, force: bool = False) -> bool:
        """Stop an application gracefully or forcefully."""
        try:
            with self.lock:
                if name not in self.apps:
                    logger.error(f"App not registered: {name}")
                    return False
                
                app = self.apps[name]
                
                if not app.is_running():
                    logger.info(f"App {name} is not running")
                    return True
                
                if force:
                    return app.force_kill()
                else:
                    # Try graceful first, then force if needed
                    if app.terminate_gracefully(timeout=5.0):
                        return True
                    else:
                        logger.warning(f"Graceful termination failed for {name}, force killing")
                        return app.force_kill()
                        
        except Exception as e:
            logger.error(f"Error stopping app {name}: {e}")
            return False
    
    def is_app_running(self, name: str) -> bool:
        """Check if an application is running."""
        with self.lock:
            if name not in self.apps:
                return False
            return self.apps[name].is_running()
    
    def get_app_status(self, name: str) -> Dict:
        """Get detailed status of an application."""
        with self.lock:
            if name not in self.apps:
                return {"registered": False}
            
            app = self.apps[name]
            return {
                "registered": True,
                "running": app.is_running(),
                "pid": app.pid,
                "start_time": app.start_time,
                "script_path": app.script_path
            }
    
    def stop_all_apps(self):
        """Stop all managed applications."""
        logger.info("Stopping all managed applications")
        with self.lock:
            for name in list(self.apps.keys()):
                self.stop_app(name, force=True)


# Global instance
app_manager = DesktopAppManager()


def get_app_manager() -> DesktopAppManager:
    """Get the global application manager instance."""
    return app_manager
