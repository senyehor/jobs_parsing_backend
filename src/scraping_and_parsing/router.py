import asyncio
from asyncio import gather
from concurrent.futures import ThreadPoolExecutor
from contextlib import AsyncExitStack
from typing import Iterable

from fastapi import APIRouter
from httpx import AsyncClient
from playwright.async_api import async_playwright
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.scraping_and_parsing.logic.slug_filtering import (
    get_httpx_sites,
    get_playwright_sites, get_selenium_sites,
)
from src.scraping_and_parsing.models import JobPosting
from src.scraping_and_parsing.scraping_bases import HtmlScraperBaseAsync, HtmlScraperBaseSync
from src.scraping_and_parsing.sites import SiteBase

router = APIRouter()


@router.post('/job-postings')
async def scrape_job_postings(
        keywords: list[str],
        site_slugs: list[str] | None = None
) -> Iterable[JobPosting]:
    selenium_sites = get_selenium_sites(site_slugs)
    playwright_sites = get_playwright_sites(site_slugs)
    httpx_sites = get_httpx_sites(site_slugs)

    async with AsyncExitStack() as stack:
        results = await gather(
            *(handle_httpx(site, keywords, stack) for site in httpx_sites),
            *(handle_playwright(site, keywords, stack) for site in playwright_sites),
            *(handle_selenium(site, keywords) for site in selenium_sites),
        )

    return [job for sublist in results for job in sublist]


async def handle_httpx(
        site: SiteBase,
        keywords: list[str],
        stack: AsyncExitStack
) -> list[JobPosting]:
    client = await stack.enter_async_context(AsyncClient())
    scraper = site.scraper_class(client)
    return await scrape_and_parse_async(site, scraper, keywords)


async def handle_playwright(
        site: SiteBase,
        keywords: list[str],
        stack: AsyncExitStack
) -> list[JobPosting]:
    """Process Playwright-based sites"""
    playwright = await stack.enter_async_context(async_playwright())
    browser = await playwright.chromium.launch(headless=False)
    scraper = site.scraper_class(browser)
    return await scrape_and_parse_async(site, scraper, keywords)


async def handle_selenium(site: SiteBase, keywords: list[str]) -> list[JobPosting]:
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(
            pool,
            sync_selenium_scrape,
            site,
            keywords
        )


def sync_selenium_scrape(site: SiteBase, keywords: list[str]) -> list[JobPosting]:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        scraper = site.scraper_class(driver)
        return scrape_and_parse_sync(site, scraper, keywords)
    finally:
        driver.quit()


async def scrape_and_parse_async(
        site: SiteBase,
        scraper: HtmlScraperBaseAsync,
        keywords: list[str]
) -> list[JobPosting]:
    htmls = await scraper.scrape(site.base_url, keywords)
    return parse_htmls(site, htmls, keywords)


def scrape_and_parse_sync(
        site: SiteBase,
        scraper: HtmlScraperBaseSync,
        keywords: list[str]
) -> list[JobPosting]:
    htmls = scraper.scrape(site.base_url, keywords)
    return parse_htmls(site, htmls, keywords)


def parse_htmls(
        site: SiteBase,
        htmls: str | Iterable[str],
        keywords: list[str]
) -> list[JobPosting]:
    if isinstance(htmls, str):
        htmls = [htmls]
    return [
        job
        for html in htmls
        for job in site.parser_class(html).parse_jobs(keywords)
    ]
