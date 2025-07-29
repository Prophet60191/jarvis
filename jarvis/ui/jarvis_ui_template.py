#!/usr/bin/env python3
"""
Jarvis UI Template System

Standardized templates and components for creating custom Jarvis UIs.
This module provides reusable templates, themes, and components that ensure
consistency across all Jarvis user interfaces.

Usage:
    from jarvis.ui.jarvis_ui_template import JarvisUITemplate, JarvisDesktopApp
    
    class MyUI(JarvisUITemplate):
        def get_main_content(self):
            return self.components.card("Welcome", "My custom UI")
"""

import sys
import os
import json
import logging
import signal
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class JarvisTheme:
    """Standardized Jarvis theme and styling system."""
    
    # Color Palette
    COLORS = {
        'primary': '#64ffda',           # Jarvis cyan
        'secondary': '#6495ed',         # Jarvis blue
        'background': 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
        'surface': 'rgba(255, 255, 255, 0.05)',
        'surface_hover': 'rgba(255, 255, 255, 0.1)',
        'text_primary': '#e0e6ed',
        'text_secondary': '#b8c5d1',
        'text_accent': '#8892b0',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'error': '#f44336',
        'border': 'rgba(255, 255, 255, 0.1)',
        'shadow': 'rgba(0, 0, 0, 0.3)'
    }
    
    # Typography
    FONTS = {
        'primary': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        'mono': 'Monaco, "Cascadia Code", "Roboto Mono", monospace'
    }
    
    # Spacing
    SPACING = {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        'xxl': '48px'
    }
    
    def get_base_css(self) -> str:
        """Get the base CSS for Jarvis UIs."""
        return f"""
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {self.FONTS['primary']};
            margin: 0;
            padding: 0;
            background: {self.COLORS['background']};
            min-height: 100vh;
            color: {self.COLORS['text_primary']};
            display: flex;
        }}
        
        .sidebar {{
            width: 280px;
            background: {self.COLORS['surface']};
            backdrop-filter: blur(10px);
            border-right: 1px solid {self.COLORS['border']};
            padding: {self.SPACING['lg']} 0;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            z-index: 1000;
        }}
        
        .sidebar-header {{
            padding: 0 {self.SPACING['lg']} {self.SPACING['xl']} {self.SPACING['lg']};
            border-bottom: 1px solid {self.COLORS['border']};
            margin-bottom: {self.SPACING['lg']};
        }}
        
        .sidebar-header h1 {{
            color: #ffffff;
            margin: 0;
            font-size: 1.8em;
            text-shadow: 0 2px 4px {self.COLORS['shadow']};
            text-align: center;
        }}
        
        .sidebar-header .subtitle {{
            color: {self.COLORS['text_secondary']};
            font-size: 0.9em;
            text-align: center;
            margin-top: 5px;
        }}
        
        .main-content {{
            margin-left: 280px;
            padding: {self.SPACING['xl']};
            flex: 1;
            min-height: 100vh;
        }}
        
        .main-header {{
            margin-bottom: {self.SPACING['xl']};
        }}
        
        .main-header h1 {{
            font-size: 2.2em;
            margin-bottom: {self.SPACING['sm']};
            color: #ffffff;
        }}
        
        .main-header p {{
            color: {self.COLORS['text_secondary']};
            font-size: 1.1em;
        }}
        
        /* Navigation Styles */
        .nav {{
            padding: 0 {self.SPACING['sm']};
        }}
        
        .nav-section {{
            margin-bottom: 25px;
        }}
        
        .nav-section-title {{
            font-size: 12px;
            font-weight: 600;
            color: {self.COLORS['text_accent']};
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: {self.SPACING['sm']};
            padding: 0 {self.SPACING['sm']};
        }}
        
        .nav-link {{
            display: flex;
            align-items: center;
            padding: 12px 15px;
            margin: 2px 0;
            border-radius: 8px;
            text-decoration: none;
            color: {self.COLORS['text_secondary']};
            transition: all 0.2s ease;
            cursor: pointer;
            border: 1px solid transparent;
        }}
        
        .nav-link:hover {{
            background: rgba(100, 255, 218, 0.1);
            color: {self.COLORS['primary']};
            border-color: rgba(100, 255, 218, 0.2);
        }}
        
        .nav-link.active {{
            background: rgba(100, 255, 218, 0.15);
            color: {self.COLORS['primary']};
            border-color: rgba(100, 255, 218, 0.3);
        }}
        
        .nav-link .icon {{
            margin-right: {self.SPACING['sm']};
            font-size: 1.1em;
        }}
        
        /* Card Styles */
        .card {{
            background: {self.COLORS['surface']};
            backdrop-filter: blur(10px);
            border: 1px solid {self.COLORS['border']};
            border-radius: 12px;
            padding: {self.SPACING['lg']};
            margin-bottom: {self.SPACING['lg']};
            transition: all 0.3s ease;
        }}
        
        .card:hover {{
            background: {self.COLORS['surface_hover']};
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }}
        
        .card h3 {{
            margin-bottom: {self.SPACING['md']};
            color: #ffffff;
        }}
        
        .card p {{
            color: {self.COLORS['text_secondary']};
            line-height: 1.6;
            margin-bottom: {self.SPACING['md']};
        }}
        
        /* Button Styles */
        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }}
        
        .btn-primary {{
            background: {self.COLORS['primary']};
            color: #0f0f23;
        }}
        
        .btn-primary:hover {{
            background: #4fd1c7;
            transform: translateY(-1px);
        }}
        
        .btn-secondary {{
            background: {self.COLORS['secondary']};
            color: #ffffff;
        }}
        
        .btn-secondary:hover {{
            background: #5a7fd8;
            transform: translateY(-1px);
        }}
        
        .btn-danger {{
            background: {self.COLORS['error']};
            color: #ffffff;
        }}
        
        .btn-danger:hover {{
            background: #d32f2f;
            transform: translateY(-1px);
        }}
        
        /* Grid Layouts */
        .content-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: {self.SPACING['lg']};
            margin-bottom: {self.SPACING['xl']};
        }}
        
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: {self.SPACING['md']};
        }}
        
        /* Form Styles */
        .form-group {{
            margin-bottom: {self.SPACING['lg']};
        }}
        
        .form-label {{
            display: block;
            margin-bottom: {self.SPACING['sm']};
            color: {self.COLORS['text_primary']};
            font-weight: 500;
        }}
        
        .form-input {{
            width: 100%;
            padding: 12px;
            border: 1px solid {self.COLORS['border']};
            border-radius: 6px;
            background: {self.COLORS['surface']};
            color: {self.COLORS['text_primary']};
            font-size: 14px;
        }}
        
        .form-input:focus {{
            outline: none;
            border-color: {self.COLORS['primary']};
            box-shadow: 0 0 0 2px rgba(100, 255, 218, 0.2);
        }}
        
        /* Status Indicators */
        .status-indicator {{
            display: inline-flex;
            align-items: center;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        
        .status-success {{
            background: rgba(76, 175, 80, 0.2);
            color: {self.COLORS['success']};
        }}
        
        .status-warning {{
            background: rgba(255, 152, 0, 0.2);
            color: {self.COLORS['warning']};
        }}
        
        .status-error {{
            background: rgba(244, 67, 54, 0.2);
            color: {self.COLORS['error']};
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .sidebar {{
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }}
            
            .sidebar.open {{
                transform: translateX(0);
            }}
            
            .main-content {{
                margin-left: 0;
                padding: {self.SPACING['md']};
            }}
            
            .content-grid {{
                grid-template-columns: 1fr;
            }}
        }}
        """


