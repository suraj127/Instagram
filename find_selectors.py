import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def get_element_attributes(driver):
    script = (
        'let element = document.querySelector(":hover");\n'
        'if (!element) { return "No element is being hovered."; }\n'
        'let attributes = {};\n'
        'for (let i = 0; i < element.attributes.length; i++) {\n'
        '    let attr = element.attributes[i];\n'
        '    attributes[attr.name] = attr.value;\n'
        '}\n'
        'return {\n'
        "    'tagName': element.tagName,\n"
        "    'attributes': attributes,\n"
        "    'innerText': element.innerText.slice(0, 100)\n"
        '};'
    )
    try:
        return driver.execute_script(script)
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    print("--- Instagram Selector Finder ---")
    brave_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
    driver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
    if not os.path.exists(driver_path):
        print(f"CRITICAL ERROR: 'chromedriver.exe' not found in this folder: {os.getcwd()}")
        return
    chrome_options = Options()
    chrome_options.binary_location = brave_path
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    post_url = input("Enter the full Instagram post URL to inspect: ")
    if not post_url:
        print("No URL entered. Exiting.")
        driver.quit()
        return
    driver.get(post_url)
    print("\nPlease log in to Instagram manually in the browser window if you are not already logged in.")
    print("Once the post page is fully loaded, you are ready for the next step.")
    input("\n--- Step 1: Find the Comment Box ---\nMove your mouse pointer in the browser and hover it directly over the COMMENT BOX where you would type. Once your mouse is in position, come back here to the terminal and press Enter.")
    comment_box_info = get_element_attributes(driver)
    print("\n--- Comment Box Information ---")
    print(comment_box_info)
    print("-" * 30)
    input("\n--- Step 2: Find the Post Button ---\nNow, type something into the comment box in the browser to make the 'Post' button appear and become active. Then, move your mouse to hover directly over the POST BUTTON. Once in position, come back here and press Enter.")
    post_button_info = get_element_attributes(driver)
    print("\n--- Post Button Information ---")
    print(post_button_info)
    print("-" * 30)
    print("\nProcess complete. Please copy all the 'Information' output above and paste it back to me.")
    driver.quit()

if __name__ == "__main__":
    main()