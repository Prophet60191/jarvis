# 🔧 **JARVIS TROUBLESHOOTING GUIDE**

This comprehensive guide helps you diagnose and resolve common Jarvis issues quickly and effectively.

## 🚨 **EMERGENCY QUICK FIXES**

### **Jarvis Won't Start**
```bash
# Quick diagnostic
python validate_implementation.py

# If validation fails, try:
python jarvis/setup_default_voice.py
python start_jarvis.py
```

### **Voice Not Working**
```bash
# Test audio system
python jarvis/diagnose_audio.py

# Reset voice settings
python jarvis/setup_default_voice.py
```

### **System Frozen/Unresponsive**
```bash
# Emergency stop
python test_emergency_stop.py

# Or force quit
pkill -f "jarvis"  # Linux/Mac
taskkill /f /im python.exe  # Windows
```

## 📋 **DIAGNOSTIC TOOLS**

### **System Health Check**
```bash
# Complete system validation
python validate_implementation.py

# Specific component checks
python debug_jarvis_issue.py
python jarvis/diagnose_tts.py
python jarvis/diagnose_audio.py
```

### **Performance Analysis**
```bash
# Performance diagnostics
python analyze_mps_performance.py

# Memory usage check
python debug_tool_loading.py
```

### **Configuration Verification**
```bash
# Settings validation
python verify_settings.py
python debug_jarvis_settings.py
```

## 🎯 **COMMON ISSUES & SOLUTIONS**

### **1. Installation Issues**

#### **Problem**: Dependencies won't install
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solutions**:
```bash
# Update pip first
python -m pip install --upgrade pip

# Install with user flag
pip install --user -r requirements-enhanced.txt

# Use conda if pip fails
conda install -c conda-forge pyaudio speechrecognition
```

#### **Problem**: Python version incompatibility
```
ERROR: Python 3.7 is not supported
```

**Solutions**:
```bash
# Check Python version
python --version

# Install Python 3.8+ from python.org
# Or use pyenv to manage versions
pyenv install 3.9.7
pyenv local 3.9.7
```

### **2. Audio Issues**

#### **Problem**: Microphone not detected
```
ERROR: No microphone found
```

**Solutions**:
```bash
# Check audio devices
python jarvis/diagnose_audio.py

# On macOS - grant microphone permission
# System Preferences → Security & Privacy → Microphone

# On Linux - install audio dependencies
sudo apt-get install portaudio19-dev python3-pyaudio

# On Windows - update audio drivers
```

#### **Problem**: Voice recognition not working
```
ERROR: Could not understand audio
```

**Solutions**:
1. **Check microphone settings**:
   ```bash
   python jarvis_settings_app.py
   # Go to Voice → Microphone → Test
   ```

2. **Adjust sensitivity**:
   - Increase microphone gain in system settings
   - Reduce background noise
   - Speak closer to microphone

3. **Test with different phrases**:
   - Try "Hey Jarvis" clearly
   - Ensure no background music/TV
   - Check for accent/language settings

#### **Problem**: TTS (Text-to-Speech) not working
```
ERROR: TTS engine failed to initialize
```

**Solutions**:
```bash
# Test TTS system
python jarvis/diagnose_tts.py

# Reset to default voice
python jarvis/setup_default_voice.py

# Install TTS dependencies
pip install pyttsx3 coqui-tts

# On Linux, install espeak
sudo apt-get install espeak espeak-data
```

### **3. Performance Issues**

#### **Problem**: Slow response times
```
Response time: 5000ms (target: <500ms)
```

**Solutions**:
1. **Check system resources**:
   ```bash
   python analyze_mps_performance.py
   ```

2. **Optimize settings**:
   ```bash
   python jarvis_settings_app.py
   # Performance → Enable Auto-optimization
   # Performance → Reduce cache size if low memory
   ```

3. **Close unnecessary applications**:
   - Check CPU usage in Task Manager/Activity Monitor
   - Close browser tabs, video players, etc.

