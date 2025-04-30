# Seed URLs to start crawling
SEED_URLS = [
    # "https://www.google.com/search?q=jobs",
    # "https://en.wikipedia.org/wiki/Main_Page",
    # "http://host.docker.internal:8000/test_limnkedin.html",
    # "http://host.docker.internal:8000/test_indeed.html",
    # Internshala seed URL
    "https://internshala.com/internships/",
    # Sample internship detail URLs for testing
    "https://internshala.com/internship/detail/ai-machine-learning-internship-in-noida-at-next-crest-media1745224020",  # Example ID;
    "https://internshala.com/internship/detail/full-stack-development-internship-in-mumbai-at-rentkar-switch-to-share1744960978",  # Example ID;
]

# Scrapy settings for politeness and scalability
SCRAPY_SETTINGS = {
    "USER_AGENT": "JobScraperBot/1.0 (+https://myjobscraper.com)",
    "ROBOTSTXT_OBEY": False,
    "CONCURRENT_REQUESTS": 2,
    "DOWNLOAD_DELAY": 1,
    "AUTOTHROTTLE_ENABLED": True,
    "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
    "LOG_LEVEL": "DEBUG",
    "RETRY_ENABLED": True,
    "RETRY_TIMES": 3,
    "DOWNLOAD_TIMEOUT": 30,
}

# RabbitMQ settings
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = "urls_to_classify"
