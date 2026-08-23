"""
Application Configuration Settings
"""

import os
from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Universal Resume Extraction and Injection Engine"
    version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",
        "chrome-extension://*",
        "moz-extension://*",
        "*"
    ]


settings = Settings()
