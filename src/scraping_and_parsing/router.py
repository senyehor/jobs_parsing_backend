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

router = APIRouter()


@router.post('/job-postings')
async def scrape_job_postings(
        keywords: list[str], site_slugs: list[str] | None = None
) -> Iterable[JobPosting]:
    selenium_sites = get_selenium_sites(site_slugs)
    httpx_sites = get_httpx_sites(site_slugs)
    playwright_sites = get_playwright_sites(site_slugs)
    job_postings = []
    for site in httpx_sites:
        async with AsyncClient() as client:
            scraper = site.scraper_class(client)
            htmls = await scraper.scrape(site.base_url, keywords)
            if isinstance(htmls, str):
                htmls = (htmls,)
            for html in htmls:
                parser = site.parser_class(html)
                job_postings.extend(parser.parse_jobs(keywords))
    for site in playwright_sites:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            try:
                scraper = site.scraper_class(browser)
                htmls = await scraper.scrape(site.base_url, keywords)
            finally:
                await browser.close()
            if isinstance(htmls, str):
                htmls = (htmls,)
            for html in htmls:
                parser = site.parser_class(html)
                job_postings.extend(parser.parse_jobs(keywords))
    for site in selenium_sites:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        scraper = site.scraper_class(driver)
        try:
            htmls = await scraper.scrape(site.base_url, keywords)
            if isinstance(htmls, str):
                htmls = (htmls,)
        finally:
            driver.quit()
        for html in htmls:
            parser = site.parser_class(html)
            job_postings.extend(parser.parse_jobs(keywords))

    return job_postings
