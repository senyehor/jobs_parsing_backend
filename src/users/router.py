import secrets

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.config import Config
from starlette.responses import RedirectResponse

from src.config import APP_CONFIG
from src.db.engine import create_db
from src.users.config import OAUTH_CONFIG
from src.users.logic import get_user_by_id, register_or_get_user
from src.users.models import User

router = APIRouter()

oauth = OAuth(
    Config(
        environ={
            'GOOGLE_CLIENT_ID':     OAUTH_CONFIG.GOOGLE_CLIENT_ID,
            "GOOGLE_CLIENT_SECRET": OAUTH_CONFIG.GOOGLE_SECRET_KEY,
            'SECRET_KEY':           OAUTH_CONFIG.APP_SECRET_KEY
        }
    )
)
oauth.register(
    name='google',
    client_id=OAUTH_CONFIG.GOOGLE_CLIENT_ID,
    client_secret=OAUTH_CONFIG.GOOGLE_SECRET_KEY,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    authorize_params={"scope": "openid email profile"},
    access_token_url="https://oauth2.googleapis.com/token",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    nonce = secrets.token_urlsafe(16)
    request.session['nonce'] = nonce
    return await oauth.google.authorize_redirect(request, redirect_uri, nonce=nonce)


@router.get("/auth/callback")
async def auth_callback(request: Request, db: AsyncSession = Depends(create_db)):
    token = await oauth.google.authorize_access_token(request)
    nonce = request.session.pop("nonce", None)
    google_user = await oauth.google.parse_id_token(token, nonce)
    db_user = await register_or_get_user(
        db,
        email=google_user['email'],
        name=google_user['given_name'],
        google_subject_id=google_user['sub']
    )
    request.session['user_id'] = db_user.id
    return RedirectResponse(APP_CONFIG.FRONTEND_URL, status_code=status.HTTP_303_SEE_OTHER)


@router.get("users/logout")
async def logout(request: Request):
    request.session.pop('user_id', None)
    return RedirectResponse(APP_CONFIG.FRONTEND_URL, status_code=status.HTTP_303_SEE_OTHER)


@router.post('/users/me')
async def me(request: Request, db: AsyncSession = Depends(create_db)) -> User:
    if user := await get_user_by_id(db, request.session.get('user_id', None)):
        return user
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
