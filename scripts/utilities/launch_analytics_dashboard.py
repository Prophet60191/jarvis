#!/usr/bin/env python3
"""
Analytics Dashboard Launcher

Launches the Jarvis Usage Analytics Dashboard with proper initialization
and sample data generation for demonstration purposes.
"""

import sys
import time
import threading
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def generate_sample_data():
    """Generate sample analytics data for demonstration."""
    try:
        from jarvis.jarvis.core.analytics.usage_analytics import usage_analytics
        from jarvis.jarvis.core.monitoring.performance_tracker import performance_tracker
        
        print("🔄 Generating sample analytics data...")
        
        # Sample users and sessions
        users = ["user_001", "user_002", "user_003", "user_004", "user_005"]
        tools = [
            "file_manager", "web_search", "text_editor", "calculator", 
            "email_client", "calendar", "note_taker", "image_editor",
            "code_analyzer", "data_processor"
        ]
        
        # Generate sample data
        for i in range(100):
            session_id = f"sample_session_{i}"
            user_id = users[i % len(users)]
            
            # Track conversation start
            usage_analytics.track_conversation_event(
                session_id=session_id,
                event_type='start',
                user_id=user_id
            )
            
            # Simulate tool usage in session
            num_tools = min(3 + (i % 4), len(tools))  # 3-6 tools per session
            session_tools = tools[:num_tools]
            
            for j, tool_name in enumerate(session_tools):
                # Simulate realistic execution times
                base_time = 100 + (j * 50)
                execution_time = base_time + (i % 100)  # Add some variance
                success = (i + j) % 10 != 0  # 90% success rate
                
                usage_analytics.track_tool_usage(
                    tool_name=tool_name,
                    session_id=session_id,
                    execution_time_ms=execution_time,
                    success=success,
                    user_id=user_id,
                    input_size_bytes=1024 + (i * 100),
                    output_size_bytes=2048 + (i * 150),
                    error_message="Sample error" if not success else None,
                    context={
                        "session_step": j,
                        "complexity": "medium" if i % 3 == 0 else "low",
                        "user_intent": "productivity" if i % 2 == 0 else "analysis"
                    }
                )
                
                # Track performance metrics
                op_id = performance_tracker.start_operation(f"sample_{tool_name}")
                time.sleep(0.001)  # Simulate brief work
                performance_tracker.end_operation(
                    op_id, 
                    success=success,
                    error_message="Sample error" if not success else None,
                    metadata={"tool": tool_name, "session": session_id}
                )
            
            # Track conversation end
            usage_analytics.track_conversation_event(
                session_id=session_id,
                event_type='end',
                user_id=user_id
            )
        
        # Add some performance metrics
        for i in range(50):
            performance_tracker.record_metric(
                name="response_time",
                value=150 + (i % 200),
                unit="ms",
                category="performance"
            )
            
            performance_tracker.record_metric(
                name="memory_usage",
                value=60 + (i % 30),
                unit="percent",
                category="system"
            )
        
        print("✅ Sample data generated successfully!")
        print(f"   - 100 sessions created")
        print(f"   - {len(users)} unique users")
        print(f"   - {len(tools)} different tools")
        print(f"   - ~400 tool usage events")
        
    except Exception as e:
        print(f"❌ Error generating sample data: {e}")
        print("   Dashboard will still work but may show empty data")

def start_performance_monitoring():
    """Start background performance monitoring."""
    try:
        from jarvis.jarvis.core.monitoring.performance_tracker import performance_tracker
        
        print("🔄 Starting performance monitoring...")
        performance_tracker.start_monitoring(interval_seconds=5.0)
        print("✅ Performance monitoring started")
        
    except Exception as e:
        print(f"❌ Error starting performance monitoring: {e}")

def launch_dashboard():
    """Launch the analytics dashboard."""
    try:
        print("🚀 Launching Jarvis Analytics Dashboard...")
        
        # Import and run dashboard
        from jarvis.jarvis.ui.analytics_dashboard import main
        main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure PyQt6 is installed: pip install PyQt6")
        print("   Or install with charts: pip install PyQt6[charts]")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        sys.exit(1)

def main():
    """Main launcher function."""
    print("=" * 60)
    print("🎯 JARVIS USAGE ANALYTICS DASHBOARD LAUNCHER")
    print("=" * 60)
    
    # Check dependencies
    try:
        import PyQt6
        print("✅ PyQt6 found")
    except ImportError:
        print("❌ PyQt6 not found - installing...")
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])
            print("✅ PyQt6 installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyQt6")
            print("   Please install manually: pip install PyQt6")
            sys.exit(1)
    
    # Generate sample data in background
    data_thread = threading.Thread(target=generate_sample_data, daemon=True)
    data_thread.start()
    
    # Start performance monitoring
    monitor_thread = threading.Thread(target=start_performance_monitoring, daemon=True)
    monitor_thread.start()
    
    # Wait a moment for data generation
    print("⏳ Initializing system components...")
    time.sleep(2)
    
    # Launch dashboard
    launch_dashboard()

if __name__ == "__main__":
    main()
