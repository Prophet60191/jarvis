"""
Vault UI Tool Plugin

Voice commands for opening and managing the Vault (Knowledge Vault) interface.
Provides document upload, knowledge management, and RAG configuration through voice commands.

Voice Commands:
- "Open vault" / "Show vault" / "Manage vault"
- "Close vault"
- "Show vault status"

This plugin follows the same architecture as the Jarvis Settings UI for consistency.
"""

import subprocess
import sys
import os
import logging
import requests
from pathlib import Path
from typing import List

from langchain.tools import tool

# Import app manager with proper error handling
try:
    from jarvis.utils.app_manager import get_app_manager
except ImportError:
    # Fallback if app_manager not available
    def get_app_manager():
        return None

# Setup logging
logger = logging.getLogger(__name__)


@tool
def open_rag_manager(panel: str = "main") -> str:
    """
    Open the Vault interface when user asks to "open vault", "show vault", "manage vault",
    "open documents", "upload documents", or similar requests.

    This opens a native desktop application for:
    - Document upload and management
    - Knowledge vault management
    - RAG system configuration
    - Database Agent monitoring
    - Document versioning and history

    Use this tool when the user wants to:
    - Open the knowledge vault
    - Upload or manage documents
    - View or manage stored knowledge
    - Configure vault settings
    - Monitor document processing
    - Access intelligent document features
    - Manage the Database Agent

    Args:
        panel: Which panel to open. Options: 'main', 'upload', 'documents', 'memory', 'settings'

    Returns:
        Status message about opening the Vault
    """
    try:
        # First, check if the app is already running and close it
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and 'rag_app.py' in ' '.join(cmdline):
                        logger.info(f"Found existing Vault process (PID: {proc.info['pid']}), terminating...")
                        proc.terminate()
                        try:
                            proc.wait(timeout=2)
                        except psutil.TimeoutExpired:
                            proc.kill()
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except ImportError:
            pass  # psutil not available, continue anyway

        # Find the RAG desktop app script
        current_dir = Path(__file__).parent.parent.parent.parent.parent  # Go up to project root
        desktop_script = current_dir / "rag_app.py"

        if not desktop_script.exists():
            logger.error(f"RAG desktop app not found at: {desktop_script}")
            return "Sorry, I couldn't find the RAG Management desktop app. Please check the installation."

        # Validate panel
        valid_panels = ["main", "upload", "documents", "memory", "settings"]
        if panel not in valid_panels:
            panel = "main"
            logger.warning(f"Invalid panel requested, defaulting to 'main'")

        logger.info(f"Opening RAG Management desktop app with panel: {panel}")

        # Try to use the robust application manager, fallback to direct launch
        app_manager = get_app_manager()

        if app_manager:
            # Use robust application manager
            app_name = "vault"
            app_manager.register_app(
                name=app_name,
                script_path=str(desktop_script),
                args=["--panel", panel]
            )

            if app_manager.start_app(app_name):
                panel_names = {
                    "main": "Main Dashboard",
                    "upload": "Document Upload",
                    "documents": "Document Library",
                    "memory": "Memory Management",
                    "settings": "RAG Configuration"
                }

                panel_name = panel_names.get(panel, panel.title())
                return f"The Vault ({panel_name}) is now open in the desktop app."
            else:
                return "I encountered an error while trying to open the Vault. Please try again."
        else:
            # Fallback to direct launch
            try:
                import webview
                cmd = [sys.executable, str(desktop_script), "--panel", panel]
                subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )

                panel_names = {
                    "main": "Main Dashboard",
                    "upload": "Document Upload",
                    "documents": "Document Library",
                    "memory": "Memory Management",
                    "settings": "RAG Configuration"
                }

                panel_name = panel_names.get(panel, panel.title())
                return f"Opening Vault {panel_name} in the desktop app. The window should appear on your screen shortly."

            except ImportError:
                return "The Vault desktop app requires pywebview. Please install it with: pip install pywebview"

    except Exception as e:
        logger.error(f"Failed to open Vault desktop app: {e}")
        return f"Sorry, I couldn't open the Vault interface. Error: {str(e)}"


