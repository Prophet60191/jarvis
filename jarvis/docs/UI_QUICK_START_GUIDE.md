# 🚀 Jarvis UI Quick Start Guide

Get up and running with custom Jarvis UIs in minutes using the template system.

## ⚡ 5-Minute Setup

### **Step 1: Choose Your Template**

```python
# For simple interfaces
from jarvis.ui.templates.simple_template import SimpleJarvisTemplate, SimpleJarvisApp

# For dashboards and monitoring
from jarvis.ui.templates.dashboard_template import JarvisDashboardTemplate, JarvisDashboardApp

# For full customization
from jarvis.ui.jarvis_ui_template import JarvisUITemplate, JarvisDesktopApp
```

### **Step 2: Create Your UI Class**

```python
class MyJarvisUI(SimpleJarvisTemplate):
    def __init__(self):
        super().__init__("My Jarvis UI", "1.0")
    
    def get_main_content(self):
        return f"""
        <h2>Welcome to My Custom Jarvis Interface!</h2>
        
        {self.components.card("Quick Status", '''
            <p>System is running smoothly</p>
            <div style="margin-top: 1rem;">
                <span class="status-indicator status-success">Online</span>
            </div>
        ''')}
        
        {self.components.card("Quick Actions", '''
            <div style="display: flex; gap: 1rem;">
                <button class="btn btn-primary" onclick="testVoice()">
                    🎤 Test Voice
                </button>
                <button class="btn btn-secondary" onclick="openSettings()">
                    ⚙️ Settings
                </button>
            </div>
        ''')}
        """
    
    def get_javascript(self):
        return super().get_javascript() + """
        function testVoice() {
            alert('Voice test would happen here!');
        }
        
        function openSettings() {
            alert('Settings would open here!');
        }
        """
```

### **Step 3: Create Desktop App**

```python
class MyJarvisApp(SimpleJarvisApp):
    def __init__(self):
        super().__init__("My Jarvis UI")
        self.ui = MyJarvisUI()
    
    def get_html_content(self):
        content = self.ui.get_main_content()
        return self.ui.get_html_template("Home", content)
```

### **Step 4: Run Your App**

```python
if __name__ == "__main__":
    app = MyJarvisApp()
    app.run(width=1200, height=800)
```

## 📋 Complete Example

Save this as `my_jarvis_ui.py`:

```python
#!/usr/bin/env python3
"""
My Custom Jarvis UI - Complete Example
"""

import sys
from pathlib import Path

# Add jarvis to path (adjust as needed)
sys.path.insert(0, str(Path(__file__).parent.parent))

from jarvis.ui.templates.simple_template import SimpleJarvisTemplate, SimpleJarvisApp


class MyJarvisUI(SimpleJarvisTemplate):
    def __init__(self):
        super().__init__("My Jarvis UI", "1.0")
    
    def get_navigation(self):
        return self.components.navigation_section("My App", [
            {"icon": "🏠", "label": "Home", "url": "/", "active": True},
            {"icon": "📊", "label": "Status", "url": "/status"},
            {"icon": "🔧", "label": "Tools", "url": "/tools"},
            {"icon": "⚙️", "label": "Settings", "url": "/settings"}
        ])
    
    def get_main_content(self):
        return f"""
        <div class="welcome-section">
            <h2>🎉 Welcome to My Jarvis Interface!</h2>
            <p>This is a custom UI built with the Jarvis Template System.</p>
            
            {self.components.card("System Overview", '''
                <div class="status-overview">
                    <div class="status-row">
                        <span>Jarvis Core:</span>
                        <span class="status-indicator status-success">Running</span>
                    </div>
                    <div class="status-row">
                        <span>Active Plugins:</span>
                        <span class="status-indicator status-success">8</span>
                    </div>
                    <div class="status-row">
                        <span>Memory Usage:</span>
                        <span class="status-indicator status-warning">2.1GB</span>
                    </div>
                </div>
            ''', [
                {"label": "Refresh", "action": "refreshStatus()", "style": "primary"},
                {"label": "Details", "action": "showDetails()", "style": "secondary"}
            ])}
            
            {self.components.card("Quick Actions", '''
                <div class="quick-actions">
                    <button class="action-button" onclick="quickAction('voice')">
                        <div class="action-icon">🎤</div>
                        <div class="action-text">Test Voice</div>
                    </button>
                    <button class="action-button" onclick="quickAction('memory')">
                        <div class="action-icon">🧠</div>
                        <div class="action-text">Check Memory</div>
                    </button>
                    <button class="action-button" onclick="quickAction('plugins')">
                        <div class="action-icon">🔌</div>
                        <div class="action-text">Manage Plugins</div>
                    </button>
                    <button class="action-button" onclick="quickAction('logs')">
                        <div class="action-icon">📋</div>
                        <div class="action-text">View Logs</div>
                    </button>
                </div>
            ''')}
            
            {self.components.card("Recent Activity", '''
                <div class="activity-feed">
                    <div class="activity-item">
                        <span class="activity-time">2 min ago</span>
                        <span class="activity-text">Voice command: "What time is it?"</span>
                    </div>
                    <div class="activity-item">
                        <span class="activity-time">5 min ago</span>
                        <span class="activity-text">Plugin loaded: device_time_tool</span>
                    </div>
                    <div class="activity-item">
                        <span class="activity-time">10 min ago</span>
                        <span class="activity-text">System started successfully</span>
                    </div>
                </div>
            ''')}
        </div>
        """
    
    def get_custom_css(self):
        return super().get_custom_css() + """
        .welcome-section {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .status-overview {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .status-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 4px;
        }
        
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
        }
        
        .action-button {
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
        
        .action-button:hover {
            background: rgba(100, 255, 218, 0.1);
            border-color: rgba(100, 255, 218, 0.2);
            transform: translateY(-2px);
        }
        
        .action-icon {
            font-size: 1.5em;
            margin-bottom: 0.5rem;
        }
        
        .action-text {
            font-size: 0.9em;
            font-weight: 500;
        }
        
        .activity-feed {
            max-height: 200px;
            overflow-y: auto;
        }
        
        .activity-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .activity-time {
            color: #8892b0;
            font-size: 0.8em;
            min-width: 80px;
        }
        
        .activity-text {
            flex: 1;
            margin-left: 1rem;
        }
        
        @media (max-width: 768px) {
            .quick-actions {
                grid-template-columns: 1fr;
            }
            
            .activity-item {
                flex-direction: column;
                align-items: flex-start;
                gap: 0.25rem;
            }
            
            .activity-text {
                margin-left: 0;
            }
        }
        """
    
    def get_javascript(self):
        return super().get_javascript() + """
        function refreshStatus() {
            // Simulate status refresh
            console.log('Refreshing system status...');
            alert('Status refreshed! (In a real app, this would update the display)');
        }
        
        function showDetails() {
            alert('Detailed system information would be displayed here.');
        }
        
        function quickAction(action) {
            switch(action) {
                case 'voice':
                    alert('🎤 Voice Test: "Hey Jarvis, what time is it?"');
                    break;
                case 'memory':
                    alert('🧠 Memory Status: 2.1GB used, 1.9GB available');
                    break;
                case 'plugins':
                    alert('🔌 Plugin Manager would open here');
                    break;
                case 'logs':
                    alert('📋 System logs would be displayed here');
                    break;
                default:
                    alert('Action not implemented: ' + action);
            }
        }
        """


class MyJarvisApp(SimpleJarvisApp):
    def __init__(self):
        super().__init__("My Custom Jarvis UI")
        self.ui = MyJarvisUI()
    
    def get_html_content(self):
        content = self.ui.get_main_content()
        return self.ui.get_html_template("Home", content)


if __name__ == "__main__":
    print("🚀 Starting My Custom Jarvis UI...")
    print("Close the window or press Ctrl+C to exit.")

    app = MyJarvisApp()
    app.run(width=1200, height=800)
```

