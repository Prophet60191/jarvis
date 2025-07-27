"""
Enhanced Terminal UI for Jarvis Voice Assistant

Provides a clean, user-friendly terminal interface with:
- Clear conversation display
- Status indicators
- Progress feedback
- Error handling
- Startup information

Author: Jarvis Team
"""

import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class TerminalColors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'

class StatusType(Enum):
    """Types of status messages."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"

class TerminalUI:
    """Enhanced terminal user interface for Jarvis."""
    
    def __init__(self):
        self.colors = TerminalColors()
        self.last_status_line = ""
        self.conversation_count = 0
        
    def clear_screen(self):
        """Clear the terminal screen."""
        print('\033[2J\033[H', end='')
        
    def print_header(self):
        """Print the Jarvis header."""
        print(f"\n{self.colors.CYAN}{self.colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                    🤖 JARVIS VOICE ASSISTANT                 ║")
        print("║                     Ready to Assist You                     ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{self.colors.RESET}")
        
    def print_startup_info(self, config: Dict[str, Any]):
        """Print startup configuration information."""
        print(f"{self.colors.BLUE}📋 System Configuration:{self.colors.RESET}")
        print(f"   🎤 Microphone: {config.get('microphone', 'Default')}")
        print(f"   🧠 AI Model: {self.colors.GREEN}{config.get('model', 'llama3.1:8b')}{self.colors.RESET}")
        print(f"   🔧 Tools Available: {config.get('tool_count', 0)}")
        print(f"   👂 Wake Word: '{self.colors.YELLOW}{config.get('wake_word', 'jarvis')}{self.colors.RESET}'")
        print(f"   ⏱️  Timeout: {config.get('timeout', 30)}s")
        print()
        
    def print_controls(self):
        """Print control instructions."""
        print(f"{self.colors.MAGENTA}🎮 Controls:{self.colors.RESET}")
        print(f"   💬 Say '{self.colors.YELLOW}jarvis{self.colors.RESET}' to start conversation")
        print(f"   🛑 Press {self.colors.RED}Ctrl+C{self.colors.RESET} to stop anytime (even during speech)")
        print(f"   🔄 Follow-up questions don't need wake word")
        print()
        
    def print_separator(self, char="─", length=60):
        """Print a separator line."""
        print(f"{self.colors.GRAY}{char * length}{self.colors.RESET}")
        
    def show_status(self, status_type: StatusType, message: str, clear_previous: bool = True):
        """Show a status message with appropriate styling."""
        if clear_previous and self.last_status_line:
            # Clear previous status line
            print(f"\r{' ' * len(self.last_status_line)}\r", end='')
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Choose color and icon based on status type
        if status_type == StatusType.LISTENING:
            icon = "👂"
            color = self.colors.BLUE
        elif status_type == StatusType.THINKING:
            icon = "🧠"
            color = self.colors.YELLOW
        elif status_type == StatusType.SPEAKING:
            icon = "🔊"
            color = self.colors.GREEN
        elif status_type == StatusType.SUCCESS:
            icon = "✅"
            color = self.colors.GREEN
        elif status_type == StatusType.WARNING:
            icon = "⚠️"
            color = self.colors.YELLOW
        elif status_type == StatusType.ERROR:
            icon = "❌"
            color = self.colors.RED
        else:  # INFO
            icon = "ℹ️"
            color = self.colors.CYAN
            
        status_line = f"{self.colors.GRAY}[{timestamp}]{self.colors.RESET} {icon} {color}{message}{self.colors.RESET}"
        print(status_line)
        self.last_status_line = status_line
        
    def show_conversation_start(self):
        """Show conversation start indicator."""
        self.conversation_count += 1
        print(f"\n{self.colors.CYAN}{'═' * 60}{self.colors.RESET}")
        print(f"{self.colors.CYAN}{self.colors.BOLD}   💬 CONVERSATION #{self.conversation_count} STARTED{self.colors.RESET}")
        print(f"{self.colors.CYAN}{'═' * 60}{self.colors.RESET}")
        
    def show_user_input(self, text: str, confidence: Optional[float] = None):
        """Display user input in conversation format."""
        confidence_str = f" (confidence: {confidence:.2f})" if confidence else ""
        print(f"\n{self.colors.BLUE}{self.colors.BOLD}👤 You:{self.colors.RESET} {text}{self.colors.GRAY}{confidence_str}{self.colors.RESET}")
        
    def show_jarvis_response(self, text: str, thinking_time: Optional[float] = None):
        """Display Jarvis response in conversation format."""
        thinking_str = f" (processed in {thinking_time:.1f}s)" if thinking_time else ""
        print(f"{self.colors.GREEN}{self.colors.BOLD}🤖 Jarvis:{self.colors.RESET} {text}{self.colors.GRAY}{thinking_str}{self.colors.RESET}")
        
    def show_conversation_end(self, reason: str = "timeout"):
        """Show conversation end indicator."""
        print(f"\n{self.colors.GRAY}{'─' * 60}{self.colors.RESET}")
        print(f"{self.colors.GRAY}   💬 Conversation ended ({reason}){self.colors.RESET}")
        print(f"{self.colors.GRAY}{'─' * 60}{self.colors.RESET}\n")
        
    def show_listening_prompt(self):
        """Show the main listening prompt."""
        print(f"{self.colors.BLUE}👂 Listening for wake word...{self.colors.RESET}")
        print(f"{self.colors.DIM}   Say 'jarvis' clearly and wait for response{self.colors.RESET}")
        
    def show_error(self, error_msg: str, suggestions: Optional[list] = None):
        """Show an error message with optional suggestions."""
        print(f"\n{self.colors.RED}❌ Error: {error_msg}{self.colors.RESET}")
        if suggestions:
            print(f"{self.colors.YELLOW}💡 Suggestions:{self.colors.RESET}")
            for suggestion in suggestions:
                print(f"   • {suggestion}")
        print()
        
    def show_warning(self, warning_msg: str):
        """Show a warning message."""
        print(f"{self.colors.YELLOW}⚠️  Warning: {warning_msg}{self.colors.RESET}")
        
    def show_success(self, success_msg: str):
        """Show a success message."""
        print(f"{self.colors.GREEN}✅ {success_msg}{self.colors.RESET}")
        
    def show_thinking_animation(self, duration: float = 2.0):
        """Show a thinking animation."""
        thinking_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        start_time = time.time()
        i = 0
        
        while time.time() - start_time < duration:
            char = thinking_chars[i % len(thinking_chars)]
            print(f"\r{self.colors.YELLOW}{char} Thinking...{self.colors.RESET}", end='', flush=True)
            time.sleep(0.1)
            i += 1
            
        print(f"\r{' ' * 20}\r", end='')  # Clear the thinking line
        
    def show_emergency_stop(self):
        """Show emergency stop message."""
        print(f"\n{self.colors.RED}{self.colors.BOLD}🛑 EMERGENCY STOP ACTIVATED{self.colors.RESET}")
        print(f"{self.colors.RED}   Shutting down all systems...{self.colors.RESET}")
        
    def show_shutdown(self):
        """Show shutdown message."""
        print(f"\n{self.colors.CYAN}🛑 Shutting down Jarvis...{self.colors.RESET}")
        print(f"{self.colors.GRAY}   Cleaning up components...{self.colors.RESET}")
        
    def show_shutdown_complete(self):
        """Show shutdown complete message."""
        print(f"{self.colors.GREEN}✅ Shutdown complete{self.colors.RESET}")
        print(f"{self.colors.CYAN}👋 Goodbye! Thanks for using Jarvis.{self.colors.RESET}\n")
        
    def show_component_status(self, component: str, status: str, success: bool = True):
        """Show component initialization/shutdown status."""
        icon = "✅" if success else "❌"
        color = self.colors.GREEN if success else self.colors.RED
        print(f"   {icon} {color}{component}: {status}{self.colors.RESET}")
        
    def show_tool_list(self, tools: list):
        """Show available tools in a formatted way."""
        if not tools:
            print(f"{self.colors.YELLOW}   No tools available{self.colors.RESET}")
            return
            
        print(f"{self.colors.BLUE}🔧 Available Tools:{self.colors.RESET}")
        for i, tool in enumerate(tools, 1):
            print(f"   {i}. {self.colors.GREEN}{tool}{self.colors.RESET}")
        print()
        
    def prompt_user(self, message: str) -> str:
        """Prompt user for input with styling."""
        return input(f"{self.colors.CYAN}❓ {message}: {self.colors.RESET}")
        
    def show_debug_info(self, info: Dict[str, Any]):
        """Show debug information."""
        print(f"\n{self.colors.MAGENTA}🐛 Debug Information:{self.colors.RESET}")
        for key, value in info.items():
            print(f"   {key}: {self.colors.YELLOW}{value}{self.colors.RESET}")
        print()

# Global instance
terminal_ui = TerminalUI()