@tool
def close_rag_manager() -> str:
    """
    Close the Vault desktop application when user asks to "close vault".

    This will gracefully shut down the Vault native desktop app.

    Returns:
        Status message about closing the Vault
    """
    try:
        logger.info("Attempting to close Vault desktop app")

        # Try to use the robust application manager, fallback to process termination
        app_manager = get_app_manager()

        if app_manager:
            # Use robust application manager
            app_name = "vault"
            if app_manager.is_app_running(app_name):
                if app_manager.stop_app(app_name):
                    return "I've successfully closed the Vault desktop app."
                else:
                    return "I encountered an error while trying to close the Vault app. Please try closing it manually."
            else:
                return "The Vault app doesn't appear to be running, or it's already closed."
        else:
            # Fallback to direct process termination
            try:
                import psutil
                terminated_count = 0

                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        cmdline = proc.info['cmdline']
                        if cmdline and 'rag_app.py' in ' '.join(cmdline):
                            proc.terminate()
                            terminated_count += 1
                            try:
                                proc.wait(timeout=3)
                            except psutil.TimeoutExpired:
                                proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                if terminated_count > 0:
                    return f"I've successfully closed the Vault desktop app."
                else:
                    return "The Vault app doesn't appear to be running, or it's already closed."

            except ImportError:
                return "Unable to close the Vault app automatically. Please close it manually from the window."

    except Exception as e:
        logger.error(f"Error closing Vault desktop app: {e}")
        return f"I encountered an error while trying to close the Vault app: {str(e)}"


@tool
def show_rag_status() -> str:
    """
    Show the current status of the Vault system when user asks to "show vault status".

    This provides information about:
    - Vault system availability
    - Database Agent status
    - Document count and storage
    - Knowledge statistics
    - Desktop app status

    Returns:
        Status information about the Vault system
    """
    try:
        status_info = []

        # Check if RAG desktop app is running
        try:
            import psutil
            app_running = False

            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and 'rag_app.py' in ' '.join(cmdline):
                        status_info.append(f"✅ Vault App: Running (PID: {proc.info['pid']})")
                        app_running = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if not app_running:
                status_info.append("❌ Vault App: Not running")

        except ImportError:
            status_info.append("❓ Vault App: Unable to check (psutil not available)")

        # Check RAG system availability
        try:
            from jarvis.tools.rag_service import RAGService
            from jarvis.tools.database_agent import get_database_agent
            from jarvis.config import get_config

            config = get_config()
            status_info.append("✅ RAG System: Available")
            status_info.append(f"🤖 Main Model: {config.llm.model}")
            status_info.append("🧠 Database Agent: Qwen2.5:3b-instruct ready")

            # Try to get document count
            try:
                from pathlib import Path
                docs_path = Path(config.rag.documents_path)
                if docs_path.exists():
                    doc_count = len([f for f in docs_path.iterdir() if f.is_file() and f.suffix.lower() in {'.txt', '.pdf', '.doc', '.docx'}])
                    status_info.append(f"📄 Documents: {doc_count} files")
                    status_info.append(f"📁 Path: {docs_path}")
                else:
                    status_info.append("📄 Documents: Directory not found")
            except Exception:
                status_info.append("📄 Documents: Unable to check")

            # Try to get memory stats
            try:
                rag_service = RAGService(config)
                collection = rag_service.vector_store._collection
                memory_count = collection.count()
                status_info.append(f"🧠 Memories: {memory_count} stored")
                status_info.append("💾 ChromaDB: Connected")
            except Exception:
                status_info.append("🧠 Memories: Unable to check")
                status_info.append("💾 ChromaDB: Status unknown")

        except ImportError:
            status_info.append("❌ RAG System: Not available")

        # Check pywebview availability
        try:
            import webview
            status_info.append("✅ pywebview: Available for desktop app")
        except ImportError:
            status_info.append("❌ pywebview: Not installed (required for desktop app)")

        if status_info:
            return "RAG System Status:\n" + "\n".join(status_info)
        else:
            return "Unable to determine RAG system status."

    except Exception as e:
        logger.error(f"Error getting RAG status: {e}")
        return f"Error checking RAG system status: {str(e)}"


class RAGUIToolPlugin:
    """Plugin class for RAG Management UI tools."""
    
    def __init__(self):
        self.name = "RAG Management UI Tools"
        self.version = "1.0.0"
        self.description = "Voice commands for RAG document and memory management interface"
    
    def get_metadata(self):
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": "Jarvis Assistant",
            "tags": ["rag", "documents", "memory", "ui", "management"]
        }
    
    def get_tools(self) -> List:
        return [open_rag_manager, close_rag_manager, show_rag_status]


# Create plugin instance for automatic discovery
plugin = RAGUIToolPlugin()

# Export tools for direct import
__all__ = ["open_rag_manager", "close_rag_manager", "show_rag_status", "plugin"]
