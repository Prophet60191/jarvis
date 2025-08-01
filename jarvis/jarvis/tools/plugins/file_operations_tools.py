"""
Enhanced File Operations Tools

System-wide tools for comprehensive file and directory operations.
These tools enable Jarvis to read, write, edit, and manage files and directories.
"""

import os
import shutil
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from langchain.tools import tool
import tempfile
import zipfile
import tarfile

from ...plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


@tool
def read_file_content(file_path: str, encoding: str = "utf-8") -> str:
    """
    Read the complete content of a file.
    
    Args:
        file_path: Path to the file to read
        encoding: File encoding (default: utf-8)
        
    Returns:
        File content or error message
    """
    try:
        logger.info(f"Reading file: {file_path}")
        
        path = Path(file_path)
        if not path.exists():
            return f"❌ File not found: {file_path}"
        
        if not path.is_file():
            return f"❌ Path is not a file: {file_path}"
        
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        
        file_size = path.stat().st_size
        line_count = content.count('\n') + 1
        
        output = f"📄 File: {file_path}\n"
        output += f"📊 Size: {file_size} bytes, {line_count} lines\n"
        output += f"🔤 Encoding: {encoding}\n\n"
        output += "📝 CONTENT:\n"
        output += "-" * 40 + "\n"
        output += content
        
        return output
        
    except UnicodeDecodeError:
        return f"❌ Cannot decode file with {encoding} encoding: {file_path}"
    except Exception as e:
        logger.error(f"File reading failed: {e}")
        return f"❌ File reading failed: {str(e)}"


@tool
def write_file_content(file_path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True) -> str:
    """
    Write content to a file, creating directories if needed.
    
    Args:
        file_path: Path where to write the file
        content: Content to write
        encoding: File encoding (default: utf-8)
        create_dirs: Whether to create parent directories
        
    Returns:
        Write operation status
    """
    try:
        logger.info(f"Writing file: {file_path}")
        
        path = Path(file_path)
        
        # Create parent directories if needed
        if create_dirs:
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        
        file_size = path.stat().st_size
        line_count = content.count('\n') + 1
        
        output = f"✅ File written successfully!\n\n"
        output += f"📄 File: {file_path}\n"
        output += f"📊 Size: {file_size} bytes, {line_count} lines\n"
        output += f"🔤 Encoding: {encoding}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"File writing failed: {e}")
        return f"❌ File writing failed: {str(e)}"


@tool
def append_to_file(file_path: str, content: str, encoding: str = "utf-8") -> str:
    """
    Append content to an existing file.
    
    Args:
        file_path: Path to the file
        content: Content to append
        encoding: File encoding (default: utf-8)
        
    Returns:
        Append operation status
    """
    try:
        logger.info(f"Appending to file: {file_path}")
        
        path = Path(file_path)
        
        # Append content
        with open(path, 'a', encoding=encoding) as f:
            f.write(content)
        
        file_size = path.stat().st_size
        
        output = f"✅ Content appended successfully!\n\n"
        output += f"📄 File: {file_path}\n"
        output += f"📊 New size: {file_size} bytes\n"
        output += f"➕ Appended: {len(content)} characters\n"
        
        return output
        
    except Exception as e:
        logger.error(f"File appending failed: {e}")
        return f"❌ File appending failed: {str(e)}"


@tool
def create_directory(directory_path: str, parents: bool = True) -> str:
    """
    Create a directory and optionally its parent directories.
    
    Args:
        directory_path: Path of directory to create
        parents: Whether to create parent directories
        
    Returns:
        Directory creation status
    """
    try:
        logger.info(f"Creating directory: {directory_path}")
        
        path = Path(directory_path)
        
        if path.exists():
            if path.is_dir():
                return f"ℹ️ Directory already exists: {directory_path}"
            else:
                return f"❌ Path exists but is not a directory: {directory_path}"
        
        path.mkdir(parents=parents, exist_ok=True)
        
        output = f"✅ Directory created successfully!\n\n"
        output += f"📁 Directory: {directory_path}\n"
        output += f"🔧 Parents created: {parents}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Directory creation failed: {e}")
        return f"❌ Directory creation failed: {str(e)}"


