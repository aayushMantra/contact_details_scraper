# discovery_service/job_scraper/middlewares.py
import logging
import random
from scrapy.http import HtmlResponse
from scrapy_user_agents.middlewares import RandomUserAgentMiddleware
import time

logger = logging.getLogger(__name__)

# Add UserAgentMiddleware configuration
class CustomUserAgentMiddleware(RandomUserAgentMiddleware):
    def __init__(self, user_agent_list):
        self.user_agent_list = user_agent_list

    @classmethod
    def from_crawler(cls, crawler):
        user_agent_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
        ]  # Free, manually curated list
        return cls(user_agent_list)

    def process_request(self, request, spider):
        request.headers["User-Agent"] = self.user_agent_list[
            spider.crawler.stats.get_value("user_agent_index", 0) % len(self.user_agent_list)
        ]
        request.headers["Accept-Language"] = random.choice(["en-US,en;q=0.5", "en-GB,en;q=0.5", "fr-FR,fr;q=0.5"])
        spider.crawler.stats.inc_value("user_agent_index", 1)
        return None