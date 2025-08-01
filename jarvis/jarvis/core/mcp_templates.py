"""
MCP Server Templates for Jarvis Voice Assistant.

This module provides pre-configured templates for popular MCP servers
to make it easy for users to add common integrations.
"""

from typing import Dict, List
from .mcp_client import MCPServerConfig, MCPTransportType


class MCPServerTemplate:
    """Template for an MCP server configuration."""
    
    def __init__(
        self,
        name: str,
        description: str,
        config: MCPServerConfig,
        setup_instructions: str = "",
        required_env_vars: List[str] = None,
        documentation_url: str = ""
    ):
        self.name = name
        self.description = description
        self.config = config
        self.setup_instructions = setup_instructions
        self.required_env_vars = required_env_vars or []
        self.documentation_url = documentation_url


# Pre-configured MCP server templates
MCP_SERVER_TEMPLATES: Dict[str, MCPServerTemplate] = {
    "github": MCPServerTemplate(
        name="GitHub Integration",
        description="Access GitHub repositories, issues, pull requests, and more",
        config=MCPServerConfig(
            name="github",
            transport=MCPTransportType.STDIO,
            command="npx",
            args=["-m", "@modelcontextprotocol/server-github"],
            env={"GITHUB_TOKEN": ""},
            enabled=True
        ),
        setup_instructions="""
1. Install the GitHub MCP server:
   npm install -g @modelcontextprotocol/server-github

2. Create a GitHub Personal Access Token:
   - Go to GitHub Settings > Developer settings > Personal access tokens
   - Generate a new token with appropriate permissions
   - Copy the token

3. Set the GITHUB_TOKEN environment variable to your token
        """.strip(),
        required_env_vars=["GITHUB_TOKEN"],
        documentation_url="https://github.com/modelcontextprotocol/servers/tree/main/src/github"
    ),
    
    "filesystem": MCPServerTemplate(
        name="File System Access",
        description="Read, write, and manage local files and directories",
        config=MCPServerConfig(
            name="filesystem",
            transport=MCPTransportType.STDIO,
            command="npx",
            args=["-m", "@modelcontextprotocol/server-filesystem", "/Users"],
            enabled=True
        ),
        setup_instructions="""
1. Install the Filesystem MCP server:
   npm install -g @modelcontextprotocol/server-filesystem

2. The server will have access to the specified directory (/Users by default)
3. You can modify the path in the arguments to restrict access to specific directories
        """.strip(),
        required_env_vars=[],
        documentation_url="https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem"
    ),
    
    "brave_search": MCPServerTemplate(
        name="Brave Search",
        description="Search the web using Brave Search API",
        config=MCPServerConfig(
            name="brave-search",
            transport=MCPTransportType.STDIO,
            command="npx",
            args=["-m", "@modelcontextprotocol/server-brave-search"],
            env={"BRAVE_API_KEY": ""},
            enabled=True
        ),
        setup_instructions="""
1. Install the Brave Search MCP server:
   npm install -g @modelcontextprotocol/server-brave-search

2. Get a Brave Search API key:
   - Go to https://api.search.brave.com/
   - Sign up for an account
   - Get your API key

3. Set the BRAVE_API_KEY environment variable to your API key
        """.strip(),
        required_env_vars=["BRAVE_API_KEY"],
        documentation_url="https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search"
    ),
    
    "google_drive": MCPServerTemplate(
        name="Google Drive",
        description="Access and manage Google Drive files and folders",
        config=MCPServerConfig(
            name="google-drive",
            transport=MCPTransportType.STDIO,
            command="npx",
            args=["-m", "@modelcontextprotocol/server-gdrive"],
            env={"GOOGLE_APPLICATION_CREDENTIALS": ""},
            enabled=True
        ),
        setup_instructions="""
1. Install the Google Drive MCP server:
   npm install -g @modelcontextprotocol/server-gdrive

2. Set up Google Drive API credentials:
   - Go to Google Cloud Console
   - Create a new project or select existing
   - Enable Google Drive API
   - Create service account credentials
   - Download the JSON credentials file

3. Set GOOGLE_APPLICATION_CREDENTIALS to the path of your credentials file
        """.strip(),
        required_env_vars=["GOOGLE_APPLICATION_CREDENTIALS"],
        documentation_url="https://github.com/modelcontextprotocol/servers/tree/main/src/gdrive"
    ),
    
    "slack": MCPServerTemplate(
        name="Slack Integration",
        description="Send messages and interact with Slack workspaces",
        config=MCPServerConfig(
            name="slack",
            transport=MCPTransportType.STDIO,
            command="npx",
            args=["-m", "@modelcontextprotocol/server-slack"],
            env={"SLACK_BOT_TOKEN": ""},
            enabled=True
        ),
        setup_instructions="""
1. Install the Slack MCP server:
   npm install -g @modelcontextprotocol/server-slack

2. Create a Slack App:
   - Go to https://api.slack.com/apps
   - Create a new app
   - Add bot token scopes (chat:write, channels:read, etc.)
   - Install the app to your workspace

3. Set SLACK_BOT_TOKEN to your bot token (starts with xoxb-)
        """.strip(),
        required_env_vars=["SLACK_BOT_TOKEN"],
        documentation_url="https://github.com/modelcontextprotocol/servers/tree/main/src/slack"
    ),
    
    "postgres": MCPServerTemplate(
        name="PostgreSQL Database",
        description="Query and manage PostgreSQL databases",
        config=MCPServerConfig(
            name="postgres",
            transport=MCPTransportType.STDIO,
            command="npx",
            args=["-m", "@modelcontextprotocol/server-postgres"],
            env={"DATABASE_URL": ""},
            enabled=True
        ),
        setup_instructions="""
1. Install the PostgreSQL MCP server:
   npm install -g @modelcontextprotocol/server-postgres

2. Set up your PostgreSQL connection:
   - Ensure you have a PostgreSQL database running
   - Get your database connection URL

3. Set DATABASE_URL to your PostgreSQL connection string:
   postgresql://username:password@host:port/database
        """.strip(),
        required_env_vars=["DATABASE_URL"],
        documentation_url="https://github.com/modelcontextprotocol/servers/tree/main/src/postgres"
    ),
    
    "sqlite": MCPServerTemplate(
        name="SQLite Database",
        description="Query and manage SQLite databases",
        config=MCPServerConfig(
            name="sqlite",
            transport=MCPTransportType.STDIO,
            command="npx",
            args=["-m", "@modelcontextprotocol/server-sqlite", "/path/to/database.db"],
            enabled=True
        ),
        setup_instructions="""
1. Install the SQLite MCP server:
   npm install -g @modelcontextprotocol/server-sqlite

2. Update the database path in the arguments:
   - Replace "/path/to/database.db" with your actual SQLite database file path
   - The database file will be created if it doesn't exist
        """.strip(),
        required_env_vars=[],
        documentation_url="https://github.com/modelcontextprotocol/servers/tree/main/src/sqlite"
    ),
    
    "memory": MCPServerTemplate(
        name="Memory Storage",
        description="Persistent memory storage for conversations and data",
        config=MCPServerConfig(
            name="memory",
            transport=MCPTransportType.STDIO,
            command="npx",
            args=["-m", "@modelcontextprotocol/server-memory"],
            enabled=True
        ),
        setup_instructions="""
1. Install the Memory MCP server:
   npm install -g @modelcontextprotocol/server-memory

2. The memory server provides persistent storage for:
   - Conversation history
   - User preferences
   - Custom data storage

3. No additional configuration required
        """.strip(),
        required_env_vars=[],
        documentation_url="https://github.com/modelcontextprotocol/servers/tree/main/src/memory"
    ),
    
    "puppeteer": MCPServerTemplate(
        name="Web Automation",
        description="Automate web browsers using Puppeteer",
        config=MCPServerConfig(
            name="puppeteer",
            transport=MCPTransportType.STDIO,
            command="npx",
            args=["-m", "@modelcontextprotocol/server-puppeteer"],
            enabled=True
        ),
        setup_instructions="""
1. Install the Puppeteer MCP server:
   npm install -g @modelcontextprotocol/server-puppeteer

2. The server provides web automation capabilities:
   - Take screenshots
   - Navigate web pages
   - Fill forms
   - Extract data

3. Chrome/Chromium will be downloaded automatically if not present
        """.strip(),
        required_env_vars=[],
        documentation_url="https://github.com/modelcontextprotocol/servers/tree/main/src/puppeteer"
    ),
    
    "everything": MCPServerTemplate(
        name="Everything Search (Windows)",
        description="Search files on Windows using Everything search engine",
        config=MCPServerConfig(
            name="everything",
            transport=MCPTransportType.STDIO,
            command="npx",
            args=["-m", "@modelcontextprotocol/server-everything"],
            enabled=True
        ),
        setup_instructions="""
1. Install Everything search engine:
   - Download from https://www.voidtools.com/
   - Install and run Everything

2. Install the Everything MCP server:
   npm install -g @modelcontextprotocol/server-everything

3. Windows only - provides fast file search capabilities
        """.strip(),
        required_env_vars=[],
        documentation_url="https://github.com/modelcontextprotocol/servers/tree/main/src/everything"
    ),



    "custom_mcp": MCPServerTemplate(
        name="Add Any MCP Server",
        description="Universal template to add any MCP server from mcpservers.org",
        config=MCPServerConfig(
            name="my-custom-mcp",
            transport=MCPTransportType.STDIO,
            command="npx",
            args=["-y", "PACKAGE_NAME_HERE"],
            enabled=True
        ),
        setup_instructions="""
🎯 HOW TO USE THIS TEMPLATE:

1. Visit https://mcpservers.org to browse available MCP servers
2. Find the MCP you want (e.g., Apple Notes, Browser MCP, Calculator, etc.)
3. Replace 'PACKAGE_NAME_HERE' with the actual package name from the website
4. Update the server name to something descriptive
5. Add any required API keys in the Environment Variables section

📋 EXAMPLES:
• Apple Notes: Replace with 'mcp-apple-notes'
• Browser Automation: Replace with 'browsermcp'
• Calculator: Replace with 'mcp-server-calculator'
• Any other MCP from mcpservers.org

✅ Most MCPs are completely FREE and work immediately!
        """.strip(),
        required_env_vars=[],
        documentation_url="https://mcpservers.org"
    )
}


