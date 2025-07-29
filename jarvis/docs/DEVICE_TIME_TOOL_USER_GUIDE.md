# 🕐 Device Time Tool User Guide

Complete guide for using the Device Time Tool with Jarvis Voice Assistant.

## 🎯 What is the Device Time Tool?

The Device Time Tool is one of Jarvis's core plugins that provides current time and date information from your local device. It's designed to be simple, reliable, and always available for quick time queries.

### **Key Features**
- **Instant time access**: Get current time with simple voice commands
- **Local timezone support**: Uses your system's configured timezone
- **12-hour format**: Returns time in easy-to-read AM/PM format
- **Error handling**: Graceful handling of system time issues
- **Always available**: Core plugin that's always loaded

## 🎤 Voice Commands

### **Basic Time Queries**

#### **Current Time**
```
"What time is it?"
"What's the current time?"
"Tell me the time"
"What's the time right now?"
"Give me the current time"
```

#### **Alternative Phrasings**
```
"What time do we have?"
"Can you tell me what time it is?"
"I need to know the time"
"Time check"
"Current time please"
```

### **Expected Responses**

When you ask for the time, Jarvis will respond with:

**Standard Response Format**:
```
"It's 2:30 PM"
"The current time is 9:15 AM"
"It's 11:45 PM"
```

**With Context** (sometimes):
```
"It's 2:30 PM on Tuesday"
"The time is 9:15 AM, July 29th"
```

## 🔧 How It Works

### **1. Voice Command Recognition**
1. You say a time-related query
2. Jarvis recognizes it as a time request
3. The command is routed to the Device Time Tool

### **2. System Time Retrieval**
1. Tool accesses your system's current time
2. Converts to 12-hour format with AM/PM
3. Formats the response for natural speech

### **3. Response Delivery**
1. Jarvis speaks the current time
2. Time is also displayed in the web interface (if open)
3. Response is logged for debugging purposes

## 📝 Usage Examples

### **Example 1: Basic Time Check**

**Voice Command**: "What time is it?"

**Jarvis Response**: "It's 2:30 PM"

**What Happens**:
1. Voice command is processed
2. Device Time Tool is called
3. System time (14:30) is converted to "2:30 PM"
4. Response is spoken back to you

### **Example 2: During a Meeting**

**Voice Command**: "Tell me the time"

**Jarvis Response**: "The current time is 3:45 PM"

**Use Case**: Quick time check without looking at clock or phone

### **Example 3: Late Night Check**

**Voice Command**: "What's the current time?"

**Jarvis Response**: "It's 11:30 PM"

**Use Case**: Check time when working late without screen glare

## ⚙️ Technical Details

### **Time Format**

**Input**: System time in 24-hour format (e.g., 14:30:00)
**Output**: 12-hour format with AM/PM (e.g., "2:30 PM")

**Conversion Examples**:
- 00:30 → "12:30 AM"
- 09:15 → "9:15 AM"
- 12:00 → "12:00 PM"
- 15:45 → "3:45 PM"
- 23:59 → "11:59 PM"

### **Timezone Handling**

The Device Time Tool uses your system's configured timezone:

- **Automatic Detection**: Uses system timezone settings
- **No Manual Configuration**: No need to set timezone in Jarvis
- **Daylight Saving**: Automatically handles DST changes
- **Cross-Platform**: Works on macOS, Linux, and Windows

### **Error Handling**

The tool includes robust error handling:

**System Time Unavailable**:
- Graceful error message
- Suggests checking system clock
- Logs error for debugging

**Format Conversion Issues**:
- Falls back to basic time display
- Ensures some response is always provided
- Logs technical details for troubleshooting

## 🔍 Troubleshooting

### **Common Issues**

#### **"Time not available" Error**

**Symptoms**: Jarvis says time is not available

**Solutions**:
1. **Check system clock**: Ensure your system time is set correctly
2. **Restart Jarvis**: Sometimes fixes temporary issues
3. **Check system permissions**: Ensure Jarvis can access system time

#### **Wrong Time Displayed**

**Symptoms**: Time is incorrect or in wrong timezone

**Solutions**:
1. **Check system timezone**: Verify your system timezone is correct
2. **Update system time**: Sync with time servers if needed
3. **Restart after timezone changes**: Restart Jarvis after changing timezone

#### **No Response to Time Commands**

