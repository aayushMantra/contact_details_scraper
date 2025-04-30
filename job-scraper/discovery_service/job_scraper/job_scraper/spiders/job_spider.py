# discovery_service/job_scraper/job_scraper/spiders/job_spider.py
import time
import scrapy
from scrapy_splash import SplashRequest
from scrapy.linkextractors import LinkExtractor
import json
import logging
from job_scraper.rabbitmq import RabbitMQProducer
from job_scraper.config import SEED_URLS
from prometheus_client import Counter, Gauge, Histogram, start_http_server

logger = logging.getLogger(__name__)

# Prometheus metrics
urls_crawled = Counter(
    "job_spider_urls_crawled_total", "Total number of URLs crawled by the spider"
)
errors = Counter(
    "job_spider_errors_total", "Total number of errors encountered by the spider"
)
crawl_rate = Gauge(
    "job_spider_crawl_rate_urls_per_minute", "Crawl rate in URLs per minute"
)
response_time = Histogram(
    "job_spider_response_time_seconds",
    "Response time of crawled URLs in seconds",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

# Lua script to simulate human-like behavior in Splash
SPLASH_LUA_SCRIPT = """
function main(splash, args)
    splash:set_viewport_size(1920, 1080)
    splash:set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    -- Enable resource timeout
    splash.resource_timeout = 10
    
    -- Disable loading images
    splash.images_enabled = false
    
    local ok, reason = splash:go(args.url)
    if not ok then
        splash:log("Failed to load page: " .. reason)
        return {error = reason}
    end
    
    -- Wait for initial page load
    assert(splash:wait(3))

    -- Simulate scrolling with error handling
    for i=1,2 do
        local ok, err = pcall(function()
            splash:runjs('window.scrollBy(0, 500)')
            splash:wait(0.5)
        end)
        if not ok then splash:log("Scroll error: " .. err) end
    end

    -- Wait for any dynamic content to load
    assert(splash:wait(2))
    
    return {
        html = splash:html(),
        url = splash:url(),
        cookies = splash:get_cookies(),
        har = splash:har()
    }
end
"""

class JobSpider(scrapy.Spider):
    name = "job_spider"
    start_urls = SEED_URLS
    # Restrict to Internshala but allow all paths
    allowed_domains = ["internshala.com", "splash"]
    custom_settings = {
        "SPLASH_URL": "http://splash:8050",  # Ensure Splash URL is set
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy_splash.SplashCookiesMiddleware": 723,
            "scrapy_splash.SplashMiddleware": 725,
            "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
        },
        "SPIDER_MIDDLEWARES": {
            "scrapy_splash.SplashDeduplicateArgsMiddleware": 100,
        },
        "DUPEFILTER_CLASS": "scrapy_splash.SplashAwareDupeFilter",
        "HTTPCACHE_STORAGE": "scrapy_splash.SplashAwareFSCacheStorage",
        "CONCURRENT_REQUESTS": 2,  # Reduced to avoid overloading Splash
        "DOWNLOAD_DELAY": 5,      # Aligned with settings.py for politeness
        "DOWNLOAD_TIMEOUT": 90,   # Increased for Splash rendering
    }

    def __init__(self, *args, **kwargs):
        super(JobSpider, self).__init__(*args, **kwargs)
        logger.info("Initializing JobSpider")

        try:
            self.producer = RabbitMQProducer()
            self.rabbitmq_available = True
            logger.info("RabbitMQ producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RabbitMQ producer: {e}")
            self.rabbitmq_available = False
            self.producer = None
            logger.warning("Spider will run without RabbitMQ integration")

        # Initialize Prometheus metrics
        self.crawled_count = 0
        self.start_time = time.time()

        # Start Prometheus HTTP server to expose metrics on port 8000
        try:
            start_http_server(8000)
            logger.info("Prometheus metrics server started on port 8000")
        except Exception as e:
            logger.error(f"Failed to start Prometheus metrics server: {e}")

        # Link extractor for internship detail pages
        self.link_extractor = LinkExtractor(
            allow=r"/internship/detail/.*",  # Focus on internship detail pages
            deny=(),  # Allow all paths, including prohibited URLs
            allow_domains=["internshala.com"],
        )

    def start_requests(self):
        for url in self.start_urls:
            logger.info(f"Starting with URL: {url}")
            try:
                # First try with Playwright for JavaScript rendering
                logger.info(f"Requesting {url} with Playwright")
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    errback=self.handle_error,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            "wait_for_selector('body')",
                            "wait_for_timeout(3000)",
                        ],
                        "source_url": url,
                        "is_playwright": True,
                        "playwright_context_kwargs": {
                            "viewport": {"width": 1920, "height": 1080},
                            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                        },
                    },
                    dont_filter=False,
                )
            except Exception as e:
                logger.error(f"Error creating Playwright request for {url}: {e}")
                # Fallback to regular request
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    errback=self.handle_regular_error,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    },
                    meta={"source_url": url, "is_playwright": False},
                    dont_filter=True,
                )


    def parse(self, response):
        start_time = time.time()
        # Log the URL being crawled
        logger.info(
            f"Successfully crawled URL: {response.url} (Status: {response.status})"
        )

        # Increment URLs crawled counter
        urls_crawled.inc()
        self.crawled_count += 1

        # Update crawl rate
        elapsed_minutes = (time.time() - self.start_time) / 60.0
        if elapsed_minutes > 0:
            rate = self.crawled_count / elapsed_minutes
            crawl_rate.set(rate)

        # Record response time
        response_time.observe(time.time() - start_time)

        #  end the URL to the Classification Service via RabbitMQ
        if self.rabbitmq_available:
            message = {"url": response.url, "source": "discovery_service"}
            self.producer.publish(message)  # Remove the json.dumps() call
            logger.info(
                f"Published message to queue 'urls_to_classify': {message}")

        # Extract and follow internship detail links
        links = self.link_extractor.extract_links(response)
        for link in links:
            if self.is_valid_url(link.url):
                logger.info(f"Following link: {link.url}")
                yield SplashRequest(
                    link.url,
                    callback=self.parse,
                    endpoint="execute",
                    args={
                        "lua_source": SPLASH_LUA_SCRIPT,
                        "wait": 10,          # Increased to handle scrolling
                        "timeout": 90,       # Aligned with DOWNLOAD_TIMEOUT
                        "images": 0,
                        "render_all": 1,     # Ensure full page rendering
                    },
                    dont_filter=True,
                )

        # Fallback to general link extraction for other pages
        general_links = response.css("a::attr(href)").getall()
        for link in general_links:
            link = response.urljoin(link)
            if (
                self.is_valid_url(link)
                and "internshala.com" in link
                and link not in [l.url for l in links]
            ):
                logger.info(f"Following general link: {link}")
                yield SplashRequest(
                    link,
                    callback=self.parse,
                    endpoint="execute",
                    args={
                        "lua_source": SPLASH_LUA_SCRIPT,
                        "wait": 10,          # Increased to handle scrolling
                        "timeout": 90,       # Aligned with DOWNLOAD_TIMEOUT
                        "images": 0,
                        "render_all": 1,     # Ensure full page rendering
                    },
                    dont_filter=True,
                )

    def handle_error(self, failure):
        # Log failures
        logger.error(f"Failed to crawl URL: {failure.request.url}")
        logger.error(f"Error: {repr(failure)}")

        # Increment error counter
        errors.inc()

        if failure.value.response is None and "splash" in failure.request.meta.get("splash", {}):
            logger.info(f"Retrying URL with Splash: {failure.request.url}")
            yield SplashRequest(
                failure.request.url,
                callback=self.parse,
                errback=self.handle_error,
                endpoint="execute",
                args={
                    "lua_source": SPLASH_LUA_SCRIPT,
                    "wait": 10,
                    "timeout": 90,
                    "images": 0,
                },
                dont_filter=True,
            )

        # Try to extract the URL and requeue it with a different approach
        url = failure.request.url
        if url and self.is_valid_url(url):
            logger.info(f"Retrying URL with standard request: {url}")
            yield scrapy.Request(url, callback=self.parse, errback=self.handle_error)

    def is_valid_url(self, url):
        # Filter out non-HTTP links and irrelevant pages
        if not url.startswith(("http://", "https://")):
            return False
        if "#" in url or "mailto:" in url or "javascript:" in url:
            return False
        # Exclude file types like images, PDFs, etc.
        if url.endswith((".jpg", ".jpeg", ".png", ".pdf", ".zip")):
            return False
        return True

    def closed(self, reason):
        """Close RabbitMQ connection when spider is closed"""
        if self.producer is not None:
            self.producer.close()
        logger.info(f"Spider closed with reason: {reason}")