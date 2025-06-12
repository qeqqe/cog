from fastapi import FastAPI
from .routes import api_router
from core.config import Settings

app = FastAPI(title=Settings.PROJECT_NAME)

app.include_router(api_router)
@app.get("/health")
def health_check():
    return {"status": "ok"}