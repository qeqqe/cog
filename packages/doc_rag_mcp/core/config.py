from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    PROJECT_NAME: str = "Document RAG MCP"
    QDRANT_URL: str
    QDRANT_COLLECTION_NAME: str = "docs_collection"
    EMBEDDING_MODEL_NAME: str = "text-embedding-3-large"
