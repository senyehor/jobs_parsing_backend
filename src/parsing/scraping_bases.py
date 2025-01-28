from abc import ABC, abstractmethod
from copy import copy
from typing import Iterable

from httpx import AsyncClient, HTTPStatusError
from selenium.webdriver.chrome.webdriver import WebDriver
from urllib3.exceptions import RequestError

from src.exceptions import ExceptionWithMessageForUser


class HtmlScraperBase(ABC):
    def __init__(self, url: str, keywords: list[str]):
        self._url = url
        self._keywords = copy(keywords)

    @abstractmethod
    async def scrape(self) -> str | Iterable[str]:
        pass


class HttpxScraperBase(HtmlScraperBase):
    def __init__(self, client: AsyncClient, url: str, keywords: list[str]):
        super().__init__(url, keywords)
        self._client = client

    async def scrape(self) -> str | Iterable[str]:
        try:
            response = await self._client.get(self._url)
            response.raise_for_status()
            return response.text
        except (RequestError, HTTPStatusError) as e:
            raise ExceptionWithMessageForUser(
                message_for_user=f'Failed to fetch data from url: "f{self._url}"'
            ) from e


class SeleniumScraperBase(HtmlScraperBase, ABC):
    def __init__(self, driver: WebDriver, url: str, keywords: list[str]):
        super().__init__(url, keywords)
        self._driver = driver
