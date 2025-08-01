"""
Process Management Tools

System-wide tools for process control, application startup, and background task management.
These tools enable Jarvis to start, stop, and manage running applications and processes.
"""

import os
import sys
import subprocess
import psutil
import signal
import time
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from langchain.tools import tool
import threading

from ...plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


@tool
def start_application(file_path: str, background: bool = True, working_directory: str = "") -> str:
    """
    Start a Python application, optionally in the background.
    
    Args:
        file_path: Path to Python application to start
        background: Whether to run in background (default: True)
        working_directory: Working directory for the application
        
    Returns:
        Application startup status and process information
    """
    try:
        logger.info(f"Starting application: {file_path}")
        
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            return f"❌ Application file not found: {file_path}"
        
        # Determine working directory
        if working_directory:
            work_dir = Path(working_directory)
        else:
            work_dir = file_path_obj.parent
        
        if not work_dir.exists():
            return f"❌ Working directory not found: {work_dir}"
        
        # Find Python executable (prefer virtual environment)
        python_cmd = sys.executable
        venv_paths = [
            work_dir / "venv" / "bin" / "python",
            work_dir / "venv" / "Scripts" / "python.exe",
            work_dir / ".venv" / "bin" / "python",
            work_dir / ".venv" / "Scripts" / "python.exe"
        ]
        
        for venv_path in venv_paths:
            if venv_path.exists():
                python_cmd = str(venv_path)
                break
        
        output = f"🚀 Starting Application: {file_path}\n"
        output += "=" * 50 + "\n\n"
        output += f"📁 Working Directory: {work_dir}\n"
        output += f"🐍 Python: {python_cmd}\n"
        output += f"🔄 Background: {background}\n\n"
        
        if background:
            # Start in background
            process = subprocess.Popen([
                python_cmd, str(file_path_obj)
            ], cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Give it a moment to start
            time.sleep(1)
            
            # Check if process is still running
            if process.poll() is None:
                output += f"✅ Application started successfully!\n"
                output += f"🆔 Process ID: {process.pid}\n"
                output += f"🔄 Status: Running in background\n"
                output += f"💡 Use 'stop_process({process.pid})' to stop\n"
            else:
                # Process exited immediately
                stdout, stderr = process.communicate()
                output += f"❌ Application exited immediately\n"
                output += f"🔄 Return Code: {process.returncode}\n"
                if stderr:
                    output += f"⚠️ Error: {stderr.decode()[:200]}...\n"
        else:
            # Run in foreground (blocking)
            output += "⏳ Running application in foreground...\n"
            result = subprocess.run([
                python_cmd, str(file_path_obj)
            ], cwd=work_dir, capture_output=True, text=True)
            
            output += f"🔄 Return Code: {result.returncode}\n"
            
            if result.stdout:
                output += f"📤 Output:\n{result.stdout[:500]}...\n"
            
            if result.stderr:
                output += f"⚠️ Errors:\n{result.stderr[:500]}...\n"
            
            if result.returncode == 0:
                output += "✅ Application completed successfully\n"
            else:
                output += "❌ Application exited with errors\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        return f"❌ Application startup failed: {str(e)}"


@tool
def stop_process(process_id: int, force: bool = False) -> str:
    """
    Stop a running process by its process ID.
    
    Args:
        process_id: Process ID to stop
        force: Whether to force kill the process
        
    Returns:
        Process termination status
    """
    try:
        logger.info(f"Stopping process: {process_id}")
        
        # Check if process exists
        try:
            process = psutil.Process(process_id)
        except psutil.NoSuchProcess:
            return f"❌ Process {process_id} not found"
        
        output = f"🛑 Stopping Process: {process_id}\n"
        output += "=" * 40 + "\n\n"
        
        # Get process info
        try:
            process_name = process.name()
            process_status = process.status()
            output += f"📋 Name: {process_name}\n"
            output += f"🔄 Status: {process_status}\n"
            output += f"💪 Force: {force}\n\n"
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            output += f"⚠️ Limited access to process information\n\n"
        
        # Terminate process
        try:
            if force:
                process.kill()
                action = "killed"
            else:
                process.terminate()
                action = "terminated"
            
            # Wait for process to end
            try:
                process.wait(timeout=5)
                output += f"✅ Process {action} successfully\n"
            except psutil.TimeoutExpired:
                if not force:
                    # Try force kill if terminate didn't work
                    process.kill()
                    process.wait(timeout=3)
                    output += f"✅ Process force killed after timeout\n"
                else:
                    output += f"⚠️ Process may still be running\n"
                    
        except psutil.NoSuchProcess:
            output += f"ℹ️ Process already terminated\n"
        except psutil.AccessDenied:
            output += f"❌ Access denied - cannot terminate process\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Process termination failed: {e}")
        return f"❌ Process termination failed: {str(e)}"


