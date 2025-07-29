# 🌐 LaVague Web Automation User Guide

Complete guide for using LaVague AI-powered web automation with Jarvis Voice Assistant.

## 🎯 What is LaVague Web Automation?

LaVague Web Automation enables you to control websites using natural language voice commands. Instead of manually clicking buttons and filling forms, you can simply tell Jarvis what you want to do on a website, and LaVague will perform those actions automatically.

### **Key Capabilities**
- **Natural language web control**: Describe what you want to do in plain English
- **Intelligent web navigation**: AI understands web page structure and content
- **Form filling**: Automatically fill out forms with specified information
- **Data extraction**: Scrape information from websites
- **Cross-site automation**: Work with any website without custom scripts

## 🛠️ Setup and Installation

### **1. Install LaVague**

```bash
# Install LaVague core and Selenium driver
pip install lavague-core lavague-drivers-selenium

# Install additional dependencies
pip install selenium webdriver-manager
```

### **2. Browser Setup**

LaVague uses Chrome/Chromium browser:

```bash
# Chrome will be automatically detected
# Or install Chromium if needed:
# macOS: brew install chromium
# Ubuntu: sudo apt install chromium-browser
```

### **3. Verify Setup**

Use Jarvis to check if LaVague is properly configured:

```
"Check LaVague status"
```

You should see confirmation that LaVague is installed and ready.

## 🎤 Voice Commands

### **Basic Web Navigation**

#### **Opening and Navigating Websites**
```
"Navigate to google.com"
"Go to amazon.com and search for laptops"
"Open reddit.com and go to the programming subreddit"
"Visit wikipedia.org and search for artificial intelligence"
```

#### **Clicking Elements**
```
"Click the login button on github.com"
"Click the search button"
"Click the 'Add to Cart' button"
"Click the menu icon in the top right"
```

#### **Scrolling and Navigation**
```
"Scroll down on this page"
"Go to the next page"
"Click the back button"
"Refresh the page"
```

### **Form Filling and Data Entry**

#### **Basic Form Filling**
```
"Fill out the contact form on example.com with my information"
"Enter 'john@email.com' in the email field"
"Type 'password123' in the password field"
"Select 'United States' from the country dropdown"
```

#### **Complex Form Operations**
```
"Fill out the registration form with name John Smith, email john@example.com, and phone 555-1234"
"Complete the checkout form with my billing address"
"Submit the survey with positive ratings for all questions"
```

### **Data Extraction and Scraping**

#### **Getting Information**
```
"Get the price from this product page"
"Extract the contact information from this website"
"What is the main headline on this news article?"
"Get all the email addresses from this page"
```

#### **Structured Data Extraction**
```
"Extract all product names and prices from this shopping page"
"Get the list of job titles from this careers page"
"Extract the restaurant hours and phone number"
"Get all the links from the navigation menu"
```

### **E-commerce Automation**

#### **Shopping Tasks**
```
"Search for 'wireless headphones' on Amazon"
"Add the first laptop under $1000 to cart"
"Find the cheapest iPhone on this electronics site"
"Compare prices of the same product on different sites"
```

#### **Account Management**
```
"Log into my account on this website"
"Update my profile information"
"Change my password to a new one"
"Add a new address to my account"
```

## 🔧 How It Works

### **1. Voice Command Processing**
1. You give a voice command describing the web task
2. Jarvis recognizes it as a web automation request
3. LaVague receives the natural language instruction

### **2. AI Web Understanding**
1. LaVague opens the specified website
2. AI analyzes the page structure and content
3. Identifies the relevant elements (buttons, forms, links)
4. Plans the sequence of actions needed

### **3. Automated Execution**
1. LaVague performs the actions (clicking, typing, scrolling)
2. Handles dynamic content and page changes
3. Extracts requested information if needed
4. Reports results back to Jarvis

## 📝 Usage Examples

### **Example 1: Online Shopping**

**Voice Command**: "Go to Amazon and search for wireless keyboards under $50"

**What Happens**:
1. Opens Amazon.com
2. Finds and clicks the search box
3. Types "wireless keyboards"
4. Applies price filter for under $50
5. Shows you the results

### **Example 2: Form Submission**

**Voice Command**: "Fill out the contact form on example.com with name John Doe, email john@example.com, and message 'Interested in your services'"

**What Happens**:
1. Navigates to example.com
2. Locates the contact form
3. Fills in the name field with "John Doe"
4. Enters the email address
5. Types the message in the message field
6. Submits the form

