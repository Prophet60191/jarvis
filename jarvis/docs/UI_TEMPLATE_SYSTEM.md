# 🎨 Jarvis UI Template System

Complete guide for creating custom Jarvis UIs using the standardized template system.

## 🎯 Overview

The Jarvis UI Template System provides a standardized, reusable framework for creating custom user interfaces that integrate seamlessly with Jarvis. Based on analysis of existing UIs (Settings Panel, RAG Vault, Web Interface), this system ensures consistency, maintainability, and rapid development.

### **Key Benefits**
- **Consistent Design Language**: All UIs share the same visual identity
- **Rapid Development**: Pre-built components and templates
- **Responsive Design**: Works across desktop, tablet, and mobile
- **Easy Integration**: Built-in Jarvis API connectivity
- **Modular Architecture**: Reusable components and patterns

## 🏗️ Architecture Analysis

### **Existing UI Patterns Identified**

#### **1. Web Interface Pattern** (`jarvis/ui/jarvis_ui.py`)
- **Framework**: Pure Python HTTP server with embedded HTML/CSS/JS
- **Structure**: Single-file application with template method
- **Styling**: Embedded CSS with dark theme and glassmorphism
- **Navigation**: Fixed sidebar with section-based navigation
- **API**: RESTful endpoints for configuration and status

#### **2. Desktop App Pattern** (`rag_app.py`, `jarvis_settings_app.py`)
- **Framework**: PyWebView for native desktop windows
- **Structure**: Python backend with HTML frontend
- **Integration**: Direct API calls to Jarvis components
- **Lifecycle**: Proper startup/shutdown with signal handling
- **Panels**: Multi-panel support with URL-based routing

