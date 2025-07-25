"""
Time tool for Jarvis Voice Assistant.

This module provides time-related functionality with timezone support
and proper error handling.
"""

import logging
import datetime
import pytz
from typing import Dict, Any, Optional

from ..exceptions import ToolExecutionError
from .base import BaseTool, ToolResult, create_success_result, create_error_result


logger = logging.getLogger(__name__)


class TimeTool(BaseTool):
    """
    Tool for getting current time in various timezones.
    
    This tool provides time information for different cities and timezones
    with comprehensive timezone support and error handling.
    """
    
    def __init__(self):
        """Initialize the time tool."""
        super().__init__(
            name="get_time",
            description="ALWAYS use this tool to get the current time. Returns time in 12-hour format (AM/PM). "
                       "Get the current time in a specific city or local time if no city specified. "
                       "Supports major cities worldwide with automatic timezone detection. "
                       "NEVER provide time information without using this tool."
        )
        
        # Comprehensive city timezone mapping
        self.city_timezones = {
            # North America
            'new york': 'America/New_York',
            'ny': 'America/New_York',
            'nyc': 'America/New_York',
            'rochester': 'America/New_York',
            'rochester ny': 'America/New_York',
            'boston': 'America/New_York',
            'washington dc': 'America/New_York',
            'dc': 'America/New_York',
            'atlanta': 'America/New_York',
            'miami': 'America/New_York',
            'philadelphia': 'America/New_York',
            'detroit': 'America/New_York',
            
            'chicago': 'America/Chicago',
            'dallas': 'America/Chicago',
            'houston': 'America/Chicago',
            'austin': 'America/Chicago',
            'minneapolis': 'America/Chicago',
            'milwaukee': 'America/Chicago',
            'kansas city': 'America/Chicago',
            'st louis': 'America/Chicago',
            
            'denver': 'America/Denver',
            'phoenix': 'America/Phoenix',
            'salt lake city': 'America/Denver',
            'albuquerque': 'America/Denver',
            
            'los angeles': 'America/Los_Angeles',
            'la': 'America/Los_Angeles',
            'san francisco': 'America/Los_Angeles',
            'sf': 'America/Los_Angeles',
            'seattle': 'America/Los_Angeles',
            'portland': 'America/Los_Angeles',
            'san diego': 'America/Los_Angeles',
            'las vegas': 'America/Los_Angeles',
            
            # Canada
            'toronto': 'America/Toronto',
            'vancouver': 'America/Vancouver',
            'montreal': 'America/Montreal',
            'calgary': 'America/Edmonton',
            'ottawa': 'America/Toronto',
            
            # Europe
            'london': 'Europe/London',
            'paris': 'Europe/Paris',
            'berlin': 'Europe/Berlin',
            'rome': 'Europe/Rome',
            'madrid': 'Europe/Madrid',
            'amsterdam': 'Europe/Amsterdam',
            'brussels': 'Europe/Brussels',
            'vienna': 'Europe/Vienna',
            'zurich': 'Europe/Zurich',
            'stockholm': 'Europe/Stockholm',
            'oslo': 'Europe/Oslo',
            'copenhagen': 'Europe/Copenhagen',
            'helsinki': 'Europe/Helsinki',
            'warsaw': 'Europe/Warsaw',
            'prague': 'Europe/Prague',
            'budapest': 'Europe/Budapest',
            'moscow': 'Europe/Moscow',
            'istanbul': 'Europe/Istanbul',
            'athens': 'Europe/Athens',
            'lisbon': 'Europe/Lisbon',
            'dublin': 'Europe/Dublin',
            
            # Asia
            'tokyo': 'Asia/Tokyo',
            'beijing': 'Asia/Shanghai',
            'shanghai': 'Asia/Shanghai',
            'hong kong': 'Asia/Hong_Kong',
            'singapore': 'Asia/Singapore',
            'mumbai': 'Asia/Kolkata',
            'delhi': 'Asia/Kolkata',
            'bangalore': 'Asia/Kolkata',
            'kolkata': 'Asia/Kolkata',
            'dubai': 'Asia/Dubai',
            'riyadh': 'Asia/Riyadh',
            'tehran': 'Asia/Tehran',
            'bangkok': 'Asia/Bangkok',
            'jakarta': 'Asia/Jakarta',
            'manila': 'Asia/Manila',
            'seoul': 'Asia/Seoul',
            'taipei': 'Asia/Taipei',
            'kuala lumpur': 'Asia/Kuala_Lumpur',
            
            # Australia & Oceania
            'sydney': 'Australia/Sydney',
            'melbourne': 'Australia/Melbourne',
            'brisbane': 'Australia/Brisbane',
            'perth': 'Australia/Perth',
            'adelaide': 'Australia/Adelaide',
            'auckland': 'Pacific/Auckland',
            'wellington': 'Pacific/Auckland',
            
            # Africa
            'cairo': 'Africa/Cairo',
            'johannesburg': 'Africa/Johannesburg',
            'cape town': 'Africa/Johannesburg',
            'lagos': 'Africa/Lagos',
            'nairobi': 'Africa/Nairobi',
            'casablanca': 'Africa/Casablanca',
            
            # South America
            'sao paulo': 'America/Sao_Paulo',
            'rio de janeiro': 'America/Sao_Paulo',
            'buenos aires': 'America/Argentina/Buenos_Aires',
            'mexico city': 'America/Mexico_City',
            'lima': 'America/Lima',
            'bogota': 'America/Bogota',
            'santiago': 'America/Santiago',
            'caracas': 'America/Caracas'
        }
        
        self.set_metadata("version", "2.0")
        self.set_metadata("timezone_count", len(self.city_timezones))
        
        logger.debug(f"TimeTool initialized with {len(self.city_timezones)} city mappings")
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get tool parameter schema.
        
        Returns:
            Dictionary describing tool parameters
        """
        return {
            "city": {
                "type": "string",
                "description": "Name of the city to get time for. If empty or not provided, returns local time.",
                "required": False,
                "default": "",
                "examples": ["New York", "London", "Tokyo", "Sydney", ""]
            }
        }
    
    def validate_parameters(self, **kwargs) -> bool:
        """
        Validate tool parameters.
        
        Args:
            **kwargs: Parameters to validate
            
        Returns:
            True if parameters are valid, False otherwise
        """
        # City parameter is optional, so any value (including None/empty) is valid
        city = kwargs.get("city", "")
        return isinstance(city, (str, type(None)))
    
    def execute(self, city: str = "") -> ToolResult:
        """
        Execute the time tool.
        
        Args:
            city: Name of the city to get time for
            
        Returns:
            ToolResult containing time information
        """
        try:
            logger.debug(f"Getting time for city: '{city}'")
            
            if not city or city.strip() == "":
                # Return local time
                result = self._get_local_time()
            else:
                # Return time for specified city
                result = self._get_city_time(city.strip())
            
            return create_success_result(
                data=result,
                metadata={
                    "city": city,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "tool_version": self.get_metadata("version")
                }
            )
            
        except Exception as e:
            logger.error(f"TimeTool execution failed: {str(e)}")
            return create_error_result(
                error=ToolExecutionError(f"Failed to get time: {str(e)}", tool_name=self.name),
                metadata={"city": city}
            )
    
    def _get_local_time(self) -> str:
        """
        Get local time.
        
        Returns:
            Formatted local time string
        """
        now = datetime.datetime.now()
        return f"The current local time is {now.strftime('%I:%M %p on %A, %B %d, %Y')}"
    
    def _get_city_time(self, city: str) -> str:
        """
        Get time for a specific city.
        
        Args:
            city: City name
            
        Returns:
            Formatted time string for the city
            
        Raises:
            ToolExecutionError: If city timezone is not found
        """
        # Normalize city name
        city_lower = city.lower().strip()
        
        # Find timezone
        timezone_name = self._find_timezone(city_lower)
        
        if not timezone_name:
            # Try to provide helpful suggestions
            suggestions = self._get_city_suggestions(city_lower)
            suggestion_text = ""
            if suggestions:
                suggestion_text = f" Did you mean: {', '.join(suggestions[:3])}?"
            
            raise ToolExecutionError(
                f"Sorry, I don't have timezone information for '{city}'. "
                f"I can help with major cities like New York, London, Tokyo, etc.{suggestion_text}"
            )
        
        # Get time in specified timezone
        tz = pytz.timezone(timezone_name)
        now = datetime.datetime.now(tz)
        
        # Format the response
        formatted_time = now.strftime('%I:%M %p on %A, %B %d, %Y')
        return f"The current time in {city.title()} is {formatted_time}"
    
    def _find_timezone(self, city_lower: str) -> Optional[str]:
        """
        Find timezone for a city.
        
        Args:
            city_lower: Lowercase city name
            
        Returns:
            Timezone name or None if not found
        """
        # Direct match
        if city_lower in self.city_timezones:
            return self.city_timezones[city_lower]
        
        # Partial matching for common variations
        for city_key, tz in self.city_timezones.items():
            if city_lower in city_key or city_key in city_lower:
                return tz
        
        return None
    
    def _get_city_suggestions(self, city_lower: str) -> list:
        """
        Get city suggestions based on partial matching.
        
        Args:
            city_lower: Lowercase city name
            
        Returns:
            List of suggested city names
        """
        suggestions = []
        
        # Find cities that contain the search term or vice versa
        for city_key in self.city_timezones.keys():
            if (len(city_lower) >= 3 and city_lower in city_key) or \
               (len(city_key) >= 3 and city_key in city_lower):
                suggestions.append(city_key.title())
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_supported_cities(self) -> list:
        """
        Get list of all supported cities.
        
        Returns:
            List of supported city names
        """
        return sorted([city.title() for city in self.city_timezones.keys()])
    
    def add_city_timezone(self, city: str, timezone: str) -> bool:
        """
        Add a new city-timezone mapping.
        
        Args:
            city: City name
            timezone: Timezone identifier (e.g., 'America/New_York')
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Validate timezone
            pytz.timezone(timezone)
            
            # Add mapping
            self.city_timezones[city.lower().strip()] = timezone
            self.set_metadata("timezone_count", len(self.city_timezones))
            
            logger.info(f"Added city-timezone mapping: {city} -> {timezone}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add city-timezone mapping: {str(e)}")
            return False
