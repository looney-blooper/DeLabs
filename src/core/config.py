from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, PostgresDsn, AmqpDsn
from functools import lru_cache

class Settings(BaseSettings):
    #llm api
    gemini_api_key : SecretStr | None = None
    groq_api_key : SecretStr 

    #tracking
    langchain_tracking_v2 : str = "true"
    langchain_api_key : SecretStr | None = None
    langchain_project :str = "DeLabs_Dev"
    wandb_api_key : SecretStr | None = None

    #infra
    database_url : PostgresDsn
    rabbitmq_url : AmqpDsn

    #Minio Configurations
    MINIO_ENDPOINT : str | None = None
    MINIO_ROOT_USER : str | None = None
    MINIO_ROOT_PASSWORD : str | None = None

    #app config
    environment : str = "development"
    debug : bool = True

    #looks for .env file in root for the api keys
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()