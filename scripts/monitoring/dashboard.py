#!/usr/bin/env python3
"""
Monitoring Dashboard for Enhanced Jarvis Features

Provides a web-based dashboard for monitoring:
- System performance metrics
- Enhanced feature usage analytics
- Real-time health status
- Performance trends and alerts
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("FastAPI not available. Install with: pip install fastapi uvicorn")

from enhanced_monitoring import monitoring_system

logger = logging.getLogger(__name__)

class MonitoringDashboard:
    """Web-based monitoring dashboard."""
    
    def __init__(self, host: str = "localhost", port: int = 8001):
        self.host = host
        self.port = port
        self.app = None
        self.websocket_connections: List[WebSocket] = []
        
        if FASTAPI_AVAILABLE:
            self._setup_fastapi_app()
    
    def _setup_fastapi_app(self):
        """Set up FastAPI application."""
        self.app = FastAPI(title="Jarvis Enhanced Monitoring Dashboard")
        
        # API endpoints
        self.app.get("/api/health")(self.get_health_status)
        self.app.get("/api/metrics")(self.get_metrics)
        self.app.get("/api/performance")(self.get_performance_data)
        self.app.get("/api/system")(self.get_system_metrics)
        self.app.websocket("/ws")(self.websocket_endpoint)
        
        # Serve dashboard HTML
        self.app.get("/")(self.serve_dashboard)
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current system health status."""
        try:
            health_report = monitoring_system.generate_health_report()
            return {
                "status": "success",
                "data": health_report
            }
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get dashboard metrics data."""
        try:
            dashboard_data = monitoring_system.get_dashboard_data()
            return {
                "status": "success",
                "data": dashboard_data
            }
        except Exception as e:
            logger.error(f"Error getting metrics: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_performance_data(self, component: str = None, hours: int = 1) -> Dict[str, Any]:
        """Get performance data for specific component."""
        try:
            summary = monitoring_system.collector.get_metrics_summary(
                component=component,
                time_window_minutes=hours * 60
            )
            return {
                "status": "success",
                "data": summary
            }
        except Exception as e:
            logger.error(f"Error getting performance data: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def get_system_metrics(self, hours: int = 1) -> Dict[str, Any]:
        """Get system resource metrics."""
        try:
            cutoff_time = time.time() - (hours * 3600)
            
            with monitoring_system.collector._lock:
                system_metrics = [
                    {
                        "timestamp": m.timestamp,
                        "cpu_percent": m.cpu_percent,
                        "memory_mb": m.memory_mb,
                        "memory_percent": m.memory_percent,
                        "disk_usage_percent": m.disk_usage_percent
                    }
                    for m in monitoring_system.collector.system_metrics
                    if m.timestamp >= cutoff_time
                ]
            
            return {
                "status": "success",
                "data": system_metrics
            }
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def websocket_endpoint(self, websocket: WebSocket):
        """WebSocket endpoint for real-time updates."""
        await websocket.accept()
        self.websocket_connections.append(websocket)
        
        try:
            while True:
                # Send periodic updates
                dashboard_data = monitoring_system.get_dashboard_data()
                await websocket.send_json({
                    "type": "dashboard_update",
                    "data": dashboard_data,
                    "timestamp": time.time()
                })
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
        except WebSocketDisconnect:
            self.websocket_connections.remove(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            if websocket in self.websocket_connections:
                self.websocket_connections.remove(websocket)
    
    async def broadcast_alert(self, alert: Dict[str, Any]):
        """Broadcast alert to all connected WebSocket clients."""
        if not self.websocket_connections:
            return
        
        message = {
            "type": "alert",
            "data": alert,
            "timestamp": time.time()
        }
        
        # Send to all connected clients
        disconnected = []
        for websocket in self.websocket_connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected:
            self.websocket_connections.remove(websocket)
    
    async def serve_dashboard(self) -> HTMLResponse:
        """Serve the dashboard HTML page."""
        html_content = self._generate_dashboard_html()
        return HTMLResponse(content=html_content)
    
    def _generate_dashboard_html(self) -> str:
        """Generate dashboard HTML content."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jarvis Enhanced Monitoring Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }
        .status-healthy { color: #28a745; }
        .status-degraded { color: #ffc107; }
        .status-critical { color: #dc3545; }
        .alert {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
        }
        .chart-container {
            height: 200px;
            margin-top: 15px;
        }
        #connection-status {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.8em;
        }
        .connected { background: #d4edda; color: #155724; }
        .disconnected { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div id="connection-status" class="disconnected">Connecting...</div>
    
    <div class="header">
        <h1>🤖 Jarvis Enhanced Monitoring Dashboard</h1>
        <p>Real-time monitoring for System Integration & Code Consciousness features</p>
    </div>
    
    <div id="alerts-container"></div>
    
    <div class="dashboard-grid">
        <div class="card">
            <h3>System Health</h3>
            <div id="health-status" class="metric-value">Loading...</div>
            <div class="metric-label">Overall Status</div>
            <div id="health-issues"></div>
        </div>
        
        <div class="card">
            <h3>Plugin Registry</h3>
            <div id="registry-success-rate" class="metric-value">-</div>
            <div class="metric-label">Success Rate</div>
            <div id="registry-avg-time" class="metric-label">Avg Response: -</div>
        </div>
        
        <div class="card">
            <h3>Context Manager</h3>
            <div id="context-success-rate" class="metric-value">-</div>
            <div class="metric-label">Success Rate</div>
            <div id="context-avg-time" class="metric-label">Avg Response: -</div>
        </div>
        
        <div class="card">
            <h3>Orchestrator</h3>
            <div id="orchestrator-success-rate" class="metric-value">-</div>
            <div class="metric-label">Success Rate</div>
            <div id="orchestrator-avg-time" class="metric-label">Avg Response: -</div>
        </div>
        
        <div class="card">
            <h3>System Resources</h3>
            <div id="cpu-usage" class="metric-value">-</div>
            <div class="metric-label">CPU Usage</div>
            <div id="memory-usage" class="metric-label">Memory: -</div>
        </div>
        
        <div class="card">
            <h3>Performance Trends</h3>
            <div class="chart-container" id="performance-chart">
                <p>Performance chart will be displayed here</p>
            </div>
        </div>
    </div>
    
    <script>
        let ws = null;
        let reconnectInterval = null;
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('WebSocket connected');
                document.getElementById('connection-status').textContent = 'Connected';
                document.getElementById('connection-status').className = 'connected';
                
                if (reconnectInterval) {
                    clearInterval(reconnectInterval);
                    reconnectInterval = null;
                }
            };
            
            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                
                if (message.type === 'dashboard_update') {
                    updateDashboard(message.data);
                } else if (message.type === 'alert') {
                    showAlert(message.data);
                }
            };
            
            ws.onclose = function() {
                console.log('WebSocket disconnected');
                document.getElementById('connection-status').textContent = 'Disconnected';
                document.getElementById('connection-status').className = 'disconnected';
                
                // Attempt to reconnect
                if (!reconnectInterval) {
                    reconnectInterval = setInterval(connectWebSocket, 5000);
                }
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }
        
        function updateDashboard(data) {
            // Update health status
            const healthReport = data.summary || {};
            const healthStatus = healthReport.health_status || 'unknown';
            const healthElement = document.getElementById('health-status');
            
            healthElement.textContent = healthStatus.toUpperCase();
            healthElement.className = `metric-value status-${healthStatus}`;
            
            // Update component summaries
            const summaries = data.component_summaries || {};
            
            updateComponentCard('registry', summaries.plugin_registry);
            updateComponentCard('context', summaries.context_manager);
            updateComponentCard('orchestrator', summaries.orchestrator);
            
            // Update system metrics
            const systemMetrics = data.system_metrics || [];
            if (systemMetrics.length > 0) {
                const latest = systemMetrics[systemMetrics.length - 1];
                document.getElementById('cpu-usage').textContent = `${latest.cpu_percent.toFixed(1)}%`;
                document.getElementById('memory-usage').textContent = `Memory: ${latest.memory_mb.toFixed(0)}MB (${latest.memory_percent.toFixed(1)}%)`;
            }
        }
        
        function updateComponentCard(component, summary) {
            if (!summary) return;
            
            const successRate = (summary.success_rate * 100).toFixed(1);
            const avgTime = summary.mean_duration_ms.toFixed(1);
            
            document.getElementById(`${component}-success-rate`).textContent = `${successRate}%`;
            document.getElementById(`${component}-avg-time`).textContent = `Avg Response: ${avgTime}ms`;
        }
        
        function showAlert(alert) {
            const alertsContainer = document.getElementById('alerts-container');
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert';
            alertDiv.textContent = `Alert: ${alert.type} - ${JSON.stringify(alert)}`;
            
            alertsContainer.appendChild(alertDiv);
            
            // Remove alert after 10 seconds
            setTimeout(() => {
                alertDiv.remove();
            }, 10000);
        }
        
        // Initialize dashboard
        connectWebSocket();
        
        // Refresh data every 30 seconds as fallback
        setInterval(async () => {
            if (ws && ws.readyState === WebSocket.OPEN) return;
            
            try {
                const response = await fetch('/api/metrics');
                const result = await response.json();
                if (result.status === 'success') {
                    updateDashboard(result.data);
                }
            } catch (error) {
                console.error('Failed to fetch metrics:', error);
            }
        }, 30000);
    </script>
</body>
</html>
        """
    
    def run(self):
        """Run the monitoring dashboard server."""
        if not FASTAPI_AVAILABLE:
            print("FastAPI is required to run the dashboard. Install with: pip install fastapi uvicorn")
            return
        
        # Set up alert broadcasting
        monitoring_system.collector.add_alert_callback(self._handle_alert)
        
        print(f"Starting monitoring dashboard at http://{self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")
    
    def _handle_alert(self, alert: Dict[str, Any]):
        """Handle alerts from the monitoring system."""
        # Broadcast alert to WebSocket clients
        asyncio.create_task(self.broadcast_alert(alert))

def main():
    """Main entry point for the dashboard."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Jarvis Enhanced Monitoring Dashboard")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    
    args = parser.parse_args()
    
    # Start monitoring system if not already running
    if not monitoring_system.running:
        monitoring_system.start_monitoring()
    
    # Start dashboard
    dashboard = MonitoringDashboard(host=args.host, port=args.port)
    dashboard.run()

if __name__ == "__main__":
    main()
