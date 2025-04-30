# discovery_service/contact_scraper/contact_scraper/config.py

# CSV file path for input/output
CSV_FILE_PATH = "/app/output/contact_data.csv"

# Initial URLs to start crawling
SEED_URLS = [
    "https://granth.in/",  # Replace with your target website URL
    # Add more URLs as needed
    "https://esupl.com/",
    "https://peg.co/",
    "https://morbax.com",
    "https://www.motionedits.com/",
    "https://www.vidzy.in/",
    "https://increditors.com/",
    "https://www.videocaddy.com/"
]

# Scrapy settings for politeness and scalability
SCRAPY_SETTINGS = {
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "ROBOTSTXT_OBEY": False,
    "CONCURRENT_REQUESTS": 2,
    "DOWNLOAD_DELAY": 3,
    "AUTOTHROTTLE_ENABLED": True,
    "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
    "LOG_LEVEL": "INFO",
    "RETRY_ENABLED": True,
    "RETRY_TIMES": 3,
    "DOWNLOAD_TIMEOUT": 180,
}

# RabbitMQ settings (for future use)
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = "contact_data"
