from typing import Annotated, Iterable

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from src.parsing.logic.parsing import DouParser, GenTechJobParser
from src.parsing.logic.querying import DouSeleniumScraper, fetch_html
from src.parsing.models import JobPosting

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
async def root(keyword: Annotated[list[str] | str, Query()]) -> Iterable[JobPosting]:
    async with AsyncClient() as client:
        url = 'https://gen-tech.breezy.hr/'
        html = await fetch_html(url, client)
        if isinstance(keyword, str):
            keyword = (keyword,)
        parser = GenTechJobParser(html, 'Genesis', keyword, url)
        return parser.get_jobs()


@app.get('/api/dou-by-category')
async def dou(keywords: Annotated[list[str] | str, Query()]) -> Iterable[JobPosting]:
    url = f'https://jobs.dou.ua/vacancies/'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    if isinstance(keywords, str):
        keywords = (keywords,)
    try:
        scraper = DouSeleniumScraper(url=url, driver=driver, keywords=keywords)
        htmls = await scraper.scrape()
        jobs = []
        for html in htmls:
            parser = DouParser(html, ('Python', 'Java'))
            jobs.extend(parser.get_jobs())
        return jobs
    finally:
        driver.quit()