#### **3. Common Design Elements**
- **Color Scheme**: Dark gradient background (#0f0f23 → #1a1a2e → #16213e)
- **Typography**: System fonts (-apple-system, BlinkMacSystemFont, 'Segoe UI')
- **Layout**: Sidebar + main content area
- **Components**: Cards, buttons, forms, status indicators
- **Effects**: Backdrop blur, glassmorphism, smooth transitions

## 🎨 Template System Components

### **1. Base Template Structure**

```python
class JarvisUITemplate:
    """Base template for all Jarvis UIs."""
    
    def __init__(self, app_name: str, version: str = "1.0"):
        self.app_name = app_name
        self.version = version
        self.theme = JarvisTheme()
        self.components = JarvisComponents()
    
    def get_html_template(self, title: str, content: str) -> str:
        """Generate complete HTML page with Jarvis styling."""
        return self.theme.wrap_content(title, content, self.get_navigation())
    
    def get_navigation(self) -> str:
        """Override to provide custom navigation."""
        return ""
```

### **2. Theme System**

```python
class JarvisTheme:
    """Standardized Jarvis theme and styling."""
    
    # Color Palette
    COLORS = {
        'primary': '#64ffda',      # Jarvis cyan
        'secondary': '#6495ed',    # Jarvis blue
        'background': 'linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)',
        'surface': 'rgba(255, 255, 255, 0.05)',
        'text_primary': '#e0e6ed',
        'text_secondary': '#b8c5d1',
        'accent': '#8892b0',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'error': '#f44336'
    }
    
    # Typography
    FONTS = {
        'primary': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        'mono': 'Monaco, "Cascadia Code", "Roboto Mono", monospace'
    }
```

### **3. Component Library**

```python
class JarvisComponents:
    """Reusable UI components for Jarvis interfaces."""
    
    def card(self, title: str, content: str, actions: str = "") -> str:
        """Standard Jarvis card component."""
        
    def button(self, text: str, action: str, style: str = "primary") -> str:
        """Standard Jarvis button component."""
        
    def form_field(self, label: str, field_type: str, name: str, **kwargs) -> str:
        """Standard form field component."""
        
    def status_indicator(self, status: str, label: str) -> str:
        """Status indicator component."""
        
    def navigation_section(self, title: str, links: list) -> str:
        """Navigation section component."""
```

## 🚀 Quick Start Guide

### **1. Basic UI Application**

```python
#!/usr/bin/env python3
"""
My Custom Jarvis UI
"""

import sys
import os
from pathlib import Path

# Add Jarvis UI templates to path
sys.path.insert(0, str(Path(__file__).parent / "jarvis" / "ui"))

from jarvis_ui_template import JarvisUITemplate, JarvisDesktopApp

class MyCustomUI(JarvisUITemplate):
    """Custom UI for my specific use case."""
    
    def __init__(self):
        super().__init__("My Custom UI", "1.0")
    
    def get_navigation(self) -> str:
        """Custom navigation for my UI."""
        return self.components.navigation_section("My Tools", [
            {"icon": "🏠", "label": "Dashboard", "url": "/"},
            {"icon": "⚙️", "label": "Settings", "url": "/settings"},
            {"icon": "📊", "label": "Analytics", "url": "/analytics"}
        ])
    
    def get_dashboard_content(self) -> str:
        """Dashboard page content."""
        return self.components.card(
            "Welcome", 
            "This is my custom Jarvis UI dashboard.",
            self.components.button("Get Started", "showWelcome()")
        )

class MyCustomApp(JarvisDesktopApp):
    """Desktop app wrapper for my custom UI."""
    
    def __init__(self):
        super().__init__("My Custom UI")
        self.ui = MyCustomUI()
    
    def get_html_content(self) -> str:
        """Get the complete HTML for the app."""
        content = self.ui.get_dashboard_content()
        return self.ui.get_html_template("My Custom UI", content)

if __name__ == "__main__":
    app = MyCustomApp()
    app.run()
```

### **2. Web Interface Application**

```python
#!/usr/bin/env python3
"""
My Custom Web Interface
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from jarvis_ui_template import JarvisUITemplate
import json

class MyWebHandler(BaseHTTPRequestHandler):
    """HTTP handler for my custom web interface."""
    
    def __init__(self, *args, **kwargs):
        self.ui = JarvisUITemplate("My Web UI")
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/":
            self.serve_main_page()
        elif self.path == "/api/status":
            self.serve_api_status()
        else:
            self.serve_404()
    
    def serve_main_page(self):
        """Serve the main page."""
        content = self.get_main_content()
        html = self.ui.get_html_template("My Web UI", content)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def get_main_content(self) -> str:
        """Get main page content."""
        return """
        <div class="main-header">
            <h1>My Custom Web Interface</h1>
            <p>Built with Jarvis UI Template System</p>
        </div>
        
        <div class="content-grid">
            <div class="card">
                <h3>Feature 1</h3>
                <p>Description of my custom feature.</p>
                <button class="btn btn-primary" onclick="feature1()">Use Feature</button>
            </div>
            
            <div class="card">
                <h3>Feature 2</h3>
                <p>Another custom feature description.</p>
                <button class="btn btn-secondary" onclick="feature2()">Configure</button>
            </div>
        </div>
        """

def run_server(port: int = 8090):
    """Run the web server."""
    server = HTTPServer(('localhost', port), MyWebHandler)
    print(f"🌐 My Web UI running at http://localhost:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
```

## 📱 Template Types

### **1. Desktop Application Template**

**Use Case**: Native desktop apps with pywebview
**Features**: 
- Native window management
- System integration
- Offline operation
- File system access

**Template**: `JarvisDesktopAppTemplate`

### **2. Web Interface Template**

**Use Case**: Browser-based interfaces
**Features**:
- HTTP server integration
- RESTful API endpoints
- Real-time updates
- Cross-platform access

**Template**: `JarvisWebInterfaceTemplate`

### **3. Panel Template**

**Use Case**: Multi-panel applications
**Features**:
- Tab-based navigation
- Panel switching
- State management
- URL routing

**Template**: `JarvisPanelTemplate`

### **4. Dashboard Template**

**Use Case**: Monitoring and status interfaces
**Features**:
- Real-time data display
- Chart integration
- Status indicators
- Auto-refresh

**Template**: `JarvisDashboardTemplate`

## 🎨 Styling Guidelines

### **Color Usage**

```css
/* Primary Actions */
.btn-primary { background: #64ffda; }

/* Secondary Actions */
.btn-secondary { background: #6495ed; }

/* Success States */
.status-success { color: #4CAF50; }

/* Warning States */
.status-warning { color: #FF9800; }

/* Error States */
.status-error { color: #f44336; }
```

### **Typography Scale**

```css
/* Headings */
h1 { font-size: 1.8em; font-weight: 600; }
h2 { font-size: 1.5em; font-weight: 600; }
h3 { font-size: 1.3em; font-weight: 500; }
h4 { font-size: 1.1em; font-weight: 500; }

/* Body Text */
body { font-size: 14px; line-height: 1.6; }
.small { font-size: 12px; }
.large { font-size: 16px; }
```

### **Spacing System**

```css
/* Margins and Padding */
.m-1 { margin: 8px; }
.m-2 { margin: 16px; }
.m-3 { margin: 24px; }
.m-4 { margin: 32px; }

.p-1 { padding: 8px; }
.p-2 { padding: 16px; }
.p-3 { padding: 24px; }
.p-4 { padding: 32px; }
```

## 🔧 Component Reference

### **Navigation Components**

```python
# Sidebar Navigation
navigation = components.sidebar_navigation([
    {"section": "Main", "links": [
        {"icon": "🏠", "label": "Dashboard", "url": "/"},
        {"icon": "📊", "label": "Status", "url": "/status"}
    ]},
    {"section": "Tools", "links": [
        {"icon": "⚙️", "label": "Settings", "url": "/settings"},
        {"icon": "🔧", "label": "Tools", "url": "/tools"}
    ]}
])

# Tab Navigation
tabs = components.tab_navigation([
    {"id": "overview", "label": "Overview", "active": True},
    {"id": "details", "label": "Details", "active": False},
    {"id": "settings", "label": "Settings", "active": False}
])
```

### **Content Components**

```python
# Cards
card = components.card(
    title="System Status",
    content="All systems operational",
    actions=[
        {"label": "Refresh", "action": "refresh()", "style": "primary"},
        {"label": "Details", "action": "showDetails()", "style": "secondary"}
    ]
)

# Forms
form = components.form([
    {"type": "text", "name": "username", "label": "Username", "required": True},
    {"type": "password", "name": "password", "label": "Password", "required": True},
    {"type": "select", "name": "role", "label": "Role", "options": ["Admin", "User"]},
    {"type": "checkbox", "name": "remember", "label": "Remember me"}
])

# Status Indicators
status = components.status_grid([
    {"label": "System", "status": "online", "value": "Operational"},
    {"label": "Memory", "status": "warning", "value": "75% Used"},
    {"label": "Storage", "status": "success", "value": "45% Used"}
])
```

### **Interactive Components**

```python
# Buttons
buttons = [
    components.button("Primary Action", "primaryAction()", "primary"),
    components.button("Secondary", "secondaryAction()", "secondary"),
    components.button("Danger", "dangerAction()", "danger")
]

# Modals
modal = components.modal(
    id="confirm-modal",
    title="Confirm Action",
    content="Are you sure you want to proceed?",
    actions=[
        {"label": "Cancel", "action": "closeModal()", "style": "secondary"},
        {"label": "Confirm", "action": "confirmAction()", "style": "primary"}
    ]
)
```

## 🔌 API Integration

### **Jarvis API Client**

```python
class JarvisAPIClient:
    """Client for connecting to Jarvis APIs."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
    
    async def get_status(self) -> dict:
        """Get system status."""
        
    async def get_config(self, section: str = None) -> dict:
        """Get configuration."""
        
    async def update_config(self, section: str, data: dict) -> dict:
        """Update configuration."""
        
    async def call_tool(self, tool_name: str, **kwargs) -> dict:
        """Call a Jarvis tool."""
```

### **Real-time Updates**

```javascript
// WebSocket connection for real-time updates
class JarvisWebSocket {
    constructor(url) {
        this.url = url;
        this.connect();
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleUpdate(data);
        };
    }
    
    handleUpdate(data) {
        // Update UI based on real-time data
        if (data.type === 'status_update') {
            updateStatusDisplay(data.status);
        }
    }
}
```

## 🚀 Template Examples

### **1. Simple UI Template**

```python
from jarvis.ui.templates.simple_template import SimpleJarvisTemplate

class MySimpleUI(SimpleJarvisTemplate):
    def get_main_content(self):
        return f"""
        <h2>Welcome to My Custom UI</h2>
        {self.components.card("Status", "System is running normally")}
        {self.components.card("Actions", '''
            <button class="btn btn-primary" onclick="doSomething()">
                Primary Action
            </button>
        ''')}
        """
```

### **2. Dashboard Template**

```python
from jarvis.ui.templates.dashboard_template import JarvisDashboardTemplate

class MyDashboard(JarvisDashboardTemplate):
    def get_dashboard_widgets(self):
        return [
            self.create_status_widget("System", "online", "success"),
            self.create_metric_widget("Users", "42", "👥"),
            self.create_chart_widget("Performance", [85, 90, 88, 92])
        ]
```

## 📁 File Structure

```
jarvis/ui/
├── jarvis_ui_template.py      # Base template system
├── templates/
│   ├── __init__.py
│   ├── simple_template.py     # Simple UI template
│   └── dashboard_template.py  # Dashboard template
└── components/                # Reusable components (future)

examples/
├── custom_ui_example.py       # Complete example
├── simple_ui_example.py       # Basic example
└── dashboard_example.py       # Dashboard example
```

## 🎯 Best Practices

### **Template Selection**
- **Simple Template**: Basic interfaces, settings panels, about pages
- **Dashboard Template**: Monitoring interfaces, status displays, metrics
- **Custom Template**: Specialized workflows, unique requirements

### **Component Usage**
- Use `components.card()` for content sections
- Use `components.button()` for consistent actions
- Use `components.form_field()` for user input
- Use `components.status_indicator()` for system status

### **Styling Guidelines**
- Follow the Jarvis color palette
- Use consistent spacing (theme.SPACING)
- Implement responsive design patterns
- Maintain accessibility standards

### **JavaScript Integration**
- Keep JavaScript simple and focused
- Use modern ES6+ features
- Implement proper error handling
- Follow the template's JavaScript patterns

## 🔧 Advanced Customization

### **Custom Themes**

```python
class MyCustomTheme(JarvisTheme):
    COLORS = {
        **JarvisTheme.COLORS,
        'primary': '#ff6b6b',      # Custom primary color
        'secondary': '#4ecdc4',    # Custom secondary color
    }

class MyUI(JarvisUITemplate):
    def __init__(self):
        super().__init__("My UI")
        self.theme = MyCustomTheme()
        self.components = JarvisComponents(self.theme)
```

### **Custom Components**

```python
class MyComponents(JarvisComponents):
    def custom_widget(self, title: str, data: dict) -> str:
        return f"""
        <div class="custom-widget">
            <h3>{title}</h3>
            <div class="widget-data">
                {self._render_data(data)}
            </div>
        </div>
        """

    def _render_data(self, data: dict) -> str:
        # Custom data rendering logic
        return "".join([f"<p>{k}: {v}</p>" for k, v in data.items()])
```

## 📱 Responsive Design

All templates include responsive design patterns:

```css
/* Mobile-first approach */
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
    }

    .main-content {
        margin-left: 0;
    }

    .content-grid {
        grid-template-columns: 1fr;
    }
}
```

## 🔌 Jarvis Integration

### **API Connectivity**

```python
class JarvisIntegratedUI(JarvisUITemplate):
    def __init__(self):
        super().__init__("Integrated UI")
        self.api_client = JarvisAPIClient()

    async def get_system_status(self):
        return await self.api_client.get_status()

    async def call_jarvis_tool(self, tool_name: str, **kwargs):
        return await self.api_client.call_tool(tool_name, **kwargs)
```

### **Real-time Updates**

```javascript
// WebSocket integration for live updates
const ws = new JarvisWebSocket('ws://localhost:8080/ws');
ws.onUpdate = (data) => {
    updateUIElements(data);
};
```

## 🧪 Testing Templates

### **Template Testing**

```python
import unittest
from jarvis.ui.templates.simple_template import SimpleJarvisTemplate

class TestSimpleTemplate(unittest.TestCase):
    def setUp(self):
        self.template = SimpleJarvisTemplate("Test UI")

    def test_navigation_generation(self):
        nav = self.template.get_navigation()
        self.assertIn("Home", nav)
        self.assertIn("Settings", nav)

    def test_main_content(self):
        content = self.template.get_main_content()
        self.assertIn("Welcome", content)
```

## 📚 Migration Guide

### **From Existing UIs**

1. **Identify UI Pattern**: Determine which template fits your existing UI
2. **Extract Components**: Move reusable elements to template methods
3. **Update Styling**: Migrate to template CSS classes
4. **Test Functionality**: Ensure all features work with new template

### **Template Upgrade Path**

1. **Start Simple**: Begin with SimpleJarvisTemplate
2. **Add Features**: Gradually incorporate more components
3. **Custom Template**: Create specialized template when needed
4. **Share Templates**: Contribute useful templates back to the system

## 🎤 Voice Command Integration

### **Setting Up Voice Commands for Your UI**

To enable voice commands like "open my app" and "close my app", you need to create a plugin tool that integrates with Jarvis's application manager.

#### **Step 1: Create a UI Control Plugin**

Create a file `jarvis/jarvis/tools/plugins/my_app_tool.py`:

```python
#!/usr/bin/env python3
"""
My App UI Control Plugin

Voice commands to open and close your custom UI application.
"""

import logging
from langchain.tools import tool
from jarvis.utils.app_manager import get_app_manager

logger = logging.getLogger(__name__)

@tool
def open_my_app(panel: str = "main") -> str:
    """
    Open My Custom App when user asks to "open my app", "show my app", or similar requests.

    Use this tool when the user wants to:
    - Open your custom application
    - Access specific panels or sections
    - Launch your UI interface

    Args:
        panel: Which panel to open. Options: 'main', 'dashboard', 'settings', etc.
    """
    try:
        logger.info(f"Opening My App with panel: {panel}")

        # Get the application manager
        app_manager = get_app_manager()

        if app_manager:
            # Use the robust application manager
            app_name = "my_app"  # Must match registration name

            if app_manager.start_app(app_name):
                panel_names = {
                    "main": "Main Interface",
                    "dashboard": "Dashboard",
                    "settings": "Settings Panel",
                    "tools": "Tools Panel"
                }

                panel_name = panel_names.get(panel, f"'{panel}' panel")
                return f"My Custom App ({panel_name}) is now open in the desktop app."
            else:
                return "I encountered an error while trying to open My App. Please try again."
        else:
            return "Application manager not available. Please check your Jarvis configuration."

    except Exception as e:
        logger.error(f"Error opening My App: {e}")
        return f"I encountered an error while trying to open My App: {str(e)}"

@tool
def close_my_app() -> str:
    """
    Close My Custom App when user asks to "close my app".

    This will gracefully shut down your custom UI application.

    Returns:
        Status message about closing the app
    """
    try:
        logger.info("Attempting to close My App")

        # Get the application manager
        app_manager = get_app_manager()

        if app_manager:
            app_name = "my_app"  # Must match registration name

            if app_manager.is_app_running(app_name):
                if app_manager.stop_app(app_name):
                    return "I've successfully closed My Custom App."
                else:
                    return "I encountered an error while trying to close My App. Please try closing it manually."
            else:
                return "My App doesn't appear to be running, or it's already closed."
        else:
            return "Application manager not available. Cannot close app automatically."

    except Exception as e:
        logger.error(f"Error closing My App: {e}")
        return f"I encountered an error while trying to close My App: {str(e)}"
```

#### **Step 2: Register Your App with the Application Manager**

In your main app file, register with the application manager:

```python
#!/usr/bin/env python3
"""
My Custom App - Main Entry Point
"""

import sys
import os
from pathlib import Path

# Add jarvis to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from jarvis.ui.templates.simple_template import SimpleJarvisApp
from jarvis.utils.app_manager import get_app_manager

class MyCustomApp(SimpleJarvisApp):
    def __init__(self):
        super().__init__("My Custom App")
        # Register with application manager
        self.register_with_app_manager()

    def register_with_app_manager(self):
        """Register this app with Jarvis application manager."""
        try:
            app_manager = get_app_manager()
            if app_manager:
                # Register the app
                app_manager.register_app(
                    name="my_app",
                    script_path=__file__,
                    description="My Custom Jarvis UI Application"
                )
                print("✅ Registered with Jarvis Application Manager")
            else:
                print("⚠️  Application Manager not available")
        except Exception as e:
            print(f"❌ Failed to register with Application Manager: {e}")

if __name__ == "__main__":
    app = MyCustomApp()
    app.run()
```

#### **Step 3: Voice Command Examples**

Once your plugin is created and your app is registered, users can use these voice commands:

**Opening Commands**:
```
"Hey Jarvis, open my app"
"Jarvis, show my app"
"Open my custom app"
"Launch my app dashboard"
"Open my app settings"
```

**Closing Commands**:
```
"Hey Jarvis, close my app"
"Jarvis, close my custom app"
"Shut down my app"
```

### **Advanced Voice Command Features**

#### **Panel-Specific Commands**

You can create more specific voice commands for different panels:

```python
@tool
def open_my_app_dashboard() -> str:
    """Open My App dashboard specifically."""
    return open_my_app("dashboard")

@tool
def open_my_app_settings() -> str:
    """Open My App settings panel specifically."""
    return open_my_app("settings")
```

This enables commands like:
- "Open my app dashboard"
- "Show my app settings"

#### **Status Checking**

Add a status check tool:

```python
@tool
def check_my_app_status() -> str:
    """Check if My App is currently running."""
    try:
        app_manager = get_app_manager()
        if app_manager and app_manager.is_app_running("my_app"):
            return "My Custom App is currently running."
        else:
            return "My Custom App is not currently running."
    except Exception as e:
        return f"Unable to check app status: {str(e)}"
```

### **Voice Command Best Practices**

#### **1. Clear Tool Descriptions**
- Use descriptive docstrings that explain when to use the tool
- Include example phrases users might say
- Specify the tool's purpose and scope

#### **2. Error Handling**
- Always include try/catch blocks
- Provide helpful error messages
- Log errors for debugging

#### **3. Consistent Naming**
- Use consistent app names across all tools
- Match registration names exactly
- Use clear, memorable command phrases

#### **4. User Feedback**
- Provide clear success/failure messages
- Include specific panel names in responses
- Give helpful guidance when things go wrong

### **Testing Voice Commands**

#### **Direct Testing**

```python
# Test your voice command tools directly
from jarvis.tools.plugins.my_app_tool import open_my_app, close_my_app

# Test opening
result = open_my_app.invoke({"panel": "main"})
print(f"Open result: {result}")

# Test closing
result = close_my_app.invoke({})
print(f"Close result: {result}")
```

#### **Voice Testing**

1. Start Jarvis: `python start_jarvis.py`
2. Say: "Hey Jarvis, open my app"
3. Verify the app opens
4. Say: "Hey Jarvis, close my app"
5. Verify the app closes

### **Integration with Existing Patterns**

Your voice commands will work alongside existing Jarvis UI commands:

**Existing Commands**:
- "Open settings" → Opens Jarvis settings
- "Open vault" → Opens RAG knowledge vault
- "Close settings" → Closes Jarvis settings
- "Close vault" → Closes knowledge vault

**Your Commands**:
- "Open my app" → Opens your custom UI
- "Close my app" → Closes your custom UI

This comprehensive template system enables rapid development of consistent, professional Jarvis UIs while maintaining the flexibility to create specialized interfaces for unique requirements.
