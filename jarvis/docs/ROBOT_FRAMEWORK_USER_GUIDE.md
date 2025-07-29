# Robot Framework User Guide for Jarvis Voice Assistant

## 🎯 Overview

This guide will help you use Robot Framework to test Jarvis Voice Assistant effectively. Whether you're a developer, QA engineer, or contributor, this guide covers everything from basic test execution to advanced test development.

## 🚀 Quick Start

### Prerequisites
- Jarvis Voice Assistant installed and working
- Robot Framework integration setup completed
- Python 3.11+ environment

### Your First Test Run

1. **Navigate to Jarvis directory**:
   ```bash
   cd /path/to/jarvis
   ```

2. **Run smoke tests** (essential functionality):
   ```bash
   python scripts/run_robot_tests.py --tags smoke
   ```

3. **Check results**:
   - Results appear in terminal
   - Detailed reports saved to `test_results/` directory
   - Open HTML reports in your browser

## 📋 Available Commands

### Basic Test Execution

```bash
# Run all tests
python scripts/run_robot_tests.py

# Run specific test suite
python scripts/run_robot_tests.py --suite core_functionality
python scripts/run_robot_tests.py --suite open_interpreter_tests

# Run tests with specific tags
python scripts/run_robot_tests.py --tags smoke
python scripts/run_robot_tests.py --tags memory
python scripts/run_robot_tests.py --tags performance

# Exclude certain tests
python scripts/run_robot_tests.py --exclude-tags slow

# List available test suites
python scripts/run_robot_tests.py --list-suites
```

### Advanced Options

```bash
# Run with debug logging
python scripts/run_robot_tests.py --log-level DEBUG

# Dry run (validate tests without execution)
python scripts/run_robot_tests.py --dry-run

# Custom output directory
python scripts/run_robot_tests.py --output-dir my_test_results

# Set custom variables
python scripts/run_robot_tests.py --variable TIMEOUT:60s --variable DEBUG:true
```

## 🏷️ Test Tags Reference

### Core System Tags
- **`smoke`** - Essential functionality tests (run these first!)
- **`core`** - Core system functionality
- **`memory`** - Memory system tests
- **`audio`** - Audio processing tests
- **`wake-word`** - Wake word detection tests
- **`speech-recognition`** - Speech recognition tests

### Open Interpreter Tags
- **`open-interpreter`** - All Open Interpreter tests
- **`code-execution`** - Code execution tests
- **`file-analysis`** - File analysis tests
- **`script-creation`** - Script creation tests
- **`system-tasks`** - System administration tests

### Quality Tags
- **`performance`** - Performance and timing tests
- **`error-handling`** - Error handling validation
- **`integration`** - Integration tests
- **`health-check`** - System health verification

## 📊 Understanding Test Results

### Terminal Output
```
==============================================================================
Core Functionality :: Core functionality tests for Jarvis Voice Assistant
==============================================================================
Test Wake Word Detection :: Test that Jarvis responds to wake word... | PASS |
Test Basic Speech Recognition :: Test basic speech recognition...      | PASS |
Test Memory Storage :: Test that Jarvis can store information...       | PASS |
==============================================================================
Core Functionality :: Core functionality tests...                     | PASS |
10 tests, 10 passed, 0 failed
==============================================================================
```

### Result Indicators
- **PASS** ✅ - Test completed successfully
- **FAIL** ❌ - Test failed (check logs for details)
- **SKIP** ⏭️ - Test was skipped (usually due to conditions)

### HTML Reports
After test execution, check these files in `test_results/`:
- **`report_[timestamp].html`** - Executive summary with pass/fail statistics
- **`log_[timestamp].html`** - Detailed test execution log
- **`output_[timestamp].xml`** - Machine-readable results

## 🧪 Test Suites Explained

### 1. Core Functionality Tests (`core_functionality.robot`)

**Purpose**: Validate essential Jarvis functionality

**Test Cases**:
1. **Wake Word Detection** - Tests "Jarvis" wake word recognition
2. **Basic Speech Recognition** - Validates speech-to-text accuracy
3. **Simple Question Response** - Tests basic Q&A functionality
4. **Memory Storage** - Validates information storage
5. **Memory Retrieval** - Tests information recall
6. **Error Handling** - Validates graceful error handling
7. **System Health Check** - Overall system responsiveness
8. **Response Time Performance** - Speed benchmarking
9. **Multiple Commands Sequence** - Sequential command handling
10. **Conversation Context** - Context retention testing

**When to Run**: 
- Before any release
- After core system changes
- Daily regression testing

### 2. Open Interpreter Tests (`open_interpreter_tests.robot`)

**Purpose**: Validate code execution and analysis capabilities

**Test Cases**:
1. **Tool Availability** - Verify tools are loaded
2. **Basic Code Execution** - Simple calculations
3. **Mathematical Calculations** - Complex math operations
4. **System Tasks** - Disk usage, process monitoring
5. **File Analysis** - CSV, JSON, text file processing
6. **Script Creation** - Python, Bash script generation
7. **Data Processing** - Complex data workflows
8. **File System Operations** - File management tasks
9. **Error Handling** - Code execution error recovery
10. **Performance Monitoring** - System resource tracking
11. **Response Time** - Code execution speed
12. **Multiple Tool Usage** - Tool integration testing

**When to Run**:
- After Open Interpreter updates
- Before deploying code execution features
- When troubleshooting user-reported issues

