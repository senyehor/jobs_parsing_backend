from src.scraping_and_parsing.sites.dou import Dou
from src.scraping_and_parsing.sites.genesis import Genesis
from src.scraping_and_parsing.sites.robotaua import RobotaUA
from src.scraping_and_parsing.sites.site_base import SiteBase

SELENIUM_SITES = {
    Dou.slug: Dou,
}

HTTPX_SITES = {
    Genesis.slug: Genesis,
}

Playwright_SITES = {
    RobotaUA.slug: RobotaUA
}
