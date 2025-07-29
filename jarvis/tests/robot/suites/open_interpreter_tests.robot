*** Settings ***
Documentation    Open Interpreter integration tests for Jarvis Voice Assistant
...              This test suite covers Open Interpreter functionality including
...              code execution, file analysis, script creation, and system tasks.

Resource         ../keywords/jarvis_keywords.robot
Library          ../libraries/JarvisLibrary.py
Library          OperatingSystem

Suite Setup      Setup Open Interpreter Test Suite
Suite Teardown   Teardown Open Interpreter Test Suite
Test Setup       Setup Individual Test
Test Teardown    Teardown Individual Test

*** Variables ***
${TEST_CSV_FILE}        /tmp/jarvis_test/sample_data.csv
${TEST_SCRIPT_PATH}     /tmp/jarvis_test/test_script.py
${CODE_EXECUTION_TIMEOUT}    45s

*** Test Cases ***
Test Execute Code Tool Availability
    [Documentation]    Verify that Open Interpreter execute_code tool is available
    [Tags]    open-interpreter    tools    smoke
    
    Log    Testing execute_code tool availability
    Activate Jarvis
    
    # Verify tool is available
    Verify Tool Is Available    execute_code
    
    Log    Execute code tool availability test passed

Test Basic Code Execution
    [Documentation]    Test basic code execution functionality
    [Tags]    open-interpreter    code-execution    smoke
    
    Log    Testing basic code execution
    Activate Jarvis
    
    # Test simple calculation
    Send Voice Command    Execute code to calculate 2 plus 2    ${CODE_EXECUTION_TIMEOUT}
    Response Should Contain    4
    
    Log    Basic code execution test passed

Test Mathematical Calculations
    [Documentation]    Test mathematical calculations through code execution
    [Tags]    open-interpreter    math    smoke
    
    Log    Testing mathematical calculations
    Activate Jarvis
    
    # Test compound calculation
    Send Voice Command    Execute code to calculate 15 percent of 100    ${CODE_EXECUTION_TIMEOUT}
    Response Should Contain    15
    
    Log    Mathematical calculations test passed

Test System Task Tool
    [Documentation]    Test system task functionality
    [Tags]    open-interpreter    system-tasks    smoke
    
    Log    Testing system task functionality
    Activate Jarvis
    
    # Test disk usage check
    Send Voice Command    Check my disk usage    ${CODE_EXECUTION_TIMEOUT}
    Response Should Contain    GB
    
    Log    System task test passed

Test File Analysis Tool Availability
    [Documentation]    Verify that file analysis tool is available
    [Tags]    open-interpreter    tools    file-analysis
    
    Log    Testing file analysis tool availability
    Activate Jarvis
    
    # Verify tool is available
    Verify Tool Is Available    analyze_file
    
    Log    File analysis tool availability test passed

Test CSV File Analysis
    [Documentation]    Test CSV file analysis functionality
    [Tags]    open-interpreter    file-analysis
    
    Log    Testing CSV file analysis
    
    # Create test CSV file
    Create Test CSV File    ${TEST_CSV_FILE}
    
    Activate Jarvis
    
    # Test file analysis
    Send Voice Command    Analyze the CSV file at ${TEST_CSV_FILE}    ${CODE_EXECUTION_TIMEOUT}
    Response Should Contain    analysis
    
    Log    CSV file analysis test passed

Test Script Creation Tool
    [Documentation]    Test script creation functionality
    [Tags]    open-interpreter    script-creation
    
    Log    Testing script creation
    Activate Jarvis
    
    # Verify tool is available
    Verify Tool Is Available    create_script
    
    # Test script creation
    Send Voice Command    Create a simple Python script that prints hello world    ${CODE_EXECUTION_TIMEOUT}
    Response Should Contain    script
    
    Log    Script creation test passed

Test Data Processing Task
    [Documentation]    Test complex data processing task
    [Tags]    open-interpreter    data-processing
    
    Log    Testing data processing task
    
    # Create test data file
    Create Test CSV File    ${TEST_CSV_FILE}
    
    Activate Jarvis
    
    # Test data processing
    Send Voice Command    Process the CSV file at ${TEST_CSV_FILE} and show me statistics    ${CODE_EXECUTION_TIMEOUT}
    Response Should Contain    statistics
    
    Log    Data processing task test passed