## 🛠️ Test Development

### Creating New Test Cases

1. **Choose the right test suite**:
   - Core functionality → `core_functionality.robot`
   - Open Interpreter → `open_interpreter_tests.robot`
   - New domain → Create new suite file

2. **Basic test structure**:
   ```robot
   *** Test Cases ***
   My New Test Case
       [Documentation]    Description of what this test does
       [Tags]    appropriate-tag
       
       # Test setup
       Activate Jarvis
       
       # Test execution
       Send Voice Command    Your test command
       
       # Verification
       Response Should Contain    expected result
   ```

3. **Use existing keywords**:
   - `Activate Jarvis` - Wake up Jarvis
   - `Send Voice Command` - Send a command
   - `Response Should Contain` - Verify response
   - `Verify Tool Is Available` - Check tool availability

### Adding Custom Keywords

1. **Edit** `tests/robot/keywords/jarvis_keywords.robot`
2. **Follow the pattern**:
   ```robot
   My Custom Keyword
       [Documentation]    What this keyword does
       [Arguments]    ${parameter1}    ${parameter2}=default
       [Tags]    keyword-category
       
       # Keyword implementation
       Log    Executing custom keyword
       # Your logic here
   ```

### Test Data Management

1. **Configuration**: Edit `tests/robot/resources/test_config.yaml`
2. **Test files**: Place in `tests/fixtures/`
3. **Variables**: Define in test suite or keyword files

## 🔧 Troubleshooting

### Common Issues and Solutions

#### "Robot Framework not found"
```bash
# Solution: Install Robot Framework
pip install robotframework
```

#### "JarvisLibrary import failed"
```bash
# Solution: Check Python path and library location
python -c "from tests.robot.libraries.JarvisLibrary import JarvisLibrary; print('OK')"
```

#### "Jarvis not responding in tests"
- Check if Jarvis is already running
- Verify test configuration in `test_config.yaml`
- Check audio system is not in use by other applications

#### "Tests are slow"
- Use `--tags smoke` for faster essential tests
- Check system resources (CPU, memory)
- Verify Ollama model is loaded

#### "Test failures"
1. **Check the HTML log** for detailed error information
2. **Run individual test** to isolate the issue:
   ```bash
   python scripts/run_robot_tests.py --suite core_functionality --include "Test Wake Word Detection"
   ```
3. **Enable debug logging**:
   ```bash
   python scripts/run_robot_tests.py --log-level DEBUG
   ```

### Debug Mode

Enable detailed logging for troubleshooting:
```bash
python scripts/run_robot_tests.py --log-level DEBUG --variable DEBUG:true
```

This provides:
- Detailed keyword execution logs
- Variable values at each step
- System interaction details
- Timing information

## 📈 Best Practices

### Test Execution Strategy

1. **Daily Development**:
   ```bash
   python scripts/run_robot_tests.py --tags smoke
   ```

2. **Before Commits**:
   ```bash
   python scripts/run_robot_tests.py --suite core_functionality
   ```

3. **Before Releases**:
   ```bash
   python scripts/run_robot_tests.py
   ```

4. **Performance Monitoring**:
   ```bash
   python scripts/run_robot_tests.py --tags performance
   ```

### Test Maintenance

1. **Regular Updates**:
   - Update test cases when features change
   - Add tests for new functionality
   - Remove obsolete tests

2. **Performance Monitoring**:
   - Track test execution times
   - Monitor success rates
   - Identify flaky tests

3. **Documentation**:
   - Keep test documentation current
   - Document test data requirements
   - Maintain troubleshooting guides

## 🎯 Integration with Development Workflow

### Pre-Commit Testing
```bash
# Add to your pre-commit hook
python scripts/run_robot_tests.py --tags smoke --log-level WARN
```

### Continuous Integration
```yaml
# Example GitHub Actions workflow
- name: Run Robot Framework Tests
  run: |
    cd jarvis
    python scripts/run_robot_tests.py --tags smoke
```

### Release Validation
```bash
# Full test suite before release
python scripts/run_robot_tests.py --output-dir release_validation_$(date +%Y%m%d)
```

## 📚 Additional Resources

### Robot Framework Documentation
- **Official Guide**: https://robotframework.org/robotframework/
- **Keyword Documentation**: Built-in and library keywords
- **Test Data Syntax**: How to structure test data

### Jarvis-Specific Resources
- **Integration Plan**: `docs/ROBOT_FRAMEWORK_INTEGRATION_PLAN.md`
- **Implementation Details**: `docs/ROBOT_FRAMEWORK_INTEGRATION_COMPLETE.md`
- **Custom Keywords**: `tests/robot/keywords/jarvis_keywords.robot`

### Getting Help

1. **Check HTML logs** for detailed error information
2. **Review test documentation** in test files
3. **Run debug mode** for detailed execution traces
4. **Check Jarvis logs** for system-level issues

## 🎉 Success Tips

1. **Start Small**: Begin with smoke tests, then expand
2. **Use Tags**: Organize tests with meaningful tags
3. **Monitor Performance**: Track test execution times
4. **Keep Tests Updated**: Maintain tests as features evolve
5. **Document Issues**: Record solutions for future reference

---

**Happy Testing! 🚀**

This guide should help you effectively use Robot Framework to ensure Jarvis quality and reliability. Remember: good tests lead to better software!
