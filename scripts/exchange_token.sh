#!/usr/bin/env bash
set -euo pipefail
BASE=${OPENEMR_BASE_URL:-http://localhost:9300}
ISSUER=${OAUTH_ISSUER:-/oauth2/default}
curl -sS -X POST "$BASE/${ISSUER#/}/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=$1" \
  -d "redirect_uri=${REDIRECT_URI}" \
  -d "client_id=${OAUTH_CLIENT_ID}" \
  -d "client_secret=${OAUTH_CLIENT_SECRET}"
