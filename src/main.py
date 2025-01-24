from typing import Annotated, Iterable

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.parsing.logic.querying import DouSeleniumScraper, fetch_html
from src.parsing.models import JobPosting
from src.parsing.parsing import DouParser, GenTechJobParser

origins = [
    "http://localhost:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/get-jobs")
async def root(keywords: Annotated[list[str] | str, Query()]) -> Iterable[JobPosting]:
    async with AsyncClient() as client:
        url = 'https://gen-tech.breezy.hr/'
        html = await fetch_html(url, client)
        if isinstance(keywords, str):
            keywords = (keywords,)
        parser = GenTechJobParser(html, keywords)
        return parser.parse_jobs()


@app.get('/api/dou-by-category')
async def dou(keywords: Annotated[list[str] | str, Query()]) -> Iterable[JobPosting]:
    url = f'https://jobs.dou.ua/vacancies/'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    if isinstance(keywords, str):
        keywords = (keywords,)
    try:
        scraper = DouSeleniumScraper(url=url, driver=driver, keywords=keywords)
        htmls = await scraper.scrape()
        if isinstance(htmls, str):
            htmls = (htmls,)
        jobs = []
        for html in htmls:
            parser = DouParser(html)
            jobs.extend(parser.parse_jobs())
        return jobs
    finally:
        driver.quit()