def get_template(template_name: str) -> MCPServerTemplate:
    """Get a specific MCP server template by name."""
    return MCP_SERVER_TEMPLATES.get(template_name)


def get_all_templates() -> Dict[str, MCPServerTemplate]:
    """Get all available MCP server templates."""
    return MCP_SERVER_TEMPLATES.copy()


def get_templates_by_category() -> Dict[str, List[str]]:
    """Get templates organized by category."""
    categories = {
        "Development": ["github", "filesystem"],
        "Search & Web": ["brave_search", "puppeteer", "everything"],
        "Cloud Storage": ["google_drive"],
        "Communication": ["slack"],
        "Databases": ["postgres", "sqlite"],
        "Utilities": ["memory"],
        "Custom": ["custom_mcp"]
    }
    return categories


def create_config_from_template(template_name: str, custom_name: str = None, **overrides) -> MCPServerConfig:
    """
    Create a new MCP server configuration from a template.
    
    Args:
        template_name: Name of the template to use
        custom_name: Custom name for the server (defaults to template name)
        **overrides: Configuration overrides
        
    Returns:
        MCPServerConfig instance
    """
    template = get_template(template_name)
    if not template:
        raise ValueError(f"Template '{template_name}' not found")
    
    # Create a copy of the template config
    config = MCPServerConfig(
        name=custom_name or template.config.name,
        transport=template.config.transport,
        enabled=template.config.enabled,
        command=template.config.command,
        args=template.config.args.copy() if template.config.args else [],
        env=template.config.env.copy() if template.config.env else {},
        cwd=template.config.cwd,
        url=template.config.url,
        headers=template.config.headers.copy() if template.config.headers else {},
        timeout=template.config.timeout
    )
    
    # Apply overrides
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    return config
