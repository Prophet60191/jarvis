"""
Web Research Tools

System-wide tools for internet research, documentation fetching, and web-based information gathering.
These tools enable Jarvis and aider to research current best practices, documentation, and examples.
"""

import requests
import logging
from typing import Dict, Any, List, Optional
from langchain.tools import tool
from bs4 import BeautifulSoup
import json
import re
from urllib.parse import urljoin, urlparse

from jarvis.plugins.base import PluginBase, PluginMetadata

logger = logging.getLogger(__name__)


@tool
def web_search(query: str, num_results: int = 5) -> str:
    """
    Search the web for current information, documentation, and best practices.
    
    Args:
        query: Search query (e.g., "Python tkinter button color change tutorial")
        num_results: Number of results to return (default: 5, max: 10)
        
    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    try:
        # Use DuckDuckGo for web search (no API key required)
        from duckduckgo_search import DDGS
        
        logger.info(f"Searching web for: {query}")
        
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=min(num_results, 10)))
        
        if not results:
            return f"No search results found for: {query}"
        
        formatted_results = f"🔍 Web Search Results for: {query}\n"
        formatted_results += "=" * 60 + "\n\n"
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            url = result.get('href', 'No URL')
            snippet = result.get('body', 'No description')
            
            formatted_results += f"{i}. **{title}**\n"
            formatted_results += f"   URL: {url}\n"
            formatted_results += f"   Description: {snippet[:200]}...\n\n"
        
        return formatted_results
        
    except ImportError:
        return "❌ Web search requires 'duckduckgo-search' package. Install with: pip install duckduckgo-search"
    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return f"❌ Web search failed: {str(e)}"


@tool
def fetch_documentation(url: str, extract_code: bool = True) -> str:
    """
    Fetch and extract content from documentation pages, tutorials, or code examples.
    
    Args:
        url: URL to fetch (documentation, tutorial, GitHub page, etc.)
        extract_code: Whether to extract and highlight code blocks
        
    Returns:
        Cleaned and formatted content from the page
    """
    try:
        logger.info(f"Fetching documentation from: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Jarvis Research Bot) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Extract main content
        content_selectors = [
            'main', 'article', '.content', '.documentation', 
            '.markdown-body', '.post-content', '#content'
        ]
        
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.find('body') or soup
        
        # Extract text content
        text_content = main_content.get_text(separator='\n', strip=True)
        
        # Clean up excessive whitespace
        text_content = re.sub(r'\n\s*\n\s*\n', '\n\n', text_content)
        
        # Extract code blocks if requested
        code_blocks = []
        if extract_code:
            for code in main_content.find_all(['code', 'pre']):
                code_text = code.get_text(strip=True)
                if len(code_text) > 20:  # Only include substantial code blocks
                    code_blocks.append(code_text)
        
        result = f"📄 Documentation from: {url}\n"
        result += "=" * 60 + "\n\n"
        result += text_content[:3000]  # Limit to first 3000 characters
        
        if len(text_content) > 3000:
            result += "\n\n... (content truncated)"
        
        if code_blocks:
            result += "\n\n🔧 CODE EXAMPLES FOUND:\n"
            result += "-" * 30 + "\n"
            for i, code in enumerate(code_blocks[:3], 1):  # Show first 3 code blocks
                result += f"\nExample {i}:\n```\n{code[:500]}\n```\n"
        
        return result
        
    except requests.RequestException as e:
        logger.error(f"Failed to fetch URL {url}: {e}")
        return f"❌ Failed to fetch {url}: {str(e)}"
    except Exception as e:
        logger.error(f"Documentation extraction failed: {e}")
        return f"❌ Documentation extraction failed: {str(e)}"


@tool
def github_search(query: str, language: str = "", num_results: int = 5) -> str:
    """
    Search GitHub for code examples, repositories, and implementations.
    
    Args:
        query: Search query (e.g., "tkinter color changing button")
        language: Programming language filter (e.g., "python", "javascript")
        num_results: Number of results to return (default: 5)
        
    Returns:
        GitHub search results with repository info and code snippets
    """
    try:
        logger.info(f"Searching GitHub for: {query}")
        
        # Build GitHub search URL
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        # Use GitHub's web search (no API key required)
        search_url = f"https://github.com/search?q={requests.utils.quote(search_query)}&type=repositories"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Jarvis Research Bot) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract repository results
        repo_items = soup.find_all('div', class_='Box-row')[:num_results]
        
        if not repo_items:
            return f"No GitHub repositories found for: {query}"
        
        result = f"🐙 GitHub Search Results for: {query}\n"
        result += "=" * 60 + "\n\n"
        
        for i, item in enumerate(repo_items, 1):
            # Extract repository name and URL
            title_link = item.find('a', {'data-testid': 'results-list-repo-path'})
            if not title_link:
                continue
                
            repo_name = title_link.get_text(strip=True)
            repo_url = urljoin('https://github.com', title_link.get('href', ''))
            
            # Extract description
            desc_elem = item.find('p', class_='mb-1')
            description = desc_elem.get_text(strip=True) if desc_elem else "No description"
            
            # Extract language and stars
            lang_elem = item.find('span', {'itemprop': 'programmingLanguage'})
            language_found = lang_elem.get_text(strip=True) if lang_elem else "Unknown"
            
            result += f"{i}. **{repo_name}**\n"
            result += f"   URL: {repo_url}\n"
            result += f"   Language: {language_found}\n"
            result += f"   Description: {description[:150]}...\n\n"
        
        return result
        
    except Exception as e:
        logger.error(f"GitHub search failed: {e}")
        return f"❌ GitHub search failed: {str(e)}"


@tool
def research_best_practices(topic: str, technology: str = "") -> str:
    """
    Research current best practices for a specific technology or development topic.
    
    Args:
        topic: Topic to research (e.g., "GUI button design", "error handling")
        technology: Specific technology (e.g., "tkinter", "react", "python")
        
    Returns:
        Comprehensive research summary with best practices and recommendations
    """
    try:
        logger.info(f"Researching best practices for: {topic} ({technology})")
        
        # Build comprehensive search query
        search_queries = [
            f"{topic} best practices {technology}",
            f"{topic} tutorial {technology} 2024",
            f"how to {topic} {technology} examples"
        ]
        
        all_results = []
        
        for query in search_queries:
            try:
                # Search for each query
                search_result = web_search(query, num_results=3)
                all_results.append(search_result)
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {e}")
                continue
        
        if not all_results:
            return f"❌ Could not research best practices for: {topic}"
        
        # Combine and format results
        result = f"📚 Best Practices Research: {topic}"
        if technology:
            result += f" ({technology})"
        result += "\n" + "=" * 60 + "\n\n"
        
        for i, search_result in enumerate(all_results, 1):
            result += f"🔍 Search {i}:\n{search_result}\n\n"
        
        result += "\n💡 RESEARCH SUMMARY:\n"
        result += "-" * 30 + "\n"
        result += f"Use the above search results to understand current best practices for {topic}.\n"
        result += "Focus on recent tutorials, official documentation, and well-maintained examples.\n"
        
        return result
        
    except Exception as e:
        logger.error(f"Best practices research failed: {e}")
        return f"❌ Best practices research failed: {str(e)}"


class WebResearchPlugin(PluginBase):
    """Plugin providing web research and documentation tools."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="WebResearch",
            version="1.0.0",
            description="Web research, documentation fetching, and GitHub search tools for current information gathering",
            author="Jarvis Team",
            dependencies=["requests", "beautifulsoup4", "duckduckgo-search"]
        )
    
    def get_tools(self):
        return [
            web_search,
            fetch_documentation,
            github_search,
            research_best_practices
        ]
