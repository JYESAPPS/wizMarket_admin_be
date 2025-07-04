import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from app.api.endpoints import (
    biz_detail_category,
    biz_main_category,
    biz_sub_category,
    cai_info,
    category,
    category_content,
    city,
    classification,
    district,
    hello,
    reference,
    rising_business,
    commercial_district,
    local_store_content,
    ads,
    cms
)
from app.api.endpoints import loc_info
from app.api.endpoints import population
from app.api.endpoints import city
from app.api.endpoints import loc_store
from app.api.endpoints import business_area_category
from app.api.endpoints import statistics

app = FastAPI()

load_dotenv()

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(os.getenv("ALLOWED_ORIGINS", ""))

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI!"}


app.include_router(hello.router, prefix="/hello")
app.include_router(population.router, prefix="/population")
app.include_router(loc_info.router, prefix="/loc/info")
app.include_router(loc_store.router, prefix="/loc/store")
app.include_router(commercial_district.router, prefix="/commercial")
app.include_router(rising_business.router, prefix="/rising")
app.include_router(cai_info.router, prefix="/cai")
app.include_router(city.router, prefix="/city")
app.include_router(district.router, prefix="/district")
app.include_router(reference.router, prefix="/reference")
app.include_router(biz_main_category.router, prefix="/biz_main_category")
app.include_router(biz_sub_category.router, prefix="/biz_sub_category")
app.include_router(biz_detail_category.router, prefix="/biz_detail_category")
app.include_router(business_area_category.router, prefix="/business_area_category")
app.include_router(category.router, prefix="/category")
app.include_router(classification.router, prefix="/classification")
app.include_router(statistics.router, prefix="/statistics")
app.include_router(local_store_content.router, prefix="/store/content")
app.include_router(category_content.router, prefix="/category/content")
app.include_router(ads.router, prefix="/ads")
app.include_router(cms.router, prefix="/cms")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=["."]
    )
