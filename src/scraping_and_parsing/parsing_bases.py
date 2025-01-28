from abc import ABC, abstractmethod
from typing import Iterable

from bs4 import BeautifulSoup

from src.scraping_and_parsing.models import JobPosting


class JobParser(ABC):

    def __init__(self, html: str) -> None:
        self._soup = BeautifulSoup(html, 'html.parser')

    @abstractmethod
    def parse_jobs(self, keywords: Iterable[str] | None = None) -> Iterable[JobPosting]:
        pass
