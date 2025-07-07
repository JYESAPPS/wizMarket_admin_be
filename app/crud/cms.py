import pymysql
from typing import Optional
from app.db.connect import get_db_connection, close_connection, close_cursor, commit, get_re_db_connection, rollback
import pandas as pd
from typing import List, Optional
from fastapi import HTTPException


def insert_thumbnail(data):
    conn = get_re_db_connection()
    cursor = conn.cursor()

    try:
        category_id = data.categoryId
        styles = data.styles

        for style in styles:
            design_id = style.designId
            prompts = style.prompts

            file_index = 1  # ✅ 디자인별 파일 번호 초기화

            for prompt in prompts:
                # 썸네일 테이블에 insert
                insert_sql = """
                    INSERT INTO thumbnail (category_id, design_id, prompt)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_sql, (category_id, design_id, prompt))
                thumbnail_id = cursor.lastrowid

                # ✅ design별 번호로 경로 구성
                image_path = f"http://221.151.48.225:58002/uploads/thumbnail/{category_id}/{design_id}/thumbnail_{file_index}_thumb.jpg"
                file_index += 1

                # 썸네일 패스 테이블에 insert
                path_sql = """
                    INSERT INTO thumbnail_path (thumbnail_id, image_path)
                    VALUES (%s, %s)
                """
                cursor.execute(path_sql, (thumbnail_id, image_path))

        commit(conn)
        print("[OK] 썸네일 및 경로 데이터 삽입 완료")

    except Exception as e:
        rollback(conn)
        print(f"[ERROR] 삽입 실패: {e}")
        raise HTTPException(status_code=500, detail="DB 삽입 실패")

    finally:
        close_cursor(cursor)
        close_connection(conn)
