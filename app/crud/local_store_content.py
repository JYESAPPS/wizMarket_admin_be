from app.db.connect import (
    get_db_connection, commit, close_connection, rollback, close_cursor, get_re_db_connection
)
from dotenv import load_dotenv
import pymysql
import os
from fastapi import HTTPException
import logging
from app.schemas.local_store_content import LocStoreContent, LocStoreContentList, LocStoreCategoryList, LocStoreDetailContent, LocStoreDetailContentResponse,LocStoreImage
from typing import Optional, List


load_dotenv()
logger = logging.getLogger(__name__)

def insert_store_content(store_business_number: str, title: str, content: str):
    # 데이터베이스 연결 설정
    connection = get_re_db_connection()
    
    try:
        with connection.cursor() as cursor:
            # 데이터 인서트 쿼리
            insert_query = """
                INSERT INTO LOCAL_STORE_CONTENT 
                (STORE_BUSINESS_NUMBER, TITLE, CONTENT) 
                VALUES (%s, %s, %s)
            """
            # 쿼리 실행
            cursor.execute(insert_query, (store_business_number, title, content))
            # 자동 생성된 PK 가져오기
            pk = cursor.lastrowid
            # 커밋하여 DB에 반영
            commit(connection)
            return pk

    except pymysql.MySQLError as e:
        rollback(connection)  # 오류 시 롤백
        print(f"Database error: {e}")
        raise

    finally:
        close_cursor(cursor)   # 커서 종료
        close_connection(connection)  # 연결 종료



def select_loc_store_content_list():
    connection = get_re_db_connection()

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            select_query = """
                SELECT 
                    ls.LOCAL_STORE_CONTENT_ID,
                    ls.STORE_BUSINESS_NUMBER,
                    r.STORE_NAME,
                    r.ROAD_NAME,
                    ls.TITLE,
                    ls.CONTENT,
                    ls.STATUS,
                    ls.CREATED_AT
                FROM
                    LOCAL_STORE_CONTENT ls
                STRAIGHT_JOIN REPORT r
                ON r.STORE_BUSINESS_NUMBER = ls.STORE_BUSINESS_NUMBER
                AND ls.STATUS != 'D';

            """
            cursor.execute(select_query)
            rows = cursor.fetchall()
            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail="LocStoreContentList 해당하는 매장 정보를 찾을 수 없습니다.",
                )
            result = [
                LocStoreContentList(
                    local_store_content_id=row["LOCAL_STORE_CONTENT_ID"],
                    store_business_number=row["STORE_BUSINESS_NUMBER"],
                    store_name=row["STORE_NAME"],
                    road_name=row["ROAD_NAME"],
                    title=row["TITLE"],
                    content=row["CONTENT"],
                    status=row["STATUS"],
                    created_at=row["CREATED_AT"],
                )
                for row in rows
            ]
            return result
    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred LocalStoreBasicInfo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        close_connection(connection)  # connection만 닫기



# 업종 조회
def select_loc_store_category(store_business_number: str):
    connection = get_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            select_query = """
                SELECT 
                    STORE_BUSINESS_NUMBER,
                    LARGE_CATEGORY_NAME,
                    MEDIUM_CATEGORY_NAME,
                    SMALL_CATEGORY_NAME
                FROM
                    LOCAL_STORE
                WHERE
                    STORE_BUSINESS_NUMBER = %s
                """
            cursor.execute(select_query, (store_business_number,))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"LocStoreCategoryList 해당하는 매장 정보를 찾을 수 없습니다.",
                )

            result = LocStoreCategoryList(
                store_business_number=row["STORE_BUSINESS_NUMBER"],
                large_category_name=row["LARGE_CATEGORY_NAME"],
                medium_category_name=row["MEDIUM_CATEGORY_NAME"],
                small_category_name=row["SMALL_CATEGORY_NAME"]
            )
            return result

    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred LocalStoreBasicInfo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        if cursor:
            close_cursor(cursor)
        close_connection(connection)



