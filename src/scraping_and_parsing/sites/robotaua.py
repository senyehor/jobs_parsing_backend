from typing import Iterable, List
from urllib.parse import urljoin

from playwright.async_api import Error, Page

from src.exceptions import ExceptionWithMessageForUser
from src.scraping_and_parsing.models import JobPosting
from src.scraping_and_parsing.parsing_bases import JobParser
from src.scraping_and_parsing.scraping_bases import PlayWrightScraperBase
from src.scraping_and_parsing.sites.site_base import SiteBase

_BASE_URL = 'https://robota.ua/'


class RobotaUAScraper(PlayWrightScraperBase):
    __NEXT_BUTTON_SELECTOR = 'a.side-btn.next.ng-star-inserted'
    __SEARCH_INPUT_SELECTOR = 'alliance-jobseeker-search input'

    async def scrape(self, base_url: str, keywords: list[str] | None = None) -> str | Iterable[str]:
        context = await self._browser.new_context()
        htmls = []
        for keyword in keywords:
            page = await context.new_page()
            try:
                htmls.extend(await self.__scrape_for_keyword(page, base_url, keyword))
            except Error as e:
                raise ExceptionWithMessageForUser(
                    message_for_user=f"Failed to process page: {base_url}"
                ) from e
            finally:
                await page.close()
        return htmls

    async def __scrape_for_keyword(self, page: Page, base_url: str, keyword: str) -> List[str]:
        await page.goto(base_url)
        await page.fill(self.__SEARCH_INPUT_SELECTOR, keyword)
        await page.press(self.__SEARCH_INPUT_SELECTOR, 'Enter')
        await page.wait_for_load_state("networkidle")
        htmls = [await page.content()]
        while True:
            next_button = await page.query_selector(self.__NEXT_BUTTON_SELECTOR)
            if not next_button or await next_button.is_disabled():
                break
            async with page.expect_navigation(wait_until="networkidle"):
                await next_button.click()
            htmls.append(await page.content())

        return htmls


class RobotaUAParser(JobParser):
    __BASE_URL = _BASE_URL

    def parse_jobs(self, keywords: Iterable[str] | None = None) -> Iterable[JobPosting]:
        jobs_container = self._soup.find('alliance-jobseeker-desktop-vacancies-list')
        job_divs = jobs_container.find_all('alliance-vacancy-card-desktop')
        jobs_list = []
        for div_with_job_info in job_divs:
            job_title = div_with_job_info.find('h2').get_text(strip=True)
            job_link = urljoin(self.__BASE_URL, div_with_job_info.find('a').get('href'))
            div_with_company_name_and_location = div_with_job_info.find(
                'div',
                class_=['santa-flex', 'santa-justify-between']
            )
            spans = div_with_company_name_and_location.find_all('span')
            company_name = spans[0].get_text(strip=True)
            location = spans[1].get_text(strip=True)
            jobs_list.append(
                JobPosting(
                    link=job_link,
                    company_name=company_name,
                    job_title=job_title,
                    location=location,
                )
            )
        return jobs_list


class RobotaUA(SiteBase):
    slug = 'robotaua'
    base_url = _BASE_URL
    scraper_class = RobotaUAScraper
    parser_class = RobotaUAParser
