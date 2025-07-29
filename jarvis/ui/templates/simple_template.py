#!/usr/bin/env python3
"""
Simple Jarvis UI Template

Basic template for creating simple, clean Jarvis UIs with minimal setup.
Perfect for quick prototypes and straightforward interfaces.

Usage:
    from jarvis.ui.templates.simple_template import SimpleJarvisTemplate
    
    class MySimpleUI(SimpleJarvisTemplate):
        def get_main_content(self):
            return self.components.card("Welcome", "My simple Jarvis UI")
"""

from typing import Dict, List, Any
from ..jarvis_ui_template import JarvisUITemplate, JarvisDesktopApp


class SimpleJarvisTemplate(JarvisUITemplate):
    """Simple template for basic Jarvis UIs."""
    
    def __init__(self, app_name: str, version: str = "1.0"):
        super().__init__(app_name, version)
    
    def get_navigation(self) -> str:
        """Simple navigation structure."""
        return self.components.navigation_section("Main", [
            {"icon": "🏠", "label": "Home", "url": "/", "active": True},
            {"icon": "⚙️", "label": "Settings", "url": "/settings"},
            {"icon": "ℹ️", "label": "About", "url": "/about"}
        ])
    
    def get_main_content(self) -> str:
        """Override to provide main page content."""
        return self.components.card(
            "Welcome",
            f"Welcome to {self.app_name}! This is a simple Jarvis UI template.",
            [
                {"label": "Get Started", "action": "showWelcome()", "style": "primary"},
                {"label": "Learn More", "action": "showInfo()", "style": "secondary"}
            ]
        )
    
    def get_settings_content(self) -> str:
        """Settings page content."""
        return f"""
        <div class="settings-container">
            <h2>Settings</h2>
            
            <div class="settings-section">
                <h3>General</h3>
                {self.components.form_field("App Name", "text", "app_name", value=self.app_name)}
                {self.components.form_field("Theme", "select", "theme", options=["Dark", "Light"], value="Dark")}
            </div>
            
            <div class="settings-section">
                <h3>Preferences</h3>
                {self.components.form_field("Auto-refresh", "checkbox", "auto_refresh")}
                {self.components.form_field("Notifications", "checkbox", "notifications")}
            </div>
            
            <div class="settings-actions">
                {self.components.button("Save Settings", "saveSettings()", "primary")}
                {self.components.button("Reset", "resetSettings()", "secondary")}
            </div>
        </div>
        """
    
    def get_about_content(self) -> str:
        """About page content."""
        return f"""
        <div class="about-container">
            <h2>About {self.app_name}</h2>
            
            {self.components.card("Application Info", f"""
                <p><strong>Name:</strong> {self.app_name}</p>
                <p><strong>Version:</strong> {self.version}</p>
                <p><strong>Built with:</strong> Jarvis UI Template System</p>
                <p><strong>Framework:</strong> Python + HTML/CSS/JS</p>
            """)}
            
            {self.components.card("Features", """
                <ul>
                    <li>Clean, modern interface</li>
                    <li>Responsive design</li>
                    <li>Easy customization</li>
                    <li>Built-in Jarvis integration</li>
                </ul>
            """)}
            
            {self.components.card("Support", """
                <p>For help and support, please refer to the Jarvis documentation.</p>
                <div style="margin-top: 1rem;">
                    <a href="#" class="btn btn-primary" onclick="openDocs()">View Documentation</a>
                </div>
            """)}
        </div>
        """
    
    def get_custom_css(self) -> str:
        """Simple template specific CSS."""
        return """
        .settings-container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        .settings-section {
            margin-bottom: 2rem;
            padding: 1.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .settings-section h3 {
            margin-bottom: 1rem;
            color: #64ffda;
            font-size: 1.2em;
        }
        
        .settings-actions {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
        }
        
        .about-container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .about-container ul {
            list-style: none;
            padding: 0;
        }
        
        .about-container li {
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .about-container li:last-child {
            border-bottom: none;
        }
        
        .about-container li:before {
            content: "✓";
            color: #64ffda;
            margin-right: 0.5rem;
        }
        """
    
    def get_javascript(self) -> str:
        """Simple template JavaScript."""
        return """
        function showWelcome() {
            alert('Welcome to your Jarvis UI! You can customize this message.');
        }
        
        function showInfo() {
            alert('This is built with the Jarvis UI Template System. Check the documentation for more features.');
        }
        
        function saveSettings() {
            // Get form values
            const appName = document.getElementById('app_name').value;
            const theme = document.getElementById('theme').value;
            const autoRefresh = document.getElementById('auto_refresh').checked;
            const notifications = document.getElementById('notifications').checked;
            
            // Here you would typically send to your backend
            console.log('Settings:', { appName, theme, autoRefresh, notifications });
            
            alert('Settings saved successfully!');
        }
        
        function resetSettings() {
            if (confirm('Are you sure you want to reset all settings?')) {
                // Reset form values
                document.getElementById('app_name').value = 'Simple Jarvis UI';
                document.getElementById('theme').value = 'Dark';
                document.getElementById('auto_refresh').checked = false;
                document.getElementById('notifications').checked = false;
                
                alert('Settings reset to defaults.');
            }
        }
        
        function openDocs() {
            // In a real app, this would open documentation
            alert('Documentation would open here. Check the Jarvis UI Template System docs.');
        }
        
        // Simple routing for single-page app
        function navigateTo(page) {
            const content = document.querySelector('.content');
            
            switch(page) {
                case 'home':
                    content.innerHTML = getMainContent();
                    break;
                case 'settings':
                    content.innerHTML = getSettingsContent();
                    break;
                case 'about':
                    content.innerHTML = getAboutContent();
                    break;
            }
            
            // Update active nav link
            document.querySelectorAll('.nav-link').forEach(link => {
                link.classList.remove('active');
            });
            document.querySelector(`[data-page="${page}"]`).classList.add('active');
        }
        
        // Add click handlers to navigation
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.nav-link').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const page = this.getAttribute('data-page') || 'home';
                    navigateTo(page);
                });
            });
        });
        """


