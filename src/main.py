from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.jobs.router import router as jobs_router
from src.scraping_and_parsing.router import router as scraping_router
from src.users.config import OAUTH_CONFIG
from src.users.router import router as users_router

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
app.include_router(users_router, prefix='/api/v1')