class JarvisComponents:
    """Reusable UI components for Jarvis interfaces."""
    
    def __init__(self, theme: JarvisTheme):
        self.theme = theme
    
    def card(self, title: str, content: str, actions: List[Dict] = None) -> str:
        """Create a standard Jarvis card component."""
        actions_html = ""
        if actions:
            actions_html = '<div class="card-actions">'
            for action in actions:
                actions_html += self.button(
                    action.get('label', 'Action'),
                    action.get('action', ''),
                    action.get('style', 'primary')
                )
            actions_html += '</div>'
        
        return f"""
        <div class="card">
            <h3>{title}</h3>
            <div class="card-content">{content}</div>
            {actions_html}
        </div>
        """
    
    def button(self, text: str, action: str, style: str = "primary") -> str:
        """Create a standard Jarvis button component."""
        return f'<button class="btn btn-{style}" onclick="{action}">{text}</button>'
    
    def form_field(self, label: str, field_type: str, name: str, **kwargs) -> str:
        """Create a standard form field component."""
        required = 'required' if kwargs.get('required', False) else ''
        placeholder = f'placeholder="{kwargs.get("placeholder", "")}"' if kwargs.get('placeholder') else ''
        value = f'value="{kwargs.get("value", "")}"' if kwargs.get('value') else ''
        
        if field_type == 'select':
            options_html = ""
            for option in kwargs.get('options', []):
                selected = 'selected' if option == kwargs.get('value') else ''
                options_html += f'<option value="{option}" {selected}>{option}</option>'
            
            return f"""
            <div class="form-group">
                <label class="form-label" for="{name}">{label}</label>
                <select class="form-input" name="{name}" id="{name}" {required}>
                    {options_html}
                </select>
            </div>
            """
        
        return f"""
        <div class="form-group">
            <label class="form-label" for="{name}">{label}</label>
            <input class="form-input" type="{field_type}" name="{name}" id="{name}" 
                   {placeholder} {value} {required}>
        </div>
        """
    
    def status_indicator(self, status: str, label: str) -> str:
        """Create a status indicator component."""
        return f'<span class="status-indicator status-{status}">{label}</span>'
    
    def navigation_section(self, title: str, links: List[Dict]) -> str:
        """Create a navigation section component."""
        links_html = ""
        for link in links:
            active_class = "active" if link.get('active', False) else ""
            links_html += f"""
            <a href="{link['url']}" class="nav-link {active_class}">
                <span class="icon">{link.get('icon', '•')}</span>
                {link['label']}
            </a>
            """
        
        return f"""
        <div class="nav-section">
            <div class="nav-section-title">{title}</div>
            {links_html}
        </div>
        """


