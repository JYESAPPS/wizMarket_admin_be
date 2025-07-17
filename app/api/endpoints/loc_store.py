from fastapi import APIRouter, HTTPException
from app.service.loc_store import (
    filter_loc_store,
    select_loc_store_for_content_by_store_business_number as service_select_loc_store_for_content_by_store_business_number,
    
)
from app.service.loc_store_to_report import (
    match_exist_store as service_match_exist_store,
    add_new_store as service_add_new_store,
    copy_new_store as service_copy_new_store
)
from app.schemas.loc_store import *
import logging
import requests
import os
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# 필터로 조회
@router.post("/select/store/list")
def filter_data(filters: FilterRequest):
    # 필터 정보를 서비스 레이어로 전달
    data =  filter_loc_store(filters)

    return {
        "filtered_data": data,     # 페이징된 데이터
    }




# 매장 리스트에서 모달창 띄우기
@router.post("/select/init/content", response_model=LocStoreInfoForContentOutPut)
def select_loc_store_for_content_by_store_business_number(store_business_number: str):
    # 쿼리 매개변수로 전달된 store_business_number 값 수신
    try:
        data = service_select_loc_store_for_content_by_store_business_number(store_business_number)
        return data
    except HTTPException as http_ex:
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        raise http_ex
    except Exception as e:
        error_msg = f"Unexpected error while processing request: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


# 매장 1개 등록
@router.post("/add")
def add_new_store(request: AddRequest):
    # 1. 기존 매장 존재 여부 확인
    if not service_match_exist_store(request):
        return JSONResponse(
            status_code=200,
            content={"success": False, "message": "이미 등록된 매장입니다."}
        )

    # 2. 위경도 조회
    key = os.getenv("ROAD_NAME_KEY")
    apiurl = "https://api.vworld.kr/req/address"
    params = {
        "service": "address",
        "request": "getcoord",
        "crs": "epsg:4326",
        "address": request.road_name,
        "format": "json",
        "type": "road",
        "key": key
    }

    response = requests.get(apiurl, params=params)
    if response.status_code != 200:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "위경도 조회 실패", "number" : ""}
        )

    data = response.json()
    try:
        longitude = str(data['response']['result']['point']['x'])
        latitude = str(data['response']['result']['point']['y'])
    except (KeyError, TypeError, ValueError):
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "좌표 파싱 실패", "number" : ""}
        )

    # 3. 매장 등록 시도
    success, store_business_number = service_add_new_store(request, longitude, latitude)

    if success:
        return JSONResponse(
            status_code=200,
            content={"success": True, "message": "매장이 성공적으로 등록되었습니다.", "number" : store_business_number}
        )
    else:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "매장 등록 중 오류 발생", "number" : ""}
        )
    

# 등록한 매장 Report DB 로 연동
@router.post("/copy")
def copy_new_store(request: ReportRequest):
    store_business_number = request.store_business_number

    # 서비스 레이어 전달
    sucess = service_copy_new_store(store_business_number)








