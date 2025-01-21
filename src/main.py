from typing import Annotated, Iterable

from fastapi import FastAPI, Query
from httpx import AsyncClient

from src.parsing.logic.parsing import GenTechJobParser
from src.parsing.logic.querying import fetch_html
from src.parsing.models import JobPosting

app = FastAPI()


@app.get("/")
async def root(keywords: Annotated[list[str] | str, Query()]) -> Iterable[JobPosting]:
    async with AsyncClient() as client:
        url = 'https://gen-tech.breezy.hr/'
        html = await fetch_html(url, client)
        if isinstance(keywords, str):
            keywords = (keywords,)
        parser = GenTechJobParser(html, 'Genesis', keywords, url)
        return parser.get_jobs()