class JarvisUITemplate(ABC):
    """Base template for all Jarvis UIs."""
    
    def __init__(self, app_name: str, version: str = "1.0"):
        self.app_name = app_name
        self.version = version
        self.theme = JarvisTheme()
        self.components = JarvisComponents(self.theme)
    
    def get_html_template(self, title: str, content: str) -> str:
        """Generate complete HTML page with Jarvis styling."""
        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title} - {self.app_name}</title>
            <style>
                {self.theme.get_base_css()}
                {self.get_custom_css()}
            </style>
        </head>
        <body>
            <div class="sidebar">
                <div class="sidebar-header">
                    <h1>{self.app_name}</h1>
                    <div class="subtitle">v{self.version}</div>
                </div>
                <nav class="nav">
                    {self.get_navigation()}
                </nav>
            </div>
            
            <div class="main-content">
                <div class="main-header">
                    <h1>{title}</h1>
                </div>
                <div class="content">
                    {content}
                </div>
            </div>
            
            <script>
                {self.get_javascript()}
            </script>
        </body>
        </html>
        """
    
    @abstractmethod
    def get_navigation(self) -> str:
        """Override to provide custom navigation."""
        return ""
    
    def get_custom_css(self) -> str:
        """Override to provide custom CSS."""
        return ""
    
    def get_javascript(self) -> str:
        """Override to provide custom JavaScript."""
        return ""


class JarvisDesktopApp:
    """Base class for Jarvis desktop applications using pywebview."""
    
    def __init__(self, app_name: str, debug: bool = False):
        self.app_name = app_name
        self.debug = debug
        self.window = None
        self.shutdown_event = threading.Event()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
    
    def shutdown(self):
        """Shutdown the application."""
        self.shutdown_event.set()
        if self.window:
            try:
                import webview
                webview.destroy_window(self.window)
            except:
                pass
    
    @abstractmethod
    def get_html_content(self) -> str:
        """Override to provide HTML content."""
        return "<h1>Override get_html_content()</h1>"
    
    def run(self, width: int = 1200, height: int = 800):
        """Run the desktop application."""
        try:
            import webview
        except ImportError:
            print("⚠️  pywebview not installed. Install with: pip install pywebview")
            return
        
        # Create the window
        self.window = webview.create_window(
            self.app_name,
            html=self.get_html_content(),
            width=width,
            height=height,
            resizable=True,
            shadow=True
        )
        
        # Start webview
        webview.start(debug=self.debug)
