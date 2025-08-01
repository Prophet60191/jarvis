"""LaVague browser interface for direct browser interactions."""

import asyncio
import logging
import tempfile
import os
import time
from typing import Any, Dict, Optional

from ..context import Context

logger = logging.getLogger(__name__)

class LaVagueBrowser:
    """Browser interface using LaVague for direct browser interactions."""
    
    def __init__(self):
        """Initialize the LaVague browser interface."""
        self._temp_dir = tempfile.mkdtemp(prefix='jarvis_browser_')
        logger.info(f"Created temporary directory for browser files: {self._temp_dir}")
    
    async def display_in_browser(self, html_content: str, context: Context) -> Dict[str, Any]:
        """Display HTML content in a browser window.
        
        Args:
            html_content: HTML content to display
            context: Current context
            
        Returns:
            Dict containing result information
        """
        try:
            # Create a temporary HTML file
            file_path = os.path.join(self._temp_dir, f"page_{int(time.time())}.html")
            
            with open(file_path, 'w') as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Jarvis Browser Interface</title>
                    <style>
                        body {{
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                            margin: 0;
                            padding: 20px;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                        }}
                        .content {{
                            background: white;
                            padding: 2rem;
                            border-radius: 8px;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            text-align: center;
                        }}
                        h1 {{
                            color: #2d3748;
                            margin: 0;
                            font-size: 2.5rem;
                            font-weight: 600;
                        }}
                    </style>
                </head>
                <body>
                    <div class="content">
                        {html_content}
                    </div>
                </body>
                </html>
                """)
            
            # Open the file in the default browser
            import webbrowser
            webbrowser.open(f'file://{file_path}')
            
            return {
                "success": True,
                "file_path": file_path,
                "message": "Content displayed in browser"
            }
            
        except Exception as e:
            logger.error(f"Error displaying content in browser: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def __del__(self):
        """Clean up temporary files on deletion."""
        try:
            import shutil
            shutil.rmtree(self._temp_dir)
            logger.info(f"Cleaned up temporary directory: {self._temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary directory: {e}")
