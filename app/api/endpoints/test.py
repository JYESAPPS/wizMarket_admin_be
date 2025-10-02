# app/routers/kcb.py
import uuid
import requests
import logging
import os
from fastapi import APIRouter, HTTPException

from app.schemas.test import StartReq, StartRes, DecryptReq, DecryptRes
from app.core.settings import settings, POPUP_START_URL
from app.service.kcb_token import get_access_token
from app.utils.kcb_crypto import derive_personal_key_from_enc_key, aes_cbc_pkcs7_b64_decrypt, _hex_iv_to_bytes


log = logging.getLogger("kcb")
router = APIRouter(prefix="/test/kcb", tags=["kcb"])

@router.post("/start", response_model=StartRes)
def kcb_start(req: StartReq):
    log.info(f"[KCB START] return_url={req.return_url}")
    
    try:
        access_token = get_access_token()
    except RuntimeError as e:
        # get_access_token에서 이미 상태/바디를 포함해 raise했으니 그대로 노출
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth 실패: {e}")
    
    x_api_tran_id = uuid.uuid4().hex[:32]
    rqst_svc_tx_seqno = uuid.uuid4().hex[:20]

    body = {
        "idcf_mbr_com_cd": settings.KCB_SITE_CD,
        "rqst_svc_tx_seqno": rqst_svc_tx_seqno,
        "return_url": str(req.return_url),
        "site_name": settings.KCB_SITE_NAME,
        "site_url": settings.KCB_SITE_URL,
        # ✅ 암호화 설정 필수
        "enc_algo_cd": settings.KCB_ENC_ALGO_CD,
        "enc_iv": settings.KCB_ENC_IV,
        "rqst_cause_cd": "00",  # ✅ 요청사유코드(2자리). 예: 00
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-api-tran-id": x_api_tran_id,
        "Content-Type": "application/json",
    }

    log.info(f"[KCB START] POST {POPUP_START_URL} headers={{auth,tran-id}} body={body}")

    try:
        resp = requests.post(POPUP_START_URL, json=body, headers=headers, timeout=10)
        log.info(f"[KCB START] status={resp.status_code}")
        if resp.status_code >= 400:
            log.error(f"[KCB START] body={resp.text}")
        resp.raise_for_status()
        data = resp.json()
    except requests.HTTPError:
        # 그대로 응답 바디를 프런트로 전달(디버그 편의)
        try:
            err = resp.json()
        except Exception:
            err = {"detail": resp.text}
        raise HTTPException(status_code=resp.status_code, detail=err)
    except requests.exceptions.SSLError as e:
        log.exception("[KCB START] SSL 오류")
        raise HTTPException(status_code=500, detail="KCB START SSL 오류")
    except Exception as e:
        log.exception("[KCB START] 요청 실패")
        raise HTTPException(status_code=500, detail=f"KCB popup-start 호출 실패: {e}")

    rsp_cd = data.get("rsp_cd", "")
    if rsp_cd != "B000":
        log.warning(f"[KCB START] rsp_cd={rsp_cd}, body={data}")
        raise HTTPException(status_code=400, detail=data)

    log.info(f"[KCB START] success: svc_tkn len={len(data.get('svc_tkn',''))}, seq={data.get('rqst_svc_tx_seqno')}")
    return {
        "rsp_cd": rsp_cd,
        "rsp_msg": data.get("rsp_msg"),
        "idcf_mbr_com_cd": data.get("idcf_mbr_com_cd") or settings.KCB_SITE_CD,
        "svc_tkn": data.get("svc_tkn"),
        "rqst_svc_tx_seqno": data.get("rqst_svc_tx_seqno") or rqst_svc_tx_seqno,
        "enc_key": data.get("enc_key"),      # ← 추가
        "enc_algo_cd": settings.KCB_ENC_ALGO_CD,
        "enc_iv": settings.KCB_ENC_IV,
    }


POPUP_RESULT_URL = "https://api.ok-name.co.kr:20443/v1/id/phone/popup-result"

@router.post("/decrypt", response_model=DecryptRes)
def kcb_decrypt(req: DecryptReq):
    """
    개발 모드: 서버 저장 없이 1회성 복호화
    - 입력: svc_tkn (return_url에서), enc_key (start 응답의 암호문)
    - 내부: popup-result 조회 -> enc_key 복호화 -> 필드 복호화
    """
    # 1) OAuth
    try:
        access_token = get_access_token()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth 실패: {e}")
    
    # 2) popup-result 조회
    x_api_tran_id = uuid.uuid4().hex[:32]
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-api-tran-id": x_api_tran_id,
        "Content-Type": "application/json",
    }
    body = {
        "idcf_mbr_com_cd": settings.KCB_SITE_CD,
        "svc_tkn": req.svc_tkn,
    }
    insecure = os.getenv("KCB_SSL_INSECURE", "false").lower() == "true"
    try:
        resp = requests.post(POPUP_RESULT_URL, json=body, headers=headers, timeout=10, verify=not insecure)
        data = resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"popup-result 호출 실패: {e}")

    rsp_cd = data.get("rsp_cd", "")
    if rsp_cd != "B000":
        # 실패코드면 원문 그대로 반환
        return {"rsp_cd": rsp_cd, "rsp_msg": data.get("rsp_msg"), "raw": data}

    # 3) 복호화 준비 (AES 1331 가정)
    enc_algo_cd = (req.enc_algo_cd or settings.KCB_ENC_ALGO_CD or "").strip()
    if enc_algo_cd != "1331":
        # 명세상 1331(AES) 또는 1131(SEED)인데, 개발은 AES로 고정
        raise HTTPException(status_code=400, detail=f"지원하지 않는 enc_algo_cd={enc_algo_cd} (개발은 1331 AES만 처리)")

    iv_hex = (req.enc_iv or settings.KCB_ENC_IV)
    iv = _hex_iv_to_bytes(iv_hex)

    enc_key_b64 = req.enc_key
    if not enc_key_b64:
        raise HTTPException(status_code=400, detail="enc_key 누락 (개발 모드: start 응답에서 전달받아야 함)")

    # 4) step1: 개인정보키 복원
    try:
        personal_key = derive_personal_key_from_enc_key(enc_key_b64, settings.KCB_SITE_CD, iv_hex)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"enc_key 복호화 실패: {e}")

    # 5) step2: 각 항목 복호화 (있을 때만)
    def dec(v):
        if not v:
            return None
        raw = aes_cbc_pkcs7_b64_decrypt(v, personal_key, iv)  # bytes

        # 1) CP949(EUC-KR) 우선
        for enc in ("cp949", "euc-kr", "utf-8"):
            try:
                s = raw.decode(enc)  # strict
                return s.strip()
            except Exception:
                continue

        # 최후 폴백(깨짐 방지용)
        return raw.decode("latin1", errors="replace").strip()

    user = {
        "name": dec(data.get("nm")),
        "birth": dec(data.get("brdt")),   # YYYYMMDD
        "sex": dec(data.get("sex")),      # 1/2 등
        "nation": dec(data.get("ntv_frnr_cd")),
        "phone": dec(data.get("mbphn_no")),
        "ci": dec(data.get("ci")),
        "di": dec(data.get("di")),
        "telco": dec(data.get("cmcm_tp_cd")),   # 통신사 코드
    }

    return {"rsp_cd": "B000", "user": user, "raw": data}