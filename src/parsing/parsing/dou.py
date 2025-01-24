from typing import Iterable

from src.parsing.models import JobPosting
from src.parsing.parsing.bases import JobParser


class DouParser(JobParser):

    def parse_jobs(self) -> Iterable[JobPosting]:
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
