from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, HttpUrl


class _EmploymentOptions(StrEnum):
    remote = 'remote'
    on_site = 'on-site'
    hybrid = 'hybrid'


class JobPosting(BaseModel):
    link: HttpUrl
    job_title: str
    company_name: str
    location: str | None
    employment_type: _EmploymentOptions
    posted_at: datetime | None
