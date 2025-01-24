from abc import ABC, abstractmethod
from copy import copy
from typing import Iterable

from httpx import Client
from selenium.webdriver.chrome.webdriver import WebDriver


class HtmlScraperBase(ABC):
    def __init__(self, url: str, keywords: list[str]):
        self._url = url
        self._keywords = copy(keywords)

    @abstractmethod
    async def scrape(self) -> str | Iterable[str]:
        pass


class HttpxScraperBase(HtmlScraperBase, ABC):
    def __init__(self, client: Client, url: str, keywords: list[str]):
        super().__init__(url, keywords)
        self._client = client


class SeleniumScraperBase(HtmlScraperBase, ABC):
    def __init__(self, driver: WebDriver, url: str, keywords: list[str]):
        super().__init__(url, keywords)
        self._driver = driver
