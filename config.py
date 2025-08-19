# Instagram Credentials
USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"

# Search Settings
SEARCH_KEYWORD = "travel"  # Can be a hashtag or a user account

# Comment Settings
COMMENTS = [
    "Awesome!",
    "Great content!",
    "Love this!",
    "So cool!",
    "Inspiring!",
]

# Bot Settings
NUM_REELS_TO_PROCESS = 10
HEADLESS_MODE = False  # Set to True to run without opening a browser window
LIKE_REEL = True  # Set to True to like the reel before commenting

# File Paths
CHROME_DRIVER_PATH = "path/to/your/chromedriver"  # Only needed if not using webdriver-manager
COOKIES_PATH = "instagram_cookies.pkl"
PROCESSED_REELS_PATH = "processed_reels.json"
LOG_FILE_PATH = "comment_log.txt"
