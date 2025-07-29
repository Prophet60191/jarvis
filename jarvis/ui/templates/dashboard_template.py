#!/usr/bin/env python3
"""
Jarvis Dashboard Template

Template for creating dashboard-style UIs with real-time monitoring,
status displays, and interactive controls.

Usage:
    from jarvis.ui.templates.dashboard_template import JarvisDashboardTemplate
    
    class MyDashboard(JarvisDashboardTemplate):
        def get_dashboard_widgets(self):
            return [
                self.create_status_widget("System", "online"),
                self.create_metric_widget("CPU Usage", "45%"),
                self.create_chart_widget("Memory", [65, 70, 68, 72])
            ]
"""

import json
from typing import Dict, List, Any
from ..jarvis_ui_template import JarvisUITemplate, JarvisDesktopApp


class JarvisDashboardTemplate(JarvisUITemplate):
    """Template for dashboard-style Jarvis UIs."""
    
    def __init__(self, app_name: str, version: str = "1.0"):
        super().__init__(app_name, version)
        self.refresh_interval = 5000  # 5 seconds
    
    def get_navigation(self) -> str:
        """Default dashboard navigation."""
        return self.components.navigation_section("Dashboard", [
            {"icon": "📊", "label": "Overview", "url": "/", "active": True},
            {"icon": "📈", "label": "Metrics", "url": "/metrics"},
            {"icon": "🔔", "label": "Alerts", "url": "/alerts"},
            {"icon": "⚙️", "label": "Settings", "url": "/settings"}
        ])
    
    def get_dashboard_content(self) -> str:
        """Generate dashboard content with widgets."""
        widgets = self.get_dashboard_widgets()
        widgets_html = "".join(widgets)
        
        return f"""
        <div class="dashboard-container">
            <div class="dashboard-header">
                <h2>System Overview</h2>
                <div class="dashboard-controls">
                    <button class="btn btn-secondary" onclick="refreshDashboard()">
                        🔄 Refresh
                    </button>
                    <span class="last-updated" id="last-updated">
                        Last updated: {self.get_current_time()}
                    </span>
                </div>
            </div>
            
            <div class="dashboard-grid">
                {widgets_html}
            </div>
            
            <div class="dashboard-footer">
                <p>Auto-refresh every {self.refresh_interval // 1000} seconds</p>
            </div>
        </div>
        """
    
    def get_dashboard_widgets(self) -> List[str]:
        """Override to provide custom dashboard widgets."""
        return [
            self.create_status_widget("System Status", "operational", "success"),
            self.create_metric_widget("Active Users", "42", "👥"),
            self.create_metric_widget("Response Time", "125ms", "⚡"),
            self.create_chart_widget("Performance", [85, 90, 88, 92, 87])
        ]
    
    def create_status_widget(self, title: str, status: str, status_type: str = "success") -> str:
        """Create a status display widget."""
        return f"""
        <div class="dashboard-widget status-widget">
            <div class="widget-header">
                <h3>{title}</h3>
                {self.components.status_indicator(status_type, status.title())}
            </div>
            <div class="widget-content">
                <div class="status-display">
                    <div class="status-icon status-{status_type}">
                        {'✅' if status_type == 'success' else '⚠️' if status_type == 'warning' else '❌'}
                    </div>
                    <div class="status-text">{status.title()}</div>
                </div>
            </div>
        </div>
        """
    
    def create_metric_widget(self, title: str, value: str, icon: str = "📊") -> str:
        """Create a metric display widget."""
        return f"""
        <div class="dashboard-widget metric-widget">
            <div class="widget-header">
                <h3>{title}</h3>
                <span class="widget-icon">{icon}</span>
            </div>
            <div class="widget-content">
                <div class="metric-value">{value}</div>
                <div class="metric-trend">
                    <span class="trend-indicator">↗️</span>
                    <span class="trend-text">+5% from last hour</span>
                </div>
            </div>
        </div>
        """
    
    def create_chart_widget(self, title: str, data: List[int], chart_type: str = "line") -> str:
        """Create a chart widget."""
        data_json = json.dumps(data)
        chart_id = f"chart-{title.lower().replace(' ', '-')}"
        
        return f"""
        <div class="dashboard-widget chart-widget">
            <div class="widget-header">
                <h3>{title}</h3>
                <div class="chart-controls">
                    <button class="btn-small" onclick="toggleChartType('{chart_id}')">📈</button>
                </div>
            </div>
            <div class="widget-content">
                <div class="chart-container">
                    <canvas id="{chart_id}" data-values="{data_json}" data-type="{chart_type}"></canvas>
                </div>
            </div>
        </div>
        """
    
    def create_list_widget(self, title: str, items: List[Dict], icon: str = "📋") -> str:
        """Create a list display widget."""
        items_html = ""
        for item in items:
            status_class = f"status-{item.get('status', 'default')}"
            items_html += f"""
            <div class="list-item {status_class}">
                <div class="item-title">{item.get('title', 'Item')}</div>
                <div class="item-meta">{item.get('meta', '')}</div>
                <div class="item-actions">
                    {item.get('actions', '')}
                </div>
            </div>
            """
        
        return f"""
        <div class="dashboard-widget list-widget">
            <div class="widget-header">
                <h3>{title}</h3>
                <span class="widget-icon">{icon}</span>
            </div>
            <div class="widget-content">
                <div class="list-container">
                    {items_html}
                </div>
            </div>
        </div>
        """
    
    def get_custom_css(self) -> str:
        """Dashboard-specific CSS."""
        return """
        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .dashboard-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .dashboard-controls {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .last-updated {
            color: #8892b0;
            font-size: 0.9em;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .dashboard-widget {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
        }
        
        .dashboard-widget:hover {
            background: rgba(255, 255, 255, 0.08);
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }
        
        .widget-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .widget-header h3 {
            margin: 0;
            color: #ffffff;
            font-size: 1.1em;
        }
        
        .widget-icon {
            font-size: 1.2em;
        }
        
        .status-display {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .status-icon {
            font-size: 2em;
        }
        
        .status-text {
            font-size: 1.2em;
            font-weight: 500;
        }
        
        .metric-value {
            font-size: 2.5em;
            font-weight: 600;
            color: #64ffda;
            margin-bottom: 0.5rem;
        }
        
        .metric-trend {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: #8892b0;
            font-size: 0.9em;
        }
        
        .chart-container {
            height: 200px;
            position: relative;
        }
        
        .chart-container canvas {
            width: 100%;
            height: 100%;
        }
        
        .list-container {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .list-item {
            padding: 0.75rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .list-item:last-child {
            border-bottom: none;
        }
        
        .item-title {
            font-weight: 500;
            color: #e0e6ed;
        }
        
        .item-meta {
            color: #8892b0;
            font-size: 0.9em;
        }
        
        .btn-small {
            padding: 4px 8px;
            font-size: 0.8em;
            border: none;
            border-radius: 4px;
            background: rgba(255, 255, 255, 0.1);
            color: #e0e6ed;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .btn-small:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .dashboard-footer {
            text-align: center;
            color: #8892b0;
            font-size: 0.9em;
            padding-top: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .dashboard-header {
                flex-direction: column;
                gap: 1rem;
                align-items: flex-start;
            }
        }
        """
    
    def get_javascript(self) -> str:
        """Dashboard-specific JavaScript."""
        return f"""
        // Auto-refresh functionality
        let refreshInterval;
        
        function startAutoRefresh() {{
            refreshInterval = setInterval(refreshDashboard, {self.refresh_interval});
        }}
        
        function stopAutoRefresh() {{
            if (refreshInterval) {{
                clearInterval(refreshInterval);
            }}
        }}
        
        function refreshDashboard() {{
            // Update timestamp
            document.getElementById('last-updated').textContent = 
                'Last updated: ' + new Date().toLocaleTimeString();
            
            // Trigger custom refresh logic
            if (typeof onDashboardRefresh === 'function') {{
                onDashboardRefresh();
            }}
        }}
        
        // Simple chart rendering
        function renderCharts() {{
            const charts = document.querySelectorAll('canvas[data-values]');
            charts.forEach(renderChart);
        }}
        
        function renderChart(canvas) {{
            const ctx = canvas.getContext('2d');
            const data = JSON.parse(canvas.dataset.values);
            const type = canvas.dataset.type || 'line';
            
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Simple line chart implementation
            if (type === 'line') {{
                drawLineChart(ctx, data, canvas.width, canvas.height);
            }}
        }}
        
        function drawLineChart(ctx, data, width, height) {{
            if (data.length < 2) return;
            
            const padding = 20;
            const chartWidth = width - 2 * padding;
            const chartHeight = height - 2 * padding;
            
            const max = Math.max(...data);
            const min = Math.min(...data);
            const range = max - min || 1;
            
            ctx.strokeStyle = '#64ffda';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            data.forEach((value, index) => {{
                const x = padding + (index / (data.length - 1)) * chartWidth;
                const y = padding + (1 - (value - min) / range) * chartHeight;
                
                if (index === 0) {{
                    ctx.moveTo(x, y);
                }} else {{
                    ctx.lineTo(x, y);
                }}
            }});
            
            ctx.stroke();
        }}
        
        function toggleChartType(chartId) {{
            const canvas = document.getElementById(chartId);
            const currentType = canvas.dataset.type || 'line';
            canvas.dataset.type = currentType === 'line' ? 'bar' : 'line';
            renderChart(canvas);
        }}
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {{
            renderCharts();
            startAutoRefresh();
        }});
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', function() {{
            stopAutoRefresh();
        }});
        """
    
    def get_current_time(self) -> str:
        """Get current time string."""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")


