from abc import ABC

from src.scraping_and_parsing.parsing_bases import JobParser
from src.scraping_and_parsing.scraping_bases import HtmlScraperBase


class SiteBase(ABC):
    site_name: str
    base_url: str
    parser: type[JobParser]
    scraper: type[HtmlScraperBase]
