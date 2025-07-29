#!/usr/bin/env python3
"""
Voice-Controlled UI Example

Complete example showing how to create a custom Jarvis UI with voice commands.
This demonstrates:
1. Custom UI using template system
2. Voice command plugin creation
3. Application manager integration
4. Complete voice control workflow

Usage:
    1. Run this file to start the UI
    2. Start Jarvis: python start_jarvis.py
    3. Say: "Hey Jarvis, open my demo app"
    4. Say: "Hey Jarvis, close my demo app"
"""

import sys
import os
import logging
from pathlib import Path

# Add the jarvis package to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from jarvis.ui.templates.simple_template import SimpleJarvisTemplate, SimpleJarvisApp
from jarvis.utils.app_manager import get_app_manager

logger = logging.getLogger(__name__)


class VoiceControlledUI(SimpleJarvisTemplate):
    """Example UI that can be controlled by voice commands."""
    
    def __init__(self):
        super().__init__("Voice Demo App", "1.0")
    
    def get_navigation(self):
        """Custom navigation for the demo app."""
        return f"""
        {self.components.navigation_section("Demo App", [
            {"icon": "🏠", "label": "Home", "url": "/", "active": True},
            {"icon": "🎤", "label": "Voice Test", "url": "/voice"},
            {"icon": "📊", "label": "Status", "url": "/status"},
            {"icon": "⚙️", "label": "Settings", "url": "/settings"}
        ])}
        
        {self.components.navigation_section("Voice Commands", [
            {"icon": "🔊", "label": "Open Commands", "url": "#open"},
            {"icon": "🔇", "label": "Close Commands", "url": "#close"},
            {"icon": "❓", "label": "Help", "url": "/help"}
        ])}
        """
    
    def get_main_content(self):
        """Main page content with voice command information."""
        return f"""
        <div class="demo-container">
            <div class="hero-section">
                <h1>🎤 Voice-Controlled Demo App</h1>
                <p>This app demonstrates voice command integration with Jarvis</p>
            </div>
            
            {self.components.card("Voice Commands", '''
                <div class="voice-commands">
                    <div class="command-section">
                        <h4>🔊 Opening Commands</h4>
                        <ul class="command-list">
                            <li>"Hey Jarvis, open my demo app"</li>
                            <li>"Jarvis, show my demo app"</li>
                            <li>"Open the demo application"</li>
                            <li>"Launch my demo app"</li>
                        </ul>
                    </div>
                    
                    <div class="command-section">
                        <h4>🔇 Closing Commands</h4>
                        <ul class="command-list">
                            <li>"Hey Jarvis, close my demo app"</li>
                            <li>"Jarvis, close the demo app"</li>
                            <li>"Shut down my demo app"</li>
                            <li>"Close demo application"</li>
                        </ul>
                    </div>
                </div>
            ''', [
                {"label": "Test Voice", "action": "testVoiceCommand()", "style": "primary"},
                {"label": "Show Help", "action": "showVoiceHelp()", "style": "secondary"}
            ])}
            
            {self.components.card("App Status", '''
                <div class="status-display">
                    <div class="status-item">
                        <span class="status-label">Application:</span>
                        <span class="status-indicator status-success">Running</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Voice Commands:</span>
                        <span class="status-indicator status-success">Active</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">App Manager:</span>
                        <span class="status-indicator status-success">Registered</span>
                    </div>
                </div>
            ''', [
                {"label": "Refresh Status", "action": "refreshStatus()", "style": "secondary"}
            ])}
            
            {self.components.card("How It Works", '''
                <div class="how-it-works">
                    <div class="step">
                        <div class="step-number">1</div>
                        <div class="step-content">
                            <h5>Plugin Creation</h5>
                            <p>Voice command plugin created in <code>jarvis/tools/plugins/</code></p>
                        </div>
                    </div>
                    
                    <div class="step">
                        <div class="step-number">2</div>
                        <div class="step-content">
                            <h5>App Registration</h5>
                            <p>App registered with Jarvis Application Manager</p>
                        </div>
                    </div>
                    
                    <div class="step">
                        <div class="step-number">3</div>
                        <div class="step-content">
                            <h5>Voice Recognition</h5>
                            <p>Jarvis recognizes voice commands and calls plugin tools</p>
                        </div>
                    </div>
                    
                    <div class="step">
                        <div class="step-number">4</div>
                        <div class="step-content">
                            <h5>App Control</h5>
                            <p>Application Manager starts/stops the UI application</p>
                        </div>
                    </div>
                </div>
            ''')}
        </div>
        """
    
    def get_custom_css(self):
        """Custom CSS for the demo app."""
        return super().get_custom_css() + """
        .demo-container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .hero-section {
            text-align: center;
            margin-bottom: 2rem;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(100, 255, 218, 0.1) 0%, rgba(100, 149, 237, 0.1) 100%);
            border-radius: 12px;
            border: 1px solid rgba(100, 255, 218, 0.2);
        }
        
        .hero-section h1 {
            margin-bottom: 0.5rem;
            color: #64ffda;
        }
        
        .voice-commands {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }
        
        .command-section h4 {
            color: #64ffda;
            margin-bottom: 1rem;
        }
        
        .command-list {
            list-style: none;
            padding: 0;
        }
        
        .command-list li {
            padding: 0.5rem;
            margin: 0.25rem 0;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 4px;
            border-left: 3px solid #64ffda;
            font-family: Monaco, "Cascadia Code", monospace;
            font-size: 0.9em;
        }
        
        .status-display {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        
        .status-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 6px;
        }
        
        .status-label {
            font-weight: 500;
        }
        
        .how-it-works {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        
        .step {
            display: flex;
            align-items: flex-start;
            gap: 1rem;
        }
        
        .step-number {
            width: 32px;
            height: 32px;
            background: #64ffda;
            color: #0f0f23;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            flex-shrink: 0;
        }
        
        .step-content h5 {
            margin: 0 0 0.5rem 0;
            color: #ffffff;
        }
        
        .step-content p {
            margin: 0;
            color: #b8c5d1;
            line-height: 1.5;
        }
        
        .step-content code {
            background: rgba(255, 255, 255, 0.1);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: Monaco, "Cascadia Code", monospace;
            font-size: 0.85em;
        }
        
        @media (max-width: 768px) {
            .voice-commands {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
        }
        """
    
    def get_javascript(self):
        """Custom JavaScript for the demo app."""
        return super().get_javascript() + """
        function testVoiceCommand() {
            alert('🎤 Voice Command Test\\n\\nTry saying:\\n"Hey Jarvis, close my demo app"\\n\\nThen say:\\n"Hey Jarvis, open my demo app"\\n\\nto test the voice commands!');
        }
        
        function showVoiceHelp() {
            alert('🆘 Voice Command Help\\n\\n1. Make sure Jarvis is running\\n2. Say the wake word "Hey Jarvis"\\n3. Wait for acknowledgment\\n4. Give your command clearly\\n\\nExample: "Hey Jarvis, open my demo app"');
        }
        
        function refreshStatus() {
            // Simulate status refresh
            console.log('Refreshing app status...');
            
            // Update status indicators (in a real app, this would check actual status)
            const indicators = document.querySelectorAll('.status-indicator');
            indicators.forEach(indicator => {
                indicator.textContent = 'Active';
                indicator.className = 'status-indicator status-success';
            });
            
            alert('✅ Status refreshed! All systems operational.');
        }
        """


