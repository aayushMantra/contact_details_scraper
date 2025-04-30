import json
import os
from bs4 import BeautifulSoup
import re
import dateparser
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from config import logger, DEFAULT_VALUES, CURRENCY_BASE, POSTGRES_URL
from models import JobPosting, Base
from elasticsearch import Elasticsearch
from prometheus_client import Counter, Histogram

# Prometheus Metrics
CLEANING_SUCCESS = Counter('cleaning_success_total', 'Number of successful data cleaning operations', ['type'])
CLEANING_FAILURE = Counter('cleaning_failure_total', 'Number of failed data cleaning operations', ['type'])
CLEANING_TIME = Histogram('cleaning_time_seconds', 'Time spent cleaning data')
STORAGE_SUCCESS = Counter('storage_success_total', 'Number of successful storage operations')
STORAGE_FAILURE = Counter('storage_failure_total', 'Number of failed storage operations')
DUPLICATE_COUNT = Counter('duplicate_jobs_total', 'Number of duplicate jobs detected')
INDEXING_SUCCESS = Counter('indexing_success_total', 'Number of successful indexing operations')
INDEXING_FAILURE = Counter('indexing_failure_total', 'Number of failed indexing operations')
DERIVED_DATA_COMPUTED = Counter('derived_data_computed_total', 'Number of derived data computations')

