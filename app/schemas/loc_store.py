from pydantic import BaseModel
from typing import Optional, List


class FilterRequest(BaseModel):
    city: Optional[int] = None  # 기본값 None을 설정
    district: Optional[int] = None
    subDistrict: Optional[int] = None
    storeName: Optional[str] = None
    matchType: Optional[str] = "="  # = 또는 LIKE 검색
    reference: Optional[int] = 3
    mainCategory: Optional[str] = None
    subCategory: Optional[str] = None
    detailCategory: Optional[str] = None
    selectedOptions: Optional[list] = None



class LocalStoreSubdistrict(BaseModel):
    local_store_id: int
    store_business_number: str
    sub_district_id: int
    sub_district_name: str

    class Config:
        from_attributes = True


class LocalStoreCityDistrictSubDistrict(BaseModel):
    local_store_id: int
    store_business_number: str
    store_name: str
    city_id: int
    city_name: str
    district_id: int
    district_name: str
    sub_district_id: int
    sub_district_name: str
    large_category_name: str
    medium_category_name: str
    small_category_name: str
    reference_id: int

    class Config:
        from_attributes = True
    
class BusinessAreaCategoryReportOutput(BaseModel):
    business_area_category_id: int

    class Config:
        from_attributes = True   

class BizDetailCategoryIdOutPut(BaseModel):
    rep_id: int
    biz_detail_category_name: str

    class Config:
        from_attributes = True  

class BizCategoriesNameOutPut(BaseModel):
    biz_main_category_name: str
    biz_sub_category_name: str
    biz_detail_category_name: str


class RisingMenuOutPut(BaseModel):
    market_size: Optional[int] = 0
    average_sales: Optional[int] = 0
    average_payment: Optional[int] = 0
    usage_count: Optional[int] = 0
    avg_profit_per_mon: Optional[float] = 0.0
    avg_profit_per_tue: Optional[float] = 0.0
    avg_profit_per_wed: Optional[float] = 0.0
    avg_profit_per_thu: Optional[float] = 0.0
    avg_profit_per_fri: Optional[float] = 0.0
    avg_profit_per_sat: Optional[float] = 0.0
    avg_profit_per_sun: Optional[float] = 0.0
    avg_profit_per_06_09: Optional[float] = 0.0
    avg_profit_per_09_12: Optional[float] = 0.0
    avg_profit_per_12_15: Optional[float] = 0.0
    avg_profit_per_15_18: Optional[float] = 0.0
    avg_profit_per_18_21: Optional[float] = 0.0
    avg_profit_per_21_24: Optional[float] = 0.0
    avg_profit_per_24_06: Optional[float] = 0.0
    avg_client_per_m_20: Optional[float] = 0.0
    avg_client_per_m_30: Optional[float] = 0.0
    avg_client_per_m_40: Optional[float] = 0.0
    avg_client_per_m_50: Optional[float] = 0.0
    avg_client_per_m_60: Optional[float] = 0.0
    avg_client_per_f_20: Optional[float] = 0.0
    avg_client_per_f_30: Optional[float] = 0.0
    avg_client_per_f_40: Optional[float] = 0.0
    avg_client_per_f_50: Optional[float] = 0.0
    avg_client_per_f_60: Optional[float] = 0.0
    top_menu_1: Optional[str] = 0.0
    top_menu_2: Optional[str] = 0.0
    top_menu_3: Optional[str] = 0.0
    top_menu_4: Optional[str] = 0.0
    top_menu_5: Optional[str] = 0.0

    class Config:
        from_attributes = True



class LocalStoreInfo(BaseModel):
    road_name_address: Optional[str] = ""
    store_name: Optional[str] = ""
    building_name: Optional[str] = ""
    floor_info: Optional[str] = ""
    small_category_name: Optional[str] = ""
    store_img_url: Optional[str] = "/static/images/report/basic_store_img.png"

    class Config:
        from_attributes = True


class LocalStoreLatLng(BaseModel):
    longitude: Optional[str] = ""
    latitude: Optional[str] = ""

    class Config:
        from_attributes = True


class WeatherInfo(BaseModel):
    icon: str
    temp: float

    class Config:
        from_attributes = True

class WeatherToday(BaseModel):
    weather: str
    temp: float
    sunset: int

    class Config:
        from_attributes = True


class LocalStoreInfoWeaterInfo(BaseModel):
    localStoreInfo: LocalStoreInfo
    weatherInfo: WeatherInfo

    class Config:
        from_attributes = True

class LocalStoreCityDistrictSubDistrict(BaseModel):
    local_store_id: int
    store_business_number: str
    store_name: str
    city_id: int
    city_name: str
    district_id: int
    district_name: str
    sub_district_id: int
    sub_district_name: str
    large_category_name: str
    medium_category_name: str
    small_category_name: str

    class Config:
        from_attributes = True


class StoreBusinessNumberInput(BaseModel):
    store_business_number: str

    class Config:
        from_attributes = True

class LocStoreInfoForContentOutPut(BaseModel):
    store_business_number: str
    store_name:str
    road_name_address:str

    class Config:
        from_attributes = True





class AddRequest(BaseModel):
    city_id: int
    district_id: int
    sub_district_id: int 

    reference_id:int 
    large_category_code: str 
    medium_category_code: str 
    small_category_code: str

    store_name: str 
    road_name : str
    selected: Optional[List[str]] = None


class ReportRequest(BaseModel):
    store_business_number: str



class OneStoreRequest(BaseModel):
    city_id: int
    district_id: int
    sub_district_id: int 

    reference_id:int 
    large_category_code: str 
    medium_category_code: str 
    small_category_code: str

    store_name: str 
    road_name : str
