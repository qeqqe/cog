from fastapi import APIRouter
from ingestion.sequential_crawler.crawl import crawl_sequentially

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.get("/get_context")
async def get_context(url: str):
    """Runs the RAG pipeline on the given sitemap URL and returns the context metadata.
    Args:
        url (str): The URL to scrape and process.
    """
    result = await crawl_sequentially(url)
    return result