class VoiceControlledApp(SimpleJarvisApp):
    """Desktop app wrapper with voice command integration."""
    
    def __init__(self):
        super().__init__("Voice Demo App")
        self.ui = VoiceControlledUI()
        self.register_with_app_manager()
    
    def register_with_app_manager(self):
        """Register this app with Jarvis application manager for voice commands."""
        try:
            app_manager = get_app_manager()
            if app_manager:
                # Register the app with a unique name
                app_manager.register_app(
                    name="voice_demo_app",
                    script_path=str(Path(__file__).absolute()),  # Ensure absolute path
                    description="Voice-Controlled Demo UI Application"
                )
                print("✅ Successfully registered with Jarvis Application Manager")
                print(f"📁 Script path: {Path(__file__).absolute()}")
                print("🎤 Voice commands are now available:")
                print("   - 'Hey Jarvis, open my demo app'")
                print("   - 'Hey Jarvis, close my demo app'")

                # Debug: Check if registration worked
                status = app_manager.get_app_status("voice_demo_app")
                print(f"🔍 Registration status: {status}")
            else:
                print("⚠️  Application Manager not available")
                print("   Voice commands may not work properly")
        except Exception as e:
            print(f"❌ Failed to register with Application Manager: {e}")
            print(f"   Error details: {type(e).__name__}: {str(e)}")
            print("   Voice commands will not be available")
    
    def get_html_content(self):
        """Get the complete HTML for the voice-controlled app."""
        content = self.ui.get_main_content()
        return self.ui.get_html_template("Voice Demo", content)


if __name__ == "__main__":
    print("🚀 Starting Voice-Controlled Demo App...")
    print("=" * 60)
    print("This app demonstrates voice command integration with Jarvis.")
    print()
    print("📋 Setup Instructions:")
    print("1. This app will register itself for voice commands")
    print("2. Start Jarvis in another terminal: python start_jarvis.py")
    print("3. Test voice commands:")
    print("   - 'Hey Jarvis, open my demo app'")
    print("   - 'Hey Jarvis, close my demo app'")
    print()
    print("🔧 For this to work, you need to create the voice command plugin.")
    print("   See the documentation for complete setup instructions.")
    print()
    print("Close the window or press Ctrl+C to exit.")
    print("=" * 60)
    
    app = VoiceControlledApp()
    app.run(width=1200, height=900)
