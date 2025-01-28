from abc import ABC, abstractmethod
from typing import Iterable

from bs4 import BeautifulSoup

from src.scraping_and_parsing.models import JobPosting


class JobParser(ABC):

    def __init__(self, html: str) -> None:
        self._soup = BeautifulSoup(html, 'html.parser')

    @abstractmethod
    def parse_jobs(self) -> Iterable[JobPosting]:
        pass


class JobParserWithTitleFiltering(JobParser, ABC):

    def __init__(self, html: str, title_filtering_keywords: Iterable[str]) -> None:
        super().__init__(html)
        self._keywords = title_filtering_keywords
