from app.schemas.loc_store import LocStoreInfoForContentOutPut
from app.service.population import *
from app.db.connect import *
from app.crud.loc_store import (
    select_loc_store_for_content_by_store_business_number as crud_select_loc_store_for_content_by_store_business_number,
    match_exist_store as crud_match_exist_store,
    get_category_name as crud_get_category_name,
    get_max_number as crud_get_max_number, 
    add_new_store as crud_add_new_store,
    get_store_data as crud_get_store_data,
    get_city_data as crud_get_city_data,
    get_loc_info_data as crud_get_loc_info_data,
    get_category_data as crud_get_category_data,
    get_biz_id as crud_get_biz_id,
    get_biz_category_name as crud_get_biz_category_name,
    get_top5 as crud_get_top5
)
from app.crud.loc_store import *


# 필터로 조회
def filter_loc_store(filters):

    data = get_filtered_loc_store(
        filters.dict()
    )  # 필터 데이터를 딕셔너리로 전달

    return data


def select_loc_store_for_content_by_store_business_number(
    store_business_number: str,
) -> LocStoreInfoForContentOutPut:

    results = crud_select_loc_store_for_content_by_store_business_number(
        store_business_number
    )
    if not results:
        raise HTTPException(status_code=404, detail="report loc_info not found")
    return results



# 기존 매장 일치 여부
def match_exist_store(data) :
    city_id = data.city_id
    district_id = data.district_id
    sub_district_id = data.sub_district_id
    large_category_code = data.large_category_code
    medium_category_code = data.medium_category_code
    small_category_code = data.small_category_code
    store_name = data.store_name


    sucess = crud_match_exist_store(
        city_id, district_id, sub_district_id,
        large_category_code, medium_category_code, small_category_code,
        store_name
    )

    return sucess


# 값 넣기
def add_new_store(data, longitude, latitude):
    city_id = data.city_id
    district_id = data.district_id
    sub_district_id = data.sub_district_id
    reference_id = data.reference_id
    large_category_code = data.large_category_code
    medium_category_code = data.medium_category_code
    small_category_code = data.small_category_code
    store_name = data.store_name
    road_name = data.road_name
    selected = data.selected

    # 초기값은 모두 0
    tag_flags = {
        "jsam": 0,
        "ktmyshop": 0,
        "PULMUONE": 0
    }

    # selected 리스트에 포함된 항목이 있으면 해당 플래그를 1로 설정
    for key in tag_flags:
        if key in selected:
            tag_flags[key] = 1

    large_category_name, medium_category_name, small_cateogry_name = crud_get_category_name(small_category_code)

    # MAX 매장 관리 번호 값 뽑기
    prev_number = crud_get_max_number()  # 예: "JS0012"

    # JS 접두사 제거 + 숫자 변환
    if prev_number:
        number = int(prev_number[0]) + 1
    else:
        number = 1  # 처음 등록이라면 JS0001부터 시작

    # 다음 store_business_number 구성
    store_business_number = f"JS{number:04d}"  # JS0013 형식
    sucess = crud_add_new_store(
        store_business_number, city_id, district_id, sub_district_id, reference_id, 
        large_category_code, medium_category_code, small_category_code,
        large_category_name, medium_category_name, small_cateogry_name,
        store_name, road_name, longitude, latitude, tag_flags
    )

    return sucess, store_business_number


# DB 연동
def copy_new_store(store_business_number):

    # 매장 데이터 꺼내오기
    sub_district_id, store_name, road_name, small_category_name, small_category_code, longitude, latitude = crud_get_store_data(store_business_number)

    # 지역 명 가져오기
    city_name, district_name, sub_district_name = crud_get_city_data(sub_district_id)

    # 입지 정보 값 가져오기
    shop, move_pop, sales, work_pop, income, spend, house, resident = crud_get_loc_info_data(sub_district_id)

    # 입지 j-score 값 가져오기

    # 상권 정보 값 가져오기
    ## 카테고리 엮기
    
    ### 상권 정보 분류표 ID 가져오기
    business_area_category_id = crud_get_category_data(small_category_code)

    ### 매핑 값 가져오기
    rep_id = crud_get_biz_id(business_area_category_id)

    ### 매핑한 NAME 값 가져오기
    biz_main_category_id, biz_sub_category_id, biz_detail_category_id = crud_get_biz_category_name(rep_id)

    # 소분류 주문 TOP 메뉴 가져오기
    top_1, top_2, top_3, top_4, top_5 = crud_get_top5(sub_district_id, rep_id)
    print(top_1)
    # 리포트에 넣기
    print(small_category_code)