@tool
def list_running_processes(filter_name: str = "") -> str:
    """
    List running processes, optionally filtered by name.
    
    Args:
        filter_name: Filter processes by name (optional)
        
    Returns:
        List of running processes
    """
    try:
        logger.info(f"Listing running processes (filter: {filter_name})")
        
        output = f"📋 Running Processes\n"
        if filter_name:
            output += f"🔍 Filter: {filter_name}\n"
        output += "=" * 50 + "\n\n"
        
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent']):
            try:
                proc_info = proc.info
                
                # Apply filter if specified
                if filter_name and filter_name.lower() not in proc_info['name'].lower():
                    continue
                
                processes.append(proc_info)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not processes:
            if filter_name:
                return output + f"ℹ️ No processes found matching '{filter_name}'\n"
            else:
                return output + f"ℹ️ No processes found\n"
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
        
        # Show top processes
        output += f"📊 Found {len(processes)} processes\n\n"
        output += f"{'PID':<8} {'NAME':<20} {'STATUS':<12} {'CPU%':<8} {'MEM%':<8}\n"
        output += "-" * 60 + "\n"
        
        for proc in processes[:20]:  # Show top 20
            pid = proc.get('pid', 'N/A')
            name = proc.get('name', 'Unknown')[:19]
            status = proc.get('status', 'Unknown')[:11]
            cpu = proc.get('cpu_percent', 0)
            mem = proc.get('memory_percent', 0)
            
            output += f"{pid:<8} {name:<20} {status:<12} {cpu:<8.1f} {mem:<8.1f}\n"
        
        if len(processes) > 20:
            output += f"\n... and {len(processes) - 20} more processes\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Process listing failed: {e}")
        return f"❌ Process listing failed: {str(e)}"


@tool
def check_process_status(process_id: int) -> str:
    """
    Check the status of a specific process.
    
    Args:
        process_id: Process ID to check
        
    Returns:
        Detailed process status information
    """
    try:
        logger.info(f"Checking process status: {process_id}")
        
        try:
            process = psutil.Process(process_id)
        except psutil.NoSuchProcess:
            return f"❌ Process {process_id} not found"
        
        output = f"📊 Process Status: {process_id}\n"
        output += "=" * 40 + "\n\n"
        
        try:
            # Basic info
            output += f"📋 Name: {process.name()}\n"
            output += f"🔄 Status: {process.status()}\n"
            output += f"⏰ Created: {time.ctime(process.create_time())}\n"
            
            # Resource usage
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            output += f"\n💻 RESOURCE USAGE:\n"
            output += f"🔥 CPU: {cpu_percent:.1f}%\n"
            output += f"🧠 Memory: {memory_percent:.1f}% ({memory_info.rss / 1024 / 1024:.1f} MB)\n"
            
            # Process details
            try:
                cmdline = process.cmdline()
                if cmdline:
                    output += f"\n🔧 COMMAND LINE:\n"
                    output += f"{' '.join(cmdline)}\n"
                
                cwd = process.cwd()
                output += f"\n📁 Working Directory: {cwd}\n"
                
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                output += f"\n⚠️ Limited access to process details\n"
            
            # Children processes
            try:
                children = process.children()
                if children:
                    output += f"\n👶 CHILD PROCESSES: {len(children)}\n"
                    for child in children[:5]:  # Show first 5
                        output += f"   🔗 {child.pid}: {child.name()}\n"
                
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            
        except psutil.AccessDenied:
            output += f"❌ Access denied - limited information available\n"
        except psutil.NoSuchProcess:
            output += f"❌ Process terminated during status check\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Process status check failed: {e}")
        return f"❌ Process status check failed: {str(e)}"


@tool
def find_processes_by_name(process_name: str) -> str:
    """
    Find all processes matching a specific name.
    
    Args:
        process_name: Name of process to find
        
    Returns:
        List of matching processes
    """
    try:
        logger.info(f"Finding processes by name: {process_name}")
        
        output = f"🔍 Finding Processes: {process_name}\n"
        output += "=" * 40 + "\n\n"
        
        matching_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'status', 'create_time']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    matching_processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not matching_processes:
            return output + f"ℹ️ No processes found matching '{process_name}'\n"
        
        output += f"📊 Found {len(matching_processes)} matching processes:\n\n"
        
        for proc_info in matching_processes:
            pid = proc_info.get('pid', 'N/A')
            name = proc_info.get('name', 'Unknown')
            status = proc_info.get('status', 'Unknown')
            created = time.ctime(proc_info.get('create_time', 0))
            
            output += f"🔗 PID {pid}: {name}\n"
            output += f"   Status: {status}\n"
            output += f"   Created: {created}\n\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Process search failed: {e}")
        return f"❌ Process search failed: {str(e)}"


class ProcessManagementPlugin(PluginBase):
    """Plugin providing process management and application control tools."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ProcessManagement",
            version="1.0.0",
            description="Process control, application startup, and background task management tools",
            author="Jarvis Team",
            dependencies=["psutil"]
        )
    
    def get_tools(self):
        return [
            start_application,
            stop_process,
            list_running_processes,
            check_process_status,
            find_processes_by_name
        ]
