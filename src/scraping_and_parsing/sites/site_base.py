from abc import ABC

from src.scraping_and_parsing.parsing_bases import JobParser
from src.scraping_and_parsing.scraping_bases import (
    HtmlScraperBase,
)


class SiteBase(ABC):
    slug: str
    base_url: str
    parser_class: type[JobParser]
    scraper_class: type[HtmlScraperBase]
