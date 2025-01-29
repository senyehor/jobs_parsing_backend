import re
from typing import Iterable
from urllib.parse import urljoin

from bs4 import Tag

from src.scraping_and_parsing.models import JobPosting
from src.scraping_and_parsing.parsing_bases import JobParser
from src.scraping_and_parsing.scraping_bases import HttpxScraperBase
from src.scraping_and_parsing.sites.site_base import SiteBase

_SITE_NAME = 'Genesis'
_BASE_URL = 'https://gen-tech.breezy.hr/'


class GenesisParser(JobParser):
    __LOCATION_CODES_MAPPING = {
        '%LABEL_POSITION_TYPE_REMOTE_ANY%':    'remote',
        '%LABEL_POSITION_TYPE_REMOTE_WITHIN%': 'remote within location'
    }
    __EMPLOYMENT_TYPES_MAPPING = {
        '%LABEL_POSITION_TYPE_FULL_TIME%': 'full-time',
        '%LABEL_POSITION_TYPE_PART_TIME%': 'part-time',
    }
    __SITE_NAME = _SITE_NAME
    __BASE_URL = _BASE_URL

    def parse_jobs(self, keywords: Iterable[str] | None = None) -> Iterable[JobPosting]:
        positions_container = self._soup.find('div', class_='positions-container')
        jobs_containers = positions_container.find_all('li', class_='position transition')
        jobs = []
        for job in jobs_containers:
            last_a_tag = job.find_all('a')[-1]
            job_title = last_a_tag.find(re.compile(r'h[1-6]')).text.strip()
            if not self.__check_title_for_keywords(job_title, keywords or []):
                continue
            href_to_job = last_a_tag.get('href')
            location = self.__extract_location(last_a_tag)
            employment_type = self.__extract_employment_type(last_a_tag)
            jobs.append(
                JobPosting(
                    link=urljoin(self.__BASE_URL, href_to_job),
                    job_title=job_title,
                    company_name=self.__SITE_NAME,
                    location=location,
                    employment_type=employment_type
                )
            )
        return jobs

    def __extract_location(self, outer_tag: Tag) -> Iterable[str] | str:
        spans = outer_tag.select('li.location span:not(.spacer)')
        locations = []
        for span in spans:
            location = span.text
            # replace location code with human-readable value due to how
            # location is represented when request is made programmatically
            if location in self.__LOCATION_CODES_MAPPING:
                location = self.__LOCATION_CODES_MAPPING[location]
            locations.append(location)
        return locations if len(locations) > 1 else locations[0]

    def __extract_employment_type(self, outer_tag: Tag) -> str:
        employment_type = outer_tag.find('li', class_='type').find('span').text
        if employment_type in self.__EMPLOYMENT_TYPES_MAPPING:
            employment_type = self.__EMPLOYMENT_TYPES_MAPPING[employment_type]
        return employment_type

    def __check_title_for_keywords(self, title: str, keywords: Iterable[str]) -> bool:
        for keyword in keywords:
            if keyword.lower() in title.lower():
                return True
        return False


class GenesisScraper(HttpxScraperBase):
    pass


class Genesis(SiteBase):
    site_name = _SITE_NAME
    base_url = _BASE_URL
    scraper_class = GenesisScraper
    parser_class = GenesisParser
