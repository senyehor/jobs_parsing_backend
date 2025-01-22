from typing import Annotated, Iterable

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from httpx import AsyncClient

from src.parsing.logic.parsing import GenTechJobParser
from src.parsing.logic.querying import fetch_html
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
