from datetime import datetime
from typing import Iterable

from pydantic import BaseModel, HttpUrl


class JobPosting(BaseModel):
    link: HttpUrl
    job_title: str
    company_name: str
    location: str | None | Iterable[str] = None
    employment_type: str
    posted_at: datetime | None = None
