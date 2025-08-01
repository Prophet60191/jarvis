#!/usr/bin/env python3
"""
Web Automation Tool for carceralconsultation.com
Created by Jarvis - Comprehensive Chrome automation with data extraction
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def create_chrome_driver():
    """Initialize Chrome WebDriver with optimal settings."""
    options = Options()
    
    # Keep browser open for user to see
    options.add_experimental_option("detach", True)
    
    # Additional options for better automation
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # Try to use ChromeDriver from PATH first
        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        print("Please ensure ChromeDriver is installed and in your PATH")
        print("You can install it with: brew install chromedriver (on macOS)")
        return None

def safe_find_element(driver, by, value, timeout=10):
    """Safely find an element with timeout."""
    try:
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located((by, value)))
        return element
    except TimeoutException:
        return None

def safe_find_elements(driver, by, value, timeout=10):
    """Safely find multiple elements with timeout."""
    try:
        wait = WebDriverWait(driver, timeout)
        wait.until(EC.presence_of_element_located((by, value)))
        return driver.find_elements(by, value)
    except TimeoutException:
        return []

def extract_website_data(driver, url):
    """Extract comprehensive data from the website."""
    print(f"🌐 Navigating to {url}...")
    driver.get(url)
    
    # Wait for page to load
    time.sleep(3)
    
    print("📊 Extracting website data...")
    
    # Extract page title
    page_title = driver.title
    print(f"📄 Page Title: {page_title}")
    
    # Extract main headings (h1, h2, h3)
    main_headings = {
        "h1": [h.text.strip() for h in safe_find_elements(driver, By.TAG_NAME, "h1") if h.text.strip()],
        "h2": [h.text.strip() for h in safe_find_elements(driver, By.TAG_NAME, "h2") if h.text.strip()],
        "h3": [h.text.strip() for h in safe_find_elements(driver, By.TAG_NAME, "h3") if h.text.strip()]
    }
    
    print(f"📋 Found {len(main_headings['h1'])} H1 headings, {len(main_headings['h2'])} H2 headings, {len(main_headings['h3'])} H3 headings")
    
    # Extract contact information
    contact_info = {}
    
    # Look for phone numbers
    phone_links = safe_find_elements(driver, By.XPATH, "//a[contains(@href, 'tel:')]")
    if phone_links:
        contact_info["phones"] = [link.get_attribute("href").replace("tel:", "") for link in phone_links]
    
    # Look for email addresses
    email_links = safe_find_elements(driver, By.XPATH, "//a[contains(@href, 'mailto:')]")
    if email_links:
        contact_info["emails"] = [link.get_attribute("href").replace("mailto:", "") for link in email_links]
    
    # Look for address information
    address_elements = safe_find_elements(driver, By.XPATH, "//*[contains(text(), 'Address') or contains(text(), 'Location')]")
    if address_elements:
        contact_info["addresses"] = [elem.text.strip() for elem in address_elements if elem.text.strip()]
    
    print(f"📞 Contact Info: {len(contact_info)} types found")
    
    # Extract services offered (try multiple selectors)
    services_offered = []
    
    # Try common service selectors
    service_selectors = [
        ".service-box-title",
        ".service-title", 
        ".services h3",
        ".service h3",
        "[class*='service'] h3",
        "[class*='service'] h2"
    ]
    
    for selector in service_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                services_offered.extend([elem.text.strip() for elem in elements if elem.text.strip()])
                break
        except:
            continue
    
    # If no services found with specific selectors, look for general patterns
    if not services_offered:
        # Look for lists that might contain services
        list_items = safe_find_elements(driver, By.XPATH, "//ul/li | //ol/li")
        potential_services = [item.text.strip() for item in list_items if item.text.strip() and len(item.text.strip()) > 10]
        services_offered = potential_services[:10]  # Limit to first 10 items
    
    print(f"🛠️  Services: {len(services_offered)} found")
    
    # Extract additional metadata
    meta_description = ""
    meta_element = safe_find_element(driver, By.XPATH, "//meta[@name='description']")
    if meta_element:
        meta_description = meta_element.get_attribute("content")
    
    # Get page URL (in case of redirects)
    current_url = driver.current_url
    
    # Prepare comprehensive data structure
    extracted_data = {
        "extraction_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "url_requested": url,
        "url_actual": current_url,
        "page_title": page_title,
        "meta_description": meta_description,
        "main_headings": main_headings,
        "contact_info": contact_info,
        "services_offered": services_offered,
        "page_stats": {
            "total_links": len(safe_find_elements(driver, By.TAG_NAME, "a")),
            "total_images": len(safe_find_elements(driver, By.TAG_NAME, "img")),
            "total_headings": sum(len(headings) for headings in main_headings.values())
        }
    }
    
    return extracted_data

def main():
    """Main execution function."""
    print("🚀 Starting Web Automation Tool")
    print("=" * 50)
    
    # Initialize Chrome driver
    driver = create_chrome_driver()
    if not driver:
        print("❌ Failed to initialize Chrome driver")
        return
    
    try:
        # Target website
        target_url = "https://carceralconsultation.com"
        
        # Extract data
        data = extract_website_data(driver, target_url)
        
        # Save data to JSON file
        output_file = "carceralconsultation_data.json"
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Data extraction completed!")
        print(f"📁 Data saved to: {output_file}")
        print(f"🌐 Browser window will remain open for your inspection")
        
        # Print summary
        print("\n📊 EXTRACTION SUMMARY:")
        print(f"   Page Title: {data['page_title']}")
        print(f"   Total Headings: {data['page_stats']['total_headings']}")
        print(f"   Contact Methods: {len(data['contact_info'])}")
        print(f"   Services Found: {len(data['services_offered'])}")
        print(f"   Total Links: {data['page_stats']['total_links']}")
        
        # Keep browser open for user inspection
        print(f"\n🔍 Browser will stay open for inspection.")
        print(f"💡 Close the browser window manually when done.")
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
    
    # Note: We don't call driver.quit() to keep browser open for inspection

if __name__ == "__main__":
    main()
