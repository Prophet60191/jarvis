# MCP Troubleshooting Guide

## Common Issues and Solutions

### Server Connection Issues

#### Problem: Server Won't Connect
**Symptoms:**
- Server status shows "Error" or "Disconnected"
- "Connection failed" error messages
- Tools not appearing in tool list

**Solutions:**

1. **Check Prerequisites**
   ```bash
   # Verify Node.js installation
   node --version
   npm --version
   
   # Check if MCP server is installed
   npm list -g | grep modelcontextprotocol
   ```

2. **Test Command Manually**
   ```bash
   # Test the exact command from your configuration
   npx -m @modelcontextprotocol/server-github
   
   # Should show initialization message, not errors
   ```

3. **Verify Environment Variables**
   ```bash
   # Check if environment variables are set
   echo $GITHUB_TOKEN
   echo $BRAVE_API_KEY
   
   # Set if missing
   export GITHUB_TOKEN="your_token_here"
   ```

4. **Check Jarvis Logs**
   ```bash
   # View detailed error messages
   tail -f jarvis_debug.log | grep mcp
   ```

#### Problem: "Command not found" Error
**Symptoms:**
- Error: "Command 'npx' not found"
- Server fails to start

**Solutions:**

1. **Install Node.js**
   ```bash
   # macOS with Homebrew
   brew install node
   
   # Ubuntu/Debian
   sudo apt install nodejs npm
   
   # Windows - download from nodejs.org
   ```

2. **Update PATH**
   ```bash
   # Add Node.js to PATH
   export PATH=$PATH:/usr/local/bin
   
   # Or use full path in command
   /usr/local/bin/npx -m @modelcontextprotocol/server-github
   ```

#### Problem: Permission Denied
**Symptoms:**
- "Permission denied" when executing command
- Server fails to start with permission error

**Solutions:**

1. **Fix npm Permissions**
   ```bash
   # Change npm global directory
   mkdir ~/.npm-global
   npm config set prefix '~/.npm-global'
   export PATH=~/.npm-global/bin:$PATH
   ```

2. **Use sudo (not recommended)**
   ```bash
   # Only as last resort
   sudo npm install -g @modelcontextprotocol/server-github
   ```

### Tool Discovery Issues

#### Problem: Tools Not Appearing
**Symptoms:**
- Server connected but no tools shown
- Tool count remains 0

**Solutions:**

1. **Wait for Discovery**
   - Tool discovery can take 5-10 seconds
   - Check server logs for discovery completion

2. **Manual Refresh**
   ```python
   # In Python console
   from jarvis.tools import get_mcp_tool_manager
   tool_manager = get_mcp_tool_manager()
   tool_manager.refresh_tools()
   ```

3. **Check Server Capabilities**
   - Ensure server implements `tools/list` method
   - Verify server is MCP-compatible

#### Problem: Tools Disabled
**Symptoms:**
- Tools appear but are grayed out
- Tools don't execute when called

**Solutions:**

1. **Enable Tools in UI**
   - Go to MCP management page
   - Toggle tools to enabled state

2. **Check Tool Permissions**
   - Verify API tokens have required permissions
   - Check tool-specific requirements

### Configuration Issues

#### Problem: Invalid Configuration
**Symptoms:**
- "Configuration is invalid" error
- Test connection fails

**Solutions:**

1. **Validate Required Fields**
   ```python
   # Check required fields for transport type
   # STDIO: name, transport, command
   # HTTP/SSE: name, transport, url
   # WebSocket: name, transport, url
   ```

2. **Check URL Format**
   ```python
   # Valid URLs
   https://api.example.com/mcp  # HTTP/SSE
   wss://api.example.com/mcp    # WebSocket
   
   # Invalid URLs
   api.example.com              # Missing protocol
   http://                      # Missing host
   ```

3. **Verify Environment Variables Format**
   ```
   # Correct format (one per line)
   GITHUB_TOKEN=ghp_xxxxxxxxxxxx
   API_KEY=your_api_key_here
   
   # Incorrect format
   GITHUB_TOKEN ghp_xxxxxxxxxxxx  # Missing =
   GITHUB_TOKEN="token"           # Quotes not needed
   ```

#### Problem: Encryption/Decryption Errors
**Symptoms:**
- "Failed to decrypt configuration" error
- Configuration file corrupted

**Solutions:**

1. **Reset Configuration**
   ```bash
   # Backup current config
   cp ~/.jarvis/mcp_servers.json ~/.jarvis/mcp_servers.json.backup
   
   # Remove corrupted config
   rm ~/.jarvis/mcp_servers.json
   
   # Restart Jarvis to create new config
   ```

2. **Check File Permissions**
   ```bash
   # Ensure proper permissions
   chmod 600 ~/.jarvis/mcp_servers.json
   ```

### API Token Issues

#### Problem: GitHub Authentication Failed
**Symptoms:**
- "Authentication failed" error
- 401/403 HTTP errors

**Solutions:**

1. **Verify Token Permissions**
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Ensure token has required scopes:
     - `repo` (for repository access)
     - `read:user` (for user information)
     - `read:org` (for organization access)