Test File System Operations
    [Documentation]    Test file system operations through system tasks
    [Tags]    open-interpreter    file-system
    
    Log    Testing file system operations
    Activate Jarvis
    
    # Test directory listing
    Send Voice Command    Show me the files in the tmp directory    ${CODE_EXECUTION_TIMEOUT}
    Response Should Contain    files
    
    Log    File system operations test passed

Test Error Handling In Code Execution
    [Documentation]    Test how Open Interpreter handles code execution errors
    [Tags]    open-interpreter    error-handling
    
    Log    Testing error handling in code execution
    Activate Jarvis
    
    # Test with intentionally problematic code request
    Send Voice Command    Execute code to divide by zero    ${CODE_EXECUTION_TIMEOUT}
    # Should handle error gracefully, not crash
    Response Should Not Contain    exception
    Response Should Not Contain    crashed
    
    Log    Error handling in code execution test passed

Test Performance Monitoring Task
    [Documentation]    Test system performance monitoring
    [Tags]    open-interpreter    performance    system-tasks
    
    Log    Testing performance monitoring
    Activate Jarvis
    
    # Test system monitoring
    Send Voice Command    Check system memory usage    ${CODE_EXECUTION_TIMEOUT}
    Response Should Contain    memory
    
    Log    Performance monitoring test passed

Test Code Execution Response Time
    [Documentation]    Test that code execution completes within reasonable time
    [Tags]    open-interpreter    performance
    
    Log    Testing code execution response time
    Activate Jarvis
    
    # Measure response time for code execution
    ${response_time}=    Measure Response Time    Execute code to print the current date
    
    # Code execution should complete within 45 seconds
    Should Be True    ${response_time} < 45    Code execution time ${response_time}s exceeds 45s limit
    
    Log    Code execution response time test passed: ${response_time}s

Test Multiple Tool Usage
    [Documentation]    Test using multiple Open Interpreter tools in sequence
    [Tags]    open-interpreter    integration
    
    Log    Testing multiple tool usage
    
    # Create test file
    Create Test CSV File    ${TEST_CSV_FILE}
    
    Activate Jarvis
    
    # Use multiple tools in sequence
    Send Voice Command    Analyze the file at ${TEST_CSV_FILE}    ${CODE_EXECUTION_TIMEOUT}
    Response Should Contain    analysis
    
    Send Voice Command    Execute code to calculate the sum of 10 and 20    ${CODE_EXECUTION_TIMEOUT}
    Response Should Contain    30
    
    Send Voice Command    Check available disk space    ${CODE_EXECUTION_TIMEOUT}
    Response Should Contain    space
    
    Log    Multiple tool usage test passed

*** Keywords ***
Setup Open Interpreter Test Suite
    [Documentation]    Set up the Open Interpreter test suite environment
    
    Log    Setting up Open Interpreter test suite
    Setup Jarvis Test Environment
    
    # Create test directories
    Create Directory    /tmp/jarvis_test
    
    Start Jarvis For Testing
    Wait For Jarvis Ready
    
    # Verify Open Interpreter is available
    Sleep    5s    # Extra time for Open Interpreter initialization
    
    Log    Open Interpreter test suite setup completed

Teardown Open Interpreter Test Suite
    [Documentation]    Clean up after Open Interpreter test suite
    
    Log    Tearing down Open Interpreter test suite
    Stop Jarvis Safely
    
    # Clean up test files
    Run Keyword And Ignore Error    Remove File    ${TEST_CSV_FILE}
    Run Keyword And Ignore Error    Remove File    ${TEST_SCRIPT_PATH}
    
    Teardown Jarvis Test Environment
    Log    Open Interpreter test suite teardown completed

Setup Individual Test
    [Documentation]    Set up for individual Open Interpreter test case
    
    Log    Setting up individual Open Interpreter test
    Sleep    2s    # Allow time between tests for Open Interpreter

Teardown Individual Test
    [Documentation]    Clean up after individual Open Interpreter test case
    
    Log    Cleaning up individual Open Interpreter test
    Sleep    2s    # Allow time for cleanup

Create Test CSV File
    [Documentation]    Create a test CSV file for analysis testing
    [Arguments]    ${file_path}
    
    ${csv_content}=    Set Variable    Name,Age,City\nJohn,25,New York\nJane,30,Los Angeles\nBob,35,Chicago\nAlice,28,Boston
    
    Create File    ${file_path}    ${csv_content}
    File Should Exist    ${file_path}
    
    Log    Test CSV file created: ${file_path}
