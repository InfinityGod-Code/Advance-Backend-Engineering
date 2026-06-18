from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    postgres_user: str = "postgres"
    postgres_password: str = "app"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "performance_optimizations"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    model_config = SettingsConfigDict(env_file=".env")


settings = DatabaseSettings()
