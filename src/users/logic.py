from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User


async def register_user_if_not_already(
        db: AsyncSession, email: str, name: str,
        google_subject_id: int
):
    existing_user = await db.execute(select(User).where(User.email == email))
    if existing_user.all():
        # todo maybe exception
        return None
    new_user = User(email=email, name=name, google_subject_id=google_subject_id)
    db.add(new_user)
    await db.commit()
    return new_user
