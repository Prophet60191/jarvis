#!/usr/bin/env python3
"""
Jarvis UI Application

Voice-activated configuration and monitoring interface for Jarvis Voice Assistant.
This application provides a web-based interface for managing Jarvis settings,
monitoring system status, and configuring audio/performance parameters.

Usage:
    python jarvis_ui.py [--panel PANEL_NAME] [--port PORT]

Panels:
    - main: Main dashboard (default)
    - settings: Configuration settings
    - audio: Audio configuration
    - performance: Performance monitoring
    - tools: Tool management
    - status: System status
"""

import sys
import argparse
import threading
import json
import os
import webbrowser
import time
import platform
import psutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the jarvis package to the path for configuration access
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'jarvis'))

try:
    from jarvis.config import get_config, reload_config, trigger_config_reload, JarvisConfig
    from jarvis.audio.voice_profiles import VoiceProfileManager
    CONFIG_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import Jarvis configuration: {e}")
    CONFIG_AVAILABLE = False

# Configuration content is embedded in this file
CONTENT_AVAILABLE = True


class ConfigurationManager:
    """Manages Jarvis configuration through the web interface."""

    def __init__(self):
        self.config_file = Path.home() / ".jarvis" / "config.json"
        self.env_file = Path.cwd() / ".env"

    def get_current_config(self) -> Dict[str, Any]:
        """Get the current configuration as a dictionary."""
        if not CONFIG_AVAILABLE:
            return {"error": "Configuration system not available"}

        try:
            config = get_config()
            return {
                "audio": {
                    "mic_index": config.audio.mic_index,
                    "mic_name": config.audio.mic_name,
                    "energy_threshold": config.audio.energy_threshold,
                    "timeout": config.audio.timeout,
                    "phrase_time_limit": config.audio.phrase_time_limit,
                    "tts_rate": config.audio.tts_rate,
                    "tts_volume": config.audio.tts_volume,
                    "tts_voice_preference": config.audio.tts_voice_preference,
                    "response_delay": config.audio.response_delay,
                    "coqui_model": config.audio.coqui_model,
                    "coqui_language": config.audio.coqui_language,
                    "coqui_device": config.audio.coqui_device,
                    "coqui_use_gpu": config.audio.coqui_use_gpu,
                    "coqui_speaker_wav": config.audio.coqui_speaker_wav,
                    "coqui_temperature": config.audio.coqui_temperature,
                    "coqui_length_penalty": config.audio.coqui_length_penalty,
                    "coqui_repetition_penalty": config.audio.coqui_repetition_penalty,
                    "coqui_top_k": config.audio.coqui_top_k,
                    "coqui_top_p": config.audio.coqui_top_p,
                    "coqui_streaming": config.audio.coqui_streaming,
                    "tts_fallback_voices": config.audio.tts_fallback_voices,
                    "tts_fallback_rate_cap": config.audio.tts_fallback_rate_cap,
                    "tts_fallback_enabled": config.audio.tts_fallback_enabled,
                },
                "conversation": {
                    "wake_word": config.conversation.wake_word,
                    "conversation_timeout": config.conversation.conversation_timeout,
                    "max_retries": config.conversation.max_retries,
                    "enable_full_duplex": config.conversation.enable_full_duplex,
                },
                "llm": {
                    "model": config.llm.model,
                    "verbose": config.llm.verbose,
                    "reasoning": config.llm.reasoning,
                    "temperature": config.llm.temperature,
                    "max_tokens": config.llm.max_tokens,
                },
                "logging": {
                    "level": config.logging.level,
                    "file": config.logging.file,
                    "format": config.logging.format,
                    "date_format": config.logging.date_format,
                },
                "general": {
                    "debug": config.general.debug,
                    "data_dir": str(config.general.data_dir),
                    "config_file": str(config.general.config_file) if config.general.config_file else None,
                }
            }
        except Exception as e:
            logger.error(f"Error getting configuration: {e}")
            return {"error": str(e)}

    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration with new values."""
        if not CONFIG_AVAILABLE:
            return {"success": False, "error": "Configuration system not available"}

        try:
            # Update environment variables
            env_vars = {}

            # Map configuration updates to environment variables
            if "audio" in updates:
                audio = updates["audio"]
                if "mic_index" in audio:
                    env_vars["JARVIS_MIC_INDEX"] = str(audio["mic_index"])
                if "mic_name" in audio:
                    env_vars["JARVIS_MIC_NAME"] = audio["mic_name"]
                if "energy_threshold" in audio:
                    env_vars["JARVIS_ENERGY_THRESHOLD"] = str(audio["energy_threshold"])
                if "timeout" in audio:
                    env_vars["JARVIS_AUDIO_TIMEOUT"] = str(audio["timeout"])
                if "phrase_time_limit" in audio:
                    env_vars["JARVIS_PHRASE_TIME_LIMIT"] = str(audio["phrase_time_limit"])
                if "tts_rate" in audio:
                    env_vars["JARVIS_TTS_RATE"] = str(audio["tts_rate"])
                if "tts_volume" in audio:
                    env_vars["JARVIS_TTS_VOLUME"] = str(audio["tts_volume"])
                if "tts_voice_preference" in audio:
                    env_vars["JARVIS_TTS_VOICE"] = audio["tts_voice_preference"]
                if "response_delay" in audio:
                    env_vars["JARVIS_RESPONSE_DELAY"] = str(audio["response_delay"])
                if "coqui_model" in audio:
                    env_vars["JARVIS_COQUI_MODEL"] = audio["coqui_model"]
                if "coqui_language" in audio:
                    env_vars["JARVIS_COQUI_LANGUAGE"] = audio["coqui_language"]
                if "coqui_device" in audio:
                    env_vars["JARVIS_COQUI_DEVICE"] = audio["coqui_device"]
                if "coqui_use_gpu" in audio:
                    env_vars["JARVIS_COQUI_USE_GPU"] = str(audio["coqui_use_gpu"]).lower()
                if "coqui_speaker_wav" in audio:
                    env_vars["JARVIS_COQUI_SPEAKER_WAV"] = audio["coqui_speaker_wav"] or ""
                if "coqui_temperature" in audio:
                    env_vars["JARVIS_COQUI_TEMPERATURE"] = str(audio["coqui_temperature"])
                if "coqui_length_penalty" in audio:
                    env_vars["JARVIS_COQUI_LENGTH_PENALTY"] = str(audio["coqui_length_penalty"])
                if "coqui_repetition_penalty" in audio:
                    env_vars["JARVIS_COQUI_REPETITION_PENALTY"] = str(audio["coqui_repetition_penalty"])
                if "coqui_top_k" in audio:
                    env_vars["JARVIS_COQUI_TOP_K"] = str(audio["coqui_top_k"])
                if "coqui_top_p" in audio:
                    env_vars["JARVIS_COQUI_TOP_P"] = str(audio["coqui_top_p"])
                if "coqui_streaming" in audio:
                    env_vars["JARVIS_COQUI_STREAMING"] = str(audio["coqui_streaming"]).lower()
                if "tts_fallback_voices" in audio:
                    env_vars["JARVIS_TTS_FALLBACK_VOICES"] = ",".join(audio["tts_fallback_voices"])
                if "tts_fallback_rate_cap" in audio:
                    env_vars["JARVIS_TTS_FALLBACK_RATE_CAP"] = str(audio["tts_fallback_rate_cap"])
                if "tts_fallback_enabled" in audio:
                    env_vars["JARVIS_TTS_FALLBACK_ENABLED"] = str(audio["tts_fallback_enabled"]).lower()

            if "conversation" in updates:
                conv = updates["conversation"]
                if "wake_word" in conv:
                    env_vars["JARVIS_WAKE_WORD"] = conv["wake_word"]
                if "conversation_timeout" in conv:
                    env_vars["JARVIS_CONVERSATION_TIMEOUT"] = str(conv["conversation_timeout"])
                if "max_retries" in conv:
                    env_vars["JARVIS_MAX_RETRIES"] = str(conv["max_retries"])
                if "enable_full_duplex" in conv:
                    env_vars["JARVIS_ENABLE_FULL_DUPLEX"] = str(conv["enable_full_duplex"]).lower()

            if "llm" in updates:
                llm = updates["llm"]
                if "model" in llm:
                    env_vars["JARVIS_MODEL"] = llm["model"]
                if "verbose" in llm:
                    env_vars["JARVIS_VERBOSE"] = str(llm["verbose"]).lower()
                if "reasoning" in llm:
                    env_vars["JARVIS_REASONING"] = str(llm["reasoning"]).lower()
                if "temperature" in llm:
                    env_vars["JARVIS_TEMPERATURE"] = str(llm["temperature"])
                if "max_tokens" in llm:
                    env_vars["JARVIS_MAX_TOKENS"] = str(llm["max_tokens"]) if llm["max_tokens"] else ""

            if "logging" in updates:
                log = updates["logging"]
                if "level" in log:
                    env_vars["JARVIS_LOG_LEVEL"] = log["level"]
                if "file" in log:
                    env_vars["JARVIS_LOG_FILE"] = log["file"] or ""
                if "format" in log:
                    env_vars["JARVIS_LOG_FORMAT"] = log["format"]
                if "date_format" in log:
                    env_vars["JARVIS_LOG_DATE_FORMAT"] = log["date_format"]

            if "general" in updates:
                gen = updates["general"]
                if "debug" in gen:
                    env_vars["JARVIS_DEBUG"] = str(gen["debug"]).lower()
                if "data_dir" in gen:
                    env_vars["JARVIS_DATA_DIR"] = gen["data_dir"] or ""
                if "config_file" in gen:
                    env_vars["JARVIS_CONFIG_FILE"] = gen["config_file"] or ""

            # Update .env file
            self._update_env_file(env_vars)

            # Trigger configuration reload and notify all components
            trigger_config_reload()

            return {"success": True, "message": "Configuration updated successfully. All components have been notified of the changes."}

        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return {"success": False, "error": str(e)}

    def _update_env_file(self, env_vars: Dict[str, str]):
        """Update the .env file with new environment variables."""
        # Read existing .env file
        existing_vars = {}
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        existing_vars[key] = value

        # Update with new values
        existing_vars.update(env_vars)

        # Write back to .env file
        self.env_file.parent.mkdir(exist_ok=True)
        with open(self.env_file, 'w') as f:
            f.write("# Jarvis Voice Assistant Configuration\n")
            f.write("# Updated via Web Interface\n\n")

            # Group by category
            categories = {
                "Audio Configuration": [k for k in existing_vars.keys() if k.startswith("JARVIS_") and any(x in k for x in ["MIC", "TTS", "AUDIO", "COQUI"])],
                "Conversation Configuration": [k for k in existing_vars.keys() if k.startswith("JARVIS_") and any(x in k for x in ["WAKE", "CONVERSATION", "RETRIES", "DUPLEX"])],
                "LLM Configuration": [k for k in existing_vars.keys() if k.startswith("JARVIS_") and any(x in k for x in ["MODEL", "VERBOSE", "REASONING", "TEMPERATURE", "TOKENS"])],
                "Logging Configuration": [k for k in existing_vars.keys() if k.startswith("JARVIS_") and any(x in k for x in ["LOG"])],
                "General Configuration": [k for k in existing_vars.keys() if k.startswith("JARVIS_") and any(x in k for x in ["DEBUG", "DATA", "CONFIG"])]
            }

            for category, keys in categories.items():
                if keys:
                    f.write(f"# {category}\n")
                    for key in sorted(keys):
                        if key in existing_vars:
                            f.write(f"{key}={existing_vars[key]}\n")
                    f.write("\n")


# Global configuration manager instance
config_manager = ConfigurationManager()


class JarvisUIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Jarvis UI web interface."""

    # Class variable to store server reference for shutdown
    _server_instance = None

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)

        if path == "/" or path == "/main":
            self.serve_main_page()
        elif path == "/status":
            self.serve_status_page()
        elif path == "/settings":
            self.serve_settings_page()
        elif path == "/audio":
            self.serve_audio_config_page()
        elif path == "/llm":
            self.serve_llm_config_page()
        elif path == "/conversation":
            self.serve_conversation_config_page()
        elif path == "/logging":
            self.serve_logging_config_page()
        elif path == "/general":
            self.serve_general_config_page()
        elif path == "/voice-profiles":
            self.serve_voice_profiles_page()
        elif path == "/device":
            self.serve_device_config_page()
        elif path == "/mcp":
            self.serve_mcp_page()
        elif path == "/api/status":
            self.serve_status_api()
        elif path == "/api/config":
            self.serve_config_api()
        elif path == "/api/config/reload":
            self.serve_config_reload_api()
        elif path == "/api/shutdown":
            self.serve_shutdown_api()
        elif path == "/api/close-window":
            self.serve_close_window_api()
        elif path == "/api/voice-profiles":
            self.serve_voice_profiles_api()
        elif path == "/api/device-info":
            self.serve_device_info_api()
        elif path == "/api/mcp/servers":
            self.serve_mcp_servers_api()
        elif path == "/api/mcp/tools":
            self.serve_mcp_tools_api()
        else:
            self.serve_404()

    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/api/config":
            self.handle_config_update()
        elif path == "/api/config/reload":
            self.handle_config_reload()
        elif path == "/api/shutdown":
            self.handle_shutdown()
        elif path == "/api/close-window":
            self.handle_close_window()
        elif path == "/api/voice-profiles":
            self.handle_voice_profile_action()
        elif path == "/api/mcp/servers":
            self.handle_mcp_server_action()
        elif path == "/api/mcp/connect":
            self.handle_mcp_connect_action()
        elif path == "/api/mcp/disconnect":
            self.handle_mcp_disconnect_action()
        elif path == "/api/mcp/tools/toggle":
            self.handle_mcp_tool_toggle()
        else:
            self.serve_404()

    def serve_main_page(self):
        """Serve the main dashboard page."""
        html = self.get_html_template("Jarvis Dashboard", self.get_main_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_status_page(self):
        """Serve the status page."""
        html = self.get_html_template("System Status", self.get_status_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_status_api(self):
        """Serve status data as JSON API."""
        try:
            import psutil
            import platform

            status_data = {
                "system": {
                    "platform": f"{platform.system()} {platform.release()}",
                    "python": platform.python_version(),
                    "cpu_usage": psutil.cpu_percent(interval=0.1),
                    "memory_usage": psutil.virtual_memory().percent,
                    "available_memory": round(psutil.virtual_memory().available / (1024**3), 1)
                },
                "audio": {
                    "speech_recognition": "Whisper (Local)",
                    "tts": "Apple System Voices",
                    "microphone": "Active"
                },
                "jarvis": {
                    "status": "Running",
                    "wake_word": "Active",
                    "conversation": "Ready"
                }
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status_data, indent=2).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def serve_404(self):
        """Serve 404 page."""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>404 - Page Not Found</h1>")

    def serve_settings_page(self):
        """Serve the main settings page."""
        html = self.get_html_template("Settings Overview", self.get_settings_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_audio_config_page(self):
        """Serve the audio configuration page."""
        html = self.get_html_template("Audio Configuration", self.get_audio_config_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_llm_config_page(self):
        """Serve the LLM configuration page."""
        html = self.get_html_template("LLM Configuration", self.get_llm_config_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_conversation_config_page(self):
        """Serve the conversation configuration page."""
        html = self.get_html_template("Conversation Configuration", self.get_conversation_config_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_logging_config_page(self):
        """Serve the logging configuration page."""
        html = self.get_html_template("Logging Configuration", self.get_logging_config_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_general_config_page(self):
        """Serve the general configuration page."""
        html = self.get_html_template("General Configuration", self.get_general_config_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_voice_profiles_page(self):
        """Serve the voice profiles page."""
        html = self.get_html_template("Voice Profiles", self.get_voice_profiles_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_device_config_page(self):
        """Serve the device configuration page."""
        html = self.get_html_template("Device Configuration", self.get_device_config_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_mcp_page(self):
        """Serve the MCP management page."""
        html = self.get_html_template("MCP Tools & Servers", self.get_mcp_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_config_api(self):
        """Serve configuration data as JSON API."""
        try:
            config_data = config_manager.get_current_config()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(config_data, indent=2).encode())
        except Exception as e:
            logger.error(f"Error serving config API: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def serve_config_reload_api(self):
        """Serve configuration reload API."""
        try:
            if not CONFIG_AVAILABLE:
                result = {"success": False, "error": "Configuration system not available"}
            else:
                # Trigger configuration reload
                new_config = trigger_config_reload()
                result = {
                    "success": True,
                    "message": "Configuration reloaded successfully. All components have been notified.",
                    "timestamp": time.time()
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            logger.error(f"Error reloading configuration: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def serve_shutdown_api(self):
        """Serve shutdown API for graceful server shutdown."""
        try:
            result = {
                "success": True,
                "message": "Jarvis UI server is shutting down...",
                "timestamp": time.time()
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

            # Schedule shutdown after response is sent
            def delayed_shutdown():
                time.sleep(1)  # Give time for response to be sent
                logger.info("Shutting down Jarvis UI server via API request")
                # Get the server instance from the class variable
                server = JarvisUIHandler._server_instance
                if server and hasattr(server, 'shutdown'):
                    server.shutdown()
                    server.server_close()
                else:
                    # Fallback: exit the process
                    import os
                    os._exit(0)

            threading.Thread(target=delayed_shutdown, daemon=True).start()

        except Exception as e:
            logger.error(f"Error handling shutdown request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def serve_voice_profiles_api(self):
        """Serve voice profiles data as JSON API."""
        try:
            if not CONFIG_AVAILABLE:
                profiles_data = {"error": "Voice profiles not available"}
            else:
                # TODO: Implement voice profiles API
                profiles_data = {"profiles": [], "message": "Voice profiles feature coming soon"}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(profiles_data, indent=2).encode())
        except Exception as e:
            logger.error(f"Error serving voice profiles API: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def serve_device_info_api(self):
        """Serve device information as JSON API."""
        try:
            device_info = {
                "system": {
                    "platform": platform.system(),
                    "platform_release": platform.release(),
                    "platform_version": platform.version(),
                    "architecture": platform.machine(),
                    "processor": platform.processor(),
                    "python_version": platform.python_version(),
                    "python_implementation": platform.python_implementation(),
                },
                "hardware": {
                    "cpu_count": psutil.cpu_count(),
                    "cpu_count_logical": psutil.cpu_count(logical=True),
                    "memory_total": round(psutil.virtual_memory().total / (1024**3), 2),
                    "memory_available": round(psutil.virtual_memory().available / (1024**3), 2),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": {
                        "total": round(psutil.disk_usage('/').total / (1024**3), 2),
                        "used": round(psutil.disk_usage('/').used / (1024**3), 2),
                        "free": round(psutil.disk_usage('/').free / (1024**3), 2),
                        "percent": round((psutil.disk_usage('/').used / psutil.disk_usage('/').total) * 100, 1)
                    }
                },
                "network": {
                    "hostname": platform.node(),
                    "interfaces": list(psutil.net_if_addrs().keys())
                }
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(device_info, indent=2).encode())
        except Exception as e:
            logger.error(f"Error serving device info API: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def serve_mcp_servers_api(self):
        """Serve MCP servers information as JSON API."""
        try:
            # Get MCP client manager
            from jarvis.tools import get_mcp_client
            mcp_client = get_mcp_client()

            # Get all servers
            all_servers = mcp_client.get_all_servers()

            # Format server data for UI
            servers_data = {"servers": {}}
            for server_name, server_info in all_servers.items():
                servers_data["servers"][server_name] = {
                    "config": {
                        "name": server_info.config.name,
                        "transport": server_info.config.transport.value,
                        "command": server_info.config.command,
                        "args": server_info.config.args,
                        "url": server_info.config.url,
                        "enabled": server_info.config.enabled
                    },
                    "status": server_info.status.value,
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "enabled": tool.enabled
                        }
                        for tool in server_info.tools
                    ],
                    "last_error": server_info.last_error,
                    "connected_at": server_info.connected_at
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(servers_data, indent=2).encode())
        except Exception as e:
            logger.error(f"Error serving MCP servers API: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def serve_mcp_tools_api(self):
        """Serve MCP tools information as JSON API."""
        try:
            # Get MCP client manager
            from jarvis.tools import get_mcp_client
            mcp_client = get_mcp_client()

            # Get all tools
            all_tools = mcp_client.get_all_tools()

            # Format tools data for UI
            tools_data = {"tools": {}}
            for tool in all_tools:
                tool_key = f"{tool.server_name}:{tool.name}"
                tools_data["tools"][tool_key] = {
                    "name": tool.name,
                    "description": tool.description,
                    "server_name": tool.server_name,
                    "enabled": tool.enabled,
                    "parameters": tool.parameters
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(tools_data, indent=2).encode())
        except Exception as e:
            logger.error(f"Error serving MCP tools API: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def handle_mcp_server_action(self):
        """Handle MCP server management actions."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            action = data.get('action')

            # Get MCP client manager
            from jarvis.tools import get_mcp_client
            from jarvis.core.mcp_client import MCPServerConfig, MCPTransportType
            mcp_client = get_mcp_client()

            if action == 'add':
                # Create server configuration
                config = MCPServerConfig(
                    name=data.get('name'),
                    transport=MCPTransportType(data.get('transport')),
                    enabled=data.get('enabled', True),
                    command=data.get('command'),
                    args=data.get('args', []),
                    env=data.get('env', {}),
                    cwd=data.get('cwd'),
                    url=data.get('url'),
                    headers=data.get('headers', {}),
                    timeout=data.get('timeout', 30)
                )

                success = mcp_client.add_server(config)
                result = {"success": success, "message": "Server added successfully" if success else "Failed to add server"}

            elif action == 'remove':
                server_name = data.get('name')
                success = mcp_client.remove_server(server_name)
                result = {"success": success, "message": "Server removed successfully" if success else "Failed to remove server"}

            elif action == 'test':
                # For test, create a temporary config and try to validate it
                try:
                    config = MCPServerConfig(
                        name=data.get('name', 'test'),
                        transport=MCPTransportType(data.get('transport')),
                        command=data.get('command'),
                        args=data.get('args', []),
                        url=data.get('url'),
                        headers=data.get('headers', {}),
                        timeout=data.get('timeout', 30)
                    )
                    config.validate()
                    result = {"success": True, "message": "Configuration is valid"}
                except Exception as e:
                    result = {"success": False, "error": f"Configuration error: {str(e)}"}
            else:
                result = {"success": False, "error": "Unknown action"}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            logger.error(f"Error handling MCP server action: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_mcp_connect_action(self):
        """Handle MCP server connect action."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            server_name = data.get('server')

            # Get MCP client manager
            from jarvis.tools import get_mcp_client
            mcp_client = get_mcp_client()

            # Connect to server asynchronously
            import asyncio
            if mcp_client.event_loop:
                future = asyncio.run_coroutine_threadsafe(
                    mcp_client.connect_server(server_name),
                    mcp_client.event_loop
                )
                success = future.result(timeout=10)  # 10 second timeout
                result = {"success": success, "message": f"Connected to {server_name}" if success else f"Failed to connect to {server_name}"}
            else:
                result = {"success": False, "error": "MCP system not running"}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            logger.error(f"Error handling MCP connect action: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_mcp_disconnect_action(self):
        """Handle MCP server disconnect action."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            server_name = data.get('server')

            # Get MCP client manager
            from jarvis.tools import get_mcp_client
            mcp_client = get_mcp_client()

            # Disconnect from server asynchronously
            import asyncio
            if mcp_client.event_loop:
                future = asyncio.run_coroutine_threadsafe(
                    mcp_client.disconnect_server(server_name),
                    mcp_client.event_loop
                )
                future.result(timeout=5)  # 5 second timeout
                result = {"success": True, "message": f"Disconnected from {server_name}"}
            else:
                result = {"success": False, "error": "MCP system not running"}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            logger.error(f"Error handling MCP disconnect action: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_mcp_tool_toggle(self):
        """Handle MCP tool enable/disable toggle."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            tool_name = data.get('tool')
            enabled = data.get('enabled', True)

            # Get MCP tool manager
            from jarvis.tools import get_mcp_tool_manager
            mcp_tool_manager = get_mcp_tool_manager()

            # Toggle tool
            if enabled:
                success = mcp_tool_manager.enable_tool(tool_name)
            else:
                success = mcp_tool_manager.disable_tool(tool_name)

            result = {
                "success": success,
                "message": f"Tool {tool_name} {'enabled' if enabled else 'disabled'}" if success else f"Failed to {'enable' if enabled else 'disable'} tool {tool_name}"
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            logger.error(f"Error handling MCP tool toggle: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_config_update(self):
        """Handle configuration update requests."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            updates = json.loads(post_data.decode('utf-8'))

            result = config_manager.update_config(updates)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            logger.error(f"Error handling config update: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_config_reload(self):
        """Handle configuration reload requests."""
        try:
            if not CONFIG_AVAILABLE:
                result = {"success": False, "error": "Configuration system not available"}
            else:
                # Trigger configuration reload
                new_config = trigger_config_reload()
                result = {
                    "success": True,
                    "message": "Configuration reloaded successfully. All components have been notified.",
                    "timestamp": time.time()
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            logger.error(f"Error handling config reload: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_shutdown(self):
        """Handle shutdown requests."""
        try:
            result = {
                "success": True,
                "message": "Jarvis UI server is shutting down...",
                "timestamp": time.time()
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

            # Schedule shutdown after response is sent
            def delayed_shutdown():
                time.sleep(1)  # Give time for response to be sent
                logger.info("Shutting down Jarvis UI server via API request")
                if hasattr(self.server, 'shutdown'):
                    self.server.shutdown()

            threading.Thread(target=delayed_shutdown, daemon=True).start()

        except Exception as e:
            logger.error(f"Error handling shutdown request: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def serve_close_window_api(self):
        """Serve close window API for desktop app window closure."""
        try:
            result = {
                "success": True,
                "message": "Desktop window close signal sent",
                "action": "close_window"
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            logger.error(f"Error serving close window API: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_close_window(self):
        """Handle close window requests."""
        try:
            result = {
                "success": True,
                "message": "Desktop window close signal sent",
                "action": "close_window"
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            logger.error(f"Error handling close window: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_voice_profile_action(self):
        """Handle voice profile actions."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            action_data = json.loads(post_data.decode('utf-8'))

            # TODO: Implement voice profile actions
            result = {"success": False, "error": "Voice profile actions not yet implemented"}

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            logger.error(f"Error handling voice profile action: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def get_html_template(self, title: str, content: str) -> str:
        """Get the HTML template with the specified title and content."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Jarvis Control Panel</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #e0e6ed;
            display: flex;
        }}
        .sidebar {{
            width: 280px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px 0;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            z-index: 1000;
        }}
        .sidebar-header {{
            padding: 0 20px 30px 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 20px;
        }}
        .sidebar-header h1 {{
            color: #ffffff;
            margin: 0;
            font-size: 1.8em;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            text-align: center;
        }}
        .sidebar-header .subtitle {{
            color: #b8c5d1;
            font-size: 0.9em;
            text-align: center;
            margin-top: 5px;
        }}
        .nav {{
            padding: 0;
        }}
        .nav-section {{
            margin-bottom: 25px;
        }}
        .nav-section-title {{
            color: #6495ed;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 0 20px 10px 20px;
            margin-bottom: 10px;
        }}
        .nav a {{
            color: #e0e6ed;
            text-decoration: none;
            padding: 12px 20px;
            display: block;
            border-left: 3px solid transparent;
            transition: all 0.3s ease;
            position: relative;
        }}
        .nav a:hover {{
            background: rgba(100, 149, 237, 0.1);
            border-left-color: rgba(100, 149, 237, 0.5);
            color: #ffffff;
        }}
        .nav a.active {{
            background: rgba(100, 149, 237, 0.2);
            border-left-color: #6495ed;
            color: #ffffff;
        }}
        .nav a .icon {{
            display: inline-block;
            width: 20px;
            margin-right: 12px;
            text-align: center;
        }}
        .main-content {{
            flex: 1;
            margin-left: 280px;
            padding: 20px;
            min-height: 100vh;
        }}
        .content {{
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            max-width: 1200px;
        }}
        .page-header {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .page-header h1 {{
            color: #ffffff;
            margin: 0 0 10px 0;
            font-size: 2.2em;
        }}
        .page-header .breadcrumb {{
            color: #b8c5d1;
            font-size: 0.9em;
        }}
        .page-header .breadcrumb a {{
            color: #6495ed;
            text-decoration: none;
        }}
        .page-header .breadcrumb a:hover {{
            text-decoration: underline;
        }}
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .status-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #6495ed;
            transition: all 0.3s ease;
        }}
        .status-card:hover {{
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(100, 149, 237, 0.3);
            transform: translateY(-2px);
        }}
        .status-card h3 {{
            margin-top: 0;
            color: #ffffff;
            font-weight: 600;
        }}
        .status-item {{
            margin: 10px 0;
            padding: 5px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            color: #b8c5d1;
        }}
        .status-item:last-child {{
            border-bottom: none;
        }}
        .status-item strong {{
            color: #e0e6ed;
        }}
        h2 {{
            color: #ffffff;
            margin-top: 0;
        }}
        p {{
            color: #b8c5d1;
            line-height: 1.6;
        }}
        .config-form {{
            max-width: 800px;
            margin: 0 auto;
        }}
        .config-section {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .config-section h3 {{
            color: #ffffff;
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        .form-group {{
            margin-bottom: 15px;
        }}
        .form-group label {{
            display: block;
            color: #e0e6ed;
            margin-bottom: 5px;
            font-weight: 500;
        }}
        .form-group input, .form-group select, .form-group textarea {{
            width: 100%;
            padding: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            font-size: 14px;
            box-sizing: border-box;
        }}
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {{
            outline: none;
            border-color: rgba(100, 149, 237, 0.5);
            box-shadow: 0 0 0 2px rgba(100, 149, 237, 0.2);
        }}
        .form-group input[type="checkbox"] {{
            width: auto;
            margin-right: 8px;
        }}
        .form-group .checkbox-label {{
            display: flex;
            align-items: center;
            cursor: pointer;
        }}
        .form-group small {{
            color: #b8c5d1;
            font-size: 12px;
            margin-top: 5px;
            display: block;
        }}
        .btn {{
            background: rgba(100, 149, 237, 0.8);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        .btn:hover {{
            background: rgba(100, 149, 237, 1);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(100, 149, 237, 0.3);
        }}
        .btn-secondary {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .btn-secondary:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}
        .btn-danger {{
            background: rgba(220, 53, 69, 0.8);
            border: 1px solid rgba(220, 53, 69, 0.9);
            color: white;
        }}
        .btn-danger:hover {{
            background: rgba(220, 53, 69, 1);
            border: 1px solid rgba(220, 53, 69, 1);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(220, 53, 69, 0.3);
        }}
        .alert {{
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .alert-success {{
            background: rgba(34, 197, 94, 0.2);
            border: 1px solid rgba(34, 197, 94, 0.3);
            color: #86efac;
        }}
        .alert-error {{
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
        }}
        .form-actions {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }}
        .form-actions .btn {{
            margin: 0 10px;
        }}
        .config-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }}
        .voice-profile-card {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
        }}
        .voice-profile-card h4 {{
            color: #ffffff;
            margin: 0 0 10px 0;
        }}
        .voice-profile-meta {{
            color: #b8c5d1;
            font-size: 12px;
            margin-bottom: 10px;
        }}
        .voice-profile-actions {{
            display: flex;
            gap: 10px;
        }}
        .voice-profile-actions .btn {{
            padding: 6px 12px;
            font-size: 12px;
        }}

        /* Mobile Responsive Design */
        @media (max-width: 768px) {{
            .sidebar {{
                width: 100%;
                height: auto;
                position: relative;
                border-right: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .main-content {{
                margin-left: 0;
                padding: 10px;
            }}
            .nav {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                padding: 10px;
            }}
            .nav-section {{
                margin-bottom: 0;
            }}
            .nav-section-title {{
                display: none;
            }}
            .nav a {{
                padding: 8px 12px;
                border-radius: 20px;
                border-left: none;
                background: rgba(255, 255, 255, 0.1);
                font-size: 0.9em;
            }}
            .nav a .icon {{
                margin-right: 5px;
            }}
            .sidebar-header h1 {{
                font-size: 1.5em;
            }}
            .page-header h1 {{
                font-size: 1.8em;
            }}
            .config-grid {{
                grid-template-columns: 1fr;
            }}
            .form-actions .btn {{
                width: 100%;
                margin: 5px 0;
            }}
        }}

        /* Tablet Responsive Design */
        @media (max-width: 1024px) and (min-width: 769px) {{
            .sidebar {{
                width: 240px;
            }}
            .main-content {{
                margin-left: 240px;
            }}
            .config-grid {{
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            }}
        }}
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="sidebar-header">
            <h1>Jarvis</h1>
            <div class="subtitle">Control Panel</div>
        </div>

        <nav class="nav">
            <div class="nav-section">
                <div class="nav-section-title">Main</div>
                <a href="/" class="nav-link" data-page="dashboard">
                    <span class="icon">🏠</span>Dashboard
                </a>
                <a href="/status" class="nav-link" data-page="status">
                    <span class="icon">📊</span>Status
                </a>
                <a href="/settings" class="nav-link" data-page="settings">
                    <span class="icon">⚙️</span>Settings
                </a>
            </div>

            <div class="nav-section">
                <div class="nav-section-title">Configuration</div>
                <a href="/audio" class="nav-link" data-page="audio">
                    <span class="icon">🎤</span>Audio Config
                </a>
                <a href="/llm" class="nav-link" data-page="llm">
                    <span class="icon">🤖</span>LLM Config
                </a>
                <a href="/conversation" class="nav-link" data-page="conversation">
                    <span class="icon">💬</span>Conversation
                </a>
                <a href="/logging" class="nav-link" data-page="logging">
                    <span class="icon">📝</span>Logging
                </a>
                <a href="/general" class="nav-link" data-page="general">
                    <span class="icon">🔧</span>General
                </a>
            </div>

            <div class="nav-section">
                <div class="nav-section-title">Advanced</div>
                <a href="/voice-profiles" class="nav-link" data-page="voice-profiles">
                    <span class="icon">🎭</span>Voice Profiles
                </a>
                <a href="/device" class="nav-link" data-page="device">
                    <span class="icon">💻</span>Device Info
                </a>
                <a href="/mcp" class="nav-link" data-page="mcp">
                    <span class="icon">🔗</span>MCP Tools
                </a>
            </div>
        </nav>
    </div>

    <div class="main-content">
        <div class="content">
            {content}
        </div>
    </div>

    <script>
    // Highlight active navigation item
    function setActiveNav() {{
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');

        navLinks.forEach(link => {{
            link.classList.remove('active');
            if (link.getAttribute('href') === currentPath ||
                (currentPath === '/' && link.getAttribute('href') === '/') ||
                (currentPath === '/main' && link.getAttribute('href') === '/')) {{
                link.classList.add('active');
            }}
        }});
    }}

    // Monitor server status and close window when server shuts down (desktop app only)
    function startServerMonitoring() {{
        let consecutiveFailures = 0;
        const maxFailures = 3;

        function checkServerStatus() {{
            fetch('/api/config', {{
                method: 'GET'
            }})
            .then(response => {{
                if (response.ok) {{
                    consecutiveFailures = 0;
                }} else {{
                    consecutiveFailures++;
                }}
            }})
            .catch(error => {{
                consecutiveFailures++;
                console.log('Server check failed:', error);

                if (consecutiveFailures >= maxFailures) {{
                    console.log('Server appears to be down, closing window...');
                    closeDesktopWindow();
                }}
            }});
        }}

        // Check every 2 seconds
        setInterval(checkServerStatus, 2000);
    }}

    // Close desktop window using various methods
    function closeDesktopWindow() {{
        try {{
            // Method 1: pywebview API (newer versions)
            if (window.pywebview && window.pywebview.api && window.pywebview.api.close_window) {{
                window.pywebview.api.close_window();
                return;
            }}

            // Method 2: pywebview destroy (older versions)
            if (window.pywebview && window.pywebview.destroy) {{
                window.pywebview.destroy();
                return;
            }}

            // Method 3: Standard window close
            window.close();

        }} catch (error) {{
            console.log('Error closing window:', error);
            // Fallback: just try window.close()
            window.close();
        }}
    }}

    // Set active nav on page load and start monitoring if desktop app
    document.addEventListener('DOMContentLoaded', function() {{
        setActiveNav();

        // Start monitoring server status for desktop app auto-close
        if (window.pywebview || navigator.userAgent.includes('pywebview')) {{
            console.log('Desktop app detected, starting server monitoring...');
            startServerMonitoring();
        }}
    }});
    </script>
</body>
</html>
        """

    def get_main_content(self) -> str:
        """Get the main dashboard content."""
        return """
        <div class="page-header">
            <h1>Dashboard</h1>
            <div class="breadcrumb">
                <a href="/">Home</a> / Dashboard
            </div>
        </div>

        <h2>Welcome to Jarvis Control Panel</h2>
        <p>This is your voice-activated control panel for the Jarvis Voice Assistant.</p>

        <h3>Quick Actions</h3>
        <p>You can access this panel anytime by saying:</p>
        <ul>
            <li><strong>"Jarvis, open settings"</strong></li>
            <li><strong>"Jarvis, show control panel"</strong></li>
            <li><strong>"Jarvis, open dashboard"</strong></li>
        </ul>

        <h3>Available Sections</h3>
        <div class="status-grid">
            <div class="status-card">
                <h4>System Status</h4>
                <p>Monitor real-time system performance, memory usage, and Jarvis status.</p>
            </div>
            <div class="status-card">
                <h4>Audio Configuration</h4>
                <p>Configure microphone settings, TTS voices, and audio quality.</p>
            </div>
            <div class="status-card">
                <h4>Performance Monitor</h4>
                <p>View performance metrics and optimize system settings.</p>
            </div>
            <div class="status-card">
                <h4>Tool Management</h4>
                <p>Manage available tools, plugins, and extensions.</p>
            </div>
        </div>
        """

    def get_status_content(self) -> str:
        """Get the status page content."""
        return """
        <div class="page-header">
            <h1>System Status</h1>
            <div class="breadcrumb">
                <a href="/">Home</a> / <a href="/status">Status</a>
            </div>
        </div>

        <div id="status-content">
            <p>Loading system status...</p>
        </div>

        <script>
        async function loadStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();

                const statusHtml = `
                    <div class="status-grid">
                        <div class="status-card">
                            <h3>🖥️ System Information</h3>
                            <div class="status-item"><strong>Platform:</strong> ${data.system.platform}</div>
                            <div class="status-item"><strong>Python:</strong> ${data.system.python}</div>
                            <div class="status-item"><strong>CPU Usage:</strong> ${data.system.cpu_usage.toFixed(1)}%</div>
                            <div class="status-item"><strong>Memory Usage:</strong> ${data.system.memory_usage.toFixed(1)}%</div>
                            <div class="status-item"><strong>Available Memory:</strong> ${data.system.available_memory} GB</div>
                        </div>

                        <div class="status-card">
                            <h3>Audio Status</h3>
                            <div class="status-item"><strong>Speech Recognition:</strong> ${data.audio.speech_recognition}</div>
                            <div class="status-item"><strong>Text-to-Speech:</strong> ${data.audio.tts}</div>
                            <div class="status-item"><strong>Microphone:</strong> ${data.audio.microphone}</div>
                        </div>

                        <div class="status-card">
                            <h3>Jarvis Status</h3>
                            <div class="status-item"><strong>Voice Assistant:</strong> ${data.jarvis.status}</div>
                            <div class="status-item"><strong>Wake Word Detection:</strong> ${data.jarvis.wake_word}</div>
                            <div class="status-item"><strong>Conversation Mode:</strong> ${data.jarvis.conversation}</div>
                        </div>
                    </div>
                `;

                document.getElementById('status-content').innerHTML = statusHtml;
            } catch (error) {
                document.getElementById('status-content').innerHTML = '<p>Error loading status: ' + error.message + '</p>';
            }
        }

        loadStatus();
        setInterval(loadStatus, 5000); // Refresh every 5 seconds
        </script>
        """

    def get_settings_content(self) -> str:
        """Get the settings overview content."""
        return """
        <div class="page-header">
            <h1>Configuration Overview</h1>
            <div class="breadcrumb">
                <a href="/">Home</a> / <a href="/settings">Settings</a>
            </div>
        </div>

        <p>Manage all aspects of your Jarvis Voice Assistant configuration.</p>

        <div class="config-grid">
            <div class="status-card">
                <h3>Audio Configuration</h3>
                <p>Configure microphone settings, TTS voices, Coqui TTS parameters, and audio quality settings.</p>
                <a href="/audio" class="btn">Configure Audio</a>
            </div>

            <div class="status-card">
                <h3>LLM Configuration</h3>
                <p>Set up language model parameters, temperature, token limits, and reasoning capabilities.</p>
                <a href="/llm" class="btn">Configure LLM</a>
            </div>

            <div class="status-card">
                <h3>Conversation Settings</h3>
                <p>Customize wake word, conversation timeout, retry behavior, and duplex mode.</p>
                <a href="/conversation" class="btn">Configure Conversation</a>
            </div>

            <div class="status-card">
                <h3>Voice Profiles</h3>
                <p>Manage voice cloning profiles for personalized TTS output using Coqui TTS.</p>
                <a href="/voice-profiles" class="btn">Manage Profiles</a>
            </div>

            <div class="status-card">
                <h3>Device Settings</h3>
                <p>View device information, hardware capabilities, and system configuration.</p>
                <a href="/device" class="btn">View Device Info</a>
            </div>

            <div class="status-card">
                <h3>Logging Configuration</h3>
                <p>Configure logging levels, output files, and log formatting options.</p>
                <a href="/logging" class="btn">Configure Logging</a>
            </div>

            <div class="status-card">
                <h3>General Settings</h3>
                <p>Debug mode, data directories, and other general application settings.</p>
                <a href="/general" class="btn">General Settings</a>
            </div>

            <div class="status-card">
                <h3>MCP Tools & Servers</h3>
                <p>Manage Model Context Protocol servers and discover external tools and integrations.</p>
                <a href="/mcp" class="btn">Manage MCP</a>
            </div>
        </div>

        <div class="form-actions">
            <button class="btn" onclick="exportConfig()">Export Configuration</button>
            <button class="btn" onclick="reloadConfig()">Reload Configuration</button>
            <button class="btn btn-secondary" onclick="resetToDefaults()">Reset to Defaults</button>
            <button class="btn btn-danger" onclick="shutdownUI()">Shutdown UI</button>
        </div>

        <script>
        function exportConfig() {
            fetch('/api/config')
                .then(response => response.json())
                .then(data => {
                    const blob = new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'jarvis-config.json';
                    a.click();
                    URL.revokeObjectURL(url);
                })
                .catch(error => alert('Error exporting configuration: ' + error.message));
        }

        function reloadConfig() {
            if (confirm('Reload configuration from .env file and notify all components?')) {
                fetch('/api/config/reload', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('Configuration reloaded successfully! All components have been notified of the changes.');
                        // Refresh the page to show updated values
                        window.location.reload();
                    } else {
                        alert('Error reloading configuration: ' + (data.error || 'Unknown error'));
                    }
                })
                .catch(error => alert('Error reloading configuration: ' + error.message));
            }
        }

        function resetToDefaults() {
            if (confirm('Are you sure you want to reset all settings to defaults? This cannot be undone.')) {
                // TODO: Implement reset to defaults
                alert('Reset to defaults feature coming soon.');
            }
        }

        function shutdownUI() {{
            if (confirm('Are you sure you want to shutdown the Jarvis UI server?')) {{
                // For desktop app, send close window signal first
                if (window.pywebview || navigator.userAgent.includes('pywebview')) {{
                    fetch('/api/close-window', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }})
                    .then(() => {{
                        // Then shutdown the server
                        return fetch('/api/shutdown', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }}
                        }});
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.success) {{
                            // Desktop window should close automatically via monitoring
                            closeDesktopWindow();
                        }}
                    }})
                    .catch(error => {{
                        // Server is shutting down, close window
                        closeDesktopWindow();
                    }});
                }} else {{
                    // Browser - just shutdown normally
                    fetch('/api/shutdown', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }}
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.success) {{
                            alert('Jarvis UI server is shutting down. You can close this browser tab.');
                            setTimeout(() => {{
                                window.close();
                            }}, 2000);
                        }} else {{
                            alert('Error shutting down UI: ' + (data.error || 'Unknown error'));
                        }}
                    }})
                    .catch(error => {{
                        alert('Jarvis UI server has been shut down. You can close this browser tab.');
                        setTimeout(() => {{
                            window.close();
                        }}, 2000);
                    }});
                }}
            }}
        }}
        </script>
        """

    def get_audio_config_content(self) -> str:
        """Get the audio configuration content."""
        # Embedded audio configuration content for reliability
        return """
        <div class="page-header">
            <h1>Audio Configuration</h1>
            <div class="breadcrumb">
                <a href="/">Home</a> / <a href="/settings">Settings</a> / <a href="/audio">Audio</a>
            </div>
        </div>

        <p>Configure all audio-related settings for Jarvis Voice Assistant.</p>

        <form id="audio-config-form" class="config-form">
            <div class="config-section">
                <h3>Microphone Settings</h3>

                <div class="form-group">
                    <label for="mic_index">Microphone Index</label>
                    <input type="number" id="mic_index" name="mic_index" min="0" max="10">
                    <small>Index of the microphone device to use (0 = default)</small>
                </div>

                <div class="form-group">
                    <label for="mic_name">Microphone Name</label>
                    <input type="text" id="mic_name" name="mic_name">
                    <small>Name of the preferred microphone device</small>
                </div>

                <div class="form-group">
                    <label for="energy_threshold">Energy Threshold</label>
                    <input type="number" id="energy_threshold" name="energy_threshold" min="50" max="1000">
                    <small>Minimum audio energy to consider as speech (50-1000)</small>
                </div>

                <div class="form-group">
                    <label for="timeout">Audio Timeout (seconds)</label>
                    <input type="number" id="timeout" name="timeout" min="1" max="10" step="0.1">
                    <small>Maximum time to wait for speech input</small>
                </div>

                <div class="form-group">
                    <label for="phrase_time_limit">Phrase Time Limit (seconds)</label>
                    <input type="number" id="phrase_time_limit" name="phrase_time_limit" min="1" max="30" step="0.1">
                    <small>Maximum duration for a single phrase</small>
                </div>
            </div>

            <div class="config-section">
                <h3>Text-to-Speech Settings</h3>

                <div class="form-group">
                    <label for="tts_rate">TTS Rate (WPM)</label>
                    <input type="number" id="tts_rate" name="tts_rate" min="100" max="300">
                    <small>Speech rate in words per minute</small>
                </div>

                <div class="form-group">
                    <label for="tts_volume">TTS Volume</label>
                    <input type="number" id="tts_volume" name="tts_volume" min="0" max="1" step="0.1">
                    <small>Speech volume (0.0 to 1.0)</small>
                </div>

                <div class="form-group">
                    <label for="tts_voice_preference">Preferred Voice</label>
                    <select id="tts_voice_preference" name="tts_voice_preference">
                        <option value="Daniel">Daniel (British Male)</option>
                        <option value="Alex">Alex (US Male)</option>
                        <option value="Victoria">Victoria (US Female)</option>
                        <option value="Samantha">Samantha (US Female)</option>
                    </select>
                    <small>Preferred system voice for TTS</small>
                </div>

                <div class="form-group">
                    <label for="response_delay">Response Delay (seconds)</label>
                    <input type="number" id="response_delay" name="response_delay" min="0" max="2" step="0.1">
                    <small>Delay after speech completion before listening again</small>
                </div>
            </div>

            <div class="config-section">
                <h3>Coqui TTS Settings</h3>

                <div class="form-group">
                    <label for="coqui_model">Coqui Model</label>
                    <select id="coqui_model" name="coqui_model">
                        <option value="tts_models/multilingual/multi-dataset/xtts_v2">XTTS v2 (Multilingual)</option>
                        <option value="tts_models/en/ljspeech/tacotron2-DDC">Tacotron2 (English)</option>
                        <option value="tts_models/en/ljspeech/glow-tts">Glow-TTS (English)</option>
                    </select>
                    <small>Coqui TTS model to use for voice synthesis</small>
                </div>

                <div class="form-group">
                    <label for="coqui_language">Language</label>
                    <select id="coqui_language" name="coqui_language">
                        <option value="en">English</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                        <option value="de">German</option>
                        <option value="it">Italian</option>
                        <option value="pt">Portuguese</option>
                        <option value="pl">Polish</option>
                        <option value="tr">Turkish</option>
                        <option value="ru">Russian</option>
                        <option value="nl">Dutch</option>
                        <option value="cs">Czech</option>
                        <option value="ar">Arabic</option>
                        <option value="zh-cn">Chinese (Simplified)</option>
                        <option value="ja">Japanese</option>
                        <option value="hu">Hungarian</option>
                        <option value="ko">Korean</option>
                    </select>
                    <small>Language for Coqui TTS synthesis</small>
                </div>

                <div class="form-group">
                    <label for="coqui_device">Device</label>
                    <select id="coqui_device" name="coqui_device">
                        <option value="auto">Auto</option>
                        <option value="cpu">CPU</option>
                        <option value="cuda">CUDA (NVIDIA GPU)</option>
                        <option value="mps">MPS (Apple Silicon)</option>
                    </select>
                    <small>Device to use for Coqui TTS processing</small>
                </div>

                <div class="form-group">
                    <div class="checkbox-label">
                        <input type="checkbox" id="coqui_use_gpu" name="coqui_use_gpu">
                        <label for="coqui_use_gpu">Use GPU Acceleration</label>
                    </div>
                    <small>Enable GPU acceleration if available</small>
                </div>

                <div class="form-group">
                    <label for="coqui_speaker_wav">Speaker WAV File</label>
                    <input type="text" id="coqui_speaker_wav" name="coqui_speaker_wav" placeholder="/path/to/speaker.wav">
                    <small>Path to WAV file for voice cloning (optional)</small>
                </div>

                <div class="form-group">
                    <label for="coqui_temperature">Temperature</label>
                    <input type="number" id="coqui_temperature" name="coqui_temperature" min="0.1" max="2.0" step="0.05">
                    <small>Controls randomness in speech generation (0.1-2.0)</small>
                </div>

                <div class="form-group">
                    <label for="coqui_length_penalty">Length Penalty</label>
                    <input type="number" id="coqui_length_penalty" name="coqui_length_penalty" min="0.5" max="2.0" step="0.1">
                    <small>Penalty for sequence length (0.5-2.0)</small>
                </div>

                <div class="form-group">
                    <label for="coqui_repetition_penalty">Repetition Penalty</label>
                    <input type="number" id="coqui_repetition_penalty" name="coqui_repetition_penalty" min="1.0" max="10.0" step="0.1">
                    <small>Penalty for repetitive speech (1.0-10.0)</small>
                </div>

                <div class="form-group">
                    <label for="coqui_top_k">Top K</label>
                    <input type="number" id="coqui_top_k" name="coqui_top_k" min="1" max="100">
                    <small>Number of top tokens to consider (1-100)</small>
                </div>

                <div class="form-group">
                    <label for="coqui_top_p">Top P</label>
                    <input type="number" id="coqui_top_p" name="coqui_top_p" min="0.1" max="1.0" step="0.05">
                    <small>Cumulative probability threshold (0.1-1.0)</small>
                </div>

                <div class="form-group">
                    <div class="checkbox-label">
                        <input type="checkbox" id="coqui_streaming" name="coqui_streaming">
                        <label for="coqui_streaming">Enable Streaming Mode</label>
                    </div>
                    <small>Enable real-time streaming synthesis (experimental)</small>
                </div>
            </div>

            <div class="config-section">
                <h3>TTS Fallback Settings</h3>
                <p><small>Configure fallback TTS behavior when neural TTS is unavailable</small></p>

                <div class="form-group">
                    <div class="checkbox-label">
                        <input type="checkbox" id="tts_fallback_enabled" name="tts_fallback_enabled">
                        <label for="tts_fallback_enabled">Enable Enhanced Fallback TTS</label>
                    </div>
                    <small>Use enhanced fallback TTS with optimized voice selection when neural TTS fails</small>
                </div>

                <div class="form-group">
                    <label for="tts_fallback_voices">Preferred Fallback Voices (Priority Order)</label>
                    <input type="text" id="tts_fallback_voices" name="tts_fallback_voices" placeholder="daniel,alex,samantha,victoria,karen">
                    <small>Comma-separated list of preferred voice names for fallback TTS</small>
                </div>

                <div class="form-group">
                    <label for="tts_fallback_rate_cap">Fallback Rate Cap (WPM)</label>
                    <input type="number" id="tts_fallback_rate_cap" name="tts_fallback_rate_cap" min="100" max="300">
                    <small>Maximum speech rate for fallback TTS to ensure clarity</small>
                </div>
            </div>

            <div class="form-actions">
                <button type="submit" class="btn">Save Audio Configuration</button>
                <button type="button" class="btn btn-secondary" onclick="loadAudioConfig()">Reset to Current</button>
                <button type="button" class="btn btn-secondary" onclick="testAudio()">Test Audio</button>
            </div>
        </form>

        <script>
        function loadAudioConfig() {
            fetch('/api/config')
                .then(response => response.json())
                .then(data => {
                    if (data.audio) {
                        const audio = data.audio;
                        document.getElementById('mic_index').value = audio.mic_index || 0;
                        document.getElementById('mic_name').value = audio.mic_name || '';
                        document.getElementById('energy_threshold').value = audio.energy_threshold || 100;
                        document.getElementById('timeout').value = audio.timeout || 3.0;
                        document.getElementById('phrase_time_limit').value = audio.phrase_time_limit || 5.0;
                        document.getElementById('tts_rate').value = audio.tts_rate || 180;
                        document.getElementById('tts_volume').value = audio.tts_volume || 0.8;
                        document.getElementById('tts_voice_preference').value = audio.tts_voice_preference || 'Daniel';
                        document.getElementById('response_delay').value = audio.response_delay || 0.5;
                        document.getElementById('coqui_model').value = audio.coqui_model || 'tts_models/multilingual/multi-dataset/xtts_v2';
                        document.getElementById('coqui_language').value = audio.coqui_language || 'en';
                        document.getElementById('coqui_device').value = audio.coqui_device || 'auto';
                        document.getElementById('coqui_use_gpu').checked = audio.coqui_use_gpu || false;
                        document.getElementById('coqui_speaker_wav').value = audio.coqui_speaker_wav || '';
                        document.getElementById('coqui_temperature').value = audio.coqui_temperature || 0.75;
                        document.getElementById('coqui_length_penalty').value = audio.coqui_length_penalty || 1.0;
                        document.getElementById('coqui_repetition_penalty').value = audio.coqui_repetition_penalty || 5.0;
                        document.getElementById('coqui_top_k').value = audio.coqui_top_k || 50;
                        document.getElementById('coqui_top_p').value = audio.coqui_top_p || 0.85;
                        document.getElementById('coqui_streaming').checked = audio.coqui_streaming || false;
                        document.getElementById('tts_fallback_enabled').checked = audio.tts_fallback_enabled !== undefined ? audio.tts_fallback_enabled : true;
                        document.getElementById('tts_fallback_voices').value = (audio.tts_fallback_voices || ['daniel', 'alex', 'samantha', 'victoria', 'karen']).join(',');
                        document.getElementById('tts_fallback_rate_cap').value = audio.tts_fallback_rate_cap || 200;
                    }
                })
                .catch(error => console.error('Error loading audio config:', error));
        }

        document.getElementById('audio-config-form').addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const audioConfig = {};

            for (let [key, value] of formData.entries()) {
                if (key.includes('_')) {
                    if (['mic_index', 'energy_threshold', 'tts_rate', 'coqui_top_k', 'tts_fallback_rate_cap'].includes(key)) {
                        audioConfig[key] = parseInt(value);
                    } else if (['timeout', 'phrase_time_limit', 'tts_volume', 'response_delay', 'coqui_temperature', 'coqui_length_penalty', 'coqui_repetition_penalty', 'coqui_top_p'].includes(key)) {
                        audioConfig[key] = parseFloat(value);
                    } else if (['coqui_use_gpu', 'coqui_streaming', 'tts_fallback_enabled'].includes(key)) {
                        audioConfig[key] = true;
                    } else if (key === 'tts_fallback_voices') {
                        audioConfig[key] = value.split(',').map(v => v.trim()).filter(v => v);
                    } else {
                        audioConfig[key] = value;
                    }
                }
            }

            if (!formData.has('coqui_use_gpu')) audioConfig.coqui_use_gpu = false;
            if (!formData.has('coqui_streaming')) audioConfig.coqui_streaming = false;
            if (!formData.has('tts_fallback_enabled')) audioConfig.tts_fallback_enabled = false;

            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({audio: audioConfig})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Audio configuration saved successfully!');
                } else {
                    alert('Error saving configuration: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => alert('Error saving configuration: ' + error.message));
        });

        function testAudio() {
            alert('Audio test feature coming soon. This will test microphone input and TTS output.');
        }

        loadAudioConfig();
        </script>
        """

    def get_llm_config_content(self) -> str:
        """Get the LLM configuration content."""
        return """
        <div class="page-header">
            <h1>LLM Configuration</h1>
            <div class="breadcrumb">
                <a href="/">Home</a> / <a href="/settings">Settings</a> / <a href="/llm">LLM</a>
            </div>
        </div>

        <p>Configure language model settings for Jarvis Voice Assistant.</p>

        <form id="llm-config-form" class="config-form">
            <div class="config-section">
                <h3>Model Settings</h3>

                <div class="form-group">
                    <label for="model">Model Name</label>
                    <input type="text" id="model" name="model" placeholder="llama3.1:8b">
                    <small>Ollama model name to use for responses</small>
                </div>

                <div class="form-group">
                    <label for="temperature">Temperature</label>
                    <input type="number" id="temperature" name="temperature" min="0.0" max="2.0" step="0.1">
                    <small>Controls randomness in responses (0.0 = deterministic, 2.0 = very creative)</small>
                </div>

                <div class="form-group">
                    <label for="max_tokens">Max Tokens</label>
                    <input type="number" id="max_tokens" name="max_tokens" min="100" max="8192" placeholder="Leave empty for unlimited">
                    <small>Maximum number of tokens in response (optional)</small>
                </div>
            </div>

            <div class="config-section">
                <h3>Behavior Settings</h3>

                <div class="form-group">
                    <div class="checkbox-label">
                        <input type="checkbox" id="verbose" name="verbose">
                        <label for="verbose">Verbose Mode</label>
                    </div>
                    <small>Enable detailed logging of LLM interactions</small>
                </div>

                <div class="form-group">
                    <div class="checkbox-label">
                        <input type="checkbox" id="reasoning" name="reasoning">
                        <label for="reasoning">Reasoning Mode</label>
                    </div>
                    <small>Enable step-by-step reasoning in responses</small>
                </div>
            </div>

            <div class="form-actions">
                <button type="submit" class="btn">Save LLM Configuration</button>
                <button type="button" class="btn btn-secondary" onclick="loadLLMConfig()">Reset to Current</button>
                <button type="button" class="btn btn-secondary" onclick="testLLM()">Test LLM</button>
            </div>
        </form>

        <script>
        function loadLLMConfig() {
            fetch('/api/config')
                .then(response => response.json())
                .then(data => {
                    if (data.llm) {
                        const llm = data.llm;
                        document.getElementById('model').value = llm.model || '';
                        document.getElementById('temperature').value = llm.temperature || 0.7;
                        document.getElementById('max_tokens').value = llm.max_tokens || '';
                        document.getElementById('verbose').checked = llm.verbose || false;
                        document.getElementById('reasoning').checked = llm.reasoning || false;
                    }
                })
                .catch(error => console.error('Error loading LLM config:', error));
        }

        document.getElementById('llm-config-form').addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const llmConfig = {};

            llmConfig.model = formData.get('model') || '';
            llmConfig.temperature = parseFloat(formData.get('temperature')) || 0.7;
            llmConfig.max_tokens = formData.get('max_tokens') ? parseInt(formData.get('max_tokens')) : null;
            llmConfig.verbose = formData.has('verbose');
            llmConfig.reasoning = formData.has('reasoning');

            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({llm: llmConfig})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('LLM configuration saved successfully!');
                } else {
                    alert('Error saving configuration: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => alert('Error saving configuration: ' + error.message));
        });

        function testLLM() {
            alert('LLM test feature coming soon. This will test the language model connection.');
        }

        loadLLMConfig();
        </script>
        """

    def get_conversation_config_content(self) -> str:
        """Get the conversation configuration content."""
        return """
        <h2>Conversation Configuration</h2>
        <p>Configure conversation flow and wake word detection settings.</p>

        <form id="conversation-config-form" class="config-form">
            <div class="config-section">
                <h3>Wake Word Settings</h3>

                <div class="form-group">
                    <label for="wake_word">Wake Word</label>
                    <input type="text" id="wake_word" name="wake_word" placeholder="jarvis">
                    <small>Word or phrase to activate Jarvis (case insensitive)</small>
                </div>
            </div>

            <div class="config-section">
                <h3>Conversation Flow</h3>

                <div class="form-group">
                    <label for="conversation_timeout">Conversation Timeout (seconds)</label>
                    <input type="number" id="conversation_timeout" name="conversation_timeout" min="5" max="300">
                    <small>How long to wait for user input before ending conversation</small>
                </div>

                <div class="form-group">
                    <label for="max_retries">Max Retries</label>
                    <input type="number" id="max_retries" name="max_retries" min="1" max="10">
                    <small>Maximum number of retry attempts for failed operations</small>
                </div>

                <div class="form-group">
                    <div class="checkbox-label">
                        <input type="checkbox" id="enable_full_duplex" name="enable_full_duplex">
                        <label for="enable_full_duplex">Enable Full Duplex Mode</label>
                    </div>
                    <small>Allow simultaneous listening and speaking (experimental, may cause cutoffs)</small>
                </div>
            </div>

            <div class="form-actions">
                <button type="submit" class="btn">Save Conversation Configuration</button>
                <button type="button" class="btn btn-secondary" onclick="loadConversationConfig()">Reset to Current</button>
            </div>
        </form>

        <script>
        function loadConversationConfig() {
            fetch('/api/config')
                .then(response => response.json())
                .then(data => {
                    if (data.conversation) {
                        const conv = data.conversation;
                        document.getElementById('wake_word').value = conv.wake_word || 'jarvis';
                        document.getElementById('conversation_timeout').value = conv.conversation_timeout || 30;
                        document.getElementById('max_retries').value = conv.max_retries || 3;
                        document.getElementById('enable_full_duplex').checked = conv.enable_full_duplex || false;
                    }
                })
                .catch(error => console.error('Error loading conversation config:', error));
        }

        document.getElementById('conversation-config-form').addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const conversationConfig = {
                wake_word: formData.get('wake_word') || 'jarvis',
                conversation_timeout: parseInt(formData.get('conversation_timeout')) || 30,
                max_retries: parseInt(formData.get('max_retries')) || 3,
                enable_full_duplex: formData.has('enable_full_duplex')
            };

            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({conversation: conversationConfig})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Conversation configuration saved successfully!');
                } else {
                    alert('Error saving configuration: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => alert('Error saving configuration: ' + error.message));
        });

        loadConversationConfig();
        </script>
        """

    def get_logging_config_content(self) -> str:
        """Get the logging configuration content."""
        return """
        <h2>Logging Configuration</h2>
        <p>Configure logging levels and output settings.</p>

        <form id="logging-config-form" class="config-form">
            <div class="config-section">
                <h3>Logging Settings</h3>

                <div class="form-group">
                    <label for="log_level">Log Level</label>
                    <select id="log_level" name="level">
                        <option value="DEBUG">DEBUG</option>
                        <option value="INFO">INFO</option>
                        <option value="WARNING">WARNING</option>
                        <option value="ERROR">ERROR</option>
                        <option value="CRITICAL">CRITICAL</option>
                    </select>
                    <small>Minimum level of messages to log</small>
                </div>

                <div class="form-group">
                    <label for="log_file">Log File Path</label>
                    <input type="text" id="log_file" name="file" placeholder="Leave empty for console only">
                    <small>Path to log file (optional)</small>
                </div>

                <div class="form-group">
                    <label for="log_format">Log Format</label>
                    <input type="text" id="log_format" name="format" placeholder="%(asctime)s - %(name)s - %(levelname)s - %(message)s">
                    <small>Python logging format string</small>
                </div>

                <div class="form-group">
                    <label for="log_date_format">Date Format</label>
                    <input type="text" id="log_date_format" name="date_format" placeholder="%Y-%m-%d %H:%M:%S">
                    <small>Date format for log timestamps</small>
                </div>
            </div>

            <div class="form-actions">
                <button type="submit" class="btn">Save Logging Configuration</button>
                <button type="button" class="btn btn-secondary" onclick="loadLoggingConfig()">Reset to Current</button>
            </div>
        </form>

        <script>
        function loadLoggingConfig() {
            fetch('/api/config')
                .then(response => response.json())
                .then(data => {
                    if (data.logging) {
                        const log = data.logging;
                        document.getElementById('log_level').value = log.level || 'INFO';
                        document.getElementById('log_file').value = log.file || '';
                        document.getElementById('log_format').value = log.format || '%(asctime)s - %(name)s - %(levelname)s - %(message)s';
                        document.getElementById('log_date_format').value = log.date_format || '%Y-%m-%d %H:%M:%S';
                    }
                })
                .catch(error => console.error('Error loading logging config:', error));
        }

        document.getElementById('logging-config-form').addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const loggingConfig = {
                level: formData.get('level') || 'INFO',
                file: formData.get('file') || null,
                format: formData.get('format') || '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                date_format: formData.get('date_format') || '%Y-%m-%d %H:%M:%S'
            };

            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({logging: loggingConfig})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Logging configuration saved successfully!');
                } else {
                    alert('Error saving configuration: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => alert('Error saving configuration: ' + error.message));
        });

        loadLoggingConfig();
        </script>
        """

    def get_general_config_content(self) -> str:
        """Get the general configuration content."""
        return """
        <h2>General Configuration</h2>
        <p>Configure general application settings and directories.</p>

        <form id="general-config-form" class="config-form">
            <div class="config-section">
                <h3>Application Settings</h3>

                <div class="form-group">
                    <div class="checkbox-label">
                        <input type="checkbox" id="debug" name="debug">
                        <label for="debug">Debug Mode</label>
                    </div>
                    <small>Enable debug mode for detailed troubleshooting</small>
                </div>

                <div class="form-group">
                    <label for="data_dir">Data Directory</label>
                    <input type="text" id="data_dir" name="data_dir" placeholder="~/.jarvis">
                    <small>Directory for storing Jarvis data files</small>
                </div>

                <div class="form-group">
                    <label for="config_file">Config File Path</label>
                    <input type="text" id="config_file" name="config_file" placeholder="Leave empty for default">
                    <small>Path to configuration file (optional)</small>
                </div>
            </div>

            <div class="form-actions">
                <button type="submit" class="btn">Save General Configuration</button>
                <button type="button" class="btn btn-secondary" onclick="loadGeneralConfig()">Reset to Current</button>
            </div>
        </form>

        <script>
        function loadGeneralConfig() {
            fetch('/api/config')
                .then(response => response.json())
                .then(data => {
                    if (data.general) {
                        const gen = data.general;
                        document.getElementById('debug').checked = gen.debug || false;
                        document.getElementById('data_dir').value = gen.data_dir || '';
                        document.getElementById('config_file').value = gen.config_file || '';
                    }
                })
                .catch(error => console.error('Error loading general config:', error));
        }

        document.getElementById('general-config-form').addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const generalConfig = {
                debug: formData.has('debug'),
                data_dir: formData.get('data_dir') || '',
                config_file: formData.get('config_file') || null
            };

            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({general: generalConfig})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('General configuration saved successfully!');
                } else {
                    alert('Error saving configuration: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => alert('Error saving configuration: ' + error.message));
        });

        loadGeneralConfig();
        </script>
        """

    def get_voice_profiles_content(self) -> str:
        """Get the voice profiles content."""
        return """
        <h2>Voice Profiles</h2>
        <p>Manage voice cloning profiles for personalized TTS output.</p>

        <div class="config-section">
            <h3>Create New Voice Profile</h3>
            <form id="voice-profile-form" class="config-form">
                <div class="form-group">
                    <label for="profile_name">Profile Name</label>
                    <input type="text" id="profile_name" name="name" required>
                    <small>Unique name for this voice profile</small>
                </div>

                <div class="form-group">
                    <label for="audio_file">Audio File</label>
                    <input type="file" id="audio_file" name="audio_file" accept=".wav,.mp3,.flac,.m4a,.ogg" required>
                    <small>High-quality audio sample (10-120 seconds, WAV/MP3/FLAC)</small>
                </div>

                <div class="form-group">
                    <label for="description">Description</label>
                    <textarea id="description" name="description" rows="3"></textarea>
                    <small>Optional description of this voice profile</small>
                </div>

                <div class="form-actions">
                    <button type="submit" class="btn">Create Voice Profile</button>
                </div>
            </form>
        </div>

        <div class="config-section">
            <h3>Existing Voice Profiles</h3>
            <div id="voice-profiles-list">
                <p>Loading voice profiles...</p>
            </div>
        </div>

        <script>
        function loadVoiceProfiles() {
            fetch('/api/voice-profiles')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('voice-profiles-list');
                    if (data.profiles && data.profiles.length > 0) {
                        container.innerHTML = data.profiles.map(profile => `
                            <div class="voice-profile-card">
                                <h4>${profile.name}</h4>
                                <div class="voice-profile-meta">
                                    Created: ${new Date(profile.created_at).toLocaleDateString()}<br>
                                    Duration: ${profile.duration.toFixed(1)}s | Quality: ${(profile.quality_score * 100).toFixed(0)}%
                                </div>
                                <p>${profile.description || 'No description'}</p>
                                <div class="voice-profile-actions">
                                    <button class="btn" onclick="useProfile('${profile.id}')">Use Profile</button>
                                    <button class="btn btn-secondary" onclick="deleteProfile('${profile.id}')">Delete</button>
                                </div>
                            </div>
                        `).join('');
                    } else {
                        container.innerHTML = '<p>No voice profiles found. Create your first profile above.</p>';
                    }
                })
                .catch(error => {
                    document.getElementById('voice-profiles-list').innerHTML = '<p>Error loading voice profiles: ' + error.message + '</p>';
                });
        }

        function useProfile(profileId) {
            alert('Voice profile activation feature coming soon.');
        }

        function deleteProfile(profileId) {
            if (confirm('Are you sure you want to delete this voice profile?')) {
                alert('Voice profile deletion feature coming soon.');
            }
        }

        document.getElementById('voice-profile-form').addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Voice profile creation feature coming soon.');
        });

        loadVoiceProfiles();
        </script>
        """

    def get_device_config_content(self) -> str:
        """Get the device configuration content."""
        return """
        <h2>Device Configuration</h2>
        <p>View device information and hardware capabilities.</p>

        <div id="device-info-content">
            <p>Loading device information...</p>
        </div>

        <script>
        function loadDeviceInfo() {
            fetch('/api/device-info')
                .then(response => response.json())
                .then(data => {
                    const html = `
                        <div class="config-grid">
                            <div class="status-card">
                                <h3>System Information</h3>
                                <div class="status-item"><strong>Platform:</strong> ${data.system.platform}</div>
                                <div class="status-item"><strong>Release:</strong> ${data.system.platform_release}</div>
                                <div class="status-item"><strong>Architecture:</strong> ${data.system.architecture}</div>
                                <div class="status-item"><strong>Processor:</strong> ${data.system.processor}</div>
                                <div class="status-item"><strong>Python:</strong> ${data.system.python_version} (${data.system.python_implementation})</div>
                            </div>

                            <div class="status-card">
                                <h3>Hardware Information</h3>
                                <div class="status-item"><strong>CPU Cores:</strong> ${data.hardware.cpu_count} physical, ${data.hardware.cpu_count_logical} logical</div>
                                <div class="status-item"><strong>Total Memory:</strong> ${data.hardware.memory_total} GB</div>
                                <div class="status-item"><strong>Available Memory:</strong> ${data.hardware.memory_available} GB</div>
                                <div class="status-item"><strong>Memory Usage:</strong> ${data.hardware.memory_percent}%</div>
                            </div>

                            <div class="status-card">
                                <h3>Storage Information</h3>
                                <div class="status-item"><strong>Total Disk:</strong> ${data.hardware.disk_usage.total} GB</div>
                                <div class="status-item"><strong>Used Disk:</strong> ${data.hardware.disk_usage.used} GB</div>
                                <div class="status-item"><strong>Free Disk:</strong> ${data.hardware.disk_usage.free} GB</div>
                                <div class="status-item"><strong>Disk Usage:</strong> ${data.hardware.disk_usage.percent}%</div>
                            </div>

                            <div class="status-card">
                                <h3>Network Information</h3>
                                <div class="status-item"><strong>Hostname:</strong> ${data.network.hostname}</div>
                                <div class="status-item"><strong>Network Interfaces:</strong> ${data.network.interfaces.join(', ')}</div>
                            </div>
                        </div>
                    `;
                    document.getElementById('device-info-content').innerHTML = html;
                })
                .catch(error => {
                    document.getElementById('device-info-content').innerHTML = '<p>Error loading device information: ' + error.message + '</p>';
                });
        }

        loadDeviceInfo();
        setInterval(loadDeviceInfo, 30000); // Refresh every 30 seconds
        </script>
        """

    def get_mcp_content(self) -> str:
        """Get the MCP management content."""
        return """
        <div class="page-header">
            <h1>MCP Tools & Servers</h1>
            <div class="breadcrumb">
                <a href="/settings">Settings</a> > MCP Tools & Servers
            </div>
        </div>

        <div class="info-banner">
            <h3>🔗 Model Context Protocol (MCP)</h3>
            <p>Connect Jarvis to external tools and services through MCP servers. Popular options include GitHub integration, file system access, web search, and database connections.</p>
            <details>
                <summary>📚 Quick Setup Guide</summary>
                <div class="setup-guide">
                    <h4>Getting Started:</h4>
                    <ol>
                        <li><strong>Install Node.js</strong> if you haven't already (required for most MCP servers)</li>
                        <li><strong>Click "Add Server"</strong> and choose a template for quick setup</li>
                        <li><strong>Popular first choice:</strong> Memory Storage (no setup required)</li>
                        <li><strong>For GitHub:</strong> Get a personal access token from GitHub Settings</li>
                        <li><strong>Test connection</strong> before saving to ensure everything works</li>
                    </ol>
                    <p><strong>Need help?</strong> Each template includes detailed setup instructions.</p>
                </div>
            </details>
        </div>

        <div class="config-section">
            <div class="section-header">
                <h2>MCP Servers</h2>
                <button class="btn btn-primary" onclick="showAddServerModal()">
                    <i class="icon">+</i> Add Server
                </button>
            </div>

            <div id="servers-list" class="servers-grid">
                <p>Loading MCP servers...</p>
            </div>
        </div>

        <div class="config-section">
            <div class="section-header">
                <h2>Available Tools</h2>
                <button class="btn btn-secondary" onclick="refreshTools()">
                    <i class="icon">🔄</i> Refresh Tools
                </button>
            </div>

            <div id="tools-list" class="tools-grid">
                <p>Loading tools...</p>
            </div>
        </div>

        <!-- Add Server Modal -->
        <div id="add-server-modal" class="modal" style="display: none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add MCP Server</h3>
                    <button class="modal-close" onclick="hideAddServerModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="add-server-form">
                        <div class="form-group">
                            <label for="server-template">Quick Setup (Optional):</label>
                            <select id="server-template" onchange="loadTemplate()">
                                <option value="">Custom Configuration</option>
                                <option value="github">GitHub Integration</option>
                                <option value="filesystem">File System Access</option>
                                <option value="brave_search">Brave Search</option>
                                <option value="memory">Memory Storage</option>
                                <option value="sqlite">SQLite Database</option>
                            </select>
                            <small>Select a template for quick setup, or choose "Custom Configuration" to configure manually</small>
                        </div>

                        <div class="form-group">
                            <label for="server-name">Server Name:</label>
                            <input type="text" id="server-name" name="name" required
                                   placeholder="e.g., GitHub Integration">
                        </div>

                        <div class="form-group">
                            <label for="transport-type">Transport Type:</label>
                            <select id="transport-type" name="transport" onchange="updateTransportConfig()">
                                <option value="stdio">STDIO (Process)</option>
                                <option value="sse">HTTP/SSE</option>
                                <option value="websocket">WebSocket</option>
                            </select>
                        </div>

                        <!-- STDIO Configuration -->
                        <div id="stdio-config" class="transport-config">
                            <div class="form-group">
                                <label for="command">Command:</label>
                                <input type="text" id="command" name="command"
                                       placeholder="e.g., npx">
                            </div>
                            <div class="form-group">
                                <label for="args">Arguments:</label>
                                <input type="text" id="args" name="args"
                                       placeholder="e.g., -m @modelcontextprotocol/server-github">
                                <small>Separate multiple arguments with spaces</small>
                            </div>
                            <div class="form-group">
                                <label for="env-vars">Environment Variables:</label>
                                <textarea id="env-vars" name="env" rows="3"
                                          placeholder="KEY1=value1
KEY2=value2"></textarea>
                                <small>One per line, format: KEY=value</small>
                            </div>
                        </div>

                        <!-- HTTP/SSE Configuration -->
                        <div id="http-config" class="transport-config" style="display: none;">
                            <div class="form-group">
                                <label for="server-url">Server URL:</label>
                                <input type="url" id="server-url" name="url"
                                       placeholder="https://api.example.com/mcp">
                            </div>
                            <div class="form-group">
                                <label for="headers">Headers:</label>
                                <textarea id="headers" name="headers" rows="3"
                                          placeholder="Authorization: Bearer token
X-API-Key: key"></textarea>
                                <small>One per line, format: Header: value</small>
                            </div>
                            <div class="form-group">
                                <label for="timeout">Timeout (seconds):</label>
                                <input type="number" id="timeout" name="timeout" value="30" min="1" max="300">
                            </div>
                        </div>

                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="enabled" name="enabled" checked>
                                Enable server automatically
                            </label>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="hideAddServerModal()">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="testConnection()">Test Connection</button>
                    <button type="button" class="btn btn-primary" onclick="addServer()">Add Server</button>
                </div>
            </div>
        </div>

        <style>
        .info-banner {
            background: rgba(33, 150, 243, 0.1);
            border: 1px solid rgba(33, 150, 243, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 2rem;
        }

        .info-banner h3 {
            margin: 0 0 0.5rem 0;
            color: #2196F3;
        }

        .info-banner p {
            margin: 0 0 1rem 0;
            color: rgba(255, 255, 255, 0.8);
        }

        .info-banner details {
            margin-top: 1rem;
        }

        .info-banner summary {
            cursor: pointer;
            color: #2196F3;
            font-weight: bold;
        }

        .setup-guide {
            margin-top: 1rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
        }

        .setup-guide h4 {
            margin: 0 0 0.5rem 0;
            color: white;
        }

        .setup-guide ol {
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }

        .setup-guide li {
            margin: 0.5rem 0;
            color: rgba(255, 255, 255, 0.9);
        }

        .servers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .server-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1rem;
            backdrop-filter: blur(10px);
        }

        .server-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 0.5rem;
        }

        .server-name {
            font-weight: bold;
            font-size: 1.1rem;
        }

        .server-status {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: bold;
        }

        .status-connected { background: #4CAF50; color: white; }
        .status-connecting { background: #FF9800; color: white; }
        .status-disconnected { background: #757575; color: white; }
        .status-error { background: #F44336; color: white; }

        .server-info {
            margin: 0.5rem 0;
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.7);
        }

        .server-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 1rem;
        }

        .tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .tool-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1rem;
            backdrop-filter: blur(10px);
        }

        .tool-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }

        .tool-name {
            font-weight: bold;
        }

        .tool-server {
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.6);
        }

        .tool-description {
            margin: 0.5rem 0;
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.8);
        }

        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            background: rgba(30, 30, 30, 0.95);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            max-width: 600px;
            width: 90%;
            max-height: 80vh;
            overflow-y: auto;
            backdrop-filter: blur(20px);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .modal-close {
            background: none;
            border: none;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
        }

        .modal-body {
            padding: 1rem;
        }

        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 0.5rem;
            padding: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .transport-config {
            margin-top: 1rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        }

        .form-group {
            margin-bottom: 1rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: bold;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            color: white;
        }

        .form-group small {
            display: block;
            margin-top: 0.25rem;
            color: rgba(255, 255, 255, 0.6);
            font-size: 0.8rem;
        }

        .btn {
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }

        .btn-primary {
            background: #2196F3;
            color: white;
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            color: white;
        }

        .btn-danger {
            background: #F44336;
            color: white;
        }

        .btn-small {
            padding: 0.25rem 0.5rem;
            font-size: 0.8rem;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }

        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 24px;
        }

        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }

        .toggle-slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 24px;
        }

        .toggle-slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }

        input:checked + .toggle-slider {
            background-color: #2196F3;
        }

        input:checked + .toggle-slider:before {
            transform: translateX(26px);
        }

        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            z-index: 10000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            max-width: 400px;
            word-wrap: break-word;
        }

        .notification.show {
            transform: translateX(0);
        }

        .notification-success {
            background: #4CAF50;
            border: 1px solid #45a049;
        }

        .notification-error {
            background: #F44336;
            border: 1px solid #da190b;
        }

        .notification-info {
            background: #2196F3;
            border: 1px solid #0b7dda;
        }
        </style>

        <script>
        let servers = {};
        let tools = {};

        function loadServers() {
            fetch('/api/mcp/servers')
                .then(response => response.json())
                .then(data => {
                    servers = data.servers || {};
                    renderServers();
                })
                .catch(error => {
                    console.error('Error loading servers:', error);
                    document.getElementById('servers-list').innerHTML =
                        '<p>Error loading servers: ' + error.message + '</p>';
                });
        }

        function loadTools() {
            fetch('/api/mcp/tools')
                .then(response => response.json())
                .then(data => {
                    tools = data.tools || {};
                    renderTools();
                })
                .catch(error => {
                    console.error('Error loading tools:', error);
                    document.getElementById('tools-list').innerHTML =
                        '<p>Error loading tools: ' + error.message + '</p>';
                });
        }

        function renderServers() {
            const serversList = document.getElementById('servers-list');

            if (Object.keys(servers).length === 0) {
                serversList.innerHTML = '<p>No MCP servers configured. Click "Add Server" to get started.</p>';
                return;
            }

            const html = Object.entries(servers).map(([name, server]) => `
                <div class="server-card">
                    <div class="server-header">
                        <div class="server-name">${name}</div>
                        <div class="server-status status-${server.status}">${server.status.toUpperCase()}</div>
                    </div>
                    <div class="server-info">
                        <div><strong>Transport:</strong> ${server.config.transport}</div>
                        ${server.config.transport === 'stdio' ?
                            `<div><strong>Command:</strong> ${server.config.command} ${server.config.args.join(' ')}</div>` :
                            `<div><strong>URL:</strong> ${server.config.url}</div>`
                        }
                        <div><strong>Tools:</strong> ${server.tools ? server.tools.length : 0} available</div>
                        ${server.last_error ? `<div style="color: #F44336;"><strong>Error:</strong> ${server.last_error}</div>` : ''}
                    </div>
                    <div class="server-actions">
                        ${server.status === 'connected' ?
                            `<button class="btn btn-secondary btn-small" onclick="disconnectServer('${name}')">Disconnect</button>` :
                            `<button class="btn btn-primary btn-small" onclick="connectServer('${name}')">Connect</button>`
                        }
                        <button class="btn btn-secondary btn-small" onclick="configureServer('${name}')">Configure</button>
                        <button class="btn btn-danger btn-small" onclick="removeServer('${name}')">Remove</button>
                    </div>
                </div>
            `).join('');

            serversList.innerHTML = html;
        }

        function renderTools() {
            const toolsList = document.getElementById('tools-list');

            if (Object.keys(tools).length === 0) {
                toolsList.innerHTML = '<p>No tools available. Connect to MCP servers to discover tools.</p>';
                return;
            }

            const html = Object.entries(tools).map(([name, tool]) => `
                <div class="tool-card">
                    <div class="tool-header">
                        <div>
                            <div class="tool-name">${tool.name}</div>
                            <div class="tool-server">[${tool.server_name}]</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" ${tool.enabled ? 'checked' : ''}
                                   onchange="toggleTool('${name}', this.checked)">
                            <span class="toggle-slider"></span>
                        </label>
                    </div>
                    <div class="tool-description">${tool.description || 'No description available'}</div>
                </div>
            `).join('');

            toolsList.innerHTML = html;
        }

        function showAddServerModal() {
            document.getElementById('add-server-modal').style.display = 'flex';
        }

        function hideAddServerModal() {
            document.getElementById('add-server-modal').style.display = 'none';
            document.getElementById('add-server-form').reset();
        }

        function loadTemplate() {
            const template = document.getElementById('server-template').value;
            if (!template) return;

            const templates = {
                github: {
                    name: 'GitHub Integration',
                    transport: 'stdio',
                    command: 'npx',
                    args: '-m @modelcontextprotocol/server-github',
                    env: 'GITHUB_TOKEN=your_github_token_here'
                },
                filesystem: {
                    name: 'File System Access',
                    transport: 'stdio',
                    command: 'npx',
                    args: '-m @modelcontextprotocol/server-filesystem /Users',
                    env: ''
                },
                brave_search: {
                    name: 'Brave Search',
                    transport: 'stdio',
                    command: 'npx',
                    args: '-m @modelcontextprotocol/server-brave-search',
                    env: 'BRAVE_API_KEY=your_brave_api_key_here'
                },
                memory: {
                    name: 'Memory Storage',
                    transport: 'stdio',
                    command: 'npx',
                    args: '-m @modelcontextprotocol/server-memory',
                    env: ''
                },
                sqlite: {
                    name: 'SQLite Database',
                    transport: 'stdio',
                    command: 'npx',
                    args: '-m @modelcontextprotocol/server-sqlite /path/to/database.db',
                    env: ''
                }
            };

            const config = templates[template];
            if (config) {
                document.getElementById('server-name').value = config.name;
                document.getElementById('transport-type').value = config.transport;
                document.getElementById('command').value = config.command;
                document.getElementById('args').value = config.args;
                document.getElementById('env-vars').value = config.env;
                updateTransportConfig();
            }
        }

        function updateTransportConfig() {
            const transport = document.getElementById('transport-type').value;
            const stdioConfig = document.getElementById('stdio-config');
            const httpConfig = document.getElementById('http-config');

            if (transport === 'stdio') {
                stdioConfig.style.display = 'block';
                httpConfig.style.display = 'none';
            } else {
                stdioConfig.style.display = 'none';
                httpConfig.style.display = 'block';
            }
        }

        function testConnection() {
            const formData = getFormData();
            if (!formData) return;

            // Show loading state
            const testBtn = event.target;
            const originalText = testBtn.textContent;
            testBtn.textContent = 'Testing...';
            testBtn.disabled = true;

            fetch('/api/mcp/servers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'test', ...formData })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Connection test successful!');
                } else {
                    alert('Connection test failed: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                alert('Connection test failed: ' + error.message);
            })
            .finally(() => {
                testBtn.textContent = originalText;
                testBtn.disabled = false;
            });
        }

        function addServer() {
            const formData = getFormData();
            if (!formData) return;

            // Show loading state
            const addBtn = document.querySelector('button[onclick="addServer()"]');
            const originalText = addBtn.textContent;
            addBtn.textContent = 'Adding...';
            addBtn.disabled = true;

            fetch('/api/mcp/servers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'add', ...formData })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    hideAddServerModal();
                    loadServers();
                    loadTools();
                    showNotification('Server added successfully!', 'success');
                } else {
                    showNotification('Failed to add server: ' + (data.error || 'Unknown error'), 'error');
                }
            })
            .catch(error => {
                showNotification('Failed to add server: ' + error.message, 'error');
            })
            .finally(() => {
                addBtn.textContent = originalText;
                addBtn.disabled = false;
            });
        }

        function getFormData() {
            const form = document.getElementById('add-server-form');
            const formData = new FormData(form);

            const data = {
                name: formData.get('name'),
                transport: formData.get('transport'),
                enabled: formData.get('enabled') === 'on'
            };

            if (!data.name) {
                alert('Please enter a server name');
                return null;
            }

            if (data.transport === 'stdio') {
                data.command = formData.get('command');
                data.args = formData.get('args') ? formData.get('args').split(' ').filter(arg => arg.trim()) : [];

                // Parse environment variables
                const envText = formData.get('env') || '';
                data.env = {};
                envText.split('\n').forEach(line => {
                    const [key, ...valueParts] = line.split('=');
                    if (key && valueParts.length > 0) {
                        data.env[key.trim()] = valueParts.join('=').trim();
                    }
                });

                if (!data.command) {
                    alert('Please enter a command for STDIO transport');
                    return null;
                }
            } else {
                data.url = formData.get('url');
                data.timeout = parseInt(formData.get('timeout')) || 30;

                // Parse headers
                const headersText = formData.get('headers') || '';
                data.headers = {};
                headersText.split('\n').forEach(line => {
                    const [key, ...valueParts] = line.split(':');
                    if (key && valueParts.length > 0) {
                        data.headers[key.trim()] = valueParts.join(':').trim();
                    }
                });

                if (!data.url) {
                    alert('Please enter a URL for HTTP/WebSocket transport');
                    return null;
                }
            }

            return data;
        }

        function connectServer(serverName) {
            fetch('/api/mcp/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ server: serverName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadServers();
                    loadTools();
                } else {
                    alert('Failed to connect: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                alert('Failed to connect: ' + error.message);
            });
        }

        function disconnectServer(serverName) {
            fetch('/api/mcp/disconnect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ server: serverName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadServers();
                    loadTools();
                } else {
                    alert('Failed to disconnect: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                alert('Failed to disconnect: ' + error.message);
            });
        }

        function removeServer(serverName) {
            if (!confirm(`Are you sure you want to remove server "${serverName}"?`)) {
                return;
            }

            fetch('/api/mcp/servers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'remove', name: serverName })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    loadServers();
                    loadTools();
                } else {
                    alert('Failed to remove server: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => {
                alert('Failed to remove server: ' + error.message);
            });
        }

        function toggleTool(toolName, enabled) {
            fetch('/api/mcp/tools/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tool: toolName, enabled: enabled })
            })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    alert('Failed to toggle tool: ' + (data.error || 'Unknown error'));
                    loadTools(); // Reload to reset state
                }
            })
            .catch(error => {
                alert('Failed to toggle tool: ' + error.message);
                loadTools(); // Reload to reset state
            });
        }

        function refreshTools() {
            loadTools();
        }

        function configureServer(serverName) {
            // TODO: Implement server configuration modal
            showNotification('Server configuration coming soon!', 'info');
        }

        function showNotification(message, type = 'info') {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.textContent = message;

            // Add to page
            document.body.appendChild(notification);

            // Show with animation
            setTimeout(() => notification.classList.add('show'), 100);

            // Auto-hide after 5 seconds
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => document.body.removeChild(notification), 300);
            }, 5000);
        }

        // Load data on page load
        loadServers();
        loadTools();

        // Auto-refresh every 30 seconds
        setInterval(() => {
            loadServers();
            loadTools();
        }, 30000);
        </script>
        """

    def log_message(self, format, *args):
        """Override to reduce log noise."""
        pass


class JarvisUI:
    """Main Jarvis UI application class."""

    def __init__(self, initial_panel: str = "main", port: int = 8080):
        """Initialize the Jarvis UI application."""
        self.initial_panel = initial_panel
        self.port = port
        self.server = None
    
    def start_server(self):
        """Start the HTTP server."""
        try:
            self.server = HTTPServer(('localhost', self.port), JarvisUIHandler)
            # Store server reference in handler class for shutdown access
            JarvisUIHandler._server_instance = self.server
            logger.info(f"Starting Jarvis UI server on http://localhost:{self.port}")

            # Open browser after a short delay
            def open_browser():
                time.sleep(1)
                url = f"http://localhost:{self.port}/{self.initial_panel}"
                webbrowser.open(url)
                logger.info(f"Opened browser to {url}")

            threading.Thread(target=open_browser, daemon=True).start()

            # Start server
            self.server.serve_forever()

        except KeyboardInterrupt:
            self.stop_server()
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
            raise

    def stop_server(self):
        """Stop the HTTP server."""
        if self.server:
            logger.info("Stopping Jarvis UI server...")
            self.server.shutdown()
            self.server.server_close()

    def run(self):
        """Run the application."""
        try:
            self.start_server()
        except KeyboardInterrupt:
            self.stop_server()


def main():
    """Main entry point for the Jarvis UI application."""
    parser = argparse.ArgumentParser(description="Jarvis Voice Assistant Control Panel")
    parser.add_argument(
        "--panel",
        default="main",
        choices=["main", "settings", "audio", "performance", "tools", "status"],
        help="Initial panel to display"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to run the web server on (default: 8080)"
    )

    args = parser.parse_args()

    try:
        app = JarvisUI(initial_panel=args.panel, port=args.port)
        app.run()
    except Exception as e:
        logger.error(f"Failed to start Jarvis UI: {e}")
        print(f"Error: Failed to start Jarvis UI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
