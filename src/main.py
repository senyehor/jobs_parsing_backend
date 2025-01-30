from typing import Annotated, Iterable

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.scraping_and_parsing.models import JobPosting
from src.scraping_and_parsing.sites import HTTPX_BASED_SITES, SELENIUM_BASED_SITES
from src.scraping_and_parsing.sites.dou import DouParser, DouSeleniumScraper
from src.scraping_and_parsing.sites.genesis import GenesisParser, GenesisScraper

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


@app.get('/api/all-sites/')
async def all_sites(keywords: Annotated[list[str], Query()]) -> Iterable[JobPosting]:
    jobs = []
    for site in SELENIUM_BASED_SITES:
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
        for site in HTTPX_BASED_SITES:
            scraper = site.scraper_class(client)
            htmls = await scraper.scrape(site.base_url, keywords)
            if isinstance(htmls, str):
                htmls = (htmls,)
            for html in htmls:
                parser = site.parser_class(html)
                jobs.extend(parser.parse_jobs(keywords))
    return jobs


@app.get("/api/get-jobs")
async def root(keywords: Annotated[list[str], Query()]) -> Iterable[JobPosting]:
    async with AsyncClient() as client:
        url = 'https://gen-tech.breezy.hr/'
        scraper = GenesisScraper(client)
        html = await scraper.scrape(url, keywords)
        parser = GenesisParser(html)
        return parser.parse_jobs(keywords)


@app.get('/api/dou-by-category')
async def dou(keywords: Annotated[list[str], Query()]) -> Iterable[JobPosting]:
    url = f'https://jobs.dou.ua/vacancies/'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    scraper = DouSeleniumScraper(driver=driver)
    try:
        htmls = await scraper.scrape(url, keywords)
        if isinstance(htmls, str):
            htmls = (htmls,)
        jobs = []
        for html in htmls:
            parser = DouParser(html)
            jobs.extend(parser.parse_jobs(keywords))
        return jobs
    finally:
        driver.quit()