2. **Check Token Format**
   ```bash
   # GitHub tokens start with specific prefixes
   ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Personal access token
   github_pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxx   # Fine-grained token
   ```

3. **Test Token Manually**
   ```bash
   # Test GitHub API access
   curl -H "Authorization: Bearer YOUR_TOKEN" https://api.github.com/user
   ```

#### Problem: Brave Search API Errors
**Symptoms:**
- "Invalid API key" error
- Search requests fail

**Solutions:**

1. **Get Valid API Key**
   - Sign up at https://api.search.brave.com/
   - Generate API key from dashboard

2. **Check API Key Format**
   ```bash
   # Brave API keys start with BSA-
   BSA-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Verify Usage Limits**
   - Check API usage in Brave dashboard
   - Ensure you haven't exceeded rate limits

### Network and Connectivity Issues

#### Problem: Timeout Errors
**Symptoms:**
- "Connection timeout" error
- Slow server responses

**Solutions:**

1. **Increase Timeout**
   ```python
   # In server configuration
   timeout = 60  # Increase from default 30 seconds
   ```

2. **Check Network Connection**
   ```bash
   # Test connectivity
   ping api.example.com
   curl -I https://api.example.com/mcp
   ```

3. **Proxy Configuration**
   ```bash
   # If behind corporate proxy
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=https://proxy.company.com:8080
   ```

#### Problem: SSL Certificate Errors
**Symptoms:**
- "SSL certificate verification failed"
- HTTPS connection errors

**Solutions:**

1. **Update Certificates**
   ```bash
   # macOS
   brew install ca-certificates
   
   # Ubuntu/Debian
   sudo apt update && sudo apt install ca-certificates
   ```

2. **Verify Server Certificate**
   ```bash
   # Check SSL certificate
   openssl s_client -connect api.example.com:443
   ```

### Performance Issues

#### Problem: Slow Tool Execution
**Symptoms:**
- Tools take long time to execute
- UI becomes unresponsive

**Solutions:**

1. **Check Server Performance**
   - Monitor server resource usage
   - Consider server location/latency

2. **Optimize Configuration**
   ```python
   # Reduce timeout for faster failure
   timeout = 10
   
   # Use connection pooling if available
   ```

3. **Monitor Logs**
   ```bash
   # Check for performance bottlenecks
   tail -f jarvis_debug.log | grep -E "(slow|timeout|performance)"
   ```

### UI Issues

#### Problem: JavaScript Errors in Browser
**Symptoms:**
- "Function not defined" errors
- UI buttons not working

**Solutions:**

1. **Clear Browser Cache**
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   - Clear browser cache and cookies

2. **Check Browser Console**
   - Open Developer Tools (F12)
   - Look for JavaScript errors in Console tab

3. **Update Browser**
   - Ensure using modern browser with JavaScript enabled
   - Test in different browser

#### Problem: Form Validation Errors
**Symptoms:**
- "Please enter a server name" despite filled form
- Form submission fails

**Solutions:**

1. **Check Required Fields**
   - Ensure all required fields are filled
   - Check for hidden validation messages

2. **Verify Input Format**
   ```
   # Environment variables (one per line)
   KEY1=value1
   KEY2=value2
   
   # Headers (one per line)
   Authorization: Bearer token
   X-API-Key: key
   ```

## Diagnostic Commands

### System Information
```bash
# Check Jarvis installation
python -c "import jarvis; print(jarvis.__version__)"

# Check MCP system status
python -c "from jarvis.tools import get_mcp_client; print(get_mcp_client().get_all_servers())"

# List installed MCP servers
npm list -g | grep modelcontextprotocol
```

### Log Analysis
```bash
# View MCP-specific logs
grep -i mcp jarvis_debug.log | tail -20

# Monitor real-time MCP activity
tail -f jarvis_debug.log | grep -E "(mcp|MCP)"

# Check for errors
grep -i error jarvis_debug.log | grep -i mcp
```

### Configuration Verification
```bash
# Check configuration file
cat ~/.jarvis/mcp_servers.json | python -m json.tool

# Verify environment variables
env | grep -E "(GITHUB|BRAVE|API)"

# Test server commands manually
npx -m @modelcontextprotocol/server-memory
```

## Getting Help

### Log Collection
When reporting issues, include:

1. **Jarvis Version**
   ```bash
   python -c "import jarvis; print(jarvis.__version__)"
   ```

2. **System Information**
   ```bash
   python --version
   node --version
   uname -a  # Linux/Mac
   ```

3. **Relevant Logs**
   ```bash
   # Last 50 lines of MCP-related logs
   grep -i mcp jarvis_debug.log | tail -50
   ```

4. **Configuration (sanitized)**
   ```bash
   # Remove sensitive data before sharing
   cat ~/.jarvis/mcp_servers.json | sed 's/"[A-Za-z0-9_]*TOKEN[A-Za-z0-9_]*": "[^"]*"/"TOKEN": "REDACTED"/g'
   ```

### Community Resources

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check latest documentation for updates
- **MCP Community**: Official MCP community for server-specific issues

### Professional Support

For enterprise deployments or complex issues:
- Review security best practices
- Consider professional consultation
- Implement monitoring and alerting
