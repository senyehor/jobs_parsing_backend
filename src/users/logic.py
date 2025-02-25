from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User


async def register_or_get_user(
        db: AsyncSession, email: str, name: str,
        google_subject_id: int
) -> User:
    existing_user_query = await db.execute(select(User).where(User.email == email))
    if existing_user := existing_user_query.scalars().first():
        return existing_user
    new_user = User(email=email, name=name, google_subject_id=google_subject_id)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
