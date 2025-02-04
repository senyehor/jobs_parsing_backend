from functools import partial
from typing import Iterable

from src.scraping_and_parsing.sites import Playwright_SITES, SELENIUM_BASED_SITES, SiteBase


def _filter_sites_dict_by_slug(
        site_slugs: Iterable[str], sites: dict[str, type[SiteBase]]
) -> Iterable[type[SiteBase]]:
    return [sites[slug] for slug in site_slugs if slug in sites]


filter_selenium_sites = partial(_filter_sites_dict_by_slug, sites=SELENIUM_BASED_SITES)
filter_httpx_sites = partial(_filter_sites_dict_by_slug, sites=SELENIUM_BASED_SITES)
filter_playwright_sites = partial(_filter_sites_dict_by_slug, sites=Playwright_SITES)
