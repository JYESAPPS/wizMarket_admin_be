from fastapi import APIRouter, HTTPException
import logging
from app.schemas.test_router import (
    TestRouter
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/select/init/stat/corr")
def init_data(request : TestRouter):
    name = request.name

    return {"name" : name} 