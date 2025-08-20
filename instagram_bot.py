import config
import time
import random
import os
import json
import logging
import pickle
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

class InstagramBot:
    """
    A class to automate Instagram actions using undetected-chromedriver for stealth.
    """
    def __init__(self):
        self.config = config
        self._setup_logging()

        self.logger.info("Setting up stealth WebDriver for Brave Browser...")
        options = uc.ChromeOptions()

        # Point to the Brave Browser executable
        brave_path = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        if os.path.exists(brave_path):
            options.binary_location = brave_path
        else:
            self.logger.warning(f"Brave Browser not found at {brave_path}. The script will default to Chrome.")

        if self.config.HEADLESS_MODE:
            options.add_argument("--headless")

        try:
            self.driver = uc.Chrome(options=options)
        except Exception as e:
            self.logger.error("Failed to initialize undetected-chromedriver. Make sure you have Chrome installed.")
            self.logger.error(f"Error: {e}")
            raise

        self.processed_reels = self._load_processed_reels()

    def _human_delay(self, a=1.0, b=3.0):
        time.sleep(random.uniform(a, b))

    def _setup_logging(self):
        if not logging.getLogger(__name__).handlers:
            logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                                handlers=[logging.FileHandler(config.LOG_FILE_PATH, mode='w'), logging.StreamHandler()])
        self.logger = logging.getLogger(__name__)

    def _load_processed_reels(self):
        if not os.path.exists(self.config.PROCESSED_REELS_PATH): return set()
        with open(self.config.PROCESSED_REELS_PATH, 'r') as f:
            try: return set(json.load(f))
            except json.JSONDecodeError: return set()

    def _save_processed_reels(self):
        with open(self.config.PROCESSED_REELS_PATH, 'w') as f:
            json.dump(list(self.processed_reels), f, indent=4)

    def _wait_for_element(self, by, value, timeout=10):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for element: {value}")
            return None

    def login(self):
        self.logger.info("Attempting to log in...")
        self.driver.get("https://www.instagram.com/accounts/login/")
        self._human_delay(3, 5)

        try:
            username_box = self._wait_for_element(By.NAME, "username")
            password_box = self._wait_for_element(By.NAME, "password")
            if not username_box or not password_box:
                self.logger.error("Could not find login fields.")
                return False

            self.logger.info("Typing credentials...")
            for ch in self.config.USERNAME:
                username_box.send_keys(ch)
                time.sleep(random.uniform(0.1, 0.3))
            self._human_delay(0.5, 1)
            for ch in self.config.PASSWORD:
                password_box.send_keys(ch)
                time.sleep(random.uniform(0.1, 0.3))

            password_box.send_keys(Keys.RETURN)

            self.logger.info("Login attempt submitted. Pausing for 60 seconds for you to observe the browser...")
            self.logger.info("Please check the browser for any error messages, 2-Factor-Auth requests, or other popups.")
            time.sleep(60)

            self.logger.info("Checking for login confirmation...")
            # Check for a successful login by looking for the "Not Now" button for notifications
            not_now_button = self._wait_for_element(By.XPATH, "//button[contains(text(), 'Not Now')]")
            if not_now_button:
                not_now_button.click()
                self.logger.info("Login successful, handled notification popup.")
                return True
            # If popup not found, check for another element that confirms login
            elif self._wait_for_element(By.CSS_SELECTOR, "svg[aria-label='Home']"):
                 self.logger.info("Login successful.")
                 return True
            else:
                self.logger.error("Login failed. Could not confirm login.")
                return False
        except Exception as e:
            self.logger.error(f"An error occurred during login: {e}")
            return False

    def search_and_find_first_post(self):
        keyword = self.config.SEARCH_KEYWORD
        self.logger.info(f"Searching for first post for keyword: #{keyword}")
        self.driver.get(f"https://www.instagram.com/explore/tags/{keyword}/")
        self._human_delay(4, 6)

        try:
            self.logger.info("Looking for the first available post...")
            all_links = self._wait_for_element(By.XPATH, "//main//a[contains(@href, '/p/') or contains(@href, '/reel/')]", 20)
            if not all_links:
                self.logger.warning("No posts found on page.")
                return None

            all_links = self.driver.find_elements(By.XPATH, "//main//a[contains(@href, '/p/') or contains(@href, '/reel/')]")
            for link in all_links:
                href = link.get_attribute('href')
                if href and href not in self.processed_reels:
                    self.logger.info(f"Found new post: {href}")
                    return href

            self.logger.warning("All visible posts have already been processed.")
            return None
        except Exception as e:
            self.logger.error(f"Error finding first post: {e}")
            return None

    def comment_on_post(self, post_url):
        """
        Navigates to a post, types the comment, and submits it by pressing Enter.
        Includes a retry mechanism for stale elements.
        """
        self.logger.info(f"Navigating to post to comment: {post_url}")
        self.driver.get(post_url)
        self._human_delay(5, 8)

        try:
            self.logger.info("Searching for comment box using generic <textarea> tag...")
            comment_box = self._wait_for_element(By.TAG_NAME, "textarea", 15)

            if not comment_box:
                self.logger.error("Could not find a <textarea> on the page to comment in.")
                return False

            self.logger.info("Activating comment box...")
            try:
                ActionChains(self.driver).move_to_element(comment_box).click().perform()
            except Exception:
                self.driver.execute_script("arguments[0].click();", comment_box)

            self._human_delay(1, 2)

            self.logger.info("Setting comment text using JavaScript for multi-line support...")
            comment_text = self.config.COMMENT_TEXT

            # Use JavaScript to set the value, which is the only reliable way for multi-line text
            self.driver.execute_script("arguments[0].value = arguments[1];", comment_box, comment_text)
            # Trigger an input event to ensure the website's framework (like React) recognizes the change
            self.driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", comment_box)

            self._human_delay(1, 2)

            self.logger.info("Submitting comment with 'Enter' key...")
            comment_box.send_keys(Keys.RETURN)

            self.logger.info("✅ Comment submitted successfully!")
            self.processed_reels.add(post_url)
            self._human_delay(3, 5)
            return True

        except Exception as e:
            self.logger.error(f"An unexpected error occurred while trying to comment: {e}", exc_info=True)
            return False

    def close_session(self):
        self._save_processed_reels()
        self.logger.info("Session closed.")
        self.driver.quit()

if __name__ == "__main__":
    bot = InstagramBot()
    try:
        if bot.login():
            for keyword in config.SEARCH_KEYWORDS:
                bot.logger.info(f"--- Processing keyword: '{keyword}' ---")
                bot.config.SEARCH_KEYWORD = keyword

                post_url = bot.search_and_find_first_post()
                if post_url:
                    bot.comment_on_post(post_url)

                bot._human_delay(20, 40)
        else:
            bot.logger.error("Login failed. Shutting down.")
    except KeyboardInterrupt:
        bot.logger.info("Bot interrupted by user.")
    except Exception as e:
        bot.logger.critical(f"A critical error occurred: {e}", exc_info=True)
    finally:
        bot.logger.info("All keywords processed. Shutting down.")
        bot.close_session()
