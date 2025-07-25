"""
Video content creation tool for Jarvis Voice Assistant.

This module provides video content creation advice and suggestions
based on current trends and best practices.
"""

import logging
import datetime
import random
from typing import Dict, Any, List

from ..exceptions import ToolExecutionError
from .base import BaseTool, ToolResult, create_success_result, create_error_result


logger = logging.getLogger(__name__)


class VideoTool(BaseTool):
    """
    Tool for providing video content creation advice and suggestions.
    
    This tool offers day-specific content ideas, trending topics,
    and general video creation tips.
    """
    
    def __init__(self):
        """Initialize the video tool."""
        super().__init__(
            name="video_day",
            description="Get advice and suggestions for video content creation based on the current day, "
                       "including trending topics and best practices."
        )
        
        # Day-specific video content suggestions
        self.day_suggestions = {
            'Monday': [
                "Monday Motivation videos perform well - share inspiring stories or productivity tips",
                "Start the week with 'Monday Mindset' content about goal setting",
                "Tutorial Mondays are great for educational content",
                "Behind-the-scenes content showing your weekly planning process",
                "Monday Morning Routines - share how successful people start their week",
                "Motivational Monday - feature success stories or overcoming challenges"
            ],
            'Tuesday': [
                "Tuesday is perfect for technical tutorials and how-to videos",
                "Transformation Tuesday content showing before/after or progress updates",
                "Tool Tuesday - showcase useful software, apps, or equipment",
                "Q&A Tuesday responding to audience questions",
                "Tutorial Tuesday for in-depth educational content",
                "Tech Tuesday - review new gadgets or software"
            ],
            'Wednesday': [
                "Wednesday Wisdom - share insights, lessons learned, or expert advice",
                "Mid-week motivation content to help people push through",
                "Workflow Wednesday showing your creative process",
                "Collaboration content - interviews or guest appearances work well",
                "Wednesday Wind-down - relaxing or stress-relief content",
                "What's Working Wednesday - share successful strategies"
            ],
            'Thursday': [
                "Throwback Thursday content reviewing past projects or memories",
                "Thursday Thoughts - opinion pieces or commentary on industry trends",
                "Tutorial Thursday for in-depth educational content",
                "Planning content for the upcoming weekend",
                "Thursday Theory - explain complex concepts simply",
                "Thankful Thursday - gratitude and appreciation content"
            ],
            'Friday': [
                "Friday Fun content - lighter, entertaining videos",
                "Week recap or Friday Favorites highlighting the best of the week",
                "Friday Features showcasing community content or user submissions",
                "Weekend preparation content or Friday wind-down videos",
                "Friday Fails - learning from mistakes (if appropriate for your niche)",
                "Fun Friday - games, challenges, or interactive content"
            ],
            'Saturday': [
                "Saturday is great for longer-form content when people have more time",
                "Weekend projects, DIY content, or creative challenges",
                "Saturday Spotlight featuring other creators or community members",
                "Relaxed, casual content like vlogs or personal stories",
                "Saturday Sessions - deep dives into topics of interest",
                "Social Saturday - community engagement and interaction"
            ],
            'Sunday': [
                "Sunday Setup content for the upcoming week",
                "Sunday Reflection videos looking back on achievements",
                "Planning and goal-setting content for the new week",
                "Sunday Funday - family-friendly or community-focused content",
                "Sunday Stories - personal narratives or case studies",
                "Self-care Sunday - wellness and mental health content"
            ]
        }
        
        # General video creation tips
        self.general_tips = [
            "Post consistently at the same time your audience is most active",
            "Use trending hashtags relevant to your niche",
            "Engage with your audience in the comments within the first hour",
            "Create eye-catching thumbnails with bright colors and clear text",
            "Keep your intro under 15 seconds to maintain viewer attention",
            "End with a clear call-to-action (like, subscribe, comment)",
            "Use good lighting - natural light or a ring light works well",
            "Ensure clear audio quality - invest in a decent microphone",
            "Tell a story - even educational content benefits from narrative structure",
            "Hook viewers in the first 3 seconds with a compelling opening",
            "Use the 'rule of thirds' for better visual composition",
            "Add captions or subtitles to make content accessible",
            "Optimize your video title for search with relevant keywords",
            "Create playlists to increase watch time and session duration",
            "Collaborate with other creators in your niche",
            "Analyze your analytics to understand what content performs best",
            "Batch create content to maintain consistency",
            "Use trending audio or music (where appropriate and licensed)",
            "Create content series to build anticipation and return viewers",
            "Repurpose content across different platforms with platform-specific optimizations"
        ]
        
        # Trending content categories
        self.trending_topics = [
            "AI and Technology",
            "Productivity and Life Hacks",
            "Remote Work and Digital Nomad Life",
            "Sustainable Living and Eco-Friendly Tips",
            "Mental Health and Wellness",
            "Creative Process and Behind-the-Scenes",
            "Industry Insights and Expert Interviews",
            "Tool Reviews and Comparisons",
            "Personal Development and Growth",
            "Community Highlights and User-Generated Content",
            "Educational Content and Skill Building",
            "Trend Analysis and Future Predictions",
            "Problem-Solving and Troubleshooting",
            "Success Stories and Case Studies",
            "Interactive Content and Live Streams"
        ]
        
        # Platform-specific tips
        self.platform_tips = {
            "YouTube": [
                "Focus on longer-form content (8+ minutes for better monetization)",
                "Use YouTube Shorts for quick tips and teasers",
                "Create compelling thumbnails that stand out in search results",
                "Optimize for YouTube SEO with keywords in title, description, and tags"
            ],
            "TikTok": [
                "Keep videos under 60 seconds for maximum engagement",
                "Use trending sounds and effects",
                "Post at peak times (6-10 PM in your audience's timezone)",
                "Jump on trending challenges and hashtags quickly"
            ],
            "Instagram": [
                "Use Instagram Reels for maximum reach",
                "Post Stories regularly to stay top-of-mind",
                "Use relevant hashtags (mix of popular and niche)",
                "Engage with your community through comments and DMs"
            ],
            "LinkedIn": [
                "Focus on professional development and industry insights",
                "Share behind-the-scenes of your work process",
                "Create educational content that adds value to professionals",
                "Use LinkedIn native video for better reach"
            ]
        }
        
        self.set_metadata("version", "2.0")
        self.set_metadata("suggestion_count", sum(len(suggestions) for suggestions in self.day_suggestions.values()))
        
        logger.debug(f"VideoTool initialized with {self.get_metadata('suggestion_count')} suggestions")
    
    def get_parameters(self) -> Dict[str, Any]:
        """
        Get tool parameter schema.
        
        Returns:
            Dictionary describing tool parameters
        """
        return {
            "topic": {
                "type": "string",
                "description": "Specific topic or theme for video content advice. If not provided, gives general daily advice.",
                "required": False,
                "default": "",
                "examples": ["productivity", "technology", "wellness", "education"]
            },
            "platform": {
                "type": "string",
                "description": "Target platform for the video content (YouTube, TikTok, Instagram, LinkedIn).",
                "required": False,
                "default": "",
                "examples": ["YouTube", "TikTok", "Instagram", "LinkedIn"]
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
        topic = kwargs.get("topic", "")
        platform = kwargs.get("platform", "")
        
        # Both parameters are optional strings
        return (isinstance(topic, (str, type(None))) and 
                isinstance(platform, (str, type(None))))
    
    def execute(self, topic: str = "", platform: str = "") -> ToolResult:
        """
        Execute the video tool.
        
        Args:
            topic: Specific topic for content advice
            platform: Target platform for the content
            
        Returns:
            ToolResult containing video content advice
        """
        try:
            logger.debug(f"Getting video advice for topic: '{topic}', platform: '{platform}'")
            
            now = datetime.datetime.now()
            day_name = now.strftime('%A')
            
            # Build response
            response_parts = []
            
            # Day-specific suggestion
            day_suggestion = self._get_day_suggestion(day_name, topic)
            response_parts.append(f"For {day_name} video content: {day_suggestion}")
            
            # Platform-specific tip if requested
            if platform:
                platform_tip = self._get_platform_tip(platform)
                if platform_tip:
                    response_parts.append(f"\n{platform} tip: {platform_tip}")
            
            # General tip
            general_tip = random.choice(self.general_tips)
            response_parts.append(f"\nPro tip: {general_tip}")
            
            # Trending topic suggestion
            trending_topic = random.choice(self.trending_topics)
            response_parts.append(f"\nTrending topic to consider: {trending_topic}")
            
            # Analytics reminder
            response_parts.append(f"\nRemember to check your analytics to see when your audience is most active on {day_name}s!")
            
            response = "".join(response_parts)
            
            return create_success_result(
                data=response,
                metadata={
                    "day": day_name,
                    "topic": topic,
                    "platform": platform,
                    "timestamp": now.isoformat(),
                    "tool_version": self.get_metadata("version")
                }
            )
            
        except Exception as e:
            logger.error(f"VideoTool execution failed: {str(e)}")
            return create_error_result(
                error=ToolExecutionError(f"Failed to get video advice: {str(e)}", tool_name=self.name),
                metadata={"topic": topic, "platform": platform}
            )
    
    def _get_day_suggestion(self, day_name: str, topic: str = "") -> str:
        """
        Get day-specific suggestion, optionally filtered by topic.
        
        Args:
            day_name: Name of the day
            topic: Optional topic filter
            
        Returns:
            Day-specific suggestion
        """
        suggestions = self.day_suggestions.get(day_name, ["Great day for creating content!"])
        
        if topic:
            # Filter suggestions by topic if possible
            topic_lower = topic.lower()
            filtered_suggestions = [
                s for s in suggestions 
                if topic_lower in s.lower()
            ]
            if filtered_suggestions:
                suggestions = filtered_suggestions
        
        return random.choice(suggestions)
    
    def _get_platform_tip(self, platform: str) -> str:
        """
        Get platform-specific tip.
        
        Args:
            platform: Platform name
            
        Returns:
            Platform-specific tip or empty string if platform not found
        """
        platform_key = platform.title()
        if platform_key in self.platform_tips:
            return random.choice(self.platform_tips[platform_key])
        return ""
    
    def get_trending_topics(self) -> List[str]:
        """
        Get list of trending topics.
        
        Returns:
            List of trending topic suggestions
        """
        return self.trending_topics.copy()
    
    def get_platform_tips(self, platform: str) -> List[str]:
        """
        Get all tips for a specific platform.
        
        Args:
            platform: Platform name
            
        Returns:
            List of platform-specific tips
        """
        platform_key = platform.title()
        return self.platform_tips.get(platform_key, [])
    
    def get_day_suggestions(self, day: str) -> List[str]:
        """
        Get all suggestions for a specific day.
        
        Args:
            day: Day name
            
        Returns:
            List of day-specific suggestions
        """
        return self.day_suggestions.get(day, [])
    
    def add_suggestion(self, day: str, suggestion: str) -> bool:
        """
        Add a new suggestion for a specific day.
        
        Args:
            day: Day name
            suggestion: New suggestion to add
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            if day not in self.day_suggestions:
                self.day_suggestions[day] = []
            
            self.day_suggestions[day].append(suggestion)
            self.set_metadata("suggestion_count", sum(len(suggestions) for suggestions in self.day_suggestions.values()))
            
            logger.info(f"Added suggestion for {day}: {suggestion}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add suggestion: {str(e)}")
            return False
    
    def add_trending_topic(self, topic: str) -> bool:
        """
        Add a new trending topic.
        
        Args:
            topic: New trending topic to add
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            if topic not in self.trending_topics:
                self.trending_topics.append(topic)
                logger.info(f"Added trending topic: {topic}")
                return True
            else:
                logger.debug(f"Trending topic already exists: {topic}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to add trending topic: {str(e)}")
            return False
