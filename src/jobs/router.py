from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.engine import create_session
from src.db.models import JobSite as JobSiteDBModel
from src.jobs.models import JobSite

router = APIRouter()


@router.get('/job-sites')
async def job_sites(db: AsyncSession = Depends(create_session)) -> list[JobSite]:
    results = await db.execute(select(JobSiteDBModel))
    return results.scalars().all()  # noqa
