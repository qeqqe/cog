from fastapi import APIRouter

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.get("/get_context")
async def get_context(url: str):
    
    return {"url": url}