from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "FinanceAI Copilot"
    API_V1_STR: str = "/api/v1"
    
    # Security: SECRET_KEY must be provided via the environment
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v: Optional[str]) -> str:
        if not v or v.strip() == "":
            raise ValueError(
                "SECRET_KEY environment variable is missing. "
                "For security, the application cannot start without it. "
                "Please configure SECRET_KEY in your .env file."
            )
        return v

    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int = 5432
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        if isinstance(v, str) and v:
            return v
        
        data = info.data
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg2",
                username=data.get("POSTGRES_USER"),
                password=data.get("POSTGRES_PASSWORD"),
                host=data.get("POSTGRES_SERVER"),
                port=data.get("POSTGRES_PORT"),
                path=data.get("POSTGRES_DB") or "",
            )
        )

    # LLM Settings (Groq and future providers)
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama3-8b-8192"

    # Centralized Storage Configuration
    # Defaults to `/app/storage` (as mounted in Docker Compose) or local fallback
    STORAGE_DIR: Path = Path("/app/storage")

    @field_validator("STORAGE_DIR", mode="before")
    @classmethod
    def resolve_storage_dir(cls, v: Optional[str]) -> Path:
        if v:
            path = Path(v)
        else:
            path = BASE_DIR / "storage"
        
        # If the default /app/storage isn't writeable or we are running locally, fallback
        if not path.exists() and str(path) == "/app/storage":
            # Fallback to local workspace storage directory
            path = BASE_DIR.parent / "storage"
            
        return path.resolve()

    # Derived Paths (Exposed under settings)
    UPLOADS_DIR: Optional[Path] = None
    PARSED_DIR: Optional[Path] = None
    EMBEDDINGS_DIR: Optional[Path] = None
    FAISS_INDEX_PATH: Optional[str] = None
    GENERATED_REPORTS_DIR: Optional[Path] = None
    LOGS_DIR: Optional[Path] = None

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"), env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )

    def __init__(self, **values: Any):
        super().__init__(**values)
        # Dynamically set subdirectories based on STORAGE_DIR to avoid hardcoding
        self.UPLOADS_DIR = self.STORAGE_DIR / "uploads"
        self.PARSED_DIR = self.STORAGE_DIR / "parsed"
        self.EMBEDDINGS_DIR = self.STORAGE_DIR / "embeddings"
        self.FAISS_INDEX_PATH = str(self.STORAGE_DIR / "faiss")
        self.GENERATED_REPORTS_DIR = self.STORAGE_DIR / "generated_reports"
        self.LOGS_DIR = self.STORAGE_DIR / "logs"

        # Ensure directories exist
        for directory in [
            self.STORAGE_DIR,
            self.UPLOADS_DIR,
            self.PARSED_DIR,
            self.EMBEDDINGS_DIR,
            Path(self.FAISS_INDEX_PATH),
            self.GENERATED_REPORTS_DIR,
            self.LOGS_DIR,
        ]:
            directory.mkdir(parents=True, exist_ok=True)


# Instantiate settings - will fail if SECRET_KEY is missing
settings = Settings()
