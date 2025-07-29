#!/usr/bin/env python3
"""
Custom Jarvis UI Example

This example demonstrates how to create a custom Jarvis UI using the template system.
It shows various components, styling options, and integration patterns.

Usage:
    python examples/custom_ui_example.py
"""

import sys
import os
from pathlib import Path

# Add the jarvis package to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jarvis.ui.jarvis_ui_template import JarvisUITemplate, JarvisDesktopApp
from jarvis.ui.templates.simple_template import SimpleJarvisTemplate


class CustomJarvisUI(JarvisUITemplate):
    """Example custom Jarvis UI demonstrating various features."""
    
    def __init__(self):
        super().__init__("Custom Jarvis UI", "1.0")
        self.current_page = "dashboard"
    
    def get_navigation(self) -> str:
        """Custom navigation with multiple sections."""
        return f"""
        {self.components.navigation_section("Main", [
            {"icon": "🏠", "label": "Dashboard", "url": "/", "active": True},
            {"icon": "📊", "label": "Analytics", "url": "/analytics"},
            {"icon": "🔧", "label": "Tools", "url": "/tools"}
        ])}
        
        {self.components.navigation_section("Management", [
            {"icon": "👥", "label": "Users", "url": "/users"},
            {"icon": "📁", "label": "Files", "url": "/files"},
            {"icon": "🔐", "label": "Security", "url": "/security"}
        ])}
        
        {self.components.navigation_section("System", [
            {"icon": "⚙️", "label": "Settings", "url": "/settings"},
            {"icon": "📋", "label": "Logs", "url": "/logs"},
            {"icon": "ℹ️", "label": "About", "url": "/about"}
        ])}
        """
    
    def get_dashboard_content(self) -> str:
        """Dashboard page with various widgets."""
        return f"""
        <div class="page-header">
            <h1>Dashboard</h1>
            <p>Welcome to your custom Jarvis interface</p>
        </div>
        
        <div class="content-grid">
            {self.components.card("System Status", '''
                <div class="status-grid">
                    <div class="status-item">
                        <span class="status-label">Jarvis Core:</span>
                        <span class="status-indicator status-success">Running</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Plugins:</span>
                        <span class="status-indicator status-success">8 Active</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Memory:</span>
                        <span class="status-indicator status-warning">75% Used</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Storage:</span>
                        <span class="status-indicator status-success">45% Used</span>
                    </div>
                </div>
            ''', [
                {"label": "Refresh", "action": "refreshStatus()", "style": "primary"},
                {"label": "Details", "action": "showDetails()", "style": "secondary"}
            ])}
            
            {self.components.card("Quick Actions", '''
                <div class="action-grid">
                    <button class="action-btn" onclick="quickAction('voice')">
                        <div class="action-icon">🎤</div>
                        <div class="action-label">Voice Test</div>
                    </button>
                    <button class="action-btn" onclick="quickAction('memory')">
                        <div class="action-icon">🧠</div>
                        <div class="action-label">Memory</div>
                    </button>
                    <button class="action-btn" onclick="quickAction('plugins')">
                        <div class="action-icon">🔌</div>
                        <div class="action-label">Plugins</div>
                    </button>
                    <button class="action-btn" onclick="quickAction('settings')">
                        <div class="action-icon">⚙️</div>
                        <div class="action-label">Settings</div>
                    </button>
                </div>
            ''')}
            
            {self.components.card("Recent Activity", '''
                <div class="activity-list">
                    <div class="activity-item">
                        <div class="activity-icon">✅</div>
                        <div class="activity-content">
                            <div class="activity-title">Plugin loaded successfully</div>
                            <div class="activity-meta">device_time_tool • 2 minutes ago</div>
                        </div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-icon">🎤</div>
                        <div class="activity-content">
                            <div class="activity-title">Voice command processed</div>
                            <div class="activity-meta">"What time is it?" • 5 minutes ago</div>
                        </div>
                    </div>
                    <div class="activity-item">
                        <div class="activity-icon">🔧</div>
                        <div class="activity-content">
                            <div class="activity-title">Configuration updated</div>
                            <div class="activity-meta">Audio settings • 10 minutes ago</div>
                        </div>
                    </div>
                </div>
            ''', [
                {"label": "View All", "action": "showAllActivity()", "style": "secondary"}
            ])}
        </div>
        """
    
    def get_tools_content(self) -> str:
        """Tools page with available Jarvis tools."""
        return f"""
        <div class="page-header">
            <h1>Jarvis Tools</h1>
            <p>Manage and interact with Jarvis plugins and tools</p>
        </div>
        
        <div class="tools-container">
            <div class="tools-section">
                <h3>Core Tools</h3>
                <div class="tools-grid">
                    <div class="tool-card">
                        <div class="tool-icon">🕐</div>
                        <div class="tool-info">
                            <h4>Device Time Tool</h4>
                            <p>Get current time and date information</p>
                            <div class="tool-status">
                                <span class="status-indicator status-success">Active</span>
                            </div>
                        </div>
                        <div class="tool-actions">
                            <button class="btn btn-primary btn-small" onclick="testTool('time')">Test</button>
                        </div>
                    </div>
                    
                    <div class="tool-card">
                        <div class="tool-icon">🧠</div>
                        <div class="tool-info">
                            <h4>RAG Memory</h4>
                            <p>Store and retrieve information</p>
                            <div class="tool-status">
                                <span class="status-indicator status-success">Active</span>
                            </div>
                        </div>
                        <div class="tool-actions">
                            <button class="btn btn-primary btn-small" onclick="testTool('memory')">Test</button>
                        </div>
                    </div>
                    
                    <div class="tool-card">
                        <div class="tool-icon">👤</div>
                        <div class="tool-info">
                            <h4>User Profile</h4>
                            <p>Manage user information and preferences</p>
                            <div class="tool-status">
                                <span class="status-indicator status-success">Active</span>
                            </div>
                        </div>
                        <div class="tool-actions">
                            <button class="btn btn-primary btn-small" onclick="testTool('profile')">Test</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="tools-section">
                <h3>Advanced Tools</h3>
                <div class="tools-grid">
                    <div class="tool-card">
                        <div class="tool-icon">🤖</div>
                        <div class="tool-info">
                            <h4>Aider Integration</h4>
                            <p>AI-powered code editing</p>
                            <div class="tool-status">
                                <span class="status-indicator status-success">Active</span>
                            </div>
                        </div>
                        <div class="tool-actions">
                            <button class="btn btn-primary btn-small" onclick="testTool('aider')">Test</button>
                        </div>
                    </div>
                    
                    <div class="tool-card">
                        <div class="tool-icon">🌐</div>
                        <div class="tool-info">
                            <h4>Web Automation</h4>
                            <p>LaVague web automation</p>
                            <div class="tool-status">
                                <span class="status-indicator status-warning">Available</span>
                            </div>
                        </div>
                        <div class="tool-actions">
                            <button class="btn btn-secondary btn-small" onclick="enableTool('web')">Enable</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def get_custom_css(self) -> str:
        """Custom CSS for this UI."""
        return """
        .page-header {
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .page-header h1 {
            margin-bottom: 0.5rem;
        }
        
        .page-header p {
            color: #8892b0;
            margin: 0;
        }
        
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 4px;
        }
        
        .status-label {
            font-weight: 500;
        }
        
        .action-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }
        
        .action-btn {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            color: #e0e6ed;
        }
        
        .action-btn:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }
        
        .action-icon {
            font-size: 1.5em;
            margin-bottom: 0.5rem;
        }
        
        .action-label {
            font-size: 0.9em;
            font-weight: 500;
        }
        
        .activity-list {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .activity-item {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
            padding: 0.75rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .activity-icon {
            font-size: 1.2em;
            margin-top: 0.2rem;
        }
        
        .activity-title {
            font-weight: 500;
            margin-bottom: 0.25rem;
        }
        
        .activity-meta {
            color: #8892b0;
            font-size: 0.9em;
        }
        
        .tools-container {
            max-width: 1000px;
        }
        
        .tools-section {
            margin-bottom: 2rem;
        }
        
        .tools-section h3 {
            color: #64ffda;
            margin-bottom: 1rem;
        }
        
        .tools-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
        }
        
        .tool-card {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            transition: all 0.2s ease;
        }
        
        .tool-card:hover {
            background: rgba(255, 255, 255, 0.08);
        }
        
        .tool-icon {
            font-size: 2em;
            flex-shrink: 0;
        }
        
        .tool-info {
            flex: 1;
        }
        
        .tool-info h4 {
            margin: 0 0 0.25rem 0;
            color: #ffffff;
        }
        
        .tool-info p {
            margin: 0 0 0.5rem 0;
            color: #8892b0;
            font-size: 0.9em;
        }
        
        .tool-status {
            margin: 0;
        }
        
        .tool-actions {
            flex-shrink: 0;
        }
        
        .btn-small {
            padding: 6px 12px;
            font-size: 0.8em;
        }
        """
    
    def get_javascript(self) -> str:
        """Custom JavaScript for this UI."""
        return """
        function refreshStatus() {
            alert('Status refreshed! (This would update real data in a full implementation)');
        }
        
        function showDetails() {
            alert('Detailed system information would be shown here.');
        }
        
        function quickAction(action) {
            switch(action) {
                case 'voice':
                    alert('Voice test: "Hey Jarvis, what time is it?"');
                    break;
                case 'memory':
                    alert('Memory test: Accessing stored information...');
                    break;
                case 'plugins':
                    alert('Plugin management interface would open here.');
                    break;
                case 'settings':
                    alert('Settings panel would open here.');
                    break;
            }
        }
        
        function testTool(tool) {
            alert(`Testing ${tool} tool... (This would execute the actual tool in a full implementation)`);
        }
        
        function enableTool(tool) {
            alert(`Enabling ${tool} tool... (This would activate the tool in a full implementation)`);
        }
        
        function showAllActivity() {
            alert('Full activity log would be displayed here.');
        }
        
        // Simple page routing
        function showPage(page) {
            const content = document.querySelector('.content');
            
            switch(page) {
                case 'dashboard':
                    content.innerHTML = getDashboardContent();
                    break;
                case 'tools':
                    content.innerHTML = getToolsContent();
                    break;
                default:
                    content.innerHTML = '<h2>Page not implemented yet</h2><p>This page is coming soon!</p>';
            }
        }
        """


class CustomJarvisApp(JarvisDesktopApp):
    """Desktop app for the custom UI example."""
    
    def __init__(self):
        super().__init__("Custom Jarvis UI Example")
        self.ui = CustomJarvisUI()
    
    def get_html_content(self) -> str:
        """Get the complete HTML for the custom app."""
        content = self.ui.get_dashboard_content()
        return self.ui.get_html_template("Dashboard", content)


if __name__ == "__main__":
    print("🚀 Starting Custom Jarvis UI Example...")
    print("This demonstrates the Jarvis UI Template System capabilities.")
    print("Close the window or press Ctrl+C to exit.")
    
    app = CustomJarvisApp()
    app.run(width=1400, height=900)
