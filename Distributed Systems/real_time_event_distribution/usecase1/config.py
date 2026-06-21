import os

class Settings:
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    EVENT_CHANNEL: str = "realtime_events"

settings = Settings()