# 게시 상태 여부 업데이트
def update_loc_store_content_status(local_store_content_id: int, status: str) -> bool:
    connection = get_re_db_connection()

    try:
        with connection.cursor() as cursor:
            # 업데이트 쿼리 작성
            update_query = """
                UPDATE LOCAL_STORE_CONTENT
                SET STATUS = %s
                WHERE LOCAL_STORE_CONTENT_ID = %s
            """
            # 쿼리 실행
            cursor.execute(update_query, (status, local_store_content_id))
            connection.commit()
            
            # rowcount를 통해 업데이트 성공 여부 확인
            if cursor.rowcount == 0:
                return False  # 업데이트된 행이 없는 경우 False 반환
            return True  # 업데이트 성공 시 True 반환
    except pymysql.MySQLError as e:
        print(f"Database error occurred: {e}")
        raise HTTPException(status_code=503, detail="Database Connection Error")
    finally:
        if cursor:
            close_cursor(cursor)
        close_connection(connection)



# 글 상세 조회
def select_loc_store_for_detail_content(local_store_content_id: int):
    connection = get_re_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 첫 번째 쿼리: 매장 기본 정보 조회
            select_content_query = """
                SELECT 
                    LOCAL_STORE_CONTENT_ID,
                    TITLE,
                    CONTENT,
                    STATUS
                FROM
                    LOCAL_STORE_CONTENT
                WHERE
                    LOCAL_STORE_CONTENT_ID = %s
            """
            cursor.execute(select_content_query, (local_store_content_id,))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail="해당하는 매장 정보를 찾을 수 없습니다."
                )

            # 두 번째 쿼리: 이미지 정보 조회
            select_images_query = """
                SELECT 
                    LOCAL_STORE_CONTENT_IMAGE_URL
                FROM
                    LOCAL_STORE_CONTENT_IMAGE  
                WHERE
                    LOCAL_STORE_CONTENT_ID = %s
            """

            cursor.execute(select_images_query, (local_store_content_id,))
            images = cursor.fetchall()
            image_urls = [LocStoreImage(local_store_image_url=image["LOCAL_STORE_CONTENT_IMAGE_URL"]) for image in images]

            # 결과를 Pydantic 모델 형식에 맞춰 반환
            result = LocStoreDetailContentResponse(
                local_store_detail_content=LocStoreDetailContent(
                    local_store_content_id=row["LOCAL_STORE_CONTENT_ID"],
                    title=row["TITLE"],
                    content=row["CONTENT"],
                    status=row["STATUS"]
                ),
                image=image_urls
            )
            return result
    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred LocStoreDetailContentResponse: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")



# 게시글 삭제
def delete_loc_store_content_status(local_store_content_id: int) -> bool:
    connection = get_re_db_connection()

    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 업데이트 쿼리 작성
            delete_query = """
                UPDATE LOCAL_STORE_CONTENT
                SET STATUS = 'D'
                WHERE LOCAL_STORE_CONTENT_ID = %s
            """
            # 쿼리 실행
            cursor.execute(delete_query, (local_store_content_id))
            connection.commit()
            
            # rowcount를 통해 업데이트 성공 여부 확인
            if cursor.rowcount == 0:
                return False  # 업데이트된 행이 없는 경우 False 반환
            return True  # 업데이트 성공 시 True 반환
    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred delete: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        connection.close()


