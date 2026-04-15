from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    log_level: str = "INFO"

    openai_api_key: str = ""

    postgres_user: str = "opsmind"
    postgres_password: str = "opsmind"
    postgres_db: str = "opsmind"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    redis_host: str = "localhost"
    redis_port: int = 6379

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    api_port: int = 8000

    embedding_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o-mini"

    chunk_target_tokens: int = 512
    chunk_overlap_tokens: int = 80
    retrieval_top_k: int = 12
    hybrid_semantic_weight: float = 0.55
    min_confidence_threshold: float = 0.35

    max_question_chars: int = 8000

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
