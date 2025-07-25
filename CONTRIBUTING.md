# Contributing to Jarvis Voice Assistant

Thank you for your interest in contributing to Jarvis! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **🐛 Bug Reports**: Help us identify and fix issues
- **✨ Feature Requests**: Suggest new functionality
- **📝 Documentation**: Improve or add documentation
- **🔧 Code Contributions**: Fix bugs or implement features
- **🧪 Testing**: Add or improve tests
- **🎨 UI/UX**: Improve user experience
- **🌍 Translations**: Add support for other languages

### Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/jarvis-assistant.git
   cd jarvis-assistant
   ```
3. **Set up development environment**:
   ```bash
   python -m venv jarvis-dev
   source jarvis-dev/bin/activate  # On Windows: jarvis-dev\Scripts\activate
   pip install -r requirements.txt
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

## 📋 Development Guidelines

### Code Style

We follow Python best practices and use automated tools for consistency:

- **PEP 8**: Python style guide
- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking

```bash
# Format code
black jarvis/ tests/

# Check linting
flake8 jarvis/ tests/ --max-line-length=120

# Type checking
mypy jarvis/ --ignore-missing-imports
```

### Code Structure

Follow the existing architecture patterns:

```
jarvis/
├── audio/           # Audio management components
├── core/            # Core business logic
├── tools/           # Tool system and implementations
├── utils/           # Utilities and helpers
├── config.py        # Configuration management
├── exceptions.py    # Custom exceptions
└── main.py          # Application entry point
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `SpeechManager`)
- **Functions/Methods**: `snake_case` (e.g., `listen_for_speech`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
- **Files/Modules**: `snake_case` (e.g., `speech_manager.py`)

### Documentation

- Use **docstrings** for all public classes and methods
- Follow **Google style** docstrings
- Include **type hints** for function parameters and returns
- Add **inline comments** for complex logic

Example:
```python
def process_audio(self, audio_data: AudioData, enhance: bool = True) -> str:
    """
    Process audio data and return recognized text.
    
    Args:
        audio_data: Raw audio data from microphone
        enhance: Whether to apply audio enhancement
        
    Returns:
        Recognized text from speech recognition
        
    Raises:
        SpeechRecognitionError: If speech recognition fails
    """
    # Implementation here
```

### Error Handling

- Use **custom exceptions** from `jarvis.exceptions`
- Provide **meaningful error messages**
- Log errors appropriately
- Handle edge cases gracefully

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {str(e)}")
    raise CustomJarvisError(f"Failed to process: {str(e)}") from e
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Run specific test types
python tests/run_tests.py --unit
python tests/run_tests.py --integration

# Run with coverage
python tests/run_tests.py --coverage
```

### Writing Tests

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **Use mocks** for external dependencies
- **Follow AAA pattern**: Arrange, Act, Assert

Example:
```python
def test_speech_recognition_success(self, mock_recognizer):
    """Test successful speech recognition."""
    # Arrange
    mock_recognizer.recognize_google.return_value = "test speech"
    manager = SpeechManager(test_config)
    
    # Act
    result = manager.recognize_speech(mock_audio_data)
    
    # Assert
    assert result == "test speech"
    mock_recognizer.recognize_google.assert_called_once()
```

### Test Coverage

- Aim for **80%+ code coverage**
- Focus on **critical paths** and **error conditions**
- Test **edge cases** and **boundary conditions**

## 🔧 Adding New Features

### Tools

To add a new tool:

1. **Create tool class**:
   ```python
   from jarvis.tools.base import BaseTool, ToolResult, create_success_result
   
   class MyTool(BaseTool):
       def __init__(self):
           super().__init__("my_tool", "Description of my tool")
       
       def execute(self, **kwargs):
           # Tool implementation
           return create_success_result("Tool result")
       
       def get_parameters(self):
           return {"param": {"type": "string", "description": "Parameter"}}
   ```

2. **Register the tool**:
   ```python
   from jarvis.tools import tool_registry
   tool_registry.register(MyTool())
   ```

3. **Add tests**:
   ```python
   def test_my_tool_execution():
       tool = MyTool()
       result = tool.execute(param="test")
       assert result.is_success
   ```

### Audio Components

For audio-related features:

1. **Follow existing patterns** in `jarvis.audio`
2. **Use proper error handling** with audio exceptions
3. **Test with mocked audio** to avoid hardware dependencies
4. **Consider cross-platform compatibility**

### Core Components

For core functionality:

1. **Maintain separation of concerns**
2. **Use dependency injection** for configuration
3. **Follow the existing state management** patterns
4. **Add comprehensive logging**

## 📝 Pull Request Process

### Before Submitting

1. **Run the full test suite**:
   ```bash
   python tests/run_tests.py --all --lint --type-check
   ```

2. **Update documentation** if needed
3. **Add tests** for new functionality
4. **Update CHANGELOG.md** if applicable

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Testing** on different platforms if needed
4. **Approval** and merge by maintainers

## 🐛 Bug Reports

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Test with latest version**
3. **Check documentation** and troubleshooting guide

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12.0]
- Python: [e.g., 3.11.0]
- Jarvis Version: [e.g., 1.0.0]
- Ollama Version: [e.g., 0.1.0]

## Additional Context
Any other relevant information
```

## ✨ Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other approaches you've considered

## Additional Context
Any other relevant information
```

## 📚 Documentation

### Types of Documentation

- **API Documentation**: Code docstrings
- **User Guides**: How to use features
- **Developer Guides**: How to contribute/extend
- **Examples**: Practical usage examples

### Documentation Standards

- **Clear and concise** language
- **Step-by-step instructions** where appropriate
- **Code examples** with explanations
- **Screenshots** for UI-related documentation

## 🌍 Community Guidelines

### Code of Conduct

- **Be respectful** and inclusive
- **Help others** learn and contribute
- **Provide constructive feedback**
- **Focus on the code**, not the person

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Pull Requests**: Code contributions and reviews

## 🏆 Recognition

Contributors are recognized in:

- **CONTRIBUTORS.md**: List of all contributors
- **Release Notes**: Major contributions highlighted
- **GitHub**: Contributor statistics and badges

## 📞 Getting Help

If you need help contributing:

1. **Check the documentation** in `docs/`
2. **Search GitHub Issues** for similar questions
3. **Create a GitHub Discussion** for general questions
4. **Join our community** channels (if available)

## 📄 License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

Thank you for contributing to Jarvis Voice Assistant! 🤖✨
