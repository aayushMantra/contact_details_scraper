#!/usr/bin/env python3
"""
Script to run the contact scraper from the command line with input/output files.
This is used by the API service to process CSV files.
"""

import argparse
import os
import sys
import logging
import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from contact_scraper.spiders.contact_spider import ContactSpider
from contact_scraper.csv_handler import CSVHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the contact scraper on a CSV file')
    parser.add_argument('--input', required=True, help='Input CSV file with URLs')
    parser.add_argument('--output', required=True, help='Output CSV file for results')
    args = parser.parse_args()
    
    input_file = args.input
    output_file = args.output
    
    # Ensure the input file exists
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        sys.exit(1)
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Read URLs from the input file
    try:
        df = pd.read_csv(input_file)
        if len(df.columns) == 0:
            logger.error("Input file is empty")
            sys.exit(1)
        
        # Get URLs from the first column
        url_column = df.iloc[:, 0]
        urls = url_column.tolist()
        
        logger.info(f"Found {len(urls)} URLs in the input file")
        
        # Initialize the CSV handler with the output file
        csv_handler = CSVHandler(output_file)
        
        # Add URLs to the CSV handler
        for url in urls:
            if url and isinstance(url, str):
                csv_handler.update_result(url, [], [])
        
        # Run the spider
        settings = get_project_settings()
        process = CrawlerProcess(settings)
        process.crawl(ContactSpider, csv_file=output_file)
        process.start()
        
        logger.info(f"Scraping completed. Results saved to {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()