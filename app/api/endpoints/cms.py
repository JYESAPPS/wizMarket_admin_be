from fastapi import APIRouter, HTTPException
from app.schemas.cms import ThumbnailInsertRequest
from fastapi import Request
from app.service.cms import (
    insert_thumbnail as service_insert_thumbnail
)

router = APIRouter()



router = APIRouter()

@router.post("/thumbnail/insert")
async def insert_thumbnail(data: ThumbnailInsertRequest):
    # 예: categoryName, styles 접근
    print("카테고리명:", data.categoryId)
    for style in data.styles:
        print(f"스타일 {style.designId} - 프롬프트 수: {len(style.prompts)}")
    
    service_insert_thumbnail(data)

    return {"message": "ok"}