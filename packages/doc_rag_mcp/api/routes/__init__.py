from fastapi import APIRouter
from .scrape.scrape import router as scraping_router

api_router = APIRouter()

api_router.include_router(scraping_router)