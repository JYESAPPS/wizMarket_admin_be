from typing import List
from pydantic import BaseModel

class StylePrompt(BaseModel):
    designId: int
    prompts: List[str]

class ThumbnailInsertRequest(BaseModel):
    categoryId: int
    styles: List[StylePrompt]
