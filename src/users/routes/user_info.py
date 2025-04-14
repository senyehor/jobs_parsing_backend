from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from src.db.engine import create_session
from src.users.logic import get_user_by_id
from src.users.models import User

router = APIRouter()


@router.get('/users/me')
async def me(request: Request, db: AsyncSession = Depends(create_session)) -> User:
    if user := await get_user_by_id(db, request.session.get('user_id', None)):
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