# 게시글 수정
def update_loc_store_content(local_store_content_id: int, title: str, content: str) -> bool:
    connection = get_re_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 업데이트 쿼리 작성
            update_query = """
                UPDATE LOCAL_STORE_CONTENT
                SET 
                    TITLE = %s,
                    CONTENT = %s
                WHERE LOCAL_STORE_CONTENT_ID = %s
            """
            # 쿼리 실행
            cursor.execute(update_query, (title, content, local_store_content_id))
            connection.commit()

            # 업데이트 성공 시 데이터 다시 조회

            select_query = """
                SELECT 
                    ls.LOCAL_STORE_CONTENT_ID,
                    ls.STORE_BUSINESS_NUMBER,
                    r.STORE_NAME,
                    r.ROAD_NAME,
                    ls.TITLE,
                    ls.CONTENT,
                    ls.STATUS,
                    ls.CREATED_AT
                FROM
                    LOCAL_STORE_CONTENT ls
                STRAIGHT_JOIN REPORT r
                ON 
                    r.STORE_BUSINESS_NUMBER = ls.STORE_BUSINESS_NUMBER
                WHERE 
                    ls.LOCAL_STORE_CONTENT_ID = %s;
                """
            cursor.execute(select_query, (local_store_content_id,))
            row = cursor.fetchone()  # 조회된 데이터 가져오기
                
            updated_item = LocStoreContentList(
                local_store_content_id=row["LOCAL_STORE_CONTENT_ID"],
                store_business_number=row["STORE_BUSINESS_NUMBER"],
                store_name= row["STORE_NAME"],
                road_name= row["ROAD_NAME"],
                title=row["TITLE"],
                content=row["CONTENT"],
                status=row["STATUS"],
                created_at=row["CREATED_AT"]
            )
            return updated_item


    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred LocStoreDetailContent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        connection.close()

def select_loc_store_existing_image(local_store_content_id : int):
    connection = get_re_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 업데이트 쿼리 작성
            select_query = """
                SELECT 
                    LOCAL_STORE_CONTENT_IMAGE_URL
                FROM LOCAL_STORE_CONTENT_IMAGE
                WHERE LOCAL_STORE_CONTENT_ID = %s
            """
            # 쿼리 실행
            cursor.execute(select_query, (local_store_content_id))
            rows = cursor.fetchall()
            if not rows:
                return []
            
            result = [
                LocStoreImage(
                    local_store_image_url=row["LOCAL_STORE_CONTENT_IMAGE_URL"],
                )
                for row in rows
            ]
            return result
    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred LocStoreImage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")
    finally:
        connection.close()

# 기존 이미지 삭제
def delete_loc_store_existing_image(local_store_content_id: int, images_to_delete: List[str]):
    connection = get_re_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 기존 이미지 목록에서 삭제할 이미지 조건을 추가
            delete_query = """
                DELETE FROM LOCAL_STORE_CONTENT_IMAGE
                WHERE LOCAL_STORE_CONTENT_ID = %s AND LOCAL_STORE_CONTENT_IMAGE_URL IN (%s)
            """
            # 이미지 URL 리스트를 쿼리에 맞게 변환
            formatted_urls = ', '.join(['%s'] * len(images_to_delete))
            final_query = delete_query % (local_store_content_id, formatted_urls)

            # 쿼리 실행
            cursor.execute(final_query, images_to_delete)
            connection.commit()

            # 삭제된 행의 개수 확인
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="해당하는 매장 이미지 정보를 찾을 수 없습니다.",
                )

            return True

    except pymysql.MySQLError as e:
        print(f"Database error occurred: {e}")
        raise HTTPException(status_code=503, detail="Database Connection Error")
    finally:
        connection.close()




def insert_loc_store_new_image(local_store_content_id: int, new_image_urls: List[str]):
    connection = get_re_db_connection()
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # 데이터 인서트 쿼리
            insert_query = """
                INSERT INTO LOCAL_STORE_CONTENT_IMAGE
                (LOCAL_STORE_CONTENT_ID, LOCAL_STORE_CONTENT_IMAGE_URL) 
                VALUES (%s, %s)
            """
            # URL 리스트를 각 튜플로 구성
            data_to_insert = [(local_store_content_id, url) for url in new_image_urls]
            
            # 여러 개의 레코드 삽입
            cursor.executemany(insert_query, data_to_insert)

            # 커밋하여 DB에 반영
            connection.commit()
    except pymysql.MySQLError as e:
        connection.rollback()  # 오류 시 롤백
        print(f"Database error occurred: {e}")
        raise HTTPException(status_code=503, detail="Database Connection Error")

    finally:
        close_connection(connection)  # 연결 종료