@tool
def list_directory_contents(directory_path: str, show_hidden: bool = False, recursive: bool = False) -> str:
    """
    List contents of a directory with detailed information.
    
    Args:
        directory_path: Path to directory to list
        show_hidden: Whether to show hidden files (starting with .)
        recursive: Whether to list subdirectories recursively
        
    Returns:
        Directory listing with file details
    """
    try:
        logger.info(f"Listing directory: {directory_path}")
        
        path = Path(directory_path)
        
        if not path.exists():
            return f"❌ Directory not found: {directory_path}"
        
        if not path.is_dir():
            return f"❌ Path is not a directory: {directory_path}"
        
        output = f"📁 Directory: {directory_path}\n"
        output += "=" * 60 + "\n\n"
        
        if recursive:
            items = list(path.rglob('*'))
        else:
            items = list(path.iterdir())
        
        # Filter hidden files if requested
        if not show_hidden:
            items = [item for item in items if not item.name.startswith('.')]
        
        # Sort items: directories first, then files
        items.sort(key=lambda x: (x.is_file(), x.name.lower()))
        
        dirs_count = 0
        files_count = 0
        total_size = 0
        
        for item in items:
            try:
                if item.is_dir():
                    dirs_count += 1
                    output += f"📁 {item.name}/\n"
                else:
                    files_count += 1
                    size = item.stat().st_size
                    total_size += size
                    
                    # Format file size
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.1f} KB"
                    else:
                        size_str = f"{size / (1024 * 1024):.1f} MB"
                    
                    output += f"📄 {item.name} ({size_str})\n"
                    
            except OSError:
                output += f"❓ {item.name} (access denied)\n"
        
        # Summary
        output += f"\n📊 SUMMARY:\n"
        output += f"📁 Directories: {dirs_count}\n"
        output += f"📄 Files: {files_count}\n"
        
        if total_size > 0:
            if total_size < 1024 * 1024:
                size_str = f"{total_size / 1024:.1f} KB"
            else:
                size_str = f"{total_size / (1024 * 1024):.1f} MB"
            output += f"💾 Total size: {size_str}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Directory listing failed: {e}")
        return f"❌ Directory listing failed: {str(e)}"


@tool
def copy_file_or_directory(source_path: str, destination_path: str, overwrite: bool = False) -> str:
    """
    Copy a file or directory to a new location.
    
    Args:
        source_path: Source file or directory path
        destination_path: Destination path
        overwrite: Whether to overwrite existing files
        
    Returns:
        Copy operation status
    """
    try:
        logger.info(f"Copying {source_path} to {destination_path}")
        
        source = Path(source_path)
        destination = Path(destination_path)
        
        if not source.exists():
            return f"❌ Source not found: {source_path}"
        
        if destination.exists() and not overwrite:
            return f"❌ Destination exists (use overwrite=True): {destination_path}"
        
        if source.is_file():
            # Copy file
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            operation = "File copied"
        else:
            # Copy directory
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(source, destination)
            operation = "Directory copied"
        
        output = f"✅ {operation} successfully!\n\n"
        output += f"📂 Source: {source_path}\n"
        output += f"📁 Destination: {destination_path}\n"
        output += f"🔄 Overwrite: {overwrite}\n"
        
        return output
        
    except Exception as e:
        logger.error(f"Copy operation failed: {e}")
        return f"❌ Copy operation failed: {str(e)}"


@tool
def delete_file_or_directory(path: str, force: bool = False) -> str:
    """
    Delete a file or directory.
    
    Args:
        path: Path to file or directory to delete
        force: Whether to force deletion of non-empty directories
        
    Returns:
        Deletion status
    """
    try:
        logger.info(f"Deleting: {path}")
        
        target = Path(path)
        
        if not target.exists():
            return f"❌ Path not found: {path}"
        
        if target.is_file():
            target.unlink()
            operation = "File deleted"
        else:
            if force:
                shutil.rmtree(target)
                operation = "Directory deleted (forced)"
            else:
                target.rmdir()  # Only works for empty directories
                operation = "Empty directory deleted"
        
        output = f"✅ {operation} successfully!\n\n"
        output += f"🗑️ Deleted: {path}\n"
        output += f"💪 Force: {force}\n"
        
        return output
        
    except OSError as e:
        if "Directory not empty" in str(e):
            return f"❌ Directory not empty (use force=True): {path}"
        else:
            return f"❌ Deletion failed: {str(e)}"
    except Exception as e:
        logger.error(f"Deletion failed: {e}")
        return f"❌ Deletion failed: {str(e)}"


