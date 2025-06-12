from fastapi import APIRouter
from .scrape.scrape import router as scraping_router

api_router = APIRouter(prefix="/api")

api_router.add_api_route(scraping_router)