## 🎤 Adding Voice Commands

To enable "Hey Jarvis, open my app" and "close my app" commands, create a plugin:

### **Create Voice Command Plugin**

Save as `jarvis/jarvis/tools/plugins/my_ui_tool.py`:

```python
#!/usr/bin/env python3
"""Voice commands for My Custom UI"""

import logging
from langchain.tools import tool
from jarvis.utils.app_manager import get_app_manager

logger = logging.getLogger(__name__)

@tool
def open_my_ui(panel: str = "main") -> str:
    """Open My Custom UI when user says 'open my app' or similar."""
    try:
        app_manager = get_app_manager()
        if app_manager and app_manager.start_app("my_ui"):
            return "My Custom UI is now open."
        else:
            return "Error opening My Custom UI."
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def close_my_ui() -> str:
    """Close My Custom UI when user says 'close my app'."""
    try:
        app_manager = get_app_manager()
        if app_manager and app_manager.stop_app("my_ui"):
            return "My Custom UI has been closed."
        else:
            return "My Custom UI was not running."
    except Exception as e:
        return f"Error: {str(e)}"
```

### **Register Your App**

Add to your main app file:

```python
from jarvis.utils.app_manager import get_app_manager

class MyJarvisApp(SimpleJarvisApp):
    def __init__(self):
        super().__init__("My Custom UI")
        self.register_app()

    def register_app(self):
        """Register with Jarvis for voice commands."""
        try:
            app_manager = get_app_manager()
            if app_manager:
                app_manager.register_app(
                    name="my_ui",
                    script_path=__file__,
                    description="My Custom Jarvis UI"
                )
                print("✅ Registered for voice commands")
        except Exception as e:
            print(f"⚠️  Registration failed: {e}")
```

### **Test Voice Commands**

1. Start Jarvis: `python start_jarvis.py`
2. Say: **"Hey Jarvis, open my app"**
3. Your UI should open!
4. Say: **"Hey Jarvis, close my app"**
5. Your UI should close!
```

## 🎯 Next Steps

### **1. Customize Your UI**
- Modify colors in `get_custom_css()`
- Add your own components
- Implement real Jarvis API calls

### **2. Add More Pages**
- Create methods for different pages
- Implement navigation between pages
- Add forms and interactive elements

### **3. Add Voice Commands**
- Create plugin for "open my app" / "close my app" commands
- Register with Jarvis application manager
- Test voice integration

### **4. Integrate with Jarvis**
- Connect to Jarvis APIs
- Add real-time updates
- Implement advanced features

### **4. Deploy Your UI**
- Package as standalone app
- Add to Jarvis plugin system
- Share with the community

## 📚 Resources

- **[Full UI Template Documentation](UI_TEMPLATE_SYSTEM.md)**
- **[Plugin Reference Guide](../PLUGIN_REFERENCE_GUIDE.md)**
- **[API Documentation](API_DOCUMENTATION.md)**
- **[Example UIs](../../examples/)**

## 🆘 Getting Help

1. **Check Examples**: Look at `examples/custom_ui_example.py`
2. **Review Templates**: Study existing templates in `jarvis/ui/templates/`
3. **Read Documentation**: Full guides in `jarvis/docs/`
4. **Ask Questions**: Create GitHub issues for help

---

**Ready to build?** Copy the complete example above, save it as `my_jarvis_ui.py`, and run it to see your custom Jarvis interface in action! 🎉