**Symptoms**: Jarvis doesn't respond to "What time is it?"

**Solutions**:
1. **Check plugin loading**: Use "Check plugin status"
2. **Try alternative phrasing**: Use "Tell me the time"
3. **Check microphone**: Ensure voice commands are being heard
4. **Review logs**: Open debug logs to see what's happening

### **Debugging Commands**

```
"Check plugin status"           # Verify Device Time Tool is loaded
"Open debug logs"              # See technical details
"Test time tool"               # Direct plugin test (if available)
```

### **Log Analysis**

When debugging time tool issues, look for these log entries:

**Successful Operation**:
```
[DEBUG] device_time_tool: get_current_time() called
[DEBUG] device_time_tool: System time retrieved: 14:30:00
[DEBUG] device_time_tool: Converted to 12-hour: 2:30 PM
[INFO] device_time_tool: Returning time: "It's 2:30 PM"
```

**Error Condition**:
```
[ERROR] device_time_tool: Failed to get system time
[DEBUG] device_time_tool: Exception: [error details]
[WARNING] device_time_tool: Returning error message
```

## 🎯 Best Practices

### **Effective Usage**

**✅ Good Practices**:
- Use natural language: "What time is it?" works better than "Time"
- Speak clearly for better recognition
- Use during hands-free situations (cooking, working, etc.)

**✅ Alternative Commands**:
- Keep multiple phrasings in mind
- "Tell me the time" if "What time is it?" doesn't work
- "Current time please" for formal requests

### **Integration with Workflow**

**During Work**:
- Quick time checks without breaking focus
- Time awareness during video calls
- Scheduling and time management

**Daily Life**:
- Morning routine time checks
- Cooking and timing activities
- Bedtime awareness

### **Voice Recognition Tips**

1. **Clear Pronunciation**: Speak "time" clearly (not "thyme")
2. **Natural Pace**: Don't speak too fast or too slow
3. **Quiet Environment**: Reduce background noise for better recognition
4. **Consistent Phrasing**: Use commands that work reliably for you

## 🚀 Advanced Usage

### **Integration with Other Tools**

The Device Time Tool works well with other Jarvis features:

**With Memory System**:
```
"Remember that my meeting is at 3 PM"
# Later: "What time is it?" → "It's 2:45 PM"
# You know you have 15 minutes until the meeting
```

**With Scheduling**:
```
"What time is it?" → "It's 9 AM"
"Remember I have a call at 10 AM"
```

### **Automation Possibilities**

While the Device Time Tool itself is simple, it can be part of larger workflows:

**Time-Based Reminders**:
- Check time before important events
- Use with other tools for scheduling

**Productivity Tracking**:
- Time awareness during work sessions
- Break timing and management

## 🔧 Plugin Development Notes

### **For Developers**

The Device Time Tool serves as an excellent example of a simple, reliable plugin:

**Key Implementation Features**:
- Single function: `get_current_time()`
- Error handling with try/catch
- Consistent return format
- Clear documentation strings

**Code Structure**:
```python
@tool
def get_current_time() -> str:
    """Get the current time from the local device."""
    try:
        current_time = datetime.now()
        formatted_time = current_time.strftime("%I:%M %p")
        return f"It's {formatted_time}"
    except Exception as e:
        return "I'm sorry, I couldn't get the current time."
```

### **Extension Possibilities**

Developers could extend this tool with:
- Date information
- Multiple timezone support
- Time formatting options
- Calendar integration

## 📚 Additional Resources

### **Related Documentation**
- [Plugin Reference Guide](../PLUGIN_REFERENCE_GUIDE.md)
- [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)

### **System Time Resources**
- [Python datetime Documentation](https://docs.python.org/3/library/datetime.html)
- [System Time Configuration](https://support.apple.com/guide/mac-help/set-the-date-and-time-mchlp2996/mac) (macOS)
- [Linux Time Configuration](https://ubuntu.com/tutorials/setting-the-time-and-timezone)

### **Voice Command Resources**
- [Complete User Guide](../USER_GUIDE.md)
- [Voice Recognition Tips](TROUBLESHOOTING.md#voice-recognition-issues)

---

**Pro Tip**: The Device Time Tool is perfect for getting comfortable with Jarvis voice commands. It's simple, reliable, and always works. Use it to test your microphone setup and voice recognition before trying more complex features!
