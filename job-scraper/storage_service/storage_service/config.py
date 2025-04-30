# job-scraper/storage_service/config.py
import os
import logging
from urllib.parse import quote_plus

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# RabbitMQ settings
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = "urls_to_extract"  # Queue to consume from
RABBITMQ_STORE_QUEUE = "data_to_store"
RABBITMQ_EXCHANGE = ""  # Default exchange
USER_AGENT = "JobScraperExtractor/1.0 (+https://myjobscraper.com)"

# PostgreSQL settings
POSTGRES_USER = "aayush"
POSTGRES_PASSWORD = "A@yush191102"
POSTGRES_HOST = "postgres"
POSTGRES_PORT = 5432
POSTGRES_DB = "job_scraper_db"
encoded_password = quote_plus(POSTGRES_PASSWORD)
POSTGRES_URL = f"postgresql://{POSTGRES_USER}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

logger.info(f"Database URL (with password masked): postgresql://{POSTGRES_USER}:****@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

# Elasticsearch settings
ELASTICSEARCH_HOST = "elasticsearch"
ELASTICSEARCH_PORT = 9200
ELASTICSEARCH_INDEX = "job_postings"

# Default values for missing fields
DEFAULT_VALUES = {
    "title": "Not specified",
    "company": "Not specified",
    "location": "Not specified",
    "description": "Not specified",
    "salary": "Not specified",
    "url": "Not specified",
    "source": "Not specified",
    "date_posted": "1970-01-01T00:00:00Z"  # ISO default
}

# Cleaning parameters
CURRENCY_BASE = "USD"  # Base currency for normalization