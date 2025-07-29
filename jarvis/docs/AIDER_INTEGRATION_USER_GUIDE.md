# 🤖 Aider Integration User Guide

Complete guide for using Aider AI code editing integration with Jarvis Voice Assistant.

## 🎯 What is Aider Integration?

Aider Integration allows Jarvis to seamlessly hand off complex code editing tasks to Aider AI, a powerful AI-powered code editor. This enables you to use voice commands for sophisticated code modifications, refactoring, and project-wide changes.

### **Key Benefits**
- **Voice-controlled code editing**: Use natural language to describe code changes
- **Intelligent refactoring**: AI understands code structure and context
- **Multi-file operations**: Make changes across multiple files simultaneously
- **Automatic git commits**: Changes are automatically committed with descriptive messages
- **Seamless handoff**: Jarvis manages the entire process and returns control when complete

## 🛠️ Setup and Installation

### **1. Install Aider**

```bash
# Install Aider using pip
pip install aider-chat

# Verify installation
aider --version
```

### **2. Configure API Keys**

Aider requires an AI model API key. Add to your `.env` file:

```bash
# For OpenAI GPT models (recommended)
OPENAI_API_KEY=your_openai_api_key

# For Anthropic Claude models
ANTHROPIC_API_KEY=your_anthropic_api_key

# For other models, see Aider documentation
```

### **3. Verify Setup**

Use Jarvis to check if Aider is properly configured:

```
"Check Aider status"
```

You should see confirmation that Aider is installed and ready.

## 🎤 Voice Commands

### **Basic Code Editing**

#### **File-Specific Edits**
```
"Edit main.py to add error logging"
"Edit config.py to add a new setting for timeout"
"Edit utils.py to add input validation"
"Fix the bug in authentication.py"
"Add error handling to database.py"
```

#### **Feature Additions**
```
"Edit app.py to add user authentication"
"Edit server.py to add rate limiting"
"Edit models.py to add a new User class"
"Add a search function to search.py"
```

#### **Code Improvements**
```
"Refactor main.py to use async/await"
"Refactor database.py to use connection pooling"
"Optimize the performance of slow_function in utils.py"
"Add type hints to all functions in helpers.py"
```

### **Project-Wide Operations**

#### **Large-Scale Refactoring**
```
"Refactor the entire project to use dependency injection"
"Update all files to follow PEP 8 style guidelines"
"Modernize this codebase to use Python 3.11 features"
"Apply the factory pattern across the project"
```

#### **Maintenance Tasks**
```
"Update all imports in the project"
"Rename the User class to Customer everywhere"
"Replace all print statements with proper logging"
"Update all docstrings to use Google style"
```

#### **Architecture Changes**
```
"Convert the project to use FastAPI instead of Flask"
"Refactor to use SQLAlchemy instead of raw SQL"
"Apply MVC pattern to the entire codebase"
"Add async support throughout the project"
```

## 🔧 How It Works

### **1. Voice Command Processing**
1. You give a voice command to Jarvis
2. Jarvis recognizes it as a code editing task
3. Jarvis prepares the handoff to Aider

### **2. Aider Execution**
1. Jarvis launches Aider with your specifications
2. Aider analyzes the code and makes changes
3. Changes are automatically committed to git
4. Aider provides a summary of what was changed

### **3. Return to Jarvis**
1. Aider completes the task and exits
2. Jarvis regains control
3. Jarvis reports the results back to you

## 📝 Usage Examples

### **Example 1: Adding a Feature**

**Voice Command**: "Edit app.py to add user authentication"

**What Happens**:
1. Aider analyzes your `app.py` file
2. Adds authentication middleware
3. Creates login/logout routes
4. Updates imports and dependencies
5. Commits changes with message: "Add user authentication to app.py"

### **Example 2: Bug Fix**

**Voice Command**: "Fix the bug in database.py where connections aren't closed"

**What Happens**:
1. Aider examines `database.py`
2. Identifies connection management issues
3. Adds proper connection cleanup
4. Implements context managers or try/finally blocks
5. Commits with message: "Fix connection leak bug in database.py"

### **Example 3: Project Refactoring**

**Voice Command**: "Refactor the entire project to use async/await"

