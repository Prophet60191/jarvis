# Robot Framework Quick Reference Card

## 🚀 Essential Commands

### Basic Test Execution
```bash
# Run all tests
python scripts/run_robot_tests.py

# Run smoke tests (fastest, essential functionality)
python scripts/run_robot_tests.py --tags smoke

# Run specific test suite
python scripts/run_robot_tests.py --suite core_functionality
python scripts/run_robot_tests.py --suite open_interpreter_tests

# List available test suites
python scripts/run_robot_tests.py --list-suites
```

### Debug and Troubleshooting
```bash
# Dry run (validate without execution)
python scripts/run_robot_tests.py --dry-run

# Debug logging
python scripts/run_robot_tests.py --log-level DEBUG

# Run single test with debug
python scripts/run_robot_tests.py --suite core_functionality --include "Test Wake Word Detection" --log-level DEBUG
```

## 🏷️ Test Tags

| Tag | Purpose | Example Usage |
|-----|---------|---------------|
| `smoke` | Essential tests | `--tags smoke` |
| `core` | Core functionality | `--tags core` |
| `memory` | Memory system | `--tags memory` |
| `open-interpreter` | Code execution | `--tags open-interpreter` |
| `performance` | Speed tests | `--tags performance` |
| `error-handling` | Error recovery | `--tags error-handling` |

## 📊 Test Results

### Quick Status Check
- ✅ **PASS** - Test successful
- ❌ **FAIL** - Test failed (check logs)
- ⏭️ **SKIP** - Test skipped

### Result Files (in `test_results/`)
- **`report_*.html`** - Executive summary
- **`log_*.html`** - Detailed execution log
- **`output_*.xml`** - Machine-readable results

## 🧪 Test Suites Overview

### Core Functionality (10 tests)
- Wake word detection
- Speech recognition
- Memory storage/retrieval
- Error handling
- Performance monitoring

### Open Interpreter (13 tests)
- Code execution
- File analysis
- Script creation
- System tasks
- Tool integration

## 🔧 Common Troubleshooting

| Issue | Quick Fix |
|-------|-----------|
| "Robot Framework not found" | `pip install robotframework` |
| "JarvisLibrary import failed" | Check Python path |
| "Jarvis not responding" | Stop other Jarvis instances |
| "Tests are slow" | Use `--tags smoke` |
| "Test failures" | Check HTML logs, run with `--log-level DEBUG` |

## 📈 Recommended Workflow

### Daily Development
```bash
python scripts/run_robot_tests.py --tags smoke
```

### Before Commits
```bash
python scripts/run_robot_tests.py --suite core_functionality
```

### Before Releases
```bash
python scripts/run_robot_tests.py
```

### Performance Check
```bash
python scripts/run_robot_tests.py --tags performance
```

## 🎯 Quick Test Creation

### Basic Test Structure
```robot
*** Test Cases ***
My Test Case
    [Documentation]    What this test does
    [Tags]    appropriate-tag
    
    Activate Jarvis
    Send Voice Command    test command
    Response Should Contain    expected result
```

### Available Keywords
- `Activate Jarvis` - Wake up Jarvis
- `Send Voice Command` - Send command
- `Response Should Contain` - Verify response
- `Verify Tool Is Available` - Check tool
- `Test Memory Storage` - Test memory
- `Measure Response Time` - Performance test

## 📚 File Locations

```
jarvis/
├── scripts/run_robot_tests.py     # Test runner
├── tests/robot/
│   ├── suites/                    # Test suites
│   ├── keywords/                  # Reusable keywords
│   ├── libraries/                 # Custom libraries
│   └── resources/                 # Configuration
├── test_results/                  # Test outputs
└── docs/                          # Documentation
```

## 🎉 Success Tips

1. **Start with smoke tests** - fastest feedback
2. **Use meaningful tags** - organize your tests
3. **Check HTML logs** - detailed error info
4. **Run debug mode** - when troubleshooting
5. **Keep tests updated** - maintain as features change

---

**Need more help?** Check `docs/ROBOT_FRAMEWORK_USER_GUIDE.md` for detailed information!