class SimpleJarvisApp(JarvisDesktopApp):
    """Desktop app wrapper for simple template."""
    
    def __init__(self, app_name: str = "Simple Jarvis UI", debug: bool = False):
        super().__init__(app_name, debug)
        self.ui = SimpleJarvisTemplate(app_name)
    
    def get_html_content(self) -> str:
        """Get the complete HTML for the simple app."""
        content = self.ui.get_main_content()
        return self.ui.get_html_template("Home", content)


# Example usage
if __name__ == "__main__":
    class MyCustomSimpleUI(SimpleJarvisTemplate):
        def get_main_content(self):
            return f"""
            <div class="welcome-section">
                <h2>My Custom Jarvis Interface</h2>
                <p>This is my personalized Jarvis UI built with the Simple Template.</p>
                
                {self.components.card("Quick Actions", '''
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                        <button class="btn btn-primary" onclick="quickAction1()">Action 1</button>
                        <button class="btn btn-secondary" onclick="quickAction2()">Action 2</button>
                        <button class="btn btn-secondary" onclick="quickAction3()">Action 3</button>
                    </div>
                ''')}
                
                {self.components.card("System Status", '''
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>Jarvis Core:</span>
                        <span class="status-indicator status-success">Online</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                        <span>Plugins:</span>
                        <span class="status-indicator status-success">8 Active</span>
                    </div>
                ''')}
            </div>
            """
    
    class MySimpleApp(SimpleJarvisApp):
        def __init__(self):
            super().__init__("My Custom UI")
            self.ui = MyCustomSimpleUI("My Custom UI")
    
    app = MySimpleApp()
    app.run()
