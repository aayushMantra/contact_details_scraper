import os
from elasticsearch import Elasticsearch
import random
import datetime

# Connect to Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# Connect to Elasticsearch using the service name from docker-compose
es_host = os.getenv('ELASTICSEARCH_HOST', 'http://elasticsearch:9200')
print(f"Connecting to Elasticsearch at {es_host}")
es = Elasticsearch([es_host])

# Check if Elasticsearch is available
if not es.ping():
    raise ConnectionError(f"Cannot connect to Elasticsearch at {es_host}")
print("Successfully connected to Elasticsearch")


# Sample data
job_titles = [
    "Software Engineer", "Data Scientist", "Product Manager", 
    "DevOps Engineer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "Machine Learning Engineer", "UX Designer",
    "QA Engineer", "Systems Architect", "Database Administrator"
]

companies = [
    "Google", "Amazon", "Microsoft", "Apple", "Meta", 
    "Netflix", "Spotify", "Airbnb", "Uber", "Twitter",
    "LinkedIn", "Salesforce", "Adobe", "IBM", "Oracle"
]

locations = [
    "San Francisco, CA", "Seattle, WA", "New York, NY", 
    "Austin, TX", "Boston, MA", "Chicago, IL", "Los Angeles, CA",
    "Denver, CO", "Atlanta, GA", "Portland, OR", "San Diego, CA"
]

# Generate and index 20 job postings
for i in range(1, 21):
    job_title = random.choice(job_titles)
    company = random.choice(companies)
    location = random.choice(locations)
    
    # Generate random date within last 30 days
    days_ago = random.randint(0, 30)
    date_posted = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Generate random salary range
    base_salary = random.randint(50000, 150000)
    salary_max = base_salary + random.randint(10000, 50000)
    salary_midpoint = (base_salary + salary_max) / 2
    
    # Create document
    doc = {
        "title": job_title,
        "company": company,
        "location": location,
        "description": f"We are looking for a talented {job_title} to join our team at {company}. This is an exciting opportunity to work on cutting-edge technology.",
        "url": f"http://example.com/jobs/{i}",
        "source": random.choice(["linkedin", "indeed", "glassdoor", "monster"]),
        "date_posted": date_posted,
        "salary": f"{base_salary} - {salary_max} USD",
        "posting_age_days": days_ago,
        "salary_midpoint_usd": salary_midpoint
    }
    
    # Index the document
    es.index(index="job_postings", body=doc)
    print(f"Indexed job {i}: {job_title} at {company}")

print("Indexing complete. Added 20 sample job postings.")
