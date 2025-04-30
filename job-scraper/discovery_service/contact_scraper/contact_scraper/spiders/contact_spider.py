import os
import re
import logging
import scrapy
from scrapy.linkextractors import LinkExtractor
from contact_scraper.config import SEED_URLS
from contact_scraper.csv_handler import CSVHandler

logger = logging.getLogger(__name__)

class ContactSpider(scrapy.Spider):
    name = "contact_spider"
    allowed_domains = []
    custom_settings = {
        "CONCURRENT_REQUESTS": 2,
        "DOWNLOAD_DELAY": 3,
        "DOWNLOAD_TIMEOUT": 60,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 408, 429],
    }

    def __init__(self, csv_file=None, *args, **kwargs):
        super(ContactSpider, self).__init__(*args, **kwargs)
        logger.info("Initializing ContactSpider")

        # Initialize CSV handler
        self.csv_file = csv_file or os.path.join("/app/output", "contact_data.csv")
        logger.info(f"Using CSV file: {self.csv_file}")
        self.csv_handler = CSVHandler(self.csv_file)

        # Link extractor for social media links
        self.social_media_domains = [
            "linkedin.com",
            "twitter.com",
            "facebook.com",
            "instagram.com",
            "youtube.com",
            "pinterest.com",
            "tiktok.com",
            "reddit.com",
        ]
        self.social_link_extractor = LinkExtractor(
            allow_domains=self.social_media_domains,
            deny=(),
        )

        # Link extractor for "Contact Us" or similar pages
        self.contact_link_extractor = LinkExtractor(
            allow=r"/(contact|about|support|help|info).*",
            deny=(),
        )

        # Set start URLs from CSV or fallback to config
        urls_from_csv = self.csv_handler.get_urls()
        if urls_from_csv:
            self.start_urls = urls_from_csv
            logger.info(f"Starting with {len(self.start_urls)} URLs from CSV")
        else:
            self.start_urls = SEED_URLS
            logger.info(f"No URLs found in CSV, using {len(self.start_urls)} seed URLs")

    def parse(self, response):
        logger.info(f"Parsing URL: {response.url}")
        source_url = response.meta.get("source_url", response.url)

        # Log response status and size
        logger.info(
            f"Response status: {response.status}, size: {len(response.body)} bytes"
        )
        
         # Check if this is a Playwright response
        is_playwright = response.meta.get("is_playwright", False)
        logger.info(f"Using Playwright: {is_playwright}")
        
         # Close the Playwright page if it exists
        if is_playwright and "playwright_page" in response.meta:
            page = response.meta["playwright_page"]
            page.close()
            logger.info("Closed Playwright page")

        # Extract emails and social media links
        emails = self.extract_emails(response)
        logger.info(f"Extracted emails: {emails}")

        social_links = self.extract_social_links(response)
        logger.info(f"Extracted social links: {social_links}")

        # Update CSV with extracted data
        self.csv_handler.update_result(source_url, emails, social_links)

        # Yield data for optional JSON output
        yield {
            "url": source_url,
            "emails": list(emails),
            "social_media_links": list(social_links),
        }

        # Follow "Contact Us" links
        contact_links = self.contact_link_extractor.extract_links(response)
        for link in contact_links[:3]:  # Limit to 3 links
            if self.is_valid_url(link.url):
                logger.info(f"Following contact link: {link.url}")
                yield scrapy.Request(
                    link.url,
                    callback=self.parse_contact_page,
                    errback=self.handle_error,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            'wait_for_selector("body")',
                            "wait_for_timeout(3000)",
                        ],
                        "source_url": source_url,
                        "is_playwright": True,
                    },
                    dont_filter=False,
                )

    def parse_contact_page(self, response):
        """Parse a contact page and update the original URL's data."""
        logger.info(f"Parsing contact page: {response.url}")
        source_url = response.meta.get("source_url")
        
         # Check if this is a Playwright response
        is_playwright = response.meta.get("is_playwright", False)
        logger.info(f"Using Playwright for contact page: {is_playwright}")
        
        # Close the Playwright page if it exists
        if is_playwright and "playwright_page" in response.meta:
            page = response.meta["playwright_page"]
            page.close()
            logger.info("Closed Playwright page for contact page")

        # Extract emails and social links
        emails = self.extract_emails(response)
        social_links = self.extract_social_links(response)

        if emails or social_links:
            logger.info(f"Found additional data on contact page for {source_url}")
            self.csv_handler.update_result(source_url, emails, social_links)

    def extract_emails(self, response):
        """Extract email addresses from the page using regex."""

        text = response.text + " ".join(response.xpath("//text()").getall())
        logger.info(f"Text content length for email extraction: {len(text)} characters")

        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = set(re.findall(email_pattern, text, re.IGNORECASE))

        # Log all found emails before filtering
        logger.info(f"All found emails before filtering: {emails}")

        # Filter out false positives
        filtered_emails = {
            email
            for email in emails
            if "example" not in email
            and "your-email" not in email
            and "@your" not in email
            and "user@" not in email
            and "username@" not in email
        }
        return filtered_emails

    def extract_social_links(self, response):
        """Extract social media links from the page."""
        social_links = set()

        # Extract links using LinkExtractor
        links = self.social_link_extractor.extract_links(response)
        for link in links:
            social_links.add(link.url)

        # Also check footer, header, and social-specific sections
        selectors = [
             "footer a::attr(href)",
            ".footer a::attr(href)",
            "header a::attr(href)",
            ".header a::attr(href)",
            ".social a::attr(href)",
            ".social-media a::attr(href)",
            ".social-links a::attr(href)",
            ".socials a::attr(href)",
            "[class*='social'] a::attr(href)",
        ]
        for selector in selectors:
            for link in response.css(selector).getall():
                full_link = response.urljoin(link)
                if any(domain in full_link for domain in self.social_media_domains):
                    social_links.add(full_link)

        return social_links

    def handle_error(self, failure):
        logger.error(f"Failed to crawl URL: {failure.request.url}")
        logger.error(f"Error: {repr(failure)}")

        # Get the source URL
        source_url = failure.request.meta.get("source_url")
        
        # Check if this was a Playwright request
        is_playwright = failure.request.meta.get("is_playwright", False)
        
        if is_playwright:
            logger.info(f"Playwright request failed for {failure.request.url}. Trying with regular request.")
            # If Playwright failed, try with a regular request
            yield scrapy.Request(
                failure.request.url,
                callback=self.parse,
                errback=self.handle_regular_error,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                },
                meta={"source_url": source_url, "is_playwright": False},
                dont_filter=True,
            )
        else:
            # Count the error
            self.crawler.stats.inc_value("error_count")
            
            # Update CSV even if error occurred
            if source_url:
                self.csv_handler.update_result(source_url, [], [])
                
    def handle_regular_error(self, failure):
        """Handle errors from regular (non-Playwright) requests."""
        logger.error(f"Regular request failed for URL: {failure.request.url}")
        logger.error(f"Error: {repr(failure)}")
        
        # Count the error
        self.crawler.stats.inc_value("error_count")
        
        # Update CSV even if error occurred
        source_url = failure.request.meta.get("source_url")
        if source_url:
            self.csv_handler.update_result(source_url, [], [])


    def is_valid_url(self, url):
        """Check if the URL is valid for crawling."""
        if not url.startswith(("http://", "https://")):
            return False
        if "#" in url or "mailto:" in url or "javascript:" in url:
            return False
        if url.endswith((".jpg", ".jpeg", ".png", ".pdf", ".zip")):
            return False
        return True
