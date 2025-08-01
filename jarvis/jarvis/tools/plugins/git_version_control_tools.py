"""
Git & Version Control Tools

System-wide tools for Git operations and version control management.
These tools enable Jarvis to initialize repositories, commit changes, and manage version control.
"""

import os
import subprocess
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from langchain.tools import tool

from ...plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


@tool
def git_init_repository(project_path: str, initial_commit: bool = True) -> str:
    """
    Initialize a Git repository in a project directory.
    
    Args:
        project_path: Path to the project directory
        initial_commit: Whether to create an initial commit
        
    Returns:
        Git initialization status
    """
    try:
        logger.info(f"Initializing Git repository in: {project_path}")
        
        project_dir = Path(project_path)
        if not project_dir.exists():
            return f"❌ Project directory not found: {project_path}"
        
        # Initialize Git repository
        result = subprocess.run([
            "git", "init"
        ], cwd=project_dir, capture_output=True, text=True)
        
        if result.returncode != 0:
            return f"❌ Git init failed: {result.stderr}"
        
        output = f"✅ Git repository initialized!\n\n"
        output += f"📁 Repository: {project_path}\n"
        
        # Create initial commit if requested
        if initial_commit:
            # Add .gitignore if it doesn't exist
            gitignore_path = project_dir / ".gitignore"
            if not gitignore_path.exists():
                gitignore_content = """__pycache__/
*.pyc
*.pyo
*.pyd
.Python
venv/
.venv/
.env
.DS_Store
*.log
node_modules/
dist/
build/
"""
                with open(gitignore_path, 'w') as f:
                    f.write(gitignore_content)
                output += "📄 Created .gitignore file\n"
            
            # Add all files
            add_result = subprocess.run([
                "git", "add", "."
            ], cwd=project_dir, capture_output=True, text=True)
            
            if add_result.returncode == 0:
                # Create initial commit
                commit_result = subprocess.run([
                    "git", "commit", "-m", "Initial commit"
                ], cwd=project_dir, capture_output=True, text=True)
                
                if commit_result.returncode == 0:
                    output += "✅ Initial commit created\n"
                else:
                    output += f"⚠️ Initial commit failed: {commit_result.stderr}\n"
            else:
                output += f"⚠️ Git add failed: {add_result.stderr}\n"
        
        return output
        
    except FileNotFoundError:
        return "❌ Git not found. Please install Git first."
    except Exception as e:
        logger.error(f"Git init failed: {e}")
        return f"❌ Git init failed: {str(e)}"


@tool
def git_add_and_commit(project_path: str, commit_message: str, files: str = ".") -> str:
    """
    Add files and create a Git commit.
    
    Args:
        project_path: Path to the Git repository
        commit_message: Commit message
        files: Files to add (default: "." for all files)
        
    Returns:
        Git commit status
    """
    try:
        logger.info(f"Creating Git commit in: {project_path}")
        
        project_dir = Path(project_path)
        if not project_dir.exists():
            return f"❌ Project directory not found: {project_path}"
        
        # Check if it's a Git repository
        git_dir = project_dir / ".git"
        if not git_dir.exists():
            return f"❌ Not a Git repository: {project_path}"
        
        # Add files
        add_result = subprocess.run([
            "git", "add", files
        ], cwd=project_dir, capture_output=True, text=True)
        
        if add_result.returncode != 0:
            return f"❌ Git add failed: {add_result.stderr}"
        
        # Create commit
        commit_result = subprocess.run([
            "git", "commit", "-m", commit_message
        ], cwd=project_dir, capture_output=True, text=True)
        
        if commit_result.returncode != 0:
            if "nothing to commit" in commit_result.stdout:
                return "ℹ️ No changes to commit"
            else:
                return f"❌ Git commit failed: {commit_result.stderr}"
        
        # Get commit hash
        hash_result = subprocess.run([
            "git", "rev-parse", "HEAD"
        ], cwd=project_dir, capture_output=True, text=True)
        
        commit_hash = hash_result.stdout.strip()[:8] if hash_result.returncode == 0 else "unknown"
        
        output = f"✅ Git commit created successfully!\n\n"
        output += f"📁 Repository: {project_path}\n"
        output += f"💬 Message: {commit_message}\n"
        output += f"🔗 Commit: {commit_hash}\n"
        output += f"📄 Files: {files}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Git commit failed: {e}")
        return f"❌ Git commit failed: {str(e)}"


