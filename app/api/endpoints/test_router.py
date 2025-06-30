from fastapi import APIRouter, HTTPException
import logging
from app.schemas.test_router import (
    TestRouter
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/router")
def init_data(request : TestRouter):
    name_python = request.name
    print(name_python)
    return {"name" : name_python} 