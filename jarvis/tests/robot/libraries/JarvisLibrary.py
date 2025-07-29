"""
Custom Robot Framework library for testing Jarvis Voice Assistant.

This library provides keywords for interacting with and testing Jarvis
functionality including wake word detection, speech recognition, tool execution,
and memory systems.
"""

import os
import sys
import time
import json
import subprocess
import threading
import requests
from pathlib import Path
from typing import Optional, Dict, Any

from robot.api.deco import keyword
from robot.libraries.BuiltIn import BuiltIn


class JarvisLibrary:
    """Custom Robot Framework library for Jarvis testing."""
    
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = '1.0.0'
    
    def __init__(self):
        """Initialize the Jarvis test library."""
        self.jarvis_process: Optional[subprocess.Popen] = None
        self.jarvis_api_url = "http://localhost:8080"
        self.test_mode = True
        self.last_response = ""
        self.builtin = BuiltIn()
        
        # Test data storage
        self.test_responses = []
        self.test_commands = []
        
    # ============================================================================
    # Application Control Keywords
    # ============================================================================
    
    @keyword
    def start_jarvis_application(self, config_file: str = "test_config.yaml"):
        """
        Start Jarvis application in test mode.
        
        Args:
            config_file: Configuration file to use for testing
            
        Example:
            | Start Jarvis Application | test_config.yaml |
        """
        if self.jarvis_process and self.jarvis_process.poll() is None:
            self.builtin.log("Jarvis is already running", level='WARN')
            return
            
        try:
            # Set up test environment
            env = os.environ.copy()
            env['JARVIS_TEST_MODE'] = 'true'
            env['JARVIS_CONFIG'] = config_file
            
            # Start Jarvis process
            jarvis_path = Path(__file__).parent.parent.parent.parent / "jarvis"
            cmd = [sys.executable, "-m", "jarvis.main"]
            
            self.jarvis_process = subprocess.Popen(
                cmd,
                cwd=str(jarvis_path),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for startup
            self._wait_for_jarvis_startup()
            self.builtin.log(f"Jarvis started with PID: {self.jarvis_process.pid}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to start Jarvis: {str(e)}")
    
    @keyword
    def stop_jarvis_application(self):
        """
        Stop Jarvis application gracefully.
        
        Example:
            | Stop Jarvis Application |
        """
        if not self.jarvis_process:
            self.builtin.log("Jarvis is not running", level='WARN')
            return
            
        try:
            # Send termination signal
            self.jarvis_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self.jarvis_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.builtin.log("Force killing Jarvis process", level='WARN')
                self.jarvis_process.kill()
                self.jarvis_process.wait()
                
            self.jarvis_process = None
            self.builtin.log("Jarvis stopped successfully")
            
        except Exception as e:
            raise RuntimeError(f"Failed to stop Jarvis: {str(e)}")
    
    # ============================================================================
    # Voice Interaction Keywords
    # ============================================================================
    
    @keyword
    def say_wake_word(self, wake_word: str = "jarvis"):
        """
        Trigger wake word detection in test mode.
        
        Args:
            wake_word: Wake word to trigger (default: jarvis)
            
        Example:
            | Say Wake Word | jarvis |
        """
        try:
            # In test mode, we simulate wake word detection
            response = requests.post(
                f"{self.jarvis_api_url}/test/wake_word",
                json={"wake_word": wake_word},
                timeout=5
            )
            
            if response.status_code == 200:
                self.builtin.log(f"Wake word '{wake_word}' triggered successfully")
            else:
                raise RuntimeError(f"Wake word trigger failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            # Fallback: simulate wake word via file system
            self._simulate_wake_word_file(wake_word)
    
    @keyword
    def say_command(self, command: str):
        """
        Send voice command to Jarvis in test mode.
        
        Args:
            command: Voice command to send
            
        Example:
            | Say Command | What time is it |
        """
        try:
            response = requests.post(
                f"{self.jarvis_api_url}/test/command",
                json={"command": command},
                timeout=10
            )
            
            if response.status_code == 200:
                self.builtin.log(f"Command sent: '{command}'")
                self.test_commands.append(command)
            else:
                raise RuntimeError(f"Command failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            # Fallback: simulate command via file system
            self._simulate_command_file(command)
    
    @keyword
    def wait_for_response(self, timeout: str = "10s"):
        """
        Wait for Jarvis to respond to a command.
        
        Args:
            timeout: Maximum time to wait (e.g., "10s", "30s")
            
        Example:
            | Wait For Response | 15s |
        """
        timeout_seconds = self._parse_timeout(timeout)
        start_time = time.time()
        
        while time.time() - start_time < timeout_seconds:
            try:
                response = requests.get(
                    f"{self.jarvis_api_url}/test/response",
                    timeout=2
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('response'):
                        self.last_response = data['response']
                        self.test_responses.append(self.last_response)
                        self.builtin.log(f"Received response: {self.last_response}")
                        return
                        
            except requests.exceptions.RequestException:
                pass
                
            time.sleep(0.5)
        
        # Fallback: check for response file
        response = self._check_response_file()
        if response:
            self.last_response = response
            return
            
        raise RuntimeError(f"No response received within {timeout}")
    
    # ============================================================================
    # Verification Keywords
    # ============================================================================
    
    @keyword
    def response_should_contain(self, expected_text: str):
        """
        Verify that the last response contains expected text.
        
        Args:
            expected_text: Text that should be in the response
            
        Example:
            | Response Should Contain | disk usage |
        """
        if not self.last_response:
            raise AssertionError("No response available to check")
            
        if expected_text.lower() not in self.last_response.lower():
            raise AssertionError(
                f"Response '{self.last_response}' does not contain '{expected_text}'"
            )
            
        self.builtin.log(f"Response contains expected text: '{expected_text}'")
    
    @keyword
    def response_should_not_contain(self, unexpected_text: str):
        """
        Verify that the last response does not contain unexpected text.
        
        Args:
            unexpected_text: Text that should not be in the response
            
        Example:
            | Response Should Not Contain | error |
        """
        if not self.last_response:
            raise AssertionError("No response available to check")
            
        if unexpected_text.lower() in self.last_response.lower():
            raise AssertionError(
                f"Response '{self.last_response}' contains unexpected text '{unexpected_text}'"
            )
            
        self.builtin.log(f"Response does not contain unexpected text: '{unexpected_text}'")
    
    @keyword
    def tool_should_be_available(self, tool_name: str):
        """
        Verify that a specific tool is loaded and available.
        
        Args:
            tool_name: Name of the tool to check
            
        Example:
            | Tool Should Be Available | execute_code |
        """
        try:
            response = requests.get(
                f"{self.jarvis_api_url}/test/tools",
                timeout=5
            )
            
            if response.status_code == 200:
                tools = response.json().get('tools', [])
                if tool_name in tools:
                    self.builtin.log(f"Tool '{tool_name}' is available")
                    return
                    
            raise AssertionError(f"Tool '{tool_name}' is not available")
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to check tool availability: {str(e)}")
    
    # ============================================================================
    # Helper Methods
    # ============================================================================
    
    def _wait_for_jarvis_startup(self, timeout: int = 30):
        """Wait for Jarvis to start up and be ready."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.jarvis_process and self.jarvis_process.poll() is not None:
                raise RuntimeError("Jarvis process terminated during startup")
                
            try:
                response = requests.get(f"{self.jarvis_api_url}/test/health", timeout=2)
                if response.status_code == 200:
                    return
            except requests.exceptions.RequestException:
                pass
                
            time.sleep(1)
            
        raise RuntimeError("Jarvis failed to start within timeout")
    
    def _parse_timeout(self, timeout_str: str) -> float:
        """Parse timeout string to seconds."""
        if timeout_str.endswith('s'):
            return float(timeout_str[:-1])
        elif timeout_str.endswith('m'):
            return float(timeout_str[:-1]) * 60
        else:
            return float(timeout_str)
    
    def _simulate_wake_word_file(self, wake_word: str):
        """Simulate wake word via file system (fallback method)."""
        test_dir = Path("/tmp/jarvis_test")
        test_dir.mkdir(exist_ok=True)
        
        wake_word_file = test_dir / "wake_word.txt"
        wake_word_file.write_text(wake_word)
        
        self.builtin.log(f"Wake word simulated via file: {wake_word}")
    
    def _simulate_command_file(self, command: str):
        """Simulate command via file system (fallback method)."""
        test_dir = Path("/tmp/jarvis_test")
        test_dir.mkdir(exist_ok=True)
        
        command_file = test_dir / "command.txt"
        command_file.write_text(command)
        
        self.builtin.log(f"Command simulated via file: {command}")
    
    def _check_response_file(self) -> Optional[str]:
        """Check for response file (fallback method)."""
        test_dir = Path("/tmp/jarvis_test")
        response_file = test_dir / "response.txt"
        
        if response_file.exists():
            response = response_file.read_text()
            response_file.unlink()  # Clean up
            return response
            
        return None
    
    # ============================================================================
    # Cleanup
    # ============================================================================
    
    def __del__(self):
        """Cleanup when library is destroyed."""
        if self.jarvis_process and self.jarvis_process.poll() is None:
            try:
                self.jarvis_process.terminate()
                self.jarvis_process.wait(timeout=5)
            except:
                pass
