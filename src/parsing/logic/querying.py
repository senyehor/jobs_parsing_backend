from abc import ABC, abstractmethod
from asyncio import sleep
from copy import copy
from typing import Iterable
from urllib.parse import urlencode, urljoin

from httpx import AsyncClient, Client, HTTPStatusError, RequestError
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.exceptions import ExceptionWithMessageForUser


async def fetch_html(url: str, client: AsyncClient) -> str:
    try:
        response = await client.get(url)
        response.raise_for_status()
        return response.text
    except (RequestError, HTTPStatusError) as e:
        raise ExceptionWithMessageForUser(
            message_for_user=f'Failed to fetch data from url: "f{url}"'
        ) from e


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


class DouSeleniumScraper(SeleniumScraperBase):

    async def scrape(self) -> str | Iterable[str]:
        # todo handle non-existent keywords?
        urls = [
            urljoin(
                self._url,
                f'?{urlencode({"category": keyword})}'  # creating q-parameters
            )
            for keyword in self._keywords
        ]
        pages = []
        for url in urls:
            self._driver.get(url)
            await self.__load_all_jobs()
            pages.append(self._driver.page_source)
        return pages if len(pages) > 1 else pages[0]

    async def __load_all_jobs(self):
        while True:
            try:
                load_more_button = WebDriverWait(self._driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='more-btn']/a")
                    )
                )
                if load_more_button.is_displayed():
                    load_more_button.click()
                    # give the browser some time to render,
                    # clicks on a job posting otherwise
                    await sleep(1)
                else:
                    break

            except Exception as e:  # todo think of specific exceptions
                print(f"Error during clicking load more button: {e}")
                break
