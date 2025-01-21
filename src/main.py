from typing import Iterable

from fastapi import FastAPI
from httpx import AsyncClient

from src.parsing.logic.parsing import GenTechJobParser
from src.parsing.logic.querying import fetch_html
from src.parsing.models import JobPosting

app = FastAPI()


@app.get("/")
async def root() -> Iterable[JobPosting]:
    async with AsyncClient() as client:
        url = 'https://gen-tech.breezy.hr/'
        html = await fetch_html(url, client)
        parser = GenTechJobParser(html, 'Genesis', ('python',), url)
        return parser.get_jobs()
