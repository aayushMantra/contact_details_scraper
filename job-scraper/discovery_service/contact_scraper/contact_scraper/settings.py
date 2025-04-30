# discovery_service/contact_scraper/contact_scraper/settings.py
from contact_scraper.config import SCRAPY_SETTINGS, CSV_FILE_PATH
import sys
import os

# Add the discovery_service directory to sys.path
discovery_service_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if discovery_service_path not in sys.path:
    sys.path.insert(0, discovery_service_path)

# Apply settings from config.py
for key, value in SCRAPY_SETTINGS.items():
    globals()[key] = value

# Scrapy settings
BOT_NAME = "contact_scraper"
SPIDER_MODULES = ["contact_scraper.spiders"]
NEWSPIDER_MODULE = "contact_scraper.spiders"

# Playwright settings
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Stealth settings
CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1
ROBOTSTXT_OBEY = False

# Default request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Crawl limits
CLOSESPIDER_PAGECOUNT = 20
CLOSESPIDER_TIMEOUT = 600

# Logging
LOG_LEVEL = 'INFO'
RETRY_ENABLED = True

# Memory settings
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 1024
MEMUSAGE_WARNING_MB = 768
DOWNLOAD_TIMEOUT = 180

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

RETRY_TIMES = 3

# CSV file settings
CSV_FILE_PATH = CSV_FILE_PATH

# Optional: Configure item pipelines
ITEM_PIPELINES = {
    # No custom pipelines needed as we're handling CSV directly
}

# Future-proof settings
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

FEED_EXPORT_ENCODING = "utf-8"

PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 60000,  # 60 seconds
}

# Rotate user agents
USER_AGENT_CHOICES = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
]

# Add a middleware to rotate user agents
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'contact_scraper.middlewares.CustomUserAgentMiddleware': 400,
}

# Default request headers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Add a middleware to rotate user agents
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'contact_scraper.middlewares.CustomUserAgentMiddleware': 400,
}


# Ensure FEED settings are correct for JSON output
FEEDS = {
    "/app/output/output.json": {
        "format": "json",
        "encoding": "utf8",
        "store_empty": True,
        "indent": 4,
    }
}
