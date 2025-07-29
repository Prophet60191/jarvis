"""
LaVague Web Automation Plugin for Jarvis Voice Assistant.

This plugin provides AI-powered web automation capabilities using LaVague,
allowing users to interact with websites through natural language voice commands.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
import asyncio
import threading

from langchain_core.tools import tool
from jarvis.tools.base import BaseTool
from jarvis.plugins.base import PluginBase, PluginMetadata

# LaVague imports
try:
    from lavague.core import WorldModel, ActionEngine
    from lavague.core.agents import WebAgent
    from lavague.drivers.selenium import SeleniumDriver
    LAVAGUE_AVAILABLE = True
except ImportError as e:
    LAVAGUE_AVAILABLE = False
    LAVAGUE_ERROR = str(e)

logger = logging.getLogger(__name__)


@tool
def web_automation_task(task_description: str, website_url: str = None, headless: bool = True) -> str:
    """
    Perform AI-powered web automation tasks using natural language.
    
    Use this tool when users ask to:
    - "Navigate to [website] and [do something]"
    - "Fill out the form on [website]"
    - "Search for [something] on [website]"
    - "Click the [button/link] on [website]"
    - "Extract information from [website]"
    - "Automate [task] on [website]"
    
    Args:
        task_description: Natural language description of what to do on the website
        website_url: URL of the website to interact with (optional if included in task)
        headless: Run browser in headless mode (default: True for voice commands)
    
    Returns:
        Result of the web automation task
    """
    if not LAVAGUE_AVAILABLE:
        return f"❌ LaVague web automation is not available: {LAVAGUE_ERROR}\n\nPlease install LaVague with: pip install lavague-core lavague-drivers-selenium"
    
    try:
        logger.info(f"Starting web automation task: {task_description}")
        
        # Initialize LaVague components
        selenium_driver = SeleniumDriver(headless=headless)
        world_model = WorldModel()
        action_engine = ActionEngine(selenium_driver)
        agent = WebAgent(world_model, action_engine)
        
        # If website URL is provided, navigate there first
        if website_url:
            logger.info(f"Navigating to: {website_url}")
            selenium_driver.get(website_url)
            
            # Execute the task
            result = agent.run(task_description)
        else:
            # Task should include navigation
            result = agent.run(task_description)
        
        # Take a screenshot for reference
        screenshot_path = _take_screenshot(selenium_driver)
        
        # Clean up
        selenium_driver.driver.quit()
        
        response = f"✅ Web automation task completed successfully!\n\n"
        response += f"📋 Task: {task_description}\n"
        if website_url:
            response += f"🌐 Website: {website_url}\n"
        response += f"📸 Screenshot saved: {screenshot_path}\n\n"
        response += f"🤖 LaVague Result: {result}"
        
        logger.info("Web automation task completed successfully")
        return response
        
    except Exception as e:
        error_msg = f"❌ Web automation task failed: {str(e)}\n\nTask: {task_description}"
        if website_url:
            error_msg += f"\nWebsite: {website_url}"
        logger.error(f"Web automation failed: {e}")
        return error_msg


@tool
def web_scraping_task(website_url: str, data_to_extract: str, headless: bool = True) -> str:
    """
    Extract specific information from a website using AI.
    
    Use this tool when users ask to:
    - "Get the [information] from [website]"
    - "Extract [data] from [website]"
    - "What is the [information] on [website]"
    - "Scrape [data] from [website]"
    
    Args:
        website_url: URL of the website to scrape
        data_to_extract: Description of what information to extract
        headless: Run browser in headless mode (default: True)
    
    Returns:
        Extracted information from the website
    """
    if not LAVAGUE_AVAILABLE:
        return f"❌ LaVague web automation is not available: {LAVAGUE_ERROR}"
    
    try:
        logger.info(f"Starting web scraping task: {data_to_extract} from {website_url}")
        
        # Initialize LaVague components
        selenium_driver = SeleniumDriver(headless=headless)
        world_model = WorldModel()
        action_engine = ActionEngine(selenium_driver)
        agent = WebAgent(world_model, action_engine)
        
        # Navigate to the website
        selenium_driver.get(website_url)
        
        # Create extraction task
        extraction_task = f"Extract the following information: {data_to_extract}"
        result = agent.run(extraction_task)
        
        # Take a screenshot for reference
        screenshot_path = _take_screenshot(selenium_driver)
        
        # Clean up
        selenium_driver.driver.quit()
        
        response = f"✅ Web scraping completed successfully!\n\n"
        response += f"🌐 Website: {website_url}\n"
        response += f"📋 Extracted: {data_to_extract}\n"
        response += f"📸 Screenshot: {screenshot_path}\n\n"
        response += f"📊 Results:\n{result}"
        
        logger.info("Web scraping task completed successfully")
        return response
        
    except Exception as e:
        error_msg = f"❌ Web scraping failed: {str(e)}\n\nWebsite: {website_url}\nData: {data_to_extract}"
        logger.error(f"Web scraping failed: {e}")
        return error_msg


@tool
def web_form_filling(website_url: str, form_data: str, submit_form: bool = False) -> str:
    """
    Fill out web forms automatically using AI.
    
    Use this tool when users ask to:
    - "Fill out the form on [website] with [data]"
    - "Complete the registration on [website]"
    - "Submit my information to [website]"
    
    Args:
        website_url: URL of the website with the form
        form_data: Description of data to fill in the form
        submit_form: Whether to submit the form after filling (default: False for safety)
    
    Returns:
        Result of the form filling operation
    """
    if not LAVAGUE_AVAILABLE:
        return f"❌ LaVague web automation is not available: {LAVAGUE_ERROR}"
    
    try:
        logger.info(f"Starting form filling task on {website_url}")
        
        # Initialize LaVague components
        selenium_driver = SeleniumDriver(headless=True)
        world_model = WorldModel()
        action_engine = ActionEngine(selenium_driver)
        agent = WebAgent(world_model, action_engine)
        
        # Navigate to the website
        selenium_driver.get(website_url)
        
        # Create form filling task
        if submit_form:
            task = f"Fill out the form with the following information and submit it: {form_data}"
        else:
            task = f"Fill out the form with the following information (do not submit): {form_data}"
        
        result = agent.run(task)
        
        # Take a screenshot for reference
        screenshot_path = _take_screenshot(selenium_driver)
        
        # Clean up
        selenium_driver.driver.quit()
        
        response = f"✅ Form filling completed successfully!\n\n"
        response += f"🌐 Website: {website_url}\n"
        response += f"📝 Form Data: {form_data}\n"
        response += f"📤 Submitted: {'Yes' if submit_form else 'No (filled only)'}\n"
        response += f"📸 Screenshot: {screenshot_path}\n\n"
        response += f"🤖 Result: {result}"
        
        logger.info("Form filling task completed successfully")
        return response
        
    except Exception as e:
        error_msg = f"❌ Form filling failed: {str(e)}\n\nWebsite: {website_url}\nData: {form_data}"
        logger.error(f"Form filling failed: {e}")
        return error_msg


@tool
def check_lavague_status() -> str:
    """
    Check if LaVague web automation is available and working.
    
    Use this tool when users ask:
    - "Is web automation working"
    - "Can you browse websites"
    - "Check LaVague status"
    
    Returns:
        Status of LaVague web automation system
    """
    if not LAVAGUE_AVAILABLE:
        return f"❌ LaVague web automation is not available.\n\nError: {LAVAGUE_ERROR}\n\nTo install LaVague:\npip install lavague-core lavague-drivers-selenium"
    
    try:
        # Test basic LaVague functionality
        selenium_driver = SeleniumDriver(headless=True)
        selenium_driver.get("https://example.com")
        title = selenium_driver.driver.title  # Access the underlying WebDriver
        selenium_driver.driver.quit()  # Access the underlying WebDriver
        
        response = "✅ LaVague web automation is working correctly!\n\n"
        response += "🌐 Capabilities:\n"
        response += "• Navigate to websites\n"
        response += "• Fill out forms automatically\n"
        response += "• Extract information from pages\n"
        response += "• Click buttons and links\n"
        response += "• Perform complex web tasks\n\n"
        response += f"🧪 Test Result: Successfully loaded example.com ('{title}')\n\n"
        response += "🎤 Voice Commands:\n"
        response += "• 'Navigate to [website] and [do something]'\n"
        response += "• 'Fill out the form on [website]'\n"
        response += "• 'Extract [information] from [website]'\n"
        response += "• 'Search for [something] on [website]'"
        
        return response
        
    except Exception as e:
        return f"❌ LaVague is installed but not working properly: {str(e)}\n\nPlease check your browser setup and internet connection."


def _take_screenshot(driver) -> str:
    """Take a screenshot and save it to a temporary file."""
    try:
        # Create screenshots directory
        screenshots_dir = Path.home() / "Desktop" / "jarvis_screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = screenshots_dir / f"web_automation_{timestamp}.png"
        
        # Take screenshot
        driver.save_screenshot(str(screenshot_path))
        
        return str(screenshot_path)
        
    except Exception as e:
        logger.warning(f"Failed to take screenshot: {e}")
        return "Screenshot not available"


class LaVagueWebAutomationPlugin(PluginBase):
    """Plugin that provides AI-powered web automation capabilities using LaVague."""
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="LaVagueWebAutomation",
            version="1.0.0",
            description="AI-powered web automation using LaVague for natural language web interactions",
            author="Jarvis Team",
            dependencies=[]  # Dependencies are checked at runtime
        )
    
    def get_tools(self) -> List[BaseTool]:
        """Return the LaVague web automation tools."""
        return [
            web_automation_task,
            web_scraping_task, 
            web_form_filling,
            check_lavague_status
        ]


# Required variables for plugin discovery system
PLUGIN_CLASS = LaVagueWebAutomationPlugin
PLUGIN_METADATA = LaVagueWebAutomationPlugin().get_metadata()