@tool
def find_files(directory_path: str, pattern: str = "*", file_type: str = "all") -> str:
    """
    Find files matching a pattern in a directory.
    
    Args:
        directory_path: Directory to search in
        pattern: File pattern to match (e.g., "*.py", "test_*")
        file_type: Type of files to find ("files", "dirs", "all")
        
    Returns:
        List of matching files/directories
    """
    try:
        logger.info(f"Finding files in {directory_path} with pattern {pattern}")
        
        path = Path(directory_path)
        
        if not path.exists():
            return f"❌ Directory not found: {directory_path}"
        
        if not path.is_dir():
            return f"❌ Path is not a directory: {directory_path}"
        
        # Find matching items
        matches = list(path.rglob(pattern))
        
        # Filter by type
        if file_type == "files":
            matches = [m for m in matches if m.is_file()]
        elif file_type == "dirs":
            matches = [m for m in matches if m.is_dir()]
        
        # Sort matches
        matches.sort()
        
        output = f"🔍 Search Results in: {directory_path}\n"
        output += f"🎯 Pattern: {pattern}\n"
        output += f"📋 Type: {file_type}\n"
        output += f"📊 Found: {len(matches)} items\n\n"
        
        if matches:
            for match in matches:
                relative_path = match.relative_to(path)
                if match.is_dir():
                    output += f"📁 {relative_path}/\n"
                else:
                    size = match.stat().st_size
                    if size < 1024:
                        size_str = f"{size} B"
                    elif size < 1024 * 1024:
                        size_str = f"{size / 1024:.1f} KB"
                    else:
                        size_str = f"{size / (1024 * 1024):.1f} MB"
                    output += f"📄 {relative_path} ({size_str})\n"
        else:
            output += "ℹ️ No matching files found.\n"
        
        return output
        
    except Exception as e:
        logger.error(f"File search failed: {e}")
        return f"❌ File search failed: {str(e)}"


class FileOperationsPlugin(PluginBase):
    """Plugin providing enhanced file and directory operations."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="FileOperations",
            version="1.0.0",
            description="Enhanced file and directory operations for comprehensive file management",
            author="Jarvis Team",
            dependencies=[]
        )
    
    def get_tools(self):
        return [
            read_file_content,
            write_file_content,
            append_to_file,
            create_directory,
            list_directory_contents,
            copy_file_or_directory,
            delete_file_or_directory,
            find_files
        ]


@tool
def download_file(url: str, destination_path: str, filename: str = "") -> str:
    """
    Download a file from a URL to a local path.

    Args:
        url: URL to download from
        destination_path: Local directory to save the file
        filename: Optional custom filename (uses URL filename if not provided)

    Returns:
        Download status and file information
    """
    try:
        import requests
        from urllib.parse import urlparse

        logger.info(f"Downloading file from: {url}")

        # Determine filename
        if not filename:
            parsed_url = urlparse(url)
            filename = Path(parsed_url.path).name
            if not filename:
                filename = "downloaded_file"

        dest_dir = Path(destination_path)
        dest_dir.mkdir(parents=True, exist_ok=True)

        file_path = dest_dir / filename

        # Download file
        headers = {
            'User-Agent': 'Mozilla/5.0 (Jarvis Download Bot) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        # Write file in chunks
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = file_path.stat().st_size

        output = f"✅ File downloaded successfully!\n\n"
        output += f"🌐 URL: {url}\n"
        output += f"📁 Destination: {file_path}\n"
        output += f"📊 Size: {file_size} bytes\n"

        # Check content type
        content_type = response.headers.get('content-type', 'unknown')
        output += f"📋 Content Type: {content_type}\n"

        return output

    except requests.RequestException as e:
        return f"❌ Download failed: {str(e)}"
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return f"❌ Download failed: {str(e)}"
