# job-scraper/search_service/main.py
from fastapi import FastAPI, Query, HTTPException
from elasticsearch import Elasticsearch
from config import es, logger
from typing import List, Optional
from pydantic import BaseModel
import pandas as pd
from io import StringIO
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Job Search API",
    description="API to search and filter job postings",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Define response model
class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    date_posted: Optional[str] = None
    salary: str
    posting_age_days: Optional[int] = None
    salary_midpoint_usd: Optional[float] = None
    
class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    data: List[JobPosting]

# Health check endpoint
@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    if es.ping():
        return {"status": "healthy"}
    return {"status": "unhealthy"}

# Search endpoint
@app.get("/search", response_model=PaginatedResponse)
async def search_jobs(
    query: str = Query(None, description="Search term for job title or description"),
    location: str = Query(None, description="Filter by location"),
    salary_min: float = Query(None, description="Minimum salary in USD"),
    salary_max: float = Query(None, description="Maximum salary in USD"),
    company: str = Query(None, description="Filter by company"),
    max_age_days: int = Query(None, description="Maximum posting age in days"),
    sort_by: str = Query("date_posted", description="Sort by (date_posted or salary_midpoint_usd)", regex="^(date_posted|salary_midpoint_usd)$"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)", regex="^(asc|desc)$"),
    page: int = Query(1, description="Page number", ge=1),
    size: int = Query(10, description="Number of results per page", ge=1, le=100)
):
    logger.info(f"Search requested with query={query}, location={location}, salary_min={salary_min}, salary_max={salary_max}, "
                f"company={company}, max_age_days={max_age_days}, sort_by={sort_by}, sort_order={sort_order}, page={page}, size={size}")
    
    # Calculate from value for Elasticsearch pagination
    from_value = (page - 1) * size
    
    # Build Elasticsearch query
    search_query = {
        "query": {
            "bool": {
                "must": [],
                "filter": []
            }
        },
        "sort": [{sort_by: {"order": sort_order}}]
    }

    # Full-text search on title and description
    if query:
        search_query["query"]["bool"]["must"].append({
            "multi_match": {
                "query": query,
                "fields": ["title", "description"],
                "fuzziness": "AUTO"
            }
        })

    # Filters
    if location:
        # Use match query instead of term for partial matching on location
        search_query["query"]["bool"]["filter"].append({
            "match": {
                "location": {
                    "query": location,
                    "fuzziness": "AUTO"
                }
            }
        })
    if company:
        # Use match query for company as well for better results
        search_query["query"]["bool"]["filter"].append({
            "match": {
                "company": {
                    "query": company,
                    "fuzziness": "AUTO"
                }
            }
        })
    if salary_min is not None:
        search_query["query"]["bool"]["filter"].append({"range": {"salary_midpoint_usd": {"gte": salary_min}}})
    if salary_max is not None:
        search_query["query"]["bool"]["filter"].append({"range": {"salary_midpoint_usd": {"lte": salary_max}}})
    if max_age_days is not None:
        search_query["query"]["bool"]["filter"].append({"range": {"posting_age_days": {"lte": max_age_days}}})

    # Execute search
    try:
        logger.info(f"Executing Elasticsearch query: {search_query}")
        # Pass from and size as separate parameters, not in the body
        response = es.search(
            index="job_postings", 
            body=search_query,
            from_=from_value,  # Use from_ parameter instead of in body
            size=size          # Use size parameter instead of in body
        )
        
        hits = response["hits"]["hits"]
        total = response["hits"]["total"]["value"]
        jobs = [hit["_source"] for hit in hits]
        logger.info(f"Found {len(jobs)} job postings on page {page} of {total} total")
        
        return PaginatedResponse(
            total=total,
            page=page,
            size=size,
            data=jobs
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
# Export endpoint
@app.get("/export")
async def export_jobs(
    query: str = Query(None, description="Search term for job title or description"),
    location: str = Query(None, description="Filter by location"),
    salary_min: float = Query(None, description="Minimum salary in USD"),
    salary_max: float = Query(None, description="Maximum salary in USD"),
    company: str = Query(None, description="Filter by company"),
    max_age_days: int = Query(None, description="Maximum posting age in days"),
    sort_by: str = Query("date_posted", description="Sort by (date_posted or salary_midpoint_usd)", regex="^(date_posted|salary_midpoint_usd)$"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)", regex="^(asc|desc)$")
):
    logger.info(f"Export requested with query={query}, location={location}, salary_min={salary_min}, salary_max={salary_max}, "
                f"company={company}, max_age_days={max_age_days}, sort_by={sort_by}, sort_order={sort_order}")
    
    # Build Elasticsearch query without pagination for full export
    search_query = {
        "query": {
            "bool": {
                "must": [],
                "filter": []
            }
        },
        "sort": [{sort_by: {"order": sort_order}}]
    }

    if query:
        search_query["query"]["bool"]["must"].append({
            "multi_match": {
                "query": query,
                "fields": ["title", "description"],
                "fuzziness": "AUTO"
            }
        })

    if location:
        search_query["query"]["bool"]["filter"].append({
            "match": {
                "location": {
                    "query": location,
                    "fuzziness": "AUTO"
                }
            }
        })
    if company:
        search_query["query"]["bool"]["filter"].append({
            "match": {
                "company": {
                    "query": company,
                    "fuzziness": "AUTO"
                }
            }
        })
    if salary_min is not None:
        search_query["query"]["bool"]["filter"].append({"range": {"salary_midpoint_usd": {"gte": salary_min}}})
    if salary_max is not None:
        search_query["query"]["bool"]["filter"].append({"range": {"salary_midpoint_usd": {"lte": salary_max}}})
    if max_age_days is not None:
        search_query["query"]["bool"]["filter"].append({"range": {"posting_age_days": {"lte": max_age_days}}})

    try:
        # Fetch all matching records (use scroll or multiple requests if dataset is very large)
        response = es.search(index="job_postings", body=search_query, size=1000)
        hits = response["hits"]["hits"]
        jobs = [hit["_source"] for hit in hits]

        # Convert to DataFrame
        df = pd.DataFrame(jobs)
        logger.info(f"Exported {len(jobs)} job postings to CSV")

        # Convert to CSV and stream as response
        output = StringIO()
        df.to_csv(output, index=False)
        headers = {'Content-Disposition': 'attachment; filename="job_postings.csv"'}
        return StreamingResponse(
            iter([output.getvalue()]),
            headers=headers,
            media_type="text/csv"
        )
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
