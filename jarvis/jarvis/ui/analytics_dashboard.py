"""
Usage Analytics Dashboard

Real-time dashboard for monitoring system usage, performance metrics,
and user behavior patterns. Built using the Jarvis UI template.
"""

import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout,
    QWidget, QLabel, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QScrollArea, QFrame, QProgressBar, QComboBox, QDateEdit, QTextEdit,
    QSplitter, QGroupBox, QCheckBox
)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal, QDate
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QPieSeries, QBarSeries, QBarSet

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from jarvis.jarvis.core.analytics.usage_analytics import usage_analytics

logger = logging.getLogger(__name__)
from jarvis.jarvis.core.monitoring.performance_tracker import performance_tracker

class MetricCard(QFrame):
    """Individual metric display card."""
    
    def __init__(self, title: str, value: str, unit: str = "", trend: Optional[str] = None):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #cccccc; font-size: 12px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Value
        value_layout = QHBoxLayout()
        value_label = QLabel(value)
        value_label.setStyleSheet("color: #ffffff; font-size: 24px; font-weight: bold;")
        value_layout.addWidget(value_label)
        
        if unit:
            unit_label = QLabel(unit)
            unit_label.setStyleSheet("color: #888888; font-size: 14px;")
            value_layout.addWidget(unit_label)
        
        value_layout.addStretch()
        layout.addLayout(value_layout)
        
        # Trend indicator
        if trend:
            trend_label = QLabel(trend)
            if trend.startswith('+'):
                trend_label.setStyleSheet("color: #4CAF50; font-size: 12px;")
            elif trend.startswith('-'):
                trend_label.setStyleSheet("color: #f44336; font-size: 12px;")
            else:
                trend_label.setStyleSheet("color: #888888; font-size: 12px;")
            layout.addWidget(trend_label)
        
        layout.addStretch()
        self.setLayout(layout)

class AnalyticsDataThread(QThread):
    """Background thread for fetching analytics data."""
    
    data_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def run(self):
        """Main thread loop."""
        while self.running:
            try:
                # Fetch analytics data
                system_stats = usage_analytics.get_system_usage_stats()
                performance_summary = performance_tracker.get_performance_summary()
                
                data = {
                    'system_stats': system_stats,
                    'performance_summary': performance_summary,
                    'timestamp': time.time()
                }
                
                self.data_updated.emit(data)
                
                # Wait 5 seconds before next update
                self.msleep(5000)
                
            except Exception as e:
                logger.error(f"Error fetching analytics data: {e}", exc_info=True)
                print(f"Error fetching analytics data: {e}")  # Keep print for UI feedback
                self.msleep(5000)
    
    def stop(self):
        """Stop the thread."""
        self.running = False

