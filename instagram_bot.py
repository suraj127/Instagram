import config
import time
import random
import os
import json
import logging
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class InstagramBot:
    """
    A class to automate Instagram actions such as logging in, searching,
    and commenting on reels.
    """
    def __init__(self):
        """
        Initializes the InstagramBot.
        - Sets up Chrome options (e.g., headless mode).
        - Initializes the WebDriver.
        - Loads processed reels from the JSON file.
        - Configures logging.
        """
        self.config = config
        self._setup_logging() # Setup logging first to capture all messages

        # --- Settings for Brave Browser ---
        brave_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        driver_path = os.path.join(os.getcwd(), 'chromedriver.exe')

        # --- VERY IMPORTANT: Check if chromedriver.exe exists ---
        if not os.path.exists(driver_path):
            self.logger.error("="*80)
            self.logger.error("CRITICAL ERROR: 'chromedriver.exe' not found!")
            self.logger.error(f"The script is looking for it in this exact folder: {os.getcwd()}")
            self.logger.error("Please make sure you have downloaded chromedriver.exe and placed it in that folder.")
            self.logger.error("="*80)
            raise FileNotFoundError("Could not find chromedriver.exe. Please read the error message above.")

        # Check if Brave browser exists at the specified path
        if not os.path.exists(brave_path):
             self.logger.warning(f"Warning: Brave Browser not found at the default path: {brave_path}")
             self.logger.warning("If the bot fails to start, please check that this path is correct.")

        chrome_options = Options()
        chrome_options.binary_location = brave_path

        if self.config.HEADLESS_MODE:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--log-level=3")

<<<<<<< Updated upstream
=======
        # Use the manually downloaded chromedriver.exe from the project folder
        driver_path = os.path.join(os.getcwd(), 'chromedriver.exe')
