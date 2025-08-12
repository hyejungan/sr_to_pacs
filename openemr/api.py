import os, requests
from dotenv import load_dotenv

load_dotenv()

BASE = os.getenv("OPENEMR_BASE_URL", "http://localhost:9300").rstrip("/")
FHIR_BASE = os.getenv("FHIR_BASE", "/apis/default/fhir").strip("/")
FHIR_URL = f"{BASE}/{FHIR_BASE}"

def get_patients(access_token: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(f"{FHIR_URL}/Patient", headers=headers, timeout=20)
    r.raise_for_status()
    return r.json()
