from src.scraping_and_parsing.sites.dou import Dou
from src.scraping_and_parsing.sites.genesis import Genesis
from src.scraping_and_parsing.sites.site_base import SiteBase

SITES_LIST: list[type[SiteBase]] = [
    Dou,
    Genesis
]

SITES_MAP_BY_NAME = {
    site.site_name: site for site in SITES_LIST
}
