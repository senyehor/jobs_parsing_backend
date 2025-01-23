import re
from typing import Iterable

from bs4 import BeautifulSoup, Tag

from src.exceptions import ExceptionWithMessageForUser
from src.parsing.models import JobPosting


class GenTechJobParser:
    __LOCATION_CODES_MAPPING = {
        '%LABEL_POSITION_TYPE_REMOTE_ANY%':    'remote',
        '%LABEL_POSITION_TYPE_REMOTE_WITHIN%': 'remote within location'
    }

    __EMPLOYMENT_TYPES_MAPPING = {
        '%LABEL_POSITION_TYPE_FULL_TIME%': 'full-time',
        '%LABEL_POSITION_TYPE_PART_TIME%': 'part-time',
    }

    def __init__(
            self, page_html: str, company_name: str,
            job_title_keywords: Iterable[str], base_url: str
    ):
        self.__soup = BeautifulSoup(page_html, 'html.parser')
        self.__keywords = job_title_keywords
        self.__company_name = company_name
        self.__base_url = base_url

    def get_jobs(self) -> Iterable[JobPosting]:
        try:
            return self.__parse()
        except Exception as e:
            raise ExceptionWithMessageForUser(
                message_for_user='Encountered unexpected error while parsing jobs'
            ) from e

    def __parse(self):
        positions_container = self.__soup.find('div', class_='positions-container')
        jobs_containers = positions_container.find_all('li', class_='position transition')
        jobs = []
        for job in jobs_containers:
            last_a_tag = job.find_all('a')[-1]
            job_title = last_a_tag.find(re.compile(r'h[1-6]')).text.strip()
            if not self.__check_title_for_keywords(job_title):
                continue
            href_to_job = last_a_tag.get('href')
            location = self.__extract_location(last_a_tag)
            employment_type = self.__extract_employment_type(last_a_tag)
            jobs.append(
                JobPosting(
                    link=self.__base_url.rstrip('/') + href_to_job,
                    job_title=job_title,
                    company_name=self.__company_name,
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

    def __check_title_for_keywords(self, title: str) -> bool:
        for keyword in self.__keywords:
            if keyword.lower() in title.lower():
                return True
        return False


class DouParser:
    def __init__(
            self, page_html: str,
            job_title_keywords: Iterable[str]
    ):
        self.__soup = BeautifulSoup(page_html, 'html.parser')
        self.__keywords = job_title_keywords

    def get_jobs(self) -> Iterable[JobPosting]:
        try:
            return self.__parse()
        except Exception as e:
            raise ExceptionWithMessageForUser(
                message_for_user='Encountered unexpected error while parsing jobs'
            ) from e

    def __parse(self):
        jobs_div = self.__soup.find('div', id='vacancyListId')
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
