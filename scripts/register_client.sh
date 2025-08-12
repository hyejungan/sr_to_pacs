#!/usr/bin/env bash
set -euo pipefail
BASE=${OPENEMR_BASE_URL:-http://localhost:9300}
ISSUER=${OAUTH_ISSUER:-/oauth2/default}
curl -sS -X POST -H "Content-Type: application/json" \
  -d @client.json \
  "$BASE/${ISSUER#/}/registration"
