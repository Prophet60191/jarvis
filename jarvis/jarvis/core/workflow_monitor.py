"""
Web-Based Workflow Monitor

A clean, dark-themed web interface for monitoring Jarvis Professional App Builder workflow progress.
"""

import threading
import time
import os
import webbrowser
import http.server
import socketserver
from pathlib import Path
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)


class WebWorkflowMonitor:
    """Clean, dark-themed web-based workflow monitoring interface."""

    def __init__(self, project_name: str, log_file: Path, project_info: dict = None):
        self.project_name = project_name
        self.log_file = log_file
        self.project_info = project_info or {}
        self.start_time = datetime.now()
        self.phase_times = {}
        self.current_phase = None
        self.is_running = True
        self.port = 8765

        # Phase definitions
        self.phases = [
            "1. Research & Analysis",
            "2. Project Initialization",
            "2.5 Environment Setup",
            "3. Frontend Development",
            "4. Backend Development",
            "5. Database Integration",
            "6. Testing & QA",
            "6.5 Runtime Verification",
            "7. Deployment"
        ]

        self.phase_status = {phase: "⏳ Pending" for phase in self.phases}
        self.activity_log = []

        self.start_monitoring()
        self.start_web_server()

    def generate_html(self):
        """Generate the dark-themed HTML interface."""
        elapsed = datetime.now() - self.start_time
        elapsed_str = f"{int(elapsed.total_seconds() // 60):02d}:{int(elapsed.total_seconds() % 60):02d}"

        # Build phase status HTML
        phase_html = ""
        for i, phase in enumerate(self.phases):
            status = self.phase_status[phase]
            if "Complete" in status:
                color = "#4caf50"
                icon = "✅"
                status_text = status
            elif "In Progress" in status:
                color = "#ff9800"
                icon = "🔄"
                status_text = "In Progress"
            else:
                color = "#666666"
                icon = "⏳"
                status_text = "Pending"

            # Add progress indicator
            progress_bar = ""
            if "Complete" in status:
                progress_bar = '<span style="color: #4caf50;">████████████</span>'
            elif "In Progress" in status:
                progress_bar = '<span style="color: #ff9800;">██████░░░░░░</span>'
            else:
                progress_bar = '<span style="color: #333333;">░░░░░░░░░░░░</span>'

            phase_html += f'''
            <div style="color: {color}; margin: 8px 0; font-family: monospace; padding: 5px; background-color: #2a2a2a; border-radius: 3px;">
                {icon} <strong>{phase}</strong><br>
                <span style="font-size: 12px; margin-left: 20px;">Status: {status_text}</span><br>
                <span style="font-size: 10px; margin-left: 20px;">{progress_bar}</span>
            </div>'''

        # Build activity log HTML
        activity_html = ""
        for entry in self.activity_log[-15:]:  # Last 15 entries
            activity_html += f'<div style="margin: 2px 0; font-family: monospace; font-size: 12px;">{entry}</div>'

        # Project info
        location = self.project_info.get('location', f'projects/{self.project_name}')
        tech_stack = self.project_info.get('tech_stack', 'Auto-selected')
        auto_start = self.project_info.get('auto_start', 'Enabled')

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🏗️ Jarvis Workflow Monitor - {self.project_name}</title>
            <meta http-equiv="refresh" content="2">
            <style>
                body {{
                    background-color: #1e1e1e;
                    color: #ffffff;
                    font-family: 'Consolas', 'Monaco', monospace;
                    margin: 20px;
                    line-height: 1.4;
                }}
                .header {{
                    border-bottom: 2px solid #333333;
                    padding-bottom: 15px;
                    margin-bottom: 20px;
                }}
                .section {{
                    margin-bottom: 25px;
                    padding: 15px;
                    background-color: #2d2d2d;
                    border-radius: 5px;
                }}
                .section-title {{
                    color: #007acc;
                    font-weight: bold;
                    margin-bottom: 10px;
                    font-size: 14px;
                }}
                .activity-log {{
                    background-color: #333333;
                    padding: 10px;
                    border-radius: 3px;
                    max-height: 200px;
                    overflow-y: auto;
                }}
                .project-info {{
                    background-color: #2a2a2a;
                }}
                .status {{
                    color: #007acc;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🏗️ Jarvis Workflow Monitor</h2>
                <div><strong>Project:</strong> {self.project_name}</div>
                <div class="status">Status: {self.current_phase or "Initializing..."}</div>
                <div><strong>Elapsed:</strong> {elapsed_str}</div>
            </div>

            <div class="section">
                <div class="section-title">WORKFLOW PROGRESS:</div>
                {phase_html}
            </div>

            <div class="section">
                <div class="section-title">CURRENT ACTIVITY:</div>
                <div class="activity-log">
                    {activity_html}
                </div>
            </div>

            <div class="section project-info">
                <div class="section-title">PROJECT INFO:</div>
                <div><strong>Location:</strong> {location}</div>
                <div><strong>Tech Stack:</strong> {tech_stack}</div>
                <div><strong>Auto-start:</strong> {auto_start}</div>
            </div>

            <div style="text-align: center; margin-top: 30px; color: #666666; font-size: 12px;">
                Auto-refreshing every 2 seconds • Jarvis Professional App Builder
            </div>
        </body>
        </html>
        """
        return html
    
    def start_web_server(self):
        """Start the web server for the monitor interface."""
        class MonitorHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, monitor, *args, **kwargs):
                self.monitor = monitor
                super().__init__(*args, **kwargs)

            def do_GET(self):
                if self.path == '/' or self.path == '/monitor':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    html = self.monitor.generate_html()
                    self.wfile.write(html.encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                # Suppress server logs
                pass

        def create_handler(*args, **kwargs):
            return MonitorHandler(self, *args, **kwargs)

        def start_server():
            try:
                with socketserver.TCPServer(("", self.port), create_handler) as httpd:
                    self.httpd = httpd
                    httpd.serve_forever()
            except Exception as e:
                logger.warning(f"Web server error: {e}")

        self.server_thread = threading.Thread(target=start_server, daemon=True)
        self.server_thread.start()

        # Open browser
        time.sleep(0.5)  # Give server time to start
        try:
            webbrowser.open(f'http://localhost:{self.port}/monitor')
        except Exception as e:
            logger.warning(f"Could not open browser: {e}")

    def start_monitoring(self):
        """Start monitoring the workflow log file."""
        def monitor_thread():
            last_size = 0
            while self.is_running:
                try:
                    if self.log_file.exists():
                        current_size = self.log_file.stat().st_size
                        if current_size > last_size:
                            with open(self.log_file, 'r') as f:
                                f.seek(last_size)
                                new_content = f.read()
                                self.process_new_log_content(new_content)
                            last_size = current_size
                    time.sleep(1)
                except Exception as e:
                    logger.warning(f"Error monitoring log file: {e}")
                    time.sleep(2)

        self.monitor_thread = threading.Thread(target=monitor_thread, daemon=True)
        self.monitor_thread.start()

    def process_new_log_content(self, content):
        """Process new log file content."""
        lines = content.strip().split('\n')
        for line in lines:
            if line.strip():
                self.add_activity_entry(line)
                self.update_phase_status(line)

    def add_activity_entry(self, entry):
        """Add entry to activity log."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_entry = f"[{timestamp}] {entry}"
        self.activity_log.append(formatted_entry)



        # Keep only last 50 entries
        if len(self.activity_log) > 50:
            self.activity_log = self.activity_log[-50:]

    def update_phase_status(self, log_entry):
        """Update phase status based on log entry."""
        # Parse phase information from log entries
        log_lower = log_entry.lower()

        # Check for phase patterns in the log entry
        for i, phase in enumerate(self.phases):
            phase_num = phase.split('.')[0]
            phase_name = phase.split('. ', 1)[1] if '. ' in phase else phase

            # Multiple patterns to match phase updates
            patterns = [
                f"phase {phase_num}",
                f"phase {phase_num}:",
                f"📋 phase {phase_num}",
                phase_name.lower(),
                f"phase {phase_num}.5" if ".5" in phase_num else None
            ]

            # Remove None patterns
            patterns = [p for p in patterns if p is not None]

            # Check if any pattern matches
            phase_mentioned = any(pattern in log_lower for pattern in patterns)

            if phase_mentioned:
                if any(word in log_lower for word in ["starting", "start", "begin", "commenced"]):
                    self.phase_status[phase] = "🔄 In Progress"
                    self.current_phase = phase
                    self.phase_times[phase] = datetime.now()

                elif any(word in log_lower for word in ["complete", "completed", "finished", "done", "success"]):
                    if phase in self.phase_times:
                        duration = datetime.now() - self.phase_times[phase]
                        self.phase_status[phase] = f"✅ Complete [{self.format_duration(duration)}]"
                    else:
                        self.phase_status[phase] = "✅ Complete"


    def format_duration(self, duration):
        """Format duration as MM:SS."""
        total_seconds = int(duration.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def close(self):
        """Close the workflow monitor."""
        self.is_running = False
        if hasattr(self, 'httpd'):
            self.httpd.shutdown()


def start_workflow_monitor(project_name: str, log_file: Path, project_info: dict = None):
    """Start the web-based workflow monitor."""
    try:
        monitor = WebWorkflowMonitor(project_name, log_file, project_info)
        logger.info(f"Started web workflow monitor at http://localhost:{monitor.port}/monitor")
        return monitor
    except Exception as e:
        logger.error(f"Error starting workflow monitor: {e}")
        return None