4. **Restart Jarvis**:
   ```bash
   python test_emergency_stop.py
   python start_jarvis.py
   ```

#### **Problem**: High memory usage
```
Memory usage: 85% (concerning threshold)
```

**Solutions**:
```bash
# Check memory usage
python debug_tool_loading.py

# Reduce cache size
python jarvis_settings_app.py
# Performance → Cache Settings → Reduce size

# Restart with clean state
python cleanup_ui_processes.py
python start_jarvis.py
```

### **4. AI/LLM Issues**

#### **Problem**: API key errors
```
ERROR: Invalid API key
```

**Solutions**:
1. **Verify API key**:
   ```bash
   python debug_jarvis_settings.py
   # Check API key format and validity
   ```

2. **Update API key**:
   ```bash
   python jarvis_settings_app.py
   # AI Settings → API Configuration → Update key
   ```

3. **Check API quotas**:
   - Visit OpenAI/Anthropic dashboard
   - Verify billing and usage limits

#### **Problem**: Model not responding
```
ERROR: Model request timeout
```

**Solutions**:
1. **Check internet connection**:
   ```bash
   ping openai.com
   ```

2. **Try different model**:
   ```bash
   python jarvis_settings_app.py
   # AI Settings → Model Selection → Try GPT-3.5
   ```

3. **Adjust timeout settings**:
   ```bash
   python jarvis_settings_app.py
   # AI Settings → Advanced → Increase timeout
   ```

### **5. Plugin/Tool Issues**

#### **Problem**: Tools not loading
```
ERROR: Failed to load plugin: file_manager
```

**Solutions**:
```bash
# Check plugin status
python manage_plugins.py --status

# Reload plugins
python manage_plugins.py --reload

# Check plugin dependencies
python debug_tool_path.py
```

#### **Problem**: Tool execution failures
```
ERROR: Tool execution failed
```

**Solutions**:
1. **Check tool permissions**:
   - File manager: Check file system permissions
   - Web browser: Verify browser installation
   - System tools: Check admin privileges

2. **Update tool configurations**:
   ```bash
   python jarvis_settings_app.py
   # Tools → [Tool Name] → Configuration
   ```

3. **Reinstall problematic tools**:
   ```bash
   python manage_plugins.py --reinstall file_manager
   ```

### **6. UI/Interface Issues**

#### **Problem**: Settings UI won't open
```
ERROR: Failed to start settings application
```

**Solutions**:
```bash
# Check UI dependencies
pip install PyQt6

# Clean UI processes
python cleanup_ui_processes.py

# Try minimal settings
python test_minimal_settings.py
```

#### **Problem**: Analytics dashboard crashes
```
ERROR: Dashboard failed to initialize
```

**Solutions**:
```bash
# Install dashboard dependencies
pip install PyQt6 psutil

# Launch with debug mode
python launch_analytics_dashboard.py --debug

# Check for port conflicts
netstat -an | grep 8080
```

## 🔍 **ADVANCED DIAGNOSTICS**

### **Log Analysis**

#### **Check Log Files**
```bash
# Main application logs
tail -f jarvis/logs/jarvis.log

# Debug logs
tail -f jarvis_debug.log

# MCP integration logs
tail -f open_interpreter_mcp.log
```

#### **Log Levels**
- **ERROR**: Critical issues requiring attention
- **WARNING**: Potential problems to monitor
- **INFO**: Normal operation information
- **DEBUG**: Detailed diagnostic information

### **Configuration Debugging**

#### **Check Configuration Files**
```bash
# Main configuration
cat data/context_manager.json

# Plugin registry
cat data/plugin_registry.json

# Settings validation
python verify_settings.py
```

#### **Reset Configuration**
```bash
# Backup current settings
cp data/context_manager.json data/context_manager.json.backup

# Reset to defaults
python jarvis/create_jarvis_dir.py --reset

# Restore from backup if needed
cp data/context_manager.json.backup data/context_manager.json
```