### **Example 3: Data Extraction**

**Voice Command**: "Extract the business hours and phone number from this restaurant website"

**What Happens**:
1. Scans the current webpage
2. Identifies sections containing business information
3. Extracts hours of operation
4. Finds and extracts phone number
5. Returns the structured information

## ⚙️ Configuration Options

### **Browser Settings**

**Headless Mode** (default for voice commands):
- Browser runs in background without visible window
- Faster execution
- Less resource intensive

**Visible Mode** (for debugging):
```
"Navigate to google.com with visible browser"
```

### **Timeout Settings**

LaVague automatically handles page loading and element waiting, but you can specify timeouts:

```
"Wait for the page to fully load before extracting data"
"Give the form 30 seconds to submit"
```

### **Data Format Options**

When extracting data, you can specify the format:

```
"Extract the product information as a list"
"Get the contact details in JSON format"
"Save the extracted data to a file"
```

## 🔍 Monitoring and Debugging

### **Checking Status**

```
"Check LaVague status"
```

This shows:
- LaVague installation status
- Browser availability
- Recent automation activity
- System capabilities

### **Troubleshooting Commands**

```
"Show me what's on the current page"
"Take a screenshot of the current page"
"What elements can be clicked on this page?"
```

### **Common Issues and Solutions**

**1. "LaVague not available"**
```bash
# Install LaVague
pip install lavague-core lavague-drivers-selenium
```

**2. "Browser not found"**
```bash
# Install Chrome or Chromium
# macOS: brew install google-chrome
# Ubuntu: sudo apt install google-chrome-stable
```

**3. "Element not found"**
- Try more specific descriptions
- Wait for page to fully load
- Check if element is in a popup or iframe

**4. "Page not loading"**
- Check internet connection
- Verify URL is correct
- Try with visible browser mode for debugging

## 🎯 Best Practices

### **Effective Voice Commands**

**✅ Good Commands**:
- "Fill out the login form with username 'john' and password 'secret'"
- "Extract all product prices from this page"
- "Click the blue 'Submit' button at the bottom"

**❌ Avoid Vague Commands**:
- "Do something on this website"
- "Click that thing"
- "Get the information"

### **Website Compatibility**

**Works Best With**:
- Standard HTML forms and buttons
- Common e-commerce sites
- News and information websites
- Social media platforms

**May Have Issues With**:
- Heavy JavaScript applications
- Sites with complex authentication
- Pages with unusual layouts
- Sites that block automation

### **Safety and Ethics**

1. **Respect robots.txt**: Don't automate sites that prohibit it
2. **Rate limiting**: Don't overwhelm servers with rapid requests
3. **Terms of service**: Ensure automation is allowed
4. **Personal data**: Be careful with sensitive information
5. **Testing**: Use test sites for learning and development

## 🚀 Advanced Features

### **Multi-Step Workflows**

```
"Go to LinkedIn, search for software engineers in San Francisco, 
 and save the first 10 profiles to a list"
```

### **Conditional Actions**

```
"If the product is in stock, add it to cart, otherwise notify me"
"Check if there are any new messages and read them to me"
```

### **Cross-Site Comparisons**

```
"Compare the price of iPhone 14 on Amazon, Best Buy, and Apple.com"
"Find the same product on three different shopping sites"
```

### **Scheduled Automation**

```
"Check this website every hour for new job postings"
"Monitor this product page for price changes"
```

## 🛡️ Security Considerations

### **Safe Practices**
- Never automate login with real credentials on untrusted sites
- Use test accounts for experimentation
- Be aware of what information you're sharing
- Review extracted data before using it

### **Privacy Protection**
- LaVague runs locally on your machine
- No data is sent to external servers
- Browser sessions are isolated
- Cookies and data are cleared after sessions

## 📚 Additional Resources

### **LaVague Documentation**
- [Official LaVague Documentation](https://docs.lavague.ai/)
- [LaVague GitHub Repository](https://github.com/lavague-ai/LaVague)

### **Web Automation Best Practices**
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Web Scraping Ethics](https://blog.apify.com/web-scraping-ethics/)

### **Jarvis Integration**
- [Plugin Reference Guide](../PLUGIN_REFERENCE_GUIDE.md)
- [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

---

**Pro Tip**: Start with simple tasks like navigating to websites and clicking buttons. As you get comfortable, move on to form filling and data extraction. LaVague's AI is quite capable, but clear, specific instructions always work best!
