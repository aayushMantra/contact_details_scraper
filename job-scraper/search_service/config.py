# job-scraper/search_service/config.py
import logging
from elasticsearch import Elasticsearch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcoded Elasticsearch configuration
ELASTICSEARCH_HOST = "http://elasticsearch:9200"
logger.info(f"Initializing Elasticsearch with host: {ELASTICSEARCH_HOST}")

try:
    es = Elasticsearch([ELASTICSEARCH_HOST])
    if not es.ping():
        logger.error("Elasticsearch ping failed")
        raise ConnectionError("Cannot connect to Elasticsearch")
    logger.info("Elasticsearch connection established")
except Exception as e:
    logger.error(f"Failed to initialize Elasticsearch: {e}")
    raise
