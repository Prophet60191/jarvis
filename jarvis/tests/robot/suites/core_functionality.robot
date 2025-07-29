*** Settings ***
Documentation    Core functionality tests for Jarvis Voice Assistant
...              This test suite covers basic Jarvis functionality including
...              wake word detection, speech recognition, and basic responses.

Resource         ../keywords/jarvis_keywords.robot
Library          ../libraries/JarvisLibrary.py

Suite Setup      Setup Test Suite
Suite Teardown   Teardown Test Suite
Test Setup       Setup Individual Test
Test Teardown    Teardown Individual Test

*** Variables ***
${WAKE_WORD}            jarvis
${TEST_TIMEOUT}         30s
${BASIC_COMMAND}        What time is it
${MEMORY_TEST_INFO}     I like coffee

*** Test Cases ***
Test Wake Word Detection
    [Documentation]    Test that Jarvis responds to wake word correctly
    [Tags]    core    wake-word    smoke
    
    Log    Testing wake word detection
    Activate Jarvis    ${WAKE_WORD}
    
    # Verify Jarvis is listening
    Send Voice Command    Hello
    Response Should Contain    hello
    
    Log    Wake word detection test passed

Test Basic Speech Recognition
    [Documentation]    Test basic speech recognition functionality
    [Tags]    core    speech-recognition    smoke
    
    Log    Testing basic speech recognition
    Activate Jarvis
    
    # Test simple command
    Send Command And Verify Response    ${BASIC_COMMAND}    time
    
    Log    Basic speech recognition test passed

Test Simple Question Response
    [Documentation]    Test Jarvis responds to simple questions
    [Tags]    core    responses    smoke
    
    Log    Testing simple question responses
    Activate Jarvis
    
    # Test general knowledge question
    Send Command And Verify Response    What is 2 plus 2    4
    
    Log    Simple question response test passed

Test Memory Storage
    [Documentation]    Test that Jarvis can store information in memory
    [Tags]    core    memory    smoke
    
    Log    Testing memory storage functionality
    Activate Jarvis
    
    # Store information
    Test Memory Storage    ${MEMORY_TEST_INFO}
    
    Log    Memory storage test passed

Test Memory Retrieval
    [Documentation]    Test that Jarvis can retrieve stored information
    [Tags]    core    memory    smoke
    
    Log    Testing memory retrieval functionality
    Activate Jarvis
    
    # Store and retrieve information
    Test Memory Workflow    ${MEMORY_TEST_INFO}    What do you remember about my preferences
    
    Log    Memory retrieval test passed

Test Error Handling
    [Documentation]    Test how Jarvis handles unclear or invalid commands
    [Tags]    core    error-handling
    
    Log    Testing error handling
    Activate Jarvis
    
    # Test with unclear command
    Test Error Handling    asdfghjkl random nonsense
    
    Log    Error handling test passed

Test System Health Check
    [Documentation]    Verify overall system health and responsiveness
    [Tags]    core    health-check    smoke
    
    Log    Testing system health
    Activate Jarvis
    
    # Verify system is responsive
    Verify System Health
    
    Log    System health check passed

Test Response Time Performance
    [Documentation]    Test that responses are within acceptable time limits
    [Tags]    core    performance
    
    Log    Testing response time performance
    Activate Jarvis
    
    # Measure response time for basic command
    ${response_time}=    Measure Response Time    ${BASIC_COMMAND}
    
    # Response should be under 15 seconds for basic commands
    Should Be True    ${response_time} < 15    Response time ${response_time}s exceeds 15s limit
    
    Log    Response time performance test passed: ${response_time}s

Test Multiple Commands In Sequence
    [Documentation]    Test handling multiple commands in sequence
    [Tags]    core    sequence    smoke
    
    Log    Testing multiple commands in sequence
    Activate Jarvis
    
    # Send multiple commands
    Send Command And Verify Response    What time is it    time
    Send Command And Verify Response    What is 5 plus 3    8
    Send Command And Verify Response    Hello Jarvis    hello
    
    Log    Multiple commands sequence test passed

Test Conversation Context
    [Documentation]    Test that Jarvis maintains conversation context
    [Tags]    core    context
    
    Log    Testing conversation context
    Activate Jarvis
    
    # Establish context
    Send Command And Verify Response    Remember that my favorite color is blue    remember
    
    # Test context retention
    Send Command And Verify Response    What is my favorite color    blue
    
    Log    Conversation context test passed

*** Keywords ***
Setup Test Suite
    [Documentation]    Set up the test suite environment
    
    Log    Setting up core functionality test suite
    Setup Jarvis Test Environment
    Start Jarvis For Testing
    Wait For Jarvis Ready
    Log    Test suite setup completed

Teardown Test Suite
    [Documentation]    Clean up after test suite
    
    Log    Tearing down core functionality test suite
    Stop Jarvis Safely
    Teardown Jarvis Test Environment
    Log    Test suite teardown completed

Setup Individual Test
    [Documentation]    Set up for individual test case
    
    Log    Setting up individual test
    # Reset any test state if needed
    Sleep    1s    # Brief pause between tests

Teardown Individual Test
    [Documentation]    Clean up after individual test case
    
    Log    Cleaning up individual test
    # Clean up any test-specific state
    Sleep    1s    # Brief pause after tests
