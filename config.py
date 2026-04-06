from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    gemini_api_key: str
    langchain_api_key: str = ""
    langchain_tracing_v2: str = "true"
    langchain_project: str = "code-reviewer"
    llm_model: str = "gemini-1.5-flash"
    max_tokens: int = 2000

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()