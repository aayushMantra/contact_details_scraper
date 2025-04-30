# discovery_service/contact_scraper/contact_scraper/middlewares.py
import logging
import random
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from contact_scraper.settings import USER_AGENT_CHOICES

logger = logging.getLogger(__name__)

class CustomUserAgentMiddleware(UserAgentMiddleware):
    """Middleware to rotate user agents for each request."""
    
    def process_request(self, request, spider):
        user_agent = random.choice(USER_AGENT_CHOICES)
        request.headers['User-Agent'] = user_agent
        logger.debug(f"Using User-Agent: {user_agent}")
        return None