class UsageAnalyticsDashboard(QMainWindow):
    """
    Main usage analytics dashboard window.
    
    Features:
    - Real-time metrics display
    - Tool usage statistics
    - Performance monitoring
    - User behavior analysis
    - System health indicators
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jarvis Usage Analytics Dashboard")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #404040;
                background-color: #2b2b2b;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QLabel {
                color: #ffffff;
            }
            QTableWidget {
                background-color: #2b2b2b;
                alternate-background-color: #353535;
                gridline-color: #404040;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #404040;
                color: #ffffff;
                padding: 8px;
                border: none;
            }
        """)
        
        # Initialize data thread
        self.data_thread = AnalyticsDataThread()
        self.data_thread.data_updated.connect(self.update_dashboard_data)
        
        # Initialize UI
        self.init_ui()
        
        # Start data updates
        self.data_thread.start()
    
    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("Usage Analytics Dashboard")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Overview tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "Overview")
        
        # Tool Usage tab
        self.tool_usage_tab = self.create_tool_usage_tab()
        self.tab_widget.addTab(self.tool_usage_tab, "Tool Usage")
        
        # Performance tab
        self.performance_tab = self.create_performance_tab()
        self.tab_widget.addTab(self.performance_tab, "Performance")
        
        # User Behavior tab
        self.user_behavior_tab = self.create_user_behavior_tab()
        self.tab_widget.addTab(self.user_behavior_tab, "User Behavior")
        
        layout.addWidget(self.tab_widget)
        central_widget.setLayout(layout)
    
    def create_overview_tab(self) -> QWidget:
        """Create the overview tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Key metrics cards
        metrics_layout = QGridLayout()
        
        # Initialize metric cards (will be updated with real data)
        self.total_sessions_card = MetricCard("Total Sessions", "0")
        self.total_tools_card = MetricCard("Tool Calls", "0")
        self.unique_users_card = MetricCard("Unique Users", "0")
        self.success_rate_card = MetricCard("Success Rate", "0", "%")
        
        metrics_layout.addWidget(self.total_sessions_card, 0, 0)
        metrics_layout.addWidget(self.total_tools_card, 0, 1)
        metrics_layout.addWidget(self.unique_users_card, 0, 2)
        metrics_layout.addWidget(self.success_rate_card, 0, 3)
        
        layout.addLayout(metrics_layout)
        
        # System status
        status_group = QGroupBox("System Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ffffff; }")
        status_layout = QVBoxLayout()
        
        self.system_status_label = QLabel("System: Operational")
        self.system_status_label.setStyleSheet("color: #4CAF50; font-size: 14px;")
        status_layout.addWidget(self.system_status_label)
        
        self.last_update_label = QLabel("Last Update: Never")
        self.last_update_label.setStyleSheet("color: #888888; font-size: 12px;")
        status_layout.addWidget(self.last_update_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Recent activity
        activity_group = QGroupBox("Recent Activity")
        activity_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ffffff; }")
        activity_layout = QVBoxLayout()
        
        self.activity_text = QTextEdit()
        self.activity_text.setMaximumHeight(200)
        self.activity_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                color: #ffffff;
                font-family: monospace;
            }
        """)
        activity_layout.addWidget(self.activity_text)
        
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_tool_usage_tab(self) -> QWidget:
        """Create the tool usage tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tool usage table
        usage_group = QGroupBox("Tool Usage Statistics")
        usage_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ffffff; }")
        usage_layout = QVBoxLayout()
        
        self.tool_usage_table = QTableWidget()
        self.tool_usage_table.setColumnCount(5)
        self.tool_usage_table.setHorizontalHeaderLabels([
            "Tool Name", "Usage Count", "Success Rate", "Avg Time (ms)", "Last Used"
        ])
        self.tool_usage_table.horizontalHeader().setStretchLastSection(True)
        usage_layout.addWidget(self.tool_usage_table)
        
        usage_group.setLayout(usage_layout)
        layout.addWidget(usage_group)
        
        # Tool chains
        chains_group = QGroupBox("Popular Tool Chains")
        chains_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ffffff; }")
        chains_layout = QVBoxLayout()
        
        self.tool_chains_table = QTableWidget()
        self.tool_chains_table.setColumnCount(3)
        self.tool_chains_table.setHorizontalHeaderLabels([
            "Tool Chain", "Usage Count", "Success Rate"
        ])
        self.tool_chains_table.horizontalHeader().setStretchLastSection(True)
        chains_layout.addWidget(self.tool_chains_table)
        
        chains_group.setLayout(chains_layout)
        layout.addWidget(chains_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_performance_tab(self) -> QWidget:
        """Create the performance tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Performance metrics
        perf_metrics_layout = QGridLayout()
        
        self.cpu_usage_card = MetricCard("CPU Usage", "0", "%")
        self.memory_usage_card = MetricCard("Memory Usage", "0", "%")
        self.response_time_card = MetricCard("Avg Response Time", "0", "ms")
        self.error_rate_card = MetricCard("Error Rate", "0", "%")
        
        perf_metrics_layout.addWidget(self.cpu_usage_card, 0, 0)
        perf_metrics_layout.addWidget(self.memory_usage_card, 0, 1)
        perf_metrics_layout.addWidget(self.response_time_card, 0, 2)
        perf_metrics_layout.addWidget(self.error_rate_card, 0, 3)
        
        layout.addLayout(perf_metrics_layout)
        
        # Performance details
        details_group = QGroupBox("Performance Details")
        details_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ffffff; }")
        details_layout = QVBoxLayout()
        
        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(6)
        self.performance_table.setHorizontalHeaderLabels([
            "Operation", "Total Calls", "Avg Time (ms)", "Min Time", "Max Time", "Success Rate"
        ])
        self.performance_table.horizontalHeader().setStretchLastSection(True)
        details_layout.addWidget(self.performance_table)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_user_behavior_tab(self) -> QWidget:
        """Create the user behavior tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # User statistics
        user_stats_layout = QGridLayout()
        
        self.active_users_card = MetricCard("Active Users", "0")
        self.avg_session_card = MetricCard("Avg Session", "0", "min")
        self.peak_hour_card = MetricCard("Peak Hour", "N/A")
        self.retention_card = MetricCard("User Retention", "0", "%")
        
        user_stats_layout.addWidget(self.active_users_card, 0, 0)
        user_stats_layout.addWidget(self.avg_session_card, 0, 1)
        user_stats_layout.addWidget(self.peak_hour_card, 0, 2)
        user_stats_layout.addWidget(self.retention_card, 0, 3)
        
        layout.addLayout(user_stats_layout)
        
        # User behavior patterns
        behavior_group = QGroupBox("User Behavior Patterns")
        behavior_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ffffff; }")
        behavior_layout = QVBoxLayout()
        
        self.behavior_text = QTextEdit()
        self.behavior_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                color: #ffffff;
                font-family: monospace;
            }
        """)
        behavior_layout.addWidget(self.behavior_text)
        
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)
        
        widget.setLayout(layout)
        return widget
    
    def update_dashboard_data(self, data: Dict[str, Any]):
        """Update dashboard with new data."""
        try:
            system_stats = data.get('system_stats')
            performance_summary = data.get('performance_summary')
            
            if system_stats:
                self.update_overview_tab(system_stats)
                self.update_tool_usage_tab(system_stats)
                self.update_user_behavior_tab(system_stats)
            
            if performance_summary:
                self.update_performance_tab(performance_summary)
            
            # Update last update time
            self.last_update_label.setText(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Error updating dashboard: {e}", exc_info=True)
            print(f"Error updating dashboard: {e}")  # Keep print for UI feedback
    
    def update_overview_tab(self, stats):
        """Update overview tab with new data."""
        # Update metric cards
        self.total_sessions_card.findChild(QLabel).setText(str(stats.total_sessions))
        self.total_tools_card.findChild(QLabel).setText(str(stats.total_tool_calls))
        self.unique_users_card.findChild(QLabel).setText(str(stats.unique_users))
        
        success_rate = 100 - stats.error_rate_percent
        self.success_rate_card.findChild(QLabel).setText(f"{success_rate:.1f}")
        
        # Update activity log
        activity_text = f"System Status: Operational\n"
        activity_text += f"Total Sessions: {stats.total_sessions}\n"
        activity_text += f"Average Session Duration: {stats.avg_session_duration_minutes:.1f} minutes\n"
        activity_text += f"Most Popular Tools: {', '.join([tool for tool, _ in stats.most_popular_tools[:3]])}\n"
        activity_text += f"Peak Usage Hours: {', '.join([f'{hour:02d}:00' for hour in stats.peak_usage_hours])}\n"
        
        self.activity_text.setPlainText(activity_text)
    
    def update_tool_usage_tab(self, stats):
        """Update tool usage tab with new data."""
        # Update tool usage table
        self.tool_usage_table.setRowCount(len(stats.most_popular_tools))
        
        for row, (tool_name, usage_count) in enumerate(stats.most_popular_tools):
            self.tool_usage_table.setItem(row, 0, QTableWidgetItem(tool_name))
            self.tool_usage_table.setItem(row, 1, QTableWidgetItem(str(usage_count)))
            self.tool_usage_table.setItem(row, 2, QTableWidgetItem("95%"))  # Placeholder
            self.tool_usage_table.setItem(row, 3, QTableWidgetItem("150"))  # Placeholder
            self.tool_usage_table.setItem(row, 4, QTableWidgetItem("Recent"))  # Placeholder
        
        # Update tool chains table
        self.tool_chains_table.setRowCount(len(stats.most_successful_tool_chains))
        
        for row, (chain, success_rate) in enumerate(stats.most_successful_tool_chains):
            chain_str = " → ".join(chain)
            self.tool_chains_table.setItem(row, 0, QTableWidgetItem(chain_str))
            self.tool_chains_table.setItem(row, 1, QTableWidgetItem("10"))  # Placeholder
            self.tool_chains_table.setItem(row, 2, QTableWidgetItem(f"{success_rate*100:.1f}%"))
    
    def update_performance_tab(self, performance_summary):
        """Update performance tab with new data."""
        system_resources = performance_summary.get('system_resources')
        operations = performance_summary.get('operations', {})
        
        if system_resources:
            # Update performance metric cards
            cpu_labels = self.cpu_usage_card.findChildren(QLabel)
            if len(cpu_labels) >= 2:
                cpu_labels[1].setText(f"{system_resources.cpu_percent:.1f}")
            
            memory_labels = self.memory_usage_card.findChildren(QLabel)
            if len(memory_labels) >= 2:
                memory_labels[1].setText(f"{system_resources.memory_percent:.1f}")
        
        # Update performance table
        self.performance_table.setRowCount(len(operations))
        
        for row, (op_name, op_stats) in enumerate(operations.items()):
            self.performance_table.setItem(row, 0, QTableWidgetItem(op_name))
            self.performance_table.setItem(row, 1, QTableWidgetItem(str(op_stats['total_executions'])))
            self.performance_table.setItem(row, 2, QTableWidgetItem(f"{op_stats['avg_time_ms']:.1f}"))
            self.performance_table.setItem(row, 3, QTableWidgetItem(f"{op_stats['min_time_ms']:.1f}"))
            self.performance_table.setItem(row, 4, QTableWidgetItem(f"{op_stats['max_time_ms']:.1f}"))
            self.performance_table.setItem(row, 5, QTableWidgetItem(f"{op_stats['success_rate']:.1f}%"))
    
    def update_user_behavior_tab(self, stats):
        """Update user behavior tab with new data."""
        # Update user metric cards
        active_labels = self.active_users_card.findChildren(QLabel)
        if len(active_labels) >= 2:
            active_labels[1].setText(str(stats.unique_users))
        
        session_labels = self.avg_session_card.findChildren(QLabel)
        if len(session_labels) >= 2:
            session_labels[1].setText(f"{stats.avg_session_duration_minutes:.1f}")
        
        peak_labels = self.peak_hour_card.findChildren(QLabel)
        if len(peak_labels) >= 2 and stats.peak_usage_hours:
            peak_labels[1].setText(f"{stats.peak_usage_hours[0]:02d}:00")
        
        # Update behavior patterns text
        behavior_text = "User Behavior Analysis:\n\n"
        behavior_text += f"• Average session duration: {stats.avg_session_duration_minutes:.1f} minutes\n"
        behavior_text += f"• Peak usage hours: {', '.join([f'{hour:02d}:00' for hour in stats.peak_usage_hours])}\n"
        behavior_text += f"• Most popular tool combinations:\n"
        
        for chain, success_rate in stats.most_successful_tool_chains[:5]:
            chain_str = " → ".join(chain)
            behavior_text += f"  - {chain_str} (Success: {success_rate*100:.1f}%)\n"
        
        self.behavior_text.setPlainText(behavior_text)
    
    def refresh_data(self):
        """Manually refresh dashboard data."""
        # Force refresh of analytics data
        usage_analytics.get_system_usage_stats(force_refresh=True)
        self.last_update_label.setText("Refreshing...")
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.data_thread.stop()
        self.data_thread.wait()
        event.accept()

def main():
    """Main function to run the analytics dashboard."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Jarvis Analytics Dashboard")
    app.setApplicationVersion("1.0.0")
    
    # Create and show dashboard
    dashboard = UsageAnalyticsDashboard()
    dashboard.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
