from asyncio import sleep
from logging import getLogger
from time import sleep
from typing import Iterable
from urllib.parse import urlencode, urljoin

from selenium.common import ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.scraping_and_parsing.models import JobPosting
from src.scraping_and_parsing.parsing_bases import JobParser
from src.scraping_and_parsing.scraping_bases import SeleniumScraperBase
from src.scraping_and_parsing.sites.site_base import SiteBase

logger = getLogger(__name__)


class DouParser(JobParser):

    def parse_jobs(self, keywords: Iterable[str] | None = None) -> Iterable[JobPosting]:
        jobs_div = self._soup.find('div', id='vacancyListId')
        jobs = jobs_div.find_all('li', class_='l-vacancy')
        jobs_list = []
        for job in jobs:
            title_div = job.find('div', class_='title')
            job_title = title_div.find('a').text
            job_link = title_div.find('a').get('href')
            date_posted = job.find('div', class_='date').text
            location = job.find('span', class_='cities').text.split(', ')
            company_name = job.find('a', class_='company').get_text(strip=True)
            jobs_list.append(
                JobPosting(
                    link=job_link,
                    company_name=company_name,
                    job_title=job_title,
                    location=location,
                    posted_at=date_posted
                )
            )
        return jobs_list


class DouSeleniumScraper(SeleniumScraperBase):

    def scrape(self, url: str, keywords: list[str] | None = None) -> str | Iterable[str]:
        # todo handle non-existent keywords?
        urls = [
            urljoin(
                url,
                f'?{urlencode({"category": keyword})}'  # creating q-parameters
            )
            for keyword in keywords
        ]
        pages = []
        for url in urls:
            self._driver.get(url)
            self.__load_all_jobs()
            pages.append(self._driver.page_source)
        return pages if len(pages) > 1 else pages[0]

    def __load_all_jobs(self):
        while True:
            try:
                load_more_button = WebDriverWait(self._driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//div[@class='more-btn']/a")
                    )
                )
                if load_more_button.is_displayed():
                    sleep(1)  # give browser some time to render, clicks on a job posting otherwise
                    load_more_button.click()
                else:
                    break

            except ElementNotInteractableException:
                # expected behavior, signaling all jobs were loaded
                break
            except Exception as e:
                logger.error('Failed to load all dou jobs', e)
                break


class Dou(SiteBase):
    slug = 'dou'
    base_url = 'https://jobs.dou.ua/vacancies/'
    scraper_class = DouSeleniumScraper
    parser_class = DouParser
