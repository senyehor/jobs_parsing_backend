from typing import Annotated, Iterable

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.jobs.router import router as jobs_router
from src.scraping_and_parsing.models import JobPosting
from src.scraping_and_parsing.sites import HTTPX_SITES, SELENIUM_SITES

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(jobs_router, prefix='api/')


@app.get('/api/all-sites/')
async def all_sites(keywords: Annotated[list[str], Query()]) -> Iterable[JobPosting]:
    jobs = []
    for site in SELENIUM_SITES:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        scraper = site.scraper_class(driver=driver)
        try:
            htmls = await scraper.scrape(site.base_url, keywords)
            if isinstance(htmls, str):
                htmls = (htmls,)
            for html in htmls:
                parser = site.parser_class(html)
                jobs.extend(parser.parse_jobs(keywords))
        finally:
            driver.quit()
    async with AsyncClient() as client:
        for site in HTTPX_SITES:
            scraper = site.scraper_class(client)
            htmls = await scraper.scrape(site.base_url, keywords)
            if isinstance(htmls, str):
                htmls = (htmls,)
            for html in htmls:
                parser = site.parser_class(html)
                jobs.extend(parser.parse_jobs(keywords))
    return jobs