>>>>>>> Stashed changes
        service = Service(executable_path=driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        self.processed_reels = self._load_processed_reels()

    def _setup_logging(self):
        """
        Configures logging to print to console and save to a file.
        """
        # Ensure logger is not configured multiple times
        if not logging.getLogger(__name__).handlers:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)s] %(message)s",
                handlers=[
                    logging.FileHandler(self.config.LOG_FILE_PATH, mode='w'),
                    logging.StreamHandler()
                ]
            )
        self.logger = logging.getLogger(__name__)

    def _load_processed_reels(self):
        """
        Loads the set of processed reel URLs from the JSON file.
        """
        if not os.path.exists(self.config.PROCESSED_REELS_PATH):
            return set()
        with open(self.config.PROCESSED_REELS_PATH, 'r') as f:
            try:
                urls = json.load(f)
                return set(urls)
            except json.JSONDecodeError:
                return set()

    def _save_processed_reels(self):
        """
        Saves the set of processed reel URLs to the JSON file.
        """
        with open(self.config.PROCESSED_REELS_PATH, 'w') as f:
            json.dump(list(self.processed_reels), f, indent=4)

    def _wait_for_element(self, by, value, timeout=10):
        """
        Waits for an element to be present on the page.
        """
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for element: {value}")
            return None

    def _handle_popups(self):
        """
        Handles post-login popups like 'Save Info' and 'Turn on Notifications'.
        """
        # Using a more generic xpath to find the "Not Now" button for notifications
        try:
            not_now_button = self._wait_for_element(By.XPATH, "//button[contains(text(),'Not Now')]", timeout=8)
            if not_now_button:
                not_now_button.click()
                self.logger.info("Handled 'Turn on Notifications' popup.")
                time.sleep(random.uniform(1, 2))
        except Exception:
            self.logger.info("'Turn on Notifications' popup not found, skipping.")

        # Handle "Save your login info?" popup
        try:
            # This popup sometimes appears with different text, so we look for a button within a specific dialog
            save_info_button = self._wait_for_element(By.XPATH, "//div[@role='dialog']//button[contains(text(),'Save Info') or contains(text(),'Not Now')]", timeout=8)
            if save_info_button:
                save_info_button.click()
                self.logger.info("Handled 'Save Info' popup.")
                time.sleep(random.uniform(1, 2))
        except Exception:
            self.logger.info("'Save Info' popup not found, skipping.")


    def login(self):
        """
        Logs into Instagram using cookies or credentials.
        """
        self.logger.info("Attempting to log in...")
        self.driver.get("https://www.instagram.com/")
        time.sleep(random.uniform(3, 5))

        # Try to load cookies
        cookies_path = self.config.COOKIES_PATH
        if os.path.exists(cookies_path):
            self.logger.info("Found cookies file. Loading cookies...")
            with open(cookies_path, 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)

            self.driver.refresh()
            time.sleep(random.uniform(4, 6))

            # Check if login was successful by looking for a key element (e.g., Home icon)
            if self._wait_for_element(By.XPATH, "//*[local-name()='svg'][@aria-label='Home']", timeout=10):
                 self.logger.info("Login successful via cookies.")
                 self._handle_popups()
                 return True
            else:
                 self.logger.warning("Cookie login failed. Proceeding with credentials.")

        # If cookies fail or don't exist, log in with credentials
        try:
            self.logger.info("Logging in with username and password.")
            username_field = self._wait_for_element(By.NAME, "username")
            password_field = self._wait_for_element(By.NAME, "password")

            if not username_field or not password_field:
                self.logger.error("Could not find username or password field.")
                return False

            username_field.send_keys(self.config.USERNAME)
            time.sleep(random.uniform(1, 2))
            password_field.send_keys(self.config.PASSWORD)
            time.sleep(random.uniform(1, 2))
            password_field.send_keys(Keys.RETURN)

            # Wait for login to complete
            if not self._wait_for_element(By.XPATH, "//*[local-name()='svg'][@aria-label='Home']", timeout=15):
                self.logger.error("Login failed. Please check your credentials.")
                return False

            self.logger.info("Login successful.")

            self._handle_popups()

            with open(cookies_path, 'wb') as f:
                pickle.dump(self.driver.get_cookies(), f)
            self.logger.info(f"Cookies saved to {cookies_path}")

            return True

        except Exception as e:
            self.logger.error(f"An error occurred during login: {e}")
            return False

    def search_and_collect_reels(self):
        """
        Searches for a keyword and finds the first available post/reel that has
        not been processed yet.
        """
        keyword = self.config.SEARCH_KEYWORD
        self.logger.info(f"Searching for the first post for keyword: #{keyword}")

        url = f"https://www.instagram.com/explore/tags/{keyword}/"
        self.driver.get(url)

        # Wait for the first post/reel link to be available
        try:
            self.logger.info("Waiting for posts to load...")
            post_element = self._wait_for_element(
                By.XPATH,
                "//main//a[contains(@href, '/p/') or contains(@href, '/reel/')]",
                timeout=20
            )

            if not post_element:
                self.logger.warning("No posts found on the page for this keyword.")
                return []

            # Find all links and iterate to find the first unprocessed one
            all_links = self.driver.find_elements(By.XPATH, "//main//a[contains(@href, '/p/') or contains(@href, '/reel/')]")
            for link in all_links:
                href = link.get_attribute('href')
                if href and href not in self.processed_reels:
                    self.logger.info(f"Found new post to process: {href}")
                    self.reels_to_process = [href] # Return a list with this single URL
                    return self.reels_to_process

            self.logger.warning("All visible posts have already been processed. Nothing new to comment on.")
            return []

        except Exception as e:
            self.logger.error(f"An error occurred while trying to find the first post: {e}")
            return []

    def _like_reel(self, reel_url):
        """
        Likes the currently open reel if the option is enabled.
        """
        if not self.config.LIKE_REEL:
            return

        try:
            like_button = self._wait_for_element(By.XPATH, "//*[local-name()='svg'][@aria-label='Like']", timeout=5)
            if like_button:
                like_button.find_element(By.XPATH, './ancestor::button').click()
                self.logger.info(f"Liked reel: {reel_url}")
                time.sleep(random.uniform(1, 2))
            else:
                self.logger.info("Reel might already be liked or button not found.")
        except Exception as e:
            self.logger.warning(f"Could not like the reel {reel_url}: {e}")

    def _post_comment(self, reel_url):
        """
        Posts the fixed comment from the config file on the currently open reel.
        Uses JavaScript to handle multi-line text correctly.
        """
        try:
            comment_box = self._wait_for_element(By.CSS_SELECTOR, "textarea[aria-label='Add a comment…']", timeout=10)
            if not comment_box:
                self.logger.warning(f"Comment box not found on {reel_url}. Comments may be disabled.")
                return False

            comment_text = self.config.COMMENT_TEXT

            # Use JavaScript to set the value, which is more reliable for multi-line text
            self.driver.execute_script("arguments[0].value = arguments[1];", comment_box, comment_text)
            # Trigger an input event to ensure the website's framework (like React) recognizes the change
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", comment_box)

            time.sleep(random.uniform(1, 2)) # Brief pause after entering text

            # The selector for the post button can be fragile. This is a best guess.
            post_button = self.driver.find_element(By.XPATH, "//div[./textarea]/following-sibling::div/button[@type='submit']")
            if not post_button.is_enabled():
                self.logger.warning(f"Post button is not enabled for reel: {reel_url}. Trying a different selector.")
                # Fallback selector
                post_button = self.driver.find_element(By.XPATH, "//button[contains(text(),'Post')]")
                if not post_button.is_enabled():
                    self.logger.error(f"Post button remains disabled for reel: {reel_url}")
                    return False

            post_button.click()
            self.logger.info(f"✅ Comment posted successfully on reel: {reel_url}")
            time.sleep(random.uniform(4, 6)) # Wait for comment to appear
            return True

        except NoSuchElementException:
            self.logger.warning(f"Could not find the comment box or post button on {reel_url}. Structure may have changed.")
            return False
        except Exception as e:
            self.logger.error(f"An error occurred while commenting on {reel_url}: {e}")
            return False

    def comment_on_reels(self):
        """
        Iterates through the collected reels and performs actions (like/comment).
        """
        if not hasattr(self, 'reels_to_process') or not self.reels_to_process:
            self.logger.info("No new reels to process.")
            return

        self.logger.info(f"Starting to process {len(self.reels_to_process)} reels.")

        for reel_url in self.reels_to_process:
            if reel_url in self.processed_reels:
                self.logger.info(f"Skipping already processed reel: {reel_url}")
                continue

            try:
                self.driver.get(reel_url)
                self.logger.info(f"Navigated to reel: {reel_url}")
                time.sleep(random.uniform(5, 8))

                self._like_reel(reel_url)

                if self._post_comment(reel_url):
                    self.processed_reels.add(reel_url)
                else:
                    self.logger.warning(f"Failed to comment on reel: {reel_url}. It will be skipped.")

                sleep_duration = random.uniform(15, 30)
                self.logger.info(f"Pausing for {sleep_duration:.2f} seconds before next reel...")
                time.sleep(sleep_duration)

            except Exception as e:
                self.logger.error(f"A critical error occurred while processing reel {reel_url}: {e}")
                continue

        self.logger.info("Finished processing all collected reels.")

    def close_session(self):
        """
        Saves processed reels and closes the WebDriver.
        """
        self._save_processed_reels()
        self.logger.info("Session closed. Processed reels saved.")
        self.driver.quit()

if __name__ == "__main__":
    bot = InstagramBot()
    try:
        if bot.login():
            # Loop through the keywords defined in the config file
            for keyword in config.SEARCH_KEYWORDS:
                bot.logger.info(f"--- Starting process for keyword: '{keyword}' ---")
                bot.config.SEARCH_KEYWORD = keyword

                # Find and process the first post for this keyword
                reels = bot.search_and_collect_reels()
                if reels:
                    bot.comment_on_reels()

                pause_duration = random.uniform(20, 40)
                bot.logger.info(f"Finished with keyword '{keyword}'. Pausing for {pause_duration:.2f}s.")
                time.sleep(pause_duration)
        else:
            bot.logger.error("Bot could not log in. Shutting down.")

    except KeyboardInterrupt:
        bot.logger.info("Bot execution interrupted by user.")
    except Exception as e:
        bot.logger.critical(f"A critical error occurred during the main execution: {e}", exc_info=True)
    finally:
        bot.logger.info("All keywords processed. Shutting down bot session.")
        bot.close_session()
