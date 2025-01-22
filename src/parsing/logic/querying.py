from httpx import AsyncClient, HTTPStatusError, RequestError
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

    def fetch_html(self):
        self.__driver.get(self.__url)
        self.__click_load_more_jobs()
        return self.__driver.page_source

    def __click_load_more_jobs(self):
        while True:
            try:
                load_more_button = WebDriverWait(self.__driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='more-btn']/a")
                    )
                )
                if load_more_button.is_displayed():
                    load_more_button.click()
                else:
                    break

            except Exception as e:
                print(f"Error during clicking load more button: {e}")
                break
