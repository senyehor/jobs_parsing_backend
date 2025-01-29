from abc import ABC, abstractmethod
from typing import Iterable

from httpx import AsyncClient, HTTPStatusError
from selenium.webdriver.chrome.webdriver import WebDriver
from urllib3.exceptions import RequestError

from src.exceptions import ExceptionWithMessageForUser


class HtmlScraperBase(ABC):

    @abstractmethod
    async def scrape(self, url: str, keywords: list[str] | None = None) -> str | Iterable[str]:
        pass


class HttpxScraperBase(HtmlScraperBase):
    def __init__(self, client: AsyncClient):
        self._client = client

    async def scrape(self, url: str, keywords: list[str] | None = None) -> str | Iterable[str]:
        try:
            response = await self._client.get(url)
            response.raise_for_status()
            return response.text
        except (RequestError, HTTPStatusError) as e:
            raise ExceptionWithMessageForUser(
                message_for_user=f'Failed to fetch data from url: "f{url}"'
            ) from e


class SeleniumScraperBase(HtmlScraperBase, ABC):
    def __init__(self, driver: WebDriver):
        self._driver = driver
