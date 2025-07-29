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
                <a href="/rag" class="nav-link" data-page="rag">
                    <span class="icon">🧠</span>RAG Memory
                </a>
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
        let tools = {};

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

            const html = Object.entries(servers).map(([name, server]) =>
                '<div class="server-card">' +
                    '<div class="server-header">' +
                        '<div class="server-name">' + name + '</div>' +
                        '<div class="server-status status-' + server.status + '">' + server.status.toUpperCase() + '</div>' +
                    '</div>' +
                    '<div class="server-info">' +
                        '<div><strong>Transport:</strong> ' + server.config.transport + '</div>' +
                        (server.config.transport === 'stdio' ?
                            '<div><strong>Command:</strong> ' + server.config.command + ' ' + server.config.args.join(' ') + '</div>' :
                            '<div><strong>URL:</strong> ' + server.config.url + '</div>'
                        ) +
                        '<div><strong>Tools:</strong> ' + (server.tools ? server.tools.length : 0) + ' available</div>' +
                        (server.last_error ? '<div style="color: #F44336;"><strong>Error:</strong> ' + server.last_error + '</div>' : '') +
                    '</div>' +
                    '<div class="server-actions">' +
                        (server.status === 'connected' ?
                            '<button class="btn btn-secondary btn-small" onclick="disconnectServer(\\'' + name + '\\')">Disconnect</button>' :
                            '<button class="btn btn-primary btn-small" onclick="connectServer(\\'' + name + '\\')">Connect</button>'
                        ) +
                        '<button class="btn btn-secondary btn-small" onclick="configureServer(\\'' + name + '\\')">Configure</button>' +
                        '<button class="btn btn-danger btn-small" onclick="removeServer(\\'' + name + '\\')">Remove</button>' +
                    '</div>' +
                '</div>'
            ).join('');

            serversList.innerHTML = html;
        }

        function renderTools() {
            const toolsList = document.getElementById('tools-list');

            if (Object.keys(tools).length === 0) {
                toolsList.innerHTML = '<p>No tools available. Connect to MCP servers to discover tools.</p>';
                return;
            }

            const html = Object.entries(tools).map(([name, tool]) =>
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
                <a href="/">Home</a> / <a href="/rag">RAG Memory</a>
            </div>
        </div>

        <div class="info-banner">
            <h3>🧠 Intelligent RAG System</h3>
            <p>Manage your long-term memory, document library, and intelligent search capabilities. This system uses advanced LLM processing for semantic understanding and query optimization.</p>
        </div>

        <!-- System Status Section -->
        <div class="section">
            <h2>System Status</h2>
            <div id="rag-status" class="status-grid">
                <div class="status-card">
                    <h4>Loading...</h4>
                    <p>Fetching RAG system status...</p>
                </div>
            </div>
        </div>

        <!-- Tab Navigation -->
        <div class="tab-container">
            <div class="tab-nav">
                <button class="tab-button active" onclick="showTab('memory')">🧠 Long-Term Memory</button>
                <button class="tab-button" onclick="showTab('documents')">📚 Document Library</button>
                <button class="tab-button" onclick="showTab('search')">🔍 Intelligent Search</button>
            </div>

            <!-- Long-Term Memory Tab -->
            <div id="memory-tab" class="tab-content active">
                <div class="section-header">
                    <h3>Long-Term Memory</h3>
                    <button class="btn btn-primary" onclick="showAddMemoryModal()">Add Memory</button>
                </div>

                <div id="memory-list" class="memory-list">
                    <p>Loading memories...</p>
                </div>
            </div>

            <!-- Document Library Tab -->
            <div id="documents-tab" class="tab-content">
                <div class="section-header">
                    <h3>Document Library</h3>
                    <div class="button-group">
                        <button class="btn btn-primary" onclick="showUploadModal()">Upload Document</button>
                        <button class="btn btn-secondary" onclick="ingestDocuments()">Process All Documents</button>
                    </div>
                </div>

                <div id="documents-list" class="documents-list">
                    <p>Loading documents...</p>
                </div>
            </div>

            <!-- Intelligent Search Tab -->
            <div id="search-tab" class="tab-content">
                <div class="section-header">
                    <h3>Intelligent Search</h3>
                    <p>Test the enhanced RAG search with query optimization and result synthesis.</p>
                </div>

                <div class="search-container">
                    <div class="form-group">
                        <label for="search-query">Search Query:</label>
                        <input type="text" id="search-query" placeholder="Enter your search query..." class="form-control">
                        <button class="btn btn-primary" onclick="performSearch()">Search</button>
                    </div>

                    <div id="search-results" class="search-results">
                        <p>Enter a query to see intelligent search results with optimization and synthesis.</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Add Memory Modal -->
        <div id="add-memory-modal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Add Long-Term Memory</h3>
                    <button class="modal-close" onclick="hideAddMemoryModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label for="memory-fact">Memory/Fact:</label>
                        <textarea id="memory-fact" placeholder="Enter the information you want to remember..." rows="4" class="form-control"></textarea>
                    </div>
                    <div class="pii-warning">
                        <strong>⚠️ Privacy Notice:</strong> Avoid storing sensitive personal information like passwords, SSNs, or private details.
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="hideAddMemoryModal()">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="addMemory()">Add Memory</button>
                </div>
            </div>
        </div>

        <!-- Upload Document Modal -->
        <div id="upload-modal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Upload Document</h3>
                    <button class="modal-close" onclick="hideUploadModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <label for="document-file">Select File:</label>
                        <input type="file" id="document-file" accept=".txt,.pdf,.doc,.docx" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="document-name">Document Name (optional):</label>
                        <input type="text" id="document-name" placeholder="Leave blank to use filename" class="form-control">
                    </div>
                    <div class="upload-info">
                        <strong>Supported formats:</strong> TXT, PDF, DOC, DOCX<br>
                        <strong>Processing:</strong> Documents will be analyzed with intelligent chunking and metadata extraction.
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" onclick="hideUploadModal()">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="uploadDocument()">Upload & Process</button>
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

        .tab-container {
            margin-top: 2rem;
        }

        .tab-nav {
            display: flex;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 2rem;
        }

        .tab-button {
            background: none;
            border: none;
            color: #b8c5d1;
            padding: 1rem 1.5rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.3s ease;
            font-size: 1rem;
        }

        .tab-button:hover {
            color: #ffffff;
            background: rgba(255, 255, 255, 0.05);
        }

        .tab-button.active {
            color: #6495ed;
            border-bottom-color: #6495ed;
            background: rgba(100, 149, 237, 0.1);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .button-group {
            display: flex;
            gap: 0.5rem;
        }

        .memory-list, .documents-list {
            max-height: 500px;
            overflow-y: auto;
        }

        .memory-item, .document-item {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }

        .memory-item h4, .document-item h4 {
            margin: 0 0 0.5rem 0;
            color: #ffffff;
        }

        .memory-meta, .document-meta {
            font-size: 0.85em;
            color: #b8c5d1;
            margin-bottom: 0.5rem;
        }

        .search-container {
            max-width: 800px;
        }

        .search-results {
            margin-top: 2rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .search-result-item {
            margin-bottom: 1.5rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .search-result-item:last-child {
            border-bottom: none;
        }

        .pii-warning, .upload-info {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.3);
            border-radius: 4px;
            padding: 0.75rem;
            margin-top: 1rem;
            font-size: 0.9em;
        }

        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
        }

        .modal-content {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            margin: 5% auto;
            padding: 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            width: 90%;
            max-width: 600px;
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
        }

        .modal-footer {
            padding: 1rem 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: flex-end;
            gap: 0.5rem;
        }

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

        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .status-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1.5rem;
        }

        .status-card h4 {
            margin: 0 0 1rem 0;
            color: #6495ed;
        }

        .status-card p {
            margin: 0.5rem 0;
            color: #b8c5d1;
        }
        </style>

        <script>
        // Global variables
        let ragStatus = {};
        let memories = [];
        let documents = [];

        // Tab management
        function showTab(tabName) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab-button').forEach(button => {
                button.classList.remove('active');
            });

            // Show selected tab
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');

            // Load data for the tab
            if (tabName === 'memory') {
                loadMemories();
            } else if (tabName === 'documents') {
                loadDocuments();
            }
        }

        // Load RAG system status
        async function loadRAGStatus() {
            try {
                const response = await fetch('/api/rag/status');
                const data = await response.json();
                ragStatus = data;

                const statusHtml = `
                    <div class="status-card">
                        <h4>Database Status</h4>
                        <p>Total Documents: ${data.database?.total_documents || 0}</p>
                        <p>Unique Sources: ${data.database?.unique_sources || 0}</p>
                        <p>Status: ${data.status || 'Unknown'}</p>
                    </div>
                    <div class="status-card">
                        <h4>Intelligence Features</h4>
                        <p>Document LLM: ${data.intelligence?.document_llm || 'Unknown'}</p>
                        <p>Features: ${(data.intelligence?.features || []).join(', ')}</p>
                        <p>Capabilities: ${(data.intelligence?.capabilities || []).join(', ')}</p>
                    </div>
                    <div class="status-card">
                        <h4>Document Library</h4>
                        <p>Ingested: ${data.documents?.ingested_count || 0} documents</p>
                        <p>Path: ${data.documents?.documents_path || 'Unknown'}</p>
                        <p>Formats: ${(data.documents?.supported_formats || []).join(', ')}</p>
                    </div>
                `;

                document.getElementById('rag-status').innerHTML = statusHtml;
            } catch (error) {
                console.error('Error loading RAG status:', error);
                document.getElementById('rag-status').innerHTML = '<div class="status-card"><h4>Error</h4><p>Failed to load RAG status</p></div>';
            }
        }

        // Load memories
        async function loadMemories() {
            try {
                const response = await fetch('/api/rag/memory/long-term');
                const data = await response.json();
                memories = data.memories || [];

                let memoriesHtml = '';
                if (memories.length === 0) {
                    memoriesHtml = '<p>No memories stored yet. Add your first memory using the button above.</p>';
                } else {
                    memories.forEach(memory => {
                        memoriesHtml += `
                            <div class="memory-item">
                                <h4>${memory.title || 'Memory'}</h4>
                                <div class="memory-meta">
                                    Source: ${memory.source} | Type: ${memory.source_type} |
                                    Importance: ${memory.importance_score} |
                                    Topics: ${memory.topics || 'None'}
                                </div>
                                <p>${memory.content}</p>
                            </div>
                        `;
                    });
                }

                document.getElementById('memory-list').innerHTML = memoriesHtml;
            } catch (error) {
                console.error('Error loading memories:', error);
                document.getElementById('memory-list').innerHTML = '<p>Error loading memories: ' + error.message + '</p>';
            }
        }

        // Load documents
        async function loadDocuments() {
            try {
                const response = await fetch('/api/rag/documents');
                const data = await response.json();
                documents = data.documents || [];

                let documentsHtml = '';
                if (documents.length === 0) {
                    documentsHtml = '<p>No documents in library. Upload documents using the button above.</p>';
                } else {
                    documents.forEach(doc => {
                        const ingestedBadge = doc.ingested ?
                            '<span style="color: #4CAF50;">✓ Processed</span>' :
                            '<span style="color: #FF9800;">⚠ Not Processed</span>';

                        documentsHtml += `
                            <div class="document-item">
                                <h4>${doc.name} ${ingestedBadge}</h4>
                                <div class="document-meta">
                                    Size: ${doc.size_mb} MB | Modified: ${doc.modified} |
                                    Type: ${doc.type} | Chunks: ${doc.chunk_count || 0}
                                </div>
                                <div class="button-group" style="margin-top: 0.5rem;">
                                    <button class="btn btn-sm btn-danger" onclick="deleteDocument('${doc.name}')">Delete</button>
                                </div>
                            </div>
                        `;
                    });
                }

                document.getElementById('documents-list').innerHTML = documentsHtml;
            } catch (error) {
                console.error('Error loading documents:', error);
                document.getElementById('documents-list').innerHTML = '<p>Error loading documents: ' + error.message + '</p>';
            }
        }

        // Modal management
        function showAddMemoryModal() {
            document.getElementById('add-memory-modal').style.display = 'block';
        }

        function hideAddMemoryModal() {
            document.getElementById('add-memory-modal').style.display = 'none';
            document.getElementById('memory-fact').value = '';
        }

        function showUploadModal() {
            document.getElementById('upload-modal').style.display = 'block';
        }

        function hideUploadModal() {
            document.getElementById('upload-modal').style.display = 'none';
            document.getElementById('document-file').value = '';
            document.getElementById('document-name').value = '';
        }

        // Add memory
        async function addMemory() {
            const fact = document.getElementById('memory-fact').value.trim();
            if (!fact) {
                alert('Please enter a memory/fact to store.');
                return;
            }

            try {
                const response = await fetch('/api/rag/memory/add', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ fact: fact })
                });

                const result = await response.json();
                if (result.success) {
                    hideAddMemoryModal();
                    loadMemories(); // Refresh the list
                    showNotification('Memory added successfully!', 'success');
                } else {
                    alert('Error adding memory: ' + result.error);
                }
            } catch (error) {
                console.error('Error adding memory:', error);
                alert('Error adding memory: ' + error.message);
            }
        }

        // Upload document
        async function uploadDocument() {
            const fileInput = document.getElementById('document-file');
            const nameInput = document.getElementById('document-name');

            if (!fileInput.files[0]) {
                alert('Please select a file to upload.');
                return;
            }

            const file = fileInput.files[0];
            const filename = nameInput.value.trim() || file.name;

            try {
                const fileContent = await file.text();

                const response = await fetch('/api/rag/documents/upload', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        filename: filename,
                        content: fileContent
                    })
                });

                const result = await response.json();
                if (result.success) {
                    hideUploadModal();
                    loadDocuments(); // Refresh the list
                    showNotification('Document uploaded successfully!', 'success');
                } else {
                    alert('Error uploading document: ' + result.error);
                }
            } catch (error) {
                console.error('Error uploading document:', error);
                alert('Error uploading document: ' + error.message);
            }
        }

        // Ingest documents
        async function ingestDocuments() {
            if (!confirm('This will process all documents in the library with intelligent analysis. Continue?')) {
                return;
            }

            try {
                showNotification('Processing documents... This may take a few minutes.', 'info');

                const response = await fetch('/api/rag/documents/ingest', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });

                const result = await response.json();
                if (result.success) {
                    loadDocuments(); // Refresh the list
                    loadRAGStatus(); // Refresh status
                    showNotification('Documents processed successfully!', 'success');
                } else {
                    alert('Error processing documents: ' + result.error);
                }
            } catch (error) {
                console.error('Error processing documents:', error);
                alert('Error processing documents: ' + error.message);
            }
        }

        // Delete document
        async function deleteDocument(filename) {
            if (!confirm(`Are you sure you want to delete "${filename}"?`)) {
                return;
            }

            try {
                const response = await fetch('/api/rag/documents/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ filename: filename })
                });

                const result = await response.json();
                if (result.success) {
                    loadDocuments(); // Refresh the list
                    showNotification('Document deleted successfully!', 'success');
                } else {
                    alert('Error deleting document: ' + result.error);
                }
            } catch (error) {
                console.error('Error deleting document:', error);
                alert('Error deleting document: ' + error.message);
            }
        }

        // Perform intelligent search
        async function performSearch() {
            const query = document.getElementById('search-query').value.trim();
            if (!query) {
                alert('Please enter a search query.');
                return;
            }

            try {
                document.getElementById('search-results').innerHTML = '<p>Searching with intelligent optimization...</p>';

                const response = await fetch(`/api/rag/search?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                if (data.results) {
                    const results = data.results;
                    const synthesis = results.synthesis || {};
                    const queryOpt = results.query_optimization || {};
                    const searchMeta = results.search_metadata || {};

                    let resultsHtml = `
                        <div class="search-result-item">
                            <h4>🎯 Synthesized Answer</h4>
                            <p><strong>Query:</strong> ${data.query}</p>
                            <p><strong>Optimized Query:</strong> ${queryOpt.optimized_query || 'N/A'}</p>
                            <p><strong>Answer:</strong> ${synthesis.synthesized_answer || 'No answer generated'}</p>
                            <p><strong>Confidence:</strong> ${synthesis.confidence_score || 0} | <strong>Completeness:</strong> ${synthesis.answer_completeness || 'unknown'}</p>
                        </div>
                    `;

                    if (synthesis.key_points && synthesis.key_points.length > 0) {
                        resultsHtml += `
                            <div class="search-result-item">
                                <h4>🔑 Key Points</h4>
                                <ul>
                                    ${synthesis.key_points.map(point => `<li>${point}</li>`).join('')}
                                </ul>
                            </div>
                        `;
                    }

                    if (synthesis.source_citations && synthesis.source_citations.length > 0) {
                        resultsHtml += `
                            <div class="search-result-item">
                                <h4>📚 Sources</h4>
                                <ul>
                                    ${synthesis.source_citations.map(cite => `<li>${cite.source} (${cite.relevance} relevance)</li>`).join('')}
                                </ul>
                            </div>
                        `;
                    }

                    if (results.retrieved_documents && results.retrieved_documents.length > 0) {
                        resultsHtml += `
                            <div class="search-result-item">
                                <h4>📄 Retrieved Documents (${results.retrieved_documents.length})</h4>
                        `;
                        results.retrieved_documents.forEach((doc, index) => {
                            resultsHtml += `
                                <div style="margin-bottom: 1rem; padding: 0.5rem; background: rgba(255,255,255,0.05); border-radius: 4px;">
                                    <strong>Document ${index + 1}:</strong> ${doc.metadata.source || 'Unknown'}<br>
                                    <em>Content:</em> ${doc.content}
                                </div>
                            `;
                        });
                        resultsHtml += '</div>';
                    }

                    resultsHtml += `
                        <div class="search-result-item">
                            <h4>🔍 Search Metadata</h4>
                            <p><strong>Queries Tried:</strong> ${searchMeta.queries_tried ? searchMeta.queries_tried.length : 0}</p>
                            <p><strong>Total Results Found:</strong> ${searchMeta.total_results_found || 0}</p>
                            <p><strong>Final Results:</strong> ${searchMeta.final_results || 0}</p>
                            <p><strong>Query Intent:</strong> ${queryOpt.query_intent || 'unknown'}</p>
                            <p><strong>Search Strategy:</strong> ${queryOpt.search_strategy || 'unknown'}</p>
                        </div>
                    `;

                    document.getElementById('search-results').innerHTML = resultsHtml;
                } else {
                    document.getElementById('search-results').innerHTML = '<p>No results found or error occurred.</p>';
                }
            } catch (error) {
                console.error('Error performing search:', error);
                document.getElementById('search-results').innerHTML = '<p>Error performing search: ' + error.message + '</p>';
            }
        }

        // Notification system
        function showNotification(message, type = 'info') {
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
                setTimeout(() => document.body.removeChild(notification), 300);
            }, 3000);
        }

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            loadRAGStatus();
            loadMemories(); // Load initial tab

            // Handle Enter key in search
            document.getElementById('search-query').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    performSearch();
                }
            });

            // Close modals when clicking outside
            window.addEventListener('click', function(event) {
                if (event.target.classList.contains('modal')) {
                    event.target.style.display = 'none';
                }
            });
        });
        </script>
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
