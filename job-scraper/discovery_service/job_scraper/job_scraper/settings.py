# discovery_service/job_scraper/job_scraper/settings.py
from job_scraper.config import SCRAPY_SETTINGS
import sys
import os

print("Initial sys.path:", sys.path)

# Get the absolute path to the discovery_service directory (two levels up)
discovery_service_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../")
)

# Add it to the Python path
if discovery_service_path not in sys.path:
    sys.path.insert(0, discovery_service_path)

print("Updated sys path:", sys.path)
print("Discovery service path added:", discovery_service_path)

# Now import from discovery_service

# Apply settings from config.py
for key, value in SCRAPY_SETTINGS.items():
    globals()[key] = value

# Additional Scrapy settings (Scrapy defaults)
BOT_NAME = "job_scraper"
SPIDER_MODULES = ["job_scraper.spiders"]
NEWSPIDER_MODULE = "job_scraper.spiders"

DOWNLOADER_MIDDLEWARES = {
    # Disable the built-in middleware
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "job_scraper.middlewares.CustomUserAgentMiddleware": 400,
    "scrapy_splash.SplashCookiesMiddleware": 723,
    "scrapy_splash.SplashMiddleware": 725,
    "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
    # Disable OffsiteMiddleware globally
    "scrapy.downloadermiddlewares.offsite.OffsiteMiddleware": None,
}

# Proxy settings (commented out for now)
# PROXY_LIST = "/app/proxies.txt"  # Path inside Docker container
# PROXY_MODE = 0  # 0 = random proxy per request

# Stealth settings
CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 5
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1  # Already low, but explicit for clarity
ROBOTSTXT_OBEY = False  # Already set, confirming bypass

# Add custom headers to mimic real browsers
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Crawl limit for testing
CLOSESPIDER_PAGECOUNT = 10  # Stop after crawling 10 pages
CLOSESPIDER_TIMEOUT = 300  # 5 minutes

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "job_scraper (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure Scrapy logs
LOG_LEVEL = 'DEBUG'
RETRY_ENABLED = True

# Memory-friendly settings
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 1024
MEMUSAGE_WARNING_MB = 768
DOWNLOAD_TIMEOUT = 180  # Changed from 30 to 180

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "job_scraper.middlewares.JobScraperSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "job_scraper.middlewares.JobScraperDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "job_scraper.pipelines.JobScraperPipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Splash settings
# SPLASH_URL = 'http://splash:8050'
# SPIDER_MIDDLEWARES = {
#     'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
# }
# DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
# HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# Simplify the Lua script in your spider
# SPLASH_ARGS = {
#     'lua_source': '''
#     function main(splash, args)
#         splash:set_viewport_size(1024, 768)
#         assert(splash:go(args.url))
#         assert(splash:wait(2))
#         return splash:html()
#     end
#     ''',
#     'timeout': 20,
#     'wait': 2
# }

# Custom middlewares
# DOWNLOADER_MIDDLEWARES.update({
#     'job_scraper.middlewares.CustomUserAgentMiddleware': 543,
#     'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
# })
