# classification_service/classifier.py
import time
from bs4 import BeautifulSoup
import requests
from config import USER_AGENT, logger
from prometheus_client import Counter
import extruct
import re

class JobPostingClassifier:
    def __init__(self):
        self.headers= {"User-Agent": USER_AGENT}
        # Keywords to look for in the page content (case-insensitive)
        self.job_keywords = [
            "careers", "jobs", "apply now", "hiring", "vacancy", "position available",
            "job description", "employment", "recruitment", "we're hiring", "join our team"
        ]
        # Keywords to look for in the URL
        self.url_keywords = ["job", "career", "vacancy", "hiring", "recruitment"]
        # Minimum number of keyword matches to consider it a job posting
        self.keyword_threshold = 2
        
        # Prometheus Metrics
        self.URLS_CLASSIFIED = Counter('urls_classified_total', 'Total number of URLs classified')
        self.CLASSIFICATION_TIME = Counter('classification_time_total', 'Total time spent classifying URLs')
        self.CLASSIFICATION_ACCURACY = Counter('classification_accuracy_total', 'Number of correct classifications', ['result'])
        
    def download_page(self, url):
        """
        Download the HTML content of a page with retry logic.
        Args:
            url (str): The URL to download.
        Returns:
            str or None: The HTML content or None if download fails.
        """
        max_retries = 3
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                logger.info(f"Successfully downloaded content for {url}")
                return response.text
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed to download {url} after {max_retries} attempts")
                    return None

    def extract_structured_data(self, html_content):
        """
        Extract structured data (e.g., schema.org/JobPosting) from the HTML content.
        Args:
            html_content (str): The HTML content of the page.
        Returns:
            list: List of schema.org/JobPosting objects, if found.
        """
        try:
            data = extruct.extract(html_content, syntaxes=['microdata', 'json-ld'])
            job_postings = []
            # Check microdata
            for item in data.get('microdata', []):
                if item.get('type') == 'http://schema.org/JobPosting':
                    job_postings.append(item)
            # Check JSON-LD
            for item in data.get('json-ld', []):
                if item.get('@type') == 'JobPosting':
                    job_postings.append(item)
            return job_postings
        except Exception as e:
            print(f"Error extracting structured data: {e}")
            return []

    def count_keyword_matches(self, text, keywords):
        """
        Count the number of keyword matches in the text.
        Args:
            text (str): The text to search in.
            keywords (list): List of keywords to search for.
        Returns:
            int: Number of unique keyword matches.
        """
        text = text.lower()
        matches = set()
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                matches.add(keyword)
        return len(matches)

    def classify_page(self, url, html_content):
        """
        Classify a page as a job posting or not.
        Args:
            url (str): The URL of the page.
            html_content (str): The HTML content of the page.
        Returns:
            tuple: (bool, str) - (is_job_posting, reason)
        """
        if not html_content:
            return False, "No HTML content available"

        # Check for structured data (schema.org/JobPosting)
        structured_data = self.extract_structured_data(html_content)
        if structured_data:
            return True, "Found schema.org/JobPosting structured data"

        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True).lower()

        # Check for keywords in the URL
        url_matches = self.count_keyword_matches(url.lower(), self.url_keywords)
        if url_matches >= 1:
            return True, f"URL contains job-related keywords: {url_matches} matches"

        # Check for keywords in the page content
        content_matches = self.count_keyword_matches(text_content, self.job_keywords)
        if content_matches >= self.keyword_threshold:
            return True, f"Page content contains job-related keywords: {content_matches} matches"

        # If none of the above, it's not a job posting
        return False, "No job posting indicators found"
    
    def set_ground_truth(self, url, is_true_job):
        """
        Set ground truth for a URL to track classification accuracy manually.
        Args:
            url (str): The URL to set ground truth for.
            is_true_job (bool): True if the URL is a job posting, False otherwise.
        """
        ground_truth_result = "correct" if self.classify_page(url)[0] == is_true_job else "incorrect"
        self.CLASSIFICATION_ACCURACY.labels(result=ground_truth_result).inc()
        logger.info(f"Ground truth set for {url}: {'True (job posting)' if is_true_job else 'False (not a job posting)'} - Classification {ground_truth_result}")