# discovery_service/contact_scraper/contact_scraper/csv_handler.py
import csv
import os
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class CSVHandler:
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.urls = []
        self.results = {}
        self.social_media_platforms = set()
        self.headers = []
        self.initialize()

    def initialize(self):
        """Initialize the CSV handler by reading the input file or creating it if it doesn't exist."""
        if not os.path.exists(self.csv_path):
            logger.info(f"Creating new CSV file at {self.csv_path}")
            # Create a new CSV file with just the URL column
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["url", "emails"])
        else:
            logger.info(f"Reading existing CSV file from {self.csv_path}")
            self.read_csv()

    def read_csv(self):
        """Read URLs and existing data from the CSV file."""
        try:
            with open(self.csv_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.headers = next(reader)  # Get header row

                # Ensure we have at least the URL and emails columns
                if len(self.headers) < 2:
                    self.headers = ["url", "emails"]

                # Read each row
                for row in reader:
                    if not row or not row[0]:  # Skip empty rows
                        continue

                    url = row[0].strip()
                    self.urls.append(url)

                    # Store existing data for this URL
                    self.results[url] = {
                        "emails": row[1] if len(row) > 1 else "",
                        "social_links": {},
                    }

                    # Read existing social media links
                    for i in range(2, len(row)):
                        if i < len(self.headers) and row[i]:
                            platform = self.headers[i]
                            self.results[url]["social_links"][platform] = row[i]
                            self.social_media_platforms.add(platform)

            logger.info(f"Loaded {len(self.urls)} URLs from CSV")
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            # If there's an error, start with empty data
            self.urls = []
            self.results = {}

    def get_urls(self):
        """Return the list of URLs to process."""
        return self.urls

    def update_result(self, url, emails, social_links):
        """Update the results for a specific URL."""

        logger.info(f"Updating result for URL: {url}")
        logger.info(f"Emails to add: {emails}")
        logger.info(f"Social links to add: {social_links}")

        if url not in self.results:
            self.results[url] = {"emails": "", "social_links": {}}
            self.urls.append(url)
            logger.info(f"Added new URL to results: {url}")

        # Update emails (comma-separated)
        existing_emails = set(self.results[url]['emails'].split(',')) if self.results[url]['emails'] else set()
        all_emails = existing_emails.union(emails)
        all_emails = {email for email in all_emails if email}  # Remove empty strings
        
        if all_emails:
            self.results[url]['emails'] = ','.join(all_emails)
            logger.info(f"Updated emails for {url}: {self.results[url]['emails']}")

        # Update social media links and track platforms
        for link in social_links:
            platform = self.get_platform_from_url(link)
            if platform:
                self.results[url]["social_links"][platform] = link
                self.social_media_platforms.add(platform)
                logger.info(f"Added {platform} link for {url}: {link}")

        # Write updated results back to CSV
        self.write_csv()

    def get_platform_from_url(self, url):
        """Extract the social media platform name from a URL."""
        domain = urlparse(url).netloc.lower()

        # Map domains to platform names
        if "linkedin.com" in domain:
            return "linkedin"
        elif "twitter.com" in domain or "x.com" in domain:
            return "twitter"
        elif "facebook.com" in domain or "fb.com" in domain:
            return "facebook"
        elif "instagram.com" in domain:
            return "instagram"
        elif "youtube.com" in domain or "youtu.be" in domain:
            return "youtube"
        elif "pinterest.com" in domain:
            return "pinterest"
        elif "tiktok.com" in domain:
            return "tiktok"
        elif "reddit.com" in domain:
            return "reddit"
        else:
            # For unknown platforms, use the domain
            return domain.replace("www.", "").split(".")[0]

    def write_csv(self):
        """Write the current results back to the CSV file."""
        try:
            # Create headers: url, emails, followed by all social media platforms
            headers = ["url", "emails"] + sorted(list(self.social_media_platforms))

            # Create rows for each URL
            rows = []
            for url in self.urls:
                row = [url, self.results[url]["emails"]]

                # Add social media links in the correct order
                for platform in sorted(list(self.social_media_platforms)):
                    row.append(self.results[url]["social_links"].get(platform, ""))

                rows.append(row)

            # Write to CSV
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)

            logger.info(f"Updated CSV file with {len(rows)} URLs")
        except Exception as e:
            logger.error(f"Error writing to CSV file: {e}")
