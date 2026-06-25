import os
from dataclasses import dataclass


@dataclass
class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./cotton_pilot.db")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "cotton-pilot-dev-secret")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
    agent_step_delay_ms: int = int(os.getenv("AGENT_STEP_DELAY_MS", "250"))
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "")
    llm_model: str = os.getenv("LLM_MODEL", "")
    llm_timeout: float = float(os.getenv("LLM_TIMEOUT", "8"))


settings = Settings()