### **Network Diagnostics**

#### **API Connectivity**
```bash
# Test OpenAI connection
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.openai.com/v1/models

# Test Anthropic connection
curl -H "x-api-key: YOUR_API_KEY" \
     https://api.anthropic.com/v1/messages
```

#### **Proxy/Firewall Issues**
```bash
# Check proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Test direct connection
python -c "import requests; print(requests.get('https://api.openai.com').status_code)"
```

## 🛠️ **SYSTEM OPTIMIZATION**

### **Performance Tuning**

#### **Memory Optimization**
```bash
# Reduce memory usage
python jarvis_settings_app.py
# Performance → Memory → Reduce cache sizes
# Performance → Memory → Enable garbage collection
```

#### **CPU Optimization**
```bash
# Adjust processing priorities
python jarvis_settings_app.py
# Performance → CPU → Reduce concurrent operations
# Performance → CPU → Enable power saving mode
```

### **Storage Cleanup**

#### **Clear Temporary Files**
```bash
# Clean temporary data
rm -rf data/temp/*

# Clean old logs (keep last 7 days)
find jarvis/logs -name "*.log" -mtime +7 -delete

# Clean old analytics data
python -c "from jarvis.jarvis.core.analytics.usage_analytics import usage_analytics; usage_analytics.cleanup_old_data()"
```

#### **Database Maintenance**
```bash
# Optimize vector database
python -c "import chromadb; client = chromadb.PersistentClient('data/chroma_db'); client.reset()"

# Rebuild search index
python ingest.py --rebuild-index
```

## 📞 **GETTING HELP**

### **Self-Help Resources**

1. **Built-in Help**:
   ```bash
   # Ask Jarvis directly
   "Hey Jarvis, help me troubleshoot audio issues"
   ```

2. **Documentation**:
   - [User Guide](USER_GUIDE.md) - Complete feature guide
   - [Getting Started](GETTING_STARTED_COMPLETE.md) - Setup guide
   - [Analytics Guide](ANALYTICS_DASHBOARD_USER_GUIDE.md) - Dashboard help

3. **Diagnostic Scripts**:
   ```bash
   python validate_implementation.py  # System health
   python debug_jarvis_issue.py      # Issue diagnosis
   python analyze_mps_performance.py # Performance analysis
   ```

### **Community Support**

1. **GitHub Issues**: Report bugs and get help
2. **Documentation**: Check latest guides and updates
3. **Examples**: Review working configurations

### **Creating Support Requests**

When asking for help, include:

1. **System Information**:
   ```bash
   python --version
   uname -a  # Linux/Mac
   systeminfo  # Windows
   ```

2. **Error Messages**:
   ```bash
   # Copy exact error messages
   tail -n 50 jarvis/logs/jarvis.log
   ```

3. **Configuration**:
   ```bash
   # Sanitized configuration (remove API keys)
   python debug_jarvis_settings.py --export
   ```

4. **Steps to Reproduce**:
   - What you were trying to do
   - Exact commands or voice inputs used
   - Expected vs. actual behavior

## ✅ **PREVENTION TIPS**

### **Regular Maintenance**
1. **Weekly**: Check system health with `validate_implementation.py`
2. **Monthly**: Clean temporary files and optimize database
3. **Quarterly**: Update dependencies and review settings

### **Best Practices**
1. **Keep backups** of working configurations
2. **Monitor performance** regularly via analytics dashboard
3. **Update gradually** - test changes in development first
4. **Document customizations** for easier troubleshooting

### **Early Warning Signs**
- Response times increasing gradually
- Memory usage trending upward
- Error rates above 5%
- Unusual patterns in analytics dashboard

**Remember**: Most issues have simple solutions. Start with the basics (restart, check logs, verify settings) before diving into complex diagnostics! 🚀
