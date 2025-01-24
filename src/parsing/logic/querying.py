from abc import ABC, abstractmethod
from asyncio import sleep
from copy import copy
from typing import Iterable

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


class DouSeleniumScraper:
    def __init__(self, url: str, driver: WebDriver) -> None:
        self.__url = url
        self.__driver = driver

    async def fetch_html(self):
        self.__driver.delete_all_cookies()
        self.__driver.get(self.__url)
        await self.__click_load_more_jobs()
        return self.__driver.page_source

    async def __click_load_more_jobs(self):
        while True:
            try:
                load_more_button = WebDriverWait(self.__driver, 10).until(
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

            except Exception as e:
                print(f"Error during clicking load more button: {e}")
                break


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