@tool
def git_status(project_path: str) -> str:
    """
    Get Git repository status.
    
    Args:
        project_path: Path to the Git repository
        
    Returns:
        Git status information
    """
    try:
        logger.info(f"Getting Git status for: {project_path}")
        
        project_dir = Path(project_path)
        if not project_dir.exists():
            return f"❌ Project directory not found: {project_path}"
        
        # Check if it's a Git repository
        git_dir = project_dir / ".git"
        if not git_dir.exists():
            return f"❌ Not a Git repository: {project_path}"
        
        # Get status
        status_result = subprocess.run([
            "git", "status", "--porcelain"
        ], cwd=project_dir, capture_output=True, text=True)
        
        if status_result.returncode != 0:
            return f"❌ Git status failed: {status_result.stderr}"
        
        # Get branch info
        branch_result = subprocess.run([
            "git", "branch", "--show-current"
        ], cwd=project_dir, capture_output=True, text=True)
        
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        
        # Get last commit
        log_result = subprocess.run([
            "git", "log", "-1", "--oneline"
        ], cwd=project_dir, capture_output=True, text=True)
        
        last_commit = log_result.stdout.strip() if log_result.returncode == 0 else "No commits"
        
        output = f"📊 Git Status: {project_path}\n"
        output += "=" * 50 + "\n\n"
        output += f"🌿 Branch: {current_branch}\n"
        output += f"📝 Last Commit: {last_commit}\n\n"
        
        if status_result.stdout.strip():
            output += "📋 CHANGES:\n"
            for line in status_result.stdout.strip().split('\n'):
                status_code = line[:2]
                filename = line[3:]
                
                if status_code == "??":
                    output += f"❓ Untracked: {filename}\n"
                elif status_code == " M":
                    output += f"📝 Modified: {filename}\n"
                elif status_code == "A ":
                    output += f"➕ Added: {filename}\n"
                elif status_code == " D":
                    output += f"🗑️ Deleted: {filename}\n"
                else:
                    output += f"🔄 {status_code}: {filename}\n"
        else:
            output += "✅ Working directory clean\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Git status failed: {e}")
        return f"❌ Git status failed: {str(e)}"


@tool
def git_create_branch(project_path: str, branch_name: str, switch_to_branch: bool = True) -> str:
    """
    Create a new Git branch.
    
    Args:
        project_path: Path to the Git repository
        branch_name: Name of the new branch
        switch_to_branch: Whether to switch to the new branch
        
    Returns:
        Branch creation status
    """
    try:
        logger.info(f"Creating Git branch '{branch_name}' in: {project_path}")
        
        project_dir = Path(project_path)
        if not project_dir.exists():
            return f"❌ Project directory not found: {project_path}"
        
        # Check if it's a Git repository
        git_dir = project_dir / ".git"
        if not git_dir.exists():
            return f"❌ Not a Git repository: {project_path}"
        
        if switch_to_branch:
            # Create and switch to branch
            result = subprocess.run([
                "git", "checkout", "-b", branch_name
            ], cwd=project_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                return f"❌ Branch creation failed: {result.stderr}"
            
            action = "created and switched to"
        else:
            # Just create branch
            result = subprocess.run([
                "git", "branch", branch_name
            ], cwd=project_dir, capture_output=True, text=True)
            
            if result.returncode != 0:
                return f"❌ Branch creation failed: {result.stderr}"
            
            action = "created"
        
        output = f"✅ Branch {action} successfully!\n\n"
        output += f"📁 Repository: {project_path}\n"
        output += f"🌿 Branch: {branch_name}\n"
        output += f"🔄 Switched: {switch_to_branch}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Git branch creation failed: {e}")
        return f"❌ Git branch creation failed: {str(e)}"


@tool
def git_log(project_path: str, num_commits: int = 5) -> str:
    """
    Get Git commit history.
    
    Args:
        project_path: Path to the Git repository
        num_commits: Number of recent commits to show
        
    Returns:
        Git commit history
    """
    try:
        logger.info(f"Getting Git log for: {project_path}")
        
        project_dir = Path(project_path)
        if not project_dir.exists():
            return f"❌ Project directory not found: {project_path}"
        
        # Check if it's a Git repository
        git_dir = project_dir / ".git"
        if not git_dir.exists():
            return f"❌ Not a Git repository: {project_path}"
        
        # Get commit log
        result = subprocess.run([
            "git", "log", f"-{num_commits}", "--oneline", "--decorate"
        ], cwd=project_dir, capture_output=True, text=True)
        
        if result.returncode != 0:
            return f"❌ Git log failed: {result.stderr}"
        
        output = f"📜 Git Commit History: {project_path}\n"
        output += "=" * 50 + "\n\n"
        
        if result.stdout.strip():
            output += f"📋 Last {num_commits} commits:\n"
            for line in result.stdout.strip().split('\n'):
                output += f"🔗 {line}\n"
        else:
            output += "ℹ️ No commits found\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Git log failed: {e}")
        return f"❌ Git log failed: {str(e)}"


class GitVersionControlPlugin(PluginBase):
    """Plugin providing Git and version control tools."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="GitVersionControl",
            version="1.0.0",
            description="Git operations and version control management tools",
            author="Jarvis Team",
            dependencies=[]
        )
    
    def get_tools(self):
        return [
            git_init_repository,
            git_add_and_commit,
            git_status,
            git_create_branch,
            git_log
        ]
