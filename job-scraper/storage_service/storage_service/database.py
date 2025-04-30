# from sqlalchemy import create_engine, Column, Integer, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.sql import func
# from elasticsearch import Elasticsearch
# from config import POSTGRES_URL, ELASTICSEARCH_HOST, ELASTICSEARCH_PORT, ELASTICSEARCH_INDEX
# import time

# # PostgreSQL setup
# Base = declarative_base()

# def create_engine_with_retry(url, max_retries=10, retry_delay=5):
#     for attempt in range(max_retries):
#         try:
#             engine = create_engine(url, echo=True)
#             with engine.connect() as conn:
#                 print("Connected to PostgreSQL")
#             return engine
#         except Exception as e:
#             print(f"Failed to connect to PostgreSQL (attempt {attempt + 1}/{max_retries}): {e}")
#             if attempt < max_retries - 1:
#                 time.sleep(retry_delay)
#             else:
#                 raise Exception("Failed to connect to PostgreSQL after maximum retries")

# engine = create_engine_with_retry(POSTGRES_URL)

# class JobPosting(Base):
#     __tablename__ = 'job_postings'
#     id = Column(Integer, primary_key=True)
#     job_title = Column(String)
#     company = Column(String)
#     location = Column(String)
#     description = Column(String)
#     salary = Column(String)
#     posting_date = Column(String)
#     application_url = Column(String)
#     source = Column(String)
#     scraped_at = Column(DateTime, server_default=func.now())

# # Create the table
# Base.metadata.create_all(engine)

# # Elasticsearch setup
# def connect_elasticsearch(max_retries=10, retry_delay=5):
#     for attempt in range(max_retries):
#         try:
#             es = Elasticsearch([{'host': ELASTICSEARCH_HOST, 'port': ELASTICSEARCH_PORT}])
#             if es.ping():
#                 print("Connected to Elasticsearch")
#                 return es
#             else:
#                 raise Exception("Elasticsearch ping failed")
#         except Exception as e:
#             print(f"Failed to connect to Elasticsearch (attempt {attempt + 1}/{max_retries}): {e}")
#             if attempt < max_retries - 1:
#                 time.sleep(retry_delay)
#             else:
#                 raise Exception("Failed to connect to Elasticsearch after maximum retries")

# es = connect_elasticsearch()

# def save_to_elasticsearch(job_data):
#     try:
#         es.index(index=ELASTICSEARCH_INDEX, body=job_data)
#         print(f"Indexed job posting in Elasticsearch: {job_data['job_title']}")
#     except Exception as e:
#         print(f"Failed to index in Elasticsearch: {e}")