# Job Scraper
A distributed web scraper to crawl the entire internet for job postings.

## Goals
- Scrape all job postings online.
- Provide searchable results with filters.

## Architecture
- Discovery Service: Crawls the web.
- Classification Service: Identifies job postings.
- Extraction Service: Extracts job data.
- Storage Service: Saves data.
- Search Service: Handles queries.

## Internshala Scraping Approach
- **Objective**: Scrape all internship data from Internshala (e.g., titles, companies, stipends) including prohibited URLs (e.g., `/internship/detail/*`).
- **Strategy**: Bypass `robots.txt` and Terms of Service restrictions using stealth techniques (e.g., rotating proxies, headless browsers, random delays) to remain undetected.
- **Ethical Boundaries**: Avoid sensitive personal data (e.g., applicant details, login pages `/login`, `/register`, `/internships/apply/`) to minimize legal exposure.
- **Note**: This is a private strategy for development purposes only. See `scraping_strategy_internshala.md` and `compliance_notes.md` for details.
- We’ll bypass robots.txt for prohibited URLs using rotating proxies, headless browsers, and human-like behavior. See scraping_strategy_intershala.md for details.