"""Browser Manager for Jarvis

This module provides browser management functionality for Jarvis.
"""

import logging
import webbrowser
from typing import Optional

logger = logging.getLogger(__name__)

class BrowserManager:
    """Manages browser operations for Jarvis."""
    
    def __init__(self):
        """Initialize the browser manager."""
        self._browser = None
    
    def open_url(self, url: str) -> None:
        """Open a URL in the default browser.
        
        Args:
            url: The URL to open
        """
        try:
            logger.info(f"Opening URL: {url}")
            webbrowser.open(url)
        except Exception as e:
            logger.error(f"Error opening URL {url}: {e}")
            raise
