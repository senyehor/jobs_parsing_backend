from asyncio import sleep
from typing import Iterable
from urllib.parse import urlencode, urljoin

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.parsing.scraping_bases import SeleniumScraperBase


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
