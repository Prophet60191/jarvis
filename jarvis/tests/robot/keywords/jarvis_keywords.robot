*** Settings ***
Documentation    Common keywords for Jarvis Voice Assistant testing
Library          ../libraries/JarvisLibrary.py
Library          OperatingSystem
Library          Process
Library          Collections
Library          String

*** Variables ***
${JARVIS_STARTUP_TIMEOUT}    30s
${COMMAND_TIMEOUT}          15s
${RESPONSE_TIMEOUT}         10s
${TEST_CONFIG_FILE}         test_config.yaml

*** Keywords ***
# ============================================================================
# Setup and Teardown Keywords
# ============================================================================

Setup Jarvis Test Environment
    [Documentation]    Set up the test environment for Jarvis testing
    [Tags]    setup
    
    # Create test directories
    Create Directory    /tmp/jarvis_test
    Create Directory    /tmp/jarvis_test_memory
    
    # Clean up any existing test files
    Remove Files    /tmp/jarvis_test/*
    
    # Set test environment variables
    Set Environment Variable    JARVIS_TEST_MODE    true
    Set Environment Variable    PYTHONPATH    ${CURDIR}/../../../
    
    Log    Test environment setup completed

Teardown Jarvis Test Environment
    [Documentation]    Clean up the test environment after testing
    [Tags]    teardown
    
    # Stop Jarvis if still running
    Run Keyword And Ignore Error    Stop Jarvis Application
    
    # Clean up test files
    Run Keyword And Ignore Error    Remove Directory    /tmp/jarvis_test    recursive=True
    Run Keyword And Ignore Error    Remove Directory    /tmp/jarvis_test_memory    recursive=True
    
    # Clean up environment variables
    Remove Environment Variable    JARVIS_TEST_MODE
    
    Log    Test environment cleanup completed

# ============================================================================
# Jarvis Application Control Keywords
# ============================================================================

Start Jarvis For Testing
    [Documentation]    Start Jarvis application with test configuration
    [Arguments]    ${config_file}=${TEST_CONFIG_FILE}
    [Tags]    jarvis-control
    
    Log    Starting Jarvis with config: ${config_file}
    Start Jarvis Application    ${config_file}
    Sleep    3s    # Allow time for full startup
    Log    Jarvis started successfully

Stop Jarvis Safely
    [Documentation]    Stop Jarvis application safely with error handling
    [Tags]    jarvis-control
    
    ${status}=    Run Keyword And Return Status    Stop Jarvis Application
    Run Keyword If    not ${status}    Log    Warning: Jarvis may not have stopped cleanly    WARN
    Sleep    2s    # Allow time for cleanup
    Log    Jarvis stopped

# ============================================================================
# Voice Interaction Keywords
# ============================================================================

Activate Jarvis
    [Documentation]    Activate Jarvis with wake word
    [Arguments]    ${wake_word}=jarvis
    [Tags]    voice-interaction
    
    Log    Activating Jarvis with wake word: ${wake_word}
    Say Wake Word    ${wake_word}
    Sleep    1s    # Allow time for wake word processing
    Log    Jarvis activated

Send Voice Command
    [Documentation]    Send a voice command to Jarvis and wait for response
    [Arguments]    ${command}    ${timeout}=${RESPONSE_TIMEOUT}
    [Tags]    voice-interaction
    
    Log    Sending command: ${command}
    Say Command    ${command}
    Wait For Response    ${timeout}
    Log    Command sent and response received

Send Command And Verify Response
    [Documentation]    Send command and verify response contains expected text
    [Arguments]    ${command}    ${expected_text}    ${timeout}=${RESPONSE_TIMEOUT}
    [Tags]    voice-interaction
    
    Send Voice Command    ${command}    ${timeout}
    Response Should Contain    ${expected_text}
    Log    Command verified: ${command} -> ${expected_text}

# ============================================================================
# Tool Testing Keywords
# ============================================================================

Verify Tool Is Available
    [Documentation]    Verify that a specific tool is loaded and available
    [Arguments]    ${tool_name}
    [Tags]    tool-testing
    
    Log    Checking availability of tool: ${tool_name}
    Tool Should Be Available    ${tool_name}
    Log    Tool ${tool_name} is available

Test Tool Execution
    [Documentation]    Test execution of a specific tool with a command
    [Arguments]    ${tool_name}    ${command}    ${expected_response}
    [Tags]    tool-testing
    
    Log    Testing tool: ${tool_name}
    Verify Tool Is Available    ${tool_name}
    Send Command And Verify Response    ${command}    ${expected_response}
    Log    Tool ${tool_name} executed successfully

# ============================================================================
# Memory Testing Keywords
# ============================================================================

Test Memory Storage
    [Documentation]    Test storing information in memory
    [Arguments]    ${information}    ${memory_command}=Remember that ${information}
    [Tags]    memory-testing
    
    Log    Testing memory storage: ${information}
    Send Voice Command    ${memory_command}
    Response Should Contain    remember
    Log    Information stored in memory

Test Memory Retrieval
    [Documentation]    Test retrieving information from memory
    [Arguments]    ${query}    ${expected_info}
    [Tags]    memory-testing
    
    Log    Testing memory retrieval: ${query}
    Send Voice Command    ${query}
    Response Should Contain    ${expected_info}
    Log    Information retrieved from memory

Test Memory Workflow
    [Documentation]    Test complete memory workflow (store and retrieve)
    [Arguments]    ${information}    ${retrieval_query}
    [Tags]    memory-testing
    
    Test Memory Storage    ${information}
    Sleep    1s    # Allow time for storage processing
    Test Memory Retrieval    ${retrieval_query}    ${information}
    Log    Memory workflow completed successfully

# ============================================================================
# System Testing Keywords
# ============================================================================

Verify System Health
    [Documentation]    Verify that Jarvis system is healthy and responsive
    [Tags]    system-testing
    
    Log    Checking system health
    Send Command And Verify Response    What time is it    time
    Log    System health verified

Test Error Handling
    [Documentation]    Test how Jarvis handles invalid or problematic commands
    [Arguments]    ${invalid_command}
    [Tags]    system-testing
    
    Log    Testing error handling with: ${invalid_command}
    Send Voice Command    ${invalid_command}
    # Response should not contain error indicators
    Response Should Not Contain    error
    Response Should Not Contain    failed
    Response Should Not Contain    exception
    Log    Error handling test completed

# ============================================================================
# Performance Testing Keywords
# ============================================================================

Measure Response Time
    [Documentation]    Measure response time for a command
    [Arguments]    ${command}
    [Tags]    performance-testing
    
    ${start_time}=    Get Time    epoch
    Send Voice Command    ${command}
    ${end_time}=    Get Time    epoch
    ${response_time}=    Evaluate    ${end_time} - ${start_time}
    
    Log    Response time for "${command}": ${response_time} seconds
    Should Be True    ${response_time} < 30    Response time should be under 30 seconds
    
    RETURN    ${response_time}

# ============================================================================
# Utility Keywords
# ============================================================================

Create Test File
    [Documentation]    Create a test file for file analysis testing
    [Arguments]    ${file_path}    ${content}
    [Tags]    utility
    
    Create File    ${file_path}    ${content}
    File Should Exist    ${file_path}
    Log    Test file created: ${file_path}

Wait For Jarvis Ready
    [Documentation]    Wait for Jarvis to be fully ready for commands
    [Arguments]    ${timeout}=${JARVIS_STARTUP_TIMEOUT}
    [Tags]    utility
    
    Log    Waiting for Jarvis to be ready...
    Sleep    5s    # Basic wait for startup
    # Could add more sophisticated readiness checks here
    Log    Jarvis should be ready

Log Test Results
    [Documentation]    Log test results and system state
    [Arguments]    ${test_name}    ${result}
    [Tags]    utility
    
    Log    Test: ${test_name}
    Log    Result: ${result}
    Log    Timestamp: ${CURDIR}/../../../logs/test_${test_name}_${result}.log
