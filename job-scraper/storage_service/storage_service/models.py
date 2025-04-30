# job-scraper/storage_service/storage_service/models.py
from sqlalchemy import Column, Float, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class JobPosting(Base):
    __tablename__ = 'job_postings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    description = Column(String, nullable=False)
    url = Column(String(255), unique=True, nullable=False)
    source = Column(String(50), nullable=False)
    date_posted = Column(DateTime, nullable=False)
    salary = Column(String(50), nullable=True)
    posting_age_days = Column(Integer, nullable=True)
    salary_midpoint_usd = Column(Float, nullable=True)  

    def __repr__(self):
        return f"<JobPosting(title={self.title}, company={self.company}, location={self.location})>"