from typing import Iterable

from src.scraping_and_parsing.sites import HTTPX_SITES, Playwright_SITES, SELENIUM_SITES, SiteBase


def _filter_sites_dict_by_slug(
        site_slugs: Iterable[str], sites: dict[str, type[SiteBase]]
) -> Iterable[type[SiteBase]]:
    return [sites[slug] for slug in site_slugs if slug in sites]


def get_selenium_sites(
        site_slugs: Iterable[str],
        selenium_sites_dict: dict[str, type[SiteBase]] = SELENIUM_SITES
) -> Iterable[type[SiteBase]]:
    return _filter_sites_dict_by_slug(site_slugs, selenium_sites_dict)


def get_httpx_sites(
        site_slugs: Iterable[str],
        httpx_sites_dict: dict[str, type[SiteBase]] = HTTPX_SITES
) -> Iterable[type[SiteBase]]:
    return _filter_sites_dict_by_slug(site_slugs, httpx_sites_dict)


def get_playwright_sites(
        site_slugs: Iterable[str],
        playwright_sites_dict: dict[str, type[SiteBase]] = Playwright_SITES
) -> Iterable[type[SiteBase]]:
    return _filter_sites_dict_by_slug(site_slugs, playwright_sites_dict)
