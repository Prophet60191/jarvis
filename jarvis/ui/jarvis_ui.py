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
import asyncio

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
                    "coqui_voice_preset": config.audio.coqui_voice_preset,
                    "coqui_voice_speed": config.audio.coqui_voice_speed,
                    "coqui_speaker_id": config.audio.coqui_speaker_id,
                    "coqui_voice_conditioning_latents": config.audio.coqui_voice_conditioning_latents,
                    "coqui_emotion": config.audio.coqui_emotion,
                    "coqui_sample_rate": config.audio.coqui_sample_rate,
                    "coqui_vocoder_model": config.audio.coqui_vocoder_model,
                    "coqui_speed_factor": config.audio.coqui_speed_factor,
                    "coqui_enable_text_splitting": config.audio.coqui_enable_text_splitting,
                    "coqui_do_trim_silence": config.audio.coqui_do_trim_silence,

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
                "agent": {
                    "max_iterations": config.agent.max_iterations,
                    "max_execution_time": config.agent.max_execution_time,
                    "enable_memory": config.agent.enable_memory,
                    "handle_parsing_errors": config.agent.handle_parsing_errors,
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
                },
                "mcp": {
                    "enabled": config.mcp.enabled,
                    "servers": {
                        name: {
                            "name": server.name,
                            "command": server.command,
                            "args": server.args,
                            "env": server.env,
                            "enabled": server.enabled,
                            "timeout": server.timeout
                        }
                        for name, server in config.mcp.servers.items()
                    }
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
                if "coqui_voice_preset" in audio:
                    env_vars["JARVIS_COQUI_VOICE_PRESET"] = audio["coqui_voice_preset"]
                if "coqui_voice_speed" in audio:
                    env_vars["JARVIS_COQUI_VOICE_SPEED"] = str(audio["coqui_voice_speed"])
                if "coqui_speaker_id" in audio:
                    env_vars["JARVIS_COQUI_SPEAKER_ID"] = audio["coqui_speaker_id"] or ""
                if "coqui_voice_conditioning_latents" in audio:
                    env_vars["JARVIS_COQUI_VOICE_CONDITIONING_LATENTS"] = audio["coqui_voice_conditioning_latents"] or ""
                if "coqui_emotion" in audio:
                    env_vars["JARVIS_COQUI_EMOTION"] = audio["coqui_emotion"]
                if "coqui_sample_rate" in audio:
                    env_vars["JARVIS_COQUI_SAMPLE_RATE"] = str(audio["coqui_sample_rate"])
                if "coqui_vocoder_model" in audio:
                    env_vars["JARVIS_COQUI_VOCODER_MODEL"] = audio["coqui_vocoder_model"]
                if "coqui_speed_factor" in audio:
                    env_vars["JARVIS_COQUI_SPEED_FACTOR"] = str(audio["coqui_speed_factor"])
                if "coqui_enable_text_splitting" in audio:
                    env_vars["JARVIS_COQUI_ENABLE_TEXT_SPLITTING"] = str(audio["coqui_enable_text_splitting"]).lower()
                if "coqui_do_trim_silence" in audio:
                    env_vars["JARVIS_COQUI_DO_TRIM_SILENCE"] = str(audio["coqui_do_trim_silence"]).lower()


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

            if "agent" in updates:
                agent = updates["agent"]
                if "max_iterations" in agent:
                    env_vars["JARVIS_MAX_ITERATIONS"] = str(agent["max_iterations"])
                if "max_execution_time" in agent:
                    env_vars["JARVIS_MAX_EXECUTION_TIME"] = str(agent["max_execution_time"])
                if "enable_memory" in agent:
                    env_vars["JARVIS_ENABLE_MEMORY"] = str(agent["enable_memory"]).lower()
                if "handle_parsing_errors" in agent:
                    env_vars["JARVIS_HANDLE_PARSING_ERRORS"] = str(agent["handle_parsing_errors"]).lower()

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

            if "mcp" in updates:
                mcp = updates["mcp"]
                if "enabled" in mcp:
                    env_vars["JARVIS_MCP_ENABLED"] = str(mcp["enabled"]).lower()
                # Note: MCP server configurations are handled through the MCP management interface
                # and stored separately from environment variables

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
                "Agent Configuration": [k for k in existing_vars.keys() if k.startswith("JARVIS_") and any(x in k for x in ["ITERATIONS", "EXECUTION", "MEMORY", "PARSING"])],
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

            # Write any remaining JARVIS variables that weren't categorized
            uncategorized = [k for k in existing_vars.keys() if k.startswith("JARVIS_") and not any(k in cat_keys for cat_keys in categories.values())]
            if uncategorized:
                f.write("# Other Configuration\n")
                for key in sorted(uncategorized):
                    f.write(f"{key}={existing_vars[key]}\n")
                f.write("\n")

        logger.info(f"Updated .env file with {len(env_vars)} variables")


# Global configuration manager instance
config_manager = ConfigurationManager()


class JarvisUIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the Jarvis UI web interface."""

    # Class variable to store server reference for shutdown
    _server_instance = None

    def _get_rag_service(self):
        """Get RAG service instance with proper configuration."""
        try:
            # Import here to avoid circular imports
            sys.path.append(str(Path(__file__).parent.parent))
            from jarvis.config import get_config
            from jarvis.tools.rag_service import RAGService

            config = get_config()
            return RAGService(config)
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            return None

    def _get_rag_memory_manager(self):
        """Get RAG memory manager for backward compatibility."""
        try:
            # Import here to avoid circular imports
            sys.path.append(str(Path(__file__).parent.parent))
            from jarvis.config import get_config
            from jarvis.tools.rag_memory_manager import RAGMemoryManager

            config = get_config()
            return RAGMemoryManager(config)
        except Exception as e:
            logger.error(f"Failed to initialize RAG memory manager: {e}")
            return None

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
        elif path == "/agent":
            self.serve_agent_config_page()
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
        elif path == "/tools":
            self.serve_tools_page()
        elif path == "/mcp":
            self.serve_mcp_page()
        elif path == "/rag":
            self.serve_rag_page()
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
        elif path == "/api/jarvis/tools":
            self.serve_jarvis_tools_api()
        elif path == "/api/plugins":
            self.serve_plugins_api()
        # RAG Management API endpoints
        elif path == "/api/rag/status":
            self.serve_rag_status_api()
        elif path == "/api/rag/memory/long-term":
            self.serve_long_term_memory_api()
        elif path == "/api/rag/documents":
            self.serve_documents_api()
        elif path == "/api/rag/documents/stats":
            self.serve_document_stats_api()
        elif path == "/api/rag/search":
            self.serve_rag_search_api()
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
        # RAG Management POST endpoints
        elif path == "/api/rag/memory/add":
            self.handle_add_memory()
        elif path == "/api/rag/memory/delete":
            self.handle_delete_memory()
        elif path == "/api/plugins":
            self.handle_plugin_action()
        elif path == "/api/rag/documents/upload":
            self.handle_document_upload()
        elif path == "/api/rag/documents/ingest":
            self.handle_document_ingest()
        elif path == "/api/rag/documents/delete":
            self.handle_document_delete()
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

    def serve_agent_config_page(self):
        """Serve the agent configuration page."""
        html = self.get_html_template("Agent Configuration", self.get_agent_config_content())
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

    def serve_tools_page(self):
        """Serve the Tools & Plugins management page."""
        html = self.get_html_template("Tools & Plugins", self.get_tools_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_mcp_page(self):
        """Serve the MCP management page."""
        html = self.get_html_template("MCP Servers", self.get_mcp_content())
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def serve_rag_page(self):
        """Serve the RAG management page."""
        html = self.get_html_template("RAG Memory Management", self.get_rag_content())
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
            # Get MCP config manager
            from jarvis.tools import get_mcp_config_manager
            config_manager = get_mcp_config_manager()

            if not config_manager:
                return self._send_json_response({"servers": {}}, 200)

            # Get all server configs
            all_server_configs = config_manager.get_all_servers()

            # Format server data for UI
            servers_data = {"servers": {}}

            # Convert config information for UI
            for server_id, config in all_server_configs.items():
                servers_data["servers"][server_id] = {
                    "config": {
                        "name": config.name,
                        "description": config.description,
                        "transport": config.transport.value,
                        "command": config.command,
                        "args": config.args,
                        "env": config.env,
                        "enabled": config.enabled,
                        "timeout": config.timeout,
                        "created_at": config.created_at,
                        "last_modified": config.last_modified
                    },
                    "status": {
                        "connected": False,  # Default to false for now
                        "tools_count": 0     # Default to 0 for now
                    }
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

    def serve_jarvis_tools_api(self):
        """Serve Jarvis plugin tools information as JSON API."""
        try:
            # Get plugin manager
            from jarvis.tools import plugin_manager

            # Get all plugin tools
            plugin_tools = plugin_manager.get_all_tools()

            # Format tools data for UI
            tools_data = {"tools": {}}
            for tool in plugin_tools:
                tool_key = f"jarvis:{tool.name}"
                tools_data["tools"][tool_key] = {
                    "name": tool.name,
                    "description": tool.description,
                    "source": "jarvis_plugin",
                    "plugin_name": getattr(tool, 'plugin_name', 'unknown'),
                    "enabled": True,  # Plugin tools are always enabled
                    "type": "plugin"
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(tools_data, indent=2).encode())
        except Exception as e:
            logger.error(f"Error serving Jarvis tools API: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def serve_plugins_api(self):
        """Serve plugins information as JSON API."""
        try:
            # Get plugin manager
            from jarvis.tools import plugin_manager

            # Get all plugins and their tools
            plugins_data = {"plugins": {}}

            # Access the plugin manager's internal data
            loaded_plugins = getattr(plugin_manager, '_loaded_plugins', {})
            plugin_tools_map = getattr(plugin_manager, '_plugin_tools', {})

            logger.info(f"Found {len(loaded_plugins)} loaded plugins")
            logger.info(f"Plugin tools map has {len(plugin_tools_map)} entries")

            # If we have plugin instances, use them
            if loaded_plugins:
                for plugin_name, plugin_instance in loaded_plugins.items():
                    try:
                        # Get metadata from plugin
                        metadata = plugin_instance.get_metadata()
                        tools = plugin_instance.get_tools()

                        plugins_data["plugins"][plugin_name] = {
                            "name": metadata.name,
                            "description": metadata.description,
                            "version": metadata.version,
                            "author": metadata.author,
                            "tools": [
                                {
                                    "name": tool.name,
                                    "description": tool.description or "No description available",
                                    "enabled": True
                                }
                                for tool in tools
                            ],
                            "enabled": metadata.enabled,
                            "type": "jarvis_plugin",
                            "voice_phrases": getattr(metadata, 'voice_phrases', [])
                        }

                    except Exception as e:
                        logger.error(f"Error processing plugin {plugin_name}: {e}")
                        # Fallback for this plugin
                        plugins_data["plugins"][plugin_name] = {
                            "name": plugin_name,
                            "description": "Plugin information unavailable",
                            "tools": [],
                            "enabled": True,
                            "type": "jarvis_plugin",
                            "voice_phrases": []
                        }

            # If we have plugin tools but no plugin instances, use the mapping approach
            elif plugin_tools_map:
                for plugin_name, tools in plugin_tools_map.items():
                    plugins_data["plugins"][plugin_name] = {
                        "name": plugin_name,
                        "description": f"Plugin with {len(tools)} tools",
                        "tools": [
                            {
                                "name": tool.name,
                                "description": tool.description or "No description available",
                                "enabled": True
                            }
                            for tool in tools
                        ],
                        "enabled": True,
                        "type": "jarvis_plugin",
                        "voice_phrases": []
                    }

            # Fallback: use all tools and group by heuristics
            else:
                logger.warning("No plugin structure found, using fallback approach")
                all_tools = plugin_manager.get_all_tools()

                # Group tools by common patterns
                plugins_by_name = {}

                for tool in all_tools:
                    # Determine plugin name from tool name patterns
                    tool_name = tool.name.lower()

                    if 'aider' in tool_name:
                        plugin_name = "AiderIntegration"
                    elif 'rag' in tool_name or 'memory' in tool_name:
                        plugin_name = "RAG Plugin"
                    elif 'web' in tool_name or 'lavague' in tool_name:
                        plugin_name = "LaVagueWebAutomation"
                    elif 'mcp' in tool_name:
                        plugin_name = "MCP Management"
                    elif 'time' in tool_name:
                        plugin_name = "DeviceTime"
                    elif 'ui' in tool_name or 'jarvis' in tool_name:
                        plugin_name = "Jarvis UI Tool"
                    elif 'profile' in tool_name or 'name' in tool_name:
                        plugin_name = "User Profile Tool"
                    elif 'log' in tool_name or 'terminal' in tool_name:
                        plugin_name = "LogTerminalTools"
                    elif 'robot' in tool_name or 'test' in tool_name:
                        plugin_name = "RobotFrameworkController"
                    else:
                        plugin_name = "Other Tools"

                    if plugin_name not in plugins_by_name:
                        plugins_by_name[plugin_name] = {
                            "name": plugin_name,
                            "description": f"Plugin containing {plugin_name.lower()} tools",
                            "tools": [],
                            "enabled": True,
                            "type": "jarvis_plugin",
                            "voice_phrases": []
                        }

                    plugins_by_name[plugin_name]["tools"].append({
                        "name": tool.name,
                        "description": tool.description or "No description available",
                        "enabled": True
                    })

                plugins_data["plugins"] = plugins_by_name

            logger.info(f"Serving {len(plugins_data['plugins'])} plugins")

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(plugins_data, indent=2).encode())

        except Exception as e:
            logger.error(f"Error serving plugins API: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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

            # Get MCP config manager
            from jarvis.tools import get_mcp_config_manager
            from jarvis.core.mcp_config_manager import MCPServerConfig, MCPTransportType
            config_manager = get_mcp_config_manager()

            if not config_manager:
                result = {"success": False, "message": "MCP config manager not available"}
            elif action == 'add':
                # Parse arguments - handle both string and list
                args_data = data.get('args', '')
                if isinstance(args_data, list):
                    args_list = args_data
                elif isinstance(args_data, str):
                    args_list = [arg.strip() for arg in args_data.split() if arg.strip()] if args_data else []
                else:
                    args_list = []

                # Parse environment variables
                env_str = data.get('env', '')
                env_dict = {}
                if env_str:
                    for line in env_str.split('\n'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            env_dict[key.strip()] = value.strip()

                # Create server configuration with only valid fields
                config = MCPServerConfig(
                    name=data.get('name', '').strip(),
                    description=data.get('description', ''),
                    transport=MCPTransportType(data.get('transport', 'stdio')),
                    command=data.get('command', '').strip(),
                    args=args_list,
                    env=env_dict,
                    enabled=data.get('enabled', True),
                    timeout=int(data.get('timeout', 30))
                )

                success = config_manager.add_server(config)
                result = {"success": success, "message": f"Server '{config.name}' added successfully" if success else "Failed to add server"}

            elif action == 'remove':
                server_name = data.get('name')
                success = config_manager.remove_server(server_name)
                result = {"success": success, "message": f"Server '{server_name}' removed successfully" if success else "Failed to remove server"}

            elif action == 'test':
                # For test, create a temporary config and try to validate it
                try:
                    # Parse arguments - handle both string and list
                    args_data = data.get('args', '')
                    if isinstance(args_data, list):
                        args_list = args_data
                    elif isinstance(args_data, str):
                        args_list = [arg.strip() for arg in args_data.split() if arg.strip()] if args_data else []
                    else:
                        args_list = []

                    # Parse environment variables
                    env_str = data.get('env', '')
                    env_dict = {}
                    if env_str:
                        for line in env_str.split('\n'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                env_dict[key.strip()] = value.strip()

                    config = MCPServerConfig(
                        name=data.get('name', 'test'),
                        description=data.get('description', ''),
                        transport=MCPTransportType(data.get('transport', 'stdio')),
                        command=data.get('command', '').strip(),
                        args=args_list,
                        env=env_dict,
                        timeout=int(data.get('timeout', 30))
                    )
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
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Error handling MCP connect action: {e}")
            logger.error(f"Full traceback: {error_details}")
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

    def handle_plugin_action(self):
        """Handle plugin management actions (add, edit, delete)."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            action = data.get('action')
            result = {"success": False, "message": "Unknown action"}

            if action == 'add':
                result = self._add_plugin(data)
            elif action == 'edit':
                result = self._edit_plugin(data)
            elif action == 'delete':
                result = self._delete_plugin(data)
            elif action == 'toggle':
                result = self._toggle_plugin(data)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            logger.error(f"Error handling plugin action: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def _add_plugin(self, data):
        """Add a new plugin."""
        try:
            plugin_name = data.get('name', '').strip()
            plugin_description = data.get('description', '').strip()
            plugin_code = data.get('code', '').strip()
            voice_phrases = data.get('voice_phrases', [])

            if not plugin_name or not plugin_code:
                return {"success": False, "message": "Plugin name and code are required"}

            # Ensure plugins directory exists
            import os
            plugins_dir = "jarvis/tools/plugins"
            os.makedirs(plugins_dir, exist_ok=True)

            # Create plugin file
            plugin_filename = f"{plugin_name.lower().replace(' ', '_')}_plugin.py"
            plugin_path = os.path.join(plugins_dir, plugin_filename)

            # Check if plugin already exists
            if os.path.exists(plugin_path):
                return {"success": False, "message": f"Plugin '{plugin_name}' already exists"}

            # Generate plugin code with voice phrases
            plugin_template = self._generate_plugin_code(plugin_name, plugin_description, plugin_code, voice_phrases, data.get('version', '1.0.0'), data.get('author', 'User'))

            # Write plugin file
            with open(plugin_path, 'w') as f:
                f.write(plugin_template)

            # Refresh plugin manager
            from jarvis.tools import plugin_manager
            plugin_manager.refresh_plugins()

            return {"success": True, "message": f"Plugin '{plugin_name}' added successfully"}
        except Exception as e:
            logger.error(f"Error adding plugin: {e}")
            return {"success": False, "message": f"Error adding plugin: {str(e)}"}

    def _edit_plugin(self, data):
        """Edit an existing plugin."""
        try:
            plugin_name = data.get('name', '').strip()
            # For now, return success - full edit functionality would require more complex file parsing
            return {"success": True, "message": f"Plugin '{plugin_name}' edit functionality coming soon"}
        except Exception as e:
            logger.error(f"Error editing plugin: {e}")
            return {"success": False, "message": f"Error editing plugin: {str(e)}"}

    def _delete_plugin(self, data):
        """Delete a plugin."""
        try:
            plugin_name = data.get('name', '').strip()

            if not plugin_name:
                return {"success": False, "message": "Plugin name is required"}

            # Find plugin file in multiple possible directories
            import os
            import glob

            # Check both possible plugin directories
            possible_dirs = [
                "jarvis/plugins",  # Main plugins directory
                "jarvis/tools/plugins"  # User-created plugins directory
            ]

            # Look for plugin files that might match
            possible_files = [
                f"{plugin_name.lower().replace(' ', '_')}.py",
                f"{plugin_name.lower().replace(' ', '_')}_plugin.py",
                f"{plugin_name.lower()}_plugin.py",
                f"{plugin_name}_plugin.py",
                f"{plugin_name.lower()}.py",
                f"{plugin_name}.py"
            ]

            deleted_file = None
            deleted_path = None

            # Search in all directories for the plugin file
            for plugins_dir in possible_dirs:
                if not os.path.exists(plugins_dir):
                    continue

                for filename in possible_files:
                    file_path = os.path.join(plugins_dir, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        deleted_file = filename
                        deleted_path = file_path
                        break

                if deleted_file:
                    break

            if deleted_file:
                # Also remove compiled Python cache files
                try:
                    cache_dir = os.path.join(os.path.dirname(deleted_path), "__pycache__")
                    if os.path.exists(cache_dir):
                        cache_file = os.path.join(cache_dir, f"{os.path.splitext(deleted_file)[0]}.cpython-*.pyc")
                        import glob
                        for cache_file_path in glob.glob(cache_file):
                            os.remove(cache_file_path)
                except Exception as cache_error:
                    logger.warning(f"Could not remove cache files: {cache_error}")

                # Refresh plugin manager
                try:
                    from jarvis.plugins.manager import PluginManager
                    # Get the plugin manager instance and refresh
                    if hasattr(self.server, 'plugin_manager'):
                        self.server.plugin_manager.discover_and_load_plugins()
                    else:
                        logger.warning("Plugin manager not accessible for refresh")
                except Exception as refresh_error:
                    logger.warning(f"Could not refresh plugin manager: {refresh_error}")

                return {"success": True, "message": f"Plugin '{plugin_name}' deleted successfully from {deleted_path}"}
            else:
                # List available plugins for debugging
                available_plugins = []
                for plugins_dir in possible_dirs:
                    if os.path.exists(plugins_dir):
                        available_plugins.extend([f for f in os.listdir(plugins_dir) if f.endswith('.py')])

                return {"success": False, "message": f"Plugin file for '{plugin_name}' not found. Available plugins: {', '.join(available_plugins)}"}

        except Exception as e:
            logger.error(f"Error deleting plugin: {e}")
            return {"success": False, "message": f"Error deleting plugin: {str(e)}"}

    def _toggle_plugin(self, data):
        """Toggle plugin enabled/disabled state."""
        try:
            plugin_name = data.get('name', '').strip()
            enabled = data.get('enabled', True)
            # For now, return success - plugin toggling would require plugin state management
            return {"success": True, "message": f"Plugin '{plugin_name}' {'enabled' if enabled else 'disabled'}"}
        except Exception as e:
            logger.error(f"Error toggling plugin: {e}")
            return {"success": False, "message": f"Error toggling plugin: {str(e)}"}

    def _generate_plugin_code(self, name, description, code, voice_phrases, version="1.0.0", author="User"):
        """Generate plugin code template."""
        voice_phrases_str = ', '.join([f'"{phrase}"' for phrase in voice_phrases]) if voice_phrases else "None"

        return f'''"""
{name} Plugin for Jarvis Voice Assistant.

{description}

Version: {version}
Author: {author}
Voice Phrases: {voice_phrases_str}
"""

import logging
from langchain_core.tools import tool
from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)

{code}

class {name.replace(' ', '')}Plugin(PluginBase):
    """Plugin for {name}."""

    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="{name}",
            version="1.0.0",
            description="{description}",
            author="User Generated",
            tags=["user", "custom"],
            voice_phrases=[{voice_phrases_str}]
        )

    def get_tools(self) -> List:
        # Return your tools here
        return []

# Create plugin instance for automatic discovery
plugin = {name.replace(' ', '')}Plugin()
'''

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

    # RAG Management API Methods

    def serve_rag_status_api(self):
        """Serve RAG system status as JSON API."""
        try:
            rag_service = self._get_rag_service()
            if not rag_service:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "RAG service not available"}).encode())
                return

            # Get document statistics
            doc_stats = rag_service.get_document_stats()

            # Get ingested documents info
            ingested_docs = rag_service.get_ingested_documents()

            status_data = {
                "status": "active",
                "database": {
                    "total_documents": doc_stats.get("total_documents", 0),
                    "unique_sources": doc_stats.get("unique_sources", 0),
                    "collection_name": rag_service.config.rag.collection_name,
                    "vector_store_path": rag_service.config.rag.vector_store_path
                },
                "documents": {
                    "ingested_count": len(ingested_docs),
                    "documents_path": rag_service.config.rag.documents_path,
                    "supported_formats": [".txt", ".pdf", ".doc", ".docx"]
                },
                "intelligence": {
                    "document_llm": "qwen2.5:3b-instruct",
                    "features": ["query_optimization", "semantic_chunking", "result_synthesis"],
                    "capabilities": ["intelligent_search", "document_analysis", "quality_assessment"]
                }
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(status_data, indent=2).encode())

        except Exception as e:
            logger.error(f"Error serving RAG status API: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def serve_long_term_memory_api(self):
        """Serve long-term memory data as JSON API."""
        try:
            rag_service = self._get_rag_service()
            if not rag_service:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "RAG service not available"}).encode())
                return

            # Get all documents from the vector store
            try:
                collection = rag_service.vector_store._collection
                results = collection.get(include=['metadatas', 'documents'])

                memories = []
                if results and results.get('metadatas') and results.get('documents'):
                    for i, (metadata, document) in enumerate(zip(results['metadatas'], results['documents'])):
                        if metadata:
                            memory_item = {
                                "id": f"memory_{i}",
                                "content": document[:200] + "..." if len(document) > 200 else document,
                                "full_content": document,
                                "source": metadata.get('source', 'conversational'),
                                "source_type": metadata.get('source_type', 'conversational'),
                                "title": metadata.get('title', 'Untitled'),
                                "topics": metadata.get('topics', ''),
                                "concepts": metadata.get('concepts', ''),
                                "importance_score": metadata.get('importance_score', 0.5),
                                "timestamp": metadata.get('ingestion_timestamp', 'unknown'),
                                "intelligent_processing": metadata.get('intelligent_processing', False)
                            }
                            memories.append(memory_item)

                memory_data = {
                    "memories": memories,
                    "total_count": len(memories),
                    "conversational_count": len([m for m in memories if m['source_type'] == 'conversational']),
                    "document_count": len([m for m in memories if m['source_type'] == 'document'])
                }

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(memory_data, indent=2).encode())

            except Exception as e:
                logger.error(f"Error accessing vector store: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Vector store error: {str(e)}"}).encode())

        except Exception as e:
            logger.error(f"Error serving long-term memory API: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def serve_documents_api(self):
        """Serve documents information as JSON API."""
        try:
            rag_service = self._get_rag_service()
            if not rag_service:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "RAG service not available"}).encode())
                return

            # Get documents from the documents folder
            documents_path = Path(rag_service.config.rag.documents_path)
            documents_path.mkdir(parents=True, exist_ok=True)

            documents = []
            supported_extensions = {'.txt', '.pdf', '.doc', '.docx'}

            for file_path in documents_path.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                    stat = file_path.stat()
                    documents.append({
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "size_mb": round(stat.st_size / (1024 * 1024), 2),
                        "modified": time.ctime(stat.st_mtime),
                        "modified_timestamp": stat.st_mtime,
                        "extension": file_path.suffix.lower(),
                        "type": self._get_document_type(file_path.suffix.lower())
                    })

            # Get ingested documents info
            ingested_docs = rag_service.get_ingested_documents()

            # Mark which documents are ingested
            for doc in documents:
                doc["ingested"] = any(ing_doc["source"] == doc["name"] for ing_doc in ingested_docs)
                if doc["ingested"]:
                    # Find matching ingested doc for chunk count
                    matching = next((ing_doc for ing_doc in ingested_docs if ing_doc["source"] == doc["name"]), None)
                    doc["chunk_count"] = matching.get("chunk_count", 0) if matching else 0
                else:
                    doc["chunk_count"] = 0

            documents_data = {
                "documents": sorted(documents, key=lambda x: x["name"]),
                "total_count": len(documents),
                "ingested_count": len([d for d in documents if d["ingested"]]),
                "total_size_mb": round(sum(d["size"] for d in documents) / (1024 * 1024), 2),
                "documents_path": str(documents_path),
                "supported_formats": list(supported_extensions)
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(documents_data, indent=2).encode())

        except Exception as e:
            logger.error(f"Error serving documents API: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _get_document_type(self, extension: str) -> str:
        """Get human-readable document type from extension."""
        type_map = {
            '.txt': 'Text Document',
            '.pdf': 'PDF Document',
            '.doc': 'Word Document',
            '.docx': 'Word Document'
        }
        return type_map.get(extension, 'Unknown Document')

    def serve_document_stats_api(self):
        """Serve document statistics as JSON API."""
        try:
            rag_service = self._get_rag_service()
            if not rag_service:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "RAG service not available"}).encode())
                return

            # Get comprehensive document statistics
            doc_stats = rag_service.get_document_stats()
            ingested_docs = rag_service.get_ingested_documents()

            # Calculate additional statistics
            total_chunks = sum(doc.get("chunk_count", 0) for doc in ingested_docs)
            avg_chunks_per_doc = total_chunks / len(ingested_docs) if ingested_docs else 0

            stats_data = {
                "database": {
                    "total_documents": doc_stats.get("total_documents", 0),
                    "unique_sources": doc_stats.get("unique_sources", 0),
                    "total_chunks": total_chunks,
                    "average_chunks_per_document": round(avg_chunks_per_doc, 1)
                },
                "ingested_documents": ingested_docs,
                "processing": {
                    "intelligent_processing_enabled": True,
                    "features": ["semantic_chunking", "quality_assessment", "metadata_enrichment"],
                    "llm_model": "qwen2.5:3b-instruct"
                }
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(stats_data, indent=2).encode())

        except Exception as e:
            logger.error(f"Error serving document stats API: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def serve_rag_search_api(self):
        """Serve RAG search functionality as JSON API."""
        try:
            # Get query parameter
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            query = query_params.get('q', [''])[0]

            if not query:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Query parameter 'q' is required"}).encode())
                return

            rag_service = self._get_rag_service()
            if not rag_service:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "RAG service not available"}).encode())
                return

            # Perform intelligent search (this is async, so we need to handle it)
            def run_async_search():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(rag_service.intelligent_search(query, max_results=5))
                finally:
                    loop.close()

            search_results = run_async_search()

            # Convert Document objects to serializable format
            serializable_results = {}
            if search_results:
                serializable_results = {
                    "query_optimization": search_results.get("query_optimization", {}),
                    "synthesis": search_results.get("synthesis", {}),
                    "search_metadata": search_results.get("search_metadata", {}),
                    "retrieved_documents": []
                }

                # Convert Document objects to dictionaries
                for doc in search_results.get("retrieved_documents", []):
                    doc_dict = {
                        "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                        "metadata": dict(doc.metadata) if hasattr(doc, 'metadata') else {}
                    }
                    serializable_results["retrieved_documents"].append(doc_dict)

            # Format results for API response
            api_response = {
                "query": query,
                "results": serializable_results,
                "timestamp": time.time()
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(api_response, indent=2).encode())

        except Exception as e:
            logger.error(f"Error serving RAG search API: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    # RAG Management POST Handlers

    def handle_add_memory(self):
        """Handle adding new memory to long-term storage."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            fact = data.get('fact', '').strip()
            if not fact:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Fact content is required"}).encode())
                return

            rag_service = self._get_rag_service()
            if not rag_service:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "RAG service not available"}).encode())
                return

            # Add conversational memory
            rag_service.add_conversational_memory(fact)

            result = {
                "success": True,
                "message": f"Added memory: '{fact[:50]}{'...' if len(fact) > 50 else ''}'",
                "fact": fact
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            logger.error(f"Error adding memory: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_document_ingest(self):
        """Handle document ingestion request."""
        try:
            rag_service = self._get_rag_service()
            if not rag_service:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "RAG service not available"}).encode())
                return

            # Run document ingestion (this is async)
            def run_async_ingestion():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(rag_service.ingest_documents_from_folder())
                finally:
                    loop.close()

            ingestion_results = run_async_ingestion()

            result = {
                "success": True,
                "message": "Document ingestion completed",
                "results": ingestion_results
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result, indent=2).encode())

        except Exception as e:
            logger.error(f"Error ingesting documents: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_document_upload(self):
        """Handle document upload request."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            filename = data.get('filename', '').strip()
            content = data.get('content', '').strip()

            if not filename or not content:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Filename and content are required"}).encode())
                return

            rag_service = self._get_rag_service()
            if not rag_service:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "RAG service not available"}).encode())
                return

            # Save file to documents directory
            documents_path = Path(rag_service.config.rag.documents_path)
            documents_path.mkdir(parents=True, exist_ok=True)

            file_path = documents_path / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            result = {
                "success": True,
                "message": f"Document '{filename}' uploaded successfully",
                "filename": filename,
                "path": str(file_path),
                "size": len(content)
            }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_delete_memory(self):
        """Handle memory deletion request."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            memory_id = data.get('memory_id', '').strip()
            if not memory_id:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Memory ID is required"}).encode())
                return

            # Note: ChromaDB doesn't have easy individual document deletion by ID
            # This would require implementing a more sophisticated memory management system
            # For now, return a placeholder response
            result = {
                "success": False,
                "message": "Memory deletion not yet implemented",
                "note": "Individual memory deletion requires enhanced vector store management"
            }

            self.send_response(501)  # Not Implemented
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            logger.error(f"Error deleting memory: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def handle_document_delete(self):
        """Handle document deletion request."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            filename = data.get('filename', '').strip()
            if not filename:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Filename is required"}).encode())
                return

            rag_service = self._get_rag_service()
            if not rag_service:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "RAG service not available"}).encode())
                return

            # Delete file from documents directory
            documents_path = Path(rag_service.config.rag.documents_path)
            file_path = documents_path / filename

            if file_path.exists():
                file_path.unlink()
                result = {
                    "success": True,
                    "message": f"Document '{filename}' deleted successfully",
                    "filename": filename,
                    "note": "Document removed from filesystem. Re-run ingestion to update vector store."
                }
            else:
                result = {
                    "success": False,
                    "error": f"Document '{filename}' not found",
                    "filename": filename
                }

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

    def get_html_template(self, title: str, content: str) -> str:
        """Get the HTML template with the specified title and content."""
        return """
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

        .section-description {{
            color: #ccc;
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
            font-style: italic;
        }}

        input[type="range"] {{
            width: 100%;
            margin: 0.5rem 0;
            background: rgba(255, 255, 255, 0.1);
        }}

        input[type="range"] + span {{
            display: inline-block;
            min-width: 3rem;
            text-align: center;
            font-weight: bold;
            color: #2196F3;
            margin-left: 0.5rem;
        }}

        optgroup {{
            font-weight: bold;
            color: #333;
            background: #f5f5f5;
        }}

        optgroup option {{
            font-weight: normal;
            padding-left: 1rem;
            color: #666;
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

        /* Professional Plugin Cards */
        .plugins-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }}

        .plugin-card {{
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.06));
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 0;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            backdrop-filter: blur(12px);
        }}

        .plugin-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #6495ed, #4169e1, #1e90ff);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .plugin-card:hover {{
            transform: translateY(-6px);
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
            border-color: rgba(100, 149, 237, 0.4);
        }}

        .plugin-card:hover::before {{
            opacity: 1;
        }}

        .plugin-card.selected {{
            border-color: #6495ed;
            box-shadow: 0 12px 40px rgba(100, 149, 237, 0.25);
            background: linear-gradient(145deg, rgba(100, 149, 237, 0.15), rgba(100, 149, 237, 0.08));
        }}

        .plugin-card.selected::before {{
            opacity: 1;
        }}

        .plugin-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 2rem 2rem 0 2rem;
            margin-bottom: 1.5rem;
        }}

        .plugin-title {{
            margin: 0;
            color: #ffffff;
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            line-height: 1.2;
        }}

        .plugin-actions {{
            display: flex;
            gap: 0.75rem;
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translateX(12px);
        }}

        .plugin-card:hover .plugin-actions {{
            opacity: 1;
            transform: translateX(0);
        }}

        .btn-text {{
            background: rgba(255, 255, 255, 0.12);
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            cursor: pointer;
            color: #ffffff;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            white-space: nowrap;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(8px);
        }}

        .btn-text:hover {{
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}

        .btn-text.btn-danger:hover {{
            background: rgba(244, 67, 54, 0.25);
            color: #ff6b6b;
        }}

        .plugin-description {{
            color: #c8d3e0;
            margin-bottom: 1.5rem;
            line-height: 1.5;
            font-size: 0.95rem;
            padding: 0 2rem;
            opacity: 0.9;
        }}

        .plugin-stats {{
            display: flex;
            gap: 1.5rem;
            margin: 0;
            padding: 1.5rem 2rem 2rem 2rem;
            background: rgba(255, 255, 255, 0.03);
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }}

        .stat-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            flex: 1;
            color: #b8c5d1;
            font-size: 0.85rem;
            font-weight: 500;
        }}

        .stat-item strong {{
            display: block;
            color: #6495ed;
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}

        /* MCP Server Cards */
        .mcp-servers-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }}

        .mcp-server-card {{
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.06));
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 0;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            backdrop-filter: blur(12px);
        }}

        .mcp-server-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #32cd32, #228b22, #006400);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .mcp-server-card:hover {{
            transform: translateY(-6px);
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
            border-color: rgba(50, 205, 50, 0.4);
        }}

        .mcp-server-card:hover::before {{
            opacity: 1;
        }}

        .mcp-server-card.connected {{
            border-color: #32cd32;
            box-shadow: 0 12px 40px rgba(50, 205, 50, 0.25);
            background: linear-gradient(145deg, rgba(50, 205, 50, 0.15), rgba(50, 205, 50, 0.08));
        }}

        .mcp-server-card.connected::before {{
            opacity: 1;
        }}

        .mcp-server-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 2rem 2rem 0 2rem;
            margin-bottom: 1.5rem;
        }}

        .mcp-server-title {{
            margin: 0;
            color: #ffffff;
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            line-height: 1.2;
        }}

        .mcp-server-actions {{
            display: flex;
            gap: 0.75rem;
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translateX(12px);
        }}

        .mcp-server-card:hover .mcp-server-actions {{
            opacity: 1;
            transform: translateX(0);
        }}

        .mcp-server-description {{
            color: #c8d3e0;
            margin-bottom: 1.5rem;
            line-height: 1.5;
            font-size: 0.95rem;
            padding: 0 2rem;
            opacity: 0.9;
        }}

        .mcp-server-stats {{
            display: flex;
            gap: 1.5rem;
            margin: 0;
            padding: 1.5rem 2rem 2rem 2rem;
            background: rgba(255, 255, 255, 0.03);
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }}

        .mcp-server-status {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            flex: 1;
            color: #b8c5d1;
            font-size: 0.85rem;
            font-weight: 500;
        }}

        .mcp-server-status strong {{
            display: block;
            color: #32cd32;
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}

        .mcp-server-status.disconnected strong {{
            color: #ff6b6b;
        }}

        /* MCP Server Details Modal */
        .mcp-server-details {{
            color: #c8d3e0;
            line-height: 1.6;
        }}

        .mcp-server-details p {{
            margin: 0.75rem 0;
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .mcp-server-details p:last-child {{
            border-bottom: none;
        }}

        .mcp-server-details strong {{
            color: #ffffff;
            font-weight: 600;
            display: inline-block;
            min-width: 120px;
        }}

        .mcp-server-details h4 {{
            color: #6495ed;
            margin: 1.5rem 0 0.75rem 0;
            font-size: 1.1rem;
        }}

        .mcp-server-details ul {{
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }}

        .mcp-server-details li {{
            margin: 0.5rem 0;
        }}

        .mcp-timestamps {{
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 2px solid rgba(100, 149, 237, 0.3);
        }}

        .status-connected {{
            color: #32cd32;
            font-weight: 600;
        }}

        .status-disconnected {{
            color: #ff6b6b;
            font-weight: 600;
        }}

        /* Notification styles */
        .notification {{
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            max-width: 400px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}

        .notification.show {{
            transform: translateX(0);
        }}

        .notification-success {{
            background: linear-gradient(135deg, #32cd32, #228b22);
        }}

        .notification-error {{
            background: linear-gradient(135deg, #ff6b6b, #e74c3c);
        }}

        .notification-info {{
            background: linear-gradient(135deg, #6495ed, #4169e1);
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
                <a href="/agent" class="nav-link" data-page="agent">
                    <span class="icon">⚙️</span>Agent Config
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
                <a href="/rag" class="nav-link" data-page="rag">
                    <span class="icon">🧠</span>RAG Memory
                </a>
                <a href="/voice-profiles" class="nav-link" data-page="voice-profiles">
                    <span class="icon">🎭</span>Voice Profiles
                </a>
                <a href="/device" class="nav-link" data-page="device">
                    <span class="icon">💻</span>Device Info
                </a>
                <a href="/tools" class="nav-link" data-page="tools">
                    <span class="icon">🔧</span>Tools & Plugins
                </a>
                <a href="/mcp" class="nav-link" data-page="mcp">
                    <span class="icon">🔗</span>MCP Servers
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
        """.format(title=title, content=content)

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

        <script type="text/javascript">
        (function() {
            // Tools & Plugins JavaScript - Scoped to avoid conflicts
            let plugins = {};

            function loadPlugins() {
                console.log('loadPlugins() called');
                const pluginsList = document.getElementById('plugins-list');
                if (!pluginsList) {
                    console.log('plugins-list element not found');
                    return;
                }

                pluginsList.innerHTML = '<p>Loading plugins...</p>';

                fetch('/api/plugins')
                    .then(response => {
                        console.log('API response status:', response.status);
                        if (!response.ok) {
                            throw new Error('HTTP ' + response.status + ': ' + response.statusText);
                        }
                        return response.json();
                    })
                    .then(data => {
                        console.log('Plugins data received:', data);
                        plugins = data.plugins || {};
                        console.log('Number of plugins:', Object.keys(plugins).length);
                        renderPlugins();
                        updateToolsStatus();
                    })
                    .catch(error => {
                        console.error('Error loading plugins:', error);
                        if (pluginsList) {
                            pluginsList.innerHTML = '<p>Error loading plugins: ' + error.message + '</p>';
                        }
                    });
            }

            function renderPlugins() {
                const pluginsList = document.getElementById('plugins-list');

                if (!pluginsList) return;

                if (Object.keys(plugins).length === 0) {
                    pluginsList.innerHTML = '<p>No plugins found. The plugin system may still be loading.</p>';
                    return;
                }

                const html = Object.entries(plugins).map(function([name, plugin]) {
                    const toolsHtml = plugin.tools.map(function(tool) {
                        return '<li><strong>' + tool.name + '</strong>: ' + (tool.description || 'No description') + '</li>';
                    }).join('');

                    return '<div class="plugin-card">' +
                        '<div class="plugin-header">' +
                            '<h3 class="plugin-title">' + plugin.name + '</h3>' +
                        '</div>' +
                        '<div class="plugin-description">' + (plugin.description || 'No description available') + '</div>' +
                        (plugin.tools.length > 0 ?
                            '<div class="plugin-tools">' +
                                '<h5>Tools (' + plugin.tools.length + '):</h5>' +
                                '<ul class="tool-list">' + toolsHtml + '</ul>' +
                            '</div>' : ''
                        ) +
                    '</div>';
                }).join('');

                pluginsList.innerHTML = html;
            }

            function updateToolsStatus() {
                const activePluginsCount = document.getElementById('active-plugins-count');
                const availableToolsCount = document.getElementById('available-tools-count');
                const voiceCommandsCount = document.getElementById('voice-commands-count');

                if (activePluginsCount) {
                    activePluginsCount.textContent = Object.keys(plugins).length;
                }

                if (availableToolsCount) {
                    const totalTools = Object.values(plugins).reduce(function(sum, plugin) {
                        return sum + plugin.tools.length;
                    }, 0);
                    availableToolsCount.textContent = totalTools;
                }

                if (voiceCommandsCount) {
                    const totalCommands = Object.values(plugins).reduce(function(sum, plugin) {
                        return sum + (plugin.voice_phrases ? plugin.voice_phrases.length : 0);
                    }, 0);
                    voiceCommandsCount.textContent = totalCommands;
                }
            }

            window.showAddPluginModal = function() {
                alert('Add Plugin functionality coming soon!');
            };

            // Load plugins when DOM is ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('DOM loaded - loading plugins...');
                    setTimeout(loadPlugins, 100);
                });
            } else {
                console.log('DOM already ready - loading plugins immediately...');
                setTimeout(loadPlugins, 100);
            }
        })();
        </script>
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
                <h3>Agent Configuration</h3>
                <p>Configure agent execution settings including iteration limits, timeouts, and tool creation capabilities.</p>
                <a href="/agent" class="btn">Configure Agent</a>
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

        function shutdownUI() {
            if (confirm('Are you sure you want to shutdown the Jarvis UI server?')) {
                // For desktop app, send close window signal first
                if (window.pywebview || navigator.userAgent.includes('pywebview')) {
                    fetch('/api/close-window', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    })
                    .then(() => {
                        // Then shutdown the server
                        return fetch('/api/shutdown', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' }
                        });
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            // Desktop window should close automatically via monitoring
                            closeDesktopWindow();
                        }
                    })
                    .catch(error => {
                        // Server is shutting down, close window
                        closeDesktopWindow();
                    });
                } else {
                    // Browser - just shutdown normally
                    fetch('/api/shutdown', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('Jarvis UI server is shutting down. You can close this browser tab.');
                            setTimeout(() => {
                                window.close();
                            }, 2000);
                        } else {
                            alert('Error shutting down UI: ' + (data.error || 'Unknown error'));
                        }
                    })
                    .catch(error => {
                        alert('Jarvis UI server has been shut down. You can close this browser tab.');
                        setTimeout(() => {
                            window.close();
                        }, 2000);
                    });
                }
            }
        }
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
                    <label for="response_delay">Response Delay (seconds)</label>
                    <input type="number" id="response_delay" name="response_delay" min="0" max="2" step="0.1">
                    <small>Delay after speech completion before listening again</small>
                </div>
            </div>

            <div class="config-section">
                <h3>🎤 Coqui TTS Settings</h3>
                <p class="section-description">Configure advanced neural text-to-speech with Coqui TTS</p>

                <div class="form-group">
                    <label for="coqui_voice_preset">🎤 Voice Selection</label>
                    <select id="coqui_voice_preset" name="coqui_voice_preset">
                        <optgroup label="👩 US Female Voices (Ready to Use)">
                            <option value="ljspeech_tacotron2">Linda Johnson - Professional (Tacotron2)</option>
                            <option value="ljspeech_glow">Linda Johnson - Premium (Glow-TTS)</option>
                            <option value="ljspeech_fastpitch">Linda Johnson - Fast (FastPitch)</option>
                        </optgroup>
                        <optgroup label="👨 US Male Voices (VCTK Multi-Speaker)">
                            <option value="vctk_p302">American Male 302 (Age 23)</option>
                            <option value="vctk_p304">American Male 304 (Age 23)</option>
                            <option value="vctk_p311">American Male 311 (Age 21)</option>
                            <option value="vctk_p316">American Male 316 (Age 26)</option>
                            <option value="vctk_p326">American Male 326 (Age 26)</option>
                            <option value="vctk_p334">American Male 334 (Age 18)</option>
                            <option value="vctk_p345">American Male 345 (Age 22)</option>
                            <option value="vctk_p347">American Male 347 (Age 20)</option>
                            <option value="vctk_p360">American Male 360 (Age 19)</option>
                            <option value="vctk_p363">American Male 363 (Age 22)</option>
                            <option value="vctk_p364">American Male 364 (Age 22)</option>
                            <option value="vctk_p374">American Male 374 (Age 28)</option>
                            <option value="vctk_p376">American Male 376 (Age 19)</option>
                        </optgroup>
                        <optgroup label="👩 US Female Voices (VCTK Multi-Speaker)">
                            <option value="vctk_p300">American Female 300 (Age 26)</option>
                            <option value="vctk_p301">American Female 301 (Age 18)</option>
                            <option value="vctk_p303">American Female 303 (Age 26)</option>
                            <option value="vctk_p305">American Female 305 (Age 22)</option>
                            <option value="vctk_p306">American Female 306 (Age 26)</option>
                            <option value="vctk_p307">American Female 307 (Age 21)</option>
                            <option value="vctk_p308">American Female 308 (Age 20)</option>
                            <option value="vctk_p310">American Female 310 (Age 21)</option>
                            <option value="vctk_p312">American Female 312 (Age 20)</option>
                            <option value="vctk_p313">American Female 313 (Age 22)</option>
                            <option value="vctk_p314">American Female 314 (Age 26)</option>
                            <option value="vctk_p317">American Female 317 (Age 20)</option>
                            <option value="vctk_p318">American Female 318 (Age 21)</option>
                            <option value="vctk_p323">American Female 323 (Age 19)</option>
                            <option value="vctk_p329">American Female 329 (Age 23)</option>
                            <option value="vctk_p330">American Female 330 (Age 26)</option>
                            <option value="vctk_p333">American Female 333 (Age 24)</option>
                            <option value="vctk_p335">American Female 335 (Age 23)</option>
                            <option value="vctk_p336">American Female 336 (Age 19)</option>
                            <option value="vctk_p339">American Female 339 (Age 21)</option>
                            <option value="vctk_p340">American Female 340 (Age 19)</option>
                            <option value="vctk_p341">American Female 341 (Age 18)</option>
                            <option value="vctk_p343">American Female 343 (Age 20)</option>
                            <option value="vctk_p351">American Female 351 (Age 21)</option>
                            <option value="vctk_p361">American Female 361 (Age 21)</option>
                            <option value="vctk_p362">American Female 362 (Age 22)</option>
                        </optgroup>
                        <optgroup label="🌍 Advanced Models">
                            <option value="custom_model">Custom Model Configuration</option>
                        </optgroup>
                    </select>
                    <small>Choose from 42 US English voices. Single-speaker models work immediately, multi-speaker models offer natural variety.</small>
                </div>

                <div class="form-group" id="custom_model_group" style="display: none;">
                    <label for="coqui_model">Custom TTS Model</label>
                    <select id="coqui_model" name="coqui_model">
                        <optgroup label="🚀 Single Speaker Models">
                            <option value="tts_models/en/ljspeech/tacotron2-DDC">Tacotron2 + HiFiGAN</option>
                            <option value="tts_models/en/ljspeech/glow-tts">Glow-TTS</option>
                            <option value="tts_models/en/ljspeech/fast_pitch">FastPitch</option>
                            <option value="tts_models/en/ljspeech/vits">VITS</option>
                        </optgroup>
                        <optgroup label="👥 Multi-Speaker Models">
                            <option value="tts_models/en/vctk/vits">VCTK VITS (109 Speakers)</option>
                            <option value="tts_models/en/sam/tacotron-DDC">SAM Tacotron</option>
                        </optgroup>
                        <optgroup label="🌍 Multilingual Models">
                            <option value="tts_models/multilingual/multi-dataset/xtts_v2">XTTS v2 (49 Languages)</option>
                            <option value="tts_models/multilingual/multi-dataset/your_tts">YourTTS</option>
                        </optgroup>
                    </select>
                    <small>Advanced model selection for custom configurations.</small>
                </div>

                <div class="form-group">
                    <label for="coqui_voice_speed">Voice Speed</label>
                    <input type="range" id="coqui_voice_speed" name="coqui_voice_speed" min="0.5" max="2.0" step="0.1" value="1.0">
                    <span id="coqui_voice_speed_value">1.0x</span>
                    <small>Adjust speech speed (0.5x = slow, 1.0x = normal, 2.0x = fast)</small>
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
                    <label for="coqui_device">Processing Device</label>
                    <select id="coqui_device" name="coqui_device">
                        <option value="cpu">🖥️ CPU (Most Compatible)</option>
                        <option value="auto">🤖 Auto-Detect</option>
                        <option value="cuda">🚀 NVIDIA GPU (CUDA)</option>
                        <option value="mps">🍎 Apple Silicon (MPS)</option>
                    </select>
                    <small>CPU is most stable, GPU is faster but may have compatibility issues</small>
                </div>

                <div class="form-group">
                    <div class="checkbox-label">
                        <input type="checkbox" id="coqui_use_gpu" name="coqui_use_gpu">
                        <label for="coqui_use_gpu">Enable GPU Acceleration</label>
                    </div>
                    <small>Use GPU for faster processing (requires compatible hardware)</small>
                </div>

                <div class="form-group">
                    <label for="coqui_speaker_id">Speaker ID (Multi-Speaker Models)</label>
                    <input type="text" id="coqui_speaker_id" name="coqui_speaker_id" placeholder="p225, p226, etc.">
                    <small>Speaker ID for multi-speaker models (e.g., VCTK speakers: p225, p226, p227...)</small>
                </div>

                <div class="form-group">
                    <label for="coqui_speaker_wav">🎭 Voice Cloning Audio File</label>
                    <input type="text" id="coqui_speaker_wav" name="coqui_speaker_wav" placeholder="/path/to/voice_sample.wav">
                    <small>WAV file (3-10 seconds) for voice cloning with XTTS models. Clear speech, no background noise.</small>
                </div>

                <div class="form-group">
                    <label for="coqui_voice_conditioning_latents">Voice Conditioning Latents</label>
                    <input type="text" id="coqui_voice_conditioning_latents" name="coqui_voice_conditioning_latents" placeholder="/path/to/conditioning_latents.pth">
                    <small>Pre-computed voice conditioning latents for faster voice cloning (optional)</small>
                </div>

                <div class="form-group">
                    <label for="coqui_emotion">Emotion/Style</label>
                    <select id="coqui_emotion" name="coqui_emotion">
                        <option value="neutral">😐 Neutral</option>
                        <option value="happy">😊 Happy</option>
                        <option value="sad">😢 Sad</option>
                        <option value="angry">😠 Angry</option>
                        <option value="surprised">😲 Surprised</option>
                        <option value="calm">😌 Calm</option>
                        <option value="excited">🤩 Excited</option>
                    </select>
                    <small>Emotional tone for speech synthesis (model-dependent)</small>
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
                        <label for="coqui_streaming">🌊 Enable Streaming Mode</label>
                    </div>
                    <small>Real-time streaming synthesis for faster response (experimental)</small>
                </div>
            </div>

            <div class="config-section">
                <h3>🎛️ Advanced Coqui Settings</h3>
                <p class="section-description">Fine-tune voice quality and performance</p>

                <div class="form-group">
                    <label for="coqui_sample_rate">Sample Rate (Hz)</label>
                    <select id="coqui_sample_rate" name="coqui_sample_rate">
                        <option value="16000">16 kHz (Phone Quality)</option>
                        <option value="22050">22.05 kHz (Standard)</option>
                        <option value="24000">24 kHz (High Quality)</option>
                        <option value="44100">44.1 kHz (CD Quality)</option>
                        <option value="48000">48 kHz (Professional)</option>
                    </select>
                    <small>Audio sample rate - higher = better quality but larger files</small>
                </div>

                <div class="form-group">
                    <label for="coqui_vocoder_model">Vocoder Model</label>
                    <select id="coqui_vocoder_model" name="coqui_vocoder_model">
                        <option value="auto">🤖 Auto (Recommended)</option>
                        <option value="vocoder_models/en/ljspeech/hifigan_v2">HiFiGAN v2 (Fast)</option>
                        <option value="vocoder_models/en/ljspeech/multiband-melgan">MultiBand MelGAN (Quality)</option>
                        <option value="vocoder_models/universal/libri-tts/wavegrad">WaveGrad (Universal)</option>
                    </select>
                    <small>Vocoder converts mel-spectrograms to audio waveforms</small>
                </div>

                <div class="form-group">
                    <label for="coqui_speed_factor">Speed Factor</label>
                    <input type="range" id="coqui_speed_factor" name="coqui_speed_factor" min="0.25" max="4.0" step="0.25" value="1.0">
                    <span id="coqui_speed_factor_value">1.0x</span>
                    <small>Fine-tune speech speed (0.25x = very slow, 4.0x = very fast)</small>
                </div>

                <div class="form-group">
                    <div class="checkbox-label">
                        <input type="checkbox" id="coqui_enable_text_splitting" name="coqui_enable_text_splitting">
                        <label for="coqui_enable_text_splitting">📝 Enable Text Splitting</label>
                    </div>
                    <small>Split long texts into sentences for better synthesis quality</small>
                </div>

                <div class="form-group">
                    <div class="checkbox-label">
                        <input type="checkbox" id="coqui_do_trim_silence" name="coqui_do_trim_silence">
                        <label for="coqui_do_trim_silence">✂️ Trim Silence</label>
                    </div>
                    <small>Remove silence from beginning and end of generated audio</small>
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

                        // Voice preset selection
                        document.getElementById('coqui_voice_preset').value = audio.coqui_voice_preset || 'ljspeech_tacotron2';

                        // Advanced Coqui settings
                        document.getElementById('coqui_voice_speed').value = audio.coqui_voice_speed || 1.0;
                        document.getElementById('coqui_voice_speed_value').textContent = (audio.coqui_voice_speed || 1.0) + 'x';
                        document.getElementById('coqui_speaker_id').value = audio.coqui_speaker_id || '';
                        document.getElementById('coqui_voice_conditioning_latents').value = audio.coqui_voice_conditioning_latents || '';
                        document.getElementById('coqui_emotion').value = audio.coqui_emotion || 'neutral';
                        document.getElementById('coqui_sample_rate').value = audio.coqui_sample_rate || 22050;
                        document.getElementById('coqui_vocoder_model').value = audio.coqui_vocoder_model || 'auto';
                        document.getElementById('coqui_speed_factor').value = audio.coqui_speed_factor || 1.0;
                        document.getElementById('coqui_speed_factor_value').textContent = (audio.coqui_speed_factor || 1.0) + 'x';
                        document.getElementById('coqui_enable_text_splitting').checked = audio.coqui_enable_text_splitting !== undefined ? audio.coqui_enable_text_splitting : true;
                        document.getElementById('coqui_do_trim_silence').checked = audio.coqui_do_trim_silence !== undefined ? audio.coqui_do_trim_silence : true;

                    }
                })
                .catch(error => console.error('Error loading audio config:', error));
        }

        // Handle voice preset selection
        document.getElementById('coqui_voice_preset').addEventListener('change', function() {
            const customGroup = document.getElementById('custom_model_group');
            if (this.value === 'custom_model') {
                customGroup.style.display = 'block';
            } else {
                customGroup.style.display = 'none';
            }
        });

        // Handle range slider updates for real-time feedback
        document.getElementById('coqui_voice_speed').addEventListener('input', function() {
            document.getElementById('coqui_voice_speed_value').textContent = this.value + 'x';
        });

        document.getElementById('coqui_speed_factor').addEventListener('input', function() {
            document.getElementById('coqui_speed_factor_value').textContent = this.value + 'x';
        });

        document.getElementById('audio-config-form').addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const audioConfig = {};

            for (let [key, value] of formData.entries()) {
                if (key.includes('_')) {
                    if (['mic_index', 'energy_threshold', 'tts_rate', 'coqui_top_k', 'coqui_sample_rate'].includes(key)) {
                        audioConfig[key] = parseInt(value);
                    } else if (['timeout', 'phrase_time_limit', 'tts_volume', 'response_delay', 'coqui_temperature', 'coqui_length_penalty', 'coqui_repetition_penalty', 'coqui_top_p', 'coqui_voice_speed', 'coqui_speed_factor'].includes(key)) {
                        audioConfig[key] = parseFloat(value);
                    } else if (['coqui_use_gpu', 'coqui_streaming', 'coqui_enable_text_splitting', 'coqui_do_trim_silence'].includes(key)) {
                        audioConfig[key] = true;

                    } else {
                        audioConfig[key] = value;
                    }
                }
            }

            if (!formData.has('coqui_use_gpu')) audioConfig.coqui_use_gpu = false;
            if (!formData.has('coqui_streaming')) audioConfig.coqui_streaming = false;

            if (!formData.has('coqui_enable_text_splitting')) audioConfig.coqui_enable_text_splitting = false;
            if (!formData.has('coqui_do_trim_silence')) audioConfig.coqui_do_trim_silence = false;

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

    def get_agent_config_content(self) -> str:
        """Get the agent configuration content."""
        return """
        <div class="page-header">
            <h1>Agent Configuration</h1>
            <div class="breadcrumb">
                <a href="/">Home</a> / <a href="/settings">Settings</a> / <a href="/agent">Agent</a>
            </div>
        </div>

        <form id="agent-config-form" class="config-form">
            <div class="config-section">
                <h3>Execution Settings</h3>
                <p>Configure how the AI agent processes complex requests and creates tools.</p>

                <div class="form-group">
                    <label for="max_iterations">Max Iterations</label>
                    <input type="number" id="max_iterations" name="max_iterations" min="1" max="50" step="1">
                    <small>Maximum number of thinking steps for complex tasks (default: 15, increased from 5 for tool creation)</small>
                </div>

                <div class="form-group">
                    <label for="max_execution_time">Max Execution Time (seconds)</label>
                    <input type="number" id="max_execution_time" name="max_execution_time" min="10" max="600" step="10">
                    <small>Maximum time allowed for complex operations (default: 120 seconds, increased from 30 for tool creation)</small>
                </div>
            </div>

            <div class="config-section">
                <h3>Memory & Error Handling</h3>

                <div class="form-group">
                    <div class="checkbox-group">
                        <input type="checkbox" id="enable_memory" name="enable_memory">
                        <label for="enable_memory">Enable Conversation Memory</label>
                    </div>
                    <small>Allow the agent to remember conversation context</small>
                </div>

                <div class="form-group">
                    <div class="checkbox-group">
                        <input type="checkbox" id="handle_parsing_errors" name="handle_parsing_errors">
                        <label for="handle_parsing_errors">Handle Parsing Errors</label>
                    </div>
                    <small>Automatically recover from tool calling errors</small>
                </div>
            </div>

            <div class="form-actions">
                <button type="submit" class="btn">Save Agent Configuration</button>
                <button type="button" class="btn btn-secondary" onclick="loadAgentConfig()">Reset to Current</button>
            </div>
        </form>

        <div class="info-section">
            <h3>Performance Impact</h3>
            <div class="info-card">
                <h4>🚀 Tool Creation Capability</h4>
                <p>Higher iteration limits (15+) enable Jarvis to create custom tools and handle complex multi-step requests.</p>
            </div>
            <div class="info-card">
                <h4>⏱️ Response Time</h4>
                <p>Longer execution times (120s+) allow for complex operations like code generation and tool development.</p>
            </div>
            <div class="info-card">
                <h4>🎯 Recommended Settings</h4>
                <p><strong>Tool Creation:</strong> 15+ iterations, 120+ seconds<br>
                   <strong>Fast Responses:</strong> 5-10 iterations, 30-60 seconds</p>
            </div>
        </div>

        <script>
        function loadAgentConfig() {
            fetch('/api/config')
                .then(response => response.json())
                .then(data => {
                    if (data.agent) {
                        const agent = data.agent;
                        document.getElementById('max_iterations').value = agent.max_iterations || 15;
                        document.getElementById('max_execution_time').value = agent.max_execution_time || 120;
                        document.getElementById('enable_memory').checked = agent.enable_memory !== false;
                        document.getElementById('handle_parsing_errors').checked = agent.handle_parsing_errors !== false;
                    }
                })
                .catch(error => console.error('Error loading agent config:', error));
        }

        document.getElementById('agent-config-form').addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const agentConfig = {
                max_iterations: parseInt(formData.get('max_iterations')) || 15,
                max_execution_time: parseInt(formData.get('max_execution_time')) || 120,
                enable_memory: formData.get('enable_memory') === 'on',
                handle_parsing_errors: formData.get('handle_parsing_errors') === 'on'
            };

            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({agent: agentConfig})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Agent configuration saved successfully! Restart Jarvis to apply changes.');
                } else {
                    alert('Error saving configuration: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => alert('Error saving configuration: ' + error.message));
        });

        loadAgentConfig();
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
                        <input type="checkbox" id="enable_full_duplex" name="enable_full_duplex" disabled>
                        <label for="enable_full_duplex" style="color: #888;">Enable Full Duplex Mode (Disabled)</label>
                    </div>
                    <small style="color: #888;">Full-duplex mode has been removed due to TTS cutoff issues. Jarvis now uses reliable single-mode conversation.</small>
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
                        document.getElementById('enable_full_duplex').checked = false;  // Always disabled
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
                enable_full_duplex: false  // Always disabled - full-duplex removed
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

    def get_tools_content(self) -> str:
        """Get the Tools & Plugins management content - Clean rebuild."""
        return """
        <div class="page-header">
            <h1>Tools & Plugins</h1>
            <div class="breadcrumb">
                <a href="/settings">Settings</a> > Tools & Plugins
            </div>
        </div>

        <div class="info-banner">
            <h3>Jarvis Tools & Plugins</h3>
            <p>Manage your Jarvis plugins and tools. View current plugins, add custom tools, and configure voice commands.</p>

            <div class="tools-status-overview" id="tools-status-overview">
                <div class="status-item">
                    <span class="status-label">Active Plugins:</span>
                    <span class="status-value" id="active-plugins-count">0</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Available Tools:</span>
                    <span class="status-value" id="available-tools-count">0</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Voice Commands:</span>
                    <span class="status-value" id="voice-commands-count">0</span>
                </div>
            </div>
        </div>

        <div class="config-section">
            <div class="section-header">
                <h2>Current Plugins</h2>
                <button class="btn btn-primary" id="add-plugin-btn">
                    Add Plugin
                </button>
            </div>

            <div id="plugins-list" class="plugins-grid">
                <p>Loading plugins...</p>
            </div>
        </div>

        <!-- Plugin Details Modal -->
        <div id="plugin-modal" class="modal-overlay" style="display: none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 id="modal-title">Plugin Details</h3>
                    <button class="modal-close" id="modal-close">&times;</button>
                </div>
                <div class="modal-body" id="modal-body">
                    <!-- Content populated by JavaScript -->
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" id="modal-close-btn">Close</button>
                </div>
            </div>
        </div>

        <!-- Add Plugin Form Modal -->
        <div id="add-plugin-modal" class="modal-overlay" style="display: none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add New Plugin</h3>
                    <button class="modal-close" id="add-modal-close">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="add-plugin-form">
                        <div class="form-group">
                            <label for="plugin-name">Plugin Name *</label>
                            <input type="text" id="plugin-name" name="name" required
                                   placeholder="Enter plugin name (e.g., MyCustomTool)">
                            <small>Use PascalCase for plugin names (no spaces or special characters)</small>
                        </div>

                        <div class="form-group">
                            <label for="plugin-description">Description *</label>
                            <textarea id="plugin-description" name="description" rows="3" required
                                      placeholder="Describe what this plugin does..."></textarea>
                        </div>

                        <div class="form-group">
                            <label for="plugin-version">Version</label>
                            <input type="text" id="plugin-version" name="version"
                                   placeholder="1.0.0" value="1.0.0">
                        </div>

                        <div class="form-group">
                            <label for="plugin-author">Author</label>
                            <input type="text" id="plugin-author" name="author"
                                   placeholder="Your name">
                        </div>

                        <div class="form-group">
                            <label for="plugin-code">Plugin Code *</label>
                            <textarea id="plugin-code" name="code" rows="12" required
                                      placeholder="Enter your Python plugin code here..."></textarea>
                            <small>Write Python code that defines your plugin class and tools</small>
                        </div>

                        <div class="form-group">
                            <label>Voice Commands</label>
                            <div class="voice-commands-section">
                                <div class="voice-input-group">
                                    <input type="text" id="voice-command-input"
                                           placeholder="Enter voice command phrase (e.g., 'run my custom tool')">
                                    <button type="button" id="add-voice-command" class="btn btn-secondary">Add</button>
                                </div>
                                <div id="voice-commands-list" class="voice-commands-list">
                                    <!-- Voice commands will be added here -->
                                </div>
                                <small>Add voice phrases that will trigger this plugin. Users can say these phrases to activate your tools.</small>
                            </div>
                        </div>

                        <div class="form-group">
                            <div class="form-help">
                                <h4>Plugin Development Tips:</h4>
                                <ul>
                                    <li>Your plugin should inherit from the base Plugin class</li>
                                    <li>Define tools using the @tool decorator</li>
                                    <li>Include proper docstrings for all functions</li>
                                    <li>Test your code before submitting</li>
                                    <li>Voice commands should be natural phrases users would say</li>
                                </ul>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" id="add-modal-cancel">Cancel</button>
                    <button type="submit" form="add-plugin-form" class="btn btn-primary">Create Plugin</button>
                </div>
            </div>
        </div>

        <script>
        // Clean Tools & Plugins JavaScript - Modern ES6+ approach
        class ToolsManager {
            constructor() {
                this.plugins = {};
                this.modal = null;
                this.voiceCommands = [];
                this.init();
            }

            init() {
                this.setupEventListeners();
                this.loadPlugins();
            }

            setupEventListeners() {
                // Add plugin button
                const addBtn = document.getElementById('add-plugin-btn');
                if (addBtn) {
                    addBtn.addEventListener('click', () => this.showAddPluginModal());
                }

                // Plugin details modal close handlers
                const modal = document.getElementById('plugin-modal');
                if (modal) {
                    const closeBtn = modal.querySelector('#modal-close');
                    const closeBtnFooter = modal.querySelector('#modal-close-btn');

                    if (closeBtn) closeBtn.addEventListener('click', () => this.hideModal());
                    if (closeBtnFooter) closeBtnFooter.addEventListener('click', () => this.hideModal());

                    // Close on background click
                    modal.addEventListener('click', (e) => {
                        if (e.target === modal) this.hideModal();
                    });
                }

                // Add plugin modal handlers
                const addModal = document.getElementById('add-plugin-modal');
                if (addModal) {
                    const closeBtn = addModal.querySelector('#add-modal-close');
                    const cancelBtn = addModal.querySelector('#add-modal-cancel');

                    if (closeBtn) closeBtn.addEventListener('click', () => this.hideAddPluginModal());
                    if (cancelBtn) cancelBtn.addEventListener('click', () => this.hideAddPluginModal());

                    // Close on background click
                    addModal.addEventListener('click', (e) => {
                        if (e.target === addModal) this.hideAddPluginModal();
                    });
                }

                // Voice command handlers
                const addVoiceBtn = document.getElementById('add-voice-command');
                const voiceInput = document.getElementById('voice-command-input');

                if (addVoiceBtn) {
                    addVoiceBtn.addEventListener('click', () => this.addVoiceCommand());
                }

                if (voiceInput) {
                    voiceInput.addEventListener('keypress', (e) => {
                        if (e.key === 'Enter') {
                            e.preventDefault();
                            this.addVoiceCommand();
                        }
                    });
                }

                // Form submission
                const form = document.getElementById('add-plugin-form');
                if (form) {
                    form.addEventListener('submit', (e) => this.handleFormSubmit(e));
                }
            }

            async loadPlugins() {
                console.log('Loading plugins...');
                const pluginsList = document.getElementById('plugins-list');

                if (!pluginsList) {
                    console.error('plugins-list element not found');
                    return;
                }

                try {
                    pluginsList.innerHTML = '<p>Loading plugins...</p>';

                    const response = await fetch('/api/plugins');
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const data = await response.json();
                    this.plugins = data.plugins || {};

                    console.log(`Loaded ${Object.keys(this.plugins).length} plugins`);

                    this.renderPlugins();
                    this.updateStatus();

                } catch (error) {
                    console.error('Error loading plugins:', error);
                    pluginsList.innerHTML = `<p>Error loading plugins: ${error.message}</p>`;
                }
            }

            renderPlugins() {
                const pluginsList = document.getElementById('plugins-list');
                if (!pluginsList) return;

                if (Object.keys(this.plugins).length === 0) {
                    pluginsList.innerHTML = '<p>No plugins found. The plugin system may still be loading.</p>';
                    return;
                }

                // Clear container
                pluginsList.innerHTML = '';

                // Create plugin cards
                Object.entries(this.plugins).forEach(([name, plugin]) => {
                    const card = this.createPluginCard(name, plugin);
                    pluginsList.appendChild(card);
                });
            }

            createPluginCard(name, plugin) {
                const toolCount = plugin.tools?.length || 0;
                const voiceCount = plugin.voice_phrases?.length || 0;

                // Main card
                const card = document.createElement('div');
                card.className = 'plugin-card';
                card.addEventListener('click', () => this.selectPlugin(name, card));

                // Header
                const header = document.createElement('div');
                header.className = 'plugin-header';

                const title = document.createElement('h3');
                title.className = 'plugin-title';
                title.textContent = plugin.name || name;

                const actions = document.createElement('div');
                actions.className = 'plugin-actions';

                // Action buttons
                const viewBtn = this.createActionButton('View', 'View Details', () => this.viewPlugin(name));
                const editBtn = this.createActionButton('Edit', 'Edit Plugin', () => this.editPlugin(name));
                const deleteBtn = this.createActionButton('Delete', 'Delete Plugin', () => this.deletePlugin(name), 'btn-danger');

                actions.append(viewBtn, editBtn, deleteBtn);
                header.append(title, actions);

                // Description
                const description = document.createElement('div');
                description.className = 'plugin-description';
                description.textContent = plugin.description || 'No description available';

                // Stats
                const stats = document.createElement('div');
                stats.className = 'plugin-stats';

                const toolStat = document.createElement('div');
                toolStat.className = 'stat-item';
                toolStat.innerHTML = `<strong>${toolCount}</strong>Tools`;

                const voiceStat = document.createElement('div');
                voiceStat.className = 'stat-item';
                voiceStat.innerHTML = `<strong>${voiceCount}</strong>Voice Commands`;

                stats.append(toolStat, voiceStat);

                // Assemble card
                card.append(header, description, stats);
                return card;
            }

            createActionButton(text, title, onClick, extraClass = '') {
                const btn = document.createElement('button');
                btn.className = `btn-text ${extraClass}`;
                btn.title = title;
                btn.textContent = text;
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    onClick();
                });
                return btn;
            }

            selectPlugin(name, cardElement) {
                // Remove previous selections
                document.querySelectorAll('.plugin-card.selected').forEach(card => {
                    card.classList.remove('selected');
                });

                // Add selection
                cardElement.classList.add('selected');
                console.log('Selected plugin:', name);
            }

            viewPlugin(name) {
                const plugin = this.plugins[name];
                if (!plugin) return;

                const modalTitle = document.getElementById('modal-title');
                const modalBody = document.getElementById('modal-body');

                if (modalTitle) modalTitle.textContent = plugin.name || name;
                if (modalBody) modalBody.innerHTML = this.createPluginDetailsHTML(plugin);

                this.showModal();
            }

            createPluginDetailsHTML(plugin) {
                let html = `
                    <p><strong>Description:</strong> ${this.escapeHtml(plugin.description || 'No description')}</p>
                    <p><strong>Version:</strong> ${this.escapeHtml(plugin.version || 'Unknown')}</p>
                    <p><strong>Author:</strong> ${this.escapeHtml(plugin.author || 'Unknown')}</p>
                `;

                // Tools section
                if (plugin.tools && plugin.tools.length > 0) {
                    html += `<h4>Tools (${plugin.tools.length}):</h4><ul>`;
                    plugin.tools.forEach(tool => {
                        html += `<li><strong>${this.escapeHtml(tool.name)}</strong><br>`;
                        html += `<em>${this.escapeHtml(tool.description || 'No description')}</em></li>`;
                    });
                    html += '</ul>';
                }

                // Voice commands section
                html += '<h4>Voice Commands:</h4>';
                if (plugin.voice_phrases && plugin.voice_phrases.length > 0) {
                    html += '<ul>';
                    plugin.voice_phrases.forEach(phrase => {
                        html += `<li>"${this.escapeHtml(phrase)}"</li>`;
                    });
                    html += '</ul>';
                } else {
                    html += '<p>No voice commands configured.</p>';
                }

                return html;
            }

            editPlugin(name) {
                const plugin = this.plugins[name];
                if (!plugin) {
                    this.showNotification(`Plugin "${name}" not found`, 'error');
                    return;
                }

                // For now, show plugin details with edit suggestion
                const modalTitle = document.getElementById('modal-title');
                const modalBody = document.getElementById('modal-body');

                if (modalTitle) modalTitle.textContent = `Edit Plugin: ${plugin.name}`;
                if (modalBody) {
                    modalBody.innerHTML = `
                        <div class="edit-plugin-info">
                            <p><strong>Current Plugin:</strong> ${this.escapeHtml(plugin.name)}</p>
                            <p><strong>Description:</strong> ${this.escapeHtml(plugin.description || 'No description')}</p>
                            <p><strong>Tools:</strong> ${plugin.tools?.length || 0}</p>
                            <p><strong>Voice Commands:</strong> ${plugin.voice_phrases?.length || 0}</p>

                            <div class="edit-options">
                                <h4>Edit Options:</h4>
                                <p>To edit this plugin, you can:</p>
                                <ul>
                                    <li><strong>Delete and recreate:</strong> Use the delete button, then create a new plugin with your changes</li>
                                    <li><strong>Manual edit:</strong> Edit the plugin file directly in <code>jarvis/tools/plugins/</code></li>
                                    <li><strong>Voice commands:</strong> Add new voice phrases by recreating the plugin</li>
                                </ul>

                                <div class="edit-actions">
                                    <button class="btn btn-danger" onclick="toolsManager.deletePlugin('${name}'); toolsManager.hideModal();">
                                        Delete This Plugin
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                }

                this.showModal();
            }

            async deletePlugin(name) {
                if (!confirm(`Are you sure you want to delete the plugin "${name}"? This action cannot be undone.`)) {
                    return;
                }

                try {
                    const response = await fetch('/api/plugins', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            action: 'delete',
                            name: name
                        })
                    });

                    const result = await response.json();

                    if (result.success) {
                        this.showNotification(`Plugin "${name}" deleted successfully!`, 'success');
                        this.loadPlugins(); // Refresh the plugin list
                    } else {
                        this.showNotification(`Error deleting plugin: ${result.message}`, 'error');
                    }
                } catch (error) {
                    console.error('Error deleting plugin:', error);
                    this.showNotification(`Error deleting plugin: ${error.message}`, 'error');
                }
            }

            showAddPluginModal() {
                this.voiceCommands = [];
                this.renderVoiceCommands();
                const modal = document.getElementById('add-plugin-modal');
                if (modal) modal.style.display = 'flex';

                // Reset form
                const form = document.getElementById('add-plugin-form');
                if (form) form.reset();
            }

            hideAddPluginModal() {
                const modal = document.getElementById('add-plugin-modal');
                if (modal) modal.style.display = 'none';
                this.voiceCommands = [];
            }

            addVoiceCommand() {
                const input = document.getElementById('voice-command-input');
                if (!input) return;

                const command = input.value.trim();
                if (command && !this.voiceCommands.includes(command)) {
                    this.voiceCommands.push(command);
                    input.value = '';
                    this.renderVoiceCommands();
                }
            }

            removeVoiceCommand(index) {
                this.voiceCommands.splice(index, 1);
                this.renderVoiceCommands();
            }

            renderVoiceCommands() {
                const container = document.getElementById('voice-commands-list');
                if (!container) return;

                if (this.voiceCommands.length === 0) {
                    container.innerHTML = '<p class="no-commands">No voice commands added yet.</p>';
                    return;
                }

                const html = this.voiceCommands.map((command, index) =>
                    `<div class="voice-command-item">
                        <span class="command-text">"${this.escapeHtml(command)}"</span>
                        <button type="button" class="remove-command" onclick="toolsManager.removeVoiceCommand(${index})">Remove</button>
                    </div>`
                ).join('');

                container.innerHTML = html;
            }

            hideAddPluginModal() {
                const modal = document.getElementById('add-plugin-modal');
                if (modal) modal.style.display = 'none';
                this.voiceCommands = [];
            }

            addVoiceCommand() {
                const input = document.getElementById('voice-command-input');
                if (!input) return;

                const command = input.value.trim();
                if (command && !this.voiceCommands.includes(command)) {
                    this.voiceCommands.push(command);
                    input.value = '';
                    this.renderVoiceCommands();
                }
            }

            removeVoiceCommand(index) {
                this.voiceCommands.splice(index, 1);
                this.renderVoiceCommands();
            }

            renderVoiceCommands() {
                const container = document.getElementById('voice-commands-list');
                if (!container) return;

                if (this.voiceCommands.length === 0) {
                    container.innerHTML = '<p class="no-commands">No voice commands added yet.</p>';
                    return;
                }

                const html = this.voiceCommands.map((command, index) =>
                    `<div class="voice-command-item">
                        <span class="command-text">"${this.escapeHtml(command)}"</span>
                        <button type="button" class="remove-command" onclick="toolsManager.removeVoiceCommand(${index})">Remove</button>
                    </div>`
                ).join('');

                container.innerHTML = html;
            }

            async handleFormSubmit(e) {
                e.preventDefault();

                const form = e.target;
                const formData = new FormData(form);

                const pluginData = {
                    action: 'add',
                    name: formData.get('name'),
                    description: formData.get('description'),
                    version: formData.get('version') || '1.0.0',
                    author: formData.get('author') || 'Unknown',
                    code: formData.get('code'),
                    voice_phrases: this.voiceCommands
                };

                try {
                    const response = await fetch('/api/plugins', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(pluginData)
                    });

                    const result = await response.json();

                    if (result.success) {
                        this.showNotification('Plugin created successfully!', 'success');
                        this.hideAddPluginModal();
                        this.loadPlugins(); // Refresh the plugin list
                    } else {
                        this.showNotification(`Error creating plugin: ${result.message}`, 'error');
                    }
                } catch (error) {
                    console.error('Error creating plugin:', error);
                    this.showNotification(`Error creating plugin: ${error.message}`, 'error');
                }
            }

            showNotification(message, type = 'info') {
                // Create notification element
                const notification = document.createElement('div');
                notification.className = `notification notification-${type}`;
                notification.textContent = message;

                // Add to page
                document.body.appendChild(notification);

                // Show notification
                setTimeout(() => notification.classList.add('show'), 100);

                // Hide and remove notification
                setTimeout(() => {
                    notification.classList.remove('show');
                    setTimeout(() => {
                        if (notification.parentNode) {
                            document.body.removeChild(notification);
                        }
                    }, 300);
                }, 4000);
            }

            showModal() {
                const modal = document.getElementById('plugin-modal');
                if (modal) modal.style.display = 'flex';
            }

            hideModal() {
                const modal = document.getElementById('plugin-modal');
                if (modal) modal.style.display = 'none';
            }

            updateStatus() {
                const activeCount = document.getElementById('active-plugins-count');
                const toolsCount = document.getElementById('available-tools-count');
                const voiceCount = document.getElementById('voice-commands-count');

                const pluginCount = Object.keys(this.plugins).length;
                const totalTools = Object.values(this.plugins).reduce((sum, plugin) =>
                    sum + (plugin.tools?.length || 0), 0);
                const totalVoice = Object.values(this.plugins).reduce((sum, plugin) =>
                    sum + (plugin.voice_phrases?.length || 0), 0);

                if (activeCount) activeCount.textContent = pluginCount;
                if (toolsCount) toolsCount.textContent = totalTools;
                if (voiceCount) voiceCount.textContent = totalVoice;
            }

            async handleFormSubmit(e) {
                e.preventDefault();

                const form = e.target;
                const formData = new FormData(form);

                const pluginData = {
                    action: 'add',
                    name: formData.get('name'),
                    description: formData.get('description'),
                    version: formData.get('version') || '1.0.0',
                    author: formData.get('author') || 'Unknown',
                    code: formData.get('code'),
                    voice_phrases: this.voiceCommands
                };

                try {
                    const response = await fetch('/api/plugins', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(pluginData)
                    });

                    const result = await response.json();

                    if (result.success) {
                        this.showNotification('Plugin created successfully!', 'success');
                        this.hideAddPluginModal();
                        this.loadPlugins(); // Refresh the plugin list
                    } else {
                        this.showNotification(`Error creating plugin: ${result.message}`, 'error');
                    }
                } catch (error) {
                    console.error('Error creating plugin:', error);
                    this.showNotification(`Error creating plugin: ${error.message}`, 'error');
                }
            }

            showNotification(message, type = 'info') {
                // Create notification element
                const notification = document.createElement('div');
                notification.className = `notification notification-${type}`;
                notification.textContent = message;

                // Add to page
                document.body.appendChild(notification);

                // Show notification
                setTimeout(() => notification.classList.add('show'), 100);

                // Hide and remove notification
                setTimeout(() => {
                    notification.classList.remove('show');
                    setTimeout(() => {
                        if (notification.parentNode) {
                            document.body.removeChild(notification);
                        }
                    }, 300);
                }, 4000);
            }

            escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }
        }

        // Initialize when DOM is ready
        let toolsManager;
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                toolsManager = new ToolsManager();
            });
        } else {
            toolsManager = new ToolsManager();
        }
        </script>
        """

    def get_mcp_content(self) -> str:
        """Get the MCP management content."""
        return """
        <div class="page-header">
            <h1>MCP Servers</h1>
            <div class="breadcrumb">
                <a href="/settings">Settings</a> > MCP Servers
            </div>
        </div>

        <div class="info-banner">
            <h3>🔗 Model Context Protocol (MCP)</h3>
            <p>Connect Jarvis to external tools and services through MCP servers. Popular options include GitHub integration, file system access, web search, and database connections.</p>

            <!-- Status Overview -->
            <div class="mcp-status-overview" id="mcp-status-overview">
                <div class="status-item">
                    <span class="status-label">System Status:</span>
                    <span class="status-value" id="mcp-system-status">Loading...</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Connected Servers:</span>
                    <span class="status-value" id="connected-servers-count">0</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Available Tools:</span>
                    <span class="status-value" id="available-tools-count">0</span>
                </div>
            </div>

            <details>
                <summary>📚 Quick Setup Guide</summary>
                <div class="setup-guide">
                    <h4>🚀 Getting Started (3 Easy Steps):</h4>
                    <div class="setup-steps">
                        <div class="setup-step">
                            <div class="step-number">1</div>
                            <div class="step-content">
                                <h5>Choose a Template</h5>
                                <p>Click <strong>"Add Server"</strong> and select from popular templates like GitHub, File System, or Web Search</p>
                            </div>
                        </div>
                        <div class="setup-step">
                            <div class="step-number">2</div>
                            <div class="step-content">
                                <h5>Configure & Test</h5>
                                <p>Fill in required fields (API keys, etc.) and use <strong>"Test Connection"</strong> to verify setup</p>
                            </div>
                        </div>
                        <div class="setup-step">
                            <div class="step-number">3</div>
                            <div class="step-content">
                                <h5>Start Using</h5>
                                <p>Save the server and start using new tools through voice commands or the interface</p>
                            </div>
                        </div>
                    </div>

                    <div class="popular-templates">
                        <h5>🌟 Popular First Choices:</h5>
                        <div class="template-grid">
                            <div class="template-card" onclick="quickAddTemplate('universal')">
                                <div class="template-icon">🌐</div>
                                <div class="template-name">Universal MCP</div>
                                <div class="template-desc">Works with any MCP server</div>
                            </div>
                            <div class="template-card" onclick="quickAddTemplate('filesystem')">
                                <div class="template-icon">📁</div>
                                <div class="template-name">File System</div>
                                <div class="template-desc">Access local files</div>
                            </div>
                            <div class="template-card" onclick="quickAddTemplate('github')">
                                <div class="template-icon">🐙</div>
                                <div class="template-name">GitHub</div>
                                <div class="template-desc">Repository management</div>
                            </div>
                        </div>
                    </div>

                    <div class="help-links">
                        <p><strong>Need help?</strong>
                        <a href="#" onclick="showTroubleshootingModal()">Troubleshooting Guide</a> |
                        <a href="https://mcpservers.org" target="_blank">Browse More MCPs</a> |
                        <a href="#" onclick="showVoiceCommandsModal()">Voice Commands</a>
                        </p>
                    </div>
                </div>
            </details>
        </div>

        <div class="config-section">
            <h2>MCP Configuration</h2>
            <form id="mcp-config-form" class="config-form">
                <div class="form-group">
                    <div class="checkbox-label">
                        <input type="checkbox" id="mcp_enabled" name="mcp_enabled">
                        <label for="mcp_enabled">Enable MCP System</label>
                    </div>
                    <small>Enable or disable the Model Context Protocol system globally</small>
                </div>

                <div class="form-actions">
                    <button type="submit" class="btn btn-primary">Save MCP Settings</button>
                </div>
            </form>
        </div>

        <div class="config-section">
            <div class="section-header">
                <h2>MCP Servers</h2>
                <button class="btn btn-primary" onclick="showAddServerModal()" id="add-server-btn">
                    <i class="icon">+</i> Add Server
                </button>
            </div>

            <div id="servers-list" class="servers-grid">
                <p>Loading MCP servers...</p>
            </div>
        </div>

        <div class="config-section">
            <div class="section-header">
                <h2>Available MCP Tools</h2>
                <button class="btn btn-secondary" onclick="refreshTools()">
                    Refresh Tools
                </button>
            </div>

            <div id="tools-list" class="tools-grid">
                <p>Loading MCP tools...</p>
            </div>
        </div>

        <!-- Add Server Modal -->
        <div id="add-server-modal" class="modal">
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

        <!-- MCP Server Details Modal -->
        <div id="plugin-modal" class="modal" style="display: none;">
            <div class="modal-content">
                <div class="modal-header">
                    <h3 id="modal-title">MCP Server Details</h3>
                    <button class="modal-close" onclick="hideMCPModal()">&times;</button>
                </div>
                <div class="modal-body" id="modal-body">
                    <!-- Server details will be populated here -->
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="hideMCPModal()">Close</button>
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

        /* MCP Status Overview */
        .mcp-status-overview {
            display: flex;
            gap: 2rem;
            margin: 1rem 0;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
            flex-wrap: wrap;
        }

        .status-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            min-width: 120px;
        }

        .status-label {
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 0.25rem;
        }

        .status-value {
            font-size: 1.1rem;
            font-weight: bold;
            color: #2196F3;
        }

        /* Setup Steps */
        .setup-steps {
            display: flex;
            gap: 1rem;
            margin: 1rem 0;
            flex-wrap: wrap;
        }

        .setup-step {
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
            flex: 1;
            min-width: 200px;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
        }

        .step-number {
            background: #2196F3;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9rem;
            flex-shrink: 0;
        }

        .step-content h5 {
            margin: 0 0 0.5rem 0;
            color: #2196F3;
            font-size: 0.95rem;
        }

        .step-content p {
            margin: 0;
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.8);
            line-height: 1.4;
        }

        /* Popular Templates */
        .popular-templates {
            margin: 1.5rem 0;
        }

        .popular-templates h5 {
            margin: 0 0 1rem 0;
            color: #2196F3;
        }

        .template-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
        }

        .template-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 6px;
            padding: 1rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .template-card:hover {
            background: rgba(33, 150, 243, 0.1);
            border-color: rgba(33, 150, 243, 0.3);
            transform: translateY(-2px);
        }

        .template-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }

        .template-name {
            font-weight: bold;
            color: #2196F3;
            margin-bottom: 0.25rem;
        }

        .template-desc {
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.7);
        }

        /* Help Links */
        .help-links {
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .help-links a {
            color: #2196F3;
            text-decoration: none;
        }

        .help-links a:hover {
            text-decoration: underline;
        }

        /* Status Indicators */
        .status-success {
            color: #4CAF50 !important;
        }

        .status-warning {
            color: #FF9800 !important;
        }

        .status-error {
            color: #F44336 !important;
        }

        /* Troubleshooting Modal */
        .troubleshooting-section {
            margin-bottom: 1.5rem;
        }

        .issue-item {
            margin-bottom: 1rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
        }

        .issue-item strong {
            color: #2196F3;
            display: block;
            margin-bottom: 0.5rem;
        }

        .issue-item ul {
            margin: 0;
            padding-left: 1.5rem;
        }

        .issue-item li {
            margin-bottom: 0.25rem;
            color: rgba(255, 255, 255, 0.8);
        }

        .issue-item code {
            background: rgba(255, 255, 255, 0.1);
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #2196F3;
        }

        .troubleshooting-actions {
            display: flex;
            gap: 1rem;
            justify-content: center;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Voice Commands Modal */
        .voice-commands-section h4 {
            color: #2196F3;
            margin: 1rem 0 0.5rem 0;
        }

        .voice-commands-section h4:first-child {
            margin-top: 0;
        }

        .command-list {
            list-style: none;
            padding: 0;
            margin: 0 0 1rem 0;
        }

        .command-list li {
            padding: 0.5rem;
            margin-bottom: 0.25rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            color: rgba(255, 255, 255, 0.8);
        }

        .command-list strong {
            color: #2196F3;
        }

        /* Enhanced Server Cards */
        .server-card {
            position: relative;
            transition: all 0.2s ease;
        }

        .server-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .server-status-indicator {
            position: absolute;
            top: 10px;
            right: 10px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #F44336;
        }

        .server-status-indicator.connected {
            background: #4CAF50;
        }

        .server-status-indicator.connecting {
            background: #FF9800;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        /* Tools & Plugins Page Styles */
        .tools-status-overview {
            display: flex;
            gap: 2rem;
            margin: 1rem 0;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 6px;
            flex-wrap: wrap;
        }

        .plugins-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }

        .plugin-card {
            background: linear-gradient(145deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.06));
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 16px;
            padding: 0;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
            backdrop-filter: blur(12px);
        }

        .plugin-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #6495ed, #4169e1, #1e90ff);
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .plugin-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.2);
            border-color: rgba(100, 149, 237, 0.4);
        }

        .plugin-card:hover::before {
            opacity: 1;
        }

        .plugin-card.selected {
            border-color: #6495ed;
            box-shadow: 0 12px 40px rgba(100, 149, 237, 0.25);
            background: linear-gradient(145deg, rgba(100, 149, 237, 0.15), rgba(100, 149, 237, 0.08));
        }

        .plugin-card.selected::before {
            opacity: 1;
        }

        .plugin-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding: 2rem 2rem 0 2rem;
            margin-bottom: 1.5rem;
        }

        .plugin-title {
            margin: 0;
            color: #ffffff;
            font-size: 1.4rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            line-height: 1.2;
        }

        .plugin-actions {
            display: flex;
            gap: 0.75rem;
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            transform: translateX(12px);
        }

        .plugin-card:hover .plugin-actions {
            opacity: 1;
            transform: translateX(0);
        }

        .btn-text {
            background: rgba(255, 255, 255, 0.12);
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            cursor: pointer;
            color: #ffffff;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            white-space: nowrap;
            display: flex;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(8px);
        }

        .btn-text:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .btn-text.btn-danger:hover {
            background: rgba(244, 67, 54, 0.25);
            color: #ff6b6b;
        }

        .plugin-description {
            color: #c8d3e0;
            margin-bottom: 1.5rem;
            line-height: 1.5;
            font-size: 0.95rem;
            padding: 0 2rem;
            opacity: 0.9;
        }

        .plugin-stats {
            display: flex;
            gap: 1.5rem;
            margin: 0;
            padding: 1.5rem 2rem 2rem 2rem;
            background: rgba(255, 255, 255, 0.03);
            border-top: 1px solid rgba(255, 255, 255, 0.08);
        }

        .stat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            flex: 1;
        }

        .stat-item strong {
            display: block;
            color: #6495ed;
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .stat-item {
            color: #b8c5d1;
            font-size: 0.85rem;
            font-weight: 500;
        }

        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
        }

        .modal-content {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            width: 90%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }

        .modal-header {
            padding: 1.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .modal-header h3 {
            margin: 0;
            color: #ffffff;
        }

        .modal-close {
            background: none;
            border: none;
            color: #b8c5d1;
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-close:hover {
            color: #ffffff;
        }

        .modal-body {
            padding: 1.5rem;
            color: #e0e6ed;
        }

        .modal-body h4 {
            color: #6495ed;
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
        }

        .modal-body ul {
            margin: 0.5rem 0;
            padding-left: 1.5rem;
        }

        .modal-body li {
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }

        .modal-footer {
            padding: 1rem 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: flex-end;
            gap: 0.5rem;
        }

        /* Form Styles */
        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            color: #ffffff;
            font-weight: 500;
        }

        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.05);
            color: #ffffff;
            font-size: 0.9rem;
            transition: border-color 0.2s ease;
        }

        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #6495ed;
            box-shadow: 0 0 0 2px rgba(100, 149, 237, 0.2);
        }

        .form-group small {
            display: block;
            margin-top: 0.25rem;
            color: #b8c5d1;
            font-size: 0.8rem;
        }

        .voice-commands-section {
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.02);
        }

        .voice-input-group {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }

        .voice-input-group input {
            flex: 1;
            margin-bottom: 0;
        }

        .voice-commands-list {
            min-height: 60px;
            max-height: 150px;
            overflow-y: auto;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.02);
        }

        .voice-command-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem;
            margin-bottom: 0.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
        }

        .voice-command-item:last-child {
            margin-bottom: 0;
        }

        .command-text {
            color: #ffffff;
            font-style: italic;
        }

        .remove-command {
            background: rgba(244, 67, 54, 0.2);
            border: none;
            border-radius: 3px;
            padding: 0.25rem 0.5rem;
            color: #ff6b6b;
            font-size: 0.8rem;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }

        .remove-command:hover {
            background: rgba(244, 67, 54, 0.3);
        }

        .no-commands {
            color: #b8c5d1;
            font-style: italic;
            text-align: center;
            margin: 1rem 0;
        }

        .form-help {
            background: rgba(100, 149, 237, 0.1);
            border: 1px solid rgba(100, 149, 237, 0.3);
            border-radius: 4px;
            padding: 1rem;
        }

        .form-help h4 {
            margin: 0 0 0.5rem 0;
            color: #6495ed;
        }

        .form-help ul {
            margin: 0;
            padding-left: 1.5rem;
        }

        .form-help li {
            color: #e0e6ed;
            margin-bottom: 0.25rem;
        }

        /* Notification Styles */
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }

        .notification.show {
            transform: translateX(0);
        }

        .notification-success {
            background: linear-gradient(135deg, #4CAF50, #45a049);
        }

        .notification-error {
            background: linear-gradient(135deg, #f44336, #da190b);
        }

        .notification-info {
            background: linear-gradient(135deg, #2196F3, #1976D2);
        }

        /* Edit Plugin Styles */
        .edit-plugin-info {
            color: #e0e6ed;
        }

        .edit-options {
            margin-top: 1.5rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 4px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .edit-options h4 {
            color: #6495ed;
            margin: 0 0 1rem 0;
        }

        .edit-options ul {
            margin: 1rem 0;
            padding-left: 1.5rem;
        }

        .edit-options li {
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }

        .edit-options code {
            background: rgba(255, 255, 255, 0.1);
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #6495ed;
        }

        .edit-actions {
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }

        .plugin-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1.5rem;
            transition: all 0.2s ease;
        }

        .plugin-card:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(33, 150, 243, 0.3);
            transform: translateY(-2px);
        }

        .plugin-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 1rem;
        }

        .plugin-title {
            font-size: 1.2rem;
            font-weight: bold;
            color: #2196F3;
            margin: 0;
        }

        .plugin-actions {
            display: flex;
            gap: 0.5rem;
        }

        .plugin-actions button {
            padding: 0.25rem 0.5rem;
            font-size: 0.8rem;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .plugin-actions .edit-btn {
            background: rgba(33, 150, 243, 0.2);
            color: #2196F3;
        }

        .plugin-actions .delete-btn {
            background: rgba(244, 67, 54, 0.2);
            color: #F44336;
        }

        .plugin-actions button:hover {
            opacity: 0.8;
        }

        .plugin-description {
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 1rem;
            line-height: 1.4;
        }

        .plugin-tools {
            margin-bottom: 1rem;
        }

        .plugin-tools h5 {
            color: #2196F3;
            margin: 0 0 0.5rem 0;
            font-size: 0.9rem;
        }

        .tool-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }

        .tool-list li {
            background: rgba(255, 255, 255, 0.05);
            padding: 0.5rem;
            margin-bottom: 0.25rem;
            border-radius: 4px;
            font-size: 0.85rem;
        }

        .plugin-voice-phrases {
            margin-bottom: 1rem;
        }

        .plugin-voice-phrases h5 {
            color: #2196F3;
            margin: 0 0 0.5rem 0;
            font-size: 0.9rem;
        }

        .voice-phrase-tag {
            display: inline-block;
            background: rgba(33, 150, 243, 0.2);
            color: #2196F3;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.75rem;
            margin: 0.25rem 0.25rem 0.25rem 0;
        }

        /* Plugin Form Styles */
        .large-modal .modal-content {
            max-width: 800px;
            width: 90vw;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }

        .voice-phrases-container {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .voice-phrases-container input {
            flex: 1;
        }

        .voice-phrases-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
        }

        .voice-phrase-item {
            display: flex;
            align-items: center;
            background: rgba(33, 150, 243, 0.2);
            color: #2196F3;
            padding: 0.25rem 0.5rem;
            border-radius: 12px;
            font-size: 0.8rem;
        }

        .voice-phrase-item .remove-phrase {
            background: none;
            border: none;
            color: #F44336;
            cursor: pointer;
            margin-left: 0.5rem;
            padding: 0;
            font-size: 1rem;
        }

        .voice-phrase-item .remove-phrase:hover {
            opacity: 0.7;
        }

        #plugin-code, #edit-plugin-code {
            font-family: 'Courier New', monospace;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: #fff;
            padding: 1rem;
            border-radius: 4px;
            resize: vertical;
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
            display: none;
            align-items: center;
            justify-content: center;
        }

        .modal.show {
            display: flex;
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
        let mcpTools = {};
        let jarvisTools = {};
        let allTools = {};
        let currentToolFilter = 'all';

        // Debug: Test if functions are accessible
        console.log('MCP JavaScript starting to load...');

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

        function loadMCPTools() {
            fetch('/api/mcp/tools')
                .then(response => response.json())
                .then(data => {
                    mcpTools = data.tools || {};
                    updateAllTools();
                    renderTools();
                })
                .catch(error => {
                    console.error('Error loading MCP tools:', error);
                });
        }

        function loadJarvisTools() {
            fetch('/api/jarvis/tools')
                .then(response => response.json())
                .then(data => {
                    jarvisTools = data.tools || {};
                    updateAllTools();
                    renderTools();
                })
                .catch(error => {
                    console.error('Error loading Jarvis tools:', error);
                });
        }

        function loadTools() {
            loadMCPTools();
            loadJarvisTools();
        }

        function updateAllTools() {
            allTools = { ...jarvisTools, ...mcpTools };
        }

        function renderServers() {
            const serversList = document.getElementById('servers-list');

            if (Object.keys(servers).length === 0) {
                serversList.innerHTML = '<p>No MCP servers configured. Click "Add Server" to get started.</p>';
                return;
            }

            // Clear the container
            serversList.innerHTML = '';
            serversList.className = 'mcp-servers-grid';

            // Create server cards using DOM methods
            Object.entries(servers).forEach(([serverId, server]) => {
                const isConnected = server.status && server.status.connected;
                const toolsCount = server.status ? server.status.tools_count : 0;

                // Main card
                const card = document.createElement('div');
                card.className = `mcp-server-card ${isConnected ? 'connected' : 'disconnected'}`;
                card.addEventListener('click', () => selectMCPServer(serverId, card));

                // Header
                const header = document.createElement('div');
                header.className = 'mcp-server-header';

                const title = document.createElement('h3');
                title.className = 'mcp-server-title';
                title.textContent = server.config.name || serverId;

                const actions = document.createElement('div');
                actions.className = 'mcp-server-actions';

                // Action buttons
                const viewBtn = createMCPActionButton('View', 'View Details', () => viewMCPServer(serverId));
                const connectBtn = createMCPActionButton(
                    isConnected ? 'Disconnect' : 'Connect',
                    isConnected ? 'Disconnect Server' : 'Connect Server',
                    () => isConnected ? disconnectMCPServer(serverId) : connectMCPServer(serverId),
                    isConnected ? 'btn-danger' : 'btn-success'
                );
                const deleteBtn = createMCPActionButton('Delete', 'Delete Server', () => deleteMCPServer(serverId), 'btn-danger');

                actions.append(viewBtn, connectBtn, deleteBtn);
                header.append(title, actions);

                // Description
                const description = document.createElement('div');
                description.className = 'mcp-server-description';
                description.textContent = server.config.description || `${server.config.transport.toUpperCase()} MCP server`;

                // Stats
                const stats = document.createElement('div');
                stats.className = 'mcp-server-stats';

                const statusStat = document.createElement('div');
                statusStat.className = `mcp-server-status ${isConnected ? 'connected' : 'disconnected'}`;
                statusStat.innerHTML = `<strong>${isConnected ? 'Connected' : 'Disconnected'}</strong>Status`;

                const toolsStat = document.createElement('div');
                toolsStat.className = 'mcp-server-status';
                toolsStat.innerHTML = `<strong>${toolsCount}</strong>Tools`;

                const transportStat = document.createElement('div');
                transportStat.className = 'mcp-server-status';
                transportStat.innerHTML = `<strong>${server.config.transport.toUpperCase()}</strong>Transport`;

                stats.append(statusStat, toolsStat, transportStat);

                // Assemble card
                card.append(header, description, stats);

                // Add to container
                serversList.appendChild(card);
            });
        }

        function createMCPActionButton(text, title, onClick, extraClass = '') {
            const btn = document.createElement('button');
            btn.className = `btn-text ${extraClass}`;
            btn.title = title;
            btn.textContent = text;
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                onClick();
            });
            return btn;
        }

        function selectMCPServer(serverId, cardElement) {
            // Remove previous selections
            document.querySelectorAll('.mcp-server-card.selected').forEach(card => {
                card.classList.remove('selected');
            });

            // Add selection
            cardElement.classList.add('selected');
            console.log('Selected MCP server:', serverId);
        }

        function viewMCPServer(serverId) {
            const server = servers[serverId];
            if (!server) return;

            // Create modal content
            const modalTitle = document.getElementById('modal-title');
            const modalBody = document.getElementById('modal-body');

            if (modalTitle) modalTitle.textContent = `MCP Server: ${server.config.name}`;
            if (modalBody) {
                modalBody.innerHTML = createMCPServerDetailsHTML(server);
            }

            showMCPModal();
        }

        function createMCPServerDetailsHTML(server) {
            const config = server.config;
            const status = server.status;

            let html = `
                <div class="mcp-server-details">
                    <p><strong>Name:</strong> ${escapeHtml(config.name)}</p>
                    <p><strong>Description:</strong> ${escapeHtml(config.description || 'No description')}</p>
                    <p><strong>Transport:</strong> ${escapeHtml(config.transport.toUpperCase())}</p>
                    <p><strong>Command:</strong> ${escapeHtml(config.command)}</p>
                    <p><strong>Arguments:</strong> ${escapeHtml(config.args.join(' '))}</p>
                    <p><strong>Enabled:</strong> ${config.enabled ? 'Yes' : 'No'}</p>
                    <p><strong>Timeout:</strong> ${config.timeout} seconds</p>
                    <p><strong>Status:</strong> <span class="${status.connected ? 'status-connected' : 'status-disconnected'}">${status.connected ? 'Connected' : 'Disconnected'}</span></p>
                    <p><strong>Available Tools:</strong> ${status.tools_count}</p>
            `;

            // Environment variables
            if (config.env && Object.keys(config.env).length > 0) {
                html += '<h4>Environment Variables:</h4><ul>';
                Object.entries(config.env).forEach(([key, value]) => {
                    html += `<li><strong>${escapeHtml(key)}:</strong> ${escapeHtml(value)}</li>`;
                });
                html += '</ul>';
            }

            // Timestamps
            html += `
                    <div class="mcp-timestamps">
                        <p><strong>Created:</strong> ${new Date(config.created_at).toLocaleString()}</p>
                        <p><strong>Last Modified:</strong> ${new Date(config.last_modified).toLocaleString()}</p>
                    </div>
                </div>
            `;

            return html;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        async function connectMCPServer(serverId) {
            try {
                const response = await fetch('/api/mcp/connect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        server: serverId
                    })
                });

                const result = await response.json();

                if (result.success) {
                    showMCPNotification(`MCP server "${serverId}" connected successfully!`, 'success');
                    loadServers(); // Refresh the server list
                } else {
                    showMCPNotification(`Error connecting to MCP server: ${result.message}`, 'error');
                }
            } catch (error) {
                console.error('Error connecting to MCP server:', error);
                showMCPNotification(`Error connecting to MCP server: ${error.message}`, 'error');
            }
        }

        async function disconnectMCPServer(serverId) {
            try {
                const response = await fetch('/api/mcp/disconnect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        server: serverId
                    })
                });

                const result = await response.json();

                if (result.success) {
                    showMCPNotification(`MCP server "${serverId}" disconnected successfully!`, 'success');
                    loadServers(); // Refresh the server list
                } else {
                    showMCPNotification(`Error disconnecting MCP server: ${result.message}`, 'error');
                }
            } catch (error) {
                console.error('Error disconnecting MCP server:', error);
                showMCPNotification(`Error disconnecting MCP server: ${error.message}`, 'error');
            }
        }

        async function testMCPConnection() {
            const form = document.getElementById('add-server-form');
            if (!form) return;

            const formData = new FormData(form);
            const serverData = {
                action: 'test',
                name: formData.get('name') || 'test-connection',
                transport: formData.get('transport'),
                command: formData.get('command'),
                args: formData.get('args'),
                env: formData.get('env'),
                timeout: formData.get('timeout')
            };

            try {
                const response = await fetch('/api/mcp/servers', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(serverData)
                });

                const result = await response.json();

                if (result.success) {
                    showMCPNotification('Connection test successful!', 'success');
                } else {
                    showMCPNotification(`Connection test failed: ${result.error}`, 'error');
                }
            } catch (error) {
                console.error('Error testing connection:', error);
                showMCPNotification(`Connection test failed: ${error.message}`, 'error');
            }
        }

        function showMCPModal() {
            const modal = document.getElementById('plugin-modal'); // Reuse the plugin modal
            if (modal) modal.style.display = 'flex';
        }

        function hideMCPModal() {
            const modal = document.getElementById('plugin-modal');
            if (modal) modal.style.display = 'none';
        }

        async function refreshTools() {
            showMCPNotification('Refreshing MCP tools...', 'info');

            try {
                // Reload both MCP and Jarvis tools
                await loadTools();
                await loadJarvisTools();

                showMCPNotification('Tools refreshed successfully!', 'success');
            } catch (error) {
                console.error('Error refreshing tools:', error);
                showMCPNotification(`Error refreshing tools: ${error.message}`, 'error');
            }
        }

        // Alias for the form button
        function testConnection() {
            testMCPConnection();
        }

        async function deleteMCPServer(serverId) {
            if (!confirm(`Are you sure you want to delete the MCP server "${serverId}"? This action cannot be undone.`)) {
                return;
            }

            try {
                const response = await fetch('/api/mcp/servers', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        action: 'remove',
                        name: serverId
                    })
                });

                const result = await response.json();

                if (result.success) {
                    showMCPNotification(`MCP server "${serverId}" deleted successfully!`, 'success');
                    loadServers(); // Refresh the server list
                } else {
                    showMCPNotification(`Error deleting MCP server: ${result.message}`, 'error');
                }
            } catch (error) {
                console.error('Error deleting MCP server:', error);
                showMCPNotification(`Error deleting MCP server: ${error.message}`, 'error');
            }
        }

        function showMCPNotification(message, type = 'info') {
            // Create notification element
            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.textContent = message;

            // Add to page
            document.body.appendChild(notification);

            // Show notification
            setTimeout(() => notification.classList.add('show'), 100);

            // Hide and remove notification
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    if (notification.parentNode) {
                        document.body.removeChild(notification);
                    }
                }, 300);
            }, 4000);
        }

        function renderTools() {
            const toolsList = document.getElementById('tools-list');

            if (Object.keys(mcpTools).length === 0) {
                toolsList.innerHTML = '<p>No tools available. Connect to MCP servers to discover tools.</p>';
                return;
            }

            const html = Object.entries(mcpTools).map(([name, tool]) =>
                '<div class="tool-card">' +
                    '<div class="tool-header">' +
                        '<div>' +
                            '<div class="tool-name">' + tool.name + '</div>' +
                            '<div class="tool-server">[' + tool.server_name + ']</div>' +
                        '</div>' +
                        '<label class="toggle-switch">' +
                            '<input type="checkbox" ' + (tool.enabled ? 'checked' : '') +
                                   ' onchange="toggleTool(\\'' + name + '\\', this.checked)">' +
                            '<span class="toggle-slider"></span>' +
                        '</label>' +
                    '</div>' +
                    '<div class="tool-description">' + (tool.description || 'No description available') + '</div>' +
                '</div>'
            ).join('');

            toolsList.innerHTML = html;
        }

        function showAddServerModal() {
            console.log('showAddServerModal called');
            const modal = document.getElementById('add-server-modal');
            if (modal) {
                modal.classList.add('show');
                console.log('Modal should now be visible');
            } else {
                console.error('Modal element not found!');
                alert('Error: Modal element not found. Please refresh the page.');
            }
        }

        // Make function globally accessible
        window.showAddServerModal = showAddServerModal;

        function hideAddServerModal() {
            console.log('hideAddServerModal called');
            const modal = document.getElementById('add-server-modal');
            if (modal) {
                modal.classList.remove('show');
            }

            const form = document.getElementById('add-server-form');
            if (form) {
                form.reset();
            }
        }

        // Make function globally accessible
        window.hideAddServerModal = hideAddServerModal;

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
                envText.split('\\n').forEach(line => {
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
                headersText.split('\\n').forEach(line => {
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
            if (!confirm('Are you sure you want to remove server "' + serverName + '"?')) {
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
            notification.className = 'notification notification-' + type;
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
        console.log('MCP page JavaScript loaded');
        loadServers();
        loadTools();

        // Initialize page when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM loaded for MCP page');

            // Check if elements exist
            const addButton = document.getElementById('add-server-btn');
            const modal = document.getElementById('add-server-modal');
            const form = document.getElementById('add-server-form');

            console.log('Add button found:', !!addButton);
            console.log('Modal found:', !!modal);
            console.log('Form found:', !!form);

            if (!addButton) console.error('Add Server button not found!');
            if (!modal) console.error('Modal not found!');
            if (!form) console.error('Form not found!');

            // Add fallback event listener for the Add Server button
            if (addButton) {
                console.log('Adding click event listener to Add Server button');
                addButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log('Add Server button clicked via event listener');
                    showAddServerModal();
                });
            }
        });

        // MCP Configuration Management
        function loadMCPConfig() {
            fetch('/api/config')
                .then(response => response.json())
                .then(data => {
                    if (data.mcp) {
                        document.getElementById('mcp_enabled').checked = data.mcp.enabled || false;
                    }
                })
                .catch(error => console.error('Error loading MCP config:', error));
        }

        document.getElementById('mcp-config-form').addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);
            const mcpConfig = {
                enabled: formData.has('mcp_enabled')
            };

            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({mcp: mcpConfig})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('MCP configuration saved successfully!', 'success');
                    // Reload servers and tools to reflect changes
                    setTimeout(() => {
                        loadServers();
                        loadTools();
                    }, 1000);
                } else {
                    showNotification('Error saving MCP configuration: ' + (data.error || 'Unknown error'), 'error');
                }
            })
            .catch(error => showNotification('Error saving MCP configuration: ' + error.message, 'error'));
        });

        // Load MCP configuration on page load
        loadMCPConfig();

        // Enhanced Status Updates
        function updateMCPStatus() {
            const systemStatus = document.getElementById('mcp-system-status');
            const serversCount = document.getElementById('connected-servers-count');
            const toolsCount = document.getElementById('available-tools-count');

            if (systemStatus) {
                const connectedServers = Object.values(servers).filter(s => s.status && s.status.connected).length;
                const totalServers = Object.keys(servers).length;

                if (totalServers === 0) {
                    systemStatus.textContent = 'No servers configured';
                    systemStatus.className = 'status-value status-warning';
                } else if (connectedServers === 0) {
                    systemStatus.textContent = 'Ready';
                    systemStatus.className = 'status-value status-success';
                } else if (connectedServers === totalServers) {
                    systemStatus.textContent = 'All Connected';
                    systemStatus.className = 'status-value status-success';
                } else {
                    systemStatus.textContent = 'Partially Connected';
                    systemStatus.className = 'status-value status-warning';
                }
            }

            if (serversCount) {
                const connected = Object.values(servers).filter(s => s.status && s.status.connected).length;
                const total = Object.keys(servers).length;
                serversCount.textContent = `${connected}/${total}`;
            }

            if (toolsCount) {
                toolsCount.textContent = Object.keys(mcpTools).length;
            }
        }

        // Quick Template Addition
        function quickAddTemplate(templateName) {
            showAddServerModal();
            const templateSelect = document.getElementById('server-template');
            if (templateSelect) {
                templateSelect.value = templateName;
                loadTemplate();
            }
        }

        // Enhanced Modal Functions
        function showTroubleshootingModal() {
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>🔧 MCP Troubleshooting</h3>
                        <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="troubleshooting-section">
                            <h4>Common Issues:</h4>
                            <div class="issue-item">
                                <strong>Server won't connect:</strong>
                                <ul>
                                    <li>Check if Node.js is installed: <code>node --version</code></li>
                                    <li>Verify MCP server package is installed</li>
                                    <li>Test the command manually in terminal</li>
                                    <li>Check API keys and environment variables</li>
                                </ul>
                            </div>
                            <div class="issue-item">
                                <strong>No tools appearing:</strong>
                                <ul>
                                    <li>Ensure server is connected (green status)</li>
                                    <li>Refresh the tools list</li>
                                    <li>Check server logs for errors</li>
                                </ul>
                            </div>
                            <div class="issue-item">
                                <strong>Voice commands not working:</strong>
                                <ul>
                                    <li>Make sure Jarvis main application is running</li>
                                    <li>Try: "Jarvis, list MCP servers"</li>
                                    <li>Check if tools are enabled</li>
                                </ul>
                            </div>
                        </div>
                        <div class="troubleshooting-actions">
                            <button class="btn btn-primary" onclick="runDiagnostics()">Run Diagnostics</button>
                            <button class="btn btn-secondary" onclick="refreshAllConnections()">Refresh All</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        function showVoiceCommandsModal() {
            const modal = document.createElement('div');
            modal.className = 'modal';
            modal.innerHTML = `
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>🎤 MCP Voice Commands</h3>
                        <button class="modal-close" onclick="this.closest('.modal').remove()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="voice-commands-section">
                            <h4>Server Management:</h4>
                            <ul class="command-list">
                                <li><strong>"List MCP servers"</strong> - Show all configured servers</li>
                                <li><strong>"Add filesystem MCP server"</strong> - Add file system access</li>
                                <li><strong>"Add GitHub MCP server"</strong> - Add GitHub integration</li>
                                <li><strong>"Enable [server name] MCP"</strong> - Enable a server</li>
                                <li><strong>"Disable [server name] MCP"</strong> - Disable a server</li>
                                <li><strong>"Remove [server name] MCP"</strong> - Delete a server</li>
                            </ul>
                            <h4>Configuration:</h4>
                            <ul class="command-list">
                                <li><strong>"Edit [server] MCP command"</strong> - Change server command</li>
                                <li><strong>"Update [server] MCP timeout 30"</strong> - Set timeout</li>
                                <li><strong>"Change [server] MCP environment variable API_KEY=abc123"</strong> - Set env var</li>
                            </ul>
                            <h4>Quick Access:</h4>
                            <ul class="command-list">
                                <li><strong>"Open MCP settings"</strong> - Open this interface</li>
                                <li><strong>"Show MCP status"</strong> - Display server status</li>
                            </ul>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }

        // Diagnostic Functions
        function runDiagnostics() {
            showNotification('Running MCP diagnostics...', 'info');

            // Check system requirements
            const diagnostics = {
                nodeJs: false,
                mcpServers: 0,
                connectedServers: 0,
                availableTools: 0
            };

            // Update diagnostics display
            setTimeout(() => {
                const connectedCount = Object.values(servers).filter(s => s.status === 'connected').length;
                const toolCount = Object.keys(mcpTools).length;

                let message = `Diagnostics Complete:\\n`;
                message += `• Connected Servers: ${connectedCount}/${Object.keys(servers).length}\\n`;
                message += `• Available Tools: ${toolCount}\\n`;

                if (connectedCount === 0 && Object.keys(servers).length > 0) {
                    message += `\\n⚠️ No servers connected. Check server configurations.`;
                } else if (toolCount === 0 && connectedCount > 0) {
                    message += `\\n⚠️ No tools available. Servers may not be providing tools.`;
                } else if (connectedCount > 0 && toolCount > 0) {
                    message += `\\n✅ MCP system is working correctly!`;
                }

                alert(message);
            }, 1000);
        }

        function refreshAllConnections() {
            showNotification('Refreshing all MCP connections...', 'info');

            // Refresh servers and tools
            loadServers();
            loadTools();

            // Force reconnection for all servers
            Object.keys(servers).forEach(serverName => {
                if (servers[serverName].status !== 'connected') {
                    connectServer(serverName);
                }
            });

            setTimeout(() => {
                updateMCPStatus();
                showNotification('MCP connections refreshed', 'success');
            }, 2000);
        }

        // Override existing functions to include status updates
        const originalLoadServers = loadServers;
        loadServers = function() {
            originalLoadServers();
            setTimeout(updateMCPStatus, 500);
        };

        const originalLoadTools = loadTools;
        loadTools = function() {
            originalLoadTools();
            setTimeout(updateMCPStatus, 500);
        };

        // Auto-refresh every 30 seconds
        setInterval(() => {
            loadServers();
            loadTools();
        }, 30000);
        </script>
        """





    def get_rag_content(self) -> str:
        """Get the RAG management content."""
        return """
        <div class="page-header">
            <h1>RAG Memory Management</h1>
            <div class="breadcrumb">
                <a href="/settings">Settings</a> > RAG Memory
            </div>
        </div>

        <div class="info-banner">
            <h3>Intelligent RAG System</h3>
            <p>RAG (Retrieval-Augmented Generation) system for long-term memory and document management.</p>
            <p><strong>Note:</strong> Full RAG interface coming soon. For now, use voice commands to interact with the RAG system.</p>
        </div>

        <div class="config-section">
            <h3>Voice Commands</h3>
            <ul>
                <li><strong>"Remember that..."</strong> - Add information to long-term memory</li>
                <li><strong>"Search my memory for..."</strong> - Search stored information</li>
                <li><strong>"What do I know about..."</strong> - Query knowledge base</li>
            </ul>
        </div>


        """

    def log_message(self, format, *args):
        """Override to reduce log noise."""
        pass


class JarvisUI:
    """Main Jarvis UI application class."""

    def __init__(self, initial_panel: str = "main", port: int = 8080, open_browser: bool = True):
        """Initialize the Jarvis UI application."""
        self.initial_panel = initial_panel
        self.port = port
        self.server = None
        self.open_browser = open_browser

        # Start MCP system
        self._start_mcp_system()

    def _start_mcp_system(self):
        """Start the MCP client system."""
        try:
            from jarvis.tools import start_mcp_system
            success = start_mcp_system()
            if success:
                logger.info("MCP system started successfully")
            else:
                logger.warning("Failed to start MCP system")
        except Exception as e:
            logger.error(f"Error starting MCP system: {e}")

    def start_server(self):
        """Start the HTTP server."""
        try:
            self.server = HTTPServer(('localhost', self.port), JarvisUIHandler)
            # Store server reference in handler class for shutdown access
            JarvisUIHandler._server_instance = self.server
            logger.info(f"Starting Jarvis UI server on http://localhost:{self.port}")

            # Open browser after a short delay (only if requested)
            if self.open_browser:
                def open_browser():
                    time.sleep(1)
                    url = f"http://localhost:{self.port}/{self.initial_panel}"
                    webbrowser.open(url)
                    logger.info(f"Opened browser to {url}")

                threading.Thread(target=open_browser, daemon=True).start()
            else:
                logger.info(f"Web server started at http://localhost:{self.port}/{self.initial_panel} (browser not opened)")

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

        # Stop MCP system
        self._stop_mcp_system()

    def _stop_mcp_system(self):
        """Stop the MCP client system."""
        try:
            from jarvis.tools import stop_mcp_system
            success = stop_mcp_system()
            if success:
                logger.info("MCP system stopped successfully")
            else:
                logger.warning("Failed to stop MCP system")
        except Exception as e:
            logger.error(f"Error stopping MCP system: {e}")

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
        choices=["main", "settings", "audio", "performance", "tools", "status", "mcp"],
        help="Initial panel to display"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to run the web server on (default: 8080)"
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't automatically open browser window"
    )

    args = parser.parse_args()

    try:
        app = JarvisUI(initial_panel=args.panel, port=args.port, open_browser=not args.no_browser)
        app.run()
    except Exception as e:
        logger.error(f"Failed to start Jarvis UI: {e}")
        print(f"Error: Failed to start Jarvis UI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
