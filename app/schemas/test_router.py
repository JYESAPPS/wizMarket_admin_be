from pydantic import BaseModel
from typing import Optional


class TestRouter(BaseModel):
    name: str  # 기본값 None을 설정
    