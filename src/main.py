import secrets

from authlib.integrations.starlette_client import OAuth
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.config import Config
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from src.config import OAUTH_CONFIG
from src.db.engine import create_db
from src.jobs.router import router as jobs_router
from src.scraping_and_parsing.router import router as scraping_router
from src.users.logic import register_or_get_user
from src.users.models import User

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=OAUTH_CONFIG.APP_SECRET_KEY)

app.include_router(jobs_router, prefix='/api/v1')
app.include_router(scraping_router, prefix='/api/v1')

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


@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    nonce = secrets.token_urlsafe(16)
    request.session['nonce'] = nonce
    return await oauth.google.authorize_redirect(request, redirect_uri, nonce=nonce)


@app.get("/auth/callback")
async def auth_callback(request: Request, db: AsyncSession = Depends(create_db)) -> User:
    token = await oauth.google.authorize_access_token(request)
    nonce = request.session.pop("nonce", None)
    google_user = await oauth.google.parse_id_token(token, nonce)
    db_user = await register_or_get_user(
        db,
        email=google_user['email'],
        name=google_user['given_name'],
        google_subject_id=google_user['sub']
    )
    request.session["user_id"] = db_user.id
    return db_user


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse("/")