class DataProcessor:
    def __init__(self):
        self.html_tags = re.compile(r'<[^>]+>')
        self.special_chars = re.compile(r'[^\w\s.,-]')
        self.currency_pattern = re.compile(
            r'\$?(\d{1,3}(?:[,\.]?\d{3})*(?:[.,]\d{2})?)\s*-\s*\$?(\d{1,3}(?:[,\.]?\d{3})*(?:[.,]\d{2})?)\s*(USD|EUR|GBP|CAD|AUD)?', re.IGNORECASE)
        # Database setup
        self.engine = create_engine(POSTGRES_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        # Elasticsearch setup
        self.es = Elasticsearch(
            hosts=[{'host': os.getenv('ELASTICSEARCH_HOST', 'localhost'), 'port': int(os.getenv('ELASTICSEARCH_PORT', '9200'))}],
            timeout=30
        )
        self.index_name = 'job_postings'
        self._setup_index()
        
    def _setup_index(self):
        if not self.es.indices.exists(index=self.index_name):
            index_settings = {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 1
                },
                "mappings": {
                    "properties": {
                        "title": {"type": "text", "analyzer": "standard"},
                        "company": {"type": "text", "analyzer": "standard"},
                        "location": {"type": "text", "analyzer": "standard"},
                        "description": {"type": "text", "analyzer": "standard"},
                        "url": {"type": "keyword"},
                        "source": {"type": "keyword"},
                        "date_posted": {"type": "date"},
                        "salary": {"type": "text"},
                        "posting_age_days": {"type": "integer"},
                        "salary_midpoint_usd": {"type": "float"}
                    }
                }
            }
            self.es.indices.create(index=self.index_name, body=index_settings)
            logger.info(f"Created Elasticsearch index: {self.index_name}")

    def clean_text(self, text):
        if not isinstance(text, str):
            return text
        try:
            text = self.html_tags.sub('', text)
            text = self.special_chars.sub('', text)
            text = ' '.join(text.split())
            CLEANING_SUCCESS.labels(type='text').inc()
            logger.info(f"Cleaned text: {text[:50]}...")
            return text
        except Exception as e:
            CLEANING_FAILURE.labels(type='text').inc()
            logger.error(f"Failed to clean text: {e}")
            return text

    def standardize_date(self, date_str):
        if not date_str or not isinstance(date_str, str):
            return DEFAULT_VALUES["date_posted"]
        try:
            parsed_date = dateparser.parse(date_str, settings={
                'RELATIVE_BASE': datetime.utcnow(),
                'PREFER_DATES_FROM': 'past',  # Changed to 'past' for "Posted 2 days ago"
                'RETURN_AS_TIMEZONE_AWARE': True
            })
            if parsed_date:
                iso_date = parsed_date.isoformat()
                CLEANING_SUCCESS.labels(type='date').inc()
                logger.info(f"Standardized date to ISO: {iso_date}")
                return iso_date
            return DEFAULT_VALUES["date_posted"]
        except Exception as e:
            CLEANING_FAILURE.labels(type='date').inc()
            logger.error(f"Failed to standardize date {date_str}: {e}")
            return DEFAULT_VALUES["date_posted"]

    def normalize_salary(self, salary_str):
        if not salary_str or not isinstance(salary_str, str):
            return DEFAULT_VALUES["salary"]
        try:
            match = self.currency_pattern.search(salary_str)
            if not match:
                return DEFAULT_VALUES["salary"]
            min_amount = float(match.group(1).replace(',', ''))
            max_amount = float(match.group(2).replace(',', ''))
            currency = match.group(3).upper() if match.group(3) else "USD"

            conversion_rates = {"EUR": 1.1, "GBP": 1.3, "CAD": 0.75, "AUD": 0.65, "USD": 1.0}
            min_amount *= conversion_rates.get(currency, 1.0)
            max_amount *= conversion_rates.get(currency, 1.0)

            normalized = f"{min_amount:.2f} - {max_amount:.2f} {CURRENCY_BASE}"
            CLEANING_SUCCESS.labels(type='salary').inc()
            logger.info(f"Normalized salary to: {normalized}")
            return normalized
        except Exception as e:
            CLEANING_FAILURE.labels(type='salary').inc()
            logger.error(f"Failed to normalize salary {salary_str}: {e}")
            return DEFAULT_VALUES["salary"]

    def compute_derived_data(self, job_data):
        """Compute derived fields: posting age and salary midpoint."""
        try:
            # Compute posting age in days
            date_str = job_data.get("date_posted", DEFAULT_VALUES["date_posted"])

            # Handle ISO format dates (which your data now has)
            try:
                if 'T' in date_str:
                    date_posted = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    date_posted = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S%z")
            except (ValueError, TypeError):
                # Fall back to dateparser for other formats
                date_posted = dateparser.parse(date_str)
            
            current_date = datetime.utcnow()
             # Calculate days difference - ensure both dates are naive or both are aware
            if date_posted and date_posted.tzinfo:
                current_date = current_date.replace(tzinfo=date_posted.tzinfo)
            
            posting_age_days = (current_date - date_posted).days if date_posted else None

            # Compute salary midpoint
            salary_midpoint_usd = None
            salary = job_data.get("salary", DEFAULT_VALUES["salary"])
            if salary != DEFAULT_VALUES["salary"]:
                # Extract numbers from the normalized salary string
                parts = re.findall(r'\d+\.\d+', salary)  # Match only decimal numbers
                if len(parts) == 2:
                    min_salary = float(parts[0])
                    max_salary = float(parts[1])
                    salary_midpoint_usd = (min_salary + max_salary) / 2
                elif len(parts) == 1:
                    salary_midpoint_usd = float(parts[0])

            DERIVED_DATA_COMPUTED.inc()
            logger.info(f"Computed derived data: posting_age_days={posting_age_days}, salary_midpoint_usd={salary_midpoint_usd}")
            return {"posting_age_days": posting_age_days, "salary_midpoint_usd": salary_midpoint_usd}
        except Exception as e:
            logger.error(f"Failed to compute derived data: {e}")
            return {"posting_age_days": None, "salary_midpoint_usd": None}

    def store_job_posting(self, job_data):
        session = self.Session()
        try:
            existing = session.query(JobPosting).filter_by(
                title=job_data["title"],
                company=job_data["company"],
                location=job_data["location"]
            ).first()
            # Compute derived data even for duplicates for debugging
            derived_data = self.compute_derived_data(job_data)
            logger.info(f"Derived data for {job_data['title']}: {derived_data}")

            if existing:
                DUPLICATE_COUNT.inc()
                logger.warning(f"Duplicate job detected: {job_data['title']} at {job_data['url']}")
                # Update existing record if duplicate
                existing.date_posted = job_data.get("date_posted", DEFAULT_VALUES["date_posted"])
                existing.salary = job_data.get("salary", DEFAULT_VALUES["salary"])
                existing.posting_age_days = derived_data["posting_age_days"]
                existing.salary_midpoint_usd = derived_data["salary_midpoint_usd"]
                session.commit()
                STORAGE_SUCCESS.inc()
                logger.info(f"Updated duplicate job posting: {job_data['title']} at {job_data['url']}")
                session.close()
                return True
            else:
                new_job = JobPosting(
                    title=job_data["title"],
                    company=job_data["company"],
                    location=job_data["location"],
                    description=job_data["description"],
                    url=job_data["url"],
                    source=job_data["source"],
                    date_posted=job_data.get("date_posted", DEFAULT_VALUES["date_posted"]),
                    salary=job_data.get("salary", DEFAULT_VALUES["salary"]),
                    posting_age_days=derived_data["posting_age_days"],
                    salary_midpoint_usd=derived_data["salary_midpoint_usd"]
                )
                session.add(new_job)
                session.commit()
                STORAGE_SUCCESS.inc()
                logger.info(f"Stored job posting: {job_data['title']} at {job_data['url']} with derived data")
                session.close()
                return True
        except IntegrityError as e:
            session.rollback()
            STORAGE_FAILURE.inc()
            logger.error(f"Integrity error storing job posting: {e}")
            session.close()
            return False
        except Exception as e:
            session.rollback()
            STORAGE_FAILURE.inc()
            logger.error(f"Error storing job posting: {e}")
            session.close()
            return False
        
    def index_job_posting(self, job_posting):
        
        # Recompute derived data to ensure it's up to date
        derived_data = self.compute_derived_data({
            "date_posted": job_posting.date_posted,
            "salary": job_posting.salary
        })
    
        doc = {
            "title": job_posting.title,
            "company": job_posting.company,
            "location": job_posting.location,
            "description": job_posting.description,
            "url": job_posting.url,
            "source": job_posting.source,
            "date_posted": job_posting.date_posted,
            "salary": job_posting.salary,
            "posting_age_days": derived_data["posting_age_days"],
            "salary_midpoint_usd": derived_data["salary_midpoint_usd"]
        }
        try:
            self.es.index(index=self.index_name, document=doc)  # Updated to use 'document'
            INDEXING_SUCCESS.inc()
            logger.info(f"Indexed job posting: {job_posting.title} at {job_posting.url}")
        except Exception as e:
            INDEXING_FAILURE.inc()
            logger.error(f"Failed to index job posting {job_posting.url}: {e}")

    def process_data(self, job_data):
        with CLEANING_TIME.time():
            logger.info(f"Processing raw job data: {json.dumps(job_data, indent=2)}")
            cleaned_data = {}
            for key, value in job_data.items():
                if key == "description" or key == "title":
                    cleaned_value = self.clean_text(value)
                    cleaned_data[key] = cleaned_value if cleaned_value else DEFAULT_VALUES.get(key, "Not specified")
                elif key == "date_posted":
                    cleaned_data[key] = self.standardize_date(value)
                elif key == "salary":
                    cleaned_data[key] = self.normalize_salary(value)
                else:
                    cleaned_data[key] = value if value else DEFAULT_VALUES.get(key)
            logger.info(f"Processed job data: {json.dumps(cleaned_data, indent=2)}")
            # Store in PostgreSQL
            stored = self.store_job_posting(cleaned_data)
            if stored:
                # Index in Elasticsearch only if storage succeeds
                self.index_job_posting(JobPosting(**cleaned_data))
            return cleaned_data

if __name__ == "__main__":
    processor = DataProcessor()
    test_data = {
        "title": "<h1>Software Engineer</h1>",
        "company": "Tech Corp",
        "location": "San Francisco, CA",
        "description": "<p>Develop software solutions.</p>",
        "url": "http://host.docker.internal:8000/test_linkedin.html",
        "source": "linkedin",
        "date_posted": "Posted 2 days ago",
        "salary": "$50,000 - $60,000"
    }
    cleaned = processor.process_data(test_data)
    print(json.dumps(cleaned, indent=2))