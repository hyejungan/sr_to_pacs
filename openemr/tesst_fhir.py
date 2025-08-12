from openemr.auth import exchange_and_save, get_valid_access_token, authorized_get
import os
from dotenv import load_dotenv

load_dotenv()
BASE = os.getenv("OPENEMR_BASE_URL", "http://localhost:9300").rstrip("/")

# === 1) 처음 한 번만 실행해서 code -> token 저장 ===
# 브라우저에서 받은 code를 아래에 넣고 주석 해제
# tokens = exchange_and_save("<브라우저에서 받은 code>")
# print(tokens)

# === 2) 이후부터는 자동갱신된 access_token 가져와서 사용 ===
FHIR = f"{BASE}/apis/default/fhir"
res = authorized_get(f"{FHIR}/Patient")
print(res.status_code)
print(res.text)
