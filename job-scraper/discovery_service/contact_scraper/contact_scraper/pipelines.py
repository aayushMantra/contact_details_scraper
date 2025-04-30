# discovery_service/contact_scraper/contact_scraper/pipelines.py
class ContactScraperPipeline:
    def process_item(self, item, spider):
        return item