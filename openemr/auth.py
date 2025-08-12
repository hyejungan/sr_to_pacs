import os
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# ===== 환경 변수 =====
BASE = os.getenv("OPENEMR_BASE_URL", "http://localhost:9300").rstrip("/")
ISSUER = os.getenv("OAUTH_ISSUER", "/oauth2/default").strip("/")
REDIRECT_URI = os.getenv("REDIRECT_URI")
CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
SCOPES = os.getenv("OAUTH_SCOPES", "openid offline_access api:oemr api:fhir")
TOKENS_PATH = os.getenv("TOKENS_PATH", ".tokens.json")

AUTH_URL  = f"{BASE}/{ISSUER}/authorize"
TOKEN_URL = f"{BASE}/{ISSUER}/token"

# ===== 토큰 POST 공통 처리 =====
def __post_token(payload: dict) -> dict:
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(TOKEN_URL, data=payload, headers=headers, timeout=20)
    r.raise_for_status() #에러일때 예외 던지기
    return r.json()

# 토큰 발급
def exchange_code_for_token(code: str) -> dict:
    return __post_token({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    })

#갱신
def refresh_token(refresh_token_value: str) -> dict:
    return __post_token({
        "grant_type": "refresh_token",
        "refresh_token": refresh_token_value,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    })

# ===== 로컬 파일 저장/로드 =====
def save_tokens(tokens: dict) -> None:
    tokens["_saved_at"] = int(time.time())
    with open(TOKENS_PATH, "w") as f:
        json.dump(tokens, f)

def load_tokens() -> dict | None:
    try:
        with open(TOKENS_PATH) as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# ===== 편의 함수: 교환/갱신 + 저장 =====
def exchange_and_save(code: str) -> dict:
    """authorization_code 교환 후 전체 토큰 저장"""
    tokens = exchange_code_for_token(code)
    save_tokens(tokens)
    return tokens

def refresh_and_save(refresh_token_value: str) -> dict:
    """갱신 후 저장"""
    tokens = refresh_token(refresh_token_value)
    if "refresh_token" not in tokens:
        tokens["refresh_token"] = refresh_token_value
    save_tokens(tokens)
    return tokens

# ===== 유효한 access_token 가져오기(자동 갱신) =====
def get_valid_access_token(buffer_sec: int = 60) -> str:
    tokens = load_tokens()
    if not tokens:
        raise RuntimeError("토큰 없음. exchange_and_save()를 먼저 호출.")

    saved_at = int(tokens.get("_saved_at", time.time()))
    expires_in = int(tokens.get("expires_in", 3600))
    # 만료 임박 또는 만료 시 갱신
    if time.time() >= saved_at + expires_in - buffer_sec:
        tokens = refresh_and_save(tokens["refresh_token"])
    return tokens["access_token"]

# ===== 401 대응 1회 재시도 포함한 요청 헬퍼 =====
def authorized_get(url: str, timeout: int = 20) -> requests.Response:
    at = get_valid_access_token()
    r = requests.get(url, headers={"Authorization": f"Bearer {at}"}, timeout=timeout)
    if r.status_code == 401:
        tokens = load_tokens()
        if tokens and "refresh_token" in tokens:
            new = refresh_and_save(tokens["refresh_token"])
            r = requests.get(url, headers={"Authorization": f"Bearer {new['access_token']}"}, timeout=timeout)
    return r

def authorized_post(url: str, data=None, json_body=None, timeout: int = 20) -> requests.Response:
    at = get_valid_access_token()
    headers = {"Authorization": f"Bearer {at}"}
    r = requests.post(url, data=data, json=json_body, headers=headers, timeout=timeout)
    if r.status_code == 401:
        tokens = load_tokens()
        if tokens and "refresh_token" in tokens:
            new = refresh_and_save(tokens["refresh_token"])
            headers = {"Authorization": f"Bearer {new['access_token']}"}
            r = requests.post(url, data=data, json=json_body, headers=headers, timeout=timeout)
    return r

# ===== 샘플 사용법 =====
# 1) 처음 1회: 브라우저에서 받은 code로 교환/저장
# tokens = exchange_and_save("<AUTHORIZATION_CODE>")
# print(tokens)

# 2) 이후: 자동으로 갱신/사용
# from openemr.auth import get_valid_access_token, authorized_get
# FHIR = f"{BASE}/apis/default/fhir"
# res = authorized_get(f"{FHIR}/Patient")
# print(res.status_code, res.text)