class JarvisDashboardApp(JarvisDesktopApp):
    """Desktop app wrapper for dashboard template."""
    
    def __init__(self, app_name: str = "Jarvis Dashboard", debug: bool = False):
        super().__init__(app_name, debug)
        self.dashboard = JarvisDashboardTemplate(app_name)
    
    def get_html_content(self) -> str:
        """Get the complete HTML for the dashboard app."""
        content = self.dashboard.get_dashboard_content()
        return self.dashboard.get_html_template("Dashboard", content)


# Example usage
if __name__ == "__main__":
    class MyCustomDashboard(JarvisDashboardTemplate):
        def get_dashboard_widgets(self):
            return [
                self.create_status_widget("Jarvis Core", "running", "success"),
                self.create_metric_widget("Active Plugins", "8", "🔌"),
                self.create_metric_widget("Memory Usage", "2.1GB", "💾"),
                self.create_chart_widget("CPU Usage", [45, 52, 48, 61, 55, 49, 63]),
                self.create_list_widget("Recent Activities", [
                    {"title": "Plugin loaded: device_time_tool", "meta": "2 minutes ago", "status": "success"},
                    {"title": "Voice command processed", "meta": "5 minutes ago", "status": "success"},
                    {"title": "Configuration updated", "meta": "10 minutes ago", "status": "info"}
                ])
            ]
    
    class MyDashboardApp(JarvisDashboardApp):
        def __init__(self):
            super().__init__("My Jarvis Dashboard")
            self.dashboard = MyCustomDashboard("My Jarvis Dashboard")
    
    app = MyDashboardApp()
    app.run()
