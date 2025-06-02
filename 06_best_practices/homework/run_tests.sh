#!/usr/bin/env bash
set -euo pipefail               # fail fast on any error

################################################################################
# 1️⃣  Environment – credentials + paths + Localstack endpoint
################################################################################
export AWS_ACCESS_KEY_ID=test                     # dummy creds accepted by Localstack
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1

export S3_ENDPOINT_URL="http://localhost:4566"    # <─ your Localstack edge port
export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet" :contentReference[oaicite:1]{index=1}

alias awslocal="aws --endpoint-url $S3_ENDPOINT_URL"      # convenience alias :contentReference[oaicite:3]{index=3}

################################################################################
# 2️⃣  Start (or restart) Localstack
################################################################################
echo "🔄  Starting Localstack…"
docker compose up -d localstack    # idempotent: recreates only if needed

# Wait until the edge port responds
until awslocal s3 ls >/dev/null 2>&1; do
  printf '.'; sleep 1
done
echo -e "\n✅  Localstack is ready"

################################################################################
# 3️⃣  Ensure the bucket exists (harmless if it’s already there)
################################################################################
awslocal s3 mb s3://nyc-duration 2>/dev/null || true

################################################################################
# 4️⃣  Run the full test-suite
################################################################################
echo "🧪  Running pytest…"
pytest -q

echo "🎉  All tests passed"