**What Happens**:
1. Aider scans all Python files in the project
2. Converts synchronous functions to async
3. Updates function calls to use await
4. Modifies imports to include asyncio
5. Updates tests to handle async functions
6. Commits with message: "Convert project to async/await pattern"

## ⚙️ Configuration Options

### **Model Selection**

You can specify which AI model Aider should use:

```
"Edit main.py using GPT-4 to add logging"
"Refactor utils.py using Claude to improve performance"
```

**Available Models**:
- `gpt-4` (default, most capable)
- `gpt-3.5-turbo` (faster, less expensive)
- `claude-3-opus` (excellent for complex refactoring)
- `claude-3-sonnet` (good balance of speed and capability)

### **Auto-Commit Settings**

By default, Aider automatically commits changes. You can control this:

```python
# In your voice command, you can specify:
"Edit main.py to add logging without auto-commit"
```

### **File Targeting**

You can specify multiple files or directories:

```
"Edit main.py and utils.py to add error handling"
"Refactor all files in the src/ directory"
"Update the entire models/ folder to use dataclasses"
```

## 🔍 Monitoring and Debugging

### **Checking Status**

```
"Check Aider status"
```

This command shows:
- Aider installation status
- Available models
- Current configuration
- Recent activity

### **Viewing Changes**

After Aider completes a task, you can:

```bash
# View the git log to see what was changed
git log --oneline -5

# See the diff of the last commit
git show HEAD

# View specific file changes
git diff HEAD~1 filename.py
```

### **Troubleshooting**

**Common Issues**:

1. **"Aider not found"**
   - Install Aider: `pip install aider-chat`
   - Verify installation: `aider --version`

2. **"API key not configured"**
   - Add your API key to `.env` file
   - Restart Jarvis to load new environment variables

3. **"No files specified"**
   - Be more specific about which files to edit
   - Use full file paths if needed

4. **"Git repository required"**
   - Initialize git: `git init`
   - Make initial commit: `git add . && git commit -m "Initial commit"`

## 🎯 Best Practices

### **Effective Voice Commands**

**✅ Good Commands**:
- "Edit user.py to add email validation"
- "Refactor database.py to use connection pooling"
- "Fix the memory leak in cache.py"

**❌ Avoid Vague Commands**:
- "Make the code better"
- "Fix everything"
- "Update the project"

### **Project Preparation**

1. **Use Git**: Aider works best with git repositories
2. **Clear Structure**: Well-organized code gets better results
3. **Good Documentation**: Comments and docstrings help Aider understand context
4. **Test Coverage**: Having tests helps Aider avoid breaking changes

### **Safety Tips**

1. **Review Changes**: Always review Aider's changes before deploying
2. **Backup Important Work**: Use git branches for experimental changes
3. **Test After Changes**: Run your tests after Aider modifications
4. **Start Small**: Begin with simple edits before complex refactoring

## 🚀 Advanced Features

### **Custom Instructions**

You can provide detailed instructions:

```
"Edit api.py to add rate limiting with Redis backend, 
 using a decorator pattern, and include proper error handling"
```

### **Context-Aware Editing**

Aider understands your project structure:

```
"Add a new endpoint to the API that follows the same pattern as the existing ones"
"Create a new model that inherits from BaseModel like the others"
```

### **Integration with Development Workflow**

```
"Edit the failing test in test_auth.py to make it pass"
"Add the missing imports that are causing the build to fail"
"Update the code to fix all the linting errors"
```

## 📚 Additional Resources

### **Aider Documentation**
- [Official Aider Documentation](https://aider.chat/docs/)
- [Aider GitHub Repository](https://github.com/paul-gauthier/aider)

### **Jarvis Integration**
- [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Plugin Reference Guide](../PLUGIN_REFERENCE_GUIDE.md)

### **Getting Help**
- Use "Check Aider status" for configuration issues
- Check the [Troubleshooting Guide](TROUBLESHOOTING.md) for common problems
- Report integration issues on the Jarvis GitHub repository

---

**Pro Tip**: Start with simple file edits to get familiar with the system, then gradually move to more complex project-wide refactoring tasks. Aider's AI is very capable, but clear, specific instructions always yield the best results!
