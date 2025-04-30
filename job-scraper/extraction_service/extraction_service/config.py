# extraction_service/extraction_service/config.py
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

RABBITMQ_HOST = "rabbitmq"
RABBITMQ_PORT = 5672
RABBITMQ_CLASSIFY_QUEUE = "urls_to_classify"  # Classification Service
RABBITMQ_EXTRACT_QUEUE = "urls_to_extract"    # Extraction Service
RABBITMQ_STORE_QUEUE = "data_to_store"        # Extraction Service
RABBITMQ_EXCHANGE = ""  # Default exchange
USER_AGENT = "JobScraperExtractor/1.0 (+https://myjobscraper.com)"