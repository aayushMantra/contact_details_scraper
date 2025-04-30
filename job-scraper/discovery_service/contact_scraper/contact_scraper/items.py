# discovery_service/contact_scraper/contact_scraper/items.py
import scrapy

class ContactScraperItem(scrapy.Item):
    url = scrapy.Field()
    emails = scrapy.Field()
    social_media_links = scrapy.Field()